from __future__ import annotations

import argparse
import csv
import inspect
import json
import os
import random
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
DEFAULT_DATASET_CSV = Path(__file__).resolve().parent / "artifacts" / "phase1_assistant_only_training_data.csv"
DEFAULT_MANIFEST_JSON = Path(__file__).resolve().parent / "artifacts" / "phase1_assistant_only_manifest.json"
DEFAULT_OUTPUT_DIR = Path("/kaggle/working/adapter_phase1")
BOXED_INSTRUCTION = "Please put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`"
LORA_RANK = 32
MAX_SEQ_LEN = 2048
NUM_EPOCHS = 2
BATCH_SIZE = 1
GRAD_ACCUM = 4
LR = 1e-4
DEFAULT_SEED = 42
VERIFIED_QUOTAS = {
    "gravity_constant": 120,
    "unit_conversion": 120,
    "roman_numeral": 120,
    "text_decryption": 100,
    "bit_manipulation": 160,
    "symbol_equation": 60,
}
ANSWER_ONLY_QUOTAS = {
    "text_decryption": 20,
    "bit_manipulation": 120,
    "symbol_equation": 80,
}
DEFAULT_SUBSAMPLE_SIZE = sum(VERIFIED_QUOTAS.values()) + sum(ANSWER_ONLY_QUOTAS.values())
FAMILY_LABELS = {
    "gravity_constant": "gravity",
    "unit_conversion": "unit",
    "roman_numeral": "roman",
    "text_decryption": "text",
    "bit_manipulation": "binary",
    "symbol_equation": "symbol",
}
OUTPUT_COLUMNS = [
    "id",
    "prompt",
    "answer",
    "generated_cot",
    "label",
    "assistant_style",
    "source_selection_tier",
]
REQUIRED_SOURCE_COLUMNS = {
    "id",
    "prompt",
    "answer",
    "family",
    "template_subtype",
    "teacher_solver_candidate",
    "selection_tier",
    "family_analysis_json",
}
STRONG_BINARY_SOLVERS = {
    "binary_affine_xor",
    "binary_two_bit_boolean",
    "binary_three_bit_boolean",
    "binary_byte_transform",
    "binary_bit_permutation_bijection",
    "binary_bit_permutation_independent",
    "binary_structured_byte_formula",
    "binary_structured_byte_formula_abstract",
}


@dataclass(frozen=True)
class SelectedRow:
    row: dict[str, str]
    rank_key: tuple[Any, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 1 training pipeline for baseline/cot. "
            "Builds a curated dataset and reimplements the baseline training flow with assistant-only loss."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("build-dataset", "preview", "train"),
        default="build-dataset",
        help="build-dataset writes the CSV/manifest, preview prints a few rendered samples, train runs the LoRA training pipeline.",
    )
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--dataset-csv", type=Path, default=DEFAULT_DATASET_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--model-path", type=str, default="")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--subsample-size", type=int, default=DEFAULT_SUBSAMPLE_SIZE)
    parser.add_argument("--preview-rows", type=int, default=3)
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
        missing = set(OUTPUT_COLUMNS).difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
        rows = [dict(row) for row in reader]
    if len(rows) == 0:
        raise ValueError(f"Dataset CSV is empty: {path}")
    return rows


def parse_family_payload(row: dict[str, str]) -> dict[str, Any]:
    text = row.get("family_analysis_json", "")
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def solver_priority(row: dict[str, str]) -> int:
    solver = row.get("teacher_solver_candidate", "")
    priorities = {
        "roman_standard": 100,
        "gravity_numeric_rule": 100,
        "unit_numeric_rule": 100,
        "text_char_substitution": 95,
        "text_word_dictionary": 90,
        "binary_structured_byte_formula": 96,
        "binary_structured_byte_formula_abstract": 93,
        "binary_affine_xor": 92,
        "binary_two_bit_boolean": 91,
        "binary_three_bit_boolean": 89,
        "binary_byte_transform": 88,
        "binary_bit_permutation_bijection": 87,
        "binary_bit_permutation_independent": 85,
        "symbol_numeric_operator_formula": 72,
        "symbol_char_substitution": 68,
    }
    return priorities.get(solver, 50)


def structured_support_strength(row: dict[str, str]) -> int:
    safe_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    return max(safe_support * 10, abstract_support)


def rank_verified_row(row: dict[str, str]) -> tuple[Any, ...]:
    example_count = parse_int(row.get("num_examples", "0"), 0)
    same_operator = parse_int(row.get("symbol_same_operator_example_count", "0"), 0)
    hard_score = parse_float(row.get("hard_score", ""), 999.0)
    if hard_score is None:
        hard_score = 999.0
    return (
        -solver_priority(row),
        -example_count,
        -same_operator,
        -structured_support_strength(row),
        hard_score,
        row.get("id", ""),
    )


def rank_answer_only_row(row: dict[str, str]) -> tuple[Any, ...]:
    family = row.get("family", "")
    example_count = parse_int(row.get("num_examples", "0"), 0)
    hard_score = parse_float(row.get("hard_score", ""), 999.0)
    if hard_score is None:
        hard_score = 999.0
    if family == "bit_manipulation":
        return (
            -hard_score,
            -example_count,
            -structured_support_strength(row),
            -solver_priority(row),
            row.get("id", ""),
        )
    return (
        hard_score,
        -example_count,
        -solver_priority(row),
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
        raise ValueError(f"Unable to satisfy quota {quota}; only {available} rows available")
    return selected


def verified_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
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


def answer_only_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("selection_tier") == "answer_only_keep"]


def select_verified_mix(rows: list[dict[str, str]], seed: int) -> list[dict[str, str]]:
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        family = row.get("family", "")
        if family in VERIFIED_QUOTAS:
            by_family[family].append(row)
    selected: list[dict[str, str]] = []
    for index, family in enumerate(VERIFIED_QUOTAS):
        family_rows = by_family.get(family, [])
        quota = VERIFIED_QUOTAS[family]
        if len(family_rows) < quota:
            raise ValueError(f"Verified family {family} has only {len(family_rows)} rows; needs {quota}")
        family_selected = round_robin_select(
            make_selected(family_rows, rank_verified_row),
            quota=quota,
            seed=seed + index,
            key_fn=lambda item: item.row.get("template_subtype", "unknown"),
        )
        selected.extend(family_selected)
    return selected


def answer_only_group_key(row: dict[str, str]) -> str:
    family = row.get("family", "")
    if family == "bit_manipulation":
        return row.get("teacher_solver_candidate", "") or row.get("template_subtype", "unknown")
    if family == "symbol_equation":
        return row.get("symbol_query_operator", "") or row.get("template_subtype", "unknown")
    return row.get("template_subtype", "unknown")


def select_answer_only_mix(rows: list[dict[str, str]], used_ids: set[str], seed: int) -> list[dict[str, str]]:
    remaining = [row for row in rows if row.get("id", "") not in used_ids]
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in remaining:
        family = row.get("family", "")
        if family in ANSWER_ONLY_QUOTAS:
            by_family[family].append(row)
    selected: list[dict[str, str]] = []
    for index, family in enumerate(ANSWER_ONLY_QUOTAS):
        family_rows = by_family.get(family, [])
        quota = ANSWER_ONLY_QUOTAS[family]
        if len(family_rows) < quota:
            raise ValueError(f"Answer-only family {family} has only {len(family_rows)} rows; needs {quota}")
        family_selected = round_robin_select(
            make_selected(family_rows, rank_answer_only_row),
            quota=quota,
            seed=seed + 100 + index,
            key_fn=lambda item: answer_only_group_key(item.row),
        )
        selected.extend(family_selected)
    return selected


def humanize_rule_name(rule_name: str) -> str:
    return rule_name.replace("_", " ") if rule_name else "verified transformation"


def build_roman_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    query = row.get("query_raw", "").strip()
    value = parse_int(row.get("roman_query_value", payload.get("query_value", "0")), 0)
    return f"<think>The examples follow standard Roman numeral conversion. Converting {query} gives {value}, so the query evaluates to {row['answer']}.</think>"


def build_gravity_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    query = row.get("query_raw", "").strip()
    g_value = payload.get("median_g", row.get("estimated_g", ""))
    return (
        f"<think>The examples fit d = 0.5 * g * t^2 with g ≈ {g_value}. "
        f"Substituting t = {query} gives {row['answer']}.</think>"
    )


def build_unit_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    query = row.get("query_raw", "").strip()
    ratio = payload.get("median_ratio", row.get("estimated_ratio", ""))
    return (
        f"<think>The examples show a fixed conversion ratio of {ratio}. "
        f"Applying that ratio to {query} gives {row['answer']}.</think>"
    )


def build_text_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    solver = row.get("teacher_solver_candidate", "")
    if solver == "text_word_dictionary":
        return (
            f"<think>The examples define a consistent word-level substitution. "
            f"Applying the same dictionary to the query yields {row['answer']}.</think>"
        )
    unknown_chars = row.get("text_unknown_chars", "")
    if unknown_chars:
        return (
            f"<think>The examples define a consistent substitution cipher, and the query characters {unknown_chars} are already covered. "
            f"Applying that mapping yields {row['answer']}.</think>"
        )
    return (
        f"<think>The examples define a consistent character substitution. "
        f"Applying the same mapping to the query yields {row['answer']}.</think>"
    )


def bit_rule_description(row: dict[str, str], payload: dict[str, Any]) -> str:
    solver = row.get("teacher_solver_candidate", "")
    if solver in {"binary_structured_byte_formula", "binary_structured_byte_formula_abstract"}:
        detail = row.get("bit_structured_formula_name", "") or row.get("bit_structured_formula_abstract_family", "")
        if detail:
            return humanize_rule_name(detail)
    if solver == "binary_byte_transform":
        names = row.get("bit_byte_transform_names", "") or "byte transform"
        return humanize_rule_name(names.split("|")[0])
    if solver == "binary_affine_xor":
        return "an affine XOR relation over the byte"
    if solver == "binary_three_bit_boolean":
        return "a verified 3-bit boolean rule"
    if solver == "binary_two_bit_boolean":
        return "a verified 2-bit boolean rule"
    if solver == "binary_bit_permutation_bijection":
        return "a fixed bit permutation/inversion"
    if solver == "binary_bit_permutation_independent":
        return "an independent bit permutation/inversion"
    detail = payload.get("structured_formula_name", "")
    return humanize_rule_name(str(detail)) if detail else humanize_rule_name(solver)


def build_bit_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    description = bit_rule_description(row, payload)
    return (
        f"<think>The examples match the verified bit rule {description}. "
        "I apply the same transformation to the query byte and keep the result as one exact 8-bit binary string with leading zeros. "
        "I will present only that final byte in the box.</think>"
    )


def build_symbol_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    operator = row.get("symbol_query_operator", "") or str(payload.get("query_operator", "")).strip()
    formula = row.get("symbol_numeric_formula_name", "") or str(payload.get("formula_name", "")).strip()
    if formula:
        formula_text = humanize_rule_name(formula)
        return (
            f"<think>For operator {operator}, the examples fit the verified rule {formula_text}. "
            f"Applying that rule to the query gives {row['answer']}.</think>"
        )
    return (
        f"<think>The examples support one verified symbol transformation for operator {operator}. "
        f"Applying it to the query gives {row['answer']}.</think>"
    )


def build_verified_cot(row: dict[str, str]) -> str:
    payload = parse_family_payload(row)
    family = row.get("family", "")
    if family == "roman_numeral":
        return build_roman_trace(row, payload)
    if family == "gravity_constant":
        return build_gravity_trace(row, payload)
    if family == "unit_conversion":
        return build_unit_trace(row, payload)
    if family == "text_decryption":
        return build_text_trace(row, payload)
    if family == "bit_manipulation":
        return build_bit_trace(row, payload)
    if family == "symbol_equation":
        return build_symbol_trace(row, payload)
    raise ValueError(f"Unsupported family for trace generation: {family}")


def build_output_rows(selected_verified: list[dict[str, str]], selected_answer_only: list[dict[str, str]]) -> list[dict[str, str]]:
    output_rows: list[dict[str, str]] = []
    for row in selected_verified:
        output_rows.append(
            {
                "id": row["id"],
                "prompt": row["prompt"],
                "answer": row["answer"],
                "generated_cot": build_verified_cot(row),
                "label": FAMILY_LABELS[row["family"]],
                "assistant_style": "trace_boxed",
                "source_selection_tier": row["selection_tier"],
            }
        )
    for row in selected_answer_only:
        output_rows.append(
            {
                "id": row["id"],
                "prompt": row["prompt"],
                "answer": row["answer"],
                "generated_cot": "",
                "label": FAMILY_LABELS[row["family"]],
                "assistant_style": "boxed_only",
                "source_selection_tier": row["selection_tier"],
            }
        )
    return output_rows


def validate_output(rows: list[dict[str, str]], expected_size: int) -> None:
    if len(rows) != expected_size:
        raise ValueError(f"Expected {expected_size} rows, found {len(rows)}")
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate ids detected in output rows")
    for row in rows:
        if set(row) != set(OUTPUT_COLUMNS):
            raise ValueError(f"Unexpected output columns for row {row.get('id', '')}")
        if row["assistant_style"] == "trace_boxed":
            if not row["generated_cot"].startswith("<think>") or not row["generated_cot"].endswith("</think>"):
                raise ValueError(f"Trace rows must be wrapped by <think>: {row['id']}")
            if row["label"] == "binary" and row["answer"] in row["generated_cot"]:
                raise ValueError(f"Binary trace should not repeat the final answer outside the box: {row['id']}")
        elif row["assistant_style"] == "boxed_only":
            if row["generated_cot"]:
                raise ValueError(f"boxed_only rows must not carry generated_cot: {row['id']}")
        else:
            raise ValueError(f"Unsupported assistant_style: {row['assistant_style']}")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_manifest(
    *,
    source_rows: list[dict[str, str]],
    output_rows: list[dict[str, str]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    source_index = {row["id"]: row for row in source_rows}
    family_counts = Counter(source_index[row["id"]]["family"] for row in output_rows)
    source_tier_counts = Counter(row["source_selection_tier"] for row in output_rows)
    style_counts = Counter(row["assistant_style"] for row in output_rows)
    template_counts = Counter(source_index[row["id"]].get("template_subtype", "unknown") for row in output_rows)
    solver_counts = Counter(source_index[row["id"]].get("teacher_solver_candidate", "") for row in output_rows)
    binary_rows = [row for row in output_rows if row["label"] == "binary"]
    binary_trace_rows = [row for row in binary_rows if row["assistant_style"] == "trace_boxed"]
    binary_boxed_only_rows = [row for row in binary_rows if row["assistant_style"] == "boxed_only"]
    return {
        "source_csv": str(args.source_csv),
        "dataset_csv": str(args.dataset_csv),
        "manifest_json": str(args.manifest_json),
        "subsample_size": len(output_rows),
        "seed": args.seed,
        "verified_quotas": VERIFIED_QUOTAS,
        "answer_only_quotas": ANSWER_ONLY_QUOTAS,
        "family_counts": dict(sorted(family_counts.items())),
        "source_selection_tier_counts": dict(sorted(source_tier_counts.items())),
        "assistant_style_counts": dict(sorted(style_counts.items())),
        "template_subtype_counts": dict(sorted(template_counts.items())),
        "teacher_solver_counts": dict(sorted(solver_counts.items())),
        "training_plumbing": {
            "assistant_only_loss": True,
            "template_alignment_goal": "user prompt uses README-compatible boxed instruction and assistant-only labels mask user tokens",
            "boxed_instruction": BOXED_INSTRUCTION,
            "max_seq_len": MAX_SEQ_LEN,
            "epochs": NUM_EPOCHS,
            "learning_rate": LR,
            "lora_rank": LORA_RANK,
            "target_modules_default": "all-linear",
        },
        "binary_phase1_design": {
            "verified_binary_trace_rows": len(binary_trace_rows),
            "answer_only_binary_boxed_rows": len(binary_boxed_only_rows),
            "binary_answer_only_is_boxed_only": True,
            "binary_trace_avoids_repeating_final_answer_inside_think": True,
        },
        "notes": [
            "This Phase 1 dataset keeps the baseline structure but moves beyond the old 600-row verified-only mix.",
            "verified_trace_ready rows remain short trace teachers, while answer_only_keep rows are boxed-only to strengthen final answer closure without inventing reasoning.",
            "The companion training path uses assistant-only labels so user prompt tokens do not contribute to the loss.",
        ],
    }


def build_dataset(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source_rows = load_rows(args.source_csv)
    verified = verified_rows(source_rows)
    answer_only = answer_only_rows(source_rows)
    selected_verified = select_verified_mix(verified, seed=args.seed)
    used_ids = {row["id"] for row in selected_verified}
    selected_answer_only = select_answer_only_mix(answer_only, used_ids=used_ids, seed=args.seed)
    output_rows = build_output_rows(selected_verified, selected_answer_only)
    validate_output(output_rows, expected_size=args.subsample_size)
    manifest = build_manifest(source_rows=source_rows, output_rows=output_rows, args=args)
    write_csv(args.dataset_csv, output_rows, OUTPUT_COLUMNS)
    ensure_parent(args.manifest_json)
    args.manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_rows, manifest


def render_assistant_message(row: dict[str, str]) -> str:
    if row["assistant_style"] == "trace_boxed":
        return f"{row['generated_cot']}\n\n\\boxed{{{row['answer']}}}"
    if row["assistant_style"] == "boxed_only":
        return f"\\boxed{{{row['answer']}}}"
    raise ValueError(f"Unsupported assistant_style: {row['assistant_style']}")


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


def build_user_message(prompt: str) -> str:
    return prompt + "\n" + BOXED_INSTRUCTION


def render_training_pair(tokenizer: Any, row: dict[str, str]) -> tuple[str, str, str, str]:
    user_message = build_user_message(row["prompt"])
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


def tokenize_training_row(tokenizer: Any, row: dict[str, str]) -> dict[str, Any]:
    _, assistant_message, _, full_text = render_training_pair(tokenizer, row)
    assistant_char_start = full_text.find(assistant_message)
    if assistant_char_start < 0:
        raise ValueError(f"Assistant span not found in rendered chat for row {row['id']}")
    try:
        full_encoded = tokenizer(
            full_text,
            add_special_tokens=False,
            truncation=True,
            max_length=MAX_SEQ_LEN,
            return_offsets_mapping=True,
        )
    except (NotImplementedError, TypeError):
        full_encoded = tokenizer(
            full_text,
            add_special_tokens=False,
            truncation=True,
            max_length=MAX_SEQ_LEN,
        )
    input_ids = list(full_encoded["input_ids"])
    attention_mask = list(full_encoded["attention_mask"])
    offset_mapping = full_encoded.get("offset_mapping")
    assistant_token_start: int | None = None
    if offset_mapping:
        for index, (start, _end) in enumerate(offset_mapping):
            if start >= assistant_char_start:
                assistant_token_start = index
                break
    if assistant_token_start is None:
        prefix_text = full_text[:assistant_char_start]
        prefix_ids = tokenizer(
            prefix_text,
            add_special_tokens=False,
            truncation=True,
            max_length=MAX_SEQ_LEN,
        )["input_ids"]
        assistant_token_start = len(prefix_ids)
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
    print(f"Previewing {min(preview_count, len(rows))} rows from {len(rows)}-row Phase 1 dataset")
    for row in rows[:preview_count]:
        print("=" * 80)
        print(f"id={row['id']} label={row['label']} style={row['assistant_style']} tier={row['source_selection_tier']}")
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
    import inspect

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
    print("Starting Phase 1 training with assistant-only loss...")
    trainer.train()
    trainer.model.save_pretrained(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    print(f"Adapter saved to {args.output_dir}")


def main() -> None:
    args = parse_args()
    if args.subsample_size != DEFAULT_SUBSAMPLE_SIZE:
        raise ValueError(
            f"subsample-size must equal {DEFAULT_SUBSAMPLE_SIZE} for the current quota design; got {args.subsample_size}"
        )
    rows, manifest = build_dataset(args)
    print(f"Wrote Phase 1 dataset CSV: {args.dataset_csv}")
    print(f"Wrote Phase 1 manifest: {args.manifest_json}")
    print(json.dumps(manifest["family_counts"], ensure_ascii=False, sort_keys=True))
    print(json.dumps(manifest["assistant_style_counts"], ensure_ascii=False, sort_keys=True))

    if args.mode == "build-dataset":
        return
    if args.mode == "preview":
        preview_rows(rows, args.preview_rows)
        return
    train(args, rows)


if __name__ == "__main__":
    main()
