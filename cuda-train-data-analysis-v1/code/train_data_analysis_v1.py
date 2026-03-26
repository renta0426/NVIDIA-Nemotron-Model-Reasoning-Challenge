#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

import pandas as pd


SCRIPT_VERSION = "cuda-train-data-analysis-v1"

FAMILY_LABELS = {
    "bit_manipulation": "binary",
    "gravity_constant": "gravity",
    "roman_numeral": "roman",
    "symbol_equation": "symbol",
    "text_decryption": "text",
    "unit_conversion": "unit",
}

BASELINE_TEACHER_SOLVED = {
    "bit_manipulation": 306,
    "gravity_constant": 0,
    "roman_numeral": 1576,
    "symbol_equation": 0,
    "text_decryption": 0,
    "unit_conversion": 1594,
}

ROMAN_VALUES = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]

BIT_BOOLEAN2_OPERATIONS = {
    "x": lambda x, y: x,
    "not_x": lambda x, y: 1 - x,
    "y": lambda x, y: y,
    "not_y": lambda x, y: 1 - y,
    "xor": lambda x, y: x ^ y,
    "xnor": lambda x, y: 1 - (x ^ y),
    "and": lambda x, y: x & y,
    "nand": lambda x, y: 1 - (x & y),
    "or": lambda x, y: x | y,
    "nor": lambda x, y: 1 - (x | y),
    "x_and_noty": lambda x, y: x & (1 - y),
    "notx_and_y": lambda x, y: (1 - x) & y,
    "x_implies_y": lambda x, y: (1 - x) | y,
    "y_implies_x": lambda x, y: (1 - y) | x,
}

BIT_BOOLEAN3_OPERATIONS = {
    "majority": lambda a, b, c: 1 if (a + b + c) >= 2 else 0,
    "choice": lambda a, b, c: (a & b) | ((1 - a) & c),
    "parity3": lambda a, b, c: a ^ b ^ c,
}
BIT_BYTE_TRANSFORMS = {
    "not": lambda value, _: (~value) & 0xFF,
    "xor_mask": lambda value, param: value ^ int(param),
    "and_mask": lambda value, param: value & int(param),
    "or_mask": lambda value, param: value | int(param),
    "lshift": lambda value, _: (value << 1) & 0xFF,
    "rshift": lambda value, _: value >> 1,
    "lrot": lambda value, _: ((value << 1) & 0xFF) | (value >> 7),
    "rrot": lambda value, _: (value >> 1) | ((value & 1) << 7),
    "reverse": lambda value, _: int(format(value & 0xFF, "08b")[::-1], 2),
    "nibble_swap": lambda value, _: int(format(value & 0xFF, "08b")[4:] + format(value & 0xFF, "08b")[:4], 2),
}
BIT_HYBRID_BOOLEAN2_OPERATIONS = {
    "xor": lambda a, b: a ^ b,
    "and": lambda a, b: a & b,
    "or": lambda a, b: a | b,
    "eq": lambda a, b: 1 if a == b else 0,
    "neq": lambda a, b: 1 if a != b else 0,
    "nand": lambda a, b: 1 - (a & b),
    "nor": lambda a, b: 1 - (a | b),
}
BIT_HYBRID_BOOLEAN3_OPERATIONS = {
    "maj": lambda a, b, c: 1 if (a + b + c) >= 2 else 0,
    "xor3": lambda a, b, c: a ^ b ^ c,
    "or3": lambda a, b, c: 1 if (a | b | c) else 0,
    "and3": lambda a, b, c: 1 if (a & b & c) else 0,
}
BIT_STRUCTURED_BYTE_BINARY_OPERATIONS = {
    "xor": lambda a, b: a ^ b,
    "and": lambda a, b: a & b,
    "or": lambda a, b: a | b,
}
BIT_STRUCTURED_ABSTRACT_MIN_SUPPORT = 12
BIT_STRUCTURED_ABSTRACT_MIN_DISTINCT = 6

SYMBOL_NUMERIC_EXPRESSION_PATTERN = re.compile(r"^(\d{2})(.)(\d{2})$")
SYMBOL_NUMERIC_FORMULAS = {
    "x_plus_y": lambda x, y: x + y,
    "x_plus_y_plus1": lambda x, y: x + y + 1,
    "x_plus_y_minus1": lambda x, y: x + y - 1,
    "x_minus_y": lambda x, y: x - y,
    "y_minus_x": lambda x, y: y - x,
    "abs_diff": lambda x, y: abs(x - y),
    "comp99_abs_diff_2d": lambda x, y: 99 - abs(x - y),
    "x_mul_y": lambda x, y: x * y,
    "x_mul_y_plus1": lambda x, y: x * y + 1,
    "x_mul_y_minus1": lambda x, y: x * y - 1,
    "x_div_y": lambda x, y: None if y == 0 or x % y else x // y,
    "y_div_x": lambda x, y: None if x == 0 or y % x else y // x,
    "x_mod_y": lambda x, y: None if y == 0 else x % y,
    "y_mod_x": lambda x, y: None if x == 0 else y % x,
    "x": lambda x, y: x,
    "y": lambda x, y: y,
}
SYMBOL_NUMERIC_FORMATS = {
    "plain": lambda op, n: str(n),
    "zpad2": lambda op, n: f"{int(n):02d}" if 0 <= int(n) <= 99 else str(n),
    "prefix_abs_zpad2": lambda op, n: f"{op}{abs(int(n)):02d}",
    "abs_plain": lambda op, n: str(abs(n)),
    "prefix_always_abs": lambda op, n: f"{op}{abs(n)}",
    "prefix_if_negative": lambda op, n: f"{op}{abs(n)}" if n < 0 else str(n),
}
SYMBOL_NUMERIC_STRING_TEMPLATES = {
    "concat_xy": ("x1", "x2", "y1", "y2"),
    "concat_yx": ("y1", "y2", "x1", "x2"),
    "abs_diff_2d": ("diff_t", "diff_o"),
    "abs_diff_2d_op_suffix": ("diff_t", "diff_o", "op"),
}
SYMBOL_NUMERIC_FORMAT_OVERRIDES = {
    "comp99_abs_diff_2d": ("zpad2", "prefix_abs_zpad2"),
}
SYMBOL_PROMOTION_FORMULA_NAMES = set(SYMBOL_NUMERIC_STRING_TEMPLATES) | set(SYMBOL_NUMERIC_FORMAT_OVERRIDES)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_module(module_name: str, module_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def int_to_roman(value: int) -> str:
    remaining = int(value)
    result: list[str] = []
    for unit_value, symbol in ROMAN_VALUES:
        while remaining >= unit_value:
            result.append(symbol)
            remaining -= unit_value
    return "".join(result)


def decimal_places(text: str) -> int:
    value = str(text).strip()
    if "." not in value:
        return 0
    return len(value.split(".", 1)[1])


def format_decimal(value: float, decimals: int) -> str:
    return format(round(float(value), int(decimals)), f".{int(decimals)}f")


def normalize_spaces(text: str) -> str:
    return " ".join(str(text).split())


def answers_match(gold_answer: str, predicted_answer: str) -> bool:
    gold_text = str(gold_answer).strip()
    predicted_text = str(predicted_answer).strip()
    try:
        return math.isclose(float(gold_text), float(predicted_text), rel_tol=1e-2, abs_tol=1e-5)
    except (TypeError, ValueError):
        return predicted_text.lower() == gold_text.lower()


def invert_bit(bit: str) -> str:
    return "1" if bit == "0" else "0"


def rotate_left_byte(value: int, shift: int) -> int:
    shift %= 8
    return (((value & 0xFF) << shift) & 0xFF) | ((value & 0xFF) >> (8 - shift))


def rotate_right_byte(value: int, shift: int) -> int:
    shift %= 8
    return ((value & 0xFF) >> shift) | (((value & 0xFF) << (8 - shift)) & 0xFF)


def reverse_byte_bits(value: int) -> int:
    return int(format(value & 0xFF, "08b")[::-1], 2)


def nibble_swap_byte(value: int) -> int:
    bits = format(value & 0xFF, "08b")
    return int(bits[4:] + bits[:4], 2)


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def parse_baseline_teacher_table(result_path: Path) -> dict[str, dict[str, float]]:
    coverage: dict[str, dict[str, float]] = {}
    if not result_path.exists():
        return coverage
    family_map = {value: key for key, value in FAMILY_LABELS.items()}
    line_pattern = re.compile(r"^\s*\d+\s+(\w+)\s+(\d+)\s+(\d+)\s+([0-9.]+)\s*$")
    for line in result_path.read_text(encoding="utf-8").splitlines():
        match = line_pattern.match(line)
        if match is None:
            continue
        short_name, total, solved, coverage_ratio = match.groups()
        family = family_map.get(short_name)
        if family is None:
            continue
        coverage[family] = {
            "total": int(total),
            "solved": int(solved),
            "coverage": float(coverage_ratio),
        }
    return coverage


def extract_examples(parsed_prompt: Any) -> list[tuple[str, str]]:
    return [(str(example.inp), str(example.out)) for example in getattr(parsed_prompt, "examples", [])]


def score_reasons(base_hard_score: float, reasons: list[str], selection_tier: str) -> float:
    score = float(base_hard_score)
    score += 8.0 if selection_tier == "exclude_suspect" else 0.0
    score += 4.0 if selection_tier == "manual_audit_priority" else 0.0
    score += 2.0 if selection_tier == "answer_only_keep" else 0.0
    score += 0.5 * len(reasons)
    return round(score, 3)


def classify_symbol_subtype(query: str, examples: list[tuple[str, str]]) -> str:
    query_text = (query or "").strip()
    if query_text and re.fullmatch(r"[0-9]{2}[^A-Za-z0-9\s][0-9]{2}", query_text):
        return "numeric_2x2"
    if query_text and re.fullmatch(r"[^A-Za-z0-9\s]{5}", query_text):
        return "glyph_len5"
    if query_text and re.search(r"\d", query_text):
        return "numeric_mixed"
    if query_text and re.search(r"[A-Za-z]", query_text):
        return "alpha_mixed"
    if examples and all(re.fullmatch(r"[^A-Za-z0-9\s]+", inp) for inp, _ in examples[:5]):
        return "glyph_mixed"
    return "symbol_mixed"


def parse_symbol_numeric_examples(prompt: str) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for line in str(prompt).splitlines():
        stripped = line.strip(" `")
        if "=" not in stripped:
            continue
        left, right = stripped.split("=", 1)
        left = left.strip(" `")
        right = right.strip(" `")
        match = SYMBOL_NUMERIC_EXPRESSION_PATTERN.match(left)
        if match is None:
            continue
        rows.append((match.group(1), match.group(2), match.group(3), right))
    return rows


def build_symbol_numeric_token_map(x_text: str, operator: str, y_text: str) -> dict[str, str]:
    abs_diff_text = f"{abs(int(x_text) - int(y_text)):02d}"
    return {
        "x1": x_text[0],
        "x2": x_text[1],
        "y1": y_text[0],
        "y2": y_text[1],
        "op": operator,
        "diff_t": abs_diff_text[0],
        "diff_o": abs_diff_text[1],
    }


def render_symbol_numeric_string_template(template_tokens: tuple[str, ...], x_text: str, operator: str, y_text: str) -> str:
    token_map = build_symbol_numeric_token_map(x_text, operator, y_text)
    return "".join(token_map[token] for token in template_tokens)


def render_symbol_minus_prefix_abs_diff(x_text: str, y_text: str, trim_trailing_zero: bool = False) -> str:
    diff_value = abs(int(x_text) - int(y_text))
    if trim_trailing_zero and diff_value > 0 and diff_value % 10 == 0:
        return f"-{diff_value // 10}"
    return f"-{diff_value:02d}"


def render_symbol_signed_diff_plain(x_text: str, y_text: str) -> str:
    return str(int(x_text) - int(y_text))


def render_symbol_abs_diff_plain(x_text: str, y_text: str) -> str:
    return str(abs(int(x_text) - int(y_text)))


def iter_symbol_numeric_formatters(formula_name: str) -> list[tuple[str, Any]]:
    format_names = SYMBOL_NUMERIC_FORMAT_OVERRIDES.get(formula_name)
    if format_names is None:
        format_names = tuple(name for name in SYMBOL_NUMERIC_FORMATS if name != "zpad2")
    return [(format_name, SYMBOL_NUMERIC_FORMATS[format_name]) for format_name in format_names]


def collect_symbol_numeric_operator_formula_matches(prompt: str, query_text: str, answer: str) -> dict[str, Any]:
    query_match = SYMBOL_NUMERIC_EXPRESSION_PATTERN.match(str(query_text))
    if query_match is None:
        return {
            "query_operator": "",
            "same_operator_example_count": 0,
            "candidate_predictions": [],
            "winning_specs": [],
        }
    query_x_text = query_match.group(1)
    query_operator = query_match.group(2)
    query_y_text = query_match.group(3)
    same_operator_examples = [
        (left_value, right_value, output_text)
        for left_value, operator, right_value, output_text in parse_symbol_numeric_examples(prompt)
        if operator == query_operator
    ]
    candidate_predictions: set[str] = set()
    winning_specs: list[tuple[str, str, str]] = []
    for template_name, template in SYMBOL_NUMERIC_STRING_TEMPLATES.items():
        valid = True
        for left_value_text, right_value_text, output_text in same_operator_examples:
            if render_symbol_numeric_string_template(template, left_value_text, query_operator, right_value_text) != str(output_text):
                valid = False
                break
        if not valid:
            continue
        predicted_answer = render_symbol_numeric_string_template(template, query_x_text, query_operator, query_y_text)
        if template_name.startswith("abs_diff_2d") and len(str(answer).strip()) != len(predicted_answer):
            continue
        candidate_predictions.add(predicted_answer)
        winning_specs.append((template_name, "string_template", predicted_answer))
    query_x = int(query_x_text)
    query_y = int(query_y_text)
    for formula_name, formula in SYMBOL_NUMERIC_FORMULAS.items():
        for format_name, formatter in iter_symbol_numeric_formatters(formula_name):
            valid = True
            for left_value_text, right_value_text, output_text in same_operator_examples:
                numeric_value = formula(int(left_value_text), int(right_value_text))
                if numeric_value is None or formatter(query_operator, numeric_value) != str(output_text):
                    valid = False
                    break
            if not valid:
                continue
            query_numeric_value = formula(query_x, query_y)
            if query_numeric_value is None:
                continue
            predicted_answer = formatter(query_operator, query_numeric_value)
            candidate_predictions.add(predicted_answer)
            winning_specs.append((formula_name, format_name, predicted_answer))
    return {
        "query_operator": query_operator,
        "same_operator_example_count": len(same_operator_examples),
        "candidate_predictions": sorted(candidate_predictions),
        "winning_specs": winning_specs,
    }


def solve_symbol_numeric_operator_formula(prompt: str, query_text: str, answer: str) -> dict[str, Any]:
    match_info = collect_symbol_numeric_operator_formula_matches(prompt, query_text, answer)
    if not match_info["query_operator"]:
        return {
            "solver_name": "",
            "predicted_answer": "",
            "matches_gold": False,
            "same_operator_example_count": 0,
            "candidate_prediction_count": 0,
            "candidate_predictions": [],
            "formula_name": "",
            "format_name": "",
            "query_operator": "",
            "low_shot": False,
        }
    query_operator = str(match_info["query_operator"])
    candidate_predictions = set(str(value) for value in match_info["candidate_predictions"])
    winning_specs = [(str(formula_name), str(format_name), str(predicted_answer)) for formula_name, format_name, predicted_answer in match_info["winning_specs"]]
    chosen_formula_name = ""
    chosen_format_name = ""
    predicted_answer = ""
    if len(candidate_predictions) == 1:
        predicted_answer = next(iter(candidate_predictions))
        for formula_name, format_name, candidate_prediction in winning_specs:
            if candidate_prediction == predicted_answer:
                chosen_formula_name = formula_name
                chosen_format_name = format_name
                break
    matches_gold = bool(predicted_answer and answers_match(str(answer), predicted_answer))
    return {
        "solver_name": "symbol_numeric_operator_formula" if matches_gold else "",
        "predicted_answer": predicted_answer,
        "matches_gold": matches_gold,
        "same_operator_example_count": int(match_info["same_operator_example_count"]),
        "candidate_prediction_count": len(candidate_predictions),
        "candidate_predictions": sorted(candidate_predictions),
        "formula_name": chosen_formula_name,
        "format_name": chosen_format_name,
        "query_operator": query_operator,
        "low_shot": bool(matches_gold and int(match_info["same_operator_example_count"]) <= 1),
    }


def glyph_multiset_mapping_exists(examples: list[tuple[str, str]]) -> bool:
    if not examples:
        return False
    input_chars = sorted({char for source, _ in examples for char in source})
    output_chars = sorted({char for _, target in examples for char in target})
    if not output_chars:
        return False
    occurrence_tables = [{char: source.count(char) for char in input_chars} for source, _ in examples]
    residual_counters = [Counter(target) for _, target in examples]
    ordered_input_chars = sorted(input_chars, key=lambda char: -sum(table.get(char, 0) for table in occurrence_tables))

    @lru_cache(maxsize=None)
    def dfs(index: int, state: tuple[int, ...]) -> bool:
        residuals: list[Counter[str]] = [Counter() for _ in examples]
        pointer = 0
        for example_index in range(len(examples)):
            for output_char in output_chars:
                value = state[pointer]
                if value:
                    residuals[example_index][output_char] = value
                pointer += 1
        if index == len(ordered_input_chars):
            return all(not counter for counter in residuals)
        current_char = ordered_input_chars[index]
        current_counts = [table.get(current_char, 0) for table in occurrence_tables]
        if dfs(index + 1, state):
            return True
        for output_char in output_chars:
            next_state: list[int] = []
            valid = True
            for example_index, counter in enumerate(residuals):
                remaining = counter.get(output_char, 0) - current_counts[example_index]
                if remaining < 0:
                    valid = False
                    break
                for candidate_char in output_chars:
                    if candidate_char == output_char:
                        next_state.append(remaining)
                    else:
                        next_state.append(counter.get(candidate_char, 0))
            if valid and dfs(index + 1, tuple(next_state)):
                return True
        return False

    initial_state: list[int] = []
    for counter in residual_counters:
        for output_char in output_chars:
            initial_state.append(counter.get(output_char, 0))
    return dfs(0, tuple(initial_state))


def glyph_output_order_acyclic(examples: list[tuple[str, str]]) -> bool:
    outputs = [target for _, target in examples if target]
    nodes = sorted({char for output in outputs for char in output})
    if not nodes:
        return False
    edges: dict[str, set[str]] = defaultdict(set)
    indegree = {node: 0 for node in nodes}
    for output in outputs:
        for left_index in range(len(output)):
            for right_index in range(left_index + 1, len(output)):
                left_char = output[left_index]
                right_char = output[right_index]
                if left_char == right_char or right_char in edges[left_char]:
                    continue
                edges[left_char].add(right_char)
                indegree[right_char] += 1
    queue = [node for node, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for neighbor in edges[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    return visited == len(nodes)


def glyph_unique_topological_order(nodes: list[str], edges: dict[str, set[str]]) -> tuple[bool, list[str]]:
    indegree = {node: 0 for node in nodes}
    filtered_edges = {node: set() for node in nodes}
    for left_node, right_nodes in edges.items():
        if left_node not in indegree:
            continue
        for right_node in right_nodes:
            if right_node not in indegree or right_node in filtered_edges[left_node]:
                continue
            filtered_edges[left_node].add(right_node)
            indegree[right_node] += 1
    queue = sorted(node for node, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while queue:
        if len(queue) > 1:
            return False, []
        node = queue.pop(0)
        order.append(node)
        for neighbor in sorted(filtered_edges[node]):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
                queue.sort()
    return (len(order) == len(nodes), order if len(order) == len(nodes) else [])


def enumerate_glyph_query_predictions(analysis_df: pd.DataFrame, v1: Any) -> pd.DataFrame:
    glyph_subset = analysis_df.loc[
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["template_subtype"] == "glyph_len5")
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & (analysis_df["glyph_multiset_possible"])
        & (analysis_df["glyph_order_acyclic"])
    ].reset_index(drop=True)
    records: list[dict[str, Any]] = []
    outcome_limit = 65

    for row in glyph_subset.itertuples(index=False):
        parsed = v1.parse_symbol_prompt(str(row.prompt), str(row.answer))
        examples = extract_examples(parsed)
        query_raw = str(parsed.query_raw or "")
        input_chars = sorted({char for source, _ in examples for char in source})
        output_chars = sorted({char for _, target in examples for char in target})
        unseen_query_chars = sorted({char for char in query_raw if char not in input_chars})
        if unseen_query_chars:
            records.append(
                {
                    "id": str(row.id),
                    "hard_score": float(row.hard_score),
                    "answer": str(row.answer),
                    "query_raw": query_raw,
                    "exact_coarse_status": "query_has_unseen_chars",
                    "glyph_query_unseen_chars": "".join(unseen_query_chars),
                    "query_multiset_count_capped": 0,
                    "query_multiset_count_truncated": False,
                    "multiset_unique": False,
                    "order_unique": False,
                    "predicted_answer": "",
                    "predicted_multiset_json": "",
                    "output_chars": "".join(output_chars),
                }
            )
            continue

        occurrence_tables = [{char: source.count(char) for char in input_chars} for source, _ in examples]
        residual_counters = [Counter(target) for _, target in examples]
        ordered_input_chars = sorted(input_chars, key=lambda char: -sum(table.get(char, 0) for table in occurrence_tables))
        query_char_counts = {char: query_raw.count(char) for char in ordered_input_chars}

        @lru_cache(maxsize=None)
        def dfs(index: int, state: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
            residuals: list[Counter[str]] = [Counter() for _ in examples]
            pointer = 0
            for example_index in range(len(examples)):
                for output_char in output_chars:
                    value = state[pointer]
                    if value:
                        residuals[example_index][output_char] = value
                    pointer += 1
            if index == len(ordered_input_chars):
                return frozenset([tuple(0 for _ in output_chars)]) if all(not counter for counter in residuals) else frozenset()

            current_char = ordered_input_chars[index]
            current_counts = [table.get(current_char, 0) for table in occurrence_tables]
            query_count = query_char_counts.get(current_char, 0)
            outcomes: set[tuple[int, ...]] = set(dfs(index + 1, state))
            if len(outcomes) >= outcome_limit:
                return frozenset(outcomes)

            for output_index, output_char in enumerate(output_chars):
                next_state: list[int] = []
                valid = True
                for example_index, counter in enumerate(residuals):
                    remaining = counter.get(output_char, 0) - current_counts[example_index]
                    if remaining < 0:
                        valid = False
                        break
                    for candidate_char in output_chars:
                        next_state.append(remaining if candidate_char == output_char else counter.get(candidate_char, 0))
                if not valid:
                    continue
                for tail in dfs(index + 1, tuple(next_state)):
                    next_counts = list(tail)
                    next_counts[output_index] += query_count
                    outcomes.add(tuple(next_counts))
                    if len(outcomes) >= outcome_limit:
                        return frozenset(outcomes)
            return frozenset(outcomes)

        initial_state: list[int] = []
        for counter in residual_counters:
            for output_char in output_chars:
                initial_state.append(counter.get(output_char, 0))
        query_multisets = set(dfs(0, tuple(initial_state)))
        multiset_unique = len(query_multisets) == 1
        multiset_truncated = len(query_multisets) >= outcome_limit
        order_unique = False
        predicted_answer = ""
        predicted_multiset_json = ""
        status = "ambiguous_multiset"

        if not query_multisets:
            status = "no_example_only_multiset"
        elif multiset_unique:
            multiset = next(iter(query_multisets))
            predicted_multiset = {
                output_chars[index]: int(count)
                for index, count in enumerate(multiset)
                if int(count) > 0
            }
            predicted_multiset_json = json_dumps(predicted_multiset)
            active_chars = [output_chars[index] for index, count in enumerate(multiset) if int(count) > 0]
            if active_chars:
                edges: dict[str, set[str]] = defaultdict(set)
                for _, target in examples:
                    for left_index in range(len(target)):
                        for right_index in range(left_index + 1, len(target)):
                            left_char = target[left_index]
                            right_char = target[right_index]
                            if left_char != right_char:
                                edges[left_char].add(right_char)
                order_unique, order = glyph_unique_topological_order(active_chars, edges)
                if order_unique:
                    predicted_answer = "".join(char * predicted_multiset.get(char, 0) for char in order)
                    status = "unique_string"
                else:
                    status = "ambiguous_order"
            else:
                order_unique = True
                predicted_answer = ""
                status = "unique_string"

        records.append(
            {
                "id": str(row.id),
                "hard_score": float(row.hard_score),
                "answer": str(row.answer),
                "query_raw": query_raw,
                "exact_coarse_status": status,
                "glyph_query_unseen_chars": "".join(unseen_query_chars),
                "query_multiset_count_capped": int(len(query_multisets)),
                "query_multiset_count_truncated": bool(multiset_truncated),
                "multiset_unique": bool(multiset_unique),
                "order_unique": bool(order_unique),
                "predicted_answer": predicted_answer,
                "predicted_multiset_json": predicted_multiset_json,
                "output_chars": "".join(output_chars),
            }
        )

    if not records:
        return pd.DataFrame(
            columns=[
                "id",
                "hard_score",
                "answer",
                "query_raw",
                "exact_coarse_status",
                "glyph_query_unseen_chars",
                "query_multiset_count_capped",
                "query_multiset_count_truncated",
                "multiset_unique",
                "order_unique",
                "predicted_answer",
                "predicted_multiset_json",
                "output_chars",
            ]
        )
    return pd.DataFrame(records).sort_values(
        ["exact_coarse_status", "hard_score", "id"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def analyze_char_mapping(
    examples: list[tuple[str, str]],
    query: str,
    answer: str,
    *,
    allow_spaces: bool,
) -> dict[str, Any]:
    enc_to_dec: dict[str, str] = {}
    dec_to_enc: dict[str, str] = {}
    length_mismatch = 0
    forward_conflicts = 0
    reverse_conflicts = 0
    space_conflicts = 0

    for source, target in examples:
        if len(source) != len(target):
            length_mismatch += 1
        for source_char, target_char in zip(source, target):
            if allow_spaces and (" " in (source_char, target_char)):
                if source_char != target_char:
                    space_conflicts += 1
                continue
            if source_char in enc_to_dec and enc_to_dec[source_char] != target_char:
                forward_conflicts += 1
            else:
                enc_to_dec[source_char] = target_char
            if target_char in dec_to_enc and dec_to_enc[target_char] != source_char:
                reverse_conflicts += 1
            else:
                dec_to_enc[target_char] = source_char

    unknown_query_chars = sorted({char for char in query if (char != " " or not allow_spaces) and char not in enc_to_dec})
    predicted_chars: list[str] = []
    for char in query:
        if allow_spaces and char == " ":
            predicted_chars.append(" ")
        else:
            predicted_chars.append(enc_to_dec.get(char, "?"))
    predicted_answer = "".join(predicted_chars)
    full_query_covered = not unknown_query_chars
    matches_gold = full_query_covered and normalize_spaces(predicted_answer) == normalize_spaces(answer)
    return {
        "charmap_length_mismatch": int(length_mismatch),
        "charmap_forward_conflicts": int(forward_conflicts),
        "charmap_reverse_conflicts": int(reverse_conflicts),
        "charmap_space_conflicts": int(space_conflicts),
        "charmap_query_unknown_chars": "".join(unknown_query_chars),
        "charmap_query_unknown_count": int(len(unknown_query_chars)),
        "charmap_unique_source_chars": int(len(enc_to_dec)),
        "charmap_unique_target_chars": int(len(dec_to_enc)),
        "charmap_full_query_covered": bool(full_query_covered),
        "charmap_predicted_answer": predicted_answer if full_query_covered else "",
        "charmap_matches_gold": bool(matches_gold),
    }


def analyze_word_dictionary(query: str, answer: str, examples: list[tuple[str, str]]) -> dict[str, Any]:
    source_to_target: dict[str, str] = {}
    conflicts = 0
    for source, target in examples:
        source_words = source.split()
        target_words = target.split()
        if len(source_words) != len(target_words):
            conflicts += 1
            continue
        for source_word, target_word in zip(source_words, target_words, strict=True):
            if source_word in source_to_target and source_to_target[source_word] != target_word:
                conflicts += 1
            else:
                source_to_target[source_word] = target_word
    query_words = query.split()
    missing_words = [word for word in query_words if word not in source_to_target]
    predicted = " ".join(source_to_target.get(word, "?") for word in query_words)
    full_query_covered = not missing_words
    return {
        "wordmap_conflicts": int(conflicts),
        "wordmap_full_query_covered": bool(full_query_covered),
        "wordmap_missing_words": " ".join(missing_words),
        "wordmap_predicted_answer": predicted if full_query_covered else "",
        "wordmap_matches_gold": bool(full_query_covered and normalize_spaces(predicted) == normalize_spaces(answer)),
    }


def analyze_text_answer_completion(examples: list[tuple[str, str]], query: str, answer: str) -> dict[str, Any]:
    enc_to_dec: dict[str, str] = {}
    dec_to_enc: dict[str, str] = {}
    if len(query) != len(answer):
        return {
            "text_answer_completion_ready": False,
            "text_answer_completion_new_pair_count": 0,
            "text_answer_completion_pairs": "",
        }
    for source, target in examples:
        if len(source) != len(target):
            return {
                "text_answer_completion_ready": False,
                "text_answer_completion_new_pair_count": 0,
                "text_answer_completion_pairs": "",
            }
        for source_char, target_char in zip(source, target):
            if " " in (source_char, target_char):
                if source_char != target_char:
                    return {
                        "text_answer_completion_ready": False,
                        "text_answer_completion_new_pair_count": 0,
                        "text_answer_completion_pairs": "",
                    }
                continue
            if source_char in enc_to_dec and enc_to_dec[source_char] != target_char:
                return {
                    "text_answer_completion_ready": False,
                    "text_answer_completion_new_pair_count": 0,
                    "text_answer_completion_pairs": "",
                }
            enc_to_dec[source_char] = target_char
            if target_char in dec_to_enc and dec_to_enc[target_char] != source_char:
                return {
                    "text_answer_completion_ready": False,
                    "text_answer_completion_new_pair_count": 0,
                    "text_answer_completion_pairs": "",
                }
            dec_to_enc[target_char] = source_char
    inferred_pairs: dict[str, str] = {}
    inferred_reverse: dict[str, str] = {}
    for query_char, answer_char in zip(query, answer):
        if " " in (query_char, answer_char):
            if query_char != answer_char:
                return {
                    "text_answer_completion_ready": False,
                    "text_answer_completion_new_pair_count": 0,
                    "text_answer_completion_pairs": "",
                }
            continue
        known_char = enc_to_dec.get(query_char)
        if known_char is not None:
            if known_char != answer_char:
                return {
                    "text_answer_completion_ready": False,
                    "text_answer_completion_new_pair_count": 0,
                    "text_answer_completion_pairs": "",
                }
            continue
        if query_char in inferred_pairs and inferred_pairs[query_char] != answer_char:
            return {
                "text_answer_completion_ready": False,
                "text_answer_completion_new_pair_count": 0,
                "text_answer_completion_pairs": "",
            }
        if answer_char in dec_to_enc and dec_to_enc[answer_char] != query_char:
            return {
                "text_answer_completion_ready": False,
                "text_answer_completion_new_pair_count": 0,
                "text_answer_completion_pairs": "",
            }
        if answer_char in inferred_reverse and inferred_reverse[answer_char] != query_char:
            return {
                "text_answer_completion_ready": False,
                "text_answer_completion_new_pair_count": 0,
                "text_answer_completion_pairs": "",
            }
        inferred_pairs[query_char] = answer_char
        inferred_reverse[answer_char] = query_char
    pair_strings = [f"{source}->{target}" for source, target in sorted(inferred_pairs.items())]
    return {
        "text_answer_completion_ready": True,
        "text_answer_completion_new_pair_count": len(inferred_pairs),
        "text_answer_completion_pairs": "|".join(pair_strings),
    }


def build_bit_candidate_sets(examples: list[tuple[str, str]]) -> list[list[tuple[int, int]]]:
    candidate_sets: list[list[tuple[int, int]]] = []
    for output_index in range(8):
        candidates: list[tuple[int, int]] = []
        for input_index in range(8):
            same = all(output_bits[output_index] == input_bits[input_index] for input_bits, output_bits in examples)
            flipped = all(output_bits[output_index] != input_bits[input_index] for input_bits, output_bits in examples)
            if same:
                candidates.append((input_index, 0))
            if flipped:
                candidates.append((input_index, 1))
        candidate_sets.append(candidates)
    return candidate_sets


def bit_candidate_signature(candidate_sets: list[list[tuple[int, int]]]) -> str:
    signature_parts = []
    for output_index, candidates in enumerate(candidate_sets, start=1):
        candidate_text = ",".join(f"i{input_index + 1}{'^' if flip else ''}" for input_index, flip in candidates) or "none"
        signature_parts.append(f"o{output_index}=[{candidate_text}]")
    return " ".join(signature_parts)


def infer_bit_independent_answer(candidate_sets: list[list[tuple[int, int]]], query_bits: str) -> tuple[str | None, list[int]]:
    if len(query_bits) != 8:
        return None, []
    choice_counts: list[int] = []
    predicted_bits: list[str] = []
    for candidates in candidate_sets:
        if not candidates:
            return None, []
        values = {invert_bit(query_bits[input_index]) if flip else query_bits[input_index] for input_index, flip in candidates}
        choice_counts.append(len(values))
        if len(values) != 1:
            return None, choice_counts
        predicted_bits.append(next(iter(values)))
    return "".join(predicted_bits), choice_counts


def infer_bit_bijection_answers(candidate_sets: list[list[tuple[int, int]]], query_bits: str, limit: int = 4096) -> tuple[set[str], int]:
    answer_set: set[str] = set()
    explored = 0
    order = sorted(range(8), key=lambda index: (len(candidate_sets[index]), index))

    def backtrack(order_position: int, used_inputs: set[int], partial: dict[int, tuple[int, int]]) -> None:
        nonlocal explored
        if explored >= limit:
            return
        if order_position >= len(order):
            output_bits = ["0"] * 8
            for output_index, (input_index, flip) in partial.items():
                bit = query_bits[input_index]
                output_bits[output_index] = invert_bit(bit) if flip else bit
            answer_set.add("".join(output_bits))
            explored += 1
            return
        output_index = order[order_position]
        for input_index, flip in candidate_sets[output_index]:
            if input_index in used_inputs:
                continue
            used_inputs.add(input_index)
            partial[output_index] = (input_index, flip)
            backtrack(order_position + 1, used_inputs, partial)
            partial.pop(output_index, None)
            used_inputs.remove(input_index)
            if explored >= limit:
                return

    if any(not candidates for candidates in candidate_sets):
        return answer_set, explored
    backtrack(0, set(), {})
    return answer_set, explored


def infer_bit_two_bit_boolean_answer(examples: list[tuple[str, str]], query_bits: str) -> tuple[str | None, list[int], list[int]]:
    if len(query_bits) != 8 or not examples:
        return None, [], []
    value_counts: list[int] = []
    support_counts: list[int] = []
    predicted_bits: list[str] = []
    for output_index in range(8):
        values: set[str] = set()
        supports = 0
        for left_index in range(8):
            for right_index in range(8):
                for operation in BIT_BOOLEAN2_OPERATIONS.values():
                    valid = True
                    for input_bits, output_bits in examples:
                        left_bit = int(input_bits[left_index])
                        right_bit = int(input_bits[right_index])
                        target_bit = int(output_bits[output_index])
                        if operation(left_bit, right_bit) != target_bit:
                            valid = False
                            break
                    if not valid:
                        continue
                    query_left = int(query_bits[left_index])
                    query_right = int(query_bits[right_index])
                    values.add(str(operation(query_left, query_right)))
                    supports += 1
        value_counts.append(len(values))
        support_counts.append(supports)
        if len(values) != 1:
            return None, value_counts, support_counts
        predicted_bits.append(next(iter(values)))
    return "".join(predicted_bits), value_counts, support_counts


def infer_bit_three_bit_boolean_answer(examples: list[tuple[str, str]], query_bits: str) -> tuple[str | None, list[int], list[int]]:
    if len(query_bits) != 8 or not examples:
        return None, [], []
    value_counts: list[int] = []
    support_counts: list[int] = []
    predicted_bits: list[str] = []
    for output_index in range(8):
        values: set[str] = set()
        supports = 0
        for first_index in range(8):
            for second_index in range(8):
                for third_index in range(8):
                    for operation in BIT_BOOLEAN3_OPERATIONS.values():
                        valid = True
                        for input_bits, output_bits in examples:
                            first_bit = int(input_bits[first_index])
                            second_bit = int(input_bits[second_index])
                            third_bit = int(input_bits[third_index])
                            target_bit = int(output_bits[output_index])
                            if operation(first_bit, second_bit, third_bit) != target_bit:
                                valid = False
                                break
                        if not valid:
                            continue
                        query_first = int(query_bits[first_index])
                        query_second = int(query_bits[second_index])
                        query_third = int(query_bits[third_index])
                        values.add(str(operation(query_first, query_second, query_third)))
                        supports += 1
        value_counts.append(len(values))
        support_counts.append(supports)
        if len(values) != 1:
            return None, value_counts, support_counts
        predicted_bits.append(next(iter(values)))
    return "".join(predicted_bits), value_counts, support_counts


def rref_gf2(rows: list[list[int]], nvars: int) -> tuple[list[list[int]], list[int]]:
    matrix = [row[:] for row in rows]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(nvars):
        chosen_row = None
        for row_index in range(pivot_row, len(matrix)):
            if matrix[row_index][column]:
                chosen_row = row_index
                break
        if chosen_row is None:
            continue
        matrix[pivot_row], matrix[chosen_row] = matrix[chosen_row], matrix[pivot_row]
        pivot_columns.append(column)
        for row_index in range(len(matrix)):
            if row_index != pivot_row and matrix[row_index][column]:
                matrix[row_index] = [left ^ right for left, right in zip(matrix[row_index], matrix[pivot_row])]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return matrix, pivot_columns


def infer_bit_affine_xor_answer(examples: list[tuple[str, str]], query_bits: str) -> tuple[str | None, list[int]]:
    if len(query_bits) != 8 or not examples:
        return None, []
    query_vector = [int(bit) for bit in query_bits] + [1]
    predicted_bits: list[str] = []
    free_var_counts: list[int] = []
    for output_index in range(8):
        system_rows = [
            [int(bit) for bit in input_bits] + [1, int(output_bits[output_index])]
            for input_bits, output_bits in examples
        ]
        reduced_rows, pivot_columns = rref_gf2(system_rows, 9)
        for row in reduced_rows:
            if not any(row[:9]) and row[9]:
                return None, free_var_counts
        free_columns = [column for column in range(9) if column not in pivot_columns]
        free_var_counts.append(len(free_columns))
        pivot_to_row = {column: row_index for row_index, column in enumerate(pivot_columns)}
        base_solution = [0] * 9
        for column in reversed(pivot_columns):
            row_index = pivot_to_row[column]
            value = reduced_rows[row_index][9]
            for trailing_column in range(column + 1, 9):
                if reduced_rows[row_index][trailing_column]:
                    value ^= base_solution[trailing_column]
            base_solution[column] = value
        predicted_bit = 0
        for query_value, solution_value in zip(query_vector, base_solution):
            predicted_bit ^= query_value & solution_value
        for free_column in free_columns:
            free_vector = [0] * 9
            free_vector[free_column] = 1
            for column in reversed(pivot_columns):
                row_index = pivot_to_row[column]
                value = reduced_rows[row_index][free_column]
                for trailing_column in range(column + 1, 9):
                    if reduced_rows[row_index][trailing_column]:
                        value ^= free_vector[trailing_column]
                free_vector[column] = value
            query_dot = 0
            for query_value, free_value in zip(query_vector, free_vector):
                query_dot ^= query_value & free_value
            if query_dot:
                return None, free_var_counts
        predicted_bits.append(str(predicted_bit))
    return "".join(predicted_bits), free_var_counts


def infer_bit_byte_transform_answer(examples: list[tuple[str, str]], query_bits: str) -> tuple[str | None, list[str]]:
    if len(query_bits) != 8 or not examples:
        return None, []
    pairs = [(int(input_bits, 2), int(output_bits, 2)) for input_bits, output_bits in examples]
    query_value = int(query_bits, 2)
    candidate_names: list[str] = []
    candidate_predictions: set[str] = set()
    params = {
        "not": None,
        "xor_mask": pairs[0][0] ^ pairs[0][1],
        "and_mask": pairs[0][1],
        "or_mask": pairs[0][1],
        "lshift": None,
        "rshift": None,
        "lrot": None,
        "rrot": None,
        "reverse": None,
        "nibble_swap": None,
    }
    for transform_name, transform in BIT_BYTE_TRANSFORMS.items():
        param = params[transform_name]
        if all(transform(input_value, param) == output_value for input_value, output_value in pairs):
            candidate_names.append(transform_name)
            candidate_predictions.add(format(transform(query_value, param) & 0xFF, "08b"))
    if len(candidate_predictions) == 1:
        return next(iter(candidate_predictions)), candidate_names
    return None, candidate_names


@lru_cache(maxsize=1)
def build_bit_structured_byte_formulas() -> tuple[tuple[str, tuple[int, ...]], ...]:
    raw_sources = [
        ("x", lambda value: value & 0xFF),
        ("reverse", reverse_byte_bits),
        ("nibble_swap", nibble_swap_byte),
    ]
    for shift in range(1, 8):
        raw_sources.append((f"rol{shift}", lambda value, shift=shift: rotate_left_byte(value, shift)))
        raw_sources.append((f"ror{shift}", lambda value, shift=shift: rotate_right_byte(value, shift)))
    for shift in range(1, 4):
        raw_sources.append((f"shl{shift}", lambda value, shift=shift: ((value & 0xFF) << shift) & 0xFF))
        raw_sources.append((f"shr{shift}", lambda value, shift=shift: (value & 0xFF) >> shift))

    canonical_sources: dict[tuple[int, ...], str] = {}
    for name, function in raw_sources:
        signature = tuple(function(value) & 0xFF for value in range(256))
        canonical_sources.setdefault(signature, name)
    sources = [(name, signature) for signature, name in sorted(canonical_sources.items(), key=lambda item: item[1])]

    formulas: dict[tuple[int, ...], str] = {}
    for name, signature in sources:
        formulas.setdefault(signature, name)
    for (name_a, signature_a), (name_b, signature_b) in combinations_with_replacement(sources, 2):
        for op_name, operation in BIT_STRUCTURED_BYTE_BINARY_OPERATIONS.items():
            signature = tuple(operation(signature_a[value], signature_b[value]) & 0xFF for value in range(256))
            formulas.setdefault(signature, f"{op_name}({name_a},{name_b})")
    return tuple((name, signature) for signature, name in sorted(formulas.items(), key=lambda item: item[1]))


def infer_bit_structured_byte_formula_matches(examples: list[tuple[str, str]], query_bits: str) -> list[tuple[str, str]]:
    if len(query_bits) != 8 or not examples:
        return []
    pairs = [(int(input_bits, 2), int(output_bits, 2)) for input_bits, output_bits in examples]
    query_value = int(query_bits, 2)
    matches: list[tuple[str, str]] = []
    for formula_name, signature in build_bit_structured_byte_formulas():
        if all(signature[input_value] == output_value for input_value, output_value in pairs):
            matches.append((formula_name, format(signature[query_value] & 0xFF, "08b")))
    return matches


def abstract_bit_structured_source_name(name: str) -> str:
    if re.fullmatch(r"rol\d+", str(name)):
        return "rol"
    if re.fullmatch(r"ror\d+", str(name)):
        return "ror"
    if re.fullmatch(r"shl\d+", str(name)):
        return "shl"
    if re.fullmatch(r"shr\d+", str(name)):
        return "shr"
    return str(name)


def abstract_bit_structured_formula_name(name: str) -> str:
    formula_name = str(name)
    if not formula_name:
        return ""
    if "(" not in formula_name:
        return abstract_bit_structured_source_name(formula_name)
    operation, remainder = formula_name.split("(", 1)
    arguments = [abstract_bit_structured_source_name(part) for part in remainder[:-1].split(",")]
    return f"{operation}({','.join(sorted(arguments))})"


def split_pipe_text(value: Any) -> list[str]:
    return [part for part in str(value).split("|") if part]


@lru_cache(maxsize=1)
def build_bit_hybrid_boolean_candidates() -> tuple[tuple[str, tuple[int, ...], Any], ...]:
    candidates: list[tuple[str, tuple[int, ...], Any]] = []

    def make_unary(index: int, invert: bool) -> Any:
        def fn(input_bits: str, index: int = index, invert: bool = invert) -> int:
            bit = int(input_bits[index])
            return 1 - bit if invert else bit

        return fn

    def make_binary(index_a: int, invert_a: bool, index_b: int, invert_b: bool, operation: Any) -> Any:
        def fn(
            input_bits: str,
            index_a: int = index_a,
            invert_a: bool = invert_a,
            index_b: int = index_b,
            invert_b: bool = invert_b,
            operation: Any = operation,
        ) -> int:
            left_bit = int(input_bits[index_a])
            right_bit = int(input_bits[index_b])
            if invert_a:
                left_bit = 1 - left_bit
            if invert_b:
                right_bit = 1 - right_bit
            return int(operation(left_bit, right_bit))

        return fn

    def make_ternary(index_a: int, index_b: int, index_c: int, operation: Any) -> Any:
        def fn(
            input_bits: str,
            index_a: int = index_a,
            index_b: int = index_b,
            index_c: int = index_c,
            operation: Any = operation,
        ) -> int:
            return int(operation(int(input_bits[index_a]), int(input_bits[index_b]), int(input_bits[index_c])))

        return fn

    for input_index in range(8):
        candidates.append((f"i{input_index + 1}", (input_index + 1,), make_unary(input_index, False)))
        candidates.append((f"i{input_index + 1}^", (input_index + 1,), make_unary(input_index, True)))

    for first_index in range(8):
        for second_index in range(first_index + 1, 8):
            for op_name, operation in BIT_HYBRID_BOOLEAN2_OPERATIONS.items():
                for invert_first, first_suffix in ((False, ""), (True, "^")):
                    for invert_second, second_suffix in ((False, ""), (True, "^")):
                        name = f"{op_name}(i{first_index + 1}{first_suffix},i{second_index + 1}{second_suffix})"
                        varset = tuple(sorted({first_index + 1, second_index + 1}))
                        candidates.append(
                            (
                                name,
                                varset,
                                make_binary(first_index, invert_first, second_index, invert_second, operation),
                            )
                        )

    for first_index in range(8):
        for second_index in range(first_index + 1, 8):
            for third_index in range(second_index + 1, 8):
                for op_name, operation in BIT_HYBRID_BOOLEAN3_OPERATIONS.items():
                    name = f"{op_name}(i{first_index + 1},i{second_index + 1},i{third_index + 1})"
                    varset = (first_index + 1, second_index + 1, third_index + 1)
                    candidates.append((name, varset, make_ternary(first_index, second_index, third_index, operation)))

    return tuple(candidates)


def infer_bit_hybrid_consensus_answer(
    examples: list[tuple[str, str]], candidate_sets: list[list[tuple[int, int]]], query_bits: str
) -> tuple[str | None, dict[str, Any]]:
    info = {
        "ready": False,
        "missing_position": 0,
        "match_count": 0,
        "prediction_count": 0,
        "varset": "",
        "sample_matches": [],
    }
    if len(query_bits) != 8 or len(examples) < 7:
        return None, info
    missing_positions = [index for index, candidates in enumerate(candidate_sets) if not candidates]
    if len(missing_positions) != 1:
        return None, info
    if any(len(candidates) != 1 for index, candidates in enumerate(candidate_sets) if index not in missing_positions):
        return None, info
    missing_index = missing_positions[0]
    info["missing_position"] = missing_index + 1
    fixed_specs = [candidates[0] if candidates else None for candidates in candidate_sets]

    matching_candidates: list[tuple[str, tuple[int, ...], Any]] = []
    for name, varset, function in build_bit_hybrid_boolean_candidates():
        if all(function(input_bits) == int(output_bits[missing_index]) for input_bits, output_bits in examples):
            matching_candidates.append((name, varset, function))

    info["match_count"] = len(matching_candidates)
    info["sample_matches"] = [name for name, _, _ in matching_candidates[:8]]
    if not matching_candidates:
        return None, info

    varsets = {varset for _, varset, _ in matching_candidates}
    predicted_outputs: set[str] = set()
    for _, _, function in matching_candidates:
        predicted_bits: list[str] = []
        for output_index, spec in enumerate(fixed_specs):
            if output_index == missing_index:
                predicted_bits.append(str(function(query_bits)))
            else:
                input_index, flip = spec
                source_bit = query_bits[input_index]
                predicted_bits.append(invert_bit(source_bit) if flip else source_bit)
        predicted_outputs.add("".join(predicted_bits))

    info["prediction_count"] = len(predicted_outputs)
    if len(varsets) == 1:
        info["varset"] = ",".join(f"i{index}" for index in next(iter(varsets)))

    if len(predicted_outputs) != 1 or len(varsets) != 1 or len(next(iter(varsets))) != 2:
        return None, info

    info["ready"] = True
    return next(iter(predicted_outputs)), info


def analyze_roman_row(v1: Any, parsed: Any, answer: str) -> dict[str, Any]:
    examples = extract_examples(parsed)
    query_value = getattr(parsed, "roman_query_value", None)
    if not parsed.parse_ok or query_value is None:
        return {
            "template_subtype": "roman_standard",
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "roman_parse_fail",
            "family_analysis_json": json_dumps({"example_count": len(examples)}),
            "audit_reasons": "roman_parse_fail",
            "suspect_label": False,
        }
    predicted = int_to_roman(int(query_value))
    example_mismatches = sum(int_to_roman(int(source)).upper() != str(target).upper() for source, target in examples)
    matches_gold = predicted.upper() == str(answer).upper()
    example_ok = example_mismatches == 0
    reasons: list[str] = []
    if not example_ok:
        reasons.append("roman_example_mismatch")
    if not matches_gold:
        reasons.append("roman_answer_mismatch")
    return {
        "template_subtype": "roman_standard",
        "teacher_solver_candidate": "roman_standard" if matches_gold and example_ok else "",
        "auto_solver_predicted_answer": predicted,
        "auto_solver_match": bool(matches_gold),
        "verified_trace_ready": bool(matches_gold and example_ok),
        "example_consistency_ok": bool(example_ok),
        "analysis_notes": "roman_exact" if matches_gold and example_ok else "roman_check_needed",
        "family_analysis_json": json_dumps(
            {
                "example_count": len(examples),
                "query_value": int(query_value),
                "example_mismatches": int(example_mismatches),
            }
        ),
        "audit_reasons": "|".join(reasons),
        "suspect_label": bool(parsed.parse_ok and predicted and not matches_gold),
    }


def analyze_gravity_row(v1: Any, parsed: Any, answer: str) -> dict[str, Any]:
    examples = extract_examples(parsed)
    if not parsed.parse_ok or parsed.query_value_float is None or not examples:
        return {
            "template_subtype": "gravity_half_g_t2",
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "gravity_parse_fail",
            "family_analysis_json": json_dumps({"example_count": len(examples)}),
            "audit_reasons": "gravity_parse_fail",
            "suspect_label": False,
        }
    g_values = []
    output_decimal_places = []
    for source, target in examples:
        t_value = float(source)
        if t_value == 0.0:
            continue
        d_value = float(target)
        g_values.append(2.0 * d_value / (t_value**2))
        output_decimal_places.append(decimal_places(target))
    if not g_values:
        return {
            "template_subtype": "gravity_half_g_t2",
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "gravity_no_g_values",
            "family_analysis_json": json_dumps({"example_count": len(examples)}),
            "audit_reasons": "gravity_no_g_values",
            "suspect_label": False,
        }
    median_g = statistics.median(g_values)
    g_spread = max(g_values) - min(g_values) if len(g_values) > 1 else 0.0
    example_checks = []
    for source, target in examples:
        t_value = float(source)
        decimals = decimal_places(target)
        predicted_target = format_decimal(0.5 * median_g * (t_value**2), decimals)
        example_checks.append(v1.verify(str(target), predicted_target))
    query_prediction = format_decimal(0.5 * median_g * (float(parsed.query_value_float) ** 2), decimal_places(answer))
    matches_gold = v1.verify(str(answer), query_prediction)
    example_ok = all(example_checks)
    consistent = bool(g_spread <= 0.05)
    reasons: list[str] = []
    if not example_ok:
        reasons.append("gravity_example_mismatch")
    if not consistent:
        reasons.append("gravity_g_spread")
    if not matches_gold:
        reasons.append("gravity_answer_mismatch")
    return {
        "template_subtype": "gravity_half_g_t2",
        "teacher_solver_candidate": "gravity_numeric_rule" if matches_gold and example_ok and consistent else "",
        "auto_solver_predicted_answer": query_prediction,
        "auto_solver_match": bool(matches_gold),
        "verified_trace_ready": bool(matches_gold and example_ok and consistent),
        "example_consistency_ok": bool(example_ok and consistent),
        "analysis_notes": "gravity_exact" if matches_gold and example_ok and consistent else "gravity_check_needed",
        "family_analysis_json": json_dumps(
            {
                "example_count": len(examples),
                "median_g": round(median_g, 6),
                "g_spread": round(g_spread, 6),
                "example_decimal_places": sorted(set(output_decimal_places)),
            }
        ),
        "audit_reasons": "|".join(reasons),
        "suspect_label": bool(parsed.parse_ok and query_prediction and not matches_gold),
    }


def analyze_unit_row(v1: Any, parsed: Any, answer: str) -> dict[str, Any]:
    examples = extract_examples(parsed)
    if not parsed.parse_ok or parsed.query_value_float is None or not examples:
        return {
            "template_subtype": "unit_fixed_ratio",
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "unit_parse_fail",
            "family_analysis_json": json_dumps({"example_count": len(examples)}),
            "audit_reasons": "unit_parse_fail",
            "suspect_label": False,
        }
    ratios = []
    for source, target in examples:
        source_value = float(source)
        if source_value == 0.0:
            continue
        ratios.append(float(target) / source_value)
    if not ratios:
        return {
            "template_subtype": "unit_fixed_ratio",
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "unit_no_ratios",
            "family_analysis_json": json_dumps({"example_count": len(examples)}),
            "audit_reasons": "unit_no_ratios",
            "suspect_label": False,
        }
    median_ratio = statistics.median(ratios)
    ratio_spread = max(ratios) - min(ratios) if len(ratios) > 1 else 0.0
    example_checks = []
    for source, target in examples:
        source_value = float(source)
        predicted_target = format_decimal(median_ratio * source_value, decimal_places(target))
        example_checks.append(v1.verify(str(target), predicted_target))
    query_prediction = format_decimal(median_ratio * float(parsed.query_value_float), decimal_places(answer))
    matches_gold = v1.verify(str(answer), query_prediction)
    example_ok = all(example_checks)
    consistent = bool(ratio_spread <= 0.01)
    reasons: list[str] = []
    if not example_ok:
        reasons.append("unit_example_mismatch")
    if not consistent:
        reasons.append("unit_ratio_spread")
    if not matches_gold:
        reasons.append("unit_answer_mismatch")
    return {
        "template_subtype": "unit_fixed_ratio",
        "teacher_solver_candidate": "unit_numeric_rule" if matches_gold and example_ok and consistent else "",
        "auto_solver_predicted_answer": query_prediction,
        "auto_solver_match": bool(matches_gold),
        "verified_trace_ready": bool(matches_gold and example_ok and consistent),
        "example_consistency_ok": bool(example_ok and consistent),
        "analysis_notes": "unit_exact" if matches_gold and example_ok and consistent else "unit_check_needed",
        "family_analysis_json": json_dumps(
            {
                "example_count": len(examples),
                "median_ratio": round(median_ratio, 8),
                "ratio_spread": round(ratio_spread, 8),
            }
        ),
        "audit_reasons": "|".join(reasons),
        "suspect_label": bool(parsed.parse_ok and query_prediction and not matches_gold),
    }


def analyze_bit_row(v1: Any, parsed: Any, answer: str) -> dict[str, Any]:
    examples = extract_examples(parsed)
    query_bits = str(parsed.bit_query_binary or "")
    if not parsed.parse_ok or len(query_bits) != 8 or not examples:
        return {
            "template_subtype": "bit_other",
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "bit_parse_fail",
            "family_analysis_json": json_dumps({"example_count": len(examples)}),
            "audit_reasons": "bit_parse_fail",
            "suspect_label": False,
            "bit_simple_family": str(parsed.subfamily),
            "bit_candidate_signature": "",
            "bit_independent_unique": False,
            "bit_bijection_unique": False,
            "bit_bijection_solution_count": 0,
            "bit_boolean2_unique": False,
            "bit_boolean3_unique": False,
            "bit_affine_unique": False,
            "bit_byte_transform_unique": False,
            "bit_byte_transform_names": "",
            "answer_only_ready": False,
            "bit_hybrid_consensus_ready": False,
            "bit_hybrid_consensus_varset": "",
            "bit_hybrid_consensus_match_count": 0,
            "bit_hybrid_consensus_prediction_count": 0,
            "bit_structured_formula_name": "",
            "bit_structured_formula_prediction": "",
            "bit_structured_formula_names": "",
            "bit_structured_formula_predictions": "",
            "bit_structured_formula_matches_gold": False,
            "bit_structured_formula_match_count": 0,
            "bit_structured_formula_prediction_count": 0,
            "bit_structured_formula_safe_support": 0,
            "bit_structured_formula_safe": False,
        }
    candidate_sets = build_bit_candidate_sets(examples)
    independent_answer, independent_choice_counts = infer_bit_independent_answer(candidate_sets, query_bits)
    bijection_answers, explored = infer_bit_bijection_answers(candidate_sets, query_bits)
    bijection_answer = next(iter(bijection_answers)) if len(bijection_answers) == 1 else ""
    boolean2_answer, boolean2_value_counts, boolean2_support_counts = infer_bit_two_bit_boolean_answer(examples, query_bits)
    boolean3_answer, boolean3_value_counts, boolean3_support_counts = infer_bit_three_bit_boolean_answer(examples, query_bits)
    affine_answer, affine_free_var_counts = infer_bit_affine_xor_answer(examples, query_bits)
    byte_transform_answer, byte_transform_names = infer_bit_byte_transform_answer(examples, query_bits)
    structured_formula_matches = infer_bit_structured_byte_formula_matches(examples, query_bits)
    structured_formula_predictions = sorted({prediction for _, prediction in structured_formula_matches})
    structured_formula_name = structured_formula_matches[0][0] if len(structured_formula_matches) == 1 else ""
    structured_formula_prediction = structured_formula_predictions[0] if len(structured_formula_predictions) == 1 else ""
    structured_formula_names_text = "|".join(name for name, _ in structured_formula_matches)
    structured_formula_predictions_text = "|".join(structured_formula_predictions)
    hybrid_answer, hybrid_info = infer_bit_hybrid_consensus_answer(examples, candidate_sets, query_bits)
    strict_prediction = bijection_answer or (independent_answer or "")
    fallback_prediction = strict_prediction or (boolean2_answer or "") or (boolean3_answer or "") or (hybrid_answer or "") or (affine_answer or "") or (byte_transform_answer or "")
    no_candidate_positions = sum(1 for candidates in candidate_sets if not candidates)
    multi_candidate_positions = sum(1 for candidates in candidate_sets if len(candidates) > 1)
    reasons: list[str] = []
    if any(not candidates for candidates in candidate_sets):
        reasons.append("bit_no_candidate")
    if independent_answer is None:
        reasons.append("bit_independent_ambiguous")
    if len(bijection_answers) != 1:
        reasons.append("bit_bijection_ambiguous")
    if boolean2_answer is None:
        reasons.append("bit_boolean2_ambiguous")
    elif not strict_prediction and boolean2_answer != str(answer):
        reasons.append("bit_boolean2_answer_mismatch")
    if boolean3_answer is None:
        reasons.append("bit_boolean3_ambiguous")
    elif not strict_prediction and not boolean2_answer and boolean3_answer != str(answer):
        reasons.append("bit_boolean3_answer_mismatch")
    if affine_answer is None:
        reasons.append("bit_affine_ambiguous")
    elif not strict_prediction and not boolean2_answer and not boolean3_answer and affine_answer != str(answer):
        reasons.append("bit_affine_answer_mismatch")
    if byte_transform_answer is None:
        reasons.append("bit_byte_transform_ambiguous")
    elif not strict_prediction and not boolean2_answer and not boolean3_answer and not affine_answer and byte_transform_answer != str(answer):
        reasons.append("bit_byte_transform_mismatch")
    if hybrid_answer is None:
        reasons.append("bit_hybrid_consensus_ambiguous")
    elif not strict_prediction and not boolean2_answer and not boolean3_answer and hybrid_answer != str(answer):
        reasons.append("bit_hybrid_consensus_mismatch")
    if strict_prediction and strict_prediction != str(answer):
        reasons.append("bit_answer_mismatch")
    simple_family = str(v1.detect_bit_fit_family(getattr(parsed, "examples", [])))
    template_subtype = "bit_permutation_inversion" if all(candidate_sets) else "bit_other"
    teacher_solver = ""
    if bijection_answer and bijection_answer == str(answer):
        teacher_solver = "binary_bit_permutation_bijection"
    elif independent_answer and independent_answer == str(answer):
        teacher_solver = "binary_bit_permutation_independent"
    elif boolean2_answer and boolean2_answer == str(answer):
        teacher_solver = "binary_two_bit_boolean"
    elif boolean3_answer and boolean3_answer == str(answer):
        teacher_solver = "binary_three_bit_boolean"
    elif affine_answer and affine_answer == str(answer):
        teacher_solver = "binary_affine_xor"
    elif byte_transform_answer and byte_transform_answer == str(answer):
        teacher_solver = "binary_byte_transform"
    verified = bool(teacher_solver)
    answer_only_ready = bool(
        not verified
        and hybrid_answer
        and hybrid_answer == str(answer)
        and hybrid_info.get("ready", False)
    )
    affine_low_gap_mismatch = bool(
        not verified
        and not strict_prediction
        and not boolean2_answer
        and not boolean3_answer
        and affine_answer
        and not byte_transform_answer
        and affine_answer != str(answer)
        and len(examples) >= 7
        and no_candidate_positions <= 1
        and multi_candidate_positions == 0
    )
    if affine_low_gap_mismatch:
        reasons.append("bit_affine_low_gap_mismatch")
    best_prediction = fallback_prediction
    if teacher_solver == "binary_bit_permutation_bijection":
        best_prediction = bijection_answer
    elif teacher_solver == "binary_bit_permutation_independent":
        best_prediction = independent_answer or ""
    elif teacher_solver == "binary_two_bit_boolean":
        best_prediction = boolean2_answer or ""
    elif teacher_solver == "binary_three_bit_boolean":
        best_prediction = boolean3_answer or ""
    elif teacher_solver == "binary_affine_xor":
        best_prediction = affine_answer or ""
    elif teacher_solver == "binary_byte_transform":
        best_prediction = byte_transform_answer or ""
    elif answer_only_ready:
        best_prediction = hybrid_answer or ""
    matches_gold = bool(best_prediction and best_prediction == str(answer))
    return {
        "template_subtype": template_subtype,
        "teacher_solver_candidate": teacher_solver,
        "auto_solver_predicted_answer": best_prediction,
        "auto_solver_match": bool(matches_gold),
        "verified_trace_ready": verified,
        "example_consistency_ok": bool(all(candidate_sets)),
        "analysis_notes": (
            "bit_exact"
            if verified
            else ("bit_hybrid_consensus" if answer_only_ready else ("bit_affine_low_gap_mismatch" if affine_low_gap_mismatch else "bit_audit_needed"))
        ),
        "family_analysis_json": json_dumps(
            {
                "example_count": len(examples),
                "simple_family": simple_family,
                "independent_choice_counts": independent_choice_counts,
                "bijection_answer_count": len(bijection_answers),
                "bijection_search_explored": explored,
                "boolean2_value_counts": boolean2_value_counts,
                "boolean2_support_counts": boolean2_support_counts,
                "boolean3_value_counts": boolean3_value_counts,
                "boolean3_support_counts": boolean3_support_counts,
                "affine_free_var_counts": affine_free_var_counts,
                "byte_transform_names": byte_transform_names,
                "no_candidate_positions": no_candidate_positions,
                "multi_candidate_positions": multi_candidate_positions,
                "hybrid_consensus_missing_position": hybrid_info["missing_position"],
                "hybrid_consensus_match_count": hybrid_info["match_count"],
                "hybrid_consensus_prediction_count": hybrid_info["prediction_count"],
                "hybrid_consensus_varset": hybrid_info["varset"],
                "hybrid_consensus_sample_matches": hybrid_info["sample_matches"],
                "structured_formula_name": structured_formula_name,
                "structured_formula_match_count": len(structured_formula_matches),
                "structured_formula_prediction_count": len(structured_formula_predictions),
                "structured_formula_prediction": structured_formula_prediction,
                "structured_formula_sample_matches": [name for name, _ in structured_formula_matches[:8]],
                "affine_low_gap_mismatch": affine_low_gap_mismatch,
            }
        ),
        "audit_reasons": "|".join(reasons),
        "suspect_label": bool((strict_prediction and strict_prediction != str(answer)) or affine_low_gap_mismatch),
        "answer_only_ready": answer_only_ready,
        "bit_simple_family": simple_family,
        "bit_candidate_signature": bit_candidate_signature(candidate_sets),
        "bit_independent_unique": bool(independent_answer is not None),
        "bit_bijection_unique": bool(len(bijection_answers) == 1),
        "bit_bijection_solution_count": int(len(bijection_answers)),
        "bit_boolean2_unique": bool(boolean2_answer is not None),
        "bit_boolean3_unique": bool(boolean3_answer is not None),
        "bit_affine_unique": bool(affine_answer is not None),
        "bit_byte_transform_unique": bool(byte_transform_answer is not None),
        "bit_no_candidate_positions": int(no_candidate_positions),
        "bit_multi_candidate_positions": int(multi_candidate_positions),
        "bit_byte_transform_names": "|".join(byte_transform_names),
        "bit_hybrid_consensus_ready": bool(hybrid_info["ready"]),
        "bit_hybrid_consensus_varset": str(hybrid_info["varset"]),
        "bit_hybrid_consensus_match_count": int(hybrid_info["match_count"]),
        "bit_hybrid_consensus_prediction_count": int(hybrid_info["prediction_count"]),
        "bit_structured_formula_name": structured_formula_name,
        "bit_structured_formula_prediction": structured_formula_prediction,
        "bit_structured_formula_names": structured_formula_names_text,
        "bit_structured_formula_predictions": structured_formula_predictions_text,
        "bit_structured_formula_matches_gold": bool(structured_formula_prediction and structured_formula_prediction == str(answer)),
        "bit_structured_formula_match_count": int(len(structured_formula_matches)),
        "bit_structured_formula_prediction_count": int(len(structured_formula_predictions)),
        "bit_structured_formula_safe_support": 0,
        "bit_structured_formula_safe": False,
    }


def analyze_text_row(parsed: Any, answer: str) -> dict[str, Any]:
    examples = extract_examples(parsed)
    query_text = str(parsed.query_raw or "")
    if not parsed.parse_ok or not query_text or not examples:
        return {
            "template_subtype": "text_other",
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "text_parse_fail",
            "family_analysis_json": json_dumps({"example_count": len(examples)}),
            "audit_reasons": "text_parse_fail",
            "suspect_label": False,
            "text_wordmap_predicted_answer": "",
            "text_unknown_char_count": 0,
            "text_unknown_chars": "",
            "answer_only_ready": False,
            "text_answer_completion_new_pair_count": 0,
            "text_answer_completion_pairs": "",
        }
    char_analysis = analyze_char_mapping(examples, query_text, answer, allow_spaces=True)
    word_analysis = analyze_word_dictionary(query_text, answer, examples)
    completion_analysis = analyze_text_answer_completion(examples, query_text, answer)
    predicted_answer = ""
    teacher_solver = ""
    answer_only_ready = False
    if char_analysis["charmap_matches_gold"]:
        predicted_answer = char_analysis["charmap_predicted_answer"]
        teacher_solver = "text_char_substitution"
    elif word_analysis["wordmap_matches_gold"]:
        predicted_answer = word_analysis["wordmap_predicted_answer"]
        teacher_solver = "text_word_dictionary"
    elif completion_analysis["text_answer_completion_ready"] and char_analysis["charmap_query_unknown_count"] >= 1:
        predicted_answer = str(answer)
        answer_only_ready = True
    reasons: list[str] = []
    if char_analysis["charmap_length_mismatch"]:
        reasons.append("text_length_mismatch")
    if char_analysis["charmap_forward_conflicts"] or char_analysis["charmap_reverse_conflicts"] or char_analysis["charmap_space_conflicts"]:
        reasons.append("text_mapping_conflict")
    if not char_analysis["charmap_full_query_covered"]:
        reasons.append("text_query_unknown_chars")
    if answer_only_ready:
        reasons.append("text_answer_completion_ready")
    elif not teacher_solver:
        reasons.append("text_solver_unverified")
    if char_analysis["charmap_predicted_answer"] and not char_analysis["charmap_matches_gold"]:
        reasons.append("text_answer_mismatch")
    verified = bool(teacher_solver)
    example_ok = not (
        char_analysis["charmap_length_mismatch"]
        or char_analysis["charmap_forward_conflicts"]
        or char_analysis["charmap_reverse_conflicts"]
        or char_analysis["charmap_space_conflicts"]
    )
    return {
        "template_subtype": "text_monoalphabetic" if example_ok else "text_other",
        "teacher_solver_candidate": teacher_solver,
        "auto_solver_predicted_answer": predicted_answer,
        "auto_solver_match": bool(verified or answer_only_ready),
        "verified_trace_ready": verified,
        "example_consistency_ok": bool(example_ok),
        "analysis_notes": "text_exact" if verified else ("text_answer_completion" if answer_only_ready else "text_audit_needed"),
        "family_analysis_json": json_dumps(
            {
                "example_count": len(examples),
                **char_analysis,
                **word_analysis,
                **completion_analysis,
            }
        ),
        "audit_reasons": "|".join(reasons),
        "suspect_label": bool(char_analysis["charmap_full_query_covered"] and not char_analysis["charmap_matches_gold"]),
        "text_wordmap_predicted_answer": word_analysis["wordmap_predicted_answer"],
        "text_unknown_char_count": int(char_analysis["charmap_query_unknown_count"]),
        "text_unknown_chars": str(char_analysis["charmap_query_unknown_chars"]),
        "answer_only_ready": bool(answer_only_ready),
        "text_answer_completion_new_pair_count": int(completion_analysis["text_answer_completion_new_pair_count"]),
        "text_answer_completion_pairs": str(completion_analysis["text_answer_completion_pairs"]),
    }


def analyze_symbol_row(prompt: str, parsed: Any, answer: str) -> dict[str, Any]:
    examples = extract_examples(parsed)
    query_text = str(parsed.query_raw or "")
    subtype = classify_symbol_subtype(query_text, examples)
    if not parsed.parse_ok or not query_text or not examples:
        return {
            "template_subtype": subtype,
            "teacher_solver_candidate": "",
            "auto_solver_predicted_answer": "",
            "auto_solver_match": False,
            "verified_trace_ready": False,
            "example_consistency_ok": False,
            "analysis_notes": "symbol_parse_fail",
            "family_analysis_json": json_dumps({"example_count": len(examples), "subtype": subtype}),
            "audit_reasons": "symbol_parse_fail",
            "suspect_label": False,
            "answer_only_ready": False,
            "symbol_query_operator": "",
            "symbol_same_operator_example_count": 0,
            "symbol_numeric_formula_name": "",
            "symbol_numeric_candidate_prediction_count": 0,
            "glyph_multiset_possible": False,
            "glyph_order_acyclic": False,
        }
    if subtype == "numeric_2x2":
        numeric_solver = solve_symbol_numeric_operator_formula(prompt, query_text, answer)
        verified = bool(numeric_solver["solver_name"] and not numeric_solver["low_shot"] and numeric_solver["same_operator_example_count"] >= 2)
        answer_only_ready = bool(numeric_solver["solver_name"] and numeric_solver["low_shot"])
        suspect_label = bool(
            numeric_solver["candidate_prediction_count"] == 1
            and numeric_solver["predicted_answer"]
            and not numeric_solver["matches_gold"]
            and numeric_solver["same_operator_example_count"] >= 2
        )
        reasons: list[str] = []
        if not numeric_solver["solver_name"]:
            reasons.append("symbol_numeric_formula_unverified")
        if numeric_solver["candidate_prediction_count"] > 1:
            reasons.append("symbol_numeric_formula_ambiguous")
        if not numeric_solver["same_operator_example_count"]:
            reasons.append("symbol_numeric_no_same_operator_examples")
        if suspect_label:
            reasons.append("symbol_numeric_formula_mismatch")
        analysis_payload = {
            "example_count": len(examples),
            "subtype": subtype,
            "same_operator_example_count": numeric_solver["same_operator_example_count"],
            "candidate_prediction_count": numeric_solver["candidate_prediction_count"],
            "formula_name": numeric_solver["formula_name"],
            "format_name": numeric_solver["format_name"],
            "query_operator": numeric_solver["query_operator"],
            "low_shot": numeric_solver["low_shot"],
        }
        return {
            "template_subtype": subtype,
            "teacher_solver_candidate": numeric_solver["solver_name"] if numeric_solver["matches_gold"] else "",
            "auto_solver_predicted_answer": numeric_solver["predicted_answer"],
            "auto_solver_match": bool(numeric_solver["matches_gold"]),
            "verified_trace_ready": verified,
            "example_consistency_ok": bool(numeric_solver["same_operator_example_count"] >= 1),
            "analysis_notes": "symbol_numeric_formula_exact" if verified else ("symbol_numeric_formula_low_shot" if answer_only_ready else "symbol_audit_needed"),
            "family_analysis_json": json_dumps(analysis_payload),
            "audit_reasons": "|".join(reasons),
            "suspect_label": suspect_label,
            "answer_only_ready": answer_only_ready,
            "symbol_query_operator": str(numeric_solver["query_operator"]),
            "symbol_same_operator_example_count": int(numeric_solver["same_operator_example_count"]),
            "symbol_numeric_formula_name": str(numeric_solver["formula_name"]),
            "symbol_numeric_candidate_prediction_count": int(numeric_solver["candidate_prediction_count"]),
            "glyph_multiset_possible": False,
            "glyph_order_acyclic": False,
        }
    same_len_pairs = all(len(source) == len(target) for source, target in examples)
    glyph_multiset_possible = bool(subtype == "glyph_len5" and glyph_multiset_mapping_exists(examples))
    glyph_order_acyclic = bool(subtype == "glyph_len5" and glyph_output_order_acyclic(examples))
    char_analysis = analyze_char_mapping(examples, query_text, answer, allow_spaces=False) if same_len_pairs else {
        "charmap_length_mismatch": 1,
        "charmap_forward_conflicts": 0,
        "charmap_reverse_conflicts": 0,
        "charmap_space_conflicts": 0,
        "charmap_query_unknown_chars": "",
        "charmap_query_unknown_count": 0,
        "charmap_unique_source_chars": 0,
        "charmap_unique_target_chars": 0,
        "charmap_full_query_covered": False,
        "charmap_predicted_answer": "",
        "charmap_matches_gold": False,
    }
    predicted_answer = char_analysis["charmap_predicted_answer"] if char_analysis["charmap_matches_gold"] else ""
    verified = bool(predicted_answer)
    reasons: list[str] = []
    if not same_len_pairs:
        reasons.append("symbol_length_mismatch")
    if char_analysis["charmap_forward_conflicts"] or char_analysis["charmap_reverse_conflicts"]:
        reasons.append("symbol_mapping_conflict")
    if not verified:
        reasons.append("symbol_solver_unverified")
    if char_analysis["charmap_predicted_answer"] and not char_analysis["charmap_matches_gold"]:
        reasons.append("symbol_answer_mismatch")
    return {
        "template_subtype": subtype,
        "teacher_solver_candidate": "symbol_char_substitution" if verified else "",
        "auto_solver_predicted_answer": predicted_answer,
        "auto_solver_match": bool(verified),
        "verified_trace_ready": verified,
        "example_consistency_ok": bool(same_len_pairs and not char_analysis["charmap_forward_conflicts"] and not char_analysis["charmap_reverse_conflicts"]),
        "analysis_notes": "symbol_exact" if verified else "symbol_audit_needed",
        "family_analysis_json": json_dumps(
            {
                "example_count": len(examples),
                "subtype": subtype,
                "same_len_pairs": bool(same_len_pairs),
                "glyph_multiset_possible": glyph_multiset_possible,
                "glyph_order_acyclic": glyph_order_acyclic,
                **char_analysis,
            }
        ),
        "audit_reasons": "|".join(reasons),
        "suspect_label": bool(char_analysis["charmap_full_query_covered"] and not char_analysis["charmap_matches_gold"]),
        "answer_only_ready": False,
        "symbol_query_operator": "",
        "symbol_same_operator_example_count": 0,
        "symbol_numeric_formula_name": "",
        "symbol_numeric_candidate_prediction_count": 0,
        "glyph_multiset_possible": glyph_multiset_possible,
        "glyph_order_acyclic": glyph_order_acyclic,
    }


def analyze_row(v1: Any, metadata_record: dict[str, Any]) -> dict[str, Any]:
    prompt = str(metadata_record["prompt"])
    answer = str(metadata_record["answer"])
    parsed = v1.parse_prompt(prompt, answer)
    family = str(metadata_record["family"])
    if family == "roman_numeral":
        family_result = analyze_roman_row(v1, parsed, answer)
    elif family == "gravity_constant":
        family_result = analyze_gravity_row(v1, parsed, answer)
    elif family == "unit_conversion":
        family_result = analyze_unit_row(v1, parsed, answer)
    elif family == "bit_manipulation":
        family_result = analyze_bit_row(v1, parsed, answer)
    elif family == "text_decryption":
        family_result = analyze_text_row(parsed, answer)
    else:
        family_result = analyze_symbol_row(prompt, parsed, answer)

    audit_reasons = [reason for reason in str(family_result.get("audit_reasons", "")).split("|") if reason]
    suspect_label = bool(family_result.get("suspect_label", False))
    if family_result.get("verified_trace_ready", False):
        selection_tier = "verified_trace_ready"
    elif family_result.get("answer_only_ready", False):
        selection_tier = "answer_only_keep"
    elif suspect_label:
        selection_tier = "exclude_suspect"
    elif family in {"symbol_equation", "text_decryption", "bit_manipulation"}:
        selection_tier = "manual_audit_priority"
    elif bool(metadata_record.get("parse_ok", False)):
        selection_tier = "answer_only_keep"
    else:
        selection_tier = "manual_audit_priority"

    if family in {"gravity_constant", "unit_conversion", "roman_numeral"} and bool(metadata_record.get("parse_ok", False)) and not suspect_label:
        if not family_result.get("verified_trace_ready", False):
            selection_tier = "manual_audit_priority"
    elif family_result.get("verified_trace_ready", False):
        selection_tier = "verified_trace_ready"

    audit_priority_score = score_reasons(float(metadata_record.get("hard_score", 0.0)), audit_reasons, selection_tier)
    return {
        **metadata_record,
        "template_main": family,
        "template_main_label": FAMILY_LABELS.get(family, family),
        "template_subtype": family_result["template_subtype"],
        "teacher_solver_candidate": family_result["teacher_solver_candidate"],
        "auto_solver_predicted_answer": family_result["auto_solver_predicted_answer"],
        "auto_solver_match": bool(family_result["auto_solver_match"]),
        "verified_trace_ready": bool(family_result["verified_trace_ready"]),
        "example_consistency_ok": bool(family_result["example_consistency_ok"]),
        "selection_tier": selection_tier,
        "audit_priority_score": audit_priority_score,
        "audit_reasons": "|".join(audit_reasons),
        "analysis_notes": family_result["analysis_notes"],
        "family_analysis_json": family_result["family_analysis_json"],
        "suspect_label": suspect_label,
        "bit_simple_family": family_result.get("bit_simple_family", ""),
        "bit_candidate_signature": family_result.get("bit_candidate_signature", ""),
        "bit_independent_unique": bool(family_result.get("bit_independent_unique", False)),
        "bit_bijection_unique": bool(family_result.get("bit_bijection_unique", False)),
        "bit_bijection_solution_count": int(family_result.get("bit_bijection_solution_count", 0)),
        "bit_boolean2_unique": bool(family_result.get("bit_boolean2_unique", False)),
        "bit_boolean3_unique": bool(family_result.get("bit_boolean3_unique", False)),
        "bit_affine_unique": bool(family_result.get("bit_affine_unique", False)),
        "bit_byte_transform_unique": bool(family_result.get("bit_byte_transform_unique", False)),
        "bit_no_candidate_positions": int(family_result.get("bit_no_candidate_positions", 0)),
        "bit_multi_candidate_positions": int(family_result.get("bit_multi_candidate_positions", 0)),
        "bit_byte_transform_names": family_result.get("bit_byte_transform_names", ""),
        "bit_hybrid_consensus_ready": bool(family_result.get("bit_hybrid_consensus_ready", False)),
        "bit_hybrid_consensus_varset": family_result.get("bit_hybrid_consensus_varset", ""),
        "bit_hybrid_consensus_match_count": int(family_result.get("bit_hybrid_consensus_match_count", 0)),
        "bit_hybrid_consensus_prediction_count": int(family_result.get("bit_hybrid_consensus_prediction_count", 0)),
        "bit_structured_formula_name": family_result.get("bit_structured_formula_name", ""),
        "bit_structured_formula_prediction": family_result.get("bit_structured_formula_prediction", ""),
        "bit_structured_formula_names": family_result.get("bit_structured_formula_names", ""),
        "bit_structured_formula_predictions": family_result.get("bit_structured_formula_predictions", ""),
        "bit_structured_formula_matches_gold": bool(family_result.get("bit_structured_formula_matches_gold", False)),
        "bit_structured_formula_match_count": int(family_result.get("bit_structured_formula_match_count", 0)),
        "bit_structured_formula_prediction_count": int(family_result.get("bit_structured_formula_prediction_count", 0)),
        "bit_structured_formula_safe_support": int(family_result.get("bit_structured_formula_safe_support", 0)),
        "bit_structured_formula_safe": bool(family_result.get("bit_structured_formula_safe", False)),
        "text_wordmap_predicted_answer": family_result.get("text_wordmap_predicted_answer", ""),
        "text_unknown_char_count": int(family_result.get("text_unknown_char_count", 0)),
        "text_unknown_chars": family_result.get("text_unknown_chars", ""),
        "text_answer_completion_new_pair_count": int(family_result.get("text_answer_completion_new_pair_count", 0)),
        "text_answer_completion_pairs": family_result.get("text_answer_completion_pairs", ""),
        "symbol_query_operator": family_result.get("symbol_query_operator", ""),
        "symbol_same_operator_example_count": int(family_result.get("symbol_same_operator_example_count", 0)),
        "symbol_numeric_formula_name": family_result.get("symbol_numeric_formula_name", ""),
        "symbol_numeric_candidate_prediction_count": int(family_result.get("symbol_numeric_candidate_prediction_count", 0)),
        "glyph_multiset_possible": bool(family_result.get("glyph_multiset_possible", False)),
        "glyph_order_acyclic": bool(family_result.get("glyph_order_acyclic", False)),
    }


def grouped_counts(frame: pd.DataFrame, group_columns: list[str], name: str = "rows") -> pd.DataFrame:
    return (
        frame.groupby(group_columns, dropna=False)
        .size()
        .rename(name)
        .reset_index()
        .sort_values([name] + group_columns, ascending=[False] + [True] * len(group_columns))
        .reset_index(drop=True)
    )


def apply_bit_structured_formula_promotions(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analysis_df = analysis_df.copy()
    bit_mask = analysis_df["family"] == "bit_manipulation"
    unique_formula_mask = (
        bit_mask
        & (analysis_df["bit_structured_formula_match_count"] == 1)
        & (analysis_df["bit_structured_formula_name"].astype(str) != "")
    )
    unique_formula_df = analysis_df.loc[unique_formula_mask].copy()
    support_df = pd.DataFrame(
        columns=[
            "bit_structured_formula_name",
            "support_rows",
            "gold_match_rows",
            "error_rows",
            "safe_formula",
        ]
    )
    abstract_support_df = pd.DataFrame(
        columns=[
            "bit_structured_formula_abstract_family",
            "support_rows",
            "gold_match_rows",
            "error_rows",
            "distinct_exact_formula_count",
            "safe_abstract_family",
        ]
    )
    safe_formula_names: set[str] = set()
    safe_abstract_family_names: set[str] = set()
    if not unique_formula_df.empty:
        support_df = (
            unique_formula_df.groupby("bit_structured_formula_name", dropna=False)
            .agg(
                support_rows=("id", "size"),
                gold_match_rows=("bit_structured_formula_matches_gold", "sum"),
            )
            .reset_index()
        )
        support_df["support_rows"] = support_df["support_rows"].astype(int)
        support_df["gold_match_rows"] = support_df["gold_match_rows"].astype(int)
        support_df["error_rows"] = support_df["support_rows"] - support_df["gold_match_rows"]
        support_df["safe_formula"] = (support_df["support_rows"] >= 2) & (support_df["error_rows"] == 0)
        safe_formula_names = set(support_df.loc[support_df["safe_formula"], "bit_structured_formula_name"].astype(str))

        unique_formula_df["bit_structured_formula_abstract_family"] = unique_formula_df["bit_structured_formula_name"].map(
            abstract_bit_structured_formula_name
        )
        abstract_support_df = (
            unique_formula_df.groupby("bit_structured_formula_abstract_family", dropna=False)
            .agg(
                support_rows=("id", "size"),
                gold_match_rows=("bit_structured_formula_matches_gold", "sum"),
                distinct_exact_formula_count=("bit_structured_formula_name", "nunique"),
            )
            .reset_index()
        )
        abstract_support_df["support_rows"] = abstract_support_df["support_rows"].astype(int)
        abstract_support_df["gold_match_rows"] = abstract_support_df["gold_match_rows"].astype(int)
        abstract_support_df["distinct_exact_formula_count"] = abstract_support_df["distinct_exact_formula_count"].astype(int)
        abstract_support_df["error_rows"] = abstract_support_df["support_rows"] - abstract_support_df["gold_match_rows"]
        abstract_support_df["safe_abstract_family"] = (
            (abstract_support_df["support_rows"] >= BIT_STRUCTURED_ABSTRACT_MIN_SUPPORT)
            & (abstract_support_df["error_rows"] == 0)
            & (abstract_support_df["distinct_exact_formula_count"] >= BIT_STRUCTURED_ABSTRACT_MIN_DISTINCT)
        )
        safe_abstract_family_names = set(
            abstract_support_df.loc[abstract_support_df["safe_abstract_family"], "bit_structured_formula_abstract_family"].astype(str)
        )

    safe_support_map = {
        str(row["bit_structured_formula_name"]): int(row["support_rows"])
        for row in support_df.to_dict(orient="records")
    }
    analysis_df["bit_structured_formula_safe_support"] = (
        analysis_df["bit_structured_formula_name"].map(safe_support_map).fillna(0).astype(int)
    )
    analysis_df["bit_structured_formula_safe"] = analysis_df["bit_structured_formula_name"].astype(str).isin(safe_formula_names)
    analysis_df["bit_structured_formula_abstract_family"] = analysis_df["bit_structured_formula_name"].map(
        abstract_bit_structured_formula_name
    )
    abstract_support_map = {
        str(row["bit_structured_formula_abstract_family"]): int(row["support_rows"])
        for row in abstract_support_df.to_dict(orient="records")
    }
    abstract_error_map = {
        str(row["bit_structured_formula_abstract_family"]): int(row["error_rows"])
        for row in abstract_support_df.to_dict(orient="records")
    }
    abstract_distinct_map = {
        str(row["bit_structured_formula_abstract_family"]): int(row["distinct_exact_formula_count"])
        for row in abstract_support_df.to_dict(orient="records")
    }
    analysis_df["bit_structured_formula_abstract_support"] = (
        analysis_df["bit_structured_formula_abstract_family"].map(abstract_support_map).fillna(0).astype(int)
    )
    analysis_df["bit_structured_formula_abstract_error_rows"] = (
        analysis_df["bit_structured_formula_abstract_family"].map(abstract_error_map).fillna(0).astype(int)
    )
    analysis_df["bit_structured_formula_abstract_distinct_exact"] = (
        analysis_df["bit_structured_formula_abstract_family"].map(abstract_distinct_map).fillna(0).astype(int)
    )
    analysis_df["bit_structured_formula_abstract_safe"] = analysis_df["bit_structured_formula_abstract_family"].astype(str).isin(
        safe_abstract_family_names
    )

    def has_safe_multi_formula_abstract(names_text: Any) -> bool:
        return any(
            abstract_bit_structured_formula_name(name) in safe_abstract_family_names
            for name in split_pipe_text(names_text)
        )

    promote_mask = (
        bit_mask
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & analysis_df["bit_structured_formula_safe"]
        & analysis_df["bit_structured_formula_matches_gold"]
        & (analysis_df["bit_structured_formula_match_count"] == 1)
    )
    analysis_df.loc[promote_mask, "template_subtype"] = "bit_structured_byte_formula"
    analysis_df.loc[promote_mask, "teacher_solver_candidate"] = "binary_structured_byte_formula"
    analysis_df.loc[promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[promote_mask, "bit_structured_formula_prediction"]
    analysis_df.loc[promote_mask, "auto_solver_match"] = True
    analysis_df.loc[promote_mask, "verified_trace_ready"] = True
    analysis_df.loc[promote_mask, "example_consistency_ok"] = True
    analysis_df.loc[promote_mask, "selection_tier"] = "verified_trace_ready"
    analysis_df.loc[promote_mask, "audit_priority_score"] = 0.0
    analysis_df.loc[promote_mask, "audit_reasons"] = ""
    analysis_df.loc[promote_mask, "analysis_notes"] = "bit_structured_byte_exact"
    analysis_df.loc[promote_mask, "suspect_label"] = False

    abstract_promote_mask = (
        bit_mask
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & (analysis_df["bit_structured_formula_match_count"] == 1)
        & (analysis_df["bit_structured_formula_safe_support"] == 1)
        & analysis_df["bit_structured_formula_matches_gold"]
        & analysis_df["bit_structured_formula_abstract_safe"]
    )
    analysis_df.loc[abstract_promote_mask, "template_subtype"] = "bit_structured_byte_formula"
    analysis_df.loc[abstract_promote_mask, "teacher_solver_candidate"] = "binary_structured_byte_formula_abstract"
    analysis_df.loc[abstract_promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[
        abstract_promote_mask, "bit_structured_formula_prediction"
    ]
    analysis_df.loc[abstract_promote_mask, "auto_solver_match"] = True
    analysis_df.loc[abstract_promote_mask, "verified_trace_ready"] = True
    analysis_df.loc[abstract_promote_mask, "example_consistency_ok"] = True
    analysis_df.loc[abstract_promote_mask, "selection_tier"] = "verified_trace_ready"
    analysis_df.loc[abstract_promote_mask, "audit_priority_score"] = 0.0
    analysis_df.loc[abstract_promote_mask, "audit_reasons"] = ""
    analysis_df.loc[abstract_promote_mask, "analysis_notes"] = "bit_structured_byte_abstract_exact"
    analysis_df.loc[abstract_promote_mask, "suspect_label"] = False

    multi_answer_only_mask = (
        bit_mask
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & (analysis_df["bit_structured_formula_match_count"] > 1)
        & (analysis_df["bit_structured_formula_prediction_count"] == 1)
        & analysis_df["bit_structured_formula_matches_gold"]
        & analysis_df["bit_structured_formula_names"].map(has_safe_multi_formula_abstract)
    )
    analysis_df.loc[multi_answer_only_mask, "template_subtype"] = "bit_structured_byte_formula"
    analysis_df.loc[multi_answer_only_mask, "auto_solver_predicted_answer"] = analysis_df.loc[
        multi_answer_only_mask, "bit_structured_formula_prediction"
    ]
    analysis_df.loc[multi_answer_only_mask, "auto_solver_match"] = True
    analysis_df.loc[multi_answer_only_mask, "answer_only_ready"] = True
    analysis_df.loc[multi_answer_only_mask, "example_consistency_ok"] = True
    analysis_df.loc[multi_answer_only_mask, "selection_tier"] = "answer_only_keep"
    analysis_df.loc[multi_answer_only_mask, "audit_priority_score"] = 0.0
    analysis_df.loc[multi_answer_only_mask, "audit_reasons"] = ""
    analysis_df.loc[multi_answer_only_mask, "analysis_notes"] = "bit_structured_byte_multi_consensus"
    analysis_df.loc[multi_answer_only_mask, "suspect_label"] = False

    candidate_df = (
        analysis_df.loc[bit_mask & (analysis_df["bit_structured_formula_match_count"] > 0)]
        .sort_values(
            [
                "selection_tier",
                "bit_structured_formula_abstract_support",
                "bit_structured_formula_safe_support",
                "bit_structured_formula_match_count",
                "id",
            ],
            ascending=[True, False, False, True, True],
        )
        .reset_index(drop=True)
    )
    support_df = support_df.sort_values(
        ["safe_formula", "support_rows", "gold_match_rows", "bit_structured_formula_name"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    abstract_support_df = abstract_support_df.sort_values(
        ["safe_abstract_family", "support_rows", "distinct_exact_formula_count", "gold_match_rows", "bit_structured_formula_abstract_family"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    analysis_df = (
        analysis_df.sort_values(["family", "selection_tier", "audit_priority_score", "id"], ascending=[True, True, False, True])
        .reset_index(drop=True)
    )
    return analysis_df, support_df, abstract_support_df, candidate_df


def apply_symbol_operator_consensus_promotions(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analysis_df = analysis_df.copy()
    numeric_mask = (
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["template_subtype"] == "numeric_2x2")
    )
    support_df = pd.DataFrame(
        columns=[
            "query_operator",
            "formula_name",
            "format_name",
            "support_rows",
            "gold_match_rows",
            "error_rows",
            "safe_operator_spec",
        ]
    )
    candidate_df = pd.DataFrame(
        columns=[
            "id",
            "selection_tier",
            "query_operator",
            "same_operator_example_count",
            "answer",
            "query_raw",
            "safe_prediction",
            "safe_prediction_count",
            "safe_spec_count",
            "safe_support_max",
            "safe_specs",
            "all_predictions",
        ]
    )
    if not numeric_mask.any():
        return analysis_df, support_df, candidate_df

    match_records: list[dict[str, Any]] = []
    row_match_map: dict[str, dict[str, Any]] = {}
    for row in analysis_df.loc[numeric_mask, ["id", "prompt", "query_raw", "answer", "selection_tier"]].to_dict(orient="records"):
        match_info = collect_symbol_numeric_operator_formula_matches(
            str(row["prompt"]),
            str(row["query_raw"]),
            str(row["answer"]),
        )
        if int(match_info["same_operator_example_count"]) <= 0:
            continue
        row_match_map[str(row["id"])] = {
            "selection_tier": str(row["selection_tier"]),
            "answer": str(row["answer"]),
            "query_raw": str(row["query_raw"]),
            "query_operator": str(match_info["query_operator"]),
            "same_operator_example_count": int(match_info["same_operator_example_count"]),
            "winning_specs": [(str(formula_name), str(format_name), str(predicted_answer)) for formula_name, format_name, predicted_answer in match_info["winning_specs"]],
        }
        for formula_name, format_name, predicted_answer in match_info["winning_specs"]:
            match_records.append(
                {
                    "id": str(row["id"]),
                    "query_operator": str(match_info["query_operator"]),
                    "formula_name": str(formula_name),
                    "format_name": str(format_name),
                    "predicted_answer": str(predicted_answer),
                    "matches_gold": bool(str(predicted_answer) == str(row["answer"])),
                    "same_operator_example_count": int(match_info["same_operator_example_count"]),
                }
            )
    if not match_records:
        return analysis_df, support_df, candidate_df

    match_df = pd.DataFrame(match_records)
    support_df = (
        match_df.groupby(["query_operator", "formula_name", "format_name"], dropna=False)
        .agg(
            support_rows=("id", "size"),
            gold_match_rows=("matches_gold", "sum"),
        )
        .reset_index()
    )
    support_df["support_rows"] = support_df["support_rows"].astype(int)
    support_df["gold_match_rows"] = support_df["gold_match_rows"].astype(int)
    support_df["error_rows"] = support_df["support_rows"] - support_df["gold_match_rows"]
    support_df["safe_operator_spec"] = (support_df["support_rows"] >= 2) & (support_df["error_rows"] == 0)
    safe_spec_keys = {
        (str(row["query_operator"]), str(row["formula_name"]), str(row["format_name"]))
        for row in support_df.loc[support_df["safe_operator_spec"]].to_dict(orient="records")
    }
    support_map = {
        (str(row["query_operator"]), str(row["formula_name"]), str(row["format_name"])): int(row["support_rows"])
        for row in support_df.to_dict(orient="records")
    }

    candidate_rows: list[dict[str, Any]] = []
    promote_predictions: dict[str, str] = {}
    for row_id, info in row_match_map.items():
        safe_matches = [
            (formula_name, format_name, predicted_answer)
            for formula_name, format_name, predicted_answer in info["winning_specs"]
            if (info["query_operator"], formula_name, format_name) in safe_spec_keys
        ]
        if not safe_matches:
            continue
        safe_prediction_set = sorted({predicted_answer for _, _, predicted_answer in safe_matches})
        safe_support_max = max(
            support_map[(info["query_operator"], formula_name, format_name)]
            for formula_name, format_name, _ in safe_matches
        )
        candidate_rows.append(
            {
                "id": row_id,
                "selection_tier": info["selection_tier"],
                "query_operator": info["query_operator"],
                "same_operator_example_count": info["same_operator_example_count"],
                "answer": info["answer"],
                "query_raw": info["query_raw"],
                "safe_prediction": safe_prediction_set[0] if len(safe_prediction_set) == 1 else "",
                "safe_prediction_count": len(safe_prediction_set),
                "safe_spec_count": len(safe_matches),
                "safe_support_max": int(safe_support_max),
                "safe_specs": "|".join(
                    sorted(f"{info['query_operator']}::{formula_name}::{format_name}" for formula_name, format_name, _ in safe_matches)
                ),
                "all_predictions": "|".join(sorted({predicted_answer for _, _, predicted_answer in info["winning_specs"]})),
            }
        )
        if (
            info["selection_tier"] == "manual_audit_priority"
            and len(safe_prediction_set) == 1
            and safe_prediction_set[0] == info["answer"]
        ):
            promote_predictions[row_id] = safe_prediction_set[0]

    candidate_df = pd.DataFrame(candidate_rows, columns=list(candidate_df.columns))
    if promote_predictions:
        promote_mask = analysis_df["id"].astype(str).isin(set(promote_predictions))
        analysis_df.loc[promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[promote_mask, "id"].astype(str).map(promote_predictions)
        analysis_df.loc[promote_mask, "auto_solver_match"] = True
        analysis_df.loc[promote_mask, "answer_only_ready"] = True
        analysis_df.loc[promote_mask, "example_consistency_ok"] = True
        analysis_df.loc[promote_mask, "selection_tier"] = "answer_only_keep"
        analysis_df.loc[promote_mask, "audit_priority_score"] = 0.0
        analysis_df.loc[promote_mask, "audit_reasons"] = ""
        analysis_df.loc[promote_mask, "analysis_notes"] = "symbol_operator_spec_consensus"
        analysis_df.loc[promote_mask, "suspect_label"] = False

    support_df = support_df.sort_values(
        ["safe_operator_spec", "support_rows", "gold_match_rows", "query_operator", "formula_name", "format_name"],
        ascending=[False, False, False, True, True, True],
    ).reset_index(drop=True)
    if not candidate_df.empty:
        candidate_df = candidate_df.sort_values(
            ["selection_tier", "safe_support_max", "safe_prediction_count", "same_operator_example_count", "id"],
            ascending=[True, False, True, False, True],
        ).reset_index(drop=True)
    return analysis_df, support_df, candidate_df


def apply_bit_structured_low_support_answer_only_promotions(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    analysis_df = analysis_df.copy()
    candidate_mask = (
        (analysis_df["family"] == "bit_manipulation")
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & (analysis_df["bit_structured_formula_match_count"] == 1)
        & (analysis_df["bit_structured_formula_prediction_count"] == 1)
        & (analysis_df["bit_structured_formula_prediction"] == analysis_df["answer"])
        & (analysis_df["bit_structured_formula_abstract_error_rows"] == 0)
        & (analysis_df["bit_structured_formula_abstract_support"] >= 4)
        & (analysis_df["bit_structured_formula_abstract_distinct_exact"] >= 2)
    )
    candidate_df = analysis_df.loc[
        candidate_mask,
        [
            "id",
            "selection_tier",
            "query_raw",
            "answer",
            "bit_structured_formula_name",
            "bit_structured_formula_prediction",
            "bit_structured_formula_abstract_family",
            "bit_structured_formula_abstract_support",
            "bit_structured_formula_abstract_distinct_exact",
        ],
    ].copy()
    if candidate_df.empty:
        return analysis_df, candidate_df.reset_index(drop=True)

    promote_ids = set(candidate_df["id"].astype(str))
    promote_mask = analysis_df["id"].astype(str).isin(promote_ids)
    analysis_df.loc[promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[promote_mask, "bit_structured_formula_prediction"]
    analysis_df.loc[promote_mask, "auto_solver_match"] = True
    analysis_df.loc[promote_mask, "answer_only_ready"] = True
    analysis_df.loc[promote_mask, "example_consistency_ok"] = True
    analysis_df.loc[promote_mask, "selection_tier"] = "answer_only_keep"
    analysis_df.loc[promote_mask, "audit_priority_score"] = 0.0
    analysis_df.loc[promote_mask, "audit_reasons"] = ""
    analysis_df.loc[promote_mask, "analysis_notes"] = "bit_structured_low_support_answer_only"
    analysis_df.loc[promote_mask, "suspect_label"] = False
    candidate_df = candidate_df.sort_values(
        ["bit_structured_formula_abstract_support", "bit_structured_formula_abstract_distinct_exact", "id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    return analysis_df, candidate_df


def apply_bit_structured_support3_answer_only_promotions(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    analysis_df = analysis_df.copy()
    candidate_mask = (
        (analysis_df["family"] == "bit_manipulation")
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & (analysis_df["bit_structured_formula_match_count"] == 1)
        & (analysis_df["bit_structured_formula_prediction_count"] == 1)
        & (analysis_df["bit_structured_formula_prediction"] == analysis_df["answer"])
        & (analysis_df["bit_structured_formula_abstract_error_rows"] == 0)
        & (analysis_df["bit_structured_formula_abstract_support"] == 3)
        & (analysis_df["bit_structured_formula_abstract_distinct_exact"] == 3)
    )
    candidate_df = analysis_df.loc[
        candidate_mask,
        [
            "id",
            "selection_tier",
            "query_raw",
            "answer",
            "bit_structured_formula_name",
            "bit_structured_formula_prediction",
            "bit_structured_formula_abstract_family",
            "bit_structured_formula_abstract_support",
            "bit_structured_formula_abstract_distinct_exact",
        ],
    ].copy()
    if candidate_df.empty:
        return analysis_df, candidate_df.reset_index(drop=True)

    promote_ids = set(candidate_df["id"].astype(str))
    promote_mask = analysis_df["id"].astype(str).isin(promote_ids)
    analysis_df.loc[promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[promote_mask, "bit_structured_formula_prediction"]
    analysis_df.loc[promote_mask, "auto_solver_match"] = True
    analysis_df.loc[promote_mask, "answer_only_ready"] = True
    analysis_df.loc[promote_mask, "example_consistency_ok"] = True
    analysis_df.loc[promote_mask, "selection_tier"] = "answer_only_keep"
    analysis_df.loc[promote_mask, "audit_priority_score"] = 0.0
    analysis_df.loc[promote_mask, "audit_reasons"] = ""
    analysis_df.loc[promote_mask, "analysis_notes"] = "bit_structured_support3_answer_only"
    analysis_df.loc[promote_mask, "suspect_label"] = False
    candidate_df = candidate_df.sort_values(
        ["bit_structured_formula_abstract_family", "bit_structured_formula_name", "id"],
        ascending=[True, True, True],
    ).reset_index(drop=True)
    return analysis_df, candidate_df


def collect_symbol_minus_prefix_subfamily_matches(prompt: str, query_text: str, answer: str) -> dict[str, Any]:
    query_match = SYMBOL_NUMERIC_EXPRESSION_PATTERN.match(str(query_text))
    if query_match is None or query_match.group(2) != "-":
        return {
            "query_operator": "",
            "same_operator_example_count": 0,
            "candidate_predictions": [],
            "winning_specs": [],
        }
    query_x_text = query_match.group(1)
    query_y_text = query_match.group(3)
    same_operator_examples = [
        (left_value, right_value, output_text)
        for left_value, operator, right_value, output_text in parse_symbol_numeric_examples(prompt)
        if operator == "-"
    ]
    if not same_operator_examples:
        return {
            "query_operator": "",
            "same_operator_example_count": 0,
            "candidate_predictions": [],
            "winning_specs": [],
        }
    if any(
        render_symbol_minus_prefix_abs_diff(left_value_text, right_value_text) != str(output_text)
        for left_value_text, right_value_text, output_text in same_operator_examples
    ):
        return {
            "query_operator": "",
            "same_operator_example_count": len(same_operator_examples),
            "candidate_predictions": [],
            "winning_specs": [],
        }

    query_x_tens = int(query_x_text[0])
    query_x_ones = int(query_x_text[1])
    query_y_tens = int(query_y_text[0])
    query_y_ones = int(query_y_text[1])
    diff_value = abs(int(query_x_text) - int(query_y_text))
    winning_specs: list[tuple[str, str, str]] = []
    if query_x_tens <= query_y_tens and query_x_ones < query_y_ones:
        predicted_answer = render_symbol_minus_prefix_abs_diff(query_x_text, query_y_text)
        winning_specs.append(("minus_prefix_reverse_no_borrow_zpad2", "string_template", predicted_answer))
    if query_x_tens <= query_y_tens and query_x_ones == query_y_ones and diff_value > 0 and diff_value % 10 == 0:
        predicted_answer = render_symbol_minus_prefix_abs_diff(query_x_text, query_y_text, trim_trailing_zero=True)
        winning_specs.append(("minus_prefix_reverse_no_borrow_trim_zero", "string_template", predicted_answer))
    return {
        "query_operator": "-",
        "same_operator_example_count": len(same_operator_examples),
        "candidate_predictions": sorted({predicted_answer for _, _, predicted_answer in winning_specs}),
        "winning_specs": winning_specs,
    }


def apply_symbol_minus_prefix_subfamily_promotions(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analysis_df = analysis_df.copy()
    numeric_mask = (
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["template_subtype"] == "numeric_2x2")
    )
    support_df = pd.DataFrame(
        columns=[
            "query_operator",
            "subfamily_name",
            "support_rows",
            "gold_match_rows",
            "error_rows",
            "safe_subfamily",
        ]
    )
    candidate_df = pd.DataFrame(
        columns=[
            "id",
            "selection_tier",
            "query_operator",
            "same_operator_example_count",
            "answer",
            "query_raw",
            "safe_prediction",
            "safe_support_rows",
            "safe_subfamily_name",
            "all_predictions",
        ]
    )
    if not numeric_mask.any():
        return analysis_df, support_df, candidate_df

    match_records: list[dict[str, Any]] = []
    row_match_map: dict[str, dict[str, Any]] = {}
    for row in analysis_df.loc[numeric_mask, ["id", "prompt", "query_raw", "answer", "selection_tier"]].to_dict(orient="records"):
        match_info = collect_symbol_minus_prefix_subfamily_matches(
            str(row["prompt"]),
            str(row["query_raw"]),
            str(row["answer"]),
        )
        if int(match_info["same_operator_example_count"]) <= 0 or not match_info["winning_specs"]:
            continue
        row_match_map[str(row["id"])] = {
            "selection_tier": str(row["selection_tier"]),
            "answer": str(row["answer"]),
            "query_raw": str(row["query_raw"]),
            "query_operator": str(match_info["query_operator"]),
            "same_operator_example_count": int(match_info["same_operator_example_count"]),
            "winning_specs": [
                (str(subfamily_name), str(format_name), str(predicted_answer))
                for subfamily_name, format_name, predicted_answer in match_info["winning_specs"]
            ],
        }
        for subfamily_name, format_name, predicted_answer in match_info["winning_specs"]:
            match_records.append(
                {
                    "id": str(row["id"]),
                    "query_operator": str(match_info["query_operator"]),
                    "subfamily_name": str(subfamily_name),
                    "format_name": str(format_name),
                    "predicted_answer": str(predicted_answer),
                    "matches_gold": bool(str(predicted_answer) == str(row["answer"])),
                }
            )
    if not match_records:
        return analysis_df, support_df, candidate_df

    match_df = pd.DataFrame(match_records)
    support_df = (
        match_df.groupby(["query_operator", "subfamily_name"], dropna=False)
        .agg(
            support_rows=("id", "size"),
            gold_match_rows=("matches_gold", "sum"),
        )
        .reset_index()
    )
    support_df["support_rows"] = support_df["support_rows"].astype(int)
    support_df["gold_match_rows"] = support_df["gold_match_rows"].astype(int)
    support_df["error_rows"] = support_df["support_rows"] - support_df["gold_match_rows"]
    support_df["safe_subfamily"] = (support_df["support_rows"] >= 2) & (support_df["error_rows"] == 0)
    safe_keys = {
        (str(row["query_operator"]), str(row["subfamily_name"]))
        for row in support_df.loc[support_df["safe_subfamily"]].to_dict(orient="records")
    }
    support_map = {
        (str(row["query_operator"]), str(row["subfamily_name"])): int(row["support_rows"])
        for row in support_df.to_dict(orient="records")
    }

    candidate_rows: list[dict[str, Any]] = []
    promote_predictions: dict[str, str] = {}
    for row_id, info in row_match_map.items():
        safe_matches = [
            (subfamily_name, predicted_answer)
            for subfamily_name, _, predicted_answer in info["winning_specs"]
            if (info["query_operator"], subfamily_name) in safe_keys
        ]
        if not safe_matches:
            continue
        safe_prediction_set = sorted({predicted_answer for _, predicted_answer in safe_matches})
        safe_subfamily_names = sorted({subfamily_name for subfamily_name, _ in safe_matches})
        safe_support_rows = max(
            support_map[(info["query_operator"], subfamily_name)]
            for subfamily_name in safe_subfamily_names
        )
        candidate_rows.append(
            {
                "id": row_id,
                "selection_tier": info["selection_tier"],
                "query_operator": info["query_operator"],
                "same_operator_example_count": info["same_operator_example_count"],
                "answer": info["answer"],
                "query_raw": info["query_raw"],
                "safe_prediction": safe_prediction_set[0] if len(safe_prediction_set) == 1 else "",
                "safe_support_rows": int(safe_support_rows),
                "safe_subfamily_name": "|".join(safe_subfamily_names),
                "all_predictions": "|".join(sorted({predicted_answer for _, _, predicted_answer in info["winning_specs"]})),
            }
        )
        if (
            info["selection_tier"] == "manual_audit_priority"
            and len(safe_prediction_set) == 1
            and safe_prediction_set[0] == info["answer"]
        ):
            promote_predictions[row_id] = safe_prediction_set[0]

    candidate_df = pd.DataFrame(candidate_rows, columns=list(candidate_df.columns))
    if promote_predictions:
        promote_mask = analysis_df["id"].astype(str).isin(set(promote_predictions))
        analysis_df.loc[promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[promote_mask, "id"].astype(str).map(promote_predictions)
        analysis_df.loc[promote_mask, "auto_solver_match"] = True
        analysis_df.loc[promote_mask, "answer_only_ready"] = True
        analysis_df.loc[promote_mask, "example_consistency_ok"] = True
        analysis_df.loc[promote_mask, "selection_tier"] = "answer_only_keep"
        analysis_df.loc[promote_mask, "audit_priority_score"] = 0.0
        analysis_df.loc[promote_mask, "audit_reasons"] = ""
        analysis_df.loc[promote_mask, "analysis_notes"] = "symbol_minus_prefix_subfamily"
        analysis_df.loc[promote_mask, "suspect_label"] = False

    support_df = support_df.sort_values(
        ["safe_subfamily", "support_rows", "gold_match_rows", "query_operator", "subfamily_name"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    if not candidate_df.empty:
        candidate_df = candidate_df.sort_values(
            ["selection_tier", "safe_support_rows", "same_operator_example_count", "id"],
            ascending=[True, False, False, True],
        ).reset_index(drop=True)
    return analysis_df, support_df, candidate_df


def collect_symbol_minus_direct_plain_matches(prompt: str, query_text: str, answer: str) -> dict[str, Any]:
    query_match = SYMBOL_NUMERIC_EXPRESSION_PATTERN.match(str(query_text))
    if query_match is None or query_match.group(2) != "-":
        return {
            "query_operator": "",
            "same_operator_example_count": 0,
            "candidate_predictions": [],
            "winning_specs": [],
        }
    query_x_text = query_match.group(1)
    query_y_text = query_match.group(3)
    same_operator_examples = [
        (left_value, right_value, output_text)
        for left_value, operator, right_value, output_text in parse_symbol_numeric_examples(prompt)
        if operator == "-"
    ]
    if not same_operator_examples:
        return {
            "query_operator": "",
            "same_operator_example_count": 0,
            "candidate_predictions": [],
            "winning_specs": [],
        }

    signed_plain_examples = all(
        render_symbol_signed_diff_plain(left_value_text, right_value_text) == str(output_text)
        for left_value_text, right_value_text, output_text in same_operator_examples
    )
    abs_plain_examples = all(
        render_symbol_abs_diff_plain(left_value_text, right_value_text) == str(output_text)
        for left_value_text, right_value_text, output_text in same_operator_examples
    )
    if not signed_plain_examples and not abs_plain_examples:
        return {
            "query_operator": "-",
            "same_operator_example_count": len(same_operator_examples),
            "candidate_predictions": [],
            "winning_specs": [],
        }

    winning_specs: list[tuple[str, str, str]] = []
    if query_x_text[0] < query_y_text[0] and query_x_text[1] < query_y_text[1] and signed_plain_examples:
        winning_specs.append(
            ("minus_signed_plain_both_lt", "string_template", render_symbol_signed_diff_plain(query_x_text, query_y_text))
        )
    if query_x_text[0] > query_y_text[0] and query_x_text[1] > query_y_text[1]:
        if signed_plain_examples:
            winning_specs.append(
                ("minus_signed_plain_both_gt", "string_template", render_symbol_signed_diff_plain(query_x_text, query_y_text))
            )
        if abs_plain_examples:
            winning_specs.append(
                ("minus_abs_plain_both_gt", "string_template", render_symbol_abs_diff_plain(query_x_text, query_y_text))
            )
    return {
        "query_operator": "-",
        "same_operator_example_count": len(same_operator_examples),
        "candidate_predictions": sorted({predicted_answer for _, _, predicted_answer in winning_specs}),
        "winning_specs": winning_specs,
    }


def apply_symbol_minus_direct_plain_promotions(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analysis_df = analysis_df.copy()
    numeric_mask = (
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["template_subtype"] == "numeric_2x2")
    )
    support_df = pd.DataFrame(
        columns=[
            "query_operator",
            "subfamily_name",
            "support_rows",
            "gold_match_rows",
            "error_rows",
            "safe_subfamily",
        ]
    )
    candidate_df = pd.DataFrame(
        columns=[
            "id",
            "selection_tier",
            "query_operator",
            "same_operator_example_count",
            "answer",
            "query_raw",
            "safe_prediction",
            "safe_support_rows",
            "safe_subfamily_name",
            "all_predictions",
        ]
    )
    if not numeric_mask.any():
        return analysis_df, support_df, candidate_df

    match_records: list[dict[str, Any]] = []
    row_match_map: dict[str, dict[str, Any]] = {}
    for row in analysis_df.loc[numeric_mask, ["id", "prompt", "query_raw", "answer", "selection_tier"]].to_dict(orient="records"):
        match_info = collect_symbol_minus_direct_plain_matches(
            str(row["prompt"]),
            str(row["query_raw"]),
            str(row["answer"]),
        )
        if int(match_info["same_operator_example_count"]) <= 0 or not match_info["winning_specs"]:
            continue
        row_match_map[str(row["id"])] = {
            "selection_tier": str(row["selection_tier"]),
            "answer": str(row["answer"]),
            "query_raw": str(row["query_raw"]),
            "query_operator": str(match_info["query_operator"]),
            "same_operator_example_count": int(match_info["same_operator_example_count"]),
            "winning_specs": [
                (str(subfamily_name), str(format_name), str(predicted_answer))
                for subfamily_name, format_name, predicted_answer in match_info["winning_specs"]
            ],
        }
        for subfamily_name, format_name, predicted_answer in match_info["winning_specs"]:
            match_records.append(
                {
                    "id": str(row["id"]),
                    "query_operator": str(match_info["query_operator"]),
                    "subfamily_name": str(subfamily_name),
                    "format_name": str(format_name),
                    "predicted_answer": str(predicted_answer),
                    "matches_gold": bool(str(predicted_answer) == str(row["answer"])),
                }
            )
    if not match_records:
        return analysis_df, support_df, candidate_df

    match_df = pd.DataFrame(match_records)
    support_df = (
        match_df.groupby(["query_operator", "subfamily_name"], dropna=False)
        .agg(
            support_rows=("id", "size"),
            gold_match_rows=("matches_gold", "sum"),
        )
        .reset_index()
    )
    support_df["support_rows"] = support_df["support_rows"].astype(int)
    support_df["gold_match_rows"] = support_df["gold_match_rows"].astype(int)
    support_df["error_rows"] = support_df["support_rows"] - support_df["gold_match_rows"]
    support_df["safe_subfamily"] = (support_df["support_rows"] >= 3) & (support_df["error_rows"] == 0)
    safe_keys = {
        (str(row["query_operator"]), str(row["subfamily_name"]))
        for row in support_df.loc[support_df["safe_subfamily"]].to_dict(orient="records")
    }
    support_map = {
        (str(row["query_operator"]), str(row["subfamily_name"])): int(row["support_rows"])
        for row in support_df.to_dict(orient="records")
    }

    candidate_rows: list[dict[str, Any]] = []
    promote_predictions: dict[str, str] = {}
    for row_id, info in row_match_map.items():
        safe_matches = [
            (subfamily_name, predicted_answer)
            for subfamily_name, _, predicted_answer in info["winning_specs"]
            if (info["query_operator"], subfamily_name) in safe_keys
        ]
        if not safe_matches:
            continue
        safe_prediction_set = sorted({predicted_answer for _, predicted_answer in safe_matches})
        safe_subfamily_names = sorted({subfamily_name for subfamily_name, _ in safe_matches})
        safe_support_rows = max(
            support_map[(info["query_operator"], subfamily_name)]
            for subfamily_name in safe_subfamily_names
        )
        candidate_rows.append(
            {
                "id": row_id,
                "selection_tier": info["selection_tier"],
                "query_operator": info["query_operator"],
                "same_operator_example_count": info["same_operator_example_count"],
                "answer": info["answer"],
                "query_raw": info["query_raw"],
                "safe_prediction": safe_prediction_set[0] if len(safe_prediction_set) == 1 else "",
                "safe_support_rows": int(safe_support_rows),
                "safe_subfamily_name": "|".join(safe_subfamily_names),
                "all_predictions": "|".join(sorted({predicted_answer for _, _, predicted_answer in info["winning_specs"]})),
            }
        )
        if (
            info["selection_tier"] == "manual_audit_priority"
            and len(safe_prediction_set) == 1
            and safe_prediction_set[0] == info["answer"]
        ):
            promote_predictions[row_id] = safe_prediction_set[0]

    candidate_df = pd.DataFrame(candidate_rows, columns=list(candidate_df.columns))
    if promote_predictions:
        promote_mask = analysis_df["id"].astype(str).isin(set(promote_predictions))
        analysis_df.loc[promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[promote_mask, "id"].astype(str).map(promote_predictions)
        analysis_df.loc[promote_mask, "auto_solver_match"] = True
        analysis_df.loc[promote_mask, "answer_only_ready"] = True
        analysis_df.loc[promote_mask, "example_consistency_ok"] = True
        analysis_df.loc[promote_mask, "selection_tier"] = "answer_only_keep"
        analysis_df.loc[promote_mask, "audit_priority_score"] = 0.0
        analysis_df.loc[promote_mask, "audit_reasons"] = ""
        analysis_df.loc[promote_mask, "analysis_notes"] = "symbol_minus_direct_plain_subfamily"
        analysis_df.loc[promote_mask, "suspect_label"] = False

    support_df = support_df.sort_values(
        ["safe_subfamily", "support_rows", "gold_match_rows", "query_operator", "subfamily_name"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    if not candidate_df.empty:
        candidate_df = candidate_df.sort_values(
            ["selection_tier", "safe_support_rows", "same_operator_example_count", "id"],
            ascending=[True, False, False, True],
        ).reset_index(drop=True)
    return analysis_df, support_df, candidate_df


def collect_symbol_star_prefix_if_negative_matches(prompt: str, query_text: str, answer: str) -> dict[str, Any]:
    match_info = collect_symbol_numeric_operator_formula_matches(prompt, query_text, answer)
    query_operator = str(match_info["query_operator"])
    same_operator_example_count = int(match_info["same_operator_example_count"])
    if query_operator != "*":
        return {
            "query_operator": "",
            "same_operator_example_count": 0,
            "candidate_predictions": [],
            "all_predictions": [],
            "winning_specs": [],
        }
    if same_operator_example_count != 1:
        return {
            "query_operator": query_operator,
            "same_operator_example_count": same_operator_example_count,
            "candidate_predictions": [],
            "all_predictions": sorted({str(prediction) for prediction in match_info["candidate_predictions"]}),
            "winning_specs": [],
        }

    winning_specs = [
        ("star_prefix_if_negative_same_bucket1", "string_template", str(predicted_answer))
        for formula_name, format_name, predicted_answer in match_info["winning_specs"]
        if str(formula_name) == "x_minus_y" and str(format_name) == "prefix_if_negative"
    ]
    return {
        "query_operator": query_operator,
        "same_operator_example_count": same_operator_example_count,
        "candidate_predictions": sorted({predicted_answer for _, _, predicted_answer in winning_specs}),
        "all_predictions": sorted({str(prediction) for prediction in match_info["candidate_predictions"]}),
        "winning_specs": winning_specs,
    }


def apply_symbol_star_prefix_if_negative_promotions(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    analysis_df = analysis_df.copy()
    numeric_mask = (
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["template_subtype"] == "numeric_2x2")
    )
    support_df = pd.DataFrame(
        columns=[
            "query_operator",
            "subfamily_name",
            "support_rows",
            "gold_match_rows",
            "error_rows",
            "safe_subfamily",
        ]
    )
    candidate_df = pd.DataFrame(
        columns=[
            "id",
            "selection_tier",
            "query_operator",
            "same_operator_example_count",
            "answer",
            "query_raw",
            "safe_prediction",
            "safe_support_rows",
            "safe_subfamily_name",
            "all_predictions",
        ]
    )
    if not numeric_mask.any():
        return analysis_df, support_df, candidate_df

    match_records: list[dict[str, Any]] = []
    row_match_map: dict[str, dict[str, Any]] = {}
    for row in analysis_df.loc[numeric_mask, ["id", "prompt", "query_raw", "answer", "selection_tier"]].to_dict(orient="records"):
        match_info = collect_symbol_star_prefix_if_negative_matches(
            str(row["prompt"]),
            str(row["query_raw"]),
            str(row["answer"]),
        )
        if int(match_info["same_operator_example_count"]) <= 0 or not match_info["winning_specs"]:
            continue
        row_match_map[str(row["id"])] = {
            "selection_tier": str(row["selection_tier"]),
            "answer": str(row["answer"]),
            "query_raw": str(row["query_raw"]),
            "query_operator": str(match_info["query_operator"]),
            "same_operator_example_count": int(match_info["same_operator_example_count"]),
            "all_predictions": [str(prediction) for prediction in match_info["all_predictions"]],
            "winning_specs": [
                (str(subfamily_name), str(format_name), str(predicted_answer))
                for subfamily_name, format_name, predicted_answer in match_info["winning_specs"]
            ],
        }
        for subfamily_name, format_name, predicted_answer in match_info["winning_specs"]:
            match_records.append(
                {
                    "id": str(row["id"]),
                    "query_operator": str(match_info["query_operator"]),
                    "subfamily_name": str(subfamily_name),
                    "format_name": str(format_name),
                    "predicted_answer": str(predicted_answer),
                    "matches_gold": bool(str(predicted_answer) == str(row["answer"])),
                }
            )
    if not match_records:
        return analysis_df, support_df, candidate_df

    match_df = pd.DataFrame(match_records)
    support_df = (
        match_df.groupby(["query_operator", "subfamily_name"], dropna=False)
        .agg(
            support_rows=("id", "size"),
            gold_match_rows=("matches_gold", "sum"),
        )
        .reset_index()
    )
    support_df["support_rows"] = support_df["support_rows"].astype(int)
    support_df["gold_match_rows"] = support_df["gold_match_rows"].astype(int)
    support_df["error_rows"] = support_df["support_rows"] - support_df["gold_match_rows"]
    support_df["safe_subfamily"] = (support_df["support_rows"] >= 3) & (support_df["error_rows"] == 0)
    safe_keys = {
        (str(row["query_operator"]), str(row["subfamily_name"]))
        for row in support_df.loc[support_df["safe_subfamily"]].to_dict(orient="records")
    }
    support_map = {
        (str(row["query_operator"]), str(row["subfamily_name"])): int(row["support_rows"])
        for row in support_df.to_dict(orient="records")
    }

    candidate_rows: list[dict[str, Any]] = []
    promote_predictions: dict[str, str] = {}
    for row_id, info in row_match_map.items():
        safe_matches = [
            (subfamily_name, predicted_answer)
            for subfamily_name, _, predicted_answer in info["winning_specs"]
            if (info["query_operator"], subfamily_name) in safe_keys
        ]
        if not safe_matches:
            continue
        safe_prediction_set = sorted({predicted_answer for _, predicted_answer in safe_matches})
        safe_subfamily_names = sorted({subfamily_name for subfamily_name, _ in safe_matches})
        safe_support_rows = max(
            support_map[(info["query_operator"], subfamily_name)]
            for subfamily_name in safe_subfamily_names
        )
        candidate_rows.append(
            {
                "id": row_id,
                "selection_tier": info["selection_tier"],
                "query_operator": info["query_operator"],
                "same_operator_example_count": info["same_operator_example_count"],
                "answer": info["answer"],
                "query_raw": info["query_raw"],
                "safe_prediction": safe_prediction_set[0] if len(safe_prediction_set) == 1 else "",
                "safe_support_rows": int(safe_support_rows),
                "safe_subfamily_name": "|".join(safe_subfamily_names),
                "all_predictions": "|".join(info["all_predictions"]),
            }
        )
        if (
            info["selection_tier"] == "manual_audit_priority"
            and len(safe_prediction_set) == 1
            and safe_prediction_set[0] == info["answer"]
        ):
            promote_predictions[row_id] = safe_prediction_set[0]

    candidate_df = pd.DataFrame(candidate_rows, columns=list(candidate_df.columns))
    if promote_predictions:
        promote_mask = analysis_df["id"].astype(str).isin(set(promote_predictions))
        analysis_df.loc[promote_mask, "auto_solver_predicted_answer"] = analysis_df.loc[promote_mask, "id"].astype(str).map(promote_predictions)
        analysis_df.loc[promote_mask, "auto_solver_match"] = True
        analysis_df.loc[promote_mask, "answer_only_ready"] = True
        analysis_df.loc[promote_mask, "example_consistency_ok"] = True
        analysis_df.loc[promote_mask, "selection_tier"] = "answer_only_keep"
        analysis_df.loc[promote_mask, "audit_priority_score"] = 0.0
        analysis_df.loc[promote_mask, "audit_reasons"] = ""
        analysis_df.loc[promote_mask, "analysis_notes"] = "symbol_star_prefix_if_negative_subfamily"
        analysis_df.loc[promote_mask, "suspect_label"] = False

    support_df = support_df.sort_values(
        ["safe_subfamily", "support_rows", "gold_match_rows", "query_operator", "subfamily_name"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    if not candidate_df.empty:
        candidate_df = candidate_df.sort_values(
            ["selection_tier", "safe_support_rows", "same_operator_example_count", "id"],
            ascending=[True, False, False, True],
        ).reset_index(drop=True)
    return analysis_df, support_df, candidate_df


def write_dataframe(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def escape_markdown(text: Any) -> str:
    value = str(text)
    value = value.replace("\n", " ").replace("|", "\\|")
    return value


def markdown_table(frame: pd.DataFrame, columns: list[str], limit: int | None = None) -> str:
    subset = frame.loc[:, columns]
    if limit is not None:
        subset = subset.head(limit)
    headers = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = [
        "| " + " | ".join(escape_markdown(value) for value in row) + " |"
        for row in subset.itertuples(index=False, name=None)
    ]
    return "\n".join([headers, divider, *rows]) if rows else "\n".join([headers, divider])


def family_summary_table(analysis_df: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for family, group in analysis_df.groupby("family", sort=True):
        summary_rows.append(
            {
                "family": family,
                "rows": int(len(group)),
                "parse_ok_rate": round(float(group["parse_ok"].mean()), 4),
                "verified_trace_ready": int(group["verified_trace_ready"].sum()),
                "answer_only_keep": int((group["selection_tier"] == "answer_only_keep").sum()),
                "manual_audit_priority": int((group["selection_tier"] == "manual_audit_priority").sum()),
                "exclude_suspect": int((group["selection_tier"] == "exclude_suspect").sum()),
                "suspect_labels": int(group["suspect_label"].sum()),
                "avg_hard_score": round(float(group["hard_score"].mean()), 4),
            }
        )
    return pd.DataFrame(summary_rows).sort_values("family").reset_index(drop=True)


def baseline_recovery_table(
    analysis_df: pd.DataFrame,
    baseline_coverage: dict[str, dict[str, float]],
) -> pd.DataFrame:
    rows = []
    for family, group in analysis_df.groupby("family", sort=True):
        total = int(len(group))
        baseline = baseline_coverage.get(family, {})
        baseline_solved = int(baseline.get("solved", BASELINE_TEACHER_SOLVED.get(family, 0)))
        recovered = int(group["verified_trace_ready"].sum())
        rows.append(
            {
                "family": family,
                "total": total,
                "baseline_solved": baseline_solved,
                "baseline_coverage": round(baseline_solved / total, 4) if total else 0.0,
                "recovered_solved": recovered,
                "recovered_coverage": round(recovered / total, 4) if total else 0.0,
                "delta_solved": recovered - baseline_solved,
            }
        )
    return pd.DataFrame(rows).sort_values("family").reset_index(drop=True)


def probe_symbol_tail_cases(analysis_df: pd.DataFrame, v1: Any) -> tuple[pd.DataFrame, pd.DataFrame]:
    extra_formulas: dict[str, Any] = {}
    for coeff_x in [-2, -1, 0, 1, 2]:
        for coeff_y in [-2, -1, 0, 1, 2]:
            if coeff_x == 0 and coeff_y == 0:
                continue
            for bias in [-3, -2, -1, 0, 1, 2, 3]:
                formula_name = f"linear_{coeff_x}_{coeff_y}_{bias}"
                extra_formulas[formula_name] = (
                    lambda coeff_x, coeff_y, bias: lambda x, y: coeff_x * x + coeff_y * y + bias
                )(coeff_x, coeff_y, bias)
    extra_formulas.update(
        {
            "max_xy": lambda x, y: max(x, y),
            "min_xy": lambda x, y: min(x, y),
            "avg_if_int": lambda x, y: (x + y) // 2 if (x + y) % 2 == 0 else None,
        }
    )

    numeric_subset = analysis_df.loc[
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["template_subtype"] == "numeric_2x2")
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & (analysis_df["symbol_same_operator_example_count"] >= 2)
    ].reset_index(drop=True)

    numeric_additional_recovery = 0
    for row in numeric_subset.itertuples(index=False):
        prompt = str(row.prompt)
        matches: list[tuple[str, str, str, str]] = []
        for line in prompt.splitlines():
            stripped = line.strip()
            if "=" not in stripped:
                continue
            left_text, right_text = [part.strip() for part in stripped.split("=", 1)]
            match = SYMBOL_NUMERIC_EXPRESSION_PATTERN.match(left_text)
            if match is None:
                continue
            matches.append((match.group(1), match.group(2), match.group(3), right_text.strip(" `")))
        if len(matches) < 2:
            continue
        *examples, query = matches
        query_x = int(query[0])
        query_operator = query[1]
        query_y = int(query[2])
        same_operator_examples = [
            (int(left_value), int(right_value), output_text)
            for left_value, operator, right_value, output_text in examples
            if operator == query_operator
        ]
        candidate_predictions: set[str] = set()
        all_formula_specs = [*SYMBOL_NUMERIC_FORMULAS.items(), *extra_formulas.items()]
        for formula_name, formula in all_formula_specs:
            for _, formatter in iter_symbol_numeric_formatters(formula_name):
                valid = True
                for left_value, right_value, output_text in same_operator_examples:
                    numeric_value = formula(left_value, right_value)
                    if numeric_value is None or formatter(query_operator, numeric_value) != str(output_text):
                        valid = False
                        break
                if not valid:
                    continue
                query_numeric_value = formula(query_x, query_y)
                if query_numeric_value is None:
                    continue
                candidate_predictions.add(formatter(query_operator, query_numeric_value))
        if len(candidate_predictions) == 1 and answers_match(str(row.answer), next(iter(candidate_predictions))):
            numeric_additional_recovery += 1

    glyph_subset = analysis_df.loc[
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["template_subtype"] == "glyph_len5")
        & (analysis_df["selection_tier"] == "manual_audit_priority")
    ].reset_index(drop=True)
    glyph_query_consistent_records: list[dict[str, Any]] = []
    for row in glyph_subset.itertuples(index=False):
        parsed = v1.parse_symbol_prompt(str(row.prompt), str(row.answer))
        examples = extract_examples(parsed)
        with_query = examples + [(str(parsed.query_raw or ""), str(row.answer))]
        if glyph_multiset_mapping_exists(with_query) and glyph_output_order_acyclic(with_query):
            glyph_query_consistent_records.append(
                {
                    "id": str(row.id),
                    "hard_score": float(row.hard_score),
                    "answer": str(row.answer),
                    "query_raw": str(parsed.query_raw or ""),
                    "audit_reasons": str(row.audit_reasons),
                }
            )

    probe_summary_df = pd.DataFrame(
        [
            {
                "probe_name": "numeric_broader_linear_small_coeff",
                "rows_checked": int(len(numeric_subset)),
                "rows_consistent_or_recovered": int(numeric_additional_recovery),
                "notes": "a,b in [-2,2], c in [-3,3], plus min/max/avg_if_int; no safe extra recoveries",
            },
            {
                "probe_name": "glyph_query_answer_consistency",
                "rows_checked": int(len(glyph_subset)),
                "rows_consistent_or_recovered": int(len(glyph_query_consistent_records)),
                "notes": "query+gold preserves multiset+order constraints but remains non-unique, so rows stay manual",
            },
        ]
    )
    glyph_query_consistent_df = pd.DataFrame(glyph_query_consistent_records).sort_values(
        ["hard_score", "id"], ascending=[False, True]
    ).reset_index(drop=True) if glyph_query_consistent_records else pd.DataFrame(
        columns=["id", "hard_score", "answer", "query_raw", "audit_reasons"]
    )
    return probe_summary_df, glyph_query_consistent_df


def collect_symbol_query_only_arithmetic_rejections(
    manual_pass1_df: pd.DataFrame,
    prompt_by_id: dict[str, str],
) -> pd.DataFrame:
    columns = [
        "id",
        "query_raw",
        "answer",
        "query_only_matching_families",
        "same_operator_example_count",
        "candidate_prediction_count",
        "candidate_predictions",
        "rejection_reason",
        "prompt_example_lines",
    ]
    if len(manual_pass1_df) == 0:
        return pd.DataFrame(columns=columns)

    subset = manual_pass1_df.loc[
        (manual_pass1_df["audit_focus"] == "symbol_numeric_same_op")
        & (manual_pass1_df["selection_tier"] == "manual_audit_priority")
        & (manual_pass1_df["symbol_same_operator_example_count"] >= 2)
    ].copy()
    if len(subset) == 0:
        return pd.DataFrame(columns=columns)

    records: list[dict[str, Any]] = []
    for row in subset.to_dict(orient="records"):
        query_text = str(row.get("query_raw", ""))
        match = SYMBOL_NUMERIC_EXPRESSION_PATTERN.match(query_text)
        if match is None:
            continue
        x_text, _, y_text = match.groups()
        x_value = int(x_text)
        y_value = int(y_text)
        gold_answer = str(row.get("answer", "")).strip()
        matching_families: list[str] = []
        if gold_answer == str(x_value + y_value):
            matching_families.append("x_plus_y")
        if gold_answer == str(x_value - y_value):
            matching_families.append("x_minus_y")
        abs_diff_plain = str(abs(x_value - y_value))
        abs_diff_zpad = f"{abs(x_value - y_value):02d}"
        if gold_answer in {abs_diff_plain, abs_diff_zpad}:
            matching_families.append("abs_diff_2d")
        if gold_answer == f"{99 - abs(x_value - y_value):02d}":
            matching_families.append("comp99_abs_diff_2d")
        if not matching_families:
            continue

        prompt = prompt_by_id.get(str(row.get("id", "")), "")
        solve_result = solve_symbol_numeric_operator_formula(prompt, query_text, gold_answer)
        rejection_reason = (
            "same_operator_examples_conflict"
            if int(solve_result["candidate_prediction_count"]) == 0
            else "query_format_ambiguous"
        )
        prompt_example_lines = " || ".join(
            line.strip()
            for line in str(prompt).splitlines()
            if "=" in line and any(char.isdigit() for char in line)
        )
        records.append(
            {
                "id": str(row.get("id", "")),
                "query_raw": query_text,
                "answer": gold_answer,
                "query_only_matching_families": "|".join(sorted(set(matching_families))),
                "same_operator_example_count": int(row.get("symbol_same_operator_example_count", 0)),
                "candidate_prediction_count": int(solve_result["candidate_prediction_count"]),
                "candidate_predictions": "|".join(solve_result["candidate_predictions"]),
                "rejection_reason": rejection_reason,
                "prompt_example_lines": prompt_example_lines,
            }
        )

    if not records:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(records).sort_values(
        ["rejection_reason", "same_operator_example_count", "id"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def load_optional_dataframe(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=columns)
    df = pd.read_csv(path, low_memory=False)
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    return df.loc[:, columns].copy()


def build_symbol_mimic_union(
    symbol_query_only_rejection_df: pd.DataFrame,
    known_family_mimic_df: pd.DataFrame,
) -> pd.DataFrame:
    base_columns = [
        "id",
        "query_raw",
        "answer",
        "query_only_matching_families",
        "same_operator_example_count",
        "candidate_prediction_count",
        "candidate_predictions",
        "rejection_reason",
        "prompt_example_lines",
        "source",
    ]
    query_df = symbol_query_only_rejection_df.copy()
    if len(query_df):
        query_df["source"] = "report17"
        query_df = query_df.loc[:, base_columns]
    else:
        query_df = pd.DataFrame(columns=base_columns)

    known_df = known_family_mimic_df.copy()
    if len(known_df):
        if "source" not in known_df.columns:
            known_df["source"] = "known_family"
        known_df = known_df.loc[:, base_columns]
    else:
        known_df = pd.DataFrame(columns=base_columns)

    union_df = pd.concat([query_df, known_df], ignore_index=True)
    if not len(union_df):
        return pd.DataFrame(columns=base_columns)
    union_df = union_df.drop_duplicates(subset=["id"], keep="first")
    return union_df.sort_values(
        ["source", "rejection_reason", "same_operator_example_count", "id"],
        ascending=[True, True, False, True],
    ).reset_index(drop=True)


def same_operator_bucket_label(value: Any) -> str:
    count = int(value)
    if count <= 1:
        return "1"
    if count == 2:
        return "2"
    if count == 3:
        return "3"
    return "4+"


def build_symbol_round2_cluster_summary(
    analysis_df: pd.DataFrame,
    symbol_mimic_union_df: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "symbol_query_operator",
        "answer_len",
        "answer_has_operator_char",
        "same_operator_bucket",
        "rows",
        "representative_ids",
    ]
    subset = analysis_df.loc[
        (analysis_df["family"] == "symbol_equation")
        & (analysis_df["selection_tier"] == "manual_audit_priority")
        & (analysis_df["template_subtype"] == "numeric_2x2")
        & (analysis_df["symbol_same_operator_example_count"] >= 1)
    ].copy()
    if len(symbol_mimic_union_df):
        subset = subset.loc[~subset["id"].astype(str).isin(set(symbol_mimic_union_df["id"].astype(str)))].copy()
    if not len(subset):
        return pd.DataFrame(columns=columns)

    subset["answer_text"] = subset["answer"].astype(str)
    subset["answer_len"] = subset["answer_text"].str.len()
    subset["answer_has_operator_char"] = subset["answer_text"].str.contains(r"[+\-*/]", regex=True)
    subset["same_operator_bucket"] = subset["symbol_same_operator_example_count"].map(same_operator_bucket_label)

    records: list[dict[str, Any]] = []
    group_cols = ["symbol_query_operator", "answer_len", "answer_has_operator_char", "same_operator_bucket"]
    for group_key, group in subset.groupby(group_cols, sort=False):
        representative_ids = ",".join(
            group.sort_values(["hard_score", "id"], ascending=[False, True])["id"].astype(str).head(5)
        )
        records.append(
            {
                "symbol_query_operator": group_key[0],
                "answer_len": int(group_key[1]),
                "answer_has_operator_char": bool(group_key[2]),
                "same_operator_bucket": str(group_key[3]),
                "rows": int(len(group)),
                "representative_ids": representative_ids,
            }
        )
    return pd.DataFrame(records, columns=columns).sort_values(
        ["rows", "answer_has_operator_char", "symbol_query_operator", "answer_len", "same_operator_bucket"],
        ascending=[False, True, True, True, True],
    ).reset_index(drop=True)


def build_reports(
    out_root: Path,
    analysis_df: pd.DataFrame,
    family_summary_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
    template_df: pd.DataFrame,
    selection_df: pd.DataFrame,
    bit_df: pd.DataFrame,
    text_df: pd.DataFrame,
    symbol_df: pd.DataFrame,
    text_unknown_df: pd.DataFrame,
    text_completion_df: pd.DataFrame,
    symbol_operator_df: pd.DataFrame,
    symbol_tail_probe_df: pd.DataFrame,
    symbol_string_promotion_df: pd.DataFrame,
    glyph_query_consistent_df: pd.DataFrame,
    glyph_exact_df: pd.DataFrame,
    binary_affine_exclude_df: pd.DataFrame,
    binary_affine_manual_df: pd.DataFrame,
    binary_cluster_df: pd.DataFrame,
    glyph_summary_df: pd.DataFrame,
    text_manual_queue_df: pd.DataFrame,
    symbol_manual_queue_df: pd.DataFrame,
    binary_manual_queue_df: pd.DataFrame,
    manual_pass1_df: pd.DataFrame,
    symbol_query_only_rejection_df: pd.DataFrame,
    symbol_mimic_union_df: pd.DataFrame,
    symbol_round2_cluster_df: pd.DataFrame,
) -> None:
    reports_dir = out_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    verified_count = int((analysis_df["selection_tier"] == "verified_trace_ready").sum())
    answer_only_count = int((analysis_df["selection_tier"] == "answer_only_keep").sum())
    manual_count = int((analysis_df["selection_tier"] == "manual_audit_priority").sum())
    exclude_count = int((analysis_df["selection_tier"] == "exclude_suspect").sum())
    top_manual = (
        analysis_df.loc[analysis_df["selection_tier"] == "manual_audit_priority", ["id", "family", "template_subtype", "hard_score", "audit_priority_score", "audit_reasons", "answer"]]
        .sort_values(["audit_priority_score", "hard_score", "id"], ascending=[False, False, True])
        .head(20)
        .reset_index(drop=True)
    )
    glyph_promising_df = (
        analysis_df.loc[
            (analysis_df["family"] == "symbol_equation")
            & (analysis_df["template_subtype"] == "glyph_len5")
            & (analysis_df["glyph_multiset_possible"])
            & (analysis_df["glyph_order_acyclic"])
        ]
        .sort_values(["hard_score", "id"], ascending=[False, True])
        .reset_index(drop=True)
    )
    symbol_query_only_rejection_summary_df = grouped_counts(
        symbol_query_only_rejection_df,
        ["query_only_matching_families", "rejection_reason"],
        name="rows",
    ) if len(symbol_query_only_rejection_df) else pd.DataFrame(
        columns=["query_only_matching_families", "rejection_reason", "rows"]
    )
    symbol_query_only_conflict_count = int(
        (symbol_query_only_rejection_df["rejection_reason"] == "same_operator_examples_conflict").sum()
    ) if len(symbol_query_only_rejection_df) else 0
    symbol_query_only_ambiguous_count = int(
        (symbol_query_only_rejection_df["rejection_reason"] == "query_format_ambiguous").sum()
    ) if len(symbol_query_only_rejection_df) else 0
    symbol_mimic_union_summary_df = grouped_counts(
        symbol_mimic_union_df,
        ["query_only_matching_families", "rejection_reason"],
        name="rows",
    ) if len(symbol_mimic_union_df) else pd.DataFrame(
        columns=["query_only_matching_families", "rejection_reason", "rows"]
    )
    symbol_mimic_union_total = int(len(symbol_mimic_union_df))
    symbol_mimic_report17_count = int((symbol_mimic_union_df["source"] == "report17").sum()) if len(symbol_mimic_union_df) else 0
    symbol_mimic_known_count = int((symbol_mimic_union_df["source"] == "known_family").sum()) if len(symbol_mimic_union_df) else 0
    symbol_round2_remaining_count = int(symbol_round2_cluster_df["rows"].sum()) if len(symbol_round2_cluster_df) else 0
    comp99_family_df = (
        analysis_df.loc[
            (analysis_df["family"] == "symbol_equation")
            & (analysis_df["template_subtype"] == "numeric_2x2")
            & (analysis_df["symbol_numeric_formula_name"] == "comp99_abs_diff_2d")
        ]
        .sort_values(["selection_tier", "symbol_same_operator_example_count", "id"], ascending=[True, False, True])
        .reset_index(drop=True)
    )
    comp99_summary_df = grouped_counts(
        comp99_family_df,
        ["selection_tier", "symbol_same_operator_example_count", "analysis_notes"],
        name="rows",
    ) if len(comp99_family_df) else pd.DataFrame(
        columns=["selection_tier", "symbol_same_operator_example_count", "analysis_notes", "rows"]
    )
    comp99_promoted_df = (
        comp99_family_df.loc[
            comp99_family_df["selection_tier"].isin(["verified_trace_ready", "answer_only_keep"])
        ]
        .copy()
        .reset_index(drop=True)
    )
    comp99_manual_df = (
        comp99_family_df.loc[comp99_family_df["selection_tier"] == "manual_audit_priority"]
        .copy()
        .reset_index(drop=True)
    )
    comp99_query_only_rejection_df = (
        symbol_query_only_rejection_df.loc[
            symbol_query_only_rejection_df["query_only_matching_families"].fillna("").str.contains("comp99_abs_diff_2d")
        ]
        .copy()
        .reset_index(drop=True)
    )
    glyph_exact_summary_df = grouped_counts(
        glyph_exact_df,
        ["exact_coarse_status", "multiset_unique", "order_unique"],
        name="rows",
    ) if len(glyph_exact_df) else pd.DataFrame(
        columns=["exact_coarse_status", "multiset_unique", "order_unique", "rows"]
    )
    glyph_exact_unseen_count = int((glyph_exact_df["exact_coarse_status"] == "query_has_unseen_chars").sum()) if len(glyph_exact_df) else 0
    glyph_exact_ambiguous_multiset_count = int((glyph_exact_df["exact_coarse_status"] == "ambiguous_multiset").sum()) if len(glyph_exact_df) else 0
    glyph_exact_ambiguous_order_count = int((glyph_exact_df["exact_coarse_status"] == "ambiguous_order").sum()) if len(glyph_exact_df) else 0
    glyph_exact_no_multiset_count = int((glyph_exact_df["exact_coarse_status"] == "no_example_only_multiset").sum()) if len(glyph_exact_df) else 0
    glyph_exact_unique_count = int((glyph_exact_df["exact_coarse_status"] == "unique_string").sum()) if len(glyph_exact_df) else 0
    glyph_exact_unique_gold_match_count = int(
        ((glyph_exact_df["exact_coarse_status"] == "unique_string") & (glyph_exact_df["predicted_answer"] == glyph_exact_df["answer"])).sum()
    ) if len(glyph_exact_df) else 0
    glyph_exact_nontrivial_df = glyph_exact_df.loc[
        glyph_exact_df["exact_coarse_status"] != "query_has_unseen_chars"
    ].copy() if len(glyph_exact_df) else pd.DataFrame(
        columns=["id", "exact_coarse_status", "answer", "predicted_answer", "query_raw", "glyph_query_unseen_chars"]
    )
    glyph_exact_unseen_df = glyph_exact_df.loc[
        glyph_exact_df["exact_coarse_status"] == "query_has_unseen_chars"
    ].copy() if len(glyph_exact_df) else pd.DataFrame(
        columns=["id", "answer", "query_raw", "glyph_query_unseen_chars"]
    )

    overview_lines = [
        f"# {SCRIPT_VERSION} overview",
        "",
        f"- generated_at_utc: `{utc_now()}`",
        "- grounded_in: `README.md`, `try-cuda-train-data-analyst-plan.md`, `try-cuda-train-result.md`, `try-cuda-train.md`",
        f"- analyzed_rows: `{len(analysis_df)}`",
        f"- verified_trace_ready: `{verified_count}`",
        f"- answer_only_keep: `{answer_only_count}`",
        f"- manual_audit_priority: `{manual_count}`",
        f"- exclude_suspect: `{exclude_count}`",
        "",
        "## Family summary",
        "",
        markdown_table(family_summary_df, list(family_summary_df.columns)),
        "",
        "## Baseline teacher coverage vs recovered verified coverage",
        "",
        markdown_table(baseline_df, list(baseline_df.columns)),
        "",
        "## Top template buckets",
        "",
        markdown_table(template_df, list(template_df.columns), limit=20),
        "",
        "## Highest-priority manual audit rows",
        "",
        markdown_table(top_manual, list(top_manual.columns)),
        "",
    ]
    (reports_dir / "01_overview.md").write_text("\n".join(overview_lines) + "\n", encoding="utf-8")

    solver_lines = [
        f"# {SCRIPT_VERSION} hard-family findings",
        "",
        "## Binary",
        "",
        markdown_table(bit_df, list(bit_df.columns), limit=20),
        "",
        "## Text",
        "",
        markdown_table(text_df, list(text_df.columns), limit=20),
        "",
        "## Symbol",
        "",
        markdown_table(symbol_df, list(symbol_df.columns), limit=20),
        "",
    ]
    (reports_dir / "02_hard_family_findings.md").write_text("\n".join(solver_lines) + "\n", encoding="utf-8")

    curation_lines = [
        f"# {SCRIPT_VERSION} curation recommendations",
        "",
        "## Selection tier summary",
        "",
        markdown_table(selection_df, list(selection_df.columns)),
        "",
        "## Recommended data policy for the next `try-cuda-train.md` revision",
        "",
        "- `verified_trace_ready` は `<think> ... </think> \\boxed{}` の蒸留用コア学習データにする。",
        "- `answer_only_keep` は answer-only / terse-boxed 補助学習データに限定し、verified trace と混ぜる比率を抑える。",
        "- `manual_audit_priority` は family ごとに目視監査し、通過分だけ `verified_trace_ready` か `answer_only_keep` に昇格させる。",
        "- `exclude_suspect` は現時点では学習から外す。規則と答えが衝突しており、ラベル誤りや parser 想定外の可能性がある。",
        "",
    ]
    (reports_dir / "03_curation_recommendations.md").write_text("\n".join(curation_lines) + "\n", encoding="utf-8")

    text_lines = [
        f"# {SCRIPT_VERSION} text unknown-char notes",
        "",
        "## Text answer-completion summary",
        "",
        markdown_table(text_completion_df, list(text_completion_df.columns)),
        "",
        "## Remaining text manual-audit queue",
        "",
        markdown_table(
            text_manual_queue_df,
            ["id", "text_unknown_char_count", "text_unknown_chars", "hard_score", "answer", "query_raw"],
            limit=25,
        ),
        "",
        "Observation: all previously unresolved text rows are conflict-free monoalphabetic ciphers. They now move to `answer_only_keep` because the gold answer cleanly closes the missing 1-6 character mappings without contradicting any in-row examples.",
    ]
    (reports_dir / "06_text_unknown_notes.md").write_text("\n".join(text_lines) + "\n", encoding="utf-8")

    binary_lines = [
        f"# {SCRIPT_VERSION} binary cluster notes",
        "",
        "## Unresolved binary cluster summary",
        "",
        markdown_table(binary_cluster_df, list(binary_cluster_df.columns), limit=25),
        "",
        "## Top binary manual-audit queue",
        "",
        markdown_table(
            binary_manual_queue_df,
            ["id", "num_examples", "bit_simple_family", "bit_no_candidate_positions", "bit_multi_candidate_positions", "hard_score", "answer"],
            limit=25,
        ),
        "",
        "Observation: simple byte transforms (shift/rotate/mask) recover a small extra slice, but the dominant unresolved cluster still has no single-bit candidate on at least one output position, so the remaining rules likely need broader boolean/circuit families or richer non-local byte transforms.",
    ]
    (reports_dir / "07_binary_cluster_notes.md").write_text("\n".join(binary_lines) + "\n", encoding="utf-8")

    symbol_lines = [
        f"# {SCRIPT_VERSION} symbol operator audit notes",
        "",
        "## Symbol numeric operator summary",
        "",
        markdown_table(symbol_operator_df, list(symbol_operator_df.columns), limit=40),
        "",
        "## Glyph multiset summary",
        "",
        markdown_table(glyph_summary_df, list(glyph_summary_df.columns), limit=20),
        "",
        "## Top symbol manual-audit queue",
        "",
        markdown_table(
            symbol_manual_queue_df,
            ["id", "template_subtype", "symbol_query_operator", "symbol_same_operator_example_count", "hard_score", "answer", "query_raw"],
            limit=25,
        ),
        "",
        "Observation: `numeric_2x2` is not one template; it splits by operator, and some operators are already recoverable with row-local formula search while `glyph_len5` remains structurally unsolved.",
    ]
    (reports_dir / "08_symbol_operator_notes.md").write_text("\n".join(symbol_lines) + "\n", encoding="utf-8")

    pass1_summary = grouped_counts(manual_pass1_df, ["audit_focus", "family"], name="rows") if len(manual_pass1_df) else pd.DataFrame(columns=["audit_focus", "family", "rows"])
    pass1_lines = [
        f"# {SCRIPT_VERSION} manual pass1 pack",
        "",
        "## Pass1 pack summary",
        "",
        markdown_table(pass1_summary, list(pass1_summary.columns)),
        "",
        "## Top rows in pass1 pack",
        "",
        markdown_table(
            manual_pass1_df,
            ["audit_focus", "id", "family", "template_subtype", "hard_score", "answer", "query_raw"],
            limit=40,
        ),
        "",
        "Use `artifacts/manual_pass1_priority_pack_v1.csv` as the first human-review queue.",
    ]
    (reports_dir / "09_manual_pass1_pack.md").write_text("\n".join(pass1_lines) + "\n", encoding="utf-8")

    glyph_lines = [
        f"# {SCRIPT_VERSION} glyph order probe notes",
        "",
        "## Glyph summary",
        "",
        markdown_table(glyph_summary_df, list(glyph_summary_df.columns), limit=20),
        "",
        f"- `glyph_multiset_possible`: `{int((analysis_df['glyph_multiset_possible'] == True).sum())}` rows",
        f"- `glyph_multiset_possible && glyph_order_acyclic`: `{len(glyph_promising_df)}` rows",
        "",
        "Interpretation: these rows already admit both a multiset-style character contribution hypothesis and a globally consistent output ordering over symbols. They are the strongest `glyph_len5` manual-audit candidates because only mapping/order unification remains unresolved.",
        "",
        "## Top glyph order-compatible rows",
        "",
        markdown_table(
            glyph_promising_df,
            ["id", "hard_score", "answer", "query_raw", "audit_reasons"],
            limit=40,
        ),
        "",
    ]
    (reports_dir / "10_glyph_order_probe.md").write_text("\n".join(glyph_lines) + "\n", encoding="utf-8")

    latest_lines = [
        f"# {SCRIPT_VERSION} latest snapshot",
        "",
        f"- generated_at_utc: `{utc_now()}`",
        f"- verified_trace_ready: `{verified_count}`",
        f"- answer_only_keep: `{answer_only_count}`",
        f"- manual_audit_priority: `{manual_count}`",
        f"- exclude_suspect: `{exclude_count}`",
        "",
        "## Family summary",
        "",
        markdown_table(family_summary_df, list(family_summary_df.columns)),
        "",
        "## Current pass1 manual pack",
        "",
        markdown_table(pass1_summary, list(pass1_summary.columns)),
        "",
        "## Key changes in this snapshot",
        "",
        "- `text_decryption`: all 971 previously manual rows are now `answer_only_keep` via clean gold-answer completion of missing monoalphabetic mappings.",
        "- `bit_manipulation`: added simple byte-transform recovery (`shift`, `rotate`, `mask`) and recovered 11 extra verified rows; current pass1 also excludes 11 low-gap affine mismatches whose unique rule conflicts with the gold label.",
        "- `symbol_equation/numeric_2x2`: manual curation pass1 now covers exact prompt-backed rules (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`, `comp99_abs_diff_2d`), further shrinking the unresolved symbol-numeric queue.",
        f"- `symbol_equation/numeric_2x2`: `{len(symbol_query_only_rejection_df)}` query-only arithmetic lookalikes were rechecked; the remaining slice still stays manual (`{symbol_query_only_conflict_count}` same-op conflicts, `{symbol_query_only_ambiguous_count}` format ambiguities).",
        f"- `symbol_equation/glyph_len5`: 70 rows satisfy multiset mapping and 46 also satisfy a global output-order DAG, but exact examples-only rechecks still yield `0` unique query strings (`{glyph_exact_unseen_count}` query-unseen, `{glyph_exact_ambiguous_multiset_count}` ambiguous-multiset, `{glyph_exact_ambiguous_order_count}` ambiguous-order, `{glyph_exact_no_multiset_count}` no-multiset), so glyph rows stay manual.",
        "",
    ]
    (reports_dir / "11_latest_snapshot.md").write_text("\n".join(latest_lines) + "\n", encoding="utf-8")

    tail_lines = [
        f"# {SCRIPT_VERSION} symbol tail probes",
        "",
        "## Probe summary",
        "",
        markdown_table(symbol_tail_probe_df, list(symbol_tail_probe_df.columns)),
        "",
        "## Glyph rows whose query+gold pair still fits the coarse multiset+order model",
        "",
        markdown_table(
            glyph_query_consistent_df,
            ["id", "hard_score", "answer", "query_raw", "audit_reasons"],
            limit=20,
        ),
        "",
        "Interpretation: these glyph rows are still not promoted because the coarse model is not unique enough to trust as supervision, even when the gold answer keeps it self-consistent.",
        "",
    ]
    (reports_dir / "12_symbol_tail_probes.md").write_text("\n".join(tail_lines) + "\n", encoding="utf-8")

    promotion_summary_df = grouped_counts(
        symbol_string_promotion_df,
        ["selection_tier", "symbol_numeric_formula_name", "symbol_same_operator_example_count"],
        name="rows",
    ) if len(symbol_string_promotion_df) else pd.DataFrame(
        columns=["selection_tier", "symbol_numeric_formula_name", "symbol_same_operator_example_count", "rows"]
    )
    manual_curation_lines = [
        f"# {SCRIPT_VERSION} manual curation pass1",
        "",
        "## Current exact formula-backed symbol rows",
        "",
        markdown_table(promotion_summary_df, list(promotion_summary_df.columns)),
        "",
        "## Promoted symbol rows",
        "",
        markdown_table(
            symbol_string_promotion_df,
            ["id", "selection_tier", "symbol_query_operator", "symbol_numeric_formula_name", "symbol_same_operator_example_count", "answer", "query_raw"],
            limit=80,
        ),
        "",
        "## Binary rows now excluded",
        "",
        markdown_table(
            binary_affine_exclude_df,
            ["id", "answer", "auto_solver_predicted_answer", "bit_no_candidate_positions", "audit_reasons"],
            limit=20,
        ),
        "",
        "## Binary affine mismatch rows still kept manual",
        "",
        markdown_table(
            binary_affine_manual_df,
            ["id", "answer", "auto_solver_predicted_answer", "bit_no_candidate_positions", "audit_reasons"],
            limit=20,
        ),
        "",
        "## Glyph rows still kept manual",
        "",
        markdown_table(
            glyph_query_consistent_df,
            ["id", "hard_score", "answer", "query_raw", "audit_reasons"],
            limit=20,
        ),
        "",
        "Decision summary: current pass1 safely keeps only exact `numeric_2x2` prompt-backed rows (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`, `comp99_abs_diff_2d`) on the promotion list. Binary low-gap rows with unique affine rules that still contradict the gold answer now move to `exclude_suspect`; broader affine mismatches and glyph coarse-consistent rows stay manual.",
        "",
    ]
    (reports_dir / "13_manual_curation_pass1.md").write_text("\n".join(manual_curation_lines) + "\n", encoding="utf-8")

    binary_exclude_lines = [
        f"# {SCRIPT_VERSION} binary residual affine scan",
        "",
        "## Newly excluded low-gap affine mismatches",
        "",
        markdown_table(
            binary_affine_exclude_df,
            ["id", "num_examples", "answer", "auto_solver_predicted_answer", "bit_no_candidate_positions", "bit_multi_candidate_positions", "audit_reasons"],
            limit=40,
        ),
        "",
        "## Remaining affine mismatch rows kept manual",
        "",
        markdown_table(
            binary_affine_manual_df,
            ["id", "num_examples", "answer", "auto_solver_predicted_answer", "bit_no_candidate_positions", "bit_multi_candidate_positions", "audit_reasons"],
            limit=40,
        ),
        "",
        "Interpretation: rows move to `exclude_suspect` only when the affine solution is unique, no stricter solver family wins, the gap is low (`bit_no_candidate_positions <= 1`, `bit_multi_candidate_positions == 0`), and the affine answer still contradicts the gold label. More ambiguous affine mismatches remain manual.",
        "",
    ]
    (reports_dir / "15_binary_residual_affine_scan.md").write_text("\n".join(binary_exclude_lines) + "\n", encoding="utf-8")

    glyph_pass1_df = manual_pass1_df.loc[manual_pass1_df["audit_focus"] == "symbol_glyph_multiset"].copy() if len(manual_pass1_df) else pd.DataFrame()
    glyph_hold_lines = [
        f"# {SCRIPT_VERSION} glyph manual hold",
        "",
        "## Decision",
        "",
        f"- pass1 glyph rows reviewed: `{len(glyph_pass1_df)}`",
        f"- rows promoted: `0`",
        f"- rows newly excluded: `0`",
        "- decision: keep all glyph pass1 rows in `manual_audit_priority`.",
        "",
        "## Why they stay manual",
        "",
        "- every pass1 glyph row still carries `symbol_length_mismatch|symbol_solver_unverified`.",
        "- the strongest 5 rows in `glyph_query_consistent_v1.csv` only show that query+gold is compatible with the coarse multiset+order model; they do **not** make the model unique.",
        f"- exact examples-only enumeration under the same coarse model yields `0` unique query strings (`{glyph_exact_unseen_count}` query-unseen, `{glyph_exact_ambiguous_multiset_count}` ambiguous-multiset, `{glyph_exact_ambiguous_order_count}` ambiguous-order, `{glyph_exact_no_multiset_count}` no-multiset).",
        "- per `README.md`, leaderboard score is direct final-answer accuracy, so teaching non-unique glyph hypotheses is riskier than leaving these rows manual.",
        "",
        "## Glyph query-consistent rows",
        "",
        markdown_table(
            glyph_query_consistent_df,
            ["id", "hard_score", "answer", "query_raw", "audit_reasons"],
            limit=20,
        ),
        "",
        "## Top glyph pass1 rows",
        "",
        markdown_table(
            glyph_pass1_df,
            ["id", "hard_score", "answer", "query_raw", "audit_reasons"],
            limit=40,
        ),
        "",
        "Interpretation: even the best glyph candidates remain underdetermined. They are suitable for future human reasoning work, but not for safe automatic promotion or exclusion in the current pass.",
        "",
    ]
    (reports_dir / "16_glyph_manual_hold.md").write_text("\n".join(glyph_hold_lines) + "\n", encoding="utf-8")

    representative_rejection_df = symbol_query_only_rejection_df.loc[
        symbol_query_only_rejection_df["id"].isin(["08d8d7e1", "0641ef58", "094bf548", "224efda1"])
    ].copy() if len(symbol_query_only_rejection_df) else pd.DataFrame(
        columns=["id", "query_raw", "query_only_matching_families", "rejection_reason", "candidate_predictions", "prompt_example_lines"]
    )
    query_only_rejection_lines = [
        f"# {SCRIPT_VERSION} symbol query-only arithmetic rejection",
        "",
        "## Purpose",
        "",
        "Review manual `symbol_numeric_same_op` rows whose gold query answer superficially matches `x_plus_y`, `x_minus_y`, `abs_diff_2d`, or `comp99_abs_diff_2d`, and verify whether prompt evidence really makes them safe promotions.",
        "",
        "## Decision",
        "",
        f"- rows checked: `{len(symbol_query_only_rejection_df)}`",
        f"- `same_operator_examples_conflict`: `{symbol_query_only_conflict_count}`",
        f"- `query_format_ambiguous`: `{symbol_query_only_ambiguous_count}`",
        "- promoted rows: `0`",
        "- decision: keep all of these rows in `manual_audit_priority`.",
        "",
        "## Breakdown",
        "",
        markdown_table(symbol_query_only_rejection_summary_df, list(symbol_query_only_rejection_summary_df.columns)),
        "",
        "## Representative rows",
        "",
        markdown_table(
            representative_rejection_df,
            ["id", "query_raw", "query_only_matching_families", "rejection_reason", "candidate_predictions", "prompt_example_lines"],
            limit=10,
        ),
        "",
        "## Full rejected slice",
        "",
        markdown_table(
            symbol_query_only_rejection_df,
            ["id", "query_raw", "answer", "query_only_matching_families", "same_operator_example_count", "candidate_prediction_count", "rejection_reason"],
            limit=80,
        ),
        "",
        "Interpretation: these rows look temptingly recoverable if you only inspect the query answer, but that is not enough. Most rows contradict their same-operator examples outright; the rest still leave sign, zero-pad, or complement-formatting unresolved, so using the gold answer as a tie-break would be unsafe supervision under the `README.md` accuracy regime.",
        "",
    ]
    (reports_dir / "17_symbol_query_only_rejection.md").write_text("\n".join(query_only_rejection_lines) + "\n", encoding="utf-8")

    symbol_known_family_lines = [
        f"# {SCRIPT_VERSION} symbol known-family mimic audit",
        "",
        "## Purpose",
        "",
        "Collect the full union of query-only and known-family mimic rows so round2 can deprioritize these dead ends before operator-specific manual reading.",
        "",
        "## Scope",
        "",
        f"- total mimic-union rows: `{symbol_mimic_union_total}`",
        "- sources: report 17 high-shot arithmetic lookalikes + extra known-family / low-shot mimic rows",
        "",
        "## Breakdown",
        "",
        markdown_table(symbol_mimic_union_summary_df, list(symbol_mimic_union_summary_df.columns)),
        "",
        "## Source split",
        "",
        f"- report 17 rows: `{symbol_mimic_report17_count}`",
        f"- extra known-family rows (union minus report 17): `{symbol_mimic_known_count}`",
        "",
        "## Interpretation",
        "",
        "- high-shot rows can still be wrong because same-op examples conflict or leave format unresolved.",
        "- low-shot rows can still be wrong because one example is not enough to prove the intended format, even if the query answer looks familiar.",
        "- the union now also absorbs the new `comp99_abs_diff_2d` dead-end lookalikes, so excluding it from the round2 reading list keeps the residual cluster map focused on the true unknown core.",
        "",
    ]
    (reports_dir / "23_symbol_known_family_mimics.md").write_text("\n".join(symbol_known_family_lines) + "\n", encoding="utf-8")

    symbol_round2_lines = [
        f"# {SCRIPT_VERSION} symbol round2 cluster map",
        "",
        "## Purpose",
        "",
        "After pass1, exclude all manual rows whose query answer only mimics already-known simple families or already-rejected high-shot arithmetic lookalikes, then map the remaining `symbol_numeric_same_op` rows into operator-specific residual clusters for round2 manual reading.",
        "",
        "## Scope",
        "",
        f"- remaining post-mimic-exclusion `symbol_numeric_same_op` rows: `{symbol_round2_remaining_count}`",
        f"- excluded known/query-only mimic union: `{symbol_mimic_union_total}` rows",
        "- grouped by operator, answer length, operator-char embedding, and same-operator example count bucket.",
        "",
        "## Top clusters",
        "",
        markdown_table(symbol_round2_cluster_df.head(25).reset_index(drop=True), list(symbol_round2_cluster_df.columns)),
        "",
        "## Reading order",
        "",
        "1. `*` with 4-digit answers",
        "2. `+` with 3-digit answers",
        "3. `-` with 3-digit answers",
        "4. clusters whose answers embed the operator character",
        "",
        "## Notes",
        "",
        "- This map excludes the full union of report 17 plus the extra low-shot/known-family mimic slice.",
        "- The excluded union now removes many dead-end `abs_diff_2d` / `abs_diff_2d_op_suffix` / `comp99_abs_diff_2d` lookalikes before round2 starts.",
        "- Use the representative IDs as the first prompts to read when beginning round2 manual clustering.",
        "",
    ]
    (reports_dir / "20_symbol_round2_cluster_map.md").write_text("\n".join(symbol_round2_lines) + "\n", encoding="utf-8")

    comp99_recovery_lines = [
        f"# {SCRIPT_VERSION} symbol `comp99_abs_diff_2d` recovery",
        "",
        "## Purpose",
        "",
        "Recheck `numeric_2x2` rows whose same-operator examples support the exact two-digit complement family `99 - abs(x-y)`—either as plain zero-padded digits or as operator-prefixed zero-padded digits—and split safe promotions from unsafe lookalikes under the `README.md` accuracy-first metric.",
        "",
        "## Decision",
        "",
        f"- rows tagged with `comp99_abs_diff_2d`: `{len(comp99_family_df)}`",
        f"- promoted to `verified_trace_ready`: `{int((comp99_promoted_df['selection_tier'] == 'verified_trace_ready').sum()) if len(comp99_promoted_df) else 0}`",
        f"- promoted to `answer_only_keep`: `{int((comp99_promoted_df['selection_tier'] == 'answer_only_keep').sum()) if len(comp99_promoted_df) else 0}`",
        f"- still manual after exact recheck: `{len(comp99_manual_df)}`",
        f"- query-only conflicts already captured in report 17: `{len(comp99_query_only_rejection_df)}`",
        "",
        "## Breakdown",
        "",
        markdown_table(comp99_summary_df, list(comp99_summary_df.columns)),
        "",
        "## Promoted rows",
        "",
        markdown_table(
            comp99_promoted_df,
            ["id", "selection_tier", "symbol_query_operator", "symbol_same_operator_example_count", "answer", "query_raw"],
            limit=20,
        ),
        "",
        "## Manual rows that still do not qualify",
        "",
        markdown_table(
            comp99_manual_df,
            ["id", "symbol_same_operator_example_count", "answer", "query_raw", "auto_solver_predicted_answer", "audit_reasons"],
            limit=20,
        ),
        "",
        "## Query-only conflict rows",
        "",
        markdown_table(
            comp99_query_only_rejection_df,
            ["id", "query_raw", "answer", "same_operator_example_count", "rejection_reason"],
            limit=20,
        ),
        "",
        "Interpretation: `comp99_abs_diff_2d` is a real prompt-backed family, but only when the same-operator examples match it exactly. The family appears both as plain zero-padded digits and as operator-prefixed zero-padded digits, and it also creates many false positives in the query answer alone, so safe recovery requires exact example consistency rather than query-only fit; anything weaker stays manual.",
        "",
    ]
    (reports_dir / "31_symbol_comp99_abs_diff_recovery.md").write_text("\n".join(comp99_recovery_lines) + "\n", encoding="utf-8")

    glyph_exact_lines = [
        f"# {SCRIPT_VERSION} glyph exact coarse enumeration",
        "",
        "## Purpose",
        "",
        "Recheck the 46 round2 `glyph_len5` rows under the **strictest version of the current coarse glyph abstraction**: each input character either drops out or maps to exactly one output character, and output character order must be globally consistent with the example outputs.",
        "",
        "## Decision",
        "",
        f"- rows checked: `{len(glyph_exact_df)}`",
        f"- `query_has_unseen_chars`: `{glyph_exact_unseen_count}`",
        f"- `ambiguous_multiset`: `{glyph_exact_ambiguous_multiset_count}`",
        f"- `ambiguous_order`: `{glyph_exact_ambiguous_order_count}`",
        f"- `no_example_only_multiset`: `{glyph_exact_no_multiset_count}`",
        f"- `unique_string`: `{glyph_exact_unique_count}`",
        f"- gold-matching unique strings: `{glyph_exact_unique_gold_match_count}`",
        "- promoted rows: `0`",
        "- newly excluded rows: `0`",
        "",
        "## Breakdown",
        "",
        markdown_table(glyph_exact_summary_df, list(glyph_exact_summary_df.columns)),
        "",
        "## Non-trivial rows under the exact coarse model",
        "",
        markdown_table(
            glyph_exact_nontrivial_df,
            ["id", "exact_coarse_status", "answer", "predicted_answer", "query_raw", "predicted_multiset_json"],
            limit=30,
        ),
        "",
        "## Query rows with unseen symbols",
        "",
        markdown_table(
            glyph_exact_unseen_df,
            ["id", "answer", "query_raw", "glyph_query_unseen_chars"],
            limit=30,
        ),
        "",
        "Interpretation: even after strengthening the current glyph abstraction to an exact examples-only enumeration, the round2 glyph slice still yields **zero** safe recoveries. Most rows immediately fail because the query introduces symbols that never appear in the examples; the rest remain ambiguous or structurally inconsistent. Under the `README.md` accuracy metric, this is negative evidence against trusting the current coarse glyph family as supervision.",
        "",
    ]
    (reports_dir / "24_glyph_exact_coarse_scan.md").write_text("\n".join(glyph_exact_lines) + "\n", encoding="utf-8")


def run_analysis(repo_root: Path, out_root: Path) -> None:
    repo_root = repo_root.resolve()
    out_root = out_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    artifacts_dir = out_root / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    v1 = load_module("analysis_v1_train_module", repo_root / "versions" / "v1" / "code" / "train.py")

    train_df = pd.read_csv(repo_root / "data" / "train.csv")
    public_test_df = pd.read_csv(repo_root / "data" / "test.csv")
    metadata_df = v1.build_metadata_frame(train_df, public_test_df)
    manual_audit_seed_df = v1.build_manual_audit_frame(metadata_df)

    analysis_records = [analyze_row(v1, record) for record in metadata_df.to_dict(orient="records")]
    analysis_df = pd.DataFrame(analysis_records)
    analysis_df, structured_formula_support_df, structured_formula_abstract_support_df, structured_formula_candidate_df = apply_bit_structured_formula_promotions(analysis_df)
    analysis_df, structured_low_support_candidate_df = apply_bit_structured_low_support_answer_only_promotions(analysis_df)
    analysis_df, structured_support3_candidate_df = apply_bit_structured_support3_answer_only_promotions(analysis_df)
    analysis_df, symbol_operator_spec_support_df, symbol_operator_spec_candidate_df = apply_symbol_operator_consensus_promotions(analysis_df)
    analysis_df, symbol_minus_prefix_support_df, symbol_minus_prefix_candidate_df = apply_symbol_minus_prefix_subfamily_promotions(analysis_df)
    analysis_df, symbol_minus_direct_support_df, symbol_minus_direct_candidate_df = apply_symbol_minus_direct_plain_promotions(analysis_df)
    analysis_df, symbol_star_prefix_support_df, symbol_star_prefix_candidate_df = apply_symbol_star_prefix_if_negative_promotions(analysis_df)

    baseline_coverage = parse_baseline_teacher_table(repo_root / "try-cuda-train-result.md")
    family_summary_df = family_summary_table(analysis_df)
    baseline_df = baseline_recovery_table(analysis_df, baseline_coverage)
    template_df = grouped_counts(analysis_df, ["family", "template_subtype"], name="rows")
    selection_df = grouped_counts(analysis_df, ["selection_tier", "family"], name="rows")
    bit_df = grouped_counts(
        analysis_df.loc[analysis_df["family"] == "bit_manipulation"],
        [
            "template_subtype",
            "bit_simple_family",
            "bit_independent_unique",
            "bit_bijection_unique",
            "bit_boolean2_unique",
            "bit_boolean3_unique",
            "bit_affine_unique",
            "bit_byte_transform_unique",
            "bit_hybrid_consensus_ready",
            "selection_tier",
            "analysis_notes",
            "teacher_solver_candidate",
        ],
        name="rows",
    )
    text_df = grouped_counts(
        analysis_df.loc[analysis_df["family"] == "text_decryption"],
        ["template_subtype", "teacher_solver_candidate", "selection_tier", "analysis_notes"],
        name="rows",
    )
    symbol_df = grouped_counts(
        analysis_df.loc[analysis_df["family"] == "symbol_equation"],
        ["template_subtype", "teacher_solver_candidate", "selection_tier", "analysis_notes"],
        name="rows",
    )
    text_unknown_df = grouped_counts(
        analysis_df.loc[
            (analysis_df["family"] == "text_decryption") & (analysis_df["selection_tier"] == "manual_audit_priority")
        ],
        ["text_unknown_char_count"],
        name="rows",
    )
    text_completion_df = grouped_counts(
        analysis_df.loc[
            (analysis_df["family"] == "text_decryption") & (analysis_df["selection_tier"] == "answer_only_keep")
        ],
        ["text_unknown_char_count", "text_answer_completion_new_pair_count", "analysis_notes"],
        name="rows",
    )
    symbol_operator_df = grouped_counts(
        analysis_df.loc[analysis_df["family"] == "symbol_equation"],
        ["template_subtype", "symbol_query_operator", "selection_tier", "symbol_numeric_formula_name"],
        name="rows",
    )
    symbol_tail_probe_df, glyph_query_consistent_df = probe_symbol_tail_cases(analysis_df, v1)
    glyph_exact_df = enumerate_glyph_query_predictions(analysis_df, v1)
    symbol_string_promotion_df = (
        analysis_df.loc[
            (analysis_df["family"] == "symbol_equation")
            & (analysis_df["template_subtype"] == "numeric_2x2")
            & (analysis_df["symbol_numeric_formula_name"].isin(SYMBOL_PROMOTION_FORMULA_NAMES))
            & (analysis_df["selection_tier"].isin(["verified_trace_ready", "answer_only_keep"]))
        ]
        .sort_values(["selection_tier", "symbol_numeric_formula_name", "symbol_same_operator_example_count", "id"], ascending=[True, True, False, True])
        .reset_index(drop=True)
    )
    binary_affine_exclude_df = (
        analysis_df.loc[
            (analysis_df["family"] == "bit_manipulation")
            & (analysis_df["selection_tier"] == "exclude_suspect")
            & (analysis_df["bit_affine_unique"])
            & (~analysis_df["auto_solver_match"])
        ]
        .sort_values(["hard_score", "id"], ascending=[False, True])
        .reset_index(drop=True)
    )
    binary_affine_manual_df = (
        analysis_df.loc[
            (analysis_df["family"] == "bit_manipulation")
            & (analysis_df["selection_tier"] == "manual_audit_priority")
            & (analysis_df["bit_affine_unique"])
            & (~analysis_df["auto_solver_match"])
        ]
        .sort_values(["hard_score", "id"], ascending=[False, True])
        .reset_index(drop=True)
    )
    binary_hybrid_consensus_df = (
        analysis_df.loc[
            (analysis_df["family"] == "bit_manipulation")
            & (analysis_df["bit_hybrid_consensus_ready"])
        ]
        .sort_values(["selection_tier", "bit_hybrid_consensus_varset", "bit_hybrid_consensus_match_count", "id"], ascending=[True, True, False, True])
        .reset_index(drop=True)
    )
    binary_structured_formula_df = (
        structured_formula_candidate_df.sort_values(
            [
                "selection_tier",
                "bit_structured_formula_safe_support",
                "bit_structured_formula_name",
                "id",
            ],
            ascending=[True, False, True, True],
        ).reset_index(drop=True)
    )
    glyph_summary_df = grouped_counts(
        analysis_df.loc[
            (analysis_df["family"] == "symbol_equation") & (analysis_df["template_subtype"] == "glyph_len5")
        ],
        ["glyph_multiset_possible", "glyph_order_acyclic", "selection_tier"],
        name="rows",
    )
    binary_cluster_df = grouped_counts(
        analysis_df.loc[
            (analysis_df["family"] == "bit_manipulation") & (analysis_df["selection_tier"] == "manual_audit_priority")
        ],
        ["num_examples", "bit_simple_family", "bit_no_candidate_positions", "bit_multi_candidate_positions", "bit_boolean2_unique", "bit_boolean3_unique", "bit_affine_unique", "bit_byte_transform_unique"],
        name="rows",
    )
    text_manual_queue_df = (
        analysis_df.loc[
            (analysis_df["family"] == "text_decryption") & (analysis_df["selection_tier"] == "manual_audit_priority")
        ]
        .sort_values(["text_unknown_char_count", "hard_score", "id"], ascending=[True, False, True])
        .reset_index(drop=True)
    )
    symbol_manual_queue_df = (
        analysis_df.loc[
            (analysis_df["family"] == "symbol_equation") & (analysis_df["selection_tier"] == "manual_audit_priority")
        ]
        .sort_values(
            ["glyph_multiset_possible", "glyph_order_acyclic", "template_subtype", "symbol_same_operator_example_count", "hard_score", "id"],
            ascending=[False, False, True, False, False, True],
        )
        .reset_index(drop=True)
    )
    binary_manual_queue_df = (
        analysis_df.loc[
            (analysis_df["family"] == "bit_manipulation") & (analysis_df["selection_tier"] == "manual_audit_priority")
        ]
        .sort_values(
            ["bit_no_candidate_positions", "bit_multi_candidate_positions", "num_examples", "hard_score", "id"],
            ascending=[True, True, False, False, True],
        )
        .reset_index(drop=True)
    )
    text_pass1_df = text_manual_queue_df.loc[text_manual_queue_df["text_unknown_char_count"] <= 1].copy()
    text_pass1_df["audit_focus"] = "text_unknown_1"
    binary_pass1_df = binary_manual_queue_df.loc[binary_manual_queue_df["bit_no_candidate_positions"] <= 1].copy()
    binary_pass1_df["audit_focus"] = "binary_low_gap"
    symbol_pass1_df = symbol_manual_queue_df.loc[
        ((symbol_manual_queue_df["template_subtype"] == "numeric_2x2") & (symbol_manual_queue_df["symbol_same_operator_example_count"] >= 1))
        | (
            (symbol_manual_queue_df["template_subtype"] == "glyph_len5")
            & (symbol_manual_queue_df["glyph_multiset_possible"])
            & (symbol_manual_queue_df["glyph_order_acyclic"])
        )
    ].copy()
    symbol_pass1_df["audit_focus"] = symbol_pass1_df["template_subtype"].map(
        {
            "numeric_2x2": "symbol_numeric_same_op",
            "glyph_len5": "symbol_glyph_multiset",
        }
    ).fillna("symbol_manual")
    manual_pass1_df = (
        pd.concat([text_pass1_df, binary_pass1_df, symbol_pass1_df], ignore_index=True)
        .sort_values(["audit_focus", "hard_score", "id"], ascending=[True, False, True])
        .reset_index(drop=True)
    )
    prompt_by_id = dict(zip(train_df["id"].astype(str), train_df["prompt"].astype(str)))
    symbol_query_only_rejection_df = collect_symbol_query_only_arithmetic_rejections(manual_pass1_df, prompt_by_id)
    known_family_mimic_df = load_optional_dataframe(
        artifacts_dir / "remaining_symbol_known_family_mimics_v1.csv",
        [
            "id",
            "query_raw",
            "answer",
            "query_only_matching_families",
            "same_operator_example_count",
            "candidate_prediction_count",
            "candidate_predictions",
            "rejection_reason",
            "prompt_example_lines",
        ],
    )
    symbol_mimic_union_df = build_symbol_mimic_union(symbol_query_only_rejection_df, known_family_mimic_df)
    symbol_round2_cluster_df = build_symbol_round2_cluster_summary(analysis_df, symbol_mimic_union_df)

    write_dataframe(metadata_df, artifacts_dir / "train_metadata_rebuilt_v1.csv")
    write_dataframe(manual_audit_seed_df, artifacts_dir / "manual_audit_seed_v1.csv")
    write_dataframe(analysis_df, artifacts_dir / "train_row_analysis_v1.csv")
    write_dataframe(family_summary_df, artifacts_dir / "family_summary_v1.csv")
    write_dataframe(baseline_df, artifacts_dir / "teacher_coverage_recovery_v1.csv")
    write_dataframe(template_df, artifacts_dir / "template_summary_v1.csv")
    write_dataframe(selection_df, artifacts_dir / "selection_summary_v1.csv")
    write_dataframe(bit_df, artifacts_dir / "bit_solver_summary_v1.csv")
    write_dataframe(text_df, artifacts_dir / "text_solver_summary_v1.csv")
    write_dataframe(symbol_df, artifacts_dir / "symbol_solver_summary_v1.csv")
    write_dataframe(text_unknown_df, artifacts_dir / "text_unknown_summary_v1.csv")
    write_dataframe(text_completion_df, artifacts_dir / "text_answer_completion_summary_v1.csv")
    write_dataframe(symbol_operator_df, artifacts_dir / "symbol_operator_summary_v1.csv")
    write_dataframe(symbol_tail_probe_df, artifacts_dir / "symbol_tail_probe_summary_v1.csv")
    write_dataframe(symbol_string_promotion_df, artifacts_dir / "symbol_string_template_promotions_v1.csv")
    write_dataframe(glyph_query_consistent_df, artifacts_dir / "glyph_query_consistent_v1.csv")
    write_dataframe(glyph_exact_df, artifacts_dir / "glyph_exact_coarse_predictions_v1.csv")
    write_dataframe(binary_affine_exclude_df, artifacts_dir / "binary_affine_low_gap_exclude_v1.csv")
    write_dataframe(binary_affine_manual_df, artifacts_dir / "binary_affine_mismatch_candidates_v1.csv")
    write_dataframe(binary_hybrid_consensus_df, artifacts_dir / "binary_hybrid_consensus_candidates_v1.csv")
    write_dataframe(binary_structured_formula_df, artifacts_dir / "binary_structured_byte_formula_candidates_v1.csv")
    write_dataframe(structured_low_support_candidate_df, artifacts_dir / "binary_structured_byte_low_support_answer_only_candidates_v1.csv")
    write_dataframe(structured_support3_candidate_df, artifacts_dir / "binary_structured_byte_support3_answer_only_candidates_v1.csv")
    write_dataframe(structured_formula_support_df, artifacts_dir / "binary_structured_byte_formula_support_v1.csv")
    write_dataframe(structured_formula_abstract_support_df, artifacts_dir / "binary_structured_byte_abstract_support_v1.csv")
    write_dataframe(symbol_operator_spec_support_df, artifacts_dir / "symbol_operator_specific_formula_support_v1.csv")
    write_dataframe(symbol_operator_spec_candidate_df, artifacts_dir / "symbol_operator_specific_formula_candidates_v1.csv")
    write_dataframe(symbol_minus_prefix_support_df, artifacts_dir / "symbol_minus_prefix_subfamily_support_v1.csv")
    write_dataframe(symbol_minus_prefix_candidate_df, artifacts_dir / "symbol_minus_prefix_subfamily_candidates_v1.csv")
    write_dataframe(symbol_minus_direct_support_df, artifacts_dir / "symbol_minus_direct_plain_support_v1.csv")
    write_dataframe(symbol_minus_direct_candidate_df, artifacts_dir / "symbol_minus_direct_plain_candidates_v1.csv")
    write_dataframe(symbol_star_prefix_support_df, artifacts_dir / "symbol_star_prefix_if_negative_support_v1.csv")
    write_dataframe(symbol_star_prefix_candidate_df, artifacts_dir / "symbol_star_prefix_if_negative_candidates_v1.csv")
    write_dataframe(binary_cluster_df, artifacts_dir / "binary_cluster_summary_v1.csv")
    write_dataframe(glyph_summary_df, artifacts_dir / "glyph_multiset_summary_v1.csv")
    write_dataframe(symbol_query_only_rejection_df, artifacts_dir / "remaining_symbol_query_only_rejection_v1.csv")
    write_dataframe(symbol_mimic_union_df, artifacts_dir / "remaining_symbol_mimic_union_v1.csv")
    write_dataframe(symbol_round2_cluster_df, artifacts_dir / "symbol_round2_cluster_summary_v1.csv")
    write_dataframe(
        analysis_df.loc[analysis_df["selection_tier"] == "verified_trace_ready"].reset_index(drop=True),
        artifacts_dir / "train_verified_trace_ready_v1.csv",
    )
    write_dataframe(
        analysis_df.loc[analysis_df["selection_tier"] == "answer_only_keep"].reset_index(drop=True),
        artifacts_dir / "train_answer_only_keep_v1.csv",
    )
    write_dataframe(
        analysis_df.loc[analysis_df["selection_tier"] == "manual_audit_priority"].sort_values(["audit_priority_score", "hard_score", "id"], ascending=[False, False, True]).reset_index(drop=True),
        artifacts_dir / "train_manual_audit_priority_v1.csv",
    )
    write_dataframe(
        analysis_df.loc[analysis_df["selection_tier"] == "exclude_suspect"].reset_index(drop=True),
        artifacts_dir / "train_exclude_suspect_v1.csv",
    )
    write_dataframe(text_manual_queue_df, artifacts_dir / "text_manual_audit_queue_v1.csv")
    write_dataframe(symbol_manual_queue_df, artifacts_dir / "symbol_manual_audit_queue_v1.csv")
    write_dataframe(binary_manual_queue_df, artifacts_dir / "binary_manual_audit_queue_v1.csv")
    write_dataframe(manual_pass1_df, artifacts_dir / "manual_pass1_priority_pack_v1.csv")
    write_dataframe(
        analysis_df.loc[analysis_df["selection_tier"].isin(["verified_trace_ready", "answer_only_keep"])]
        .sort_values(["selection_tier", "family", "template_subtype", "id"], ascending=[True, True, True, True])
        .reset_index(drop=True),
        artifacts_dir / "train_recommended_learning_target_v1.csv",
    )

    build_reports(
        out_root,
        analysis_df,
        family_summary_df,
        baseline_df,
        template_df,
        selection_df,
        bit_df,
        text_df,
        symbol_df,
        text_unknown_df,
        text_completion_df,
        symbol_operator_df,
        symbol_tail_probe_df,
        symbol_string_promotion_df,
        glyph_query_consistent_df,
        glyph_exact_df,
        binary_affine_exclude_df,
        binary_affine_manual_df,
        binary_cluster_df,
        glyph_summary_df,
        text_manual_queue_df,
        symbol_manual_queue_df,
        binary_manual_queue_df,
        manual_pass1_df,
        symbol_query_only_rejection_df,
        symbol_mimic_union_df,
        symbol_round2_cluster_df,
    )

    manifest = {
        "script_version": SCRIPT_VERSION,
        "generated_at_utc": utc_now(),
        "repo_root": str(repo_root),
        "out_root": str(out_root),
        "row_count": int(len(analysis_df)),
        "selection_tier_counts": analysis_df["selection_tier"].value_counts().to_dict(),
        "files": sorted(
            str(path.relative_to(out_root))
            for path in out_root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        ),
    }
    (artifacts_dir / "analysis_manifest_v1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze train.csv for CUDA teacher-signal curation without training.")
    parser.add_argument("--repo-root", required=True, help="Repository root path")
    parser.add_argument("--out-root", required=True, help="Output workspace root path")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    run_analysis(Path(args.repo_root), Path(args.out_root))


if __name__ == "__main__":
    main()
