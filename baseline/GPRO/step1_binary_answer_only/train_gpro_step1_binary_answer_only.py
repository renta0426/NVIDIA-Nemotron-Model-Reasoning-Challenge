from __future__ import annotations

import argparse
import csv
import inspect
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
DEFAULT_DATASET_CSV = Path(__file__).resolve().parent / "artifacts" / "step1_binary_answer_only_training_data.csv"
DEFAULT_MANIFEST_JSON = Path(__file__).resolve().parent / "artifacts" / "step1_binary_answer_only_manifest.json"
DEFAULT_OUTPUT_DIR = Path("/kaggle/working/adapter_gpro_step1_binary")
BOXED_INSTRUCTION = "Please put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`"
DEFAULT_SEED = 42
DEFAULT_SHORT_TRACE_QUOTA = 160
LORA_RANK = 32
MAX_SEQ_LEN = 2048
NUM_EPOCHS = 2
BATCH_SIZE = 1
GRAD_ACCUM = 4
LR = 1e-4
REQUIRED_DATASET_COLUMNS = [
    "id",
    "prompt",
    "answer",
    "generated_cot",
    "label",
    "assistant_style",
    "source_selection_tier",
]
PRECOMPUTED_TEXT_COLUMNS = [
    "user_message",
    "assistant_message",
]
OUTPUT_COLUMNS = REQUIRED_DATASET_COLUMNS + PRECOMPUTED_TEXT_COLUMNS
REQUIRED_SOURCE_COLUMNS = {
    "id",
    "prompt",
    "answer",
    "family",
    "template_subtype",
    "teacher_solver_candidate",
    "selection_tier",
}
STRICT_BOXED_COMPLETION_RE = re.compile(
    r"^\s*(?:(?P<think><think>[\s\S]*?</think>)\s*)?\\boxed\{(?P<boxed>[01]{8})\}\s*$"
)


@dataclass(frozen=True)
class SelectedRow:
    row: dict[str, str]
    rank_key: tuple[Any, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "GPRO Step 1 for binary-specialist warm start. "
            "Builds a binary-only dataset that is mostly boxed-only, with a small ultra-short trace subset, "
            "and can train an assistant-only LoRA on top of it."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("build-dataset", "preview", "train"),
        default="build-dataset",
        help="build-dataset writes the CSV/manifest, preview prints a few rows, train runs the assistant-only LoRA path.",
    )
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--dataset-csv", type=Path, default=DEFAULT_DATASET_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--model-path", type=str, default="")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--short-trace-quota",
        type=int,
        default=DEFAULT_SHORT_TRACE_QUOTA,
        help="How many verified binary rows keep an ultra-short trace. The rest become boxed-only.",
    )
    parser.add_argument(
        "--rollout-success-csv",
        type=Path,
        default=None,
        help=(
            "Optional CSV of strict rollout successes to fold into Step 1 as positive teachers. "
            "Only manual_audit_priority binary rows are accepted from this file."
        ),
    )
    parser.add_argument("--preview-rows", type=int, default=4)
    return parser.parse_args()


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def parse_float(value: Any, default: float | None = None) -> float | None:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header is missing: {path}")
        missing = REQUIRED_SOURCE_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
        return [dict(row) for row in reader]


def load_dataset_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header is missing: {path}")
        missing = set(REQUIRED_DATASET_COLUMNS).difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError(f"Dataset CSV is empty: {path}")
    return rows


def solver_priority(row: dict[str, str]) -> int:
    solver = row.get("teacher_solver_candidate", "")
    priorities = {
        "binary_structured_byte_formula": 100,
        "binary_structured_byte_formula_abstract": 96,
        "binary_affine_xor": 94,
        "binary_two_bit_boolean": 93,
        "binary_three_bit_boolean": 91,
        "binary_byte_transform": 90,
        "binary_bit_permutation_bijection": 88,
        "binary_bit_permutation_independent": 86,
        "binary_structured_byte_not_formula": 84,
    }
    return priorities.get(solver, 50)


def structured_support_strength(row: dict[str, str]) -> int:
    safe_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    return max(safe_support * 10, abstract_support)


def rank_verified_short_trace_row(row: dict[str, str]) -> tuple[Any, ...]:
    hard_score = parse_float(row.get("hard_score", ""), 999.0)
    if hard_score is None:
        hard_score = 999.0
    example_count = parse_int(row.get("num_examples", "0"), 0)
    return (
        -solver_priority(row),
        -structured_support_strength(row),
        -example_count,
        hard_score,
        row.get("id", ""),
    )


def make_selected(items: list[dict[str, str]], ranker: Callable[[dict[str, str]], tuple[Any, ...]]) -> list[SelectedRow]:
    return [SelectedRow(row=item, rank_key=ranker(item)) for item in items]


def round_robin_select(
    items: list[SelectedRow],
    quota: int,
    seed: int,
    key_fn: Callable[[SelectedRow], str],
) -> list[dict[str, str]]:
    if quota <= 0:
        return []
    if len(items) <= quota:
        return [item.row for item in sorted(items, key=lambda item: item.rank_key)]
    groups: dict[str, list[SelectedRow]] = defaultdict(list)
    for item in items:
        groups[key_fn(item)].append(item)
    group_names = sorted(groups)
    rng = random.Random(seed)
    for group_name in group_names:
        groups[group_name].sort(key=lambda item: item.rank_key)
    order = group_names[:]
    rng.shuffle(order)
    queues = {group_name: deque(groups[group_name]) for group_name in order}
    selected: list[dict[str, str]] = []
    while len(selected) < quota and queues:
        for group_name in list(order):
            queue = queues.get(group_name)
            if not queue:
                continue
            selected.append(queue.popleft().row)
            if len(selected) >= quota:
                break
            if not queue:
                queues.pop(group_name, None)
        order = [group_name for group_name in order if group_name in queues]
    if len(selected) != quota:
        available = sum(len(group_items) for group_items in groups.values())
        raise ValueError(f"Unable to satisfy quota {quota}; only {available} candidates available")
    return selected


def binary_non_exclude_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        if row.get("family") != "bit_manipulation":
            continue
        if row.get("selection_tier") == "exclude_suspect":
            continue
        selected.append(row)
    return selected


def verified_binary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        if row.get("selection_tier") != "verified_trace_ready":
            continue
        if not parse_bool(row.get("verified_trace_ready", "true")):
            continue
        if not row.get("teacher_solver_candidate", ""):
            continue
        selected.append(row)
    return selected


def answer_only_binary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("selection_tier") == "answer_only_keep"]


def build_short_binary_trace(row: dict[str, str]) -> str:
    solver = row.get("teacher_solver_candidate", "")
    phrases = {
        "binary_structured_byte_formula": "Infer the byte-level rule from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_structured_byte_formula_abstract": "Infer the repeated byte pattern from the examples, apply it once to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_structured_byte_not_formula": "Infer the bytewise negation-style rule from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_affine_xor": "Infer the XOR-style bit rule from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_two_bit_boolean": "Infer the local 2-bit boolean rule from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_three_bit_boolean": "Infer the local 3-bit boolean rule from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_byte_transform": "Infer the byte transform from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_bit_permutation_bijection": "Infer the bit permutation from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
        "binary_bit_permutation_independent": "Infer how each bit position moves from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
    }
    sentence = phrases.get(
        solver,
        "Infer the binary transformation from the examples, apply it to the query, and preserve exactly 8 bits with leading zeros.",
    )
    return f"<think>{sentence}</think>"


def build_user_message(prompt: str) -> str:
    return prompt + "\n" + BOXED_INSTRUCTION


def render_assistant_message_from_fields(*, answer: str, generated_cot: str, assistant_style: str) -> str:
    if assistant_style == "trace_boxed":
        return f"{generated_cot}\n\n\\boxed{{{answer}}}"
    if assistant_style == "boxed_only":
        return f"\\boxed{{{answer}}}"
    raise ValueError(f"Unsupported assistant_style: {assistant_style}")


def enrich_output_row(row: dict[str, str]) -> dict[str, str]:
    enriched = dict(row)
    enriched["user_message"] = build_user_message(enriched["prompt"])
    enriched["assistant_message"] = render_assistant_message_from_fields(
        answer=enriched["answer"],
        generated_cot=enriched["generated_cot"],
        assistant_style=enriched["assistant_style"],
    )
    return enriched


def detect_rollout_completion_field(fieldnames: list[str]) -> str:
    for candidate in ("completion", "assistant_message", "response", "raw_output"):
        if candidate in fieldnames:
            return candidate
    raise ValueError(
        "rollout-success-csv must contain one of: completion, assistant_message, response, raw_output"
    )


def split_strict_rollout_completion(completion: str, expected_answer: str) -> tuple[str, str]:
    text = completion.strip()
    match = STRICT_BOXED_COMPLETION_RE.fullmatch(text)
    if not match:
        raise ValueError("completion is not strict boxed success")
    if match.group("boxed") != expected_answer:
        raise ValueError("completion boxed answer does not match source answer")
    think_text = match.group("think") or ""
    if think_text and expected_answer in think_text:
        raise ValueError("completion repeats the final answer outside the final box")
    assistant_style = "trace_boxed" if think_text else "boxed_only"
    return assistant_style, think_text


def load_rollout_success_rows(
    path: Path | None,
    *,
    source_index: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    if path is None:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header is missing: {path}")
        if "id" not in reader.fieldnames:
            raise ValueError(f"rollout-success-csv must contain id column: {path}")
        completion_field = detect_rollout_completion_field(list(reader.fieldnames))
        rows = [dict(row) for row in reader]
    output_rows: list[dict[str, str]] = []
    per_id_counter: Counter[str] = Counter()
    for row in rows:
        source_id = row.get("id", "")
        if source_id not in source_index:
            raise ValueError(f"Unknown rollout source id: {source_id}")
        source_row = source_index[source_id]
        if source_row.get("family") != "bit_manipulation":
            raise ValueError(f"Rollout success id is not binary: {source_id}")
        if source_row.get("selection_tier") != "manual_audit_priority":
            raise ValueError(
                f"Rollout success id must come from manual_audit_priority for Step 1: {source_id}"
            )
        answer = source_row.get("answer", "").strip()
        assistant_style, generated_cot = split_strict_rollout_completion(row.get(completion_field, ""), answer)
        per_id_counter[source_id] += 1
        output_rows.append(
            {
                "id": f"{source_id}__rollout_{per_id_counter[source_id]:03d}",
                "prompt": source_row["prompt"],
                "answer": answer,
                "generated_cot": generated_cot,
                "label": "binary",
                "assistant_style": assistant_style,
                "source_selection_tier": "rollout_strict_success",
            }
        )
    if not output_rows:
        raise ValueError(f"No valid strict rollout successes found in {path}")
    return output_rows


def build_output_rows(
    *,
    verified_rows: list[dict[str, str]],
    answer_only_rows: list[dict[str, str]],
    rollout_rows: list[dict[str, str]],
    short_trace_quota: int,
    seed: int,
) -> list[dict[str, str]]:
    short_trace_selected = round_robin_select(
        make_selected(verified_rows, rank_verified_short_trace_row),
        quota=min(short_trace_quota, len(verified_rows)),
        seed=seed,
        key_fn=lambda item: item.row.get("teacher_solver_candidate", "unknown"),
    )
    short_trace_ids = {row["id"] for row in short_trace_selected}
    output_rows: list[dict[str, str]] = []
    for row in verified_rows:
        use_trace = row["id"] in short_trace_ids
        output_rows.append(
            {
                "id": row["id"],
                "prompt": row["prompt"],
                "answer": row["answer"].strip(),
                "generated_cot": build_short_binary_trace(row) if use_trace else "",
                "label": "binary",
                "assistant_style": "trace_boxed" if use_trace else "boxed_only",
                "source_selection_tier": "verified_trace_ready",
            }
        )
    for row in answer_only_rows:
        output_rows.append(
            {
                "id": row["id"],
                "prompt": row["prompt"],
                "answer": row["answer"].strip(),
                "generated_cot": "",
                "label": "binary",
                "assistant_style": "boxed_only",
                "source_selection_tier": "answer_only_keep",
            }
        )
    output_rows.extend(rollout_rows)
    output_rows.sort(key=lambda row: row["id"])
    return [enrich_output_row(row) for row in output_rows]


def validate_output(rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("Output dataset is empty")
    seen_ids: set[str] = set()
    for row in rows:
        row_id = row.get("id", "")
        if not row_id:
            raise ValueError("Every row must have an id")
        if row_id in seen_ids:
            raise ValueError(f"Duplicate output row id: {row_id}")
        seen_ids.add(row_id)
        if set(row) != set(OUTPUT_COLUMNS):
            raise ValueError(f"Unexpected output columns for row {row_id}")
        if row["label"] != "binary":
            raise ValueError(f"Step 1 dataset must be binary-only: {row_id}")
        if not re.fullmatch(r"[01]{8}", row["answer"]):
            raise ValueError(f"Binary answers must stay exact 8-bit strings: {row_id}")
        expected_user_message = build_user_message(row["prompt"])
        if row["user_message"] != expected_user_message:
            raise ValueError(f"user_message mismatch for row {row_id}")
        expected_assistant_message = render_assistant_message_from_fields(
            answer=row["answer"],
            generated_cot=row["generated_cot"],
            assistant_style=row["assistant_style"],
        )
        if row["assistant_message"] != expected_assistant_message:
            raise ValueError(f"assistant_message mismatch for row {row_id}")
        if row["assistant_style"] == "trace_boxed":
            if not row["generated_cot"].startswith("<think>") or not row["generated_cot"].endswith("</think>"):
                raise ValueError(f"trace_boxed rows must use a <think> wrapper: {row_id}")
            if row["answer"] in row["generated_cot"]:
                raise ValueError(f"Binary traces must not repeat the final 8-bit answer outside the box: {row_id}")
        elif row["assistant_style"] == "boxed_only":
            if row["generated_cot"]:
                raise ValueError(f"boxed_only rows must not carry generated_cot: {row_id}")
        else:
            raise ValueError(f"Unsupported assistant_style for row {row_id}: {row['assistant_style']}")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def base_source_id(output_id: str) -> str:
    return output_id.split("__rollout_", 1)[0]


def build_manifest(
    *,
    source_rows: list[dict[str, str]],
    output_rows: list[dict[str, str]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    source_index = {row["id"]: row for row in source_rows}
    solver_counts = Counter(source_index[base_source_id(row["id"])].get("teacher_solver_candidate", "") for row in output_rows)
    template_counts = Counter(source_index[base_source_id(row["id"])].get("template_subtype", "") for row in output_rows)
    source_tier_counts = Counter(row["source_selection_tier"] for row in output_rows)
    style_counts = Counter(row["assistant_style"] for row in output_rows)
    verified_rows = [row for row in output_rows if row["source_selection_tier"] == "verified_trace_ready"]
    answer_only_rows = [row for row in output_rows if row["source_selection_tier"] == "answer_only_keep"]
    rollout_rows = [row for row in output_rows if row["source_selection_tier"] == "rollout_strict_success"]
    boxed_only_ratio = sum(1 for row in output_rows if row["assistant_style"] == "boxed_only") / len(output_rows)
    return {
        "source_csv": str(args.source_csv),
        "dataset_csv": str(args.dataset_csv),
        "manifest_json": str(args.manifest_json),
        "seed": args.seed,
        "dataset_size": len(output_rows),
        "source_binary_non_exclude_count": len(binary_non_exclude_rows(source_rows)),
        "source_verified_trace_ready_count": len(verified_binary_rows(binary_non_exclude_rows(source_rows))),
        "source_answer_only_keep_count": len(answer_only_binary_rows(binary_non_exclude_rows(source_rows))),
        "short_trace_quota_requested": args.short_trace_quota,
        "assistant_style_counts": dict(sorted(style_counts.items())),
        "source_selection_tier_counts": dict(sorted(source_tier_counts.items())),
        "teacher_solver_counts": dict(sorted(solver_counts.items())),
        "template_subtype_counts": dict(sorted(template_counts.items())),
        "training_plumbing": {
            "assistant_only_loss": True,
            "precomputed_messages_in_dataset": True,
            "boxed_instruction": BOXED_INSTRUCTION,
            "max_seq_len": MAX_SEQ_LEN,
            "epochs": NUM_EPOCHS,
            "learning_rate": LR,
            "lora_rank": LORA_RANK,
            "target_modules_default": "all-linear",
        },
        "step1_binary_design": {
            "goal": "stabilize short exact boxed 8-bit outputs before ORPO/GRPO",
            "uses_binary_only_rows": True,
            "excludes_selection_tier": "exclude_suspect",
            "verified_rows_boxed_only_majority": True,
            "verified_short_trace_rows": sum(1 for row in verified_rows if row["assistant_style"] == "trace_boxed"),
            "verified_boxed_only_rows": sum(1 for row in verified_rows if row["assistant_style"] == "boxed_only"),
            "answer_only_boxed_rows": len(answer_only_rows),
            "rollout_strict_success_rows": len(rollout_rows),
            "boxed_only_ratio": round(boxed_only_ratio, 4),
            "rollout_success_source_rule": "manual_audit_priority only",
            "binary_trace_avoids_repeating_final_answer_inside_think": True,
        },
        "notes": [
            "README evaluation prioritizes boxed extraction and otherwise falls back to heuristic extraction, so Step 1 biases the policy toward short exact boxed answers.",
            "Most verified binary rows are converted to boxed-only supervision; only a small diverse subset keeps an ultra-short, answer-free <think> one-liner.",
            "manual_audit_priority rows are excluded from the base positive set and may only re-enter via strict rollout successes.",
            "The completed dataset precomputes user_message and assistant_message so notebook training only performs tokenizer-dependent rendering and tokenization.",
        ],
    }


def build_dataset(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source_rows = load_rows(args.source_csv)
    binary_rows = binary_non_exclude_rows(source_rows)
    verified_rows = verified_binary_rows(binary_rows)
    answer_only_rows = answer_only_binary_rows(binary_rows)
    source_index = {row["id"]: row for row in source_rows}
    rollout_rows = load_rollout_success_rows(args.rollout_success_csv, source_index=source_index)
    output_rows = build_output_rows(
        verified_rows=verified_rows,
        answer_only_rows=answer_only_rows,
        rollout_rows=rollout_rows,
        short_trace_quota=args.short_trace_quota,
        seed=args.seed,
    )
    validate_output(output_rows)
    manifest = build_manifest(source_rows=source_rows, output_rows=output_rows, args=args)
    write_csv(args.dataset_csv, output_rows, OUTPUT_COLUMNS)
    ensure_parent(args.manifest_json)
    args.manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_rows, manifest


def render_assistant_message(row: dict[str, str]) -> str:
    if row.get("assistant_message"):
        return row["assistant_message"]
    return render_assistant_message_from_fields(
        answer=row["answer"],
        generated_cot=row.get("generated_cot", ""),
        assistant_style=row["assistant_style"],
    )


def import_training_stack() -> dict[str, object]:
    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

    return {
        "torch": torch,
        "Dataset": Dataset,
        "LoraConfig": LoraConfig,
        "TaskType": TaskType,
        "get_peft_model": get_peft_model,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "Trainer": Trainer,
        "TrainingArguments": TrainingArguments,
    }


def patch_runtime() -> None:
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    try:
        import triton.backends.nvidia.compiler as nv_compiler
    except Exception:
        return
    os.environ.setdefault("TRITON_PTXAS_BLACKWELL_PATH", "/tmp/ptxas-blackwell")
    nv_compiler.get_ptxas_version = lambda arch: "12.0"
    for name, mod in sys.modules.items():
        if "modeling_nemotron_h" in name:
            mod.is_fast_path_available = False


def apply_chat_template_safe(
    tokenizer: Any,
    messages: list[dict[str, str]],
    *,
    add_generation_prompt: bool,
    enable_thinking: bool,
) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=enable_thinking,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
        )
    except Exception:
        rendered: list[str] = []
        for message in messages:
            rendered.append(f"<|{message['role']}|>\n{message['content']}")
        if add_generation_prompt:
            if enable_thinking:
                rendered.append("<|assistant|>\n<think>")
            else:
                rendered.append("<|assistant|>")
        return "\n".join(rendered)


def render_training_pair(tokenizer: Any, row: dict[str, str]) -> tuple[str, str, str, str]:
    user_message = row.get("user_message") or build_user_message(row["prompt"])
    assistant_message = render_assistant_message(row)
    prompt_prefix = apply_chat_template_safe(
        tokenizer,
        [{"role": "user", "content": user_message}],
        add_generation_prompt=True,
        enable_thinking=True,
    )
    full_text = apply_chat_template_safe(
        tokenizer,
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ],
        add_generation_prompt=False,
        enable_thinking=True,
    )
    return user_message, assistant_message, prompt_prefix, full_text


def shared_token_prefix_length(prefix_ids: list[int], full_ids: list[int]) -> int:
    limit = min(len(prefix_ids), len(full_ids))
    index = 0
    while index < limit and prefix_ids[index] == full_ids[index]:
        index += 1
    return index


def tokenize_training_row(tokenizer: Any, row: dict[str, str]) -> dict[str, Any]:
    _, _assistant_message, prompt_prefix, full_text = render_training_pair(tokenizer, row)
    prefix_ids = list(
        tokenizer(
            prompt_prefix,
            add_special_tokens=False,
            truncation=True,
            max_length=MAX_SEQ_LEN,
        )["input_ids"]
    )
    try:
        full_encoded = tokenizer(
            full_text,
            add_special_tokens=False,
            truncation=True,
            max_length=MAX_SEQ_LEN,
        )
    except TypeError:
        full_encoded = tokenizer(full_text, add_special_tokens=False, truncation=True, max_length=MAX_SEQ_LEN)
    input_ids = list(full_encoded["input_ids"])
    attention_mask = list(full_encoded["attention_mask"])
    # Supervise from the actual generation boundary, not from the raw assistant content.
    # For boxed_only rows the chat template renders `<think></think>\boxed{...}` while the
    # user-only prompt ends at `<think>`. If loss starts at `\boxed{...}`, the model never
    # learns to emit `</think>` and tends to continue a long reasoning trace at inference.
    assistant_token_start = shared_token_prefix_length(prefix_ids, input_ids)
    if assistant_token_start == 0:
        raise ValueError(f"Prompt prefix did not align with full chat rendering for row {row['id']}")
    if assistant_token_start >= len(input_ids):
        raise ValueError(f"Assistant tokens were truncated out for row {row['id']}")
    labels = [-100] * assistant_token_start + input_ids[assistant_token_start:]
    if len(labels) != len(input_ids):
        raise ValueError(f"Label/input length mismatch for row {row['id']}")
    return {
        "id": row["id"],
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


class AssistantOnlyDataCollator:
    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = pad_token_id

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        import torch

        max_len = max(len(feature["input_ids"]) for feature in features)
        input_ids_batch: list[list[int]] = []
        attention_batch: list[list[int]] = []
        labels_batch: list[list[int]] = []
        for feature in features:
            pad = max_len - len(feature["input_ids"])
            input_ids_batch.append(feature["input_ids"] + [self.pad_token_id] * pad)
            attention_batch.append(feature["attention_mask"] + [0] * pad)
            labels_batch.append(feature["labels"] + [-100] * pad)
        return {
            "input_ids": torch.tensor(input_ids_batch, dtype=torch.long),
            "attention_mask": torch.tensor(attention_batch, dtype=torch.long),
            "labels": torch.tensor(labels_batch, dtype=torch.long),
        }


def preview_rows(rows: list[dict[str, str]], preview_count: int) -> None:
    print(f"Previewing {min(preview_count, len(rows))} rows from {len(rows)}-row GPRO Step 1 dataset")
    for row in rows[:preview_count]:
        print("=" * 80)
        print(f"id={row['id']} style={row['assistant_style']} tier={row['source_selection_tier']}")
        print(build_user_message(row["prompt"])[:500])
        print("--- assistant ---")
        print(render_assistant_message(row)[:500])


def train(args: argparse.Namespace, rows: list[dict[str, str]]) -> None:
    if not args.model_path:
        raise ValueError("--model-path is required for mode=train")
    stack = import_training_stack()
    patch_runtime()
    tokenizer = stack["AutoTokenizer"].from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenized_rows = [tokenize_training_row(tokenizer, row) for row in rows]
    dataset = stack["Dataset"].from_list(tokenized_rows)
    data_collator = AssistantOnlyDataCollator(tokenizer.pad_token_id)

    torch = stack["torch"]
    model = stack["AutoModelForCausalLM"].from_pretrained(
        args.model_path,
        device_map={"": 0},
        trust_remote_code=True,
        dtype=torch.bfloat16,
    )
    model.gradient_checkpointing_enable()
    lora_config = stack["LoraConfig"](
        r=LORA_RANK,
        lora_alpha=32,
        target_modules="all-linear",
        lora_dropout=0.05,
        bias="none",
        task_type=stack["TaskType"].CAUSAL_LM,
    )
    model = stack["get_peft_model"](model, lora_config)

    training_args = stack["TrainingArguments"](
        output_dir=str(args.output_dir),
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LR,
        logging_steps=5,
        bf16=True,
        max_grad_norm=1.0,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        save_strategy="no",
        report_to="none",
        gradient_checkpointing=True,
        remove_unused_columns=False,
    )

    trainer_kwargs = {
        "model": model,
        "args": training_args,
        "train_dataset": dataset,
        "data_collator": data_collator,
    }
    trainer_signature = inspect.signature(stack["Trainer"].__init__).parameters
    if "processing_class" in trainer_signature:
        trainer_kwargs["processing_class"] = tokenizer
    elif "tokenizer" in trainer_signature:
        trainer_kwargs["tokenizer"] = tokenizer
    trainer = stack["Trainer"](**trainer_kwargs)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    print("Starting GPRO Step 1 binary-only assistant-only training...")
    trainer.train()
    trainer.model.save_pretrained(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    print(f"Adapter saved to {args.output_dir}")


def main() -> None:
    args = parse_args()
    rows, manifest = build_dataset(args)
    print(f"Wrote GPRO Step 1 dataset CSV: {args.dataset_csv}")
    print(f"Wrote GPRO Step 1 manifest: {args.manifest_json}")
    print(json.dumps(manifest["assistant_style_counts"], ensure_ascii=False, sort_keys=True))
    print(json.dumps(manifest["source_selection_tier_counts"], ensure_ascii=False, sort_keys=True))
    if args.mode == "build-dataset":
        return
    if args.mode == "preview":
        preview_rows(rows, args.preview_rows)
        return
    train(args, rows)


if __name__ == "__main__":
    main()
