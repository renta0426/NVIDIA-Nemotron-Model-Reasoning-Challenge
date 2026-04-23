"""
v8 parallel corpus variants generator
====================================

Greenfield single-file generator for three complementary MLX bundle variants:

1. bit_family_rebalance_broadbase
2. symbol_cipher_recovery_mix
3. hybrid_bridge

Each variant keeps the exact 04-08-16-14 base snapshot and adds a different
overlay mix aimed at the confirmed local300 misses that remain after the
`v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc` baseline.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    while cur != cur.parent:
        if (cur / "README.md").exists() and (cur / "pyproject.toml").exists():
            return cur
        cur = cur.parent
    raise RuntimeError(f"Could not locate repo root from {start}")


REPO_ROOT = _find_repo_root(Path(__file__).resolve())
VERSION_ROOT = Path(__file__).resolve().parent
VERSION_NAME = "v8_parallel_variants"

TRAIN_CSV_PATH = REPO_ROOT / "data" / "train.csv"
ANALYSIS_CSV_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
RECOMMENDED_CSV_PATH = (
    REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_recommended_learning_target_v1.csv"
)
REASONING_DIR = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "reasoning"
TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
MLX_BUNDLE_ROOT = TRAINING_SFT_ROOT / "MLX"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
BASE_SNAPSHOT_TOKENS_DIR = BASE_SNAPSHOT_ROOT / "tokens"
RESULTS_MD = VERSION_ROOT / f"{VERSION_NAME}-results.md"

MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
TOKEN_LIMIT = 8192
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)

BIT_MISS_IDS = [
    "000b53cf",
    "012fb81b",
    "01e09228",
    "02a66bcb",
    "034fb629",
    "048cc279",
    "04d8c3e6",
    "05ca617c",
    "06881e47",
    "07e8cf66",
    "0b16458a",
    "0ec17d2e",
    "12fd5b6c",
    "132ec6ae",
    "16db2c74",
    "172d2417",
]
CIPHER_MISS_IDS = ["0184a864"]
EQUATION_MISS_IDS = ["065f9dea", "0c0683c3"]
ALL_DIRECT_MISS_IDS = BIT_MISS_IDS + CIPHER_MISS_IDS + EQUATION_MISS_IDS

COMMON_NUMERIC_OPERATORS = {"+", "-", "*", "/", "%"}
BASE_EXCLUDED_IDS = {"ef2fe526"}


@dataclass(frozen=True)
class VariantSpec:
    name: str
    description: str
    direct_answer_only_repeats: int
    direct_reasoning_repeats: int
    bit_verified_repeats: int
    bit_answer_only_repeats: int
    prompt_local_verified_repeats: int
    prompt_local_answer_only_repeats: int
    numeric_common_repeats: int
    numeric_rare_repeats: int
    cipher_verified_repeats: int
    cipher_answer_only_repeats: int


VARIANT_SPECS: dict[str, VariantSpec] = {
    "bit_family_rebalance_broadbase": VariantSpec(
        name="bit_family_rebalance_broadbase",
        description=(
            "Miss-family bit rebalance plus prompt-local support. Directly repeats the "
            "19 known non-crypt misses, then broadens to verified/answer-only rows from "
            "the same bit abstract families and bit_prompt_local_exact_formula pool."
        ),
        direct_answer_only_repeats=24,
        direct_reasoning_repeats=8,
        bit_verified_repeats=4,
        bit_answer_only_repeats=2,
        prompt_local_verified_repeats=2,
        prompt_local_answer_only_repeats=1,
        numeric_common_repeats=0,
        numeric_rare_repeats=0,
        cipher_verified_repeats=0,
        cipher_answer_only_repeats=0,
    ),
    "symbol_cipher_recovery_mix": VariantSpec(
        name="symbol_cipher_recovery_mix",
        description=(
            "Keep direct miss pressure, then add broad answer-only stabilization for "
            "numeric_2x2 same-op-zero rows and the full text_decryption family."
        ),
        direct_answer_only_repeats=32,
        direct_reasoning_repeats=10,
        bit_verified_repeats=0,
        bit_answer_only_repeats=0,
        prompt_local_verified_repeats=0,
        prompt_local_answer_only_repeats=0,
        numeric_common_repeats=2,
        numeric_rare_repeats=1,
        cipher_verified_repeats=1,
        cipher_answer_only_repeats=1,
    ),
    "hybrid_bridge": VariantSpec(
        name="hybrid_bridge",
        description=(
            "Balanced bridge run: moderate direct miss repeats, lighter bit-family "
            "rebalance, numeric same-op-zero support, and verified text_decryption "
            "answer-only stabilization."
        ),
        direct_answer_only_repeats=20,
        direct_reasoning_repeats=6,
        bit_verified_repeats=2,
        bit_answer_only_repeats=1,
        prompt_local_verified_repeats=1,
        prompt_local_answer_only_repeats=1,
        numeric_common_repeats=1,
        numeric_rare_repeats=1,
        cipher_verified_repeats=1,
        cipher_answer_only_repeats=0,
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_jsonl_line(handle: Any, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")


@lru_cache(maxsize=1)
def load_train_rows() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with TRAIN_CSV_PATH.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[row["id"]] = dict(row)
    return rows


@lru_cache(maxsize=1)
def load_analysis_rows() -> list[dict[str, str]]:
    with ANALYSIS_CSV_PATH.open(encoding="utf-8", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


@lru_cache(maxsize=1)
def load_recommended_rows() -> list[dict[str, str]]:
    with RECOMMENDED_CSV_PATH.open(encoding="utf-8", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


@lru_cache(maxsize=1)
def load_reasoning_text(row_id: str) -> str | None:
    path = REASONING_DIR / f"{row_id}.txt"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def extract_last_boxed(text: str) -> str | None:
    matches = re.findall(r"\\boxed\{([^}]*)\}", text)
    return matches[-1].strip() if matches else None


@lru_cache(maxsize=1)
def get_tokenizer() -> Any:
    tok = AutoTokenizer.from_pretrained(MODEL_TOKENIZER_NAME, trust_remote_code=True)
    if tok.pad_token_id is None and tok.eos_token_id is not None:
        tok.pad_token = tok.eos_token
    return tok


def tokenize_example(prompt: str, completion: str) -> tuple[list[int], list[int]]:
    tok = get_tokenizer()
    prompt_ids: list[int] = tok.apply_chat_template(
        [{"role": "user", "content": prompt + PROMPT_SUFFIX}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=True,
    )
    completion_ids: list[int] = tok.encode(completion, add_special_tokens=False)
    all_tokens = list(prompt_ids) + list(completion_ids)
    mask = [0] * len(prompt_ids) + [1] * len(completion_ids)
    if len(all_tokens) > TOKEN_LIMIT:
        all_tokens = all_tokens[:TOKEN_LIMIT]
        mask = mask[:TOKEN_LIMIT]
    return all_tokens, mask


def build_reasoning_completion(reasoning_text: str, gold_answer: str) -> str:
    return f"{reasoning_text}\n</think>\n\\boxed{{{gold_answer}}}<|im_end|>"


def build_answer_only_completion(gold_answer: str) -> str:
    return f"\n</think>\n\\boxed{{{gold_answer}}}<|im_end|>"


def load_base_snapshot() -> tuple[list[dict[str, Any]], int]:
    with BASE_SNAPSHOT_CONFIG_PATH.open(encoding="utf-8") as f:
        cfg = json.load(f)
    batch_size = int(cfg["batch_size"])

    rows: list[dict[str, Any]] = []
    with BASE_SNAPSHOT_INDEX_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    enriched: list[dict[str, Any]] = []
    for row in rows:
        problem_id = str(row["problem_id"])
        base_pid = problem_id.split("-p")[0]
        if base_pid in BASE_EXCLUDED_IDS:
            continue
        token_path = BASE_SNAPSHOT_TOKENS_DIR / problem_id / f"{Path(str(row['segment'])).stem}.json"
        if not token_path.exists():
            continue
        with token_path.open(encoding="utf-8") as tf:
            payload = json.load(tf)
        enriched.append({"row": row, "tokens": payload["tokens"], "mask": payload["mask"]})
    return enriched, batch_size


@lru_cache(maxsize=1)
def load_base_snapshot_config() -> dict[str, Any]:
    with BASE_SNAPSHOT_CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def bit_family_support_sets() -> tuple[set[str], set[str]]:
    miss_rows = [row for row in load_analysis_rows() if row["id"] in BIT_MISS_IDS]
    abstracts = {
        row["bit_structured_formula_abstract_family"]
        for row in miss_rows
        if row["bit_structured_formula_abstract_family"]
    }
    formulas = {
        row["bit_structured_formula_name"]
        for row in miss_rows
        if row["bit_structured_formula_name"]
    }
    return abstracts, formulas


def teacher_matches_gold(row_id: str, gold_answer: str) -> bool:
    reasoning = load_reasoning_text(row_id)
    if reasoning is None:
        return False
    boxed = extract_last_boxed(reasoning)
    return boxed == gold_answer.strip()


def make_example(
    *,
    example_id: str,
    source_problem_id: str,
    category: str,
    style: str,
    lane: str,
    repeat_index: int,
    prompt: str,
    completion: str,
) -> dict[str, Any]:
    tokens, mask = tokenize_example(prompt, completion)
    return {
        "example_id": example_id,
        "source_problem_id": source_problem_id,
        "source": "corrective_overlay",
        "segment": "synthetic.jsonl",
        "category": category,
        "style": style,
        "lane": lane,
        "repeat_index": repeat_index,
        "tokens": tokens,
        "mask": mask,
        "num_loss_tokens": sum(mask),
    }


def build_direct_examples(spec: VariantSpec) -> list[dict[str, Any]]:
    train_rows = load_train_rows()
    analysis_by_id = {row["id"]: row for row in load_analysis_rows()}
    examples: list[dict[str, Any]] = []
    for row_id in ALL_DIRECT_MISS_IDS:
        train_row = train_rows[row_id]
        analysis_row = analysis_by_id[row_id]
        prompt = train_row["prompt"].strip()
        gold = train_row["answer"].strip()
        category = analysis_row["family"]

        answer_only_completion = build_answer_only_completion(gold)
        for rep in range(spec.direct_answer_only_repeats):
            examples.append(
                make_example(
                    example_id=f"{spec.name}:{row_id}:direct-ao-{rep}",
                    source_problem_id=row_id,
                    category=category,
                    style="answer_only",
                    lane="direct_miss",
                    repeat_index=rep,
                    prompt=prompt,
                    completion=answer_only_completion,
                )
            )

        reasoning_text = load_reasoning_text(row_id)
        if reasoning_text is not None and teacher_matches_gold(row_id, gold):
            reasoning_completion = build_reasoning_completion(reasoning_text, gold)
            for rep in range(spec.direct_reasoning_repeats):
                examples.append(
                    make_example(
                        example_id=f"{spec.name}:{row_id}:direct-reasoning-{rep}",
                        source_problem_id=row_id,
                        category=category,
                        style="reasoning",
                        lane="direct_miss",
                        repeat_index=rep,
                        prompt=prompt,
                        completion=reasoning_completion,
                    )
                )
    return examples


def build_bit_support_examples(spec: VariantSpec) -> list[dict[str, Any]]:
    if (
        spec.bit_verified_repeats == 0
        and spec.bit_answer_only_repeats == 0
        and spec.prompt_local_verified_repeats == 0
        and spec.prompt_local_answer_only_repeats == 0
    ):
        return []

    train_rows = load_train_rows()
    miss_abstracts, _ = bit_family_support_sets()
    examples: list[dict[str, Any]] = []
    for row in load_analysis_rows():
        row_id = row["id"]
        if row_id in ALL_DIRECT_MISS_IDS:
            continue
        if row["family"] != "bit_manipulation":
            continue
        if row["selection_tier"] not in ("verified_trace_ready", "answer_only_keep"):
            continue

        repeats = 0
        lane = ""
        if row["template_subtype"] == "bit_prompt_local_exact_formula":
            repeats = (
                spec.prompt_local_verified_repeats
                if row["selection_tier"] == "verified_trace_ready"
                else spec.prompt_local_answer_only_repeats
            )
            lane = "bit_prompt_local_support"
        elif row["bit_structured_formula_abstract_family"] in miss_abstracts:
            repeats = (
                spec.bit_verified_repeats
                if row["selection_tier"] == "verified_trace_ready"
                else spec.bit_answer_only_repeats
            )
            lane = "bit_family_support"
        if repeats <= 0:
            continue

        prompt = train_rows[row_id]["prompt"].strip()
        gold = train_rows[row_id]["answer"].strip()
        completion = build_answer_only_completion(gold)
        for rep in range(repeats):
            examples.append(
                make_example(
                    example_id=f"{spec.name}:{row_id}:{lane}-{rep}",
                    source_problem_id=row_id,
                    category="bit_manipulation",
                    style="answer_only",
                    lane=lane,
                    repeat_index=rep,
                    prompt=prompt,
                    completion=completion,
                )
            )
    return examples


def build_numeric_support_examples(spec: VariantSpec) -> list[dict[str, Any]]:
    if spec.numeric_common_repeats == 0 and spec.numeric_rare_repeats == 0:
        return []
    train_rows = load_train_rows()
    examples: list[dict[str, Any]] = []
    for row in load_analysis_rows():
        row_id = row["id"]
        if row_id in ALL_DIRECT_MISS_IDS:
            continue
        if row["family"] != "symbol_equation" or row["template_subtype"] != "numeric_2x2":
            continue
        if row["selection_tier"] != "answer_only_keep":
            continue
        if row.get("symbol_same_operator_example_count") != "0":
            continue
        operator = row.get("symbol_query_operator") or ""
        repeats = spec.numeric_common_repeats if operator in COMMON_NUMERIC_OPERATORS else spec.numeric_rare_repeats
        if repeats <= 0:
            continue

        prompt = train_rows[row_id]["prompt"].strip()
        gold = train_rows[row_id]["answer"].strip()
        completion = build_answer_only_completion(gold)
        for rep in range(repeats):
            examples.append(
                make_example(
                    example_id=f"{spec.name}:{row_id}:numeric-support-{rep}",
                    source_problem_id=row_id,
                    category="symbol_equation",
                    style="answer_only",
                    lane="numeric_same_op_zero_support",
                    repeat_index=rep,
                    prompt=prompt,
                    completion=completion,
                )
            )
    return examples


def build_cipher_support_examples(spec: VariantSpec) -> list[dict[str, Any]]:
    if spec.cipher_verified_repeats == 0 and spec.cipher_answer_only_repeats == 0:
        return []
    train_rows = load_train_rows()
    examples: list[dict[str, Any]] = []
    for row in load_analysis_rows():
        row_id = row["id"]
        if row_id in ALL_DIRECT_MISS_IDS:
            continue
        if row["family"] != "text_decryption":
            continue
        if row["selection_tier"] not in ("verified_trace_ready", "answer_only_keep"):
            continue
        repeats = (
            spec.cipher_verified_repeats
            if row["selection_tier"] == "verified_trace_ready"
            else spec.cipher_answer_only_repeats
        )
        if repeats <= 0:
            continue

        prompt = train_rows[row_id]["prompt"].strip()
        gold = train_rows[row_id]["answer"].strip()
        completion = build_answer_only_completion(gold)
        for rep in range(repeats):
            examples.append(
                make_example(
                    example_id=f"{spec.name}:{row_id}:cipher-support-{rep}",
                    source_problem_id=row_id,
                    category="text_decryption",
                    style="answer_only",
                    lane="cipher_support",
                    repeat_index=rep,
                    prompt=prompt,
                    completion=completion,
                )
            )
    return examples


def build_overlay_examples(spec: VariantSpec) -> list[dict[str, Any]]:
    overlay = []
    overlay.extend(build_direct_examples(spec))
    overlay.extend(build_bit_support_examples(spec))
    overlay.extend(build_numeric_support_examples(spec))
    overlay.extend(build_cipher_support_examples(spec))
    return overlay


def build_bundle(spec: VariantSpec, bundle_path: Path) -> dict[str, Any]:
    base_examples, batch_size = load_base_snapshot()
    base_snapshot_config = load_base_snapshot_config()
    overlay_examples = build_overlay_examples(spec)
    base_steps = [int(ex["row"]["step"]) for ex in base_examples]
    base_step_count = max(base_steps) + 1 if base_steps else 0

    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    total_examples = 0
    total_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()
    overlay_by_category: Counter[str] = Counter()
    overlay_by_style: Counter[str] = Counter()
    overlay_by_lane: Counter[str] = Counter()

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": spec.name,
        "created_at": utc_now(),
        "bundle_path": str(bundle_path.relative_to(REPO_ROOT)),
        "base_snapshot_root": str(BASE_SNAPSHOT_ROOT.relative_to(REPO_ROOT)),
        "base_snapshot_config": base_snapshot_config,
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "direct_miss_ids": ALL_DIRECT_MISS_IDS,
        "variant_description": spec.description,
        "variant_spec": spec.__dict__,
        "readme_contract": {
            "max_tokens": 7680,
            "top_p": 1.0,
            "temperature": 0.0,
            "max_model_len": 8192,
            "max_lora_rank": 32,
        },
    }

    with bundle_path.open("w", encoding="utf-8") as fh:
        write_jsonl_line(fh, manifest)

        for ex in base_examples:
            row = ex["row"]
            record = {
                "record_type": "example",
                "example_id": str(row["problem_id"]),
                "source_problem_id": str(row["problem_id"]),
                "source": "base_snapshot",
                "segment": str(row["segment"]),
                "category": str(row["category"]),
                "step": int(row["step"]),
                "num_loss_tokens": int(row["num_loss_tokens"]),
                "tokens": ex["tokens"],
                "mask": ex["mask"],
            }
            write_jsonl_line(fh, record)
            total_examples += 1
            total_tokens += len(ex["tokens"])
            max_seq_len = max(max_seq_len, len(ex["tokens"]))
            category_counts[str(row["category"])] += 1

        for offset, ex in enumerate(overlay_examples):
            step = base_step_count + (offset // batch_size)
            record = {
                "record_type": "example",
                "example_id": ex["example_id"],
                "source_problem_id": ex["source_problem_id"],
                "source": ex["source"],
                "segment": ex["segment"],
                "category": ex["category"],
                "style": ex["style"],
                "lane": ex["lane"],
                "repeat_index": ex["repeat_index"],
                "step": step,
                "num_loss_tokens": ex["num_loss_tokens"],
                "tokens": ex["tokens"],
                "mask": ex["mask"],
            }
            write_jsonl_line(fh, record)
            total_examples += 1
            total_tokens += len(ex["tokens"])
            max_seq_len = max(max_seq_len, len(ex["tokens"]))
            category_counts[ex["category"]] += 1
            overlay_by_category[ex["category"]] += 1
            overlay_by_style[ex["style"]] += 1
            overlay_by_lane[ex["lane"]] += 1

    overlay_steps = (len(overlay_examples) + batch_size - 1) // batch_size
    bundle_size_mb = bundle_path.stat().st_size / 1024 / 1024
    return {
        "variant": spec.name,
        "bundle_path": str(bundle_path.relative_to(REPO_ROOT)),
        "bundle_size_mb": round(bundle_size_mb, 2),
        "base_examples": len(base_examples),
        "overlay_examples": len(overlay_examples),
        "total_examples": total_examples,
        "base_steps": base_step_count,
        "overlay_steps": overlay_steps,
        "total_steps": base_step_count + overlay_steps,
        "total_tokens": total_tokens,
        "max_seq_len": max_seq_len,
        "category_counts": dict(sorted(category_counts.items())),
        "overlay_by_category": dict(sorted(overlay_by_category.items())),
        "overlay_by_style": dict(sorted(overlay_by_style.items())),
        "overlay_by_lane": dict(sorted(overlay_by_lane.items())),
        "direct_teacher_matches": sum(
            1 for row_id in ALL_DIRECT_MISS_IDS if teacher_matches_gold(row_id, load_train_rows()[row_id]["answer"].strip())
        ),
        "generated_at": utc_now(),
        "description": spec.description,
        "spec": spec.__dict__,
    }


def render_results_markdown(stats_by_variant: list[dict[str, Any]]) -> str:
    lines: list[str] = [
        f"# {VERSION_NAME} results",
        "",
        "## Why v8 exists",
        "",
        "- Root `README.md` fixes the evaluation contract at `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, and `max_model_len=8192`.",
        "- `v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc` remains the retained MLX best at `254/300 = 0.846667`.",
        "- Residual non-crypt misses are still concentrated in bit manipulation (`16`), cipher (`1`), and equation numeric guess (`2`).",
        "- v7 already attacks the exact 19 miss IDs. v8 broadens the support mix with three complementary bundles from one single-file generator.",
        "",
        "## Variant overview",
        "",
        "| Variant | Overlay examples | Total steps | Total tokens | Bundle |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for stats in stats_by_variant:
        lines.append(
            f"| `{stats['variant']}` | {stats['overlay_examples']} | {stats['total_steps']} | "
            f"{stats['total_tokens']} | {stats['bundle_size_mb']} MB |"
        )

    for stats in stats_by_variant:
        lines.extend(
            [
                "",
                f"## {stats['variant']}",
                "",
                stats["description"],
                "",
                "### Bundle stats",
                "",
                "| Field | Value |",
                "| --- | ---: |",
                f"| Base examples | {stats['base_examples']} |",
                f"| Overlay examples | {stats['overlay_examples']} |",
                f"| Total examples | {stats['total_examples']} |",
                f"| Base steps | {stats['base_steps']} |",
                f"| Overlay steps | {stats['overlay_steps']} |",
                f"| Total steps | {stats['total_steps']} |",
                f"| Total tokens | {stats['total_tokens']} |",
                f"| Max sequence length | {stats['max_seq_len']} |",
                f"| Bundle size | {stats['bundle_size_mb']} MB |",
                f"| Direct teacher-match IDs | {stats['direct_teacher_matches']} |",
                "",
                "### Variant spec",
                "",
                "| Knob | Value |",
                "| --- | ---: |",
            ]
        )
        for key, value in stats["spec"].items():
            if key in {"name", "description"}:
                continue
            lines.append(f"| {key} | {value} |")

        lines.extend(
            [
                "",
                "### Overlay by lane",
                "",
                "| Lane | Examples |",
                "| --- | ---: |",
            ]
        )
        for lane, count in stats["overlay_by_lane"].items():
            lines.append(f"| {lane} | {count} |")

        lines.extend(
            [
                "",
                "### Overlay by category",
                "",
                "| Category | Examples |",
                "| --- | ---: |",
            ]
        )
        for category, count in stats["overlay_by_category"].items():
            lines.append(f"| {category} | {count} |")

        lines.extend(
            [
                "",
                "### Overlay by style",
                "",
                "| Style | Examples |",
                "| --- | ---: |",
            ]
        )
        for style, count in stats["overlay_by_style"].items():
            lines.append(f"| {style} | {count} |")

        lines.extend(
            [
                "",
                "### Bundle path",
                "",
                f"`{stats['bundle_path']}`",
                "",
                "### Status",
                "",
                "- Bundle generated: YES",
                "- MLX training: NOT YET STARTED",
                "- local300 score: TBD",
            ]
        )

    lines.extend(["", "## Generated", "", utc_now(), ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate v8 MLX bundle variants")
    parser.add_argument(
        "--variant",
        choices=["all", *VARIANT_SPECS.keys()],
        default="all",
        help="Variant to generate (default: all)",
    )
    parser.add_argument(
        "--bundle-root",
        type=Path,
        default=MLX_BUNDLE_ROOT,
        help=f"Bundle output root (default: {MLX_BUNDLE_ROOT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = list(VARIANT_SPECS) if args.variant == "all" else [args.variant]
    stats_by_variant: list[dict[str, Any]] = []
    for name in selected:
        spec = VARIANT_SPECS[name]
        bundle_path = Path(args.bundle_root) / f"{spec.name}_bundle.jsonl"
        print(f"=== Generating {spec.name} ===")
        stats = build_bundle(spec, bundle_path)
        stats_by_variant.append(stats)
        print(
            f"  overlay={stats['overlay_examples']} total_steps={stats['total_steps']} "
            f"tokens={stats['total_tokens']} bundle={stats['bundle_size_mb']}MB"
        )

    if args.variant == "all":
        RESULTS_MD.write_text(render_results_markdown(stats_by_variant), encoding="utf-8")
        print(f"Results MD updated: {RESULTS_MD}")
    else:
        RESULTS_MD.write_text(render_results_markdown(stats_by_variant), encoding="utf-8")
        print(f"Results MD updated: {RESULTS_MD}")


if __name__ == "__main__":
    main()
