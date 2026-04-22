from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


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
RESULTS_MD = VERSION_ROOT / "v20_corrective_corpus_v8_mainline-results.md"

README_PATH = REPO_ROOT / "README.md"
STRATEGY_NOTE_PATH = REPO_ROOT / "versions" / "v20_to_088_reassessment_2026-04-18.md"

TRAIN_RECOMMENDED_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_recommended_learning_target_v1.csv"
SYMBOL_OPERATOR_SPECIFIC_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "symbol_operator_specific_formula_candidates_v1.csv"
SYMBOL_MANUAL_PROMPT_EXACT_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "symbol_manual_prompt_exact_answer_only_candidates_v1.csv"
SYMBOL_GLYPH_TRAINING_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "symbol_glyph_training_answer_only_candidates_v1.csv"
SYMBOL_GLYPH_GROUPED_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "symbol_glyph_grouped_exact_answer_only_candidates_v1.csv"
SYMBOL_TRACE_POLICY_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "symbol_trace_teacher_policy_v1.csv"
TRAIN_CSV_PATH = REPO_ROOT / "data" / "train.csv"
PROBLEMS_PATH = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "problems.jsonl"
REASONING_DIR = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "reasoning"
TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
DEFAULT_BUNDLE_PATH = TRAINING_SFT_ROOT / "v20_corrective_corpus_v8_mainline_bundle.jsonl"
MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)
TOKEN_LIMIT = 8192

RESULT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "result"
RESULT_BASE_VALIDATION_PATH = RESULT_ROOT / "results-v20" / "validation.csv"
RESULT_CURRENT_VALIDATION_PATH = RESULT_ROOT / "results-v7-1" / "validation.csv"
RESULT_V4_VALIDATION_PATH = RESULT_ROOT / "results-v4" / "validation.csv"
RESULT_BASE_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval_v20" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"
RESULT_CURRENT_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval-v7-1" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"
RESULT_V4_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval-v4" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"

README_EVAL_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}

BUCKET_ORDER = (
    "binary_structured_exact_core",
    "binary_logic_exact",
    "binary_permutation_exact",
    "binary_prompt_local_exact",
    "symbol_numeric_exact",
    "symbol_glyph_exact",
    "surface_numeral_boxed",
    "surface_cipher_boxed",
    "surface_unit_tail",
    "easy_gravity_fragile",
)

DEFAULT_BUCKET_LIMITS = {
    "binary_structured_exact_core": 224,
    "binary_logic_exact": 88,
    "binary_permutation_exact": 64,
    "binary_prompt_local_exact": 96,
    "symbol_numeric_exact": 48,
    "symbol_glyph_exact": 48,
    "surface_numeral_boxed": 18,
    "surface_cipher_boxed": 4,
    "surface_unit_tail": 4,
    "easy_gravity_fragile": 4,
}

DEFAULT_REPEAT_COUNTS = {
    "binary_structured_exact_core": 2,
    "binary_logic_exact": 2,
    "binary_permutation_exact": 2,
    "binary_prompt_local_exact": 2,
    "symbol_numeric_exact": 2,
    "symbol_glyph_exact": 2,
    "surface_numeral_boxed": 1,
    "surface_cipher_boxed": 1,
    "surface_unit_tail": 1,
    "easy_gravity_fragile": 1,
}

PRIORITY_BINARY_FAMILIES = (
    "xor(shl,shr)",
    "choose(shl,shr,rol)",
    "choose(shl,shr,ror)",
    "majority(ror,shl,shr)",
    "majority(rol,shl,shr)",
    "xor(ror,shl)",
    "or(rol,shr)",
    "or(ror,shr)",
)

PRIORITY_BINARY_FAMILY_QUOTAS = {
    "xor(shl,shr)": 96,
    "choose(shl,shr,rol)": 24,
    "choose(shl,shr,ror)": 24,
    "majority(ror,shl,shr)": 20,
    "majority(rol,shl,shr)": 20,
    "xor(ror,shl)": 12,
    "or(rol,shr)": 10,
    "or(ror,shr)": 10,
}

STRUCTURED_SPILLOVER_SLOTS = 40
BINARY_HARD_EXTRA_VARIANTS = 1

BASE_EXCLUDED_IDS = {"ef2fe526"}

MANDATORY_IDS = {
    "binary_structured_exact_core": {
        "012fb81b",
        "01e09228",
        "0520a6ec",
        "0a50c4a8",
        "1532c0d1",
        "17fd9612",
        "59c78e51",
        "8e5d6fe6",
        "a6192d29",
    },
    "binary_logic_exact": {"0dd5caf4", "c30a782a"},
    "binary_permutation_exact": {"b9500f41", "fa67da07"},
    "binary_prompt_local_exact": {"12fd5b6c", "2d790c98"},
    "symbol_numeric_exact": {"8158a14c", "878c843c", "b7b1d1a8", "e8de8b47"},
    "symbol_glyph_exact": {"a85864a9", "be7101dc", "d7e5414c", "dc240ebd"},
}

HARDBLACKLIST_IDS = {
    "binary_structured_exact_core": {"2817d770", "06b5da9f"},
    "binary_logic_exact": {"6a333ed6"},
}

HARD_DEFAULT1_TARGET_IDS = {
    "0dd5caf4",
    "012fb81b",
    "01e09228",
    "0245b9bb",
    "0311b798",
    "0520a6ec",
    "0a50c4a8",
    "1126e314",
    "12fd5b6c",
    "1532c0d1",
    "172d2417",
    "17fd9612",
    "2d790c98",
    "59c78e51",
    "8e5d6fe6",
    "a6192d29",
    "c30a782a",
}

SELECTION_TIER_PRIORITY = {
    "verified_trace_ready": 3,
    "manual_audit_priority": 2,
    "answer_only_keep": 1,
}

SYMBOL_ALLOWED_TIERS = {"verified_trace_ready", "manual_audit_priority", "answer_only_keep"}

SOURCE_ROW_METADATA_FIELDS = (
    "selection_tier",
    "template_subtype",
    "teacher_solver_candidate",
    "hard_score",
    "audit_reasons",
    "analysis_notes",
    "symbol_query_operator",
    "bit_query_binary",
    "bit_structured_formula_name",
    "bit_structured_formula_prediction",
    "bit_structured_formula_abstract_family",
    "bit_structured_formula_abstract_support",
    "bit_not_structured_formula_name",
    "bit_not_structured_formula_prediction",
    "bit_not_structured_formula_abstract_family",
    "bit_not_structured_formula_abstract_support",
)


@dataclass
class Candidate:
    row: dict[str, str]
    bucket: str
    source_tags: tuple[str, ...]
    proxy_failed: bool
    validation_failed: bool
    priority_key: tuple[Any, ...]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_float(value: Any, default: float = 0.0) -> float:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def copy_source_metadata(target: dict[str, str], source_row: dict[str, str]) -> None:
    for field in SOURCE_ROW_METADATA_FIELDS:
        target[field] = str(source_row.get(field, "")).strip()


def binary_family_key(row: dict[str, str]) -> str:
    return (
        str(row.get("bit_structured_formula_abstract_family", "")).strip()
        or str(row.get("bit_not_structured_formula_abstract_family", "")).strip()
        or str(row.get("bit_structured_formula_name", "")).strip()
        or str(row.get("bit_not_structured_formula_name", "")).strip()
        or str(row.get("teacher_solver_candidate", "")).strip()
        or str(row.get("template_subtype", "")).strip()
        or "NONE"
    )


def build_completion_from_think_lines(lines: list[str], answer: str) -> str:
    return "\n".join(["<think>", *lines, "</think>", f"\\boxed{{{answer}}}<|im_end|>"])


def build_binary_completion(candidate: Candidate, assistant_style: str) -> str:
    row = candidate.row
    bucket = candidate.bucket
    family = binary_family_key(row)
    exact_rule = str(row.get("bit_structured_formula_name", "")).strip() or str(
        row.get("bit_not_structured_formula_name", "")
    ).strip()
    solver = str(row.get("teacher_solver_candidate", "")).strip() or "verified_binary_rule"
    if assistant_style == "exact_rule_commit":
        if bucket == "binary_structured_exact_core":
            lines = [
                f"Verified structured binary family: {family}." if family != "NONE" else "Use the verified structured binary rule from the examples.",
                f"Concrete rule: {exact_rule}." if exact_rule else f"Recovered solver pattern: {solver}.",
                "Apply the same verified transformation to the query byte.",
                "Keep the final byte exact with leading zeros and no fallback bits.",
            ]
        elif bucket == "binary_logic_exact":
            lines = [
                f"Verified bitwise rule family: {family}." if family != "NONE" else "Use the verified bitwise rule from the examples.",
                f"Concrete logic rule: {exact_rule}." if exact_rule else f"Recovered solver pattern: {solver}.",
                "Resolve every bit from the verified logic pattern.",
                "Keep the final byte exact with leading zeros.",
            ]
        elif bucket == "binary_permutation_exact":
            lines = [
                "Use the exact source-bit reordering verified in the examples.",
                f"Recovered permutation family: {solver}." if solver else "Copy each output bit from its verified source position.",
                "Preserve the exact 8-bit ordering and leading zeros.",
                "Return only the final reordered byte in the box.",
            ]
        elif bucket == "binary_prompt_local_exact":
            lines = [
                "Use the exact prompt-local binary rule verified by the examples.",
                f"Recovered exact pattern: {solver}." if solver else "Keep the query under the same prompt-local exact rule.",
                "Preserve exact 8-bit closure with leading zeros.",
                "Return only the final byte in the box.",
            ]
        else:
            raise ValueError(f"Unsupported binary bucket for exact_rule_commit: {bucket}")
    elif assistant_style == "exact_closure_commit":
        lines = [
            f"Verified binary family: {family}." if family != "NONE" else "Use the verified binary rule from the examples.",
            "Use only the bits justified by the verified rule.",
            "Keep exact 8-bit closure with leading zeros from start to finish.",
            "Only the final byte belongs in the box.",
        ]
    elif assistant_style == "anti_default1_commit":
        lines = [
            f"Verified binary family: {family}." if family != "NONE" else "Use the verified binary rule from the examples.",
            "Do not use default 1, fallback bits, or guessed activations.",
            "If a bit is not justified by the verified rule, it stays off.",
            "Return only the exact final 8-bit byte in the box.",
        ]
    else:
        raise ValueError(f"Unsupported binary assistant style: {assistant_style}")
    return build_completion_from_think_lines(lines, answer=row["answer"])


def build_symbol_completion(candidate: Candidate, assistant_style: str) -> str:
    row = candidate.row
    if candidate.bucket == "symbol_numeric_exact":
        if assistant_style == "symbol_operator_commit":
            lines = [
                "Use the same prompt-specific numeric operator rule shown in the examples.",
                "Preserve digit order, zero padding, and any prefix or suffix exactly.",
                "Do not normalize the surface form into a different equivalent string.",
                "Return only the exact final string in the box.",
            ]
        elif assistant_style == "symbol_format_commit":
            lines = [
                "Commit to the verified output contract implied by the examples.",
                "No dropped symbols, no reordered digits, and no rewritten formatting.",
                "Keep the answer surface exactly as required by the prompt pattern.",
                "Return only the exact final string in the box.",
            ]
        else:
            raise ValueError(f"Unsupported numeric symbol assistant style: {assistant_style}")
    elif candidate.bucket == "symbol_glyph_exact":
        if assistant_style == "symbol_glyph_copy_commit":
            lines = [
                "Use the same per-character symbol transduction shown in the examples.",
                "Preserve output length and slot order exactly.",
                "Do not drop, add, or reorder characters.",
                "Return only the exact final string in the box.",
            ]
        elif assistant_style == "symbol_glyph_length_commit":
            lines = [
                "Commit to the verified symbol copy and transduction contract.",
                "Each output slot must stay aligned to the same pattern as the examples.",
                "Keep the sequence length and character order exact.",
                "Return only the exact final string in the box.",
            ]
        else:
            raise ValueError(f"Unsupported glyph symbol assistant style: {assistant_style}")
    else:
        raise ValueError(f"Unsupported symbol bucket: {candidate.bucket}")
    return build_completion_from_think_lines(lines, answer=row["answer"])


def build_surface_completion(candidate: Candidate) -> str:
    row = candidate.row
    bucket = candidate.bucket
    if bucket == "surface_numeral_boxed":
        lines = [
            "Use the verified numeral conversion from the examples.",
            "Keep the final numeral surface exact.",
            "Return only the final answer in \\boxed{...}.",
        ]
    elif bucket == "surface_cipher_boxed":
        lines = [
            "Use the verified cipher mapping from the examples.",
            "Do not add quotes, slashes, or extra symbols.",
            "Return only the final answer in \\boxed{...}.",
        ]
    elif bucket == "surface_unit_tail":
        lines = [
            "Use the verified unit conversion from the examples.",
            "Keep decimal formatting and trailing zeros exact.",
            "Return only the final answer in \\boxed{...}.",
        ]
    elif bucket == "easy_gravity_fragile":
        lines = [
            "Use the verified gravity rule from the examples.",
            "Keep the final numeric formatting exact.",
            "Return only the final answer in \\boxed{...}.",
        ]
    else:
        raise ValueError(f"Unsupported surface bucket: {bucket}")
    return build_completion_from_think_lines(lines, answer=row["answer"])


def build_supervision_variants(candidate: Candidate, base_variant_count: int) -> list[dict[str, str]]:
    if candidate.bucket.startswith("binary_"):
        variant_styles = ["exact_rule_commit", "exact_closure_commit"]
        if candidate.row["id"] in HARD_DEFAULT1_TARGET_IDS:
            variant_styles.append("anti_default1_commit")
        target_count = base_variant_count + (
            BINARY_HARD_EXTRA_VARIANTS if candidate.row["id"] in HARD_DEFAULT1_TARGET_IDS else 0
        )
        target_count = min(target_count, len(variant_styles))
        return [
            {
                "assistant_style": style,
                "supervision_role": "lane1_exact_binary" if style != "anti_default1_commit" else "lane1b_anti_default1",
                "completion_text": build_binary_completion(candidate, style),
            }
            for style in variant_styles[:target_count]
        ]
    if candidate.bucket == "symbol_numeric_exact":
        variant_styles = ["symbol_operator_commit", "symbol_format_commit"]
        return [
            {
                "assistant_style": style,
                "supervision_role": "lane2_symbol_numeric_exact",
                "completion_text": build_symbol_completion(candidate, style),
            }
            for style in variant_styles[: min(base_variant_count, len(variant_styles))]
        ]
    if candidate.bucket == "symbol_glyph_exact":
        variant_styles = ["symbol_glyph_copy_commit", "symbol_glyph_length_commit"]
        return [
            {
                "assistant_style": style,
                "supervision_role": "lane3_symbol_glyph_exact",
                "completion_text": build_symbol_completion(candidate, style),
            }
            for style in variant_styles[: min(base_variant_count, len(variant_styles))]
        ]
    return [
        {
            "assistant_style": "surface_boxed_tail",
            "supervision_role": "lane4_surface_stabilizer",
            "completion_text": build_surface_completion(candidate),
        }
    ]


def extract_think_body(completion_text: str) -> str:
    start = completion_text.find("<think>")
    end = completion_text.find("</think>")
    if start == -1 or end == -1 or end <= start:
        return ""
    return completion_text[start + len("<think>") : end].strip()


def nonempty_line_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def answer_has_symbolic_prefix(answer: str) -> bool:
    text = str(answer).strip()
    return bool(text) and not text[0].isalnum()


def read_csv_map(path: Path, key: str = "id") -> dict[str, dict[str, str]]:
    return {row[key]: row for row in load_csv_rows(path)}


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
            raise SystemExit(
                f"README.md evaluation mismatch for {key}: expected {expected}, got {contract[key]}"
            )
    return contract


def load_train_prompts() -> dict[str, dict[str, str]]:
    return {row["id"]: row for row in load_csv_rows(TRAIN_CSV_PATH)}


def load_problem_categories() -> dict[str, str]:
    categories: dict[str, str] = {}
    for row in load_jsonl_rows(PROBLEMS_PATH):
        categories[str(row["id"])] = str(row["category"])
    return categories


def extract_boxed_answer(reasoning_text: str) -> str:
    matches = re.findall(r"\\boxed\{([^}]*)", reasoning_text)
    return matches[-1].strip() if matches else ""


def compare_answers(stored_answer: str, predicted: str) -> bool:
    stored_answer = stored_answer.strip()
    predicted = predicted.strip()
    if re.fullmatch(r"[01]+", stored_answer):
        return predicted.lower() == stored_answer.lower()
    try:
        return math.isclose(
            float(stored_answer),
            float(predicted),
            rel_tol=1e-2,
            abs_tol=1e-5,
        )
    except Exception:
        return predicted.lower() == stored_answer.lower()


@lru_cache(maxsize=None)
def load_reasoning_text(row_id: str) -> str:
    return (REASONING_DIR / f"{row_id}.txt").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def load_teacher_correctness() -> dict[str, bool]:
    train_prompts = load_train_prompts()
    correctness: dict[str, bool] = {}
    for row_id, row in train_prompts.items():
        path = REASONING_DIR / f"{row_id}.txt"
        if not path.exists():
            continue
        teacher_answer = extract_boxed_answer(load_reasoning_text(row_id))
        correctness[row_id] = compare_answers(str(row["answer"]), teacher_answer)
    return correctness


@lru_cache(maxsize=1)
def get_chat_tokenizer() -> Any:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_TOKENIZER_NAME, trust_remote_code=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def tokenize_overlay_example(prompt: str, completion_text: str) -> tuple[list[int], list[int]]:
    chat_tokenizer = get_chat_tokenizer()
    prompt_ids = chat_tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt + PROMPT_SUFFIX}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=True,
    )
    completion_ids = chat_tokenizer.encode(completion_text, add_special_tokens=False)
    all_tokens = list(prompt_ids) + list(completion_ids)
    mask = [0] * len(prompt_ids) + [1] * len(completion_ids)
    if len(all_tokens) > TOKEN_LIMIT:
        all_tokens = all_tokens[:TOKEN_LIMIT]
        mask = mask[:TOKEN_LIMIT]
    return all_tokens, mask


def load_base_snapshot_index_rows() -> list[dict[str, Any]]:
    if not BASE_SNAPSHOT_INDEX_PATH.exists():
        raise SystemExit(f"Missing base snapshot index: {BASE_SNAPSHOT_INDEX_PATH}")
    return load_jsonl_rows(BASE_SNAPSHOT_INDEX_PATH)


def load_base_snapshot_index_map() -> dict[str, dict[str, Any]]:
    return {str(row["problem_id"]): row for row in load_base_snapshot_index_rows()}


def load_base_snapshot_examples() -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]], int]:
    config = read_json(BASE_SNAPSHOT_CONFIG_PATH)
    batch_size = int(config["batch_size"])
    base_rows = load_base_snapshot_index_rows()
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in base_rows:
        problem_id = str(row["problem_id"])
        segment = str(row["segment"])
        token_path = BASE_SNAPSHOT_ROOT / "tokens" / problem_id / f"{Path(segment).stem}.json"
        if not token_path.exists():
            raise SystemExit(f"Missing base token snapshot: {token_path}")
        payload = read_json(token_path)
        tokens = payload["tokens"]
        mask = payload["mask"]
        num_loss_tokens = int(row["num_loss_tokens"])
        if sum(mask) != num_loss_tokens:
            raise SystemExit(
                f"num_loss_tokens mismatch for base snapshot {problem_id}: {sum(mask)} != {num_loss_tokens}"
            )
        by_key[(problem_id, segment)] = {
            "row": row,
            "tokens": tokens,
            "mask": mask,
        }
    return base_rows, by_key, batch_size


def load_measured_signals() -> dict[str, Any]:
    base_validation = read_csv_map(RESULT_BASE_VALIDATION_PATH)
    current_validation = read_csv_map(RESULT_CURRENT_VALIDATION_PATH)
    v4_validation = read_csv_map(RESULT_V4_VALIDATION_PATH)
    base_proxy = read_csv_map(RESULT_BASE_PROXY_PATH)
    current_proxy = read_csv_map(RESULT_CURRENT_PROXY_PATH)
    v4_proxy = read_csv_map(RESULT_V4_PROXY_PATH)

    base_to_current_validation_improved: set[str] = set()
    base_to_current_validation_regressed: set[str] = set()
    current_validation_fail_ids: set[str] = set()
    for row_id in sorted(set(base_validation) & set(current_validation)):
        base_correct = base_validation[row_id]["correct"] == "True"
        new_correct = current_validation[row_id]["correct"] == "True"
        if (not base_correct) and new_correct:
            base_to_current_validation_improved.add(row_id)
        elif base_correct and (not new_correct):
            base_to_current_validation_regressed.add(row_id)
        if not new_correct:
            current_validation_fail_ids.add(row_id)

    base_to_current_proxy_improved: set[str] = set()
    base_to_current_proxy_regressed: set[str] = set()
    current_proxy_fail_ids: set[str] = set()
    base_proxy_fail_ids: set[str] = set()
    for row_id in sorted(set(base_proxy) & set(current_proxy)):
        base_correct = base_proxy[row_id]["is_correct"] == "True"
        new_correct = current_proxy[row_id]["is_correct"] == "True"
        if (not base_correct) and new_correct:
            base_to_current_proxy_improved.add(row_id)
        elif base_correct and (not new_correct):
            base_to_current_proxy_regressed.add(row_id)
        if not new_correct:
            current_proxy_fail_ids.add(row_id)
        if not base_correct:
            base_proxy_fail_ids.add(row_id)

    v4_to_current_validation_improved: set[str] = set()
    v4_to_current_validation_regressed: set[str] = set()
    for row_id in sorted(set(v4_validation) & set(current_validation)):
        old_correct = v4_validation[row_id]["correct"] == "True"
        new_correct = current_validation[row_id]["correct"] == "True"
        if (not old_correct) and new_correct:
            v4_to_current_validation_improved.add(row_id)
        elif old_correct and (not new_correct):
            v4_to_current_validation_regressed.add(row_id)

    v4_to_current_proxy_improved: set[str] = set()
    v4_to_current_proxy_regressed: set[str] = set()
    for row_id in sorted(set(v4_proxy) & set(current_proxy)):
        old_correct = v4_proxy[row_id]["is_correct"] == "True"
        new_correct = current_proxy[row_id]["is_correct"] == "True"
        if (not old_correct) and new_correct:
            v4_to_current_proxy_improved.add(row_id)
        elif old_correct and (not new_correct):
            v4_to_current_proxy_regressed.add(row_id)

    outcome_score: dict[str, int] = defaultdict(int)
    for row_id in base_to_current_proxy_improved:
        outcome_score[row_id] += 3
    for row_id in base_to_current_validation_improved:
        outcome_score[row_id] += 2
    for row_id in v4_to_current_proxy_regressed:
        outcome_score[row_id] += 2
    for row_id in v4_to_current_validation_regressed:
        outcome_score[row_id] += 1
    for row_id in base_to_current_proxy_regressed:
        outcome_score[row_id] -= 4
    for row_id in base_to_current_validation_regressed:
        outcome_score[row_id] -= 3
    return {
        "base_validation": base_validation,
        "current_validation": current_validation,
        "v4_validation": v4_validation,
        "base_proxy": base_proxy,
        "current_proxy": current_proxy,
        "v4_proxy": v4_proxy,
        "base_to_current_validation_improved": base_to_current_validation_improved,
        "base_to_current_validation_regressed": base_to_current_validation_regressed,
        "base_to_current_proxy_improved": base_to_current_proxy_improved,
        "base_to_current_proxy_regressed": base_to_current_proxy_regressed,
        "v4_to_current_validation_improved": v4_to_current_validation_improved,
        "v4_to_current_validation_regressed": v4_to_current_validation_regressed,
        "v4_to_current_proxy_improved": v4_to_current_proxy_improved,
        "v4_to_current_proxy_regressed": v4_to_current_proxy_regressed,
        "base_proxy_fail_ids": base_proxy_fail_ids,
        "current_proxy_fail_ids": current_proxy_fail_ids,
        "current_validation_fail_ids": current_validation_fail_ids,
        "outcome_score": outcome_score,
    }


def choose_guardrail_ids(
    *,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    base_index_map: dict[str, dict[str, Any]],
    limit: int,
    category_name: Any,
    answer_predicate: Any,
) -> list[str]:
    if isinstance(category_name, str):
        allowed_categories = {category_name}
    else:
        allowed_categories = {str(value) for value in category_name}
    ranked: list[tuple[float, int, str]] = []
    for row_id, category in categories.items():
        if category not in allowed_categories:
            continue
        if row_id not in train_prompts or row_id not in base_index_map:
            continue
        if not answer_predicate(train_prompts[row_id]["answer"]):
            continue
        min_logprob = float(base_index_map[row_id]["min_logprob"])
        num_loss_tokens = int(base_index_map[row_id]["num_loss_tokens"])
        ranked.append((min_logprob, -num_loss_tokens, row_id))
    chosen: list[str] = []
    seen: set[str] = set()
    for _, _, row_id in sorted(ranked):
        if row_id in seen:
            continue
        chosen.append(row_id)
        seen.add(row_id)
        if len(chosen) >= limit:
            break
    return chosen


def ensure_default_row_fields(merged: dict[str, str]) -> None:
    merged.setdefault("selection_tier", "")
    merged.setdefault("template_subtype", "")
    merged.setdefault("teacher_solver_candidate", "")
    merged.setdefault("hard_score", "")
    merged.setdefault("audit_reasons", "")
    merged.setdefault("analysis_notes", "")
    merged.setdefault("symbol_query_operator", "")
    merged.setdefault("bit_query_binary", "")
    merged.setdefault("bit_structured_formula_name", "")
    merged.setdefault("bit_structured_formula_prediction", "")
    merged.setdefault("bit_structured_formula_abstract_family", "")
    merged.setdefault("bit_structured_formula_abstract_support", "")
    merged.setdefault("bit_not_structured_formula_name", "")
    merged.setdefault("bit_not_structured_formula_prediction", "")
    merged.setdefault("bit_not_structured_formula_abstract_family", "")
    merged.setdefault("bit_not_structured_formula_abstract_support", "")
    merged.setdefault("symbol_trace_teacher_tier", "")
    merged.setdefault("symbol_trace_policy", "")
    merged.setdefault("symbol_trace_contract", "")
    merged.setdefault("symbol_trace_allowed", "")
    merged.setdefault("symbol_safe_prediction", "")
    merged.setdefault("symbol_safe_prediction_count", "")
    merged.setdefault("symbol_safe_support_max", "")


def make_candidate(
    *,
    row_id: str,
    bucket: str,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    source_tags: set[str],
    proxy_failed: bool,
    validation_failed: bool,
    priority_key: tuple[Any, ...],
    require_reasoning: bool,
) -> Candidate | None:
    if require_reasoning and not (REASONING_DIR / f"{row_id}.txt").exists():
        return None
    if row_id not in train_prompts or row_id not in categories:
        return None
    merged = dict(train_prompts[row_id])
    merged["category"] = categories[row_id]
    ensure_default_row_fields(merged)
    return Candidate(
        row=merged,
        bucket=bucket,
        source_tags=tuple(sorted(source_tags)),
        proxy_failed=proxy_failed,
        validation_failed=validation_failed,
        priority_key=priority_key,
    )


def measured_bucket_for_row(row: dict[str, str]) -> str | None:
    subtype = str(row.get("template_subtype", "")).strip()
    if subtype == "bit_structured_byte_formula":
        return "binary_structured_exact_core"
    if subtype == "bit_other":
        return "binary_logic_exact"
    if subtype == "bit_permutation_inversion":
        return "binary_permutation_exact"
    if subtype == "bit_prompt_local_exact_formula":
        return "binary_prompt_local_exact"
    return None


def load_symbol_support_maps() -> dict[str, Any]:
    operator_specific_rows = load_csv_rows(SYMBOL_OPERATOR_SPECIFIC_PATH)
    manual_prompt_rows = load_csv_rows(SYMBOL_MANUAL_PROMPT_EXACT_PATH)
    glyph_training_rows = load_csv_rows(SYMBOL_GLYPH_TRAINING_PATH)
    glyph_grouped_rows = load_csv_rows(SYMBOL_GLYPH_GROUPED_PATH)
    trace_policy_rows = load_csv_rows(SYMBOL_TRACE_POLICY_PATH)
    return {
        "operator_specific": {row["id"]: row for row in operator_specific_rows},
        "manual_prompt_exact": {row["id"]: row for row in manual_prompt_rows},
        "glyph_training": {row["id"]: row for row in glyph_training_rows},
        "glyph_grouped": {row["id"]: row for row in glyph_grouped_rows},
        "trace_policy": {row["id"]: row for row in trace_policy_rows},
    }


def enrich_symbol_row(row: dict[str, str], support_maps: dict[str, Any], row_id: str) -> None:
    operator_specific = support_maps["operator_specific"].get(row_id)
    if operator_specific is not None:
        row["symbol_safe_prediction"] = str(operator_specific.get("safe_prediction", "")).strip()
        row["symbol_safe_prediction_count"] = str(operator_specific.get("safe_prediction_count", "")).strip()
        row["symbol_safe_support_max"] = str(operator_specific.get("safe_support_max", "")).strip()
    trace_row = support_maps["trace_policy"].get(row_id)
    if trace_row is not None:
        row["symbol_trace_teacher_tier"] = str(trace_row.get("symbol_trace_teacher_tier", "")).strip()
        row["symbol_trace_policy"] = str(trace_row.get("symbol_trace_policy", "")).strip()
        row["symbol_trace_contract"] = str(trace_row.get("symbol_trace_contract", "")).strip()
        row["symbol_trace_allowed"] = str(trace_row.get("symbol_trace_allowed", "")).strip()


def build_binary_candidates(
    *,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    measured: dict[str, Any],
    teacher_correctness: dict[str, bool],
) -> tuple[list[Candidate], dict[str, Any]]:
    candidates: list[Candidate] = []
    missing_reasoning_ids: list[str] = []
    teacher_mismatch_ids: dict[str, list[str]] = defaultdict(list)

    for row in load_csv_rows(TRAIN_RECOMMENDED_PATH):
        row_id = row["id"]
        bucket = measured_bucket_for_row(row)
        if bucket is None:
            continue
        if row_id in HARDBLACKLIST_IDS.get(bucket, set()):
            continue
        reasoning_exists = (REASONING_DIR / f"{row_id}.txt").exists()
        if not reasoning_exists:
            missing_reasoning_ids.append(row_id)
        teacher_correct = teacher_correctness.get(row_id, False)
        if reasoning_exists and not teacher_correct:
            teacher_mismatch_ids[bucket].append(row_id)
        tier = str(row.get("selection_tier", "")).strip()
        if tier != "verified_trace_ready":
            continue
        abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", 0), 0)
        structured_formula_safe = parse_bool(row.get("bit_structured_formula_safe", False))
        not_structured_formula_safe = parse_bool(row.get("bit_not_structured_formula_safe", False))
        current_proxy_failed = row_id in measured["current_proxy_fail_ids"]
        current_validation_failed = row_id in measured["current_validation_fail_ids"]
        mandatory_binary = row_id in MANDATORY_IDS.get(bucket, set())
        if bucket == "binary_structured_exact_core" and not (
            abstract_support >= 20
            or structured_formula_safe
            or not_structured_formula_safe
            or current_proxy_failed
            or current_validation_failed
            or mandatory_binary
        ):
            continue

        tier_priority = SELECTION_TIER_PRIORITY.get(tier, 0)
        hard_score = parse_float(row.get("hard_score", 0.0), 0.0)
        num_examples = parse_int(row.get("num_examples", 0), 0)
        prompt_len = parse_int(row.get("prompt_len_chars", 0), 0)
        outcome_score = int(measured["outcome_score"].get(row_id, 0))
        source_tags = {"train_recommended_learning_target_v1", bucket}
        if mandatory_binary:
            source_tags.add("mandatory_anchor")
        if row_id in HARD_DEFAULT1_TARGET_IDS:
            source_tags.add("hard_default1_target")
        if row_id in measured["base_to_current_proxy_improved"]:
            source_tags.add("base_to_current_proxy_improved")
        if row_id in measured["base_to_current_validation_improved"]:
            source_tags.add("base_to_current_validation_improved")
        if row_id in measured["base_to_current_proxy_regressed"]:
            source_tags.add("base_to_current_proxy_regressed")
        if row_id in measured["base_to_current_validation_regressed"]:
            source_tags.add("base_to_current_validation_regressed")
        if row_id in measured["v4_to_current_proxy_regressed"]:
            source_tags.add("v4_to_current_proxy_regressed")
        if row_id in measured["v4_to_current_validation_regressed"]:
            source_tags.add("v4_to_current_validation_regressed")
        if current_proxy_failed:
            source_tags.add("current_proxy_fail")
        if current_validation_failed:
            source_tags.add("current_validation_fail")
        if reasoning_exists:
            source_tags.add("legacy_reasoning_present")
        else:
            source_tags.add("legacy_reasoning_missing")
        if reasoning_exists and not teacher_correct:
            source_tags.add("legacy_teacher_answer_mismatch")

        priority_key = (
            -(1 if mandatory_binary else 0),
            -(1 if row_id in HARD_DEFAULT1_TARGET_IDS else 0),
            -(1 if current_proxy_failed else 0),
            -(1 if current_validation_failed else 0),
            -(1 if row_id in measured["base_to_current_proxy_improved"] else 0),
            -(1 if row_id in measured["v4_to_current_proxy_regressed"] else 0),
            -(1 if structured_formula_safe else 0),
            -(1 if not_structured_formula_safe else 0),
            -outcome_score,
            -abstract_support,
            -tier_priority,
            -hard_score,
            -num_examples,
            -prompt_len,
            row_id,
        )

        candidate = make_candidate(
            row_id=row_id,
            bucket=bucket,
            train_prompts=train_prompts,
            categories=categories,
            source_tags=source_tags,
            proxy_failed=current_proxy_failed,
            validation_failed=current_validation_failed,
            priority_key=priority_key,
            require_reasoning=False,
        )
        if candidate is None:
            continue
        copy_source_metadata(candidate.row, row)
        candidates.append(candidate)

    diagnostics = {
        "missing_reasoning_ids": sorted(set(missing_reasoning_ids)),
        "teacher_mismatch_count": sum(len(value) for value in teacher_mismatch_ids.values()),
        "teacher_mismatch_by_bucket": {
            key: sorted(value) for key, value in sorted(teacher_mismatch_ids.items())
        },
        "hardblacklist_ids": {key: sorted(value) for key, value in HARDBLACKLIST_IDS.items()},
    }
    return candidates, diagnostics


def build_symbol_numeric_candidates(
    *,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    measured: dict[str, Any],
    support_maps: dict[str, Any],
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for row in load_csv_rows(TRAIN_RECOMMENDED_PATH):
        row_id = row["id"]
        if str(row.get("template_subtype", "")).strip() != "numeric_2x2":
            continue
        tier = str(row.get("selection_tier", "")).strip()
        if tier not in SYMBOL_ALLOWED_TIERS:
            continue
        trace_row = support_maps["trace_policy"].get(row_id)
        operator_specific = support_maps["operator_specific"].get(row_id)
        manual_prompt_exact = support_maps["manual_prompt_exact"].get(row_id)
        trace_allowed = trace_row is not None and parse_bool(trace_row.get("symbol_trace_allowed", False))
        if not (
            row_id in MANDATORY_IDS["symbol_numeric_exact"]
            or operator_specific is not None
            or manual_prompt_exact is not None
            or trace_allowed
        ):
            continue

        current_proxy_failed = row_id in measured["current_proxy_fail_ids"]
        current_validation_failed = row_id in measured["current_validation_fail_ids"]
        hard_score = parse_float(row.get("hard_score", 0.0), 0.0)
        safe_support_max = parse_int(operator_specific.get("safe_support_max", 0) if operator_specific else 0, 0)
        safe_prediction_count = parse_int(operator_specific.get("safe_prediction_count", 0) if operator_specific else 0, 0)
        tier_priority = SELECTION_TIER_PRIORITY.get(tier, 0)
        trace_tier = str(trace_row.get("symbol_trace_teacher_tier", "")).strip() if trace_row else ""
        source_tags = {"symbol_numeric_exact", "train_recommended_learning_target_v1"}
        if operator_specific is not None:
            source_tags.add("symbol_operator_specific_formula_candidates_v1")
        if manual_prompt_exact is not None:
            source_tags.add("symbol_manual_prompt_exact_answer_only_candidates_v1")
        if trace_allowed:
            source_tags.add("symbol_trace_teacher_policy_v1")
        if row_id in MANDATORY_IDS["symbol_numeric_exact"]:
            source_tags.add("mandatory_anchor")
        if current_proxy_failed:
            source_tags.add("current_proxy_fail")

        priority_key = (
            -(1 if row_id in MANDATORY_IDS["symbol_numeric_exact"] else 0),
            -(1 if current_proxy_failed else 0),
            -(1 if current_validation_failed else 0),
            -(1 if operator_specific is not None else 0),
            -(1 if manual_prompt_exact is not None else 0),
            -(1 if trace_tier == "prompt_verified_trace" else 0),
            -(1 if trace_allowed else 0),
            -safe_support_max,
            -safe_prediction_count,
            -tier_priority,
            -hard_score,
            row_id,
        )

        candidate = make_candidate(
            row_id=row_id,
            bucket="symbol_numeric_exact",
            train_prompts=train_prompts,
            categories=categories,
            source_tags=source_tags,
            proxy_failed=current_proxy_failed,
            validation_failed=current_validation_failed,
            priority_key=priority_key,
            require_reasoning=False,
        )
        if candidate is None:
            continue
        copy_source_metadata(candidate.row, row)
        enrich_symbol_row(candidate.row, support_maps, row_id)
        candidates.append(candidate)
    return candidates


def build_symbol_glyph_candidates(
    *,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    measured: dict[str, Any],
    support_maps: dict[str, Any],
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for row in load_csv_rows(TRAIN_RECOMMENDED_PATH):
        row_id = row["id"]
        if str(row.get("template_subtype", "")).strip() != "glyph_len5":
            continue
        tier = str(row.get("selection_tier", "")).strip()
        if tier not in SYMBOL_ALLOWED_TIERS:
            continue
        glyph_training = support_maps["glyph_training"].get(row_id)
        glyph_grouped = support_maps["glyph_grouped"].get(row_id)
        trace_row = support_maps["trace_policy"].get(row_id)
        trace_allowed = trace_row is not None and parse_bool(trace_row.get("symbol_trace_allowed", False))
        if not (
            row_id in MANDATORY_IDS["symbol_glyph_exact"]
            or glyph_training is not None
            or glyph_grouped is not None
            or trace_allowed
        ):
            continue

        current_proxy_failed = row_id in measured["current_proxy_fail_ids"]
        current_validation_failed = row_id in measured["current_validation_fail_ids"]
        hard_score = parse_float(row.get("hard_score", 0.0), 0.0)
        group_combo_count = parse_int(glyph_grouped.get("group_combo_count", 0) if glyph_grouped else 0, 0)
        feasible_group_combo_count = parse_int(glyph_grouped.get("feasible_group_combo_count", 0) if glyph_grouped else 0, 0)
        tier_priority = SELECTION_TIER_PRIORITY.get(tier, 0)
        source_tags = {"symbol_glyph_exact", "train_recommended_learning_target_v1"}
        if glyph_training is not None:
            source_tags.add("symbol_glyph_training_answer_only_candidates_v1")
        if glyph_grouped is not None:
            source_tags.add("symbol_glyph_grouped_exact_answer_only_candidates_v1")
        if trace_allowed:
            source_tags.add("symbol_trace_teacher_policy_v1")
        if row_id in MANDATORY_IDS["symbol_glyph_exact"]:
            source_tags.add("mandatory_anchor")
        if current_proxy_failed:
            source_tags.add("current_proxy_fail")

        priority_key = (
            -(1 if row_id in MANDATORY_IDS["symbol_glyph_exact"] else 0),
            -(1 if current_proxy_failed else 0),
            -(1 if current_validation_failed else 0),
            -(1 if glyph_training is not None else 0),
            -(1 if trace_allowed else 0),
            -feasible_group_combo_count,
            -group_combo_count,
            -tier_priority,
            -hard_score,
            row_id,
        )

        candidate = make_candidate(
            row_id=row_id,
            bucket="symbol_glyph_exact",
            train_prompts=train_prompts,
            categories=categories,
            source_tags=source_tags,
            proxy_failed=current_proxy_failed,
            validation_failed=current_validation_failed,
            priority_key=priority_key,
            require_reasoning=False,
        )
        if candidate is None:
            continue
        copy_source_metadata(candidate.row, row)
        enrich_symbol_row(candidate.row, support_maps, row_id)
        candidates.append(candidate)
    return candidates


def build_guardrail_candidates(
    *,
    train_prompts: dict[str, dict[str, str]],
    categories: dict[str, str],
    base_index_map: dict[str, dict[str, Any]],
    bucket_limits: dict[str, int],
) -> list[Candidate]:
    support_specs = [
        ("surface_numeral_boxed", "numeral", lambda answer: True),
        ("surface_cipher_boxed", "cipher", lambda answer: True),
        ("surface_unit_tail", "unit_conversion", lambda answer: True),
        ("easy_gravity_fragile", "gravity", lambda answer: True),
    ]
    candidates: list[Candidate] = []
    for bucket, category_name, predicate in support_specs:
        ids = choose_guardrail_ids(
            train_prompts=train_prompts,
            categories=categories,
            base_index_map=base_index_map,
            limit=bucket_limits[bucket],
            category_name=category_name,
            answer_predicate=predicate,
        )
        for rank, row_id in enumerate(ids):
            index_row = base_index_map.get(row_id, {})
            min_logprob = parse_float(index_row.get("min_logprob"), -999.0)
            num_loss_tokens = parse_int(index_row.get("num_loss_tokens"), 0)
            source_tags = {bucket, "base_snapshot_guardrail"}
            priority_key = (min_logprob, -num_loss_tokens, rank, row_id)
            candidate = make_candidate(
                row_id=row_id,
                bucket=bucket,
                train_prompts=train_prompts,
                categories=categories,
                source_tags=source_tags,
                proxy_failed=False,
                validation_failed=False,
                priority_key=priority_key,
                require_reasoning=False,
            )
            if candidate is not None:
                candidates.append(candidate)
    return candidates


def build_budgeted_candidates(bucket_limits: dict[str, int]) -> tuple[list[Candidate], dict[str, Any]]:
    train_prompts = load_train_prompts()
    categories = load_problem_categories()
    base_index_map = load_base_snapshot_index_map()
    measured = load_measured_signals()
    teacher_correctness = load_teacher_correctness()
    support_maps = load_symbol_support_maps()

    binary_candidates, binary_diagnostics = build_binary_candidates(
        train_prompts=train_prompts,
        categories=categories,
        measured=measured,
        teacher_correctness=teacher_correctness,
    )
    numeric_candidates = build_symbol_numeric_candidates(
        train_prompts=train_prompts,
        categories=categories,
        measured=measured,
        support_maps=support_maps,
    )
    glyph_candidates = build_symbol_glyph_candidates(
        train_prompts=train_prompts,
        categories=categories,
        measured=measured,
        support_maps=support_maps,
    )
    guardrail_candidates = build_guardrail_candidates(
        train_prompts=train_prompts,
        categories=categories,
        base_index_map=base_index_map,
        bucket_limits=bucket_limits,
    )

    candidates = binary_candidates + numeric_candidates + glyph_candidates + guardrail_candidates
    bucket_rank = {name: index for index, name in enumerate(BUCKET_ORDER)}
    diagnostics = {
        "base_to_current_proxy_improved": len(measured["base_to_current_proxy_improved"]),
        "base_to_current_proxy_regressed": len(measured["base_to_current_proxy_regressed"]),
        "base_to_current_validation_improved": len(measured["base_to_current_validation_improved"]),
        "base_to_current_validation_regressed": len(measured["base_to_current_validation_regressed"]),
        "v4_to_current_proxy_improved": len(measured["v4_to_current_proxy_improved"]),
        "v4_to_current_proxy_regressed": len(measured["v4_to_current_proxy_regressed"]),
        "v4_to_current_validation_improved": len(measured["v4_to_current_validation_improved"]),
        "v4_to_current_validation_regressed": len(measured["v4_to_current_validation_regressed"]),
        "current_proxy_fail_ids": len(measured["current_proxy_fail_ids"]),
        "current_validation_fail_ids": len(measured["current_validation_fail_ids"]),
        "binary_candidates": len(binary_candidates),
        "symbol_numeric_candidates": len(numeric_candidates),
        "symbol_glyph_candidates": len(glyph_candidates),
        "guardrail_candidates": len(guardrail_candidates),
        "mandatory_ids": {key: sorted(value) for key, value in MANDATORY_IDS.items()},
        "binary_diagnostics": binary_diagnostics,
    }
    return sorted(candidates, key=lambda item: (bucket_rank[item.bucket], item.priority_key)), diagnostics


def select_candidates(candidates: list[Candidate], bucket_limits: dict[str, int]) -> list[Candidate]:
    selected: list[Candidate] = []
    counts = Counter()
    seen_ids: set[str] = set()

    def add_candidate(candidate: Candidate) -> None:
        key = candidate.row["id"]
        if key in seen_ids:
            return
        selected.append(candidate)
        counts[candidate.bucket] += 1
        seen_ids.add(key)

    structured_candidates = [candidate for candidate in candidates if candidate.bucket == "binary_structured_exact_core"]
    structured_priority_limit = max(0, bucket_limits["binary_structured_exact_core"] - STRUCTURED_SPILLOVER_SLOTS)
    structured_family_counts: Counter[str] = Counter()
    for candidate in structured_candidates:
        if candidate.row["id"] in MANDATORY_IDS["binary_structured_exact_core"]:
            if counts["binary_structured_exact_core"] >= bucket_limits["binary_structured_exact_core"]:
                break
            add_candidate(candidate)
            structured_family_counts[binary_family_key(candidate.row)] += 1
    family_candidates: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in structured_candidates:
        if candidate.row["id"] in seen_ids:
            continue
        family_candidates[binary_family_key(candidate.row)].append(candidate)
    for family in PRIORITY_BINARY_FAMILIES:
        quota = PRIORITY_BINARY_FAMILY_QUOTAS[family]
        for candidate in family_candidates.get(family, []):
            if counts["binary_structured_exact_core"] >= structured_priority_limit:
                break
            if structured_family_counts[family] >= quota:
                break
            add_candidate(candidate)
            structured_family_counts[family] += 1
    for candidate in structured_candidates:
        if counts["binary_structured_exact_core"] >= bucket_limits["binary_structured_exact_core"]:
            break
        add_candidate(candidate)

    for bucket in BUCKET_ORDER:
        if bucket == "binary_structured_exact_core":
            continue
        for candidate in candidates:
            if candidate.bucket != bucket:
                continue
            if counts[bucket] >= bucket_limits[bucket]:
                break
            add_candidate(candidate)
    return selected


def build_overlay_rows(selected: list[Candidate], repeat_counts: dict[str, int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    for candidate in selected:
        row_id = candidate.row["id"]
        variants = build_supervision_variants(candidate, base_variant_count=repeat_counts[candidate.bucket])
        repeat_count = len(variants)
        base = {
            "id": row_id,
            "category": candidate.row["category"],
            "bucket": candidate.bucket,
            "prompt": candidate.row["prompt"],
            "answer": candidate.row["answer"],
            "completion_text": variants[0]["completion_text"],
            "selection_tier": candidate.row["selection_tier"],
            "template_subtype": candidate.row["template_subtype"],
            "teacher_solver_candidate": candidate.row["teacher_solver_candidate"],
            "source_tags": list(candidate.source_tags),
            "proxy_failed": candidate.proxy_failed,
            "validation_failed": candidate.validation_failed,
            "recommended_repeat_count": repeat_count,
            "assistant_styles": [variant["assistant_style"] for variant in variants],
            "hard_score": parse_float(candidate.row["hard_score"], 0.0),
            "audit_reasons": candidate.row["audit_reasons"],
            "analysis_notes": candidate.row["analysis_notes"],
            "symbol_query_operator": candidate.row["symbol_query_operator"],
            "symbol_trace_teacher_tier": candidate.row.get("symbol_trace_teacher_tier", ""),
            "symbol_trace_policy": candidate.row.get("symbol_trace_policy", ""),
            "symbol_trace_contract": candidate.row.get("symbol_trace_contract", ""),
            "symbol_safe_prediction": candidate.row.get("symbol_safe_prediction", ""),
            "symbol_safe_prediction_count": candidate.row.get("symbol_safe_prediction_count", ""),
            "symbol_safe_support_max": candidate.row.get("symbol_safe_support_max", ""),
            "bit_query_binary": candidate.row.get("bit_query_binary", ""),
            "bit_structured_formula_name": candidate.row["bit_structured_formula_name"],
            "bit_structured_formula_prediction": candidate.row["bit_structured_formula_prediction"],
            "bit_structured_formula_abstract_family": candidate.row["bit_structured_formula_abstract_family"],
            "bit_not_structured_formula_name": candidate.row.get("bit_not_structured_formula_name", ""),
            "bit_not_structured_formula_prediction": candidate.row.get("bit_not_structured_formula_prediction", ""),
            "bit_not_structured_formula_abstract_family": candidate.row.get("bit_not_structured_formula_abstract_family", ""),
            "binary_family_key": binary_family_key(candidate.row),
        }
        unique_rows.append(base)
        for overlay_index, variant in enumerate(variants, start=1):
            repeated = dict(base)
            repeated["completion_text"] = variant["completion_text"]
            repeated["assistant_style"] = variant["assistant_style"]
            repeated["supervision_role"] = variant["supervision_role"]
            repeated["overlay_instance"] = overlay_index
            repeated_rows.append(repeated)
    return unique_rows, repeated_rows


def validate_canonical_v8(
    *,
    unique_rows: list[dict[str, Any]],
    repeated_rows: list[dict[str, Any]],
    training_bundle: dict[str, Any] | None,
    bucket_limits: dict[str, int],
) -> dict[str, Any]:
    unique_by_bucket: dict[str, set[str]] = defaultdict(set)
    for row in unique_rows:
        unique_by_bucket[row["bucket"]].add(row["id"])
    mandatory_missing: dict[str, list[str]] = {}
    for bucket, ids in MANDATORY_IDS.items():
        missing = sorted(set(ids) - unique_by_bucket.get(bucket, set()))
        if missing:
            mandatory_missing[bucket] = missing

    binary_selected = [row for row in unique_rows if row["bucket"].startswith("binary_")]
    symbol_selected = [row for row in unique_rows if row["bucket"].startswith("symbol_")]
    guardrail_selected = [row for row in unique_rows if row["bucket"].startswith("surface_") or row["bucket"] == "easy_gravity_fragile"]
    repeated_style_counts = Counter(row["assistant_style"] for row in repeated_rows)
    repeated_bucket_style_counts = Counter(f"{row['bucket']}::{row['assistant_style']}" for row in repeated_rows)
    binary_nonverified_ids = sorted(
        row["id"] for row in binary_selected if str(row.get("selection_tier", "")).strip() != "verified_trace_ready"
    )
    symbol_hard_present = sorted(
        row["id"]
        for row in symbol_selected
        if row["id"] in (MANDATORY_IDS["symbol_numeric_exact"] | MANDATORY_IDS["symbol_glyph_exact"])
    )
    answer_in_think = sorted(
        {
            row["id"]
            for row in repeated_rows
            if row["answer"] in extract_think_body(row["completion_text"])
        }
    )
    binary_max_think_lines = max(
        (nonempty_line_count(extract_think_body(row["completion_text"])) for row in repeated_rows if row["bucket"].startswith("binary_")),
        default=0,
    )
    symbol_max_think_lines = max(
        (nonempty_line_count(extract_think_body(row["completion_text"])) for row in repeated_rows if row["bucket"].startswith("symbol_")),
        default=0,
    )
    surface_max_think_lines = max(
        (
            nonempty_line_count(extract_think_body(row["completion_text"]))
            for row in repeated_rows
            if not row["bucket"].startswith("binary_") and not row["bucket"].startswith("symbol_")
        ),
        default=0,
    )
    allocation = {
        "bit_unique": len(binary_selected),
        "symbol_unique": len(symbol_selected),
        "guardrail_unique": len(guardrail_selected),
        "total_unique": len(unique_rows),
    }
    allocation["bit_share"] = round(allocation["bit_unique"] / allocation["total_unique"], 4) if allocation["total_unique"] else 0.0
    allocation["symbol_share"] = round(allocation["symbol_unique"] / allocation["total_unique"], 4) if allocation["total_unique"] else 0.0
    allocation["guardrail_share"] = round(allocation["guardrail_unique"] / allocation["total_unique"], 4) if allocation["total_unique"] else 0.0

    errors: list[str] = []
    if mandatory_missing:
        errors.append("mandatory anchor が欠落している")
    if binary_nonverified_ids:
        errors.append("binary lane に verified_trace_ready 以外が混入している")
    if answer_in_think:
        errors.append("think 内に最終 answer が再掲されている")
    if binary_max_think_lines > 4:
        errors.append("binary think 行数が長すぎる")
    if symbol_max_think_lines > 4:
        errors.append("symbol think 行数が長すぎる")
    if surface_max_think_lines > 3:
        errors.append("guardrail think 行数が長すぎる")
    if allocation["guardrail_share"] > 0.1:
        errors.append("guardrail の比率が高すぎる")
    if training_bundle is not None and int(training_bundle.get("retokenized_overlay_problem_count", 0)) <= 0:
        errors.append("overlay が retokenize されていない")

    return {
        "canonical_checks_passed": not errors,
        "errors": errors,
        "mandatory_missing": mandatory_missing,
        "binary_nonverified_ids": binary_nonverified_ids,
        "symbol_hard_present": symbol_hard_present,
        "repeated_style_counts": dict(sorted(repeated_style_counts.items())),
        "repeated_bucket_style_counts": dict(sorted(repeated_bucket_style_counts.items())),
        "binary_max_think_lines": binary_max_think_lines,
        "symbol_max_think_lines": symbol_max_think_lines,
        "surface_max_think_lines": surface_max_think_lines,
        "allocation": allocation,
        "configured_bucket_limits": dict(bucket_limits),
        "hard_default1_target_ids": sorted(HARD_DEFAULT1_TARGET_IDS),
    }


def build_training_bundle(
    repeated_rows: list[dict[str, Any]],
    bundle_path: Path,
) -> dict[str, Any]:
    base_rows, base_examples, batch_size = load_base_snapshot_examples()
    filtered_base_rows = [
        row for row in base_rows if str(row["problem_id"]).split("-p")[0] not in BASE_EXCLUDED_IDS
    ]
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    existing_steps = [int(row["step"]) for row in filtered_base_rows]
    base_step_count = max(existing_steps) + 1 if existing_steps else 0

    total_examples = 0
    total_tokens = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()
    overlay_by_bucket: Counter[str] = Counter()
    overlay_tokens_by_bucket: Counter[str] = Counter()
    overlay_examples_by_style: Counter[str] = Counter()
    retokenized_overlay_ids: set[str] = set()

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": "v20_corrective_corpus_v8_mainline",
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "base_snapshot_config": read_json(BASE_SNAPSHOT_CONFIG_PATH),
        "bundle_path": relative_to_repo(bundle_path),
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "note": (
            "Single-file training bundle for v8. Keeps the 04-08-16-14 base snapshot, "
            "adds a BIT-core exact overlay focused on binary frontier rows, "
            "adds targeted symbol exact lanes for numeric_2x2 and glyph_len5, "
            "and retains only a minimal easy-family guardrail."
        ),
    }

    with bundle_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False) + "\n")

        for row in filtered_base_rows:
            problem_id = str(row["problem_id"])
            segment = str(row["segment"])
            entry = base_examples[(problem_id, segment)]
            tokens = entry["tokens"]
            mask = entry["mask"]
            category = str(row["category"])
            payload = {
                "record_type": "example",
                "example_id": problem_id,
                "source_problem_id": problem_id,
                "source": "base_snapshot",
                "segment": segment,
                "category": category,
                "step": int(row["step"]),
                "num_loss_tokens": int(row["num_loss_tokens"]),
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[category] += 1

        for overlay_offset, row in enumerate(repeated_rows):
            problem_id = str(row["id"])
            tokens, mask = tokenize_overlay_example(
                prompt=str(row["prompt"]),
                completion_text=str(row["completion_text"]),
            )
            category = str(row["category"])
            num_loss_tokens = sum(mask)
            retokenized_overlay_ids.add(problem_id)
            overlay_step = base_step_count + (overlay_offset // batch_size)
            payload = {
                "record_type": "example",
                "example_id": f"{problem_id}#overlay-{row['overlay_instance']}",
                "source_problem_id": problem_id,
                "source": "corrective_overlay",
                "segment": "synthetic.jsonl",
                "category": category,
                "step": overlay_step,
                "num_loss_tokens": num_loss_tokens,
                "bucket": row["bucket"],
                "overlay_instance": int(row["overlay_instance"]),
                "assistant_style": row["assistant_style"],
                "supervision_role": row["supervision_role"],
                "recommended_repeat_count": int(row["recommended_repeat_count"]),
                "proxy_failed": bool(row["proxy_failed"]),
                "validation_failed": bool(row["validation_failed"]),
                "source_tags": row["source_tags"],
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[category] += 1
            overlay_by_bucket[row["bucket"]] += 1
            overlay_tokens_by_bucket[row["bucket"]] += len(tokens)
            overlay_examples_by_style[row["assistant_style"]] += 1

    total_steps = base_step_count + ((len(repeated_rows) + batch_size - 1) // batch_size)
    return {
        "path": relative_to_repo(bundle_path),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "format": "nemotron_single_file_training_bundle_v1",
        "base_examples": len(filtered_base_rows),
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "overlay_examples": len(repeated_rows),
        "total_examples": total_examples,
        "batch_size": batch_size,
        "total_steps": total_steps,
        "total_tokens": total_tokens,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_seq_len": max_seq_len,
        "overlay_by_bucket": dict(overlay_by_bucket),
        "overlay_tokens_by_bucket": dict(overlay_tokens_by_bucket),
        "overlay_examples_by_style": dict(sorted(overlay_examples_by_style.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "retokenized_overlay_problem_ids": sorted(retokenized_overlay_ids),
        "retokenized_overlay_problem_count": len(retokenized_overlay_ids),
        "retokenized_overlay_example_count": len(repeated_rows),
    }


def build_summary(
    *,
    selected: list[Candidate],
    unique_rows: list[dict[str, Any]],
    repeated_rows: list[dict[str, Any]],
    diagnostics: dict[str, Any],
    canonical_validation: dict[str, Any],
    training_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    selected_by_bucket = Counter(candidate.bucket for candidate in selected)
    repeated_by_bucket = Counter(row["bucket"] for row in repeated_rows)
    source_counts = Counter(tag for row in unique_rows for tag in row["source_tags"])
    selected_ids = {row["id"] for row in unique_rows}
    binary_hard_hits = sorted(
        row_id
        for row_id in (
            MANDATORY_IDS["binary_structured_exact_core"]
            | MANDATORY_IDS["binary_logic_exact"]
            | MANDATORY_IDS["binary_permutation_exact"]
            | MANDATORY_IDS["binary_prompt_local_exact"]
        )
        if row_id in selected_ids
    )
    symbol_hard_hits = sorted(
        row_id
        for row_id in (MANDATORY_IDS["symbol_numeric_exact"] | MANDATORY_IDS["symbol_glyph_exact"])
        if row_id in selected_ids
    )
    return {
        "version": "v20_corrective_corpus_v8_mainline",
        "created_at": utc_now(),
        "readme_eval_contract": verify_readme_eval_contract(),
        "strategy_note": relative_to_repo(STRATEGY_NOTE_PATH),
        "inputs": {
            "train_recommended_learning_target_v1": relative_to_repo(TRAIN_RECOMMENDED_PATH),
            "symbol_operator_specific_formula_candidates_v1": relative_to_repo(SYMBOL_OPERATOR_SPECIFIC_PATH),
            "symbol_manual_prompt_exact_answer_only_candidates_v1": relative_to_repo(SYMBOL_MANUAL_PROMPT_EXACT_PATH),
            "symbol_glyph_training_answer_only_candidates_v1": relative_to_repo(SYMBOL_GLYPH_TRAINING_PATH),
            "symbol_glyph_grouped_exact_answer_only_candidates_v1": relative_to_repo(SYMBOL_GLYPH_GROUPED_PATH),
            "symbol_trace_teacher_policy_v1": relative_to_repo(SYMBOL_TRACE_POLICY_PATH),
            "base_validation": relative_to_repo(RESULT_BASE_VALIDATION_PATH),
            "current_validation": relative_to_repo(RESULT_CURRENT_VALIDATION_PATH),
            "v4_validation": relative_to_repo(RESULT_V4_VALIDATION_PATH),
            "base_proxy_row_level": relative_to_repo(RESULT_BASE_PROXY_PATH),
            "current_proxy_row_level": relative_to_repo(RESULT_CURRENT_PROXY_PATH),
            "v4_proxy_row_level": relative_to_repo(RESULT_V4_PROXY_PATH),
        },
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(selected_by_bucket),
        "repeated_by_bucket": dict(repeated_by_bucket),
        "source_tag_counts": dict(source_counts),
        "proxy_failed_selected": sum(1 for row in unique_rows if row["proxy_failed"]),
        "validation_failed_selected": sum(1 for row in unique_rows if row["validation_failed"]),
        "binary_hard_hits": binary_hard_hits,
        "symbol_hard_hits": symbol_hard_hits,
        "diagnostics": diagnostics,
        "canonical_validation": canonical_validation,
        "training_bundle": training_bundle,
    }


def render_results_markdown(summary: dict[str, Any]) -> str:
    selected_by_bucket = summary["selected_by_bucket"]
    allocation = summary["canonical_validation"]["allocation"]
    bundle = summary.get("training_bundle") or {}
    lines = [
        "# v20_corrective_corpus_v8_mainline",
        "",
        f"- created_at: {summary['created_at']}",
        f"- strategy note: {summary['strategy_note']}",
        "- README basis: deterministic boxed-answer evaluation, bit_manipulation as primary score source, tokenization-aware supervision, and symbol exact-transduction weaknesses called out in the A-Open note.",
        "- status: bundle generated; model score not yet measured.",
        "",
        "## Strategy",
        "",
        "- One major run only: BIT-core mainline with targeted symbol exact lanes and minimal easy-family guardrails.",
        "- Allocation target: roughly 75-80% BIT, 15-20% symbol, <=5% guardrail.",
        "- Latest reference run remains v7-1; v8 here is a new data-generation branch, not a score claim.",
        "",
        "## Selected Unique Rows",
        "",
    ]
    for bucket in BUCKET_ORDER:
        lines.append(f"- {bucket}: {selected_by_bucket.get(bucket, 0)}")
    lines.extend(
        [
            "",
            "## Allocation Check",
            "",
            f"- bit_unique: {allocation['bit_unique']} ({allocation['bit_share']:.2%})",
            f"- symbol_unique: {allocation['symbol_unique']} ({allocation['symbol_share']:.2%})",
            f"- guardrail_unique: {allocation['guardrail_unique']} ({allocation['guardrail_share']:.2%})",
            f"- total_unique: {allocation['total_unique']}",
            "",
            "## Hard Anchors",
            "",
            f"- binary_hard_hits: {len(summary['binary_hard_hits'])}",
            f"- symbol_hard_hits: {len(summary['symbol_hard_hits'])}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle.get('path', 'not_written')}",
            f"- base_examples: {bundle.get('base_examples', 0)}",
            f"- overlay_examples: {bundle.get('overlay_examples', 0)}",
            f"- total_examples: {bundle.get('total_examples', 0)}",
            f"- total_tokens: {bundle.get('total_tokens', 0)}",
            f"- max_seq_len: {bundle.get('max_seq_len', 0)}",
            "",
            "## Canonical Validation",
            "",
            f"- passed: {summary['canonical_validation']['canonical_checks_passed']}",
            f"- errors: {summary['canonical_validation']['errors']}",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_bucket_limits(arg: str | None) -> dict[str, int]:
    limits = dict(DEFAULT_BUCKET_LIMITS)
    if not arg:
        return limits
    for chunk in arg.split(","):
        text = chunk.strip()
        if not text:
            continue
        key, value = text.split("=", 1)
        if key not in limits:
            raise SystemExit(f"Unknown bucket in --bucket-limits: {key}")
        limits[key] = int(value)
    return limits


def parse_repeat_counts(arg: str | None) -> dict[str, int]:
    counts = dict(DEFAULT_REPEAT_COUNTS)
    if not arg:
        return counts
    for chunk in arg.split(","):
        text = chunk.strip()
        if not text:
            continue
        key, value = text.split("=", 1)
        if key not in counts:
            raise SystemExit(f"Unknown bucket in --repeat-counts: {key}")
        counts[key] = int(value)
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the v8 mainline corrective corpus. "
            "This keeps the 04-08-16-14 base snapshot, "
            "adds a BIT-core exact overlay, adds targeted symbol exact lanes, "
            "and keeps only a minimal easy-family guardrail."
        )
    )
    parser.add_argument("--run-name", default="v8_mainline_default")
    parser.add_argument("--bucket-limits", default=None)
    parser.add_argument("--repeat-counts", default=None)
    parser.add_argument("--write-training-bundle", action="store_true")
    parser.add_argument("--bundle-path", type=Path, default=DEFAULT_BUNDLE_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bucket_limits = parse_bucket_limits(args.bucket_limits)
    repeat_counts = parse_repeat_counts(args.repeat_counts)

    candidates, diagnostics = build_budgeted_candidates(bucket_limits)
    selected = select_candidates(candidates, bucket_limits=bucket_limits)
    unique_rows, repeated_rows = build_overlay_rows(selected, repeat_counts=repeat_counts)
    training_bundle = None
    if args.write_training_bundle:
        training_bundle = build_training_bundle(repeated_rows=repeated_rows, bundle_path=args.bundle_path.resolve())
    canonical_validation = validate_canonical_v8(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        training_bundle=training_bundle,
        bucket_limits=bucket_limits,
    )
    if not canonical_validation["canonical_checks_passed"]:
        raise SystemExit(
            "Canonical v8 validation failed: " + "; ".join(canonical_validation["errors"])
        )

    run_root = OUTPUT_ROOT / args.run_name
    artifacts_dir = run_root / "artifacts"
    reports_dir = run_root / "reports"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    selection_rows = []
    for row in unique_rows:
        selection_rows.append(
            {
                "id": row["id"],
                "category": row["category"],
                "bucket": row["bucket"],
                "selection_tier": row["selection_tier"],
                "template_subtype": row["template_subtype"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "recommended_repeat_count": row["recommended_repeat_count"],
                "assistant_styles": "|".join(row["assistant_styles"]),
                "proxy_failed": row["proxy_failed"],
                "validation_failed": row["validation_failed"],
                "hard_score": row["hard_score"],
                "binary_family_key": row["binary_family_key"],
                "bit_query_binary": row["bit_query_binary"],
                "symbol_query_operator": row["symbol_query_operator"],
                "symbol_trace_teacher_tier": row["symbol_trace_teacher_tier"],
                "symbol_trace_policy": row["symbol_trace_policy"],
                "symbol_trace_contract": row["symbol_trace_contract"],
                "symbol_safe_prediction": row["symbol_safe_prediction"],
                "symbol_safe_prediction_count": row["symbol_safe_prediction_count"],
                "symbol_safe_support_max": row["symbol_safe_support_max"],
                "source_tags": "|".join(row["source_tags"]),
            }
        )

    summary = build_summary(
        selected=selected,
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        canonical_validation=canonical_validation,
        training_bundle=training_bundle,
    )

    write_csv(
        artifacts_dir / "corrective_selection.csv",
        selection_rows,
        fieldnames=[
            "id",
            "category",
            "bucket",
            "selection_tier",
            "template_subtype",
            "teacher_solver_candidate",
            "recommended_repeat_count",
            "assistant_styles",
            "proxy_failed",
            "validation_failed",
            "hard_score",
            "binary_family_key",
            "bit_query_binary",
            "symbol_query_operator",
            "symbol_trace_teacher_tier",
            "symbol_trace_policy",
            "symbol_trace_contract",
            "symbol_safe_prediction",
            "symbol_safe_prediction_count",
            "symbol_safe_support_max",
            "source_tags",
        ],
    )
    write_jsonl(artifacts_dir / "corrective_overlay_unique.jsonl", unique_rows)
    write_jsonl(artifacts_dir / "corrective_overlay_repeated.jsonl", repeated_rows)
    write_json(artifacts_dir / "corrective_overlay_summary.json", summary)

    markdown = render_results_markdown(summary)
    (reports_dir / "v20_corrective_corpus_v8_mainline_summary.md").write_text(markdown, encoding="utf-8")
    RESULTS_MD.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()