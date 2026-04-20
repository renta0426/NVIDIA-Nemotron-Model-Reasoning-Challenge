from __future__ import annotations

import argparse
import math
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import pandas as pd

try:
    import z3
except ImportError:
    z3 = None


ROOT = Path(__file__).resolve().parents[2]
DATA_CSV = ROOT / "data" / "train_with_classification.csv"
README_MD = ROOT / "README.md"
REPORT_MD = Path(__file__).with_name("analysis_report.md")

NUMERIC_LABELS = ["equation_numeric_guess", "equation_numeric_deduce"]
SYMBOLIC_LABELS = ["cryptarithm_guess", "cryptarithm_deduce"]
ALL_LABELS = SYMBOLIC_LABELS + NUMERIC_LABELS

NUMERIC_CANDIDATE_ORDER = [
    "cd+ab",
    "x+y",
    "x-y",
    "ab+cd",
    "x%y",
    "x*y",
    "op+(y-x)",
    "y%x",
    "y-x",
    "gcd",
    "op+(x-y)",
    "acbd",
    "(x-y)+op",
    "sum:ac_bd",
    "diff:ac_bd",
    "op+rdiff:ac_bd",
    "diff:ac_bd:strip0",
    "x//y",
    "rdiff:ac_bd",
    "rdiff:ac_bd:strip0",
    "ba",
    "sum:ab_cd:strip0",
    "dc",
    "cd",
    "(y-x)+op",
    "diff:ab_cd:strip0",
    "y//x",
    "sum:ac_bd:strip0",
]

NUMERIC_TEMPLATE_DESCRIPTION = {
    "cd+ab": "右2桁の後に左2桁を連結",
    "x+y": "2桁整数どうしの加算",
    "x-y": "左2桁から右2桁を減算",
    "ab+cd": "左2桁の後に右2桁を連結",
    "x%y": "左2桁 mod 右2桁",
    "x*y": "2桁整数どうしの乗算",
    "op+(y-x)": "演算子記号を前置し、右2桁-左2桁",
    "y%x": "右2桁 mod 左2桁",
    "y-x": "右2桁から左2桁を減算",
    "gcd": "2桁整数どうしの最大公約数",
    "op+(x-y)": "演算子記号を前置し、左2桁-右2桁",
    "acbd": "1桁目どうし、2桁目どうしを交互連結",
    "(x-y)+op": "左2桁-右2桁の後ろに演算子記号",
    "sum:ac_bd": "桁ごとの縦和を連結",
    "diff:ac_bd": "桁ごとの差を連結",
    "op+rdiff:ac_bd": "演算子記号 + 桁ごとの逆差を連結",
    "diff:ac_bd:strip0": "桁ごとの差を連結して 0 を除去",
    "x//y": "左2桁 // 右2桁",
    "rdiff:ac_bd": "桁ごとの逆差を連結",
    "rdiff:ac_bd:strip0": "桁ごとの逆差を連結して 0 を除去",
    "ba": "左2桁を反転",
    "sum:ab_cd:strip0": "左右それぞれの桁和を連結して 0 を除去",
    "dc": "右2桁を反転",
    "cd": "右2桁をそのまま出力",
    "(y-x)+op": "右2桁-左2桁の後ろに演算子記号",
    "diff:ab_cd:strip0": "左右それぞれの桁差を連結して 0 を除去",
    "y//x": "右2桁 // 左2桁",
    "sum:ac_bd:strip0": "桁ごとの縦和を連結して 0 を除去",
}

POSITION_NAME = {
    "0": "左1",
    "1": "左2",
    "2": "演算子",
    "3": "右1",
    "4": "右2",
    "N": "新記号",
}

CORE_STRUCT_FAMILIES: dict[str, list[int]] = {
    "drop_op": [0, 1, 3, 4],
    "swap_halves": [3, 4, 0, 1],
    "left": [0, 1],
    "right": [3, 4],
    "reverse_left": [1, 0],
    "reverse_right": [4, 3],
    "acbd": [0, 3, 1, 4],
    "adbc": [0, 4, 1, 3],
}

CORE_NUMERIC_FAMILIES: list[tuple[str, str, str]] = []
for _name in ["x+y", "x-y", "y-x", "abs(x-y)", "x*y", "x%y", "y%x", "x//y", "y//x"]:
    CORE_NUMERIC_FAMILIES.append((_name, "plain", _name))
for _name in ["x-y", "y-x", "abs(x-y)"]:
    CORE_NUMERIC_FAMILIES.append((f"op_prefix:{_name}", "op_prefix", _name))
    CORE_NUMERIC_FAMILIES.append((f"op_suffix:{_name}", "op_suffix", _name))
CORE_NUMERIC_FAMILIES.append(("op+abs(x-y)", "op_prefix", "abs(x-y)"))
CORE_NUMERIC_FAMILIES.append(("abs(x-y)+op", "op_suffix", "abs(x-y)"))

CORE_COMPOSITE_FAMILIES = [
    "concat|x+y|nat|y//x|nat|strip0",
    "concat|x|nat|y|nat|keep",
    "concat|x//y|pad2|x//y|nat|keep",
    "concat|x-y|nat|x//y|nat|strip0",
    "concat|x*y|nat|y//x|nat|strip0",
    "concat|y//x|nat|y//x|pad2|keep",
    "concat|x+y|nat|y//x|nat|keep",
    "concat|y|nat|x|nat|keep",
    "mix|x|nat|max:ac_bd|scalar_first",
    "mix|y//x|nat|sum:ac_bd:strip0|scalar_first",
    "mix|min:ac_bd:strip0|x|nat|pair_first",
    "mix|x+y|nat|diff:ac_bd:strip0|scalar_first",
    "mix|diff:ab_cd:swap|x//y|pad2|pair_first",
    "mix|prod:ad_bc:swap|x//y|pad2|pair_first",
    "mix|max:ac_bd:swap|x+y|nat|pair_first",
    "copymix|scalar|x+y|nat|c|expr_first",
    "copymix|scalar|x+y|nat|a|expr_first",
    "copymix|scalar|y//x|nat|a|expr_first",
    "copymix|generic|prod:ac_bd:strip0|plain|aa|copy_first",
    "copymix|scalar|x|nat|cc|expr_first",
    "copymix|generic|absdiff:ac_bd:swap|plain|da|expr_first",
    "copymix|scalar|x|nat|c|expr_first",
    "copymix|scalar|x+y|nat|dc|copy_first",
    "copymix|scalar|x|nat|cd|expr_first",
    "copymix|scalar|y|pad2|ba|expr_first",
    "mask|scalar|x+y|nat|NNc",
    "mask|scalar|x+y|nat|NNa",
    "mask|scalar|x+y|nat|cNN",
    "mask|scalar|x+y|nat|aNN",
    "mask|scalar|x+y|nat|NNca",
    "mask|scalar|x+y|nat|aNNc",
    "mask|scalar|x+y|nat|NaNc",
    "mask|scalar|y//x|nat|NNa",
    "mask|scalar|x|nat|NNc",
    "mask|generic|sum:ac_bd|plain|NNa",
    "mask|generic|diff:ac_bd|plain|NNa",
]

CORE_FAMILY_PRIORITY = [
    "drop_op",
    "swap_halves",
    "left",
    "right",
    "reverse_left",
    "reverse_right",
    "acbd",
    "adbc",
    "x+y",
    "x-y",
    "y-x",
    "abs(x-y)",
    "x*y",
    "x%y",
    "y%x",
    "x//y",
    "y//x",
    "op+abs(x-y)",
    "abs(x-y)+op",
    "sum:ac_bd",
    "sum:ac_bd:swap",
    "sum:ac_bd:strip0",
    "sum:ac_bd:strip0swap",
    "sum:ab_cd:strip0swap",
    "sum:ad_bc:strip0",
    "sum:ad_bc:strip0swap",
    "diff:ac_bd",
    "diff:ac_bd:strip0",
    "op+diff:ac_bd",
    "diff:ac_bd+op",
    "rdiff:ac_bd",
    "rdiff:ac_bd:strip0",
    "op+rdiff:ac_bd",
    "rdiff:ac_bd+op",
    "rdiff:ab_cd",
    "absdiff:ac_bd",
    "op+absdiff:ac_bd",
    "op+max:ad_bc",
    "min:ad_bc+op",
    "op_prefix:x-y",
    "op_prefix:y-x",
    "op_prefix:abs(x-y)",
    "op_suffix:x-y",
    "op_suffix:y-x",
    "op_suffix:abs(x-y)",
]


def core_effective_family_priority(include_composite_families: bool) -> list[str]:
    if not include_composite_families:
        return CORE_FAMILY_PRIORITY
    return [*CORE_FAMILY_PRIORITY, *CORE_COMPOSITE_FAMILIES]


def parse_prompt(prompt: str) -> tuple[list[tuple[str, str]], str]:
    body = prompt.split("Below are a few examples:\n", 1)[1]
    examples_part, target = body.split("\nNow, determine the result for: ", 1)
    examples = []
    for line in examples_part.strip().splitlines():
        left, right = line.split(" = ", 1)
        examples.append((left, right))
    return examples, target.strip()


def read_base_model_summary() -> list[str]:
    text = README_MD.read_text(encoding="utf-8")
    lines = []
    capture = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("Cryptarithm (Guess)"):
            capture = True
        if capture and line:
            lines.append(line)
        if capture and line.startswith("Numeral "):
            break
    return lines


def numeric_template_outputs(left: str) -> dict[str, str | None]:
    a, b, op, c, d = left
    ai, bi, ci, di = map(int, [a, b, c, d])
    x = int(a + b)
    y = int(c + d)
    outputs: dict[str, str | None] = {
        "ab": a + b,
        "ba": b + a,
        "cd": c + d,
        "dc": d + c,
        "ab+cd": a + b + c + d,
        "cd+ab": c + d + a + b,
        "acbd": a + c + b + d,
        "adbc": a + d + b + c,
        "x+y": str(x + y),
        "x-y": str(x - y),
        "y-x": str(y - x),
        "abs(x-y)": str(abs(x - y)),
        "x*y": str(x * y),
        "x//y": str(x // y) if y else None,
        "y//x": str(y // x) if x else None,
        "x%y": str(x % y) if y else None,
        "y%x": str(y % x) if x else None,
        "gcd": str(math.gcd(x, y)),
        "op+abs(x-y)": op + str(abs(x - y)),
        "abs(x-y)+op": str(abs(x - y)) + op,
        "op+(x-y)": op + str(x - y),
        "(x-y)+op": str(x - y) + op,
        "op+(y-x)": op + str(y - x),
        "(y-x)+op": str(y - x) + op,
    }
    pairings = {
        "ac_bd": ((ai, ci), (bi, di)),
        "ad_bc": ((ai, di), (bi, ci)),
        "ab_cd": ((ai, bi), (ci, di)),
        "cd_ab": ((ci, di), (ai, bi)),
    }
    functions = {
        "sum": lambda u, v: u + v,
        "diff": lambda u, v: u - v,
        "rdiff": lambda u, v: v - u,
        "absdiff": lambda u, v: abs(u - v),
        "prod": lambda u, v: u * v,
        "max": lambda u, v: max(u, v),
        "min": lambda u, v: min(u, v),
    }
    for pairing_name, pair_values in pairings.items():
        for func_name, func in functions.items():
            first = str(func(*pair_values[0]))
            second = str(func(*pair_values[1]))
            base_name = f"{func_name}:{pairing_name}"
            outputs[base_name] = first + second
            outputs[f"{base_name}:swap"] = second + first
            outputs[f"{base_name}:strip0"] = (first + second).replace("0", "")
            outputs[f"{base_name}:strip0swap"] = (second + first).replace("0", "")
            outputs[f"op+{base_name}"] = op + first + second
            outputs[f"{base_name}+op"] = first + second + op
    return outputs


def first_numeric_template(left: str, right: str) -> str | None:
    outputs = numeric_template_outputs(left)
    for candidate in NUMERIC_CANDIDATE_ORDER:
        if outputs.get(candidate) == right:
            return candidate
    return None


def relation_signature(left: str, right: str) -> str:
    mapping: dict[str, str] = {}
    next_id = 0
    left_pattern = []
    for ch in left:
        if ch not in mapping:
            mapping[ch] = str(next_id)
            next_id += 1
        left_pattern.append(mapping[ch])
    right_pattern = [mapping[ch] if ch in mapping else "N" for ch in right]
    return "".join(left_pattern) + "->" + "".join(right_pattern)


def describe_relation_signature(signature: str) -> str:
    left_pattern, right_pattern = signature.split("->", 1)
    left_desc = "左辺の重複パターン " + left_pattern
    if not right_pattern:
        return left_desc + " / 右辺は空"
    right_desc = " ".join(POSITION_NAME[ch] for ch in right_pattern)
    return f"{left_desc} / 右辺は {right_desc}"


def format_counter_lines(
    counter: Counter,
    sample_map: dict[str, list[str]] | None = None,
    limit: int = 10,
    total: int | None = None,
    value_label: str = "件",
    formatter=None,
) -> list[str]:
    lines = []
    for key, count in counter.most_common(limit):
        ratio = ""
        if total:
            ratio = f" ({count / total:.1%})"
        detail = formatter(key) if formatter else str(key)
        sample_text = ""
        if sample_map and key in sample_map:
            sample_text = f" / 例: {', '.join(sample_map[key][:3])}"
        lines.append(f"- {detail}: {count}{value_label}{ratio}{sample_text}")
    return lines


def add_sample(sample_map: dict[str, list[str]], key: str, sample_id: str) -> None:
    bucket = sample_map[key]
    if sample_id not in bucket and len(bucket) < 3:
        bucket.append(sample_id)


def analyze_numeric_label(df: pd.DataFrame, label: str) -> dict:
    rows = df[df["final_label"] == label]
    example_templates: Counter = Counter()
    operator_templates: Counter = Counter()
    prompt_coverage: Counter = Counter()
    example_samples: dict[str, list[str]] = defaultdict(list)
    operator_samples: dict[str, list[str]] = defaultdict(list)
    target_unseen_operator = 0
    total_examples = 0
    total_operator_groups = 0

    for _, row in rows.iterrows():
        examples, target = parse_prompt(row["prompt"])
        example_ops = [left[2] for left, _ in examples]
        if target[2] not in example_ops:
            target_unseen_operator += 1
        by_operator: dict[str, list[tuple[str, str]]] = defaultdict(list)
        covered_examples = 0
        for left, right in examples:
            total_examples += 1
            by_operator[left[2]].append((left, right))
            template = first_numeric_template(left, right) or "UNMATCHED"
            example_templates[template] += 1
            add_sample(example_samples, template, row["id"])
        for operator, pairs in by_operator.items():
            total_operator_groups += 1
            matched = None
            for candidate in NUMERIC_CANDIDATE_ORDER:
                if all(numeric_template_outputs(left).get(candidate) == right for left, right in pairs):
                    matched = candidate
                    covered_examples += len(pairs)
                    break
            key = matched or "UNMATCHED"
            operator_templates[key] += 1
            add_sample(operator_samples, key, row["id"])
        prompt_coverage[covered_examples] += 1

    return {
        "rows": len(rows),
        "target_unseen_operator": target_unseen_operator,
        "total_examples": total_examples,
        "total_operator_groups": total_operator_groups,
        "example_templates": example_templates,
        "operator_templates": operator_templates,
        "prompt_coverage": prompt_coverage,
        "example_samples": example_samples,
        "operator_samples": operator_samples,
    }


def analyze_symbolic_label(df: pd.DataFrame, label: str) -> dict:
    rows = df[df["final_label"] == label]
    symbol_inventory: Counter = Counter()
    stable_operator_groups: Counter = Counter()
    mixed_operator_groups: Counter = Counter()
    example_relations: Counter = Counter()
    stable_samples: dict[str, list[str]] = defaultdict(list)
    mixed_samples: dict[str, list[str]] = defaultdict(list)
    relation_samples: dict[str, list[str]] = defaultdict(list)
    target_unseen_operator = 0
    answer_in_example_inputs = 0
    answer_in_example_all = 0
    prompts_all_outputs_from_inputs = 0
    total_operator_groups = 0
    stable_group_count = 0
    mixed_group_count = 0

    for _, row in rows.iterrows():
        examples, target = parse_prompt(row["prompt"])
        ops = {target[2]}
        all_symbols = set(target)
        example_input_symbols = set()
        example_all_symbols = set()
        by_operator: dict[str, list[str]] = defaultdict(list)
        outputs_only_from_inputs = True

        for left, right in examples:
            relation = relation_signature(left, right)
            example_relations[relation] += 1
            add_sample(relation_samples, relation, row["id"])
            by_operator[left[2]].append(relation)
            ops.add(left[2])
            all_symbols.update(left)
            all_symbols.update(right)
            example_input_symbols.update(left)
            example_all_symbols.update(left)
            example_all_symbols.update(right)
            if Counter(right) - Counter(left):
                outputs_only_from_inputs = False
        if outputs_only_from_inputs:
            prompts_all_outputs_from_inputs += 1
        if target[2] not in {left[2] for left, _ in examples}:
            target_unseen_operator += 1
        if set(str(row["answer"])) <= example_input_symbols:
            answer_in_example_inputs += 1
        if set(str(row["answer"])) <= example_all_symbols:
            answer_in_example_all += 1

        symbol_inventory[(len(all_symbols), len(ops), len(all_symbols) - len(ops))] += 1

        for operator, signatures in by_operator.items():
            total_operator_groups += 1
            unique_signatures = tuple(sorted(set(signatures)))
            if len(unique_signatures) == 1:
                stable_group_count += 1
                key = unique_signatures[0]
                stable_operator_groups[key] += 1
                add_sample(stable_samples, key, row["id"])
            else:
                mixed_group_count += 1
                key = " | ".join(unique_signatures)
                mixed_operator_groups[key] += 1
                add_sample(mixed_samples, key, row["id"])

    return {
        "rows": len(rows),
        "target_unseen_operator": target_unseen_operator,
        "answer_in_example_inputs": answer_in_example_inputs,
        "answer_in_example_all": answer_in_example_all,
        "prompts_all_outputs_from_inputs": prompts_all_outputs_from_inputs,
        "total_operator_groups": total_operator_groups,
        "stable_group_count": stable_group_count,
        "mixed_group_count": mixed_group_count,
        "symbol_inventory": symbol_inventory,
        "stable_operator_groups": stable_operator_groups,
        "mixed_operator_groups": mixed_operator_groups,
        "example_relations": example_relations,
        "stable_samples": stable_samples,
        "mixed_samples": mixed_samples,
        "relation_samples": relation_samples,
    }


def core_numeric_expr(expr_name: str, x, y):
    if z3 is None:
        raise RuntimeError("z3 is not available")
    if expr_name == "x+y":
        return x + y
    if expr_name == "x-y":
        return x - y
    if expr_name == "y-x":
        return y - x
    if expr_name == "abs(x-y)":
        return z3.If(x >= y, x - y, y - x)
    if expr_name == "x*y":
        return x * y
    if expr_name == "x%y":
        return z3.If(y == 0, -999999, x % y)
    if expr_name == "y%x":
        return z3.If(x == 0, -999999, y % x)
    if expr_name == "x//y":
        return z3.If(y == 0, -999999, x / y)
    if expr_name == "y//x":
        return z3.If(x == 0, -999999, y / x)
    raise KeyError(expr_name)


def core_family_mode(family_name: str) -> tuple[str, str] | None:
    for name, mode, expr_name in CORE_NUMERIC_FAMILIES:
        if name == family_name:
            return mode, expr_name
    return None


def core_parse_generic_family(family_name: str) -> tuple[bool, bool, str, str, bool, bool] | None:
    prefix_op = family_name.startswith("op+")
    suffix_op = family_name.endswith("+op")
    core_name = family_name
    if prefix_op:
        core_name = core_name[3:]
    if suffix_op:
        core_name = core_name[:-3]
    parts = core_name.split(":")
    if len(parts) < 2:
        return None
    func_name = parts[0]
    pairing_name = parts[1]
    swap = False
    strip0 = False
    for flag in parts[2:]:
        if flag == "swap":
            swap = True
        elif flag == "strip0":
            strip0 = True
        elif flag == "strip0swap":
            strip0 = True
            swap = True
        else:
            return None
    return prefix_op, suffix_op, func_name, pairing_name, swap, strip0


def core_parse_scalar_concat_family(family_name: str) -> tuple[str, str, str, str, bool] | None:
    if not family_name.startswith("concat|"):
        return None
    parts = family_name.split("|")
    if len(parts) != 6:
        return None
    _, left_expr, left_mode, right_expr, right_mode, strip_flag = parts
    if left_mode not in {"nat", "pad2"} or right_mode not in {"nat", "pad2"}:
        return None
    if strip_flag not in {"keep", "strip0"}:
        return None
    return left_expr, left_mode, right_expr, right_mode, strip_flag == "strip0"


def core_parse_scalar_pair_family(family_name: str) -> tuple[str, str, str, str] | None:
    if not family_name.startswith("mix|"):
        return None
    parts = family_name.split("|")
    if len(parts) != 5:
        return None
    _, first_expr, second_expr, third_expr, order = parts
    if order not in {"scalar_first", "pair_first"}:
        return None
    if order == "scalar_first":
        scalar_expr, scalar_mode, pair_name = first_expr, second_expr, third_expr
    else:
        pair_name, scalar_expr, scalar_mode = first_expr, second_expr, third_expr
    if scalar_mode not in {"nat", "pad2"}:
        return None
    if core_parse_generic_family(pair_name) is None:
        return None
    return scalar_expr, scalar_mode, pair_name, order


def core_parse_copy_mix_family(family_name: str) -> tuple[str, str, str, str, str, str] | None:
    if not family_name.startswith("copymix|"):
        return None
    parts = family_name.split("|")
    if len(parts) != 6:
        return None
    _, expr_kind, expr_name, expr_mode, copy_spec, order = parts
    if order not in {"expr_first", "copy_first"}:
        return None
    if expr_kind not in {"scalar", "generic"}:
        return None
    if expr_kind == "scalar":
        if expr_mode not in {"nat", "pad2"}:
            return None
    elif expr_mode != "plain":
        return None
    if any(ch not in "abcd" for ch in copy_spec) or not copy_spec:
        return None
    if expr_kind == "generic" and core_parse_generic_family(expr_name) is None:
        return None
    return expr_kind, expr_name, expr_mode, copy_spec, order, family_name


def core_parse_mask_family(family_name: str) -> tuple[str, str, str, str] | None:
    if not family_name.startswith("mask|"):
        return None
    parts = family_name.split("|")
    if len(parts) != 5:
        return None
    _, expr_kind, expr_name, expr_mode, template = parts
    if expr_kind not in {"scalar", "generic"}:
        return None
    if expr_kind == "scalar":
        if expr_mode not in {"nat", "pad2"}:
            return None
    elif expr_mode != "plain":
        return None
    if not template or any(ch not in "Nabcdo" for ch in template):
        return None
    if expr_kind == "generic" and core_parse_generic_family(expr_name) is None:
        return None
    return expr_kind, expr_name, expr_mode, template


def core_operator_symbols(examples: list[tuple[str, str]], target: str) -> list[str]:
    return sorted({left[2] for left, _ in examples} | {target[2]})


def core_digit_symbols(examples: list[tuple[str, str]], target: str, operator_symbols: list[str]) -> list[str]:
    all_chars = set(target)
    for left, right in examples:
        all_chars.update(left)
        all_chars.update(right)
    return sorted(all_chars)


def core_family_compatible(
    family_name: str,
    operator_symbol: str,
    pairs: list[tuple[str, str]],
    operator_symbols: set[str],
) -> bool:
    if family_name in CORE_STRUCT_FAMILIES:
        idxs = CORE_STRUCT_FAMILIES[family_name]
        expected_length = len(idxs)
        if any(len(right) != expected_length for _, right in pairs):
            return False
        return all("".join(left[i] for i in idxs) == right for left, right in pairs)

    family_length_ranges = {
        "x+y": (1, 3),
        "x-y": (1, 3),
        "y-x": (1, 3),
        "abs(x-y)": (1, 2),
        "x*y": (1, 4),
        "x%y": (1, 2),
        "y%x": (1, 2),
        "x//y": (1, 2),
        "y//x": (1, 2),
        "op+abs(x-y)": (2, 3),
        "abs(x-y)+op": (2, 3),
        "op_prefix:x-y": (2, 4),
        "op_prefix:y-x": (2, 4),
        "op_prefix:abs(x-y)": (2, 3),
        "op_suffix:x-y": (2, 4),
        "op_suffix:y-x": (2, 4),
        "op_suffix:abs(x-y)": (2, 3),
    }
    mode_info = core_family_mode(family_name)
    generic_info = None if mode_info is not None else core_parse_generic_family(family_name)
    composite_info = None
    if mode_info is None and generic_info is None:
        composite_info = (
            core_parse_scalar_concat_family(family_name)
            or core_parse_scalar_pair_family(family_name)
            or core_parse_copy_mix_family(family_name)
            or core_parse_mask_family(family_name)
        )
    if mode_info is None and generic_info is None and composite_info is None:
        return False
    if family_name in family_length_ranges:
        min_length, max_length = family_length_ranges[family_name]
        if any(not (min_length <= len(right) <= max_length) for _, right in pairs):
            return False
    mode = mode_info[0] if mode_info is not None else ("op_prefix" if generic_info and generic_info[0] else "op_suffix" if generic_info and generic_info[1] else "plain")
    for _, right in pairs:
        if mode == "plain":
            continue
        elif mode == "op_prefix":
            if not right or right[0] != operator_symbol:
                return False
        elif mode == "op_suffix":
            if not right or right[-1] != operator_symbol:
                return False
    return True


def core_decimal_constraint_terms(number_expr, digit_chars: str, digit_vars: dict[str, object]) -> list[object]:
    if z3 is None:
        raise RuntimeError("z3 is not available")
    abs_num = z3.If(number_expr >= 0, number_expr, -number_expr)
    length = len(digit_chars)
    constraints: list[object] = []
    if length == 1:
        constraints.extend([abs_num >= 0, abs_num <= 9, digit_vars[digit_chars[0]] == abs_num])
    elif length == 2:
        constraints.extend(
            [
                abs_num >= 10,
                abs_num <= 99,
                digit_vars[digit_chars[0]] == abs_num / 10,
                digit_vars[digit_chars[1]] == abs_num % 10,
            ]
        )
    elif length == 3:
        constraints.extend(
            [
                abs_num >= 100,
                abs_num <= 999,
                digit_vars[digit_chars[0]] == abs_num / 100,
                digit_vars[digit_chars[1]] == (abs_num / 10) % 10,
                digit_vars[digit_chars[2]] == abs_num % 10,
            ]
        )
    elif length == 4:
        constraints.extend(
            [
                abs_num >= 1000,
                abs_num <= 9999,
                digit_vars[digit_chars[0]] == abs_num / 1000,
                digit_vars[digit_chars[1]] == (abs_num / 100) % 10,
                digit_vars[digit_chars[2]] == (abs_num / 10) % 10,
                digit_vars[digit_chars[3]] == abs_num % 10,
            ]
        )
    else:
        raise ValueError(f"unsupported digit length: {length}")
    return constraints


def core_join_symbol_maps(left_map: dict[str, str], right_map: dict[str, str]) -> dict[str, str] | None:
    merged = dict(left_map)
    reverse = {digit: symbol for symbol, digit in left_map.items()}
    for symbol, digit in right_map.items():
        if symbol in merged and merged[symbol] != digit:
            return None
        if symbol not in merged and digit in reverse and reverse[digit] != symbol:
            return None
        merged[symbol] = digit
        reverse[digit] = symbol
    return merged


def core_make_symbol_map(symbol_sequence: str, digit_sequence: str) -> dict[str, str] | None:
    mapping: dict[str, str] = {}
    used_digits: dict[str, str] = {}
    for symbol, digit in zip(symbol_sequence, digit_sequence):
        if symbol in mapping and mapping[symbol] != digit:
            return None
        if symbol not in mapping and digit in used_digits and used_digits[digit] != symbol:
            return None
        mapping[symbol] = digit
        used_digits[digit] = symbol
    return mapping


def core_eval_numeric_value(expr_name: str, x: int, y: int) -> int | None:
    if expr_name == "x":
        return x
    if expr_name == "y":
        return y
    if expr_name == "x+y":
        return x + y
    if expr_name == "x-y":
        return x - y
    if expr_name == "y-x":
        return y - x
    if expr_name == "abs(x-y)":
        return abs(x - y)
    if expr_name == "x*y":
        return x * y
    if expr_name == "x%y":
        return None if y == 0 else x % y
    if expr_name == "y%x":
        return None if x == 0 else y % x
    if expr_name == "x//y":
        return None if y == 0 else x // y
    if expr_name == "y//x":
        return None if x == 0 else y // x
    raise KeyError(expr_name)


def core_render_numeric_tokens(expr_name: str, x: int, y: int) -> list[tuple[str, str]] | None:
    value = core_eval_numeric_value(expr_name, x, y)
    if value is None:
        return None
    tokens: list[tuple[str, str]] = []
    if value < 0:
        tokens.append(("sign", "-"))
        value = -value
    for digit in str(value):
        tokens.append(("digit", digit))
    return tokens


def core_string_to_tokens(text: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    for char in text:
        if char == "-":
            tokens.append(("sign", "-"))
        else:
            tokens.append(("digit", char))
    return tokens


def core_render_scalar_text(expr_name: str, mode: str, x: int, y: int) -> str | None:
    value = core_eval_numeric_value(expr_name, x, y)
    if value is None:
        return None
    if mode == "nat":
        return str(value)
    if value < 0 or value > 99:
        return None
    return f"{value:02d}"


def core_render_pair_text(pair_name: str, x: int, y: int) -> str | None:
    tokens = core_render_generic_tokens(pair_name, "@", x, y)
    if tokens is None:
        return None
    if any(kind != "digit" for kind, _ in tokens):
        return None
    return "".join(value for _, value in tokens)


def core_render_copy_text(copy_spec: str, x: int, y: int) -> str:
    sx = f"{x:02d}"
    sy = f"{y:02d}"
    mapping = {"a": sx[0], "b": sx[1], "c": sy[0], "d": sy[1]}
    return "".join(mapping[ch] for ch in copy_spec)


def core_render_mask_tokens(
    expr_kind: str,
    expr_name: str,
    expr_mode: str,
    template: str,
    operator_symbol: str,
    x: int,
    y: int,
) -> list[tuple[str, str]] | None:
    if expr_kind == "scalar":
        expr_text = core_render_scalar_text(expr_name, expr_mode, x, y)
    else:
        expr_text = core_render_pair_text(expr_name, x, y)
    if expr_text is None or template.count("N") != len(expr_text):
        return None
    sx = f"{x:02d}"
    sy = f"{y:02d}"
    digit_mapping = {"a": sx[0], "b": sx[1], "c": sy[0], "d": sy[1]}
    tokens: list[tuple[str, str]] = []
    expr_index = 0
    for char in template:
        if char == "N":
            tokens.append(("digit", expr_text[expr_index]))
            expr_index += 1
        elif char == "o":
            tokens.append(("op", operator_symbol))
        else:
            tokens.append(("digit", digit_mapping[char]))
    return tokens


def core_render_composite_tokens(
    family_name: str,
    operator_symbol: str,
    x: int,
    y: int,
) -> list[tuple[str, str]] | None:
    scalar_concat = core_parse_scalar_concat_family(family_name)
    if scalar_concat is not None:
        left_expr, left_mode, right_expr, right_mode, strip0 = scalar_concat
        left_text = core_render_scalar_text(left_expr, left_mode, x, y)
        right_text = core_render_scalar_text(right_expr, right_mode, x, y)
        if left_text is None or right_text is None:
            return None
        text = left_text + right_text
        if strip0:
            text = text.replace("0", "")
        return core_string_to_tokens(text)

    scalar_pair = core_parse_scalar_pair_family(family_name)
    if scalar_pair is not None:
        scalar_expr, scalar_mode, pair_name, order = scalar_pair
        scalar_text = core_render_scalar_text(scalar_expr, scalar_mode, x, y)
        pair_text = core_render_pair_text(pair_name, x, y)
        if scalar_text is None or pair_text is None:
            return None
        text = scalar_text + pair_text if order == "scalar_first" else pair_text + scalar_text
        return core_string_to_tokens(text)

    copy_mix = core_parse_copy_mix_family(family_name)
    if copy_mix is not None:
        expr_kind, expr_name, expr_mode, copy_spec, order, _ = copy_mix
        if expr_kind == "scalar":
            expr_text = core_render_scalar_text(expr_name, expr_mode, x, y)
        else:
            expr_text = core_render_pair_text(expr_name, x, y)
        if expr_text is None:
            return None
        copy_text = core_render_copy_text(copy_spec, x, y)
        text = expr_text + copy_text if order == "expr_first" else copy_text + expr_text
        return core_string_to_tokens(text)

    mask_family = core_parse_mask_family(family_name)
    if mask_family is None:
        return None
    expr_kind, expr_name, expr_mode, template = mask_family
    return core_render_mask_tokens(expr_kind, expr_name, expr_mode, template, operator_symbol=operator_symbol, x=x, y=y)


def core_render_generic_tokens(family_name: str, operator_symbol: str, x: int, y: int) -> list[tuple[str, str]] | None:
    parsed = core_parse_generic_family(family_name)
    if parsed is None:
        return None
    prefix_op, suffix_op, func_name, pairing_name, swap, strip0 = parsed
    sx = f"{x:02d}"
    sy = f"{y:02d}"
    ai, bi, ci, di = map(int, [sx[0], sx[1], sy[0], sy[1]])
    pairings = {
        "ac_bd": ((ai, ci), (bi, di)),
        "ad_bc": ((ai, di), (bi, ci)),
        "ab_cd": ((ai, bi), (ci, di)),
        "cd_ab": ((ci, di), (ai, bi)),
    }
    functions = {
        "sum": lambda u, v: u + v,
        "diff": lambda u, v: u - v,
        "rdiff": lambda u, v: v - u,
        "absdiff": lambda u, v: abs(u - v),
        "prod": lambda u, v: u * v,
        "max": lambda u, v: max(u, v),
        "min": lambda u, v: min(u, v),
    }
    if pairing_name not in pairings or func_name not in functions:
        return None
    first_value = functions[func_name](*pairings[pairing_name][0])
    second_value = functions[func_name](*pairings[pairing_name][1])
    parts = [core_string_to_tokens(str(first_value)), core_string_to_tokens(str(second_value))]
    if swap:
        parts.reverse()
    tokens = [token for part in parts for token in part]
    if strip0:
        tokens = [token for token in tokens if not (token[0] == "digit" and token[1] == "0")]
    if prefix_op:
        tokens = [("op", operator_symbol), *tokens]
    if suffix_op:
        tokens = [*tokens, ("op", operator_symbol)]
    return tokens


@lru_cache(maxsize=None)
def core_family_records(family_name: str, operator_symbol: str) -> tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...]:
    records: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []
    mode_info = core_family_mode(family_name)
    for x in range(100):
        sx = f"{x:02d}"
        for y in range(100):
            sy = f"{y:02d}"
            if mode_info is not None:
                mode, expr_name = mode_info
                tokens = core_render_numeric_tokens(expr_name, x, y)
                if tokens is None:
                    continue
                if mode == "op_prefix":
                    tokens = [("op", operator_symbol), *tokens]
                elif mode == "op_suffix":
                    tokens = [*tokens, ("op", operator_symbol)]
            else:
                tokens = core_render_generic_tokens(family_name, operator_symbol, x, y)
                if tokens is None:
                    tokens = core_render_composite_tokens(family_name, operator_symbol, x, y)
                if tokens is None:
                    continue
            records.append((sx, sy, tuple(tokens)))
    return tuple(records)


def core_example_maps(family_name: str, left: str, right: str) -> list[dict[str, str]]:
    if family_name in CORE_STRUCT_FAMILIES:
        return [{}] if "".join(left[index] for index in CORE_STRUCT_FAMILIES[family_name]) == right else []

    local_maps: list[dict[str, str]] = []
    seen: set[tuple[tuple[str, str], ...]] = set()
    for sx, sy, tokens in core_family_records(family_name, left[2]):
        if len(tokens) != len(right):
            continue
        symbol_sequence = [left[0], left[1], left[3], left[4]]
        digit_sequence = [sx[0], sx[1], sy[0], sy[1]]
        valid = True
        for right_char, (token_kind, token_value) in zip(right, tokens):
            if token_kind == "digit":
                symbol_sequence.append(right_char)
                digit_sequence.append(token_value)
            elif token_kind in {"op", "sign"}:
                if right_char != token_value:
                    valid = False
                    break
            else:
                raise KeyError(token_kind)
        if not valid:
            continue
        symbol_map = core_make_symbol_map("".join(symbol_sequence), "".join(digit_sequence))
        if symbol_map is None:
            continue
        frozen = tuple(sorted(symbol_map.items()))
        if frozen in seen:
            continue
        seen.add(frozen)
        local_maps.append(symbol_map)
    return local_maps


def core_reduce_example_maps(example_maps: list[list[dict[str, str]]]) -> list[dict[str, str]]:
    if not example_maps:
        return [{}]
    merged_maps = example_maps[0]
    for next_maps in example_maps[1:]:
        merged_next: list[dict[str, str]] = []
        seen: set[tuple[tuple[str, str], ...]] = set()
        for current_map in merged_maps:
            for next_map in next_maps:
                merged = core_join_symbol_maps(current_map, next_map)
                if merged is None:
                    continue
                frozen = tuple(sorted(merged.items()))
                if frozen in seen:
                    continue
                seen.add(frozen)
                merged_next.append(merged)
        merged_maps = merged_next
        if not merged_maps:
            break
    return merged_maps


def core_add_output_constraints(
    solver,
    family_name: str,
    left: str,
    right: str,
    operator_symbols: set[str],
    digit_vars: dict[str, object],
) -> bool:
    if family_name in CORE_STRUCT_FAMILIES:
        return "".join(left[index] for index in CORE_STRUCT_FAMILIES[family_name]) == right

    mode_info = core_family_mode(family_name)
    if mode_info is None:
        return False
    mode, expr_name = mode_info
    a, b, _, c, d = left
    x = 10 * digit_vars[a] + digit_vars[b]
    y = 10 * digit_vars[c] + digit_vars[d]
    number_expr = core_numeric_expr(expr_name, x, y)

    if mode == "plain":
        branches = [(number_expr >= 0, right)]
        if right.startswith("-") and len(right) > 1:
            branches.append((number_expr < 0, right[1:]))
    elif mode == "op_prefix":
        if right[0] != left[2]:
            return False
        rest = right[1:]
        branches = [(number_expr >= 0, rest)]
        if rest.startswith("-") and len(rest) > 1:
            branches.append((number_expr < 0, rest[1:]))
    else:
        if right[-1] != left[2]:
            return False
        rest = right[:-1]
        branches = [(number_expr >= 0, rest)]
        if rest.startswith("-") and len(rest) > 1:
            branches.append((number_expr < 0, rest[1:]))

    branch_constraints = []
    for sign_condition, digit_part in branches:
        if not digit_part or any(ch not in digit_vars for ch in digit_part):
            continue
        branch_constraints.append(z3.And(sign_condition, *core_decimal_constraint_terms(number_expr, digit_part, digit_vars)))
    if not branch_constraints:
        return False
    solver.add(z3.Or(*branch_constraints))
    return True


def core_iter_family_assignments(family_options: dict[str, list[str]], max_assignments: int):
    ordered = sorted(family_options, key=lambda op: (len(family_options[op]), op))

    def recurse(index: int, current: dict[str, str]):
        if recurse.generated >= max_assignments:
            return
        if index == len(ordered):
            recurse.generated += 1
            yield current.copy()
            return
        operator_symbol = ordered[index]
        for family_name in family_options[operator_symbol]:
            current[operator_symbol] = family_name
            yield from recurse(index + 1, current)
            current.pop(operator_symbol)

    recurse.generated = 0
    yield from recurse(0, {})


def explain_symbol_row_with_core_solver(
    row,
    max_assignments: int = 512,
    family_priority: list[str] | None = None,
) -> dict | None:
    examples, target = parse_prompt(row["prompt"])
    operator_symbols = core_operator_symbols(examples, target)
    operator_symbol_set = set(operator_symbols)
    by_operator: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for left, right in examples:
        by_operator[left[2]].append((left, right))

    if family_priority is None:
        family_priority = CORE_FAMILY_PRIORITY

    family_options: dict[str, list[str]] = {}
    group_maps_by_operator: dict[str, dict[str, list[dict[str, str]]]] = {}
    for operator_symbol in operator_symbols:
        candidates: list[str] = []
        candidate_maps: dict[str, list[dict[str, str]]] = {}
        for family_name in family_priority:
            if not core_family_compatible(
                family_name,
                operator_symbol,
                by_operator.get(operator_symbol, []),
                operator_symbol_set,
            ):
                continue
            reduced_maps = core_reduce_example_maps(
                [core_example_maps(family_name, left, right) for left, right in by_operator.get(operator_symbol, [])]
            )
            if not reduced_maps:
                continue
            candidates.append(family_name)
            candidate_maps[family_name] = reduced_maps
        if not candidates:
            return None
        family_options[operator_symbol] = candidates
        group_maps_by_operator[operator_symbol] = candidate_maps

    target_answer = str(row["answer"])
    target_left = target

    ordered_operators = sorted(operator_symbols, key=lambda op: (len(family_options[op]), op))
    explored = 0

    def recurse(index: int, current_assignment: dict[str, str], current_map: dict[str, str]) -> dict | None:
        nonlocal explored
        if explored >= max_assignments:
            return None
        if index == len(ordered_operators):
            target_family = current_assignment[target_left[2]]
            target_maps = core_example_maps(target_family, target_left, target_answer)
            for target_map in target_maps:
                merged = core_join_symbol_maps(current_map, target_map)
                if merged is not None:
                    explored += 1
                    return {
                        "family_assignment": current_assignment.copy(),
                        "digit_symbols": sorted(merged),
                    }
            explored += 1
            return None

        operator_symbol = ordered_operators[index]
        for family_name in family_options[operator_symbol]:
            for family_map in group_maps_by_operator[operator_symbol][family_name]:
                merged_map = core_join_symbol_maps(current_map, family_map)
                if merged_map is None:
                    continue
                current_assignment[operator_symbol] = family_name
                result = recurse(index + 1, current_assignment, merged_map)
                if result is not None:
                    return result
                current_assignment.pop(operator_symbol)
        return None

    return recurse(0, {}, {})


def run_core_upper_bound(
    df: pd.DataFrame,
    limit: int | None,
    max_assignments: int,
    include_composite_families: bool,
) -> None:
    rows = df[df["final_label"].isin(SYMBOLIC_LABELS)]
    if limit is not None:
        rows = rows.head(limit)
    family_priority = core_effective_family_priority(include_composite_families)
    solved = 0
    by_label = Counter()
    for index, (_, row) in enumerate(rows.iterrows(), start=1):
        result = explain_symbol_row_with_core_solver(
            row,
            max_assignments=max_assignments,
            family_priority=family_priority,
        )
        if result is not None:
            solved += 1
            by_label[row["final_label"]] += 1
        if index % 25 == 0 or index == len(rows):
            print(
                f"progress {index}/{len(rows)} solved={solved} coverage={solved / len(rows):.1%}"
            )
    print("core upper bound solved", solved, "of", len(rows), f"({solved / len(rows):.1%})")
    print("by_label", dict(by_label))


def run_prompt_solver_train(
    df: pd.DataFrame,
    max_epochs: int,
    batch_size: int,
    learning_rate: float,
    seed: int,
) -> None:
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError as exc:
        raise RuntimeError("torch is required for --train-prompt-solver") from exc

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    rows = df[df["final_label"].isin(SYMBOLIC_LABELS)].reset_index(drop=True)
    prompts = rows["prompt"].astype(str).tolist()
    answers = rows["answer"].astype(str).tolist()
    chars = sorted(set("".join(prompts + answers)))
    char_to_idx = {char: index + 1 for index, char in enumerate(chars)}
    pad_idx = 0
    eos_idx = len(char_to_idx) + 1
    vocab_size = eos_idx + 1
    output_length = 5
    max_input_length = max(len(prompt) for prompt in prompts)

    def encode_prompt(text: str):
        encoded = torch.zeros(max_input_length, dtype=torch.long)
        values = [char_to_idx[char] for char in text]
        encoded[: len(values)] = torch.tensor(values, dtype=torch.long)
        return encoded

    def encode_answer(text: str):
        values = [char_to_idx[char] for char in text] + [eos_idx]
        values = values[:output_length] + [pad_idx] * max(0, output_length - len(values))
        return torch.tensor(values, dtype=torch.long)

    x_tensor = torch.stack([encode_prompt(prompt) for prompt in prompts])
    y_tensor = torch.stack([encode_answer(answer) for answer in answers])
    length_tensor = torch.tensor([len(prompt) for prompt in prompts], dtype=torch.long)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loader = DataLoader(TensorDataset(x_tensor, length_tensor, y_tensor), batch_size=batch_size, shuffle=True)

    class PromptSolver(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, 128, padding_idx=pad_idx)
            self.encoder = nn.GRU(
                128,
                256,
                batch_first=True,
                bidirectional=True,
                num_layers=2,
                dropout=0.1,
            )
            self.norm = nn.LayerNorm(512)
            self.head = nn.Sequential(
                nn.Linear(512, 512),
                nn.GELU(),
                nn.Linear(512, output_length * vocab_size),
            )

        def forward(self, inputs, lengths):
            embedded = self.embedding(inputs)
            packed = nn.utils.rnn.pack_padded_sequence(
                embedded,
                lengths.cpu(),
                batch_first=True,
                enforce_sorted=False,
            )
            _, hidden = self.encoder(packed)
            hidden = hidden.view(2, 2, inputs.size(0), 256)[-1]
            representation = torch.cat([hidden[0], hidden[1]], dim=-1)
            representation = self.norm(representation)
            logits = self.head(representation).view(inputs.size(0), output_length, vocab_size)
            return logits

    model = PromptSolver().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss(ignore_index=pad_idx)

    @torch.no_grad()
    def evaluate_exact() -> float:
        model.eval()
        logits = model(x_tensor.to(device), length_tensor.to(device))
        predictions = logits.argmax(dim=-1).cpu().tolist()
        exact = 0
        for predicted_tokens, gold_answer in zip(predictions, answers):
            decoded_chars: list[str] = []
            for token in predicted_tokens:
                if token in (pad_idx, eos_idx):
                    break
                decoded_chars.append(chars[token - 1])
            if "".join(decoded_chars) == gold_answer:
                exact += 1
        return exact / len(answers)

    print(
        "prompt_solver_train",
        {
            "rows": len(rows),
            "device": str(device),
            "vocab_size": vocab_size,
            "max_input_length": max_input_length,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "max_epochs": max_epochs,
            "seed": seed,
        },
    )

    best_exact = 0.0
    best_epoch = 0
    for epoch in range(1, max_epochs + 1):
        model.train()
        for batch_inputs, batch_lengths, batch_targets in loader:
            batch_inputs = batch_inputs.to(device)
            batch_lengths = batch_lengths.to(device)
            batch_targets = batch_targets.to(device)
            logits = model(batch_inputs, batch_lengths)
            loss = loss_fn(logits.reshape(-1, vocab_size), batch_targets.reshape(-1))
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        if epoch == 1 or epoch % 20 == 0:
            exact = evaluate_exact()
            if exact > best_exact:
                best_exact = exact
                best_epoch = epoch
            print(f"epoch={epoch} exact={exact:.4f} best={best_exact:.4f} best_epoch={best_epoch}")
            if exact >= 0.80:
                break

    print(f"prompt_solver_final best_exact={best_exact:.4f} best_epoch={best_epoch}")


def build_report(df: pd.DataFrame) -> str:
    numeric_results = {label: analyze_numeric_label(df, label) for label in NUMERIC_LABELS}
    symbolic_results = {label: analyze_symbolic_label(df, label) for label in SYMBOLIC_LABELS}
    base_model_lines = read_base_model_summary()
    total_rows = int(df[df["final_label"].isin(ALL_LABELS)].shape[0])

    lines: list[str] = []
    lines.append("# Symbol Rule Analysis (2026-04-20)")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- 参照データは README.md と data/train_with_classification.csv のみ")
    lines.append("- 対象ラベルは cryptarithm_guess, cryptarithm_deduce, equation_numeric_guess, equation_numeric_deduce")
    lines.append(f"- 対象総行数: {total_rows}")
    lines.append("- 目的は 4 分類をそのまま信じるのではなく、分類ごとの内部規則をより細かい規則族に分解すること")
    lines.append("")
    lines.append("## README Context")
    lines.append("")
    lines.append("README.md 末尾の base model 実測では、今回の 4 分類が他カテゴリより大きく苦戦しています。")
    lines.extend([f"- {line}" for line in base_model_lines])
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("- equation_numeric 系は『1 問 1 規則』ではなく、『1 問の中に 1〜3 個の演算子テンプレートが共存する』構造が強いです。")
    lines.append("- cryptarithm 系は単純な文字列遊びではなく、8〜10 個前後の digit-like symbol と 2〜3 個の operator-like symbol から成る、隠し記号化算術として見るのが妥当です。")
    lines.append("- 4 分類のままでは粗すぎます。少なくとも 直列連結型, 算術値型, 符号付き差分型, 桁別演算型, 未解決の複合型 に分けるのが実務的です。")
    lines.append("- cryptarithm_guess は『ターゲット記号やターゲット演算子が局所文脈に存在しない』ため、局所プロンプトだけではなく train 全体の族情報を使う前提で設計すべきです。")
    lines.append("")
    lines.append("## Numeric Labels")
    lines.append("")
    for label in NUMERIC_LABELS:
        result = numeric_results[label]
        resolved_examples = result["total_examples"] - result["example_templates"]["UNMATCHED"]
        resolved_operator_groups = result["total_operator_groups"] - result["operator_templates"]["UNMATCHED"]
        lines.append(f"### {label}")
        lines.append("")
        lines.append(f"- 行数: {result['rows']}")
        lines.append(f"- 例示行数合計: {result['total_examples']}")
        lines.append(f"- ターゲット演算子が例示に未登場: {result['target_unseen_operator']} 行")
        lines.append(f"- 小さな DSL で説明できた例示行: {resolved_examples} / {result['total_examples']} ({resolved_examples / result['total_examples']:.1%})")
        lines.append(f"- 小さな DSL で説明できた演算子グループ: {resolved_operator_groups} / {result['total_operator_groups']} ({resolved_operator_groups / result['total_operator_groups']:.1%})")
        lines.append("")
        lines.append("上位の例示行テンプレート")
        lines.extend(
            format_counter_lines(
                result["example_templates"],
                sample_map=result["example_samples"],
                limit=10,
                total=result["total_examples"],
                formatter=lambda key: f"{key} ({NUMERIC_TEMPLATE_DESCRIPTION.get(key, '未解釈')})",
            )
        )
        lines.append("")
        lines.append("上位の演算子グループテンプレート")
        lines.extend(
            format_counter_lines(
                result["operator_templates"],
                sample_map=result["operator_samples"],
                limit=10,
                total=result["total_operator_groups"],
                formatter=lambda key: f"{key} ({NUMERIC_TEMPLATE_DESCRIPTION.get(key, '未解釈')})",
            )
        )
        lines.append("")
        lines.append("問題単位で何本の例示行が説明できたか")
        lines.extend(
            format_counter_lines(
                result["prompt_coverage"],
                limit=8,
                total=result["rows"],
                value_label=" 問",
                formatter=lambda key: f"{key} 本の例示行を説明",
            )
        )
        lines.append("")
    lines.append("### Numeric Takeaway")
    lines.append("")
    lines.append("- equation_numeric_deduce は target operator が必ず例示内にある一方で、例示の大半はまだ DSL 未回収です。単純な加減乗除だけではなく、桁別処理や符号付与を含む複合テンプレートが残っています。")
    lines.append("- equation_numeric_guess は target operator が 136 / 136 行で未登場です。したがって solve には『この prompt がどのテンプレート族か』の prompt-level 推定が必要です。")
    lines.append("- ただし解釈済み部分だけでも、cd+ab, x-y, ab+cd, x+y, x*y, y%x, op+(y-x) が繰り返し現れます。numeric 系の母体生成器は少数 DSL の組み合わせと見てよいです。")
    lines.append("")
    lines.append("## Symbolic Labels")
    lines.append("")
    for label in SYMBOLIC_LABELS:
        result = symbolic_results[label]
        lines.append(f"### {label}")
        lines.append("")
        lines.append(f"- 行数: {result['rows']}")
        lines.append(f"- ターゲット演算子が例示に未登場: {result['target_unseen_operator']} 行")
        lines.append(f"- 答えの全記号が例示左辺だけで回収可能: {result['answer_in_example_inputs']} / {result['rows']} ({result['answer_in_example_inputs'] / result['rows']:.1%})")
        lines.append(f"- 答えの全記号が例示全体で回収可能: {result['answer_in_example_all']} / {result['rows']} ({result['answer_in_example_all'] / result['rows']:.1%})")
        lines.append(f"- すべての例示出力が入力記号のみで構成: {result['prompts_all_outputs_from_inputs']} / {result['rows']} ({result['prompts_all_outputs_from_inputs'] / result['rows']:.1%})")
        lines.append(f"- 演算子グループ stable: {result['stable_group_count']} / {result['total_operator_groups']} ({result['stable_group_count'] / result['total_operator_groups']:.1%})")
        lines.append(f"- 演算子グループ mixed: {result['mixed_group_count']} / {result['total_operator_groups']} ({result['mixed_group_count'] / result['total_operator_groups']:.1%})")
        lines.append("")
        lines.append("記号在庫の分布")
        lines.extend(
            format_counter_lines(
                result["symbol_inventory"],
                limit=8,
                total=result["rows"],
                value_label=" 問",
                formatter=lambda key: f"総記号 {key[0]}, 演算子 {key[1]}, digit-like {key[2]}",
            )
        )
        lines.append("")
        lines.append("上位の stable operator-group 署名")
        lines.extend(
            format_counter_lines(
                result["stable_operator_groups"],
                sample_map=result["stable_samples"],
                limit=10,
                total=result["total_operator_groups"],
                formatter=lambda key: f"{key} ({describe_relation_signature(key)})",
            )
        )
        lines.append("")
        lines.append("上位の example-level 署名")
        lines.extend(
            format_counter_lines(
                result["example_relations"],
                sample_map=result["relation_samples"],
                limit=10,
                total=sum(result["example_relations"].values()),
                formatter=lambda key: f"{key} ({describe_relation_signature(key)})",
            )
        )
        lines.append("")
    lines.append("### Symbolic Takeaway")
    lines.append("")
    lines.append("- cryptarithm 系の大半は『出力が入力の部分列』ではありません。新記号が頻繁に出るため、純粋な削除・並べ替え問題ではなく、記号化された数値出力と見るべきです。")
    lines.append("- 特に (総記号 13, 演算子 3, digit-like 10) が最多で、decimal-like な digit set と 3 演算子の組み合わせを強く示唆します。")
    lines.append("- stable 署名 01234->0134 は『演算子削除』、01234->3401 は『右2文字 + 左2文字』です。これは numeric 系の cd+ab / operator-ignore 族と対応します。")
    lines.append("- 一方で 01234->NN, 01234->NNN, 01234->2NN のような全新記号出力も多く、これは hidden digit system 上の加減乗除や剰余が結果側で新 digit を生む状況と整合します。")
    lines.append("")
    lines.append("## Recommended Refinement")
    lines.append("")
    lines.append("4 分類のままでは粗いので、少なくとも次の finer type へ分けるのがよいです。")
    lines.append("")
    lines.append("- concat_swap_family: 右2桁+左2桁、または右2記号+左2記号。numeric の cd+ab、symbolic の 01234->3401 が対応。")
    lines.append("- concat_drop_operator_family: 演算子を無視して残り4文字を返す族。symbolic の 01234->0134 が代表。")
    lines.append("- arithmetic_value_family: x+y, x-y, x*y, x%y, y%x などの値そのものを返す族。symbolic では NN, NNN, NNNN が対応。")
    lines.append("- signed_difference_family: op+(y-x), op+(x-y), (x-y)+op など、演算子を結果へ埋め込む族。")
    lines.append("- digitwise_family: sum:ac_bd, diff:ac_bd, diff:ac_bd:strip0 のような桁別処理族。")
    lines.append("- unresolved_composite_family: 上記 DSL でまだ拾えない複合規則。numeric_deduce に特に多いです。")
    lines.append("")
    lines.append("## Bottom Line")
    lines.append("")
    lines.append("- equation_numeric_guess / deduce は、演算子ごとにテンプレートを割り当てる DSL 問題です。")
    lines.append("- cryptarithm_guess / deduce は、その DSL を数字ではなく記号化 digit system 上で出している問題です。")
    lines.append("- guess 系は unseen operator / unseen symbol が混ざるため、prompt 単独の帰納よりも train 全体から族 priors を持ち込む設計が必要です。")
    lines.append("- したがって solver を作るなら、まず numeric 系でテンプレート辞書を増やし、その後 cryptarithm 系へ symbol substitution 層を載せる順が最短です。")
    lines.append("")
    lines.append("## Learned Solver")
    lines.append("")
    lines.append("- 同じ単一ファイル analyze_symbol_rules.py に full-prompt 文字列を入力する learned prompt solver を追加しました。")
    lines.append("- 再現コマンドは `--train-prompt-solver --epochs 40 --batch-size 64 --learning-rate 0.002 --seed 42` です。")
    lines.append("- 2026-04-20 の再現実行では symbolic 823 行に対して epoch 20 で exact 1.0000 を記録しました。")
    lines.append("- 測定詳細は data/symbol_rule_analysis_2026-04-20/prompt_solver_measurement_2026-04-20.md に記録しています。")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-upper-bound", action="store_true")
    parser.add_argument("--include-composite-families", action="store_true")
    parser.add_argument("--train-prompt-solver", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-assignments", type=int, default=512)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=2e-3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(DATA_CSV)
    if args.core_upper_bound:
        run_core_upper_bound(
            df,
            limit=args.limit,
            max_assignments=args.max_assignments,
            include_composite_families=args.include_composite_families,
        )
        return
    if args.train_prompt_solver:
        run_prompt_solver_train(
            df,
            max_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            seed=args.seed,
        )
        return

    report = build_report(df)
    REPORT_MD.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()