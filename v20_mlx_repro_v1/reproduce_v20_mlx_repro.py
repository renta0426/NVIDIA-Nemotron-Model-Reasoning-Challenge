from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import math
import os
import platform
import re
import shutil
import socket
import sys
import time
import types
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
import pandas as pd
from mlx.nn.utils import average_gradients
from mlx.utils import tree_flatten, tree_map
from mlx_lm import batch_generate, generate, load as mlx_load
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.utils import linear_to_lora_layers, print_trainable_parameters
from mlx_lm.utils import save_config

REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = Path(__file__).resolve().parent
README_PATH = REPO_ROOT / "README.md"
AOPEN_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication"
AOPEN_NEMOTRON_ROOT = AOPEN_ROOT / "nemotron"
SNAPSHOT_ROOT = AOPEN_NEMOTRON_ROOT / "training" / "sft" / "04-08-16-14"
SNAPSHOT_CONFIG_PATH = SNAPSHOT_ROOT / "config.json"
SNAPSHOT_INDEX_PATH = SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
SNAPSHOT_TOKENS_ROOT = SNAPSHOT_ROOT / "tokens"
TRAIN_CSV_PATH = REPO_ROOT / "data" / "train.csv"
PROBLEMS_INDEX_PATH = AOPEN_NEMOTRON_ROOT / "problems.jsonl"

DEFAULT_MODEL_ROOT = Path(
    "/Users/mac-studio/.cache/huggingface/hub/models--mlx-community--NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16"
)
DEFAULT_OUTPUT_ROOT = WORK_ROOT / "outputs"
DEFAULT_RUN_NAME = "v20_mlx_repro_v1_fullrun"
DEFAULT_RESULTS_MD = WORK_ROOT / "v20_mlx_repro_v1-results.md"
DEFAULT_RESULTS_JSON = WORK_ROOT / "v20_mlx_repro_v1-results.json"

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


def build_user_message(prompt: str) -> str:
    prompt_text = str(prompt).strip()
    if not prompt_text:
        raise ValueError("Prompt must not be empty.")
    return f"{prompt_text}\n{BOXED_INSTRUCTION}"


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
) -> list[str]:
    prompts: list[str] = []
    for prompt_text in prompt_series:
        prompts.append(
            apply_chat_template_safe(
                tokenizer,
                [{"role": "user", "content": build_user_message(str(prompt_text))}],
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
                "problem_ids": [example.problem_id for example in step.examples],
                "categories": [example.category for example in step.examples],
                "token_paths": [example.token_path for example in step.examples],
            }
        )
    return rows


def default_lora_keys() -> list[str]:
    return [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "in_proj",
        "out_proj",
        "switch_mlp.fc1",
        "switch_mlp.fc2",
        "shared_experts.up_proj",
        "shared_experts.down_proj",
        "lm_head",
    ]


def build_training_manifest(args: argparse.Namespace, step_plan: Sequence[StepPlan], shadow_model_dir: Path) -> dict[str, Any]:
    optimizer_steps = len(step_plan)
    microsteps = sum(
        math.ceil(len(step.examples) / max(1, int(args.micro_batch_size))) for step in step_plan
    )
    return {
        "created_at": utc_now(),
        "repo_root": str(REPO_ROOT),
        "work_root": str(WORK_ROOT),
        "run_name": str(args.run_name),
        "run_root": str((Path(args.output_root).resolve() / args.run_name).resolve()),
        "shadow_model_dir": str(shadow_model_dir.resolve()),
        "snapshot_root": str(SNAPSHOT_ROOT.resolve()),
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
    write_text(
        artifacts.run_root / "train_cmd.sh",
        "\n".join(
            [
                "#!/bin/bash",
                "set -euo pipefail",
                f'"{sys.executable}" "{Path(__file__).resolve()}" train --output-root "{Path(args.output_root).resolve()}" --run-name "{args.run_name}"',
                "",
            ]
        ),
    )
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
    mask = mx.logical_and(steps >= lengths[:, 0:1], steps <= lengths[:, 1:])
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
) -> tuple[mx.array, mx.array]:
    loaded: list[tuple[list[int], int, int]] = []
    max_length = 0
    for example in examples:
        tokens, _ = read_snapshot_token_file(Path(example.token_path))
        truncated_length = min(len(tokens), max_seq_length)
        max_length = max(max_length, truncated_length)
        loaded.append((tokens, min(example.prompt_length, truncated_length), truncated_length))

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
    return {
        "model": str(shadow_model_dir),
        "train": True,
        "fine_tune_type": "lora",
        "optimizer": "adam",
        "optimizer_config": {"adam": {}, "adamw": {}, "muon": {}, "sgd": {}, "adafactor": {}},
        "data": str(SNAPSHOT_ROOT),
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
        "v20_effective_batch_size": int(args.batch_size),
        "v20_micro_batch_size": int(args.micro_batch_size),
        "v20_optimizer_steps": int(total_steps),
        "v20_schedule_formula": "learning_rate * (1 - step / total_steps)",
    }


def save_adapter_weights(adapter_dir: Path, file_name: str, model: Any) -> Path:
    ensure_dir(adapter_dir)
    adapter_path = adapter_dir / file_name
    adapter_weights = dict(tree_flatten(model.trainable_parameters()))
    mx.save_safetensors(str(adapter_path), adapter_weights)
    return adapter_path


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


def load_category_map() -> dict[str, str]:
    rows = load_jsonl(PROBLEMS_INDEX_PATH)
    return {str(row["id"]): str(row["category"]) for row in rows}


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


def run_train(args: argparse.Namespace) -> dict[str, Any]:
    artifacts = prepare_run(args)
    step_plan = load_step_plan(artifacts.step_plan_path)
    if not step_plan:
        raise RuntimeError("Empty step plan.")
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

    schedule = build_v20_lr_schedule(total_optimizer_steps, float(args.learning_rate))
    optimizer = optim.Adam(
        learning_rate=schedule,
        betas=[float(args.beta1), float(args.beta2)],
        eps=float(args.eps),
        bias_correction=bool(args.bias_correction),
    )

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
        grad_accum = None
        weighted_loss_total = 0.0
        token_total = 0

        for microbatch_index, micro_examples in enumerate(microbatches):
            batch_array, lengths_array = build_microbatch_arrays(
                micro_examples,
                micro_batch_size=int(args.micro_batch_size),
                max_seq_length=int(args.max_seq_length),
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
            f"tokens={token_total} elapsed={elapsed:.2f}s"
        )

        if int(args.save_every_steps) > 0 and (optimizer_step_index + 1) % int(args.save_every_steps) == 0:
            save_adapter_weights(artifacts.adapter_dir, f"{optimizer_step_index + 1:07d}_adapters.safetensors", model)

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
        "snapshot_contract_path": str(artifacts.snapshot_contract_path.resolve()),
        "step_plan_path": str(artifacts.step_plan_path.resolve()),
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
    model, tokenizer = load_model_for_eval(model_root, adapter_dir, lazy_load=bool(args.lazy_load))

    benchmark_rows = load_training_rows()
    if int(args.eval_limit) > 0:
        benchmark_rows = benchmark_rows[: int(args.eval_limit)]
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

    records: list[dict[str, Any]] = []
    total_prompts = len(prompt_tokens)
    progress_path = run_root / "aopen_eval" / "benchmark_eval_progress.json"
    ensure_dir(progress_path.parent)

    for chunk_start in range(0, total_prompts, chunk_size):
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

        for row, rendered_prompt, raw_output in zip(chunk_rows, chunk_rendered_prompts, chunk_outputs):
            derived = analyze_raw_output(str(raw_output))
            prediction = str(derived["extracted_answer"])
            problem_id = str(row["id"])
            category = category_map.get(problem_id, "")
            is_correct = verify_answer(str(row["answer"]), prediction)
            records.append(
                {
                    "id": problem_id,
                    "category": category,
                    "expected_answer": str(row["answer"]),
                    "rendered_prompt": rendered_prompt,
                    "raw_output": str(raw_output),
                    "extracted_answer": prediction,
                    "is_correct": is_correct,
                    "fallback_type": derived["fallback_type"],
                    "format_bucket": derived["format_bucket"],
                    "has_boxed": derived["has_boxed"],
                    "boxed_count": derived["boxed_count"],
                }
            )

        rows_completed = min(chunk_start + len(chunk_prompts), total_prompts)
        progress_payload = {
            "created_at": utc_now(),
            "status": "running",
            "rows_total": total_prompts,
            "rows_completed": rows_completed,
            "chunk_size": chunk_size,
            "max_tokens": int(args.max_tokens),
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "max_num_seqs": int(args.max_num_seqs),
        }
        write_json(progress_path, progress_payload)
        print(f"Eval progress: {rows_completed}/{total_prompts}")

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

    summary = summarize_benchmark_scores(scored_rows)
    payload = {
        "created_at": utc_now(),
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
        "v20_target_training_set_accuracy": V20_TARGETS["overall_accuracy"],
        **summary,
    }
    write_eval_outputs(
        output_root=run_root / "aopen_eval",
        evaluation_name="aopen_train_csv_full",
        records=records,
        scored_rows=scored_rows,
        payload=payload,
    )
    write_json(progress_path, {"created_at": utc_now(), "status": "complete", "rows_total": total_prompts, "rows_completed": total_prompts})
    return payload


def render_results_markdown(run_result: dict[str, Any], eval_result: dict[str, Any]) -> str:
    overall = eval_result["overall"]
    lines = [
        "# v20_mlx_repro_v1 results",
        "",
        "> Repository note: canonical challenge contract lives in `README.md`.",
        "> This version is a local MLX reproduction of A-Open v20 using `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/` as the exact training snapshot.",
        "> It does **not** claim submission.zip parity; it measures how closely MLX reproduces the published v20 training/eval behavior.",
        "",
        "## Source contract",
        "",
        f"- Top-level README: `{relative_to_repo(README_PATH)}`",
        f"- A-Open README: `{relative_to_repo(AOPEN_ROOT / 'README.md')}`",
        f"- Data strategy: `{relative_to_repo(AOPEN_ROOT / 'データ戦略を理解する.md')}`",
        f"- SFT pipeline: `{relative_to_repo(AOPEN_ROOT / '学習SFTパイプライン.md')}`",
        f"- V20 snapshot: `{relative_to_repo(SNAPSHOT_ROOT)}`",
        "",
        "## Run summary",
        "",
        f"- run_root: `{run_result['run_root']}`",
        f"- shadow_model_dir: `{run_result['shadow_model_dir']}`",
        f"- adapter_dir: `{run_result['adapter_dir']}`",
        f"- snapshot_contract_path: `{run_result['snapshot_contract_path']}`",
        "",
        "## Training settings",
        "",
        f"- backend: `mlx`",
        f"- optimizer_steps: `{run_result['latest_train_report']['step']}`",
        f"- last_train_loss: `{run_result['latest_train_report']['train_loss']}`",
        f"- last_lr: `{run_result['latest_train_report']['lr']}`",
        "",
        "## A-Open eval result",
        "",
        f"- overall_accuracy: `{overall['accuracy']}` ({overall['correct']}/{overall['total']})",
        f"- v20_target_training_set_accuracy: `{V20_TARGETS['overall_accuracy']}` ({V20_TARGETS['overall_correct']}/{V20_TARGETS['overall_total']})",
        f"- delta_vs_v20_target: `{round(float(overall['accuracy']) - float(V20_TARGETS['overall_accuracy']), 6)}`",
        "",
        "| category | reproduced_correct | reproduced_total | reproduced_accuracy | v20_correct | v20_total | v20_accuracy |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    eval_by_category = {row["category"]: row for row in eval_result["categories"]}
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
            "- MLX-specific assumptions not explicit in the public v20 config: `lora_alpha = 32`, `lora_dropout = 0.0`, `Adam bias_correction = True`.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def update_results_files(args: argparse.Namespace, run_result: dict[str, Any], eval_result: dict[str, Any]) -> None:
    results_payload = {
        "created_at": utc_now(),
        "run_result": run_result,
        "eval_result": eval_result,
    }
    write_json(DEFAULT_RESULTS_JSON, results_payload)
    write_text(DEFAULT_RESULTS_MD, render_results_markdown(run_result, eval_result))


def run_full(args: argparse.Namespace) -> dict[str, Any]:
    run_result = run_train(args)
    eval_result = run_eval_aopen(args)
    update_results_files(args, run_result, eval_result)
    return {
        "run_result": run_result,
        "eval_result": eval_result,
        "results_md": str(DEFAULT_RESULTS_MD.resolve()),
        "results_json": str(DEFAULT_RESULTS_JSON.resolve()),
    }


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
        target.add_argument("--force-shadow-model", action="store_true")
        target.add_argument("--seed", type=int, default=123)
        target.add_argument("--batch-size", type=int, default=32, help="Effective optimizer batch size.")
        target.add_argument("--micro-batch-size", type=int, default=16)
        target.add_argument("--learning-rate", type=float, default=2e-4)
        target.add_argument("--max-seq-length", type=int, default=8192)
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
        target.add_argument("--resume-adapter-file", type=Path, default=None)
        target.add_argument("--max-optimizer-steps", type=int, default=0)
        target.add_argument("--max-tokens", type=int, default=README_EVAL_CONTRACT["max_tokens"])
        target.add_argument("--temperature", type=float, default=README_EVAL_CONTRACT["temperature"])
        target.add_argument("--top-p", type=float, default=README_EVAL_CONTRACT["top_p"])
        target.add_argument("--max-num-seqs", type=int, default=16)
        target.add_argument("--max-model-len", type=int, default=README_EVAL_CONTRACT["max_model_len"])
        target.add_argument("--prompt-chunk-size", type=int, default=16)
        target.add_argument("--prefill-batch-size", type=int, default=8)
        target.add_argument("--completion-batch-size", type=int, default=8)
        target.add_argument("--eval-limit", type=int, default=0)
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

    prepare = subparsers.add_parser("prepare", help="Prepare the v20 snapshot contract, shadow model, and run manifest.")
    add_shared_args(prepare)
    prepare.set_defaults(func=run_prepare)

    train = subparsers.add_parser("train", help="Prepare if needed, then train the MLX LoRA adapter on the exact v20 snapshot.")
    add_shared_args(train)
    train.set_defaults(func=run_train)

    eval_aopen = subparsers.add_parser("eval-aopen", help="Run A-Open-style evaluation on data/train.csv using the trained adapter.")
    add_shared_args(eval_aopen)
    eval_aopen.set_defaults(func=run_eval_aopen)

    full = subparsers.add_parser("full-run", help="Prepare, train, evaluate, and update the tracked results files.")
    add_shared_args(full)
    full.set_defaults(func=run_full)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    csv.field_size_limit(sys.maxsize)
    main()
