from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
DEFAULT_OUTPUT_CSV = Path(__file__).resolve().parent / "output-csv" / "rule_based_binary_guarded_800_training_data.csv"
DEFAULT_MANIFEST_JSON = Path(__file__).resolve().parent / "output-csv" / "rule_based_binary_guarded_800_manifest.json"
DEFAULT_SAMPLE_TEMPLATE_CSV = (
    Path(__file__).resolve().parent / "output-csv" / "rule_based_adapter_readme_inference_samples_binary_guarded_template.csv"
)

BASE_FAMILY_QUOTAS = {
    "gravity_constant": 100,
    "unit_conversion": 100,
    "roman_numeral": 100,
    "text_decryption": 100,
    "bit_manipulation": 100,
    "symbol_equation": 100,
}
BONUS_FAMILY_QUOTAS = {
    "bit_manipulation": 100,
    "gravity_constant": 25,
    "unit_conversion": 25,
    "roman_numeral": 25,
    "text_decryption": 25,
}
DEFAULT_SUBSAMPLE_SIZE = sum(BASE_FAMILY_QUOTAS.values()) + sum(BONUS_FAMILY_QUOTAS.values())
DEFAULT_SEED = 42
INFERENCE_BINARY_SAMPLES = 10
INFERENCE_OTHER_SAMPLES = 4

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
SAMPLE_TEMPLATE_COLUMNS = ["label", "id", "expected_answer", "extracted_answer", "rendered_prompt", "raw_output"]
NON_BINARY_ANCHOR_FAMILIES = ("gravity_constant", "unit_conversion", "roman_numeral", "text_decryption")
STRONG_BINARY_SOLVERS = {
    "binary_affine_xor",
    "binary_two_bit_boolean",
    "binary_three_bit_boolean",
    "binary_byte_transform",
    "binary_bit_permutation_bijection",
    "binary_bit_permutation_independent",
}


@dataclass(frozen=True)
class SelectedRow:
    row: dict[str, str]
    rank_key: tuple[Any, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a safer 800-row baseline-compatible training CSV that strengthens binary coverage "
            "without reusing the old unsafe binary-heavy 800-row mix."
        )
    )
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--sample-template-csv", type=Path, default=DEFAULT_SAMPLE_TEMPLATE_CSV)
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
        "binary_structured_byte_not_formula": 80,
        "symbol_numeric_operator_formula": 72,
        "symbol_char_substitution": 68,
    }
    return priorities.get(solver, 50)


def structured_support_strength(row: dict[str, str]) -> int:
    safe_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    return max(safe_support * 10, abstract_support)


def rank_row(row: dict[str, str]) -> tuple[Any, ...]:
    payload = parse_family_payload(row)
    example_count = parse_int(row.get("num_examples", "0"), 0)
    same_operator = parse_int(row.get("symbol_same_operator_example_count", "0"), 0)
    hard_score = parse_float(row.get("hard_score", ""), 999.0)
    if hard_score is None:
        hard_score = 999.0
    example_payload = parse_int(str(payload.get("example_count", "0")), 0)
    return (
        -solver_priority(row),
        -max(example_count, example_payload),
        -same_operator,
        -structured_support_strength(row),
        hard_score,
        row.get("id", ""),
    )


def rank_binary_bonus_row(row: dict[str, str]) -> tuple[Any, ...]:
    solver = row.get("teacher_solver_candidate", "")
    safe_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    hard_score = parse_float(row.get("hard_score", ""), 999.0)
    if hard_score is None:
        hard_score = 999.0
    return (
        -(1 if solver in STRONG_BINARY_SOLVERS else 0),
        -safe_support,
        -abstract_support,
        -solver_priority(row),
        hard_score,
        row.get("id", ""),
    )


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


def is_strong_binary_bonus_candidate(row: dict[str, str]) -> bool:
    if row.get("family") != "bit_manipulation":
        return False
    if row.get("selection_tier") != "verified_trace_ready":
        return False
    solver = row.get("teacher_solver_candidate", "")
    if solver in STRONG_BINARY_SOLVERS:
        return True
    safe_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    return safe_support >= 4 or abstract_support >= 20


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


def select_base_rows(verified: list[dict[str, str]], seed: int) -> list[dict[str, str]]:
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in verified:
        family = row.get("family", "")
        if family in BASE_FAMILY_QUOTAS:
            by_family[family].append(row)
    selected: list[dict[str, str]] = []
    for index, family in enumerate(BASE_FAMILY_QUOTAS):
        family_rows = by_family.get(family, [])
        quota = BASE_FAMILY_QUOTAS[family]
        if len(family_rows) < quota:
            raise ValueError(f"Family {family} has only {len(family_rows)} verified rows; needs {quota}")
        family_selected = round_robin_select(
            make_selected(family_rows, rank_row),
            quota=quota,
            seed=seed + index,
            key_fn=lambda item: item.row.get("template_subtype", "unknown"),
        )
        selected.extend(family_selected)
    return selected


def select_bonus_rows(verified: list[dict[str, str]], used_ids: set[str], seed: int) -> list[dict[str, str]]:
    remaining = [row for row in verified if row["id"] not in used_ids]
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in remaining:
        family = row.get("family", "")
        if family in BONUS_FAMILY_QUOTAS:
            by_family[family].append(row)
    selected: list[dict[str, str]] = []
    for index, family in enumerate(BONUS_FAMILY_QUOTAS):
        family_rows = by_family.get(family, [])
        quota = BONUS_FAMILY_QUOTAS[family]
        if family == "bit_manipulation":
            family_rows = [row for row in family_rows if is_strong_binary_bonus_candidate(row)]
            ranker = rank_binary_bonus_row
            key_fn = lambda item: item.row.get("teacher_solver_candidate", "unknown")
        else:
            ranker = rank_row
            key_fn = lambda item: item.row.get("template_subtype", "unknown")
        if len(family_rows) < quota:
            raise ValueError(f"Bonus family {family} has only {len(family_rows)} candidate rows; needs {quota}")
        family_selected = round_robin_select(
            make_selected(family_rows, ranker),
            quota=quota,
            seed=seed + 100 + index,
            key_fn=key_fn,
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


def validate_output(rows: list[dict[str, str]], expected_size: int) -> None:
    if len(rows) != expected_size:
        raise ValueError(f"Expected {expected_size} rows, found {len(rows)}")
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate ids detected in output rows")
    for row in rows:
        if set(row) != set(OUTPUT_COLUMNS):
            raise ValueError(f"Unexpected output columns for row {row.get('id', '')}")
        if not row["generated_cot"].startswith("<think>") or not row["generated_cot"].endswith("</think>"):
            raise ValueError(f"generated_cot must be wrapped by <think>: {row['id']}")
        if not row["prompt"].strip() or not row["answer"].strip() or not row["label"].strip():
            raise ValueError(f"Missing prompt/answer/label content: {row['id']}")
        if row["label"] == "binary" and row["answer"] in row["generated_cot"]:
            raise ValueError(f"Binary trace should not repeat the final answer outside the box: {row['id']}")


def try_token_length_check(rows: list[dict[str, str]], model_path: Path | None) -> dict[str, Any]:
    if model_path is None:
        return {"status": "skipped", "reason": "model_path_not_provided"}
    try:
        from transformers import AutoTokenizer  # type: ignore
    except Exception as exc:
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


def build_sample_template(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(row)
    sample_rows: list[dict[str, str]] = []
    for label, target_count in [("binary", INFERENCE_BINARY_SAMPLES)] + [
        (FAMILY_LABELS[family], INFERENCE_OTHER_SAMPLES) for family in NON_BINARY_ANCHOR_FAMILIES + ("symbol_equation",)
    ]:
        pool = sorted(by_label.get(label, []), key=lambda item: item["id"])
        if len(pool) < target_count:
            raise ValueError(f"Not enough rows for inference sample template: {label} needs {target_count}")
        for row in pool[:target_count]:
            sample_rows.append(
                {
                    "label": row["label"],
                    "id": row["id"],
                    "expected_answer": row["answer"],
                    "extracted_answer": "",
                    "rendered_prompt": (
                        row["prompt"]
                        + "\nPlease put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`"
                    ),
                    "raw_output": "",
                }
            )
    return sorted(sample_rows, key=lambda item: (item["label"], item["id"]))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_manifest(source_rows: list[dict[str, str]], output_rows: list[dict[str, str]], args: argparse.Namespace) -> dict[str, Any]:
    selected_ids = {row["id"] for row in output_rows}
    source_index = {row["id"]: row for row in source_rows}
    family_counts = Counter(source_index[row_id]["family"] for row_id in selected_ids)
    subtype_counts = Counter(source_index[row_id].get("template_subtype", "unknown") for row_id in selected_ids)
    solver_counts = Counter(source_index[row_id].get("teacher_solver_candidate", "") for row_id in selected_ids)
    binary_selected = [source_index[row_id] for row_id in selected_ids if source_index[row_id]["family"] == "bit_manipulation"]
    binary_support_min = min(
        (
            max(
                parse_int(row.get("bit_structured_formula_safe_support", "0"), 0),
                parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0),
            )
            for row in binary_selected
        ),
        default=0,
    )
    return {
        "source_csv": str(args.source_csv),
        "output_csv": str(args.output_csv),
        "sample_template_csv": str(args.sample_template_csv),
        "subsample_size": args.subsample_size,
        "seed": args.seed,
        "base_family_quotas": BASE_FAMILY_QUOTAS,
        "bonus_family_quotas": BONUS_FAMILY_QUOTAS,
        "family_counts": dict(sorted(family_counts.items())),
        "template_subtype_counts": dict(sorted(subtype_counts.items())),
        "teacher_solver_counts": dict(sorted(solver_counts.items())),
        "binary_guardrails": {
            "uses_only_verified_trace_ready_rows": True,
            "binary_bonus_requires_strong_verified_rule": True,
            "binary_trace_does_not_repeat_final_answer_inside_think": True,
            "selected_binary_rows": len(binary_selected),
            "selected_binary_min_support_signal": binary_support_min,
        },
        "notes": [
            "README evaluation prioritizes boxed extraction, so binary traces avoid restating the final 8-bit answer outside the box.",
            "This 800-row mix replaces the old binary-heavy 300-row expansion with verified-only binary bonus rows plus non-binary anchors.",
            "Sample template CSV is a scaffold for future README-compatible adapter inference; extracted_answer and raw_output are intentionally blank.",
        ],
    }


def main() -> None:
    args = parse_args()
    if args.subsample_size != DEFAULT_SUBSAMPLE_SIZE:
        raise ValueError(
            f"subsample-size must equal {DEFAULT_SUBSAMPLE_SIZE} for the current quota design; got {args.subsample_size}"
        )
    source_rows = load_rows(args.source_csv)
    verified = verified_rows(source_rows)
    base_rows = select_base_rows(verified, seed=args.seed)
    used_ids = {row["id"] for row in base_rows}
    bonus_rows = select_bonus_rows(verified, used_ids=used_ids, seed=args.seed)
    selected_rows = base_rows + bonus_rows
    output_rows = build_output_rows(selected_rows)
    validate_output(output_rows, expected_size=args.subsample_size)
    sample_template_rows = build_sample_template(output_rows)
    token_check = try_token_length_check(output_rows, args.model_path)
    manifest = build_manifest(source_rows, output_rows, args)
    manifest["token_length_check"] = token_check
    write_csv(args.output_csv, output_rows, OUTPUT_COLUMNS)
    write_csv(args.sample_template_csv, sample_template_rows, SAMPLE_TEMPLATE_COLUMNS)
    args.manifest_json.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_json.write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote training CSV: {args.output_csv}")
    print(f"Wrote sample template CSV: {args.sample_template_csv}")
    print(f"Wrote manifest: {args.manifest_json}")
    print(json.dumps(manifest["family_counts"], ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
