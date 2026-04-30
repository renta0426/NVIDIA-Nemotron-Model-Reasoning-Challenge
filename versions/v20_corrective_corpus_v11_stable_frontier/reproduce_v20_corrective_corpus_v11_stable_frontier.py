from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


VERSION_NAME = "v20_corrective_corpus_v11_stable_frontier"
MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
TOKEN_LIMIT = 8192
PROMPT_SUFFIX = "\nPlease put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`"
FORBIDDEN_COMPLETION_TERMS = ("default", "fallback", "guessed activations", "uncertain")
README_EVAL_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}

PROXY_EXACT_HARD_IDS = {"012fb81b", "01e09228", "1532c0d1", "a6192d29"}
PROXY_MANUAL_NO_SOLVER_IDS = {"101410e4", "12154247", "2230fad0", "257e7158"}
PROXY_PROMPT_OR_ANSWER_ONLY_HARD_IDS = {"12fd5b6c", "2d790c98", "31966698"}
VALIDATION_HARD_BIT_IDS = {
    "000b53cf",
    "0245b9bb",
    "0311b798",
    "048cc279",
    "04d8c3e6",
    "06881e47",
    "0ec17d2e",
    "1126e314",
    "12154247",
    "132ec6ae",
    "16db2c74",
    "172d2417",
}
NO_REGRESSION_ANCHOR_IDS = {
    "0520a6ec",
    "069dbaab",
    "c30a782a",
    "59c78e51",
    "b9500f41",
    "14a72508",
    "13009e35",
    "26a70ae0",
    "6a333ed6",
}
MANUAL_ANSWER_ONLY_ANCHOR_IDS = PROXY_MANUAL_NO_SOLVER_IDS | {"069dbaab", "0ec17d2e"}
ANSWER_ONLY_HARD_IDS = PROXY_PROMPT_OR_ANSWER_ONLY_HARD_IDS | {"04d8c3e6", "132ec6ae"}
STRUCTURED_PRIORITY_ABSTRACTS = {
    "choose(shl,shr,rol)",
    "choose(shl,shr,ror)",
    "choose(shl,shr,nibble_swap)",
    "majority(ror,shl,shr)",
    "majority(rol,shl,shr)",
    "or(rol,shl)",
    "or(rol,shr)",
    "xor(shl,shr)",
}
SURFACE_GUARDRAIL_BUCKET_PREFIXES = ("surface_", "easy_")


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / "README.md").exists() and (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError(f"Could not locate repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__).resolve())
VERSION_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = VERSION_ROOT / "outputs"
README_PATH = REPO_ROOT / "README.md"
STRATEGY_PATH = REPO_ROOT / "versions" / "v11_stable_frontier_strategy_2026-04-30.md"
TRAIN_ANALYSIS_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
V10_BUNDLE_PATH = (
    REPO_ROOT
    / "A-Open-ProgressPrizePublication"
    / "nemotron"
    / "training"
    / "sft"
    / "v20_corrective_corpus_v10_mainline_bundle.jsonl"
)
DEFAULT_BUNDLE_PATH = (
    REPO_ROOT
    / "A-Open-ProgressPrizePublication"
    / "nemotron"
    / "training"
    / "sft"
    / "v20_corrective_corpus_v11_stable_frontier_bundle.jsonl"
)
V10_OVERLAY_REPEATED_PATH = (
    REPO_ROOT
    / "versions"
    / "v20_corrective_corpus_v10_mainline"
    / "outputs"
    / "v10_mainline_default"
    / "artifacts"
    / "corrective_overlay_repeated.jsonl"
)
RESULTS_MD_PATH = VERSION_ROOT / "v20_corrective_corpus_v11_stable_frontier-results.md"


@dataclass(frozen=True)
class Expr:
    name: str
    args: tuple["Expr", ...] = ()


@dataclass
class OverlayRow:
    example_id: str
    source_problem_id: str
    category: str
    bucket: str
    prompt: str
    answer: str
    completion_text: str
    source_mix: str
    supervision_role: str
    assistant_style: str
    trace_kind: str
    selection_tier: str
    template_subtype: str
    teacher_solver_candidate: str
    source_tags: list[str]
    strategy_lane: str
    origin_id: str = ""
    exact_rule: str = ""
    query_bits: str = ""
    support_examples: list[tuple[str, str]] | None = None
    overlay_instance: int = 0
    recommended_repeat_count: int = 1

    def metadata(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "source_problem_id": self.source_problem_id,
            "category": self.category,
            "bucket": self.bucket,
            "answer": self.answer,
            "source_mix": self.source_mix,
            "supervision_role": self.supervision_role,
            "assistant_style": self.assistant_style,
            "trace_kind": self.trace_kind,
            "selection_tier": self.selection_tier,
            "template_subtype": self.template_subtype,
            "teacher_solver_candidate": self.teacher_solver_candidate,
            "source_tags": "|".join(sorted(set(self.source_tags))),
            "strategy_lane": self.strategy_lane,
            "origin_id": self.origin_id,
            "exact_rule": self.exact_rule,
            "query_bits": self.query_bits,
            "support_examples_json": json.dumps(self.support_examples or [], ensure_ascii=False),
            "overlay_instance": self.overlay_instance,
            "recommended_repeat_count": self.recommended_repeat_count,
        }

    def artifact(self) -> dict[str, Any]:
        payload = self.metadata()
        payload.update({"prompt": self.prompt, "completion_text": self.completion_text})
        return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def bits_to_int(bits: str) -> int:
    return int(bits, 2)


def int_to_bits(value: int) -> str:
    return f"{value & 0xFF:08b}"


def shl(value: int, amount: int) -> int:
    return (value << amount) & 0xFF


def shr(value: int, amount: int) -> int:
    return (value >> amount) & 0xFF


def rol(value: int, amount: int) -> int:
    amount %= 8
    return ((value << amount) | (value >> (8 - amount))) & 0xFF


def ror(value: int, amount: int) -> int:
    amount %= 8
    return ((value >> amount) | (value << (8 - amount))) & 0xFF


def reverse_bits(value: int) -> int:
    return bits_to_int(int_to_bits(value)[::-1])


def nibble_swap(value: int) -> int:
    return ((value & 0x0F) << 4) | ((value & 0xF0) >> 4)


def split_top_level_args(text: str) -> list[str]:
    args: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            args.append(text[start:index].strip())
            start = index + 1
    args.append(text[start:].strip())
    return [arg for arg in args if arg]


def parse_expr(text: str) -> Expr:
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty expression")
    if "(" not in stripped:
        return Expr(stripped)
    open_index = stripped.find("(")
    if not stripped.endswith(")"):
        raise ValueError(f"bad expression: {text}")
    name = stripped[:open_index].strip()
    inner = stripped[open_index + 1 : -1]
    return Expr(name, tuple(parse_expr(arg) for arg in split_top_level_args(inner)))


def expr_to_text(expr: Expr) -> str:
    if not expr.args:
        return expr.name
    return f"{expr.name}({','.join(expr_to_text(arg) for arg in expr.args)})"


def eval_expr(expr: Expr, value: int) -> int:
    name = expr.name.strip()
    if not expr.args:
        if name in {"x", "id", "identity"}:
            return value
        match = re.fullmatch(r"shl(\d+)", name)
        if match:
            return shl(value, int(match.group(1)))
        match = re.fullmatch(r"shr(\d+)", name)
        if match:
            return shr(value, int(match.group(1)))
        match = re.fullmatch(r"rol(\d+)", name)
        if match:
            return rol(value, int(match.group(1)))
        match = re.fullmatch(r"ror(\d+)", name)
        if match:
            return ror(value, int(match.group(1)))
        if name in {"reverse", "rev"}:
            return reverse_bits(value)
        if name in {"nibble_swap", "nibbleswap", "swap_nibbles"}:
            return nibble_swap(value)
        raise ValueError(f"unsupported atom: {name}")

    values = [eval_expr(arg, value) for arg in expr.args]
    if name == "not":
        if len(values) != 1:
            raise ValueError("not expects one argument")
        return (~values[0]) & 0xFF
    if name == "xor":
        result = 0
        for item in values:
            result ^= item
        return result & 0xFF
    if name == "and":
        result = 0xFF
        for item in values:
            result &= item
        return result & 0xFF
    if name == "or":
        result = 0
        for item in values:
            result |= item
        return result & 0xFF
    if name == "choose":
        if len(values) != 3:
            raise ValueError("choose expects three arguments")
        selector, when_one, when_zero = values
        return ((selector & when_one) | ((~selector) & when_zero)) & 0xFF
    if name == "majority":
        if len(values) != 3:
            raise ValueError("majority expects three arguments")
        a, b, c = values
        return ((a & b) | (a & c) | (b & c)) & 0xFF
    raise ValueError(f"unsupported function: {name}")


def parse_prompt_bits(prompt: str) -> tuple[list[tuple[str, str]], str]:
    bits = re.findall(r"\b[01]{8}\b", prompt)
    if len(bits) < 3 or len(bits) % 2 == 0:
        raise ValueError("expected input/output examples plus one query byte")
    examples = list(zip(bits[:-1:2], bits[1:-1:2]))
    return examples, bits[-1]


def make_bit_prompt(examples: list[tuple[str, str]], query_bits: str) -> str:
    lines = [
        "In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers. The transformation involves operations like bit shifts, rotations, XOR, AND, OR, NOT, and possibly majority or choice functions.",
        "",
        "Some examples are:",
    ]
    lines.extend(f"{left} -> {right}" for left, right in examples)
    lines.extend(["", f"Now, determine the output for: {query_bits}"])
    return "\n".join(lines)


def select_support_examples_for_expr(expr: Expr, seed_text: str, count: int = 8) -> tuple[list[tuple[str, str]], str]:
    rng = random.Random(stable_int(seed_text))
    candidates = list(range(256))
    rng.shuffle(candidates)
    selected: list[int] = []
    seen_zero = [False] * 8
    seen_one = [False] * 8

    def update_coverage(output_bits: str) -> None:
        for idx, bit in enumerate(output_bits):
            if bit == "0":
                seen_zero[idx] = True
            else:
                seen_one[idx] = True

    for value in candidates:
        output = int_to_bits(eval_expr(expr, value))
        improves = any((bit == "0" and not seen_zero[i]) or (bit == "1" and not seen_one[i]) for i, bit in enumerate(output))
        if improves or len(selected) < count:
            selected.append(value)
            update_coverage(output)
        if len(selected) >= count and all(seen_zero) and all(seen_one):
            break
    for value in candidates:
        if value not in selected and len(selected) < count:
            selected.append(value)
    query = next(value for value in candidates if value not in selected)
    examples = [(int_to_bits(value), int_to_bits(eval_expr(expr, value))) for value in selected[:count]]
    return examples, int_to_bits(query)


def render_formula_completion(formula: str, examples: list[tuple[str, str]], query_bits: str, answer: str) -> str:
    expr = parse_expr(formula)
    query_value = bits_to_int(query_bits)
    computed = int_to_bits(eval_expr(expr, query_value))
    if computed != answer:
        raise ValueError(f"formula {formula} predicts {computed}, expected {answer}")
    lines = ["<think>", "Check examples:"]
    for left, right in examples[:2]:
        predicted = int_to_bits(eval_expr(expr, bits_to_int(left)))
        lines.append(f"- {left} -> {right}; {formula}({left}) = {predicted}")
    lines.append(f"Rule = {formula}")
    lines.append(f"x = {query_bits}")
    if expr.args:
        for arg in expr.args:
            lines.append(f"{expr_to_text(arg)}(x) = {int_to_bits(eval_expr(arg, query_value))}")
    lines.append(f"{formula}(x) = {answer}")
    for index, bit in enumerate(answer):
        lines.append(f"o{index} = {bit}")
    lines.append(f"Output byte = {answer}")
    lines.append(f"Final answer = {answer}")
    lines.extend(["</think>", f"\\boxed{{{answer}}}<|im_end|>"])
    return "\n".join(lines)


def parse_signature(signature: str) -> list[tuple[int, bool] | None]:
    result: list[tuple[int, bool] | None] = []
    for match in re.finditer(r"o\d+=\[([^\]]*)\]", signature):
        inner = match.group(1).strip()
        if not inner or "," in inner or inner == "none":
            result.append(None)
            continue
        item = inner.strip()
        inverted = item.endswith("^")
        if inverted:
            item = item[:-1]
        source_match = re.fullmatch(r"i(\d+)", item)
        if not source_match:
            result.append(None)
            continue
        result.append((int(source_match.group(1)) - 1, inverted))
    return result


def apply_signature(mapping: list[tuple[int, bool]], input_bits: str) -> str:
    output: list[str] = []
    for source_index, inverted in mapping:
        bit = input_bits[source_index]
        if inverted:
            bit = "1" if bit == "0" else "0"
        output.append(bit)
    return "".join(output)


def render_mapping_completion(mapping: list[tuple[int, bool]], examples: list[tuple[str, str]], query_bits: str, answer: str) -> str:
    computed = apply_signature(mapping, query_bits)
    if computed != answer:
        raise ValueError(f"mapping predicts {computed}, expected {answer}")
    lines = ["<think>", "Check examples:"]
    for left, right in examples[:2]:
        lines.append(f"- {left} -> {right}; mapping({left}) = {apply_signature(mapping, left)}")
    lines.append("Rule = output bits copy these input positions:")
    for out_index, (source_index, inverted) in enumerate(mapping):
        op = "not " if inverted else ""
        lines.append(f"o{out_index} <- {op}i{source_index}")
    lines.append(f"x = {query_bits}")
    for out_index, (source_index, inverted) in enumerate(mapping):
        input_bit = query_bits[source_index]
        bit = "1" if (input_bit == "0" and inverted) or (input_bit == "1" and not inverted) else "0"
        op = "not " if inverted else ""
        lines.append(f"o{out_index} = {op}i{source_index} = {bit}")
    lines.append(f"Output byte = {answer}")
    lines.append(f"Final answer = {answer}")
    lines.extend(["</think>", f"\\boxed{{{answer}}}<|im_end|>"])
    return "\n".join(lines)


def solve_linear_system(equations: list[list[int]], values: list[int], width: int) -> list[int] | None:
    matrix = [row[:] + [value] for row, value in zip(equations, values)]
    pivot_columns: list[int] = []
    row_index = 0
    for col in range(width):
        pivot = None
        for candidate in range(row_index, len(matrix)):
            if matrix[candidate][col]:
                pivot = candidate
                break
        if pivot is None:
            continue
        matrix[row_index], matrix[pivot] = matrix[pivot], matrix[row_index]
        for other in range(len(matrix)):
            if other != row_index and matrix[other][col]:
                matrix[other] = [a ^ b for a, b in zip(matrix[other], matrix[row_index])]
        pivot_columns.append(col)
        row_index += 1
    for row in matrix:
        if not any(row[:width]) and row[width]:
            return None
    if len(pivot_columns) < width:
        return None
    solution = [0] * width
    for row, col in enumerate(pivot_columns):
        solution[col] = matrix[row][width]
    return solution


def solve_affine_from_examples(examples: list[tuple[str, str]]) -> list[list[int]] | None:
    equations = [[int(bit) for bit in left] + [1] for left, _ in examples]
    coeffs: list[list[int]] = []
    for out_index in range(8):
        values = [int(right[out_index]) for _, right in examples]
        solution = solve_linear_system(equations, values, 9)
        if solution is None:
            return None
        coeffs.append(solution)
    return coeffs


def apply_affine(coeffs: list[list[int]], bits: str) -> str:
    inputs = [int(bit) for bit in bits] + [1]
    output: list[str] = []
    for row in coeffs:
        value = 0
        for coeff, item in zip(row, inputs):
            value ^= coeff & item
        output.append(str(value))
    return "".join(output)


def affine_equation_text(row: list[int]) -> str:
    terms = [f"i{idx}" for idx, coeff in enumerate(row[:8]) if coeff]
    if row[8]:
        terms.append("1")
    return " xor ".join(terms) if terms else "0"


def render_affine_completion(coeffs: list[list[int]], examples: list[tuple[str, str]], query_bits: str, answer: str) -> str:
    computed = apply_affine(coeffs, query_bits)
    if computed != answer:
        raise ValueError(f"affine predicts {computed}, expected {answer}")
    lines = ["<think>", "Check examples:"]
    for left, right in examples[:2]:
        lines.append(f"- {left} -> {right}; affine({left}) = {apply_affine(coeffs, left)}")
    lines.append("Rule = affine equations over bits:")
    for index, coeff in enumerate(coeffs):
        lines.append(f"o{index} = {affine_equation_text(coeff)}")
    lines.append(f"x = {query_bits}")
    input_values = [int(bit) for bit in query_bits] + [1]
    for index, coeff in enumerate(coeffs):
        value = 0
        terms: list[str] = []
        for term_index, (coefficient, input_value) in enumerate(zip(coeff, input_values)):
            if not coefficient:
                continue
            value ^= input_value
            terms.append(str(input_value) if term_index == 8 else f"i{term_index}={input_value}")
        terms_text = " xor ".join(terms) if terms else "0"
        lines.append(f"o{index} = {terms_text} = {value}")
    lines.append(f"Output byte = {answer}")
    lines.append(f"Final answer = {answer}")
    lines.extend(["</think>", f"\\boxed{{{answer}}}<|im_end|>"])
    return "\n".join(lines)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"Missing CSV header: {path}")
        return [dict(row) for row in reader]


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def relative_to_repo(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def verify_readme_eval_contract() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    contract: dict[str, Any] = {}
    for key, expected in README_EVAL_CONTRACT.items():
        needle = f"{key}\t"
        matched = False
        for line in text.splitlines():
            if not line.startswith(needle):
                continue
            raw = line.split("\t", 1)[1].strip()
            if isinstance(expected, int) and not isinstance(expected, bool):
                contract[key] = int(raw)
            elif isinstance(expected, float):
                contract[key] = float(raw)
            else:
                contract[key] = raw
            matched = True
            break
        if not matched:
            raise SystemExit(f"Missing README.md evaluation row for {key}")
        if contract[key] != expected:
            raise SystemExit(f"README.md evaluation mismatch for {key}: expected {expected}, got {contract[key]}")
    return contract


@lru_cache(maxsize=1)
def get_chat_tokenizer() -> Any:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_TOKENIZER_NAME, trust_remote_code=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def tokenize_overlay_example(prompt: str, completion_text: str) -> tuple[list[int], list[int]]:
    tokenizer = get_chat_tokenizer()
    prompt_ids = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt + PROMPT_SUFFIX}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=True,
    )
    completion_ids = tokenizer.encode(completion_text, add_special_tokens=False)
    tokens = list(prompt_ids) + list(completion_ids)
    mask = [0] * len(prompt_ids) + [1] * len(completion_ids)
    if len(tokens) > TOKEN_LIMIT:
        raise ValueError(f"overlay example exceeds token limit: {len(tokens)}")
    return tokens, mask


def candidate_formula(row: dict[str, str]) -> str:
    return (row.get("bit_structured_formula_name") or row.get("bit_not_structured_formula_name") or "").strip()


def bit_rows_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["id"]: row for row in rows if row.get("family") == "bit_manipulation"}


def is_binary_answer(answer: str) -> bool:
    return len(answer.strip()) == 8 and set(answer.strip()) <= {"0", "1"}


def formula_supported(formula: str) -> bool:
    try:
        expr = parse_expr(formula)
        for value in (0, 1, 37, 128, 255):
            eval_expr(expr, value)
        return True
    except Exception:
        return False


def build_formula_synthetic_rows(train_rows: list[dict[str, str]], variants_per_formula: int) -> tuple[list[OverlayRow], dict[str, Any]]:
    formula_to_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    formula_to_abstract: dict[str, str] = {}
    formula_to_candidate: dict[str, str] = {}
    for row in train_rows:
        if row.get("family") != "bit_manipulation" or row.get("selection_tier") != "verified_trace_ready":
            continue
        formula = candidate_formula(row)
        if not formula or not is_binary_answer(row.get("answer", "")) or not formula_supported(formula):
            continue
        formula_to_rows[formula].append(row)
        formula_to_abstract[formula] = row.get("bit_structured_formula_abstract_family") or row.get(
            "bit_not_structured_formula_abstract_family", ""
        )
        formula_to_candidate[formula] = row.get("teacher_solver_candidate", "")

    rows: list[OverlayRow] = []
    for formula in sorted(formula_to_rows, key=lambda item: (-len(formula_to_rows[item]), item)):
        expr = parse_expr(formula)
        abstract = formula_to_abstract.get(formula, "")
        support_count = len(formula_to_rows[formula])
        seed_ids = [row["id"] for row in formula_to_rows[formula][:5]]
        extra = 2 if abstract in STRUCTURED_PRIORITY_ABSTRACTS else 0
        extra += 2 if any(row["id"] in (PROXY_EXACT_HARD_IDS | VALIDATION_HARD_BIT_IDS | NO_REGRESSION_ANCHOR_IDS) for row in formula_to_rows[formula]) else 0
        variant_count = variants_per_formula + extra
        for variant_index in range(variant_count):
            examples, query = select_support_examples_for_expr(expr, f"{formula}::{variant_index}", count=8)
            answer = int_to_bits(eval_expr(expr, bits_to_int(query)))
            completion = render_formula_completion(formula, examples, query, answer)
            row_id = f"v11_formula_{hashlib.sha1((formula + ':' + str(variant_index)).encode()).hexdigest()[:12]}"
            rows.append(
                OverlayRow(
                    example_id=row_id,
                    source_problem_id=row_id,
                    category="bit_manipulation",
                    bucket="v11_exact_program_trace_synth",
                    prompt=make_bit_prompt(examples, query),
                    answer=answer,
                    completion_text=completion,
                    source_mix="v11_exact_program_trace_synth",
                    supervision_role="lane1_exact_program_trace_synthesis",
                    assistant_style="canonical_formula_program_trace",
                    trace_kind="formula_program_trace",
                    selection_tier="synthetic_exact_trace",
                    template_subtype="bit_formula_synth",
                    teacher_solver_candidate=formula_to_candidate.get(formula, "formula_synth"),
                    source_tags=["v11", "lane1", "synthetic", "exact_formula", f"support={support_count}", *seed_ids],
                    strategy_lane="lane1_exact_program_trace_synthesis",
                    exact_rule=formula,
                    query_bits=query,
                    support_examples=examples,
                )
            )
    diagnostics = {
        "unique_formula_count": len(formula_to_rows),
        "generated_rows": len(rows),
        "top_formula_support": Counter({formula: len(items) for formula, items in formula_to_rows.items()}).most_common(20),
    }
    return rows, diagnostics


def build_hard_slot_rows(train_by_id: dict[str, dict[str, str]], repeats: int) -> tuple[list[OverlayRow], dict[str, Any]]:
    target_ids = PROXY_EXACT_HARD_IDS | VALIDATION_HARD_BIT_IDS | NO_REGRESSION_ANCHOR_IDS
    rows: list[OverlayRow] = []
    skipped: dict[str, str] = {}
    for row_id in sorted(target_ids):
        row = train_by_id.get(row_id)
        if row is None:
            skipped[row_id] = "missing"
            continue
        formula = candidate_formula(row)
        if not formula or not formula_supported(formula):
            skipped[row_id] = "no_supported_formula"
            continue
        try:
            examples, query = parse_prompt_bits(row["prompt"])
            answer = row["answer"].strip()
            completion = render_formula_completion(formula, examples, query, answer)
        except Exception as exc:
            skipped[row_id] = str(exc)
            continue
        for repeat_index in range(repeats):
            example_id = f"{row_id}#v11-hard-slot-{repeat_index + 1}"
            rows.append(
                OverlayRow(
                    example_id=example_id,
                    source_problem_id=row_id,
                    category="bit_manipulation",
                    bucket="v11_hard_row_slot_table_closure",
                    prompt=row["prompt"],
                    answer=row["answer"].strip(),
                    completion_text=completion,
                    source_mix="v11_hard_row_slot_table_closure",
                    supervision_role="lane2_hard_row_slot_table_closure",
                    assistant_style="canonical_hard_formula_slot_trace",
                    trace_kind="formula_program_trace",
                    selection_tier=row.get("selection_tier", ""),
                    template_subtype=row.get("template_subtype", ""),
                    teacher_solver_candidate=row.get("teacher_solver_candidate", ""),
                    source_tags=["v11", "lane2", "hard_row", row_id],
                    strategy_lane="lane2_hard_row_slot_table_closure",
                    origin_id=row_id,
                    exact_rule=formula,
                    query_bits=query,
                    support_examples=examples,
                )
            )
    diagnostics = {"target_ids": sorted(target_ids), "generated_rows": len(rows), "skipped": skipped}
    return rows, diagnostics


def build_affine_rows(train_rows: list[dict[str, str]], max_seed_rows: int, variants_per_seed: int) -> tuple[list[OverlayRow], dict[str, Any]]:
    rows: list[OverlayRow] = []
    used = 0
    skipped = Counter()
    for row in sorted(train_rows, key=lambda item: item["id"]):
        if row.get("family") != "bit_manipulation" or row.get("selection_tier") != "verified_trace_ready":
            continue
        if row.get("teacher_solver_candidate") != "binary_affine_xor" or not is_binary_answer(row.get("answer", "")):
            continue
        try:
            examples, query = parse_prompt_bits(row["prompt"])
            coeffs = solve_affine_from_examples(examples)
            if coeffs is None:
                skipped["not_unique"] += 1
                continue
            if apply_affine(coeffs, query) != row["answer"].strip():
                skipped["answer_mismatch"] += 1
                continue
        except Exception:
            skipped["parse_error"] += 1
            continue
        used += 1
        for variant_index in range(variants_per_seed):
            rng = random.Random(stable_int(f"affine::{row['id']}::{variant_index}"))
            values = list(range(256))
            rng.shuffle(values)
            synth_examples = [(int_to_bits(value), apply_affine(coeffs, int_to_bits(value))) for value in values[:9]]
            synth_query = int_to_bits(values[9])
            synth_answer = apply_affine(coeffs, synth_query)
            completion = render_affine_completion(coeffs, synth_examples, synth_query, synth_answer)
            example_id = f"v11_affine_{row['id']}_{variant_index + 1}"
            rows.append(
                OverlayRow(
                    example_id=example_id,
                    source_problem_id=example_id,
                    category="bit_manipulation",
                    bucket="v11_affine_program_trace_synth",
                    prompt=make_bit_prompt(synth_examples, synth_query),
                    answer=synth_answer,
                    completion_text=completion,
                    source_mix="v11_affine_program_trace_synth",
                    supervision_role="lane1_affine_program_trace_synthesis",
                    assistant_style="canonical_affine_program_trace",
                    trace_kind="affine_program_trace",
                    selection_tier="synthetic_exact_trace",
                    template_subtype="bit_affine_synth",
                    teacher_solver_candidate="binary_affine_xor",
                    source_tags=["v11", "lane1", "synthetic", "affine", row["id"]],
                    strategy_lane="lane1_exact_program_trace_synthesis",
                    origin_id=row["id"],
                    exact_rule="affine_xor",
                    query_bits=synth_query,
                    support_examples=synth_examples,
                )
            )
        if used >= max_seed_rows:
            break
    return rows, {"used_seed_rows": used, "generated_rows": len(rows), "skipped": dict(skipped)}


def build_mapping_rows(train_rows: list[dict[str, str]], max_seed_rows: int, variants_per_seed: int) -> tuple[list[OverlayRow], dict[str, Any]]:
    rows: list[OverlayRow] = []
    used = 0
    skipped = Counter()
    for row in sorted(train_rows, key=lambda item: item["id"]):
        if row.get("family") != "bit_manipulation" or row.get("selection_tier") != "verified_trace_ready":
            continue
        if row.get("teacher_solver_candidate") not in {"binary_bit_permutation_bijection", "binary_bit_permutation_independent"}:
            continue
        mapping_raw = parse_signature(row.get("bit_candidate_signature", ""))
        if len(mapping_raw) != 8 or any(item is None for item in mapping_raw):
            skipped["not_single_mapping"] += 1
            continue
        mapping = [item for item in mapping_raw if item is not None]
        try:
            examples, query = parse_prompt_bits(row["prompt"])
            if apply_signature(mapping, query) != row["answer"].strip():
                skipped["answer_mismatch"] += 1
                continue
        except Exception:
            skipped["parse_error"] += 1
            continue
        used += 1
        for variant_index in range(variants_per_seed):
            rng = random.Random(stable_int(f"mapping::{row['id']}::{variant_index}"))
            values = list(range(256))
            rng.shuffle(values)
            synth_examples = [(int_to_bits(value), apply_signature(mapping, int_to_bits(value))) for value in values[:8]]
            synth_query = int_to_bits(values[8])
            synth_answer = apply_signature(mapping, synth_query)
            completion = render_mapping_completion(mapping, synth_examples, synth_query, synth_answer)
            example_id = f"v11_mapping_{row['id']}_{variant_index + 1}"
            rows.append(
                OverlayRow(
                    example_id=example_id,
                    source_problem_id=example_id,
                    category="bit_manipulation",
                    bucket="v11_mapping_program_trace_synth",
                    prompt=make_bit_prompt(synth_examples, synth_query),
                    answer=synth_answer,
                    completion_text=completion,
                    source_mix="v11_mapping_program_trace_synth",
                    supervision_role="lane1_mapping_program_trace_synthesis",
                    assistant_style="canonical_mapping_program_trace",
                    trace_kind="mapping_program_trace",
                    selection_tier="synthetic_exact_trace",
                    template_subtype="bit_mapping_synth",
                    teacher_solver_candidate=row.get("teacher_solver_candidate", ""),
                    source_tags=["v11", "lane1", "synthetic", "mapping", row["id"]],
                    strategy_lane="lane1_exact_program_trace_synthesis",
                    origin_id=row["id"],
                    exact_rule=row.get("bit_candidate_signature", ""),
                    query_bits=synth_query,
                    support_examples=synth_examples,
                )
            )
        if used >= max_seed_rows:
            break
    return rows, {"used_seed_rows": used, "generated_rows": len(rows), "skipped": dict(skipped)}


def answer_only_completion(answer: str) -> str:
    return "\n".join(["<think>", "Use the provided final answer exactly.", "</think>", f"\\boxed{{{answer}}}<|im_end|>"])


def normalize_surface_completion(completion: str, answer: str) -> str:
    body = completion.replace("<|im_end|>", "")
    body = re.sub(r"\\boxed\{[^}]*\}", lambda match: match.group(0)[7:-1] or "boxed answer", body)
    return body.rstrip() + f"\n\\boxed{{{answer}}}<|im_end|>"


def build_answer_only_rows(train_by_id: dict[str, dict[str, str]], train_rows: list[dict[str, str]], target_count: int) -> tuple[list[OverlayRow], dict[str, Any]]:
    rows: list[OverlayRow] = []
    selected_ids: list[str] = []
    priority_ids = list(MANUAL_ANSWER_ONLY_ANCHOR_IDS | ANSWER_ONLY_HARD_IDS)
    for row_id in sorted(priority_ids):
        row = train_by_id.get(row_id)
        if row is None or not row.get("answer"):
            continue
        selected_ids.append(row_id)
    for row in sorted(train_rows, key=lambda item: item["id"]):
        if len(selected_ids) >= target_count:
            break
        if row.get("selection_tier") != "answer_only_keep":
            continue
        if row.get("family") not in {"bit_manipulation", "symbol_equation", "text_decryption"}:
            continue
        row_id = row["id"]
        if row_id not in selected_ids:
            selected_ids.append(row_id)

    for row_id in selected_ids[:target_count]:
        row = train_by_id.get(row_id)
        if row is None:
            row = next(item for item in train_rows if item["id"] == row_id)
        repeat_count = 2 if row_id in MANUAL_ANSWER_ONLY_ANCHOR_IDS else 1
        for repeat_index in range(repeat_count):
            example_id = f"{row_id}#v11-answer-only-{repeat_index + 1}"
            rows.append(
                OverlayRow(
                    example_id=example_id,
                    source_problem_id=row_id,
                    category=row.get("family", "unknown"),
                    bucket="v11_answer_only_stabilizer",
                    prompt=row["prompt"],
                    answer=row["answer"].strip(),
                    completion_text=answer_only_completion(row["answer"].strip()),
                    source_mix="v11_answer_only_stabilizer",
                    supervision_role="lane4_answer_only_stabilizer",
                    assistant_style="boxed_answer_only_stabilizer",
                    trace_kind="answer_only",
                    selection_tier=row.get("selection_tier", ""),
                    template_subtype=row.get("template_subtype", ""),
                    teacher_solver_candidate=row.get("teacher_solver_candidate", ""),
                    source_tags=["v11", "lane4", "answer_only", row_id],
                    strategy_lane="lane4_answer_only_stabilizer",
                    origin_id=row_id,
                )
            )
    return rows, {"selected_problem_ids": selected_ids[:target_count], "generated_rows": len(rows)}


def build_surface_guardrail_rows() -> tuple[list[OverlayRow], dict[str, Any]]:
    if not V10_OVERLAY_REPEATED_PATH.exists():
        return [], {"generated_rows": 0, "reason": "missing_v10_overlay"}
    rows: list[OverlayRow] = []
    v10_rows = load_jsonl_rows(V10_OVERLAY_REPEATED_PATH)
    for raw in v10_rows:
        bucket = str(raw.get("bucket", ""))
        if not bucket.startswith(SURFACE_GUARDRAIL_BUCKET_PREFIXES):
            continue
        answer = str(raw.get("answer", ""))
        completion = normalize_surface_completion(str(raw.get("completion_text", "")), answer)
        if not completion or any(term in completion.lower() for term in FORBIDDEN_COMPLETION_TERMS):
            continue
        row_id = str(raw.get("id"))
        rows.append(
            OverlayRow(
                example_id=f"{row_id}#v11-surface-{len(rows) + 1}",
                source_problem_id=row_id,
                category=str(raw.get("category", "unknown")),
                bucket="v11_surface_guardrail",
                prompt=str(raw.get("prompt", "")),
                answer=answer,
                completion_text=completion,
                source_mix="v11_surface_guardrail_from_v10",
                supervision_role="lane5_surface_guardrail",
                assistant_style=str(raw.get("assistant_style", "surface_guardrail")),
                trace_kind="surface_guardrail",
                selection_tier=str(raw.get("selection_tier", "")),
                template_subtype=str(raw.get("template_subtype", "")),
                teacher_solver_candidate=str(raw.get("teacher_solver_candidate", "")),
                source_tags=["v11", "lane5", "surface_guardrail", str(raw.get("source_mix", "v10"))],
                strategy_lane="lane5_surface_guardrail",
                origin_id=row_id,
            )
        )
    return rows, {"generated_rows": len(rows), "source_v10_rows": len(v10_rows)}


def renumber_overlay_rows(rows: list[OverlayRow]) -> list[OverlayRow]:
    counts = Counter(row.source_problem_id for row in rows)
    seen: Counter[str] = Counter()
    for row in rows:
        seen[row.source_problem_id] += 1
        row.overlay_instance = seen[row.source_problem_id]
        row.recommended_repeat_count = counts[row.source_problem_id]
    return rows


def validate_overlay_rows(rows: list[OverlayRow], diagnostics: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    by_lane = Counter(row.strategy_lane for row in rows)
    by_trace_kind = Counter(row.trace_kind for row in rows)
    by_source_mix = Counter(row.source_mix for row in rows)
    manual_full_trace = [row.source_problem_id for row in rows if row.selection_tier == "manual_audit_priority" and row.trace_kind != "answer_only"]
    if manual_full_trace:
        errors.append(f"manual_audit_priority used as full trace: {sorted(set(manual_full_trace))[:20]}")
    forbidden_hits: list[str] = []
    bad_boxed: list[str] = []
    missing_bits: list[str] = []
    for row in rows:
        lower = row.completion_text.lower()
        if any(term in lower for term in FORBIDDEN_COMPLETION_TERMS):
            forbidden_hits.append(row.example_id)
        if row.completion_text.count("\\boxed{") != 1 or f"\\boxed{{{row.answer}}}" not in row.completion_text:
            bad_boxed.append(row.example_id)
        if row.trace_kind.endswith("program_trace") and not all(f"o{idx}" in row.completion_text for idx in range(8)):
            missing_bits.append(row.example_id)
    if forbidden_hits:
        errors.append(f"forbidden completion terms found: {forbidden_hits[:20]}")
    if bad_boxed:
        errors.append(f"boxed answer format failures: {bad_boxed[:20]}")
    if missing_bits:
        errors.append(f"program traces missing output bit table: {missing_bits[:20]}")
    if len(rows) < 2500:
        errors.append(f"overlay too small for v11 non-micro change: {len(rows)} < 2500")
    if by_lane["lane1_exact_program_trace_synthesis"] < 2000:
        errors.append("lane1 exact program trace synthesis is below 2000 examples")
    if by_lane["lane2_hard_row_slot_table_closure"] == 0:
        errors.append("lane2 hard row slot table closure is empty")
    if by_lane["lane5_surface_guardrail"] == 0:
        errors.append("lane5 surface guardrail is empty")
    hard_hit_ids = {row.source_problem_id for row in rows if row.strategy_lane == "lane2_hard_row_slot_table_closure"}
    missing_exact_hard = sorted(PROXY_EXACT_HARD_IDS - hard_hit_ids)
    if missing_exact_hard:
        errors.append(f"missing proxy exact hard slot closure rows: {missing_exact_hard}")
    if "069dbaab" not in {row.source_problem_id for row in rows if row.trace_kind == "answer_only"}:
        errors.append("069dbaab answer-only anchor missing")
    return {
        "passed": not errors,
        "errors": errors,
        "overlay_examples": len(rows),
        "by_lane": dict(sorted(by_lane.items())),
        "by_trace_kind": dict(sorted(by_trace_kind.items())),
        "by_source_mix": dict(sorted(by_source_mix.items())),
        "diagnostics": diagnostics,
    }


def build_training_bundle(rows: list[OverlayRow], bundle_path: Path, validation: dict[str, Any]) -> dict[str, Any]:
    if not V10_BUNDLE_PATH.exists():
        raise SystemExit(f"Missing v10 bundle for base snapshot reuse: {V10_BUNDLE_PATH}")
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    tokenizer_cache: dict[tuple[str, str], tuple[list[int], list[int]]] = {}
    total_examples = 0
    total_tokens = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()
    base_examples = 0
    overlay_examples = 0
    base_step_max = 0
    batch_size = 32
    base_manifest: dict[str, Any] = {}

    with V10_BUNDLE_PATH.open("r", encoding="utf-8") as source, bundle_path.open("w", encoding="utf-8") as dest:
        first = source.readline()
        if not first:
            raise SystemExit("empty v10 bundle")
        base_manifest = json.loads(first)
        batch_size = int(base_manifest.get("base_snapshot_config", {}).get("batch_size", 32))
        manifest = {
            "record_type": "manifest",
            "bundle_format": "nemotron_single_file_training_bundle_v1",
            "version": VERSION_NAME,
            "created_at": utc_now(),
            "base_reuse_source_bundle": relative_to_repo(V10_BUNDLE_PATH),
            "base_snapshot_root": base_manifest.get("base_snapshot_root"),
            "base_snapshot_config": base_manifest.get("base_snapshot_config"),
            "bundle_path": relative_to_repo(bundle_path),
            "readme_eval_contract": verify_readme_eval_contract(),
            "strategy_note": relative_to_repo(STRATEGY_PATH),
            "note": "v11 replaces v10 row-answer frontier overlay with exact executable BIT program traces, keeps only narrow surface guardrails, and quarantines manual no-solver rows as answer-only anchors.",
        }
        dest.write(json.dumps(manifest, ensure_ascii=False) + "\n")
        for line in source:
            payload = json.loads(line)
            if payload.get("record_type") != "example" or payload.get("source") != "base_snapshot":
                continue
            dest.write(json.dumps(payload, ensure_ascii=False) + "\n")
            tokens = payload["tokens"]
            mask = payload["mask"]
            total_examples += 1
            base_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[str(payload.get("category", "unknown"))] += 1
            base_step_max = max(base_step_max, int(payload.get("step", 0)))

        base_step_count = base_step_max + 1
        for overlay_index, row in enumerate(rows):
            cache_key = (row.prompt, row.completion_text)
            if cache_key not in tokenizer_cache:
                tokenizer_cache[cache_key] = tokenize_overlay_example(row.prompt, row.completion_text)
            tokens, mask = tokenizer_cache[cache_key]
            payload = {
                "record_type": "example",
                "example_id": row.example_id,
                "source_problem_id": row.source_problem_id,
                "source": "v11_corrective_overlay",
                "segment": "synthetic.jsonl",
                "category": row.category,
                "step": base_step_count + (overlay_index // batch_size),
                "num_loss_tokens": sum(mask),
                "bucket": row.bucket,
                "overlay_instance": row.overlay_instance,
                "assistant_style": row.assistant_style,
                "supervision_role": row.supervision_role,
                "trace_kind": row.trace_kind,
                "strategy_lane": row.strategy_lane,
                "recommended_repeat_count": row.recommended_repeat_count,
                "source_tags": row.source_tags,
                "source_mix": row.source_mix,
                "tokens": tokens,
                "mask": mask,
            }
            dest.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            overlay_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[row.category] += 1

    total_steps = base_step_count + ((overlay_examples + batch_size - 1) // batch_size)
    return {
        "path": relative_to_repo(bundle_path),
        "format": "nemotron_single_file_training_bundle_v1",
        "base_reuse_source_bundle": relative_to_repo(V10_BUNDLE_PATH),
        "base_examples": base_examples,
        "overlay_examples": overlay_examples,
        "total_examples": total_examples,
        "batch_size": batch_size,
        "total_steps": total_steps,
        "total_tokens": total_tokens,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_seq_len": max_seq_len,
        "category_counts": dict(sorted(category_counts.items())),
        "validation_passed_before_bundle": validation["passed"],
    }


def summarize_against_v10(v11_rows: list[OverlayRow]) -> dict[str, Any]:
    v10_overlay_examples = 0
    v10_by_source = Counter()
    v10_by_bucket = Counter()
    if V10_OVERLAY_REPEATED_PATH.exists():
        for raw in load_jsonl_rows(V10_OVERLAY_REPEATED_PATH):
            v10_overlay_examples += 1
            v10_by_source[str(raw.get("source_mix", ""))] += 1
            v10_by_bucket[str(raw.get("bucket", ""))] += 1
    v11_by_source = Counter(row.source_mix for row in v11_rows)
    v11_by_bucket = Counter(row.bucket for row in v11_rows)
    return {
        "v10_overlay_examples": v10_overlay_examples,
        "v11_overlay_examples": len(v11_rows),
        "overlay_example_delta": len(v11_rows) - v10_overlay_examples,
        "v10_by_source_mix": dict(sorted(v10_by_source.items())),
        "v11_by_source_mix": dict(sorted(v11_by_source.items())),
        "v10_by_bucket_top": dict(v10_by_bucket.most_common(20)),
        "v11_by_bucket": dict(sorted(v11_by_bucket.items())),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# v20_corrective_corpus_v11_stable_frontier results",
        "",
        f"- created_at: {summary['created_at']}",
        f"- README basis: {relative_to_repo(README_PATH)} deterministic boxed-answer Accuracy contract.",
        f"- strategy note: {relative_to_repo(STRATEGY_PATH)}",
        "- status: data generated and strategy-validated; model score not yet measured.",
        "",
        "## Data Change Scale",
        "",
        f"- v10 overlay examples: `{summary['v10_comparison']['v10_overlay_examples']}`",
        f"- v11 overlay examples: `{summary['v10_comparison']['v11_overlay_examples']}`",
        f"- overlay delta: `{summary['v10_comparison']['overlay_example_delta']}`",
        f"- base examples reused from v10 bundle: `{summary['training_bundle']['base_examples']}`",
        f"- total examples: `{summary['training_bundle']['total_examples']}`",
        f"- overlay share of total examples: `{summary['overlay_share_of_total']:.4f}`",
        "",
        "## V11 Lanes",
        "",
    ]
    for lane, count in summary["validation"]["by_lane"].items():
        lines.append(f"- {lane}: `{count}`")
    lines.extend(["", "## Source Mix", ""])
    for source_mix, count in summary["validation"]["by_source_mix"].items():
        lines.append(f"- {source_mix}: `{count}`")
    lines.extend(["", "## Detailed Selection", ""])
    diagnostics = summary["diagnostics"]
    formula_diag = diagnostics["formula_synthesis"]
    hard_diag = diagnostics["hard_slot_closure"]
    affine_diag = diagnostics["affine_synthesis"]
    mapping_diag = diagnostics["mapping_synthesis"]
    answer_diag = diagnostics["answer_only"]
    surface_diag = diagnostics["surface_guardrail"]
    lines.append(f"- executable formula families: `{formula_diag['unique_formula_count']}` unique formulas -> `{formula_diag['generated_rows']}` synthetic rows")
    lines.append(f"- hard-row exact slot closure: `{hard_diag['generated_rows']}` rows; skipped without supported executable formula: `{sorted(hard_diag['skipped'])}`")
    lines.append(f"- affine XOR synthesis: `{affine_diag['used_seed_rows']}` seed rows -> `{affine_diag['generated_rows']}` rows")
    lines.append(f"- bit mapping synthesis: `{mapping_diag['used_seed_rows']}` seed rows -> `{mapping_diag['generated_rows']}` rows")
    lines.append(f"- answer-only stabilizers: `{len(answer_diag['selected_problem_ids'])}` source problems -> `{answer_diag['generated_rows']}` rows")
    lines.append(f"- v10 surface guardrails retained after boxed normalization: `{surface_diag['generated_rows']}` rows")
    lines.extend(["", "## V10 Comparison", ""])
    v10 = summary["v10_comparison"]
    ratio = v10["v11_overlay_examples"] / max(v10["v10_overlay_examples"], 1)
    lines.append(f"- overlay size multiplier vs v10: `{ratio:.2f}x`")
    lines.append("- v10 source mix:")
    for source_mix, count in v10["v10_by_source_mix"].items():
        lines.append(f"  - {source_mix}: `{count}`")
    lines.append("- v11 source mix:")
    for source_mix, count in v10["v11_by_source_mix"].items():
        lines.append(f"  - {source_mix}: `{count}`")
    lines.extend(["", "## Validation", ""])
    lines.append(f"- passed: `{summary['validation']['passed']}`")
    lines.append(f"- errors: `{summary['validation']['errors']}`")
    lines.append(f"- forbidden completion terms: none in accepted rows")
    lines.append(f"- manual full-CoT rows: none in accepted rows")
    lines.append(f"- bundle path: `{summary['training_bundle']['path']}`")
    lines.append(f"- max sequence length: `{summary['training_bundle']['max_seq_len']}`")
    lines.extend(["", "## Strategy Fit", ""])
    lines.append("- Replaced v10 short answer/rule-name frontier supervision with executable BIT program traces.")
    lines.append("- Kept manual no-solver rows out of full-CoT; they appear only as answer-only anchors when present.")
    lines.append("- Kept narrow surface guardrails from v10 instead of broad symbol/glyph CoT.")
    lines.append("- Generated a non-micro overlay change: thousands of new examples, not a few row edits.")
    lines.extend(["", "## Bundle", ""])
    bundle = summary["training_bundle"]
    for key in ["total_tokens", "total_masked_tokens", "total_unmasked_tokens", "total_steps", "category_counts"]:
        lines.append(f"- {key}: `{bundle.get(key)}`")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build v11 stable-frontier training data as a standalone script.")
    parser.add_argument("--run-name", default="v11_stable_frontier_default")
    parser.add_argument("--bundle-path", type=Path, default=DEFAULT_BUNDLE_PATH)
    parser.add_argument("--formula-variants", type=int, default=5)
    parser.add_argument("--hard-row-repeats", type=int, default=4)
    parser.add_argument("--affine-seed-rows", type=int, default=96)
    parser.add_argument("--affine-variants", type=int, default=2)
    parser.add_argument("--mapping-seed-rows", type=int, default=76)
    parser.add_argument("--mapping-variants", type=int, default=2)
    parser.add_argument("--answer-only-target", type=int, default=220)
    parser.add_argument("--skip-bundle", action="store_true")
    return parser.parse_args()


def main() -> None:
    global _V11_ALREADY_RAN
    if globals().get("_V11_ALREADY_RAN", False):
        return
    _V11_ALREADY_RAN = True
    args = parse_args()
    verify_readme_eval_contract()
    train_rows = load_csv_rows(TRAIN_ANALYSIS_PATH)
    train_by_id = bit_rows_by_id(train_rows)

    formula_rows, formula_diag = build_formula_synthetic_rows(train_rows, args.formula_variants)
    hard_rows, hard_diag = build_hard_slot_rows(train_by_id, args.hard_row_repeats)
    affine_rows, affine_diag = build_affine_rows(train_rows, args.affine_seed_rows, args.affine_variants)
    mapping_rows, mapping_diag = build_mapping_rows(train_rows, args.mapping_seed_rows, args.mapping_variants)
    answer_rows, answer_diag = build_answer_only_rows(train_by_id, train_rows, args.answer_only_target)
    surface_rows, surface_diag = build_surface_guardrail_rows()

    overlay_rows = renumber_overlay_rows(formula_rows + hard_rows + affine_rows + mapping_rows + answer_rows + surface_rows)
    diagnostics = {
        "formula_synthesis": formula_diag,
        "hard_slot_closure": hard_diag,
        "affine_synthesis": affine_diag,
        "mapping_synthesis": mapping_diag,
        "answer_only": answer_diag,
        "surface_guardrail": surface_diag,
    }
    validation = validate_overlay_rows(overlay_rows, diagnostics)
    if not validation["passed"]:
        raise SystemExit("v11 strategy validation failed: " + "; ".join(validation["errors"]))

    run_root = OUTPUT_ROOT / args.run_name
    artifacts_dir = run_root / "artifacts"
    reports_dir = run_root / "reports"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl(artifacts_dir / "v11_overlay_repeated.jsonl", [row.artifact() for row in overlay_rows])
    unique_by_source: dict[str, OverlayRow] = {}
    for row in overlay_rows:
        unique_by_source.setdefault(row.source_problem_id, row)
    write_jsonl(artifacts_dir / "v11_overlay_unique.jsonl", [row.artifact() for row in unique_by_source.values()])
    write_csv(
        artifacts_dir / "v11_selection.csv",
        [row.metadata() for row in overlay_rows],
        fieldnames=[
            "example_id",
            "source_problem_id",
            "category",
            "bucket",
            "answer",
            "source_mix",
            "supervision_role",
            "assistant_style",
            "trace_kind",
            "selection_tier",
            "template_subtype",
            "teacher_solver_candidate",
            "source_tags",
            "strategy_lane",
            "origin_id",
            "exact_rule",
            "query_bits",
            "support_examples_json",
            "overlay_instance",
            "recommended_repeat_count",
        ],
    )

    training_bundle: dict[str, Any] | None = None
    if not args.skip_bundle:
        training_bundle = build_training_bundle(overlay_rows, args.bundle_path.resolve(), validation)
    else:
        training_bundle = {"path": "not_written", "base_examples": 0, "overlay_examples": len(overlay_rows), "total_examples": len(overlay_rows), "max_seq_len": 0}

    summary = {
        "version": VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": verify_readme_eval_contract(),
        "strategy_note": relative_to_repo(STRATEGY_PATH),
        "inputs": {
            "train_row_analysis_v1": relative_to_repo(TRAIN_ANALYSIS_PATH),
            "v10_bundle": relative_to_repo(V10_BUNDLE_PATH),
            "v10_overlay_repeated": relative_to_repo(V10_OVERLAY_REPEATED_PATH),
        },
        "validation": validation,
        "diagnostics": diagnostics,
        "training_bundle": training_bundle,
        "v10_comparison": summarize_against_v10(overlay_rows),
        "overlay_share_of_total": len(overlay_rows) / max(int(training_bundle.get("total_examples", len(overlay_rows))), 1),
    }
    write_json(artifacts_dir / "v11_overlay_summary.json", summary)
    markdown = render_markdown(summary)
    (reports_dir / "v11_stable_frontier_data_validation.md").write_text(markdown, encoding="utf-8")
    RESULTS_MD_PATH.write_text(markdown, encoding="utf-8")
    print(json.dumps({"summary_path": relative_to_repo(artifacts_dir / "v11_overlay_summary.json"), "bundle": training_bundle, "validation": validation}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
