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
RESULTS_MD = VERSION_ROOT / "v20_corrective_corpus_v5a_mainline-results.md"

README_PATH = REPO_ROOT / "README.md"
TRAIN_RECOMMENDED_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_recommended_learning_target_v1.csv"
SYMBOL_MANUAL_QUEUE_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "symbol_manual_audit_queue_v1.csv"
TRAIN_CSV_PATH = REPO_ROOT / "data" / "train.csv"
PROBLEMS_PATH = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "problems.jsonl"
REASONING_DIR = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "reasoning"
TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
DEFAULT_BUNDLE_PATH = TRAINING_SFT_ROOT / "v20_corrective_corpus_v5a_mainline_bundle.jsonl"
MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)
TOKEN_LIMIT = 8192
RESULT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "result"
RESULT_BASE_VALIDATION_PATH = RESULT_ROOT / "results-v20" / "validation.csv"
RESULT_CURRENT_VALIDATION_PATH = RESULT_ROOT / "results-v4" / "validation.csv"
RESULT_V3_VALIDATION_PATH = RESULT_ROOT / "results-v3" / "validation.csv"
RESULT_BASE_RESULTS_PATH = RESULT_ROOT / "results-v20" / "results.csv"
RESULT_CURRENT_RESULTS_PATH = RESULT_ROOT / "results-v4" / "results.csv"
RESULT_BASE_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval_v20" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"
RESULT_CURRENT_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval-v4" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"
RESULT_V3_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval-v3" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"

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
    "binary_verified_core",
    "surface_numeral_boxed",
    "surface_cipher_boxed",
    "surface_unit_tail",
    "easy_gravity_fragile",
)

DEFAULT_BUCKET_LIMITS = {
    "binary_verified_core": 192,
    "surface_numeral_boxed": 28,
    "surface_cipher_boxed": 6,
    "surface_unit_tail": 6,
    "easy_gravity_fragile": 6,
}

DEFAULT_REPEAT_COUNTS = {
    "binary_verified_core": 3,
    "surface_numeral_boxed": 2,
    "surface_cipher_boxed": 2,
    "surface_unit_tail": 2,
    "easy_gravity_fragile": 1,
}

SELECTION_TIER_PRIORITY = {
    "verified_trace_ready": 3,
    "manual_audit_priority": 2,
    "answer_only_keep": 1,
}


@dataclass
class Candidate:
    row: dict[str, str]
    bucket: str
    source_tags: tuple[str, ...]
    proxy_failed: bool
    validation_failed: bool
    priority_key: tuple[Any, ...]


MEASURED_MANDATORY_IDS = {
    "binary_verified_core": {
        "0520a6ec",
        "0a50c4a8",
        "17fd9612",
        "59c78e51",
        "8e5d6fe6",
        "0dd5caf4",
        "b9500f41",
        "c30a782a",
        "fa67da07",
    },
    "surface_numeral_boxed": {
        "00d9f682",
        "018d465c",
        "02e4851e",
        "039921f2",
        "03bf2ac0",
        "05992f55",
        "07214cbb",
        "076fda72",
        "078e4ee7",
        "07c3a547",
        "0805b912",
        "081ad3f3",
        "09b26a48",
        "0aa2c5bf",
        "0adca57b",
        "0b2877ce",
        "0bb4cc45",
        "0c4e7430",
        "0c9b74fc",
        "0cce92d8",
        "0cddfe30",
        "0e50e177",
        "0ea93e44",
        "0f067a67",
        "0fb02b67",
        "105255db",
        "10effb36",
        "1112ec96",
        "1145fa6f",
        "1347c69f",
        "17288b98",
        "18840879",
        "188fe6d4",
        "18997574",
    },
    "surface_cipher_boxed": {"0184a864", "018c6f61", "13db9692", "16642d10"},
    "surface_unit_tail": {"0a0698b2", "077cfc0b", "626d6c5f"},
    "easy_gravity_fragile": {"0fd289d8"},
}

HARDBLACKLIST_IDS = {
    "binary_verified_core": {"2817d770", "06b5da9f", "6a333ed6"},
}

BASE_EXCLUDED_IDS = {"ef2fe526"}


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def read_csv_map(path: Path, key: str = "id") -> dict[str, dict[str, str]]:
    return {row[key]: row for row in load_csv_rows(path)}


def load_base_snapshot_index_map() -> dict[str, dict[str, Any]]:
    rows = load_base_snapshot_index_rows()
    return {str(row["problem_id"]): row for row in rows}


def answer_has_symbolic_prefix(answer: str) -> bool:
    text = str(answer).strip()
    return bool(text) and not text[0].isalnum()


def answer_is_symbolic_crypt(answer: str) -> bool:
    return bool(re.search(r"[^A-Za-z0-9 ]", str(answer)))


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
    rows = {}
    for row in load_csv_rows(TRAIN_CSV_PATH):
        rows[row["id"]] = row
    return rows


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
    path = REASONING_DIR / f"{row_id}.txt"
    return path.read_text(encoding="utf-8")


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


def build_completion_text(reasoning_text: str, answer: str) -> str:
    boxed_match = re.findall(r"\\boxed\{([^}]*)\}", reasoning_text)
    reasoning_answer = boxed_match[-1] if boxed_match else answer
    return f"{reasoning_text}\n</think>\n\\boxed{{{reasoning_answer}}}<|im_end|>"


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


def bucket_for_row(row: dict[str, str]) -> str | None:
    family_short = str(row.get("template_main_label", "") or row.get("family_short", "")).strip()
    subtype = str(row.get("template_subtype", "")).strip()
    if family_short == "binary" and subtype == "bit_structured_byte_formula":
        return "bit_structured_byte_formula"
    if family_short == "binary" and subtype == "bit_other":
        return "bit_other"
    if family_short == "symbol" and subtype == "numeric_2x2":
        return "symbol_numeric_2x2"
    if family_short == "symbol" and subtype == "glyph_len5":
        return "symbol_glyph_len5"
    return None


def measured_bucket_for_row(row: dict[str, str]) -> str | None:
    subtype = str(row.get("template_subtype", "")).strip()
    if subtype in {"bit_structured_byte_formula", "bit_other", "bit_permutation_inversion"}:
        return "binary_verified_core"
    return None


def is_surface_box_regression(previous_row: dict[str, str], current_row: dict[str, str]) -> bool:
    if previous_row["correct"] != "True" or current_row["correct"] != "False":
        return False
    output = current_row["output"]
    return "\\box" in output and "\\boxed" not in output


def load_measured_signals() -> dict[str, Any]:
    base_validation = read_csv_map(RESULT_BASE_VALIDATION_PATH)
    current_validation = read_csv_map(RESULT_CURRENT_VALIDATION_PATH)
    v3_validation = read_csv_map(RESULT_V3_VALIDATION_PATH)
    base_proxy = read_csv_map(RESULT_BASE_PROXY_PATH)
    current_proxy = read_csv_map(RESULT_CURRENT_PROXY_PATH)
    v3_proxy = read_csv_map(RESULT_V3_PROXY_PATH)

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

    v3_to_current_validation_improved: set[str] = set()
    v3_to_current_validation_regressed: set[str] = set()
    for row_id in sorted(set(v3_validation) & set(current_validation)):
        old_correct = v3_validation[row_id]["correct"] == "True"
        new_correct = current_validation[row_id]["correct"] == "True"
        if (not old_correct) and new_correct:
            v3_to_current_validation_improved.add(row_id)
        elif old_correct and (not new_correct):
            v3_to_current_validation_regressed.add(row_id)

    v3_to_current_proxy_improved: set[str] = set()
    v3_to_current_proxy_regressed: set[str] = set()
    for row_id in sorted(set(v3_proxy) & set(current_proxy)):
        old_correct = v3_proxy[row_id]["is_correct"] == "True"
        new_correct = current_proxy[row_id]["is_correct"] == "True"
        if (not old_correct) and new_correct:
            v3_to_current_proxy_improved.add(row_id)
        elif old_correct and (not new_correct):
            v3_to_current_proxy_regressed.add(row_id)

    outcome_score: dict[str, int] = defaultdict(int)
    for row_id in base_to_current_proxy_improved:
        outcome_score[row_id] += 3
    for row_id in base_to_current_validation_improved:
        outcome_score[row_id] += 2
    for row_id in v3_to_current_proxy_regressed:
        outcome_score[row_id] += 2
    for row_id in v3_to_current_validation_regressed:
        outcome_score[row_id] += 1
    for row_id in base_to_current_proxy_regressed:
        outcome_score[row_id] -= 4
    for row_id in base_to_current_validation_regressed:
        outcome_score[row_id] -= 3
    return {
        "base_validation": base_validation,
        "current_validation": current_validation,
        "v3_validation": v3_validation,
        "base_proxy": base_proxy,
        "current_proxy": current_proxy,
        "v3_proxy": v3_proxy,
        "base_to_current_validation_improved": base_to_current_validation_improved,
        "base_to_current_validation_regressed": base_to_current_validation_regressed,
        "base_to_current_proxy_improved": base_to_current_proxy_improved,
        "base_to_current_proxy_regressed": base_to_current_proxy_regressed,
        "v3_to_current_validation_improved": v3_to_current_validation_improved,
        "v3_to_current_validation_regressed": v3_to_current_validation_regressed,
        "v3_to_current_proxy_improved": v3_to_current_proxy_improved,
        "v3_to_current_proxy_regressed": v3_to_current_proxy_regressed,
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
    measured: dict[str, Any],
    limit: int,
    category_name: str,
    answer_predicate: Any,
    mandatory_ids: set[str],
) -> list[str]:
    ranked: list[tuple[float, int, str]] = []
    for row_id, category in categories.items():
        if category != category_name:
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
    for row_id in sorted(mandatory_ids):
        if row_id in train_prompts and (row_id in base_index_map or (REASONING_DIR / f"{row_id}.txt").exists()):
            chosen.append(row_id)
            seen.add(row_id)
    for _, _, row_id in sorted(ranked):
        if row_id in seen:
            continue
        chosen.append(row_id)
        seen.add(row_id)
        if len(chosen) >= limit:
            break
    return chosen[:limit]


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
) -> Candidate | None:
    reasoning_path = REASONING_DIR / f"{row_id}.txt"
    if not reasoning_path.exists():
        return None
    if row_id not in train_prompts or row_id not in categories:
        return None
    merged = dict(train_prompts[row_id])
    merged["category"] = categories[row_id]
    merged.setdefault("selection_tier", "")
    merged.setdefault("template_subtype", "")
    merged.setdefault("teacher_solver_candidate", "")
    merged.setdefault("hard_score", "")
    merged.setdefault("audit_reasons", "")
    merged.setdefault("analysis_notes", "")
    merged.setdefault("symbol_query_operator", "")
    merged.setdefault("bit_structured_formula_name", "")
    merged.setdefault("bit_structured_formula_prediction", "")
    merged.setdefault("bit_structured_formula_abstract_family", "")
    return Candidate(
        row=merged,
        bucket=bucket,
        source_tags=tuple(sorted(source_tags)),
        proxy_failed=proxy_failed,
        validation_failed=validation_failed,
        priority_key=priority_key,
    )


def build_budgeted_candidates(bucket_limits: dict[str, int]) -> tuple[list[Candidate], dict[str, Any]]:
    train_prompts = load_train_prompts()
    categories = load_problem_categories()
    base_index_map = load_base_snapshot_index_map()
    measured = load_measured_signals()
    teacher_correctness = load_teacher_correctness()

    candidates: list[Candidate] = []
    missing_reasoning_ids: list[str] = []
    teacher_incorrect_filtered: dict[str, list[str]] = defaultdict(list)

    for row in load_csv_rows(TRAIN_RECOMMENDED_PATH):
        row_id = row["id"]
        bucket = measured_bucket_for_row(row)
        if bucket is None:
            continue
        if row_id in HARDBLACKLIST_IDS.get(bucket, set()):
            continue
        if (REASONING_DIR / f"{row_id}.txt").exists() is False:
            missing_reasoning_ids.append(row_id)
            continue
        if not teacher_correctness.get(row_id, False):
            teacher_incorrect_filtered[bucket].append(row_id)
            continue
        tier = str(row.get("selection_tier", "")).strip()
        if bucket == "binary_verified_core" and tier != "verified_trace_ready":
            continue
        abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", 0), 0)
        structured_formula_safe = parse_bool(row.get("bit_structured_formula_safe", False))
        not_structured_formula_safe = parse_bool(row.get("bit_not_structured_formula_safe", False))
        current_proxy_failed = row_id in measured["current_proxy_fail_ids"]
        current_validation_failed = row_id in measured["current_validation_fail_ids"]
        mandatory_binary = row_id in MEASURED_MANDATORY_IDS.get(bucket, set())
        if bucket == "binary_verified_core" and not (
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
        proxy_failed = current_proxy_failed
        validation_failed = current_validation_failed
        source_tags = {"train_recommended_learning_target_v1", bucket}
        if mandatory_binary:
            source_tags.add("measured_regression")
        if row_id in measured["base_to_current_proxy_improved"]:
            source_tags.add("base_to_current_proxy_improved")
        if row_id in measured["base_to_current_validation_improved"]:
            source_tags.add("base_to_current_validation_improved")
        if row_id in measured["base_to_current_proxy_regressed"]:
            source_tags.add("base_to_current_proxy_regressed")
        if row_id in measured["base_to_current_validation_regressed"]:
            source_tags.add("base_to_current_validation_regressed")
        if row_id in measured["v3_to_current_proxy_regressed"]:
            source_tags.add("v3_to_current_proxy_regressed")
        if row_id in measured["v3_to_current_validation_regressed"]:
            source_tags.add("v3_to_current_validation_regressed")
        if current_proxy_failed:
            source_tags.add("current_proxy_fail")
        if current_validation_failed:
            source_tags.add("current_validation_fail")
        priority_key = (
            -(1 if mandatory_binary else 0),
            -(1 if proxy_failed else 0),
            -(1 if validation_failed else 0),
            -(1 if row_id in measured["base_to_current_proxy_improved"] else 0),
            -(1 if row_id in measured["v3_to_current_proxy_regressed"] else 0),
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
            proxy_failed=proxy_failed,
            validation_failed=validation_failed,
            priority_key=priority_key,
        )
        if candidate is not None:
            candidate.row["selection_tier"] = tier
            candidate.row["template_subtype"] = str(row.get("template_subtype", "")).strip()
            candidate.row["teacher_solver_candidate"] = str(row.get("teacher_solver_candidate", "")).strip()
            candidate.row["hard_score"] = str(row.get("hard_score", ""))
            candidate.row["audit_reasons"] = str(row.get("audit_reasons", "")).strip()
            candidate.row["analysis_notes"] = str(row.get("analysis_notes", "")).strip()
            candidate.row["symbol_query_operator"] = str(row.get("symbol_query_operator", "")).strip()
            candidate.row["bit_structured_formula_name"] = str(row.get("bit_structured_formula_name", "")).strip()
            candidate.row["bit_structured_formula_prediction"] = str(row.get("bit_structured_formula_prediction", "")).strip()
            candidate.row["bit_structured_formula_abstract_family"] = str(row.get("bit_structured_formula_abstract_family", "")).strip()
            candidates.append(candidate)

    support_specs = [
        ("surface_numeral_boxed", "numeral", lambda answer: True),
        ("surface_cipher_boxed", "cipher", lambda answer: True),
        ("surface_unit_tail", "unit_conversion", lambda answer: True),
        ("easy_gravity_fragile", "gravity", lambda answer: True),
    ]
    for bucket, category_name, predicate in support_specs:
        ids = choose_guardrail_ids(
            train_prompts=train_prompts,
            categories=categories,
            base_index_map=base_index_map,
            measured=measured,
            limit=bucket_limits[bucket],
            category_name=category_name,
            answer_predicate=predicate,
            mandatory_ids=MEASURED_MANDATORY_IDS.get(bucket, set()),
        )
        for rank, row_id in enumerate(ids):
            index_row = base_index_map.get(row_id, {})
            min_logprob = parse_float(index_row.get("min_logprob"), -999.0)
            num_loss_tokens = parse_int(index_row.get("num_loss_tokens"), 0)
            source_tags = {bucket, "base_snapshot_guardrail"}
            if row_id in MEASURED_MANDATORY_IDS.get(bucket, set()):
                source_tags.add("measured_regression")
            priority_key = (
                -(1 if row_id in MEASURED_MANDATORY_IDS.get(bucket, set()) else 0),
                min_logprob,
                -num_loss_tokens,
                rank,
                row_id,
            )
            candidate = make_candidate(
                row_id=row_id,
                bucket=bucket,
                train_prompts=train_prompts,
                categories=categories,
                source_tags=source_tags,
                proxy_failed=False,
                validation_failed=False,
                priority_key=priority_key,
            )
            if candidate is not None:
                candidates.append(candidate)

    diagnostics = {
        "base_to_current_proxy_improved": len(measured["base_to_current_proxy_improved"]),
        "base_to_current_proxy_regressed": len(measured["base_to_current_proxy_regressed"]),
        "base_to_current_validation_improved": len(measured["base_to_current_validation_improved"]),
        "base_to_current_validation_regressed": len(measured["base_to_current_validation_regressed"]),
        "v3_to_current_proxy_improved": len(measured["v3_to_current_proxy_improved"]),
        "v3_to_current_proxy_regressed": len(measured["v3_to_current_proxy_regressed"]),
        "v3_to_current_validation_improved": len(measured["v3_to_current_validation_improved"]),
        "v3_to_current_validation_regressed": len(measured["v3_to_current_validation_regressed"]),
        "current_proxy_fail_ids": len(measured["current_proxy_fail_ids"]),
        "current_validation_fail_ids": len(measured["current_validation_fail_ids"]),
        "missing_reasoning_ids": sorted(set(missing_reasoning_ids)),
        "teacher_incorrect_filtered_count": sum(len(value) for value in teacher_incorrect_filtered.values()),
        "teacher_incorrect_filtered_by_bucket": {
            key: sorted(value) for key, value in sorted(teacher_incorrect_filtered.items())
        },
        "hardblacklist_ids": {key: sorted(value) for key, value in HARDBLACKLIST_IDS.items()},
        "mandatory_ids": {key: sorted(value) for key, value in MEASURED_MANDATORY_IDS.items()},
    }
    bucket_rank = {name: index for index, name in enumerate(BUCKET_ORDER)}
    return sorted(candidates, key=lambda item: (bucket_rank[item.bucket], item.priority_key)), diagnostics


def load_proxy_fail_ids() -> set[str]:
    failed: set[str] = set()
    for row in load_csv_rows(PROXY_ROW_LEVEL_PATH):
        if row.get("is_correct") != "False":
            continue
        subtype = str(row.get("template_subtype", "")).strip()
        family_short = str(row.get("family_short", "")).strip()
        if subtype in {"bit_structured_byte_formula", "bit_other", "numeric_2x2", "glyph_len5"}:
            failed.add(row["id"])
            continue
        if family_short in {"binary", "symbol"}:
            failed.add(row["id"])
    return failed


def load_validation_fail_ids(validation_csv: Path | None) -> set[str]:
    if validation_csv is None or not validation_csv.exists():
        return set()
    failed: set[str] = set()
    for row in load_csv_rows(validation_csv):
        if row.get("correct") == "False" and row.get("category") in {"bit_manipulation", "equation_numeric_deduce", "equation_numeric_guess"}:
            failed.add(row["id"])
    return failed


def load_ranked_candidates(validation_csv: Path | None) -> tuple[list[Candidate], dict[str, Any]]:
    train_prompts = load_train_prompts()
    categories = load_problem_categories()
    proxy_fail_ids = load_proxy_fail_ids()
    validation_fail_ids = load_validation_fail_ids(validation_csv)

    by_id: dict[str, dict[str, str]] = {}
    source_tags_by_id: dict[str, set[str]] = defaultdict(set)

    for row in load_csv_rows(TRAIN_RECOMMENDED_PATH):
        row_id = row["id"]
        bucket = bucket_for_row(row)
        if bucket is None:
            continue
        by_id.setdefault(row_id, row)
        source_tags_by_id[row_id].add("train_recommended_learning_target_v1")

    for row in load_csv_rows(SYMBOL_MANUAL_QUEUE_PATH):
        row_id = row["id"]
        bucket = bucket_for_row(row)
        if bucket != "symbol_glyph_len5":
            continue
        by_id.setdefault(row_id, row)
        source_tags_by_id[row_id].add("symbol_manual_audit_queue_v1")

    candidates: list[Candidate] = []
    missing_reasoning_ids: list[str] = []
    missing_prompt_ids: list[str] = []
    missing_category_ids: list[str] = []

    for row_id, row in sorted(by_id.items()):
        bucket = bucket_for_row(row)
        if bucket is None:
            continue
        reasoning_path = REASONING_DIR / f"{row_id}.txt"
        if not reasoning_path.exists():
            missing_reasoning_ids.append(row_id)
            continue
        if row_id not in train_prompts:
            missing_prompt_ids.append(row_id)
            continue
        if row_id not in categories:
            missing_category_ids.append(row_id)
            continue

        tier = str(row.get("selection_tier", "")).strip()
        tier_priority = SELECTION_TIER_PRIORITY.get(tier, 0)
        proxy_failed = row_id in proxy_fail_ids
        validation_failed = row_id in validation_fail_ids
        hard_score = parse_float(row.get("hard_score", 0.0), 0.0)
        num_examples = parse_int(row.get("num_examples", 0), 0)
        prompt_len = parse_int(row.get("prompt_len_chars", 0), 0)
        source_bonus = len(source_tags_by_id[row_id])

        bucket_priority = {
            "bit_structured_byte_formula": 40,
            "bit_other": 35,
            "symbol_glyph_len5": 30,
            "symbol_numeric_2x2": 25,
        }[bucket]

        priority_key = (
            -(1 if validation_failed else 0),
            -(1 if proxy_failed else 0),
            -bucket_priority,
            -tier_priority,
            -source_bonus,
            -hard_score,
            -num_examples,
            -prompt_len,
            row_id,
        )

        merged = dict(train_prompts[row_id])
        merged["category"] = categories[row_id]
        merged["selection_tier"] = tier
        merged["template_subtype"] = str(row.get("template_subtype", "")).strip()
        merged["teacher_solver_candidate"] = str(row.get("teacher_solver_candidate", "")).strip()
        merged["hard_score"] = str(row.get("hard_score", ""))
        merged["audit_reasons"] = str(row.get("audit_reasons", "")).strip()
        merged["analysis_notes"] = str(row.get("analysis_notes", "")).strip()
        merged["symbol_query_operator"] = str(row.get("symbol_query_operator", "")).strip()
        merged["bit_structured_formula_name"] = str(row.get("bit_structured_formula_name", "")).strip()
        merged["bit_structured_formula_prediction"] = str(row.get("bit_structured_formula_prediction", "")).strip()
        merged["bit_structured_formula_abstract_family"] = str(row.get("bit_structured_formula_abstract_family", "")).strip()

        candidates.append(
            Candidate(
                row=merged,
                bucket=bucket,
                source_tags=tuple(sorted(source_tags_by_id[row_id])),
                proxy_failed=proxy_failed,
                validation_failed=validation_failed,
                priority_key=priority_key,
            )
        )

    diagnostics = {
        "proxy_fail_ids": len(proxy_fail_ids),
        "validation_fail_ids": len(validation_fail_ids),
        "missing_reasoning_ids": missing_reasoning_ids,
        "missing_prompt_ids": missing_prompt_ids,
        "missing_category_ids": missing_category_ids,
    }
    return sorted(candidates, key=lambda item: item.priority_key), diagnostics


def select_candidates(candidates: list[Candidate], bucket_limits: dict[str, int]) -> list[Candidate]:
    selected: list[Candidate] = []
    counts = Counter()
    for candidate in candidates:
        if counts[candidate.bucket] >= bucket_limits[candidate.bucket]:
            continue
        selected.append(candidate)
        counts[candidate.bucket] += 1
    return selected


def build_overlay_rows(selected: list[Candidate], repeat_counts: dict[str, int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    for candidate in selected:
        row_id = candidate.row["id"]
        reasoning_text = (REASONING_DIR / f"{row_id}.txt").read_text(encoding="utf-8").rstrip("\n")
        answer = candidate.row["answer"]
        completion_text = build_completion_text(reasoning_text, answer)
        repeat_count = repeat_counts[candidate.bucket]
        base = {
            "id": row_id,
            "category": candidate.row["category"],
            "bucket": candidate.bucket,
            "prompt": candidate.row["prompt"],
            "answer": answer,
            "completion_text": completion_text,
            "selection_tier": candidate.row["selection_tier"],
            "template_subtype": candidate.row["template_subtype"],
            "teacher_solver_candidate": candidate.row["teacher_solver_candidate"],
            "source_tags": list(candidate.source_tags),
            "proxy_failed": candidate.proxy_failed,
            "validation_failed": candidate.validation_failed,
            "recommended_repeat_count": repeat_count,
            "hard_score": parse_float(candidate.row["hard_score"], 0.0),
            "audit_reasons": candidate.row["audit_reasons"],
            "analysis_notes": candidate.row["analysis_notes"],
            "symbol_query_operator": candidate.row["symbol_query_operator"],
            "bit_structured_formula_name": candidate.row["bit_structured_formula_name"],
            "bit_structured_formula_prediction": candidate.row["bit_structured_formula_prediction"],
            "bit_structured_formula_abstract_family": candidate.row["bit_structured_formula_abstract_family"],
        }
        unique_rows.append(base)
        for overlay_index in range(repeat_count):
            repeated = dict(base)
            repeated["overlay_instance"] = overlay_index + 1
            repeated_rows.append(repeated)
    return unique_rows, repeated_rows


def build_anchor_watchlist() -> list[dict[str, Any]]:
    rows = load_csv_rows(RESULT_BASE_PROXY_PATH)
    watchlist: list[dict[str, Any]] = []
    wanted = [
        ("roman", "roman_standard"),
        ("gravity", "gravity_half_g_t2"),
        ("unit", "unit_fixed_ratio"),
        ("text", "text_monoalphabetic"),
        ("binary", "bit_permutation_inversion"),
    ]
    for family_short, subtype in wanted:
        for row in rows:
            if row.get("family_short") != family_short:
                continue
            if row.get("template_subtype") != subtype:
                continue
            if row.get("is_correct") != "True":
                continue
            watchlist.append(
                {
                    "id": row["id"],
                    "family_short": family_short,
                    "template_subtype": subtype,
                    "gold_answer": row["gold_answer"],
                    "prediction": row["prediction"],
                }
            )
            break
    return watchlist


def build_summary(
    selected: list[Candidate],
    unique_rows: list[dict[str, Any]],
    repeated_rows: list[dict[str, Any]],
    diagnostics: dict[str, Any],
    watchlist: list[dict[str, Any]],
    validation_csv: Path | None,
    training_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_by_bucket = Counter(candidate.bucket for candidate in selected)
    repeated_by_bucket = Counter(row["bucket"] for row in repeated_rows)
    source_counts = Counter(tag for row in unique_rows for tag in row["source_tags"])
    return {
        "version": "v20_corrective_corpus_v5a_mainline",
        "created_at": utc_now(),
        "readme_eval_contract": verify_readme_eval_contract(),
        "strategy_note": str((REPO_ROOT / "A-Open-ProgressPrizePublication" / "v20_to_088_strategy.md").relative_to(REPO_ROOT)),
        "inputs": {
            "train_recommended_learning_target_v1": relative_to_repo(TRAIN_RECOMMENDED_PATH),
            "base_validation": relative_to_repo(RESULT_BASE_VALIDATION_PATH),
            "current_validation": relative_to_repo(RESULT_CURRENT_VALIDATION_PATH),
            "v3_validation": relative_to_repo(RESULT_V3_VALIDATION_PATH),
            "base_proxy_row_level": relative_to_repo(RESULT_BASE_PROXY_PATH),
            "current_proxy_row_level": relative_to_repo(RESULT_CURRENT_PROXY_PATH),
            "v3_proxy_row_level": relative_to_repo(RESULT_V3_PROXY_PATH),
            "validation_csv": None if validation_csv is None else relative_to_repo(validation_csv),
        },
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(selected_by_bucket),
        "repeated_by_bucket": dict(repeated_by_bucket),
        "source_tag_counts": dict(source_counts),
        "proxy_failed_selected": sum(1 for row in unique_rows if row["proxy_failed"]),
        "validation_failed_selected": sum(1 for row in unique_rows if row["validation_failed"]),
        "diagnostics": diagnostics,
        "anchor_watchlist": watchlist,
        "training_bundle": training_bundle,
    }


def load_base_snapshot_index_rows() -> list[dict[str, Any]]:
    if not BASE_SNAPSHOT_INDEX_PATH.exists():
        raise SystemExit(f"Missing base snapshot index: {BASE_SNAPSHOT_INDEX_PATH}")
    return load_jsonl_rows(BASE_SNAPSHOT_INDEX_PATH)


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
    retokenized_overlay_ids: set[str] = set()
    synthetic_cache: dict[str, tuple[list[int], list[int], int]] = {}

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": "v20_corrective_corpus_v5a_mainline",
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "base_snapshot_config": read_json(BASE_SNAPSHOT_CONFIG_PATH),
        "bundle_path": relative_to_repo(bundle_path),
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "note": (
            "Single-file training bundle for Kaggle upload. "
            "Includes the v20 base snapshot minus metric-wrong base rows, "
            "plus a v5a verified-binary core overlay and a short easy-family boxed-surface stabilizer."
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
            segment = "synthetic.jsonl"
            key = (problem_id, segment)
            if key in base_examples:
                entry = base_examples[key]
                base_row = entry["row"]
                tokens = entry["tokens"]
                mask = entry["mask"]
                category = str(base_row["category"])
                num_loss_tokens = int(base_row["num_loss_tokens"])
            else:
                if problem_id not in synthetic_cache:
                    tokens, mask = tokenize_overlay_example(
                        prompt=str(row["prompt"]),
                        completion_text=str(row["completion_text"]),
                    )
                    synthetic_cache[problem_id] = (tokens, mask, sum(mask))
                tokens, mask, num_loss_tokens = synthetic_cache[problem_id]
                category = str(row["category"])
                retokenized_overlay_ids.add(problem_id)
            overlay_step = base_step_count + (overlay_offset // batch_size)
            payload = {
                "record_type": "example",
                "example_id": f"{problem_id}#overlay-{row['overlay_instance']}",
                "source_problem_id": problem_id,
                "source": "corrective_overlay",
                "segment": segment,
                "category": category,
                "step": overlay_step,
                "num_loss_tokens": num_loss_tokens,
                "bucket": row["bucket"],
                "overlay_instance": int(row["overlay_instance"]),
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
        "category_counts": dict(sorted(category_counts.items())),
        "retokenized_overlay_problem_ids": sorted(retokenized_overlay_ids),
        "retokenized_overlay_problem_count": len(retokenized_overlay_ids),
    }


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
            "Build the v5a mainline corpus for the v20 Kaggle reproduction path, "
            "keeping the v20 base, adding a verified-binary core overlay, "
            "and adding a short easy-family boxed-surface stabilizer."
        )
    )
    parser.add_argument("--run-name", default="v5a_mainline_default")
    parser.add_argument("--validation-csv", type=Path, default=None)
    parser.add_argument("--bucket-limits", default=None)
    parser.add_argument("--repeat-counts", default=None)
    parser.add_argument("--write-training-bundle", action="store_true")
    parser.add_argument("--bundle-path", type=Path, default=DEFAULT_BUNDLE_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bucket_limits = parse_bucket_limits(args.bucket_limits)
    repeat_counts = parse_repeat_counts(args.repeat_counts)
    validation_csv = None if args.validation_csv is None else args.validation_csv.resolve()

    candidates, diagnostics = build_budgeted_candidates(bucket_limits)
    selected = select_candidates(candidates, bucket_limits=bucket_limits)
    unique_rows, repeated_rows = build_overlay_rows(selected, repeat_counts=repeat_counts)
    watchlist = build_anchor_watchlist()
    training_bundle = None
    if args.write_training_bundle:
        training_bundle = build_training_bundle(repeated_rows=repeated_rows, bundle_path=args.bundle_path.resolve())

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
                "proxy_failed": row["proxy_failed"],
                "validation_failed": row["validation_failed"],
                "hard_score": row["hard_score"],
                "source_tags": "|".join(row["source_tags"]),
            }
        )

    summary = build_summary(
        selected=selected,
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        watchlist=watchlist,
        validation_csv=validation_csv,
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
            "proxy_failed",
            "validation_failed",
            "hard_score",
            "source_tags",
        ],
    )
    write_jsonl(artifacts_dir / "corrective_overlay_unique.jsonl", unique_rows)
    write_jsonl(artifacts_dir / "corrective_overlay_repeated.jsonl", repeated_rows)
    write_csv(
        artifacts_dir / "anchor_watchlist.csv",
        watchlist,
        fieldnames=["id", "family_short", "template_subtype", "gold_answer", "prediction"],
    )
    write_json(artifacts_dir / "corrective_overlay_summary.json", summary)

    report_lines = [
        "# v20 corrective corpus v5a mainline report",
        "",
        "## Purpose",
        "",
        "This bundle keeps the v20 base snapshot,",
        "adds a verified-binary Stage A core overlay,",
        "and adds a short Stage C easy-family boxed-surface stabilizer.",
        "",
        "## Selected unique rows",
        "",
    ]
    for bucket in BUCKET_ORDER:
        report_lines.append(f"- `{bucket}`: `{summary['selected_by_bucket'].get(bucket, 0)}`")
    report_lines.extend(
        [
            "",
            "## Repeated training rows",
            "",
        ]
    )
    for bucket in BUCKET_ORDER:
        report_lines.append(f"- `{bucket}`: `{summary['repeated_by_bucket'].get(bucket, 0)}`")
    report_lines.extend(
        [
            "",
            "## Kaggle single-file bundle",
            "",
        ]
    )
    if training_bundle is None:
        report_lines.append("- not generated in this run")
    else:
        report_lines.extend(
            [
                f"- path: `{training_bundle['path']}`",
                f"- total examples: `{training_bundle['total_examples']}`",
                f"- overlay examples: `{training_bundle['overlay_examples']}`",
                f"- total steps: `{training_bundle['total_steps']}`",
            ]
        )
    report_lines.extend(
        [
            "",
            "## Guardrail watchlist",
            "",
        ]
    )
    for row in watchlist:
        report_lines.append(
            f"- `{row['family_short']}` / `{row['template_subtype']}` -> `{row['id']}`"
        )
    (reports_dir / "corrective_overlay_report.md").write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
