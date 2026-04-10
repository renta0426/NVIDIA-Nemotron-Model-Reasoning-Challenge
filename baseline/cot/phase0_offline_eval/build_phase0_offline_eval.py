from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ANALYSIS_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parent / "artifacts"
DEFAULT_REPORT_ROOT = Path(__file__).resolve().parent / "reports"
DEFAULT_RULE_BASE_600 = REPO_ROOT / "baseline" / "cot" / "output-csv" / "rule_based_adapter_readme_inference_samples_rule_base-600.csv"
DEFAULT_RULE_BASE_800 = REPO_ROOT / "baseline" / "cot" / "output-csv" / "rule_based_adapter_readme_inference_samples_rule_base-800.csv"

GENERAL_STABLE_QUOTAS = {
    "gravity_constant": 50,
    "unit_conversion": 50,
    "roman_numeral": 50,
    "text_decryption": 50,
}
BINARY_HARD_BUCKET_QUOTAS = {
    "supported_bijection": 16,
    "dominant_structured_safe": 8,
    "supported_affine_xor": 7,
    "boolean_family": 6,
    "dominant_structured_abstract": 6,
    "no_solver_answer_only": 6,
    "no_solver_manual": 5,
    "supported_not_structured": 4,
    "rare_perm_independent": 1,
    "rare_byte_transform": 1,
}
SYMBOL_WATCH_TARGETS = [
    ("numeric_2x2", "verified_trace_ready", 15),
    ("numeric_2x2", "answer_only_keep", 15),
    ("numeric_2x2", "manual_audit_priority", 10),
    ("glyph_len5", "manual_audit_priority", 20),
]
HOLDOUT_FOLDS = 5
BOXED_PATTERN = re.compile(r"\\boxed\{([^}]*)(?:\}|$)")
FINAL_ANSWER_PATTERNS = (
    r"The final answer is:\s*([^\n]+)",
    r"Final answer is:\s*([^\n]+)",
    r"Final answer\s*[:：]\s*([^\n]+)",
    r"final answer\s*[:：]\s*([^\n]+)",
)
NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
BIT8_PATTERN = re.compile(r"^[01]{8}$")
FAMILY_SHORT = {
    "gravity_constant": "gravity",
    "unit_conversion": "unit",
    "roman_numeral": "roman",
    "text_decryption": "text",
    "bit_manipulation": "binary",
    "symbol_equation": "symbol",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 0 offline evaluation builder for baseline/cot. "
            "Creates official-like benchmark sets and scores existing prediction CSVs "
            "without loading any model."
        )
    )
    parser.add_argument("--analysis-csv", type=Path, default=DEFAULT_ANALYSIS_CSV)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument(
        "--score-csv",
        action="append",
        type=Path,
        default=[],
        help="Prediction/sample CSV to score. Can be specified multiple times.",
    )
    parser.add_argument(
        "--skip-score",
        action="store_true",
        help="Build benchmark artifacts only, without scoring any prediction CSVs.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


def stable_mod(text: str, mod: int) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % mod


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return [dict(row) for row in reader]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def prompt_len_bucket(length: int) -> str:
    if length < 300:
        return "<300"
    if length < 400:
        return "300-399"
    if length < 500:
        return "400-499"
    if length < 600:
        return "500-599"
    return "600+"


def score_rank_low(row: dict[str, str]) -> tuple[Any, ...]:
    hard_score = parse_float(row.get("hard_score"), 999.0)
    if hard_score is None:
        hard_score = 999.0
    return (
        hard_score,
        parse_int(row.get("prompt_len_chars"), 99999),
        -parse_int(row.get("num_examples"), 0),
        row.get("id", ""),
    )


def score_rank_high(row: dict[str, str]) -> tuple[Any, ...]:
    hard_score = parse_float(row.get("hard_score"), -999.0)
    if hard_score is None:
        hard_score = -999.0
    return (
        -hard_score,
        -parse_int(row.get("prompt_len_chars"), 0),
        -parse_int(row.get("num_examples"), 0),
        row.get("id", ""),
    )


def balanced_take(
    rows: list[dict[str, str]],
    *,
    quota: int,
    group_keys: tuple[str, ...],
    hard_first: bool,
) -> list[dict[str, str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = tuple(str(row.get(name, "") or "") for name in group_keys)
        grouped[key].append(row)
    rank_fn = score_rank_high if hard_first else score_rank_low
    ordered_groups = sorted(grouped.items(), key=lambda item: (item[0], len(item[1])))
    for _, group_rows in ordered_groups:
        group_rows.sort(key=rank_fn)
    selected: list[dict[str, str]] = []
    while len(selected) < quota:
        progressed = False
        for _, group_rows in ordered_groups:
            if not group_rows:
                continue
            selected.append(group_rows.pop(0))
            progressed = True
            if len(selected) >= quota:
                break
        if not progressed:
            break
    return selected


def normalize_family_label(row: dict[str, str]) -> str:
    family = row.get("family", "")
    if family in FAMILY_SHORT:
        return FAMILY_SHORT[family]
    label = row.get("label", "")
    if label:
        return label
    return family


def benchmark_columns() -> list[str]:
    return [
        "benchmark_name",
        "benchmark_role",
        "id",
        "family",
        "family_short",
        "template_subtype",
        "selection_tier",
        "teacher_solver_candidate",
        "answer_type",
        "num_examples",
        "prompt_len_chars",
        "hard_score",
        "binary_focus_bucket",
        "group_signature",
        "query_raw",
        "answer",
        "prompt",
    ]


def to_benchmark_row(row: dict[str, str], *, benchmark_name: str, benchmark_role: str) -> dict[str, Any]:
    return {
        "benchmark_name": benchmark_name,
        "benchmark_role": benchmark_role,
        "id": row.get("id", ""),
        "family": row.get("family", ""),
        "family_short": normalize_family_label(row),
        "template_subtype": row.get("template_subtype", ""),
        "selection_tier": row.get("selection_tier", ""),
        "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
        "answer_type": row.get("answer_type", ""),
        "num_examples": parse_int(row.get("num_examples"), 0),
        "prompt_len_chars": parse_int(row.get("prompt_len_chars"), 0),
        "hard_score": parse_float(row.get("hard_score"), 0.0),
        "binary_focus_bucket": row.get("binary_focus_bucket", ""),
        "group_signature": row.get("group_signature", ""),
        "query_raw": row.get("query_raw", ""),
        "answer": row.get("answer", ""),
        "prompt": row.get("prompt", ""),
    }


def binary_focus_bucket(row: dict[str, str]) -> str | None:
    solver = (row.get("teacher_solver_candidate") or "").strip()
    tier = (row.get("selection_tier") or "").strip()
    if row.get("family") != "bit_manipulation" or tier == "exclude_suspect":
        return None
    if solver == "binary_bit_permutation_independent":
        return "rare_perm_independent"
    if solver == "binary_byte_transform":
        return "rare_byte_transform"
    if solver == "binary_affine_xor":
        return "supported_affine_xor"
    if solver == "binary_bit_permutation_bijection":
        return "supported_bijection"
    if "boolean" in solver:
        return "boolean_family"
    if row.get("template_subtype") == "bit_structured_byte_formula" and (row.get("bit_structured_formula_safe") or "").lower() == "true":
        return "dominant_structured_safe"
    if (row.get("bit_structured_formula_abstract_safe") or "").lower() == "true":
        return "dominant_structured_abstract"
    if (row.get("bit_not_structured_formula_safe") or "").lower() == "true":
        return "supported_not_structured"
    if solver == "" and tier == "answer_only_keep":
        return "no_solver_answer_only"
    if solver == "" and tier == "manual_audit_priority":
        return "no_solver_manual"
    return None


def build_general_stable_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for family, quota in GENERAL_STABLE_QUOTAS.items():
        candidates = [
            row
            for row in rows
            if row.get("family") == family
            and row.get("selection_tier") == "verified_trace_ready"
            and parse_bool(row.get("verified_trace_ready", "true"))
        ]
        family_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=("template_subtype", "teacher_solver_candidate"),
            hard_first=False,
        )
        selected.extend(
            to_benchmark_row(row, benchmark_name="general_stable_set", benchmark_role="stable_replay")
            for row in family_rows
        )
    return selected


def build_binary_hard_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    bucketed_rows: list[dict[str, str]] = []
    for row in rows:
        focus_bucket = binary_focus_bucket(row)
        if focus_bucket is None:
            continue
        enriched = dict(row)
        enriched["binary_focus_bucket"] = focus_bucket
        bucketed_rows.append(enriched)
    for focus_bucket, quota in BINARY_HARD_BUCKET_QUOTAS.items():
        candidates = [row for row in bucketed_rows if row.get("binary_focus_bucket") == focus_bucket]
        group_keys = (
            "selection_tier",
            "template_subtype",
            "teacher_solver_candidate",
            "bit_structured_formula_abstract_family",
            "group_signature",
        )
        bucket_rows = balanced_take(candidates, quota=quota, group_keys=group_keys, hard_first=True)
        if len(bucket_rows) != quota:
            raise RuntimeError(f"binary_hard_set bucket {focus_bucket}: expected {quota}, got {len(bucket_rows)}")
        selected.extend(
            to_benchmark_row(row, benchmark_name="binary_hard_set", benchmark_role="hard_binary_watch")
            for row in bucket_rows
        )
    return selected


def fill_symbol_watch_candidates(rows: list[dict[str, str]], already_selected_ids: set[str]) -> list[dict[str, Any]]:
    remaining = [
        row
        for row in rows
        if row.get("family") == "symbol_equation" and row.get("id", "") not in already_selected_ids
    ]
    remaining.sort(key=score_rank_high)
    filler: list[dict[str, Any]] = []
    for row in remaining:
        filler.append(to_benchmark_row(row, benchmark_name="symbol_watch_set", benchmark_role="symbol_watch"))
        if len(filler) >= 60:
            break
    return filler


def build_symbol_watch_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    symbol_rows = [row for row in rows if row.get("family") == "symbol_equation"]
    for template_subtype, tier, quota in SYMBOL_WATCH_TARGETS:
        candidates = [
            row
            for row in symbol_rows
            if row.get("template_subtype") == template_subtype and row.get("selection_tier") == tier
        ]
        watch_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=("symbol_query_operator", "teacher_solver_candidate"),
            hard_first=True,
        )
        for row in watch_rows:
            if row.get("id", "") in selected_ids:
                continue
            selected.append(to_benchmark_row(row, benchmark_name="symbol_watch_set", benchmark_role="symbol_watch"))
            selected_ids.add(row.get("id", ""))
    if len(selected) < 60:
        for row in fill_symbol_watch_candidates(rows, selected_ids):
            if row["id"] in selected_ids:
                continue
            selected.append(row)
            selected_ids.add(row["id"])
            if len(selected) >= 60:
                break
    return selected


def holdout_key_structured_family(row: dict[str, str]) -> str:
    value = str(row.get("bit_structured_formula_abstract_family", "")).strip()
    return value or "__none__"


def holdout_key_solver(row: dict[str, str]) -> str:
    value = str(row.get("teacher_solver_candidate", "")).strip()
    return value or "__none__"


def holdout_key_gap(row: dict[str, str]) -> str:
    num_examples = parse_int(row.get("num_examples"), 0)
    no_candidate = parse_int(row.get("bit_no_candidate_positions"), -1)
    multi_candidate = parse_int(row.get("bit_multi_candidate_positions"), -1)
    return f"ex{num_examples}__no{no_candidate}__multi{multi_candidate}"


def holdout_key_prompt_signature(row: dict[str, str]) -> str:
    group_signature = str(row.get("group_signature", "")).strip()
    if group_signature:
        return group_signature
    prompt = str(row.get("prompt", ""))
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def assign_balanced_group_folds(keys: list[str], num_folds: int) -> dict[str, int]:
    group_counts = Counter(keys)
    fold_loads = [0 for _ in range(num_folds)]
    assignments: dict[str, int] = {}
    ordered_groups = sorted(group_counts.items(), key=lambda item: (-item[1], item[0]))
    for group_key, group_size in ordered_groups:
        preferred = stable_mod(group_key, num_folds)
        best_fold = min(
            range(num_folds),
            key=lambda fold: (fold_loads[fold], abs(fold - preferred), fold),
        )
        assignments[group_key] = best_fold
        fold_loads[best_fold] += group_size
    return assignments


def build_binary_holdout_assignments(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    binary_rows = [row for row in rows if row.get("family") == "bit_manipulation"]
    key_builders = {
        "structured_family": holdout_key_structured_family,
        "solver_family": holdout_key_solver,
        "gap_signature": holdout_key_gap,
        "prompt_signature": holdout_key_prompt_signature,
    }
    fold_maps = {
        holdout_kind: assign_balanced_group_folds([key_builder(row) for row in binary_rows], HOLDOUT_FOLDS)
        for holdout_kind, key_builder in key_builders.items()
    }
    assignments: list[dict[str, Any]] = []
    for row in binary_rows:
        for holdout_kind, key_builder in key_builders.items():
            holdout_key = key_builder(row)
            fold = fold_maps[holdout_kind][holdout_key]
            assignments.append(
                {
                    "id": row.get("id", ""),
                    "family": row.get("family", ""),
                    "selection_tier": row.get("selection_tier", ""),
                    "template_subtype": row.get("template_subtype", ""),
                    "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
                    "holdout_kind": holdout_kind,
                    "holdout_key": holdout_key,
                    "fold": fold,
                    "num_examples": parse_int(row.get("num_examples"), 0),
                    "bit_no_candidate_positions": parse_int(row.get("bit_no_candidate_positions"), -1),
                    "bit_multi_candidate_positions": parse_int(row.get("bit_multi_candidate_positions"), -1),
                    "group_signature": row.get("group_signature", ""),
                }
            )
    return assignments


def summarize_benchmark(rows: list[dict[str, Any]]) -> dict[str, Any]:
    family_counts = Counter(row["family_short"] for row in rows)
    tier_counts = Counter(row["selection_tier"] for row in rows)
    template_counts = Counter(row["template_subtype"] for row in rows)
    summary = {
        "rows": len(rows),
        "family_counts": dict(sorted(family_counts.items())),
        "selection_tier_counts": dict(sorted(tier_counts.items())),
        "template_subtype_counts": dict(sorted(template_counts.items())),
    }
    focus_bucket_counts = Counter(str(row.get("binary_focus_bucket", "") or "") for row in rows if row.get("binary_focus_bucket"))
    if focus_bucket_counts:
        summary["binary_focus_bucket_counts"] = dict(sorted(focus_bucket_counts.items()))
    return summary


def build_manifest(
    *,
    analysis_csv: Path,
    general_rows: list[dict[str, Any]],
    binary_rows: list[dict[str, Any]],
    symbol_rows: list[dict[str, Any]],
    holdouts: list[dict[str, Any]],
) -> dict[str, Any]:
    holdout_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in holdouts:
        holdout_counts[row["holdout_kind"]][str(row["fold"])] += 1
    return {
        "phase": "phase0_offline_eval",
        "source_analysis_csv": str(analysis_csv),
        "readme_eval_assumptions": {
            "metric": "accuracy",
            "temperature": 0.0,
            "top_p": 1.0,
            "max_tokens": 7680,
            "max_num_seqs": 64,
            "max_model_len": 8192,
            "boxed_first_extraction": True,
            "numeric_relative_tolerance": 1e-2,
        },
        "benchmark_sets": {
            "general_stable_set": summarize_benchmark(general_rows),
            "binary_hard_set": summarize_benchmark(binary_rows),
            "symbol_watch_set": summarize_benchmark(symbol_rows),
        },
        "binary_holdouts": {
            holdout_kind: dict(sorted(folds.items()))
            for holdout_kind, folds in sorted(holdout_counts.items())
        },
    }


def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"
    matches = BOXED_PATTERN.findall(text)
    if matches:
        non_empty = [match.strip() for match in matches if match.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    for pattern in FINAL_ANSWER_PATTERNS:
        matched = re.findall(pattern, text, re.IGNORECASE)
        if matched:
            return matched[-1].strip()
    numeric_matches = NUMBER_PATTERN.findall(text)
    if numeric_matches:
        return numeric_matches[-1]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"


def verify_answer(gold: str, predicted: str) -> bool:
    gold = str(gold).strip()
    predicted = str(predicted).strip()
    try:
        gold_num = float(gold)
        pred_num = float(predicted)
        return math.isclose(gold_num, pred_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == gold.lower()


def analyze_raw_output(text: str | None) -> dict[str, Any]:
    if text is None:
        return {
            "extracted_answer": "NOT_FOUND",
            "fallback_type": "not_found",
            "format_bucket": "not_found",
            "has_boxed": False,
            "boxed_count": 0,
        }
    boxed_matches = BOXED_PATTERN.findall(text)
    numeric_matches = NUMBER_PATTERN.findall(text)
    if boxed_matches:
        non_empty = [match.strip() for match in boxed_matches if match.strip()]
        if non_empty:
            extracted = non_empty[-1]
            return {
                "extracted_answer": extracted,
                "fallback_type": "boxed_non_empty",
                "format_bucket": "boxed",
                "has_boxed": True,
                "boxed_count": len(boxed_matches),
            }
        extracted = boxed_matches[-1].strip()
        return {
            "extracted_answer": extracted,
            "fallback_type": "boxed_empty",
            "format_bucket": "boxed_empty",
            "has_boxed": True,
            "boxed_count": len(boxed_matches),
        }
    for pattern in FINAL_ANSWER_PATTERNS:
        matched = re.findall(pattern, text, re.IGNORECASE)
        if matched:
            return {
                "extracted_answer": matched[-1].strip(),
                "fallback_type": "final_answer_phrase",
                "format_bucket": "final_answer",
                "has_boxed": False,
                "boxed_count": 0,
            }
    if numeric_matches:
        return {
            "extracted_answer": numeric_matches[-1],
            "fallback_type": "last_number",
            "format_bucket": "numeric_fallback",
            "has_boxed": False,
            "boxed_count": 0,
        }
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "extracted_answer": lines[-1] if lines else "NOT_FOUND",
        "fallback_type": "last_line" if lines else "not_found",
        "format_bucket": "line_fallback" if lines else "not_found",
        "has_boxed": False,
        "boxed_count": 0,
    }


def analyze_prediction_row(row: dict[str, str]) -> dict[str, Any]:
    raw_output = row.get("raw_output")
    if raw_output is not None and raw_output != "":
        return analyze_raw_output(raw_output)
    extracted = str(row.get("extracted_answer", "")).strip()
    if extracted:
        return {
            "extracted_answer": extracted,
            "fallback_type": "provided_prediction",
            "format_bucket": "provided_prediction",
            "has_boxed": False,
            "boxed_count": 0,
        }
    return {
        "extracted_answer": "NOT_FOUND",
        "fallback_type": "not_found",
        "format_bucket": "not_found",
        "has_boxed": False,
        "boxed_count": 0,
    }


def safe_div(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def aggregate_counts(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"rows": 0, "correct": 0})
    for row in rows:
        bucket_key = str(row.get(key, ""))
        buckets[bucket_key]["rows"] += 1
        buckets[bucket_key]["correct"] += int(bool(row.get("is_correct")))
    summary: list[dict[str, Any]] = []
    for bucket_key, stats in sorted(buckets.items()):
        summary.append(
            {
                key: bucket_key,
                "rows": stats["rows"],
                "correct": stats["correct"],
                "accuracy": round(safe_div(stats["correct"], stats["rows"]), 4),
            }
        )
    return summary


def build_binary_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    binary_rows = [row for row in rows if row.get("family") == "bit_manipulation" or row.get("label") == "binary"]
    regex_ok = [row for row in binary_rows if BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))]
    gold_leading_zero_rows = [row for row in binary_rows if str(row.get("gold_answer", "")).startswith("0")]
    leading_zero_ok = [
        row
        for row in gold_leading_zero_rows
        if BIT8_PATTERN.fullmatch(str(row.get("prediction", ""))) and str(row.get("prediction", "")).startswith("0")
    ]
    format_ok = [
        row
        for row in binary_rows
        if row.get("has_boxed") and BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))
    ]
    format_fail = [row for row in binary_rows if row not in format_ok]
    format_ok_but_wrong = [row for row in format_ok if not row.get("is_correct")]
    return {
        "rows": len(binary_rows),
        "boxed_extraction_success_rate": round(
            safe_div(sum(int(row.get("fallback_type") == "boxed_non_empty") for row in binary_rows), len(binary_rows)), 4
        ),
        "regex_exact_rate": round(safe_div(len(regex_ok), len(binary_rows)), 4),
        "leading_zero_retention_rate": round(safe_div(len(leading_zero_ok), len(gold_leading_zero_rows)), 4),
        "format_failure_rate": round(safe_div(len(format_fail), len(binary_rows)), 4),
        "format_ok_content_wrong_rate": round(safe_div(len(format_ok_but_wrong), len(format_ok)), 4),
        "solver_family_accuracy": aggregate_counts(binary_rows, "teacher_solver_candidate"),
    }


def render_markdown_summary(name: str, summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {name}")
    lines.append("")
    overall = summary["overall"]
    lines.append("## Overall")
    lines.append("")
    lines.append(f"- rows: `{overall['rows']}`")
    lines.append(f"- correct: `{overall['correct']}`")
    lines.append(f"- accuracy: `{overall['accuracy']:.4f}`")
    lines.append("")

    def add_table(title: str, rows: list[dict[str, Any]], key_name: str) -> None:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| {key_name} | rows | correct | accuracy |")
        lines.append("| --- | ---: | ---: | ---: |")
        for row in rows:
            lines.append(f"| `{row[key_name]}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |")
        lines.append("")

    add_table("Family accuracy", summary["by_family"], "family_short")
    add_table("Template subtype accuracy", summary["by_template_subtype"], "template_subtype")
    add_table("Answer type accuracy", summary["by_answer_type"], "answer_type")
    add_table("Prompt length buckets", summary["by_prompt_len_bucket"], "prompt_len_bucket")
    add_table("Num examples", summary["by_num_examples"], "num_examples")

    binary_metrics = summary["binary_metrics"]
    lines.append("## Binary metrics")
    lines.append("")
    for key in (
        "rows",
        "boxed_extraction_success_rate",
        "regex_exact_rate",
        "leading_zero_retention_rate",
        "format_failure_rate",
        "format_ok_content_wrong_rate",
    ):
        lines.append(f"- {key}: `{binary_metrics[key]}`")
    lines.append("")
    lines.append("### Binary solver-family accuracy")
    lines.append("")
    lines.append("| teacher_solver_candidate | rows | correct | accuracy |")
    lines.append("| --- | ---: | ---: | ---: |")
    for row in binary_metrics["solver_family_accuracy"]:
        lines.append(
            f"| `{row['teacher_solver_candidate']}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_analysis_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("id", ""): row for row in rows}


def score_prediction_csv(
    *,
    predictions_path: Path,
    analysis_index: dict[str, dict[str, str]],
    output_root: Path,
    report_root: Path,
) -> dict[str, Any]:
    prediction_rows = load_csv_rows(predictions_path)
    row_level: list[dict[str, Any]] = []
    for row in prediction_rows:
        row_id = row.get("id", "")
        analysis = analysis_index.get(row_id, {})
        derived = analyze_prediction_row(row)
        gold = row.get("expected_answer") or row.get("answer") or analysis.get("answer", "")
        prediction = derived["extracted_answer"]
        family = analysis.get("family", row.get("family", ""))
        family_short = normalize_family_label({**analysis, **row})
        prompt_len = parse_int(analysis.get("prompt_len_chars"), 0)
        num_examples = parse_int(analysis.get("num_examples"), 0)
        scored = {
            "id": row_id,
            "gold_answer": gold,
            "prediction": prediction,
            "is_correct": verify_answer(str(gold), str(prediction)),
            "family": family,
            "family_short": family_short,
            "template_subtype": analysis.get("template_subtype", ""),
            "answer_type": analysis.get("answer_type", ""),
            "teacher_solver_candidate": analysis.get("teacher_solver_candidate", ""),
            "selection_tier": analysis.get("selection_tier", ""),
            "num_examples": num_examples,
            "prompt_len_chars": prompt_len,
            "prompt_len_bucket": prompt_len_bucket(prompt_len),
            "fallback_type": derived["fallback_type"],
            "format_bucket": derived["format_bucket"],
            "has_boxed": derived["has_boxed"],
            "boxed_count": derived["boxed_count"],
            "raw_output": row.get("raw_output", ""),
            "label": row.get("label", ""),
        }
        row_level.append(scored)

    summary = {
        "overall": {
            "rows": len(row_level),
            "correct": sum(int(row["is_correct"]) for row in row_level),
            "accuracy": round(safe_div(sum(int(row["is_correct"]) for row in row_level), len(row_level)), 4),
        },
        "by_family": aggregate_counts(row_level, "family_short"),
        "by_template_subtype": aggregate_counts(row_level, "template_subtype"),
        "by_answer_type": aggregate_counts(row_level, "answer_type"),
        "by_prompt_len_bucket": aggregate_counts(row_level, "prompt_len_bucket"),
        "by_num_examples": aggregate_counts(row_level, "num_examples"),
        "binary_metrics": build_binary_metrics(row_level),
    }

    stem = predictions_path.stem
    row_csv = output_root / f"{stem}_row_level.csv"
    summary_json = output_root / f"{stem}_summary.json"
    summary_md = report_root / f"{stem}_summary.md"
    fieldnames = [
        "id",
        "gold_answer",
        "prediction",
        "is_correct",
        "family",
        "family_short",
        "template_subtype",
        "answer_type",
        "teacher_solver_candidate",
        "selection_tier",
        "num_examples",
        "prompt_len_chars",
        "prompt_len_bucket",
        "fallback_type",
        "format_bucket",
        "has_boxed",
        "boxed_count",
        "label",
        "raw_output",
    ]
    write_csv(row_csv, row_level, fieldnames)
    write_json(summary_json, summary)
    write_text(summary_md, render_markdown_summary(stem, summary))
    return summary


def render_phase0_report(manifest: dict[str, Any]) -> str:
    lines = []
    lines.append("# Phase 0 Offline Eval Manifest")
    lines.append("")
    lines.append("## README-aligned evaluation assumptions")
    lines.append("")
    for key, value in manifest["readme_eval_assumptions"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Benchmark sets")
    lines.append("")
    lines.append("| set | rows | family_counts | selection_tier_counts | binary_focus_bucket_counts |")
    lines.append("| --- | ---: | --- | --- | --- |")
    for set_name, payload in manifest["benchmark_sets"].items():
        bucket_counts = payload.get("binary_focus_bucket_counts", {})
        lines.append(
            f"| `{set_name}` | {payload['rows']} | `{json.dumps(payload['family_counts'], ensure_ascii=False)}` | `{json.dumps(payload['selection_tier_counts'], ensure_ascii=False)}` | `{json.dumps(bucket_counts, ensure_ascii=False)}` |"
        )
    lines.append("")
    lines.append("## Binary holdout fold counts")
    lines.append("")
    lines.append("| holdout_kind | fold_counts |")
    lines.append("| --- | --- |")
    for holdout_kind, fold_counts in manifest["binary_holdouts"].items():
        lines.append(f"| `{holdout_kind}` | `{json.dumps(fold_counts, ensure_ascii=False)}` |")
    lines.append("")
    return "\n".join(lines)


def mark_status_rows(rows: list[dict[str, Any]], benchmark_name: str) -> list[dict[str, Any]]:
    marked = []
    for index, row in enumerate(rows, start=1):
        new_row = dict(row)
        new_row["benchmark_index"] = index
        new_row["benchmark_name"] = benchmark_name
        marked.append(new_row)
    return marked


def main() -> None:
    args = parse_args()
    ensure_dir(args.output_root)
    ensure_dir(args.report_root)

    analysis_rows = load_csv_rows(args.analysis_csv)
    analysis_index = build_analysis_index(analysis_rows)

    general_stable = mark_status_rows(build_general_stable_set(analysis_rows), "general_stable_set")
    binary_hard = mark_status_rows(build_binary_hard_set(analysis_rows), "binary_hard_set")
    symbol_watch = mark_status_rows(build_symbol_watch_set(analysis_rows), "symbol_watch_set")
    holdout_assignments = build_binary_holdout_assignments(analysis_rows)

    write_csv(args.output_root / "general_stable_set.csv", general_stable, benchmark_columns() + ["benchmark_index"])
    write_csv(args.output_root / "binary_hard_set.csv", binary_hard, benchmark_columns() + ["benchmark_index"])
    write_csv(args.output_root / "symbol_watch_set.csv", symbol_watch, benchmark_columns() + ["benchmark_index"])
    write_csv(
        args.output_root / "binary_holdout_assignments.csv",
        holdout_assignments,
        [
            "id",
            "family",
            "selection_tier",
            "template_subtype",
            "teacher_solver_candidate",
            "holdout_kind",
            "holdout_key",
            "fold",
            "num_examples",
            "bit_no_candidate_positions",
            "bit_multi_candidate_positions",
            "group_signature",
        ],
    )

    manifest = build_manifest(
        analysis_csv=args.analysis_csv,
        general_rows=general_stable,
        binary_rows=binary_hard,
        symbol_rows=symbol_watch,
        holdouts=holdout_assignments,
    )
    write_json(args.output_root / "phase0_eval_manifest.json", manifest)
    write_text(args.report_root / "phase0_eval_manifest.md", render_phase0_report(manifest))

    score_paths: list[Path] = []
    if not args.skip_score:
        if args.score_csv:
            score_paths.extend(args.score_csv)
        else:
            for default_path in (DEFAULT_RULE_BASE_600, DEFAULT_RULE_BASE_800):
                if default_path.exists():
                    score_paths.append(default_path)
    for path in score_paths:
        score_prediction_csv(
            predictions_path=path,
            analysis_index=analysis_index,
            output_root=args.output_root,
            report_root=args.report_root,
        )

    print("Phase 0 offline eval artifacts written to:")
    print(f"  artifacts: {args.output_root}")
    print(f"  reports:   {args.report_root}")
    print(f"  general_stable_set rows: {len(general_stable)}")
    print(f"  binary_hard_set rows: {len(binary_hard)}")
    print(f"  symbol_watch_set rows: {len(symbol_watch)}")
    print(f"  binary_holdout_assignments rows: {len(holdout_assignments)}")
    if score_paths:
        print("  scored CSVs:")
        for path in score_paths:
            print(f"    - {path}")


if __name__ == "__main__":
    main()
