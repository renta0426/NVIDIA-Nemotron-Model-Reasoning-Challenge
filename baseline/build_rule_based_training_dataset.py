from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_verified_trace_ready_v1.csv"
DEFAULT_OUTPUT_CSV = Path(__file__).resolve().parent / "rule_based_verified_600_training_data.csv"
DEFAULT_MANIFEST_JSON = Path(__file__).resolve().parent / "rule_based_verified_600_training_manifest.json"
DEFAULT_SUBSAMPLE_SIZE = 600
DEFAULT_SEED = 42
TARGET_FAMILY_QUOTAS = {
    "gravity_constant": 100,
    "unit_conversion": 100,
    "roman_numeral": 100,
    "text_decryption": 100,
    "bit_manipulation": 100,
    "symbol_equation": 100,
}
FAMILY_LABELS = {
    "gravity_constant": "gravity",
    "unit_conversion": "unit",
    "roman_numeral": "roman",
    "text_decryption": "text",
    "bit_manipulation": "binary",
    "symbol_equation": "symbol",
}
REQUIRED_COLUMNS = {
    "id",
    "prompt",
    "answer",
    "family",
    "template_subtype",
    "teacher_solver_candidate",
    "selection_tier",
    "family_analysis_json",
}
OUTPUT_COLUMNS = ["id", "prompt", "answer", "generated_cot", "label"]


@dataclass(frozen=True)
class SelectedRow:
    row: dict[str, str]
    rank_key: tuple[Any, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a baseline-compatible external CSV with 600 verified rows and "
            "rule-based <think> traces derived from cuda-train-data-analysis-v1 artifacts."
        )
    )
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--subsample-size", type=int, default=DEFAULT_SUBSAMPLE_SIZE)
    parser.add_argument("--model-path", type=Path, default=None)
    return parser.parse_args()


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def parse_float(value: str, default: float | None = None) -> float | None:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header is missing: {path}")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
        return [dict(row) for row in reader]


def parse_family_payload(row: dict[str, str]) -> dict[str, Any]:
    text = row.get("family_analysis_json", "")
    if not text:
        return {}
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        return {}
    return {}


def solver_priority(row: dict[str, str]) -> int:
    solver = row.get("teacher_solver_candidate", "")
    priorities = {
        "roman_standard": 100,
        "gravity_numeric_rule": 100,
        "unit_numeric_rule": 100,
        "text_char_substitution": 95,
        "text_word_dictionary": 90,
        "binary_structured_byte_formula_manual": 95,
        "binary_structured_byte_formula": 92,
        "binary_structured_byte_formula_abstract": 85,
        "binary_byte_transform": 84,
        "binary_affine_xor": 82,
        "binary_three_bit_boolean": 80,
        "binary_two_bit_boolean": 78,
        "binary_bit_permutation_bijection": 76,
        "binary_bit_permutation_independent": 74,
        "symbol_numeric_operator_formula": 70,
        "symbol_char_substitution": 68,
    }
    return priorities.get(solver, 50)


def rank_row(row: dict[str, str]) -> tuple[Any, ...]:
    payload = parse_family_payload(row)
    example_count = parse_int(row.get("num_examples", "0"), 0)
    same_operator = parse_int(row.get("symbol_same_operator_example_count", "0"), 0)
    structured_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    hard_score = parse_float(row.get("hard_score", ""), 999.0)
    if hard_score is None:
        hard_score = 999.0
    example_payload = parse_int(str(payload.get("example_count", "0")), 0)
    return (
        -solver_priority(row),
        -max(example_count, example_payload),
        -same_operator,
        -max(structured_support, abstract_support),
        hard_score,
        row.get("id", ""),
    )


def verified_rows(rows: list[dict[str, str]]) -> list[SelectedRow]:
    selected: list[SelectedRow] = []
    for row in rows:
        if row.get("selection_tier") != "verified_trace_ready":
            continue
        if not parse_bool(row.get("verified_trace_ready", "true")):
            continue
        if not row.get("teacher_solver_candidate", ""):
            continue
        selected.append(SelectedRow(row=row, rank_key=rank_row(row)))
    return selected


def subtype_round_robin(rows: list[SelectedRow], quota: int, seed: int) -> list[dict[str, str]]:
    by_subtype: dict[str, list[SelectedRow]] = defaultdict(list)
    for item in rows:
        by_subtype[item.row.get("template_subtype", "unknown")].append(item)
    ordered_subtypes = sorted(by_subtype)
    rng = random.Random(seed)
    for subtype in ordered_subtypes:
        by_subtype[subtype].sort(key=lambda item: item.rank_key)
    shuffled_subtypes = ordered_subtypes[:]
    rng.shuffle(shuffled_subtypes)
    queues = {subtype: deque(by_subtype[subtype]) for subtype in shuffled_subtypes}
    selected: list[dict[str, str]] = []
    while len(selected) < quota and queues:
        for subtype in list(shuffled_subtypes):
            queue = queues.get(subtype)
            if not queue:
                continue
            selected.append(queue.popleft().row)
            if len(selected) >= quota:
                break
            if not queue:
                queues.pop(subtype, None)
        shuffled_subtypes = [subtype for subtype in shuffled_subtypes if subtype in queues]
    if len(selected) != quota:
        available = sum(len(items) for items in by_subtype.values())
        raise ValueError(f"Unable to satisfy quota {quota}; only {available} rows available")
    return selected


def select_rows(rows: list[dict[str, str]], subsample_size: int, seed: int) -> list[dict[str, str]]:
    verified = verified_rows(rows)
    by_family: dict[str, list[SelectedRow]] = defaultdict(list)
    for item in verified:
        family = item.row.get("family", "")
        if family in TARGET_FAMILY_QUOTAS:
            by_family[family].append(item)
    if subsample_size != sum(TARGET_FAMILY_QUOTAS.values()):
        raise ValueError(
            f"subsample-size must equal {sum(TARGET_FAMILY_QUOTAS.values())} for the current quota design; got {subsample_size}"
        )
    selected: list[dict[str, str]] = []
    for index, family in enumerate(TARGET_FAMILY_QUOTAS):
        family_rows = by_family.get(family, [])
        quota = TARGET_FAMILY_QUOTAS[family]
        if len(family_rows) < quota:
            raise ValueError(f"Family {family} has only {len(family_rows)} verified rows; needs {quota}")
        selected.extend(subtype_round_robin(family_rows, quota, seed + index))
    return selected


def humanize_rule_name(rule_name: str) -> str:
    if not rule_name:
        return "verified transformation"
    return rule_name.replace("_", " ")


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
    if solver in {"binary_structured_byte_formula", "binary_structured_byte_formula_manual", "binary_structured_byte_formula_abstract"}:
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
    if detail:
        return humanize_rule_name(str(detail))
    return humanize_rule_name(solver)


def build_bit_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    query = row.get("bit_query_binary", "").strip() or row.get("query_raw", "").strip()
    description = bit_rule_description(row, payload)
    return (
        f"<think>The examples match the verified bit rule {description}. "
        f"Applying that same transformation to {query} gives {row['answer']}.</think>"
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


def build_generated_cot(row: dict[str, str]) -> str:
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


def build_output_rows(selected_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output_rows: list[dict[str, str]] = []
    for row in selected_rows:
        output_rows.append(
            {
                "id": row["id"],
                "prompt": row["prompt"],
                "answer": row["answer"],
                "generated_cot": build_generated_cot(row),
                "label": FAMILY_LABELS[row["family"]],
            }
        )
    return output_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def try_token_length_check(rows: list[dict[str, str]], model_path: Path | None) -> dict[str, Any]:
    if model_path is None:
        return {"status": "skipped", "reason": "model_path_not_provided"}
    try:
        from transformers import AutoTokenizer  # type: ignore
    except Exception as exc:  # pragma: no cover - optional runtime path
        return {"status": "skipped", "reason": f"transformers_unavailable: {exc}"}
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    max_length = 0
    longest_id = ""
    for row in rows:
        user_msg = row["prompt"] + "\nPut your final answer inside \\boxed{}."
        assistant_msg = f"{row['generated_cot']}\n\n\\boxed{{{row['answer']}}}"
        text = tokenizer.apply_chat_template(
            [
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg},
            ],
            tokenize=False,
            add_generation_prompt=False,
        )
        token_count = len(tokenizer(text, add_special_tokens=False)["input_ids"])
        if token_count > max_length:
            max_length = token_count
            longest_id = row["id"]
    return {"status": "ok", "max_length": max_length, "longest_id": longest_id, "limit": 2048}


def validate_output(rows: list[dict[str, str]]) -> None:
    if len(rows) != DEFAULT_SUBSAMPLE_SIZE:
        raise ValueError(f"Expected {DEFAULT_SUBSAMPLE_SIZE} rows, found {len(rows)}")
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate ids detected in output rows")
    for row in rows:
        if set(row) != set(OUTPUT_COLUMNS):
            raise ValueError(f"Unexpected output columns for row {row.get('id', '')}")
        if not row["generated_cot"].startswith("<think>"):
            raise ValueError(f"generated_cot must start with <think>: {row['id']}")
        if not row["generated_cot"].endswith("</think>"):
            raise ValueError(f"generated_cot must end with </think>: {row['id']}")
        if not row["prompt"].strip() or not row["answer"].strip() or not row["label"].strip():
            raise ValueError(f"Missing prompt/answer/label content: {row['id']}")


def build_manifest(source_rows: list[dict[str, str]], output_rows: list[dict[str, str]], args: argparse.Namespace) -> dict[str, Any]:
    selected_ids = {row["id"] for row in output_rows}
    source_index = {row["id"]: row for row in source_rows}
    family_counts = Counter(source_index[row_id]["family"] for row_id in selected_ids)
    subtype_counts = Counter(source_index[row_id].get("template_subtype", "unknown") for row_id in selected_ids)
    solver_counts = Counter(source_index[row_id].get("teacher_solver_candidate", "") for row_id in selected_ids)
    return {
        "source_csv": str(args.source_csv),
        "output_csv": str(args.output_csv),
        "subsample_size": args.subsample_size,
        "seed": args.seed,
        "selection_tier": "verified_trace_ready",
        "family_quotas": TARGET_FAMILY_QUOTAS,
        "family_counts": dict(sorted(family_counts.items())),
        "template_subtype_counts": dict(sorted(subtype_counts.items())),
        "teacher_solver_counts": dict(sorted(solver_counts.items())),
        "notes": [
            "Built from solver-verified rows only.",
            "Training CSV is baseline-compatible: id,prompt,answer,generated_cot,label.",
            "generated_cot is rule-based short trace, not external LLM-generated CoT.",
        ],
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    source_rows = load_rows(args.source_csv)
    selected_rows = select_rows(source_rows, args.subsample_size, args.seed)
    output_rows = build_output_rows(selected_rows)
    validate_output(output_rows)
    token_check = try_token_length_check(output_rows, args.model_path)
    manifest = build_manifest(source_rows, output_rows, args)
    manifest["token_length_check"] = token_check
    write_csv(args.output_csv, output_rows)
    write_manifest(args.manifest_json, manifest)
    print(f"Wrote training CSV: {args.output_csv}")
    print(f"Wrote manifest: {args.manifest_json}")
    print(json.dumps(manifest["family_counts"], ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()