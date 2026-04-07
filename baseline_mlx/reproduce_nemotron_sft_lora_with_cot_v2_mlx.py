from __future__ import annotations

import argparse
import importlib.metadata as importlib_metadata
import json
import os
import random
import re
import shutil
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import pandas as pd
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL_ROOT = Path(
    "/Users/mac-studio/.cache/huggingface/hub/models--mlx-community--NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16"
)
DEFAULT_TRAIN_CSV = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "artifacts"
    / "train_split_with_cot.csv"
)
DEFAULT_OUTPUT_ROOT = WORK_ROOT / "outputs"
DEFAULT_RUN_NAME = "nemotron_sft_lora_with_cot_v2_mlx_v1"
BASE_MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"

README_MAX_LORA_RANK = 32
README_MAX_TOKENS = 7680
README_TOP_P = 1.0
README_TEMPERATURE = 0.0
README_MAX_NUM_SEQS = 64
README_MAX_MODEL_LEN = 8192

EXPECTED_COLUMNS = ["id", "prompt", "answer", "type", "generated_cot"]
DEFAULT_TYPE_SAMPLES = {
    "Numeral Conversion": 300,
    "Gravitational Constant": 400,
    "Unit Conversion": 700,
    "Text Encryption": 700,
    "Bit Manipulation": 607,
    "Equation Transformation": 200,
}
DEFAULT_SEED = 123
DEFAULT_LORA_KEYS = [
    "mixer.in_proj",
    "mixer.out_proj",
    "mixer.up_proj",
    "mixer.down_proj",
    "mixer.switch_mlp.fc1",
    "mixer.switch_mlp.fc2",
    "mixer.shared_experts.up_proj",
    "mixer.shared_experts.down_proj",
]
BOXED_INSTRUCTION = r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
LR_SCHEDULE_STEP_UNITS = ("optimizer", "micro")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def write_jsonl_records(path: Path, records: Sequence[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_json(path: Path, *, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


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


def load_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("mlx-lm", "mlx", "transformers", "pyyaml", "pandas"):
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
        raise FileNotFoundError(f"Model root must contain config.json or snapshots/: {model_root}")
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


def validate_training_frame(df: pd.DataFrame, path: Path) -> None:
    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in {path}: {missing}")


def parse_type_sample_overrides(entries: Sequence[str]) -> dict[str, int]:
    overrides: dict[str, int] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Invalid --type-sample entry '{entry}'. Expected TYPE=COUNT.")
        raw_type, raw_count = entry.split("=", 1)
        puzzle_type = raw_type.strip()
        if not puzzle_type:
            raise ValueError(f"Invalid --type-sample entry '{entry}': empty type.")
        try:
            count = int(raw_count.strip())
        except ValueError as exc:
            raise ValueError(f"Invalid sample count in '{entry}'.") from exc
        if count < 0:
            raise ValueError(f"Sample count must be >= 0 in '{entry}'.")
        overrides[puzzle_type] = count
    return overrides


def resolve_type_samples(args: argparse.Namespace) -> dict[str, int]:
    type_samples = dict(DEFAULT_TYPE_SAMPLES)
    type_samples.update(parse_type_sample_overrides(args.type_sample or []))
    unknown_types = sorted(set(type_samples) - set(DEFAULT_TYPE_SAMPLES))
    if unknown_types:
        raise ValueError(f"Unsupported puzzle types in --type-sample: {unknown_types}")
    return type_samples


def resolve_lora_keys(entries: Sequence[str]) -> list[str]:
    keys = [entry.strip() for entry in entries if entry.strip()]
    return keys or list(DEFAULT_LORA_KEYS)


def sample_training_df(df: pd.DataFrame, *, type_samples: dict[str, int], seed: int) -> pd.DataFrame:
    sampled_dfs: list[pd.DataFrame] = []
    for puzzle_type, sample_count in type_samples.items():
        subset = df[df["type"] == puzzle_type]
        if subset.empty and sample_count > 0:
            raise ValueError(f"No rows found for puzzle type '{puzzle_type}'.")
        if sample_count >= len(subset):
            sampled = subset
        else:
            sampled = subset.sample(n=sample_count, random_state=seed)
        sampled_dfs.append(sampled)
    if not sampled_dfs:
        raise ValueError("No type samples resolved for training.")
    train_df = pd.concat(sampled_dfs, ignore_index=True)
    train_df = train_df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return train_df


def clean_notebook_cot_text(generated_cot: str) -> str:
    cleaned = re.sub(r"\\boxed\{[^}]*\}", "", str(generated_cot)).rstrip()
    cleaned = re.sub(r"</think>\s*$", "", cleaned).rstrip()
    return cleaned


def build_user_message(prompt: str) -> str:
    prompt_text = str(prompt).strip()
    if not prompt_text:
        raise ValueError("Prompt must not be empty.")
    return f"{prompt_text}\n{BOXED_INSTRUCTION}"


def build_assistant_message(*, answer: str, generated_cot: str, row_id: str) -> str:
    answer_text = str(answer).strip()
    cot_text = str(generated_cot).strip()
    if not answer_text:
        raise ValueError(f"Row {row_id} is missing answer.")
    if not cot_text or cot_text.lower() == "nan":
        raise ValueError(f"Row {row_id} is missing generated_cot.")
    cot_cleaned = clean_notebook_cot_text(cot_text)
    if cot_cleaned:
        return f"{cot_cleaned}\n</think>\n\\boxed{{{answer_text}}}"
    return f"</think>\n\\boxed{{{answer_text}}}"


def build_chat_records(train_df: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    skipped_short_cot = 0
    for row in train_df.to_dict(orient="records"):
        row_id = str(row["id"]).strip()
        prompt = str(row["prompt"])
        answer = str(row["answer"])
        generated_cot = str(row["generated_cot"])
        if not generated_cot or generated_cot == "nan" or len(generated_cot.strip()) < 5:
            skipped_short_cot += 1
            continue
        assistant_content = build_assistant_message(
            answer=answer,
            generated_cot=generated_cot,
            row_id=row_id,
        )
        records.append(
            {
                "messages": [
                    {"role": "user", "content": build_user_message(prompt)},
                    {"role": "assistant", "content": assistant_content},
                ],
                "metadata": {
                    "id": row_id,
                    "answer": str(answer).strip(),
                    "type": str(row["type"]).strip(),
                },
            }
        )
    if not records:
        raise ValueError("No training records were built from the sampled CSV.")
    summary = {
        "records": len(records),
        "skipped_short_cot": skipped_short_cot,
        "type_counts": dict(
            sorted(Counter(str(record["metadata"]["type"]) for record in records).items())
        ),
    }
    return records, summary


def select_shadow_validation_records(
    records: Sequence[dict[str, Any]],
    *,
    valid_rows: int,
    minimum_rows: int,
    seed: int,
) -> list[dict[str, Any]]:
    if not records:
        raise ValueError("Training records are empty.")
    resolved_valid_rows = max(1, valid_rows, minimum_rows)
    resolved_valid_rows = min(resolved_valid_rows, len(records))
    rng = random.Random(seed)
    chosen_indices = sorted(rng.sample(range(len(records)), resolved_valid_rows))
    return [records[index] for index in chosen_indices]


def compute_total_iters(*, num_rows: int, num_epochs: float, batch_size: int) -> int:
    if batch_size <= 0:
        raise ValueError(f"batch_size must be > 0, got {batch_size}")
    return max(1, int(max(1, num_rows) * num_epochs // batch_size))


def compute_schedule_steps(
    *,
    total_iters: int,
    grad_accumulation_steps: int,
    schedule_step_unit: str,
) -> int:
    if total_iters <= 0:
        raise ValueError(f"total_iters must be > 0, got {total_iters}")
    if grad_accumulation_steps <= 0:
        raise ValueError(
            f"grad_accumulation_steps must be > 0, got {grad_accumulation_steps}"
        )
    normalized_unit = schedule_step_unit.strip().lower()
    if normalized_unit not in LR_SCHEDULE_STEP_UNITS:
        raise ValueError(
            f"lr_schedule_step_unit must be one of {LR_SCHEDULE_STEP_UNITS}, got {schedule_step_unit!r}"
        )
    if normalized_unit == "micro":
        return total_iters
    # mlx_lm advances the optimizer and its learning-rate schedule only when an
    # accumulated update is applied, so notebook parity requires optimizer-step units.
    return max(1, (total_iters + grad_accumulation_steps - 1) // grad_accumulation_steps)


def compute_final_optimizer_step_microbatches(
    *,
    total_iters: int,
    grad_accumulation_steps: int,
) -> int:
    if total_iters <= 0:
        raise ValueError(f"total_iters must be > 0, got {total_iters}")
    if grad_accumulation_steps <= 0:
        raise ValueError(
            f"grad_accumulation_steps must be > 0, got {grad_accumulation_steps}"
        )
    remainder = total_iters % grad_accumulation_steps
    if remainder:
        return remainder
    return min(total_iters, grad_accumulation_steps)


def build_mlx_lora_config(
    *,
    model_path: Path,
    dataset_dir: Path,
    adapter_dir: Path,
    resume_adapter_file: Path | None,
    mask_prompt: bool,
    enable_thinking: bool,
    batch_size: int,
    num_epochs: float,
    learning_rate: float,
    max_seq_length: int,
    grad_accumulation_steps: int,
    lora_rank: int,
    lora_alpha: float,
    lora_dropout: float,
    lora_keys: Sequence[str],
    num_layers: int,
    steps_per_report: int,
    steps_per_eval: int,
    save_every: int,
    seed: int,
    lr_schedule_name: str | None,
    lr_schedule_end: float,
    lr_warmup_ratio: float,
    lr_schedule_step_unit: str,
) -> dict[str, Any]:
    if lora_rank <= 0 or lora_rank > README_MAX_LORA_RANK:
        raise ValueError(
            f"LoRA rank must be in [1, {README_MAX_LORA_RANK}] per README.md, got {lora_rank}"
        )
    if lr_warmup_ratio < 0.0 or lr_warmup_ratio >= 1.0:
        raise ValueError(f"lr_warmup_ratio must be in [0, 1), got {lr_warmup_ratio}")
    total_iters = compute_total_iters(
        num_rows=sum(1 for _ in (dataset_dir / "train.jsonl").open("r", encoding="utf-8")),
        num_epochs=num_epochs,
        batch_size=batch_size,
    )
    schedule_steps = compute_schedule_steps(
        total_iters=total_iters,
        grad_accumulation_steps=grad_accumulation_steps,
        schedule_step_unit=lr_schedule_step_unit,
    )
    config: dict[str, Any] = {
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
        "save_every": total_iters if save_every <= 0 else save_every,
        "max_seq_length": max_seq_length,
        "grad_checkpoint": True,
        "seed": seed,
        "lora_parameters": {
            "rank": lora_rank,
            "dropout": lora_dropout,
            "scale": lora_alpha,
            "keys": list(lora_keys),
        },
    }
    if resume_adapter_file is not None:
        config["resume_adapter_file"] = str(resume_adapter_file)
    schedule_name = str(lr_schedule_name or "").strip()
    if schedule_name:
        if schedule_name != "cosine_decay":
            raise ValueError(f"Unsupported lr_schedule_name: {schedule_name}")
        schedule_config: dict[str, Any] = {
            "name": schedule_name,
            "arguments": [learning_rate, schedule_steps, float(lr_schedule_end)],
        }
        warmup_steps = int(schedule_steps * lr_warmup_ratio)
        if warmup_steps > 0:
            schedule_config["warmup"] = warmup_steps
        config["lr_schedule"] = schedule_config
    return config


def render_train_command(config_path: Path) -> str:
    return "\n".join(
        [
            "#!/bin/bash",
            "set -euo pipefail",
            f'"{sys.executable}" "{Path(__file__).resolve()}" train-mlx-config --config "{config_path}"',
            "",
        ]
    )


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
        raise ValueError("Target text span was not found in rendered chat.")
    offset_tokenizer = tokenizer if callable(tokenizer) else getattr(tokenizer, "_tokenizer", None)
    if offset_tokenizer is None or not callable(offset_tokenizer):
        raise TypeError(f"Tokenizer does not support offset mapping: {type(tokenizer)!r}")
    encoded = offset_tokenizer(
        full_text,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    for token_index, (start, end) in enumerate(encoded["offset_mapping"]):
        if start <= char_start < end or (start == end == char_start):
            return token_index
    raise ValueError("Unable to map assistant char offset to a token offset.")


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
            "Unsupported data format, see https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md#Data."
        )

    tuner_datasets.ChatDataset.__init__ = patched_chat_init
    tuner_datasets.ChatDataset.process = patched_chat_process
    tuner_datasets.CompletionsDataset.__init__ = patched_completions_init
    tuner_datasets.CompletionsDataset.process = patched_completions_process
    tuner_datasets.create_dataset = patched_create_dataset
    tuner_datasets._nemotron_enable_thinking_patch = True


def maybe_patch_mlx_trainer_final_accumulation_flush() -> None:
    import time
    from functools import partial

    import mlx.core as mx
    import mlx.nn as nn
    import mlx_lm.lora as mlx_lora
    import mlx_lm.tuner.trainer as tuner_trainer
    from mlx.nn.utils import average_gradients
    from mlx.utils import tree_flatten, tree_map

    if getattr(tuner_trainer, "_nemotron_final_accum_flush_patch", False):
        return

    def patched_train(
        model: Any,
        optimizer: Any,
        train_dataset: Any,
        val_dataset: Any,
        args: Any = tuner_trainer.TrainingArgs(),
        loss: Any = tuner_trainer.default_loss,
        iterate_batches: Any = tuner_trainer.iterate_batches,
        training_callback: Any = None,
    ) -> None:
        if mx.metal.is_available():
            mx.set_wired_limit(mx.metal.device_info()["max_recommended_working_set_size"])
        print(f"Starting training..., iters: {args.iters}")
        world = mx.distributed.init()
        world_size = world.size()
        rank = world.rank()
        if world_size > 1:
            print(f"Node {rank} of {world_size}")

        if args.grad_checkpoint:
            tuner_trainer.grad_checkpoint(model.layers[0])

        loss_value_and_grad = nn.value_and_grad(model, loss)

        grad_accum_steps = args.grad_accumulation_steps
        if grad_accum_steps < 1:
            raise ValueError("grad_accumulation_steps must be at least 1")

        state = [model.state, optimizer.state, mx.random.state]

        @partial(mx.compile, inputs=state, outputs=state)
        def step(batch: Any, prev_grad: Any, do_update: bool, grad_divisor: int) -> Any:
            (lvalue, toks), grad = loss_value_and_grad(model, *batch)

            if prev_grad is not None:
                grad = tree_map(lambda x, y: x + y, grad, prev_grad)

            if do_update:
                grad = average_gradients(grad)
                if grad_divisor > 1:
                    grad = tree_map(lambda x: x / grad_divisor, grad)
                optimizer.update(model, grad)
                grad = None

            return lvalue, toks, grad

        model.train()
        losses = 0
        n_tokens = 0
        steps = 0
        trained_tokens = 0
        train_time = 0
        grad_accum = None
        pending_micro_steps = 0

        for it, batch in zip(
            range(1, args.iters + 1),
            iterate_batches(
                dataset=train_dataset,
                batch_size=args.batch_size,
                max_seq_length=args.max_seq_length,
                loop=True,
                comm_group=world,
            ),
        ):
            tic = time.perf_counter()
            if it == 1 or it % args.steps_per_eval == 0 or it == args.iters:
                tic = time.perf_counter()
                val_loss = tuner_trainer.evaluate(
                    model=model,
                    dataset=val_dataset,
                    loss=loss,
                    batch_size=args.batch_size,
                    num_batches=args.val_batches,
                    max_seq_length=args.max_seq_length,
                    iterate_batches=iterate_batches,
                )
                model.train()
                val_time = time.perf_counter() - tic
                if rank == 0:
                    print(
                        f"Iter {it}: "
                        f"Val loss {val_loss:.3f}, "
                        f"Val took {val_time:.3f}s",
                        flush=True,
                    )

                if training_callback is not None:
                    val_info = {
                        "iteration": it - 1,
                        "val_loss": val_loss,
                        "val_time": val_time,
                    }
                    training_callback.on_val_loss_report(val_info)

                tic = time.perf_counter()

            pending_micro_steps += 1
            do_update = pending_micro_steps == grad_accum_steps or it == args.iters
            grad_divisor = pending_micro_steps if do_update else grad_accum_steps
            lvalue, toks, grad_accum = step(batch, grad_accum, do_update, grad_divisor)
            if do_update:
                pending_micro_steps = 0

            losses += lvalue
            n_tokens += toks
            steps += 1
            mx.eval(state, losses, n_tokens, grad_accum)
            train_time += time.perf_counter() - tic

            if it % args.steps_per_report == 0 or it == args.iters:
                train_loss = mx.distributed.all_sum(losses, stream=mx.cpu).item()
                train_loss /= steps * world_size
                n_tokens = mx.distributed.all_sum(n_tokens, stream=mx.cpu).item()
                learning_rate = optimizer.learning_rate.item()
                it_sec = args.steps_per_report / train_time
                tokens_sec = float(n_tokens) / train_time
                trained_tokens += n_tokens
                peak_mem = mx.get_peak_memory() / 1e9
                if rank == 0:
                    print(
                        f"Iter {it}: Train loss {train_loss:.3f}, "
                        f"Learning Rate {learning_rate:.3e}, "
                        f"It/sec {it_sec:.3f}, "
                        f"Tokens/sec {tokens_sec:.3f}, "
                        f"Trained Tokens {trained_tokens}, "
                        f"Peak mem {peak_mem:.3f} GB",
                        flush=True,
                    )

                if training_callback is not None:
                    train_info = {
                        "iteration": it,
                        "train_loss": train_loss,
                        "learning_rate": learning_rate,
                        "iterations_per_second": it_sec,
                        "tokens_per_second": tokens_sec,
                        "trained_tokens": trained_tokens,
                        "peak_memory": peak_mem,
                    }
                    training_callback.on_train_loss_report(train_info)

                losses = 0
                n_tokens = 0
                steps = 0
                train_time = 0

            if it % args.steps_per_save == 0 and rank == 0:
                adapter_weights = dict(tree_flatten(model.trainable_parameters()))
                mx.save_safetensors(str(args.adapter_file), adapter_weights)
                checkpoint = Path(args.adapter_file).parent / f"{it:07d}_adapters.safetensors"
                mx.save_safetensors(str(checkpoint), adapter_weights)
                print(
                    f"Iter {it}: Saved adapter weights to "
                    f"{args.adapter_file} and {checkpoint}.",
                    flush=True,
                )

        if rank == 0:
            adapter_weights = dict(tree_flatten(model.trainable_parameters()))
            mx.save_safetensors(str(args.adapter_file), adapter_weights)
            print(f"Saved final weights to {args.adapter_file}.")

    tuner_trainer.train = patched_train
    mlx_lora.train = patched_train
    tuner_trainer._nemotron_final_accum_flush_patch = True


def prepare_training_run(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    shadow_model_dir = build_shadow_model_dir(
        Path(args.model_root),
        run_root / "shadow_model",
        force=bool(args.force_shadow_model),
    )

    train_csv = Path(args.train_csv).resolve()
    df = pd.read_csv(train_csv)
    validate_training_frame(df, train_csv)
    type_samples = resolve_type_samples(args)
    lora_keys = resolve_lora_keys(args.lora_key or [])
    sampled_train_df = sample_training_df(
        df,
        type_samples=type_samples,
        seed=int(args.seed),
    )
    train_records, record_summary = build_chat_records(sampled_train_df)
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
    sampled_train_df.to_csv(run_root / "sampled_train_split_with_cot.csv", index=False)

    config = build_mlx_lora_config(
        model_path=shadow_model_dir,
        dataset_dir=dataset_dir,
        adapter_dir=adapter_dir,
        resume_adapter_file=(
            Path(args.resume_adapter_file).resolve() if args.resume_adapter_file else None
        ),
        mask_prompt=bool(args.mask_prompt),
        enable_thinking=bool(args.enable_thinking),
        batch_size=int(args.batch_size),
        num_epochs=float(args.num_epochs),
        learning_rate=float(args.learning_rate),
        max_seq_length=int(args.max_seq_length),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        lora_rank=int(args.lora_rank),
        lora_alpha=float(args.lora_alpha),
        lora_dropout=float(args.lora_dropout),
        lora_keys=lora_keys,
        num_layers=int(args.num_layers),
        steps_per_report=int(args.steps_per_report),
        steps_per_eval=int(args.steps_per_eval),
        save_every=int(args.save_every),
        seed=int(args.seed),
        lr_schedule_name=args.lr_schedule_name,
        lr_schedule_end=float(args.lr_schedule_end),
        lr_warmup_ratio=float(args.lr_warmup_ratio),
        lr_schedule_step_unit=str(args.lr_schedule_step_unit),
    )

    config_path = run_root / "mlx_lora_config.yaml"
    write_text(config_path, yaml.safe_dump(config, sort_keys=False))
    command_path = run_root / "train_cmd.sh"
    write_text(command_path, render_train_command(config_path))
    total_optimizer_steps = compute_schedule_steps(
        total_iters=int(config["iters"]),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        schedule_step_unit="optimizer",
    )
    effective_schedule_steps = compute_schedule_steps(
        total_iters=int(config["iters"]),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        schedule_step_unit=str(args.lr_schedule_step_unit),
    )
    final_optimizer_step_microbatches = compute_final_optimizer_step_microbatches(
        total_iters=int(config["iters"]),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
    )

    manifest = {
        "schedule": {
            "step_unit": str(args.lr_schedule_step_unit),
            "total_optimizer_steps": total_optimizer_steps,
            "effective_schedule_steps": effective_schedule_steps,
            "final_optimizer_step_microbatches": final_optimizer_step_microbatches,
            "final_grad_accumulation_flush": True,
        },
        "created_at": utc_now(),
        "repo_root": str(REPO_ROOT),
        "run_root": str(run_root),
        "model_root": str(Path(args.model_root).resolve()),
        "shadow_model_dir": str(shadow_model_dir),
        "train_csv": str(train_csv),
        "base_model_name_or_path": BASE_MODEL_NAME,
        "readme_contract": {
            "max_lora_rank": README_MAX_LORA_RANK,
            "max_tokens": README_MAX_TOKENS,
            "top_p": README_TOP_P,
            "temperature": README_TEMPERATURE,
            "max_num_seqs": README_MAX_NUM_SEQS,
            "max_model_len": README_MAX_MODEL_LEN,
        },
        "sampling": {
            "seed": int(args.seed),
            "type_samples": type_samples,
            "sampled_rows": int(len(sampled_train_df)),
            "sampled_type_counts": {
                str(key): int(value)
                for key, value in sampled_train_df["type"].value_counts().sort_index().items()
            },
        },
        "dataset": {
            "dataset_dir": str(dataset_dir),
            "train_rows": len(train_records),
            "valid_rows": len(valid_records),
            "record_summary": record_summary,
        },
        "training": {
            "batch_size": int(args.batch_size),
            "grad_accumulation_steps": int(args.grad_accumulation_steps),
            "num_epochs": float(args.num_epochs),
            "learning_rate": float(args.learning_rate),
            "max_seq_length": int(args.max_seq_length),
            "mask_prompt": bool(args.mask_prompt),
            "enable_thinking": bool(args.enable_thinking),
            "lora_rank": int(args.lora_rank),
            "lora_alpha": float(args.lora_alpha),
            "lora_dropout": float(args.lora_dropout),
            "lora_keys": list(lora_keys),
            "num_layers": int(args.num_layers),
            "steps_per_report": int(args.steps_per_report),
            "steps_per_eval": int(args.steps_per_eval),
            "save_every": int(config["save_every"]),
            "lr_schedule_name": str(args.lr_schedule_name or ""),
            "lr_schedule_end": float(args.lr_schedule_end),
            "lr_warmup_ratio": float(args.lr_warmup_ratio),
            "lr_schedule_step_unit": str(args.lr_schedule_step_unit),
            "total_iters": int(config["iters"]),
            "optimizer_steps": int(total_optimizer_steps),
            "final_optimizer_step_microbatches": int(final_optimizer_step_microbatches),
            "final_grad_accumulation_flush": True,
            "resume_adapter_file": str(Path(args.resume_adapter_file).resolve())
            if args.resume_adapter_file
            else "",
        },
        "versions": load_versions(),
        "artifacts": {
            "config_path": str(config_path),
            "command_path": str(command_path),
            "adapter_dir": str(adapter_dir),
            "sampled_train_csv": str((run_root / "sampled_train_split_with_cot.csv").resolve()),
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


def bundle_local_mlx_adapter(run_root: Path, adapter_dir: Path) -> dict[str, Any]:
    verify_training_outputs(adapter_dir)
    bundle_root = run_root / "mlx_adapter_bundle"
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    ensure_dir(bundle_root)
    shutil.copy2(adapter_dir / "adapter_config.json", bundle_root / "adapter_config.json")
    shutil.copy2(adapter_dir / "adapters.safetensors", bundle_root / "adapters.safetensors")
    bundle_manifest = {
        "created_at": utc_now(),
        "bundle_root": str(bundle_root),
        "zip_path": str((run_root / "mlx_adapter_bundle.zip").resolve()),
        "note": (
            "This is a local MLX adapter bundle. It is not claimed to be PEFT/vLLM submission-compatible."
        ),
        "files": summarize_directory(bundle_root),
    }
    write_json(bundle_root / "bundle_manifest.json", bundle_manifest)
    zip_path = run_root / "mlx_adapter_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_name in ("adapter_config.json", "adapters.safetensors", "bundle_manifest.json"):
            archive.write(bundle_root / file_name, file_name)
    bundle_manifest["zip_size_bytes"] = zip_path.stat().st_size
    write_json(bundle_root / "bundle_manifest.json", bundle_manifest)
    return bundle_manifest


def run_mlx_lora_training_from_config(config_path: Path) -> None:
    import mlx_lm.lora as mlx_lora

    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    maybe_patch_mlx_chat_dataset_enable_thinking()
    maybe_patch_mlx_trainer_final_accumulation_flush()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.load(handle, Loader=mlx_lora.yaml_loader) or {}
    for key, value in mlx_lora.CONFIG_DEFAULTS.items():
        config.setdefault(key, value)
    mlx_lora.run(argparse.Namespace(**config))


def load_existing_prepare_manifest(run_root: Path) -> dict[str, Any] | None:
    manifest_path = run_root / "prepare_manifest.json"
    if not manifest_path.exists():
        return None
    return load_json(manifest_path, default=None)


def run_prepare_train(args: argparse.Namespace) -> None:
    manifest = prepare_training_run(args)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def run_train(args: argparse.Namespace) -> None:
    run_root = Path(args.output_root).resolve() / args.run_name
    manifest = None if args.force_prepare else load_existing_prepare_manifest(run_root)
    if manifest is None:
        manifest = prepare_training_run(args)
        run_root = Path(manifest["run_root"])
    config_path = Path(manifest["artifacts"]["config_path"]).resolve()
    adapter_dir = Path(manifest["artifacts"]["adapter_dir"]).resolve()
    run_mlx_lora_training_from_config(config_path)
    verify_training_outputs(adapter_dir)
    bundle_manifest = bundle_local_mlx_adapter(run_root, adapter_dir)
    training_result = {
        "created_at": utc_now(),
        "run_root": str(run_root),
        "adapter_dir": str(adapter_dir),
        "adapter_files": summarize_directory(adapter_dir),
        "mlx_bundle": bundle_manifest,
    }
    write_json(run_root / "training_result.json", training_result)
    print(json.dumps(training_result, ensure_ascii=False, indent=2))


def run_train_mlx_config(args: argparse.Namespace) -> None:
    run_mlx_lora_training_from_config(Path(args.config).resolve())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce baseline/nemotron-sft-lora-with-cot-v2 with MLX LoRA using the README.md "
            "submission/evaluation contract as the source of truth."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_shared_train_args(target: argparse.ArgumentParser) -> None:
        target.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
        target.add_argument("--train-csv", type=Path, default=DEFAULT_TRAIN_CSV)
        target.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
        target.add_argument("--run-name", type=str, default=DEFAULT_RUN_NAME)
        target.add_argument("--seed", type=int, default=DEFAULT_SEED)
        target.add_argument("--type-sample", action="append", default=[])
        target.add_argument("--valid-shadow-rows", type=int, default=32)
        target.add_argument("--batch-size", type=int, default=1)
        target.add_argument("--grad-accumulation-steps", type=int, default=8)
        target.add_argument("--num-epochs", type=float, default=2.0)
        target.add_argument("--learning-rate", type=float, default=1e-4)
        target.add_argument("--max-seq-length", type=int, default=4096)
        target.add_argument(
            "--mask-prompt",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="Mask prompt tokens from the loss. Use --no-mask-prompt for HF-style ablations.",
        )
        target.add_argument(
            "--enable-thinking",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="Pass enable_thinking through the chat template when supported.",
        )
        target.add_argument("--lora-rank", type=int, default=32)
        target.add_argument("--lora-alpha", type=float, default=32.0)
        target.add_argument("--lora-dropout", type=float, default=0.05)
        target.add_argument(
            "--lora-key",
            action="append",
            default=[],
            help="Override LoRA target keys. Repeat the flag to provide multiple keys.",
        )
        target.add_argument(
            "--num-layers",
            type=int,
            default=-1,
            help="Use -1 to LoRA-wrap all layers, matching the baseline notebook intent.",
        )
        target.add_argument("--steps-per-report", type=int, default=10)
        target.add_argument("--steps-per-eval", type=int, default=200)
        target.add_argument(
            "--save-every",
            type=int,
            default=0,
            help="Save intermediate adapter checkpoints every N microsteps; 0 keeps final-only behavior.",
        )
        target.add_argument("--lr-schedule-name", type=str, default="cosine_decay")
        target.add_argument("--lr-schedule-end", type=float, default=0.0)
        target.add_argument("--lr-warmup-ratio", type=float, default=0.05)
        target.add_argument(
            "--lr-schedule-step-unit",
            choices=LR_SCHEDULE_STEP_UNITS,
            default="optimizer",
            help="Interpret LR warmup/decay steps in optimizer updates (HF-like) or raw microsteps.",
        )
        target.add_argument("--resume-adapter-file", type=Path, default=None)
        target.add_argument("--force-shadow-model", action="store_true")
        target.add_argument("--force-prepare", action="store_true")

    prepare_train = subparsers.add_parser(
        "prepare-train",
        help="Build the sampled CSV, JSONL dataset, shadow model, and MLX LoRA config.",
    )
    add_shared_train_args(prepare_train)
    prepare_train.set_defaults(func=run_prepare_train)

    train = subparsers.add_parser(
        "train",
        help="Prepare artifacts if needed, then run MLX LoRA training and create a local MLX bundle.",
    )
    add_shared_train_args(train)
    train.set_defaults(func=run_train)

    train_mlx_config = subparsers.add_parser(
        "train-mlx-config",
        help="Internal helper to run mlx_lm.lora from a generated YAML config.",
    )
    train_mlx_config.add_argument("--config", type=Path, required=True)
    train_mlx_config.set_defaults(func=run_train_mlx_config)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
