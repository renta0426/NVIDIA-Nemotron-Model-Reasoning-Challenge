from __future__ import annotations

import argparse
import inspect
import json
import math
import os
import random
import re
import shutil
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_CSV_PATH = REPO_ROOT / 'cuda-train-data-analysis-v1' / 'artifacts' / 'train_row_analysis_v1.csv'
DEFAULT_OUTPUT_ROOT = Path('/kaggle/working/nemotron_curated_lora')
DEFAULT_SUBMISSION_ZIP = Path('/kaggle/working/submission.zip')
OFFICIAL_BASE_MODEL_NAME = 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16'
KAGGLE_BASE_MODEL_SLUG = 'metric/nemotron-3-nano-30b-a3b-bf16/transformers/default'
SEED = 42
BOXED_INSTRUCTION = (
    'Please put your final answer inside `\\boxed{}`. '
    'For example: `\\boxed{your answer}`'
)
CURATED_TIERS = ('verified_trace_ready', 'answer_only_keep')
TARGET_MODULES = ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']
TIER_BASE_WEIGHTS = {
    'verified_trace_ready': 1.0,
    'answer_only_keep': 0.65,
}
ANSWER_SPAN_WEIGHTS = {
    'gravity_constant': 4.0,
    'unit_conversion': 4.0,
    'roman_numeral': 4.0,
    'bit_manipulation': 5.0,
    'symbol_equation': 6.0,
    'text_decryption': 3.0,
}
ROMAN_TABLE = (
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I'),
)
SYMBOL_QUERY_RE = re.compile(r'^(\d{2})([^A-Za-z0-9\s])(\d{2})$')
FINAL_ANSWER_PATTERNS = (
    re.compile(r'\\boxed\{([^}]*)\}'),
    re.compile(r'Final answer\s*[:：]\s*([^\n]+)', re.IGNORECASE),
)


@dataclass(frozen=True)
class ParsedExample:
    inp: str
    out: str


@dataclass(frozen=True)
class ParsedPrompt:
    family: str
    examples: tuple[ParsedExample, ...]
    query_raw: str | None
    estimated_ratio: float | None = None
    estimated_g: float | None = None
    roman_query_value: int | None = None
    bit_query_binary: str | None = None


class ListDataset:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self.rows[index]


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def seed_torch(torch: Any, seed: int) -> None:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True


def optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value)
    return text if text else None


def is_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {'1', 'true', 'yes', 'y'}


def safe_float(value: Any) -> float | None:
    text = optional_text(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def decimal_places(text: str) -> int:
    stripped = str(text).strip()
    if '.' not in stripped:
        return 0
    return len(stripped.split('.', 1)[1])


def median_or_none(values: Iterable[float]) -> float | None:
    seq = sorted(float(value) for value in values)
    if not seq:
        return None
    mid = len(seq) // 2
    if len(seq) % 2 == 1:
        return seq[mid]
    return 0.5 * (seq[mid - 1] + seq[mid])


def normalize_spaces(text: str) -> str:
    return ' '.join(str(text).split())


def normalize_answer(value: Any) -> str:
    return str(value).strip()


def answers_match(gold: Any, predicted: Any) -> bool:
    gold_text = normalize_answer(gold)
    pred_text = normalize_answer(predicted)
    try:
        return math.isclose(float(gold_text), float(pred_text), rel_tol=1e-2, abs_tol=1e-5)
    except ValueError:
        return gold_text.lower() == pred_text.lower()


def int_to_roman(value: int) -> str:
    remaining = int(value)
    parts: list[str] = []
    for number, symbol in ROMAN_TABLE:
        while remaining >= number:
            parts.append(symbol)
            remaining -= number
    return ''.join(parts)


def rotate_left_byte(value: int, shift: int) -> int:
    shift %= 8
    return (((value & 0xFF) << shift) & 0xFF) | ((value & 0xFF) >> (8 - shift))


def rotate_right_byte(value: int, shift: int) -> int:
    shift %= 8
    return ((value & 0xFF) >> shift) | (((value & 0xFF) << (8 - shift)) & 0xFF)


def reverse_byte_bits(value: int) -> int:
    return int(format(value & 0xFF, '08b')[::-1], 2)


def nibble_swap_byte(value: int) -> int:
    bits = format(value & 0xFF, '08b')
    return int(bits[4:] + bits[:4], 2)


def split_top_level_args(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return parts


def apply_unary_byte_transform(name: str, value: int) -> int:
    lowered = name.strip().lower()
    if lowered in {'identity', 'id'}:
        return value & 0xFF
    if lowered in {'not', 'invert'}:
        return (~value) & 0xFF
    if lowered in {'reverse', 'bit_reverse'}:
        return reverse_byte_bits(value)
    if lowered == 'nibble_swap':
        return nibble_swap_byte(value)
    if lowered.startswith('rol'):
        return rotate_left_byte(value, int(lowered[3:]))
    if lowered.startswith('ror'):
        return rotate_right_byte(value, int(lowered[3:]))
    if lowered.startswith('shl'):
        return ((value & 0xFF) << int(lowered[3:])) & 0xFF
    if lowered.startswith('shr'):
        return (value & 0xFF) >> int(lowered[3:])
    raise ValueError(f'unsupported byte transform: {name}')


def apply_byte_formula(formula_name: str, bit_text: str) -> str:
    value = int(bit_text, 2)
    lowered = formula_name.strip().lower()
    match = re.fullmatch(r'(xor|and|or)\((.+)\)', lowered)
    if match is None:
        return format(apply_unary_byte_transform(lowered, value), '08b')
    op_name, inner = match.groups()
    args = split_top_level_args(inner)
    if len(args) != 2:
        raise ValueError(f'unsupported structured formula: {formula_name}')
    left = int(apply_byte_formula(args[0], bit_text), 2)
    right = int(apply_byte_formula(args[1], bit_text), 2)
    if op_name == 'xor':
        result = left ^ right
    elif op_name == 'and':
        result = left & right
    else:
        result = left | right
    return format(result & 0xFF, '08b')


def humanize_unary_byte_transform(name: str) -> str:
    lowered = name.strip().lower()
    if lowered in {'identity', 'id'}:
        return 'the identity transform'
    if lowered in {'not', 'invert'}:
        return 'bitwise inversion'
    if lowered in {'reverse', 'bit_reverse'}:
        return 'bit reversal'
    if lowered == 'nibble_swap':
        return 'nibble swap'
    if lowered.startswith('rol'):
        return f'rotate left by {int(lowered[3:])}'
    if lowered.startswith('ror'):
        return f'rotate right by {int(lowered[3:])}'
    if lowered.startswith('shl'):
        return f'shift left by {int(lowered[3:])}'
    if lowered.startswith('shr'):
        return f'shift right by {int(lowered[3:])}'
    return lowered


def describe_byte_formula(formula_name: str) -> str:
    lowered = formula_name.strip().lower()
    match = re.fullmatch(r'(xor|and|or)\((.+)\)', lowered)
    if match is None:
        return humanize_unary_byte_transform(lowered)
    op_name, inner = match.groups()
    args = split_top_level_args(inner)
    if len(args) != 2:
        return lowered
    left = describe_byte_formula(args[0])
    right = describe_byte_formula(args[1])
    joiner = {'xor': 'XOR', 'and': 'AND', 'or': 'OR'}[op_name]
    return f'{left} {joiner} {right}'


def parse_roman_prompt(prompt: str) -> ParsedPrompt:
    examples = tuple(
        ParsedExample(match.group(1), match.group(2))
        for line in prompt.splitlines()
        if (match := re.fullmatch(r'(\d+)\s*->\s*([IVXLCDM]+)', line.strip())) is not None
    )
    query_match = re.search(r'write the number\s+(\d+)', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    return ParsedPrompt(
        family='roman_numeral',
        examples=examples,
        query_raw=query_raw,
        roman_query_value=int(query_raw) if query_raw else None,
    )


def parse_gravity_prompt(prompt: str) -> ParsedPrompt:
    pattern = re.compile(r'For t =\s*([0-9]+(?:\.[0-9]+)?)s, distance =\s*([0-9]+(?:\.[0-9]+)?)\s*m', re.IGNORECASE)
    examples = tuple(ParsedExample(match.group(1), match.group(2)) for match in pattern.finditer(prompt))
    query_match = re.search(r'falling distance for t =\s*([0-9]+(?:\.[0-9]+)?)s', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    estimated_g = median_or_none(
        [
            2.0 * float(example.out) / (float(example.inp) ** 2)
            for example in examples
            if float(example.inp) != 0.0
        ]
    )
    return ParsedPrompt(
        family='gravity_constant',
        examples=examples,
        query_raw=query_raw,
        estimated_g=estimated_g,
    )


def parse_unit_prompt(prompt: str) -> ParsedPrompt:
    pattern = re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*m becomes\s*([0-9]+(?:\.[0-9]+)?)', re.IGNORECASE)
    examples = tuple(ParsedExample(match.group(1), match.group(2)) for match in pattern.finditer(prompt))
    query_match = re.search(r'measurement:\s*([0-9]+(?:\.[0-9]+)?)\s*m', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    estimated_ratio = median_or_none(
        [
            float(example.out) / float(example.inp)
            for example in examples
            if float(example.inp) != 0.0
        ]
    )
    return ParsedPrompt(
        family='unit_conversion',
        examples=examples,
        query_raw=query_raw,
        estimated_ratio=estimated_ratio,
    )


def parse_bit_prompt(prompt: str) -> ParsedPrompt:
    examples = tuple(
        ParsedExample(match.group(1), match.group(2))
        for match in re.finditer(r'([01]{8})\s*->\s*([01]{8})', prompt)
    )
    query_match = re.search(r'output for:\s*([01]{8})', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    return ParsedPrompt(
        family='bit_manipulation',
        examples=examples,
        query_raw=query_raw,
        bit_query_binary=query_raw,
    )


def parse_text_prompt(prompt: str) -> ParsedPrompt:
    examples: list[ParsedExample] = []
    for line in prompt.splitlines():
        stripped = line.strip()
        if '->' not in stripped:
            continue
        left, right = stripped.split('->', 1)
        left = left.strip()
        right = right.strip()
        if left and right:
            examples.append(ParsedExample(left, right))
    query_match = re.search(r'decrypt the following text:\s*(.+)', prompt, re.IGNORECASE)
    query_raw = query_match.group(1).strip() if query_match else None
    return ParsedPrompt(
        family='text_decryption',
        examples=tuple(examples),
        query_raw=query_raw,
    )


def parse_symbol_prompt(prompt: str) -> ParsedPrompt:
    examples: list[ParsedExample] = []
    for line in prompt.splitlines():
        stripped = line.strip(' `')
        lowered = stripped.lower()
        if not stripped or 'examples:' in lowered or lowered.startswith('now,'):
            continue
        if '=' not in stripped:
            continue
        left, right = stripped.split('=', 1)
        left = left.strip(' `')
        right = right.strip(' `')
        if left and right:
            examples.append(ParsedExample(left, right))
    query_match = re.search(r'result for:\s*(.+)', prompt, re.IGNORECASE)
    if query_match is None:
        query_match = re.search(r'output for:\s*(.+)', prompt, re.IGNORECASE)
    query_raw = query_match.group(1).strip() if query_match else None
    return ParsedPrompt(
        family='symbol_equation',
        examples=tuple(examples),
        query_raw=query_raw,
    )


def parse_prompt(family: str, prompt: str) -> ParsedPrompt:
    if family == 'roman_numeral':
        return parse_roman_prompt(prompt)
    if family == 'gravity_constant':
        return parse_gravity_prompt(prompt)
    if family == 'unit_conversion':
        return parse_unit_prompt(prompt)
    if family == 'bit_manipulation':
        return parse_bit_prompt(prompt)
    if family == 'text_decryption':
        return parse_text_prompt(prompt)
    return parse_symbol_prompt(prompt)


def build_char_mapping(examples: Iterable[ParsedExample]) -> tuple[dict[str, str], bool]:
    mapping: dict[str, str] = {}
    reverse_mapping: dict[str, str] = {}
    consistent = True
    for example in examples:
        if len(example.inp) != len(example.out):
            consistent = False
            continue
        for src, dst in zip(example.inp, example.out):
            if src == ' ' and dst == ' ':
                continue
            if src == ' ' or dst == ' ':
                consistent = False
                continue
            if src in mapping and mapping[src] != dst:
                consistent = False
            else:
                mapping[src] = dst
            if dst in reverse_mapping and reverse_mapping[dst] != src:
                consistent = False
            else:
                reverse_mapping[dst] = src
    return mapping, consistent


def decode_with_mapping(text: str, mapping: dict[str, str]) -> str | None:
    decoded: list[str] = []
    for char in text:
        if char == ' ':
            decoded.append(char)
            continue
        if char not in mapping:
            return None
        decoded.append(mapping[char])
    return ''.join(decoded)


def format_mapping_preview(mapping: dict[str, str], limit: int = 6) -> str:
    preview = [f'{src}->{dst}' for src, dst in sorted(mapping.items())[:limit]]
    return ', '.join(preview)


def parse_symbol_query(query_raw: str | None) -> tuple[str, str, str] | None:
    if query_raw is None:
        return None
    match = SYMBOL_QUERY_RE.fullmatch(query_raw.strip())
    if match is None:
        return None
    return match.group(1), match.group(2), match.group(3)


def symbol_formula_description(formula_name: str) -> str:
    descriptions = {
        'concat_xy': 'concatenating x then y',
        'concat_yx': 'concatenating y then x',
        'x_minus_y': 'x - y',
        'x_plus_y': 'x + y',
        'x_plus_y_plus1': 'x + y + 1',
        'x_plus_y_minus1': 'x + y - 1',
        'x_mul_y': 'x * y',
        'x_mul_y_plus1': 'x * y + 1',
        'x_mul_y_minus1': 'x * y - 1',
        'abs_diff_2d': '|x - y|',
        'abs_diff_2d_op_suffix': '|x - y| with the operator kept as a suffix',
        'comp99_abs_diff_2d': '99 - |x - y|',
        'y_mod_x': 'y mod x',
        'x_mod_y': 'x mod y',
    }
    return descriptions.get(formula_name, formula_name)


def compute_symbol_core(formula_name: str, x_text: str, y_text: str) -> str | None:
    x_value = int(x_text)
    y_value = int(y_text)
    if formula_name == 'concat_xy':
        return f'{x_text}{y_text}'
    if formula_name == 'concat_yx':
        return f'{y_text}{x_text}'
    if formula_name == 'x_minus_y':
        return str(x_value - y_value)
    if formula_name == 'x_plus_y':
        return str(x_value + y_value)
    if formula_name == 'x_plus_y_plus1':
        return str(x_value + y_value + 1)
    if formula_name == 'x_plus_y_minus1':
        return str(x_value + y_value - 1)
    if formula_name == 'x_mul_y':
        return str(x_value * y_value)
    if formula_name == 'x_mul_y_plus1':
        return str((x_value * y_value) + 1)
    if formula_name == 'x_mul_y_minus1':
        return str((x_value * y_value) - 1)
    if formula_name == 'abs_diff_2d':
        return str(abs(x_value - y_value))
    if formula_name == 'abs_diff_2d_op_suffix':
        return str(abs(x_value - y_value))
    if formula_name == 'comp99_abs_diff_2d':
        return str(99 - abs(x_value - y_value))
    if formula_name == 'y_mod_x' and x_value != 0:
        return str(y_value % x_value)
    if formula_name == 'x_mod_y' and y_value != 0:
        return str(x_value % y_value)
    return None


def describe_symbol_style(answer: str, operator: str) -> str | None:
    if answer.startswith(operator):
        return f'keeping `{operator}` as a prefix'
    if answer.endswith(operator):
        return f'keeping `{operator}` as a suffix'
    core = answer.lstrip('-')
    if core.isdigit() and len(core) > 1 and core.startswith('0'):
        return 'keeping the zero-padded width from the examples'
    return None


def render_final_answer(answer: str, format_policy: str) -> str:
    if format_policy == 'final_answer':
        return f'Final answer: {answer}'
    return rf'\boxed{{{answer}}}'


def render_completion(lines: Iterable[str], answer: str, format_policy: str) -> str:
    body_lines = [normalize_spaces(line) for line in lines if normalize_spaces(line)]
    final_answer = render_final_answer(answer, format_policy)
    if body_lines:
        return '\n'.join(body_lines + ['</think>', final_answer])
    return '\n'.join(['</think>', final_answer])


def build_verified_completion(row: dict[str, Any], parsed: ParsedPrompt, format_policy: str) -> str:
    family = row['family']
    answer = normalize_answer(row['answer'])
    if family == 'roman_numeral' and parsed.roman_query_value is not None:
        roman = int_to_roman(parsed.roman_query_value)
        return render_completion(
            (
                'The examples use standard Roman numeral conversion.',
                f'Converting {parsed.roman_query_value} gives {roman}.',
            ),
            answer,
            format_policy,
        )
    if family == 'unit_conversion' and parsed.query_raw is not None:
        ratio = parsed.estimated_ratio
        if ratio is None:
            query_value = safe_float(parsed.query_raw)
            answer_value = safe_float(answer)
            if query_value not in {None, 0.0} and answer_value is not None:
                ratio = answer_value / query_value
        ratio_text = f'{ratio:.6g}' if ratio is not None else 'the same fixed factor'
        return render_completion(
            (
                'The examples show a fixed multiplicative unit conversion.',
                f'Apply the same factor ({ratio_text}) to {parsed.query_raw} m to get {answer}.',
            ),
            answer,
            format_policy,
        )
    if family == 'gravity_constant' and parsed.query_raw is not None:
        g_value = parsed.estimated_g
        if g_value is None:
            query_value = safe_float(parsed.query_raw)
            answer_value = safe_float(answer)
            if query_value not in {None, 0.0} and answer_value is not None:
                g_value = 2.0 * answer_value / (query_value ** 2)
        g_text = f'{g_value:.5g}' if g_value is not None else 'the same hidden g'
        return render_completion(
            (
                'The examples follow d = 0.5 * g * t^2 with a constant hidden g.',
                f'Using g ≈ {g_text} at t = {parsed.query_raw}s gives d = {answer} m.',
            ),
            answer,
            format_policy,
        )
    if family == 'text_decryption':
        mapping, consistent = build_char_mapping(parsed.examples)
        decoded = decode_with_mapping(parsed.query_raw or '', mapping)
        preview = format_mapping_preview(mapping)
        if consistent and decoded and answers_match(answer, decoded):
            return render_completion(
                (
                    'The examples define a consistent monoalphabetic substitution cipher.',
                    f'Using mappings such as {preview}, the query decodes to {answer}.',
                ),
                answer,
                format_policy,
            )
        return render_completion(
            (
                'The examples determine a consistent character substitution rule.',
                f'Applying it to the query yields {answer}.',
            ),
            answer,
            format_policy,
        )
    if family == 'bit_manipulation':
        formula_name = optional_text(row.get('bit_structured_formula_name'))
        query_bits = parsed.bit_query_binary or optional_text(row.get('bit_query_binary')) or 'the query byte'
        if formula_name:
            predicted = answer
            try:
                predicted = apply_byte_formula(formula_name, query_bits)
            except Exception:
                predicted = normalize_answer(row.get('auto_solver_predicted_answer') or answer)
            return render_completion(
                (
                    f'The examples fit the structured byte rule {describe_byte_formula(formula_name)}.',
                    f'Applying it to {query_bits} gives {predicted}.',
                ),
                answer,
                format_policy,
            )
        signature = optional_text(row.get('bit_candidate_signature'))
        solver = optional_text(row.get('teacher_solver_candidate')) or 'binary_exact_rule'
        solver_descriptions = {
            'binary_bit_permutation_bijection': 'copying fixed input bits to fixed output positions, optionally with inversion',
            'binary_bit_permutation_independent': 'choosing each output bit independently from stable input-bit evidence',
            'binary_affine_xor': 'an affine XOR rule over selected input bits',
            'binary_two_bit_boolean': 'a two-input boolean rule for each output bit',
            'binary_three_bit_boolean': 'a three-input boolean rule for each output bit',
            'binary_byte_transform': 'a single byte-level rotate/shift/mask transform',
        }
        detail = solver_descriptions.get(solver, 'an exact bit rule recovered from the examples')
        if signature:
            return render_completion(
                (
                    f'The examples recover {detail}.',
                    f'The recovered signature is {signature}, so the query maps to {answer}.',
                ),
                answer,
                format_policy,
            )
        return render_completion(
            (
                f'The examples recover {detail}.',
                f'Applying that rule to the query gives {answer}.',
            ),
            answer,
            format_policy,
        )
    if family == 'symbol_equation':
        formula_name = optional_text(row.get('symbol_numeric_formula_name'))
        parsed_query = parse_symbol_query(parsed.query_raw)
        if formula_name and parsed_query is not None:
            x_text, operator, y_text = parsed_query
            core = compute_symbol_core(formula_name, x_text, y_text)
            style = describe_symbol_style(answer, operator)
            second_line = f'Applying it to {x_text}{operator}{y_text} gives {answer}.'
            if core is not None and style:
                second_line = f'The core computation gives {core}, and the final string is {answer} while {style}.'
            elif core is not None:
                second_line = f'The core computation gives {core}, so the final string is {answer}.'
            return render_completion(
                (
                    f'For operator `{operator}`, the examples use {symbol_formula_description(formula_name)}.',
                    second_line,
                ),
                answer,
                format_policy,
            )
        return render_completion(
            (
                'The examples determine an exact operator-specific transformation.',
                f'Applying it to the query gives {answer}.',
            ),
            answer,
            format_policy,
        )
    return render_completion(
        (
            'The examples determine an exact transformation rule.',
            f'Applying it to the query gives {answer}.',
        ),
        answer,
        format_policy,
    )


def build_answer_only_completion(row: dict[str, Any], parsed: ParsedPrompt, format_policy: str) -> str:
    family = row['family']
    answer = normalize_answer(row['answer'])
    analysis_notes = optional_text(row.get('analysis_notes')) or ''
    if family == 'text_decryption':
        missing_pairs = int(safe_float(row.get('text_answer_completion_new_pair_count')) or safe_float(row.get('text_unknown_char_count')) or 0)
        pair_word = 'pair' if missing_pairs == 1 else 'pairs'
        return render_completion(
            (
                'The examples recover almost all of the substitution cipher.',
                f'Filling the remaining {missing_pairs} unseen letter {pair_word} consistently decodes the query to {answer}.',
            ),
            answer,
            format_policy,
        )
    if family == 'bit_manipulation':
        note_map = {
            'bit_hybrid_consensus': 'Several conservative bit hypotheses agree on the same final byte.',
            'bit_structured_low_support_answer_only': 'A thin zero-error structured-byte family still determines one final byte.',
            'bit_structured_byte_multi_consensus': 'Multiple safe structured-byte formulas agree on the same final byte.',
            'bit_structured_support3_answer_only': 'A narrow support=3 structured-byte family still determines one final byte.',
        }
        abstract_family = optional_text(row.get('bit_structured_formula_abstract_family'))
        line_two = f'Applying the agreed rule to the query gives {answer}.'
        if abstract_family:
            line_two = f'The matching family is `{abstract_family}`, and it resolves the query to {answer}.'
        return render_completion(
            (
                note_map.get(analysis_notes, 'A conservative bit consensus determines the final byte for the query.'),
                line_two,
            ),
            answer,
            format_policy,
        )
    if family == 'symbol_equation':
        formula_name = optional_text(row.get('symbol_numeric_formula_name'))
        parsed_query = parse_symbol_query(parsed.query_raw)
        first_line_map = {
            'symbol_numeric_formula_low_shot': 'The same-operator examples are low-shot, but they still narrow the query to one final string.',
            'symbol_operator_spec_consensus': 'Clean same-operator support points to one safe operator-specific rule.',
            'symbol_manual_prompt_exact_answer_only': 'A direct reread of the prompt makes the final query string clear even without a unique reusable trace.',
            'symbol_minus_prefix_subfamily': 'A zero-error minus subfamily fixes the final string for the query.',
            'symbol_minus_direct_plain_subfamily': 'A direct minus formatter matches the prompt and fixes the final string.',
            'symbol_star_prefix_if_negative_subfamily': 'A narrow star subfamily fixes the final string for the query.',
            'symbol_thin_support2_subfamily': 'A thin support-2 subfamily is still exact enough to fix the final string.',
        }
        second_line = f'Keeping the prompt style, the query resolves to {answer}.'
        if formula_name and parsed_query is not None:
            _, operator, _ = parsed_query
            second_line = (
                f'The candidate operator rule is {symbol_formula_description(formula_name)} for `{operator}`, '
                f'and the query resolves to {answer}.'
            )
        return render_completion(
            (
                first_line_map.get(analysis_notes, 'The prompt narrows the final string for the query even though the full trace stays conservative.'),
                second_line,
            ),
            answer,
            format_policy,
        )
    return render_completion(
        (
            'The examples narrow the correct transformation enough to fix the final answer.',
            f'Applying it to the query gives {answer}.',
        ),
        answer,
        format_policy,
    )


def build_completion_for_row(row: dict[str, Any], parsed: ParsedPrompt) -> tuple[str, str, str]:
    selection_tier = optional_text(row.get('selection_tier')) or 'manual_audit_priority'
    format_policy = 'boxed' if is_true(row.get('boxed_safe')) else 'final_answer'
    if selection_tier == 'verified_trace_ready':
        return build_verified_completion(row, parsed, format_policy), 'verified_trace', format_policy
    return build_answer_only_completion(row, parsed, format_policy), 'answer_only', format_policy


def compute_family_sample_factors(frame: pd.DataFrame) -> dict[str, float]:
    counts = frame['family'].value_counts().to_dict()
    if not counts:
        return {}
    max_count = max(counts.values())
    factors: dict[str, float] = {}
    for family, count in counts.items():
        factors[family] = round(min(2.5, math.sqrt(max_count / float(count))), 4)
    return factors


def maybe_limit_rows(frame: pd.DataFrame, max_rows: int | None, seed: int) -> pd.DataFrame:
    if max_rows is None or len(frame) <= max_rows:
        return frame.copy()
    return frame.sample(n=max_rows, random_state=seed).reset_index(drop=True)


def build_curated_record_frame(analysis_df: pd.DataFrame, *, max_rows: int | None, seed: int) -> pd.DataFrame:
    curated = analysis_df.loc[analysis_df['selection_tier'].isin(CURATED_TIERS)].copy().reset_index(drop=True)
    curated = maybe_limit_rows(curated, max_rows=max_rows, seed=seed)
    family_factors = compute_family_sample_factors(curated)
    records: list[dict[str, Any]] = []
    for row in curated.to_dict(orient='records'):
        family = optional_text(row.get('family')) or ''
        prompt = optional_text(row.get('prompt'))
        answer = optional_text(row.get('answer'))
        if prompt is None or answer is None or family == '':
            continue
        parsed = parse_prompt(family, prompt)
        completion, record_style, format_policy = build_completion_for_row(row, parsed)
        selection_tier = optional_text(row.get('selection_tier')) or 'manual_audit_priority'
        sample_weight = round(family_factors.get(family, 1.0) * TIER_BASE_WEIGHTS.get(selection_tier, 0.5), 4)
        records.append(
            {
                'id': optional_text(row.get('id')),
                'family': family,
                'selection_tier': selection_tier,
                'record_style': record_style,
                'format_policy': format_policy,
                'sample_weight': sample_weight,
                'prompt': prompt,
                'answer': answer,
                'completion': completion,
                'analysis_notes': optional_text(row.get('analysis_notes')) or '',
                'teacher_solver_candidate': optional_text(row.get('teacher_solver_candidate')) or '',
                'symbol_numeric_formula_name': optional_text(row.get('symbol_numeric_formula_name')) or '',
                'bit_structured_formula_name': optional_text(row.get('bit_structured_formula_name')) or '',
                'bit_structured_formula_abstract_family': optional_text(row.get('bit_structured_formula_abstract_family')) or '',
                'boxed_safe': is_true(row.get('boxed_safe')),
                'prompt_chars': len(prompt),
                'completion_chars': len(completion),
            }
        )
    return pd.DataFrame.from_records(records)


def stratified_split(frame: pd.DataFrame, valid_fraction: float, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    if frame.empty or valid_fraction <= 0.0:
        return frame.copy(), frame.iloc[0:0].copy()
    train_parts: list[pd.DataFrame] = []
    valid_parts: list[pd.DataFrame] = []
    for _, group in frame.groupby(['family', 'selection_tier'], sort=True, dropna=False):
        shuffled = group.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        if len(shuffled) == 1:
            train_parts.append(shuffled)
            continue
        valid_size = max(1, int(round(len(shuffled) * valid_fraction)))
        valid_size = min(valid_size, len(shuffled) - 1)
        valid_parts.append(shuffled.iloc[:valid_size].copy())
        train_parts.append(shuffled.iloc[valid_size:].copy())
    train_frame = pd.concat(train_parts, ignore_index=True) if train_parts else frame.iloc[0:0].copy()
    valid_frame = pd.concat(valid_parts, ignore_index=True) if valid_parts else frame.iloc[0:0].copy()
    return train_frame, valid_frame


def summarize_record_frame(frame: pd.DataFrame) -> dict[str, Any]:
    return {
        'rows': int(len(frame)),
        'family_counts': frame['family'].value_counts().sort_index().to_dict() if not frame.empty else {},
        'selection_counts': frame['selection_tier'].value_counts().sort_index().to_dict() if not frame.empty else {},
        'record_style_counts': frame['record_style'].value_counts().sort_index().to_dict() if not frame.empty else {},
        'format_policy_counts': frame['format_policy'].value_counts().sort_index().to_dict() if not frame.empty else {},
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, default=str) + '\n')


def build_jsonl_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient='records'):
        records.append(
            {
                'prompt': row['prompt'],
                'completion': row['completion'],
                'metadata': {
                    'id': row['id'],
                    'family': row['family'],
                    'selection_tier': row['selection_tier'],
                    'record_style': row['record_style'],
                    'format_policy': row['format_policy'],
                    'sample_weight': row['sample_weight'],
                    'analysis_notes': row['analysis_notes'],
                    'teacher_solver_candidate': row['teacher_solver_candidate'],
                },
            }
        )
    return records


def write_record_artifacts(output_root: Path, record_frame: pd.DataFrame, train_frame: pd.DataFrame, valid_frame: pd.DataFrame) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    write_json(
        output_root / 'curated_record_manifest.json',
        {
            'source_rows': int(len(record_frame)),
            'source_summary': summarize_record_frame(record_frame),
            'train_summary': summarize_record_frame(train_frame),
            'valid_summary': summarize_record_frame(valid_frame),
        },
    )
    preview_columns = [
        'id',
        'family',
        'selection_tier',
        'record_style',
        'format_policy',
        'sample_weight',
        'analysis_notes',
        'teacher_solver_candidate',
        'symbol_numeric_formula_name',
        'bit_structured_formula_name',
        'completion_chars',
    ]
    record_frame.loc[:, preview_columns].to_csv(output_root / 'curated_record_preview.csv', index=False)
    write_jsonl(output_root / 'train_records.jsonl', build_jsonl_records(train_frame))
    write_jsonl(output_root / 'valid_records.jsonl', build_jsonl_records(valid_frame))


def build_user_content(prompt: str) -> str:
    return f'{prompt.strip()}\n{BOXED_INSTRUCTION}'


def apply_chat_template_safe(tokenizer: Any, messages: list[dict[str, str]], *, add_generation_prompt: bool) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=True,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
        )
    except Exception:
        chunks = []
        for message in messages:
            chunks.append(f"{message['role'].upper()}:\n{message['content']}")
        if add_generation_prompt:
            chunks.append('ASSISTANT:\n')
        return '\n\n'.join(chunks)


def detect_final_line_span(text: str) -> tuple[int, int] | None:
    lines = list(re.finditer(r'[^\n]+', text))
    if not lines:
        return None
    return lines[-1].span()


def detect_final_answer_span(text: str) -> tuple[int, int] | None:
    for pattern in FINAL_ANSWER_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            return matches[-1].span(1)
    return detect_final_line_span(text)


def char_span_to_token_span(tokenizer: Any, text: str, span: tuple[int, int] | None) -> tuple[int, int] | None:
    if span is None:
        return None
    start_char, end_char = span
    start_tokens = len(tokenizer(text[:start_char], add_special_tokens=False)['input_ids'])
    end_tokens = len(tokenizer(text[:end_char], add_special_tokens=False)['input_ids'])
    return start_tokens, end_tokens


def compute_completion_token_weights(tokenizer: Any, completion: str, family: str, sample_weight: float) -> list[float]:
    token_ids = tokenizer(completion, add_special_tokens=False)['input_ids']
    weights = [float(sample_weight)] * len(token_ids)
    final_line_span = char_span_to_token_span(tokenizer, completion, detect_final_line_span(completion))
    answer_span = char_span_to_token_span(tokenizer, completion, detect_final_answer_span(completion))
    if final_line_span is not None:
        start, end = final_line_span
        for index in range(start, min(end, len(weights))):
            weights[index] = max(weights[index], float(sample_weight) * 1.5)
    answer_weight = float(sample_weight) * ANSWER_SPAN_WEIGHTS.get(family, 3.0)
    if answer_span is not None:
        start, end = answer_span
        for index in range(start, min(end, len(weights))):
            weights[index] = max(weights[index], answer_weight)
    return weights


def build_feature(tokenizer: Any, record: dict[str, Any], max_length: int) -> dict[str, Any] | None:
    messages = [
        {'role': 'user', 'content': build_user_content(record['prompt'])},
        {'role': 'assistant', 'content': record['completion']},
    ]
    full_text = apply_chat_template_safe(tokenizer, messages, add_generation_prompt=False)
    prefix_text = apply_chat_template_safe(tokenizer, messages[:1], add_generation_prompt=True)
    full_ids = tokenizer(full_text, add_special_tokens=False, truncation=True, max_length=max_length)['input_ids']
    prefix_ids = tokenizer(prefix_text, add_special_tokens=False, truncation=True, max_length=max_length)['input_ids']
    if len(full_ids) <= len(prefix_ids):
        return None
    assistant_ids = tokenizer(record['completion'], add_special_tokens=False)['input_ids']
    completion_weights = compute_completion_token_weights(
        tokenizer,
        record['completion'],
        record['family'],
        float(record['sample_weight']),
    )
    supervised_length = len(full_ids) - len(prefix_ids)
    if len(completion_weights) < supervised_length:
        pad_value = float(record['sample_weight'])
        completion_weights = completion_weights + [pad_value] * (supervised_length - len(completion_weights))
    else:
        completion_weights = completion_weights[:supervised_length]
    labels = [-100] * len(prefix_ids) + full_ids[len(prefix_ids):]
    token_weights = [0.0] * len(prefix_ids) + completion_weights
    return {
        'input_ids': full_ids,
        'attention_mask': [1] * len(full_ids),
        'labels': labels,
        'token_weights': token_weights,
        'metadata': {
            'id': record['id'],
            'family': record['family'],
            'selection_tier': record['selection_tier'],
            'assistant_tokens': len(assistant_ids),
        },
    }


def build_tokenized_rows(tokenizer: Any, frame: pd.DataFrame, max_length: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    dropped = 0
    total_tokens = 0
    total_supervised = 0
    for record in frame.to_dict(orient='records'):
        feature = build_feature(tokenizer, record, max_length=max_length)
        if feature is None:
            dropped += 1
            continue
        rows.append(feature)
        total_tokens += len(feature['input_ids'])
        total_supervised += sum(1 for label in feature['labels'] if label != -100)
    stats = {
        'rows': len(rows),
        'dropped': dropped,
        'total_tokens': total_tokens,
        'total_supervised_tokens': total_supervised,
        'avg_tokens': (total_tokens / len(rows)) if rows else 0.0,
        'avg_supervised_tokens': (total_supervised / len(rows)) if rows else 0.0,
    }
    return rows, stats


class CompletionOnlyCollator:
    def __init__(self, tokenizer: Any, pad_to_multiple_of: int = 8) -> None:
        self.tokenizer = tokenizer
        self.pad_to_multiple_of = pad_to_multiple_of

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        import torch

        batch = self.tokenizer.pad(
            [
                {
                    'input_ids': feature['input_ids'],
                    'attention_mask': feature['attention_mask'],
                }
                for feature in features
            ],
            padding=True,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors='pt',
        )
        max_len = int(batch['input_ids'].shape[1])
        labels: list[list[int]] = []
        token_weights: list[list[float]] = []
        for feature in features:
            label_row = list(feature['labels'])
            weight_row = list(feature['token_weights'])
            pad_len = max_len - len(label_row)
            labels.append(label_row + ([-100] * pad_len))
            token_weights.append(weight_row + ([0.0] * pad_len))
        batch['labels'] = torch.tensor(labels, dtype=torch.long)
        batch['token_weights'] = torch.tensor(token_weights, dtype=torch.float32)
        return batch


def load_training_libraries() -> dict[str, Any]:
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    try:
        from transformers import BitsAndBytesConfig
    except ImportError:
        BitsAndBytesConfig = None
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, EarlyStoppingCallback, Trainer, TrainingArguments

    return {
        'torch': torch,
        'AutoConfig': AutoConfig,
        'AutoModelForCausalLM': AutoModelForCausalLM,
        'AutoTokenizer': AutoTokenizer,
        'BitsAndBytesConfig': BitsAndBytesConfig,
        'EarlyStoppingCallback': EarlyStoppingCallback,
        'LoraConfig': LoraConfig,
        'Trainer': Trainer,
        'TrainingArguments': TrainingArguments,
        'get_peft_model': get_peft_model,
        'prepare_model_for_kbit_training': prepare_model_for_kbit_training,
    }


def patch_triton_runtime() -> None:
    src = '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell'
    dst = '/tmp/ptxas-blackwell'
    if not os.path.exists(src):
        return
    shutil.copy2(src, dst)
    os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    try:
        import triton.backends.nvidia as nv_backend
    except Exception:
        return
    src_bin = os.path.join(os.path.dirname(nv_backend.__file__), 'bin')
    dst_bin = '/tmp/triton_nvidia_bin'
    shutil.copytree(src_bin, dst_bin, dirs_exist_ok=True)
    for filename in os.listdir(dst_bin):
        path = os.path.join(dst_bin, filename)
        if os.path.isfile(path):
            os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    os.environ['TRITON_PTXAS_PATH'] = dst
    os.environ['TRITON_PTXAS_BLACKWELL_PATH'] = dst
    try:
        import triton.backends.nvidia.compiler as nv_compiler
        nv_compiler.get_ptxas_version = lambda arch: '12.0'
    except Exception:
        pass


def patch_nemotron_model(model: Any, torch: Any) -> None:
    try:
        module = inspect.getmodule(model.backbone.layers[0].mixer.__class__)
    except Exception:
        module = inspect.getmodule(model.__class__)
    if module is None:
        return
    if hasattr(module, 'is_fast_path_available'):
        module.is_fast_path_available = False
    for _, cls in vars(module).items():
        if not isinstance(cls, type) or not hasattr(cls, 'moe'):
            continue
        old_moe = cls.moe

        def new_moe(self: Any, hidden_states: Any, topk_indices: Any, topk_weights: Any, _old_moe: Any = old_moe) -> Any:
            topk_weights = topk_weights.to(hidden_states.dtype)
            return _old_moe(self, hidden_states, topk_indices, topk_weights)

        cls.moe = new_moe
    mlp_cls = getattr(module, 'NemotronHMLP', None)
    if mlp_cls is not None and hasattr(mlp_cls, 'forward'):
        old_forward = mlp_cls.forward

        def new_forward(self: Any, x: Any, _old_forward: Any = old_forward) -> Any:
            if (not torch.is_floating_point(x)) or x.dtype == torch.uint8:
                x = x.to(torch.bfloat16)
            return _old_forward(self, x)

        mlp_cls.forward = new_forward


def resolve_base_model(base_model: str | None) -> str:
    if base_model:
        return base_model
    env_value = os.getenv('NEMOTRON_BASE_MODEL')
    if env_value:
        return env_value
    try:
        import kagglehub
        return kagglehub.model_download(KAGGLE_BASE_MODEL_SLUG)
    except Exception:
        return OFFICIAL_BASE_MODEL_NAME


def load_model_and_tokenizer(args: argparse.Namespace, libs: dict[str, Any]) -> tuple[Any, Any]:
    torch = libs['torch']
    AutoConfig = libs['AutoConfig']
    AutoModelForCausalLM = libs['AutoModelForCausalLM']
    AutoTokenizer = libs['AutoTokenizer']
    BitsAndBytesConfig = libs['BitsAndBytesConfig']
    prepare_model_for_kbit_training = libs['prepare_model_for_kbit_training']
    LoraConfig = libs['LoraConfig']
    get_peft_model = libs['get_peft_model']

    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    patch_triton_runtime()

    base_model = resolve_base_model(args.base_model)
    print('BASE_MODEL:', base_model)
    config = AutoConfig.from_pretrained(
        base_model,
        trust_remote_code=True,
        local_files_only=args.local_files_only,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        base_model,
        config=config,
        trust_remote_code=True,
        local_files_only=args.local_files_only,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = 'right'

    model_kwargs: dict[str, Any] = {
        'config': config,
        'trust_remote_code': True,
        'local_files_only': args.local_files_only,
    }
    if args.quantization == '4bit':
        if BitsAndBytesConfig is None:
            raise RuntimeError('bitsandbytes / 4bit support is not available in this environment')
        model_kwargs['device_map'] = 'auto'
        model_kwargs['quantization_config'] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
    else:
        model_kwargs['torch_dtype'] = torch.bfloat16
        if torch.cuda.is_available():
            model_kwargs['device_map'] = {'': 0}
            model_kwargs['low_cpu_mem_usage'] = True
            model_kwargs['attn_implementation'] = 'sdpa'
    try:
        model = AutoModelForCausalLM.from_pretrained(base_model, **model_kwargs)
    except TypeError:
        model_kwargs.pop('attn_implementation', None)
        model = AutoModelForCausalLM.from_pretrained(base_model, **model_kwargs)

    patch_nemotron_model(model, torch)
    model.config.use_cache = False
    if args.quantization == '4bit':
        model = prepare_model_for_kbit_training(model)
    if hasattr(model, 'gradient_checkpointing_enable'):
        try:
            model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
        except TypeError:
            model.gradient_checkpointing_enable()
    if hasattr(model, 'enable_input_require_grads'):
        model.enable_input_require_grads()

    lora_kwargs: dict[str, Any] = {
        'r': args.lora_r,
        'lora_alpha': args.lora_alpha,
        'lora_dropout': args.lora_dropout,
        'bias': 'none',
        'task_type': 'CAUSAL_LM',
        'target_modules': TARGET_MODULES,
        'inference_mode': False,
    }
    if 'use_rslora' in inspect.signature(LoraConfig.__init__).parameters:
        lora_kwargs['use_rslora'] = True
    peft_config = LoraConfig(**lora_kwargs)
    model = get_peft_model(model, peft_config)
    for peft_entry in model.peft_config.values():
        peft_entry.base_model_name_or_path = OFFICIAL_BASE_MODEL_NAME
    try:
        model.print_trainable_parameters()
    except Exception:
        pass
    return model, tokenizer


def make_weighted_trainer(trainer_cls: Any, torch: Any) -> Any:
    class WeightedCompletionTrainer(trainer_cls):
        def compute_loss(self, model: Any, inputs: dict[str, Any], return_outputs: bool = False, num_items_in_batch: Any = None) -> Any:
            token_weights = inputs.pop('token_weights')
            labels = inputs['labels']
            outputs = model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])
            logits = outputs.logits
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            shift_weights = token_weights[..., 1:].contiguous().to(shift_logits.dtype)
            active_mask = shift_labels.ne(-100)
            safe_labels = shift_labels.masked_fill(~active_mask, 0)
            loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
            per_token = loss_fct(
                shift_logits.view(-1, shift_logits.size(-1)),
                safe_labels.view(-1),
            ).view_as(safe_labels)
            per_token = per_token * shift_weights * active_mask.to(shift_weights.dtype)
            denom = (shift_weights * active_mask.to(shift_weights.dtype)).sum().clamp(min=1e-6)
            loss = per_token.sum() / denom
            return (loss, outputs) if return_outputs else loss

    return WeightedCompletionTrainer


def build_training_arguments(args: argparse.Namespace, libs: dict[str, Any], output_root: Path, has_valid: bool) -> Any:
    TrainingArguments = libs['TrainingArguments']
    sig = inspect.signature(TrainingArguments.__init__).parameters
    kwargs: dict[str, Any] = {
        'output_dir': str(output_root / 'checkpoints'),
        'num_train_epochs': args.num_epochs,
        'learning_rate': args.learning_rate,
        'per_device_train_batch_size': args.per_device_train_batch_size,
        'per_device_eval_batch_size': args.per_device_eval_batch_size,
        'gradient_accumulation_steps': args.gradient_accumulation_steps,
        'logging_steps': args.logging_steps,
        'bf16': True,
        'fp16': False,
        'optim': 'paged_adamw_8bit' if args.quantization == '4bit' else 'adamw_torch',
        'lr_scheduler_type': 'cosine',
        'warmup_ratio': args.warmup_ratio,
        'weight_decay': 0.0,
        'max_grad_norm': 1.0,
        'gradient_checkpointing': True,
        'remove_unused_columns': False,
        'report_to': 'none',
        'dataloader_num_workers': args.dataloader_num_workers,
        'save_total_limit': 2,
        'seed': args.seed,
        'data_seed': args.seed,
    }
    eval_strategy_key = 'evaluation_strategy' if 'evaluation_strategy' in sig else 'eval_strategy'
    kwargs[eval_strategy_key] = 'epoch' if has_valid else 'no'
    kwargs['save_strategy'] = 'epoch'
    if has_valid:
        kwargs['load_best_model_at_end'] = True
        kwargs['metric_for_best_model'] = 'eval_loss'
        kwargs['greater_is_better'] = False
    return TrainingArguments(**kwargs)


def save_run_config(path: Path, args: argparse.Namespace, train_summary: dict[str, Any], valid_summary: dict[str, Any]) -> None:
    write_json(
        path,
        {
            'analysis_csv_path': str(args.analysis_csv_path),
            'output_root': str(args.output_root),
            'submission_zip': str(args.submission_zip),
            'base_model': args.base_model,
            'quantization': args.quantization,
            'num_epochs': args.num_epochs,
            'learning_rate': args.learning_rate,
            'max_length': args.max_length,
            'lora_r': args.lora_r,
            'lora_alpha': args.lora_alpha,
            'lora_dropout': args.lora_dropout,
            'gradient_accumulation_steps': args.gradient_accumulation_steps,
            'validation_fraction': args.validation_fraction,
            'train_summary': train_summary,
            'valid_summary': valid_summary,
        },
    )


def resolve_adapter_weight_path(adapter_dir: Path) -> Path:
    for name in ('adapter_model.safetensors', 'adapter_model.bin'):
        path = adapter_dir / name
        if path.exists():
            return path
    raise FileNotFoundError('adapter_model.safetensors or adapter_model.bin not found')


def package_adapter_dir(adapter_dir: Path, submission_zip: Path) -> dict[str, Any]:
    adapter_dir = Path(adapter_dir)
    submission_zip = Path(submission_zip)
    submission_zip.parent.mkdir(parents=True, exist_ok=True)
    adapter_config_path = adapter_dir / 'adapter_config.json'
    if not adapter_config_path.exists():
        raise FileNotFoundError('adapter_config.json not found')
    adapter_cfg = json.loads(adapter_config_path.read_text(encoding='utf-8'))
    rank_value = adapter_cfg.get('r', adapter_cfg.get('rank'))
    if rank_value is None or int(rank_value) > 32:
        raise ValueError(f'LoRA rank must be <= 32, got {rank_value}')
    if adapter_cfg.get('base_model_name_or_path') != OFFICIAL_BASE_MODEL_NAME:
        raise ValueError(
            'adapter_config.json must target the official BF16 Nemotron base model: '
            f"{adapter_cfg.get('base_model_name_or_path')}"
        )
    actual_modules = set(adapter_cfg.get('target_modules', []))
    if actual_modules != set(TARGET_MODULES):
        raise ValueError(f'Unexpected target_modules: {sorted(actual_modules)}')
    resolve_adapter_weight_path(adapter_dir)
    with zipfile.ZipFile(submission_zip, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in adapter_dir.rglob('*'):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(adapter_dir).as_posix())
    with zipfile.ZipFile(submission_zip, 'r') as archive:
        names = archive.namelist()
    return {'adapter_config': adapter_cfg, 'zip_contents': names}


def extract_final_answer(text: str | None) -> str:
    if text is None:
        return 'NOT_FOUND'
    boxed_matches = re.findall(r'\\boxed\{([^}]*)(?:\}|$)', text)
    if boxed_matches:
        non_empty = [match.strip() for match in boxed_matches if match.strip()]
        return non_empty[-1] if non_empty else boxed_matches[-1].strip()
    for pattern in (
        r'The final answer is:\s*([^\n]+)',
        r'Final answer is:\s*([^\n]+)',
        r'Final answer\s*[:：]\s*([^\n]+)',
        r'final answer\s*[:：]\s*([^\n]+)',
    ):
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1].strip()
    number_matches = re.findall(r'-?\d+(?:\.\d+)?', text)
    if number_matches:
        return number_matches[-1]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else 'NOT_FOUND'


def run_quick_eval(
    *,
    model: Any,
    tokenizer: Any,
    valid_frame: pd.DataFrame,
    output_root: Path,
    sample_count: int,
    max_new_tokens: int,
    seed: int,
) -> dict[str, Any]:
    import torch

    if valid_frame.empty or sample_count <= 0:
        return {'rows': 0, 'accuracy': None}
    sample = valid_frame.sample(n=min(sample_count, len(valid_frame)), random_state=seed).reset_index(drop=True)
    device = next(model.parameters()).device
    rows: list[dict[str, Any]] = []
    correct = 0
    model.config.use_cache = True
    for row in sample.to_dict(orient='records'):
        prompt_text = apply_chat_template_safe(
            tokenizer,
            [{'role': 'user', 'content': build_user_content(row['prompt'])}],
            add_generation_prompt=True,
        )
        inputs = tokenizer(prompt_text, return_tensors='pt').to(device)
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                do_sample=False,
                temperature=0.0,
                top_p=1.0,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
        raw_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
        prediction = extract_final_answer(raw_text)
        ok = answers_match(row['answer'], prediction)
        correct += int(ok)
        rows.append(
            {
                'id': row['id'],
                'family': row['family'],
                'answer': row['answer'],
                'prediction': prediction,
                'ok': ok,
                'raw_text': raw_text,
            }
        )
    accuracy = correct / len(rows)
    pd.DataFrame(rows).to_csv(output_root / 'quick_val_predictions.csv', index=False)
    metrics = {'rows': len(rows), 'accuracy': accuracy}
    write_json(output_root / 'quick_val_metrics.json', metrics)
    return metrics


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Curated Nemotron BF16/PEFT training script driven by cuda-train-data-analysis-v1 artifacts.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--analysis-csv-path', type=Path, default=DEFAULT_ANALYSIS_CSV_PATH)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--submission-zip', type=Path, default=DEFAULT_SUBMISSION_ZIP)
    parser.add_argument('--base-model', default=None)
    parser.add_argument('--local-files-only', action='store_true')
    parser.add_argument('--dry-run-dataset', action='store_true')
    parser.add_argument('--run-quick-eval', action='store_true')
    parser.add_argument('--quick-eval-samples', type=int, default=32)
    parser.add_argument('--quick-eval-max-new-tokens', type=int, default=7680)
    parser.add_argument('--quantization', choices=('bf16', '4bit'), default='bf16')
    parser.add_argument('--validation-fraction', type=float, default=0.05)
    parser.add_argument('--max-curated-rows', type=int, default=None)
    parser.add_argument('--max-length', type=int, default=1536)
    parser.add_argument('--num-epochs', type=float, default=2.0)
    parser.add_argument('--learning-rate', type=float, default=1e-4)
    parser.add_argument('--per-device-train-batch-size', type=int, default=1)
    parser.add_argument('--per-device-eval-batch-size', type=int, default=1)
    parser.add_argument('--gradient-accumulation-steps', type=int, default=8)
    parser.add_argument('--warmup-ratio', type=float, default=0.03)
    parser.add_argument('--dataloader-num-workers', type=int, default=2)
    parser.add_argument('--logging-steps', type=int, default=10)
    parser.add_argument('--lora-r', type=int, default=32)
    parser.add_argument('--lora-alpha', type=int, default=32)
    parser.add_argument('--lora-dropout', type=float, default=0.0)
    parser.add_argument('--seed', type=int, default=SEED)
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    seed_everything(args.seed)
    if not args.analysis_csv_path.exists():
        raise FileNotFoundError(f'analysis csv not found: {args.analysis_csv_path}')

    analysis_df = pd.read_csv(args.analysis_csv_path, low_memory=False)
    record_frame = build_curated_record_frame(analysis_df, max_rows=args.max_curated_rows, seed=args.seed)
    train_frame, valid_frame = stratified_split(record_frame, valid_fraction=args.validation_fraction, seed=args.seed)

    args.output_root.mkdir(parents=True, exist_ok=True)
    write_record_artifacts(args.output_root, record_frame, train_frame, valid_frame)
    save_run_config(
        args.output_root / 'run_config.json',
        args,
        summarize_record_frame(train_frame),
        summarize_record_frame(valid_frame),
    )
    print('Curated rows:', len(record_frame))
    print('Train rows  :', len(train_frame))
    print('Valid rows  :', len(valid_frame))
    print('Family counts:', summarize_record_frame(record_frame)['family_counts'])
    print('Tier counts  :', summarize_record_frame(record_frame)['selection_counts'])

    if args.dry_run_dataset:
        print('Dry-run complete. Dataset artifacts were written to', args.output_root)
        return

    libs = load_training_libraries()
    torch = libs['torch']
    seed_torch(torch, args.seed)
    model, tokenizer = load_model_and_tokenizer(args, libs)

    train_rows, train_stats = build_tokenized_rows(tokenizer, train_frame, max_length=args.max_length)
    valid_rows, valid_stats = build_tokenized_rows(tokenizer, valid_frame, max_length=args.max_length)
    write_json(
        args.output_root / 'tokenization_manifest.json',
        {
            'train': train_stats,
            'valid': valid_stats,
            'max_length': args.max_length,
        },
    )
    print('Tokenization stats:', {'train': train_stats, 'valid': valid_stats})

    train_dataset = ListDataset(train_rows)
    valid_dataset = ListDataset(valid_rows)
    collator = CompletionOnlyCollator(tokenizer)
    WeightedTrainer = make_weighted_trainer(libs['Trainer'], torch)
    training_args = build_training_arguments(args, libs, args.output_root, has_valid=bool(valid_rows))
    callbacks: list[Any] = []
    if valid_rows:
        callbacks.append(
            libs['EarlyStoppingCallback'](
                early_stopping_patience=2,
                early_stopping_threshold=0.001,
            )
        )
    trainer = WeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset if valid_rows else None,
        data_collator=collator,
        callbacks=callbacks,
    )
    print('Start training...')
    train_result = trainer.train()
    write_json(
        args.output_root / 'train_result.json',
        {
            'global_step': getattr(train_result, 'global_step', None),
            'metrics': getattr(train_result, 'metrics', {}),
        },
    )

    adapter_dir = args.output_root / 'adapter'
    adapter_dir.mkdir(parents=True, exist_ok=True)
    for peft_entry in trainer.model.peft_config.values():
        peft_entry.base_model_name_or_path = OFFICIAL_BASE_MODEL_NAME
    trainer.model.save_pretrained(adapter_dir, safe_serialization=True)
    packaged = package_adapter_dir(adapter_dir, args.submission_zip)
    write_json(
        args.output_root / 'submission_manifest.json',
        {
            'submission_zip': str(args.submission_zip),
            'zip_contents': packaged['zip_contents'],
            'adapter_config': packaged['adapter_config'],
        },
    )
    print('Submission ready:', args.submission_zip)

    if args.run_quick_eval:
        metrics = run_quick_eval(
            model=trainer.model,
            tokenizer=tokenizer,
            valid_frame=valid_frame,
            output_root=args.output_root,
            sample_count=args.quick_eval_samples,
            max_new_tokens=args.quick_eval_max_new_tokens,
            seed=args.seed,
        )
        print('Quick eval:', metrics)


if __name__ == '__main__':
    main()
