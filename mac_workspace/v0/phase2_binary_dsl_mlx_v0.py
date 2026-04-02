from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata as importlib_metadata
import json
import math
import os
import random
import shutil
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_ROOT = Path(__file__).resolve().parent

DEFAULT_MODEL_ROOT = Path(
    "/Users/mac-studio/.cache/huggingface/hub/models--mlx-community--NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16"
)
DEFAULT_TRAIN_CSV = (
    REPO_ROOT
    / "baseline"
    / "cot"
    / "phase2_binary_dsl"
    / "artifacts"
    / "phase2_binary_hybrid_training_data.csv"
)
DEFAULT_PHASE0_PREBUILT_ROOT = REPO_ROOT / "baseline" / "cot" / "phase0_offline_eval" / "artifacts"
DEFAULT_PHASE0_ANALYSIS_CSV = (
    REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
)
DEFAULT_OUTPUT_ROOT = WORK_ROOT / "outputs"
DEFAULT_RUN_NAME = "phase2_binary_hybrid_mlx_v0"
TRAIN_PROFILE_CHOICES = (
    "baseline",
    "single-adapter-focus-v1",
    "single-adapter-focus-v2",
)

BOXED_INSTRUCTION = r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
EXPECTED_PHASE2_COLUMNS = [
    "id",
    "prompt",
    "answer",
    "generated_cot",
    "label",
    "assistant_style",
    "source_selection_tier",
]
EXPECTED_PHASE2_ROWS = 900

README_MAX_LORA_RANK = 32
README_MAX_TOKENS = 7680
README_TOP_P = 1.0
README_TEMPERATURE = 0.0
README_MAX_NUM_SEQS = 64
README_MAX_MODEL_LEN = 8192

GENERAL_STABLE_QUOTAS = {
    "gravity_constant": 50,
    "unit_conversion": 50,
    "roman_numeral": 50,
    "text_decryption": 50,
}
BINARY_HARD_TIER_QUOTAS = {
    "verified_trace_ready": 20,
    "answer_only_keep": 20,
    "manual_audit_priority": 20,
}
SYMBOL_WATCH_TARGETS = [
    ("numeric_2x2", "verified_trace_ready", 15),
    ("numeric_2x2", "answer_only_keep", 15),
    ("numeric_2x2", "manual_audit_priority", 10),
    ("glyph_len5", "manual_audit_priority", 20),
]
HOLDOUT_FOLDS = 5
BOXED_PATTERN = __import__("re").compile(r"\\boxed\{([^}]*)(?:\}|$)")
FINAL_ANSWER_PATTERNS = (
    r"The final answer is:\s*([^\n]+)",
    r"Final answer is:\s*([^\n]+)",
    r"Final answer\s*[:：]\s*([^\n]+)",
    r"final answer\s*[:：]\s*([^\n]+)",
)
NUMBER_PATTERN = __import__("re").compile(r"-?\d+(?:\.\d+)?")
BIT8_PATTERN = __import__("re").compile(r"^[01]{8}$")
FAMILY_SHORT = {
    "gravity_constant": "gravity",
    "unit_conversion": "unit",
    "roman_numeral": "roman",
    "text_decryption": "text",
    "bit_manipulation": "binary",
    "symbol_equation": "symbol",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, *, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_jsonl_records(path: Path, records: Sequence[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def parse_float(value: Any, default: float | None = None) -> float | None:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def stable_mod(text: str, mod: int) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % mod


def prompt_len_bucket(length: int) -> str:
    if length < 300:
        return "<300"
    if length < 400:
        return "300-399"
    if length < 500:
        return "400-499"
    if length < 600:
        return "500-599"
    return "600+"


def load_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("mlx-lm", "mlx", "transformers", "pyyaml"):
        try:
            versions[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def resolve_hf_snapshot(model_root: Path) -> Path:
    model_root = model_root.expanduser().resolve()
    if (model_root / "config.json").exists():
        return model_root
    snapshots_dir = model_root / "snapshots"
    if not snapshots_dir.exists():
        raise FileNotFoundError(
            f"Model root must contain config.json or snapshots/: {model_root}"
        )
    main_ref = model_root / "refs" / "main"
    if main_ref.exists():
        snapshot_name = main_ref.read_text(encoding="utf-8").strip()
        candidate = snapshots_dir / snapshot_name
        if candidate.exists():
            return candidate
    snapshots = sorted(path for path in snapshots_dir.iterdir() if path.is_dir())
    if not snapshots:
        raise FileNotFoundError(f"No snapshots found under: {snapshots_dir}")
    return snapshots[-1]


def build_shadow_model_dir(model_root: Path, shadow_dir: Path, *, force: bool = False) -> Path:
    source_snapshot = resolve_hf_snapshot(model_root)
    manifest_path = shadow_dir / "shadow_manifest.json"
    current_manifest = load_json(manifest_path, default={}) or {}
    tokenizer_config_path = shadow_dir / "tokenizer_config.json"
    rebuild = force
    if not shadow_dir.exists():
        rebuild = True
    elif current_manifest.get("source_snapshot") != str(source_snapshot):
        rebuild = True
    elif not tokenizer_config_path.exists():
        rebuild = True
    else:
        try:
            tokenizer_config = json.loads(tokenizer_config_path.read_text(encoding="utf-8"))
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
        tokenizer_config = json.loads(
            (source_snapshot / "tokenizer_config.json").read_text(encoding="utf-8")
        )
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


def load_phase2_training_rows(path: Path) -> list[dict[str, str]]:
    rows = load_csv_rows(path)
    if len(rows) != EXPECTED_PHASE2_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_PHASE2_ROWS} rows in {path}, found {len(rows)}"
        )
    if rows:
        actual_columns = list(rows[0].keys())
        if actual_columns != EXPECTED_PHASE2_COLUMNS:
            raise ValueError(
                f"Unexpected CSV columns in {path}: {actual_columns} "
                f"(expected {EXPECTED_PHASE2_COLUMNS})"
            )
    return rows


def build_user_message(prompt: str) -> str:
    return f"{prompt}\n{BOXED_INSTRUCTION}"


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
    except Exception:
        rendered: list[str] = []
        for message in messages:
            rendered.append(f"<|{message['role']}|>\n{message['content']}")
        if add_generation_prompt:
            rendered.append("<|assistant|>\n<think>")
        return "\n".join(rendered)


def find_token_index_for_text_span(tokenizer: Any, full_text: str, target_text: str) -> int:
    if not target_text:
        raise ValueError("Cannot compute token offset for empty target text.")
    char_start = full_text.find(target_text)
    if char_start < 0:
        preview = full_text[:200].replace("\n", "\\n")
        target_preview = target_text[:120].replace("\n", "\\n")
        raise ValueError(
            f"Target text span was not found in rendered chat. target={target_preview!r} rendered_prefix={preview!r}"
        )
    offset_tokenizer = tokenizer if callable(tokenizer) else getattr(tokenizer, "_tokenizer", None)
    if offset_tokenizer is None or not callable(offset_tokenizer):
        raise TypeError(f"Tokenizer does not support text encoding for offset mapping: {type(tokenizer)!r}")
    encoded = offset_tokenizer(
        full_text,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    for token_index, (start, end) in enumerate(encoded["offset_mapping"]):
        if start <= char_start < end or (start == end == char_start):
            return token_index
    raise ValueError(f"Unable to map assistant char offset {char_start} to a token offset.")


def maybe_patch_mlx_chat_dataset_enable_thinking() -> None:
    import mlx_lm.tuner.datasets as tuner_datasets

    if getattr(tuner_datasets, "_nemotron_enable_thinking_patch", False):
        return

    original_chat_init = tuner_datasets.ChatDataset.__init__
    original_completions_init = tuner_datasets.CompletionsDataset.__init__

    def patched_chat_init(
        self: Any,
        data: list[dict[str, Any]],
        tokenizer: Any,
        chat_key: str = "messages",
        mask_prompt: bool = False,
        enable_thinking: bool = False,
    ) -> None:
        original_chat_init(
            self,
            data=data,
            tokenizer=tokenizer,
            chat_key=chat_key,
            mask_prompt=mask_prompt,
        )
        self.enable_thinking = bool(enable_thinking)

    def patched_chat_process(self: Any, row: dict[str, Any]) -> tuple[list[int], int]:
        messages = row[self.chat_key]
        tools = row.get("tools", None)
        try:
            tokens = self.tokenizer.apply_chat_template(
                messages,
                tools=tools,
                enable_thinking=self.enable_thinking,
            )
        except TypeError:
            tokens = self.tokenizer.apply_chat_template(messages, tools=tools)
        if not self.mask_prompt:
            return (tokens, 0)
        if messages[-1].get("role") != "assistant":
            raise ValueError("mask_prompt=True requires the last chat message to have role='assistant'.")
        full_text = apply_chat_template_safe(
            self.tokenizer,
            messages,
            add_generation_prompt=False,
            enable_thinking=self.enable_thinking,
        )
        offset = find_token_index_for_text_span(
            self.tokenizer,
            full_text,
            str(messages[-1].get("content", "")),
        )
        return (tokens, offset)

    def patched_completions_init(
        self: Any,
        data: list[dict[str, Any]],
        tokenizer: Any,
        prompt_key: str,
        completion_key: str,
        mask_prompt: bool,
        enable_thinking: bool = False,
    ) -> None:
        original_completions_init(
            self,
            data=data,
            tokenizer=tokenizer,
            prompt_key=prompt_key,
            completion_key=completion_key,
            mask_prompt=mask_prompt,
        )
        self.enable_thinking = bool(enable_thinking)

    def patched_completions_process(self: Any, row: dict[str, Any]) -> tuple[list[int], int]:
        tools = row.get("tools", None)
        messages = [
            {"role": "user", "content": row[self.prompt_key]},
            {"role": "assistant", "content": row[self.completion_key]},
        ]
        try:
            tokens = self.tokenizer.apply_chat_template(
                messages,
                tools=tools,
                enable_thinking=self.enable_thinking,
            )
        except TypeError:
            tokens = self.tokenizer.apply_chat_template(messages, tools=tools)
        if not self.mask_prompt:
            return (tokens, 0)
        full_text = apply_chat_template_safe(
            self.tokenizer,
            messages,
            add_generation_prompt=False,
            enable_thinking=self.enable_thinking,
        )
        offset = find_token_index_for_text_span(
            self.tokenizer,
            full_text,
            str(row[self.completion_key]),
        )
        return (tokens, offset)

    def patched_create_dataset(data: Any, tokenizer: Any, config: Any) -> Any:
        mask_prompt = getattr(config, "mask_prompt", False)
        prompt_feature = getattr(config, "prompt_feature", "prompt")
        text_feature = getattr(config, "text_feature", "text")
        completion_feature = getattr(config, "completion_feature", "completion")
        chat_feature = getattr(config, "chat_feature", "messages")
        enable_thinking = getattr(config, "enable_thinking", False)
        sample = data[0]
        if prompt_feature in sample and completion_feature in sample:
            return tuner_datasets.CompletionsDataset(
                data,
                tokenizer,
                prompt_feature,
                completion_feature,
                mask_prompt,
                enable_thinking,
            )
        if chat_feature in sample:
            return tuner_datasets.ChatDataset(
                data,
                tokenizer,
                chat_key=chat_feature,
                mask_prompt=mask_prompt,
                enable_thinking=enable_thinking,
            )
        if text_feature in sample:
            if mask_prompt:
                raise ValueError("Prompt masking not supported for text dataset.")
            return tuner_datasets.TextDataset(data, tokenizer, text_key=text_feature)
        raise ValueError(
            "Unsupported data format, check the supported formats here:\n"
            "https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md#Data."
        )

    tuner_datasets.ChatDataset.__init__ = patched_chat_init
    tuner_datasets.ChatDataset.process = patched_chat_process
    tuner_datasets.CompletionsDataset.__init__ = patched_completions_init
    tuner_datasets.CompletionsDataset.process = patched_completions_process
    tuner_datasets.create_dataset = patched_create_dataset
    tuner_datasets._nemotron_enable_thinking_patch = True


def render_assistant_message(row: dict[str, str]) -> str:
    style = str(row.get("assistant_style", "")).strip()
    answer = str(row.get("answer", "")).strip()
    generated_cot = str(row.get("generated_cot", "")).strip()
    if style == "trace_boxed":
        if not generated_cot:
            raise ValueError(f"trace_boxed row {row.get('id', '')} is missing generated_cot")
        return f"{generated_cot}\n\n\\boxed{{{answer}}}"
    if style == "boxed_only":
        return f"\\boxed{{{answer}}}"
    raise ValueError(f"Unsupported assistant_style: {style}")


def clone_phase2_row(row: dict[str, str]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value) for key, value in row.items()}


def summarize_phase2_rows(rows: Sequence[dict[str, str]]) -> dict[str, Any]:
    by_label = Counter(str(row.get("label", "")).strip() or "unknown" for row in rows)
    by_label_and_style = Counter(
        (
            str(row.get("label", "")).strip() or "unknown",
            str(row.get("assistant_style", "")).strip() or "unknown",
        )
        for row in rows
    )
    by_label_and_tier = Counter(
        (
            str(row.get("label", "")).strip() or "unknown",
            str(row.get("source_selection_tier", "")).strip() or "unknown",
        )
        for row in rows
    )
    return {
        "rows": len(rows),
        "by_label": {label: count for label, count in sorted(by_label.items())},
        "by_label_and_style": {
            f"{label}|{style}": count
            for (label, style), count in sorted(by_label_and_style.items())
        },
        "by_label_and_tier": {
            f"{label}|{tier}": count
            for (label, tier), count in sorted(by_label_and_tier.items())
        },
    }


def apply_phase2_train_profile(
    rows: Sequence[dict[str, str]],
    *,
    profile: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    normalized_profile = str(profile).strip().lower() or "baseline"
    input_rows = [clone_phase2_row(row) for row in rows]
    if normalized_profile == "baseline":
        summary = summarize_phase2_rows(input_rows)
        return input_rows, {
            "profile": normalized_profile,
            "input": summary,
            "output": summary,
            "transform_counts": {},
        }
    if normalized_profile not in TRAIN_PROFILE_CHOICES:
        raise ValueError(f"Unsupported train profile: {profile}")

    profiled_rows: list[dict[str, str]] = []
    transform_counts: Counter[str] = Counter()
    for original_row in input_rows:
        row = clone_phase2_row(original_row)
        label = str(row.get("label", "")).strip().lower()
        tier = str(row.get("source_selection_tier", "")).strip().lower()
        style = str(row.get("assistant_style", "")).strip().lower()
        if label in {"roman", "text"}:
            transform_counts[f"drop:{label}"] += 1
            continue
        if label in {"binary", "symbol"}:
            if style != "boxed_only":
                row["assistant_style"] = "boxed_only"
                transform_counts[f"force_boxed_only:{label}:{tier or 'unknown'}"] += 1
            else:
                transform_counts[f"keep_boxed_only:{label}:{tier or 'unknown'}"] += 1
        else:
            transform_counts[f"keep:{label}:{style or 'unknown'}"] += 1
        profiled_rows.append(row)
        if (
            normalized_profile == "single-adapter-focus-v2"
            and label in {"binary", "symbol"}
            and tier == "answer_only_keep"
        ):
            profiled_rows.append(clone_phase2_row(row))
            transform_counts[f"repeat:{label}:{tier}"] += 1
    if not profiled_rows:
        raise ValueError(f"Train profile {profile} removed all training rows.")
    return profiled_rows, {
        "profile": normalized_profile,
        "input": summarize_phase2_rows(input_rows),
        "output": summarize_phase2_rows(profiled_rows),
        "transform_counts": {
            name: count for name, count in sorted(transform_counts.items())
        },
    }


def build_phase2_chat_records(rows: Sequence[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        prompt = str(row.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Row {row.get('id', '')} is missing prompt")
        assistant_content = render_assistant_message(row)
        records.append(
            {
                "messages": [
                    {"role": "user", "content": build_user_message(prompt)},
                    {"role": "assistant", "content": assistant_content},
                ],
                "metadata": {
                    "id": row.get("id", ""),
                    "answer": row.get("answer", ""),
                    "label": row.get("label", ""),
                    "assistant_style": row.get("assistant_style", ""),
                    "source_selection_tier": row.get("source_selection_tier", ""),
                },
            }
        )
    return records


def build_phase2_completion_records(rows: Sequence[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        prompt = str(row.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Row {row.get('id', '')} is missing prompt")
        records.append(
            {
                "prompt": build_user_message(prompt),
                "completion": render_assistant_message(row),
                "metadata": {
                    "id": row.get("id", ""),
                    "answer": row.get("answer", ""),
                    "label": row.get("label", ""),
                    "assistant_style": row.get("assistant_style", ""),
                    "source_selection_tier": row.get("source_selection_tier", ""),
                },
            }
        )
    return records


def build_phase2_text_records(rows: Sequence[dict[str, str]], *, tokenizer: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        prompt = str(row.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Row {row.get('id', '')} is missing prompt")
        user_message = build_user_message(prompt)
        assistant_message = render_assistant_message(row)
        full_text = apply_chat_template_safe(
            tokenizer,
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ],
            add_generation_prompt=False,
            enable_thinking=True,
        )
        records.append(
            {
                "text": full_text,
                "metadata": {
                    "id": row.get("id", ""),
                    "answer": row.get("answer", ""),
                    "label": row.get("label", ""),
                    "assistant_style": row.get("assistant_style", ""),
                    "source_selection_tier": row.get("source_selection_tier", ""),
                },
            }
        )
    return records


def select_shadow_validation_records(
    records: Sequence[dict[str, Any]],
    *,
    valid_rows: int,
    minimum_rows: int,
    seed: int,
) -> list[dict[str, Any]]:
    if not records:
        raise ValueError("Training records are empty")
    valid_rows = max(1, valid_rows, minimum_rows)
    valid_rows = min(valid_rows, len(records))
    rng = random.Random(seed)
    chosen = sorted(rng.sample(range(len(records)), valid_rows))
    return [records[index] for index in chosen]


def compute_total_iters(num_rows: int, num_epochs: float, batch_size: int) -> int:
    effective_rows = max(1, num_rows)
    return max(1, int(effective_rows * num_epochs // max(batch_size, 1)))


def build_mlx_lora_config(
    *,
    model_path: Path,
    dataset_dir: Path,
    adapter_dir: Path,
    mask_prompt: bool,
    enable_thinking: bool,
    batch_size: int,
    num_epochs: float,
    learning_rate: float,
    max_seq_length: int,
    grad_accumulation_steps: int,
    lora_rank: int,
    lora_scale: float,
    lora_dropout: float,
    num_layers: int,
    steps_per_report: int,
    steps_per_eval: int,
    seed: int,
) -> dict[str, Any]:
    total_iters = compute_total_iters(
        num_rows=sum(1 for _ in (dataset_dir / "train.jsonl").open("r", encoding="utf-8")),
        num_epochs=num_epochs,
        batch_size=batch_size,
    )
    return {
        "model": str(model_path),
        "train": True,
        "data": str(dataset_dir),
        "fine_tune_type": "lora",
        "optimizer": "adamw",
        "mask_prompt": mask_prompt,
        "enable_thinking": enable_thinking,
        "num_layers": num_layers,
        "batch_size": batch_size,
        "iters": total_iters,
        "val_batches": -1,
        "learning_rate": learning_rate,
        "steps_per_report": steps_per_report,
        "steps_per_eval": steps_per_eval,
        "grad_accumulation_steps": grad_accumulation_steps,
        "adapter_path": str(adapter_dir),
        "save_every": total_iters,
        "max_seq_length": max_seq_length,
        "grad_checkpoint": True,
        "seed": seed,
        "lora_parameters": {
            "rank": lora_rank,
            "dropout": lora_dropout,
            "scale": lora_scale,
        },
    }


def render_train_command(config_path: Path) -> str:
    return "\n".join(
        [
            "#!/bin/bash",
            "set -euo pipefail",
            f'"{sys.executable}" "{Path(__file__).resolve()}" train-mlx-config --config "{config_path}"',
            "",
        ]
    )


def summarize_directory(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for child in sorted(path.iterdir()):
        rows.append(
            {
                "name": child.name,
                "is_dir": child.is_dir(),
                "size_bytes": child.stat().st_size if child.is_file() else 0,
            }
        )
    return rows


def prepare_training_run(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    shadow_model_dir = build_shadow_model_dir(
        Path(args.model_root),
        run_root / "shadow_model",
        force=bool(args.force_shadow_model),
    )
    source_rows = load_phase2_training_rows(Path(args.train_csv))
    profiled_rows, profile_summary = apply_phase2_train_profile(
        source_rows,
        profile=str(args.train_profile),
    )
    dataset_format = str(args.dataset_format).strip().lower()
    if dataset_format == "completions":
        dataset_format = "completion"
    if dataset_format not in {"chat", "completion", "text"}:
        raise ValueError(f"Unsupported dataset_format: {dataset_format}")
    if dataset_format == "chat":
        train_records = build_phase2_chat_records(profiled_rows)
        mask_prompt = True
        enable_thinking = True
    elif dataset_format == "completion":
        train_records = build_phase2_completion_records(profiled_rows)
        mask_prompt = True
        enable_thinking = True
    else:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(str(shadow_model_dir), trust_remote_code=True)
        if tokenizer.pad_token is None and tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token
        train_records = build_phase2_text_records(profiled_rows, tokenizer=tokenizer)
        mask_prompt = False
        enable_thinking = False
    valid_records = select_shadow_validation_records(
        train_records,
        valid_rows=int(args.valid_shadow_rows),
        minimum_rows=int(args.batch_size),
        seed=int(args.seed),
    )

    dataset_dir = run_root / "dataset"
    adapter_dir = run_root / "adapter"
    write_jsonl_records(dataset_dir / "train.jsonl", train_records)
    write_jsonl_records(dataset_dir / "valid.jsonl", valid_records)
    test_path = dataset_dir / "test.jsonl"
    if test_path.exists():
        test_path.unlink()

    config = build_mlx_lora_config(
        model_path=shadow_model_dir,
        dataset_dir=dataset_dir,
        adapter_dir=adapter_dir,
        mask_prompt=mask_prompt,
        enable_thinking=enable_thinking,
        batch_size=int(args.batch_size),
        num_epochs=float(args.num_epochs),
        learning_rate=float(args.learning_rate),
        max_seq_length=int(args.max_seq_length),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        lora_rank=int(args.lora_rank),
        lora_scale=float(args.lora_alpha),
        lora_dropout=float(args.lora_dropout),
        num_layers=int(args.num_layers),
        steps_per_report=int(args.steps_per_report),
        steps_per_eval=int(args.steps_per_eval),
        seed=int(args.seed),
    )

    config_path = run_root / "mlx_lora_config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    command_path = run_root / "train_cmd.sh"
    command_path.write_text(render_train_command(config_path), encoding="utf-8")

    manifest = {
        "created_at": utc_now(),
        "repo_root": str(REPO_ROOT),
        "run_root": str(run_root),
        "model_root": str(Path(args.model_root).resolve()),
        "shadow_model_dir": str(shadow_model_dir),
        "train_csv": str(Path(args.train_csv).resolve()),
        "phase2_rows": len(source_rows),
        "training_profile": profile_summary,
        "dataset": {
            "dataset_dir": str(dataset_dir),
            "dataset_format": dataset_format,
            "enable_thinking": enable_thinking,
            "train_rows": len(train_records),
            "valid_rows": len(valid_records),
            "valid_strategy": f"shadow_sample={int(args.valid_shadow_rows)}",
        },
        "training": {
            "mask_prompt": mask_prompt,
            "batch_size": int(args.batch_size),
            "grad_accumulation_steps": int(args.grad_accumulation_steps),
            "num_epochs": float(args.num_epochs),
            "learning_rate": float(args.learning_rate),
            "max_seq_length": int(args.max_seq_length),
            "lora_rank": int(args.lora_rank),
            "lora_alpha": float(args.lora_alpha),
            "lora_dropout": float(args.lora_dropout),
            "num_layers": int(args.num_layers),
            "steps_per_report": int(args.steps_per_report),
            "steps_per_eval": int(args.steps_per_eval),
            "total_iters": int(config["iters"]),
        },
        "versions": load_versions(),
        "artifacts": {
            "config_path": str(config_path),
            "command_path": str(command_path),
            "adapter_dir": str(adapter_dir),
        },
    }
    write_json(run_root / "prepare_manifest.json", manifest)
    return manifest


def verify_training_outputs(adapter_dir: Path) -> None:
    required = [
        adapter_dir / "adapter_config.json",
        adapter_dir / "adapters.safetensors",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "MLX training did not produce expected adapter files: " + ", ".join(missing)
        )


def benchmark_columns() -> list[str]:
    return [
        "benchmark_name",
        "benchmark_role",
        "id",
        "family",
        "family_short",
        "template_subtype",
        "selection_tier",
        "teacher_solver_candidate",
        "answer_type",
        "num_examples",
        "prompt_len_chars",
        "hard_score",
        "group_signature",
        "query_raw",
        "answer",
        "prompt",
    ]


def normalize_family_label(row: dict[str, str]) -> str:
    family = row.get("family", "")
    if family in FAMILY_SHORT:
        return FAMILY_SHORT[family]
    label = row.get("label", "")
    if label:
        return label
    return family


def to_benchmark_row(
    row: dict[str, str],
    *,
    benchmark_name: str,
    benchmark_role: str,
) -> dict[str, Any]:
    return {
        "benchmark_name": benchmark_name,
        "benchmark_role": benchmark_role,
        "id": row.get("id", ""),
        "family": row.get("family", ""),
        "family_short": normalize_family_label(row),
        "template_subtype": row.get("template_subtype", ""),
        "selection_tier": row.get("selection_tier", ""),
        "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
        "answer_type": row.get("answer_type", ""),
        "num_examples": parse_int(row.get("num_examples"), 0),
        "prompt_len_chars": parse_int(row.get("prompt_len_chars"), 0),
        "hard_score": parse_float(row.get("hard_score"), 0.0),
        "group_signature": row.get("group_signature", ""),
        "query_raw": row.get("query_raw", ""),
        "answer": row.get("answer", ""),
        "prompt": row.get("prompt", ""),
    }


def score_rank_low(row: dict[str, str]) -> tuple[Any, ...]:
    hard_score = parse_float(row.get("hard_score"), 999.0)
    if hard_score is None:
        hard_score = 999.0
    return (
        hard_score,
        parse_int(row.get("prompt_len_chars"), 99999),
        -parse_int(row.get("num_examples"), 0),
        row.get("id", ""),
    )


def score_rank_high(row: dict[str, str]) -> tuple[Any, ...]:
    hard_score = parse_float(row.get("hard_score"), -999.0)
    if hard_score is None:
        hard_score = -999.0
    return (
        -hard_score,
        -parse_int(row.get("prompt_len_chars"), 0),
        -parse_int(row.get("num_examples"), 0),
        row.get("id", ""),
    )


def balanced_take(
    rows: list[dict[str, str]],
    *,
    quota: int,
    group_keys: Sequence[str],
    hard_first: bool,
) -> list[dict[str, str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = tuple(str(row.get(name, "") or "") for name in group_keys)
        grouped[key].append(row)
    rank_fn = score_rank_high if hard_first else score_rank_low
    ordered_groups = sorted(grouped.items(), key=lambda item: (item[0], len(item[1])))
    for _, group_rows in ordered_groups:
        group_rows.sort(key=rank_fn)
    selected: list[dict[str, str]] = []
    while len(selected) < quota:
        progressed = False
        for _, group_rows in ordered_groups:
            if not group_rows:
                continue
            selected.append(group_rows.pop(0))
            progressed = True
            if len(selected) >= quota:
                break
        if not progressed:
            break
    return selected


def build_general_stable_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for family, quota in GENERAL_STABLE_QUOTAS.items():
        candidates = [
            row
            for row in rows
            if row.get("family") == family
            and row.get("selection_tier") == "verified_trace_ready"
            and parse_bool(row.get("verified_trace_ready", "true"))
        ]
        family_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=("template_subtype", "teacher_solver_candidate"),
            hard_first=False,
        )
        selected.extend(
            to_benchmark_row(
                row,
                benchmark_name="general_stable_set",
                benchmark_role="stable_replay",
            )
            for row in family_rows
        )
    return selected


def build_binary_hard_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    binary_rows = [row for row in rows if row.get("family") == "bit_manipulation"]
    for tier, quota in BINARY_HARD_TIER_QUOTAS.items():
        candidates = [row for row in binary_rows if row.get("selection_tier") == tier]
        tier_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=(
                "teacher_solver_candidate",
                "bit_structured_formula_abstract_family",
                "group_signature",
            ),
            hard_first=True,
        )
        selected.extend(
            to_benchmark_row(
                row,
                benchmark_name="binary_hard_set",
                benchmark_role="hard_binary_watch",
            )
            for row in tier_rows
        )
    return selected


def fill_symbol_watch_candidates(
    rows: list[dict[str, str]],
    already_selected_ids: set[str],
) -> list[dict[str, Any]]:
    remaining = [
        row
        for row in rows
        if row.get("family") == "symbol_equation" and row.get("id", "") not in already_selected_ids
    ]
    remaining.sort(key=score_rank_high)
    filler: list[dict[str, Any]] = []
    for row in remaining:
        filler.append(
            to_benchmark_row(
                row,
                benchmark_name="symbol_watch_set",
                benchmark_role="symbol_watch",
            )
        )
        if len(filler) >= 60:
            break
    return filler


def build_symbol_watch_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    symbol_rows = [row for row in rows if row.get("family") == "symbol_equation"]
    for template_subtype, tier, quota in SYMBOL_WATCH_TARGETS:
        candidates = [
            row
            for row in symbol_rows
            if row.get("template_subtype") == template_subtype and row.get("selection_tier") == tier
        ]
        watch_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=("symbol_query_operator", "teacher_solver_candidate"),
            hard_first=True,
        )
        for row in watch_rows:
            row_id = row.get("id", "")
            if row_id in selected_ids:
                continue
            selected.append(
                to_benchmark_row(
                    row,
                    benchmark_name="symbol_watch_set",
                    benchmark_role="symbol_watch",
                )
            )
            selected_ids.add(row_id)
    if len(selected) < 60:
        for row in fill_symbol_watch_candidates(rows, selected_ids):
            row_id = row["id"]
            if row_id in selected_ids:
                continue
            selected.append(row)
            selected_ids.add(row_id)
            if len(selected) >= 60:
                break
    return selected


def holdout_key_structured_family(row: dict[str, str]) -> str:
    value = str(row.get("bit_structured_formula_abstract_family", "")).strip()
    return value or "__none__"


def holdout_key_solver(row: dict[str, str]) -> str:
    value = str(row.get("teacher_solver_candidate", "")).strip()
    return value or "__none__"


def holdout_key_gap(row: dict[str, str]) -> str:
    num_examples = parse_int(row.get("num_examples"), 0)
    no_candidate = parse_int(row.get("bit_no_candidate_positions"), -1)
    multi_candidate = parse_int(row.get("bit_multi_candidate_positions"), -1)
    return f"ex{num_examples}__no{no_candidate}__multi{multi_candidate}"


def holdout_key_prompt_signature(row: dict[str, str]) -> str:
    group_signature = str(row.get("group_signature", "")).strip()
    if group_signature:
        return group_signature
    prompt = str(row.get("prompt", ""))
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def assign_balanced_group_folds(keys: list[str], num_folds: int) -> dict[str, int]:
    group_counts = Counter(keys)
    fold_loads = [0 for _ in range(num_folds)]
    assignments: dict[str, int] = {}
    ordered_groups = sorted(group_counts.items(), key=lambda item: (-item[1], item[0]))
    for group_key, group_size in ordered_groups:
        preferred = stable_mod(group_key, num_folds)
        best_fold = min(
            range(num_folds),
            key=lambda fold: (fold_loads[fold], abs(fold - preferred), fold),
        )
        assignments[group_key] = best_fold
        fold_loads[best_fold] += group_size
    return assignments


def build_binary_holdout_assignments(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    binary_rows = [row for row in rows if row.get("family") == "bit_manipulation"]
    key_builders = {
        "structured_family": holdout_key_structured_family,
        "solver_family": holdout_key_solver,
        "gap_signature": holdout_key_gap,
        "prompt_signature": holdout_key_prompt_signature,
    }
    fold_maps = {
        holdout_kind: assign_balanced_group_folds(
            [key_builder(row) for row in binary_rows],
            HOLDOUT_FOLDS,
        )
        for holdout_kind, key_builder in key_builders.items()
    }
    assignments: list[dict[str, Any]] = []
    for row in binary_rows:
        for holdout_kind, key_builder in key_builders.items():
            holdout_key = key_builder(row)
            fold = fold_maps[holdout_kind][holdout_key]
            assignments.append(
                {
                    "id": row.get("id", ""),
                    "family": row.get("family", ""),
                    "selection_tier": row.get("selection_tier", ""),
                    "template_subtype": row.get("template_subtype", ""),
                    "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
                    "holdout_kind": holdout_kind,
                    "holdout_key": holdout_key,
                    "fold": fold,
                    "num_examples": parse_int(row.get("num_examples"), 0),
                    "bit_no_candidate_positions": parse_int(row.get("bit_no_candidate_positions"), -1),
                    "bit_multi_candidate_positions": parse_int(row.get("bit_multi_candidate_positions"), -1),
                    "group_signature": row.get("group_signature", ""),
                }
            )
    return assignments


def summarize_benchmark(rows: list[dict[str, Any]]) -> dict[str, Any]:
    family_counts = Counter(row["family_short"] for row in rows)
    tier_counts = Counter(row["selection_tier"] for row in rows)
    template_counts = Counter(row["template_subtype"] for row in rows)
    return {
        "rows": len(rows),
        "family_counts": dict(sorted(family_counts.items())),
        "selection_tier_counts": dict(sorted(tier_counts.items())),
        "template_subtype_counts": dict(sorted(template_counts.items())),
    }


def build_phase0_manifest(
    *,
    analysis_csv: Path,
    general_rows: list[dict[str, Any]],
    binary_rows: list[dict[str, Any]],
    symbol_rows: list[dict[str, Any]],
    holdouts: list[dict[str, Any]],
) -> dict[str, Any]:
    holdout_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in holdouts:
        holdout_counts[row["holdout_kind"]][str(row["fold"])] += 1
    return {
        "phase": "phase0_offline_eval",
        "source_analysis_csv": str(analysis_csv),
        "readme_eval_assumptions": {
            "metric": "accuracy",
            "temperature": README_TEMPERATURE,
            "top_p": README_TOP_P,
            "max_tokens": README_MAX_TOKENS,
            "max_num_seqs": README_MAX_NUM_SEQS,
            "max_model_len": README_MAX_MODEL_LEN,
            "boxed_first_extraction": True,
            "numeric_relative_tolerance": 1e-2,
        },
        "benchmark_sets": {
            "general_stable_set": summarize_benchmark(general_rows),
            "binary_hard_set": summarize_benchmark(binary_rows),
            "symbol_watch_set": summarize_benchmark(symbol_rows),
        },
        "binary_holdouts": {
            holdout_kind: dict(sorted(folds.items()))
            for holdout_kind, folds in sorted(holdout_counts.items())
        },
    }


def render_phase0_report(manifest: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Phase 0 Offline Eval Manifest")
    lines.append("")
    lines.append("## README-aligned evaluation assumptions")
    lines.append("")
    for key, value in manifest["readme_eval_assumptions"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Benchmark sets")
    lines.append("")
    lines.append("| set | rows | family_counts | selection_tier_counts |")
    lines.append("| --- | ---: | --- | --- |")
    for set_name, payload in manifest["benchmark_sets"].items():
        lines.append(
            f"| `{set_name}` | {payload['rows']} | "
            f"`{json.dumps(payload['family_counts'], ensure_ascii=False)}` | "
            f"`{json.dumps(payload['selection_tier_counts'], ensure_ascii=False)}` |"
        )
    lines.append("")
    lines.append("## Binary holdout fold counts")
    lines.append("")
    lines.append("| holdout_kind | fold_counts |")
    lines.append("| --- | --- |")
    for holdout_kind, fold_counts in manifest["binary_holdouts"].items():
        lines.append(f"| `{holdout_kind}` | `{json.dumps(fold_counts, ensure_ascii=False)}` |")
    lines.append("")
    return "\n".join(lines)


def mark_status_rows(rows: Sequence[dict[str, Any]], benchmark_name: str) -> list[dict[str, Any]]:
    marked: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        new_row = dict(row)
        new_row["benchmark_index"] = index
        new_row["benchmark_name"] = benchmark_name
        marked.append(new_row)
    return marked


def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"
    matches = BOXED_PATTERN.findall(text)
    if matches:
        non_empty = [match.strip() for match in matches if match.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    for pattern in FINAL_ANSWER_PATTERNS:
        matched = __import__("re").findall(pattern, text, __import__("re").IGNORECASE)
        if matched:
            return matched[-1].strip()
    numeric_matches = NUMBER_PATTERN.findall(text)
    if numeric_matches:
        return numeric_matches[-1]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"


def verify_answer(gold: str, predicted: str) -> bool:
    gold = str(gold).strip()
    predicted = str(predicted).strip()
    try:
        gold_num = float(gold)
        pred_num = float(predicted)
        return math.isclose(gold_num, pred_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == gold.lower()


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
        matched = __import__("re").findall(pattern, text, __import__("re").IGNORECASE)
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


def safe_div(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def aggregate_counts(rows: Sequence[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"rows": 0, "correct": 0})
    for row in rows:
        bucket_key = str(row.get(key, ""))
        buckets[bucket_key]["rows"] += 1
        buckets[bucket_key]["correct"] += int(bool(row.get("is_correct")))
    summary: list[dict[str, Any]] = []
    for bucket_key, stats in sorted(buckets.items()):
        summary.append(
            {
                key: bucket_key,
                "rows": stats["rows"],
                "correct": stats["correct"],
                "accuracy": round(safe_div(stats["correct"], stats["rows"]), 4),
            }
        )
    return summary


def build_binary_metrics(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    binary_rows = [
        row
        for row in rows
        if row.get("family") == "bit_manipulation" or row.get("family_short") == "binary"
    ]
    regex_ok = [row for row in binary_rows if BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))]
    gold_leading_zero_rows = [
        row for row in binary_rows if str(row.get("gold_answer", "")).startswith("0")
    ]
    leading_zero_ok = [
        row
        for row in gold_leading_zero_rows
        if BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))
        and str(row.get("prediction", "")).startswith("0")
    ]
    format_ok = [
        row
        for row in binary_rows
        if row.get("has_boxed") and BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))
    ]
    format_fail = [row for row in binary_rows if row not in format_ok]
    format_ok_but_wrong = [row for row in format_ok if not row.get("is_correct")]
    return {
        "rows": len(binary_rows),
        "boxed_extraction_success_rate": round(
            safe_div(
                sum(int(row.get("fallback_type") == "boxed_non_empty") for row in binary_rows),
                len(binary_rows),
            ),
            4,
        ),
        "regex_exact_rate": round(safe_div(len(regex_ok), len(binary_rows)), 4),
        "leading_zero_retention_rate": round(
            safe_div(len(leading_zero_ok), len(gold_leading_zero_rows)),
            4,
        ),
        "format_failure_rate": round(safe_div(len(format_fail), len(binary_rows)), 4),
        "format_ok_content_wrong_rate": round(safe_div(len(format_ok_but_wrong), len(format_ok)), 4),
        "solver_family_accuracy": aggregate_counts(binary_rows, "teacher_solver_candidate"),
    }


def summarize_scored_rows(row_level: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return {
        "overall": {
            "rows": len(row_level),
            "correct": sum(int(row["is_correct"]) for row in row_level),
            "accuracy": round(
                safe_div(sum(int(row["is_correct"]) for row in row_level), len(row_level)),
                4,
            ),
        },
        "by_family": aggregate_counts(row_level, "family_short"),
        "by_template_subtype": aggregate_counts(row_level, "template_subtype"),
        "by_answer_type": aggregate_counts(row_level, "answer_type"),
        "by_prompt_len_bucket": aggregate_counts(row_level, "prompt_len_bucket"),
        "by_num_examples": aggregate_counts(row_level, "num_examples"),
        "by_selection_tier": aggregate_counts(row_level, "selection_tier"),
        "binary_metrics": build_binary_metrics(row_level),
    }


def render_markdown_summary(name: str, summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {name}")
    lines.append("")
    overall = summary["overall"]
    lines.append("## Overall")
    lines.append("")
    lines.append(f"- rows: `{overall['rows']}`")
    lines.append(f"- correct: `{overall['correct']}`")
    lines.append(f"- accuracy: `{overall['accuracy']:.4f}`")
    lines.append("")

    def add_table(title: str, rows: Sequence[dict[str, Any]], key_name: str) -> None:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| {key_name} | rows | correct | accuracy |")
        lines.append("| --- | ---: | ---: | ---: |")
        for row in rows:
            lines.append(
                f"| `{row[key_name]}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |"
            )
        lines.append("")

    add_table("Family accuracy", summary["by_family"], "family_short")
    add_table("Template subtype accuracy", summary["by_template_subtype"], "template_subtype")
    add_table("Answer type accuracy", summary["by_answer_type"], "answer_type")
    add_table("Prompt length buckets", summary["by_prompt_len_bucket"], "prompt_len_bucket")
    add_table("Num examples", summary["by_num_examples"], "num_examples")
    add_table("Selection tier accuracy", summary["by_selection_tier"], "selection_tier")

    binary_metrics = summary["binary_metrics"]
    lines.append("## Binary metrics")
    lines.append("")
    for key in (
        "rows",
        "boxed_extraction_success_rate",
        "regex_exact_rate",
        "leading_zero_retention_rate",
        "format_failure_rate",
        "format_ok_content_wrong_rate",
    ):
        lines.append(f"- {key}: `{binary_metrics[key]}`")
    lines.append("")
    lines.append("### Binary solver-family accuracy")
    lines.append("")
    lines.append("| teacher_solver_candidate | rows | correct | accuracy |")
    lines.append("| --- | ---: | ---: | ---: |")
    for row in binary_metrics["solver_family_accuracy"]:
        lines.append(
            f"| `{row['teacher_solver_candidate']}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_binary_holdout_accuracy_rows(
    scored_rows: Sequence[dict[str, Any]],
    holdout_rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    binary_by_id = {
        row["id"]: row
        for row in scored_rows
        if row.get("family") == "bit_manipulation" or row.get("family_short") == "binary"
    }
    joined: list[dict[str, Any]] = []
    for holdout in holdout_rows:
        scored = binary_by_id.get(holdout.get("id", ""))
        if scored is None:
            continue
        joined.append(
            {
                "holdout_kind": holdout.get("holdout_kind", ""),
                "fold": str(holdout.get("fold", "")),
                "rows": 1,
                "correct": int(bool(scored.get("is_correct"))),
            }
        )
    buckets: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"rows": 0, "correct": 0})
    for row in joined:
        key = (row["holdout_kind"], row["fold"])
        buckets[key]["rows"] += row["rows"]
        buckets[key]["correct"] += row["correct"]
    summary: list[dict[str, Any]] = []
    for (holdout_kind, fold), stats in sorted(buckets.items()):
        summary.append(
            {
                "holdout_kind": holdout_kind,
                "fold": fold,
                "rows": stats["rows"],
                "correct": stats["correct"],
                "accuracy": round(safe_div(stats["correct"], stats["rows"]), 4),
            }
        )
    return summary


def prepare_phase0_benchmark_artifacts(
    *,
    prebuilt_root: Path,
    analysis_csv: Path,
    artifact_root: Path,
    report_root: Path,
    rebuild: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    ensure_dir(artifact_root)
    ensure_dir(report_root)
    prebuilt_general = prebuilt_root / "general_stable_set.csv"
    prebuilt_binary = prebuilt_root / "binary_hard_set.csv"
    prebuilt_symbol = prebuilt_root / "symbol_watch_set.csv"
    prebuilt_holdouts = prebuilt_root / "binary_holdout_assignments.csv"
    prebuilt_manifest = prebuilt_root / "phase0_eval_manifest.json"
    prebuilt_ready = (
        not rebuild
        and prebuilt_general.exists()
        and prebuilt_binary.exists()
        and prebuilt_symbol.exists()
    )

    if prebuilt_ready:
        general_rows = load_csv_rows(prebuilt_general)
        binary_rows = load_csv_rows(prebuilt_binary)
        symbol_rows = load_csv_rows(prebuilt_symbol)
        holdout_rows = load_csv_rows(prebuilt_holdouts) if prebuilt_holdouts.exists() else []
        manifest = load_json(prebuilt_manifest, default=None)
        if manifest is None:
            manifest = build_phase0_manifest(
                analysis_csv=analysis_csv,
                general_rows=general_rows,
                binary_rows=binary_rows,
                symbol_rows=symbol_rows,
                holdouts=holdout_rows,
            )
    else:
        analysis_rows = load_csv_rows(analysis_csv)
        general_rows = build_general_stable_set(analysis_rows)
        binary_rows = build_binary_hard_set(analysis_rows)
        symbol_rows = build_symbol_watch_set(analysis_rows)
        holdout_rows = build_binary_holdout_assignments(analysis_rows)
        manifest = build_phase0_manifest(
            analysis_csv=analysis_csv,
            general_rows=general_rows,
            binary_rows=binary_rows,
            symbol_rows=symbol_rows,
            holdouts=holdout_rows,
        )

    general_rows = mark_status_rows(general_rows, "general_stable_set")
    binary_rows = mark_status_rows(binary_rows, "binary_hard_set")
    symbol_rows = mark_status_rows(symbol_rows, "symbol_watch_set")
    benchmark_rows = general_rows + binary_rows + symbol_rows

    benchmark_fieldnames = benchmark_columns() + ["benchmark_index"]
    write_csv_rows(artifact_root / "general_stable_set.csv", general_rows, benchmark_fieldnames)
    write_csv_rows(artifact_root / "binary_hard_set.csv", binary_rows, benchmark_fieldnames)
    write_csv_rows(artifact_root / "symbol_watch_set.csv", symbol_rows, benchmark_fieldnames)
    if holdout_rows:
        write_csv_rows(
            artifact_root / "binary_holdout_assignments.csv",
            holdout_rows,
            [
                "id",
                "family",
                "selection_tier",
                "template_subtype",
                "teacher_solver_candidate",
                "holdout_kind",
                "holdout_key",
                "fold",
                "num_examples",
                "bit_no_candidate_positions",
                "bit_multi_candidate_positions",
                "group_signature",
            ],
        )
    write_csv_rows(artifact_root / "phase0_combined_eval_set.csv", benchmark_rows, benchmark_fieldnames)
    write_json(artifact_root / "phase0_eval_manifest.json", manifest)
    write_text(report_root / "phase0_eval_manifest.md", render_phase0_report(manifest))
    return benchmark_rows, holdout_rows, manifest


def build_prompts(tokenizer: Any, prompt_series: Sequence[str]) -> list[str]:
    prompts: list[str] = []
    for prompt_text in prompt_series:
        user_content = f"{prompt_text}\n{BOXED_INSTRUCTION}"
        try:
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": user_content}],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True,
            )
        except TypeError:
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": user_content}],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            rendered = user_content
        prompts.append(rendered)
    return prompts


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            rows.append(json.loads(stripped))
    return rows


def tail_text(path: Path, max_chars: int = 6000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def clamp_eval_batch_size(value: int | None, *, default: int, max_num_seqs: int) -> int:
    candidate = default if value is None or int(value) <= 0 else int(value)
    return max(1, min(candidate, int(max_num_seqs)))


def resolve_phase0_eval_num_shards(
    *,
    requested_shards: int,
    total_rows: int,
    memory_budget_gb: float,
    estimated_worker_memory_gb: float,
) -> int:
    if total_rows <= 0:
        return 1
    if requested_shards > 0:
        return max(1, min(requested_shards, total_rows))
    auto = int(float(memory_budget_gb) // max(float(estimated_worker_memory_gb), 1.0))
    auto = max(1, auto)
    return min(auto, total_rows)


def maybe_patch_batch_generator_stats(mx: Any) -> None:
    from mlx_lm.generate import BatchGenerator

    if getattr(BatchGenerator.stats, "_copilot_zero_time_safe", False):
        return

    def _safe_batch_generator_stats(self: Any) -> Any:
        stats = self._stats
        prompt_time = float(getattr(stats, "prompt_time", 0.0) or 0.0)
        generation_time = float(getattr(stats, "generation_time", 0.0) or 0.0)
        stats.prompt_tps = (
            float(getattr(stats, "prompt_tokens", 0) or 0) / prompt_time
            if prompt_time > 0.0
            else 0.0
        )
        stats.generation_tps = (
            float(getattr(stats, "generation_tokens", 0) or 0) / generation_time
            if generation_time > 0.0
            else 0.0
        )
        stats.peak_memory = mx.get_peak_memory() / 1e9
        return stats

    setattr(_safe_batch_generator_stats, "_copilot_zero_time_safe", True)
    BatchGenerator.stats = _safe_batch_generator_stats


def maybe_patch_mamba_cache_extract() -> None:
    import mlx.core as mx  # type: ignore
    from mlx_lm.models.cache import MambaCache  # type: ignore

    if hasattr(MambaCache, "extract") and getattr(MambaCache.extract, "_copilot_enabled", False):
        return
    if hasattr(MambaCache, "extract") and not getattr(MambaCache.extract, "_copilot_enabled", False):
        return

    def _extract(self: Any, idx: int) -> Any:
        cache = MambaCache()
        cache.cache = [
            None if state is None else mx.contiguous(state[idx : idx + 1])
            for state in self.cache
        ]
        cache.left_padding = None
        return cache

    setattr(_extract, "_copilot_enabled", True)
    MambaCache.extract = _extract


def encode_prompt(tokenizer: Any, prompt: str) -> list[int]:
    bos_token = getattr(tokenizer, "bos_token", None)
    add_special_tokens = bos_token is None or not prompt.startswith(str(bos_token))
    encoded = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
    return list(encoded)


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
    if normalized_ids == {expected_id}:
        return
    tokenizer.eos_token_ids = {expected_id}


def generate_phase0_records_batched(
    *,
    benchmark_rows: Sequence[dict[str, Any]],
    model_path: Path,
    adapter_dir: Path | None,
    max_tokens: int,
    top_p: float,
    temperature: float,
    max_num_seqs: int,
    prompt_chunk_size: int,
    prefill_batch_size: int,
    completion_batch_size: int,
    lazy_load: bool,
    progress_every: int,
    worker_label: str,
) -> list[dict[str, Any]]:
    import mlx.core as mx  # type: ignore
    from mlx_lm import batch_generate, generate, load  # type: ignore
    from mlx_lm.sample_utils import make_sampler  # type: ignore

    maybe_patch_batch_generator_stats(mx)
    maybe_patch_mamba_cache_extract()
    load_kwargs: dict[str, Any] = {"lazy": lazy_load}
    if adapter_dir is not None:
        load_kwargs["adapter_path"] = str(adapter_dir)
    model, tokenizer = load(str(model_path), **load_kwargs)
    maybe_fix_tokenizer_eos_ids(tokenizer)
    prompts = build_prompts(tokenizer, [str(row["prompt"]) for row in benchmark_rows])
    prompt_tokens = [encode_prompt(tokenizer, prompt) for prompt in prompts]
    sampler = make_sampler(
        temp=float(temperature),
        top_p=float(top_p) if 0.0 < float(top_p) < 1.0 else 0.0,
    )

    chunk_size = clamp_eval_batch_size(
        prompt_chunk_size,
        default=max_num_seqs,
        max_num_seqs=max_num_seqs,
    )
    prefill_size = clamp_eval_batch_size(
        prefill_batch_size,
        default=min(max_num_seqs, 32),
        max_num_seqs=max_num_seqs,
    )
    completion_size = clamp_eval_batch_size(
        completion_batch_size,
        default=min(max_num_seqs, 32),
        max_num_seqs=max_num_seqs,
    )

    records: list[dict[str, Any]] = []
    total_prompts = len(prompt_tokens)
    total_chunks = max(1, math.ceil(total_prompts / chunk_size))
    run_started_at = time.perf_counter()
    heartbeat_sec = 60.0

    for chunk_start in range(0, total_prompts, chunk_size):
        chunk_prompts = prompt_tokens[chunk_start : chunk_start + chunk_size]
        chunk_rows = benchmark_rows[chunk_start : chunk_start + len(chunk_prompts)]
        chunk_rendered_prompts = prompts[chunk_start : chunk_start + len(chunk_prompts)]
        chunk_index = (chunk_start // chunk_size) + 1
        chunk_end = chunk_start + len(chunk_prompts)
        chunk_started_at = time.perf_counter()
        print(
            f"[phase0-eval:{worker_label}] "
            f"chunk={chunk_index}/{total_chunks} prompts={chunk_start + 1}-{chunk_end}/{total_prompts} status=started",
            flush=True,
        )

        heartbeat_stop = threading.Event()
        heartbeat_thread: threading.Thread | None = None
        if heartbeat_sec > 0:
            def emit_heartbeat() -> None:
                while not heartbeat_stop.wait(heartbeat_sec):
                    chunk_elapsed = time.perf_counter() - chunk_started_at
                    total_elapsed = time.perf_counter() - run_started_at
                    print(
                        f"[phase0-eval:{worker_label}] "
                        f"chunk={chunk_index}/{total_chunks} status=running "
                        f"chunk_elapsed_sec={chunk_elapsed:.1f} total_elapsed_sec={total_elapsed:.1f}",
                        flush=True,
                    )

            heartbeat_thread = threading.Thread(target=emit_heartbeat, daemon=True)
            heartbeat_thread.start()

        try:
            try:
                batch_response = batch_generate(
                    model,
                    tokenizer,
                    chunk_prompts,
                    max_tokens=max_tokens,
                    sampler=sampler,
                    verbose=False,
                    prefill_batch_size=min(prefill_size, len(chunk_prompts)),
                    completion_batch_size=min(completion_size, len(chunk_prompts)),
                )
                chunk_outputs = list(batch_response.texts)
            except AttributeError as exc:
                error_text = f"{type(exc).__name__}: {exc}"
                if "MambaCache" not in error_text or "extract" not in error_text:
                    raise
                print(
                    f"[phase0-eval:{worker_label}] "
                    f"chunk={chunk_index}/{total_chunks} status=batch_generate_fallback "
                    f"reason={error_text}",
                    flush=True,
                )
                chunk_outputs = [
                    generate(
                        model,
                        tokenizer,
                        prompt=prompt_tokens_single,
                        verbose=False,
                        max_tokens=max_tokens,
                        sampler=sampler,
                    )
                    for prompt_tokens_single in chunk_prompts
                ]
                batch_response = None
        finally:
            if heartbeat_thread is not None:
                heartbeat_stop.set()
                heartbeat_thread.join()

        for row, rendered_prompt, raw_output in zip(
            chunk_rows,
            chunk_rendered_prompts,
            chunk_outputs,
        ):
            records.append(
                {
                    "benchmark_name": row["benchmark_name"],
                    "benchmark_role": row["benchmark_role"],
                    "benchmark_index": row["benchmark_index"],
                    "family": row["family"],
                    "family_short": row["family_short"],
                    "template_subtype": row["template_subtype"],
                    "selection_tier": row["selection_tier"],
                    "teacher_solver_candidate": row["teacher_solver_candidate"],
                    "answer_type": row["answer_type"],
                    "num_examples": row["num_examples"],
                    "prompt_len_chars": row["prompt_len_chars"],
                    "id": row["id"],
                    "expected_answer": row["answer"],
                    "rendered_prompt": rendered_prompt,
                    "raw_output": raw_output,
                    "extracted_answer": extract_final_answer(raw_output),
                }
            )

        chunk_elapsed = time.perf_counter() - chunk_started_at
        total_elapsed = time.perf_counter() - run_started_at
        stats = getattr(batch_response, "stats", None) if batch_response is not None else None
        stats_suffix = ""
        if stats is not None:
            stats_suffix = (
                f" prompt_tps={getattr(stats, 'prompt_tps', 0.0):.2f}"
                f" generation_tps={getattr(stats, 'generation_tps', 0.0):.2f}"
                f" peak_memory_gb={getattr(stats, 'peak_memory', 0.0):.2f}"
            )
        print(
            f"[phase0-eval:{worker_label}] "
            f"chunk={chunk_index}/{total_chunks} prompts={chunk_start + 1}-{chunk_end}/{total_prompts} "
            f"status=completed chunk_elapsed_sec={chunk_elapsed:.1f} total_elapsed_sec={total_elapsed:.1f}"
            f"{stats_suffix}",
            flush=True,
        )
        if progress_every > 0 and (
            chunk_end == total_prompts
            or chunk_end % progress_every == 0
        ):
            print(
                f"[phase0-eval:{worker_label}] completed {chunk_end}/{total_prompts} rows",
                flush=True,
            )
        mx.clear_cache()

    return records


def score_phase0_records(
    *,
    records: Sequence[dict[str, Any]],
    holdout_rows: Sequence[dict[str, Any]],
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored_rows: list[dict[str, Any]] = []
    for row in records:
        derived = analyze_raw_output(str(row["raw_output"]))
        prediction = derived["extracted_answer"]
        scored_rows.append(
            {
                "benchmark_name": row["benchmark_name"],
                "benchmark_role": row["benchmark_role"],
                "benchmark_index": row["benchmark_index"],
                "id": row["id"],
                "gold_answer": row["expected_answer"],
                "prediction": prediction,
                "is_correct": verify_answer(str(row["expected_answer"]), str(prediction)),
                "family": row["family"],
                "family_short": row["family_short"],
                "template_subtype": row["template_subtype"],
                "answer_type": row["answer_type"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "selection_tier": row["selection_tier"],
                "num_examples": row["num_examples"],
                "prompt_len_chars": row["prompt_len_chars"],
                "prompt_len_bucket": prompt_len_bucket(parse_int(row["prompt_len_chars"], 0)),
                "fallback_type": derived["fallback_type"],
                "format_bucket": derived["format_bucket"],
                "has_boxed": derived["has_boxed"],
                "boxed_count": derived["boxed_count"],
                "raw_output": row["raw_output"],
            }
        )

    overall_summary = summarize_scored_rows(scored_rows)
    by_benchmark_summary = {
        benchmark_name: summarize_scored_rows(
            [row for row in scored_rows if row["benchmark_name"] == benchmark_name]
        )
        for benchmark_name in ("general_stable_set", "binary_hard_set", "symbol_watch_set")
    }
    binary_holdout_accuracy = build_binary_holdout_accuracy_rows(scored_rows, holdout_rows)
    summary_payload = {
        "manifest": manifest,
        "overall": overall_summary,
        "by_benchmark": by_benchmark_summary,
        "binary_holdout_accuracy": binary_holdout_accuracy,
    }
    return scored_rows, summary_payload


def write_phase0_eval_outputs(
    *,
    artifact_root: Path,
    report_root: Path,
    records: Sequence[dict[str, Any]],
    scored_rows: Sequence[dict[str, Any]],
    summary_payload: dict[str, Any],
) -> None:
    write_csv_rows(
        artifact_root / "phase0_eval_raw_outputs.csv",
        records,
        [
            "benchmark_name",
            "benchmark_role",
            "benchmark_index",
            "family",
            "family_short",
            "template_subtype",
            "selection_tier",
            "teacher_solver_candidate",
            "answer_type",
            "num_examples",
            "prompt_len_chars",
            "id",
            "expected_answer",
            "rendered_prompt",
            "raw_output",
            "extracted_answer",
        ],
    )
    write_csv_rows(
        artifact_root / "phase0_eval_row_level.csv",
        scored_rows,
        [
            "benchmark_name",
            "benchmark_role",
            "benchmark_index",
            "id",
            "gold_answer",
            "prediction",
            "is_correct",
            "family",
            "family_short",
            "template_subtype",
            "answer_type",
            "teacher_solver_candidate",
            "selection_tier",
            "num_examples",
            "prompt_len_chars",
            "prompt_len_bucket",
            "fallback_type",
            "format_bucket",
            "has_boxed",
            "boxed_count",
            "raw_output",
        ],
    )
    write_json(artifact_root / "phase0_eval_summary.json", summary_payload)
    write_text(
        report_root / "phase0_eval_summary.md",
        render_markdown_summary("phase0_eval_overall", summary_payload["overall"]),
    )
    binary_holdout_accuracy = summary_payload["binary_holdout_accuracy"]
    if binary_holdout_accuracy:
        write_csv_rows(
            artifact_root / "phase0_binary_holdout_accuracy.csv",
            binary_holdout_accuracy,
            ["holdout_kind", "fold", "rows", "correct", "accuracy"],
        )
    for benchmark_name, payload in summary_payload["by_benchmark"].items():
        write_json(artifact_root / f"{benchmark_name}_summary.json", payload)
        write_text(report_root / f"{benchmark_name}_summary.md", render_markdown_summary(benchmark_name, payload))


def run_phase0_eval_parallel(
    *,
    benchmark_rows: Sequence[dict[str, Any]],
    model_path: Path,
    adapter_dir: Path | None,
    eval_root: Path,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    num_shards = resolve_phase0_eval_num_shards(
        requested_shards=int(args.num_shards),
        total_rows=len(benchmark_rows),
        memory_budget_gb=float(args.memory_budget_gb),
        estimated_worker_memory_gb=float(args.estimated_worker_memory_gb),
    )
    if num_shards <= 1:
        return generate_phase0_records_batched(
            benchmark_rows=benchmark_rows,
            model_path=model_path,
            adapter_dir=adapter_dir,
            max_tokens=int(args.max_tokens),
            top_p=float(args.top_p),
            temperature=float(args.temperature),
            max_num_seqs=int(args.max_num_seqs),
            prompt_chunk_size=int(args.prompt_chunk_size),
            prefill_batch_size=int(args.prefill_batch_size),
            completion_batch_size=int(args.completion_batch_size),
            lazy_load=bool(args.lazy_load),
            progress_every=int(args.progress_every),
            worker_label="main",
        )

    shard_root = eval_root / "_parallel"
    ensure_dir(shard_root)
    shard_rows = [
        list(benchmark_rows[shard_index::num_shards])
        for shard_index in range(num_shards)
    ]
    launched_processes: list[tuple[int, Path, Path, subprocess.Popen[Any], Any]] = []

    print(
        f"[phase0-eval] launching {num_shards} shard workers "
        f"(memory_budget_gb={float(args.memory_budget_gb):.1f}, "
        f"estimated_worker_memory_gb={float(args.estimated_worker_memory_gb):.1f})",
        flush=True,
    )

    try:
        for shard_index, rows in enumerate(shard_rows):
            shard_input_path = shard_root / f"shard_{shard_index:02d}.jsonl"
            shard_output_path = shard_root / f"shard_{shard_index:02d}_records.jsonl"
            shard_log_path = shard_root / f"shard_{shard_index:02d}.log"
            write_jsonl_records(shard_input_path, rows)
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "eval-phase0-worker",
                "--model-path",
                str(model_path),
                "--input-jsonl",
                str(shard_input_path),
                "--output-jsonl",
                str(shard_output_path),
                "--max-tokens",
                str(int(args.max_tokens)),
                "--temperature",
                str(float(args.temperature)),
                "--top-p",
                str(float(args.top_p)),
                "--max-num-seqs",
                str(int(args.max_num_seqs)),
                "--prompt-chunk-size",
                str(int(args.prompt_chunk_size)),
                "--prefill-batch-size",
                str(int(args.prefill_batch_size)),
                "--completion-batch-size",
                str(int(args.completion_batch_size)),
                "--progress-every",
                str(int(args.progress_every)),
                "--worker-label",
                f"shard{shard_index + 1}of{num_shards}",
            ]
            if adapter_dir is not None:
                command.extend(["--adapter-path", str(adapter_dir)])
            if args.lazy_load:
                command.append("--lazy-load")
            log_handle = shard_log_path.open("w", encoding="utf-8")
            process = subprocess.Popen(
                command,
                cwd=str(REPO_ROOT),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            launched_processes.append(
                (shard_index, shard_output_path, shard_log_path, process, log_handle)
            )
            print(
                f"[phase0-eval] launched shard={shard_index + 1}/{num_shards} "
                f"rows={len(rows)} log={shard_log_path}",
                flush=True,
            )

        for shard_index, shard_output_path, shard_log_path, process, log_handle in launched_processes:
            return_code = process.wait()
            log_handle.close()
            if return_code != 0:
                raise RuntimeError(
                    f"phase0 worker failed: shard={shard_index + 1}/{num_shards} "
                    f"return_code={return_code} log={shard_log_path}\n{tail_text(shard_log_path)}"
                )
            if not shard_output_path.exists():
                raise FileNotFoundError(
                    f"phase0 worker did not produce output: shard={shard_index + 1}/{num_shards} "
                    f"path={shard_output_path}"
                )
            print(
                f"[phase0-eval] completed shard={shard_index + 1}/{num_shards} log={shard_log_path}",
                flush=True,
            )
    finally:
        for _, _, _, process, log_handle in launched_processes:
            if not log_handle.closed:
                log_handle.close()
            if process.poll() is None:
                process.kill()
                process.wait()

    records: list[dict[str, Any]] = []
    for _, shard_output_path, _, _, _ in launched_processes:
        records.extend(load_jsonl_records(shard_output_path))
    records.sort(
        key=lambda row: (
            str(row.get("benchmark_name", "")),
            int(row.get("benchmark_index", 0)),
            str(row.get("id", "")),
        )
    )
    return records


def run_prepare_train(args: argparse.Namespace) -> None:
    manifest = prepare_training_run(args)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def run_mlx_lora_training_from_config(config_path: Path) -> None:
    import mlx_lm.lora as mlx_lora

    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    maybe_patch_mlx_chat_dataset_enable_thinking()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.load(handle, Loader=mlx_lora.yaml_loader) or {}
    for key, value in mlx_lora.CONFIG_DEFAULTS.items():
        config.setdefault(key, value)
    mlx_lora.run(argparse.Namespace(**config))


def run_train(args: argparse.Namespace) -> None:
    manifest = prepare_training_run(args)
    run_root = Path(manifest["run_root"])
    adapter_dir = Path(manifest["artifacts"]["adapter_dir"])
    config_path = Path(manifest["artifacts"]["config_path"])
    command = [sys.executable, str(Path(__file__).resolve()), "train-mlx-config", "--config", str(config_path)]
    print("Running MLX LoRA training:")
    print(" ".join(command))
    run_mlx_lora_training_from_config(config_path)
    verify_training_outputs(adapter_dir)
    training_result = {
        "created_at": utc_now(),
        "run_root": str(run_root),
        "adapter_dir": str(adapter_dir),
        "adapter_files": summarize_directory(adapter_dir),
    }
    write_json(run_root / "training_result.json", training_result)
    print(json.dumps(training_result, ensure_ascii=False, indent=2))


def run_train_mlx_config(args: argparse.Namespace) -> None:
    run_mlx_lora_training_from_config(Path(args.config).resolve())


def run_phase0_eval(args: argparse.Namespace) -> None:
    adapter_dir = None
    if args.adapter_path is not None:
        adapter_dir = Path(args.adapter_path).resolve()
        if not adapter_dir.exists():
            raise FileNotFoundError(f"Adapter directory does not exist: {adapter_dir}")
        verify_training_outputs(adapter_dir)

    if adapter_dir is not None:
        run_root = adapter_dir.parent
    else:
        run_root = Path(args.output_root).resolve() / str(args.eval_name)
        ensure_dir(run_root)
    shadow_model_dir = build_shadow_model_dir(
        Path(args.model_root),
        run_root / "shadow_model",
        force=bool(args.force_shadow_model),
    )

    eval_root = run_root / "phase0_offline_eval"
    artifact_root = eval_root / "artifacts"
    report_root = eval_root / "reports"
    benchmark_rows, holdout_rows, manifest = prepare_phase0_benchmark_artifacts(
        prebuilt_root=Path(args.phase0_prebuilt_root),
        analysis_csv=Path(args.phase0_analysis_csv),
        artifact_root=artifact_root,
        report_root=report_root,
        rebuild=bool(args.rebuild_phase0),
    )
    if args.max_samples is not None:
        benchmark_rows = benchmark_rows[: int(args.max_samples)]
    records = run_phase0_eval_parallel(
        benchmark_rows=benchmark_rows,
        model_path=shadow_model_dir,
        adapter_dir=adapter_dir,
        eval_root=eval_root,
        args=args,
    )
    scored_rows, summary_payload = score_phase0_records(
        records=records,
        holdout_rows=holdout_rows,
        manifest=manifest,
    )
    write_phase0_eval_outputs(
        artifact_root=artifact_root,
        report_root=report_root,
        records=records,
        scored_rows=scored_rows,
        summary_payload=summary_payload,
    )
    print(json.dumps(summary_payload["overall"], ensure_ascii=False, indent=2))


def run_phase0_eval_worker(args: argparse.Namespace) -> None:
    adapter_dir = None
    if args.adapter_path is not None:
        adapter_dir = Path(args.adapter_path).resolve()
        verify_training_outputs(adapter_dir)
    benchmark_rows = load_jsonl_records(Path(args.input_jsonl))
    records = generate_phase0_records_batched(
        benchmark_rows=benchmark_rows,
        model_path=Path(args.model_path).resolve(),
        adapter_dir=adapter_dir,
        max_tokens=int(args.max_tokens),
        top_p=float(args.top_p),
        temperature=float(args.temperature),
        max_num_seqs=int(args.max_num_seqs),
        prompt_chunk_size=int(args.prompt_chunk_size),
        prefill_batch_size=int(args.prefill_batch_size),
        completion_batch_size=int(args.completion_batch_size),
        lazy_load=bool(args.lazy_load),
        progress_every=int(args.progress_every),
        worker_label=str(args.worker_label),
    )
    write_jsonl_records(Path(args.output_jsonl), records)
    print(
        json.dumps(
            {
                "created_at": utc_now(),
                "worker_label": str(args.worker_label),
                "rows": len(records),
                "output_jsonl": str(Path(args.output_jsonl).resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def add_common_train_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--train-csv", type=Path, default=DEFAULT_TRAIN_CSV)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-name", type=str, default=DEFAULT_RUN_NAME)
    parser.add_argument("--train-profile", type=str, choices=TRAIN_PROFILE_CHOICES, default="baseline")
    parser.add_argument(
        "--dataset-format",
        type=str,
        choices=("chat", "completion", "completions", "text"),
        default="chat",
    )
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accumulation-steps", type=int, default=4)
    parser.add_argument("--num-epochs", type=float, default=2.0)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--lora-rank", type=int, default=32)
    parser.add_argument("--lora-alpha", type=float, default=32.0)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--num-layers", type=int, default=-1)
    parser.add_argument("--valid-shadow-rows", type=int, default=32)
    parser.add_argument("--steps-per-report", type=int, default=5)
    parser.add_argument("--steps-per-eval", type=int, default=900)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force-shadow-model", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-file mac_workspace/v0 pipeline for reproducing "
            "baseline/cot/phase2_binary_dsl with MLX LoRA and running a phase0-style offline eval."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_train = subparsers.add_parser("prepare-train", help="Build shadow model, dataset jsonl, and MLX config.")
    add_common_train_args(prepare_train)
    prepare_train.set_defaults(func=run_prepare_train)

    train = subparsers.add_parser("train", help="Prepare artifacts and launch mlx_lm.lora training.")
    add_common_train_args(train)
    train.set_defaults(func=run_train)

    train_mlx_config = subparsers.add_parser(
        "train-mlx-config",
        help="Internal helper: run mlx_lm.lora in-process so local dataset patches apply.",
    )
    train_mlx_config.add_argument("--config", type=Path, required=True)
    train_mlx_config.set_defaults(func=run_train_mlx_config)

    phase0_eval = subparsers.add_parser("eval-phase0", help="Run phase0-style offline evaluation with MLX generation.")
    phase0_eval.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    phase0_eval.add_argument("--adapter-path", type=Path, default=None)
    phase0_eval.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    phase0_eval.add_argument("--eval-name", type=str, default="phase0_base_model_mlx_eval")
    phase0_eval.add_argument("--phase0-prebuilt-root", type=Path, default=DEFAULT_PHASE0_PREBUILT_ROOT)
    phase0_eval.add_argument("--phase0-analysis-csv", type=Path, default=DEFAULT_PHASE0_ANALYSIS_CSV)
    phase0_eval.add_argument("--rebuild-phase0", action="store_true")
    phase0_eval.add_argument("--max-samples", type=int, default=None)
    phase0_eval.add_argument("--max-tokens", type=int, default=README_MAX_TOKENS)
    phase0_eval.add_argument("--temperature", type=float, default=README_TEMPERATURE)
    phase0_eval.add_argument("--top-p", type=float, default=README_TOP_P)
    phase0_eval.add_argument("--max-num-seqs", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval.add_argument("--num-shards", type=int, default=0)
    phase0_eval.add_argument("--memory-budget-gb", type=float, default=420.0)
    phase0_eval.add_argument("--estimated-worker-memory-gb", type=float, default=100.0)
    phase0_eval.add_argument("--prompt-chunk-size", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval.add_argument("--prefill-batch-size", type=int, default=32)
    phase0_eval.add_argument("--completion-batch-size", type=int, default=32)
    phase0_eval.add_argument("--progress-every", type=int, default=10)
    phase0_eval.add_argument("--lazy-load", action="store_true")
    phase0_eval.add_argument("--force-shadow-model", action="store_true")
    phase0_eval.set_defaults(func=run_phase0_eval)

    phase0_eval_worker = subparsers.add_parser(
        "eval-phase0-worker",
        help="Internal worker for sharded phase0 MLX evaluation.",
    )
    phase0_eval_worker.add_argument("--model-path", type=Path, required=True)
    phase0_eval_worker.add_argument("--adapter-path", type=Path, default=None)
    phase0_eval_worker.add_argument("--input-jsonl", type=Path, required=True)
    phase0_eval_worker.add_argument("--output-jsonl", type=Path, required=True)
    phase0_eval_worker.add_argument("--max-tokens", type=int, default=README_MAX_TOKENS)
    phase0_eval_worker.add_argument("--temperature", type=float, default=README_TEMPERATURE)
    phase0_eval_worker.add_argument("--top-p", type=float, default=README_TOP_P)
    phase0_eval_worker.add_argument("--max-num-seqs", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval_worker.add_argument("--prompt-chunk-size", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval_worker.add_argument("--prefill-batch-size", type=int, default=32)
    phase0_eval_worker.add_argument("--completion-batch-size", type=int, default=32)
    phase0_eval_worker.add_argument("--progress-every", type=int, default=10)
    phase0_eval_worker.add_argument("--worker-label", type=str, default="worker")
    phase0_eval_worker.add_argument("--lazy-load", action="store_true")
    phase0_eval_worker.set_defaults(func=run_phase0_eval_worker)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
