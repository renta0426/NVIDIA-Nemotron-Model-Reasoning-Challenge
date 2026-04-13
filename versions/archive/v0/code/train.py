#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import math
from pathlib import Path
import re
import subprocess
import sys
import warnings
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
import yaml


SCRIPT_PATH = Path(__file__).resolve()
VERSION_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]

RAW_TRAIN_PATH = REPO_ROOT / "data" / "train.csv"
RAW_TEST_PATH = REPO_ROOT / "data" / "test.csv"

CONF_ROOT = VERSION_ROOT / "conf"
EVAL_CONF_ROOT = CONF_ROOT / "eval"

DATA_ROOT = VERSION_ROOT / "data"
PUBLIC_SMOKE_DIR = DATA_ROOT / "public_smoke"
PROCESSED_DIR = DATA_ROOT / "processed"
EVAL_PACKS_DIR = DATA_ROOT / "eval_packs"

OUTPUT_ROOT = VERSION_ROOT / "outputs"
SMOKE_OUTPUT_DIR = OUTPUT_ROOT / "smoke"
VALID_OUTPUT_DIR = OUTPUT_ROOT / "valid"
BASELINE_OUTPUT_DIR = OUTPUT_ROOT / "baselines"

DOCS_DIR = VERSION_ROOT / "docs"
TESTS_DIR = VERSION_ROOT / "tests"
README_PATH = REPO_ROOT / "README.md"
README_TABLE_KEYS = (
    "max_lora_rank",
    "max_tokens",
    "top_p",
    "temperature",
    "max_num_seqs",
    "gpu_memory_utilization",
    "max_model_len",
)
README_TABLE_VALUE_TYPES = {
    "max_lora_rank": int,
    "max_tokens": int,
    "top_p": float,
    "temperature": float,
    "max_num_seqs": int,
    "gpu_memory_utilization": float,
    "max_model_len": int,
}

DEFAULT_PUBLIC_SMOKE_PATH = PUBLIC_SMOKE_DIR / "test_public.csv"
DEFAULT_PUBLIC_SMOKE_MANIFEST_PATH = PUBLIC_SMOKE_DIR / "test_public_manifest.csv"
DEFAULT_METADATA_PATH = PROCESSED_DIR / "train_metadata.parquet"
DEFAULT_SPLITS_PATH = PROCESSED_DIR / "train_splits.parquet"
DEFAULT_PROMPT_SNAPSHOTS_PATH = PROCESSED_DIR / "prompt_snapshots.parquet"
DEFAULT_BASELINE_REGISTRY_PATH = BASELINE_OUTPUT_DIR / "baseline_registry.csv"

OFFICIAL_BOXED_INSTRUCTION = (
    r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
)

PROMPT_INVARIANCE_RULES = """\
Competition prompt invariance rules for v0

1. Do not add a system prompt.
2. Do not add few-shot examples.
3. Do not change the user-side boxed instruction.
4. Do not disable enable_thinking=True in competition-mode prompting.
5. Do not replace the tokenizer chat template without re-running prompt snapshots.
6. If the strict chat template path fails, treat it as a blocking issue for serious runs.
7. When no repo-local tokenizer asset exists, builtin-competition-tokenizer@builtin-fallback-v0 is the accepted pinned fallback; rebuild snapshots with a real tokenizer before serious promotion when available.
"""

KAGGLE_OFFICIAL_RERUN_GUIDE = """\
Kaggle official rerun guide for v0

1. Package a single LoRA adapter with adapter_config.json for Nemotron-3-Nano-30B.
2. Keep max_lora_rank <= 32.
3. Confirm the evaluation parameters match official_lb:
   - max_tokens=7680
   - top_p=1.0
   - temperature=0.0
   - max_num_seqs=64
   - gpu_memory_utilization=0.85
   - max_model_len=8192
4. Confirm the prompt path uses the competition boxed instruction plus tokenizer.apply_chat_template(..., add_generation_prompt=True, enable_thinking=True).
5. Run shadow_256 first when checking backend drift.
6. If local-vs-Kaggle extracted agreement drops below 98%, stop promotion and investigate before submitting.
"""

PROMOTION_RULES = """\
Promotion rules fixed in v0

Daily promotion:
- official_lb cv mean improves by at least +0.003
- holdout_hard does not regress
- no family drops by more than -0.010
- extraction_fail_rate does not worsen

Serious candidate:
- official_lb cv mean improves by at least +0.005, or
- holdout_hard improves by at least +0.008
- prompt / extraction / packaging smoke checks pass
- no unresolved local-vs-Kaggle drift concern

Submission candidate:
- shadow rerun under official settings completed
- PEFT load OK
- public smoke OK
- local metrics improved over best baseline
- no catastrophic family drop
"""

FAMILY_TARGETS = """\
Family targets fixed in v0

roman: 0.995+
unit: 0.990+
gravity: 0.985+
bit: 0.940+
text_decrypt: 0.920+
symbol_equation: 0.890+
"""

HARDWARE_NOTES = """\
Hardware notes for v0

Primary target hardware:
- NVIDIA RTX PRO 6000 Blackwell 98GB: use official_lb for serious evaluation.

Fallback local hardware:
- NVIDIA RTX A6000 48GB: use local_debug for smoke and report generation only.
- Keep local concurrency conservative and prefer shadow packs for drift checks.
- Final selection should still be decided by official_lb-compatible Kaggle reruns.
"""

BOXED_PATTERN = re.compile(r"\\boxed\{([^}]*)(?:\}|$)")
FINAL_ANSWER_PATTERNS = (
    r"The final answer is:\s*([^\n]+)",
    r"Final answer is:\s*([^\n]+)",
    r"Final answer\s*[:：]\s*([^\n]+)",
    r"final answer\s*[:：]\s*([^\n]+)",
)
NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
ROMAN_PATTERN = re.compile(r"^[IVXLCDM]+$", re.IGNORECASE)
BIT_PATTERN = re.compile(r"\b[01]{8}\b")

FAMILY_BASE_HARDNESS = {
    "roman": 1,
    "unit": 1,
    "gravity": 1,
    "bit": 2,
    "text_decrypt": 3,
    "symbol_equation": 4,
}


@dataclass(frozen=True)
class EvalConfig:
    name: str
    max_lora_rank: int
    max_tokens: int
    top_p: float
    temperature: float
    max_num_seqs: int
    gpu_memory_utilization: float
    max_model_len: int
    enable_thinking: bool
    add_generation_prompt: bool
    boxed_instruction: str
    strict_chat_template: bool = True


class BuiltinCompetitionTokenizer:
    name_or_path = "builtin-competition-tokenizer"
    revision = "builtin-fallback-v0"

    def apply_chat_template(
        self,
        messages: list[dict[str, str]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
        enable_thinking: bool,
    ) -> str:
        if tokenize:
            raise ValueError("BuiltinCompetitionTokenizer only supports tokenize=False.")

        rendered: list[str] = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            rendered.append(f"<|{role}|>\n{content}")

        if add_generation_prompt:
            assistant_header = "<|assistant|>"
            if enable_thinking:
                assistant_header += "\n<think>"
            rendered.append(assistant_header)

        return "\n".join(rendered)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def ensure_version_directories() -> None:
    for path in (
        PUBLIC_SMOKE_DIR,
        PROCESSED_DIR,
        EVAL_PACKS_DIR,
        SMOKE_OUTPUT_DIR,
        VALID_OUTPUT_DIR,
        BASELINE_OUTPUT_DIR,
        DOCS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported table format: {path}")


def save_table(frame: pd.DataFrame, path: Path) -> None:
    ensure_parent(path)
    if path.suffix == ".csv":
        frame.to_csv(path, index=False)
        return
    if path.suffix == ".parquet":
        frame.to_parquet(path, index=False)
        return
    raise ValueError(f"Unsupported table format: {path}")


def load_readme_eval_contract() -> dict[str, int | float]:
    text = README_PATH.read_text(encoding="utf-8")
    contract: dict[str, int | float] = {}
    for key in README_TABLE_KEYS:
        value_type = README_TABLE_VALUE_TYPES[key]
        needle = f"{key}\t"
        for line in text.splitlines():
            if not line.startswith(needle):
                continue
            raw_value = line.split("\t", 1)[1].strip()
            if raw_value == "":
                raise SystemExit(f"Malformed README.md evaluation row for {key}: missing value")
            try:
                contract[key] = value_type(raw_value)
            except ValueError as exc:
                raise SystemExit(f"Malformed README.md evaluation value for {key}: {raw_value!r}") from exc
            break
    missing_keys = [key for key in README_TABLE_KEYS if key not in contract]
    if missing_keys:
        raise SystemExit(f"Missing README.md evaluation rows: {', '.join(missing_keys)}")
    return contract


def verify_official_eval_config_against_readme(eval_config: EvalConfig) -> None:
    contract = load_readme_eval_contract()
    for key in README_TABLE_KEYS:
        expected_value = contract[key]
        actual_value = getattr(eval_config, key)
        if actual_value != expected_value:
            raise SystemExit(
                f"README.md evaluation table mismatch for official_lb.{key}: expected {expected_value}, got {actual_value}"
            )


def load_eval_config(name_or_path: str) -> EvalConfig:
    config_path = Path(name_or_path)
    if not config_path.exists():
        config_path = EVAL_CONF_ROOT / f"{name_or_path}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Evaluation config was not found: {name_or_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    eval_config = EvalConfig(**data)
    if eval_config.name == "official_lb":
        verify_official_eval_config_against_readme(eval_config)
    return eval_config


def build_user_content(raw_prompt: str, boxed_instruction: str) -> str:
    return raw_prompt + "\n" + boxed_instruction


def apply_competition_chat_template(
    tokenizer: Any,
    user_content: str,
    *,
    enable_thinking: bool,
    add_generation_prompt: bool,
    strict_chat_template: bool = True,
) -> str:
    try:
        return tokenizer.apply_chat_template(
            [{"role": "user", "content": user_content}],
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=enable_thinking,
        )
    except Exception as exc:
        if strict_chat_template:
            raise
        warnings.warn(
            f"Chat template fallback triggered: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return user_content


def build_competition_prompt(tokenizer: Any, raw_prompt: str, eval_config: EvalConfig) -> str:
    user_content = build_user_content(raw_prompt, eval_config.boxed_instruction)
    return apply_competition_chat_template(
        tokenizer,
        user_content,
        enable_thinking=eval_config.enable_thinking,
        add_generation_prompt=eval_config.add_generation_prompt,
        strict_chat_template=eval_config.strict_chat_template,
    )


def build_sft_example(
    raw_prompt: str,
    answer: Any,
    eval_config: EvalConfig,
    assistant_style: str = "boxed",
) -> dict[str, str]:
    user_content = build_user_content(raw_prompt, eval_config.boxed_instruction)
    answer_text = str(answer)
    if assistant_style == "boxed":
        assistant_content = f"\\boxed{{{answer_text}}}"
    elif assistant_style == "final_answer":
        assistant_content = f"Final answer: {answer_text}"
    else:
        raise ValueError(f"Unsupported assistant style: {assistant_style}")
    return {
        "user_content": user_content,
        "assistant_content": assistant_content,
    }


def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"

    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", text)
    if matches:
        non_empty = [match.strip() for match in matches if match.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()

    for pattern in FINAL_ANSWER_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1].strip()

    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if matches:
        return matches[-1]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"


def verify(stored_answer: str, predicted: str) -> bool:
    stored_answer = stored_answer.strip()
    predicted = predicted.strip()

    try:
        stored_num = float(stored_answer)
        predicted_num = float(predicted)
        return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == stored_answer.lower()


def estimate_output_token_count(text: str | None) -> int:
    if not text:
        return 0
    return len(re.findall(r"\S+", text))


def contains_risky_chars(text: str | None) -> bool:
    if not text:
        return False
    return any(char in text for char in ("}", "\\", "`"))


def analyze_raw_output(text: str | None) -> dict[str, Any]:
    if text is None:
        return {
            "extracted_answer": "NOT_FOUND",
            "fallback_type": "not_found",
            "format_bucket": "not_found",
            "has_boxed": False,
            "boxed_count": 0,
            "contains_extra_numbers": False,
            "contains_risky_chars": False,
            "output_num_tokens_est": 0,
        }

    boxed_matches = BOXED_PATTERN.findall(text)
    all_numbers = NUMBER_PATTERN.findall(text)
    fallback_type = "not_found"
    format_bucket = "not_found"

    if boxed_matches:
        non_empty = [match.strip() for match in boxed_matches if match.strip()]
        if non_empty:
            extracted = non_empty[-1]
            fallback_type = "boxed_non_empty"
            format_bucket = "boxed"
        else:
            extracted = boxed_matches[-1].strip()
            fallback_type = "boxed_empty"
            format_bucket = "boxed_empty"
    else:
        extracted = "NOT_FOUND"
        for pattern in FINAL_ANSWER_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                extracted = matches[-1].strip()
                fallback_type = "final_answer_phrase"
                format_bucket = "final_answer"
                break
        if extracted == "NOT_FOUND":
            if all_numbers:
                extracted = all_numbers[-1]
                fallback_type = "last_number"
                format_bucket = "numeric_fallback"
            else:
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                if lines:
                    extracted = lines[-1]
                    fallback_type = "last_line"
                    format_bucket = "line_fallback"

    return {
        "extracted_answer": extracted,
        "fallback_type": fallback_type,
        "format_bucket": format_bucket,
        "has_boxed": bool(boxed_matches),
        "boxed_count": len(boxed_matches),
        "contains_extra_numbers": len(all_numbers) > 1,
        "contains_risky_chars": contains_risky_chars(text),
        "output_num_tokens_est": estimate_output_token_count(text),
    }


def analyze_provided_prediction(text: Any) -> dict[str, Any]:
    prediction = "" if pd.isna(text) else str(text)
    extracted = prediction.strip() or "NOT_FOUND"
    return {
        "extracted_answer": extracted,
        "fallback_type": "provided_prediction",
        "format_bucket": "provided_prediction",
        "has_boxed": False,
        "boxed_count": 0,
        "contains_extra_numbers": len(NUMBER_PATTERN.findall(prediction)) > 1,
        "contains_risky_chars": contains_risky_chars(prediction),
        "output_num_tokens_est": estimate_output_token_count(prediction),
    }


def extract_special_chars(text: str) -> str:
    chars = sorted({char for char in text if not char.isalnum() and not char.isspace()})
    return "".join(chars)


def estimate_num_examples(prompt: str) -> int:
    return sum(1 for line in prompt.splitlines() if "->" in line)


def classify_family(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if "roman numeral" in prompt_lower or "roman numerals" in prompt_lower:
        return "roman"
    if any(token in prompt_lower for token in ("gravity", "distance", "fall")):
        return "gravity"
    if any(token in prompt_lower for token in ("convert", "conversion", "units", "unit conversion")):
        return "unit"
    if any(token in prompt_lower for token in ("decrypt", "decode", "cipher", "encoded text")):
        return "text_decrypt"
    if "bit manipulation" in prompt_lower or "8-bit" in prompt_lower or len(BIT_PATTERN.findall(prompt)) >= 4:
        return "bit"
    return "symbol_equation"


def infer_subfamily(prompt: str, family: str) -> str:
    prompt_lower = prompt.lower()
    if family == "bit":
        ops = [
            name
            for name in ("shift", "rotate", "rotation", "xor", "and", "or", "not", "majority", "choice")
            if name in prompt_lower
        ]
        return "+".join(ops[:3]) if ops else "bit_rule"
    if family == "gravity":
        if "distance" in prompt_lower:
            return "distance_rule"
        if "fall" in prompt_lower:
            return "free_fall"
        return "gravity_rule"
    if family == "unit":
        if "convert" in prompt_lower:
            return "conversion_table"
        return "unit_rule"
    if family == "text_decrypt":
        if "cipher" in prompt_lower:
            return "cipher_rule"
        return "decrypt_rule"
    if family == "roman":
        if any(token in prompt_lower for token in ("iv", "ix", "xl", "xc", "cd", "cm")):
            return "subtractive"
        return "roman_rule"
    if "=" in prompt:
        return "equation_transduction"
    if "->" in prompt:
        return "symbol_transduction"
    return "symbol_rule"


def infer_group_shift_signature(prompt: str, family: str, subfamily: str) -> str:
    numbers = NUMBER_PATTERN.findall(prompt)
    if family == "bit":
        return subfamily
    if family == "gravity":
        if numbers:
            first = float(numbers[0])
            return f"g-bin-{int(first)}"
        return "g-bin-unknown"
    if family == "unit":
        if len(numbers) >= 2:
            denominator = float(numbers[1])
            if denominator == 0:
                return "ratio-undefined"
            ratio = float(numbers[0]) / denominator
            if ratio < 1:
                return "ratio-lt1"
            if ratio < 10:
                return "ratio-lt10"
            return "ratio-ge10"
        return "ratio-unknown"
    if family == "text_decrypt":
        return "cipher-shift"
    if family == "roman":
        return "subtractive" if subfamily == "subtractive" else "additive"
    arrow_count = prompt.count("->")
    return f"symbol-arrow-{min(arrow_count, 9)}"


def classify_answer_type(answer: Any) -> str:
    if pd.isna(answer):
        return "unknown"
    text = str(answer).strip()
    if re.fullmatch(r"[01]{8}", text):
        return "binary8"
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        return "numeric"
    if ROMAN_PATTERN.fullmatch(text):
        return "roman"
    if re.fullmatch(r"[A-Za-z ]+", text):
        return "text_phrase" if " " in text else "word"
    return "symbolic"


def build_hard_score(record: dict[str, Any]) -> float:
    family = str(record["family"])
    score = float(FAMILY_BASE_HARDNESS.get(family, 1))
    score += 2.0 if record["risk_flag"] else 0.0
    score += min(record["answer_len"], 24) / 12.0
    score += min(record["prompt_len_words"], 200) / 100.0
    score += 0.5 * min(record["num_examples_est"], 10)
    if record["answer_type"] in {"text_phrase", "symbolic"}:
        score += 1.0
    return score


def difficulty_from_score(score: float) -> str:
    if score >= 8:
        return "extreme"
    if score >= 5:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def build_public_overlap_manifest(train_df: pd.DataFrame, public_df: pd.DataFrame) -> pd.DataFrame:
    train_ids = set(train_df["id"].astype(str))
    train_prompts = set(train_df["prompt"].astype(str))
    train_pairs = set(zip(train_df["id"].astype(str), train_df["prompt"].astype(str)))

    manifest = public_df.copy()
    manifest["id"] = manifest["id"].astype(str)
    manifest["prompt"] = manifest["prompt"].astype(str)
    manifest["id_match"] = manifest["id"].isin(train_ids)
    manifest["prompt_match"] = manifest["prompt"].isin(train_prompts)
    manifest["exact_row_match"] = manifest.apply(
        lambda row: (row["id"], row["prompt"]) in train_pairs,
        axis=1,
    )
    manifest["overlap_type"] = manifest.apply(resolve_overlap_type, axis=1)
    return manifest


def resolve_overlap_type(row: pd.Series) -> str:
    if bool(row.get("exact_row_match")):
        return "exact_row_match"
    if bool(row.get("id_match")):
        return "id_match"
    if bool(row.get("prompt_match")):
        return "prompt_match"
    return ""


def build_metadata_frame(train_df: pd.DataFrame, public_df: pd.DataFrame) -> pd.DataFrame:
    manifest = build_public_overlap_manifest(train_df, public_df)
    public_ids = set(manifest.loc[manifest["id_match"], "id"].astype(str))
    public_prompts = set(manifest.loc[manifest["prompt_match"], "prompt"].astype(str))
    public_pairs = set(
        zip(
            manifest.loc[manifest["exact_row_match"], "id"].astype(str),
            manifest.loc[manifest["exact_row_match"], "prompt"].astype(str),
        )
    )

    records: list[dict[str, Any]] = []
    for row in train_df.itertuples(index=False):
        prompt = str(row.prompt)
        answer = str(row.answer)
        family = classify_family(prompt)
        subfamily = infer_subfamily(prompt, family)
        answer_type = classify_answer_type(answer)
        combined_text = prompt + "\n" + answer
        prompt_len_words = len(prompt.split())
        answer_len = len(answer.strip())

        overlap_exact = (str(row.id), prompt) in public_pairs
        overlap_id = str(row.id) in public_ids
        overlap_prompt = prompt in public_prompts
        overlap_type = ""
        if overlap_exact:
            overlap_type = "exact_row_match"
        elif overlap_id:
            overlap_type = "id_match"
        elif overlap_prompt:
            overlap_type = "prompt_match"

        base_record = {
            "id": str(row.id),
            "prompt": prompt,
            "answer": answer,
            "family": family,
            "subfamily": subfamily,
            "group_shift_signature": infer_group_shift_signature(prompt, family, subfamily),
            "answer_type": answer_type,
            "answer_len": answer_len,
            "prompt_len_chars": len(prompt),
            "prompt_len_words": prompt_len_words,
            "special_chars": extract_special_chars(combined_text),
            "contains_right_brace": "}" in combined_text,
            "contains_backslash": "\\" in combined_text,
            "contains_backtick": "`" in combined_text,
            "num_examples_est": estimate_num_examples(prompt),
            "is_public_test_overlap": bool(overlap_type),
            "public_test_overlap_type": overlap_type,
        }
        risk_flag = any(
            (
                base_record["contains_right_brace"],
                base_record["contains_backslash"],
                base_record["contains_backtick"],
                answer_type in {"text_phrase", "symbolic"},
            )
        )
        base_record["risk_flag"] = risk_flag
        hard_score = build_hard_score(base_record)
        base_record["difficulty_hint"] = difficulty_from_score(hard_score)
        base_record["hard_score"] = hard_score
        base_record["fold_cv5"] = -1
        base_record["is_hard_holdout"] = False
        records.append(base_record)

    return pd.DataFrame.from_records(records).sort_values("id").reset_index(drop=True)


def make_stratification_labels(metadata_df: pd.DataFrame) -> pd.Series:
    labels = metadata_df["family"].astype(str) + "__" + metadata_df["answer_type"].astype(str)
    counts = labels.value_counts()
    labels = labels.where(labels.map(counts) >= 5, metadata_df["family"].astype(str))
    family_counts = labels.value_counts()
    labels = labels.where(labels.map(family_counts) >= 5, "all")
    return labels


def assign_cv5_folds(metadata_df: pd.DataFrame, random_state: int = 42) -> pd.Series:
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    labels = make_stratification_labels(metadata_df)
    fold_assignments = pd.Series(index=metadata_df.index, dtype="int64")
    for fold, (_, valid_index) in enumerate(splitter.split(metadata_df, labels)):
        fold_assignments.iloc[valid_index] = fold
    return fold_assignments.astype(int)


def select_hard_holdout(metadata_df: pd.DataFrame, ratio: float = 0.1) -> pd.Series:
    selected_ids: list[str] = []
    for _, family_df in metadata_df.groupby("family", sort=True):
        target_size = max(1, int(round(len(family_df) * ratio)))
        top_family = family_df.sort_values(
            ["hard_score", "risk_flag", "prompt_len_words", "answer_len", "id"],
            ascending=[False, False, False, False, True],
        ).head(target_size)
        selected_ids.extend(top_family["id"].tolist())
    return metadata_df["id"].isin(selected_ids)


def stratified_sample_frame(
    frame: pd.DataFrame,
    *,
    total: int,
    group_columns: list[str],
    random_state: int,
) -> pd.DataFrame:
    if len(frame) <= total:
        return frame.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    grouped = frame.groupby(group_columns, dropna=False)
    counts = grouped.size().sort_index()
    quota_float = counts / counts.sum() * total
    quota = np.floor(quota_float).astype(int)
    quota = np.minimum(quota, counts)

    remaining = int(total - quota.sum())
    if remaining > 0:
        remainders = (quota_float - quota).sort_values(ascending=False)
        for group_key in remainders.index:
            if remaining == 0:
                break
            if quota.loc[group_key] < counts.loc[group_key]:
                quota.loc[group_key] += 1
                remaining -= 1

    sampled_groups: list[pd.DataFrame] = []
    for group_index, (group_key, take_count) in enumerate(quota.items()):
        if take_count <= 0:
            continue
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        mask = np.ones(len(frame), dtype=bool)
        for column, value in zip(group_columns, group_key):
            mask &= frame[column].eq(value)
        sampled_groups.append(
            frame.loc[mask].sample(n=int(take_count), random_state=random_state + group_index)
        )

    sampled = pd.concat(sampled_groups, ignore_index=True)
    if len(sampled) < total:
        leftover = frame.loc[~frame["id"].isin(sampled["id"])]
        extra = leftover.sample(n=total - len(sampled), random_state=random_state + 997)
        sampled = pd.concat([sampled, extra], ignore_index=True)

    return sampled.sample(frac=1.0, random_state=random_state).reset_index(drop=True)


def bootstrap_accuracy_confidence(
    is_correct_values: Iterable[bool],
    *,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    values = np.asarray(list(is_correct_values), dtype=float)
    if values.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    sample_indices = rng.integers(0, values.size, size=(n_bootstrap, values.size))
    sample_means = values[sample_indices].mean(axis=1)
    return (
        float(np.quantile(sample_means, 0.025)),
        float(np.quantile(sample_means, 0.975)),
    )


def get_tokenizer(args: argparse.Namespace) -> tuple[Any, str, str]:
    tokenizer_path = getattr(args, "tokenizer_path", None)
    tokenizer_revision = getattr(args, "tokenizer_revision", None)
    tokenizer_name = getattr(args, "tokenizer_name", None)

    if tokenizer_path:
        tokenizer_path_obj = Path(tokenizer_path)
        if not tokenizer_path_obj.exists():
            raise FileNotFoundError(f"Tokenizer path does not exist: {tokenizer_path}")
        try:
            from transformers import AutoTokenizer  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional runtime path
            raise RuntimeError(
                "transformers is required when --tokenizer-path is provided."
            ) from exc
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path,
            revision=tokenizer_revision,
            trust_remote_code=True,
        )
        name = tokenizer_name or getattr(tokenizer, "name_or_path", tokenizer_path)
        revision = tokenizer_revision or "unspecified"
        return tokenizer, name, revision

    tokenizer = BuiltinCompetitionTokenizer()
    return tokenizer, tokenizer_name or tokenizer.name_or_path, tokenizer_revision or tokenizer.revision


def prepare_public_smoke(
    *,
    input_csv: Path,
    output_csv: Path,
    train_csv: Path,
    manifest_csv: Path,
) -> pd.DataFrame:
    ensure_version_directories()
    ensure_parent(output_csv)
    ensure_parent(manifest_csv)
    public_df = pd.read_csv(input_csv)
    train_df = pd.read_csv(train_csv)
    manifest_df = build_public_overlap_manifest(train_df, public_df)
    public_df.to_csv(output_csv, index=False)
    manifest_df.to_csv(manifest_csv, index=False)
    return manifest_df


def build_metadata(
    *,
    train_csv: Path,
    public_smoke_csv: Path,
    output_path: Path,
) -> pd.DataFrame:
    ensure_version_directories()
    train_df = pd.read_csv(train_csv)
    public_df = pd.read_csv(public_smoke_csv)
    metadata_df = build_metadata_frame(train_df, public_df)
    save_table(metadata_df, output_path)
    return metadata_df


def build_splits(
    *,
    metadata_path: Path,
    output_path: Path,
    random_state: int = 42,
) -> pd.DataFrame:
    ensure_version_directories()
    metadata_df = load_table(metadata_path).copy()
    metadata_df["fold_cv5"] = assign_cv5_folds(metadata_df, random_state=random_state)
    metadata_df["is_hard_holdout"] = select_hard_holdout(metadata_df)
    save_table(metadata_df, output_path)
    return metadata_df


def build_shadow_packs(
    *,
    splits_path: Path,
    output_dir: Path,
    random_state: int = 42,
) -> dict[str, Path]:
    ensure_version_directories()
    splits_df = load_table(splits_path)
    eligible = splits_df.loc[~splits_df["is_public_test_overlap"]].copy()
    columns = [
        "id",
        "prompt",
        "answer",
        "family",
        "subfamily",
        "answer_type",
        "risk_flag",
        "difficulty_hint",
        "hard_score",
    ]
    shadow_128 = stratified_sample_frame(
        eligible,
        total=128,
        group_columns=["family", "answer_type"],
        random_state=random_state,
    )[columns]
    shadow_256 = stratified_sample_frame(
        eligible,
        total=256,
        group_columns=["family", "answer_type"],
        random_state=random_state + 1,
    )[columns]
    hard_pool = eligible.loc[eligible["is_hard_holdout"]].copy()
    hard_shadow_256 = stratified_sample_frame(
        hard_pool,
        total=256,
        group_columns=["family", "answer_type"],
        random_state=random_state + 2,
    )[columns]

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "shadow_128": output_dir / "shadow_128.csv",
        "shadow_256": output_dir / "shadow_256.csv",
        "hard_shadow_256": output_dir / "hard_shadow_256.csv",
    }
    shadow_128.to_csv(paths["shadow_128"], index=False)
    shadow_256.to_csv(paths["shadow_256"], index=False)
    hard_shadow_256.to_csv(paths["hard_shadow_256"], index=False)
    return paths


def build_prompt_snapshots(
    *,
    splits_path: Path,
    public_smoke_path: Path,
    output_path: Path,
    eval_config_name: str,
    tokenizer: Any,
    tokenizer_name: str,
    tokenizer_revision: str,
) -> pd.DataFrame:
    ensure_version_directories()
    eval_config = load_eval_config(eval_config_name)
    splits_df = load_table(splits_path)
    public_df = pd.read_csv(public_smoke_path)

    first_hundred = splits_df.head(100)
    family_heads = splits_df.groupby("family", sort=True).head(5)
    selected_train_ids = set(first_hundred["id"].tolist()) | set(family_heads["id"].tolist())
    selected_train = splits_df.loc[splits_df["id"].isin(selected_train_ids)].copy()
    selected_train["source"] = "train"

    public_records = public_df.copy()
    public_records["family"] = public_records["prompt"].astype(str).map(classify_family)
    public_records["source"] = "public_smoke"

    snapshot_records: list[dict[str, Any]] = []
    for frame in (selected_train, public_records):
        for row in frame.itertuples(index=False):
            prompt = str(row.prompt)
            rendered_prompt = build_competition_prompt(tokenizer, prompt, eval_config)
            snapshot_records.append(
                {
                    "id": str(row.id),
                    "family": getattr(row, "family", classify_family(prompt)),
                    "source": getattr(row, "source", "train"),
                    "raw_prompt_hash": sha256_text(prompt),
                    "rendered_prompt_hash": sha256_text(rendered_prompt),
                    "rendered_prompt_text": rendered_prompt,
                    "tokenizer_name": tokenizer_name,
                    "tokenizer_revision": tokenizer_revision,
                    "eval_mode": eval_config.name,
                }
            )

    snapshots_df = pd.DataFrame.from_records(snapshot_records).drop_duplicates(subset=["id", "source"])
    save_table(snapshots_df, output_path)
    return snapshots_df


def validate_prompt_snapshot_artifact(snapshots_df: pd.DataFrame) -> None:
    required_columns = {
        "id",
        "family",
        "source",
        "raw_prompt_hash",
        "rendered_prompt_hash",
        "rendered_prompt_text",
        "tokenizer_name",
        "tokenizer_revision",
        "eval_mode",
    }
    missing_columns = sorted(required_columns - set(snapshots_df.columns))
    if missing_columns:
        raise ValueError(
            "Prompt snapshot artifact is missing required columns: " + ", ".join(missing_columns)
        )
    if snapshots_df.empty:
        raise ValueError("Prompt snapshot artifact must contain at least one row.")

    for column in ("tokenizer_name", "tokenizer_revision", "eval_mode", "rendered_prompt_text"):
        if snapshots_df[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Prompt snapshot artifact has blank values in {column}.")

    sources = set(snapshots_df["source"].astype(str))
    required_sources = {"train", "public_smoke"}
    missing_sources = sorted(required_sources - sources)
    if missing_sources:
        raise ValueError(
            "Prompt snapshot artifact is missing required sources: " + ", ".join(missing_sources)
        )

    eval_modes = set(snapshots_df["eval_mode"].astype(str))
    if "official_lb" not in eval_modes:
        raise ValueError("Prompt snapshot artifact must include official_lb rendering records.")


def evaluate_predictions(
    *,
    predictions_path: Path,
    splits_path: Path,
    output_dir: Path,
    run_name: str,
    model_name: str,
    adapter_name: str,
    eval_config_name: str,
    row_id_column: str,
    prediction_column: str,
    raw_output_column: str | None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_version_directories()
    eval_config = load_eval_config(eval_config_name)
    predictions_df = pd.read_csv(predictions_path)
    splits_df = load_table(splits_path)
    if row_id_column not in predictions_df.columns:
        raise KeyError(f"Missing row id column: {row_id_column}")
    if row_id_column not in splits_df.columns:
        raise KeyError(f"Missing row id column in splits: {row_id_column}")

    working_predictions = predictions_df.copy()
    if raw_output_column and raw_output_column in working_predictions.columns:
        analyses = working_predictions[raw_output_column].map(analyze_raw_output).apply(pd.Series)
        working_predictions["raw_output"] = working_predictions[raw_output_column].fillna("").astype(str)
    elif prediction_column in working_predictions.columns:
        analyses = working_predictions[prediction_column].map(analyze_provided_prediction).apply(pd.Series)
        working_predictions["raw_output"] = ""
    else:
        raise KeyError(
            f"Predictions file must include either raw output column '{raw_output_column}' "
            f"or prediction column '{prediction_column}'."
        )

    working_predictions = pd.concat([working_predictions, analyses], axis=1)
    merged = splits_df.merge(
        working_predictions,
        on=row_id_column,
        how="inner",
        suffixes=("", "_pred"),
    )
    if merged.empty:
        raise ValueError("Prediction merge produced zero rows.")

    merged["gold_answer"] = merged["answer"].astype(str)
    merged["extracted_answer"] = merged["extracted_answer"].astype(str)
    merged["is_correct"] = [
        verify(gold, pred)
        for gold, pred in zip(merged["gold_answer"], merged["extracted_answer"], strict=True)
    ]
    merged["format_fail"] = ~merged["fallback_type"].isin({"boxed_non_empty", "provided_prediction"})
    merged["extraction_fail"] = merged["extracted_answer"] == "NOT_FOUND"
    merged["prompt_hash"] = merged["prompt"].astype(str).map(sha256_text)
    merged["eval_mode"] = eval_config.name

    excluded_public = merged.loc[~merged["is_public_test_overlap"]].copy()
    hard_rows = excluded_public.loc[excluded_public["is_hard_holdout"]].copy()

    overall_ci_low, overall_ci_high = bootstrap_accuracy_confidence(excluded_public["is_correct"])
    hard_ci_low, hard_ci_high = bootstrap_accuracy_confidence(hard_rows["is_correct"])

    timestamp = utc_now()
    summary_df = pd.DataFrame(
        [
            {
                "run_name": run_name,
                "model_name": model_name,
                "adapter_name": adapter_name,
                "eval_mode": eval_config.name,
                "split_name": "cv5_strat_family",
                "overall_acc": float(excluded_public["is_correct"].mean()),
                "overall_acc_all_rows": float(merged["is_correct"].mean()),
                "hard_acc": float(hard_rows["is_correct"].mean()) if not hard_rows.empty else float("nan"),
                "extraction_fail_rate": float(excluded_public["extraction_fail"].mean()),
                "format_fail_rate": float(excluded_public["format_fail"].mean()),
                "avg_output_len": float(excluded_public["output_num_tokens_est"].mean()),
                "overall_ci_low": overall_ci_low,
                "overall_ci_high": overall_ci_high,
                "hard_ci_low": hard_ci_low,
                "hard_ci_high": hard_ci_high,
                "timestamp": timestamp,
            }
        ]
    )

    family_records: list[dict[str, Any]] = []
    for family, family_df in excluded_public.groupby("family", sort=True):
        ci_low, ci_high = bootstrap_accuracy_confidence(family_df["is_correct"])
        family_records.append(
            {
                "run_name": run_name,
                "family": family,
                "n": int(len(family_df)),
                "acc": float(family_df["is_correct"].mean()),
                "extraction_fail_rate": float(family_df["extraction_fail"].mean()),
                "format_fail_rate": float(family_df["format_fail"].mean()),
                "avg_output_len": float(family_df["output_num_tokens_est"].mean()),
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )
    family_df = pd.DataFrame.from_records(family_records)

    row_level_df = merged[
        [
            row_id_column,
            "family",
            "prompt_hash",
            "gold_answer",
            "raw_output",
            "extracted_answer",
            "is_correct",
            "has_boxed",
            "boxed_count",
            "fallback_type",
            "contains_extra_numbers",
            "contains_risky_chars",
            "eval_mode",
            "is_public_test_overlap",
            "public_test_overlap_type",
            "is_hard_holdout",
        ]
    ].copy()

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_dir / "summary.csv", index=False)
    family_df.to_csv(output_dir / "family_metrics.csv", index=False)
    row_level_df.to_parquet(output_dir / "row_level.parquet", index=False)

    return summary_df, family_df, row_level_df


def compare_shadow_results(
    *,
    local_predictions_path: Path,
    kaggle_predictions_path: Path,
    splits_path: Path,
    row_id_column: str,
    prediction_column: str,
    raw_output_column: str | None,
    output_path: Path | None,
) -> pd.DataFrame:
    def load_predictions(path: Path) -> pd.DataFrame:
        frame = pd.read_csv(path)
        if raw_output_column and raw_output_column in frame.columns:
            frame["extracted_answer"] = frame[raw_output_column].map(extract_final_answer)
        elif prediction_column in frame.columns:
            frame["extracted_answer"] = frame[prediction_column].astype(str)
        else:
            raise KeyError(
                f"File {path} must contain '{prediction_column}' or '{raw_output_column}'."
            )
        return frame[[row_id_column, "extracted_answer"]].copy()

    splits_df = load_table(splits_path)
    local_df = load_predictions(local_predictions_path).rename(columns={"extracted_answer": "local_extracted"})
    kaggle_df = load_predictions(kaggle_predictions_path).rename(columns={"extracted_answer": "kaggle_extracted"})

    merged = (
        splits_df[[row_id_column, "family", "answer"]]
        .merge(local_df, on=row_id_column, how="inner")
        .merge(kaggle_df, on=row_id_column, how="inner")
    )
    merged["local_correct"] = [
        verify(gold, pred)
        for gold, pred in zip(merged["answer"].astype(str), merged["local_extracted"].astype(str), strict=True)
    ]
    merged["kaggle_correct"] = [
        verify(gold, pred)
        for gold, pred in zip(merged["answer"].astype(str), merged["kaggle_extracted"].astype(str), strict=True)
    ]
    merged["extracted_agreement"] = merged["local_extracted"] == merged["kaggle_extracted"]
    merged["correct_agreement"] = merged["local_correct"] == merged["kaggle_correct"]

    summary_records = [
        {
            "scope": "overall",
            "family": "overall",
            "n": int(len(merged)),
            "extracted_agreement": float(merged["extracted_agreement"].mean()),
            "correct_agreement": float(merged["correct_agreement"].mean()),
        }
    ]
    for family, family_df in merged.groupby("family", sort=True):
        summary_records.append(
            {
                "scope": "family",
                "family": family,
                "n": int(len(family_df)),
                "extracted_agreement": float(family_df["extracted_agreement"].mean()),
                "correct_agreement": float(family_df["correct_agreement"].mean()),
            }
        )

    summary_df = pd.DataFrame.from_records(summary_records)
    if output_path is not None:
        ensure_parent(output_path)
        summary_df.to_csv(output_path, index=False)
    return summary_df


def init_baseline_registry(output_path: Path) -> pd.DataFrame:
    ensure_version_directories()
    ensure_parent(output_path)
    registry_df = pd.DataFrame(
        [
            {
                "baseline_type": "base-no-adapter",
                "run_name": "",
                "model_name": "Nemotron-3-Nano-30B",
                "adapter_name": "",
                "status": "reserved",
                "notes": "Record the base model without any adapter here.",
                "created_at": utc_now(),
            },
            {
                "baseline_type": "dummy-smoke-adapter",
                "run_name": "",
                "model_name": "Nemotron-3-Nano-30B",
                "adapter_name": "",
                "status": "reserved",
                "notes": "Record a random-like or smoke adapter here.",
                "created_at": utc_now(),
            },
            {
                "baseline_type": "first-minimal-real-only-lora",
                "run_name": "",
                "model_name": "Nemotron-3-Nano-30B",
                "adapter_name": "",
                "status": "reserved",
                "notes": "Record the first minimal real-only LoRA baseline here.",
                "created_at": utc_now(),
            },
        ]
    )
    registry_df.to_csv(output_path, index=False)
    return registry_df


def write_docs() -> None:
    ensure_version_directories()
    write_text(DOCS_DIR / "prompt_invariance_rules.txt", PROMPT_INVARIANCE_RULES)
    write_text(DOCS_DIR / "kaggle_official_rerun_guide.txt", KAGGLE_OFFICIAL_RERUN_GUIDE)
    write_text(DOCS_DIR / "promotion_rules.txt", PROMOTION_RULES)
    write_text(DOCS_DIR / "family_targets.txt", FAMILY_TARGETS)
    write_text(DOCS_DIR / "hardware_notes.txt", HARDWARE_NOTES)


def validate_v0() -> None:
    ensure_version_directories()
    test_files = [
        TESTS_DIR / "test_extraction.py",
        TESTS_DIR / "test_verify.py",
        TESTS_DIR / "test_prompt_builder.py",
        TESTS_DIR / "test_public_smoke_isolation.py",
        TESTS_DIR / "test_split_integrity.py",
    ]
    subprocess.run(
        [sys.executable, "-m", "pytest", *[str(path) for path in test_files], "-q"],
        check=True,
        cwd=REPO_ROOT,
    )

    required_files = [
        EVAL_CONF_ROOT / "official_lb.yaml",
        EVAL_CONF_ROOT / "notebook_default.yaml",
        EVAL_CONF_ROOT / "local_debug.yaml",
        CONF_ROOT / "data" / "split_policy.yaml",
        CONF_ROOT / "runtime" / "paths.yaml",
        DEFAULT_PUBLIC_SMOKE_PATH,
        DEFAULT_PUBLIC_SMOKE_MANIFEST_PATH,
        DEFAULT_METADATA_PATH,
        DEFAULT_SPLITS_PATH,
        DEFAULT_PROMPT_SNAPSHOTS_PATH,
        EVAL_PACKS_DIR / "shadow_128.csv",
        EVAL_PACKS_DIR / "shadow_256.csv",
        EVAL_PACKS_DIR / "hard_shadow_256.csv",
        DEFAULT_BASELINE_REGISTRY_PATH,
        DOCS_DIR / "prompt_invariance_rules.txt",
        DOCS_DIR / "kaggle_official_rerun_guide.txt",
        DOCS_DIR / "promotion_rules.txt",
        DOCS_DIR / "family_targets.txt",
        DOCS_DIR / "hardware_notes.txt",
    ]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required v0 artifacts:\n" + "\n".join(missing))

    snapshots_df = load_table(DEFAULT_PROMPT_SNAPSHOTS_PATH)
    validate_prompt_snapshot_artifact(snapshots_df)

    print("v0 validation passed.")


def command_prepare_public_smoke(args: argparse.Namespace) -> None:
    manifest_df = prepare_public_smoke(
        input_csv=Path(args.input_csv),
        output_csv=Path(args.output_csv),
        train_csv=Path(args.train_csv),
        manifest_csv=Path(args.manifest_csv),
    )
    print(
        f"Prepared public smoke at {args.output_csv} with {len(manifest_df)} rows "
        f"({int(manifest_df['exact_row_match'].sum())} exact overlaps)."
    )


def command_build_metadata(args: argparse.Namespace) -> None:
    metadata_df = build_metadata(
        train_csv=Path(args.input_csv),
        public_smoke_csv=Path(args.public_smoke_csv),
        output_path=Path(args.output),
    )
    print(
        f"Built metadata at {args.output} with {len(metadata_df)} rows and "
        f"{int(metadata_df['is_public_test_overlap'].sum())} public overlaps."
    )


def command_build_splits(args: argparse.Namespace) -> None:
    splits_df = build_splits(
        metadata_path=Path(args.input_csv),
        output_path=Path(args.output),
        random_state=args.random_state,
    )
    print(
        f"Built splits at {args.output} with "
        f"{splits_df['fold_cv5'].nunique()} CV folds and "
        f"{int(splits_df['is_hard_holdout'].sum())} hard-holdout rows."
    )


def command_build_shadow_packs(args: argparse.Namespace) -> None:
    paths = build_shadow_packs(
        splits_path=Path(args.input_csv),
        output_dir=Path(args.output_dir),
        random_state=args.random_state,
    )
    for name, path in paths.items():
        print(f"{name}: {path}")


def command_build_prompt_snapshots(args: argparse.Namespace) -> None:
    tokenizer, tokenizer_name, tokenizer_revision = get_tokenizer(args)
    snapshots_df = build_prompt_snapshots(
        splits_path=Path(args.input_csv),
        public_smoke_path=Path(args.public_smoke_csv),
        output_path=Path(args.output),
        eval_config_name=args.eval_config,
        tokenizer=tokenizer,
        tokenizer_name=tokenizer_name,
        tokenizer_revision=tokenizer_revision,
    )
    print(
        f"Built prompt snapshots at {args.output} with {len(snapshots_df)} rows "
        f"using tokenizer={tokenizer_name}@{tokenizer_revision}."
    )


def command_run_local_eval(args: argparse.Namespace) -> None:
    summary_df, family_df, row_level_df = evaluate_predictions(
        predictions_path=Path(args.predictions_csv),
        splits_path=Path(args.splits_parquet),
        output_dir=Path(args.output_dir),
        run_name=args.run_name,
        model_name=args.model_name,
        adapter_name=args.adapter_name,
        eval_config_name=args.eval_config,
        row_id_column=args.row_id_column,
        prediction_column=args.prediction_column,
        raw_output_column=args.raw_output_column,
    )
    print(
        f"Wrote local eval report to {args.output_dir}: "
        f"{len(summary_df)} summary rows, {len(family_df)} family rows, {len(row_level_df)} row-level rows."
    )


def command_compare_shadow_results(args: argparse.Namespace) -> None:
    summary_df = compare_shadow_results(
        local_predictions_path=Path(args.local_predictions_csv),
        kaggle_predictions_path=Path(args.kaggle_predictions_csv),
        splits_path=Path(args.splits_parquet),
        row_id_column=args.row_id_column,
        prediction_column=args.prediction_column,
        raw_output_column=args.raw_output_column,
        output_path=Path(args.output_csv) if args.output_csv else None,
    )
    print(summary_df.to_csv(index=False))


def command_init_baselines(args: argparse.Namespace) -> None:
    registry_df = init_baseline_registry(Path(args.output))
    print(f"Initialized baseline registry at {args.output} with {len(registry_df)} placeholder rows.")


def command_write_docs(_: argparse.Namespace) -> None:
    write_docs()
    print(f"Wrote v0 documentation artifacts to {DOCS_DIR}.")


def command_show_kaggle_rerun(_: argparse.Namespace) -> None:
    print(KAGGLE_OFFICIAL_RERUN_GUIDE.strip())


def command_validate_v0(_: argparse.Namespace) -> None:
    validate_v0()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Single-file v0 foundation for Nemotron reasoning experiments.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_public_smoke_parser = subparsers.add_parser("prepare-public-smoke")
    prepare_public_smoke_parser.add_argument("--input-csv", default=str(RAW_TEST_PATH))
    prepare_public_smoke_parser.add_argument("--output-csv", default=str(DEFAULT_PUBLIC_SMOKE_PATH))
    prepare_public_smoke_parser.add_argument("--train-csv", default=str(RAW_TRAIN_PATH))
    prepare_public_smoke_parser.add_argument(
        "--manifest-csv",
        default=str(DEFAULT_PUBLIC_SMOKE_MANIFEST_PATH),
    )
    prepare_public_smoke_parser.set_defaults(func=command_prepare_public_smoke)

    metadata_parser = subparsers.add_parser("build-metadata")
    metadata_parser.add_argument("--input-csv", default=str(RAW_TRAIN_PATH))
    metadata_parser.add_argument("--public-smoke-csv", default=str(DEFAULT_PUBLIC_SMOKE_PATH))
    metadata_parser.add_argument("--output", default=str(DEFAULT_METADATA_PATH))
    metadata_parser.set_defaults(func=command_build_metadata)

    splits_parser = subparsers.add_parser("build-splits")
    splits_parser.add_argument("--input-csv", default=str(DEFAULT_METADATA_PATH))
    splits_parser.add_argument("--output", default=str(DEFAULT_SPLITS_PATH))
    splits_parser.add_argument("--random-state", type=int, default=42)
    splits_parser.set_defaults(func=command_build_splits)

    shadow_parser = subparsers.add_parser("build-shadow-packs")
    shadow_parser.add_argument("--input-csv", default=str(DEFAULT_SPLITS_PATH))
    shadow_parser.add_argument("--output-dir", default=str(EVAL_PACKS_DIR))
    shadow_parser.add_argument("--random-state", type=int, default=42)
    shadow_parser.set_defaults(func=command_build_shadow_packs)

    prompt_parser = subparsers.add_parser("build-prompt-snapshots")
    prompt_parser.add_argument("--input-csv", default=str(DEFAULT_SPLITS_PATH))
    prompt_parser.add_argument("--public-smoke-csv", default=str(DEFAULT_PUBLIC_SMOKE_PATH))
    prompt_parser.add_argument("--output", default=str(DEFAULT_PROMPT_SNAPSHOTS_PATH))
    prompt_parser.add_argument("--eval-config", default="official_lb")
    prompt_parser.add_argument("--tokenizer-path")
    prompt_parser.add_argument("--tokenizer-name")
    prompt_parser.add_argument("--tokenizer-revision")
    prompt_parser.set_defaults(func=command_build_prompt_snapshots)

    eval_parser = subparsers.add_parser("run-local-eval")
    eval_parser.add_argument("--predictions-csv", required=True)
    eval_parser.add_argument("--splits-parquet", default=str(DEFAULT_SPLITS_PATH))
    eval_parser.add_argument("--output-dir", required=True)
    eval_parser.add_argument("--run-name", required=True)
    eval_parser.add_argument("--model-name", default="unknown-model")
    eval_parser.add_argument("--adapter-name", default="unknown-adapter")
    eval_parser.add_argument("--eval-config", default="official_lb")
    eval_parser.add_argument("--row-id-column", default="id")
    eval_parser.add_argument("--prediction-column", default="prediction")
    eval_parser.add_argument("--raw-output-column", default="raw_output")
    eval_parser.set_defaults(func=command_run_local_eval)

    compare_parser = subparsers.add_parser("compare-shadow-results")
    compare_parser.add_argument("--local-predictions-csv", required=True)
    compare_parser.add_argument("--kaggle-predictions-csv", required=True)
    compare_parser.add_argument("--splits-parquet", default=str(DEFAULT_SPLITS_PATH))
    compare_parser.add_argument("--row-id-column", default="id")
    compare_parser.add_argument("--prediction-column", default="prediction")
    compare_parser.add_argument("--raw-output-column", default="raw_output")
    compare_parser.add_argument("--output-csv")
    compare_parser.set_defaults(func=command_compare_shadow_results)

    baselines_parser = subparsers.add_parser("init-baselines")
    baselines_parser.add_argument("--output", default=str(DEFAULT_BASELINE_REGISTRY_PATH))
    baselines_parser.set_defaults(func=command_init_baselines)

    docs_parser = subparsers.add_parser("write-docs")
    docs_parser.set_defaults(func=command_write_docs)

    guide_parser = subparsers.add_parser("show-kaggle-rerun-guide")
    guide_parser.set_defaults(func=command_show_kaggle_rerun)

    validate_parser = subparsers.add_parser("validate-v0")
    validate_parser.set_defaults(func=command_validate_v0)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_version_directories()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
