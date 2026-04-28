from __future__ import annotations

import argparse
import csv
import dataclasses
import importlib.metadata as importlib_metadata
import json
import math
import os
import platform
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
import types
import zipfile
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime, timezone
from functools import lru_cache, partial
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
import pandas as pd
from safetensors.numpy import load_file, save_file
from mlx.nn.utils import average_gradients
from mlx.utils import tree_flatten, tree_map
from mlx_lm import batch_generate, generate, load as mlx_load, stream_generate
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.utils import linear_to_lora_layers, print_trainable_parameters
from mlx_lm.utils import save_config

REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = Path(__file__).resolve().parent
README_PATH = REPO_ROOT / "README.md"
AOPEN_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication"
AOPEN_NEMOTRON_ROOT = AOPEN_ROOT / "nemotron"
ADAPTER_VALIDATION_NOTEBOOK_PATH = AOPEN_ROOT / "adapter-validation-notebook.ipynb"
SNAPSHOT_ROOT = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "04-08-16-14"
SNAPSHOT_CONFIG_PATH = SNAPSHOT_ROOT / "config.json"
SNAPSHOT_INDEX_PATH = SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
SNAPSHOT_TOKENS_ROOT = SNAPSHOT_ROOT / "tokens"
TRAIN_CSV_PATH = REPO_ROOT / "data" / "train.csv"
PROBLEMS_INDEX_PATH = AOPEN_NEMOTRON_ROOT / "problems.jsonl"
ADAPTER_VALIDATION_SAMPLE_SIZE = 950
DEFAULT_ADAPTER_VALIDATION_ROOT_NAME = "adapter_validation"
DEFAULT_MINI_VALIDATION_ROOT_NAME = "adapter_validation_smoke8_snapshot"
DEFAULT_MINI_VALIDATION_SUBSET_SIZE = 8

DEFAULT_MODEL_ROOT = Path(
    "/Users/mac-studio/.cache/huggingface/hub/models--mlx-community--NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16"
)
DEFAULT_OUTPUT_ROOT = WORK_ROOT / "outputs"
BUNDLE_TOKENIZER_SHADOW_DIR = DEFAULT_OUTPUT_ROOT / "_bundle_tokenizer_shadow"
DEFAULT_RUN_NAME = "v20_mlx_repro_v1_fullrun"
DEFAULT_RESULTS_MD = WORK_ROOT / "v20_mlx_repro_v1-results.md"
DEFAULT_RESULTS_JSON = WORK_ROOT / "v20_mlx_repro_v1-results.json"
DEFAULT_SUBMISSION_BASE_MODEL_NAME_OR_PATH = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
README_REQUIRED_SUBMISSION_FILES = ("adapter_config.json", "adapter_model.safetensors")
README_SUBMISSION_ARCHIVE_NAME = "submission.zip"
TARGET_MODULE_ORDER = ("q_proj", "k_proj", "v_proj", "o_proj", "in_proj", "out_proj", "up_proj", "down_proj", "lm_head")

README_EVAL_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}
BOXED_INSTRUCTION = r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
BOXED_PATTERN = re.compile(r"\\boxed\{([^}]*)(?:\}|$)")
FINAL_ANSWER_PATTERNS = (
    r"The final answer is:\s*([^\n]+)",
    r"Final answer is:\s*([^\n]+)",
    r"Final answer:\s*([^\n]+)",
    r"final answer\s*[:：]\s*([^\n]+)",
)
NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
PAD_TO = 32
EVAL_RECORD_COLUMNS = (
    "id",
    "category",
    "expected_answer",
    "rendered_prompt",
    "raw_output",
    "extracted_answer",
    "is_correct",
    "fallback_type",
    "format_bucket",
    "has_boxed",
    "boxed_count",
)
VALIDATION_FINAL_COLUMNS = (
    "id",
    "prompt",
    "answer",
    "output",
    "category",
    "predicted",
    "correct",
    "minlogprob",
)
VALIDATION_RECORD_COLUMNS = ("row_index_within_shard",) + VALIDATION_FINAL_COLUMNS

V20_TARGETS = {
    "overall_accuracy": 8340 / 9500,
    "overall_correct": 8340,
    "overall_total": 9500,
    "leaderboard_public": 0.85,
    "categories": {
        "numeral": {"correct": 1576, "total": 1576},
        "unit_conversion": {"correct": 1590, "total": 1594},
        "gravity": {"correct": 1591, "total": 1597},
        "cipher": {"correct": 1565, "total": 1576},
        "bit_manipulation": {"correct": 1397, "total": 1602},
        "equation_numeric_deduce": {"correct": 541, "total": 596},
        "equation_numeric_guess": {"correct": 22, "total": 136},
        "cryptarithm_deduce": {"correct": 47, "total": 659},
        "cryptarithm_guess": {"correct": 11, "total": 164},
    },
}

ADAPTER_VALIDATION_NOTEBOOK_TARGET = {
    "overall_accuracy": 837 / 950,
    "overall_correct": 837,
    "overall_total": 950,
    "categories": {
        "bit_manipulation": {"correct": 149, "total": 169},
        "cipher": {"correct": 158, "total": 162},
        "cryptarithm_deduce": {"correct": 6, "total": 71},
        "cryptarithm_guess": {"correct": 3, "total": 14},
        "equation_numeric_deduce": {"correct": 42, "total": 48},
        "equation_numeric_guess": {"correct": 0, "total": 7},
        "gravity": {"correct": 159, "total": 159},
        "numeral": {"correct": 149, "total": 149},
        "unit_conversion": {"correct": 171, "total": 171},
    },
}

CUDA_ANALYSIS_ARTIFACTS_ROOT = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts"
TRAIN_VERIFIED_TRACE_READY_PATH = CUDA_ANALYSIS_ARTIFACTS_ROOT / "train_verified_trace_ready_v1.csv"
TRAIN_ANSWER_ONLY_KEEP_PATH = CUDA_ANALYSIS_ARTIFACTS_ROOT / "train_answer_only_keep_v1.csv"
TRAIN_MANUAL_AUDIT_PRIORITY_PATH = CUDA_ANALYSIS_ARTIFACTS_ROOT / "train_manual_audit_priority_v1.csv"
TRAIN_RECOMMENDED_LEARNING_TARGET_PATH = CUDA_ANALYSIS_ARTIFACTS_ROOT / "train_recommended_learning_target_v1.csv"
V11_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v11_bit_binary_mainline"
V11_RESULTS_MD = V11_RESULTS_DIR / "v20_corrective_corpus_v11_bit_binary_mainline-results.md"
V11_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v11_bit_binary_mainline_bundle.jsonl"
V11_VERSION_NAME = "v20_corrective_corpus_v11_bit_binary_mainline"
V11_RUN_NAME = "v20_mlx_v11_bit_binary_mainline_mlxdir_mb1_nobc_ckpt20"
V12_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v12_bit_binary_manual_heavy"
V12_RESULTS_MD = V12_RESULTS_DIR / "v20_corrective_corpus_v12_bit_binary_manual_heavy-results.md"
V12_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v12_bit_binary_manual_heavy_bundle.jsonl"
V12_VERSION_NAME = "v20_corrective_corpus_v12_bit_binary_manual_heavy"
V12_RUN_NAME = "v20_mlx_v12_bit_binary_manual_heavy_mlxdir_mb1_nobc_ckpt20"
V13_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v13_bit_binary_promptlocal_heavy"
V13_RESULTS_MD = V13_RESULTS_DIR / "v20_corrective_corpus_v13_bit_binary_promptlocal_heavy-results.md"
V13_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v13_bit_binary_promptlocal_heavy_bundle.jsonl"
V13_VERSION_NAME = "v20_corrective_corpus_v13_bit_binary_promptlocal_heavy"
V13_RUN_NAME = "v20_mlx_v13_bit_binary_promptlocal_heavy_mlxdir_mb1_nobc_ckpt20"
V14_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v14_bit_binary_structured_heavy"
V14_RESULTS_MD = V14_RESULTS_DIR / "v20_corrective_corpus_v14_bit_binary_structured_heavy-results.md"
V14_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v14_bit_binary_structured_heavy_bundle.jsonl"
V14_VERSION_NAME = "v20_corrective_corpus_v14_bit_binary_structured_heavy"
V14_RUN_NAME = "v20_mlx_v14_bit_binary_structured_heavy_mlxdir_mb1_nobc_ckpt20"
V15_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v15_bit_binary_bitother_heavy"
V15_RESULTS_MD = V15_RESULTS_DIR / "v20_corrective_corpus_v15_bit_binary_bitother_heavy-results.md"
V15_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v15_bit_binary_bitother_heavy_bundle.jsonl"
V15_VERSION_NAME = "v20_corrective_corpus_v15_bit_binary_bitother_heavy"
V15_RUN_NAME = "v20_mlx_v15_bit_binary_bitother_heavy_mlxdir_mb1_nobc_ckpt20"
V16_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v16_bit_binary_miss_family_heavy"
V16_RESULTS_MD = V16_RESULTS_DIR / "v20_corrective_corpus_v16_bit_binary_miss_family_heavy-results.md"
V16_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v16_bit_binary_miss_family_heavy_bundle.jsonl"
V16_VERSION_NAME = "v20_corrective_corpus_v16_bit_binary_miss_family_heavy"
V16_RUN_NAME = "v20_mlx_v16_bit_binary_miss_family_heavy_mlxdir_mb1_nobc_ckpt20"
V17_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v17_bit_binary_hybrid_miss_promptlocal"
V17_RESULTS_MD = V17_RESULTS_DIR / "v20_corrective_corpus_v17_bit_binary_hybrid_miss_promptlocal-results.md"
V17_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v17_bit_binary_hybrid_miss_promptlocal_bundle.jsonl"
V17_VERSION_NAME = "v20_corrective_corpus_v17_bit_binary_hybrid_miss_promptlocal"
V17_RUN_NAME = "v20_mlx_v17_bit_binary_hybrid_miss_promptlocal_mlxdir_mb1_nobc_ckpt20"
V18_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v18_bit_binary_explicit_local_miss"
V18_RESULTS_MD = V18_RESULTS_DIR / "v20_corrective_corpus_v18_bit_binary_explicit_local_miss-results.md"
V18_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v18_bit_binary_explicit_local_miss_bundle.jsonl"
V18_VERSION_NAME = "v20_corrective_corpus_v18_bit_binary_explicit_local_miss"
V18_RUN_NAME = "v20_mlx_v18_bit_binary_explicit_local_miss_mlxdir_mb1_nobc_ckpt20"
V19_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v19_bit_binary_hardscore_tail"
V19_RESULTS_MD = V19_RESULTS_DIR / "v20_corrective_corpus_v19_bit_binary_hardscore_tail-results.md"
V19_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v19_bit_binary_hardscore_tail_bundle.jsonl"
V19_VERSION_NAME = "v20_corrective_corpus_v19_bit_binary_hardscore_tail"
V19_RUN_NAME = "v20_mlx_v19_bit_binary_hardscore_tail_mlxdir_mb1_nobc_ckpt20"
V20_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v20_bit_binary_localmiss_hardscore_fusion"
V20_RESULTS_MD = V20_RESULTS_DIR / "v20_corrective_corpus_v20_bit_binary_localmiss_hardscore_fusion-results.md"
V20_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v20_bit_binary_localmiss_hardscore_fusion_bundle.jsonl"
V20_VERSION_NAME = "v20_corrective_corpus_v20_bit_binary_localmiss_hardscore_fusion"
V20_RUN_NAME = "v20_mlx_v20_bit_binary_localmiss_hardscore_fusion_mlxdir_mb1_nobc_ckpt20"
V21_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v21_bit_binary_structured_promptlocal_fusion"
V21_RESULTS_MD = V21_RESULTS_DIR / "v20_corrective_corpus_v21_bit_binary_structured_promptlocal_fusion-results.md"
V21_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v21_bit_binary_structured_promptlocal_fusion_bundle.jsonl"
V21_VERSION_NAME = "v20_corrective_corpus_v21_bit_binary_structured_promptlocal_fusion"
V21_RUN_NAME = "v20_mlx_v21_bit_binary_structured_promptlocal_fusion_mlxdir_mb1_nobc_ckpt20"
V22_RESULTS_DIR = REPO_ROOT / "versions" / "v20_corrective_corpus_v22_bit_binary_verified_precision_fusion"
V22_RESULTS_MD = V22_RESULTS_DIR / "v20_corrective_corpus_v22_bit_binary_verified_precision_fusion-results.md"
V22_BUNDLE_PATH = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "MLX" / "v20_corrective_corpus_v22_bit_binary_verified_precision_fusion_bundle.jsonl"
V22_VERSION_NAME = "v20_corrective_corpus_v22_bit_binary_verified_precision_fusion"
V22_RUN_NAME = "v20_mlx_v22_bit_binary_verified_precision_fusion_mlxdir_mb1_nobc_ckpt20"
V11_LOCAL_BIT_MISS_IDS = {
    "000b53cf",
    "012fb81b",
    "01e09228",
    "02a66bcb",
    "034fb629",
    "048cc279",
    "04d8c3e6",
    "05ca617c",
    "06881e47",
    "07e8cf66",
    "0b16458a",
    "0ec17d2e",
    "12fd5b6c",
    "132ec6ae",
    "16db2c74",
    "172d2417",
}
V11_LOCAL_NUMERIC_GUESS_MISS_IDS = {"065f9dea", "0c0683c3"}
V11_LOCAL_CIPHER_MISS_IDS = {"0184a864"}
V11_PRIORITY_BINARY_FAMILIES = {
    "choose(shl,shr,rol)",
    "choose(shl,shr,ror)",
    "majority(rol,shl,shr)",
    "majority(ror,shl,shr)",
    "xor(ror,shl)",
    "xor(shl,shr)",
    "choose(shr,shr,rol)",
    "choose(shl,shr1,rol3)",
}
V16_LOCAL_MISS_BINARY_FAMILIES = {
    "choose(not(rol1),not(shl7),ror)",
    "choose(rol,ror,shr)",
    "choose(shl,shr,nibble_swap)",
    "choose(shl,shr,rol)",
    "choose(shl,shr,ror)",
    "majority(nibble_swap,shl,shr)",
    "majority(rol,shl,shr)",
    "majority(ror,shl,shr)",
}
V11_BINARY_VERIFIED_SOURCE_MIX = "v11_binary_verified_curated"
V11_BINARY_ANSWER_ONLY_SOURCE_MIX = "v11_binary_answer_only_curated"
V11_BINARY_MANUAL_SOURCE_MIX = "v11_binary_manual_rescue"
V11_NUMERIC_GUESS_SOURCE_MIX = "v11_numeric_guess_rescue"
V11_CIPHER_SOURCE_MIX = "v11_cipher_guardrail"
V12_BINARY_VERIFIED_SOURCE_MIX = "v12_binary_verified_curated"
V12_BINARY_ANSWER_ONLY_SOURCE_MIX = "v12_binary_answer_only_curated"
V12_BINARY_MANUAL_SOURCE_MIX = "v12_binary_manual_full"
V12_NUMERIC_GUESS_SOURCE_MIX = "v12_numeric_guess_rescue"
V12_CIPHER_SOURCE_MIX = "v12_cipher_guardrail"
V13_BINARY_VERIFIED_SOURCE_MIX = "v13_binary_verified_promptlocal_heavy"
V13_BINARY_ANSWER_ONLY_SOURCE_MIX = "v13_binary_answer_only_curated"
V13_BINARY_MANUAL_SOURCE_MIX = "v13_binary_manual_promptlocal_heavy"
V13_NUMERIC_GUESS_SOURCE_MIX = "v13_numeric_guess_rescue"
V13_CIPHER_SOURCE_MIX = "v13_cipher_guardrail"
V14_BINARY_VERIFIED_SOURCE_MIX = "v14_binary_verified_structured_heavy"
V14_BINARY_ANSWER_ONLY_SOURCE_MIX = "v14_binary_answer_only_structured_heavy"
V14_BINARY_MANUAL_SOURCE_MIX = "v14_binary_manual_support"
V14_NUMERIC_GUESS_SOURCE_MIX = "v14_numeric_guess_rescue"
V14_CIPHER_SOURCE_MIX = "v14_cipher_guardrail"
V15_BINARY_VERIFIED_SOURCE_MIX = "v15_binary_verified_bitother_heavy"
V15_BINARY_ANSWER_ONLY_SOURCE_MIX = "v15_binary_answer_only_bitother_heavy"
V15_BINARY_MANUAL_SOURCE_MIX = "v15_binary_manual_bitother_heavy"
V15_NUMERIC_GUESS_SOURCE_MIX = "v15_numeric_guess_rescue"
V15_CIPHER_SOURCE_MIX = "v15_cipher_guardrail"
V16_BINARY_VERIFIED_SOURCE_MIX = "v16_binary_verified_miss_family_heavy"
V16_BINARY_ANSWER_ONLY_SOURCE_MIX = "v16_binary_answer_only_miss_family_heavy"
V16_BINARY_MANUAL_SOURCE_MIX = "v16_binary_manual_miss_family_heavy"
V16_NUMERIC_GUESS_SOURCE_MIX = "v16_numeric_guess_rescue"
V16_CIPHER_SOURCE_MIX = "v16_cipher_guardrail"
V17_BINARY_VERIFIED_SOURCE_MIX = "v17_binary_verified_hybrid"
V17_BINARY_ANSWER_ONLY_SOURCE_MIX = "v17_binary_answer_only_hybrid"
V17_BINARY_MANUAL_SOURCE_MIX = "v17_binary_manual_hybrid"
V17_NUMERIC_GUESS_SOURCE_MIX = "v17_numeric_guess_rescue"
V17_CIPHER_SOURCE_MIX = "v17_cipher_guardrail"
V18_BINARY_VERIFIED_SOURCE_MIX = "v18_binary_verified_local_miss"
V18_BINARY_ANSWER_ONLY_SOURCE_MIX = "v18_binary_answer_only_local_miss"
V18_BINARY_MANUAL_SOURCE_MIX = "v18_binary_manual_local_miss"
V18_NUMERIC_GUESS_SOURCE_MIX = "v18_numeric_guess_rescue"
V18_CIPHER_SOURCE_MIX = "v18_cipher_guardrail"
V19_BINARY_VERIFIED_SOURCE_MIX = "v19_binary_verified_hardscore_tail"
V19_BINARY_ANSWER_ONLY_SOURCE_MIX = "v19_binary_answer_only_hardscore_tail"
V19_BINARY_MANUAL_SOURCE_MIX = "v19_binary_manual_hardscore_tail"
V19_NUMERIC_GUESS_SOURCE_MIX = "v19_numeric_guess_rescue"
V19_CIPHER_SOURCE_MIX = "v19_cipher_guardrail"
V20_BINARY_VERIFIED_SOURCE_MIX = "v20_binary_verified_fusion"
V20_BINARY_ANSWER_ONLY_SOURCE_MIX = "v20_binary_answer_only_fusion"
V20_BINARY_MANUAL_SOURCE_MIX = "v20_binary_manual_fusion"
V20_NUMERIC_GUESS_SOURCE_MIX = "v20_numeric_guess_rescue"
V20_CIPHER_SOURCE_MIX = "v20_cipher_guardrail"
V21_BINARY_VERIFIED_SOURCE_MIX = "v21_binary_verified_structured_promptlocal"
V21_BINARY_ANSWER_ONLY_SOURCE_MIX = "v21_binary_answer_only_structured_promptlocal"
V21_BINARY_MANUAL_SOURCE_MIX = "v21_binary_manual_structured_promptlocal"
V21_NUMERIC_GUESS_SOURCE_MIX = "v21_numeric_guess_rescue"
V21_CIPHER_SOURCE_MIX = "v21_cipher_guardrail"
V22_BINARY_VERIFIED_SOURCE_MIX = "v22_binary_verified_precision"
V22_BINARY_ANSWER_ONLY_SOURCE_MIX = "v22_binary_answer_only_precision"
V22_BINARY_MANUAL_SOURCE_MIX = "v22_binary_manual_precision"
V22_NUMERIC_GUESS_SOURCE_MIX = "v22_numeric_guess_rescue"
V22_CIPHER_SOURCE_MIX = "v22_cipher_guardrail"
V11_PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)


@dataclasses.dataclass(frozen=True)
class SnapshotExample:
    problem_id: str
    category: str
    step: int
    order_in_step: int
    token_path: str
    prompt_length: int
    completion_length: int
    total_length: int
    num_loss_tokens: int


@dataclasses.dataclass(frozen=True)
class StepPlan:
    step: int
    examples: tuple[SnapshotExample, ...]


@dataclasses.dataclass
class TrainingArtifacts:
    run_root: Path
    shadow_model_dir: Path
    adapter_dir: Path
    bundle_token_dir: Path
    step_plan_path: Path
    snapshot_contract_path: Path
    config_path: Path
    train_report_jsonl: Path
    latest_train_report_path: Path
    training_result_path: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def command_path_value(path: Path) -> str:
    return relative_to_repo(Path(path).resolve())


def command_scalar_value(value: Any) -> str:
    if isinstance(value, Path):
        return command_path_value(value)
    return str(value)


def append_command_option(tokens: list[str], flag: str, value: Any) -> None:
    tokens.extend([flag, command_scalar_value(value)])


def append_command_bool_option(tokens: list[str], flag: str, enabled: bool) -> None:
    tokens.append(flag if enabled else f"--no-{flag.removeprefix('--')}")


def render_shell_command(tokens: Sequence[str]) -> str:
    return " \\\n  ".join(shlex.quote(str(token)) for token in tokens)


def write_command_script(path: Path, tokens: Sequence[str]) -> None:
    write_text(
        path,
        "\n".join(
            [
                "#!/bin/bash",
                "set -euo pipefail",
                f"cd {shlex.quote(str(REPO_ROOT))}",
                render_shell_command(tokens),
                "",
            ]
        ),
    )


def load_readme_submission_contract() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()
    if "adapter_config.json" not in text:
        raise ValueError("README.md no longer states that submission.zip must include adapter_config.json.")
    if README_SUBMISSION_ARCHIVE_NAME.lower() not in lower_text:
        raise ValueError(f"README.md no longer references submission archive {README_SUBMISSION_ARCHIVE_NAME}.")
    if "submit a lora adapter" not in lower_text:
        raise ValueError("README.md no longer states that the submission must be a LoRA adapter.")
    max_lora_rank: int | None = None
    for line in text.splitlines():
        if not line.startswith("max_lora_rank\t"):
            continue
        raw_value = line.split("\t", 1)[1].strip()
        if not raw_value:
            raise ValueError("Malformed README.md evaluation row for max_lora_rank.")
        try:
            max_lora_rank = int(raw_value)
        except ValueError as exc:
            raise ValueError(f"Malformed README.md evaluation value for max_lora_rank: {raw_value!r}") from exc
        break
    if max_lora_rank is None:
        raise ValueError("Missing README.md evaluation row for max_lora_rank.")
    contract = {
        "required_files": list(README_REQUIRED_SUBMISSION_FILES),
        "max_lora_rank": max_lora_rank,
        "single_adapter_submission_zip": True,
        "submission_archive_name": README_SUBMISSION_ARCHIVE_NAME,
    }
    if int(contract["max_lora_rank"]) != int(README_EVAL_CONTRACT["max_lora_rank"]):
        raise ValueError(
            "README.md submission contract mismatch for max_lora_rank: "
            f"expected {README_EVAL_CONTRACT['max_lora_rank']}, got {contract['max_lora_rank']}"
        )
    return contract


def extract_lora_hparams(adapter_config: dict[str, Any]) -> tuple[int, float, float, list[str]]:
    lora_parameters = adapter_config.get("lora_parameters")
    if not isinstance(lora_parameters, dict):
        raise ValueError("adapter_config.json is missing lora_parameters.")
    try:
        rank = int(lora_parameters["rank"])
    except Exception as exc:
        raise ValueError(f"Invalid LoRA rank in adapter_config.json: {lora_parameters.get('rank')}") from exc
    try:
        alpha = float(lora_parameters.get("scale", rank))
    except Exception as exc:
        raise ValueError(f"Invalid LoRA scale in adapter_config.json: {lora_parameters.get('scale')}") from exc
    try:
        dropout = float(lora_parameters.get("dropout", 0.0))
    except Exception as exc:
        raise ValueError(f"Invalid LoRA dropout in adapter_config.json: {lora_parameters.get('dropout')}") from exc
    raw_keys = lora_parameters.get("keys", [])
    if not isinstance(raw_keys, list) or not all(isinstance(item, str) for item in raw_keys):
        raise ValueError("adapter_config.json lora_parameters.keys must be a list of strings.")
    return rank, alpha, dropout, raw_keys


def build_submission_target_modules_regex(mlx_keys: list[str]) -> str:
    def has_any_fragment(*fragments: str) -> bool:
        return any(any(fragment in key for fragment in fragments) for key in mlx_keys)

    terminals: list[str] = []
    for terminal in TARGET_MODULE_ORDER:
        if terminal == "q_proj" and has_any_fragment(".mixer.q_proj.", "mixer.q_proj"):
            terminals.append(terminal)
        elif terminal == "k_proj" and has_any_fragment(".mixer.k_proj.", "mixer.k_proj"):
            terminals.append(terminal)
        elif terminal == "v_proj" and has_any_fragment(".mixer.v_proj.", "mixer.v_proj"):
            terminals.append(terminal)
        elif terminal == "o_proj" and has_any_fragment(".mixer.o_proj.", "mixer.o_proj"):
            terminals.append(terminal)
        elif terminal == "in_proj" and has_any_fragment(".mixer.in_proj.", "mixer.in_proj"):
            terminals.append(terminal)
        elif terminal == "out_proj" and has_any_fragment(".mixer.out_proj.", "mixer.out_proj"):
            terminals.append(terminal)
        elif terminal == "up_proj" and has_any_fragment(
            ".mixer.shared_experts.up_proj.",
            ".mixer.switch_mlp.fc1.",
            ".mixer.up_proj.",
            "mixer.shared_experts.up_proj",
            "mixer.switch_mlp.fc1",
            "mixer.up_proj",
        ):
            terminals.append(terminal)
        elif terminal == "down_proj" and has_any_fragment(
            ".mixer.shared_experts.down_proj.",
            ".mixer.switch_mlp.fc2.",
            ".mixer.down_proj.",
            "mixer.shared_experts.down_proj",
            "mixer.switch_mlp.fc2",
            "mixer.down_proj",
        ):
            terminals.append(terminal)
        elif terminal == "lm_head" and has_any_fragment(".lm_head.", "lm_head"):
            terminals.append(terminal)
    if not terminals:
        raise ValueError("Could not derive PEFT target_modules regex from MLX adapter keys.")
    non_root_terminals = [terminal for terminal in terminals if terminal != "lm_head"]
    if "lm_head" in terminals and non_root_terminals:
        return "(^lm_head$|.*\\.(" + "|".join(non_root_terminals) + ")$)"
    if "lm_head" in terminals:
        return "^lm_head$"
    return ".*\\.(" + "|".join(non_root_terminals) + ")$"


def ensure_nemotron_meta_import_stubs() -> None:
    def _stub(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Nemotron meta import stub was called at runtime.")

    for module_name in ("mamba_ssm", "mamba_ssm.ops", "mamba_ssm.ops.triton"):
        if module_name not in sys.modules:
            sys.modules[module_name] = types.ModuleType(module_name)
    layernorm_module = types.ModuleType("mamba_ssm.ops.triton.layernorm_gated")
    layernorm_module.rmsnorm_fn = _stub
    selective_module = types.ModuleType("mamba_ssm.ops.triton.selective_state_update")
    selective_module.selective_state_update = _stub
    ssd_module = types.ModuleType("mamba_ssm.ops.triton.ssd_combined")
    ssd_module.mamba_chunk_scan_combined = _stub
    ssd_module.mamba_split_conv1d_scan_combined = _stub
    sys.modules["mamba_ssm.ops.triton.layernorm_gated"] = layernorm_module
    sys.modules["mamba_ssm.ops.triton.selective_state_update"] = selective_module
    sys.modules["mamba_ssm.ops.triton.ssd_combined"] = ssd_module


def build_peft_adapter_config_payload(
    *,
    base_model_name_or_path: str,
    rank: int,
    alpha: float,
    dropout: float,
    target_modules: str,
) -> dict[str, Any]:
    return {
        "alora_invocation_tokens": None,
        "alpha_pattern": {},
        "arrow_config": None,
        "auto_mapping": None,
        "base_model_name_or_path": str(base_model_name_or_path),
        "bias": "none",
        "corda_config": None,
        "ensure_weight_tying": False,
        "eva_config": None,
        "exclude_modules": None,
        "fan_in_fan_out": False,
        "inference_mode": True,
        "init_lora_weights": True,
        "layer_replication": None,
        "layers_pattern": None,
        "layers_to_transform": None,
        "loftq_config": {},
        "lora_alpha": int(alpha) if float(alpha).is_integer() else float(alpha),
        "lora_bias": False,
        "lora_dropout": float(dropout),
        "megatron_config": None,
        "megatron_core": "megatron.core",
        "modules_to_save": None,
        "peft_type": "LORA",
        "peft_version": str(importlib_metadata.version("peft")),
        "qalora_group_size": 16,
        "r": int(rank),
        "rank_pattern": {},
        "revision": None,
        "target_modules": str(target_modules),
        "target_parameters": None,
        "task_type": "CAUSAL_LM",
        "trainable_token_indices": None,
        "use_dora": False,
        "use_qalora": False,
        "use_rslora": False,
    }


def build_reference_peft_shapes(
    *,
    reference_model_root: Path,
    target_modules: str,
    rank: int,
    alpha: float,
    dropout: float,
) -> dict[str, tuple[int, ...]]:
    from accelerate import init_empty_weights
    from peft import LoraConfig, TaskType, get_peft_model, get_peft_model_state_dict
    from transformers import AutoConfig, AutoModelForCausalLM

    ensure_nemotron_meta_import_stubs()
    config = AutoConfig.from_pretrained(str(reference_model_root), trust_remote_code=True)
    with init_empty_weights():
        model = AutoModelForCausalLM.from_config(config, trust_remote_code=True)
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=int(rank),
        lora_alpha=float(alpha),
        lora_dropout=float(dropout),
        target_modules=str(target_modules),
        bias="none",
        use_dora=False,
        modules_to_save=None,
        inference_mode=True,
    )
    model = get_peft_model(model, peft_config)
    return {
        key: tuple(value.shape)
        for key, value in get_peft_model_state_dict(model).items()
        if "lora_A" in key or "lora_B" in key
    }


def classify_submission_source_tensor(key: str) -> str:
    if ".mixer.q_proj." in key or ".mixer.k_proj." in key or ".mixer.v_proj." in key or ".mixer.o_proj." in key:
        return "attention"
    if ".mixer.switch_mlp.fc1." in key:
        return "switch_fc1"
    if ".mixer.switch_mlp.fc2." in key:
        return "switch_fc2"
    if ".mixer.shared_experts." in key:
        return "shared_experts"
    if ".mixer.in_proj." in key:
        return "in_proj"
    if ".mixer.out_proj." in key:
        return "out_proj"
    return "other"


def map_mlx_tensor_to_submission_entries(key: str, value: np.ndarray) -> list[tuple[str, np.ndarray]]:
    prefix, suffix = key.rsplit(".", 1)
    if suffix not in {"lora_a", "lora_b"}:
        raise ValueError(f"Unsupported LoRA tensor suffix: {key}")
    target_suffix = "lora_A.weight" if suffix == "lora_a" else "lora_B.weight"
    if ".mixer.switch_mlp.fc1." in key:
        if value.ndim != 3:
            raise ValueError(f"switch_mlp.fc1 tensor must be 3D, got {key}: {tuple(value.shape)}")
        base_prefix = prefix.replace(".mixer.switch_mlp.fc1", ".mixer.experts.{expert_index}.up_proj")
        return [
            (f"base_model.model.{base_prefix.format(expert_index=expert_index)}.{target_suffix}", value[expert_index])
            for expert_index in range(value.shape[0])
        ]
    if ".mixer.switch_mlp.fc2." in key:
        if value.ndim != 3:
            raise ValueError(f"switch_mlp.fc2 tensor must be 3D, got {key}: {tuple(value.shape)}")
        base_prefix = prefix.replace(".mixer.switch_mlp.fc2", ".mixer.experts.{expert_index}.down_proj")
        return [
            (f"base_model.model.{base_prefix.format(expert_index=expert_index)}.{target_suffix}", value[expert_index])
            for expert_index in range(value.shape[0])
        ]
    if value.ndim != 2:
        raise ValueError(f"Only 2D tensors are supported outside routed experts, got {key}: {tuple(value.shape)}")
    return [(f"base_model.model.{prefix}.{target_suffix}", value.T)]


def convert_mlx_adapter_to_submission_tensors(
    tensors: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]], dict[str, Any]]:
    converted: dict[str, np.ndarray] = {}
    conversion_preview: list[dict[str, Any]] = []
    source_rank_counts: dict[int, int] = {}
    source_family_counts: dict[str, int] = {}
    for source_key, value in sorted(tensors.items()):
        source_rank_counts[value.ndim] = source_rank_counts.get(value.ndim, 0) + 1
        family = classify_submission_source_tensor(source_key)
        source_family_counts[family] = source_family_counts.get(family, 0) + 1
        mapped_entries = map_mlx_tensor_to_submission_entries(source_key, value)
        for target_key, mapped_value in mapped_entries:
            converted[target_key] = mapped_value
            if len(conversion_preview) < 48:
                conversion_preview.append(
                    {
                        "source_key": source_key,
                        "source_shape": list(value.shape),
                        "target_key": target_key,
                        "target_shape": list(mapped_value.shape),
                    }
                )
    source_summary = {
        "source_tensor_count": len(tensors),
        "source_tensor_rank_counts": [
            {"tensor_rank": int(rank), "tensor_count": int(source_rank_counts[rank])}
            for rank in sorted(source_rank_counts)
        ],
        "source_family_counts": [
            {"family": family, "tensor_count": int(source_family_counts[family])}
            for family in sorted(source_family_counts)
        ],
    }
    return converted, conversion_preview, source_summary


def validate_submission_tensors(
    converted_tensors: dict[str, np.ndarray],
    reference_shapes: dict[str, tuple[int, ...]],
) -> dict[str, Any]:
    converted_keys = set(converted_tensors)
    reference_keys = set(reference_shapes)
    missing_keys = sorted(reference_keys - converted_keys)
    unexpected_keys = sorted(converted_keys - reference_keys)
    shape_mismatches: list[dict[str, Any]] = []
    for key in sorted(converted_keys & reference_keys):
        converted_shape = tuple(converted_tensors[key].shape)
        reference_shape = tuple(reference_shapes[key])
        if converted_shape != reference_shape:
            shape_mismatches.append(
                {
                    "key": key,
                    "converted_shape": list(converted_shape),
                    "reference_shape": list(reference_shape),
                }
            )
    return {
        "valid": not missing_keys and not unexpected_keys and not shape_mismatches,
        "converted_tensor_count": len(converted_tensors),
        "reference_tensor_count": len(reference_shapes),
        "missing_key_count": len(missing_keys),
        "unexpected_key_count": len(unexpected_keys),
        "shape_mismatch_count": len(shape_mismatches),
        "missing_key_examples": missing_keys[:12],
        "unexpected_key_examples": unexpected_keys[:12],
        "shape_mismatch_examples": shape_mismatches[:12],
    }


def resolve_submission_reference_model_root(
    *,
    run_root: Path,
    adapter_config: dict[str, Any],
    explicit_reference_model_root: Path | None,
) -> Path:
    if explicit_reference_model_root is not None:
        return Path(explicit_reference_model_root).resolve()
    configured_model_root = adapter_config.get("model")
    if isinstance(configured_model_root, str) and configured_model_root.strip():
        return Path(configured_model_root).resolve()
    return (run_root / "shadow_model").resolve()


def write_submission_export_results_md(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        f"# {manifest['run_name']} submission export",
        "",
        "## README contract",
        "",
        "- source_document: `README.md`",
        f"- max_lora_rank: `{manifest['readme_submission_contract']['max_lora_rank']}`",
        f"- required files: `{', '.join(manifest['readme_submission_contract']['required_files'])}`",
        f"- archive name: `{manifest['readme_submission_contract']['submission_archive_name']}`",
        "",
        "## Export summary",
        "",
        f"- created_at: `{manifest['created_at']}`",
        f"- run_root: `{manifest['run_root']}`",
        f"- source_adapter_dir: `{manifest['source_adapter_dir']}`",
        f"- reference_model_root: `{manifest['reference_model_root']}`",
        f"- output_root: `{manifest['output_root']}`",
        f"- submission.zip: `{manifest['submission_zip_path']}`",
        f"- submission.zip size: `{manifest['submission_zip_size_bytes']}` bytes",
        f"- base_model_name_or_path: `{manifest['base_model_name_or_path']}`",
        f"- target_modules regex: `{manifest['target_modules']}`",
        f"- rank: `{manifest['rank']}`",
        f"- lora_alpha: `{manifest['lora_alpha']}`",
        f"- lora_dropout: `{manifest['lora_dropout']}`",
        f"- converted_tensor_count: `{manifest['converted_tensor_count']}`",
        f"- validation.valid: `{manifest['validation']['valid']}`",
        "",
        "## submission.zip members",
        "",
    ]
    lines.extend(f"- `{member}`" for member in manifest["submission_zip_members"])
    write_text(path, "\n".join(lines) + "\n")


def resolve_training_data_path(args: argparse.Namespace) -> Path:
    if getattr(args, "training_bundle_path", None) is not None:
        return Path(args.training_bundle_path).resolve()
    return SNAPSHOT_ROOT


def build_command_prefix(command: str) -> list[str]:
    return ["uv", "run", "python", command_path_value(Path(__file__).resolve()), command]


def build_train_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_command_prefix("train")
    append_command_option(tokens, "--model-root", Path(args.model_root))
    append_command_option(tokens, "--output-root", Path(args.output_root))
    append_command_option(tokens, "--run-name", args.run_name)
    if args.training_bundle_path is not None:
        append_command_option(tokens, "--training-bundle-path", Path(args.training_bundle_path))
    if bool(args.force_shadow_model):
        tokens.append("--force-shadow-model")
    append_command_option(tokens, "--seed", int(args.seed))
    append_command_option(tokens, "--batch-size", int(args.batch_size))
    append_command_option(tokens, "--micro-batch-size", int(args.micro_batch_size))
    append_command_option(tokens, "--learning-rate", float(args.learning_rate))
    append_command_option(tokens, "--max-seq-length", int(args.max_seq_length))
    append_command_bool_option(tokens, "--fixed-train-padding", bool(args.fixed_train_padding))
    append_command_option(tokens, "--lora-rank", int(args.lora_rank))
    append_command_option(tokens, "--lora-alpha", float(args.lora_alpha))
    append_command_option(tokens, "--lora-dropout", float(args.lora_dropout))
    append_command_option(tokens, "--beta1", float(args.beta1))
    append_command_option(tokens, "--beta2", float(args.beta2))
    append_command_option(tokens, "--eps", float(args.eps))
    append_command_option(tokens, "--weight-decay", float(args.weight_decay))
    append_command_bool_option(tokens, "--bias-correction", bool(args.bias_correction))
    append_command_option(tokens, "--steps-per-report", int(args.steps_per_report))
    append_command_option(tokens, "--save-every-steps", int(args.save_every_steps))
    append_command_option(tokens, "--max-saved-checkpoints", int(args.max_saved_checkpoints))
    if args.resume_adapter_file is not None:
        append_command_option(tokens, "--resume-adapter-file", Path(args.resume_adapter_file))
    append_command_option(tokens, "--max-optimizer-steps", int(args.max_optimizer_steps))
    return tokens


def build_eval_adapter_validation_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_command_prefix("eval-adapter-validation")
    append_command_option(tokens, "--output-root", Path(args.output_root))
    append_command_option(tokens, "--run-name", args.run_name)
    append_command_option(tokens, "--adapter-validation-root-name", str(args.adapter_validation_root_name))
    append_command_option(tokens, "--max-tokens", int(args.max_tokens))
    append_command_option(tokens, "--temperature", float(args.temperature))
    append_command_option(tokens, "--top-p", float(args.top_p))
    append_command_option(tokens, "--max-num-seqs", int(args.max_num_seqs))
    append_command_option(tokens, "--max-model-len", int(args.max_model_len))
    append_command_option(tokens, "--prompt-chunk-size", int(args.prompt_chunk_size))
    append_command_option(tokens, "--prefill-batch-size", int(args.prefill_batch_size))
    append_command_option(tokens, "--completion-batch-size", int(args.completion_batch_size))
    append_command_option(tokens, "--eval-limit", int(args.eval_limit))
    append_command_option(tokens, "--validation-sample-size", int(args.validation_sample_size))
    append_command_option(tokens, "--validation-subset-size", int(args.validation_subset_size))
    append_command_option(tokens, "--validation-subset-mode", str(args.validation_subset_mode))
    append_command_option(tokens, "--eval-shards", int(args.eval_shards))
    append_command_option(tokens, "--eval-shard-index", int(args.eval_shard_index))
    append_command_bool_option(tokens, "--eval-enable-thinking", bool(args.eval_enable_thinking))
    append_command_bool_option(tokens, "--lazy-load", bool(args.lazy_load))
    if bool(args.force_single_generate):
        tokens.append("--force-single-generate")
    return tokens


def build_merge_adapter_validation_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_command_prefix("merge-adapter-validation")
    append_command_option(tokens, "--output-root", Path(args.output_root))
    append_command_option(tokens, "--run-name", args.run_name)
    append_command_option(tokens, "--adapter-validation-root-name", str(args.adapter_validation_root_name))
    append_command_option(tokens, "--max-tokens", int(args.max_tokens))
    append_command_option(tokens, "--temperature", float(args.temperature))
    append_command_option(tokens, "--top-p", float(args.top_p))
    append_command_option(tokens, "--max-num-seqs", int(args.max_num_seqs))
    append_command_option(tokens, "--max-model-len", int(args.max_model_len))
    append_command_option(tokens, "--prompt-chunk-size", int(args.prompt_chunk_size))
    append_command_option(tokens, "--prefill-batch-size", int(args.prefill_batch_size))
    append_command_option(tokens, "--completion-batch-size", int(args.completion_batch_size))
    append_command_option(tokens, "--validation-sample-size", int(args.validation_sample_size))
    append_command_option(tokens, "--validation-subset-size", int(args.validation_subset_size))
    append_command_option(tokens, "--validation-subset-mode", str(args.validation_subset_mode))
    append_command_bool_option(tokens, "--eval-enable-thinking", bool(args.eval_enable_thinking))
    return tokens


def build_postprocess_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_command_prefix("postprocess-run")
    append_command_option(tokens, "--output-root", Path(args.output_root))
    append_command_option(tokens, "--run-name", args.run_name)
    append_command_option(tokens, "--adapter-validation-root-name", str(args.adapter_validation_root_name))
    append_command_option(tokens, "--postprocess-eval-kind", str(args.postprocess_eval_kind))
    append_command_bool_option(tokens, "--cleanup-completed-run-artifacts", bool(args.cleanup_completed_run_artifacts))
    return tokens


def build_manage_run_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_train_command_tokens(args)
    tokens[4] = "manage-run"
    append_command_option(tokens, "--adapter-validation-root-name", str(args.adapter_validation_root_name))
    append_command_option(tokens, "--max-tokens", int(args.max_tokens))
    append_command_option(tokens, "--temperature", float(args.temperature))
    append_command_option(tokens, "--top-p", float(args.top_p))
    append_command_option(tokens, "--max-num-seqs", int(args.max_num_seqs))
    append_command_option(tokens, "--max-model-len", int(args.max_model_len))
    append_command_option(tokens, "--prompt-chunk-size", int(args.prompt_chunk_size))
    append_command_option(tokens, "--prefill-batch-size", int(args.prefill_batch_size))
    append_command_option(tokens, "--completion-batch-size", int(args.completion_batch_size))
    append_command_option(tokens, "--eval-limit", int(args.eval_limit))
    append_command_option(tokens, "--validation-sample-size", int(args.validation_sample_size))
    append_command_option(tokens, "--validation-subset-size", int(args.validation_subset_size))
    append_command_option(tokens, "--validation-subset-mode", str(args.validation_subset_mode))
    append_command_option(tokens, "--mini-validation-subset-size", int(args.mini_validation_subset_size))
    append_command_option(tokens, "--mini-validation-subset-mode", str(args.mini_validation_subset_mode))
    append_command_option(tokens, "--mini-validation-root-name", str(args.mini_validation_root_name))
    append_command_option(tokens, "--eval-shards", int(args.eval_shards))
    append_command_option(tokens, "--eval-shard-index", int(args.eval_shard_index))
    append_command_bool_option(tokens, "--eval-enable-thinking", bool(args.eval_enable_thinking))
    append_command_bool_option(tokens, "--lazy-load", bool(args.lazy_load))
    if bool(args.force_single_generate):
        tokens.append("--force-single-generate")
    append_command_option(tokens, "--postprocess-eval-kind", str(args.postprocess_eval_kind))
    append_command_bool_option(tokens, "--cleanup-completed-run-artifacts", bool(args.cleanup_completed_run_artifacts))
    append_command_option(tokens, "--manager-sleep-seconds", int(args.manager_sleep_seconds))
    append_command_option(tokens, "--progress-watch-interval-seconds", int(args.progress_watch_interval_seconds))
    append_command_option(tokens, "--stall-check-interval-seconds", int(args.stall_check_interval_seconds))
    append_command_option(tokens, "--stall-threshold-seconds", int(args.stall_threshold_seconds))
    return tokens


def build_queue_managed_run_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_manage_run_command_tokens(args)
    tokens[4] = "queue-managed-run"
    append_command_option(tokens, "--queue-log-path", Path(args.queue_log_path))
    append_command_option(tokens, "--queue-sleep-seconds", int(args.queue_sleep_seconds))
    append_command_option(tokens, "--max-active-trains-before-launch", int(args.max_active_trains_before_launch))
    for path in getattr(args, "wait_for_any_training_result_run_root", []) or []:
        append_command_option(tokens, "--wait-for-any-training-result-run-root", Path(path))
    for path in getattr(args, "require_run_start_run_root", []) or []:
        append_command_option(tokens, "--require-run-start-run-root", Path(path))
    return tokens


def build_watch_score_publish_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_command_prefix("watch-score-publish")
    append_command_option(tokens, "--score-watch-log-path", Path(args.score_watch_log_path))
    append_command_option(tokens, "--score-watch-state-dir", Path(args.score_watch_state_dir))
    append_command_option(tokens, "--score-watch-sleep-seconds", int(args.score_watch_sleep_seconds))
    append_command_option(tokens, "--postprocess-eval-kind", str(args.postprocess_eval_kind))
    append_command_bool_option(tokens, "--cleanup-completed-run-artifacts", bool(args.cleanup_completed_run_artifacts))
    for path in getattr(args, "watch_run_root", []) or []:
        append_command_option(tokens, "--watch-run-root", Path(path))
    return tokens


def build_watch_progress_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_command_prefix("watch-progress-ledger")
    append_command_option(tokens, "--progress-watch-log-path", Path(args.progress_watch_log_path))
    append_command_option(tokens, "--progress-watch-state-dir", Path(args.progress_watch_state_dir))
    append_command_option(tokens, "--progress-watch-sleep-seconds", int(args.progress_watch_sleep_seconds))
    append_command_option(tokens, "--progress-watch-step-interval", int(args.progress_watch_step_interval))
    for path in getattr(args, "watch_run_root", []) or []:
        append_command_option(tokens, "--watch-run-root", Path(path))
    return tokens


def build_export_submission_command_tokens(args: argparse.Namespace) -> list[str]:
    tokens = build_command_prefix("export-submission")
    append_command_option(tokens, "--output-root", Path(args.output_root))
    append_command_option(tokens, "--run-name", args.run_name)
    if getattr(args, "source_adapter_dir", None) is not None:
        append_command_option(tokens, "--source-adapter-dir", Path(args.source_adapter_dir))
    if getattr(args, "submission_output_root", None) is not None:
        append_command_option(tokens, "--submission-output-root", Path(args.submission_output_root))
    if getattr(args, "reference_model_root", None) is not None:
        append_command_option(tokens, "--reference-model-root", Path(args.reference_model_root))
    append_command_option(tokens, "--base-model-name-or-path", str(args.base_model_name_or_path))
    return tokens


def load_run_manifest_for_result(run_result: dict[str, Any]) -> dict[str, Any]:
    run_root_raw = run_result.get("run_root")
    if not run_root_raw:
        return {}
    manifest_path = Path(str(run_root_raw)).resolve() / "run_manifest.json"
    if not manifest_path.exists():
        return {}
    return load_json(manifest_path)


def resolve_score_ledger_target(run_result: dict[str, Any]) -> tuple[Path, str | None, str] | None:
    manifest = load_run_manifest_for_result(run_result)
    run_name = str(manifest.get("run_name", "")) if isinstance(manifest, dict) else ""
    training_data = manifest.get("training_data") if isinstance(manifest, dict) else None
    bundle_name = ""
    if isinstance(training_data, dict):
        bundle_name = Path(str(training_data.get("path", ""))).name
    if bundle_name == "v7_targeted_miss_recovery_bundle.jsonl" or "v20_mlx_v7_targeted_miss_recovery" in run_name:
        return (
            REPO_ROOT / "v20_mlx_repro_v1/experiments/v7/v7_targeted_miss_recovery-results.md",
            None,
            "- local300 score after training:",
        )
    v8_targets = {
        "bit_family_rebalance_broadbase_bundle.jsonl": "bit_family_rebalance_broadbase",
        "symbol_cipher_recovery_mix_bundle.jsonl": "symbol_cipher_recovery_mix",
        "hybrid_bridge_bundle.jsonl": "hybrid_bridge",
    }
    for bundle_key, section_name in v8_targets.items():
        if bundle_name == bundle_key or section_name in run_name:
            return (
                REPO_ROOT / "v20_mlx_repro_v1/experiments/v8/v8_parallel_variants-results.md",
                section_name,
                "- local300 score:",
            )
    if bundle_name == "v20_corrective_corpus_v10_mainline_bundle.jsonl" or "v20_mlx_v10_mainline" in run_name:
        return (
            REPO_ROOT / "versions/v20_corrective_corpus_v10_mainline/v20_corrective_corpus_v10_mainline-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v11_bit_binary_mainline_bundle.jsonl" or "v20_mlx_v11_bit_binary_mainline" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v11_bit_binary_mainline/v20_corrective_corpus_v11_bit_binary_mainline-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v12_bit_binary_manual_heavy_bundle.jsonl" or "v20_mlx_v12_bit_binary_manual_heavy" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v12_bit_binary_manual_heavy/v20_corrective_corpus_v12_bit_binary_manual_heavy-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v13_bit_binary_promptlocal_heavy_bundle.jsonl" or "v20_mlx_v13_bit_binary_promptlocal_heavy" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v13_bit_binary_promptlocal_heavy/v20_corrective_corpus_v13_bit_binary_promptlocal_heavy-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v14_bit_binary_structured_heavy_bundle.jsonl" or "v20_mlx_v14_bit_binary_structured_heavy" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v14_bit_binary_structured_heavy/v20_corrective_corpus_v14_bit_binary_structured_heavy-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v15_bit_binary_bitother_heavy_bundle.jsonl" or "v20_mlx_v15_bit_binary_bitother_heavy" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v15_bit_binary_bitother_heavy/v20_corrective_corpus_v15_bit_binary_bitother_heavy-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v16_bit_binary_miss_family_heavy_bundle.jsonl" or "v20_mlx_v16_bit_binary_miss_family_heavy" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v16_bit_binary_miss_family_heavy/v20_corrective_corpus_v16_bit_binary_miss_family_heavy-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v17_bit_binary_hybrid_miss_promptlocal_bundle.jsonl" or "v20_mlx_v17_bit_binary_hybrid_miss_promptlocal" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v17_bit_binary_hybrid_miss_promptlocal/v20_corrective_corpus_v17_bit_binary_hybrid_miss_promptlocal-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v18_bit_binary_explicit_local_miss_bundle.jsonl" or "v20_mlx_v18_bit_binary_explicit_local_miss" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v18_bit_binary_explicit_local_miss/v20_corrective_corpus_v18_bit_binary_explicit_local_miss-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v19_bit_binary_hardscore_tail_bundle.jsonl" or "v20_mlx_v19_bit_binary_hardscore_tail" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v19_bit_binary_hardscore_tail/v20_corrective_corpus_v19_bit_binary_hardscore_tail-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v20_bit_binary_localmiss_hardscore_fusion_bundle.jsonl" or "v20_mlx_v20_bit_binary_localmiss_hardscore_fusion" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v20_bit_binary_localmiss_hardscore_fusion/v20_corrective_corpus_v20_bit_binary_localmiss_hardscore_fusion-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v21_bit_binary_structured_promptlocal_fusion_bundle.jsonl" or "v20_mlx_v21_bit_binary_structured_promptlocal_fusion" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v21_bit_binary_structured_promptlocal_fusion/v20_corrective_corpus_v21_bit_binary_structured_promptlocal_fusion-results.md",
            None,
            "- local300 score:",
        )
    if bundle_name == "v20_corrective_corpus_v22_bit_binary_verified_precision_fusion_bundle.jsonl" or "v20_mlx_v22_bit_binary_verified_precision_fusion" in run_name:
        return (
            REPO_ROOT
            / "versions/v20_corrective_corpus_v22_bit_binary_verified_precision_fusion/v20_corrective_corpus_v22_bit_binary_verified_precision_fusion-results.md",
            None,
            "- local300 score:",
        )
    return None


def resolve_progress_ledger_target(run_root: Path) -> tuple[Path, str | None] | None:
    target = resolve_score_ledger_target({"run_root": str(run_root.resolve())})
    if target is None:
        return None
    ledger_path, section_name, _ = target
    return ledger_path, section_name


def replace_markdown_line_in_section(
    text: str,
    *,
    section_name: str | None,
    line_prefix: str,
    replacement_line: str,
) -> str:
    lines = text.splitlines()
    start_index = 0
    end_index = len(lines)
    if section_name is not None:
        section_heading = f"## {section_name}"
        for index, line in enumerate(lines):
            if line.strip() == section_heading:
                start_index = index + 1
                break
        else:
            raise FileNotFoundError(f"Missing markdown section {section_heading!r}")
        for index in range(start_index, len(lines)):
            if lines[index].startswith("## "):
                end_index = index
                break
    for index in range(start_index, end_index):
        if lines[index].startswith(line_prefix):
            lines[index] = replacement_line
            return "\n".join(lines) + "\n"
    insert_index = end_index
    while insert_index > start_index and lines[insert_index - 1].strip() == "":
        insert_index -= 1
    lines.insert(insert_index, replacement_line)
    return "\n".join(lines) + "\n"


def update_score_ledger(run_result: dict[str, Any], eval_result: dict[str, Any]) -> dict[str, Any] | None:
    target = resolve_score_ledger_target(run_result)
    if target is None:
        return None
    if str(eval_result.get("evaluation_kind", "")) != "adapter_validation":
        return None
    overall = eval_result.get("overall")
    if not isinstance(overall, dict) or "accuracy" not in overall:
        return None
    if int(overall.get("total", 0)) != 300:
        return None
    accuracy = float(overall["accuracy"])
    correct = overall.get("correct")
    total = overall.get("total")
    suffix = f"{accuracy:.6f}"
    if correct is not None and total is not None:
        suffix += f" ({int(correct)}/{int(total)})"
    ledger_path, section_name, line_prefix = target
    replacement_line = f"{line_prefix} {suffix}"
    original_text = ledger_path.read_text(encoding="utf-8")
    updated_text = replace_markdown_line_in_section(
        original_text,
        section_name=section_name,
        line_prefix=line_prefix,
        replacement_line=replacement_line,
    )
    changed = updated_text != original_text
    if changed:
        write_text(ledger_path, updated_text)
    return {
        "ledger_path": str(ledger_path.resolve()),
        "section_name": section_name,
        "line": replacement_line,
        "changed": changed,
    }


def summarize_retained_checkpoints(run_root: Path) -> str:
    checkpoint_names = [path.name for path in list_saved_checkpoints(run_root / "adapter")]
    return " / ".join(checkpoint_names) if checkpoint_names else "none"


def update_progress_ledger(run_root: Path, *, apply_changes: bool) -> dict[str, Any] | None:
    target = resolve_progress_ledger_target(run_root)
    if target is None:
        return None
    run_root_exists = run_root.exists()
    training_done = (run_root / "training_result.json").exists()
    validation_done = (run_root / "adapter_validation" / "validation_summary.json").exists()
    step, _ = read_latest_train_report(run_root)
    if step is None:
        step = read_training_result_step(run_root)
    checkpoint_summary = summarize_retained_checkpoints(run_root)
    if training_done and validation_done:
        runtime_status = "scored"
    elif training_done:
        runtime_status = "training_complete"
    elif step is not None:
        runtime_status = "running"
    elif run_root_exists:
        runtime_status = "queued"
    else:
        runtime_status = "not_started"
    step_display = step if step is not None else "not started"
    ledger_path, section_name = target
    original_text = ledger_path.read_text(encoding="utf-8")
    updated_text = replace_markdown_line_in_section(
        original_text,
        section_name=section_name,
        line_prefix="- runtime status:",
        replacement_line=f"- runtime status: `{runtime_status}`",
    )
    updated_text = replace_markdown_line_in_section(
        updated_text,
        section_name=section_name,
        line_prefix="- latest observed step:",
        replacement_line=f"- latest observed step: `{step_display}`",
    )
    updated_text = replace_markdown_line_in_section(
        updated_text,
        section_name=section_name,
        line_prefix="- retained checkpoints:",
        replacement_line=f"- retained checkpoints: `{checkpoint_summary}`",
    )
    changed = updated_text != original_text
    if apply_changes and changed:
        write_text(ledger_path, updated_text)
    return {
        "ledger_path": str(ledger_path.resolve()),
        "section_name": section_name,
        "step": step,
        "step_display": str(step_display),
        "checkpoint_summary": checkpoint_summary,
        "runtime_status": runtime_status,
        "changed": changed,
        "training_done": training_done,
    }


def local_now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_log_line(path: Path, message: str) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{local_now()}] {message}\n")


def git_index_lock_path() -> Path:
    return REPO_ROOT / ".git" / "index.lock"


def git_index_is_locked() -> bool:
    return git_index_lock_path().exists()


def has_git_diff(path: Path) -> bool:
    proc = subprocess.run(
        ["git", "diff", "--quiet", "--", relative_to_repo(path)],
        cwd=str(REPO_ROOT),
        check=False,
    )
    return proc.returncode == 1


def commit_and_push_tracked_file(
    *,
    tracked_path: Path,
    commit_message: str,
    log_path: Path,
    log_prefix: str,
) -> dict[str, Any]:
    if git_index_is_locked():
        append_log_line(log_path, f"{log_prefix}_git_busy path={relative_to_repo(tracked_path)}")
        return {"status": "git_busy", "tracked_path": str(tracked_path.resolve())}
    if not has_git_diff(tracked_path):
        append_log_line(log_path, f"{log_prefix}_no_diff path={relative_to_repo(tracked_path)}")
        return {"status": "no_ledger_diff", "tracked_path": str(tracked_path.resolve())}
    try:
        subprocess.run(["git", "add", "--", relative_to_repo(tracked_path)], cwd=str(REPO_ROOT), check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                commit_message,
                "-m",
                "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
            ],
            cwd=str(REPO_ROOT),
            check=True,
        )
        subprocess.run(["git", "push"], cwd=str(REPO_ROOT), check=True)
    except subprocess.CalledProcessError:
        if git_index_is_locked():
            append_log_line(log_path, f"{log_prefix}_git_busy path={relative_to_repo(tracked_path)}")
            return {"status": "git_busy", "tracked_path": str(tracked_path.resolve())}
        raise
    append_log_line(log_path, f"{log_prefix}_pushed path={relative_to_repo(tracked_path)}")
    return {
        "status": "score_pushed",
        "tracked_path": str(tracked_path.resolve()),
        "commit_message": commit_message,
    }


def commit_and_push_score_ledger(*, ledger_path: Path, run_name: str, log_path: Path) -> dict[str, Any]:
    return commit_and_push_tracked_file(
        tracked_path=ledger_path,
        commit_message=f"Publish local300 score for {run_name}",
        log_path=log_path,
        log_prefix="score_publish",
    )


def make_namespace_with(args: argparse.Namespace, **updates: Any) -> argparse.Namespace:
    payload = dict(vars(args))
    payload.update(updates)
    return argparse.Namespace(**payload)


def read_latest_train_report(run_root: Path) -> tuple[int | None, int | None]:
    report_path = run_root / "adapter" / "latest_train_report.json"
    if not report_path.exists():
        return None, None
    payload = load_json(report_path)
    step = payload.get("step")
    age_seconds = int(time.time() - report_path.stat().st_mtime)
    return int(step) if step is not None else None, age_seconds


def read_training_result_step(run_root: Path) -> int | None:
    training_result_path = run_root / "training_result.json"
    if not training_result_path.exists():
        return None
    payload = load_json(training_result_path)
    latest_report = payload.get("latest_train_report")
    if not isinstance(latest_report, dict):
        return None
    step = latest_report.get("step")
    return int(step) if step is not None else None


def parse_ps_elapsed_seconds(raw_value: str) -> int | None:
    value = raw_value.strip()
    if not value:
        return None
    day_count = 0
    if "-" in value:
        day_text, _, value = value.partition("-")
        if not day_text.isdigit():
            return None
        day_count = int(day_text)
    parts = value.split(":")
    if len(parts) == 2:
        hour_count = 0
        minute_text, second_text = parts
    elif len(parts) == 3:
        hour_text, minute_text, second_text = parts
        if not hour_text.isdigit():
            return None
        hour_count = int(hour_text)
    else:
        return None
    if not minute_text.isdigit() or not second_text.isdigit():
        return None
    return day_count * 86400 + hour_count * 3600 + int(minute_text) * 60 + int(second_text)


def read_process_elapsed_seconds(pid: int) -> int | None:
    proc = subprocess.run(
        ["ps", "-o", "etime=", "-p", str(pid)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return parse_ps_elapsed_seconds(proc.stdout)


def list_saved_checkpoints(adapter_dir: Path) -> list[Path]:
    return sorted(adapter_dir.glob("*_adapters.safetensors"))


def find_latest_checkpoint_path(adapter_dir: Path) -> Path | None:
    checkpoint_paths = list_saved_checkpoints(adapter_dir)
    return checkpoint_paths[-1] if checkpoint_paths else None


def matches_python_driver_command(line: str, script_name: str, command_name: str) -> bool:
    command_marker = f"{script_name} {command_name}"
    if command_marker not in line:
        return False
    if "bash -c" in line or "bash -lc" in line:
        return False
    if line.startswith("uv run "):
        return False
    return "python" in line


def find_run_command_pids(run_name: str, command_name: str) -> list[int]:
    proc = subprocess.run(["ps", "-axo", "pid,command"], capture_output=True, text=True, check=True)
    script_name = Path(__file__).name
    pids: list[int] = []
    for raw_line in proc.stdout.splitlines():
        line = raw_line.strip()
        if not line or script_name not in line:
            continue
        if f"--run-name {run_name}" not in line:
            continue
        _, _, command_line = line.partition(" ")
        if not matches_python_driver_command(command_line, script_name, command_name):
            continue
        pid_text, _, _ = line.partition(" ")
        if pid_text.isdigit():
            pids.append(int(pid_text))
    return pids


def count_active_train_processes() -> int:
    proc = subprocess.run(["ps", "-axo", "command"], capture_output=True, text=True, check=True)
    script_name = Path(__file__).name
    count = 0
    for raw_line in proc.stdout.splitlines():
        line = raw_line.strip()
        if not line or script_name not in line:
            continue
        if not matches_python_driver_command(line, script_name, "train"):
            continue
        count += 1
    return count


def spawn_detached_command(tokens: Sequence[str], *, log_path: Path) -> int:
    ensure_dir(log_path.parent)
    env = os.environ.copy()
    env.setdefault("UV_NO_PROGRESS", "1")
    with log_path.open("a", encoding="utf-8") as handle:
        proc = subprocess.Popen(
            list(tokens),
            cwd=str(REPO_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return int(proc.pid)


def resolve_hf_snapshot(model_root: Path) -> Path:
    resolved_root = Path(model_root).resolve()
    if (resolved_root / "config.json").exists():
        return resolved_root
    snapshots_dir = resolved_root / "snapshots"
    refs_dir = resolved_root / "refs"
    main_ref = refs_dir / "main"
    if main_ref.exists():
        snapshot_name = main_ref.read_text(encoding="utf-8").strip()
        candidate = snapshots_dir / snapshot_name
        if candidate.exists():
            return candidate
    if not snapshots_dir.exists():
        raise FileNotFoundError(f"No config.json or snapshots/ found under model_root={resolved_root}")
    snapshots = sorted(path for path in snapshots_dir.iterdir() if path.is_dir())
    if not snapshots:
        raise FileNotFoundError(f"No Hugging Face snapshots found under {snapshots_dir}")
    return snapshots[-1]


def build_shadow_model_dir(model_root: Path, shadow_dir: Path, *, force: bool = False) -> Path:
    source_snapshot = resolve_hf_snapshot(model_root)
    manifest_path = shadow_dir / "shadow_manifest.json"
    tokenizer_config_path = shadow_dir / "tokenizer_config.json"
    current_manifest = load_json(manifest_path) if manifest_path.exists() else {}
    rebuild = force
    if not shadow_dir.exists():
        rebuild = True
    elif current_manifest.get("source_snapshot") != str(source_snapshot):
        rebuild = True
    elif not tokenizer_config_path.exists():
        rebuild = True
    else:
        try:
            tokenizer_config = load_json(tokenizer_config_path)
        except json.JSONDecodeError:
            rebuild = True
        else:
            rebuild = tokenizer_config.get("tokenizer_class") != "PreTrainedTokenizerFast"

    if rebuild:
        if shadow_dir.exists():
            shutil.rmtree(shadow_dir)
        ensure_dir(shadow_dir)
        for child in source_snapshot.iterdir():
            if child.name == "tokenizer_config.json":
                continue
            (shadow_dir / child.name).symlink_to(child)
        tokenizer_config = load_json(source_snapshot / "tokenizer_config.json")
        tokenizer_config["tokenizer_class"] = "PreTrainedTokenizerFast"
        tokenizer_config.setdefault("clean_up_tokenization_spaces", False)
        write_json(tokenizer_config_path, tokenizer_config)
        write_json(
            manifest_path,
            {
                "created_at": utc_now(),
                "source_snapshot": str(source_snapshot),
                "tokenizer_class_patch": "PreTrainedTokenizerFast",
            },
        )
    return shadow_dir


def maybe_fix_tokenizer_eos_ids(tokenizer: Any) -> None:
    eos_token_id = getattr(tokenizer, "eos_token_id", None)
    eos_token = getattr(tokenizer, "eos_token", None)
    eos_token_ids = getattr(tokenizer, "eos_token_ids", None)
    if eos_token_id is None or eos_token != "<|im_end|>":
        return
    normalized_ids: set[int] = set()
    if eos_token_ids is not None:
        try:
            normalized_ids = {int(token_id) for token_id in eos_token_ids}
        except TypeError:
            normalized_ids = {int(eos_token_ids)}
    expected_id = int(eos_token_id)
    if normalized_ids != {expected_id}:
        tokenizer.eos_token_ids = {expected_id}


def normalize_tokenizer_for_hf_parity(tokenizer: Any) -> None:
    maybe_fix_tokenizer_eos_ids(tokenizer)
    eos_token = getattr(tokenizer, "eos_token", None)
    eos_token_id = getattr(tokenizer, "eos_token_id", None)
    if getattr(tokenizer, "pad_token", None) is None and eos_token is not None:
        try:
            tokenizer.pad_token = eos_token
        except (AttributeError, TypeError, ValueError):
            pass
    if getattr(tokenizer, "pad_token_id", None) is None and eos_token_id is not None:
        try:
            tokenizer.pad_token_id = int(eos_token_id)
        except (AttributeError, TypeError, ValueError):
            pass


def build_user_message(prompt: str, *, include_boxed_instruction: bool = True) -> str:
    prompt_text = str(prompt).strip()
    if not prompt_text:
        raise ValueError("Prompt must not be empty.")
    if include_boxed_instruction:
        return f"{prompt_text}\n{BOXED_INSTRUCTION}"
    return prompt_text


def apply_chat_template_safe(
    tokenizer: Any,
    messages: Sequence[dict[str, str]],
    *,
    add_generation_prompt: bool,
    enable_thinking: bool,
) -> str:
    try:
        return tokenizer.apply_chat_template(
            list(messages),
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=enable_thinking,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            list(messages),
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
        )


def encode_prompt(tokenizer: Any, prompt: str) -> list[int]:
    bos_token = getattr(tokenizer, "bos_token", None)
    add_special_tokens = bos_token is None or not str(prompt).startswith(str(bos_token))
    encoded = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
    return list(encoded)


def build_eval_prompts(
    tokenizer: Any,
    prompt_series: Sequence[str],
    *,
    enable_thinking: bool,
    include_boxed_instruction: bool = True,
) -> list[str]:
    prompts: list[str] = []
    for prompt_text in prompt_series:
        prompts.append(
            apply_chat_template_safe(
                tokenizer,
                [
                    {
                        "role": "user",
                        "content": build_user_message(
                            str(prompt_text),
                            include_boxed_instruction=include_boxed_instruction,
                        ),
                    }
                ],
                add_generation_prompt=True,
                enable_thinking=enable_thinking,
            )
        )
    return prompts


def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"
    boxed_matches = BOXED_PATTERN.findall(text)
    if boxed_matches:
        non_empty = [match.strip() for match in boxed_matches if match.strip()]
        if non_empty:
            return non_empty[-1]
        return boxed_matches[-1].strip()
    for pattern in FINAL_ANSWER_PATTERNS:
        matched = re.findall(pattern, text, re.IGNORECASE)
        if matched:
            return matched[-1].strip()
    numeric_matches = NUMBER_PATTERN.findall(text)
    if numeric_matches:
        return numeric_matches[-1]
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"


def analyze_raw_output(text: str | None) -> dict[str, Any]:
    if text is None:
        return {
            "extracted_answer": "NOT_FOUND",
            "fallback_type": "not_found",
            "format_bucket": "not_found",
            "has_boxed": False,
            "boxed_count": 0,
        }
    boxed_matches = BOXED_PATTERN.findall(text)
    numeric_matches = NUMBER_PATTERN.findall(text)
    if boxed_matches:
        non_empty = [match.strip() for match in boxed_matches if match.strip()]
        if non_empty:
            return {
                "extracted_answer": non_empty[-1],
                "fallback_type": "boxed_non_empty",
                "format_bucket": "boxed",
                "has_boxed": True,
                "boxed_count": len(boxed_matches),
            }
        return {
            "extracted_answer": boxed_matches[-1].strip(),
            "fallback_type": "boxed_empty",
            "format_bucket": "boxed_empty",
            "has_boxed": True,
            "boxed_count": len(boxed_matches),
        }
    for pattern in FINAL_ANSWER_PATTERNS:
        matched = re.findall(pattern, text, re.IGNORECASE)
        if matched:
            return {
                "extracted_answer": matched[-1].strip(),
                "fallback_type": "final_answer_phrase",
                "format_bucket": "final_answer",
                "has_boxed": False,
                "boxed_count": 0,
            }
    if numeric_matches:
        return {
            "extracted_answer": numeric_matches[-1],
            "fallback_type": "last_number",
            "format_bucket": "numeric_fallback",
            "has_boxed": False,
            "boxed_count": 0,
        }
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "extracted_answer": lines[-1] if lines else "NOT_FOUND",
        "fallback_type": "last_line" if lines else "not_found",
        "format_bucket": "line_fallback" if lines else "not_found",
        "has_boxed": False,
        "boxed_count": 0,
    }


def verify_answer(gold: str, predicted: str) -> bool:
    gold_text = str(gold).strip()
    predicted_text = str(predicted).strip()
    if re.fullmatch(r"[01]+", gold_text):
        return predicted_text.lower() == gold_text.lower()
    try:
        return math.isclose(
            float(gold_text),
            float(predicted_text),
            rel_tol=1e-2,
            abs_tol=1e-5,
        )
    except Exception:
        return predicted_text.lower() == gold_text.lower()


def detect_validation_category(prompt: str) -> str:
    if "secret bit manipulation rule transforms 8-bit binary numbers" in prompt:
        return "bit_manipulation"
    if "secret encryption rules are used on text" in prompt:
        return "cipher"
    if "secret set of transformation rules is applied to equations" in prompt:
        after_header = prompt.split("Below are a few examples:\n", 1)[1]
        examples_text, rest = after_header.split("\nNow, determine the result for: ", 1)
        question_text = rest.strip()
        if any(char.isdigit() for char in examples_text):
            question_match = re.fullmatch(r"(\d+)(\D)(\d+)", question_text)
            if question_match and re.search(
                r"\d" + re.escape(question_match.group(2)) + r"\d",
                examples_text,
            ):
                return "equation_numeric_deduce"
            return "equation_numeric_guess"
        if len(question_text) == 5:
            question_operator = question_text[2]
            for example_line in examples_text.strip().splitlines():
                input_text = example_line.split(" = ")[0].strip()
                if len(input_text) == 5 and input_text[2] == question_operator:
                    return "cryptarithm_deduce"
        return "cryptarithm_guess"
    if "gravitational constant has been secretly changed" in prompt:
        return "gravity"
    if "converted into a different numeral system" in prompt:
        return "numeral"
    if "secret unit conversion is applied to measurements" in prompt:
        return "unit_conversion"
    raise ValueError(f"Unknown validation category for prompt: {prompt[:120]!r}")


def _sampled_token_logprob(logprobs: Any, token_id: int) -> float:
    token_logprob = logprobs[int(token_id)]
    return float(token_logprob.item())


def generate_single_with_min_logprob(
    model: Any,
    tokenizer: Any,
    prompt_tokens: Sequence[int],
    *,
    max_tokens: int,
    sampler: Any,
    row_timeout_seconds: int = 0,
) -> tuple[str, float | None]:
    text_segments: list[str] = []
    min_logprob: float | None = None
    started_at = time.monotonic()
    for response in stream_generate(
        model,
        tokenizer,
        prompt=list(prompt_tokens),
        max_tokens=max_tokens,
        sampler=sampler,
    ):
        if response.text:
            text_segments.append(str(response.text))
        if response.finish_reason == "stop":
            continue
        sampled_logprob = _sampled_token_logprob(response.logprobs, int(response.token))
        min_logprob = sampled_logprob if min_logprob is None else min(min_logprob, sampled_logprob)
        if int(row_timeout_seconds) > 0 and (time.monotonic() - started_at) >= int(row_timeout_seconds):
            break
    return "".join(text_segments), min_logprob


def iter_batch_generate_with_min_logprobs(
    model: Any,
    tokenizer: Any,
    prompt_tokens: Sequence[Sequence[int]],
    *,
    max_tokens: int,
    sampler: Any,
    prefill_batch_size: int,
    completion_batch_size: int,
) -> Iterator[tuple[int, str, float | None]]:
    generator = BatchGenerator(
        model,
        stop_tokens=getattr(tokenizer, "eos_token_ids", None),
        sampler=sampler,
        prefill_batch_size=max(1, int(prefill_batch_size)),
        completion_batch_size=max(1, int(completion_batch_size)),
    )
    uids = generator.insert([list(tokens) for tokens in prompt_tokens], max_tokens=max_tokens)
    uid_to_index = {uid: index for index, uid in enumerate(uids)}
    generated_tokens: dict[int, list[int]] = {uid: [] for uid in uids}
    min_logprobs: dict[int, float | None] = {uid: None for uid in uids}
    try:
        while responses := generator.next():
            for response in responses:
                if response.finish_reason == "stop":
                    continue
                token_id = int(response.token)
                generated_tokens[response.uid].append(token_id)
                sampled_logprob = _sampled_token_logprob(response.logprobs, token_id)
                previous = min_logprobs[response.uid]
                min_logprobs[response.uid] = (
                    sampled_logprob if previous is None else min(previous, sampled_logprob)
                )
                if response.finish_reason is not None:
                    yield (
                        uid_to_index[response.uid],
                        tokenizer.decode(generated_tokens[response.uid]),
                        min_logprobs[response.uid],
                    )
                    continue
            for response in responses:
                if response.finish_reason == "stop":
                    yield (
                        uid_to_index[response.uid],
                        tokenizer.decode(generated_tokens[response.uid]),
                        min_logprobs[response.uid],
                    )
    finally:
        generator.close()


def batch_generate_with_min_logprobs(
    model: Any,
    tokenizer: Any,
    prompt_tokens: Sequence[Sequence[int]],
    *,
    max_tokens: int,
    sampler: Any,
    prefill_batch_size: int,
    completion_batch_size: int,
) -> tuple[list[str], list[float | None]]:
    texts: list[str | None] = [None] * len(prompt_tokens)
    minima: list[float | None] = [None] * len(prompt_tokens)
    for index, text, min_logprob in iter_batch_generate_with_min_logprobs(
        model,
        tokenizer,
        prompt_tokens,
        max_tokens=max_tokens,
        sampler=sampler,
        prefill_batch_size=prefill_batch_size,
        completion_batch_size=completion_batch_size,
    ):
        texts[index] = text
        minima[index] = min_logprob
    return [text or "" for text in texts], minima


def read_snapshot_token_file(token_path: Path) -> tuple[list[int], list[int]]:
    payload = load_json(token_path)
    tokens = [int(token) for token in payload["tokens"]]
    mask = [int(flag) for flag in payload["mask"]]
    if len(tokens) != len(mask):
        raise ValueError(f"Mismatched token/mask lengths in {token_path}")
    return tokens, mask


def derive_prompt_length(mask: Sequence[int], *, token_path: Path) -> int:
    prompt_length = 0
    saw_completion = False
    for flag in mask:
        if flag == 0 and not saw_completion:
            prompt_length += 1
            continue
        if flag == 1:
            saw_completion = True
            continue
        raise ValueError(f"Mask in {token_path} is not a prompt-then-completion boundary.")
    return prompt_length


def load_snapshot_step_plan(snapshot_root: Path) -> tuple[list[StepPlan], dict[str, Any]]:
    snapshot_config = load_json(snapshot_root / "config.json")
    steps_by_id: OrderedDict[int, list[SnapshotExample]] = OrderedDict()
    category_counts: Counter[str] = Counter()
    total_examples = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_total_length = 0

    with (snapshot_root / "logprobs" / "index.jsonl").open("r", encoding="utf-8") as handle:
        current_order_per_step: dict[int, int] = defaultdict(int)
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if int(record.get("epoch", -1)) != 0:
                continue
            problem_id = str(record["problem_id"])
            segment = str(record["segment"])
            if segment != "synthetic.jsonl":
                raise ValueError(f"Unexpected segment {segment!r} for {problem_id}")
            token_path = snapshot_root / "tokens" / problem_id / "synthetic.json"
            tokens, mask = read_snapshot_token_file(token_path)
            prompt_length = derive_prompt_length(mask, token_path=token_path)
            completion_length = sum(mask)
            if completion_length != int(record["num_loss_tokens"]):
                raise ValueError(
                    f"num_loss_tokens mismatch for {problem_id}: index={record['num_loss_tokens']} vs token_file={completion_length}"
                )
            total_length = len(tokens)
            max_total_length = max(max_total_length, total_length)
            total_examples += 1
            total_masked_tokens += prompt_length
            total_unmasked_tokens += completion_length
            category = str(record["category"])
            category_counts[category] += 1
            step = int(record["step"])
            example = SnapshotExample(
                problem_id=problem_id,
                category=category,
                step=step,
                order_in_step=current_order_per_step[step],
                token_path=str(token_path.resolve()),
                prompt_length=prompt_length,
                completion_length=completion_length,
                total_length=total_length,
                num_loss_tokens=completion_length,
            )
            steps_by_id.setdefault(step, []).append(example)
            current_order_per_step[step] += 1

    step_plan = [
        StepPlan(step=step, examples=tuple(examples))
        for step, examples in steps_by_id.items()
    ]
    step_batch_sizes = [len(step.examples) for step in step_plan]
    contract = {
        "snapshot_root": str(snapshot_root.resolve()),
        "config_path": str((snapshot_root / "config.json").resolve()),
        "index_path": str((snapshot_root / "logprobs" / "index.jsonl").resolve()),
        "num_examples": total_examples,
        "num_steps": len(step_plan),
        "step_batch_sizes": step_batch_sizes,
        "min_step_batch": min(step_batch_sizes) if step_batch_sizes else 0,
        "max_step_batch": max(step_batch_sizes) if step_batch_sizes else 0,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_total_length": max_total_length,
        "category_counts": dict(sorted(category_counts.items())),
        "source_config": snapshot_config,
        "matches_source_config": {
            "num_examples": total_examples == int(snapshot_config["stats"]["num_examples"]),
            "total_masked_tokens": total_masked_tokens == int(snapshot_config["stats"]["total_masked_tokens"]),
            "total_unmasked_tokens": total_unmasked_tokens == int(snapshot_config["stats"]["total_unmasked_tokens"]),
            "total_steps": len(step_plan) == int(snapshot_config["stats"]["total_steps"]),
            "batch_size": int(snapshot_config["batch_size"]) == 32,
            "micro_batch_size": int(snapshot_config["micro_batch_size"]) == 16,
            "max_length": int(snapshot_config["max_length"]) == 8192,
            "lora_rank": int(snapshot_config["lora_rank"]) == 32,
        },
    }
    return step_plan, contract


def render_step_plan(step_plan: Sequence[StepPlan]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for step in step_plan:
        rows.append(
            {
                "step": step.step,
                "size": len(step.examples),
                "examples": [
                    {
                        "problem_id": example.problem_id,
                        "category": example.category,
                        "token_path": example.token_path,
                        "prompt_length": int(example.prompt_length),
                        "completion_length": int(example.completion_length),
                        "total_length": int(example.total_length),
                        "num_loss_tokens": int(example.num_loss_tokens),
                    }
                    for example in step.examples
                ],
            }
        )
    return rows


def default_lora_keys() -> list[str]:
    return [
        "mixer.q_proj",
        "mixer.k_proj",
        "mixer.v_proj",
        "mixer.o_proj",
        "mixer.in_proj",
        "mixer.out_proj",
        "mixer.switch_mlp.fc1",
        "mixer.switch_mlp.fc2",
        "mixer.shared_experts.up_proj",
        "mixer.shared_experts.down_proj",
        "lm_head",
    ]


def _count_parameters(tree: Any) -> int:
    total = 0
    for _, value in tree_flatten(tree):
        size = 1
        for dim in value.shape:
            size *= int(dim)
        total += size
    return total


def summarize_lora_matches(model: Any) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    base_shapes: dict[str, tuple[int, ...]] = {}
    for key, value in tree_flatten(model.trainable_parameters()):
        if not key.endswith(".lora_a"):
            continue
        base_key = key[: -len(".lora_a")]
        base_shapes[base_key] = tuple(int(dim) for dim in value.shape)

    def _label_and_units(base_key: str, shape: tuple[int, ...]) -> tuple[str, int]:
        if base_key.endswith("mixer.switch_mlp.fc1"):
            return "up_proj", int(shape[0]) if len(shape) >= 3 else 1
        if base_key.endswith("mixer.switch_mlp.fc2"):
            return "down_proj", int(shape[0]) if len(shape) >= 3 else 1
        if base_key.endswith("mixer.shared_experts.up_proj"):
            return "up_proj", 1
        if base_key.endswith("mixer.shared_experts.down_proj"):
            return "down_proj", 1
        for label in ("q_proj", "k_proj", "v_proj", "o_proj", "in_proj", "out_proj", "lm_head"):
            if base_key.endswith(label):
                return label, 1
        return base_key.rsplit(".", 1)[-1], 1

    for base_key, shape in sorted(base_shapes.items()):
        label, units = _label_and_units(base_key, shape)
        counts[label] += units

    trainable_params = _count_parameters(model.trainable_parameters())
    all_params = _count_parameters(model.parameters())
    trainable_percent = 100.0 * trainable_params / all_params if all_params else 0.0
    return {
        "matched_target_modules": {
            label: int(counts[label])
            for label in ("q_proj", "k_proj", "v_proj", "o_proj", "in_proj", "out_proj", "up_proj", "down_proj", "lm_head")
            if counts.get(label)
        },
        "trainable_params": int(trainable_params),
        "all_params": int(all_params),
        "trainable_percent": float(trainable_percent),
        "num_lora_tensors": int(len(base_shapes) * 2),
        "num_lora_modules": int(len(base_shapes)),
    }


def print_lora_match_summary(summary: dict[str, Any]) -> None:
    print("Matched target modules:")
    matched = summary["matched_target_modules"]
    for label in ("q_proj", "k_proj", "v_proj", "o_proj", "in_proj", "out_proj", "up_proj", "down_proj", "lm_head"):
        if label in matched:
            print(f"  {label:<12} {matched[label]}")
    print(
        "trainable params: "
        f"{summary['trainable_params']:,} || all params: {summary['all_params']:,} || "
        f"trainable%: {summary['trainable_percent']:.4f}"
    )


def assert_lora_match_summary(summary: dict[str, Any]) -> None:
    matched = summary["matched_target_modules"]
    required = ("q_proj", "k_proj", "v_proj", "o_proj", "in_proj", "out_proj", "up_proj", "down_proj", "lm_head")
    missing = [label for label in required if int(matched.get(label, 0)) <= 0]
    if missing:
        raise RuntimeError(
            "LoRA target resolution failed; missing matched target modules for "
            + ", ".join(missing)
            + "."
        )
    if int(summary["num_lora_modules"]) <= 1 or int(summary["trainable_params"]) < 100_000_000:
        raise RuntimeError(
            "LoRA target resolution looks implausibly small "
            f"(modules={summary['num_lora_modules']}, trainable_params={summary['trainable_params']:,})."
        )


def build_training_manifest(args: argparse.Namespace, step_plan: Sequence[StepPlan], shadow_model_dir: Path) -> dict[str, Any]:
    optimizer_steps = len(step_plan)
    microsteps = sum(
        math.ceil(len(step.examples) / max(1, int(args.micro_batch_size))) for step in step_plan
    )
    training_data_path = resolve_training_data_path(args)
    training_source_type = "single_file_bundle" if getattr(args, "training_bundle_path", None) is not None else "snapshot"
    return {
        "created_at": utc_now(),
        "repo_root": str(REPO_ROOT),
        "work_root": str(WORK_ROOT),
        "run_name": str(args.run_name),
        "run_root": str((Path(args.output_root).resolve() / args.run_name).resolve()),
        "shadow_model_dir": str(shadow_model_dir.resolve()),
        "snapshot_root": str(SNAPSHOT_ROOT.resolve()),
        "training_data": {
            "source_type": training_source_type,
            "path": str(training_data_path),
            "snapshot_root": str(SNAPSHOT_ROOT.resolve()),
        },
        "readme_contract": README_EVAL_CONTRACT,
        "training": {
            "backend": "mlx",
            "base_model_name_or_path": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
            "model_root": str(Path(args.model_root).resolve()),
            "shadow_model_dir": str(shadow_model_dir.resolve()),
            "optimizer": "adam",
            "learning_rate": float(args.learning_rate),
            "optimizer_steps": optimizer_steps,
            "microsteps": microsteps,
            "effective_batch_size": int(args.batch_size),
            "micro_batch_size": int(args.micro_batch_size),
            "max_seq_length": int(args.max_seq_length),
            "epochs": 1,
            "lora_rank": int(args.lora_rank),
            "lora_alpha": float(args.lora_alpha),
            "lora_dropout": float(args.lora_dropout),
            "train_attn": True,
            "train_mlp": True,
            "train_unembed": True,
            "lora_keys": list(default_lora_keys()),
            "adam": {
                "beta1": float(args.beta1),
                "beta2": float(args.beta2),
                "eps": float(args.eps),
                "weight_decay": float(args.weight_decay),
                "bias_correction": bool(args.bias_correction),
            },
            "lr_schedule": {
                "name": "StepLinearDecayLRSchedule",
                "formula": "learning_rate * (1 - step / total_steps)",
            },
            "assumptions": {
                "lora_alpha_is_rank": True,
                "tinker_dropout_not_exposed_assumed_zero": float(args.lora_dropout) == 0.0,
                "fixed_train_padding": bool(args.fixed_train_padding),
            },
        },
        "evaluation": {
            "benchmark_csv": str(TRAIN_CSV_PATH.resolve()),
            "max_tokens": int(args.max_tokens),
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "max_num_seqs": int(args.max_num_seqs),
            "max_model_len": int(args.max_model_len),
            "enable_thinking": bool(args.eval_enable_thinking),
            "eval_shards": int(args.eval_shards),
            "eval_shard_index": int(args.eval_shard_index),
        },
    }


def build_prepare_artifacts(args: argparse.Namespace) -> TrainingArtifacts:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    shadow_model_dir = build_shadow_model_dir(Path(args.model_root), run_root / "shadow_model", force=bool(args.force_shadow_model))
    artifacts = TrainingArtifacts(
        run_root=run_root,
        shadow_model_dir=shadow_model_dir,
        adapter_dir=run_root / "adapter",
        bundle_token_dir=run_root / "training_bundle_tokens",
        step_plan_path=run_root / "step_plan.json",
        snapshot_contract_path=run_root / "snapshot_contract.json",
        config_path=run_root / "run_manifest.json",
        train_report_jsonl=run_root / "adapter" / "train_report.jsonl",
        latest_train_report_path=run_root / "adapter" / "latest_train_report.json",
        training_result_path=run_root / "training_result.json",
    )
    return artifacts


def prepare_run(args: argparse.Namespace) -> TrainingArtifacts:
    artifacts = build_prepare_artifacts(args)
    if getattr(args, "training_bundle_path", None) is not None:
        bundle_path = Path(args.training_bundle_path).resolve()
        if artifacts.bundle_token_dir.exists():
            shutil.rmtree(artifacts.bundle_token_dir)
        step_plan, snapshot_contract = load_training_bundle_step_plan(
            bundle_path,
            materialized_root=artifacts.bundle_token_dir,
        )
    else:
        step_plan, snapshot_contract = load_snapshot_step_plan(SNAPSHOT_ROOT)
    expected_batch_size = int(snapshot_contract["source_config"]["batch_size"])
    expected_micro_batch_size = int(snapshot_contract["source_config"]["micro_batch_size"])
    if int(args.batch_size) != expected_batch_size:
        raise ValueError(
            f"--batch-size must stay at the v20 value {expected_batch_size}; got {args.batch_size}"
        )
    if int(args.micro_batch_size) > expected_batch_size:
        raise ValueError(
            f"--micro-batch-size must be <= optimizer batch size {expected_batch_size}; got {args.micro_batch_size}"
        )
    if int(args.micro_batch_size) != expected_micro_batch_size:
        print(
            f"[info] overriding v20 micro_batch_size={expected_micro_batch_size} with MLX micro_batch_size={args.micro_batch_size}"
        )
    write_json(artifacts.snapshot_contract_path, snapshot_contract)
    write_json(artifacts.step_plan_path, render_step_plan(step_plan))
    run_manifest = build_training_manifest(args, step_plan, artifacts.shadow_model_dir)
    write_json(artifacts.config_path, run_manifest)
    write_command_script(artifacts.run_root / "train_cmd.sh", build_train_command_tokens(args))
    return artifacts


def v20_step_lr(step: int, total_steps: int, learning_rate: float) -> float:
    if total_steps <= 0:
        raise ValueError("total_steps must be positive")
    return float(learning_rate) * (1.0 - (float(step) / float(total_steps)))


def build_v20_lr_schedule(total_steps: int, learning_rate: float):
    total = mx.array(float(total_steps), dtype=mx.float32)
    base = mx.array(float(learning_rate), dtype=mx.float32)

    def schedule(step: mx.array) -> mx.array:
        return base * (1.0 - step.astype(mx.float32) / total)

    return schedule


def default_loss(model: Any, batch: mx.array, lengths: mx.array) -> tuple[mx.array, mx.array]:
    inputs = batch[:, :-1]
    targets = batch[:, 1:]
    logits = model(inputs)
    steps = mx.arange(1, targets.shape[1] + 1)
    mask = mx.logical_and(steps >= lengths[:, 0:1], steps < lengths[:, 1:])
    ce = nn.losses.cross_entropy(logits, targets) * mask
    ntoks = mask.sum()
    ce = ce.astype(mx.float32).sum() / ntoks
    return ce, ntoks


def chunk_examples(examples: Sequence[SnapshotExample], chunk_size: int) -> list[list[SnapshotExample]]:
    return [list(examples[i : i + chunk_size]) for i in range(0, len(examples), chunk_size)]


def build_microbatch_arrays(
    examples: Sequence[SnapshotExample],
    *,
    micro_batch_size: int,
    max_seq_length: int,
    fixed_train_padding: bool,
) -> tuple[mx.array, mx.array]:
    loaded: list[tuple[list[int], int, int]] = []
    max_length = 0
    for example in examples:
        tokens, _ = read_snapshot_token_file(Path(example.token_path))
        truncated_length = min(len(tokens), max_seq_length)
        max_length = max(max_length, truncated_length)
        loaded.append((tokens, min(example.prompt_length, truncated_length), truncated_length))

    if fixed_train_padding:
        padded_length = int(max_seq_length)
    else:
        padded_length = min(max_seq_length, 1 + PAD_TO * ((max_length + PAD_TO - 1) // PAD_TO))
    if padded_length <= 0:
        raise ValueError("Encountered empty microbatch")

    batch_arr = np.zeros((micro_batch_size, padded_length), dtype=np.int32)
    lengths_arr = np.zeros((micro_batch_size, 2), dtype=np.int32)
    for row_index, (tokens, prompt_length, truncated_length) in enumerate(loaded):
        batch_arr[row_index, :truncated_length] = np.asarray(tokens[:truncated_length], dtype=np.int32)
        lengths_arr[row_index, 0] = int(prompt_length)
        lengths_arr[row_index, 1] = int(truncated_length)
    return mx.array(batch_arr), mx.array(lengths_arr)


def create_adapter_config_payload(
    *,
    shadow_model_dir: Path,
    adapter_dir: Path,
    args: argparse.Namespace,
    total_steps: int,
) -> dict[str, Any]:
    training_data_path = resolve_training_data_path(args)
    return {
        "model": str(shadow_model_dir),
        "train": True,
        "fine_tune_type": "lora",
        "optimizer": "adam",
        "optimizer_config": {"adam": {}, "adamw": {}, "muon": {}, "sgd": {}, "adafactor": {}},
        "data": str(training_data_path),
        "seed": int(args.seed),
        "num_layers": -1,
        "batch_size": int(args.micro_batch_size),
        "iters": int(total_steps),
        "val_batches": -1,
        "learning_rate": float(args.learning_rate),
        "steps_per_report": int(args.steps_per_report),
        "steps_per_eval": int(total_steps),
        "resume_adapter_file": str(Path(args.resume_adapter_file).resolve()) if args.resume_adapter_file else None,
        "adapter_path": str(adapter_dir),
        "save_every": int(args.save_every_steps) if int(args.save_every_steps) > 0 else int(total_steps),
        "max_saved_checkpoints": int(args.max_saved_checkpoints),
        "max_seq_length": int(args.max_seq_length),
        "grad_checkpoint": True,
        "grad_accumulation_steps": 1,
        "lr_schedule": {
            "name": "v20_step_linear_decay",
            "arguments": [float(args.learning_rate), int(total_steps)],
        },
        "lora_parameters": {
            "rank": int(args.lora_rank),
            "dropout": float(args.lora_dropout),
            "scale": float(args.lora_alpha),
            "keys": list(default_lora_keys()),
        },
        "mask_prompt": True,
        "enable_thinking": True,
        "v20_snapshot_root": str(SNAPSHOT_ROOT),
        "training_data_source": "single_file_bundle" if getattr(args, "training_bundle_path", None) is not None else "snapshot",
        "training_data_path": str(training_data_path),
        "v20_effective_batch_size": int(args.batch_size),
        "v20_micro_batch_size": int(args.micro_batch_size),
        "v20_optimizer_steps": int(total_steps),
            "v20_schedule_formula": "learning_rate * (1 - step / total_steps)",
        "v20_fixed_train_padding": bool(args.fixed_train_padding),
    }


def save_adapter_weights(adapter_dir: Path, file_name: str, model: Any) -> Path:
    ensure_dir(adapter_dir)
    adapter_path = adapter_dir / file_name
    adapter_weights = dict(tree_flatten(model.trainable_parameters()))
    mx.save_safetensors(str(adapter_path), adapter_weights)
    return adapter_path


def prune_saved_checkpoints(adapter_dir: Path, *, max_saved_checkpoints: int) -> list[str]:
    if max_saved_checkpoints < 1:
        raise ValueError("max_saved_checkpoints must be >= 1 when periodic checkpoint saving is enabled")
    checkpoint_paths = sorted(adapter_dir.glob("*_adapters.safetensors"))
    removed: list[str] = []
    while len(checkpoint_paths) > max_saved_checkpoints:
        stale = checkpoint_paths.pop(0)
        stale.unlink()
        removed.append(stale.name)
    return removed


def cleanup_completed_run_artifacts(run_root: Path) -> dict[str, Any]:
    adapter_dir = run_root / "adapter"
    removed_checkpoint_files: list[str] = []
    for checkpoint_path in sorted(adapter_dir.glob("*_adapters.safetensors")):
        checkpoint_path.unlink()
        removed_checkpoint_files.append(checkpoint_path.name)

    removed_dirs: list[str] = []
    bundle_token_dir = run_root / "training_bundle_tokens"
    if bundle_token_dir.exists():
        shutil.rmtree(bundle_token_dir)
        removed_dirs.append(str(bundle_token_dir.resolve()))

    return {
        "removed_checkpoint_files": removed_checkpoint_files,
        "removed_dirs": removed_dirs,
    }


def summarize_directory(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for child in sorted(path.iterdir()):
        rows.append(
            {
                "name": child.name,
                "is_dir": child.is_dir(),
                "size_bytes": child.stat().st_size if child.is_file() else 0,
            }
        )
    return rows


def build_local_mlx_bundle(run_root: Path, adapter_dir: Path) -> dict[str, Any]:
    required = [adapter_dir / "adapter_config.json", adapter_dir / "adapters.safetensors"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing adapter artifacts: " + ", ".join(missing))
    bundle_root = run_root / "mlx_adapter_bundle"
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    ensure_dir(bundle_root)
    shutil.copy2(adapter_dir / "adapter_config.json", bundle_root / "adapter_config.json")
    shutil.copy2(adapter_dir / "adapters.safetensors", bundle_root / "adapters.safetensors")
    manifest = {
        "created_at": utc_now(),
        "bundle_root": str(bundle_root),
        "note": "Local MLX adapter bundle for v20 reproduction. Not claimed submission-compatible.",
        "files": summarize_directory(bundle_root),
    }
    write_json(bundle_root / "bundle_manifest.json", manifest)
    return manifest


def load_step_plan(path: Path) -> list[StepPlan]:
    rows = load_json(path)
    if rows and "examples" in rows[0]:
        step_plan: list[StepPlan] = []
        for row in rows:
            step_examples = []
            for order_in_step, example_row in enumerate(row["examples"]):
                step_examples.append(
                    SnapshotExample(
                        problem_id=str(example_row["problem_id"]),
                        category=str(example_row["category"]),
                        step=int(row["step"]),
                        order_in_step=order_in_step,
                        token_path=str(example_row["token_path"]),
                        prompt_length=int(example_row["prompt_length"]),
                        completion_length=int(example_row["completion_length"]),
                        total_length=int(example_row["total_length"]),
                        num_loss_tokens=int(example_row["num_loss_tokens"]),
                    )
                )
            step_plan.append(StepPlan(step=int(row["step"]), examples=tuple(step_examples)))
        return step_plan
    step_plan: list[StepPlan] = []
    for row in rows:
        step_plan.append(
            StepPlan(
                step=int(row["step"]),
                examples=tuple(
                    SnapshotExample(
                        problem_id=str(example_id),
                        category=str(category),
                        step=int(row["step"]),
                        order_in_step=order_in_step,
                        token_path=str(token_path),
                        prompt_length=0,
                        completion_length=0,
                        total_length=0,
                        num_loss_tokens=0,
                    )
                    for order_in_step, (example_id, category, token_path) in enumerate(
                        zip(row["problem_ids"], row["categories"], row["token_paths"])
                    )
                ),
            )
        )
    # Recover full metadata from the authoritative snapshot contract to avoid bloating step_plan.json.
    full_step_plan, _ = load_snapshot_step_plan(SNAPSHOT_ROOT)
    full_by_step = {step.step: step for step in full_step_plan}
    return [full_by_step[step.step] for step in step_plan]


def build_bundle_token_path(materialized_root: Path, *, step: int, order_in_step: int, problem_id: str) -> Path:
    safe_problem_id = re.sub(r"[^A-Za-z0-9._-]+", "_", str(problem_id)).strip("._")
    if not safe_problem_id:
        safe_problem_id = "example"
    return materialized_root / f"step_{step:04d}" / f"{order_in_step:04d}_{safe_problem_id}.json"


def load_training_bundle_step_plan(bundle_path: Path, *, materialized_root: Path) -> tuple[list[StepPlan], dict[str, Any]]:
    if not bundle_path.exists():
        raise FileNotFoundError(f"Missing training bundle at {bundle_path}")
    steps_by_id: OrderedDict[int, list[SnapshotExample]] = OrderedDict()
    current_order_per_step: dict[int, int] = defaultdict(int)
    category_counts: Counter[str] = Counter()
    total_examples = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_total_length = 0
    manifest: dict[str, Any] | None = None

    with bundle_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            record = json.loads(text)
            record_type = str(record.get("record_type", ""))
            if record_type == "manifest":
                manifest = dict(record)
                continue
            if record_type != "example":
                raise ValueError(f"Unexpected record_type={record_type!r} at {bundle_path}:{line_number}")
            problem_id = str(record.get("example_id") or record.get("source_problem_id") or f"line{line_number}")
            category = str(record["category"])
            step = int(record["step"])
            order_in_step = current_order_per_step[step]
            current_order_per_step[step] += 1
            tokens = [int(token) for token in record["tokens"]]
            mask = [int(flag) for flag in record["mask"]]
            if len(tokens) != len(mask):
                raise ValueError(
                    f"Mismatched token/mask lengths for {problem_id} at {bundle_path}:{line_number}"
                )
            completion_length = int(record["num_loss_tokens"])
            if sum(mask) != completion_length:
                raise ValueError(
                    f"num_loss_tokens mismatch for {problem_id} at {bundle_path}:{line_number}: "
                    f"{sum(mask)} != {completion_length}"
                )
            if str(record.get("source", "")) == "base_snapshot" and str(record.get("segment", "")) == "synthetic.jsonl":
                token_path = SNAPSHOT_ROOT / "tokens" / problem_id / "synthetic.json"
                if not token_path.exists():
                    token_path = build_bundle_token_path(
                        materialized_root,
                        step=step,
                        order_in_step=order_in_step,
                        problem_id=problem_id,
                    )
                    write_json(token_path, {"tokens": tokens, "mask": mask})
            else:
                token_path = build_bundle_token_path(
                    materialized_root,
                    step=step,
                    order_in_step=order_in_step,
                    problem_id=problem_id,
                )
                write_json(token_path, {"tokens": tokens, "mask": mask})
            prompt_length = derive_prompt_length(mask, token_path=Path(token_path))
            total_examples += 1
            total_masked_tokens += prompt_length
            total_unmasked_tokens += completion_length
            max_total_length = max(max_total_length, len(tokens))
            category_counts[category] += 1
            steps_by_id.setdefault(step, []).append(
                SnapshotExample(
                    problem_id=problem_id,
                    category=category,
                    step=step,
                    order_in_step=order_in_step,
                    token_path=str(Path(token_path).resolve()),
                    prompt_length=prompt_length,
                    completion_length=completion_length,
                    total_length=len(tokens),
                    num_loss_tokens=completion_length,
                )
            )

    if manifest is None:
        raise ValueError(f"Missing manifest record in training bundle {bundle_path}")
    step_plan = [
        StepPlan(step=step, examples=tuple(examples))
        for step, examples in steps_by_id.items()
    ]
    step_batch_sizes = [len(step.examples) for step in step_plan]
    source_config = dict(manifest.get("base_snapshot_config") or {})
    source_stats = dict(source_config.get("stats") or {})
    contract = {
        "training_source": "single_file_bundle",
        "bundle_path": str(bundle_path.resolve()),
        "bundle_manifest": manifest,
        "materialized_token_root": str(materialized_root.resolve()),
        "num_examples": total_examples,
        "num_steps": len(step_plan),
        "step_batch_sizes": step_batch_sizes,
        "min_step_batch": min(step_batch_sizes) if step_batch_sizes else 0,
        "max_step_batch": max(step_batch_sizes) if step_batch_sizes else 0,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_total_length": max_total_length,
        "category_counts": dict(sorted(category_counts.items())),
        "source_config": source_config,
        "matches_source_config": {
            "num_examples": total_examples == int(source_stats.get("num_examples", total_examples)),
            "total_masked_tokens": total_masked_tokens
            == int(source_stats.get("total_masked_tokens", total_masked_tokens)),
            "total_unmasked_tokens": total_unmasked_tokens
            == int(source_stats.get("total_unmasked_tokens", total_unmasked_tokens)),
            "total_steps": len(step_plan) == int(source_stats.get("total_steps", len(step_plan))),
            "batch_size": int(source_config.get("batch_size", 32)) == 32,
            "micro_batch_size": int(source_config.get("micro_batch_size", 16)) == 16,
            "max_length": int(source_config.get("max_length", 8192)) == 8192,
            "lora_rank": int(source_config.get("lora_rank", 32)) == 32,
        },
    }
    return step_plan, contract


def collect_runtime_preflight() -> dict[str, Any]:
    return {
        "captured_at": utc_now(),
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
    }


def render_train_markdown_summary(training_result: dict[str, Any]) -> str:
    latest = training_result.get("latest_train_report") or {}
    lines = ["# training_result", ""]
    lines.append(f"- run_root: `{training_result['run_root']}`")
    lines.append(f"- shadow_model_dir: `{training_result['shadow_model_dir']}`")
    lines.append(f"- adapter_dir: `{training_result['adapter_dir']}`")
    if training_result.get("run_manifest_path"):
        lines.append(f"- run_manifest_path: `{training_result['run_manifest_path']}`")
    if training_result.get("train_cmd_path"):
        lines.append(f"- train_cmd_path: `{training_result['train_cmd_path']}`")
    lines.append(f"- optimizer_steps_completed: `{latest.get('step', '')}`")
    lines.append(f"- latest_train_loss: `{latest.get('train_loss', '')}`")
    lines.append(f"- latest_lr: `{latest.get('lr', '')}`")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def load_training_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with TRAIN_CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "id": str(row["id"]),
                    "prompt": str(row["prompt"]),
                    "answer": str(row["answer"]),
                }
            )
    return rows


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return [dict(row) for row in reader]


def parse_bool_text(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_int_text(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def parse_float_text(value: Any, default: float = 0.0) -> float:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def is_binary_answer_text(answer: str) -> bool:
    text = str(answer).strip()
    return len(text) == 8 and set(text) <= {"0", "1"}


@lru_cache(maxsize=1)
def get_bundle_chat_tokenizer() -> Any:
    from transformers import AutoTokenizer

    tokenizer_root = build_shadow_model_dir(DEFAULT_MODEL_ROOT, BUNDLE_TOKENIZER_SHADOW_DIR)
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_root), trust_remote_code=True)
    normalize_tokenizer_for_hf_parity(tokenizer)
    return tokenizer


def tokenize_bundle_overlay_example(prompt: str, completion_text: str) -> tuple[list[int], list[int]]:
    tokenizer = get_bundle_chat_tokenizer()
    prompt_text = apply_chat_template_safe(
        tokenizer,
        [{"role": "user", "content": str(prompt).strip() + V11_PROMPT_SUFFIX}],
        add_generation_prompt=True,
        enable_thinking=True,
    )
    prompt_ids = encode_prompt(tokenizer, prompt_text)
    completion_ids = tokenizer.encode(str(completion_text), add_special_tokens=False)
    tokens = list(prompt_ids) + list(completion_ids)
    mask = [0] * len(prompt_ids) + [1] * len(completion_ids)
    token_limit = int(README_EVAL_CONTRACT["max_model_len"])
    if len(tokens) > token_limit:
        tokens = tokens[:token_limit]
        mask = mask[:token_limit]
    return tokens, mask


def load_base_snapshot_bundle_examples() -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]], int]:
    snapshot_config = load_json(SNAPSHOT_CONFIG_PATH)
    batch_size = int(snapshot_config["batch_size"])
    base_rows: list[dict[str, Any]] = []
    base_examples: dict[tuple[str, str], dict[str, Any]] = {}
    for record in load_jsonl(SNAPSHOT_INDEX_PATH):
        if int(record.get("epoch", -1)) != 0:
            continue
        problem_id = str(record["problem_id"])
        segment = str(record["segment"])
        if segment != "synthetic.jsonl":
            continue
        token_path = SNAPSHOT_TOKENS_ROOT / problem_id / "synthetic.json"
        tokens, mask = read_snapshot_token_file(token_path)
        if sum(mask) != int(record["num_loss_tokens"]):
            raise ValueError(
                f"num_loss_tokens mismatch for base snapshot {problem_id}: {sum(mask)} != {record['num_loss_tokens']}"
            )
        base_rows.append(record)
        base_examples[(problem_id, segment)] = {
            "row": record,
            "tokens": tokens,
            "mask": mask,
        }
    return base_rows, base_examples, batch_size


def build_completion_from_think_lines(lines: Sequence[str], answer: str) -> str:
    return "\n".join(["<think>", *lines, "</think>", f"\\boxed{{{answer}}}<|im_end|>"])


def v11_binary_family_key(row: dict[str, Any]) -> str:
    return (
        str(row.get("bit_structured_formula_abstract_family", "")).strip()
        or str(row.get("bit_not_structured_formula_abstract_family", "")).strip()
        or str(row.get("bit_structured_formula_name", "")).strip()
        or str(row.get("bit_not_structured_formula_name", "")).strip()
        or str(row.get("teacher_solver_candidate", "")).strip()
        or str(row.get("template_subtype", "")).strip()
        or "unknown"
    )


def build_v11_binary_completion(row: dict[str, Any], assistant_style: str) -> str:
    family = v11_binary_family_key(row)
    exact_rule = str(row.get("bit_structured_formula_name", "")).strip() or str(
        row.get("bit_not_structured_formula_name", "")
    ).strip()
    solver = str(row.get("teacher_solver_candidate", "")).strip()
    if assistant_style == "exact_rule_commit":
        lines = [
            f"Verified binary family: {family}.",
            f"Concrete rule: {exact_rule}." if exact_rule else f"Recovered solver pattern: {solver or family}.",
            "Apply the same binary transform to the query byte.",
            "Preserve exact 8-bit closure with leading zeros.",
        ]
    elif assistant_style == "exact_closure_commit":
        lines = [
            f"Verified binary family: {family}.",
            "Use only the output bits justified by the examples.",
            "Keep exact 8-bit closure from start to finish.",
            "Return only the final byte in the box.",
        ]
    elif assistant_style == "anti_default1_commit":
        lines = [
            f"Hard binary case in family: {family}.",
            "Do not invent fallback 1 bits or guessed activations.",
            "If a bit is not justified by the examples, leave it off.",
            "Return only the exact final 8-bit byte in the box.",
        ]
    elif assistant_style == "answer_only_binary_commit":
        lines = [
            f"Use the consistent binary transform from the examples ({family}).",
            "Keep leading zeros and exact 8-bit length.",
            "Do not add explanation after the answer.",
        ]
    elif assistant_style == "answer_only_binary_closure":
        lines = [
            "Use the prompt-consistent binary closure only.",
            "Preserve exact 8-bit output with leading zeros.",
            "Return only the final byte in the box.",
        ]
    else:
        raise ValueError(f"Unsupported v11 binary assistant style: {assistant_style}")
    return build_completion_from_think_lines(lines, answer=str(row["answer"]).strip())


def build_v11_text_completion(row: dict[str, Any], assistant_style: str) -> str:
    if assistant_style != "cipher_boxed_tail":
        raise ValueError(f"Unsupported v11 text assistant style: {assistant_style}")
    lines = [
        "Use the substitution implied by the examples.",
        "Return only the decrypted plaintext phrase in the box.",
        "Do not add explanation after the answer.",
    ]
    return build_completion_from_think_lines(lines, answer=str(row["answer"]).strip())


def build_v11_numeric_completion(row: dict[str, Any], assistant_style: str) -> str:
    formula = str(row.get("symbol_numeric_formula_name", "")).strip()
    operator = str(row.get("symbol_query_operator", "")).strip()
    if assistant_style not in {"numeric_guess_commit", "numeric_guess_short"}:
        raise ValueError(f"Unsupported v11 numeric assistant style: {assistant_style}")
    lines = [
        (
            f"Use the prompt-consistent numeric rule for operator {operator}."
            if operator
            else "Use the prompt-consistent numeric rule from the examples."
        ),
        f"Known candidate family: {formula}." if formula else "Keep the final answer consistent with the examples.",
        "Return only the final answer in the box.",
    ]
    if assistant_style == "numeric_guess_commit":
        lines.insert(1, "Do not substitute another operator family.")
    return build_completion_from_think_lines(lines, answer=str(row["answer"]).strip())


def expand_assistant_styles(styles: Sequence[str], repeat_count: int) -> list[str]:
    if repeat_count <= 0:
        return []
    if not styles:
        raise ValueError("expand_assistant_styles requires at least one style")
    return [str(styles[index % len(styles)]) for index in range(repeat_count)]


def build_v11_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    row_id = str(row["id"]).strip()
    family = v11_binary_family_key(row)
    repeat_count = 2 if verified else 1
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 4
    if family in V11_PRIORITY_BINARY_FAMILIES:
        repeat_count += 1
    if str(row.get("template_subtype", "")).strip() == "bit_prompt_local_exact_formula":
        repeat_count += 1
    if parse_int_text(row.get("bit_structured_formula_abstract_support", 0), 0) >= 40:
        repeat_count += 1
    cap = 7 if verified else 5
    return min(cap, repeat_count)


def build_v12_manual_repeat_count(row: dict[str, Any]) -> int:
    row_id = str(row["id"]).strip()
    family = v11_binary_family_key(row)
    repeat_count = 4
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 4
    if family in V11_PRIORITY_BINARY_FAMILIES:
        repeat_count += 1
    if str(row.get("template_subtype", "")).strip() == "bit_other":
        repeat_count += 1
    return min(8, repeat_count)


def build_v13_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    if template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 2
    if template_subtype == "bit_other":
        repeat_count += 1
    if family in {"unknown", "bit_other"}:
        repeat_count += 1
    cap = 9 if verified else 6
    return min(cap, repeat_count)


def build_v13_manual_repeat_count(row: dict[str, Any]) -> int:
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    repeat_count = 5
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 3
    if template_subtype == "bit_other":
        repeat_count += 1
    return min(9, repeat_count)


def build_v14_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    template_subtype = str(row.get("template_subtype", "")).strip()
    if template_subtype == "bit_structured_byte_formula":
        repeat_count += 2
    if template_subtype == "bit_permutation_inversion":
        repeat_count += 1
    if parse_int_text(row.get("bit_structured_formula_abstract_support", 0), 0) >= 80:
        repeat_count += 1
    cap = 9 if verified else 7
    return min(cap, repeat_count)


def build_v14_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 4
    if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 2
    return min(7, repeat_count)


def build_v15_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    if template_subtype == "bit_other":
        repeat_count += 2
    if family == "unknown":
        repeat_count += 2
    if family in V11_PRIORITY_BINARY_FAMILIES:
        repeat_count += 1
    if template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 1
    if template_subtype == "bit_structured_byte_formula":
        repeat_count += 1
    if parse_int_text(row.get("bit_structured_formula_abstract_support", 0), 0) >= 80:
        repeat_count += 1
    cap = 10 if verified else 8
    return min(cap, repeat_count)


def build_v15_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 6
    if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 3
    if str(row.get("template_subtype", "")).strip() == "bit_other":
        repeat_count += 2
    if v11_binary_family_key(row) == "unknown":
        repeat_count += 2
    return min(10, repeat_count)


def build_v16_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 2
    if family in V16_LOCAL_MISS_BINARY_FAMILIES:
        repeat_count += 3
    if family == "unknown":
        repeat_count += 1
    if template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 2
    if template_subtype == "bit_permutation_inversion":
        repeat_count += 2
    cap = 11 if verified else 8
    return min(cap, repeat_count)


def build_v16_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 6
    if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 3
    if str(row.get("template_subtype", "")).strip() == "bit_other":
        repeat_count += 2
    if v11_binary_family_key(row) == "unknown":
        repeat_count += 1
    return min(10, repeat_count)


def build_v17_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 2
    if family in V16_LOCAL_MISS_BINARY_FAMILIES:
        repeat_count += 2
    if family == "unknown":
        repeat_count += 1
    if template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 3
    if template_subtype == "bit_other":
        repeat_count += 1
    cap = 11 if verified else 9
    return min(cap, repeat_count)


def build_v17_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 6
    if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 3
    if str(row.get("template_subtype", "")).strip() == "bit_other":
        repeat_count += 2
    if v11_binary_family_key(row) == "unknown":
        repeat_count += 1
    return min(10, repeat_count)


def build_v18_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 4
    if family in V16_LOCAL_MISS_BINARY_FAMILIES:
        repeat_count += 2
    if family == "unknown":
        repeat_count += 1
    if template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 2
    if template_subtype == "bit_other":
        repeat_count += 1
    cap = 12 if verified else 10
    return min(cap, repeat_count)


def build_v18_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 8
    if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 4
    if str(row.get("template_subtype", "")).strip() == "bit_other":
        repeat_count += 2
    if v11_binary_family_key(row) == "unknown":
        repeat_count += 1
    return min(12, repeat_count)


def build_v19_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 2
    if hard_score >= 6.0:
        repeat_count += 3
    elif hard_score >= 5.0:
        repeat_count += 2
    if family in V16_LOCAL_MISS_BINARY_FAMILIES:
        repeat_count += 1
    if template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 2
    if template_subtype == "bit_other":
        repeat_count += 1
    cap = 12 if verified else 10
    return min(cap, repeat_count)


def build_v19_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 7
    if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 3
    if parse_float_text(row.get("hard_score", 0.0), 0.0) >= 5.0:
        repeat_count += 2
    if str(row.get("template_subtype", "")).strip() == "bit_other":
        repeat_count += 2
    return min(12, repeat_count)


def build_v20_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 4
    if family in V16_LOCAL_MISS_BINARY_FAMILIES:
        repeat_count += 2
    if family == "unknown":
        repeat_count += 1
    if hard_score >= 6.0:
        repeat_count += 3
    elif hard_score >= 5.0:
        repeat_count += 2
    if template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 3
    elif template_subtype in {"bit_structured_byte_formula", "bit_permutation_inversion"}:
        repeat_count += 1
    if template_subtype == "bit_other":
        repeat_count += 1
    cap = 13 if verified else 11
    return min(cap, repeat_count)


def build_v20_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 8
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 3
    if hard_score >= 6.0:
        repeat_count += 2
    elif hard_score >= 5.0:
        repeat_count += 1
    if family == "unknown":
        repeat_count += 1
    if template_subtype == "bit_other":
        repeat_count += 2
    return min(12, repeat_count)


def build_v21_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 3
    if family in V16_LOCAL_MISS_BINARY_FAMILIES:
        repeat_count += 2
    if template_subtype == "bit_structured_byte_formula":
        repeat_count += 3
    elif template_subtype == "bit_prompt_local_exact_formula":
        repeat_count += 3
    elif template_subtype == "bit_permutation_inversion":
        repeat_count += 1
    if family == "unknown":
        repeat_count += 1
    if hard_score >= 6.0:
        repeat_count += 1
    elif hard_score >= 5.0:
        repeat_count += 1
    if template_subtype == "bit_other":
        repeat_count += 1
    cap = 13 if verified else 11
    return min(cap, repeat_count)


def build_v21_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 7
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 2
    if family == "unknown":
        repeat_count += 1
    if template_subtype == "bit_other":
        repeat_count += 2
    return min(11, repeat_count)


def build_v22_binary_repeat_count(row: dict[str, Any], *, verified: bool) -> int:
    repeat_count = build_v11_binary_repeat_count(row, verified=verified)
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
    if verified:
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            repeat_count += 3
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            repeat_count += 2
        if template_subtype == "bit_structured_byte_formula":
            repeat_count += 3
        elif template_subtype == "bit_prompt_local_exact_formula":
            repeat_count += 3
        elif template_subtype == "bit_permutation_inversion":
            repeat_count += 1
        if family == "unknown":
            repeat_count += 1
        if hard_score >= 6.0:
            repeat_count += 1
        return min(14, repeat_count)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 1
    if family == "unknown":
        repeat_count += 1
    if template_subtype in {"bit_structured_byte_formula", "bit_other"}:
        repeat_count += 1
    return min(7, repeat_count)


def build_v22_manual_repeat_count(row: dict[str, Any]) -> int:
    repeat_count = 5
    row_id = str(row["id"]).strip()
    template_subtype = str(row.get("template_subtype", "")).strip()
    family = v11_binary_family_key(row)
    if row_id in V11_LOCAL_BIT_MISS_IDS:
        repeat_count += 1
    if family == "unknown":
        repeat_count += 1
    if template_subtype == "bit_other":
        repeat_count += 1
    return min(8, repeat_count)


def build_v11_binary_styles(row: dict[str, Any], *, verified: bool, repeat_count: int) -> list[str]:
    if verified:
        base_styles = ["exact_rule_commit", "exact_closure_commit"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            base_styles.append("anti_default1_commit")
    else:
        base_styles = ["answer_only_binary_commit"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            base_styles.append("answer_only_binary_closure")
    return expand_assistant_styles(base_styles, repeat_count)


def build_v11_nonbit_styles(bucket: str, repeat_count: int) -> list[str]:
    if bucket == "numeric_guess_rescue":
        return expand_assistant_styles(["numeric_guess_commit", "numeric_guess_short"], repeat_count)
    if bucket == "cipher_guardrail":
        return expand_assistant_styles(["cipher_boxed_tail"], repeat_count)
    raise ValueError(f"Unsupported v11 non-bit bucket: {bucket}")


def renumber_overlay_instances(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_counts: defaultdict[str, int] = defaultdict(int)
    total_counts = Counter(str(row["id"]) for row in rows)
    normalized: list[dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        row_id = str(copied["id"])
        seen_counts[row_id] += 1
        copied["overlay_instance"] = seen_counts[row_id]
        copied["recommended_repeat_count"] = int(total_counts[row_id])
        normalized.append(copied)
    return normalized


def select_v11_binary_rows(path: Path, *, required_tier: str) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in load_csv_rows(path):
        if str(row.get("selection_tier", "")).strip() != required_tier:
            continue
        if str(row.get("family", "")).strip() != "bit_manipulation":
            continue
        if not parse_bool_text(row.get("parse_ok", False)):
            continue
        if not parse_bool_text(row.get("boxed_safe", False)):
            continue
        if not is_binary_answer_text(str(row.get("answer", ""))):
            continue
        if parse_bool_text(row.get("suspect_label", False)):
            continue
        selected.append(row)
    return selected


def build_v11_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    manual_map = {str(row["id"]).strip(): row for row in manual_rows}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_rescue"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_rescue":
                    supervision_role = "lane2_binary_manual_rescue"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v11 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        repeat_count = build_v11_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V11_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V11_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        repeat_count = build_v11_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V11_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V11_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    selected_bit_ids = {str(row["id"]).strip() for row in unique_rows if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS}
    missing_manual_bit_ids = sorted(V11_LOCAL_BIT_MISS_IDS - selected_bit_ids)
    for row_id in missing_manual_bit_ids:
        row = manual_map.get(row_id)
        if row is None:
            continue
        styles = build_v11_binary_styles(row, verified=False, repeat_count=8)
        append_unique(
            row,
            bucket="binary_manual_rescue",
            source_mix=V11_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=["bit_manipulation", "manual_audit_priority", "best_local_bit_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="binary_manual_rescue",
            source_mix=V11_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=["bit_manipulation", "manual_audit_priority", "best_local_bit_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v11 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V11_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V11_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v11 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V11_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V11_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "selected_bit_miss_ids": sorted(
            row["id"] for row in unique_rows if row["id"] in V11_LOCAL_BIT_MISS_IDS
        ),
        "selected_numeric_guess_ids": sorted(
            row["id"] for row in unique_rows if row["id"] in V11_LOCAL_NUMERIC_GUESS_MISS_IDS
        ),
        "selected_cipher_ids": sorted(
            row["id"] for row in unique_rows if row["id"] in V11_LOCAL_CIPHER_MISS_IDS
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v12_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_full"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v12 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        repeat_count = build_v11_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V12_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V12_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        repeat_count = build_v11_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V12_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V12_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        repeat_count = build_v12_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_full", "answer_only_rescue"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V12_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V12_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v12 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V12_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V12_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v12 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V12_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V12_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v13_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_promptlocal_heavy"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v13 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        repeat_count = build_v13_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if str(row.get("template_subtype", "")).strip() == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_exact_formula")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V13_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V13_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        repeat_count = build_v13_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V13_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V13_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        repeat_count = build_v13_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_full", "promptlocal_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V13_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V13_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v13 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V13_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V13_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v13 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V13_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V13_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v14_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_structured_support"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v14 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        repeat_count = build_v14_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if str(row.get("template_subtype", "")).strip() in {"bit_structured_byte_formula", "bit_permutation_inversion"}:
            tags.append("structured_formula_priority")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V14_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V14_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        repeat_count = build_v14_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V14_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V14_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        repeat_count = build_v14_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "structured_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V14_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V14_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v14 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V14_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V14_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v14 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V14_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V14_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v15_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_bitother_support"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v15 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v15_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if template_subtype == "bit_other" or family == "unknown":
            tags.append("bitother_unknown_priority")
        if family in V11_PRIORITY_BINARY_FAMILIES:
            tags.append("hard_binary_family_priority")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V15_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V15_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v15_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary"]
        if str(row["id"]).strip() in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if template_subtype == "bit_other" or family == "unknown":
            tags.append("bitother_unknown_priority")
        if family in V11_PRIORITY_BINARY_FAMILIES:
            tags.append("hard_binary_family_priority")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V15_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V15_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v15_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "bitother_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if str(row.get("template_subtype", "")).strip() == "bit_other" or family == "unknown":
            tags.append("bitother_unknown_priority")
        if family in V11_PRIORITY_BINARY_FAMILIES:
            tags.append("hard_binary_family_priority")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V15_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V15_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v15 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V15_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V15_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v15 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V15_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V15_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v16_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_miss_family_support"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v16 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v16_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V16_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V16_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        row_id = str(row["id"]).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v16_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V16_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V16_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v16_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "miss_family_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family == "unknown":
            tags.append("unknown_family_priority")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V16_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V16_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v16 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V16_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V16_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v16 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V16_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V16_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v17_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_hybrid_support"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v17 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v17_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V17_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V17_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v17_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_other":
            tags.append("bitother_priority")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V17_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V17_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v17_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "hybrid_miss_promptlocal"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family == "unknown":
            tags.append("unknown_family_priority")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V17_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V17_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v17 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V17_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V17_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v17 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V17_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V17_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v18_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_explicit_local_miss"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v18 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v18_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary", "explicit_local_miss_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V18_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V18_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v18_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary", "explicit_local_miss_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_other":
            tags.append("bitother_priority")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V18_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V18_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v18_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "explicit_local_miss_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family == "unknown":
            tags.append("unknown_family_priority")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V18_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V18_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v18 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V18_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V18_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v18 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V18_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V18_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v19_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_hardscore_tail"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v19 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v19_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary", "hardscore_tail_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V19_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V19_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v19_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary", "hardscore_tail_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if template_subtype == "bit_other":
            tags.append("bitother_priority")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V19_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V19_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v19_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "hardscore_tail_heavy"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V19_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V19_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v19 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V19_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V19_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v19 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V19_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V19_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v20_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_fusion"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v20 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v20_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary", "localmiss_hardscore_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        if template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        elif template_subtype == "bit_structured_byte_formula":
            tags.append("structured_byte_priority")
        elif template_subtype == "bit_permutation_inversion":
            tags.append("permutation_priority")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V20_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V20_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v20_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary", "localmiss_hardscore_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        if template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        elif template_subtype == "bit_other":
            tags.append("bitother_priority")
        elif template_subtype == "bit_structured_byte_formula":
            tags.append("structured_byte_priority")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V20_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V20_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v20_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "localmiss_hardscore_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        if template_subtype == "bit_other":
            tags.append("bitother_priority")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V20_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V20_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v20 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V20_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V20_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v20 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V20_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V20_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v21_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_structured_promptlocal"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v21 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v21_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary", "structured_promptlocal_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_structured_byte_formula":
            tags.append("structured_byte_priority")
        elif template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        elif template_subtype == "bit_permutation_inversion":
            tags.append("permutation_priority")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V21_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V21_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v21_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary", "structured_promptlocal_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_structured_byte_formula":
            tags.append("structured_byte_priority")
        elif template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        elif template_subtype == "bit_other":
            tags.append("bitother_priority")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        elif hard_score >= 5.0:
            tags.append("hardscore_ge5")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V21_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V21_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v21_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "structured_promptlocal_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_other":
            tags.append("bitother_priority")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V21_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V21_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v21 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V21_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V21_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v21 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V21_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V21_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_v22_overlay_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    verified_rows = select_v11_binary_rows(TRAIN_VERIFIED_TRACE_READY_PATH, required_tier="verified_trace_ready")
    answer_only_rows = select_v11_binary_rows(TRAIN_ANSWER_ONLY_KEEP_PATH, required_tier="answer_only_keep")
    manual_rows = select_v11_binary_rows(TRAIN_MANUAL_AUDIT_PRIORITY_PATH, required_tier="manual_audit_priority")
    recommended_map = {row["id"]: row for row in load_csv_rows(TRAIN_RECOMMENDED_LEARNING_TARGET_PATH)}
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []
    unique_seen: set[tuple[str, str]] = set()

    def append_unique(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        key = (str(row["id"]).strip(), bucket)
        if key in unique_seen:
            return
        unique_rows.append(
            {
                "id": str(row["id"]).strip(),
                "category": detect_validation_category(str(row["prompt"])),
                "bucket": bucket,
                "selection_tier": str(row.get("selection_tier", "")).strip(),
                "template_subtype": str(row.get("template_subtype", "")).strip(),
                "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                "recommended_repeat_count": len(styles),
                "assistant_styles": "|".join(sorted(set(styles))),
                "source_mix": source_mix,
                "source_tags": "|".join(sorted(set(str(tag) for tag in source_tags if str(tag).strip()))),
                "binary_family_key": v11_binary_family_key(row),
                "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
            }
        )
        unique_seen.add(key)

    def append_repeated(
        row: dict[str, Any],
        *,
        bucket: str,
        source_mix: str,
        styles: Sequence[str],
        source_tags: Sequence[str],
    ) -> None:
        category = detect_validation_category(str(row["prompt"]))
        for assistant_style in styles:
            if bucket in {"binary_verified_core", "binary_answer_only_support", "binary_manual_support"}:
                completion_text = build_v11_binary_completion(row, assistant_style)
                if bucket == "binary_manual_support":
                    supervision_role = "lane2_binary_manual_precision"
                else:
                    supervision_role = (
                        "lane1_binary_verified"
                        if assistant_style in {"exact_rule_commit", "exact_closure_commit"}
                        else "lane2_binary_local_miss"
                        if assistant_style == "anti_default1_commit"
                        else "lane3_binary_answer_only"
                    )
            elif bucket == "numeric_guess_rescue":
                completion_text = build_v11_numeric_completion(row, assistant_style)
                supervision_role = "lane4_numeric_guess_rescue"
            elif bucket == "cipher_guardrail":
                completion_text = build_v11_text_completion(row, assistant_style)
                supervision_role = "lane5_cipher_guardrail"
            else:
                raise ValueError(f"Unsupported v22 bucket: {bucket}")
            repeated_rows.append(
                {
                    "id": str(row["id"]).strip(),
                    "category": category,
                    "bucket": bucket,
                    "prompt": str(row["prompt"]).strip(),
                    "answer": str(row["answer"]).strip(),
                    "completion_text": completion_text,
                    "assistant_style": assistant_style,
                    "supervision_role": supervision_role,
                    "selection_tier": str(row.get("selection_tier", "")).strip(),
                    "template_subtype": str(row.get("template_subtype", "")).strip(),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")).strip(),
                    "source_mix": source_mix,
                    "source_tags": sorted(set(str(tag) for tag in source_tags if str(tag).strip())),
                    "hard_score": parse_float_text(row.get("hard_score", 0.0), 0.0),
                    "audit_reasons": str(row.get("audit_reasons", "")).strip(),
                    "analysis_notes": str(row.get("analysis_notes", "")).strip(),
                    "symbol_query_operator": str(row.get("symbol_query_operator", "")).strip(),
                    "symbol_numeric_formula_name": str(row.get("symbol_numeric_formula_name", "")).strip(),
                    "bit_query_binary": str(row.get("bit_query_binary", "")).strip(),
                    "bit_structured_formula_name": str(row.get("bit_structured_formula_name", "")).strip(),
                    "bit_structured_formula_prediction": str(row.get("bit_structured_formula_prediction", "")).strip(),
                    "bit_structured_formula_abstract_family": str(
                        row.get("bit_structured_formula_abstract_family", "")
                    ).strip(),
                    "bit_not_structured_formula_name": str(row.get("bit_not_structured_formula_name", "")).strip(),
                    "bit_not_structured_formula_prediction": str(
                        row.get("bit_not_structured_formula_prediction", "")
                    ).strip(),
                    "bit_not_structured_formula_abstract_family": str(
                        row.get("bit_not_structured_formula_abstract_family", "")
                    ).strip(),
                }
            )

    for row in verified_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v22_binary_repeat_count(row, verified=True)
        tags = ["bit_manipulation", "verified_trace_ready", "curated_binary", "verified_precision_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family in V16_LOCAL_MISS_BINARY_FAMILIES:
            tags.append("local_miss_family_priority")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_structured_byte_formula":
            tags.append("structured_byte_priority")
        elif template_subtype == "bit_prompt_local_exact_formula":
            tags.append("promptlocal_priority")
        elif template_subtype == "bit_permutation_inversion":
            tags.append("permutation_priority")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        styles = build_v11_binary_styles(row, verified=True, repeat_count=repeat_count)
        append_unique(row, bucket="binary_verified_core", source_mix=V22_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)
        append_repeated(row, bucket="binary_verified_core", source_mix=V22_BINARY_VERIFIED_SOURCE_MIX, styles=styles, source_tags=tags)

    for row in answer_only_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        hard_score = parse_float_text(row.get("hard_score", 0.0), 0.0)
        repeat_count = build_v22_binary_repeat_count(row, verified=False)
        tags = ["bit_manipulation", "answer_only_keep", "curated_binary", "verified_precision_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_structured_byte_formula":
            tags.append("structured_byte_priority")
        elif template_subtype == "bit_other":
            tags.append("bitother_priority")
        if hard_score >= 6.0:
            tags.append("hardscore_ge6")
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        append_unique(
            row,
            bucket="binary_answer_only_support",
            source_mix=V22_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_answer_only_support",
            source_mix=V22_BINARY_ANSWER_ONLY_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row in manual_rows:
        row_id = str(row["id"]).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        family = v11_binary_family_key(row)
        repeat_count = build_v22_manual_repeat_count(row)
        styles = build_v11_binary_styles(row, verified=False, repeat_count=repeat_count)
        tags = ["bit_manipulation", "manual_audit_priority", "manual_binary_support", "verified_precision_fusion"]
        if row_id in V11_LOCAL_BIT_MISS_IDS:
            tags.append("best_local_bit_miss")
        if family == "unknown":
            tags.append("unknown_family_priority")
        if template_subtype == "bit_other":
            tags.append("bitother_priority")
        append_unique(
            row,
            bucket="binary_manual_support",
            source_mix=V22_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )
        append_repeated(
            row,
            bucket="binary_manual_support",
            source_mix=V22_BINARY_MANUAL_SOURCE_MIX,
            styles=styles,
            source_tags=tags,
        )

    for row_id in sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v22 numeric guess rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("numeric_guess_rescue", repeat_count=8)
        append_unique(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V22_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )
        append_repeated(
            row,
            bucket="numeric_guess_rescue",
            source_mix=V22_NUMERIC_GUESS_SOURCE_MIX,
            styles=styles,
            source_tags=["equation_numeric_guess", "best_local_numeric_guess_miss", "answer_only_rescue"],
        )

    for row_id in sorted(V11_LOCAL_CIPHER_MISS_IDS):
        row = recommended_map.get(row_id)
        if row is None:
            raise FileNotFoundError(f"Missing v22 cipher rescue row in recommended target: {row_id}")
        styles = build_v11_nonbit_styles("cipher_guardrail", repeat_count=6)
        append_unique(
            row,
            bucket="cipher_guardrail",
            source_mix=V22_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )
        append_repeated(
            row,
            bucket="cipher_guardrail",
            source_mix=V22_CIPHER_SOURCE_MIX,
            styles=styles,
            source_tags=["cipher", "best_local_cipher_miss", "guardrail"],
        )

    diagnostics = {
        "curated_binary_verified_unique": len(verified_rows),
        "curated_binary_answer_only_unique": len(answer_only_rows),
        "curated_binary_total_unique": len(verified_rows) + len(answer_only_rows),
        "manual_binary_unique": len(manual_rows),
        "selected_bit_miss_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_BIT_MISS_IDS}
        ),
        "selected_numeric_guess_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_NUMERIC_GUESS_MISS_IDS}
        ),
        "selected_cipher_ids": sorted(
            {str(row["id"]) for row in unique_rows if str(row["id"]) in V11_LOCAL_CIPHER_MISS_IDS}
        ),
    }
    unique_rows.sort(key=lambda row: (str(row["bucket"]), str(row["id"])))
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


def build_binary_variant_training_bundle(
    *,
    repeated_rows: Sequence[dict[str, Any]],
    bundle_path: Path,
    version_name: str,
    note: str,
) -> dict[str, Any]:
    base_rows, base_examples, batch_size = load_base_snapshot_bundle_examples()
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    base_step_count = max(int(row["step"]) for row in base_rows) + 1 if base_rows else 0
    total_examples = 0
    total_tokens = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()
    overlay_by_bucket: Counter[str] = Counter()
    overlay_examples_by_style: Counter[str] = Counter()
    source_mix_counts: Counter[str] = Counter()

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": version_name,
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(SNAPSHOT_ROOT),
        "base_snapshot_config": load_json(SNAPSHOT_CONFIG_PATH),
        "bundle_path": relative_to_repo(bundle_path),
        "overlay_token_strategy": "retokenize_all",
        "note": note,
    }

    with bundle_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False) + "\n")
        for row in base_rows:
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
            tokens, mask = tokenize_bundle_overlay_example(str(row["prompt"]), str(row["completion_text"]))
            num_loss_tokens = sum(mask)
            overlay_step = base_step_count + (overlay_offset // batch_size)
            payload = {
                "record_type": "example",
                "example_id": f"{row['id']}#overlay-{row['overlay_instance']}",
                "source_problem_id": row["id"],
                "source": "corrective_overlay",
                "segment": "synthetic.jsonl",
                "category": row["category"],
                "step": overlay_step,
                "num_loss_tokens": num_loss_tokens,
                "bucket": row["bucket"],
                "overlay_instance": int(row["overlay_instance"]),
                "assistant_style": row["assistant_style"],
                "supervision_role": row["supervision_role"],
                "recommended_repeat_count": int(row["recommended_repeat_count"]),
                "source_tags": row["source_tags"],
                "source_mix": row["source_mix"],
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[str(row["category"])] += 1
            overlay_by_bucket[str(row["bucket"])] += 1
            overlay_examples_by_style[str(row["assistant_style"])] += 1
            source_mix_counts[str(row["source_mix"])] += 1

    total_steps = base_step_count + ((len(repeated_rows) + batch_size - 1) // batch_size)
    return {
        "path": relative_to_repo(bundle_path),
        "base_examples": len(base_rows),
        "overlay_examples": len(repeated_rows),
        "total_examples": total_examples,
        "batch_size": batch_size,
        "total_steps": total_steps,
        "overlay_token_strategy": "retokenize_all",
        "total_tokens": total_tokens,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_seq_len": max_seq_len,
        "overlay_by_bucket": dict(sorted(overlay_by_bucket.items())),
        "overlay_examples_by_style": dict(sorted(overlay_examples_by_style.items())),
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "reused_base_synthetic_problem_count": 0,
        "retokenized_overlay_problem_count": len({str(row["id"]) for row in repeated_rows}),
    }


def build_v11_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V11_VERSION_NAME,
        note=(
            "Single-file training bundle for v11. Keeps the checked-in v20 snapshot intact, "
            "then heavily boosts curated binary coverage plus the observed local300 residual "
            "bit/numeric-guess/cipher misses under the README evaluation contract."
        ),
    )


def build_v12_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V12_VERSION_NAME,
        note=(
            "Single-file training bundle for v12. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, and adds all manual_audit_priority binary rows "
            "as answer-only support to widen hard bit_other coverage under the README evaluation contract."
        ),
    )


def build_v13_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V13_VERSION_NAME,
        note=(
            "Single-file training bundle for v13. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, boosts verified prompt-local exact-formula rows harder, "
            "and still includes all manual_audit_priority binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v14_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V14_VERSION_NAME,
        note=(
            "Single-file training bundle for v14. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, boosts structured-byte and permutation-style verified rows, "
            "and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v15_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V15_VERSION_NAME,
        note=(
            "Single-file training bundle for v15. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, boosts bit_other and unknown-family rows harder than v12/v14, "
            "and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v16_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V16_VERSION_NAME,
        note=(
            "Single-file training bundle for v16. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, boosts the choose/majority/unknown families tied to the observed local bit misses, "
            "and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v17_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V17_VERSION_NAME,
        note=(
            "Single-file training bundle for v17. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, jointly boosts prompt-local exact rows plus the choose/majority/unknown families tied to the observed local bit misses, "
            "and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v18_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V18_VERSION_NAME,
        note=(
            "Single-file training bundle for v18. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, explicitly boosts the observed local bit miss IDs plus their prompt-local and miss-family neighborhoods, "
            "and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v19_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V19_VERSION_NAME,
        note=(
            "Single-file training bundle for v19. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, boosts high-hard-score binary rows plus the observed local miss neighborhoods, "
            "and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v20_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V20_VERSION_NAME,
        note=(
            "Single-file training bundle for v20. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, fuses explicit local BIT miss emphasis with prompt-local and miss-family replay, "
            "adds high-hard-score tail pressure, and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v21_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V21_VERSION_NAME,
        note=(
            "Single-file training bundle for v21. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, emphasizes the overlap between local-miss families and structured/prompt-local verified rows, "
            "and keeps manual binary rows as answer-only support under the README evaluation contract."
        ),
    )


def build_v22_training_bundle(*, repeated_rows: Sequence[dict[str, Any]], bundle_path: Path) -> dict[str, Any]:
    return build_binary_variant_training_bundle(
        repeated_rows=repeated_rows,
        bundle_path=bundle_path,
        version_name=V22_VERSION_NAME,
        note=(
            "Single-file training bundle for v22. Keeps the checked-in v20 snapshot intact, "
            "retains the full curated binary core, further prioritizes verified structured/prompt-local overlaps and local-miss families, "
            "and keeps answer-only/manual binary lanes intentionally lighter under the README evaluation contract."
        ),
    )


def validate_binary_variant_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
    verified_source_mix: str,
    answer_only_source_mix: str,
    required_source_mixes: Sequence[str] = (),
) -> dict[str, Any]:
    selected_ids = {str(row["id"]) for row in unique_rows}
    missing_local_bit_miss_ids = sorted(V11_LOCAL_BIT_MISS_IDS - selected_ids)
    missing_local_numeric_guess_ids = sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS - selected_ids)
    missing_local_cipher_ids = sorted(V11_LOCAL_CIPHER_MISS_IDS - selected_ids)
    source_mix_counts = Counter(str(row["source_mix"]) for row in repeated_rows)
    errors: list[str] = []
    if missing_local_bit_miss_ids:
        errors.append("best local bit misses are not fully covered")
    if missing_local_numeric_guess_ids:
        errors.append("best local numeric-guess misses are not fully covered")
    if missing_local_cipher_ids:
        errors.append("best local cipher miss is not covered")
    if int(diagnostics["curated_binary_total_unique"]) != (
        int(diagnostics["curated_binary_verified_unique"]) + int(diagnostics["curated_binary_answer_only_unique"])
    ):
        errors.append("binary curated counts are inconsistent")
    if source_mix_counts.get(verified_source_mix, 0) <= 0:
        errors.append("verified binary lane is empty")
    if source_mix_counts.get(answer_only_source_mix, 0) <= 0:
        errors.append("answer-only binary lane is empty")
    for source_mix in required_source_mixes:
        if source_mix_counts.get(str(source_mix), 0) <= 0:
            errors.append(f"required source mix is empty: {source_mix}")
    if int(training_bundle.get("retokenized_overlay_problem_count", 0)) <= 0:
        errors.append("overlay retokenization did not occur")
    return {
        "passed": not errors,
        "errors": errors,
        "missing_local_bit_miss_ids": missing_local_bit_miss_ids,
        "missing_local_numeric_guess_ids": missing_local_numeric_guess_ids,
        "missing_local_cipher_ids": missing_local_cipher_ids,
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
    }


def validate_v11_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V11_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V11_BINARY_ANSWER_ONLY_SOURCE_MIX,
    )


def validate_v12_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V12_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V12_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V12_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v13_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V13_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V13_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V13_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v14_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V14_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V14_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V14_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v15_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V15_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V15_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V15_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v16_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V16_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V16_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V16_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v17_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V17_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V17_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V17_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v18_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V18_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V18_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V18_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v19_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V19_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V19_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V19_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v20_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V20_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V20_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V20_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v21_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V21_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V21_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V21_BINARY_MANUAL_SOURCE_MIX,),
    )


def validate_v22_summary(
    *,
    unique_rows: Sequence[dict[str, Any]],
    repeated_rows: Sequence[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    return validate_binary_variant_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
        verified_source_mix=V22_BINARY_VERIFIED_SOURCE_MIX,
        answer_only_source_mix=V22_BINARY_ANSWER_ONLY_SOURCE_MIX,
        required_source_mixes=(V22_BINARY_MANUAL_SOURCE_MIX,),
    )


def render_v11_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V11_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to use `verified_trace_ready` as the trace core, mix `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by boosting the 16 observed BIT misses plus the 2 numeric-guess and 1 cipher residuals.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V11_RUN_NAME}`",
        f"- runtime status: `not started`",
        f"- latest observed step: `not started`",
        f"- retained checkpoints: `none`",
        f"- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Strengthen nearly all curated binary rows by taking all `bit_manipulation` rows from `verified_trace_ready` and `answer_only_keep`.",
        "- Upweight the 16 observed local BIT misses explicitly instead of relying only on family-level ratio tuning.",
        "- Backfill any uncovered local BIT miss with an answer-only `manual_audit_priority` rescue row instead of promoting raw manual CoT.",
        "- Add only the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v11_bit_binary_mainline(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v11 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v11_overlay_rows()
    training_bundle = build_v11_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v11_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V11_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v11_results_markdown(summary))
    return summary


def render_v12_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V12_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by combining the full curated binary core with all 87 manual binary rows as answer-only support.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V12_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11.",
        "- Promote all `manual_audit_priority` binary rows only as answer-only support, never as raw manual CoT, to widen hard `bit_other` coverage.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v12_bit_binary_manual_heavy(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v12 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v12_overlay_rows()
    training_bundle = build_v12_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v12_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V12_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v12_results_markdown(summary))
    return summary


def render_v13_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V13_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by keeping all binary rows while pushing prompt-local exact-formula support harder than v12.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V13_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11/v12.",
        "- Upweight `bit_prompt_local_exact_formula` and other hard prompt-local / bit_other verified rows more aggressively than v12.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v13_bit_binary_promptlocal_heavy(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v13 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v13_overlay_rows()
    training_bundle = build_v13_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v13_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V13_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v13_results_markdown(summary))
    return summary


def render_v14_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V14_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by keeping all binary rows while pushing structured-byte and permutation-style support harder than v12.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V14_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11/v12/v13.",
        "- Upweight `bit_structured_byte_formula` and `bit_permutation_inversion` rows more aggressively than v12.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v14_bit_binary_structured_heavy(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v14 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v14_overlay_rows()
    training_bundle = build_v14_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v14_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V14_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v14_results_markdown(summary))
    return summary


def render_v15_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V15_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by keeping all binary rows while pushing bit_other / unknown-family coverage harder than v12/v14.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V15_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11/v12/v13/v14.",
        "- Upweight hard `bit_other` and unknown-family binary rows more aggressively than v12/v14 while still keeping priority choose/majority families hot.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v15_bit_binary_bitother_heavy(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v15 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v15_overlay_rows()
    training_bundle = build_v15_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v15_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V15_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v15_results_markdown(summary))
    return summary


def render_v16_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V16_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by keeping all binary rows while pushing the exact choose/majority/unknown families that match the observed local BIT misses.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V16_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v15.",
        "- Upweight the exact choose/majority families observed in the local BIT misses, plus the surrounding unknown-family tail, instead of only broad subtype weighting.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v16_bit_binary_miss_family_heavy(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v16 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v16_overlay_rows()
    training_bundle = build_v16_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v16_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V16_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v16_results_markdown(summary))
    return summary


def render_v17_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V17_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by combining prompt-local exact rows with the exact choose/majority/unknown families seen in the observed local BIT misses.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V17_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v16.",
        "- Upweight prompt-local exact rows and the exact choose/majority/unknown local-miss families together instead of tuning them separately.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v17_bit_binary_hybrid_miss_promptlocal(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v17 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v17_overlay_rows()
    training_bundle = build_v17_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v17_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V17_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v17_results_markdown(summary))
    return summary


def render_v18_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V18_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by explicitly over-weighting the observed local BIT miss IDs plus their prompt-local and miss-family neighborhoods.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V18_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v17.",
        "- Upweight the observed local BIT miss IDs more aggressively than v11/v17 while still keeping prompt-local and miss-family neighborhoods hot.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v18_bit_binary_explicit_local_miss(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v18 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v18_overlay_rows()
    training_bundle = build_v18_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v18_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V18_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v18_results_markdown(summary))
    return summary


def render_v19_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V19_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by boosting high-hard-score binary rows together with the observed local BIT miss neighborhoods.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V19_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v18.",
        "- Upweight high-hard-score rows (`hard_score >= 6` first, then `>= 5`) while still keeping the observed local BIT miss neighborhoods warm.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v19_bit_binary_hardscore_tail(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v19 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v19_overlay_rows()
    training_bundle = build_v19_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v19_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V19_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v19_results_markdown(summary))
    return summary


def render_v20_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V20_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by combining explicit local BIT miss replay, prompt-local support, miss-family support, and hard-score-tail replay.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V20_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v19.",
        "- Fuse the strongest current binary signals: explicit local BIT miss IDs, local miss families, `bit_prompt_local_exact_formula`, and the high-hard-score tail.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v20_bit_binary_localmiss_hardscore_fusion(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v20 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v20_overlay_rows()
    training_bundle = build_v20_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v20_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V20_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v20_results_markdown(summary))
    return summary


def render_v21_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V21_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by emphasizing the overlap between local BIT miss families and structured/prompt-local verified rows.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V21_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v20.",
        "- Emphasize where the current best local BIT misses actually live: `bit_structured_byte_formula`, `bit_prompt_local_exact_formula`, and local miss families such as `choose(...)` / `majority(...)` / `unknown`.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v21_bit_binary_structured_promptlocal_fusion(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v21 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v21_overlay_rows()
    training_bundle = build_v21_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v21_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V21_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v21_results_markdown(summary))
    return summary


def render_v22_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary["training_bundle"]
    validation = summary["validation"]
    lines = [
        f"# {V22_VERSION_NAME}",
        "",
        f"- created_at: {summary['created_at']}",
        "- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.",
        "- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.",
        "- local target: current best local300 `0.846667` -> aim for `> 0.9` by pushing verified structured/prompt-local binary rows harder while keeping answer-only/manual noise lighter.",
        "- status: bundle generated; model score not yet measured.",
        f"- planned run name: `{V22_RUN_NAME}`",
        "- runtime status: `not started`",
        "- latest observed step: `not started`",
        "- retained checkpoints: `none`",
        "- local300 score: TBD",
        "",
        "## Strategy",
        "",
        "- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.",
        "- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v21.",
        "- Push the verified precision lane harder: local miss families plus `bit_structured_byte_formula` and `bit_prompt_local_exact_formula` get the highest replay weights.",
        "- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.",
        "- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.",
        "",
        "## Selection",
        "",
        f"- curated_binary_verified_unique: {summary['diagnostics']['curated_binary_verified_unique']}",
        f"- curated_binary_answer_only_unique: {summary['diagnostics']['curated_binary_answer_only_unique']}",
        f"- curated_binary_total_unique: {summary['diagnostics']['curated_binary_total_unique']}",
        f"- manual_binary_unique: {summary['diagnostics']['manual_binary_unique']}",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(["", "### Repeated rows by source mix", ""])
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Targeted residual IDs",
            "",
            f"- local_bit_miss_ids: `{','.join(sorted(V11_LOCAL_BIT_MISS_IDS))}`",
            f"- local_numeric_guess_miss_ids: `{','.join(sorted(V11_LOCAL_NUMERIC_GUESS_MISS_IDS))}`",
            f"- local_cipher_miss_ids: `{','.join(sorted(V11_LOCAL_CIPHER_MISS_IDS))}`",
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_local_bit_miss_ids: {validation['missing_local_bit_miss_ids']}",
            f"- missing_local_numeric_guess_ids: {validation['missing_local_numeric_guess_ids']}",
            f"- missing_local_cipher_ids: {validation['missing_local_cipher_ids']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle['path']}",
            f"- base_examples: {bundle['base_examples']}",
            f"- overlay_examples: {bundle['overlay_examples']}",
            f"- total_examples: {bundle['total_examples']}",
            f"- total_steps: {bundle['total_steps']}",
            f"- total_tokens: {bundle['total_tokens']}",
            f"- max_seq_len: {bundle['max_seq_len']}",
            f"- retokenized_overlay_problem_count: {bundle['retokenized_overlay_problem_count']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_build_v22_bit_binary_verified_precision_fusion(args: argparse.Namespace) -> dict[str, Any]:
    for required_path in (
        TRAIN_VERIFIED_TRACE_READY_PATH,
        TRAIN_ANSWER_ONLY_KEEP_PATH,
        TRAIN_MANUAL_AUDIT_PRIORITY_PATH,
        TRAIN_RECOMMENDED_LEARNING_TARGET_PATH,
        SNAPSHOT_CONFIG_PATH,
        SNAPSHOT_INDEX_PATH,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Missing required v22 input: {required_path}")
    unique_rows, repeated_rows, diagnostics = build_v22_overlay_rows()
    training_bundle = build_v22_training_bundle(repeated_rows=repeated_rows, bundle_path=Path(args.bundle_path).resolve())
    validation = validate_v22_summary(
        unique_rows=unique_rows,
        repeated_rows=repeated_rows,
        diagnostics=diagnostics,
        training_bundle=training_bundle,
    )
    summary = {
        "version": V22_VERSION_NAME,
        "created_at": utc_now(),
        "readme_eval_contract": README_EVAL_CONTRACT,
        "bundle_path": relative_to_repo(Path(args.bundle_path).resolve()),
        "results_path": relative_to_repo(Path(args.results_path).resolve()),
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(Counter(str(row["bucket"]) for row in unique_rows).items())),
        "source_mix_counts": dict(sorted(Counter(str(row["source_mix"]) for row in repeated_rows).items())),
        "diagnostics": diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
    }
    write_text(Path(args.results_path).resolve(), render_v22_results_markdown(summary))
    return summary


def allocate_proportional_counts(
    category_counts: Sequence[tuple[str, int]],
    *,
    target_total: int,
) -> dict[str, int]:
    total = sum(int(count) for _, count in category_counts)
    if target_total <= 0:
        raise ValueError(f"target_total must be positive; got {target_total}")
    if total <= 0:
        raise ValueError("category_counts must contain at least one row")
    if target_total > total:
        raise ValueError(f"target_total={target_total} exceeds available rows={total}")

    allocations: dict[str, int] = {}
    remainders: list[tuple[float, int, int, str]] = []
    assigned = 0
    for order, (category, count_value) in enumerate(category_counts):
        count = int(count_value)
        exact = (count * target_total) / total
        base = math.floor(exact)
        allocations[str(category)] = base
        assigned += base
        remainders.append((exact - base, count, order, str(category)))
    for _, _, _, category in sorted(remainders, key=lambda item: (-item[0], -item[1], item[2]))[
        : target_total - assigned
    ]:
        allocations[category] += 1
    return allocations


def select_evenly_spaced_items[T](items: Sequence[T], target_count: int) -> list[T]:
    if target_count <= 0:
        return []
    if target_count >= len(items):
        return list(items)
    if target_count == 1:
        return [items[len(items) // 2]]

    selected_positions: list[int] = []
    total = len(items)
    for bucket_index in range(target_count):
        start = math.floor(bucket_index * total / target_count)
        end = math.floor((bucket_index + 1) * total / target_count) - 1
        if end < start:
            end = start
        position = (start + end) // 2
        if selected_positions and position <= selected_positions[-1]:
            position = selected_positions[-1] + 1
        max_position = total - (target_count - bucket_index)
        position = min(position, max_position)
        selected_positions.append(position)
    return [items[position] for position in selected_positions]


def build_validation_sample_selection(
    rows: Sequence[dict[str, str]],
    *,
    validation_sample_size: int,
    validation_subset_size: int,
    validation_subset_mode: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source_rows = list(rows[:validation_sample_size])
    category_buckets: OrderedDict[str, list[tuple[int, dict[str, str]]]] = OrderedDict()
    for source_index, row in enumerate(source_rows):
        category = detect_validation_category(str(row["prompt"]))
        category_buckets.setdefault(category, []).append((source_index, row))
    source_counts = {category: len(bucket_rows) for category, bucket_rows in category_buckets.items()}

    if validation_subset_size <= 0 or validation_subset_size >= len(source_rows):
        selected_rows = source_rows
        selected_counts = dict(source_counts)
        selection_mode = "head"
        selection_tag = f"head_{len(selected_rows)}"
    elif validation_subset_mode == "stratified-category-proportional":
        target_counts = allocate_proportional_counts(
            [(category, len(bucket_rows)) for category, bucket_rows in category_buckets.items()],
            target_total=validation_subset_size,
        )
        selected_indexed_rows: list[tuple[int, dict[str, str]]] = []
        selected_counts = {}
        for category, bucket_rows in category_buckets.items():
            chosen = select_evenly_spaced_items(bucket_rows, target_counts.get(category, 0))
            selected_indexed_rows.extend(chosen)
            selected_counts[category] = len(chosen)
        selected_indexed_rows.sort(key=lambda item: item[0])
        selected_rows = [row for _, row in selected_indexed_rows]
        selection_mode = "stratified-category-proportional"
        selection_tag = f"stratified_category_{len(selected_rows)}_of_{len(source_rows)}"
    else:
        raise ValueError(f"Unsupported validation_subset_mode: {validation_subset_mode}")

    return selected_rows, {
        "mode": selection_mode,
        "selection_tag": selection_tag,
        "source_total": len(source_rows),
        "selected_total": len(selected_rows),
        "source_counts": source_counts,
        "selected_counts": selected_counts,
    }


def build_adapter_validation_evaluation_name(
    sample_selection: dict[str, Any],
    *,
    total_rows_global: int,
    eval_shards: int,
    eval_shard_index: int,
) -> str:
    selection_tag = str(sample_selection.get("selection_tag", f"head_{total_rows_global}"))
    selected_total = int(sample_selection.get("selected_total", total_rows_global))
    if total_rows_global != selected_total:
        selection_tag = f"{selection_tag}_limit_{total_rows_global}"
    if eval_shards <= 1:
        return f"adapter_validation_{selection_tag}"
    return f"adapter_validation_{selection_tag}_shard_{eval_shard_index:02d}_of_{eval_shards:02d}"


def load_category_map() -> dict[str, str]:
    rows = load_jsonl(PROBLEMS_INDEX_PATH)
    return {str(row["id"]): str(row["category"]) for row in rows}


def compute_eval_slice(total_rows: int, shard_count: int, shard_index: int) -> tuple[int, int]:
    if shard_count <= 0:
        raise ValueError(f"eval_shards must be positive; got {shard_count}")
    if shard_index < 0 or shard_index >= shard_count:
        raise ValueError(f"eval_shard_index must be in [0, {shard_count}); got {shard_index}")
    base = total_rows // shard_count
    remainder = total_rows % shard_count
    start = shard_index * base + min(shard_index, remainder)
    size = base + (1 if shard_index < remainder else 0)
    return start, start + size


def resolve_eval_root(run_root: Path, *, shard_count: int, shard_index: int) -> Path:
    base_eval_root = run_root / "aopen_eval"
    if shard_count <= 1:
        return base_eval_root
    return base_eval_root / "shards" / f"shard_{shard_index:02d}_of_{shard_count:02d}"


def resolve_adapter_validation_root(
    run_root: Path,
    *,
    shard_count: int,
    shard_index: int,
    root_name: str = DEFAULT_ADAPTER_VALIDATION_ROOT_NAME,
) -> Path:
    base_validation_root = run_root / root_name
    if shard_count <= 1:
        return base_validation_root
    return base_validation_root / "shards" / f"shard_{shard_index:02d}_of_{shard_count:02d}"


def load_validation_records_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    def normalize_record(raw_record: dict[str, str], fallback_index: int) -> dict[str, Any]:
        row_index_value = raw_record.get("row_index_within_shard", "")
        row_index_text = str(row_index_value).strip()
        minlogprob_value = str(raw_record.get("minlogprob", "")).strip()
        return {
            "row_index_within_shard": int(row_index_text) if row_index_text else fallback_index,
            "id": str(raw_record.get("id", "")),
            "prompt": str(raw_record.get("prompt", "")),
            "answer": str(raw_record.get("answer", "")),
            "output": str(raw_record.get("output", "")),
            "category": str(raw_record.get("category", "")),
            "predicted": str(raw_record.get("predicted", "")),
            "correct": str(raw_record.get("correct", "")).strip().lower() in {"true", "1", "1.0"},
            "minlogprob": None if not minlogprob_value else float(minlogprob_value),
        }

    records: list[dict[str, Any]] = []
    with path.open("r", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return []
        for fallback_index, row in enumerate(reader):
            if not row:
                continue
            if len(row) == len(VALIDATION_RECORD_COLUMNS):
                field_names = VALIDATION_RECORD_COLUMNS
            elif len(row) == len(VALIDATION_FINAL_COLUMNS):
                field_names = VALIDATION_FINAL_COLUMNS
            elif len(row) == len(header):
                field_names = tuple(str(name) for name in header)
            else:
                raise RuntimeError(
                    f"Unsupported validation CSV row width in {path}: header={len(header)} row={len(row)}"
                )
            raw_record = {field_name: value for field_name, value in zip(field_names, row)}
            records.append(normalize_record(raw_record, fallback_index))
    return records


def rewrite_validation_checkpoint_records(checkpoint_path: Path, records: Sequence[dict[str, Any]]) -> None:
    ensure_dir(checkpoint_path.parent)
    with checkpoint_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=VALIDATION_RECORD_COLUMNS)
        writer.writeheader()
        for record in sort_validation_records(records):
            writer.writerow(
                {
                    column: "" if record.get(column) is None else record.get(column)
                    for column in VALIDATION_RECORD_COLUMNS
                }
            )


def append_validation_checkpoint_records(checkpoint_path: Path, records: Sequence[dict[str, Any]]) -> None:
    if not records:
        return
    ensure_dir(checkpoint_path.parent)
    write_header = not checkpoint_path.exists()
    with checkpoint_path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=VALIDATION_RECORD_COLUMNS)
        if write_header:
            writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    column: "" if record.get(column) is None else record.get(column)
                    for column in VALIDATION_RECORD_COLUMNS
                }
            )


def sort_validation_records(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda record: int(record["row_index_within_shard"]))


def build_validation_output_frame(records: Sequence[dict[str, Any]]) -> pd.DataFrame:
    ordered_records = sort_validation_records(records)
    return pd.DataFrame.from_records(ordered_records, columns=VALIDATION_FINAL_COLUMNS)


def build_validation_results_table(validation_frame: pd.DataFrame) -> pd.DataFrame:
    stats = validation_frame.groupby("category")["correct"].agg(correct="sum", total="count").sort_index()
    if stats.empty:
        totals = pd.DataFrame(
            {
                "correct": [0],
                "total": [0],
                "weightage": ["100.0%"],
                "percentage": ["0.0%"],
                "contribution": ["0.0%"],
            },
            index=["TOTAL"],
        )
        return totals
    stats["correct"] = stats["correct"].astype("int")
    grand_total = int(stats["total"].sum())
    stats["weightage"] = (stats["total"] / grand_total * 100).map("{:.1f}%".format)
    stats["percentage"] = (stats["correct"] / stats["total"] * 100).map("{:.1f}%".format)
    stats["contribution"] = (stats["correct"] / grand_total * 100).map("{:.1f}%".format)
    overall_pct = stats["correct"].sum() / grand_total * 100
    totals = pd.DataFrame(
        {
            "correct": [int(stats["correct"].sum())],
            "total": [grand_total],
            "weightage": ["100.0%"],
            "percentage": [f"{overall_pct:.1f}%"],
            "contribution": [f"{overall_pct:.1f}%"],
        },
        index=["TOTAL"],
    )
    return pd.concat([stats, totals])


def summarize_validation_results(results_frame: pd.DataFrame) -> dict[str, Any]:
    category_rows: list[dict[str, Any]] = []
    for category, row in results_frame.drop(index="TOTAL", errors="ignore").iterrows():
        correct = int(row["correct"])
        total = int(row["total"])
        category_rows.append(
            {
                "category": str(category),
                "correct": correct,
                "total": total,
                "accuracy": round(correct / total, 6) if total else 0.0,
                "weightage": str(row["weightage"]),
                "percentage": str(row["percentage"]),
                "contribution": str(row["contribution"]),
            }
        )
    total_correct = int(results_frame.loc["TOTAL", "correct"]) if "TOTAL" in results_frame.index else 0
    total_count = int(results_frame.loc["TOTAL", "total"]) if "TOTAL" in results_frame.index else 0
    return {
        "overall": {
            "correct": total_correct,
            "total": total_count,
            "accuracy": round(total_correct / total_count, 6) if total_count else 0.0,
        },
        "categories": category_rows,
    }


def normalize_smoke_prediction_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def evaluate_smoke_validation_gate(validation_root: Path) -> dict[str, Any]:
    summary_path = validation_root / "validation_summary.json"
    validation_csv_path = validation_root / "validation.csv"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing smoke validation summary at {summary_path}")
    if not validation_csv_path.exists():
        raise FileNotFoundError(f"Missing smoke validation csv at {validation_csv_path}")
    summary = load_json(summary_path)
    if not isinstance(summary, dict):
        raise ValueError(f"Invalid smoke validation summary payload at {summary_path}")
    overall = summary.get("overall") or {}
    total = int(overall.get("total", 0))
    correct = int(overall.get("correct", 0))
    accuracy = float(overall.get("accuracy", 0.0))
    validation_frame = pd.read_csv(validation_csv_path)
    if "predicted" not in validation_frame.columns:
        raise ValueError(f"Smoke validation csv is missing predicted column: {validation_csv_path}")
    normalized_predictions = [
        normalize_smoke_prediction_text(value)
        for value in validation_frame["predicted"].fillna("").tolist()
    ]
    nonempty_predictions = [value for value in normalized_predictions if value]
    distinct_predictions = sorted(set(nonempty_predictions))
    prediction_counts = Counter(nonempty_predictions)
    top_prediction = ""
    top_prediction_count = 0
    if prediction_counts:
        top_prediction, top_prediction_count = max(prediction_counts.items(), key=lambda item: (item[1], item[0]))
    min_nonempty_required = max(1, math.ceil(max(1, total) * 0.5))
    min_distinct_required = 1 if total <= 1 else 2
    failures: list[str] = []
    if total <= 0:
        failures.append("no_rows_scored")
    if len(validation_frame.index) != total:
        failures.append(f"csv_row_mismatch:{len(validation_frame.index)}!={total}")
    if len(nonempty_predictions) < min_nonempty_required:
        failures.append(f"too_many_empty_predictions:{len(nonempty_predictions)}<{min_nonempty_required}")
    if len(distinct_predictions) < min_distinct_required:
        failures.append(f"insufficient_prediction_diversity:{len(distinct_predictions)}<{min_distinct_required}")
    if total > 1 and top_prediction_count >= total:
        failures.append("single_prediction_repeated_for_all_rows")
    status = "pass" if not failures else "fail"
    return {
        "created_at": utc_now(),
        "status": status,
        "proceed": status == "pass",
        "validation_root": str(validation_root.resolve()),
        "validation_summary_path": str(summary_path.resolve()),
        "validation_csv_path": str(validation_csv_path.resolve()),
        "overall": {
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
        },
        "prediction_stats": {
            "nonempty_predictions": len(nonempty_predictions),
            "empty_predictions": total - len(nonempty_predictions),
            "distinct_predictions": len(distinct_predictions),
            "top_prediction": top_prediction,
            "top_prediction_count": top_prediction_count,
        },
        "failures": failures,
    }


def write_smoke_validation_gate_artifacts(validation_root: Path, gate_result: dict[str, Any]) -> None:
    gate_json_path = validation_root / "smoke_gate.json"
    gate_md_path = validation_root / "smoke_gate.md"
    write_json(gate_json_path, gate_result)
    overall = gate_result.get("overall") or {}
    prediction_stats = gate_result.get("prediction_stats") or {}
    lines = ["# smoke_gate", ""]
    lines.append(f"- status: `{gate_result.get('status', '')}`")
    lines.append(f"- proceed_to_full_validation: `{bool(gate_result.get('proceed', False))}`")
    lines.append(
        f"- overall_accuracy: `{float(overall.get('accuracy', 0.0)):.6f}` "
        f"({int(overall.get('correct', 0))}/{int(overall.get('total', 0))})"
    )
    lines.append(
        "- prediction_health: "
        f"nonempty={int(prediction_stats.get('nonempty_predictions', 0))}, "
        f"empty={int(prediction_stats.get('empty_predictions', 0))}, "
        f"distinct={int(prediction_stats.get('distinct_predictions', 0))}"
    )
    top_prediction = str(prediction_stats.get("top_prediction", ""))
    if top_prediction:
        lines.append(
            f"- dominant_prediction: `{top_prediction}` "
            f"(count={int(prediction_stats.get('top_prediction_count', 0))})"
        )
    failures = gate_result.get("failures") or []
    if failures:
        lines.append("- failures:")
        for failure in failures:
            lines.append(f"  - `{failure}`")
    write_text(gate_md_path, "\n".join(lines).strip() + "\n")


def render_validation_markdown_summary(evaluation_name: str, payload: dict[str, Any]) -> str:
    overall = payload["overall"]
    lines = [f"# {evaluation_name}", ""]
    lines.append(f"- notebook_reference: `{payload['notebook_reference']}`")
    lines.append(f"- benchmark_csv: `{payload['benchmark_csv']}`")
    lines.append(f"- model_root: `{payload['model_root']}`")
    lines.append(f"- adapter_dir: `{payload['adapter_dir']}`")
    lines.append(f"- overall_accuracy: `{overall['accuracy']}` ({overall['correct']}/{overall['total']})")
    notebook_reference_score = payload.get("notebook_reference_score")
    if isinstance(notebook_reference_score, dict) and notebook_reference_score:
        lines.append(
            "- notebook_reference_accuracy: "
            f"`{notebook_reference_score['overall_accuracy']}` "
            f"({notebook_reference_score['overall_correct']}/{notebook_reference_score['overall_total']})"
        )
        lines.append(
            f"- delta_vs_notebook_reference: "
            f"`{round(float(overall['accuracy']) - float(notebook_reference_score['overall_accuracy']), 6)}`"
        )
    evaluation_settings = payload.get("evaluation_settings")
    if isinstance(evaluation_settings, dict) and evaluation_settings:
        lines.append(f"- max_tokens: `{evaluation_settings.get('max_tokens', '')}`")
        lines.append(f"- max_num_seqs: `{evaluation_settings.get('max_num_seqs', '')}`")
        lines.append(f"- prompt_chunk_size: `{evaluation_settings.get('prompt_chunk_size', '')}`")
        lines.append(f"- prefill_batch_size: `{evaluation_settings.get('prefill_batch_size', '')}`")
        lines.append(f"- completion_batch_size: `{evaluation_settings.get('completion_batch_size', '')}`")
        lines.append(f"- eval_enable_thinking: `{evaluation_settings.get('eval_enable_thinking', '')}`")
    prompt_policy = payload.get("prompt_policy")
    if isinstance(prompt_policy, dict) and prompt_policy:
        lines.append(f"- append_boxed_instruction: `{prompt_policy.get('append_boxed_instruction', '')}`")
    lines.append("")
    lines.append("| category | correct | total | accuracy | weightage | percentage | contribution |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["categories"]:
        lines.append(
            f"| {row['category']} | {row['correct']} | {row['total']} | {float(row['accuracy']):.6f} | "
            f"{row['weightage']} | {row['percentage']} | {row['contribution']} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_validation_outputs(
    *,
    output_root: Path,
    evaluation_name: str,
    validation_frame: pd.DataFrame,
    results_frame: pd.DataFrame,
    payload: dict[str, Any],
) -> None:
    ensure_dir(output_root)
    validation_frame.to_csv(output_root / "validation.csv", index=False)
    results_frame.to_csv(output_root / "results.csv")
    mistakes_root = output_root / "mistakes"
    if mistakes_root.exists():
        shutil.rmtree(mistakes_root)
    mistakes_root.mkdir(parents=True, exist_ok=True)
    if not validation_frame.empty:
        for category in validation_frame["category"].unique():
            category_mistakes = validation_frame[
                (validation_frame["category"] == category) & (~validation_frame["correct"])
            ]
            if not category_mistakes.empty:
                category_mistakes.to_csv(mistakes_root / f"{category}.csv", index=False)
    write_json(output_root / "validation_summary.json", payload)
    write_text(output_root / "validation_summary.md", render_validation_markdown_summary(evaluation_name, payload))


def build_scored_rows(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    scored_rows: list[dict[str, Any]] = []
    for row in records:
        scored_rows.append(
            {
                "id": row["id"],
                "category": row["category"],
                "gold_answer": row["expected_answer"],
                "prediction": row["extracted_answer"],
                "is_correct": bool(row["is_correct"]),
                "fallback_type": row["fallback_type"],
                "format_bucket": row["format_bucket"],
                "has_boxed": row["has_boxed"],
                "boxed_count": row["boxed_count"],
                "raw_output": row["raw_output"],
            }
        )
    return scored_rows


def build_eval_settings_payload(
    args: argparse.Namespace,
    *,
    eval_shards: int,
    eval_shard_index: int,
    chunk_size: int,
    prefill_batch_size: int,
    completion_batch_size: int,
) -> dict[str, Any]:
    payload = {
        "max_tokens": int(args.max_tokens),
        "temperature": float(args.temperature),
        "top_p": float(args.top_p),
        "max_num_seqs": max(1, int(args.max_num_seqs)),
        "prompt_chunk_size": int(chunk_size),
        "prefill_batch_size": int(prefill_batch_size),
        "completion_batch_size": int(completion_batch_size),
        "eval_enable_thinking": bool(args.eval_enable_thinking),
        "lazy_load": bool(args.lazy_load),
        "force_single_generate": bool(args.force_single_generate),
        "eval_row_timeout_seconds": max(0, int(args.eval_row_timeout_seconds)),
        "eval_shards": int(eval_shards),
        "eval_shard_index": int(eval_shard_index),
    }
    validation_subset_size = int(getattr(args, "validation_subset_size", 0))
    if validation_subset_size > 0:
        payload["validation_subset_size"] = validation_subset_size
        payload["validation_subset_mode"] = str(
            getattr(args, "validation_subset_mode", "stratified-category-proportional")
        )
    return payload


def summarize_benchmark_scores(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    correct = sum(int(bool(row.get("is_correct"))) for row in rows)
    total = len(rows)
    by_category: dict[str, dict[str, int]] = {}
    for row in rows:
        category = str(row.get("category", ""))
        bucket = by_category.setdefault(category, {"correct": 0, "total": 0})
        bucket["total"] += 1
        bucket["correct"] += int(bool(row.get("is_correct")))
    category_rows = []
    for category, stats in sorted(by_category.items()):
        category_rows.append(
            {
                "category": category,
                "correct": stats["correct"],
                "total": stats["total"],
                "accuracy": round(stats["correct"] / stats["total"], 6) if stats["total"] else 0.0,
            }
        )
    return {
        "overall": {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
        },
        "categories": category_rows,
    }


def render_eval_markdown_summary(evaluation_name: str, payload: dict[str, Any]) -> str:
    overall = payload["overall"]
    lines = [f"# {evaluation_name}", ""]
    lines.append(f"- model_root: `{payload['model_root']}`")
    lines.append(f"- adapter_dir: `{payload['adapter_dir']}`")
    lines.append(f"- overall_accuracy: `{overall['accuracy']}` ({overall['correct']}/{overall['total']})")
    evaluation_settings = payload.get("evaluation_settings")
    if isinstance(evaluation_settings, dict) and evaluation_settings:
        lines.append(f"- max_tokens: `{evaluation_settings.get('max_tokens', '')}`")
        lines.append(f"- max_num_seqs: `{evaluation_settings.get('max_num_seqs', '')}`")
        lines.append(f"- prompt_chunk_size: `{evaluation_settings.get('prompt_chunk_size', '')}`")
        lines.append(f"- prefill_batch_size: `{evaluation_settings.get('prefill_batch_size', '')}`")
        lines.append(f"- completion_batch_size: `{evaluation_settings.get('completion_batch_size', '')}`")
        lines.append(f"- eval_enable_thinking: `{evaluation_settings.get('eval_enable_thinking', '')}`")
    lines.append("")
    lines.append("| category | correct | total | accuracy |")
    lines.append("| --- | ---: | ---: | ---: |")
    for row in payload["categories"]:
        lines.append(f"| {row['category']} | {row['correct']} | {row['total']} | {row['accuracy']:.6f} |")
    lines.append("")
    return "\n".join(lines)


def write_eval_outputs(
    *,
    output_root: Path,
    evaluation_name: str,
    records: Sequence[dict[str, Any]],
    scored_rows: Sequence[dict[str, Any]],
    payload: dict[str, Any],
) -> None:
    ensure_dir(output_root)
    pd.DataFrame.from_records(records).to_csv(output_root / "benchmark_eval_raw_outputs.csv", index=False)
    pd.DataFrame.from_records(scored_rows).to_csv(output_root / "benchmark_eval_row_level.csv", index=False)
    write_json(output_root / "benchmark_eval_summary.json", payload)
    write_text(output_root / "benchmark_eval_summary.md", render_eval_markdown_summary(evaluation_name, payload))


def load_eval_checkpoint_records(checkpoint_path: Path) -> list[dict[str, Any]]:
    if not checkpoint_path.exists():
        return []
    frame = pd.read_csv(
        checkpoint_path,
        keep_default_na=False,
        converters={
            "is_correct": lambda value: str(value).strip().lower() in {"true", "1", "1.0"},
            "has_boxed": lambda value: str(value).strip().lower() in {"true", "1", "1.0"},
            "boxed_count": lambda value: int(float(value)) if str(value).strip() else 0,
        },
    )
    records = frame.to_dict(orient="records")
    for record in records:
        record["id"] = str(record.get("id", ""))
        record["category"] = str(record.get("category", ""))
        record["expected_answer"] = str(record.get("expected_answer", ""))
        record["rendered_prompt"] = str(record.get("rendered_prompt", ""))
        record["raw_output"] = str(record.get("raw_output", ""))
        record["extracted_answer"] = str(record.get("extracted_answer", ""))
        record["fallback_type"] = str(record.get("fallback_type", ""))
        record["format_bucket"] = str(record.get("format_bucket", ""))
        record["is_correct"] = bool(record.get("is_correct", False))
        record["has_boxed"] = bool(record.get("has_boxed", False))
        record["boxed_count"] = int(record.get("boxed_count", 0))
    return records


def append_eval_checkpoint_records(checkpoint_path: Path, records: Sequence[dict[str, Any]]) -> None:
    if not records:
        return
    ensure_dir(checkpoint_path.parent)
    pd.DataFrame.from_records(records, columns=EVAL_RECORD_COLUMNS).to_csv(
        checkpoint_path,
        mode="a",
        header=not checkpoint_path.exists(),
        index=False,
    )


def run_train(args: argparse.Namespace) -> dict[str, Any]:
    artifacts = prepare_run(args)
    step_plan = load_step_plan(artifacts.step_plan_path)
    if not step_plan:
        raise RuntimeError("Empty step plan.")
    if int(args.save_every_steps) > 0 and int(args.max_saved_checkpoints) < 1:
        raise ValueError("--max-saved-checkpoints must be >= 1 when --save-every-steps is enabled")
    total_optimizer_steps = len(step_plan)
    run_limit = int(args.max_optimizer_steps) if int(args.max_optimizer_steps) > 0 else total_optimizer_steps
    step_plan = step_plan[:run_limit]
    total_optimizer_steps = len(step_plan)

    write_json(artifacts.run_root / "runtime_preflight.json", collect_runtime_preflight())

    print("Loading pretrained model")
    model, tokenizer = mlx_load(
        str(artifacts.shadow_model_dir),
        tokenizer_config={"trust_remote_code": True},
    )
    normalize_tokenizer_for_hf_parity(tokenizer)

    print("Configuring LoRA layers")
    model.freeze()
    linear_to_lora_layers(
        model,
        -1,
        {
            "rank": int(args.lora_rank),
            "dropout": float(args.lora_dropout),
            "scale": float(args.lora_alpha),
            "keys": list(default_lora_keys()),
        },
    )
    lora_match_summary = summarize_lora_matches(model)
    print_lora_match_summary(lora_match_summary)
    assert_lora_match_summary(lora_match_summary)
    if args.resume_adapter_file:
        resume_path = Path(args.resume_adapter_file).resolve()
        print(f"Loading fine-tuned weights from {resume_path}")
        model.load_weights(str(resume_path), strict=False)
    print_trainable_parameters(model)

    adapter_config = create_adapter_config_payload(
        shadow_model_dir=artifacts.shadow_model_dir,
        adapter_dir=artifacts.adapter_dir,
        args=args,
        total_steps=total_optimizer_steps,
    )
    ensure_dir(artifacts.adapter_dir)
    save_config(adapter_config, artifacts.adapter_dir / "adapter_config.json")
    write_json(artifacts.run_root / "lora_match_summary.json", lora_match_summary)

    schedule = build_v20_lr_schedule(total_optimizer_steps, float(args.learning_rate))
    optimizer = optim.Adam(
        learning_rate=schedule,
        betas=[float(args.beta1), float(args.beta2)],
        eps=float(args.eps),
        bias_correction=bool(args.bias_correction),
    )
    print("optimizer_kind: adam")

    if mx.metal.is_available():
        mx.set_wired_limit(mx.device_info()["max_recommended_working_set_size"])

    loss_value_and_grad = nn.value_and_grad(model, default_loss)
    state = [model.state, optimizer.state, mx.random.state]

    @partial(mx.compile, inputs=state, outputs=state)
    def micro_step(
        batch: mx.array,
        lengths: mx.array,
        prev_grad: Any,
        do_update: bool,
        grad_divisor: int,
    ) -> tuple[mx.array, mx.array, Any]:
        (loss_value, token_count), grad = loss_value_and_grad(model, batch, lengths)
        if prev_grad is not None:
            grad = tree_map(lambda left, right: left + right, grad, prev_grad)
        if do_update:
            grad = average_gradients(grad)
            if grad_divisor > 1:
                grad = tree_map(lambda value: value / grad_divisor, grad)
            optimizer.update(model, grad)
            grad = None
        return loss_value, token_count, grad

    train_report_jsonl = artifacts.train_report_jsonl
    latest_train_report_path = artifacts.latest_train_report_path
    if train_report_jsonl.exists():
        train_report_jsonl.unlink()
    if latest_train_report_path.exists():
        latest_train_report_path.unlink()

    model.train()
    trained_tokens = 0
    started_at = time.perf_counter()
    last_report: dict[str, Any] | None = None

    for optimizer_step_index, step in enumerate(step_plan):
        step_started_at = time.perf_counter()
        microbatches = chunk_examples(step.examples, int(args.micro_batch_size))
        step_status_report = {
            "observed_at": utc_now(),
            "status": "step_started",
            "step": optimizer_step_index + 1,
            "step_zero_indexed": optimizer_step_index,
            "v20_snapshot_step": int(step.step),
            "examples_in_step": len(step.examples),
            "microbatch_index": 0,
            "microbatches_in_step": len(microbatches),
            "trained_tokens": trained_tokens,
            "total_elapsed_seconds": round(time.perf_counter() - started_at, 4),
        }
        write_json(latest_train_report_path, step_status_report)
        print(
            f"Step {optimizer_step_index + 1}/{total_optimizer_steps}: "
            f"started microbatches={len(microbatches)} snapshot_step={int(step.step)}",
            flush=True,
        )
        grad_accum = None
        weighted_loss_total = 0.0
        token_total = 0

        for microbatch_index, micro_examples in enumerate(microbatches):
            write_json(
                latest_train_report_path,
                {
                    "observed_at": utc_now(),
                    "status": "running_microbatch",
                    "step": optimizer_step_index + 1,
                    "step_zero_indexed": optimizer_step_index,
                    "v20_snapshot_step": int(step.step),
                    "examples_in_step": len(step.examples),
                    "microbatch_index": microbatch_index + 1,
                    "microbatches_in_step": len(microbatches),
                    "trained_tokens": trained_tokens + token_total,
                    "step_tokens_so_far": token_total,
                    "total_elapsed_seconds": round(time.perf_counter() - started_at, 4),
                },
            )
            batch_array, lengths_array = build_microbatch_arrays(
                micro_examples,
                micro_batch_size=int(args.micro_batch_size),
                max_seq_length=int(args.max_seq_length),
                fixed_train_padding=bool(args.fixed_train_padding),
            )
            loss_value, token_count, grad_accum = micro_step(
                batch_array,
                lengths_array,
                grad_accum,
                microbatch_index == len(microbatches) - 1,
                len(microbatches),
            )
            mx.eval(state, grad_accum, loss_value, token_count)
            loss_scalar = float(loss_value.item())
            token_scalar = int(token_count.item())
            weighted_loss_total += loss_scalar * token_scalar
            token_total += token_scalar

        trained_tokens += token_total
        elapsed = time.perf_counter() - step_started_at
        lr = v20_step_lr(optimizer_step_index, total_optimizer_steps, float(args.learning_rate))
        report = {
            "observed_at": utc_now(),
            "status": "step_complete",
            "step": optimizer_step_index + 1,
            "step_zero_indexed": optimizer_step_index,
            "v20_snapshot_step": int(step.step),
            "examples_in_step": len(step.examples),
            "microbatches_in_step": len(microbatches),
            "train_loss": (weighted_loss_total / token_total) if token_total else 0.0,
            "step_tokens": token_total,
            "trained_tokens": trained_tokens,
            "lr": lr,
            "elapsed_seconds": round(elapsed, 4),
            "total_elapsed_seconds": round(time.perf_counter() - started_at, 4),
            "peak_memory_gb": round(mx.get_peak_memory() / 1e9, 4),
        }
        append_jsonl(train_report_jsonl, report)
        write_json(latest_train_report_path, report)
        last_report = report
        print(
            f"Step {optimizer_step_index + 1}/{total_optimizer_steps}: "
            f"loss={report['train_loss']:.6f} lr={lr:.8f} "
            f"tokens={token_total} elapsed={elapsed:.2f}s",
            flush=True,
        )

        if int(args.save_every_steps) > 0 and (optimizer_step_index + 1) % int(args.save_every_steps) == 0:
            save_adapter_weights(artifacts.adapter_dir, f"{optimizer_step_index + 1:07d}_adapters.safetensors", model)
            prune_saved_checkpoints(
                artifacts.adapter_dir,
                max_saved_checkpoints=int(args.max_saved_checkpoints),
            )

    final_adapter_path = save_adapter_weights(artifacts.adapter_dir, "adapters.safetensors", model)
    bundle_manifest = build_local_mlx_bundle(artifacts.run_root, artifacts.adapter_dir)
    training_result = {
        "created_at": utc_now(),
        "run_root": str(artifacts.run_root),
        "shadow_model_dir": str(artifacts.shadow_model_dir),
        "adapter_dir": str(artifacts.adapter_dir),
        "adapter_files": summarize_directory(artifacts.adapter_dir),
        "final_adapter_path": str(final_adapter_path),
        "runtime_preflight_path": str((artifacts.run_root / "runtime_preflight.json").resolve()),
        "latest_train_report": last_report,
        "run_manifest_path": str(artifacts.config_path.resolve()),
        "snapshot_contract_path": str(artifacts.snapshot_contract_path.resolve()),
        "step_plan_path": str(artifacts.step_plan_path.resolve()),
        "train_cmd_path": str((artifacts.run_root / "train_cmd.sh").resolve()),
        "mlx_bundle": bundle_manifest,
    }
    write_json(artifacts.training_result_path, training_result)
    write_text(artifacts.run_root / "training_result.md", render_train_markdown_summary(training_result))
    return training_result


def load_model_for_eval(model_root: Path, adapter_dir: Path | None, *, lazy_load: bool) -> tuple[Any, Any]:
    load_kwargs: dict[str, Any] = {"lazy": bool(lazy_load)}
    if adapter_dir is not None:
        load_kwargs["adapter_path"] = str(adapter_dir.resolve())
    model, tokenizer = mlx_load(str(model_root.resolve()), **load_kwargs)
    normalize_tokenizer_for_hf_parity(tokenizer)
    return model, tokenizer


def run_eval_aopen(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    training_result_path = run_root / "training_result.json"
    if not training_result_path.exists():
        raise FileNotFoundError(f"Missing training_result.json at {training_result_path}")
    training_result = load_json(training_result_path)
    model_root = Path(training_result["shadow_model_dir"]).resolve()
    adapter_dir = Path(training_result["adapter_dir"]).resolve()
    eval_shards = max(1, int(args.eval_shards))
    eval_shard_index = int(args.eval_shard_index)
    if eval_shards == 1 and eval_shard_index != 0:
        raise ValueError("--eval-shard-index must be 0 when --eval-shards=1")
    eval_root = resolve_eval_root(run_root, shard_count=eval_shards, shard_index=eval_shard_index)
    progress_path = eval_root / "benchmark_eval_progress.json"
    summary_path = eval_root / "benchmark_eval_summary.json"
    checkpoint_path = eval_root / "benchmark_eval_records_checkpoint.csv"
    ensure_dir(eval_root)
    if summary_path.exists() and progress_path.exists():
        progress_payload = load_json(progress_path)
        if progress_payload.get("status") == "complete":
            return load_json(summary_path)
    model, tokenizer = load_model_for_eval(model_root, adapter_dir, lazy_load=bool(args.lazy_load))

    benchmark_rows = load_training_rows()
    if int(args.eval_limit) > 0:
        benchmark_rows = benchmark_rows[: int(args.eval_limit)]
    total_benchmark_rows = len(benchmark_rows)
    row_start, row_end = compute_eval_slice(total_benchmark_rows, eval_shards, eval_shard_index)
    benchmark_rows = benchmark_rows[row_start:row_end]
    category_map = load_category_map()
    prompts = build_eval_prompts(tokenizer, [row["prompt"] for row in benchmark_rows], enable_thinking=bool(args.eval_enable_thinking))
    prompt_tokens = [encode_prompt(tokenizer, prompt) for prompt in prompts]

    sampler = make_sampler(
        temp=float(args.temperature),
        top_p=float(args.top_p) if 0.0 < float(args.top_p) < 1.0 else 0.0,
    )

    max_num_seqs = max(1, int(args.max_num_seqs))
    chunk_size = min(max_num_seqs, max(1, int(args.prompt_chunk_size)))
    prefill_batch_size = min(max_num_seqs, max(1, int(args.prefill_batch_size)))
    completion_batch_size = min(max_num_seqs, max(1, int(args.completion_batch_size)))
    force_single_generate = bool(args.force_single_generate)

    total_prompts = len(prompt_tokens)
    records = load_eval_checkpoint_records(checkpoint_path)
    if len(records) > total_prompts:
        raise RuntimeError(
            f"Eval checkpoint has more rows than the benchmark: {len(records)} > {total_prompts}. "
            f"Remove {checkpoint_path} and rerun."
        )
    if records:
        if eval_shards > 1:
            print(
                f"Resuming shard {eval_shard_index + 1}/{eval_shards} eval from "
                f"{len(records)}/{total_prompts} (rows {row_start}:{row_end})"
            )
        else:
            print(f"Resuming eval from {len(records)}/{total_prompts}")

    for chunk_start in range(len(records), total_prompts, chunk_size):
        chunk_prompts = prompt_tokens[chunk_start : chunk_start + chunk_size]
        chunk_rows = benchmark_rows[chunk_start : chunk_start + len(chunk_prompts)]
        chunk_rendered_prompts = prompts[chunk_start : chunk_start + len(chunk_prompts)]
        try:
            if force_single_generate:
                raise RuntimeError("force_single_generate")
            batch_response = batch_generate(
                model,
                tokenizer,
                chunk_prompts,
                max_tokens=int(args.max_tokens),
                sampler=sampler,
                verbose=False,
                prefill_batch_size=min(prefill_batch_size, len(chunk_prompts)),
                completion_batch_size=min(completion_batch_size, len(chunk_prompts)),
            )
            chunk_outputs = list(batch_response.texts)
        except (AttributeError, RuntimeError):
            chunk_outputs = [
                generate(
                    model,
                    tokenizer,
                    prompt=prompt_tokens_single,
                    verbose=False,
                    max_tokens=int(args.max_tokens),
                    sampler=sampler,
                )
                for prompt_tokens_single in chunk_prompts
            ]

        chunk_records: list[dict[str, Any]] = []
        for row, rendered_prompt, raw_output in zip(chunk_rows, chunk_rendered_prompts, chunk_outputs):
            derived = analyze_raw_output(str(raw_output))
            prediction = str(derived["extracted_answer"])
            problem_id = str(row["id"])
            category = category_map.get(problem_id, "")
            is_correct = verify_answer(str(row["answer"]), prediction)
            chunk_records.append(
                {
                    "id": problem_id,
                    "category": category,
                    "expected_answer": str(row["answer"]),
                    "rendered_prompt": rendered_prompt,
                    "raw_output": str(raw_output),
                    "extracted_answer": prediction,
                    "is_correct": bool(is_correct),
                    "fallback_type": str(derived["fallback_type"]),
                    "format_bucket": str(derived["format_bucket"]),
                    "has_boxed": bool(derived["has_boxed"]),
                    "boxed_count": int(derived["boxed_count"]),
                }
            )
        append_eval_checkpoint_records(checkpoint_path, chunk_records)
        records.extend(chunk_records)

        rows_completed = len(records)
        progress_payload = {
            "created_at": utc_now(),
            "status": "running",
            "rows_total": total_prompts,
            "rows_completed": rows_completed,
            "rows_total_global": total_benchmark_rows,
            "row_start": row_start,
            "row_end": row_end,
            "chunk_size": chunk_size,
            "max_tokens": int(args.max_tokens),
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "max_num_seqs": int(args.max_num_seqs),
            "eval_shards": eval_shards,
            "eval_shard_index": eval_shard_index,
            "checkpoint_path": str(checkpoint_path.resolve()),
        }
        write_json(progress_path, progress_payload)
        if eval_shards > 1:
            print(
                f"Eval shard progress {eval_shard_index + 1}/{eval_shards}: "
                f"{rows_completed}/{total_prompts} (rows {row_start}:{row_end})"
            )
        else:
            print(f"Eval progress: {rows_completed}/{total_prompts}")

    scored_rows = build_scored_rows(records)
    summary = summarize_benchmark_scores(scored_rows)
    evaluation_name = (
        "aopen_train_csv_full"
        if eval_shards <= 1
        else f"aopen_train_csv_shard_{eval_shard_index:02d}_of_{eval_shards:02d}"
    )
    evaluation_settings = build_eval_settings_payload(
        args,
        eval_shards=eval_shards,
        eval_shard_index=eval_shard_index,
        chunk_size=chunk_size,
        prefill_batch_size=prefill_batch_size,
        completion_batch_size=completion_batch_size,
    )
    payload = {
        "created_at": utc_now(),
        "evaluation_kind": "aopen_eval",
        "evaluation_name": evaluation_name,
        "benchmark_csv": str(TRAIN_CSV_PATH.resolve()),
        "model_root": str(model_root),
        "adapter_dir": str(adapter_dir),
        "readme_contract": README_EVAL_CONTRACT,
        "source_documents": [
            relative_to_repo(README_PATH),
            relative_to_repo(AOPEN_ROOT / "README.md"),
            relative_to_repo(AOPEN_ROOT / "データ戦略を理解する.md"),
            relative_to_repo(AOPEN_ROOT / "学習SFTパイプライン.md"),
        ],
        "rows_total_global": total_benchmark_rows,
        "row_start": row_start,
        "row_end": row_end,
        "eval_shards": eval_shards,
        "eval_shard_index": eval_shard_index,
        "evaluation_settings": evaluation_settings,
        "v20_target_training_set_accuracy": V20_TARGETS["overall_accuracy"],
        **summary,
    }
    write_eval_outputs(
        output_root=eval_root,
        evaluation_name=evaluation_name,
        records=records,
        scored_rows=scored_rows,
        payload=payload,
    )
    if checkpoint_path.exists():
        checkpoint_path.unlink()
    write_json(
        progress_path,
        {
            "created_at": utc_now(),
            "status": "complete",
            "rows_total": total_prompts,
            "rows_completed": total_prompts,
            "rows_total_global": total_benchmark_rows,
            "row_start": row_start,
            "row_end": row_end,
            "eval_shards": eval_shards,
            "eval_shard_index": eval_shard_index,
        },
    )
    return payload


def run_eval_adapter_validation(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    training_result_path = run_root / "training_result.json"
    if not training_result_path.exists():
        raise FileNotFoundError(f"Missing training_result.json at {training_result_path}")
    training_result = load_json(training_result_path)
    model_root = Path(training_result["shadow_model_dir"]).resolve()
    adapter_dir = Path(training_result["adapter_dir"]).resolve()
    eval_shards = max(1, int(args.eval_shards))
    eval_shard_index = int(args.eval_shard_index)
    if eval_shards == 1 and eval_shard_index != 0:
        raise ValueError("--eval-shard-index must be 0 when --eval-shards=1")
    validation_root = resolve_adapter_validation_root(
        run_root,
        shard_count=eval_shards,
        shard_index=eval_shard_index,
        root_name=str(args.adapter_validation_root_name),
    )
    progress_path = validation_root / "validation_progress.json"
    summary_path = validation_root / "validation_summary.json"
    checkpoint_path = validation_root / "validation_records_checkpoint.csv"
    ensure_dir(validation_root)
    write_command_script(validation_root / "eval_cmd.sh", build_eval_adapter_validation_command_tokens(args))
    if summary_path.exists() and progress_path.exists():
        progress_payload = load_json(progress_path)
        if progress_payload.get("status") == "complete":
            return load_json(summary_path)

    model, tokenizer = load_model_for_eval(model_root, adapter_dir, lazy_load=bool(args.lazy_load))
    benchmark_rows, sample_selection = build_validation_sample_selection(
        load_training_rows(),
        validation_sample_size=int(args.validation_sample_size),
        validation_subset_size=int(args.validation_subset_size),
        validation_subset_mode=str(args.validation_subset_mode),
    )
    if int(args.eval_limit) > 0:
        benchmark_rows = benchmark_rows[: int(args.eval_limit)]
    total_benchmark_rows = len(benchmark_rows)
    row_start, row_end = compute_eval_slice(total_benchmark_rows, eval_shards, eval_shard_index)
    benchmark_rows = benchmark_rows[row_start:row_end]
    prompts = build_eval_prompts(
        tokenizer,
        [row["prompt"] for row in benchmark_rows],
        enable_thinking=bool(args.eval_enable_thinking),
        include_boxed_instruction=False,
    )
    prompt_tokens = [encode_prompt(tokenizer, prompt) for prompt in prompts]

    sampler = make_sampler(
        temp=float(args.temperature),
        top_p=float(args.top_p) if 0.0 < float(args.top_p) < 1.0 else 0.0,
    )

    max_num_seqs = max(1, int(args.max_num_seqs))
    chunk_size = min(max_num_seqs, max(1, int(args.prompt_chunk_size)))
    prefill_batch_size = min(max_num_seqs, max(1, int(args.prefill_batch_size)))
    completion_batch_size = min(max_num_seqs, max(1, int(args.completion_batch_size)))
    force_single_generate = bool(args.force_single_generate)

    total_prompts = len(prompt_tokens)
    records = load_validation_records_csv(checkpoint_path)
    if len(records) > total_prompts:
        raise RuntimeError(
            f"Validation checkpoint has more rows than the benchmark: {len(records)} > {total_prompts}. "
            f"Remove {checkpoint_path} and rerun."
        )
    records_by_index: dict[int, dict[str, Any]] = {}
    for record in records:
        row_index_within_shard = int(record["row_index_within_shard"])
        if row_index_within_shard in records_by_index:
            raise RuntimeError(
                f"Duplicate row_index_within_shard={row_index_within_shard} in {checkpoint_path}. "
                f"Remove {checkpoint_path} and rerun."
            )
        records_by_index[row_index_within_shard] = record
    if checkpoint_path.exists():
        rewrite_validation_checkpoint_records(checkpoint_path, records_by_index.values())
    if records:
        if eval_shards > 1:
            print(
                f"Resuming adapter validation shard {eval_shard_index + 1}/{eval_shards} from "
                f"{len(records)}/{total_prompts} (rows {row_start}:{row_end})"
            )
        else:
            print(f"Resuming adapter validation from {len(records)}/{total_prompts}")
    pending_items = [
        (row_index_within_shard, benchmark_rows[row_index_within_shard], prompt_tokens[row_index_within_shard])
        for row_index_within_shard in range(total_prompts)
        if row_index_within_shard not in records_by_index
    ]

    def record_validation_completion(
        row_index_within_shard: int,
        row: dict[str, str],
        raw_output: str,
        min_logprob: float | None,
    ) -> None:
        prediction = extract_final_answer(str(raw_output))
        category = detect_validation_category(str(row["prompt"]))
        correct = verify_answer(str(row["answer"]), prediction)
        record = {
            "row_index_within_shard": int(row_index_within_shard),
            "id": str(row["id"]),
            "prompt": str(row["prompt"]),
            "answer": str(row["answer"]),
            "output": str(raw_output),
            "category": category,
            "predicted": prediction,
            "correct": bool(correct),
            "minlogprob": min_logprob,
        }
        append_validation_checkpoint_records(checkpoint_path, [record])
        records_by_index[int(row_index_within_shard)] = record

        rows_completed = len(records_by_index)
        progress_payload = {
            "created_at": utc_now(),
            "status": "running",
            "evaluation_kind": "adapter_validation",
            "rows_total": total_prompts,
            "rows_completed": rows_completed,
            "rows_total_global": total_benchmark_rows,
            "row_start": row_start,
            "row_end": row_end,
            "validation_sample_size": int(args.validation_sample_size),
            "chunk_size": chunk_size,
            "max_tokens": int(args.max_tokens),
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "max_num_seqs": int(args.max_num_seqs),
            "eval_shards": eval_shards,
            "eval_shard_index": eval_shard_index,
            "checkpoint_path": str(checkpoint_path.resolve()),
            "sample_selection": sample_selection,
        }
        write_json(progress_path, progress_payload)
        if eval_shards > 1:
            print(
                f"Adapter validation shard progress {eval_shard_index + 1}/{eval_shards}: "
                f"{rows_completed}/{total_prompts} (rows {row_start}:{row_end})"
            )
        else:
            print(f"Adapter validation progress: {rows_completed}/{total_prompts}")

    for chunk_start in range(0, len(pending_items), chunk_size):
        chunk_items = pending_items[chunk_start : chunk_start + chunk_size]
        chunk_indices = [item[0] for item in chunk_items]
        chunk_rows = [item[1] for item in chunk_items]
        chunk_prompt_tokens = [item[2] for item in chunk_items]
        if force_single_generate:
            for chunk_index, row, prompt_tokens_single in zip(chunk_indices, chunk_rows, chunk_prompt_tokens):
                raw_output, min_logprob = generate_single_with_min_logprob(
                    model,
                    tokenizer,
                    prompt_tokens_single,
                    max_tokens=int(args.max_tokens),
                    sampler=sampler,
                    row_timeout_seconds=int(args.eval_row_timeout_seconds),
                )
                record_validation_completion(chunk_index, row, raw_output, min_logprob)
        else:
            try:
                for output_index, raw_output, min_logprob in iter_batch_generate_with_min_logprobs(
                    model,
                    tokenizer,
                    chunk_prompt_tokens,
                    max_tokens=int(args.max_tokens),
                    sampler=sampler,
                    prefill_batch_size=min(prefill_batch_size, len(chunk_prompt_tokens)),
                    completion_batch_size=min(completion_batch_size, len(chunk_prompt_tokens)),
                ):
                    record_validation_completion(
                        chunk_indices[output_index],
                        chunk_rows[output_index],
                        raw_output,
                        min_logprob,
                    )
            except (AttributeError, RuntimeError):
                for chunk_index, row, prompt_tokens_single in zip(chunk_indices, chunk_rows, chunk_prompt_tokens):
                    raw_output, min_logprob = generate_single_with_min_logprob(
                        model,
                        tokenizer,
                        prompt_tokens_single,
                        max_tokens=int(args.max_tokens),
                        sampler=sampler,
                        row_timeout_seconds=int(args.eval_row_timeout_seconds),
                    )
                    record_validation_completion(chunk_index, row, raw_output, min_logprob)

    records = sort_validation_records(records_by_index.values())
    validation_frame = build_validation_output_frame(records)
    results_frame = build_validation_results_table(validation_frame)
    summary = summarize_validation_results(results_frame)
    evaluation_name = build_adapter_validation_evaluation_name(
        sample_selection,
        total_rows_global=total_benchmark_rows,
        eval_shards=eval_shards,
        eval_shard_index=eval_shard_index,
    )
    evaluation_settings = build_eval_settings_payload(
        args,
        eval_shards=eval_shards,
        eval_shard_index=eval_shard_index,
        chunk_size=chunk_size,
        prefill_batch_size=prefill_batch_size,
        completion_batch_size=completion_batch_size,
    )
    notebook_reference_score = (
        ADAPTER_VALIDATION_NOTEBOOK_TARGET
        if (
            eval_shards <= 1
            and row_start == 0
            and row_end == total_benchmark_rows
            and total_benchmark_rows == ADAPTER_VALIDATION_SAMPLE_SIZE
            and str(sample_selection.get("mode", "")) == "head"
        )
        else None
    )
    payload = {
        "created_at": utc_now(),
        "evaluation_kind": "adapter_validation",
        "evaluation_name": evaluation_name,
        "benchmark_csv": str(TRAIN_CSV_PATH.resolve()),
        "notebook_reference": relative_to_repo(ADAPTER_VALIDATION_NOTEBOOK_PATH),
        "model_root": str(model_root),
        "adapter_dir": str(adapter_dir),
        "readme_contract": README_EVAL_CONTRACT,
        "source_documents": [
            relative_to_repo(README_PATH),
            relative_to_repo(AOPEN_ROOT / "README.md"),
            relative_to_repo(AOPEN_ROOT / "データ戦略を理解する.md"),
            relative_to_repo(AOPEN_ROOT / "学習SFTパイプライン.md"),
            relative_to_repo(ADAPTER_VALIDATION_NOTEBOOK_PATH),
        ],
        "validation_sample_size": int(args.validation_sample_size),
        "sample_selection": sample_selection,
        "rows_total_global": total_benchmark_rows,
        "row_start": row_start,
        "row_end": row_end,
        "eval_shards": eval_shards,
        "eval_shard_index": eval_shard_index,
        "evaluation_settings": evaluation_settings,
        "prompt_policy": {
            "append_boxed_instruction": False,
            "enable_thinking": bool(args.eval_enable_thinking),
        },
        "notebook_reference_score": notebook_reference_score,
        **summary,
    }
    write_validation_outputs(
        output_root=validation_root,
        evaluation_name=evaluation_name,
        validation_frame=validation_frame,
        results_frame=results_frame,
        payload=payload,
    )
    if checkpoint_path.exists():
        checkpoint_path.unlink()
    write_json(
        progress_path,
        {
            "created_at": utc_now(),
            "status": "complete",
            "evaluation_kind": "adapter_validation",
            "rows_total": total_prompts,
            "rows_completed": total_prompts,
            "rows_total_global": total_benchmark_rows,
            "row_start": row_start,
            "row_end": row_end,
            "eval_shards": eval_shards,
            "eval_shard_index": eval_shard_index,
            "sample_selection": sample_selection,
        },
    )
    return payload


def run_merge_aopen_eval(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    training_result_path = run_root / "training_result.json"
    if not training_result_path.exists():
        raise FileNotFoundError(f"Missing training_result.json at {training_result_path}")
    training_result = load_json(training_result_path)
    model_root = Path(training_result["shadow_model_dir"]).resolve()
    adapter_dir = Path(training_result["adapter_dir"]).resolve()
    base_eval_root = run_root / "aopen_eval"
    shard_root = base_eval_root / "shards"
    if not shard_root.exists():
        raise FileNotFoundError(f"Missing shard eval directory at {shard_root}")

    shard_entries: list[tuple[Path, dict[str, Any]]] = []
    for summary_path in sorted(shard_root.glob("*/benchmark_eval_summary.json")):
        shard_entries.append((summary_path.parent, load_json(summary_path)))
    if not shard_entries:
        raise FileNotFoundError(f"No shard benchmark_eval_summary.json files found under {shard_root}")

    shard_entries.sort(key=lambda entry: (int(entry[1].get("row_start", 0)), entry[0].name))
    expected_shards = int(shard_entries[0][1].get("eval_shards", len(shard_entries)))
    if expected_shards <= 1:
        raise RuntimeError("Shard merge requires eval_shards > 1 in shard summaries.")
    if len(shard_entries) != expected_shards:
        raise RuntimeError(f"Expected {expected_shards} shard summaries, found {len(shard_entries)} under {shard_root}")

    total_rows_global = int(shard_entries[0][1].get("rows_total_global", 0))
    sample_selection = shard_entries[0][1].get(
        "sample_selection",
        {
            "mode": "head",
            "selection_tag": f"head_{total_rows_global}",
            "source_total": int(args.validation_sample_size),
            "selected_total": total_rows_global,
        },
    )
    next_row_start = 0
    records: list[dict[str, Any]] = []
    for expected_index, (shard_dir, payload) in enumerate(shard_entries):
        shard_index = int(payload.get("eval_shard_index", -1))
        row_start = int(payload.get("row_start", -1))
        row_end = int(payload.get("row_end", -1))
        shard_total = int(payload.get("overall", {}).get("total", -1))
        shard_rows_total_global = int(payload.get("rows_total_global", total_rows_global))
        if shard_index != expected_index:
            raise RuntimeError(f"Expected shard index {expected_index}, found {shard_index} in {shard_dir}")
        if shard_rows_total_global != total_rows_global:
            raise RuntimeError(
                f"Global row count mismatch for {shard_dir}: {shard_rows_total_global} != {total_rows_global}"
            )
        if row_start != next_row_start:
            raise RuntimeError(f"Shard coverage gap or overlap before {shard_dir}: expected {next_row_start}, found {row_start}")
        if row_end < row_start:
            raise RuntimeError(f"Invalid shard row range in {shard_dir}: {row_start}:{row_end}")
        shard_records = load_eval_checkpoint_records(shard_dir / "benchmark_eval_raw_outputs.csv")
        if len(shard_records) != shard_total or len(shard_records) != (row_end - row_start):
            raise RuntimeError(
                f"Shard row mismatch in {shard_dir}: raw_outputs={len(shard_records)} summary_total={shard_total} "
                f"row_span={row_end - row_start}"
            )
        records.extend(shard_records)
        next_row_start = row_end

    if next_row_start != total_rows_global:
        raise RuntimeError(f"Shard coverage incomplete: merged {next_row_start} rows, expected {total_rows_global}")

    scored_rows = build_scored_rows(records)
    summary = summarize_benchmark_scores(scored_rows)
    max_num_seqs = max(1, int(args.max_num_seqs))
    chunk_size = min(max_num_seqs, max(1, int(args.prompt_chunk_size)))
    prefill_batch_size = min(max_num_seqs, max(1, int(args.prefill_batch_size)))
    completion_batch_size = min(max_num_seqs, max(1, int(args.completion_batch_size)))
    evaluation_settings = build_eval_settings_payload(
        args,
        eval_shards=expected_shards,
        eval_shard_index=-1,
        chunk_size=chunk_size,
        prefill_batch_size=prefill_batch_size,
        completion_batch_size=completion_batch_size,
    )
    payload = {
        "created_at": utc_now(),
        "evaluation_kind": "aopen_eval",
        "evaluation_name": "aopen_train_csv_full",
        "benchmark_csv": str(TRAIN_CSV_PATH.resolve()),
        "model_root": str(model_root),
        "adapter_dir": str(adapter_dir),
        "readme_contract": README_EVAL_CONTRACT,
        "source_documents": [
            relative_to_repo(README_PATH),
            relative_to_repo(AOPEN_ROOT / "README.md"),
            relative_to_repo(AOPEN_ROOT / "データ戦略を理解する.md"),
            relative_to_repo(AOPEN_ROOT / "学習SFTパイプライン.md"),
        ],
        "rows_total_global": total_rows_global,
        "row_start": 0,
        "row_end": total_rows_global,
        "eval_shards": expected_shards,
        "eval_shard_index": -1,
        "evaluation_settings": evaluation_settings,
        "aggregation": {
            "mode": "sharded",
            "shard_root": str(shard_root.resolve()),
            "num_shards": expected_shards,
        },
        "v20_target_training_set_accuracy": V20_TARGETS["overall_accuracy"],
        **summary,
    }
    write_eval_outputs(
        output_root=base_eval_root,
        evaluation_name="aopen_train_csv_full",
        records=records,
        scored_rows=scored_rows,
        payload=payload,
    )
    write_json(
        base_eval_root / "benchmark_eval_progress.json",
        {
            "created_at": utc_now(),
            "status": "complete",
            "rows_total": total_rows_global,
            "rows_completed": total_rows_global,
            "rows_total_global": total_rows_global,
            "row_start": 0,
            "row_end": total_rows_global,
            "eval_shards": expected_shards,
            "eval_shard_index": -1,
            "aggregation": "sharded",
        },
    )
    root_checkpoint_path = base_eval_root / "benchmark_eval_records_checkpoint.csv"
    if root_checkpoint_path.exists():
        root_checkpoint_path.unlink()
    return payload


def run_merge_adapter_validation(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    training_result_path = run_root / "training_result.json"
    if not training_result_path.exists():
        raise FileNotFoundError(f"Missing training_result.json at {training_result_path}")
    training_result = load_json(training_result_path)
    model_root = Path(training_result["shadow_model_dir"]).resolve()
    adapter_dir = Path(training_result["adapter_dir"]).resolve()
    base_validation_root = run_root / str(args.adapter_validation_root_name)
    shard_root = base_validation_root / "shards"
    write_command_script(base_validation_root / "merge_cmd.sh", build_merge_adapter_validation_command_tokens(args))
    if not shard_root.exists():
        raise FileNotFoundError(f"Missing adapter validation shard directory at {shard_root}")

    shard_entries: list[tuple[Path, dict[str, Any]]] = []
    for summary_path in sorted(shard_root.glob("*/validation_summary.json")):
        shard_entries.append((summary_path.parent, load_json(summary_path)))
    if not shard_entries:
        raise FileNotFoundError(f"No shard validation_summary.json files found under {shard_root}")

    shard_entries.sort(key=lambda entry: (int(entry[1].get("row_start", 0)), entry[0].name))
    expected_shards = int(shard_entries[0][1].get("eval_shards", len(shard_entries)))
    if expected_shards <= 1:
        raise RuntimeError("Adapter validation merge requires eval_shards > 1 in shard summaries.")
    if len(shard_entries) != expected_shards:
        raise RuntimeError(f"Expected {expected_shards} shard summaries, found {len(shard_entries)} under {shard_root}")

    total_rows_global = int(shard_entries[0][1].get("rows_total_global", 0))
    sample_selection = shard_entries[0][1].get(
        "sample_selection",
        {
            "mode": "head",
            "selection_tag": f"head_{total_rows_global}",
            "source_total": int(args.validation_sample_size),
            "selected_total": total_rows_global,
        },
    )
    next_row_start = 0
    records: list[dict[str, Any]] = []
    for expected_index, (shard_dir, payload) in enumerate(shard_entries):
        shard_index = int(payload.get("eval_shard_index", -1))
        row_start = int(payload.get("row_start", -1))
        row_end = int(payload.get("row_end", -1))
        shard_total = int(payload.get("overall", {}).get("total", -1))
        shard_rows_total_global = int(payload.get("rows_total_global", total_rows_global))
        if shard_index != expected_index:
            raise RuntimeError(f"Expected shard index {expected_index}, found {shard_index} in {shard_dir}")
        if shard_rows_total_global != total_rows_global:
            raise RuntimeError(
                f"Global row count mismatch for {shard_dir}: {shard_rows_total_global} != {total_rows_global}"
            )
        if payload.get("sample_selection", sample_selection) != sample_selection:
            raise RuntimeError(f"Sample selection mismatch in {shard_dir}")
        if row_start != next_row_start:
            raise RuntimeError(f"Shard coverage gap or overlap before {shard_dir}: expected {next_row_start}, found {row_start}")
        if row_end < row_start:
            raise RuntimeError(f"Invalid shard row range in {shard_dir}: {row_start}:{row_end}")
        shard_records = load_validation_records_csv(shard_dir / "validation.csv")
        if len(shard_records) != shard_total or len(shard_records) != (row_end - row_start):
            raise RuntimeError(
                f"Shard row mismatch in {shard_dir}: validation_rows={len(shard_records)} summary_total={shard_total} "
                f"row_span={row_end - row_start}"
            )
        for local_index, record in enumerate(shard_records):
            record["row_index_within_shard"] = row_start + local_index
        records.extend(shard_records)
        next_row_start = row_end

    if next_row_start != total_rows_global:
        raise RuntimeError(f"Shard coverage incomplete: merged {next_row_start} rows, expected {total_rows_global}")

    validation_frame = build_validation_output_frame(records)
    results_frame = build_validation_results_table(validation_frame)
    summary = summarize_validation_results(results_frame)
    max_num_seqs = max(1, int(args.max_num_seqs))
    chunk_size = min(max_num_seqs, max(1, int(args.prompt_chunk_size)))
    prefill_batch_size = min(max_num_seqs, max(1, int(args.prefill_batch_size)))
    completion_batch_size = min(max_num_seqs, max(1, int(args.completion_batch_size)))
    evaluation_settings = build_eval_settings_payload(
        args,
        eval_shards=expected_shards,
        eval_shard_index=-1,
        chunk_size=chunk_size,
        prefill_batch_size=prefill_batch_size,
        completion_batch_size=completion_batch_size,
    )
    evaluation_name = build_adapter_validation_evaluation_name(
        sample_selection,
        total_rows_global=total_rows_global,
        eval_shards=1,
        eval_shard_index=0,
    )
    payload = {
        "created_at": utc_now(),
        "evaluation_kind": "adapter_validation",
        "evaluation_name": evaluation_name,
        "benchmark_csv": str(TRAIN_CSV_PATH.resolve()),
        "notebook_reference": relative_to_repo(ADAPTER_VALIDATION_NOTEBOOK_PATH),
        "model_root": str(model_root),
        "adapter_dir": str(adapter_dir),
        "readme_contract": README_EVAL_CONTRACT,
        "source_documents": [
            relative_to_repo(README_PATH),
            relative_to_repo(AOPEN_ROOT / "README.md"),
            relative_to_repo(AOPEN_ROOT / "データ戦略を理解する.md"),
            relative_to_repo(AOPEN_ROOT / "学習SFTパイプライン.md"),
            relative_to_repo(ADAPTER_VALIDATION_NOTEBOOK_PATH),
        ],
        "validation_sample_size": int(args.validation_sample_size),
        "sample_selection": sample_selection,
        "rows_total_global": total_rows_global,
        "row_start": 0,
        "row_end": total_rows_global,
        "eval_shards": expected_shards,
        "eval_shard_index": -1,
        "evaluation_settings": evaluation_settings,
        "aggregation": {
            "mode": "sharded",
            "shard_root": str(shard_root.resolve()),
            "num_shards": expected_shards,
        },
        "prompt_policy": {
            "append_boxed_instruction": False,
            "enable_thinking": bool(args.eval_enable_thinking),
        },
        "notebook_reference_score": (
            ADAPTER_VALIDATION_NOTEBOOK_TARGET
            if total_rows_global == ADAPTER_VALIDATION_SAMPLE_SIZE and str(sample_selection.get("mode", "")) == "head"
            else None
        ),
        **summary,
    }
    write_validation_outputs(
        output_root=base_validation_root,
        evaluation_name=evaluation_name,
        validation_frame=validation_frame,
        results_frame=results_frame,
        payload=payload,
    )
    write_json(
        base_validation_root / "validation_progress.json",
        {
            "created_at": utc_now(),
            "status": "complete",
            "evaluation_kind": "adapter_validation",
            "rows_total": total_rows_global,
            "rows_completed": total_rows_global,
            "rows_total_global": total_rows_global,
            "row_start": 0,
            "row_end": total_rows_global,
            "eval_shards": expected_shards,
            "eval_shard_index": -1,
            "aggregation": "sharded",
            "sample_selection": sample_selection,
        },
    )
    root_checkpoint_path = base_validation_root / "validation_records_checkpoint.csv"
    if root_checkpoint_path.exists():
        root_checkpoint_path.unlink()
    return payload


def render_results_markdown(run_result: dict[str, Any], eval_result: dict[str, Any]) -> str:
    overall = eval_result["overall"]
    evaluation_kind = str(eval_result.get("evaluation_kind", "aopen_eval"))
    evaluation_name = str(eval_result.get("evaluation_name", ""))
    evaluation_settings = eval_result.get("evaluation_settings")
    aggregation = eval_result.get("aggregation")
    prompt_policy = eval_result.get("prompt_policy")
    run_manifest = load_run_manifest_for_result(run_result)
    training_settings = run_manifest.get("training", {}) if isinstance(run_manifest, dict) else {}
    training_data = run_manifest.get("training_data", {}) if isinstance(run_manifest, dict) else {}
    adam_settings = training_settings.get("adam", {}) if isinstance(training_settings, dict) else {}
    latest_train_report = run_result.get("latest_train_report") or {}
    run_root = Path(str(run_result["run_root"])).resolve()
    train_cmd_path = run_root / "train_cmd.sh"
    training_source_type = str(training_data.get("source_type", "snapshot"))
    training_source_path = training_data.get("path")
    training_summary_lines: list[str] = []
    if train_cmd_path.exists():
        training_summary_lines.append(f"- train_cmd_path: `{command_path_value(train_cmd_path)}`")
    if isinstance(training_settings, dict) and training_settings:
        if "micro_batch_size" in training_settings:
            training_summary_lines.append(f"- training_micro_batch_size: `{training_settings.get('micro_batch_size', '')}`")
        if "lora_rank" in training_settings:
            training_summary_lines.append(f"- lora_rank: `{training_settings.get('lora_rank', '')}`")
        if isinstance(adam_settings, dict) and "bias_correction" in adam_settings:
            training_summary_lines.append(f"- adam_bias_correction: `{adam_settings.get('bias_correction', '')}`")
    source_documents = list(eval_result.get("source_documents") or [])
    if not source_documents:
        source_documents = [
            relative_to_repo(README_PATH),
            relative_to_repo(AOPEN_ROOT / "README.md"),
            relative_to_repo(AOPEN_ROOT / "データ戦略を理解する.md"),
            relative_to_repo(AOPEN_ROOT / "学習SFTパイプライン.md"),
        ]
    lines = [
        "# v20_mlx_repro_v1 results",
        "",
        "> Repository note: canonical challenge contract lives in `README.md`.",
        "> This version is a local MLX training/evaluation runner for A-Open v20-style Nemotron LoRA experiments.",
        "> It does **not** claim submission.zip parity; it measures local behavior under the README-grounded evaluation contract.",
        "",
        "## Source contract",
        "",
        f"- Top-level README: `{relative_to_repo(README_PATH)}`",
        f"- V20 snapshot: `{relative_to_repo(SNAPSHOT_ROOT)}`",
        f"- training_source_type: `{training_source_type}`",
        "",
        "## Run summary",
        "",
        f"- run_root: `{run_result['run_root']}`",
        f"- shadow_model_dir: `{run_result['shadow_model_dir']}`",
        f"- adapter_dir: `{run_result['adapter_dir']}`",
        f"- snapshot_contract_path: `{run_result['snapshot_contract_path']}`",
        f"- run_manifest_path: `{run_result.get('run_manifest_path', command_path_value(run_root / 'run_manifest.json'))}`",
        "",
        "## Training settings",
        "",
        f"- backend: `mlx`",
        *([f"- training_source_path: `{training_source_path}`"] if training_source_path else []),
        f"- optimizer_steps: `{latest_train_report.get('step', '')}`",
        f"- last_train_loss: `{latest_train_report.get('train_loss', '')}`",
        f"- last_lr: `{latest_train_report.get('lr', '')}`",
        *training_summary_lines,
        "",
        "## Evaluation result",
        "",
        f"- evaluation_kind: `{evaluation_kind}`",
        f"- evaluation_name: `{evaluation_name}`",
        f"- overall_accuracy: `{overall['accuracy']}` ({overall['correct']}/{overall['total']})",
        "",
    ]
    for source_document in source_documents:
        lines.append(f"- source_document: `{source_document}`")
    lines.append("")
    if evaluation_kind == "adapter_validation":
        notebook_reference = str(
            eval_result.get("notebook_reference", relative_to_repo(ADAPTER_VALIDATION_NOTEBOOK_PATH))
        )
        notebook_reference_score = eval_result.get("notebook_reference_score")
        sample_selection = eval_result.get("sample_selection", {})
        lines.append(f"- notebook_reference: `{notebook_reference}`")
        lines.append(f"- validation_sample_size: `{eval_result.get('validation_sample_size', '')}`")
        if isinstance(sample_selection, dict) and sample_selection:
            lines.append(f"- sample_selection_mode: `{sample_selection.get('mode', '')}`")
            lines.append(f"- sample_selection_tag: `{sample_selection.get('selection_tag', '')}`")
            lines.append(
                f"- sample_selection_total: `{sample_selection.get('selected_total', '')}` / `{sample_selection.get('source_total', '')}`"
            )
        if isinstance(notebook_reference_score, dict) and notebook_reference_score:
            lines.append(
                "- notebook_reference_accuracy: "
                f"`{notebook_reference_score['overall_accuracy']}` "
                f"({notebook_reference_score['overall_correct']}/{notebook_reference_score['overall_total']})"
            )
            lines.append(
                f"- delta_vs_notebook_reference: "
                f"`{round(float(overall['accuracy']) - float(notebook_reference_score['overall_accuracy']), 6)}`"
            )
        lines.append("")
    else:
        lines.append(
            f"- v20_target_training_set_accuracy: `{V20_TARGETS['overall_accuracy']}` "
            f"({V20_TARGETS['overall_correct']}/{V20_TARGETS['overall_total']})"
        )
        lines.append(
            f"- delta_vs_v20_target: `{round(float(overall['accuracy']) - float(V20_TARGETS['overall_accuracy']), 6)}`"
        )
        lines.append("")
    if isinstance(evaluation_settings, dict) and evaluation_settings:
        lines.extend(
            [
                "## Eval settings",
                "",
                f"- max_tokens: `{evaluation_settings.get('max_tokens', '')}`",
                f"- max_num_seqs: `{evaluation_settings.get('max_num_seqs', '')}`",
                f"- prompt_chunk_size: `{evaluation_settings.get('prompt_chunk_size', '')}`",
                f"- prefill_batch_size: `{evaluation_settings.get('prefill_batch_size', '')}`",
                f"- completion_batch_size: `{evaluation_settings.get('completion_batch_size', '')}`",
                f"- eval_enable_thinking: `{evaluation_settings.get('eval_enable_thinking', '')}`",
                f"- eval_shards: `{evaluation_settings.get('eval_shards', '')}`",
                "",
            ]
        )
    if isinstance(prompt_policy, dict) and prompt_policy:
        lines.extend(
            [
                "## Prompt policy",
                "",
                f"- append_boxed_instruction: `{prompt_policy.get('append_boxed_instruction', '')}`",
                f"- enable_thinking: `{prompt_policy.get('enable_thinking', '')}`",
                "",
            ]
        )
    if isinstance(aggregation, dict) and aggregation:
        lines.extend(
            [
                "## Eval aggregation",
                "",
                f"- mode: `{aggregation.get('mode', '')}`",
                f"- shard_root: `{aggregation.get('shard_root', '')}`",
                f"- num_shards: `{aggregation.get('num_shards', '')}`",
                "",
            ]
        )
    eval_by_category = {row["category"]: row for row in eval_result["categories"]}
    if evaluation_kind == "adapter_validation":
        reference = eval_result.get("notebook_reference_score")
        if isinstance(reference, dict) and reference.get("categories"):
            lines.extend(
                [
                    "| category | reproduced_correct | reproduced_total | reproduced_accuracy | notebook_correct | notebook_total | notebook_accuracy |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for category, target in reference["categories"].items():
                row = eval_by_category.get(category, {"correct": 0, "total": 0, "accuracy": 0.0})
                target_accuracy = target["correct"] / target["total"] if target["total"] else 0.0
                lines.append(
                    f"| {category} | {row['correct']} | {row['total']} | {float(row['accuracy']):.6f} | "
                    f"{target['correct']} | {target['total']} | {target_accuracy:.6f} |"
                )
        else:
            lines.extend(
                [
                    "| category | correct | total | accuracy | weightage | percentage | contribution |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for row in eval_result["categories"]:
                lines.append(
                    f"| {row['category']} | {row['correct']} | {row['total']} | {float(row['accuracy']):.6f} | "
                    f"{row.get('weightage', '')} | {row.get('percentage', '')} | {row.get('contribution', '')} |"
                )
    else:
        lines.extend(
            [
                "| category | reproduced_correct | reproduced_total | reproduced_accuracy | v20_correct | v20_total | v20_accuracy |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for category, target in V20_TARGETS["categories"].items():
            row = eval_by_category.get(category, {"correct": 0, "total": 0, "accuracy": 0.0})
            target_accuracy = target["correct"] / target["total"] if target["total"] else 0.0
            lines.append(
                f"| {category} | {row['correct']} | {row['total']} | {float(row['accuracy']):.6f} | {target['correct']} | {target['total']} | {target_accuracy:.6f} |"
            )
    lines.extend(
        [
            "",
            "## Important assumptions",
            "",
            "- Training data uses the exact checked-in v20 snapshot `04-08-16-14/tokens` + `logprobs/index.jsonl`, not the current `corpus.jsonl`.",
            "- Optimizer-step grouping uses the recorded `step` assignments from the snapshot, so the MLX run replays the actual v20 batch membership/order.",
            "",
        ]
    )
    if isinstance(training_settings, dict) and training_settings:
        lines.insert(
            -1,
            "- MLX-specific assumptions not explicit in the public v20 config: "
            f"`lora_alpha = {training_settings.get('lora_alpha', '')}`, "
            f"`lora_dropout = {training_settings.get('lora_dropout', '')}`, "
            f"`Adam bias_correction = {adam_settings.get('bias_correction', '')}`.",
        )
    return "\n".join(lines) + "\n"


def update_results_files(args: argparse.Namespace, run_result: dict[str, Any], eval_result: dict[str, Any]) -> None:
    created_at = utc_now()
    if DEFAULT_RESULTS_JSON.exists():
        existing_payload = load_json(DEFAULT_RESULTS_JSON)
        if (
            isinstance(existing_payload, dict)
            and existing_payload.get("run_result") == run_result
            and existing_payload.get("eval_result") == eval_result
            and existing_payload.get("created_at")
        ):
            created_at = str(existing_payload["created_at"])
    results_payload = {
        "created_at": created_at,
        "run_result": run_result,
        "eval_result": eval_result,
    }
    existing_results_json = load_json(DEFAULT_RESULTS_JSON) if DEFAULT_RESULTS_JSON.exists() else None
    if existing_results_json != results_payload:
        write_json(DEFAULT_RESULTS_JSON, results_payload)
    results_markdown = render_results_markdown(run_result, eval_result)
    existing_results_md = DEFAULT_RESULTS_MD.read_text(encoding="utf-8") if DEFAULT_RESULTS_MD.exists() else None
    if existing_results_md != results_markdown:
        write_text(DEFAULT_RESULTS_MD, results_markdown)


def run_full(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.eval_shards) != 1 or int(args.eval_shard_index) != 0:
        raise ValueError("full-run does not support sharded eval; use train + eval-aopen per shard + merge-aopen-eval.")
    run_result = run_train(args)
    eval_result = run_eval_aopen(args)
    update_results_files(args, run_result, eval_result)
    score_ledger_result = update_score_ledger(run_result, eval_result)
    cleanup_result = None
    if bool(args.cleanup_completed_run_artifacts):
        cleanup_result = cleanup_completed_run_artifacts(Path(run_result["run_root"]).resolve())
    result = {
        "run_result": run_result,
        "eval_result": eval_result,
        "results_md": str(DEFAULT_RESULTS_MD.resolve()),
        "results_json": str(DEFAULT_RESULTS_JSON.resolve()),
    }
    if score_ledger_result is not None:
        result["score_ledger_result"] = score_ledger_result
    if cleanup_result is not None:
        result["cleanup_result"] = cleanup_result
    return result


def run_postprocess_existing(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    write_command_script(run_root / "postprocess_cmd.sh", build_postprocess_command_tokens(args))
    training_result_path = run_root / "training_result.json"
    if not training_result_path.exists():
        raise FileNotFoundError(f"Missing training_result.json at {training_result_path}")
    postprocess_eval_kind = str(args.postprocess_eval_kind)
    if postprocess_eval_kind not in {"auto", "aopen", "adapter-validation"}:
        raise ValueError(f"Unsupported --postprocess-eval-kind: {postprocess_eval_kind}")

    eval_summary_path: Path | None = None
    if postprocess_eval_kind in {"auto", "adapter-validation"}:
        primary_validation_root = run_root / str(
            getattr(args, "adapter_validation_root_name", DEFAULT_ADAPTER_VALIDATION_ROOT_NAME)
        )
        validation_summary_path = primary_validation_root / "validation_summary.json"
        if not validation_summary_path.exists():
            validation_shard_root = primary_validation_root / "shards"
            if validation_shard_root.exists():
                run_merge_adapter_validation(args)
        if validation_summary_path.exists():
            eval_summary_path = validation_summary_path
        elif postprocess_eval_kind == "adapter-validation":
            raise FileNotFoundError(f"Missing validation_summary.json at {validation_summary_path}")

    if eval_summary_path is None and postprocess_eval_kind in {"auto", "aopen"}:
        aopen_summary_path = run_root / "aopen_eval" / "benchmark_eval_summary.json"
        if not aopen_summary_path.exists():
            shard_root = run_root / "aopen_eval" / "shards"
            if shard_root.exists():
                run_merge_aopen_eval(args)
        if aopen_summary_path.exists():
            eval_summary_path = aopen_summary_path
        elif postprocess_eval_kind == "aopen":
            raise FileNotFoundError(f"Missing benchmark_eval_summary.json at {aopen_summary_path}")

    if eval_summary_path is None:
        raise FileNotFoundError(
            f"No completed evaluation summary found under "
            f"{run_root / str(getattr(args, 'adapter_validation_root_name', DEFAULT_ADAPTER_VALIDATION_ROOT_NAME))} "
            f"or {run_root / 'aopen_eval'}"
        )
    run_result = load_json(training_result_path)
    eval_result = load_json(eval_summary_path)
    update_results_files(args, run_result, eval_result)
    score_ledger_result = update_score_ledger(run_result, eval_result)
    cleanup_result = None
    if bool(args.cleanup_completed_run_artifacts):
        cleanup_result = cleanup_completed_run_artifacts(run_root)
    result = {
        "run_root": str(run_root),
        "training_result_path": str(training_result_path.resolve()),
        "eval_summary_path": str(eval_summary_path.resolve()),
        "results_md": str(DEFAULT_RESULTS_MD.resolve()),
        "results_json": str(DEFAULT_RESULTS_JSON.resolve()),
    }
    if score_ledger_result is not None:
        result["score_ledger_result"] = score_ledger_result
    if cleanup_result is not None:
        result["cleanup_result"] = cleanup_result
    return result


def run_export_submission(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    if not run_root.exists():
        raise FileNotFoundError(f"Run root does not exist: {run_root}")
    source_adapter_dir = (
        Path(args.source_adapter_dir).resolve()
        if args.source_adapter_dir is not None
        else (run_root / "adapter").resolve()
    )
    output_root = (
        Path(args.submission_output_root).resolve()
        if args.submission_output_root is not None
        else (run_root / "submission_export").resolve()
    )
    ensure_dir(output_root)
    write_command_script(output_root / "export_submission_cmd.sh", build_export_submission_command_tokens(args))

    adapter_config_path = source_adapter_dir / "adapter_config.json"
    adapter_weights_path = source_adapter_dir / "adapters.safetensors"
    if not adapter_config_path.exists():
        raise FileNotFoundError(f"Missing adapter_config.json: {adapter_config_path}")
    if not adapter_weights_path.exists():
        raise FileNotFoundError(f"Missing adapters.safetensors: {adapter_weights_path}")

    readme_submission_contract = load_readme_submission_contract()
    adapter_config = load_json(adapter_config_path)
    if not isinstance(adapter_config, dict):
        raise ValueError(f"Invalid adapter_config.json: {adapter_config_path}")
    rank, alpha, dropout, _raw_target_keys = extract_lora_hparams(adapter_config)
    if rank > int(readme_submission_contract["max_lora_rank"]):
        raise ValueError(
            f"LoRA rank {rank} exceeds README submission limit {readme_submission_contract['max_lora_rank']}."
        )

    source_tensors = load_file(str(adapter_weights_path))
    if not source_tensors:
        raise ValueError(f"No tensors found in {adapter_weights_path}")
    target_modules = build_submission_target_modules_regex(list(source_tensors.keys()))
    reference_model_root = resolve_submission_reference_model_root(
        run_root=run_root,
        adapter_config=adapter_config,
        explicit_reference_model_root=args.reference_model_root,
    )
    if not reference_model_root.exists():
        raise FileNotFoundError(f"Reference model root does not exist: {reference_model_root}")

    converted_tensors, conversion_preview, source_summary = convert_mlx_adapter_to_submission_tensors(source_tensors)
    reference_shapes = build_reference_peft_shapes(
        reference_model_root=reference_model_root,
        target_modules=target_modules,
        rank=rank,
        alpha=alpha,
        dropout=dropout,
    )
    validation = validate_submission_tensors(converted_tensors, reference_shapes)
    if not validation["valid"]:
        raise ValueError(
            "Converted PEFT tensors do not match the Nemotron meta reference: "
            f"missing={validation['missing_key_count']} "
            f"unexpected={validation['unexpected_key_count']} "
            f"shape_mismatches={validation['shape_mismatch_count']}"
        )

    submission_dir = ensure_dir(output_root / "submission_adapter")
    peft_adapter_config = build_peft_adapter_config_payload(
        base_model_name_or_path=str(args.base_model_name_or_path),
        rank=rank,
        alpha=alpha,
        dropout=dropout,
        target_modules=target_modules,
    )
    output_adapter_config_path = submission_dir / "adapter_config.json"
    output_adapter_model_path = submission_dir / "adapter_model.safetensors"
    write_json(output_adapter_config_path, peft_adapter_config)
    save_file(converted_tensors, str(output_adapter_model_path))

    submission_zip_path = output_root / README_SUBMISSION_ARCHIVE_NAME
    with zipfile.ZipFile(submission_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(output_adapter_config_path, "adapter_config.json")
        archive.write(output_adapter_model_path, "adapter_model.safetensors")
    with zipfile.ZipFile(submission_zip_path) as archive:
        submission_zip_members = archive.namelist()
    if sorted(submission_zip_members) != sorted(readme_submission_contract["required_files"]):
        raise ValueError(
            "submission.zip members do not match README contract: "
            f"got={submission_zip_members} expected={readme_submission_contract['required_files']}"
        )

    validation_summary_path = run_root / "adapter_validation" / "validation_summary.json"
    validation_summary_payload = None
    if validation_summary_path.exists():
        loaded_validation_summary = load_json(validation_summary_path)
        if isinstance(loaded_validation_summary, dict):
            validation_summary_payload = loaded_validation_summary
    manifest = {
        "created_at": utc_now(),
        "run_name": args.run_name,
        "run_root": str(run_root),
        "source_adapter_dir": str(source_adapter_dir),
        "source_adapter_config_path": str(adapter_config_path),
        "source_adapter_weights_path": str(adapter_weights_path),
        "reference_model_root": str(reference_model_root),
        "output_root": str(output_root),
        "submission_dir": str(submission_dir),
        "submission_zip_path": str(submission_zip_path),
        "submission_zip_size_bytes": submission_zip_path.stat().st_size,
        "base_model_name_or_path": str(args.base_model_name_or_path),
        "target_modules": target_modules,
        "rank": int(rank),
        "lora_alpha": float(alpha),
        "lora_dropout": float(dropout),
        "readme_submission_contract": readme_submission_contract,
        "readme_submission_contract_verified_from_readme_file": True,
        "source_summary": source_summary,
        "converted_tensor_count": len(converted_tensors),
        "validation": validation,
        "conversion_preview": conversion_preview,
        "submission_zip_members": submission_zip_members,
        "source_validation_summary_path": str(validation_summary_path) if validation_summary_path.exists() else None,
        "source_validation_summary": validation_summary_payload,
    }
    write_json(output_root / "export_manifest.json", manifest)
    write_submission_export_results_md(output_root / "submission_export_results.md", manifest)
    return manifest


def run_prepare(args: argparse.Namespace) -> dict[str, Any]:
    artifacts = prepare_run(args)
    return {
        "run_root": str(artifacts.run_root),
        "shadow_model_dir": str(artifacts.shadow_model_dir),
        "adapter_dir": str(artifacts.adapter_dir),
        "step_plan_path": str(artifacts.step_plan_path),
        "snapshot_contract_path": str(artifacts.snapshot_contract_path),
        "run_manifest_path": str(artifacts.config_path),
    }


def run_adapter_validation_pipeline(
    args: argparse.Namespace,
    *,
    run_root: Path,
    log_path: Path,
    pipeline_label: str,
    adapter_validation_root_name: str,
    validation_subset_size: int,
    validation_subset_mode: str,
    eval_shards: int,
    run_postprocess: bool,
) -> Path:
    env = os.environ.copy()
    env.setdefault("UV_NO_PROGRESS", "1")
    pipeline_args = make_namespace_with(
        args,
        adapter_validation_root_name=str(adapter_validation_root_name),
        validation_subset_size=int(validation_subset_size),
        validation_subset_mode=str(validation_subset_mode),
        eval_shards=max(1, int(eval_shards)),
        eval_shard_index=0,
    )
    eval_shards = max(1, int(pipeline_args.eval_shards))
    for shard_index in range(eval_shards):
        shard_args = make_namespace_with(pipeline_args, eval_shard_index=shard_index)
        append_log_line(
            log_path,
            f"{pipeline_label}_shard_start shard={shard_index} root={adapter_validation_root_name}",
        )
        with log_path.open("a", encoding="utf-8") as handle:
            subprocess.run(
                build_eval_adapter_validation_command_tokens(shard_args),
                cwd=str(REPO_ROOT),
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
                check=True,
            )
        append_log_line(
            log_path,
            f"{pipeline_label}_shard_done shard={shard_index} exit=0 root={adapter_validation_root_name}",
        )
    if eval_shards > 1:
        append_log_line(log_path, f"{pipeline_label}_merge_start root={adapter_validation_root_name}")
        with log_path.open("a", encoding="utf-8") as handle:
            subprocess.run(
                build_merge_adapter_validation_command_tokens(pipeline_args),
                cwd=str(REPO_ROOT),
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
                check=True,
            )
        append_log_line(log_path, f"{pipeline_label}_merge_done exit=0 root={adapter_validation_root_name}")
    if run_postprocess:
        postprocess_args = make_namespace_with(args, postprocess_eval_kind="adapter-validation")
        append_log_line(log_path, "postprocess_start")
        with log_path.open("a", encoding="utf-8") as handle:
            subprocess.run(
                build_postprocess_command_tokens(postprocess_args),
                cwd=str(REPO_ROOT),
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
                check=True,
            )
        append_log_line(log_path, "postprocess_done exit=0")
    return resolve_adapter_validation_root(
        run_root,
        shard_count=1,
        shard_index=0,
        root_name=adapter_validation_root_name,
    )


def run_managed_adapter_validation_pipeline(args: argparse.Namespace, *, run_root: Path, log_path: Path) -> None:
    mini_validation_subset_size = max(0, int(getattr(args, "mini_validation_subset_size", 0)))
    if mini_validation_subset_size > 0:
        mini_validation_root_name = str(getattr(args, "mini_validation_root_name", DEFAULT_MINI_VALIDATION_ROOT_NAME))
        mini_validation_root = resolve_adapter_validation_root(
            run_root,
            shard_count=1,
            shard_index=0,
            root_name=mini_validation_root_name,
        )
        mini_gate_path = mini_validation_root / "smoke_gate.json"
        mini_gate_payload = load_json(mini_gate_path) if mini_gate_path.exists() else None
        if isinstance(mini_gate_payload, dict) and not bool(mini_gate_payload.get("proceed", False)):
            append_log_line(log_path, f"mini_eval_gate_blocked root={mini_validation_root_name}")
            return
        if not (isinstance(mini_gate_payload, dict) and bool(mini_gate_payload.get("proceed", False))):
            mini_validation_root = run_adapter_validation_pipeline(
                args,
                run_root=run_root,
                log_path=log_path,
                pipeline_label="mini_eval",
                adapter_validation_root_name=mini_validation_root_name,
                validation_subset_size=mini_validation_subset_size,
                validation_subset_mode=str(
                    getattr(args, "mini_validation_subset_mode", "stratified-category-proportional")
                ),
                eval_shards=1,
                run_postprocess=False,
            )
            mini_gate_payload = evaluate_smoke_validation_gate(mini_validation_root)
            write_smoke_validation_gate_artifacts(mini_validation_root, mini_gate_payload)
            append_log_line(
                log_path,
                "mini_eval_gate "
                f"status={mini_gate_payload['status']} "
                f"accuracy={float(mini_gate_payload['overall']['accuracy']):.6f} "
                f"nonempty={int(mini_gate_payload['prediction_stats']['nonempty_predictions'])} "
                f"distinct={int(mini_gate_payload['prediction_stats']['distinct_predictions'])}",
            )
            if not bool(mini_gate_payload.get("proceed", False)):
                return
    run_adapter_validation_pipeline(
        args,
        run_root=run_root,
        log_path=log_path,
        pipeline_label="full_eval",
        adapter_validation_root_name=str(args.adapter_validation_root_name),
        validation_subset_size=int(args.validation_subset_size),
        validation_subset_mode=str(args.validation_subset_mode),
        eval_shards=int(args.eval_shards),
        run_postprocess=True,
    )


def run_manage_run(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    managed_log = run_root / "managed_run.log"
    supervisor_log = run_root / "train_supervisor.log"
    progress_log = run_root / "progress_watch.log"
    completion_log = run_root / "completion_watch.log"
    eval_log = run_root / "eval300_watch.log"
    stall_log = run_root / "stall_guard.log"
    append_log_line(managed_log, f"manager_start run_name={args.run_name}")
    append_log_line(supervisor_log, f"manager_attached run_name={args.run_name}")
    append_log_line(progress_log, f"manager_attached run_name={args.run_name}")
    append_log_line(completion_log, f"manager_attached run_name={args.run_name}")
    append_log_line(eval_log, f"manager_attached run_name={args.run_name}")
    append_log_line(
        stall_log,
        f"manager_attached run_name={args.run_name} stale_seconds={int(args.stall_threshold_seconds)}",
    )
    last_completion_step: int | None | str = None
    last_progress_at = 0.0
    last_stall_at = 0.0
    manager_sleep_seconds = max(30, int(args.manager_sleep_seconds))
    progress_watch_interval_seconds = max(30, int(args.progress_watch_interval_seconds))
    stall_check_interval_seconds = max(30, int(args.stall_check_interval_seconds))
    stall_threshold_seconds = max(300, int(args.stall_threshold_seconds))
    save_every_steps = max(0, int(args.save_every_steps))

    while True:
        training_result_exists = (run_root / "training_result.json").exists()
        validation_summary_exists = (
            run_root / str(getattr(args, "adapter_validation_root_name", DEFAULT_ADAPTER_VALIDATION_ROOT_NAME))
            / "validation_summary.json"
        ).exists()
        step, age_seconds = read_latest_train_report(run_root)
        step_value: int | str = step if step is not None else "missing"

        append_log_line(
            completion_log,
            f"waiting step={step_value} train_result={int(training_result_exists)} score={int(validation_summary_exists)}",
        )
        if step is not None and step != last_completion_step and save_every_steps > 0 and step % save_every_steps == 0:
            append_log_line(completion_log, "checkpoints_after_cap")
            for checkpoint_path in list_saved_checkpoints(run_root / "adapter"):
                append_log_line(completion_log, str(checkpoint_path.resolve()))
        last_completion_step = step_value

        if training_result_exists and validation_summary_exists:
            append_log_line(completion_log, "done")
            append_log_line(managed_log, f"manager_done run_name={args.run_name}")
            return {
                "run_root": str(run_root),
                "managed_log": str(managed_log.resolve()),
                "status": "done",
            }

        now = time.time()
        if not training_result_exists:
            train_pids = find_run_command_pids(args.run_name, "train")
            if train_pids:
                append_log_line(supervisor_log, f"train_alive active={len(train_pids)}")
            else:
                latest_checkpoint = find_latest_checkpoint_path(run_root / "adapter")
                if latest_checkpoint is not None:
                    append_log_line(supervisor_log, f"relaunch_needed resume_from={latest_checkpoint}")
                    train_args = make_namespace_with(args, resume_adapter_file=latest_checkpoint)
                else:
                    append_log_line(supervisor_log, "relaunch_needed resume_from=none")
                    train_args = make_namespace_with(args, resume_adapter_file=None)
                train_pid = spawn_detached_command(
                    build_train_command_tokens(train_args),
                    log_path=run_root / "train_detached.log",
                )
                append_log_line(supervisor_log, f"train_spawned pid={train_pid}")
                train_pids = [train_pid]

            effective_age_seconds = age_seconds
            if effective_age_seconds is None and train_pids:
                pid_ages = [read_process_elapsed_seconds(pid) for pid in train_pids]
                resolved_ages = [value for value in pid_ages if value is not None]
                if resolved_ages:
                    effective_age_seconds = max(resolved_ages)

            if now - last_progress_at >= progress_watch_interval_seconds:
                if step is None and effective_age_seconds is None:
                    append_log_line(progress_log, "report_missing")
                elif step is None:
                    append_log_line(progress_log, f"report_missing age_seconds={effective_age_seconds}")
                elif effective_age_seconds is None:
                    append_log_line(progress_log, "report_missing")
                else:
                    status = "stale_progress_detected" if effective_age_seconds >= 1800 else "progress_ok"
                    append_log_line(progress_log, f"{status} step={step} age_seconds={effective_age_seconds}")
                last_progress_at = now

            if now - last_stall_at >= stall_check_interval_seconds:
                status = "ok"
                action = "none"
                missing_report_stall_threshold_seconds = max(stall_threshold_seconds * 3, 7200)
                effective_stall_threshold_seconds = (
                    stall_threshold_seconds if step is not None else missing_report_stall_threshold_seconds
                )
                if (
                    effective_age_seconds is not None
                    and effective_age_seconds >= effective_stall_threshold_seconds
                    and train_pids
                ):
                    status = "stale_detected" if step is not None else "missing_report_stale_detected"
                    action = "kill_for_supervisor_restart"
                    for pid in train_pids:
                        subprocess.run(["kill", str(pid)], check=False)
                append_log_line(
                    stall_log,
                    str(
                        {
                            "status": status,
                            "action": action,
                            "step": step_value,
                            "age_seconds": effective_age_seconds,
                            "stall_threshold_seconds": effective_stall_threshold_seconds,
                            "pids": train_pids,
                        }
                    ),
                )
                last_stall_at = now
        elif not validation_summary_exists:
            try:
                run_managed_adapter_validation_pipeline(args, run_root=run_root, log_path=eval_log)
            except subprocess.CalledProcessError as exc:
                append_log_line(eval_log, f"eval_pipeline_failed returncode={exc.returncode}")
        time.sleep(manager_sleep_seconds)


def run_launch_managed(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    write_command_script(run_root / "launch_managed_cmd.sh", build_manage_run_command_tokens(args))
    existing_pids = find_run_command_pids(args.run_name, "manage-run")
    if existing_pids:
        return {
            "run_root": str(run_root),
            "manager_pids": existing_pids,
            "managed_log": str((run_root / "managed_run.log").resolve()),
            "status": "already_running",
        }
    manager_pid = spawn_detached_command(
        build_manage_run_command_tokens(args),
        log_path=run_root / "managed_run.log",
    )
    return {
        "run_root": str(run_root),
        "manager_pids": [manager_pid],
        "managed_log": str((run_root / "managed_run.log").resolve()),
        "status": "started",
    }


def run_queue_managed(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    queue_log_path = Path(args.queue_log_path).resolve()
    write_command_script(run_root / "queue_managed_cmd.sh", build_queue_managed_run_command_tokens(args))
    append_log_line(queue_log_path, f"queue_start run_name={args.run_name}")
    wait_any_roots = [Path(path).resolve() for path in (args.wait_for_any_training_result_run_root or [])]
    require_start_roots = [Path(path).resolve() for path in (args.require_run_start_run_root or [])]
    queue_sleep_seconds = max(30, int(args.queue_sleep_seconds))
    max_active_trains_before_launch = int(args.max_active_trains_before_launch)

    while True:
        training_result_exists = (run_root / "training_result.json").exists()
        validation_summary_exists = (
            run_root / str(getattr(args, "adapter_validation_root_name", DEFAULT_ADAPTER_VALIDATION_ROOT_NAME))
            / "validation_summary.json"
        ).exists()
        existing_manager_pids = find_run_command_pids(args.run_name, "manage-run")
        if training_result_exists and validation_summary_exists:
            append_log_line(queue_log_path, f"already_completed run_name={args.run_name}")
            return {
                "run_root": str(run_root),
                "queue_log_path": str(queue_log_path),
                "status": "already_completed",
            }
        if existing_manager_pids:
            append_log_line(
                queue_log_path,
                f"already_running run_name={args.run_name} manager_pids={','.join(str(pid) for pid in existing_manager_pids)}",
            )
            return {
                "run_root": str(run_root),
                "queue_log_path": str(queue_log_path),
                "status": "already_running",
                "manager_pids": existing_manager_pids,
            }

        any_ready = True
        if wait_any_roots:
            any_ready = any((root / "training_result.json").exists() for root in wait_any_roots)

        required_started = True
        if require_start_roots:
            required_started = all(
                (root / "training_result.json").exists() or (root / "adapter" / "latest_train_report.json").exists()
                for root in require_start_roots
            )

        active_trains = count_active_train_processes()
        active_ready = active_trains <= max_active_trains_before_launch

        if any_ready and required_started and active_ready:
            append_log_line(
                queue_log_path,
                f"slot_open_detected active={active_trains} require_started={int(required_started)} any_ready={int(any_ready)}",
            )
            launch_result = run_launch_managed(args)
            append_log_line(
                queue_log_path,
                f"launch_requested run_name={args.run_name} status={launch_result['status']}",
            )
            return {
                "run_root": str(run_root),
                "queue_log_path": str(queue_log_path),
                "status": "launch_requested",
                "launch_result": launch_result,
            }

        append_log_line(
            queue_log_path,
            f"waiting_for_slot active={active_trains} require_started={int(required_started)} any_ready={int(any_ready)}",
        )
        time.sleep(queue_sleep_seconds)


def run_watch_score_publish(args: argparse.Namespace) -> dict[str, Any]:
    log_path = Path(args.score_watch_log_path).resolve()
    state_dir = Path(args.score_watch_state_dir).resolve()
    ensure_dir(state_dir)
    watch_run_roots = [Path(path).resolve() for path in (args.watch_run_root or [])]
    if not watch_run_roots:
        raise ValueError("watch-score-publish requires at least one --watch-run-root")
    write_command_script(state_dir / "score_publish_watch_cmd.sh", build_watch_score_publish_command_tokens(args))
    append_log_line(log_path, f"watcher_start watched_runs={len(watch_run_roots)}")
    sleep_seconds = max(30, int(args.score_watch_sleep_seconds))

    while True:
        touched = False
        for run_root in watch_run_roots:
            run_name = run_root.name
            done_file = state_dir / f"{re.sub(r'[^A-Za-z0-9._-]+', '_', run_name)}.done"
            if done_file.exists():
                continue
            training_result_path = run_root / "training_result.json"
            validation_summary_path = (
                run_root / str(getattr(args, "adapter_validation_root_name", DEFAULT_ADAPTER_VALIDATION_ROOT_NAME))
                / "validation_summary.json"
            )
            if not training_result_path.exists() or not validation_summary_path.exists():
                continue
            touched = True
            append_log_line(log_path, f"score_detected run_name={run_name}")
            try:
                postprocess_args = make_namespace_with(
                    args,
                    output_root=run_root.parent,
                    run_name=run_name,
                )
                postprocess_result = run_postprocess_existing(postprocess_args)
            except Exception as exc:
                append_log_line(log_path, f"postprocess_failed run_name={run_name} error={type(exc).__name__}: {exc}")
                continue
            score_ledger_result = postprocess_result.get("score_ledger_result")
            if not isinstance(score_ledger_result, dict):
                append_log_line(log_path, f"score_ledger_missing run_name={run_name}")
                write_text(done_file, utc_now() + "\n")
                continue
            ledger_path = Path(str(score_ledger_result["ledger_path"])).resolve()
            try:
                publish_result = commit_and_push_score_ledger(
                    ledger_path=ledger_path,
                    run_name=run_name,
                    log_path=log_path,
                )
            except Exception as exc:
                append_log_line(log_path, f"git_publish_failed run_name={run_name} error={type(exc).__name__}: {exc}")
                continue
            if publish_result["status"] == "git_busy":
                continue
            write_text(done_file, utc_now() + "\n")
        if not touched:
            append_log_line(log_path, "waiting_for_scores")
        time.sleep(sleep_seconds)


def run_watch_progress_ledger(args: argparse.Namespace) -> dict[str, Any]:
    log_path = Path(args.progress_watch_log_path).resolve()
    state_dir = Path(args.progress_watch_state_dir).resolve()
    ensure_dir(state_dir)
    watch_run_roots = [Path(path).resolve() for path in (args.watch_run_root or [])]
    if not watch_run_roots:
        raise ValueError("watch-progress-ledger requires at least one --watch-run-root")
    write_command_script(state_dir / "progress_watch_cmd.sh", build_watch_progress_command_tokens(args))
    append_log_line(log_path, f"progress_watcher_start watched_runs={len(watch_run_roots)}")
    sleep_seconds = max(30, int(args.progress_watch_sleep_seconds))
    step_interval = max(1, int(args.progress_watch_step_interval))

    while True:
        touched = False
        for run_root in watch_run_roots:
            progress_result = update_progress_ledger(run_root, apply_changes=False)
            if not isinstance(progress_result, dict):
                continue
            touched = True
            run_name = run_root.name
            state_path = state_dir / f"{re.sub(r'[^A-Za-z0-9._-]+', '_', run_name)}.json"
            state: dict[str, Any] = {}
            if state_path.exists():
                loaded_state = load_json(state_path)
                if isinstance(loaded_state, dict):
                    state = loaded_state
            published_step_raw = state.get("published_step")
            published_step = int(published_step_raw) if published_step_raw is not None else None
            published_checkpoints = str(state.get("published_checkpoints", ""))
            published_done = bool(state.get("published_done", False))
            published_runtime_status = str(state.get("published_runtime_status", ""))
            should_publish = False
            if str(progress_result["runtime_status"]) != published_runtime_status:
                should_publish = True
            elif progress_result["checkpoint_summary"] != published_checkpoints:
                should_publish = True
            elif progress_result["step"] is not None and (
                published_step is None or int(progress_result["step"]) >= published_step + step_interval
            ):
                should_publish = True
            elif bool(progress_result["training_done"]) and not published_done:
                should_publish = True
            if not should_publish:
                continue
            if git_index_is_locked():
                append_log_line(log_path, f"progress_publish_git_busy path={relative_to_repo(Path(str(progress_result['ledger_path'])))}")
                continue
            progress_result = update_progress_ledger(run_root, apply_changes=True)
            if not isinstance(progress_result, dict):
                continue
            ledger_path = Path(str(progress_result["ledger_path"])).resolve()
            try:
                publish_result = commit_and_push_tracked_file(
                    tracked_path=ledger_path,
                    commit_message=f"Record progress for {run_name}",
                    log_path=log_path,
                    log_prefix="progress_publish",
                )
            except Exception as exc:
                append_log_line(log_path, f"progress_publish_failed run_name={run_name} error={type(exc).__name__}: {exc}")
                continue
            if publish_result["status"] == "git_busy":
                continue
            write_json(
                state_path,
                {
                    "updated_at": utc_now(),
                    "published_step": int(progress_result["step"]) if progress_result["step"] is not None else None,
                    "published_checkpoints": str(progress_result["checkpoint_summary"]),
                    "published_done": bool(progress_result["training_done"]),
                    "published_runtime_status": str(progress_result["runtime_status"]),
                },
            )
        if not touched:
            append_log_line(log_path, "waiting_for_progress")
        time.sleep(sleep_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce the published A-Open v20 Nemotron SFT pipeline on Apple/MLX using the exact "
            "04-08-16-14 training snapshot as the source of truth."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_shared_args(target: argparse.ArgumentParser) -> None:
        target.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
        target.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
        target.add_argument("--run-name", type=str, default=DEFAULT_RUN_NAME)
        target.add_argument(
            "--training-bundle-path",
            type=Path,
            default=None,
            help="Optional single-file training bundle JSONL to use instead of the fixed 04-08-16-14 snapshot.",
        )
        target.add_argument("--force-shadow-model", action="store_true")
        target.add_argument("--seed", type=int, default=123)
        target.add_argument("--batch-size", type=int, default=32, help="Effective optimizer batch size.")
        target.add_argument("--micro-batch-size", type=int, default=16)
        target.add_argument("--learning-rate", type=float, default=2e-4)
        target.add_argument("--max-seq-length", type=int, default=8192)
        target.add_argument(
            "--fixed-train-padding",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="Pad every train microbatch to max_seq_length to avoid MLX compile-shape cache growth.",
        )
        target.add_argument("--lora-rank", type=int, default=32)
        target.add_argument("--lora-alpha", type=float, default=32.0)
        target.add_argument("--lora-dropout", type=float, default=0.0)
        target.add_argument("--beta1", type=float, default=0.9)
        target.add_argument("--beta2", type=float, default=0.95)
        target.add_argument("--eps", type=float, default=1e-8)
        target.add_argument("--weight-decay", type=float, default=0.0)
        target.add_argument(
            "--bias-correction",
            action=argparse.BooleanOptionalAction,
            default=True,
        )
        target.add_argument("--steps-per-report", type=int, default=1)
        target.add_argument("--save-every-steps", type=int, default=0)
        target.add_argument("--max-saved-checkpoints", type=int, default=3)
        target.add_argument("--resume-adapter-file", type=Path, default=None)
        target.add_argument("--max-optimizer-steps", type=int, default=0)
        target.add_argument("--max-tokens", type=int, default=README_EVAL_CONTRACT["max_tokens"])
        target.add_argument("--temperature", type=float, default=README_EVAL_CONTRACT["temperature"])
        target.add_argument("--top-p", type=float, default=README_EVAL_CONTRACT["top_p"])
        target.add_argument("--max-num-seqs", type=int, default=README_EVAL_CONTRACT["max_num_seqs"])
        target.add_argument("--max-model-len", type=int, default=README_EVAL_CONTRACT["max_model_len"])
        target.add_argument("--prompt-chunk-size", type=int, default=16)
        target.add_argument("--prefill-batch-size", type=int, default=8)
        target.add_argument("--completion-batch-size", type=int, default=8)
        target.add_argument("--eval-limit", type=int, default=0)
        target.add_argument("--validation-sample-size", type=int, default=ADAPTER_VALIDATION_SAMPLE_SIZE)
        target.add_argument("--validation-subset-size", type=int, default=0)
        target.add_argument(
            "--validation-subset-mode",
            choices=("head", "stratified-category-proportional"),
            default="head",
        )
        target.add_argument(
            "--adapter-validation-root-name",
            type=str,
            default=DEFAULT_ADAPTER_VALIDATION_ROOT_NAME,
            help="Subdirectory under run_root for the primary adapter validation artifacts.",
        )
        target.add_argument(
            "--mini-validation-subset-size",
            type=int,
            default=DEFAULT_MINI_VALIDATION_SUBSET_SIZE,
            help="If > 0, run this many stratified smoke rows before the primary adapter validation.",
        )
        target.add_argument(
            "--mini-validation-subset-mode",
            choices=("head", "stratified-category-proportional"),
            default="stratified-category-proportional",
        )
        target.add_argument(
            "--mini-validation-root-name",
            type=str,
            default=DEFAULT_MINI_VALIDATION_ROOT_NAME,
            help="Subdirectory under run_root for the smoke validation artifacts.",
        )
        target.add_argument("--eval-shards", type=int, default=1)
        target.add_argument("--eval-shard-index", type=int, default=0)
        target.add_argument(
            "--eval-enable-thinking",
            action=argparse.BooleanOptionalAction,
            default=True,
        )
        target.add_argument(
            "--lazy-load",
            action=argparse.BooleanOptionalAction,
            default=True,
        )
        target.add_argument("--force-single-generate", action="store_true")
        target.add_argument(
            "--eval-row-timeout-seconds",
            type=int,
            default=0,
            help="Optional per-row local eval timeout in seconds. 0 disables the timeout.",
        )
        target.add_argument(
            "--postprocess-eval-kind",
            choices=("auto", "aopen", "adapter-validation"),
            default="auto",
        )
        target.add_argument(
            "--cleanup-completed-run-artifacts",
            action=argparse.BooleanOptionalAction,
            default=True,
            help=(
                "After a run has both training_result.json and a completed evaluation summary, "
                "prune periodic *_adapters.safetensors checkpoints and remove training_bundle_tokens/"
            ),
        )
        target.add_argument("--manager-sleep-seconds", type=int, default=120)
        target.add_argument("--progress-watch-interval-seconds", type=int, default=300)
        target.add_argument("--stall-check-interval-seconds", type=int, default=600)
        target.add_argument("--stall-threshold-seconds", type=int, default=2400)

    prepare = subparsers.add_parser("prepare", help="Prepare the v20 snapshot contract, shadow model, and run manifest.")
    add_shared_args(prepare)
    prepare.set_defaults(func=run_prepare)

    train = subparsers.add_parser("train", help="Prepare if needed, then train the MLX LoRA adapter on the exact v20 snapshot.")
    add_shared_args(train)
    train.set_defaults(func=run_train)

    eval_aopen = subparsers.add_parser("eval-aopen", help="Run A-Open-style evaluation on data/train.csv using the trained adapter.")
    add_shared_args(eval_aopen)
    eval_aopen.set_defaults(func=run_eval_aopen)

    eval_adapter_validation = subparsers.add_parser(
        "eval-adapter-validation",
        help="Run adapter-validation-notebook.ipynb-style validation on train.csv.head(validation_sample_size) using the trained adapter.",
    )
    add_shared_args(eval_adapter_validation)
    eval_adapter_validation.set_defaults(func=run_eval_adapter_validation)

    merge_eval = subparsers.add_parser(
        "merge-aopen-eval",
        help="Merge shard-local A-Open eval outputs into run_root/aopen_eval/ and update the root summary.",
    )
    add_shared_args(merge_eval)
    merge_eval.set_defaults(func=run_merge_aopen_eval)

    merge_adapter_validation = subparsers.add_parser(
        "merge-adapter-validation",
        help="Merge shard-local adapter validation outputs into the selected adapter-validation root and update the root summary.",
    )
    add_shared_args(merge_adapter_validation)
    merge_adapter_validation.set_defaults(func=run_merge_adapter_validation)

    full = subparsers.add_parser("full-run", help="Prepare, train, evaluate, and update the tracked results files.")
    add_shared_args(full)
    full.set_defaults(func=run_full)

    postprocess = subparsers.add_parser(
        "postprocess-run",
        help="Update tracked results files from an existing run's completed evaluation summary.",
    )
    add_shared_args(postprocess)
    postprocess.set_defaults(func=run_postprocess_existing)

    export_submission = subparsers.add_parser(
        "export-submission",
        help="Convert a completed MLX adapter into a README-contract submission.zip using the single-file runner.",
    )
    export_submission.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    export_submission.add_argument("--run-name", type=str, default=DEFAULT_RUN_NAME)
    export_submission.add_argument("--source-adapter-dir", type=Path, default=None)
    export_submission.add_argument("--submission-output-root", type=Path, default=None)
    export_submission.add_argument("--reference-model-root", type=Path, default=None)
    export_submission.add_argument(
        "--base-model-name-or-path",
        type=str,
        default=DEFAULT_SUBMISSION_BASE_MODEL_NAME_OR_PATH,
    )
    export_submission.set_defaults(func=run_export_submission)

    manage_run = subparsers.add_parser(
        "manage-run",
        help="Long-running supervisor that keeps a train alive, runs smoke validation, then local300 validation and postprocess.",
    )
    add_shared_args(manage_run)
    manage_run.set_defaults(func=run_manage_run)

    launch_managed = subparsers.add_parser(
        "launch-managed-run",
        help="Spawn a detached manage-run supervisor for a run so future restarts and validation stay in one command.",
    )
    add_shared_args(launch_managed)
    launch_managed.set_defaults(func=run_launch_managed)

    queue_managed = subparsers.add_parser(
        "queue-managed-run",
        help="Wait for queue conditions and then call launch-managed-run from the single-file driver.",
    )
    add_shared_args(queue_managed)
    queue_managed.add_argument("--queue-log-path", type=Path, required=True)
    queue_managed.add_argument("--queue-sleep-seconds", type=int, default=300)
    queue_managed.add_argument("--max-active-trains-before-launch", type=int, default=0)
    queue_managed.add_argument(
        "--wait-for-any-training-result-run-root",
        action="append",
        default=[],
        type=Path,
    )
    queue_managed.add_argument(
        "--require-run-start-run-root",
        action="append",
        default=[],
        type=Path,
    )
    queue_managed.set_defaults(func=run_queue_managed)

    build_v11 = subparsers.add_parser(
        "build-v11-bit-binary-mainline",
        help="Build the v11 curated bit/binary-heavy bundle and tracked markdown ledger.",
    )
    build_v11.add_argument("--bundle-path", type=Path, default=V11_BUNDLE_PATH)
    build_v11.add_argument("--results-path", type=Path, default=V11_RESULTS_MD)
    build_v11.set_defaults(func=run_build_v11_bit_binary_mainline)

    build_v12 = subparsers.add_parser(
        "build-v12-bit-binary-manual-heavy",
        help="Build the v12 manual-heavy bit/binary bundle and tracked markdown ledger.",
    )
    build_v12.add_argument("--bundle-path", type=Path, default=V12_BUNDLE_PATH)
    build_v12.add_argument("--results-path", type=Path, default=V12_RESULTS_MD)
    build_v12.set_defaults(func=run_build_v12_bit_binary_manual_heavy)

    build_v13 = subparsers.add_parser(
        "build-v13-bit-binary-promptlocal-heavy",
        help="Build the v13 prompt-local-heavy bit/binary bundle and tracked markdown ledger.",
    )
    build_v13.add_argument("--bundle-path", type=Path, default=V13_BUNDLE_PATH)
    build_v13.add_argument("--results-path", type=Path, default=V13_RESULTS_MD)
    build_v13.set_defaults(func=run_build_v13_bit_binary_promptlocal_heavy)

    build_v14 = subparsers.add_parser(
        "build-v14-bit-binary-structured-heavy",
        help="Build the v14 structured-heavy bit/binary bundle and tracked markdown ledger.",
    )
    build_v14.add_argument("--bundle-path", type=Path, default=V14_BUNDLE_PATH)
    build_v14.add_argument("--results-path", type=Path, default=V14_RESULTS_MD)
    build_v14.set_defaults(func=run_build_v14_bit_binary_structured_heavy)

    build_v15 = subparsers.add_parser(
        "build-v15-bit-binary-bitother-heavy",
        help="Build the v15 bitother-heavy bit/binary bundle and tracked markdown ledger.",
    )
    build_v15.add_argument("--bundle-path", type=Path, default=V15_BUNDLE_PATH)
    build_v15.add_argument("--results-path", type=Path, default=V15_RESULTS_MD)
    build_v15.set_defaults(func=run_build_v15_bit_binary_bitother_heavy)

    build_v16 = subparsers.add_parser(
        "build-v16-bit-binary-miss-family-heavy",
        help="Build the v16 miss-family-heavy bit/binary bundle and tracked markdown ledger.",
    )
    build_v16.add_argument("--bundle-path", type=Path, default=V16_BUNDLE_PATH)
    build_v16.add_argument("--results-path", type=Path, default=V16_RESULTS_MD)
    build_v16.set_defaults(func=run_build_v16_bit_binary_miss_family_heavy)

    build_v17 = subparsers.add_parser(
        "build-v17-bit-binary-hybrid-miss-promptlocal",
        help="Build the v17 hybrid miss/promptlocal bit-binary bundle and tracked markdown ledger.",
    )
    build_v17.add_argument("--bundle-path", type=Path, default=V17_BUNDLE_PATH)
    build_v17.add_argument("--results-path", type=Path, default=V17_RESULTS_MD)
    build_v17.set_defaults(func=run_build_v17_bit_binary_hybrid_miss_promptlocal)

    build_v18 = subparsers.add_parser(
        "build-v18-bit-binary-explicit-local-miss",
        help="Build the v18 explicit-local-miss bit-binary bundle and tracked markdown ledger.",
    )
    build_v18.add_argument("--bundle-path", type=Path, default=V18_BUNDLE_PATH)
    build_v18.add_argument("--results-path", type=Path, default=V18_RESULTS_MD)
    build_v18.set_defaults(func=run_build_v18_bit_binary_explicit_local_miss)

    build_v19 = subparsers.add_parser(
        "build-v19-bit-binary-hardscore-tail",
        help="Build the v19 hardscore-tail bit-binary bundle and tracked markdown ledger.",
    )
    build_v19.add_argument("--bundle-path", type=Path, default=V19_BUNDLE_PATH)
    build_v19.add_argument("--results-path", type=Path, default=V19_RESULTS_MD)
    build_v19.set_defaults(func=run_build_v19_bit_binary_hardscore_tail)

    build_v20 = subparsers.add_parser(
        "build-v20-bit-binary-localmiss-hardscore-fusion",
        help="Build the v20 localmiss-hardscore fusion bit-binary bundle and tracked markdown ledger.",
    )
    build_v20.add_argument("--bundle-path", type=Path, default=V20_BUNDLE_PATH)
    build_v20.add_argument("--results-path", type=Path, default=V20_RESULTS_MD)
    build_v20.set_defaults(func=run_build_v20_bit_binary_localmiss_hardscore_fusion)

    build_v21 = subparsers.add_parser(
        "build-v21-bit-binary-structured-promptlocal-fusion",
        help="Build the v21 structured/promptlocal fusion bit-binary bundle and tracked markdown ledger.",
    )
    build_v21.add_argument("--bundle-path", type=Path, default=V21_BUNDLE_PATH)
    build_v21.add_argument("--results-path", type=Path, default=V21_RESULTS_MD)
    build_v21.set_defaults(func=run_build_v21_bit_binary_structured_promptlocal_fusion)

    build_v22 = subparsers.add_parser(
        "build-v22-bit-binary-verified-precision-fusion",
        help="Build the v22 verified-precision fusion bit-binary bundle and tracked markdown ledger.",
    )
    build_v22.add_argument("--bundle-path", type=Path, default=V22_BUNDLE_PATH)
    build_v22.add_argument("--results-path", type=Path, default=V22_RESULTS_MD)
    build_v22.set_defaults(func=run_build_v22_bit_binary_verified_precision_fusion)

    watch_score_publish = subparsers.add_parser(
        "watch-score-publish",
        help="Watch completed local300 runs, rerun postprocess, and commit/push tracked score ledger updates safely.",
    )
    watch_score_publish.add_argument("--score-watch-log-path", type=Path, required=True)
    watch_score_publish.add_argument("--score-watch-state-dir", type=Path, required=True)
    watch_score_publish.add_argument("--score-watch-sleep-seconds", type=int, default=300)
    watch_score_publish.add_argument(
        "--postprocess-eval-kind",
        choices=("auto", "aopen", "adapter-validation"),
        default="adapter-validation",
    )
    watch_score_publish.add_argument(
        "--cleanup-completed-run-artifacts",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    watch_score_publish.add_argument(
        "--watch-run-root",
        action="append",
        default=[],
        type=Path,
    )
    watch_score_publish.set_defaults(func=run_watch_score_publish)

    watch_progress = subparsers.add_parser(
        "watch-progress-ledger",
        help="Watch training progress and checkpoint retention, then commit/push tracked ledger progress updates safely.",
    )
    watch_progress.add_argument("--progress-watch-log-path", type=Path, required=True)
    watch_progress.add_argument("--progress-watch-state-dir", type=Path, required=True)
    watch_progress.add_argument("--progress-watch-sleep-seconds", type=int, default=300)
    watch_progress.add_argument("--progress-watch-step-interval", type=int, default=5)
    watch_progress.add_argument(
        "--watch-run-root",
        action="append",
        default=[],
        type=Path,
    )
    watch_progress.set_defaults(func=run_watch_progress_ledger)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    csv.field_size_limit(sys.maxsize)
    main()
