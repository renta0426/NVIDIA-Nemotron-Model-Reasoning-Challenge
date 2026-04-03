from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
DEFAULT_DATASET_CSV = Path(__file__).resolve().parent / "artifacts" / "phase2_1_2_binary_specialist_training_data.csv"
DEFAULT_MANIFEST_JSON = Path(__file__).resolve().parent / "artifacts" / "phase2_1_2_binary_specialist_manifest.json"
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
    "teacher_solver_candidate",
    "selection_tier",
    "verified_trace_ready",
    "family_analysis_json",
}
BOXED_SIBLING_SUBTYPE_QUOTAS = {
    "bit_structured_byte_formula": 320,
    "bit_other": 95,
    "bit_permutation_inversion": 30,
}
DEFAULT_BOXED_SIBLING_ROWS = sum(BOXED_SIBLING_SUBTYPE_QUOTAS.values())


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
            "label": "binary",
            "assistant_style": self.assistant_style,
            "source_selection_tier": self.source_selection_tier,
        }


@dataclass(frozen=True)
class ExprNode:
    name: str
    args: tuple["ExprNode", ...] = ()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the Phase 2.1.2 binary specialist dataset that replaces broad answer-only rows "
            "with verified boxed-only siblings and uses a short micro-DSL trace."
        )
    )
    parser.add_argument("--mode", choices=("build-dataset", "preview"), default="build-dataset")
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--dataset-csv", type=Path, default=DEFAULT_DATASET_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--preview-rows", type=int, default=4)
    parser.add_argument("--boxed-sibling-rows", type=int, default=DEFAULT_BOXED_SIBLING_ROWS)
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


def solver_priority(row: dict[str, str]) -> int:
    solver = row.get("teacher_solver_candidate", "")
    priorities = {
        "binary_structured_byte_formula": 100,
        "binary_structured_byte_formula_abstract": 97,
        "binary_byte_transform": 96,
        "binary_affine_xor": 95,
        "binary_bit_permutation_bijection": 92,
        "binary_bit_permutation_independent": 90,
        "binary_two_bit_boolean": 88,
        "binary_three_bit_boolean": 86,
        "binary_structured_byte_not_formula": 80,
    }
    return priorities.get(solver, 50)


def structured_support_strength(row: dict[str, str]) -> int:
    safe_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    distinct_exact = parse_int(row.get("bit_structured_formula_abstract_distinct_exact", "0"), 0)
    return max(safe_support * 100 + distinct_exact, abstract_support * 10 + distinct_exact)


def structured_support_bin(row: dict[str, str]) -> int:
    safe_support = parse_int(row.get("bit_structured_formula_safe_support", "0"), 0)
    abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", "0"), 0)
    distinct_exact = parse_int(row.get("bit_structured_formula_abstract_distinct_exact", "0"), 0)
    if safe_support >= 8:
        return 0
    if safe_support >= 4:
        return 1
    if abstract_support >= 20 and distinct_exact >= 6:
        return 2
    if abstract_support >= 12 and distinct_exact >= 6:
        return 3
    return 4


def trace_rank(row: dict[str, str]) -> tuple[Any, ...]:
    return (
        row.get("template_subtype", ""),
        structured_support_bin(row),
        -structured_support_strength(row),
        -solver_priority(row),
        -parse_int(row.get("num_examples", "0"), 0),
        row.get("id", ""),
    )


def boxed_sibling_rank(row: dict[str, str]) -> tuple[Any, ...]:
    subtype = row.get("template_subtype", "")
    if subtype == "bit_structured_byte_formula":
        return (
            structured_support_bin(row),
            -structured_support_strength(row),
            -solver_priority(row),
            -parse_int(row.get("num_examples", "0"), 0),
            row.get("id", ""),
        )
    return (
        -solver_priority(row),
        -parse_int(row.get("num_examples", "0"), 0),
        -structured_support_strength(row),
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


def verified_binary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        if row.get("family") != "bit_manipulation":
            continue
        if row.get("selection_tier") != "verified_trace_ready":
            continue
        if not parse_bool(row.get("verified_trace_ready", "false")):
            continue
        if not row.get("teacher_solver_candidate", "").strip():
            continue
        selected.append(row)
    return selected


def order_trace_rows(rows: list[dict[str, str]], seed: int) -> list[dict[str, str]]:
    return round_robin_select(
        make_selected(rows, trace_rank),
        quota=len(rows),
        seed=seed,
        key_fn=lambda item: item.row.get("template_subtype", "unknown"),
    )


def boxed_sibling_group_key(row: dict[str, str]) -> str:
    subtype = row.get("template_subtype", "")
    if subtype == "bit_structured_byte_formula":
        return (
            row.get("bit_structured_formula_name", "").strip()
            or row.get("bit_structured_formula_abstract_family", "").strip()
            or row.get("teacher_solver_candidate", "").strip()
            or "unknown"
        )
    if subtype == "bit_other":
        return (
            row.get("teacher_solver_candidate", "").strip()
            or row.get("bit_byte_transform_names", "").split("|")[0].strip()
            or row.get("bit_simple_family", "").strip()
            or "unknown"
        )
    return row.get("teacher_solver_candidate", "").strip() or "unknown"


def select_boxed_sibling_rows(rows: list[dict[str, str]], seed: int, sibling_total: int) -> list[dict[str, str]]:
    if sibling_total != DEFAULT_BOXED_SIBLING_ROWS:
        raise ValueError(
            f"boxed-sibling-rows must equal {DEFAULT_BOXED_SIBLING_ROWS} for the current quota design; got {sibling_total}"
        )
    selected: list[dict[str, str]] = []
    by_subtype: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_subtype[row.get("template_subtype", "unknown")].append(row)
    for index, subtype in enumerate(BOXED_SIBLING_SUBTYPE_QUOTAS):
        subtype_rows = by_subtype.get(subtype, [])
        quota = BOXED_SIBLING_SUBTYPE_QUOTAS[subtype]
        if len(subtype_rows) < quota:
            raise ValueError(f"Subtype {subtype} has only {len(subtype_rows)} verified rows; needs {quota}")
        subtype_selected = round_robin_select(
            make_selected(subtype_rows, boxed_sibling_rank),
            quota=quota,
            seed=seed + 100 + index,
            key_fn=lambda item: boxed_sibling_group_key(item.row),
        )
        selected.extend(subtype_selected)
    return selected


def split_top_level_args(text: str) -> list[str]:
    args: list[str] = []
    depth = 0
    current: list[str] = []
    for char in text:
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError(f"Unbalanced expression: {text}")
        current.append(char)
    if depth != 0:
        raise ValueError(f"Unbalanced expression: {text}")
    tail = "".join(current).strip()
    if tail:
        args.append(tail)
    return args


def parse_expr(text: str) -> ExprNode:
    expr = text.strip()
    if not expr:
        raise ValueError("Expression is empty")
    if "(" not in expr:
        return ExprNode(name=expr, args=())
    if not expr.endswith(")"):
        raise ValueError(f"Malformed expression: {expr}")
    name, rest = expr.split("(", 1)
    inner = rest[:-1]
    args = tuple(parse_expr(part) for part in split_top_level_args(inner))
    return ExprNode(name=name.strip(), args=args)


def expr_to_text(node: ExprNode) -> str:
    if not node.args:
        return node.name
    return f"{node.name}({','.join(expr_to_text(arg) for arg in node.args)})"


def format_byte(value: int) -> str:
    return format(value & 0xFF, "08b")


def rotate_left(value: int, shift: int) -> int:
    shift %= 8
    value &= 0xFF
    return ((value << shift) | (value >> (8 - shift))) & 0xFF


def rotate_right(value: int, shift: int) -> int:
    shift %= 8
    value &= 0xFF
    return ((value >> shift) | (value << (8 - shift))) & 0xFF


def nibble_swap(value: int) -> int:
    value &= 0xFF
    return ((value & 0x0F) << 4) | ((value & 0xF0) >> 4)


def eval_atom(name: str, query_value: int) -> int:
    token = name.strip()
    if token in {"x", "query"}:
        return query_value & 0xFF
    if token == "nibble_swap":
        return nibble_swap(query_value)
    if token in {"rshift", "shr"}:
        return (query_value >> 1) & 0xFF
    if token in {"lshift", "shl"}:
        return (query_value << 1) & 0xFF
    if token in {"rol", "lrot"}:
        return rotate_left(query_value, 1)
    if token in {"ror", "rrot"}:
        return rotate_right(query_value, 1)
    match = re.fullmatch(r"(shl|shr|rol|ror|lrot|rrot)(\d+)", token)
    if match:
        op = match.group(1)
        shift = int(match.group(2))
        if op == "shl":
            return (query_value << shift) & 0xFF
        if op == "shr":
            return (query_value >> shift) & 0xFF
        if op in {"rol", "lrot"}:
            return rotate_left(query_value, shift)
        if op in {"ror", "rrot"}:
            return rotate_right(query_value, shift)
    raise ValueError(f"Unsupported atom: {token}")


def eval_expr(node: ExprNode, query_value: int) -> int:
    if not node.args:
        return eval_atom(node.name, query_value)
    values = [eval_expr(arg, query_value) for arg in node.args]
    name = node.name
    if name == "not":
        if len(values) != 1:
            raise ValueError("not() expects one arg")
        return (~values[0]) & 0xFF
    if name == "xor":
        if len(values) != 2:
            raise ValueError("xor() expects two args")
        return (values[0] ^ values[1]) & 0xFF
    if name == "and":
        if len(values) != 2:
            raise ValueError("and() expects two args")
        return (values[0] & values[1]) & 0xFF
    if name == "or":
        if len(values) != 2:
            raise ValueError("or() expects two args")
        return (values[0] | values[1]) & 0xFF
    if name == "majority":
        if len(values) != 3:
            raise ValueError("majority() expects three args")
        return ((values[0] & values[1]) | (values[0] & values[2]) | (values[1] & values[2])) & 0xFF
    if name == "choose":
        if len(values) != 3:
            raise ValueError("choose() expects three args")
        a, b, c = values
        return ((a & b) | ((~a) & c)) & 0xFF
    if name == "or_mask":
        if len(values) != 2:
            raise ValueError("or_mask() expects two args")
        return (values[0] | values[1]) & 0xFF
    raise ValueError(f"Unsupported function: {name}")


def resolve_binary_rule(row: dict[str, str], payload: dict[str, Any]) -> tuple[str, str] | None:
    direct_candidates = [
        row.get("bit_structured_formula_name", "").strip(),
        str(payload.get("structured_formula_name", "")).strip(),
        row.get("bit_not_structured_formula_name", "").strip(),
        str(payload.get("not_structured_formula_name", "")).strip(),
    ]
    for candidate in direct_candidates:
        if candidate:
            return candidate, "exact_formula"
    names = row.get("bit_byte_transform_names", "").strip()
    if names:
        return names.split("|")[0].strip(), "byte_transform"
    payload_names = payload.get("byte_transform_names", [])
    if isinstance(payload_names, list) and payload_names:
        text = str(payload_names[0]).strip()
        if text:
            return text, "byte_transform"
    abstract_candidates = [
        row.get("bit_structured_formula_abstract_family", "").strip(),
        row.get("bit_not_structured_formula_abstract_family", "").strip(),
    ]
    for candidate in abstract_candidates:
        if candidate:
            return candidate, "abstract_family"
    return None


def sanitize_query_token(query_text: str, final_answer_text: str) -> str:
    return "query_byte" if query_text == final_answer_text else query_text


def render_apply_text(node: ExprNode, query_ref: str, refs: dict[str, str]) -> str:
    if not node.args:
        token = node.name
        if token in {"x", "query"}:
            return query_ref
        return refs.get(expr_to_text(node), f"{token}({query_ref})")
    child_texts = [render_apply_text(arg, query_ref, refs) for arg in node.args]
    return f"{node.name}({','.join(child_texts)})"


def build_binary_micro_trace(rule_text: str, query_text: str, final_answer_text: str) -> str:
    query_value = int(query_text, 2)
    root = parse_expr(rule_text)
    query_ref = sanitize_query_token(query_text, final_answer_text)
    lines: list[str] = [f"rule={rule_text}", f"query={query_ref}"]
    refs: dict[str, str] = {}
    step_index = 0

    def emit(node: ExprNode) -> str:
        nonlocal step_index
        text = expr_to_text(node)
        if text in refs:
            return refs[text]
        if not node.args:
            if node.name in {"x", "query"}:
                return query_ref
            label = f"step{step_index + 1}"
            step_index += 1
            value_text = format_byte(eval_expr(node, query_value))
            if value_text == final_answer_text:
                lines.append(f"{label}={node.name}({query_ref})")
            else:
                lines.append(f"{label}={node.name}({query_ref})={value_text}")
            refs[text] = label
            return label
        child_refs = [emit(arg) for arg in node.args]
        label = f"step{step_index + 1}"
        step_index += 1
        rendered = f"{node.name}({','.join(child_refs)})"
        value_text = format_byte(eval_expr(node, query_value))
        if value_text == final_answer_text:
            lines.append(f"{label}={rendered}")
        else:
            lines.append(f"{label}={rendered}={value_text}")
        refs[text] = label
        return label

    if root.args:
        for arg in root.args[:2]:
            emit(arg)
    apply_text = render_apply_text(root, query_ref=query_ref, refs=refs)
    lines.append(f"apply={apply_text}")
    lines.append("constraints=exact_8bit,leading_zeros,box_only_final")
    return "<think>" + "; ".join(lines) + "</think>"


def build_binary_generic_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    solver = row.get("teacher_solver_candidate", "").strip() or "verified_binary_rule"
    rule_family = (
        row.get("bit_structured_formula_abstract_family", "").strip()
        or row.get("bit_not_structured_formula_abstract_family", "").strip()
        or solver
    )
    query_text = row.get("query_raw", "").strip()
    query_ref = sanitize_query_token(query_text, row["answer"].strip())
    return (
        "<think>"
        f"solver={solver}; rule_family={rule_family}; query={query_ref}; "
        "constraints=exact_8bit,leading_zeros,box_only_final"
        "</think>"
    )


def build_binary_trace(row: dict[str, str]) -> str:
    query_text = row.get("query_raw", "").strip()
    answer_text = row["answer"].strip()
    if not re.fullmatch(r"[01]{8}", query_text):
        raise ValueError(f"Binary query is not an exact 8-bit string: {row['id']}")
    if not re.fullmatch(r"[01]{8}", answer_text):
        raise ValueError(f"Binary answer is not an exact 8-bit string: {row['id']}")
    payload = parse_family_payload(row)
    resolved = resolve_binary_rule(row, payload)
    if resolved is None:
        return build_binary_generic_trace(row, payload)
    rule_text, _rule_source = resolved
    try:
        return build_binary_micro_trace(rule_text=rule_text, query_text=query_text, final_answer_text=answer_text)
    except Exception:
        return build_binary_generic_trace(row, payload)


def binary_trace_category(row: dict[str, str]) -> str:
    payload = parse_family_payload(row)
    resolved = resolve_binary_rule(row, payload)
    if resolved is None:
        return "generic_solver_family"
    rule_text, rule_source = resolved
    try:
        parse_expr(rule_text)
        return f"micro_dsl_{rule_source}"
    except Exception:
        return f"generic_{rule_source}"


def build_output_records(trace_rows: list[dict[str, str]], boxed_sibling_rows: list[dict[str, str]]) -> list[OutputRecord]:
    output_records: list[OutputRecord] = []
    for row in trace_rows:
        output_records.append(
            OutputRecord(
                output_id=row["id"],
                source_id=row["id"],
                prompt=row["prompt"],
                answer=row["answer"],
                generated_cot=build_binary_trace(row),
                assistant_style="trace_boxed",
                output_origin="verified_trace_core",
                source_selection_tier=row["selection_tier"],
            )
        )
    for row in boxed_sibling_rows:
        output_records.append(
            OutputRecord(
                output_id=f"{row['id']}__boxed_sibling_v212",
                source_id=row["id"],
                prompt=row["prompt"],
                answer=row["answer"],
                generated_cot="",
                assistant_style="boxed_only",
                output_origin="verified_boxed_sibling",
                source_selection_tier=row["selection_tier"],
            )
        )
    return output_records


def validate_output(records: list[OutputRecord], source_index: dict[str, dict[str, str]], expected_size: int) -> None:
    if len(records) != expected_size:
        raise ValueError(f"Expected {expected_size} rows, found {len(records)}")
    output_ids = [record.output_id for record in records]
    if len(output_ids) != len(set(output_ids)):
        raise ValueError("Duplicate output ids detected")
    for record in records:
        source_row = source_index.get(record.source_id)
        if source_row is None:
            raise ValueError(f"Unknown source row: {record.source_id}")
        if source_row.get("family") != "bit_manipulation":
            raise ValueError(f"Non-binary source row leaked into dataset: {record.source_id}")
        if record.assistant_style == "trace_boxed":
            if not record.generated_cot.startswith("<think>") or not record.generated_cot.endswith("</think>"):
                raise ValueError(f"Trace rows must be wrapped by <think>: {record.output_id}")
            if record.answer in record.generated_cot:
                raise ValueError(f"Binary trace leaked final answer inside <think>: {record.output_id}")
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
    source_index: dict[str, dict[str, str]],
    records: list[OutputRecord],
    trace_rows: list[dict[str, str]],
    boxed_sibling_rows: list[dict[str, str]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    family_counts = Counter(source_index[record.source_id]["family"] for record in records)
    source_tier_counts = Counter(source_index[record.source_id]["selection_tier"] for record in records)
    style_counts = Counter(record.assistant_style for record in records)
    origin_counts = Counter(record.output_origin for record in records)
    template_counts = Counter(source_index[record.source_id].get("template_subtype", "unknown") for record in records)
    solver_counts = Counter(source_index[record.source_id].get("teacher_solver_candidate", "") for record in records)
    binary_trace_categories = Counter(binary_trace_category(row) for row in trace_rows)
    sibling_template_counts = Counter(row.get("template_subtype", "unknown") for row in boxed_sibling_rows)
    sibling_solver_counts = Counter(row.get("teacher_solver_candidate", "") for row in boxed_sibling_rows)
    structured_sibling_bins = Counter()
    sanitized_query_equals_answer_rows = 0
    for row in trace_rows:
        if row.get("query_raw", "").strip() == row.get("answer", "").strip():
            sanitized_query_equals_answer_rows += 1
    for row in boxed_sibling_rows:
        if row.get("template_subtype") == "bit_structured_byte_formula":
            structured_sibling_bins[f"bin_{structured_support_bin(row)}"] += 1
    return {
        "dataset_version": "v2-1-2",
        "source_csv": str(args.source_csv),
        "dataset_csv": str(args.dataset_csv),
        "manifest_json": str(args.manifest_json),
        "seed": args.seed,
        "subsample_size": len(records),
        "unique_source_id_count": len(trace_rows),
        "boxed_sibling_rows": len(boxed_sibling_rows),
        "family_counts": dict(sorted(family_counts.items())),
        "source_selection_tier_counts": dict(sorted(source_tier_counts.items())),
        "assistant_style_counts": dict(sorted(style_counts.items())),
        "output_origin_counts": dict(sorted(origin_counts.items())),
        "template_subtype_counts": dict(sorted(template_counts.items())),
        "teacher_solver_counts": dict(sorted(solver_counts.items())),
        "boxed_sibling_subtype_quotas": BOXED_SIBLING_SUBTYPE_QUOTAS,
        "boxed_sibling_subtype_counts": dict(sorted(sibling_template_counts.items())),
        "boxed_sibling_solver_counts": dict(sorted(sibling_solver_counts.items())),
        "binary_phase2_1_2_design": {
            "trace_rows_from_verified": len(trace_rows),
            "boxed_sibling_rows_from_verified": len(boxed_sibling_rows),
            "broad_answer_only_rows_used": 0,
            "manual_rows_used": 0,
            "trace_style": "micro_dsl_binary_specialist",
            "trace_avoids_repeating_final_answer_inside_think": True,
            "query_equals_answer_rows_sanitized": sanitized_query_equals_answer_rows,
            "binary_trace_category_counts": dict(sorted(binary_trace_categories.items())),
            "structured_sibling_support_bin_counts": dict(sorted(structured_sibling_bins.items())),
        },
        "selection_policy": {
            "trace_include": [
                "bit_manipulation + verified_trace_ready + teacher_solver_candidate present",
            ],
            "trace_exclude": [
                "bit_manipulation + answer_only_keep",
                "bit_manipulation + manual_audit_priority",
                "bit_manipulation + exclude_suspect",
            ],
            "boxed_sibling_policy": "Create duplicate boxed-only supervision from verified rows only; never source boxed-only rows from broad answer_only_keep.",
        },
        "notes": [
            "README.md evaluation is boxed-first, so Phase 2.1.2 keeps final 8-bit answers out of <think> and teaches closure with verified boxed-only siblings.",
            "This dataset replaces the 445 broad answer_only rows from phase2_1 with 445 duplicate boxed-only rows derived from verified binary sources.",
            "Binary traces use a short micro-DSL instead of the longer hybrid narrative because prior analysis showed long binary traces drift into fallback extraction.",
            "The dataset remains binary-only so phase2_1_2 isolates data-quality and trace-format changes before any anchored continuation experiment.",
        ],
    }


def build_dataset(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source_rows = load_rows(args.source_csv)
    verified = verified_binary_rows(source_rows)
    trace_rows = order_trace_rows(verified, seed=args.seed)
    boxed_sibling_rows = select_boxed_sibling_rows(verified, seed=args.seed, sibling_total=args.boxed_sibling_rows)
    source_index = {row["id"]: row for row in source_rows}
    records = build_output_records(trace_rows, boxed_sibling_rows)
    validate_output(records, source_index=source_index, expected_size=len(trace_rows) + len(boxed_sibling_rows))
    csv_rows = [record.to_csv_row() for record in records]
    write_csv(args.dataset_csv, csv_rows, OUTPUT_COLUMNS)
    manifest = build_manifest(
        source_index=source_index,
        records=records,
        trace_rows=trace_rows,
        boxed_sibling_rows=boxed_sibling_rows,
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
    for row in rows[:preview_count]:
        print("=" * 80)
        print(
            json.dumps(
                {
                    "id": row["id"],
                    "label": row["label"],
                    "assistant_style": row["assistant_style"],
                    "source_selection_tier": row["source_selection_tier"],
                },
                ensure_ascii=False,
            )
        )
        print("USER:")
        print(row["prompt"])
        print()
        print("ASSISTANT:")
        print(render_assistant_message(row))


def main() -> None:
    args = parse_args()
    if args.mode == "build-dataset":
        rows, manifest = build_dataset(args)
        print(f"Wrote Phase 2.1.2 dataset CSV: {args.dataset_csv}")
        print(f"Wrote Phase 2.1.2 manifest JSON: {args.manifest_json}")
        print(json.dumps(manifest["assistant_style_counts"], ensure_ascii=False, sort_keys=True))
        preview_row = next(row for row in rows if row["assistant_style"] == "trace_boxed")
        print("Sample assistant message:")
        print(render_assistant_message(preview_row))
        return
    if not args.dataset_csv.exists():
        raise FileNotFoundError(f"Dataset CSV does not exist yet: {args.dataset_csv}")
    preview_rows(args.dataset_csv, preview_count=args.preview_rows)


if __name__ == "__main__":
    main()
