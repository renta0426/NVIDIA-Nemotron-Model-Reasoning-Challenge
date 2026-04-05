#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import random
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
ORIGINAL_TRAIN_CSV = REPO_ROOT / "data" / "train.csv"
ANALYSIS_MODULE = REPO_ROOT / "cuda-train-data-analysis-v1" / "code" / "train_data_analysis_v1.py"

OUTPUT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_CSV = OUTPUT_DIR / "bit_synth_exact_trace_cot_training_data_v1_1.csv"
DEFAULT_MANIFEST_JSON = OUTPUT_DIR / "bit_synth_exact_trace_cot_manifest_v1_1.json"
DEFAULT_REPORT_MD = OUTPUT_DIR / "BIT_SYNTH_EXACT_TRACE_COT_V1_1_REPORT.md"

OUTPUT_COLUMNS = [
    "id",
    "prompt",
    "answer",
    "generated_cot",
    "label",
    "assistant_style",
    "source_selection_tier",
]

PROMPT_TEMPLATE = (
    "In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers. "
    "The transformation involves operations like bit shifts, rotations, XOR, AND, OR, NOT, "
    "and possibly majority or choice functions.\n\n"
    "Here are some examples of input -> output:\n"
    "{example_lines}\n\n"
    "Now, determine the output for: {query_bits}"
)

QUERY_PATTERN = re.compile(r"Now, determine the output for: ([01]{8})")
EXAMPLE_PATTERN = re.compile(r"^([01]{8}) -> ([01]{8})$")
TOP_LEVEL_OPS = ("xor", "and", "or", "choose", "majority")
SOURCE_PATTERN = re.compile(r"^(x|reverse|nibble_swap|(rol|ror|shl|shr)\d+)$")

STYLE_TARGET_COUNTS = {
    "trace_boxed_full": 7000,
    "trace_boxed_short": 1500,
    "trace_boxed_query_commit": 1000,
    "boxed_only_closure": 500,
}

ASSISTANT_STYLE_BY_VARIANT = {
    "trace_boxed_full": "trace_boxed",
    "trace_boxed_short": "trace_boxed",
    "trace_boxed_query_commit": "trace_boxed",
    "boxed_only_closure": "boxed_only",
}

SOURCE_TIER_BY_VARIANT = {
    "trace_boxed_full": "synthetic_exact_trace_ready_v1_1_full",
    "trace_boxed_short": "synthetic_exact_trace_ready_v1_1_short",
    "trace_boxed_query_commit": "synthetic_exact_trace_ready_v1_1_query_commit",
    "boxed_only_closure": "synthetic_exact_trace_ready_v1_1_closure_only",
}

GROUP_WEIGHTS = {
    "binary_structured_byte_formula": 1.00,
    "binary_structured_byte_formula_abstract": 1.60,
    "binary_two_bit_boolean": 1.70,
    "binary_three_bit_boolean": 1.80,
    "binary_affine_xor": 1.10,
    "binary_bit_permutation_bijection": 1.00,
    "binary_bit_permutation_independent": 4.50,
    "binary_structured_byte_not_formula": 0.70,
    "binary_byte_transform": 0.35,
}

BOOLEAN2_OPERATION_ORDER = (
    "xor",
    "xnor",
    "and",
    "or",
    "x_and_noty",
    "notx_and_y",
    "x_implies_y",
    "y_implies_x",
    "nand",
    "nor",
    "x",
    "y",
    "not_x",
    "not_y",
)

BOOLEAN3_OPERATION_ORDER = (
    "majority",
    "choice",
    "parity3",
)


@dataclass(frozen=True)
class SeedConfig:
    seed_row_id: str
    strong_group: str
    exact_rule: str
    example_count: int
    rule_payload: Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a mixed-style bit-manipulation exact-trace v1.1 CSV that keeps the "
            "existing exact-trace policy but adds short-closure and query-commit supervision."
        )
    )
    parser.add_argument("--target-rows", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260405)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--manifest-json", type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--max-attempts-per-row", type=int, default=240)
    return parser.parse_args()


def load_module(module_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("train_data_analysis_v1", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def format_byte(value: int) -> str:
    return format(value & 0xFF, "08b")


def bits_to_int(bits: str) -> int:
    return int(bits, 2)


def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"
    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", text)
    if matches:
        non_empty = [match.strip() for match in matches if match.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    patterns = [
        r"The final answer is:\s*([^\n]+)",
        r"Final answer is:\s*([^\n]+)",
        r"Final answer\s*[:：]\s*([^\n]+)",
        r"final answer\s*[:：]\s*([^\n]+)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1].strip()
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if matches:
        return matches[-1]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"


def count_non_empty_boxed(text: str) -> int:
    return sum(1 for match in re.findall(r"\\boxed\{([^}]*)\}", text) if match.strip())


def parse_binary_prompt(prompt: str) -> tuple[list[tuple[str, str]], str]:
    examples: list[tuple[str, str]] = []
    query_bits = ""
    for line in prompt.splitlines():
        line = line.strip()
        match = EXAMPLE_PATTERN.match(line)
        if match:
            examples.append((match.group(1), match.group(2)))
        query_match = QUERY_PATTERN.search(line)
        if query_match:
            query_bits = query_match.group(1)
    if not examples or not query_bits:
        raise ValueError("Failed to parse binary prompt.")
    return examples, query_bits


def parse_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        return {}


def split_top_level_arguments(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return parts


def source_text(expr: Any) -> str:
    kind = expr[0]
    if kind == "source":
        return expr[1]
    if kind == "not":
        return f"not({source_text(expr[1])})"
    raise ValueError(f"Unsupported source expr: {expr}")


def parse_formula(text: str) -> Any:
    text = text.strip()
    if SOURCE_PATTERN.fullmatch(text):
        return ("source", text)
    if text.startswith("not(") and text.endswith(")"):
        inner = text[4:-1].strip()
        return ("not", parse_formula(inner))
    for op in TOP_LEVEL_OPS:
        prefix = f"{op}("
        if text.startswith(prefix) and text.endswith(")"):
            inner = text[len(prefix) : -1]
            parts = split_top_level_arguments(inner)
            return (op, tuple(parse_formula(part) for part in parts))
    raise ValueError(f"Unsupported formula text: {text}")


def evaluate_source_expr(mod: Any, expr: Any, value: int) -> int:
    kind = expr[0]
    if kind == "source":
        name = expr[1]
        if name == "x":
            return value & 0xFF
        if name == "reverse":
            return mod.reverse_byte_bits(value)
        if name == "nibble_swap":
            return mod.nibble_swap_byte(value)
        if name.startswith("rol"):
            return mod.rotate_left_byte(value, int(name[3:]))
        if name.startswith("ror"):
            return mod.rotate_right_byte(value, int(name[3:]))
        if name.startswith("shl"):
            return ((value & 0xFF) << int(name[3:])) & 0xFF
        if name.startswith("shr"):
            return (value & 0xFF) >> int(name[3:])
        raise ValueError(f"Unsupported source name: {name}")
    if kind == "not":
        return (~evaluate_source_expr(mod, expr[1], value)) & 0xFF
    raise ValueError(f"Unsupported source expr: {expr}")


def evaluate_formula(mod: Any, ast: Any, value: int) -> int:
    kind = ast[0]
    if kind in {"source", "not"}:
        return evaluate_source_expr(mod, ast, value)
    if kind in {"xor", "and", "or"}:
        left = evaluate_source_expr(mod, ast[1][0], value)
        right = evaluate_source_expr(mod, ast[1][1], value)
        return mod.BIT_STRUCTURED_BYTE_BINARY_OPERATIONS[kind](left, right) & 0xFF
    if kind in {"choose", "majority"}:
        values = [evaluate_source_expr(mod, arg, value) for arg in ast[1]]
        return mod.BIT_STRUCTURED_BYTE_TERNARY_OPERATIONS[kind](*values) & 0xFF
    raise ValueError(f"Unsupported formula kind: {kind}")


def render_formula_support_line(mod: Any, rule_text: str, ast: Any, input_bits: str, output_bits: str) -> str:
    value = bits_to_int(input_bits)
    kind = ast[0]
    if kind in {"source", "not"}:
        return f"- {input_bits} -> {output_bits} because {rule_text}({input_bits}) = {output_bits}"
    arg_text = ", ".join(
        f"{source_text(arg)}={format_byte(evaluate_source_expr(mod, arg, value))}" for arg in ast[1]
    )
    return f"- {input_bits} -> {output_bits} because {arg_text}; {rule_text} matches the given output"


def render_formula_query_block(mod: Any, rule_text: str, ast: Any, query_bits: str) -> list[str]:
    value = bits_to_int(query_bits)
    lines = [f"Query x = {query_bits}"]
    kind = ast[0]
    if kind in {"source", "not"}:
        if kind == "not":
            inner = ast[1]
            lines.append(f"{source_text(inner)}(x) = {format_byte(evaluate_source_expr(mod, inner, value))}")
        lines.append(f"Apply {rule_text} to the query and put the resulting 8-bit output in the final box.")
        return lines
    for arg in ast[1]:
        lines.append(f"{source_text(arg)}(x) = {format_byte(evaluate_source_expr(mod, arg, value))}")
    lines.append(f"Apply {rule_text} to the query and put the resulting 8-bit output in the final box.")
    return lines


def parse_signature_counts(signature: str) -> list[int]:
    counts: list[int] = []
    for match in re.finditer(r"o\d+=\[([^\]]*)\]", signature):
        inner = match.group(1).strip()
        counts.append(0 if inner == "" else len([item for item in inner.split(",") if item]))
    return counts


def parse_unique_independent_mapping(signature: str) -> tuple[tuple[int, bool], ...] | None:
    entries: list[tuple[int, int, bool]] = []
    for match in re.finditer(r"o(\d+)=\[([^\]]*)\]", signature):
        output_index = int(match.group(1)) - 1
        items = [item for item in match.group(2).split(",") if item]
        if len(items) != 1:
            return None
        item = items[0]
        flip = item.endswith("^")
        item = item[:-1] if flip else item
        if not item.startswith("i"):
            return None
        input_index = int(item[1:]) - 1
        entries.append((output_index, input_index, flip))
    if len(entries) != 8:
        return None
    entries.sort()
    return tuple((input_index, flip) for _, input_index, flip in entries)


def parse_exact_byte_transform_rule(name: str, examples: list[tuple[str, str]]) -> tuple[str, int | None]:
    first_input, first_output = examples[0]
    input_value = bits_to_int(first_input)
    output_value = bits_to_int(first_output)
    if name == "xor_mask":
        return name, input_value ^ output_value
    if name in {"and_mask", "or_mask"}:
        return name, output_value
    return name, None


def apply_byte_transform(mod: Any, name: str, param: int | None, bits: str) -> str:
    value = bits_to_int(bits)
    transform = mod.BIT_BYTE_TRANSFORMS[name]
    return format_byte(transform(value, param))


def derive_exact_affine_coeffs(mod: Any, examples: list[tuple[str, str]]) -> tuple[tuple[int, ...], ...] | None:
    coeffs: list[tuple[int, ...]] = []
    for output_index in range(8):
        system_rows = [
            [int(bit) for bit in input_bits] + [1, int(output_bits[output_index])]
            for input_bits, output_bits in examples
        ]
        reduced_rows, pivot_columns = mod.rref_gf2(system_rows, 9)
        for row in reduced_rows:
            if not any(row[:9]) and row[9]:
                return None
        free_columns = [column for column in range(9) if column not in pivot_columns]
        if free_columns:
            return None
        pivot_to_row = {column: row_index for row_index, column in enumerate(pivot_columns)}
        base_solution = [0] * 9
        for column in reversed(pivot_columns):
            row_index = pivot_to_row[column]
            value = reduced_rows[row_index][9]
            for trailing_column in range(column + 1, 9):
                if reduced_rows[row_index][trailing_column]:
                    value ^= base_solution[trailing_column]
            base_solution[column] = value
        coeffs.append(tuple(base_solution))
    return tuple(coeffs)


def apply_affine_coeffs(coeffs: tuple[tuple[int, ...], ...], bits: str) -> str:
    vector = [int(bit) for bit in bits] + [1]
    output_bits: list[str] = []
    for coefficients in coeffs:
        bit = 0
        for left, right in zip(vector, coefficients):
            bit ^= left & right
        output_bits.append(str(bit))
    return "".join(output_bits)


def serialize_affine_equation(coefficients: tuple[int, ...]) -> str:
    terms = [f"i{index + 1}" for index, value in enumerate(coefficients[:8]) if value]
    if coefficients[8]:
        terms.append("1")
    if not terms:
        return "0"
    return " xor ".join(terms)


def render_affine_support_line(input_bits: str, output_bits: str) -> str:
    return f"- {input_bits} -> {output_bits} is consistent with the same GF(2) equations."


def render_affine_query_block(coeffs: tuple[tuple[int, ...], ...], query_bits: str) -> list[str]:
    lines = ["So the rule is:"]
    for output_index, coefficients in enumerate(coeffs, start=1):
        lines.append(f"o{output_index} = {serialize_affine_equation(coefficients)}")
    lines.append(f"Query x = {query_bits}")
    query_vector = [int(bit) for bit in query_bits] + [1]
    for output_index, coefficients in enumerate(coeffs, start=1):
        pieces = []
        for idx, value in enumerate(coefficients[:8]):
            if value:
                pieces.append(f"i{idx + 1}={query_vector[idx]}")
        if coefficients[8]:
            pieces.append("1")
        text = ", ".join(pieces) if pieces else "0"
        lines.append(f"o{output_index} uses {text}")
    lines.append("Put the resulting 8-bit output in the final box.")
    return lines


def recover_unique_bijection_mapping(
    candidate_sets: list[list[tuple[int, int]]],
) -> tuple[tuple[tuple[int, int], ...] | None, int]:
    if any(not candidates for candidates in candidate_sets):
        return None, 0
    order = sorted(range(8), key=lambda index: (len(candidate_sets[index]), index))
    assignments: list[tuple[tuple[int, int], ...]] = []

    def backtrack(position: int, used_inputs: set[int], partial: dict[int, tuple[int, int]]) -> None:
        if len(assignments) > 1:
            return
        if position >= len(order):
            assignments.append(tuple(partial[index] for index in range(8)))
            return
        output_index = order[position]
        for input_index, flip in candidate_sets[output_index]:
            if input_index in used_inputs:
                continue
            used_inputs.add(input_index)
            partial[output_index] = (input_index, flip)
            backtrack(position + 1, used_inputs, partial)
            partial.pop(output_index, None)
            used_inputs.remove(input_index)
            if len(assignments) > 1:
                return

    backtrack(0, set(), {})
    return (assignments[0] if len(assignments) == 1 else None), len(assignments)


def apply_mapping_rule(mapping: tuple[tuple[int, bool], ...], bits: str) -> str:
    output_bits: list[str] = []
    for input_index, flip in mapping:
        bit = bits[input_index]
        output_bits.append("1" if (bit == "0" and flip) or (bit == "1" and not flip) else "0")
    return "".join(output_bits)


def mapping_line(output_index: int, input_index: int, flip: bool) -> str:
    return f"o{output_index + 1} <- {'not(' if flip else ''}i{input_index + 1}{')' if flip else ''}"


def render_mapping_support_line(kind: str, input_bits: str, output_bits: str) -> str:
    noun = "bijection mapping" if kind == "binary_bit_permutation_bijection" else "copy/invert mapping"
    return f"- {input_bits} -> {output_bits} is consistent with the same {noun}."


def render_mapping_query_block(
    mapping: tuple[tuple[int, bool], ...],
    query_bits: str,
) -> list[str]:
    lines = ["So the rule is:"]
    for output_index, (input_index, flip) in enumerate(mapping):
        lines.append(mapping_line(output_index, input_index, flip))
    lines.append(f"Query x = {query_bits}")
    for output_index, (input_index, flip) in enumerate(mapping):
        if flip:
            lines.append(f"o{output_index + 1} uses not(i{input_index + 1}) with i{input_index + 1}={query_bits[input_index]}")
        else:
            lines.append(f"o{output_index + 1} uses i{input_index + 1}={query_bits[input_index]}")
    lines.append("Put the resulting 8-bit output in the final box.")
    return lines


def boolean2_expression(spec: tuple[int, int, str]) -> str:
    left_index, right_index, op_name = spec
    left = f"i{left_index + 1}"
    right = f"i{right_index + 1}"
    if op_name == "x":
        return left
    if op_name == "not_x":
        return f"not({left})"
    if op_name == "y":
        return right
    if op_name == "not_y":
        return f"not({right})"
    if op_name == "x_and_noty":
        return f"and({left},not({right}))"
    if op_name == "notx_and_y":
        return f"and(not({left}),{right})"
    if op_name == "x_implies_y":
        return f"implies({left},{right})"
    if op_name == "y_implies_x":
        return f"implies({right},{left})"
    return f"{op_name}({left},{right})"


def boolean3_expression(spec: tuple[int, int, int, str]) -> str:
    first_index, second_index, third_index, op_name = spec
    first = f"i{first_index + 1}"
    second = f"i{second_index + 1}"
    third = f"i{third_index + 1}"
    return f"{op_name}({first},{second},{third})"


def apply_boolean2_payload(mod: Any, payload: tuple[tuple[int, int, str], ...], bits: str) -> str:
    output_bits: list[str] = []
    for left_index, right_index, op_name in payload:
        left = int(bits[left_index])
        right = int(bits[right_index])
        output_bits.append(str(mod.BIT_BOOLEAN2_OPERATIONS[op_name](left, right)))
    return "".join(output_bits)


def apply_boolean3_payload(mod: Any, payload: tuple[tuple[int, int, int, str], ...], bits: str) -> str:
    output_bits: list[str] = []
    for first_index, second_index, third_index, op_name in payload:
        first = int(bits[first_index])
        second = int(bits[second_index])
        third = int(bits[third_index])
        output_bits.append(str(mod.BIT_BOOLEAN3_OPERATIONS[op_name](first, second, third)))
    return "".join(output_bits)


def derive_boolean2_payload(mod: Any, examples: list[tuple[str, str]]) -> tuple[tuple[int, int, str], ...] | None:
    payload: list[tuple[int, int, str]] = []
    for output_index in range(8):
        chosen: tuple[int, int, str] | None = None
        for op_name in BOOLEAN2_OPERATION_ORDER:
            operation = mod.BIT_BOOLEAN2_OPERATIONS[op_name]
            for left_index in range(8):
                for right_index in range(8):
                    valid = True
                    for input_bits, output_bits in examples:
                        if operation(int(input_bits[left_index]), int(input_bits[right_index])) != int(output_bits[output_index]):
                            valid = False
                            break
                    if valid:
                        chosen = (left_index, right_index, op_name)
                        break
                if chosen is not None:
                    break
            if chosen is not None:
                break
        if chosen is None:
            return None
        payload.append(chosen)
    return tuple(payload)


def derive_boolean3_payload(mod: Any, examples: list[tuple[str, str]]) -> tuple[tuple[int, int, int, str], ...] | None:
    payload: list[tuple[int, int, int, str]] = []
    for output_index in range(8):
        chosen: tuple[int, int, int, str] | None = None
        for op_name in BOOLEAN3_OPERATION_ORDER:
            operation = mod.BIT_BOOLEAN3_OPERATIONS[op_name]
            for first_index in range(8):
                for second_index in range(8):
                    for third_index in range(8):
                        valid = True
                        for input_bits, output_bits in examples:
                            if operation(
                                int(input_bits[first_index]),
                                int(input_bits[second_index]),
                                int(input_bits[third_index]),
                            ) != int(output_bits[output_index]):
                                valid = False
                                break
                        if valid:
                            chosen = (first_index, second_index, third_index, op_name)
                            break
                    if chosen is not None:
                        break
                if chosen is not None:
                    break
            if chosen is not None:
                break
        if chosen is None:
            return None
        payload.append(chosen)
    return tuple(payload)


def render_boolean2_support_line(input_bits: str, output_bits: str) -> str:
    return f"- {input_bits} -> {output_bits} is consistent with the same two-bit boolean equations."


def render_boolean3_support_line(input_bits: str, output_bits: str) -> str:
    return f"- {input_bits} -> {output_bits} is consistent with the same three-bit boolean equations."


def render_boolean2_query_block(mod: Any, payload: tuple[tuple[int, int, str], ...], query_bits: str) -> list[str]:
    lines = ["So the rule is:"]
    for output_index, spec in enumerate(payload, start=1):
        lines.append(f"o{output_index} = {boolean2_expression(spec)}")
    lines.append(f"Query x = {query_bits}")
    for output_index, spec in enumerate(payload, start=1):
        left_index, right_index, op_name = spec
        left = int(query_bits[left_index])
        right = int(query_bits[right_index])
        result = mod.BIT_BOOLEAN2_OPERATIONS[op_name](left, right)
        lines.append(f"o{output_index} uses i{left_index + 1}={left}, i{right_index + 1}={right} -> {result}")
    lines.append("Put the resulting 8-bit output in the final box.")
    return lines


def render_boolean3_query_block(mod: Any, payload: tuple[tuple[int, int, int, str], ...], query_bits: str) -> list[str]:
    lines = ["So the rule is:"]
    for output_index, spec in enumerate(payload, start=1):
        lines.append(f"o{output_index} = {boolean3_expression(spec)}")
    lines.append(f"Query x = {query_bits}")
    for output_index, spec in enumerate(payload, start=1):
        first_index, second_index, third_index, op_name = spec
        first = int(query_bits[first_index])
        second = int(query_bits[second_index])
        third = int(query_bits[third_index])
        result = mod.BIT_BOOLEAN3_OPERATIONS[op_name](first, second, third)
        lines.append(
            f"o{output_index} uses i{first_index + 1}={first}, i{second_index + 1}={second}, i{third_index + 1}={third} -> {result}"
        )
    lines.append("Put the resulting 8-bit output in the final box.")
    return lines


def build_prompt(examples: list[tuple[str, str]], query_bits: str) -> str:
    example_lines = "\n".join(f"{input_bits} -> {output_bits}" for input_bits, output_bits in examples)
    return PROMPT_TEMPLATE.format(example_lines=example_lines, query_bits=query_bits)


def deterministic_id(prefix: str, parts: list[str]) -> str:
    digest = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def desired_support_count(style_variant: str) -> int:
    if style_variant == "trace_boxed_full":
        return 2
    if style_variant in {"trace_boxed_short", "trace_boxed_query_commit"}:
        return 1
    return 0


def select_support_examples(
    rendered_lines: list[tuple[tuple[str, str], str]],
    answer: str,
    rng: random.Random,
    desired_count: int,
) -> list[tuple[str, str]]:
    if desired_count == 0:
        return []
    viable = [example for example, line in rendered_lines if answer not in line]
    if len(viable) < desired_count:
        return []
    if len(viable) == desired_count:
        return viable
    return rng.sample(viable, desired_count)


def render_trace_segments(
    mod: Any,
    strong_group: str,
    exact_rule: str,
    rule_payload: Any,
    support_examples: list[tuple[str, str]],
    query_bits: str,
) -> tuple[list[str], list[str], list[str]]:
    support_lines: list[str] = []
    rule_lines: list[str] = []
    query_lines: list[str] = []
    if strong_group in {"binary_structured_byte_formula", "binary_structured_byte_formula_abstract", "binary_structured_byte_not_formula"}:
        ast = parse_formula(exact_rule)
        for example in support_examples:
            support_lines.append(render_formula_support_line(mod, exact_rule, ast, example[0], example[1]))
        rule_lines.append(f"So the rule is {exact_rule}.")
        query_lines.extend(render_formula_query_block(mod, exact_rule, ast, query_bits))
    elif strong_group == "binary_byte_transform":
        transform_name, param = rule_payload
        for input_bits, output_bits in support_examples:
            if param is None:
                support_lines.append(f"- {input_bits} -> {output_bits} because {transform_name}({input_bits}) = {output_bits}")
            else:
                support_lines.append(
                    f"- {input_bits} -> {output_bits} because {transform_name} with mask {format_byte(param)} matches the given output"
                )
        if param is None:
            rule_lines.append(f"So the rule is {transform_name}.")
        else:
            rule_lines.append(f"So the rule is {transform_name} with mask {format_byte(param)}.")
        query_lines.append(f"Query x = {query_bits}")
        if param is not None:
            query_lines.append(f"mask = {format_byte(param)}")
        query_lines.append(f"Apply {transform_name} to the query and put the resulting 8-bit output in the final box.")
    elif strong_group == "binary_affine_xor":
        for input_bits, output_bits in support_examples:
            support_lines.append(render_affine_support_line(input_bits, output_bits))
        query_lines.extend(render_affine_query_block(rule_payload, query_bits))
    elif strong_group in {"binary_bit_permutation_bijection", "binary_bit_permutation_independent"}:
        for input_bits, output_bits in support_examples:
            support_lines.append(render_mapping_support_line(strong_group, input_bits, output_bits))
        query_lines.extend(render_mapping_query_block(rule_payload, query_bits))
    elif strong_group == "binary_two_bit_boolean":
        for input_bits, output_bits in support_examples:
            support_lines.append(render_boolean2_support_line(input_bits, output_bits))
        query_lines.extend(render_boolean2_query_block(mod, rule_payload, query_bits))
    elif strong_group == "binary_three_bit_boolean":
        for input_bits, output_bits in support_examples:
            support_lines.append(render_boolean3_support_line(input_bits, output_bits))
        query_lines.extend(render_boolean3_query_block(mod, rule_payload, query_bits))
    else:
        raise ValueError(f"Unsupported strong group: {strong_group}")
    return support_lines, rule_lines, query_lines


def compact_query_lines(query_lines: list[str], max_lines: int) -> list[str]:
    if len(query_lines) <= max_lines:
        return list(query_lines)
    if max_lines <= 1:
        return [query_lines[0]]
    query_index = next((index for index, line in enumerate(query_lines) if line.startswith("Query x = ")), None)
    selected_indices: list[int] = [0]
    if query_index is not None and query_index not in selected_indices:
        selected_indices.append(query_index)
    if (len(query_lines) - 1) not in selected_indices:
        selected_indices.append(len(query_lines) - 1)
    for index in range(1, len(query_lines) - 1):
        if len(selected_indices) >= max_lines:
            break
        if index not in selected_indices:
            selected_indices.append(index)
    selected_indices = sorted(selected_indices[:max_lines])
    return [query_lines[index] for index in selected_indices]


def render_generated_cot(
    mod: Any,
    style_variant: str,
    strong_group: str,
    exact_rule: str,
    rule_payload: Any,
    support_examples: list[tuple[str, str]],
    query_bits: str,
    answer: str,
) -> str:
    support_lines, rule_lines, query_lines = render_trace_segments(
        mod,
        strong_group,
        exact_rule,
        rule_payload,
        support_examples,
        query_bits,
    )
    lines = ["<think>"]
    if style_variant == "trace_boxed_full":
        lines.append("Check examples:")
        lines.extend(support_lines)
        lines.extend(rule_lines)
        lines.extend(query_lines)
        lines.append("Constraints: exact_8bit, leading_zeros, box_only_final.")
    elif style_variant == "trace_boxed_short":
        lines.append("Check examples:")
        lines.extend(support_lines[:1])
        lines.extend(rule_lines)
        lines.extend(compact_query_lines(query_lines, max_lines=4))
        lines.append(f"Final byte for the query = {answer}.")
        lines.append("Put only this 8-bit byte in the final box.")
        lines.append("Constraints: exact_8bit, leading_zeros, box_only_final.")
    elif style_variant == "trace_boxed_query_commit":
        lines.append("Use the same verified rule from the examples.")
        lines.extend(rule_lines)
        lines.extend(compact_query_lines(query_lines, max_lines=3))
        lines.append(f"Therefore the final 8-bit output for the query is {answer}.")
        lines.append("Only this byte belongs in the final box.")
        lines.append("Constraints: exact_8bit, leading_zeros, box_only_final.")
    elif style_variant == "boxed_only_closure":
        lines.append("Use the verified rule from the examples and output only the final 8-bit byte with leading zeros.")
        lines.append("Do not add any extra numbers outside the final box.")
        lines.append("Constraints: exact_8bit, leading_zeros, box_only_final.")
    else:
        raise ValueError(f"Unsupported style_variant: {style_variant}")
    lines.append("</think>")
    return "\n".join(lines)


def build_seed_configs(mod: Any) -> list[SeedConfig]:
    configs: list[SeedConfig] = []
    with ANALYSIS_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["family"] != "bit_manipulation" or row["selection_tier"] != "verified_trace_ready":
                continue
            strong_group = row["teacher_solver_candidate"]
            if strong_group not in GROUP_WEIGHTS:
                continue
            examples, _ = parse_binary_prompt(row["prompt"])
            example_count = len(examples)
            payload = parse_json(row["family_analysis_json"])

            if strong_group in {"binary_structured_byte_formula", "binary_structured_byte_formula_abstract"}:
                exact_rule = row["bit_structured_formula_name"]
                if not exact_rule:
                    continue
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, exact_rule))
                continue

            if strong_group == "binary_structured_byte_not_formula":
                exact_rule = row["bit_not_structured_formula_name"]
                if not exact_rule:
                    continue
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, exact_rule))
                continue

            if strong_group == "binary_byte_transform":
                names = [name for name in row["bit_byte_transform_names"].split("|") if name]
                if len(names) != 1:
                    continue
                transform_name, param = parse_exact_byte_transform_rule(names[0], examples)
                exact_rule = transform_name if param is None else f"{transform_name}({format_byte(param)})"
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, (transform_name, param)))
                continue

            if strong_group == "binary_affine_xor":
                free_vars = payload.get("affine_free_var_counts", [])
                if not free_vars or not all(value == 0 for value in free_vars):
                    continue
                coeffs = derive_exact_affine_coeffs(mod, examples)
                if coeffs is None:
                    continue
                exact_rule = "|".join(serialize_affine_equation(coeff) for coeff in coeffs)
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, coeffs))
                continue

            if strong_group == "binary_bit_permutation_bijection":
                if payload.get("bijection_search_explored", 0) != 1:
                    continue
                candidate_sets = mod.build_bit_candidate_sets(examples)
                mapping, count = recover_unique_bijection_mapping(candidate_sets)
                if mapping is None or count != 1:
                    continue
                exact_rule = "|".join(mapping_line(idx, src, bool(flip)) for idx, (src, flip) in enumerate(mapping))
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, tuple((src, bool(flip)) for src, flip in mapping)))
                continue

            if strong_group == "binary_bit_permutation_independent":
                counts = parse_signature_counts(row["bit_candidate_signature"])
                if not counts or not all(value == 1 for value in counts):
                    continue
                mapping = parse_unique_independent_mapping(row["bit_candidate_signature"])
                if mapping is None:
                    continue
                exact_rule = "|".join(mapping_line(idx, src, flip) for idx, (src, flip) in enumerate(mapping))
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, mapping))
                continue

            if strong_group == "binary_two_bit_boolean":
                rule_payload = derive_boolean2_payload(mod, examples)
                if rule_payload is None:
                    continue
                exact_rule = "|".join(f"o{idx + 1}={boolean2_expression(spec)}" for idx, spec in enumerate(rule_payload))
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, rule_payload))
                continue

            if strong_group == "binary_three_bit_boolean":
                rule_payload = derive_boolean3_payload(mod, examples)
                if rule_payload is None:
                    continue
                exact_rule = "|".join(f"o{idx + 1}={boolean3_expression(spec)}" for idx, spec in enumerate(rule_payload))
                configs.append(SeedConfig(row["id"], strong_group, exact_rule, example_count, rule_payload))
                continue
    return configs


def load_original_prompt_set() -> set[str]:
    prompts: set[str] = set()
    with ORIGINAL_TRAIN_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            prompts.add(row["prompt"])
    return prompts


def sample_distinct_values(rng: random.Random, count: int) -> list[int]:
    return rng.sample(range(256), count)


def apply_seed_rule(mod: Any, config: SeedConfig, bits: str) -> str:
    if config.strong_group in {"binary_structured_byte_formula", "binary_structured_byte_formula_abstract"}:
        return format_byte(evaluate_formula(mod, parse_formula(config.exact_rule), bits_to_int(bits)))
    if config.strong_group == "binary_structured_byte_not_formula":
        return format_byte(evaluate_formula(mod, parse_formula(config.exact_rule), bits_to_int(bits)))
    if config.strong_group == "binary_byte_transform":
        transform_name, param = config.rule_payload
        return apply_byte_transform(mod, transform_name, param, bits)
    if config.strong_group == "binary_affine_xor":
        return apply_affine_coeffs(config.rule_payload, bits)
    if config.strong_group in {"binary_bit_permutation_bijection", "binary_bit_permutation_independent"}:
        return apply_mapping_rule(config.rule_payload, bits)
    if config.strong_group == "binary_two_bit_boolean":
        return apply_boolean2_payload(mod, config.rule_payload, bits)
    if config.strong_group == "binary_three_bit_boolean":
        return apply_boolean3_payload(mod, config.rule_payload, bits)
    raise ValueError(f"Unsupported group: {config.strong_group}")


def build_support_lines(
    mod: Any,
    config: SeedConfig,
    examples: list[tuple[str, str]],
) -> list[tuple[tuple[str, str], str]]:
    rendered: list[tuple[tuple[str, str], str]] = []
    if config.strong_group in {"binary_structured_byte_formula", "binary_structured_byte_formula_abstract", "binary_structured_byte_not_formula"}:
        ast = parse_formula(config.exact_rule)
        for example in examples:
            rendered.append((example, render_formula_support_line(mod, config.exact_rule, ast, example[0], example[1])))
        return rendered
    if config.strong_group == "binary_byte_transform":
        transform_name, param = config.rule_payload
        for input_bits, output_bits in examples:
            if param is None:
                text = f"- {input_bits} -> {output_bits} because {transform_name}({input_bits}) = {output_bits}"
            else:
                text = f"- {input_bits} -> {output_bits} because {transform_name} with mask {format_byte(param)} matches the given output"
            rendered.append(((input_bits, output_bits), text))
        return rendered
    if config.strong_group == "binary_affine_xor":
        for example in examples:
            rendered.append((example, render_affine_support_line(example[0], example[1])))
        return rendered
    if config.strong_group in {"binary_bit_permutation_bijection", "binary_bit_permutation_independent"}:
        for example in examples:
            rendered.append((example, render_mapping_support_line(config.strong_group, example[0], example[1])))
        return rendered
    if config.strong_group == "binary_two_bit_boolean":
        for example in examples:
            rendered.append((example, render_boolean2_support_line(example[0], example[1])))
        return rendered
    if config.strong_group == "binary_three_bit_boolean":
        for example in examples:
            rendered.append((example, render_boolean3_support_line(example[0], example[1])))
        return rendered
    raise ValueError(f"Unsupported group: {config.strong_group}")


def recover_mask_from_examples(transform_name: str, examples: list[tuple[str, str]]) -> int | None:
    first_input, first_output = examples[0]
    input_value = bits_to_int(first_input)
    output_value = bits_to_int(first_output)
    if transform_name == "xor_mask":
        return input_value ^ output_value
    if transform_name in {"and_mask", "or_mask"}:
        return output_value
    return None


def validate_seed_row(
    mod: Any,
    config: SeedConfig,
    style_variant: str,
    prompt: str,
    examples: list[tuple[str, str]],
    support_examples: list[tuple[str, str]],
    query_bits: str,
    answer: str,
    generated_cot: str,
    blocked_prompts: set[str],
) -> tuple[bool, str]:
    if prompt in blocked_prompts:
        return False, "prompt_duplicate"
    if not generated_cot.startswith("<think>") or not generated_cot.endswith("</think>"):
        return False, "bad_think_wrapper"

    if style_variant == "trace_boxed_full" and answer in generated_cot:
        return False, "answer_leak_in_generated_cot"
    if style_variant == "boxed_only_closure" and answer in generated_cot:
        return False, "answer_leak_in_generated_cot"
    if style_variant == "trace_boxed_short" and f"Final byte for the query = {answer}." not in generated_cot:
        return False, "missing_final_commit_line"
    if style_variant == "trace_boxed_query_commit" and f"Therefore the final 8-bit output for the query is {answer}." not in generated_cot:
        return False, "missing_final_commit_line"

    teacher_response = f"{generated_cot}\n\n\\boxed{{{answer}}}"
    if count_non_empty_boxed(teacher_response) != 1:
        return False, "bad_boxed_count"
    if not teacher_response.rstrip().endswith(f"\\boxed{{{answer}}}"):
        return False, "final_box_not_terminal"
    if extract_final_answer(teacher_response) != answer:
        return False, "metric_extraction_mismatch"

    if apply_seed_rule(mod, config, query_bits) != answer:
        return False, "forward_answer_mismatch"

    if config.strong_group in {"binary_structured_byte_formula", "binary_structured_byte_formula_abstract"}:
        matches = mod.infer_bit_structured_byte_formula_matches(examples, query_bits)
        if len(matches) != 1 or matches[0] != (config.exact_rule, answer):
            return False, "solver_recovery_mismatch"
    elif config.strong_group == "binary_structured_byte_not_formula":
        matches = mod.infer_bit_structured_byte_not_formula_matches(examples, query_bits)
        if len(matches) != 1 or matches[0] != (config.exact_rule, answer):
            return False, "solver_recovery_mismatch"
    elif config.strong_group == "binary_byte_transform":
        transform_name, param = config.rule_payload
        predicted, names = mod.infer_bit_byte_transform_answer(examples, query_bits)
        if predicted != answer or len(names) != 1 or names[0] != transform_name:
            return False, "solver_recovery_mismatch"
        if recover_mask_from_examples(transform_name, examples) != param:
            return False, "byte_transform_param_mismatch"
    elif config.strong_group == "binary_affine_xor":
        predicted, free_vars = mod.infer_bit_affine_xor_answer(examples, query_bits)
        if predicted != answer or not free_vars or not all(value == 0 for value in free_vars):
            return False, "solver_recovery_mismatch"
    elif config.strong_group == "binary_bit_permutation_bijection":
        candidate_sets = mod.build_bit_candidate_sets(examples)
        recovered_mapping, count = recover_unique_bijection_mapping(candidate_sets)
        if count != 1 or recovered_mapping != config.rule_payload:
            return False, "bijection_mapping_mismatch"
        answers, explored = mod.infer_bit_bijection_answers(candidate_sets, query_bits)
        if answer not in answers or len(answers) != 1 or explored != 1:
            return False, "solver_recovery_mismatch"
    elif config.strong_group == "binary_bit_permutation_independent":
        candidate_sets = mod.build_bit_candidate_sets(examples)
        predicted, choice_counts = mod.infer_bit_independent_answer(candidate_sets, query_bits)
        if predicted != answer or not choice_counts or not all(value == 1 for value in choice_counts):
            return False, "solver_recovery_mismatch"
    elif config.strong_group == "binary_two_bit_boolean":
        predicted, value_counts, _support_counts = mod.infer_bit_two_bit_boolean_answer(examples, query_bits)
        if predicted != answer or not value_counts or not all(value == 1 for value in value_counts):
            return False, "solver_recovery_mismatch"
    elif config.strong_group == "binary_three_bit_boolean":
        predicted, value_counts, _support_counts = mod.infer_bit_three_bit_boolean_answer(examples, query_bits)
        if predicted != answer or not value_counts or not all(value == 1 for value in value_counts):
            return False, "solver_recovery_mismatch"
    else:
        return False, "unsupported_group"

    regenerated = render_generated_cot(
        mod,
        style_variant,
        config.strong_group,
        config.exact_rule,
        config.rule_payload,
        support_examples,
        query_bits,
        answer,
    )
    if generated_cot != regenerated:
        return False, "canonical_render_mismatch"

    return True, "accepted"


def generate_one_row(
    mod: Any,
    config: SeedConfig,
    style_variant: str,
    rng: random.Random,
    blocked_prompts: set[str],
    synthetic_index: int,
    max_attempts: int,
) -> tuple[dict[str, str] | None, str]:
    example_count = max(8, min(config.example_count, 10))

    for _ in range(max_attempts):
        sample_values = sample_distinct_values(rng, example_count + 1)
        query_value = sample_values[0]
        example_values = sample_values[1:]

        query_bits = format_byte(query_value)
        examples = [(format_byte(value), apply_seed_rule(mod, config, format_byte(value))) for value in example_values]
        answer = apply_seed_rule(mod, config, query_bits)

        support_lines = build_support_lines(mod, config, examples)
        support_examples = select_support_examples(
            support_lines,
            answer,
            rng,
            desired_support_count(style_variant),
        )
        if len(support_examples) < desired_support_count(style_variant):
            continue

        generated_cot = render_generated_cot(
            mod,
            style_variant,
            config.strong_group,
            config.exact_rule,
            config.rule_payload,
            support_examples,
            query_bits,
            answer,
        )
        prompt = build_prompt(examples, query_bits)

        ok, reason = validate_seed_row(
            mod=mod,
            config=config,
            style_variant=style_variant,
            prompt=prompt,
            examples=examples,
            support_examples=support_examples,
            query_bits=query_bits,
            answer=answer,
            generated_cot=generated_cot,
            blocked_prompts=blocked_prompts,
        )
        if not ok:
            continue

        synthetic_id = deterministic_id(
            "bit_synth_exact_trace_cot_v1_1",
            [
                str(synthetic_index),
                config.seed_row_id,
                config.strong_group,
                style_variant,
                config.exact_rule,
                prompt,
                answer,
            ],
        )
        return (
            {
                "id": synthetic_id,
                "prompt": prompt,
                "answer": answer,
                "generated_cot": generated_cot,
                "label": "binary",
                "assistant_style": ASSISTANT_STYLE_BY_VARIANT[style_variant],
                "source_selection_tier": SOURCE_TIER_BY_VARIANT[style_variant],
            },
            "accepted",
        )

    return None, "max_attempts_exceeded"


def weighted_generation_plan(seed_configs: list[SeedConfig], rng: random.Random, target_rows: int) -> list[tuple[str, SeedConfig]]:
    style_counts = dict(STYLE_TARGET_COUNTS)
    total = sum(style_counts.values())
    if total != target_rows:
        scale = target_rows / total
        adjusted: dict[str, int] = {}
        remaining = target_rows
        items = list(style_counts.items())
        for index, (name, count) in enumerate(items):
            if index == len(items) - 1:
                adjusted[name] = remaining
            else:
                adjusted_count = int(round(count * scale))
                adjusted[name] = adjusted_count
                remaining -= adjusted_count
        style_counts = adjusted

    weights = [GROUP_WEIGHTS[config.strong_group] for config in seed_configs]
    plan: list[tuple[str, SeedConfig]] = []
    for style_variant, count in style_counts.items():
        sampled = rng.choices(seed_configs, weights=weights, k=count)
        plan.extend((style_variant, config) for config in sampled)
    rng.shuffle(plan)
    return plan


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_report(path: Path, manifest: dict[str, Any]) -> None:
    style_counts = manifest["style_variant_counts"]
    group_counts = manifest["group_counts"]
    lines = [
        "# bit_synth_exact_trace_cot_v1_1",
        "",
        "## 概要",
        "",
        "- README.md の boxed-first 抽出を前提に、v1 の exact-trace 路線を維持しつつ near-miss 回収用の short/query-commit/closure-only supervision を追加した v1.1 生成版。",
        f"- 生成行数: {manifest['generated_rows']}",
        f"- seed: {manifest['seed']}",
        "- 計測スコア: 未計測。学習と評価はまだ実行していないため pending。",
        "",
        "## Style Mixture",
        "",
    ]
    for name, count in style_counts.items():
        lines.append(f"- {name}: {count}")
    lines.extend([
        "",
        "## Group Counts",
        "",
    ])
    for name, count in group_counts.items():
        lines.append(f"- {name}: {count}")
    lines.extend([
        "",
        "## Training Compatibility",
        "",
        "- 列構成は v1 と同一で、assistant_style は trace_boxed / boxed_only の既存2値に収めている。",
        "- 既存 train-bit-synth-exact-trace-cot_merge_lora.ipynb は、DATASET_CSV と MANIFEST_JSON の差し替えだけで v1.1 を読める。",
        "",
        "## Output Files",
        "",
        f"- CSV: {manifest['output_csv']}",
        f"- Manifest: {manifest['manifest_json']}",
        f"- Script: {manifest['script']}",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def main() -> None:
    args = parse_args()
    mod = load_module(ANALYSIS_MODULE)
    rng = random.Random(args.seed)

    blocked_prompts = load_original_prompt_set()
    seed_configs = build_seed_configs(mod)
    if not seed_configs:
        raise RuntimeError("No exact-trace-safe seed configs found.")

    generation_plan = weighted_generation_plan(seed_configs, rng, args.target_rows)
    target_style_counts = Counter(style_variant for style_variant, _config in generation_plan)
    config_weights = [GROUP_WEIGHTS[config.strong_group] for config in seed_configs]

    output_rows: list[dict[str, str]] = []
    reject_reasons: Counter[str] = Counter()
    group_counts: Counter[str] = Counter()
    seed_counts: Counter[str] = Counter()
    exact_rule_counts: Counter[str] = Counter()
    style_variant_counts: Counter[str] = Counter()

    for synthetic_index, (style_variant, config) in enumerate(generation_plan, start=1):
        row, status = generate_one_row(
            mod=mod,
            config=config,
            style_variant=style_variant,
            rng=rng,
            blocked_prompts=blocked_prompts,
            synthetic_index=synthetic_index,
            max_attempts=args.max_attempts_per_row,
        )
        if row is None:
            reject_reasons[status] += 1
            continue
        output_rows.append(row)
        blocked_prompts.add(row["prompt"])
        group_counts[config.strong_group] += 1
        seed_counts[config.seed_row_id] += 1
        exact_rule_counts[config.exact_rule] += 1
        style_variant_counts[style_variant] += 1

    fallback_attempts = 0
    while len(output_rows) < args.target_rows and fallback_attempts < args.target_rows * 40:
        missing_styles = [
            style_variant
            for style_variant, target_count in target_style_counts.items()
            if style_variant_counts[style_variant] < target_count
        ]
        if not missing_styles:
            break
        style_variant = rng.choice(missing_styles)
        config = rng.choices(seed_configs, weights=config_weights, k=1)[0]
        synthetic_index = len(output_rows) + fallback_attempts + 1
        row, status = generate_one_row(
            mod=mod,
            config=config,
            style_variant=style_variant,
            rng=rng,
            blocked_prompts=blocked_prompts,
            synthetic_index=synthetic_index,
            max_attempts=args.max_attempts_per_row,
        )
        fallback_attempts += 1
        if row is None:
            reject_reasons[status] += 1
            continue
        output_rows.append(row)
        blocked_prompts.add(row["prompt"])
        group_counts[config.strong_group] += 1
        seed_counts[config.seed_row_id] += 1
        exact_rule_counts[config.exact_rule] += 1
        style_variant_counts[style_variant] += 1

    if len(output_rows) != args.target_rows:
        raise RuntimeError(
            f"Failed to generate target rows. wanted={args.target_rows} got={len(output_rows)} reject_reasons={dict(reject_reasons)}"
        )

    write_csv(args.output_csv, output_rows)
    manifest = {
        "script": rel(Path(__file__)),
        "analysis_csv": rel(ANALYSIS_CSV),
        "original_train_csv": rel(ORIGINAL_TRAIN_CSV),
        "output_csv": rel(args.output_csv),
        "manifest_json": rel(args.manifest_json),
        "report_md": rel(args.report_md),
        "target_rows": args.target_rows,
        "generated_rows": len(output_rows),
        "seed": args.seed,
        "seed_config_count": len(seed_configs),
        "group_counts": dict(sorted(group_counts.items())),
        "style_variant_counts": dict(sorted(style_variant_counts.items())),
        "assistant_style_counts": dict(sorted(Counter(row["assistant_style"] for row in output_rows).items())),
        "source_selection_tier_counts": dict(sorted(Counter(row["source_selection_tier"] for row in output_rows).items())),
        "reject_reasons": dict(sorted(reject_reasons.items())),
        "max_attempts_per_row": args.max_attempts_per_row,
        "distinct_seed_rows_used": len(seed_counts),
        "distinct_exact_rules_used": len(exact_rule_counts),
        "group_weights": GROUP_WEIGHTS,
        "style_target_counts": STYLE_TARGET_COUNTS,
        "output_columns": OUTPUT_COLUMNS,
    }
    write_json(args.manifest_json, manifest)
    write_report(args.report_md, manifest)

    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()