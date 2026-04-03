from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
DEFAULT_DATASET_CSV = Path(__file__).resolve().parent / "artifacts" / "phase2_2_1_symbol_specialist_training_data.csv"
DEFAULT_MANIFEST_JSON = Path(__file__).resolve().parent / "artifacts" / "phase2_2_1_symbol_specialist_manifest.json"
DEFAULT_SEED = 42
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
    "query_raw",
    "teacher_solver_candidate",
    "selection_tier",
    "verified_trace_ready",
    "analysis_notes",
    "family_analysis_json",
    "suspect_label",
    "symbol_query_operator",
    "symbol_same_operator_example_count",
    "symbol_numeric_formula_name",
}


@dataclass(frozen=True)
class SelectedRow:
    row: dict[str, str]
    rank_key: tuple[Any, ...]


@dataclass(frozen=True)
class OutputRecord:
    output_id: str
    source_id: str
    prompt: str
    answer: str
    generated_cot: str
    assistant_style: str
    output_origin: str
    source_selection_tier: str

    def to_csv_row(self) -> dict[str, str]:
        return {
            "id": self.output_id,
            "prompt": self.prompt,
            "answer": self.answer,
            "generated_cot": self.generated_cot,
            "label": "symbol",
            "assistant_style": self.assistant_style,
            "source_selection_tier": self.source_selection_tier,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the Phase 2.2.1 numeric-only symbol specialist dataset that removes glyph rows, "
            "adds verified boxed-only siblings, and keeps only high-confidence numeric answer-only rows."
        )
    )
    parser.add_argument("--mode", choices=("build-dataset", "preview"), default="build-dataset")
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--dataset-csv", type=Path, default=DEFAULT_DATASET_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--preview-rows", type=int, default=6)
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
    if not rows:
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


def trace_group_key(row: dict[str, str]) -> str:
    return row.get("symbol_numeric_formula_name", "").strip() or row.get("symbol_query_operator", "").strip() or "unknown"


def answer_only_group_key(row: dict[str, str]) -> str:
    return row.get("symbol_query_operator", "").strip() or "unknown"


def trace_rank(row: dict[str, str]) -> tuple[Any, ...]:
    return (
        row.get("symbol_numeric_formula_name", "").strip(),
        -parse_int(row.get("symbol_same_operator_example_count", "0"), 0),
        row.get("symbol_query_operator", "").strip(),
        row.get("id", ""),
    )


def answer_only_rank(row: dict[str, str]) -> tuple[Any, ...]:
    formula_backed = is_formula_backed_answer_only(row)
    return (
        0 if formula_backed else 1,
        -parse_int(row.get("symbol_same_operator_example_count", "0"), 0),
        row.get("analysis_notes", "").strip(),
        row.get("symbol_numeric_formula_name", "").strip(),
        row.get("id", ""),
    )


def verified_symbol_trace_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        if row.get("family") != "symbol_equation":
            continue
        if row.get("template_subtype") != "numeric_2x2":
            continue
        if row.get("selection_tier") != "verified_trace_ready":
            continue
        if not parse_bool(row.get("verified_trace_ready", "false")):
            continue
        if not row.get("teacher_solver_candidate", "").strip():
            continue
        selected.append(row)
    return selected


def is_formula_backed_answer_only(row: dict[str, str]) -> bool:
    return (
        row.get("selection_tier") == "answer_only_keep"
        and row.get("template_subtype") == "numeric_2x2"
        and not parse_bool(row.get("suspect_label", "false"))
        and bool(row.get("symbol_numeric_formula_name", "").strip())
    )


def is_multi_evidence_answer_only(row: dict[str, str]) -> bool:
    return (
        row.get("selection_tier") == "answer_only_keep"
        and row.get("template_subtype") == "numeric_2x2"
        and not parse_bool(row.get("suspect_label", "false"))
        and parse_int(row.get("symbol_same_operator_example_count", "0"), 0) >= 3
    )


def high_confidence_answer_only_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        if row.get("family") != "symbol_equation":
            continue
        if row.get("template_subtype") != "numeric_2x2":
            continue
        if is_formula_backed_answer_only(row) or is_multi_evidence_answer_only(row):
            selected.append(row)
    return selected


def order_rows(rows: list[dict[str, str]], seed: int, ranker: Callable[[dict[str, str]], tuple[Any, ...]], key_fn: Callable[[SelectedRow], str]) -> list[dict[str, str]]:
    return round_robin_select(make_selected(rows, ranker), quota=len(rows), seed=seed, key_fn=key_fn)


def humanize_rule_name(rule_name: str) -> str:
    return rule_name.replace("_", " ").strip() or "verified_symbol_rule"


def split_query_operands(query_text: str, operator: str) -> tuple[str, str]:
    if operator and operator in query_text:
        left, right = query_text.split(operator, 1)
        if left.strip() and right.strip():
            return left.strip(), right.strip()
    return query_text.strip(), "rhs"


def sanitize_query_token(token: str, final_answer: str, fallback: str) -> str:
    token = token.strip()
    return fallback if token == final_answer else token


def build_symbol_micro_trace(row: dict[str, str]) -> str:
    operator = row.get("symbol_query_operator", "").strip()
    query_text = row.get("query_raw", "").strip()
    answer_text = row.get("answer", "").strip()
    formula = row.get("symbol_numeric_formula_name", "").strip() or "verified_symbol_rule"
    same_op_count = parse_int(row.get("symbol_same_operator_example_count", "0"), 0)
    lhs, rhs = split_query_operands(query_text, operator)
    query_ref = sanitize_query_token(query_text, answer_text, "query_expr")
    lhs_ref = sanitize_query_token(lhs, answer_text, "lhs_operand")
    rhs_ref = sanitize_query_token(rhs, answer_text, "rhs_operand")
    operator_ref = json.dumps(operator, ensure_ascii=False)
    lines = [
        f"op={operator_ref}",
        f"query={query_ref}",
        f"lhs={lhs_ref}",
        f"rhs={rhs_ref}",
        f"rule={formula}",
        f"rule_text={humanize_rule_name(formula)}",
        f"support=same_operator_examples_{max(same_op_count, 1)}",
        "apply=rule(lhs,rhs)",
        "constraints=match_examples,box_only_final",
    ]
    return "<think>" + "; ".join(lines) + "</think>"


def answer_only_origin(row: dict[str, str]) -> str:
    if is_formula_backed_answer_only(row):
        return "answer_only_formula_backed"
    return "answer_only_multi_evidence"


def build_output_records(
    trace_rows: list[dict[str, str]],
    boxed_sibling_rows: list[dict[str, str]],
    answer_only_rows: list[dict[str, str]],
) -> list[OutputRecord]:
    output_records: list[OutputRecord] = []
    for row in trace_rows:
        output_records.append(
            OutputRecord(
                output_id=row["id"],
                source_id=row["id"],
                prompt=row["prompt"],
                answer=row["answer"],
                generated_cot=build_symbol_micro_trace(row),
                assistant_style="trace_boxed",
                output_origin="verified_trace_core",
                source_selection_tier=row["selection_tier"],
            )
        )
    for row in boxed_sibling_rows:
        output_records.append(
            OutputRecord(
                output_id=f"{row['id']}__boxed_sibling_v221",
                source_id=row["id"],
                prompt=row["prompt"],
                answer=row["answer"],
                generated_cot="",
                assistant_style="boxed_only",
                output_origin="verified_boxed_sibling",
                source_selection_tier=row["selection_tier"],
            )
        )
    for row in answer_only_rows:
        output_records.append(
            OutputRecord(
                output_id=f"{row['id']}__hq_answer_only_v221",
                source_id=row["id"],
                prompt=row["prompt"],
                answer=row["answer"],
                generated_cot="",
                assistant_style="boxed_only",
                output_origin=answer_only_origin(row),
                source_selection_tier=row["selection_tier"],
            )
        )
    return output_records


def validate_output(
    records: list[OutputRecord],
    source_index: dict[str, dict[str, str]],
    expected_size: int,
) -> None:
    if len(records) != expected_size:
        raise ValueError(f"Expected {expected_size} rows, found {len(records)}")
    output_ids = [record.output_id for record in records]
    if len(output_ids) != len(set(output_ids)):
        raise ValueError("Duplicate output ids detected")
    for record in records:
        source_row = source_index.get(record.source_id)
        if source_row is None:
            raise ValueError(f"Unknown source row: {record.source_id}")
        if source_row.get("family") != "symbol_equation":
            raise ValueError(f"Non-symbol source row leaked into dataset: {record.source_id}")
        if source_row.get("template_subtype") != "numeric_2x2":
            raise ValueError(f"Non-numeric symbol row leaked into dataset: {record.source_id}")
        if source_row.get("selection_tier") in {"manual_audit_priority", "exclude_suspect"}:
            raise ValueError(f"manual/exclude row leaked into dataset: {record.source_id}")
        if record.assistant_style == "trace_boxed":
            if source_row.get("selection_tier") != "verified_trace_ready":
                raise ValueError(f"trace_boxed row must come from verified source: {record.output_id}")
            if not record.generated_cot.startswith("<think>") or not record.generated_cot.endswith("</think>"):
                raise ValueError(f"Trace rows must be wrapped by <think>: {record.output_id}")
            if "\\boxed{" in record.generated_cot:
                raise ValueError(f"Trace rows must not contain boxed answer text: {record.output_id}")
            if "apply=rule(lhs,rhs)" not in record.generated_cot:
                raise ValueError(f"Trace rows must use the phase2_2_1 micro DSL: {record.output_id}")
        elif record.assistant_style == "boxed_only":
            if record.generated_cot:
                raise ValueError(f"boxed_only rows must not carry generated_cot: {record.output_id}")
        else:
            raise ValueError(f"Unsupported assistant_style: {record.assistant_style}")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_manifest(
    *,
    source_rows: list[dict[str, str]],
    source_index: dict[str, dict[str, str]],
    records: list[OutputRecord],
    trace_rows: list[dict[str, str]],
    boxed_sibling_rows: list[dict[str, str]],
    answer_only_rows: list[dict[str, str]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    family_counts = Counter(source_index[record.source_id]["family"] for record in records)
    source_tier_counts = Counter(source_index[record.source_id]["selection_tier"] for record in records)
    style_counts = Counter(record.assistant_style for record in records)
    origin_counts = Counter(record.output_origin for record in records)
    subtype_counts = Counter(source_index[record.source_id].get("template_subtype", "unknown") for record in records)
    operator_counts = Counter(source_index[record.source_id].get("symbol_query_operator", "") for record in records)
    formula_counts = Counter(source_index[record.source_id].get("symbol_numeric_formula_name", "") for record in records)
    analysis_note_counts = Counter(row.get("analysis_notes", "") for row in answer_only_rows)
    answer_only_origin_counts = Counter(answer_only_origin(row) for row in answer_only_rows)
    selected_answer_only_ids = {row["id"] for row in answer_only_rows}
    formula_backed_ids = {row["id"] for row in answer_only_rows if is_formula_backed_answer_only(row)}
    multi_evidence_ids = {row["id"] for row in answer_only_rows if is_multi_evidence_answer_only(row)}
    all_symbol_rows = [row for row in source_rows if row.get("family") == "symbol_equation"]
    glyph_rows = [row for row in all_symbol_rows if row.get("template_subtype") == "glyph_len5"]
    numeric_answer_only_all = [
        row
        for row in all_symbol_rows
        if row.get("template_subtype") == "numeric_2x2" and row.get("selection_tier") == "answer_only_keep"
    ]
    numeric_answer_only_excluded = len(numeric_answer_only_all) - len(answer_only_rows)
    query_equals_answer_rows = sum(
        1 for row in trace_rows if row.get("query_raw", "").strip() == row.get("answer", "").strip()
    )
    return {
        "dataset_version": "v2-2-1",
        "source_csv": str(args.source_csv),
        "dataset_csv": str(args.dataset_csv),
        "manifest_json": str(args.manifest_json),
        "seed": args.seed,
        "subsample_size": len(records),
        "unique_source_id_count": len(trace_rows) + len(answer_only_rows),
        "verified_trace_rows": len(trace_rows),
        "verified_boxed_sibling_rows": len(boxed_sibling_rows),
        "high_confidence_answer_only_rows": len(answer_only_rows),
        "family_counts": dict(sorted(family_counts.items())),
        "source_selection_tier_counts": dict(sorted(source_tier_counts.items())),
        "assistant_style_counts": dict(sorted(style_counts.items())),
        "output_origin_counts": dict(sorted(origin_counts.items())),
        "template_subtype_counts": dict(sorted(subtype_counts.items())),
        "symbol_query_operator_counts": dict(sorted(operator_counts.items())),
        "symbol_numeric_formula_counts": dict(sorted(formula_counts.items())),
        "phase2_2_1_selected_answer_only_analysis_notes": dict(sorted(analysis_note_counts.items())),
        "symbol_phase2_2_1_design": {
            "training_scope": "numeric_only_symbol_specialist",
            "trace_rows_from_verified_numeric": len(trace_rows),
            "boxed_sibling_rows_from_verified_numeric": len(boxed_sibling_rows),
            "formula_backed_answer_only_rows": len(formula_backed_ids),
            "multi_evidence_answer_only_rows": len(multi_evidence_ids),
            "answer_only_overlap_rows": len(formula_backed_ids & multi_evidence_ids),
            "answer_only_origin_counts": dict(sorted(answer_only_origin_counts.items())),
            "glyph_rows_used": 0,
            "glyph_rows_excluded": len(glyph_rows),
            "numeric_answer_only_rows_excluded": numeric_answer_only_excluded,
            "manual_rows_used": 0,
            "exclude_rows_used": 0,
            "trace_style": "micro_dsl_numeric_symbol",
            "trace_avoids_repeating_final_answer_inside_think": True,
            "query_equals_answer_rows_sanitized": query_equals_answer_rows,
            "selected_answer_only_source_ids": len(selected_answer_only_ids),
        },
        "selection_policy": {
            "trace_include": [
                "symbol_equation + numeric_2x2 + verified_trace_ready + teacher_solver_candidate present",
            ],
            "boxed_sibling_include": [
                "Duplicate boxed-only supervision from the same verified numeric source rows used for trace_boxed",
            ],
            "high_confidence_answer_only_include": [
                "symbol_equation + numeric_2x2 + answer_only_keep + symbol_numeric_formula_name present",
                "symbol_equation + numeric_2x2 + answer_only_keep + symbol_same_operator_example_count >= 3",
            ],
            "exclude": [
                "glyph_len5 all rows",
                "numeric_2x2 + manual_audit_priority",
                "numeric_2x2 + exclude_suspect",
                "numeric_2x2 + answer_only_keep residual rows that are neither formula-backed nor same-operator>=3",
            ],
        },
        "notes": [
            "README.md evaluation is boxed-first Accuracy, so phase2_2_1 keeps final answers in boxed output and removes answer repetition from <think>.",
            "The phase2_2 analysis showed glyph_len5 stayed 0/20 despite 823 answer-only rows, so glyph is excluded entirely from this dataset.",
            "This dataset keeps numeric_2x2 verified trace as the core, adds same-source boxed siblings for closure, and only retains high-confidence numeric answer-only rows.",
            "The output schema matches the existing assistant-only trainer notebook: id,prompt,answer,generated_cot,label,assistant_style,source_selection_tier.",
        ],
    }


def build_dataset(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source_rows = load_rows(args.source_csv)
    verified = verified_symbol_trace_rows(source_rows)
    answer_only = high_confidence_answer_only_rows(source_rows)
    trace_rows = order_rows(verified, seed=args.seed, ranker=trace_rank, key_fn=lambda item: trace_group_key(item.row))
    boxed_sibling_rows = order_rows(verified, seed=args.seed + 100, ranker=trace_rank, key_fn=lambda item: answer_only_group_key(item.row))
    answer_only_rows = order_rows(
        answer_only,
        seed=args.seed + 200,
        ranker=answer_only_rank,
        key_fn=lambda item: answer_only_group_key(item.row),
    )
    source_index = {row["id"]: row for row in source_rows}
    records = build_output_records(trace_rows, boxed_sibling_rows, answer_only_rows)
    validate_output(
        records,
        source_index=source_index,
        expected_size=len(trace_rows) + len(boxed_sibling_rows) + len(answer_only_rows),
    )
    csv_rows = [record.to_csv_row() for record in records]
    write_csv(args.dataset_csv, csv_rows, OUTPUT_COLUMNS)
    manifest = build_manifest(
        source_rows=source_rows,
        source_index=source_index,
        records=records,
        trace_rows=trace_rows,
        boxed_sibling_rows=boxed_sibling_rows,
        answer_only_rows=answer_only_rows,
        args=args,
    )
    ensure_parent(args.manifest_json)
    args.manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return csv_rows, manifest


def render_assistant_message(row: dict[str, str]) -> str:
    if row["assistant_style"] == "trace_boxed":
        return f"{row['generated_cot']}\n\n\\boxed{{{row['answer']}}}"
    if row["assistant_style"] == "boxed_only":
        return f"\\boxed{{{row['answer']}}}"
    raise ValueError(f"Unsupported assistant_style: {row['assistant_style']}")


def preview_rows(path: Path, preview_count: int) -> None:
    rows = load_dataset_rows(path)
    print(f"Previewing {min(preview_count, len(rows))} / {len(rows)} rows from {path}")
    for index, row in enumerate(rows[:preview_count], start=1):
        print(f"[{index}] {row['id']} style={row['assistant_style']} tier={row['source_selection_tier']}")
        print(render_assistant_message(row))
        print("-" * 80)


def main() -> None:
    args = parse_args()
    if args.mode == "build-dataset":
        rows, manifest = build_dataset(args)
        print(f"Wrote {len(rows)} rows to {args.dataset_csv}")
        print(f"Wrote manifest to {args.manifest_json}")
        print(json.dumps(manifest["symbol_phase2_2_1_design"], ensure_ascii=False, indent=2))
        return
    preview_rows(args.dataset_csv, preview_count=args.preview_rows)


if __name__ == "__main__":
    main()
