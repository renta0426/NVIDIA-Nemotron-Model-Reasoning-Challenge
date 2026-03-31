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
DEFAULT_DATASET_CSV = Path(__file__).resolve().parent / "artifacts" / "phase2_binary_dsl_training_data.csv"
DEFAULT_MANIFEST_JSON = Path(__file__).resolve().parent / "artifacts" / "phase2_binary_dsl_manifest.json"
BOXED_INSTRUCTION = "Please put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`"
DEFAULT_SEED = 42

# Keep the same overall mixture as Phase 1 so Phase 2 isolates the binary teacher redesign.
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


@dataclass(frozen=True)
class SelectedRow:
    row: dict[str, str]
    rank_key: tuple[Any, ...]


@dataclass(frozen=True)
class BinaryTracePlan:
    rule_name: str
    rule_source: str
    mode: str
    trace: str


@dataclass(frozen=True)
class ExprNode:
    name: str
    args: tuple["ExprNode", ...] = ()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the Phase 2 README-aligned dataset that keeps the Phase 1 mixture "
            "but rewrites verified binary teachers into a structured DSL scratchpad."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("build-dataset", "preview"),
        default="build-dataset",
        help="build-dataset writes the CSV/manifest, preview prints a few rendered assistant messages.",
    )
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--dataset-csv", type=Path, default=DEFAULT_DATASET_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--subsample-size", type=int, default=DEFAULT_SUBSAMPLE_SIZE)
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
        payload.get("structured_formula_name", ""),
        row.get("bit_not_structured_formula_name", "").strip(),
        payload.get("not_structured_formula_name", ""),
    ]
    for candidate in direct_candidates:
        text = str(candidate).strip()
        if text:
            return text, "exact_formula"
    names = row.get("bit_byte_transform_names", "").strip()
    if names:
        return names.split("|")[0].strip(), "byte_transform"
    payload_names = payload.get("byte_transform_names", [])
    if isinstance(payload_names, list) and payload_names:
        text = str(payload_names[0]).strip()
        if text:
            return text, "byte_transform"
    for key in ("structured_formula_sample_matches", "not_structured_formula_sample_matches"):
        matches = payload.get(key, [])
        if isinstance(matches, list):
            cleaned = sorted({str(item).strip() for item in matches if str(item).strip()})
            if len(cleaned) == 1:
                return cleaned[0], f"payload_{key}"
    abstract_candidates = [
        row.get("bit_structured_formula_abstract_family", "").strip(),
        row.get("bit_not_structured_formula_abstract_family", "").strip(),
    ]
    for candidate in abstract_candidates:
        if candidate:
            return candidate, "abstract_family"
    return None


def generic_binary_rule_label(row: dict[str, str], payload: dict[str, Any]) -> str:
    resolved = resolve_binary_rule(row, payload)
    if resolved is not None:
        return resolved[0]
    solver = row.get("teacher_solver_candidate", "").strip()
    if solver:
        return solver
    return "verified_binary_rule"


def is_simple_transform(node: ExprNode) -> bool:
    return not node.args and node.name not in {"x", "query"}


def build_binary_dsl_trace(rule_text: str, query_text: str, final_answer_text: str) -> str:
    query_value = int(query_text, 2)
    root = parse_expr(rule_text)
    steps: list[str] = []
    cache: dict[str, str] = {}
    step_index = 0

    def emit(node: ExprNode, *, is_root: bool) -> str:
        nonlocal step_index
        if not node.args:
            if node.name in {"x", "query"}:
                return "query"
            if is_root:
                return f"{node.name}(query)"
            text = expr_to_text(node)
            if text in cache:
                return cache[text]
            step_index += 1
            label = f"step{step_index}"
            value = eval_expr(node, query_value)
            value_text = format_byte(value)
            if value_text == final_answer_text:
                steps.append(f"{label}={node.name}(query)")
            else:
                steps.append(f"{label}={node.name}(query)={value_text}")
            cache[text] = label
            return label

        child_refs = [emit(arg, is_root=False) for arg in node.args]
        rendered = f"{node.name}({','.join(child_refs)})"
        if is_root:
            return rendered
        text = expr_to_text(node)
        if text in cache:
            return cache[text]
        step_index += 1
        label = f"step{step_index}"
        value = eval_expr(node, query_value)
        value_text = format_byte(value)
        if value_text == final_answer_text:
            steps.append(f"{label}={rendered}")
        else:
            steps.append(f"{label}={rendered}={value_text}")
        cache[text] = label
        return label

    root_apply = emit(root, is_root=True)
    lines = [
        "family=binary",
        f"rule={rule_text}",
        f"query={query_text}",
    ]
    lines.extend(steps[:4])
    lines.append(f"apply={root_apply}")
    lines.append("constraints=exact_8bit,leading_zeros,box_only_final")
    return "<think>" + "\n".join(lines) + "</think>"


def build_binary_generic_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    solver = row.get("teacher_solver_candidate", "").strip() or "verified_binary_rule"
    rule_label = generic_binary_rule_label(row, payload)
    query_text = row.get("query_raw", "").strip()
    lines = [
        "family=binary",
        f"solver={solver}",
        f"rule_family={rule_label}",
        f"query={query_text}",
        "apply=verified_binary_program(query)",
        "constraints=exact_8bit,leading_zeros,box_only_final",
    ]
    return "<think>" + "\n".join(lines) + "</think>"


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


def build_binary_trace(row: dict[str, str], payload: dict[str, Any]) -> str:
    query_text = row.get("query_raw", "").strip()
    if not re.fullmatch(r"[01]{8}", query_text):
        raise ValueError(f"Binary query is not an exact 8-bit string: {row['id']}")
    resolved = resolve_binary_rule(row, payload)
    if resolved is not None:
        rule_text, rule_source = resolved
        try:
            return build_binary_dsl_trace(
                rule_text=rule_text,
                query_text=query_text,
                final_answer_text=row["answer"].strip(),
            )
        except Exception:
            return build_binary_generic_trace(row, payload)
    return build_binary_generic_trace(row, payload)


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
        return build_binary_trace(row, payload)
    if family == "symbol_equation":
        return build_symbol_trace(row, payload)
    raise ValueError(f"Unsupported family for trace generation: {family}")


def binary_trace_category(row: dict[str, str]) -> str:
    payload = parse_family_payload(row)
    resolved = resolve_binary_rule(row, payload)
    if resolved is None:
        return "generic_solver_family"
    rule_text, rule_source = resolved
    try:
        parse_expr(rule_text)
        return f"dsl_{rule_source}"
    except Exception:
        return f"generic_{rule_source}"


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


def build_manifest(*, source_rows: list[dict[str, str]], output_rows: list[dict[str, str]], args: argparse.Namespace) -> dict[str, Any]:
    source_index = {row["id"]: row for row in source_rows}
    family_counts = Counter(source_index[row["id"]]["family"] for row in output_rows)
    source_tier_counts = Counter(row["source_selection_tier"] for row in output_rows)
    style_counts = Counter(row["assistant_style"] for row in output_rows)
    template_counts = Counter(source_index[row["id"]].get("template_subtype", "unknown") for row in output_rows)
    solver_counts = Counter(source_index[row["id"]].get("teacher_solver_candidate", "") for row in output_rows)
    binary_trace_rows = [
        source_index[row["id"]]
        for row in output_rows
        if row["label"] == "binary" and row["assistant_style"] == "trace_boxed"
    ]
    binary_boxed_only_rows = [
        source_index[row["id"]]
        for row in output_rows
        if row["label"] == "binary" and row["assistant_style"] == "boxed_only"
    ]
    binary_trace_categories = Counter(binary_trace_category(row) for row in binary_trace_rows)
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
        "binary_phase2_design": {
            "verified_binary_trace_rows": len(binary_trace_rows),
            "answer_only_binary_boxed_rows": len(binary_boxed_only_rows),
            "binary_answer_only_is_boxed_only": True,
            "binary_trace_avoids_repeating_final_answer_inside_think": True,
            "binary_trace_category_counts": dict(sorted(binary_trace_categories.items())),
        },
        "notes": [
            "Phase 2 keeps the Phase 1 mixture fixed so binary teacher format is the main changed variable.",
            "Verified binary rows use a structured DSL-style scratchpad where possible, while answer_only_keep binary rows stay boxed-only.",
            "Binary traces never restate the final 8-bit answer inside <think> because README scoring is boxed-first and long numeric drift is harmful.",
            "The output schema matches phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.py so the existing trainer can consume this CSV via --dataset-csv.",
        ],
    }


def build_dataset(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if args.subsample_size != DEFAULT_SUBSAMPLE_SIZE:
        raise ValueError(
            f"subsample-size must equal {DEFAULT_SUBSAMPLE_SIZE} for the current quota design; got {args.subsample_size}"
        )
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
        print(f"Wrote Phase 2 dataset CSV: {args.dataset_csv}")
        print(f"Wrote Phase 2 manifest JSON: {args.manifest_json}")
        print(json.dumps(manifest["family_counts"], ensure_ascii=False, sort_keys=True))
        binary_preview = next(row for row in rows if row["label"] == "binary" and row["assistant_style"] == "trace_boxed")
        print("Sample binary assistant message:")
        print(render_assistant_message(binary_preview))
        return
    if not args.dataset_csv.exists():
        raise FileNotFoundError(f"Dataset CSV does not exist yet: {args.dataset_csv}")
    preview_rows(args.dataset_csv, preview_count=args.preview_rows)


if __name__ == "__main__":
    main()
