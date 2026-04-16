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


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / "README.md").exists() and (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError(f"Could not locate repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__).resolve())
VERSION_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = VERSION_ROOT / "outputs"
RESULTS_MD = VERSION_ROOT / "v20_corrective_corpus_v3-results.md"

README_PATH = REPO_ROOT / "README.md"
TRAIN_RECOMMENDED_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_recommended_learning_target_v1.csv"
TRAIN_CSV_PATH = REPO_ROOT / "data" / "train.csv"
PROBLEMS_PATH = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "problems.jsonl"
REASONING_DIR = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "reasoning"
TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
DEFAULT_BUNDLE_PATH = TRAINING_SFT_ROOT / "v20_corrective_corpus_v3_bundle.jsonl"

CURRENT_MLX_RUN_ROOT = (
    REPO_ROOT / "v20_mlx_repro_v1" / "outputs" / "v20_mlx_repro_v1_fullrun_targetfix_mb1"
)
CURRENT_VALIDATION_CSV_PATH = CURRENT_MLX_RUN_ROOT / "adapter_validation" / "validation.csv"
CURRENT_VALIDATION_SUMMARY_PATH = CURRENT_MLX_RUN_ROOT / "adapter_validation" / "validation_summary.json"
CURRENT_RESULTS_MD_PATH = REPO_ROOT / "v20_mlx_repro_v1" / "v20_mlx_repro_v1-results.md"
PREVIOUS_V2_SELECTION_PATH = (
    REPO_ROOT
    / "versions"
    / "v20_corrective_corpus_v2"
    / "outputs"
    / "smoke_bundle_v2"
    / "artifacts"
    / "corrective_selection.csv"
)

MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)
TOKEN_LIMIT = 8192

README_EVAL_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}

BUCKET_ORDER = (
    "current_symbol_glyph_failures",
    "current_symbol_numeric_failures",
    "current_bit_failures",
    "current_cipher_failures",
    "symbol_numeric_support",
    "symbol_glyph_support",
    "bit_formula_support",
)

DEFAULT_BUCKET_LIMITS = {
    "current_symbol_glyph_failures": 32,
    "current_symbol_numeric_failures": 16,
    "current_bit_failures": 24,
    "current_cipher_failures": 4,
    "symbol_numeric_support": 24,
    "symbol_glyph_support": 32,
    "bit_formula_support": 24,
}

DEFAULT_REPEAT_COUNTS = {
    "current_symbol_glyph_failures": 3,
    "current_symbol_numeric_failures": 4,
    "current_bit_failures": 2,
    "current_cipher_failures": 1,
    "symbol_numeric_support": 2,
    "symbol_glyph_support": 2,
    "bit_formula_support": 1,
}

SUBTYPE_TO_SUPPORT_BUCKET = {
    "numeric_2x2": "symbol_numeric_support",
    "glyph_len5": "symbol_glyph_support",
    "bit_structured_byte_formula": "bit_formula_support",
    "bit_prompt_local_exact_formula": "bit_formula_support",
    "bit_other": "bit_formula_support",
}

SUBTYPE_PRIORITY = {
    "bit_structured_byte_formula": 3,
    "bit_prompt_local_exact_formula": 2,
    "bit_other": 1,
}

SELECTION_TIER_PRIORITY = {
    "verified_trace_ready": 2,
    "answer_only_keep": 1,
}


@dataclass
class Candidate:
    row: dict[str, str]
    bucket: str
    source_tags: tuple[str, ...]
    current_failure: bool
    current_validation_category: str | None
    current_validation_minlogprob: float | None
    base_snapshot_min_logprob: float | None
    priority_key: tuple[Any, ...]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"Missing CSV header: {path}")
        return [dict(row) for row in reader]


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def relative_to_repo(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_float(value: Any, default: float = 0.0) -> float:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def verify_readme_eval_contract() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    contract: dict[str, Any] = {}
    for key, expected in README_EVAL_CONTRACT.items():
        needle = f"{key}\t"
        matched = False
        for line in text.splitlines():
            if not line.startswith(needle):
                continue
            raw = line.split("\t", 1)[1].strip()
            if isinstance(expected, int) and not isinstance(expected, bool):
                contract[key] = int(raw)
            elif isinstance(expected, float):
                contract[key] = float(raw)
            else:
                contract[key] = raw
            matched = True
            break
        if not matched:
            raise SystemExit(f"Missing README.md evaluation row for {key}")
        if contract[key] != expected:
            raise SystemExit(
                f"README.md evaluation mismatch for {key}: expected {expected}, got {contract[key]}"
            )
    return contract


def load_train_prompts() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for row in load_csv_rows(TRAIN_CSV_PATH):
        rows[row["id"]] = row
    return rows


def load_problem_categories() -> dict[str, str]:
    categories: dict[str, str] = {}
    for row in load_jsonl_rows(PROBLEMS_PATH):
        categories[str(row["id"])] = str(row["category"])
    return categories


def fill_metadata_defaults(row: dict[str, str] | None) -> dict[str, str]:
    merged = dict(row or {})
    merged.setdefault("selection_tier", "")
    merged.setdefault("template_subtype", "")
    merged.setdefault("teacher_solver_candidate", "")
    merged.setdefault("hard_score", "")
    merged.setdefault("audit_reasons", "")
    merged.setdefault("analysis_notes", "")
    merged.setdefault("symbol_query_operator", "")
    merged.setdefault("bit_structured_formula_name", "")
    merged.setdefault("bit_structured_formula_prediction", "")
    merged.setdefault("bit_structured_formula_abstract_family", "")
    merged.setdefault("verified_trace_ready", "")
    merged.setdefault("answer_only_ready", "")
    merged.setdefault("num_examples", "")
    merged.setdefault("prompt_len_chars", "")
    return merged


def load_train_metadata_map() -> dict[str, dict[str, str]]:
    return {row["id"]: fill_metadata_defaults(row) for row in load_csv_rows(TRAIN_RECOMMENDED_PATH)}


def build_completion_text(reasoning_text: str, answer: str) -> str:
    boxed_match = re.findall(r"\\boxed\{([^}]*)\}", reasoning_text)
    reasoning_answer = boxed_match[-1] if boxed_match else answer
    return f"{reasoning_text}\n</think>\n\\boxed{{{reasoning_answer}}}<|im_end|>"


@lru_cache(maxsize=1)
def get_chat_tokenizer() -> Any:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_TOKENIZER_NAME, trust_remote_code=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def tokenize_overlay_example(prompt: str, completion_text: str) -> tuple[list[int], list[int]]:
    chat_tokenizer = get_chat_tokenizer()
    prompt_ids = chat_tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt + PROMPT_SUFFIX}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=True,
    )
    completion_ids = chat_tokenizer.encode(completion_text, add_special_tokens=False)
    all_tokens = list(prompt_ids) + list(completion_ids)
    mask = [0] * len(prompt_ids) + [1] * len(completion_ids)
    if len(all_tokens) > TOKEN_LIMIT:
        all_tokens = all_tokens[:TOKEN_LIMIT]
        mask = mask[:TOKEN_LIMIT]
    return all_tokens, mask


def load_base_snapshot_index_rows() -> list[dict[str, Any]]:
    if not BASE_SNAPSHOT_INDEX_PATH.exists():
        raise SystemExit(f"Missing base snapshot index: {BASE_SNAPSHOT_INDEX_PATH}")
    return load_jsonl_rows(BASE_SNAPSHOT_INDEX_PATH)


def load_base_snapshot_index_map() -> dict[str, dict[str, Any]]:
    return {str(row["problem_id"]): row for row in load_base_snapshot_index_rows()}


def load_base_snapshot_examples() -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]], int]:
    config = read_json(BASE_SNAPSHOT_CONFIG_PATH)
    batch_size = int(config["batch_size"])
    base_rows = load_base_snapshot_index_rows()
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in base_rows:
        problem_id = str(row["problem_id"])
        segment = str(row["segment"])
        token_path = BASE_SNAPSHOT_ROOT / "tokens" / problem_id / f"{Path(segment).stem}.json"
        if not token_path.exists():
            raise SystemExit(f"Missing base token snapshot: {token_path}")
        payload = read_json(token_path)
        tokens = payload["tokens"]
        mask = payload["mask"]
        num_loss_tokens = int(row["num_loss_tokens"])
        if sum(mask) != num_loss_tokens:
            raise SystemExit(
                f"num_loss_tokens mismatch for base snapshot {problem_id}: {sum(mask)} != {num_loss_tokens}"
            )
        by_key[(problem_id, segment)] = {
            "row": row,
            "tokens": tokens,
            "mask": mask,
        }
    return base_rows, by_key, batch_size


def load_previous_v2_selection_ids() -> set[str]:
    if not PREVIOUS_V2_SELECTION_PATH.exists():
        return set()
    return {row["id"] for row in load_csv_rows(PREVIOUS_V2_SELECTION_PATH)}


def load_current_validation_profile(
    validation_csv: Path,
    validation_summary_json: Path | None,
) -> dict[str, Any]:
    rows = load_csv_rows(validation_csv)
    wrong_rows = [dict(row) for row in rows if row.get("correct") == "False"]
    correct = sum(1 for row in rows if row.get("correct") == "True")
    summary_payload = None
    if validation_summary_json is not None and validation_summary_json.exists():
        summary_payload = read_json(validation_summary_json)
    overall = summary_payload.get("overall") if summary_payload else None
    return {
        "rows": rows,
        "wrong_rows": wrong_rows,
        "wrong_ids": {row["id"] for row in wrong_rows},
        "wrong_by_category": Counter(row["category"] for row in wrong_rows),
        "correct": int(overall["correct"]) if overall else correct,
        "total": int(overall["total"]) if overall else len(rows),
        "accuracy": float(overall["accuracy"]) if overall else (correct / len(rows) if rows else 0.0),
        "summary_payload": summary_payload,
    }


def failure_bucket_for_row(validation_row: dict[str, str], metadata_row: dict[str, str] | None) -> str | None:
    category = str(validation_row.get("category", "")).strip()
    metadata = fill_metadata_defaults(metadata_row)
    subtype = str(metadata.get("template_subtype", "")).strip()
    if category == "bit_manipulation":
        return "current_bit_failures"
    if category == "cipher":
        return "current_cipher_failures"
    if subtype == "numeric_2x2" or category.startswith("equation_numeric"):
        return "current_symbol_numeric_failures"
    if subtype == "glyph_len5" or category.startswith("cryptarithm"):
        return "current_symbol_glyph_failures"
    return None


def support_bucket_for_metadata(metadata_row: dict[str, str]) -> str | None:
    subtype = str(metadata_row.get("template_subtype", "")).strip()
    return SUBTYPE_TO_SUPPORT_BUCKET.get(subtype)


def make_candidate(
    *,
    row_id: str,
    bucket: str,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    metadata_row: dict[str, str] | None,
    source_tags: set[str],
    current_failure: bool,
    current_validation_category: str | None,
    current_validation_prediction: str | None,
    current_validation_minlogprob: float | None,
    base_snapshot_min_logprob: float | None,
    priority_key: tuple[Any, ...],
) -> Candidate | None:
    reasoning_path = REASONING_DIR / f"{row_id}.txt"
    if not reasoning_path.exists():
        return None
    if row_id not in train_prompts or row_id not in categories:
        return None

    metadata = fill_metadata_defaults(metadata_row)
    merged = dict(train_prompts[row_id])
    merged["category"] = categories[row_id]
    for key, value in metadata.items():
        merged[key] = value
    merged["current_failure"] = "True" if current_failure else "False"
    merged["current_validation_category"] = current_validation_category or ""
    merged["current_validation_prediction"] = current_validation_prediction or ""
    merged["current_validation_minlogprob"] = (
        "" if current_validation_minlogprob is None else f"{current_validation_minlogprob:.6f}"
    )
    merged["base_snapshot_min_logprob"] = (
        "" if base_snapshot_min_logprob is None else f"{base_snapshot_min_logprob:.6f}"
    )
    return Candidate(
        row=merged,
        bucket=bucket,
        source_tags=tuple(sorted(source_tags)),
        current_failure=current_failure,
        current_validation_category=current_validation_category,
        current_validation_minlogprob=current_validation_minlogprob,
        base_snapshot_min_logprob=base_snapshot_min_logprob,
        priority_key=priority_key,
    )


def build_current_failure_candidates(
    *,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    metadata_map: dict[str, dict[str, str]],
    base_index_map: dict[str, dict[str, Any]],
    validation_profile: dict[str, Any],
    previous_v2_selection_ids: set[str],
) -> tuple[list[Candidate], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    candidates: list[Candidate] = []
    missing_reasoning_ids: list[str] = []
    missing_prompt_ids: list[str] = []
    missing_category_ids: list[str] = []
    missing_train_metadata_ids: list[str] = []

    numeric_operator_counts: Counter[str] = Counter()
    glyph_answer_char_counts: Counter[str] = Counter()
    glyph_answer_length_counts: Counter[int] = Counter()
    bit_solver_counts: Counter[str] = Counter()
    bit_abstract_family_counts: Counter[str] = Counter()
    current_failure_ids_by_bucket: dict[str, list[str]] = {bucket: [] for bucket in BUCKET_ORDER}
    current_failure_ids_by_category: Counter[str] = Counter()
    failure_profile_rows: list[dict[str, Any]] = []

    for validation_row in sorted(validation_profile["wrong_rows"], key=lambda row: (row["category"], row["id"])):
        row_id = validation_row["id"]
        metadata_row = metadata_map.get(row_id)
        if metadata_row is None:
            missing_train_metadata_ids.append(row_id)
        bucket = failure_bucket_for_row(validation_row, metadata_row)
        if bucket is None:
            continue

        metadata = fill_metadata_defaults(metadata_row)
        current_failure_ids_by_bucket[bucket].append(row_id)
        current_failure_ids_by_category[validation_row["category"]] += 1

        subtype = str(metadata.get("template_subtype", "")).strip()
        if bucket == "current_symbol_numeric_failures":
            numeric_operator_counts[metadata.get("symbol_query_operator", "")] += 1
        elif bucket == "current_symbol_glyph_failures":
            answer = str(validation_row.get("answer", ""))
            glyph_answer_length_counts[len(answer)] += 1
            for char in answer:
                glyph_answer_char_counts[char] += 1
        elif bucket == "current_bit_failures":
            bit_solver_counts[metadata.get("teacher_solver_candidate", "<missing>") or "<missing>"] += 1
            bit_abstract_family_counts[
                metadata.get("bit_structured_formula_abstract_family", "") or "<missing>"
            ] += 1

        base_row = base_index_map.get(row_id, {})
        base_snapshot_min_logprob = (
            parse_float(base_row.get("min_logprob"), 999.0) if base_row else None
        )
        validation_minlogprob = parse_float(validation_row.get("minlogprob"), 999.0)
        selection_tier_priority = SELECTION_TIER_PRIORITY.get(metadata.get("selection_tier", ""), 0)
        verified_trace = parse_bool(metadata.get("verified_trace_ready", ""))
        hard_score = parse_float(metadata.get("hard_score"), 0.0)
        priority_key = (
            -(1 if verified_trace else 0),
            -selection_tier_priority,
            -hard_score,
            validation_minlogprob,
            row_id,
        )

        source_tags = {
            bucket,
            "current_mlx_validation_failure",
            f"validation_category:{validation_row['category']}",
            f"template_subtype:{subtype or 'metadata_missing'}",
        }
        if verified_trace:
            source_tags.add("verified_trace_ready")
        if metadata.get("teacher_solver_candidate"):
            source_tags.add(f"teacher:{metadata['teacher_solver_candidate']}")
        if row_id in previous_v2_selection_ids:
            source_tags.add("selected_in_v2")

        candidate = make_candidate(
            row_id=row_id,
            bucket=bucket,
            train_prompts=train_prompts,
            categories=categories,
            metadata_row=metadata_row,
            source_tags=source_tags,
            current_failure=True,
            current_validation_category=validation_row["category"],
            current_validation_prediction=validation_row.get("predicted", ""),
            current_validation_minlogprob=validation_minlogprob,
            base_snapshot_min_logprob=base_snapshot_min_logprob,
            priority_key=priority_key,
        )
        if candidate is None:
            if (REASONING_DIR / f"{row_id}.txt").exists() is False:
                missing_reasoning_ids.append(row_id)
            elif row_id not in train_prompts:
                missing_prompt_ids.append(row_id)
            elif row_id not in categories:
                missing_category_ids.append(row_id)
            continue
        candidates.append(candidate)

        failure_profile_rows.append(
            {
                "id": row_id,
                "category": validation_row["category"],
                "bucket": bucket,
                "template_subtype": subtype,
                "selection_tier": metadata.get("selection_tier", ""),
                "teacher_solver_candidate": metadata.get("teacher_solver_candidate", ""),
                "hard_score": metadata.get("hard_score", ""),
                "validated_prediction": validation_row.get("predicted", ""),
                "gold_answer": validation_row.get("answer", ""),
                "validation_minlogprob": f"{validation_minlogprob:.6f}",
                "selected_in_v2": row_id in previous_v2_selection_ids,
            }
        )

    diagnostics = {
        "missing_reasoning_ids": sorted(set(missing_reasoning_ids)),
        "missing_prompt_ids": sorted(set(missing_prompt_ids)),
        "missing_category_ids": sorted(set(missing_category_ids)),
        "missing_train_metadata_ids": sorted(set(missing_train_metadata_ids)),
        "current_failure_ids_by_bucket": {
            key: sorted(value) for key, value in current_failure_ids_by_bucket.items() if value
        },
        "current_failure_ids_by_category": dict(sorted(current_failure_ids_by_category.items())),
        "numeric_failure_operator_counts": dict(sorted(numeric_operator_counts.items())),
        "glyph_failure_answer_char_counts": dict(
            sorted(glyph_answer_char_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        "glyph_failure_answer_length_counts": dict(
            sorted(glyph_answer_length_counts.items(), key=lambda item: item[0])
        ),
        "bit_failure_solver_counts": dict(
            sorted(bit_solver_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        "bit_failure_abstract_family_counts": dict(
            sorted(bit_abstract_family_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
    }
    failure_stats = {
        "failure_ids": set(validation_profile["wrong_ids"]),
        "numeric_operator_counts": numeric_operator_counts,
        "glyph_answer_char_counts": glyph_answer_char_counts,
        "glyph_answer_length_counts": glyph_answer_length_counts,
        "bit_solver_counts": bit_solver_counts,
        "bit_abstract_family_counts": bit_abstract_family_counts,
    }
    return candidates, diagnostics, failure_stats, failure_profile_rows


def build_support_candidates(
    *,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    metadata_map: dict[str, dict[str, str]],
    base_index_map: dict[str, dict[str, Any]],
    failure_stats: dict[str, Any],
) -> tuple[list[Candidate], dict[str, Any]]:
    candidates: list[Candidate] = []
    support_pool_sizes: Counter[str] = Counter()
    missing_reasoning_ids: list[str] = []
    missing_prompt_ids: list[str] = []
    missing_category_ids: list[str] = []

    failure_ids: set[str] = set(failure_stats["failure_ids"])

    for row_id, metadata_row in sorted(metadata_map.items()):
        if row_id in failure_ids:
            continue
        bucket = support_bucket_for_metadata(metadata_row)
        if bucket is None:
            continue
        if (REASONING_DIR / f"{row_id}.txt").exists() is False:
            missing_reasoning_ids.append(row_id)
            continue
        if row_id not in train_prompts:
            missing_prompt_ids.append(row_id)
            continue
        if row_id not in categories:
            missing_category_ids.append(row_id)
            continue

        support_pool_sizes[bucket] += 1
        metadata = fill_metadata_defaults(metadata_row)
        base_row = base_index_map.get(row_id, {})
        base_snapshot_min_logprob = parse_float(base_row.get("min_logprob"), 999.0) if base_row else 999.0
        selection_tier_priority = SELECTION_TIER_PRIORITY.get(metadata.get("selection_tier", ""), 0)
        hard_score = parse_float(metadata.get("hard_score"), 0.0)
        num_examples = parse_int(metadata.get("num_examples"), 0)
        prompt_len_chars = parse_int(metadata.get("prompt_len_chars"), 0)
        verified_trace = parse_bool(metadata.get("verified_trace_ready", ""))
        source_tags = {bucket, "current_mlx_support_pool"}

        if bucket == "symbol_numeric_support":
            operator = metadata.get("symbol_query_operator", "")
            operator_hits = int(failure_stats["numeric_operator_counts"].get(operator, 0))
            solver_ready = metadata.get("teacher_solver_candidate", "") == "symbol_numeric_operator_formula"
            if operator_hits > 0:
                source_tags.add("same_current_operator")
            if solver_ready:
                source_tags.add("symbol_numeric_operator_formula")
            if verified_trace:
                source_tags.add("verified_trace_ready")
            priority_key = (
                -operator_hits,
                -(1 if solver_ready else 0),
                -(1 if verified_trace else 0),
                -selection_tier_priority,
                base_snapshot_min_logprob,
                -hard_score,
                -num_examples,
                -prompt_len_chars,
                row_id,
            )
        elif bucket == "symbol_glyph_support":
            answer_text = str(train_prompts[row_id].get("answer", ""))
            char_overlap = sum(
                failure_stats["glyph_answer_char_counts"].get(char, 0) for char in answer_text
            )
            length_hits = int(failure_stats["glyph_answer_length_counts"].get(len(answer_text), 0))
            if char_overlap > 0:
                source_tags.add("same_current_answer_chars")
            priority_key = (
                -char_overlap,
                -length_hits,
                base_snapshot_min_logprob,
                -hard_score,
                -num_examples,
                -prompt_len_chars,
                row_id,
            )
        else:
            subtype = metadata.get("template_subtype", "")
            subtype_priority = SUBTYPE_PRIORITY.get(subtype, 0)
            solver_hits = int(
                failure_stats["bit_solver_counts"].get(
                    metadata.get("teacher_solver_candidate", "") or "<missing>",
                    0,
                )
            )
            abstract_family_hits = int(
                failure_stats["bit_abstract_family_counts"].get(
                    metadata.get("bit_structured_formula_abstract_family", "") or "<missing>",
                    0,
                )
            )
            if solver_hits > 0:
                source_tags.add("same_current_bit_solver")
            if abstract_family_hits > 0:
                source_tags.add("same_current_bit_family")
            if verified_trace:
                source_tags.add("verified_trace_ready")
            priority_key = (
                -(1 if verified_trace else 0),
                -subtype_priority,
                -solver_hits,
                -abstract_family_hits,
                -selection_tier_priority,
                base_snapshot_min_logprob,
                -hard_score,
                -num_examples,
                -prompt_len_chars,
                row_id,
            )

        candidate = make_candidate(
            row_id=row_id,
            bucket=bucket,
            train_prompts=train_prompts,
            categories=categories,
            metadata_row=metadata,
            source_tags=source_tags,
            current_failure=False,
            current_validation_category=None,
            current_validation_prediction=None,
            current_validation_minlogprob=None,
            base_snapshot_min_logprob=base_snapshot_min_logprob,
            priority_key=priority_key,
        )
        if candidate is not None:
            candidates.append(candidate)

    diagnostics = {
        "support_pool_sizes": dict(sorted(support_pool_sizes.items())),
        "support_missing_reasoning_ids": sorted(set(missing_reasoning_ids)),
        "support_missing_prompt_ids": sorted(set(missing_prompt_ids)),
        "support_missing_category_ids": sorted(set(missing_category_ids)),
    }
    return candidates, diagnostics


def select_candidates(candidates: list[Candidate], bucket_limits: dict[str, int]) -> list[Candidate]:
    selected: list[Candidate] = []
    counts = Counter()
    bucket_rank = {bucket: index for index, bucket in enumerate(BUCKET_ORDER)}
    for candidate in sorted(candidates, key=lambda item: (bucket_rank[item.bucket], item.priority_key)):
        if counts[candidate.bucket] >= bucket_limits[candidate.bucket]:
            continue
        selected.append(candidate)
        counts[candidate.bucket] += 1
    return selected


def build_overlay_rows(
    selected: list[Candidate],
    repeat_counts: dict[str, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    for candidate in selected:
        row_id = candidate.row["id"]
        reasoning_text = (REASONING_DIR / f"{row_id}.txt").read_text(encoding="utf-8").rstrip("\n")
        answer = candidate.row["answer"]
        completion_text = build_completion_text(reasoning_text, answer)
        repeat_count = repeat_counts[candidate.bucket]
        base = {
            "id": row_id,
            "category": candidate.row["category"],
            "bucket": candidate.bucket,
            "current_failure": candidate.current_failure,
            "current_validation_category": candidate.row["current_validation_category"],
            "current_validation_prediction": candidate.row["current_validation_prediction"],
            "current_validation_minlogprob": candidate.row["current_validation_minlogprob"],
            "base_snapshot_min_logprob": candidate.row["base_snapshot_min_logprob"],
            "prompt": candidate.row["prompt"],
            "answer": answer,
            "completion_text": completion_text,
            "selection_tier": candidate.row["selection_tier"],
            "template_subtype": candidate.row["template_subtype"],
            "teacher_solver_candidate": candidate.row["teacher_solver_candidate"],
            "source_tags": list(candidate.source_tags),
            "recommended_repeat_count": repeat_count,
            "hard_score": parse_float(candidate.row["hard_score"], 0.0),
            "audit_reasons": candidate.row["audit_reasons"],
            "analysis_notes": candidate.row["analysis_notes"],
            "symbol_query_operator": candidate.row["symbol_query_operator"],
            "bit_structured_formula_name": candidate.row["bit_structured_formula_name"],
            "bit_structured_formula_prediction": candidate.row["bit_structured_formula_prediction"],
            "bit_structured_formula_abstract_family": candidate.row["bit_structured_formula_abstract_family"],
        }
        unique_rows.append(base)
        for overlay_index in range(repeat_count):
            repeated = dict(base)
            repeated["overlay_instance"] = overlay_index + 1
            repeated_rows.append(repeated)
    return unique_rows, repeated_rows


def build_anchor_watchlist(validation_profile: dict[str, Any]) -> list[dict[str, Any]]:
    watchlist: list[dict[str, Any]] = []
    wanted_categories = ("numeral", "gravity", "unit_conversion", "cipher", "bit_manipulation")
    for category in wanted_categories:
        for row in sorted(validation_profile["rows"], key=lambda item: item["id"]):
            if row.get("category") != category:
                continue
            if row.get("correct") != "True":
                continue
            watchlist.append(
                {
                    "id": row["id"],
                    "category": category,
                    "gold_answer": row["answer"],
                    "prediction": row["predicted"],
                    "minlogprob": row.get("minlogprob", ""),
                }
            )
            break
    return watchlist


def build_summary(
    *,
    selected: list[Candidate],
    unique_rows: list[dict[str, Any]],
    repeated_rows: list[dict[str, Any]],
    validation_profile: dict[str, Any],
    validation_csv: Path,
    validation_summary_json: Path | None,
    diagnostics: dict[str, Any],
    watchlist: list[dict[str, Any]],
    training_bundle: dict[str, Any] | None,
    previous_v2_selection_ids: set[str],
) -> dict[str, Any]:
    selected_ids = {row["id"] for row in unique_rows}
    selected_failure_ids = {row["id"] for row in unique_rows if row["current_failure"]}
    current_failure_ids = set(validation_profile["wrong_ids"])
    selected_by_bucket = Counter(candidate.bucket for candidate in selected)
    repeated_by_bucket = Counter(row["bucket"] for row in repeated_rows)
    source_counts = Counter(tag for row in unique_rows for tag in row["source_tags"])
    selected_failure_by_category = Counter(
        row["current_validation_category"] for row in unique_rows if row["current_failure"]
    )
    v2_overlap_ids = sorted(current_failure_ids & previous_v2_selection_ids)
    v3_overlap_ids = sorted(current_failure_ids & selected_ids)
    current_failure_total = len(current_failure_ids)
    current_failure_selected = len(selected_failure_ids)
    current_failure_coverage = (
        current_failure_selected / current_failure_total if current_failure_total else 0.0
    )

    summary_payload = validation_profile["summary_payload"]
    current_validation = {
        "validation_csv": relative_to_repo(validation_csv),
        "validation_summary_json": relative_to_repo(validation_summary_json),
        "results_md": relative_to_repo(CURRENT_RESULTS_MD_PATH),
        "accuracy": validation_profile["accuracy"],
        "correct": validation_profile["correct"],
        "total": validation_profile["total"],
        "wrong_total": current_failure_total,
        "wrong_by_category": dict(sorted(validation_profile["wrong_by_category"].items())),
    }
    if summary_payload is not None:
        current_validation["evaluation_name"] = summary_payload.get("evaluation_name")
        current_validation["created_at"] = summary_payload.get("created_at")

    return {
        "version": "v20_corrective_corpus_v3",
        "created_at": utc_now(),
        "readme_eval_contract": verify_readme_eval_contract(),
        "strategy_basis": [
            "README.md",
            "A-Open-ProgressPrizePublication/README.md",
            "v20_mlx_repro_v1/v20_mlx_repro_v1-results.md",
        ],
        "current_mlx_validation": current_validation,
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_exact_failure_rows": current_failure_selected,
        "selected_support_rows": len(unique_rows) - current_failure_selected,
        "selected_by_bucket": dict(selected_by_bucket),
        "repeated_by_bucket": dict(repeated_by_bucket),
        "selected_failure_by_category": dict(sorted(selected_failure_by_category.items())),
        "source_tag_counts": dict(sorted(source_counts.items())),
        "current_failure_overlap": {
            "total_current_failures": current_failure_total,
            "selected_current_failures": current_failure_selected,
            "coverage": current_failure_coverage,
            "not_selected_ids": sorted(current_failure_ids - selected_failure_ids),
        },
        "v2_current_failure_overlap": {
            "selected_current_failures": len(v2_overlap_ids),
            "ids": v2_overlap_ids,
        },
        "v3_current_failure_overlap": {
            "selected_current_failures": len(v3_overlap_ids),
            "ids": v3_overlap_ids,
        },
        "diagnostics": diagnostics,
        "anchor_watchlist": watchlist,
        "training_bundle": training_bundle,
    }


def build_training_bundle(
    repeated_rows: list[dict[str, Any]],
    bundle_path: Path,
) -> dict[str, Any]:
    base_rows, base_examples, batch_size = load_base_snapshot_examples()
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    existing_steps = [int(row["step"]) for row in base_rows]
    base_step_count = max(existing_steps) + 1 if existing_steps else 0

    total_examples = 0
    total_tokens = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()
    overlay_by_bucket: Counter[str] = Counter()
    retokenized_overlay_ids: set[str] = set()
    synthetic_cache: dict[str, tuple[list[int], list[int], int]] = {}

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": "v20_corrective_corpus_v3",
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "base_snapshot_config": read_json(BASE_SNAPSHOT_CONFIG_PATH),
        "bundle_path": relative_to_repo(bundle_path),
        "note": (
            "Single-file training bundle for Kaggle upload. "
            "Includes the full v20 base snapshot plus a current-MLX-failure-first symbol+bit overlay."
        ),
    }

    with bundle_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False) + "\n")

        for row in base_rows:
            problem_id = str(row["problem_id"])
            segment = str(row["segment"])
            entry = base_examples[(problem_id, segment)]
            tokens = entry["tokens"]
            mask = entry["mask"]
            category = str(row["category"])
            payload = {
                "record_type": "example",
                "example_id": problem_id,
                "source_problem_id": problem_id,
                "source": "base_snapshot",
                "segment": segment,
                "category": category,
                "step": int(row["step"]),
                "num_loss_tokens": int(row["num_loss_tokens"]),
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[category] += 1

        for overlay_offset, row in enumerate(repeated_rows):
            problem_id = str(row["id"])
            segment = "synthetic.jsonl"
            key = (problem_id, segment)
            if key in base_examples:
                entry = base_examples[key]
                base_row = entry["row"]
                tokens = entry["tokens"]
                mask = entry["mask"]
                category = str(base_row["category"])
                num_loss_tokens = int(base_row["num_loss_tokens"])
            else:
                if problem_id not in synthetic_cache:
                    tokens, mask = tokenize_overlay_example(
                        prompt=str(row["prompt"]),
                        completion_text=str(row["completion_text"]),
                    )
                    synthetic_cache[problem_id] = (tokens, mask, sum(mask))
                tokens, mask, num_loss_tokens = synthetic_cache[problem_id]
                category = str(row["category"])
                retokenized_overlay_ids.add(problem_id)
            overlay_step = base_step_count + (overlay_offset // batch_size)
            payload = {
                "record_type": "example",
                "example_id": f"{problem_id}#overlay-{row['overlay_instance']}",
                "source_problem_id": problem_id,
                "source": "corrective_overlay",
                "segment": segment,
                "category": category,
                "step": overlay_step,
                "num_loss_tokens": num_loss_tokens,
                "bucket": row["bucket"],
                "overlay_instance": int(row["overlay_instance"]),
                "recommended_repeat_count": int(row["recommended_repeat_count"]),
                "current_failure": bool(row["current_failure"]),
                "current_validation_category": row["current_validation_category"],
                "source_tags": row["source_tags"],
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[category] += 1
            overlay_by_bucket[row["bucket"]] += 1

    total_steps = base_step_count + ((len(repeated_rows) + batch_size - 1) // batch_size)
    return {
        "path": relative_to_repo(bundle_path),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "format": "nemotron_single_file_training_bundle_v1",
        "base_examples": len(base_rows),
        "overlay_examples": len(repeated_rows),
        "total_examples": total_examples,
        "batch_size": batch_size,
        "total_steps": total_steps,
        "total_tokens": total_tokens,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_seq_len": max_seq_len,
        "overlay_by_bucket": dict(overlay_by_bucket),
        "category_counts": dict(sorted(category_counts.items())),
        "retokenized_overlay_problem_ids": sorted(retokenized_overlay_ids),
        "retokenized_overlay_problem_count": len(retokenized_overlay_ids),
    }


def parse_bucket_limits(arg: str | None) -> dict[str, int]:
    limits = dict(DEFAULT_BUCKET_LIMITS)
    if not arg:
        return limits
    for chunk in arg.split(","):
        text = chunk.strip()
        if not text:
            continue
        key, value = text.split("=", 1)
        if key not in limits:
            raise SystemExit(f"Unknown bucket in --bucket-limits: {key}")
        limits[key] = int(value)
    return limits


def parse_repeat_counts(arg: str | None) -> dict[str, int]:
    counts = dict(DEFAULT_REPEAT_COUNTS)
    if not arg:
        return counts
    for chunk in arg.split(","):
        text = chunk.strip()
        if not text:
            continue
        key, value = text.split("=", 1)
        if key not in counts:
            raise SystemExit(f"Unknown bucket in --repeat-counts: {key}")
        counts[key] = int(value)
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a current-MLX-failure-first corrective corpus for the next single-file "
            "Nemotron reproduction step."
        )
    )
    parser.add_argument("--run-name", default="smoke_current_mlx_failure_focus")
    parser.add_argument("--validation-csv", type=Path, default=CURRENT_VALIDATION_CSV_PATH)
    parser.add_argument("--validation-summary-json", type=Path, default=CURRENT_VALIDATION_SUMMARY_PATH)
    parser.add_argument("--bucket-limits", default=None)
    parser.add_argument("--repeat-counts", default=None)
    parser.add_argument("--write-training-bundle", action="store_true")
    parser.add_argument("--bundle-path", type=Path, default=DEFAULT_BUNDLE_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validation_csv = args.validation_csv.resolve()
    validation_summary_json = None if args.validation_summary_json is None else args.validation_summary_json.resolve()
    bucket_limits = parse_bucket_limits(args.bucket_limits)
    repeat_counts = parse_repeat_counts(args.repeat_counts)

    train_prompts = load_train_prompts()
    categories = load_problem_categories()
    metadata_map = load_train_metadata_map()
    base_index_map = load_base_snapshot_index_map()
    previous_v2_selection_ids = load_previous_v2_selection_ids()
    validation_profile = load_current_validation_profile(validation_csv, validation_summary_json)

    failure_candidates, failure_diagnostics, failure_stats, failure_profile_rows = build_current_failure_candidates(
        train_prompts=train_prompts,
        categories=categories,
        metadata_map=metadata_map,
        base_index_map=base_index_map,
        validation_profile=validation_profile,
        previous_v2_selection_ids=previous_v2_selection_ids,
    )
    support_candidates, support_diagnostics = build_support_candidates(
        train_prompts=train_prompts,
        categories=categories,
        metadata_map=metadata_map,
        base_index_map=base_index_map,
        failure_stats=failure_stats,
    )

    diagnostics = {
        **failure_diagnostics,
        **support_diagnostics,
    }
    selected = select_candidates(failure_candidates + support_candidates, bucket_limits=bucket_limits)
    unique_rows, repeated_rows = build_overlay_rows(selected, repeat_counts=repeat_counts)
    watchlist = build_anchor_watchlist(validation_profile)
    training_bundle = None
    if args.write_training_bundle:
        training_bundle = build_training_bundle(repeated_rows=repeated_rows, bundle_path=args.bundle_path.resolve())

    run_root = OUTPUT_ROOT / args.run_name
    artifacts_dir = run_root / "artifacts"
    reports_dir = run_root / "reports"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    selection_rows = []
    for row in unique_rows:
        selection_rows.append(
            {
                "id": row["id"],
                "category": row["category"],
                "bucket": row["bucket"],
                "current_failure": row["current_failure"],
                "current_validation_category": row["current_validation_category"],
                "selection_tier": row["selection_tier"],
                "template_subtype": row["template_subtype"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "recommended_repeat_count": row["recommended_repeat_count"],
                "hard_score": row["hard_score"],
                "current_validation_minlogprob": row["current_validation_minlogprob"],
                "base_snapshot_min_logprob": row["base_snapshot_min_logprob"],
                "source_tags": "|".join(row["source_tags"]),
            }
        )

    summary = build_summary(
        selected=selected,
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        validation_profile=validation_profile,
        validation_csv=validation_csv,
        validation_summary_json=validation_summary_json,
        diagnostics=diagnostics,
        watchlist=watchlist,
        training_bundle=training_bundle,
        previous_v2_selection_ids=previous_v2_selection_ids,
    )

    write_csv(
        artifacts_dir / "corrective_selection.csv",
        selection_rows,
        fieldnames=[
            "id",
            "category",
            "bucket",
            "current_failure",
            "current_validation_category",
            "selection_tier",
            "template_subtype",
            "teacher_solver_candidate",
            "recommended_repeat_count",
            "hard_score",
            "current_validation_minlogprob",
            "base_snapshot_min_logprob",
            "source_tags",
        ],
    )
    write_csv(
        artifacts_dir / "current_mlx_failure_profile.csv",
        failure_profile_rows,
        fieldnames=[
            "id",
            "category",
            "bucket",
            "template_subtype",
            "selection_tier",
            "teacher_solver_candidate",
            "hard_score",
            "validated_prediction",
            "gold_answer",
            "validation_minlogprob",
            "selected_in_v2",
        ],
    )
    write_jsonl(artifacts_dir / "corrective_overlay_unique.jsonl", unique_rows)
    write_jsonl(artifacts_dir / "corrective_overlay_repeated.jsonl", repeated_rows)
    write_csv(
        artifacts_dir / "anchor_watchlist.csv",
        watchlist,
        fieldnames=["id", "category", "gold_answer", "prediction", "minlogprob"],
    )
    write_json(artifacts_dir / "corrective_overlay_summary.json", summary)

    report_lines = [
        "# v20 corrective corpus v3 report",
        "",
        "## Focus",
        "",
        "- README.md: leaderboard metric is deterministic and keeps the boxed-answer contract fixed.",
        "- A-Open-ProgressPrizePublication/README.md: bit remains the main long-run lever, but equation traces and",
        "  symbol splitting/concatenation are also explicit weak points.",
        "- Current MLX reproduced run failed mainly on `glyph_len5` and `numeric_2x2`, so v3 promotes",
        "  exact current failures first instead of reusing the older Kaggle v2 diff signal.",
        "",
        "## Current failure coverage",
        "",
        f"- current failures: `{summary['current_failure_overlap']['total_current_failures']}`",
        f"- v2 overlap on these failures: `{summary['v2_current_failure_overlap']['selected_current_failures']}`",
        f"- v3 overlap on these failures: `{summary['v3_current_failure_overlap']['selected_current_failures']}`",
        "",
        "## Selected unique rows",
        "",
    ]
    for bucket in BUCKET_ORDER:
        report_lines.append(f"- `{bucket}`: `{summary['selected_by_bucket'].get(bucket, 0)}`")
    report_lines.extend(["", "## Repeated training rows", ""])
    for bucket in BUCKET_ORDER:
        report_lines.append(f"- `{bucket}`: `{summary['repeated_by_bucket'].get(bucket, 0)}`")
    report_lines.extend(
        [
            "",
            "## Current failure profile",
            "",
            f"- wrong_by_category: `{json.dumps(summary['current_mlx_validation']['wrong_by_category'], ensure_ascii=False)}`",
            f"- numeric_operator_counts: `{json.dumps(diagnostics['numeric_failure_operator_counts'], ensure_ascii=False)}`",
            f"- bit_solver_counts: `{json.dumps(diagnostics['bit_failure_solver_counts'], ensure_ascii=False)}`",
            "",
            "## Kaggle single-file bundle",
            "",
        ]
    )
    if training_bundle is None:
        report_lines.append("- not generated in this run")
    else:
        report_lines.extend(
            [
                f"- path: `{training_bundle['path']}`",
                f"- total examples: `{training_bundle['total_examples']}`",
                f"- overlay examples: `{training_bundle['overlay_examples']}`",
                f"- total steps: `{training_bundle['total_steps']}`",
            ]
        )
    (reports_dir / "corrective_overlay_report.md").write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
