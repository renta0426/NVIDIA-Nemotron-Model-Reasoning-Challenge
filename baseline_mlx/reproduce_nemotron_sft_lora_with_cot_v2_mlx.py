from __future__ import annotations

import argparse
import copy
import importlib.metadata as importlib_metadata
import json
import math
import os
import random
import re
import shutil
import subprocess
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
NOTEBOOK_CURRENT_PATH = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "nemotron-sft-lora-with-cot-v2.ipynb"
)
NOTEBOOK_ORIGINAL_PATH = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "nemotron-sft-lora-with-cot-v2-original.ipynb"
)
NOTEBOOK_CURRENT_TRAIN_CSV = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "artifacts"
    / "train_split_with_cot_v3f_safe_plus_notformula.csv"
)
NOTEBOOK_ORIGINAL_TRAIN_CSV = DEFAULT_TRAIN_CSV
NOTEBOOK_CURRENT_RUN_NAME = "nemotron_sft_lora_with_cot_v2_mlx_notebook_current_v1"
NOTEBOOK_ORIGINAL_RUN_NAME = "nemotron_sft_lora_with_cot_v2_mlx_notebook_original_v1"
TRAINING_PROFILES = ("baseline-original", "notebook-original", "notebook-current")

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
NOTEBOOK_CURRENT_TYPE_SAMPLES = {
    "Numeral Conversion": 300,
    "Gravitational Constant": 400,
    "Unit Conversion": 700,
    "Text Encryption": 700,
    "Bit Manipulation": 1021,
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
REPORT_STEP_UNITS = ("optimizer", "micro")
PROFILE_OPTION_FLAGS = {
    "train_csv": ("--train-csv",),
    "run_name": ("--run-name",),
    "seed": ("--seed",),
    "type_sample": ("--type-sample",),
    "valid_shadow_rows": ("--valid-shadow-rows",),
    "batch_size": ("--batch-size",),
    "grad_accumulation_steps": ("--grad-accumulation-steps",),
    "num_epochs": ("--num-epochs",),
    "learning_rate": ("--learning-rate",),
    "max_seq_length": ("--max-seq-length",),
    "mask_prompt": ("--mask-prompt", "--no-mask-prompt"),
    "enable_thinking": ("--enable-thinking", "--no-enable-thinking"),
    "lora_rank": ("--lora-rank",),
    "lora_alpha": ("--lora-alpha",),
    "lora_dropout": ("--lora-dropout",),
    "num_layers": ("--num-layers",),
    "steps_per_report": ("--steps-per-report",),
    "steps_per_report_step_unit": ("--steps-per-report-step-unit",),
    "steps_per_eval": ("--steps-per-eval",),
    "save_every": ("--save-every",),
    "flush_on_epoch_boundary": (
        "--flush-on-epoch-boundary",
        "--no-flush-on-epoch-boundary",
    ),
    "lr_schedule_name": ("--lr-schedule-name",),
    "lr_schedule_end": ("--lr-schedule-end",),
    "lr_warmup_ratio": ("--lr-warmup-ratio",),
    "lr_schedule_step_unit": ("--lr-schedule-step-unit",),
}

COMMON_NOTEBOOK_PROFILE_DEFAULTS: dict[str, Any] = {
    "seed": DEFAULT_SEED,
    "valid_shadow_rows": 1,
    "batch_size": 1,
    "grad_accumulation_steps": 8,
    "num_epochs": 2.0,
    "learning_rate": 1e-4,
    "max_seq_length": 4096,
    "mask_prompt": False,
    "enable_thinking": True,
    "lora_rank": 32,
    "lora_alpha": 32.0,
    "lora_dropout": 0.05,
    "num_layers": -1,
    "steps_per_report": 10,
    "steps_per_report_step_unit": "optimizer",
    "steps_per_eval": 0,
    "save_every": 0,
    "flush_on_epoch_boundary": True,
    "lr_schedule_name": "cosine_decay",
    "lr_schedule_end": 0.0,
    "lr_warmup_ratio": 0.05,
    "lr_schedule_step_unit": "optimizer",
}
NOTEBOOK_ORIGINAL_PROFILE_DEFAULTS: dict[str, Any] = {
    **COMMON_NOTEBOOK_PROFILE_DEFAULTS,
    "train_csv": NOTEBOOK_ORIGINAL_TRAIN_CSV,
    "run_name": NOTEBOOK_ORIGINAL_RUN_NAME,
    "type_sample": [f"{key}={value}" for key, value in DEFAULT_TYPE_SAMPLES.items()],
}
NOTEBOOK_CURRENT_PROFILE_DEFAULTS: dict[str, Any] = {
    **COMMON_NOTEBOOK_PROFILE_DEFAULTS,
    "train_csv": NOTEBOOK_CURRENT_TRAIN_CSV,
    "run_name": NOTEBOOK_CURRENT_RUN_NAME,
    "type_sample": [f"{key}={value}" for key, value in NOTEBOOK_CURRENT_TYPE_SAMPLES.items()],
}
NOTEBOOK_ORIGINAL_REFERENCE: dict[str, Any] = {
    "source_notebook": str(NOTEBOOK_ORIGINAL_PATH),
    "source_cells": {
        "lora": 8,
        "training": 10,
        "pretrained_check": 12,
        "packaging": 14,
    },
    "train_csv": str(NOTEBOOK_ORIGINAL_TRAIN_CSV),
    "type_samples": dict(DEFAULT_TYPE_SAMPLES),
    "observed_log": {
        "full_dataset_rows": 6558,
        "sampled_rows": 2907,
        "sft_records": 2907,
        "trainable_params": 880_138_240,
        "all_params": 32_458_075_584,
        "trainable_percent": 2.7116,
        "training_minutes": 405.7,
        "tokenizer_updates": {
            "eos_token_id": 11,
            "pad_token_id": 11,
        },
    },
    "training": {
        "seed": 123,
        "batch_size": 1,
        "grad_accumulation_steps": 8,
        "num_epochs": 2.0,
        "learning_rate": 1e-4,
        "lr_scheduler_type": "cosine",
        "warmup_ratio": 0.05,
        "optimizer_steps": 728,
        "max_seq_length": 4096,
        "logging_steps": 10,
        "logging_step_unit": "optimizer",
        "save_strategy": "no",
        "mask_prompt": False,
        "bf16": True,
        "gradient_checkpointing": True,
        "gradient_checkpointing_kwargs": {"use_reentrant": False},
        "dataloader_num_workers": 2,
        "remove_unused_columns": False,
        "report_to": "none",
        "packing": False,
    },
    "lora": {
        "rank": 32,
        "alpha": 32.0,
        "dropout": 0.05,
        "target_modules_regex": r".*\.(in_proj|out_proj|up_proj|down_proj)$",
    },
    "packaging": {
        "required_files": ["adapter_config.json", "adapter_model.safetensors"],
        "base_model_name_or_path": BASE_MODEL_NAME,
        "inference_mode": True,
        "lora_dropout": 0.0,
    },
}
NOTEBOOK_CURRENT_REFERENCE: dict[str, Any] = {
    "source_notebook": str(NOTEBOOK_CURRENT_PATH),
    "source_cells": {
        "lora": 8,
        "training": 10,
        "packaging": 14,
    },
    "train_csv": str(NOTEBOOK_CURRENT_TRAIN_CSV),
    "type_samples": dict(NOTEBOOK_CURRENT_TYPE_SAMPLES),
    "training": {
        "seed": 123,
        "batch_size": 1,
        "grad_accumulation_steps": 8,
        "num_epochs": 2.0,
        "learning_rate": 1e-4,
        "lr_scheduler_type": "cosine",
        "warmup_ratio": 0.05,
        "optimizer_steps": 832,
        "max_seq_length": 4096,
        "logging_steps": 10,
        "logging_step_unit": "optimizer",
        "save_strategy": "no",
        "mask_prompt": False,
        "bf16": True,
        "gradient_checkpointing": True,
        "gradient_checkpointing_kwargs": {"use_reentrant": False},
        "dataloader_num_workers": 2,
        "remove_unused_columns": False,
        "report_to": "none",
        "packing": False,
    },
    "lora": {
        "rank": 32,
        "alpha": 32.0,
        "dropout": 0.05,
        "target_modules_regex": r".*\.(in_proj|out_proj|up_proj|down_proj)$",
    },
    "packaging": {
        "required_files": ["adapter_config.json", "adapter_model.safetensors"],
        "base_model_name_or_path": BASE_MODEL_NAME,
        "inference_mode": True,
        "lora_dropout": 0.0,
    },
}
NOTEBOOK_PROFILE_SPECS: dict[str, dict[str, Any]] = {
    "notebook-original": {
        "defaults": NOTEBOOK_ORIGINAL_PROFILE_DEFAULTS,
        "reference": NOTEBOOK_ORIGINAL_REFERENCE,
        "artifact_prefix": "notebook_original",
        "audit_summary_name": "notebook_original_audit_summary.json",
    },
    "notebook-current": {
        "defaults": NOTEBOOK_CURRENT_PROFILE_DEFAULTS,
        "reference": NOTEBOOK_CURRENT_REFERENCE,
        "artifact_prefix": "notebook_current",
        "audit_summary_name": "notebook_current_audit_summary.json",
    },
}

PROOF_FIRST_ROUTING_ROOT = (
    REPO_ROOT / "cuda-train-data-analysis-v1" / "proof_first_solver_factory_routing"
)
ROUTE_AWARE_TRAIN_CSV = (
    PROOF_FIRST_ROUTING_ROOT / "artifacts" / "train_split_with_cot_v2_plus_binary_route_aware.csv"
)
BINARY_ROUTE_AWARE_DELTA_CSV = PROOF_FIRST_ROUTING_ROOT / "artifacts" / "binary_route_aware_delta.csv"
PHASE0_OFFLINE_EVAL_ARTIFACT_ROOT = PROOF_FIRST_ROUTING_ROOT / "result" / "phase0_offline_eval" / "artifacts"
LEADERBOARD_PROXY_V1_SET_CSV = (
    PROOF_FIRST_ROUTING_ROOT / "result" / "leaderboard_proxy_v1" / "artifacts" / "leaderboard_proxy_v1_set.csv"
)
BINARY_HARD_SET_CSV = PHASE0_OFFLINE_EVAL_ARTIFACT_ROOT / "binary_hard_set.csv"
GENERAL_STABLE_SET_CSV = PHASE0_OFFLINE_EVAL_ARTIFACT_ROOT / "general_stable_set.csv"
SYMBOL_WATCH_SET_CSV = PHASE0_OFFLINE_EVAL_ARTIFACT_ROOT / "symbol_watch_set.csv"
ATTENTION_LORA_KEYS = [
    "mixer.q_proj",
    "mixer.k_proj",
    "mixer.v_proj",
    "mixer.o_proj",
]
NEMOTRON_STAGE_BROAD_LORA_KEYS = [
    "mixer.in_proj",
    "mixer.out_proj",
    "mixer.switch_mlp.fc1",
    "mixer.switch_mlp.fc2",
    "mixer.shared_experts.up_proj",
    "mixer.shared_experts.down_proj",
]
NEMOTRON_STAGE_UNION_LORA_KEYS = list(
    dict.fromkeys(NEMOTRON_STAGE_BROAD_LORA_KEYS + ATTENTION_LORA_KEYS)
)
LORA_KEY_GROUPS: dict[str, list[str]] = {
    "broad": list(NEMOTRON_STAGE_BROAD_LORA_KEYS),
    "attention": list(ATTENTION_LORA_KEYS),
    "attention-vo": ["mixer.v_proj", "mixer.o_proj"],
    "stage-union": list(NEMOTRON_STAGE_UNION_LORA_KEYS),
}
DEFAULT_STAGE2_BINARY_SOLVERS = (
    "binary_affine_xor",
    "binary_bit_permutation_bijection",
    "binary_structured_byte_formula",
    "binary_structured_byte_formula_abstract",
    "binary_structured_byte_not_formula",
)
DEFAULT_PROXY_V2_FOCUS_BUCKETS = (
    "dominant_structured_safe",
    "supported_affine_xor",
    "supported_bijection",
)
BOXED_PATTERN = re.compile(r"\\boxed\{([^}]*)(?:\}|$)")
FINAL_ANSWER_PATTERNS = (
    r"The final answer is:\s*([^\n]+)",
    r"Final answer is:\s*([^\n]+)",
    r"Final answer\s*[:：]\s*([^\n]+)",
    r"final answer\s*[:：]\s*([^\n]+)",
)
NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
BIT8_PATTERN = re.compile(r"^[01]{8}$")


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


def argv_has_any_flag(raw_argv: Sequence[str], flags: Sequence[str]) -> bool:
    for token in raw_argv:
        for flag in flags:
            if token == flag or token.startswith(f"{flag}="):
                return True
    return False


def get_notebook_profile_spec(profile_name: str | None) -> dict[str, Any] | None:
    if profile_name is None:
        return None
    return NOTEBOOK_PROFILE_SPECS.get(str(profile_name).strip().lower())


def apply_training_profile(args: argparse.Namespace, *, raw_argv: Sequence[str]) -> dict[str, Any] | None:
    profile_name = getattr(args, "profile", None)
    if profile_name is None:
        return None
    resolved_profile = str(profile_name).strip().lower()
    if resolved_profile not in TRAINING_PROFILES:
        raise ValueError(f"Unsupported profile: {profile_name}")
    if resolved_profile == "baseline-original":
        return {"name": resolved_profile, "applied_fields": [], "explicit_fields": []}

    profile_spec = get_notebook_profile_spec(resolved_profile)
    if profile_spec is None:
        raise ValueError(f"Missing notebook profile spec for: {resolved_profile}")
    profile_defaults = profile_spec["defaults"]
    applied_fields: list[str] = []
    explicit_fields: list[str] = []
    for field_name, value in profile_defaults.items():
        flags = PROFILE_OPTION_FLAGS.get(field_name, ())
        if flags and argv_has_any_flag(raw_argv, flags):
            explicit_fields.append(field_name)
            continue
        setattr(args, field_name, copy.deepcopy(value))
        applied_fields.append(field_name)
    return {
        "name": resolved_profile,
        "applied_fields": sorted(applied_fields),
        "explicit_fields": sorted(explicit_fields),
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


def load_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("mlx-lm", "mlx", "transformers", "pyyaml", "pandas"):
        try:
            versions[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def _run_text_command(command: Sequence[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        return 127, str(exc)
    return completed.returncode, completed.stdout or completed.stderr


def collect_memory_pressure_snapshot() -> dict[str, Any]:
    returncode, output = _run_text_command(("memory_pressure",))
    snapshot: dict[str, Any] = {
        "returncode": returncode,
        "head": output.splitlines()[:20],
    }
    match = re.search(r"System-wide memory free percentage:\s*([0-9]+)%", output)
    if match:
        snapshot["system_free_percent"] = int(match.group(1))
    return snapshot


def collect_gpu_snapshot() -> dict[str, Any]:
    returncode, output = _run_text_command(
        ("ioreg", "-r", "-d1", "-c", "IOAccelerator", "-w0", "-l")
    )
    snapshot: dict[str, Any] = {
        "returncode": returncode,
        "head": output.splitlines()[:20],
    }
    for key, field in (
        ("Device Utilization %", "device_util_percent"),
        ("Renderer Utilization %", "renderer_util_percent"),
        ("Tiler Utilization %", "tiler_util_percent"),
        ("Alloc system memory", "alloc_system_memory_bytes"),
        ("In use system memory", "in_use_system_memory_bytes"),
    ):
        match = re.search(rf'"{re.escape(key)}"=([0-9]+)', output)
        if match:
            snapshot[field] = int(match.group(1))
    return snapshot


def _collect_process_rows() -> list[dict[str, Any]] | None:
    returncode, output = _run_text_command(
        ("ps", "-Ao", "pid=,ppid=,rss=,pcpu=,etime=,command=")
    )
    if returncode != 0:
        return None

    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        parts = line.strip().split(None, 5)
        if len(parts) != 6:
            continue
        pid_text, ppid_text, rss_text, pcpu_text, etime, command = parts
        try:
            pid = int(pid_text)
            ppid = int(ppid_text)
            rss_kb = int(rss_text)
            pcpu = float(pcpu_text)
        except ValueError:
            continue
        rows.append(
            {
                "pid": pid,
                "ppid": ppid,
                "rss_kb": rss_kb,
                "pcpu": pcpu,
                "etime": etime,
                "command": command,
            }
        )
    return rows


def _collect_process_ancestors(process_rows: Sequence[dict[str, Any]], *, pid: int) -> set[int]:
    pid_to_ppid = {
        int(row["pid"]): int(row["ppid"])
        for row in process_rows
        if "pid" in row and "ppid" in row
    }
    ancestors: set[int] = set()
    current = pid_to_ppid.get(pid)
    while current is not None and current > 0 and current not in ancestors:
        ancestors.add(current)
        current = pid_to_ppid.get(current)
    return ancestors


def collect_competing_mlx_train_processes(*, current_pid: int) -> list[dict[str, Any]]:
    process_rows = _collect_process_rows()
    if process_rows is None:
        return [{"error": "ps failed"}]

    ignored_related_pids = _collect_process_ancestors(process_rows, pid=current_pid)
    rows: list[dict[str, Any]] = []
    for row in process_rows:
        pid = int(row["pid"])
        ppid = int(row["ppid"])
        rss_kb = int(row["rss_kb"])
        pcpu = float(row["pcpu"])
        etime = str(row["etime"])
        command = str(row["command"])
        if pid == current_pid:
            continue
        if pid in ignored_related_pids:
            continue
        lowered = command.lower()
        if lowered.startswith("uv run python "):
            continue
        if lowered.startswith(("bash -c ", "sh -c ", "zsh -c ")):
            continue
        if "python" not in lowered or " train" not in lowered:
            continue
        if not any(token in lowered for token in ("mlx", "nemotron", "phase2_binary_dsl", "lora")):
            continue
        rows.append(
            {
                "pid": pid,
                "ppid": ppid,
                "rss_kb": rss_kb,
                "pcpu": pcpu,
                "etime": etime,
                "command": command,
            }
        )
    rows.sort(key=lambda row: row["rss_kb"], reverse=True)
    return rows


def collect_runtime_preflight(*, current_pid: int) -> dict[str, Any]:
    return {
        "captured_at": utc_now(),
        "current_pid": current_pid,
        "memory_pressure": collect_memory_pressure_snapshot(),
        "gpu_snapshot": collect_gpu_snapshot(),
        "competing_mlx_train_processes": collect_competing_mlx_train_processes(
            current_pid=current_pid
        ),
    }


def print_runtime_preflight(preflight: dict[str, Any]) -> None:
    memory_pressure = preflight.get("memory_pressure", {})
    gpu_snapshot = preflight.get("gpu_snapshot", {})
    competing = preflight.get("competing_mlx_train_processes", [])
    free_percent = memory_pressure.get("system_free_percent")
    if free_percent is not None:
        print(f"Runtime preflight: system_free_memory={free_percent}%", flush=True)
    if "device_util_percent" in gpu_snapshot:
        print(
            "Runtime preflight: "
            f"gpu_device_util={gpu_snapshot.get('device_util_percent', 'n/a')}% "
            f"renderer={gpu_snapshot.get('renderer_util_percent', 'n/a')}% "
            f"tiler={gpu_snapshot.get('tiler_util_percent', 'n/a')}%",
            flush=True,
        )
    if competing:
        print(
            f"Runtime preflight: detected {len(competing)} other MLX/Nemotron train process(es).",
            flush=True,
        )
        for row in competing[:8]:
            print(
                "  "
                f"pid={row.get('pid')} rss_gb={row.get('rss_kb', 0) / 1_000_000:.3f} "
                f"pcpu={row.get('pcpu')} etime={row.get('etime')} "
                f"cmd={row.get('command')}",
                flush=True,
            )


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


def require_columns(df: pd.DataFrame, path: Path, columns: Sequence[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {path}: {missing}")


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


def dedupe_strings(entries: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for entry in entries:
        value = str(entry).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return dedupe_strings(value.split(","))
    if isinstance(value, Sequence):
        return dedupe_strings([str(item) for item in value])
    return dedupe_strings([str(value)])


def resolve_grouped_string_values(
    *,
    explicit_entries: Sequence[str],
    group_entries: Sequence[str],
    group_map: dict[str, Sequence[str]],
    value_name: str,
) -> list[str]:
    resolved: list[str] = []
    unknown_groups = sorted(set(str(entry).strip() for entry in group_entries if str(entry).strip()) - set(group_map))
    if unknown_groups:
        raise ValueError(f"Unsupported {value_name} groups: {unknown_groups}")
    for group_name in group_entries:
        resolved.extend(group_map[str(group_name).strip()])
    resolved.extend(str(entry).strip() for entry in explicit_entries if str(entry).strip())
    return dedupe_strings(resolved)


def resolve_lora_keys(entries: Sequence[str], group_entries: Sequence[str] = ()) -> list[str]:
    keys = resolve_grouped_string_values(
        explicit_entries=entries,
        group_entries=group_entries,
        group_map=LORA_KEY_GROUPS,
        value_name="LoRA key",
    )
    return keys or list(DEFAULT_LORA_KEYS)


def resolve_trainable_lora_suffixes(
    entries: Sequence[str],
    group_entries: Sequence[str] = (),
) -> list[str]:
    return resolve_grouped_string_values(
        explicit_entries=entries,
        group_entries=group_entries,
        group_map=LORA_KEY_GROUPS,
        value_name="trainable LoRA suffix",
    )


def sample_dataframe_rows(df: pd.DataFrame, *, max_rows: int, seed: int) -> pd.DataFrame:
    if max_rows == 0:
        return df.head(0).copy().reset_index(drop=True)
    if max_rows < 0 or len(df) <= max_rows:
        return df.copy().reset_index(drop=True)
    return df.sample(n=max_rows, random_state=seed).reset_index(drop=True)


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


def resolve_steps_per_eval(*, total_iters: int, steps_per_eval: int) -> int:
    if total_iters <= 0:
        raise ValueError(f"total_iters must be > 0, got {total_iters}")
    if steps_per_eval <= 0:
        return total_iters
    return steps_per_eval


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


def build_corrective_stage2_dataframe(
    *,
    binary_delta_df: pd.DataFrame,
    symbol_source_df: pd.DataFrame,
    symbol_watch_df: pd.DataFrame,
    proxy_v1_df: pd.DataFrame,
    binary_solvers: Sequence[str],
    max_symbol_rows: int,
    max_answer_only_ratio: float,
    seed: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if max_answer_only_ratio < 0.0 or max_answer_only_ratio > 0.5:
        raise ValueError(f"max_answer_only_ratio must be in [0, 0.5], got {max_answer_only_ratio}")

    solver_set = set(dedupe_strings(binary_solvers))
    if not solver_set:
        raise ValueError("At least one binary solver must be selected for the corrective Stage 2 dataset.")

    binary_verified = binary_delta_df[
        binary_delta_df["source_selection_tier"].astype(str).eq("verified_trace_ready")
        & binary_delta_df["teacher_solver_candidate"].astype(str).isin(solver_set)
    ].copy()
    if binary_verified.empty:
        raise ValueError("Binary corrective dataset resolved to zero verified rows.")

    max_answer_only_rows = int(len(binary_verified) * max_answer_only_ratio)
    if max_answer_only_ratio > 0.0 and max_answer_only_rows <= 0:
        max_answer_only_rows = 1
    answer_only_pool = binary_delta_df[
        binary_delta_df["source_selection_tier"].astype(str).eq("answer_only_keep")
        & binary_delta_df["template_subtype"].astype(str).isin(
            ["bit_other", "bit_permutation_inversion", "bit_structured_byte_formula"]
        )
    ].copy()
    binary_answer_only = sample_dataframe_rows(
        answer_only_pool,
        max_rows=max_answer_only_rows,
        seed=seed,
    )

    symbol_watch_ids = set(
        symbol_watch_df[
            symbol_watch_df["template_subtype"].astype(str).eq("numeric_2x2")
            & symbol_watch_df["selection_tier"].astype(str).eq("verified_trace_ready")
        ]["id"].astype(str)
    )
    proxy_symbol_ids = set(
        proxy_v1_df[
            proxy_v1_df["family_short"].astype(str).eq("symbol")
            & proxy_v1_df["template_subtype"].astype(str).eq("numeric_2x2")
            & proxy_v1_df["selection_tier"].astype(str).eq("verified_trace_ready")
        ]["id"].astype(str)
    )
    symbol_candidate_ids = symbol_watch_ids | proxy_symbol_ids
    symbol_rows = symbol_source_df[
        symbol_source_df["id"].astype(str).isin(symbol_candidate_ids)
        & symbol_source_df["type"].astype(str).eq("Equation Transformation")
    ].copy()
    symbol_rows = sample_dataframe_rows(symbol_rows, max_rows=max_symbol_rows, seed=seed)

    frames = [
        binary_verified.loc[:, EXPECTED_COLUMNS],
        binary_answer_only.loc[:, EXPECTED_COLUMNS],
        symbol_rows.loc[:, EXPECTED_COLUMNS],
    ]
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset="id", keep="first")
    combined = combined.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    summary = {
        "created_at": utc_now(),
        "seed": int(seed),
        "binary_solvers": list(solver_set),
        "max_symbol_rows": int(max_symbol_rows),
        "max_answer_only_ratio": float(max_answer_only_ratio),
        "rows": int(len(combined)),
        "binary_verified_rows": int(len(binary_verified)),
        "binary_answer_only_rows": int(len(binary_answer_only)),
        "symbol_rows": int(len(symbol_rows)),
        "type_counts": {
            str(key): int(value)
            for key, value in combined["type"].astype(str).value_counts().sort_index().items()
        },
        "binary_solver_counts": {
            str(key): int(value)
            for key, value in binary_verified["teacher_solver_candidate"].astype(str).value_counts().sort_index().items()
        },
        "binary_selection_tier_counts": {
            str(key): int(value)
            for key, value in pd.concat([binary_verified, binary_answer_only], ignore_index=True)[
                "source_selection_tier"
            ]
            .astype(str)
            .value_counts()
            .sort_index()
            .items()
        },
        "binary_assistant_style_counts": {
            str(key): int(value)
            for key, value in pd.concat([binary_verified, binary_answer_only], ignore_index=True)[
                "assistant_style"
            ]
            .astype(str)
            .value_counts()
            .sort_index()
            .items()
        },
        "symbol_candidate_overlap_rows": int(len(symbol_candidate_ids & set(symbol_source_df["id"].astype(str)))),
    }
    return combined, summary


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
        user_content = build_user_message(str(prompt_text))
        prompts.append(
            apply_chat_template_safe(
                tokenizer,
                [{"role": "user", "content": user_content}],
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
    lines = [line.strip() for line in text.splitlines() if line.strip()]
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
    try:
        return math.isclose(float(gold_text), float(predicted_text), rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted_text.lower() == gold_text.lower()


def safe_div(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def aggregate_counts(rows: Sequence[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket_key = str(row.get(key, "")).strip()
        bucket = buckets.setdefault(bucket_key, {"rows": 0, "correct": 0})
        bucket["rows"] += 1
        bucket["correct"] += int(bool(row.get("is_correct")))
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
    binary_rows = [row for row in rows if str(row.get("family_short", "")).strip() == "binary"]
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
        "format_ok_content_wrong_rate": round(
            safe_div(len(format_ok_but_wrong), len(format_ok)),
            4,
        ),
        "solver_family_accuracy": aggregate_counts(binary_rows, "teacher_solver_candidate"),
    }


def summarize_benchmark_scores(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    correct = sum(int(bool(row.get("is_correct"))) for row in rows)
    return {
        "overall": {
            "rows": len(rows),
            "correct": correct,
            "accuracy": round(safe_div(correct, len(rows)), 4),
        },
        "by_family": aggregate_counts(rows, "family_short"),
        "by_template_subtype": aggregate_counts(rows, "template_subtype"),
        "by_selection_tier": aggregate_counts(rows, "selection_tier"),
        "by_teacher_solver_candidate": aggregate_counts(rows, "teacher_solver_candidate"),
        "binary_metrics": build_binary_metrics(rows),
    }


def render_eval_markdown_summary(name: str, summary: dict[str, Any]) -> str:
    lines = [f"# {name}", "", "## Overall", ""]
    overall = summary["overall"]
    lines.append(f"- rows: `{overall['rows']}`")
    lines.append(f"- correct: `{overall['correct']}`")
    lines.append(f"- accuracy: `{overall['accuracy']:.4f}`")
    lines.append("")

    def add_table(title: str, key_name: str, rows: Sequence[dict[str, Any]]) -> None:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| {key_name} | rows | correct | accuracy |")
        lines.append("| --- | ---: | ---: | ---: |")
        for row in rows:
            lines.append(
                f"| `{row[key_name]}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |"
            )
        lines.append("")

    add_table("By family", "family_short", summary["by_family"])
    add_table("By template subtype", "template_subtype", summary["by_template_subtype"])
    add_table("By selection tier", "selection_tier", summary["by_selection_tier"])
    add_table(
        "By teacher solver candidate",
        "teacher_solver_candidate",
        summary["by_teacher_solver_candidate"],
    )
    binary_metrics = summary["binary_metrics"]
    lines.append("## Binary metrics")
    lines.append("")
    for key, value in binary_metrics.items():
        if key == "solver_family_accuracy":
            continue
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    add_table(
        "Binary solver family accuracy",
        "teacher_solver_candidate",
        binary_metrics["solver_family_accuracy"],
    )
    return "\n".join(lines)


def build_leaderboard_proxy_v2_dataframe(
    *,
    proxy_v1_df: pd.DataFrame,
    binary_hard_df: pd.DataFrame,
    symbol_watch_df: pd.DataFrame,
    focus_buckets: Sequence[str],
    binary_solvers: Sequence[str],
    max_binary_hard_rows: int,
    max_symbol_rows: int,
    seed: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    focus_bucket_set = set(dedupe_strings(focus_buckets))
    solver_set = set(dedupe_strings(binary_solvers))
    if not focus_bucket_set:
        raise ValueError("At least one proxy focus bucket must be selected.")
    if not solver_set:
        raise ValueError("At least one binary solver must be selected for proxy v2.")

    proxy_focus = proxy_v1_df[
        proxy_v1_df["leaderboard_proxy_bucket"].astype(str).isin(focus_bucket_set)
        | proxy_v1_df["teacher_solver_candidate"].astype(str).isin(solver_set)
    ].copy()
    proxy_focus["proxy_v2_source"] = "leaderboard_proxy_v1_focus"

    binary_hard_topup = binary_hard_df[
        binary_hard_df["teacher_solver_candidate"].astype(str).isin(solver_set)
    ].copy()
    binary_hard_topup = binary_hard_topup.sort_values(
        by=["hard_score", "num_examples", "id"],
        ascending=[False, False, True],
    )
    binary_hard_topup = sample_dataframe_rows(
        binary_hard_topup,
        max_rows=max_binary_hard_rows,
        seed=seed,
    )
    binary_hard_topup["proxy_v2_source"] = "binary_hard_topup"

    proxy_symbol = proxy_v1_df[
        proxy_v1_df["family_short"].astype(str).eq("symbol")
        & proxy_v1_df["template_subtype"].astype(str).eq("numeric_2x2")
        & proxy_v1_df["selection_tier"].astype(str).eq("verified_trace_ready")
    ].copy()
    symbol_watch = symbol_watch_df[
        symbol_watch_df["template_subtype"].astype(str).eq("numeric_2x2")
        & symbol_watch_df["selection_tier"].astype(str).eq("verified_trace_ready")
    ].copy()
    symbol_focus = pd.concat([proxy_symbol, symbol_watch], ignore_index=True, sort=False)
    if not symbol_focus.empty:
        symbol_focus = symbol_focus.sort_values(
            by=["hard_score", "num_examples", "id"],
            ascending=[False, False, True],
        )
        symbol_focus = sample_dataframe_rows(symbol_focus, max_rows=max_symbol_rows, seed=seed)
        symbol_focus["proxy_v2_source"] = "symbol_numeric_watch"

    combined = pd.concat(
        [proxy_focus, binary_hard_topup, symbol_focus],
        ignore_index=True,
        sort=False,
    )
    combined = combined.drop_duplicates(subset="id", keep="first").reset_index(drop=True)
    combined["benchmark_name"] = "leaderboard_proxy_v2_set"
    combined["benchmark_role"] = "leaderboard_proxy_v2"
    combined["benchmark_index"] = list(range(1, len(combined) + 1))

    def resolve_proxy_v2_focus_bucket(row: pd.Series) -> str:
        for field_name in ("leaderboard_proxy_bucket", "teacher_solver_candidate"):
            value = row.get(field_name, "")
            if pd.notna(value):
                text = str(value).strip()
                if text and text.lower() != "nan":
                    return text
        family_short = str(row.get("family_short", "")).strip()
        template_subtype = str(row.get("template_subtype", "")).strip()
        return f"{family_short}:{template_subtype}".strip(":")

    combined["proxy_v2_focus_bucket"] = combined.apply(
        resolve_proxy_v2_focus_bucket,
        axis=1,
    )
    combined["proxy_v2_note"] = combined["proxy_v2_source"].map(
        {
            "leaderboard_proxy_v1_focus": "Focused hidden-gap slices from leaderboard_proxy_v1.",
            "binary_hard_topup": "Hard binary top-up for safe/bijection/structured-formula solvers.",
            "symbol_numeric_watch": "Small numeric_2x2 symbol watch slice to guard route-sensitive symbol drift.",
        }
    )

    preferred_columns = [
        "benchmark_name",
        "benchmark_role",
        "benchmark_index",
        "id",
        "prompt",
        "answer",
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
        "leaderboard_proxy_bucket",
        "proxy_v2_source",
        "proxy_v2_focus_bucket",
        "proxy_v2_note",
    ]
    ordered_columns = dedupe_strings(preferred_columns + list(combined.columns))
    combined = combined.loc[:, ordered_columns]
    summary = {
        "created_at": utc_now(),
        "seed": int(seed),
        "focus_buckets": list(focus_bucket_set),
        "binary_solvers": list(solver_set),
        "rows": int(len(combined)),
        "rows_by_source": {
            str(key): int(value)
            for key, value in combined["proxy_v2_source"].astype(str).value_counts().sort_index().items()
        },
        "rows_by_focus_bucket": {
            str(key): int(value)
            for key, value in combined["proxy_v2_focus_bucket"].astype(str).value_counts().sort_index().items()
        },
        "rows_by_family": {
            str(key): int(value)
            for key, value in combined["family_short"].astype(str).value_counts().sort_index().items()
        },
        "rows_by_solver": {
            str(key): int(value)
            for key, value in combined["teacher_solver_candidate"].astype(str).value_counts().sort_index().items()
        },
    }
    return combined, summary


def run_eval_benchmark_csv(args: argparse.Namespace) -> None:
    from mlx_lm import batch_generate, generate, load
    from mlx_lm.sample_utils import make_sampler

    benchmark_csv = Path(args.benchmark_csv).resolve()
    output_root = Path(args.output_root).resolve()
    ensure_dir(output_root)

    benchmark_df = pd.read_csv(benchmark_csv)
    require_columns(benchmark_df, benchmark_csv, ["id", "prompt", "answer"])
    for optional_column in (
        "benchmark_name",
        "benchmark_role",
        "family",
        "family_short",
        "template_subtype",
        "selection_tier",
        "teacher_solver_candidate",
        "answer_type",
        "num_examples",
        "prompt_len_chars",
    ):
        if optional_column not in benchmark_df.columns:
            benchmark_df[optional_column] = ""
    if not benchmark_df["benchmark_name"].astype(str).str.strip().any():
        benchmark_df["benchmark_name"] = benchmark_csv.stem
    if not benchmark_df["prompt_len_chars"].astype(str).str.strip().any():
        benchmark_df["prompt_len_chars"] = benchmark_df["prompt"].astype(str).map(len)
    benchmark_rows = benchmark_df.to_dict(orient="records")

    load_kwargs: dict[str, Any] = {"lazy": bool(args.lazy_load)}
    if args.adapter_dir is not None:
        load_kwargs["adapter_path"] = str(Path(args.adapter_dir).resolve())
    model, tokenizer = load(str(Path(args.model_root).resolve()), **load_kwargs)
    normalize_tokenizer_for_hf_parity(tokenizer)
    prompts = build_eval_prompts(
        tokenizer,
        [str(row["prompt"]) for row in benchmark_rows],
        enable_thinking=bool(args.eval_enable_thinking),
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

    records: list[dict[str, Any]] = []
    total_prompts = len(prompt_tokens)
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
            records.append(
                {
                    "benchmark_name": str(row.get("benchmark_name", benchmark_csv.stem)),
                    "benchmark_role": str(row.get("benchmark_role", "")),
                    "id": str(row["id"]),
                    "family": str(row.get("family", "")),
                    "family_short": str(row.get("family_short", "")),
                    "template_subtype": str(row.get("template_subtype", "")),
                    "selection_tier": str(row.get("selection_tier", "")),
                    "teacher_solver_candidate": str(row.get("teacher_solver_candidate", "")),
                    "answer_type": str(row.get("answer_type", "")),
                    "num_examples": str(row.get("num_examples", "")),
                    "prompt_len_chars": str(row.get("prompt_len_chars", "")),
                    "expected_answer": str(row["answer"]),
                    "rendered_prompt": rendered_prompt,
                    "raw_output": str(raw_output),
                    "extracted_answer": extract_final_answer(str(raw_output)),
                }
            )

    scored_rows: list[dict[str, Any]] = []
    for row in records:
        derived = analyze_raw_output(row["raw_output"])
        prediction = str(derived["extracted_answer"])
        scored_rows.append(
            {
                "benchmark_name": row["benchmark_name"],
                "benchmark_role": row["benchmark_role"],
                "id": row["id"],
                "gold_answer": row["expected_answer"],
                "prediction": prediction,
                "is_correct": verify_answer(row["expected_answer"], prediction),
                "family": row["family"],
                "family_short": row["family_short"],
                "template_subtype": row["template_subtype"],
                "selection_tier": row["selection_tier"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "answer_type": row["answer_type"],
                "num_examples": row["num_examples"],
                "prompt_len_chars": row["prompt_len_chars"],
                "fallback_type": derived["fallback_type"],
                "format_bucket": derived["format_bucket"],
                "has_boxed": derived["has_boxed"],
                "boxed_count": derived["boxed_count"],
                "raw_output": row["raw_output"],
            }
        )

    summary = summarize_benchmark_scores(scored_rows)
    payload = {
        "created_at": utc_now(),
        "benchmark_csv": str(benchmark_csv),
        "model_root": str(Path(args.model_root).resolve()),
        "adapter_dir": str(Path(args.adapter_dir).resolve()) if args.adapter_dir else "",
        "readme_eval_assumptions": {
            "metric": "accuracy",
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "max_tokens": int(args.max_tokens),
            "max_num_seqs": int(args.max_num_seqs),
            "max_model_len": int(args.max_model_len),
            "boxed_first_extraction": True,
            "numeric_relative_tolerance": 1e-2,
            "eval_enable_thinking": bool(args.eval_enable_thinking),
        },
        **summary,
    }

    raw_outputs_path = output_root / "benchmark_eval_raw_outputs.csv"
    row_level_path = output_root / "benchmark_eval_row_level.csv"
    summary_json_path = output_root / "benchmark_eval_summary.json"
    summary_md_path = output_root / "benchmark_eval_summary.md"
    pd.DataFrame.from_records(records).to_csv(raw_outputs_path, index=False)
    pd.DataFrame.from_records(scored_rows).to_csv(row_level_path, index=False)
    write_json(summary_json_path, payload)
    write_text(summary_md_path, render_eval_markdown_summary(benchmark_csv.stem, payload))
    print(json.dumps(payload, ensure_ascii=False, indent=2))


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


def compute_microsteps_per_epoch(*, num_rows: int, batch_size: int) -> int:
    if batch_size <= 0:
        raise ValueError(f"batch_size must be > 0, got {batch_size}")
    if num_rows <= 0:
        raise ValueError(f"num_rows must be > 0, got {num_rows}")
    # Match mlx_lm.tuner.trainer.iterate_batches(), which drops an incomplete tail batch.
    return max(1, num_rows // batch_size)


def compute_optimizer_steps(
    *,
    total_iters: int,
    grad_accumulation_steps: int,
    microsteps_per_epoch: int,
    flush_on_epoch_boundary: bool,
) -> int:
    if total_iters <= 0:
        raise ValueError(f"total_iters must be > 0, got {total_iters}")
    if grad_accumulation_steps <= 0:
        raise ValueError(
            f"grad_accumulation_steps must be > 0, got {grad_accumulation_steps}"
        )
    if microsteps_per_epoch <= 0:
        raise ValueError(f"microsteps_per_epoch must be > 0, got {microsteps_per_epoch}")
    if not flush_on_epoch_boundary:
        return max(1, (total_iters + grad_accumulation_steps - 1) // grad_accumulation_steps)

    remaining = total_iters
    optimizer_steps = 0
    while remaining > 0:
        chunk = min(microsteps_per_epoch, remaining)
        optimizer_steps += max(1, (chunk + grad_accumulation_steps - 1) // grad_accumulation_steps)
        remaining -= chunk
    return optimizer_steps


def compute_schedule_steps(
    *,
    total_iters: int,
    grad_accumulation_steps: int,
    microsteps_per_epoch: int,
    flush_on_epoch_boundary: bool,
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
    return compute_optimizer_steps(
        total_iters=total_iters,
        grad_accumulation_steps=grad_accumulation_steps,
        microsteps_per_epoch=microsteps_per_epoch,
        flush_on_epoch_boundary=flush_on_epoch_boundary,
    )


def compute_final_optimizer_step_microbatches(
    *,
    total_iters: int,
    grad_accumulation_steps: int,
    microsteps_per_epoch: int | None = None,
    flush_on_epoch_boundary: bool = False,
) -> int:
    if total_iters <= 0:
        raise ValueError(f"total_iters must be > 0, got {total_iters}")
    if grad_accumulation_steps <= 0:
        raise ValueError(
            f"grad_accumulation_steps must be > 0, got {grad_accumulation_steps}"
        )
    scoped_total_iters = total_iters
    if flush_on_epoch_boundary:
        if microsteps_per_epoch is None or microsteps_per_epoch <= 0:
            raise ValueError(
                f"microsteps_per_epoch must be > 0 when flush_on_epoch_boundary=True, got {microsteps_per_epoch}"
            )
        scoped_total_iters = total_iters % microsteps_per_epoch or microsteps_per_epoch
    remainder = scoped_total_iters % grad_accumulation_steps
    if remainder:
        return remainder
    return min(scoped_total_iters, grad_accumulation_steps)


def build_notebook_parity_report(
    *,
    args: argparse.Namespace,
    train_csv: Path,
    type_samples: dict[str, int],
    lora_keys: Sequence[str],
) -> dict[str, Any]:
    profile_spec = get_notebook_profile_spec(str(getattr(args, "profile", "")))
    if profile_spec is None:
        raise ValueError(f"Profile does not have notebook parity metadata: {getattr(args, 'profile', '')}")
    reference = profile_spec["reference"]
    notebook_training = reference["training"]
    notebook_lora = reference["lora"]
    expected_train_csv = Path(reference["train_csv"]).resolve()
    expected_type_samples = dict(reference["type_samples"])
    train_csv_matches = train_csv.resolve() == expected_train_csv
    type_sample_matches = type_samples == expected_type_samples
    sampled_rows = int(sum(type_samples.values()))
    total_iters = compute_total_iters(
        num_rows=sampled_rows,
        num_epochs=float(args.num_epochs),
        batch_size=int(args.batch_size),
    )
    microsteps_per_epoch = compute_microsteps_per_epoch(
        num_rows=sampled_rows,
        batch_size=int(args.batch_size),
    )
    resolved_optimizer_steps = compute_optimizer_steps(
        total_iters=total_iters,
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        microsteps_per_epoch=microsteps_per_epoch,
        flush_on_epoch_boundary=bool(getattr(args, "flush_on_epoch_boundary", False)),
    )
    lora_key_set = set(str(key) for key in lora_keys)
    required_generic_keys = {
        "mixer.in_proj",
        "mixer.out_proj",
        "mixer.up_proj",
        "mixer.down_proj",
    }
    missing_lora_keys = sorted(required_generic_keys - lora_key_set)
    extra_mlx_equivalents = sorted(lora_key_set - required_generic_keys)

    core_checks = [
        {
            "name": "train_csv",
            "expected": str(expected_train_csv),
            "actual": str(train_csv),
            "status": "aligned" if train_csv_matches else "mismatch",
        },
        {
            "name": "type_samples",
            "expected": dict(expected_type_samples),
            "actual": dict(type_samples),
            "status": "aligned" if type_sample_matches else "mismatch",
        },
        {
            "name": "seed",
            "expected": notebook_training["seed"],
            "actual": int(args.seed),
            "status": "aligned" if int(args.seed) == notebook_training["seed"] else "mismatch",
        },
        {
            "name": "batch_size",
            "expected": notebook_training["batch_size"],
            "actual": int(args.batch_size),
            "status": "aligned"
            if int(args.batch_size) == notebook_training["batch_size"]
            else "mismatch",
        },
        {
            "name": "grad_accumulation_steps",
            "expected": notebook_training["grad_accumulation_steps"],
            "actual": int(args.grad_accumulation_steps),
            "status": "aligned"
            if int(args.grad_accumulation_steps) == notebook_training["grad_accumulation_steps"]
            else "mismatch",
        },
        {
            "name": "num_epochs",
            "expected": notebook_training["num_epochs"],
            "actual": float(args.num_epochs),
            "status": "aligned"
            if float(args.num_epochs) == notebook_training["num_epochs"]
            else "mismatch",
        },
        {
            "name": "learning_rate",
            "expected": notebook_training["learning_rate"],
            "actual": float(args.learning_rate),
            "status": "aligned"
            if float(args.learning_rate) == notebook_training["learning_rate"]
            else "mismatch",
        },
        {
            "name": "lr_scheduler",
            "expected": notebook_training["lr_scheduler_type"],
            "actual": str(args.lr_schedule_name),
            "status": "aligned" if str(args.lr_schedule_name) == "cosine_decay" else "mismatch",
            "note": "MLX cosine_decay is the notebook cosine equivalent.",
        },
        {
            "name": "warmup_ratio",
            "expected": notebook_training["warmup_ratio"],
            "actual": float(args.lr_warmup_ratio),
            "status": "aligned"
            if float(args.lr_warmup_ratio) == notebook_training["warmup_ratio"]
            else "mismatch",
        },
        {
            "name": "optimizer_steps",
            "expected": notebook_training["optimizer_steps"],
            "actual": resolved_optimizer_steps,
            "status": "aligned"
            if int(resolved_optimizer_steps) == int(notebook_training["optimizer_steps"])
            else "mismatch",
            "note": "Notebook parity requires flushing grad accumulation at each epoch boundary, not only at the final global remainder.",
        },
        {
            "name": "max_seq_length",
            "expected": notebook_training["max_seq_length"],
            "actual": int(args.max_seq_length),
            "status": "aligned"
            if int(args.max_seq_length) == notebook_training["max_seq_length"]
            else "mismatch",
        },
        {
            "name": "logging_steps",
            "expected": f"{notebook_training['logging_steps']} {notebook_training['logging_step_unit']}",
            "actual": f"{int(args.steps_per_report)} {str(getattr(args, 'steps_per_report_step_unit', 'micro'))}",
            "status": "aligned"
            if (
                int(args.steps_per_report) == notebook_training["logging_steps"]
                and str(getattr(args, "steps_per_report_step_unit", "micro"))
                == notebook_training["logging_step_unit"]
            )
            else "mismatch",
            "note": "HF logging_steps counts optimizer updates, not raw microsteps.",
        },
        {
            "name": "save_strategy",
            "expected": notebook_training["save_strategy"],
            "actual": int(args.save_every),
            "status": "aligned" if int(args.save_every) <= 0 else "mismatch",
            "note": "MLX save_every<=0 means final-only save, matching save_strategy='no'.",
        },
        {
            "name": "mask_prompt",
            "expected": bool(notebook_training["mask_prompt"]),
            "actual": bool(args.mask_prompt),
            "status": "aligned"
            if bool(args.mask_prompt) == bool(notebook_training["mask_prompt"])
            else "mismatch",
            "note": (
                "HF notebook does not enable assistant_only_loss/completion_only_loss here; "
                "MLX parity should therefore keep mask_prompt=False."
            ),
        },
        {
            "name": "lora_rank",
            "expected": notebook_lora["rank"],
            "actual": int(args.lora_rank),
            "status": "aligned" if int(args.lora_rank) == notebook_lora["rank"] else "mismatch",
        },
        {
            "name": "lora_alpha",
            "expected": notebook_lora["alpha"],
            "actual": float(args.lora_alpha),
            "status": "aligned"
            if float(args.lora_alpha) == notebook_lora["alpha"]
            else "mismatch",
        },
        {
            "name": "lora_dropout",
            "expected": notebook_lora["dropout"],
            "actual": float(args.lora_dropout),
            "status": "aligned"
            if float(args.lora_dropout) == notebook_lora["dropout"]
            else "mismatch",
        },
    ]
    lora_target_mapping = {
        "expected_regex": notebook_lora["target_modules_regex"],
        "actual_keys": sorted(lora_key_set),
        "required_generic_keys": sorted(required_generic_keys),
        "missing_generic_keys": missing_lora_keys,
        "extra_mlx_equivalents": extra_mlx_equivalents,
        "status": "aligned" if not missing_lora_keys else "mismatch",
        "note": (
            "MLX keys must cover the notebook's in/out/up/down projection intent; "
            "extra switch/shared-expert keys are intentional Nemotron-H MoE mappings."
        ),
    }
    framework_specific_mappings = [
        {
            "notebook": "bf16=True",
            "mlx": "DEFAULT_MODEL_ROOT is a BF16 MLX checkpoint.",
        },
        {
            "notebook": "gradient_checkpointing=True, use_reentrant=False",
            "mlx": "build_mlx_lora_config forces grad_checkpoint=True.",
        },
        {
            "notebook": "logging_steps=10 optimizer updates",
            "mlx": "steps_per_report=10 with steps_per_report_step_unit=optimizer for comparable loss/LR checkpoints.",
        },
        {
            "notebook": "messages dataset without assistant_only_loss/completion_only_loss",
            "mlx": "Use mask_prompt=False for parity with full-sequence loss.",
        },
        {
            "notebook": "dataloader_num_workers=2",
            "mlx": "No equivalent knob in mlx_lm LoRA config.",
        },
        {
            "notebook": "remove_unused_columns=False, report_to='none', packing=False",
            "mlx": "Not applicable to mlx_lm dataset/config surface.",
        },
    ]
    mlx_scaffolding = [
        {
            "name": "valid_shadow_rows",
            "actual": int(args.valid_shadow_rows),
            "note": "HF notebook has no validation loop; MLX uses a tiny shadow validation set only for observability.",
        },
        {
            "name": "steps_per_eval",
            "requested": int(args.steps_per_eval),
            "resolved_behavior": "iter1_and_final_only"
            if int(args.steps_per_eval) <= 0
            else f"every_{int(args.steps_per_eval)}_iters",
            "note": "steps_per_eval<=0 resolves to total_iters so there are no intermediate validations.",
        },
        {
            "name": "lr_schedule_step_unit",
            "actual": str(args.lr_schedule_step_unit),
            "note": "Optimizer-step scheduling is required for notebook parity under mlx_lm grad accumulation.",
        },
        {
            "name": "shadow_model",
            "actual": True,
            "note": "MLX load path uses a patched shadow_model to avoid tokenizer/runtime mismatches.",
        },
        {
            "name": "tokenizer_special_tokens",
            "actual": True,
            "note": (
                "MLX training load normalizes eos_token_ids and sets pad_token=eos_token when absent, "
                "matching the HF log alignment to eos/pad token id 11."
            ),
        },
        {
            "name": "final_grad_accumulation_flush",
            "actual": True,
            "note": "MLX trainer is patched so the final partial accumulation matches notebook optimizer-step count.",
        },
    ]
    packaging_note = {
        "notebook": dict(reference["packaging"]),
        "mlx_current": {
            "required_files": ["adapter_config.json", "adapters.safetensors"],
            "bundle": "mlx_adapter_bundle.zip",
            "note": "This script still emits a local MLX bundle and does not claim PEFT/vLLM submission compatibility.",
        },
    }
    clear_omissions = [
        check["name"] for check in core_checks if check["status"] != "aligned"
    ]
    if missing_lora_keys:
        clear_omissions.append("lora_target_coverage")
    return {
        "status": "no_clear_omissions" if not clear_omissions else "mismatches_found",
        "source_notebook": reference["source_notebook"],
        "source_cells": dict(reference["source_cells"]),
        "profile": str(getattr(args, "profile", "")),
        "observed_log": dict(reference["observed_log"]) if "observed_log" in reference else None,
        "core_checks": core_checks,
        "lora_target_mapping": lora_target_mapping,
        "framework_specific_mappings": framework_specific_mappings,
        "mlx_scaffolding": mlx_scaffolding,
        "packaging_note": packaging_note,
        "clear_omissions": clear_omissions,
}


def render_notebook_parity_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Notebook parity report",
        "",
        f"- status: **{report['status']}**",
        f"- notebook: `{report['source_notebook']}`",
        f"- profile: `{report['profile']}`",
        "",
        "## Core checks",
        "",
        "| check | status | expected | actual | note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["core_checks"]:
        lines.append(
            "| {name} | {status} | `{expected}` | `{actual}` | {note} |".format(
                name=row["name"],
                status=row["status"],
                expected=str(row.get("expected", "")).replace("|", "\\|"),
                actual=str(row.get("actual", "")).replace("|", "\\|"),
                note=str(row.get("note", "")).replace("|", "\\|"),
            )
        )
    mapping = report["lora_target_mapping"]
    lines.extend(
        [
            "",
            "## LoRA target mapping",
            "",
            f"- status: **{mapping['status']}**",
            f"- required generic keys: `{mapping['required_generic_keys']}`",
            f"- missing generic keys: `{mapping['missing_generic_keys']}`",
            f"- extra MLX equivalents: `{mapping['extra_mlx_equivalents']}`",
            f"- note: {mapping['note']}",
            "",
            "## MLX scaffolding",
            "",
        ]
    )
    for row in report["mlx_scaffolding"]:
        lines.append(f"- `{row['name']}`: {row['note']}")
    observed_log = report.get("observed_log")
    if observed_log:
        lines.extend(
            [
                "",
                "## Observed notebook log",
                "",
            ]
        )
        for key, value in observed_log.items():
            lines.append(f"- `{key}`: `{value}`")
    if report["clear_omissions"]:
        lines.extend(
            [
                "",
                "## Clear omissions",
                "",
                f"- `{report['clear_omissions']}`",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Clear omissions",
                "",
                "- none",
            ]
        )
    return "\n".join(lines) + "\n"


def write_notebook_parity_artifacts(
    *,
    run_root: Path,
    args: argparse.Namespace,
    train_csv: Path,
    type_samples: dict[str, int],
    lora_keys: Sequence[str],
) -> dict[str, Any] | None:
    profile_spec = get_notebook_profile_spec(str(getattr(args, "profile", "")))
    if profile_spec is None:
        return None
    report = build_notebook_parity_report(
        args=args,
        train_csv=train_csv,
        type_samples=type_samples,
        lora_keys=lora_keys,
    )
    artifact_prefix = str(profile_spec["artifact_prefix"])
    json_path = run_root / f"{artifact_prefix}_parity_report.json"
    markdown_path = run_root / f"{artifact_prefix}_parity_report.md"
    write_json(json_path, report)
    write_text(markdown_path, render_notebook_parity_markdown(report))
    return {
        "status": report["status"],
        "clear_omissions": list(report["clear_omissions"]),
        "artifact_prefix": artifact_prefix,
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
    }


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
    trainable_lora_suffixes: Sequence[str],
    num_layers: int,
    steps_per_report: int,
    steps_per_report_step_unit: str,
    steps_per_eval: int,
    save_every: int,
    flush_on_epoch_boundary: bool,
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
    num_train_rows = sum(1 for _ in (dataset_dir / "train.jsonl").open("r", encoding="utf-8"))
    total_iters = compute_total_iters(
        num_rows=num_train_rows,
        num_epochs=num_epochs,
        batch_size=batch_size,
    )
    microsteps_per_epoch = compute_microsteps_per_epoch(
        num_rows=num_train_rows,
        batch_size=batch_size,
    )
    resolved_steps_per_eval = resolve_steps_per_eval(
        total_iters=total_iters,
        steps_per_eval=steps_per_eval,
    )
    schedule_steps = compute_schedule_steps(
        total_iters=total_iters,
        grad_accumulation_steps=grad_accumulation_steps,
        microsteps_per_epoch=microsteps_per_epoch,
        flush_on_epoch_boundary=flush_on_epoch_boundary,
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
        "steps_per_report_step_unit": steps_per_report_step_unit,
        "steps_per_eval": resolved_steps_per_eval,
        "grad_accumulation_steps": grad_accumulation_steps,
        "flush_on_epoch_boundary": flush_on_epoch_boundary,
        "microsteps_per_epoch": microsteps_per_epoch,
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
    if trainable_lora_suffixes:
        config["trainable_lora_suffixes"] = list(trainable_lora_suffixes)
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
        report_step_unit = str(getattr(args, "steps_per_report_step_unit", "micro")).strip().lower()
        if report_step_unit not in REPORT_STEP_UNITS:
            raise ValueError(
                f"steps_per_report_step_unit must be one of {REPORT_STEP_UNITS}, got {report_step_unit!r}"
            )
        flush_on_epoch_boundary = bool(getattr(args, "flush_on_epoch_boundary", False))
        microsteps_per_epoch = int(getattr(args, "microsteps_per_epoch", 0) or 0)
        if flush_on_epoch_boundary:
            if microsteps_per_epoch <= 0:
                microsteps_per_epoch = compute_microsteps_per_epoch(
                    num_rows=len(train_dataset),
                    batch_size=args.batch_size,
                )
        else:
            microsteps_per_epoch = 0

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
        optimizer_updates = 0

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
            epoch_boundary = flush_on_epoch_boundary and microsteps_per_epoch > 0 and (
                it % microsteps_per_epoch == 0
            )
            do_update = pending_micro_steps == grad_accum_steps or epoch_boundary or it == args.iters
            grad_divisor = pending_micro_steps if do_update else grad_accum_steps
            lvalue, toks, grad_accum = step(batch, grad_accum, do_update, grad_divisor)
            if do_update:
                pending_micro_steps = 0
                optimizer_updates += 1

            losses += lvalue
            n_tokens += toks
            steps += 1
            mx.eval(state, losses, n_tokens, grad_accum)
            train_time += time.perf_counter() - tic

            report_due = False
            if report_step_unit == "micro":
                report_due = it % args.steps_per_report == 0 or it == args.iters
            else:
                report_due = do_update and (
                    optimizer_updates % args.steps_per_report == 0 or it == args.iters
                )

            if report_due:
                train_loss = mx.distributed.all_sum(losses, stream=mx.cpu).item()
                train_loss /= steps * world_size
                n_tokens = mx.distributed.all_sum(n_tokens, stream=mx.cpu).item()
                learning_rate = optimizer.learning_rate.item()
                it_sec = steps / train_time
                tokens_sec = float(n_tokens) / train_time
                trained_tokens += n_tokens
                peak_mem = mx.get_peak_memory() / 1e9
                if rank == 0:
                    prefix = f"Iter {it}"
                    if report_step_unit == "optimizer":
                        prefix += f" (Opt {optimizer_updates})"
                    print(
                        f"{prefix}: Train loss {train_loss:.3f}, "
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
                        "optimizer_step": optimizer_updates,
                        "train_loss": train_loss,
                        "learning_rate": learning_rate,
                        "iterations_per_second": it_sec,
                        "tokens_per_second": tokens_sec,
                        "trained_tokens": trained_tokens,
                        "peak_memory": peak_mem,
                        "steps_per_report_step_unit": report_step_unit,
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
    lora_keys = resolve_lora_keys(args.lora_key or [], args.lora_key_group or [])
    trainable_lora_suffixes = resolve_trainable_lora_suffixes(
        args.trainable_lora_suffix or [],
        args.trainable_lora_suffix_group or [],
    )
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
        trainable_lora_suffixes=trainable_lora_suffixes,
        num_layers=int(args.num_layers),
        steps_per_report=int(args.steps_per_report),
        steps_per_report_step_unit=str(args.steps_per_report_step_unit),
        steps_per_eval=int(args.steps_per_eval),
        save_every=int(args.save_every),
        flush_on_epoch_boundary=bool(getattr(args, "flush_on_epoch_boundary", False)),
        seed=int(args.seed),
        lr_schedule_name=args.lr_schedule_name,
        lr_schedule_end=float(args.lr_schedule_end),
        lr_warmup_ratio=float(args.lr_warmup_ratio),
        lr_schedule_step_unit=str(args.lr_schedule_step_unit),
    )
    notebook_parity_artifacts = write_notebook_parity_artifacts(
        run_root=run_root,
        args=args,
        train_csv=train_csv,
        type_samples=type_samples,
        lora_keys=lora_keys,
    )

    config_path = run_root / "mlx_lora_config.yaml"
    write_text(config_path, yaml.safe_dump(config, sort_keys=False))
    command_path = run_root / "train_cmd.sh"
    write_text(command_path, render_train_command(config_path))
    total_optimizer_steps = compute_schedule_steps(
        total_iters=int(config["iters"]),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        microsteps_per_epoch=int(config.get("microsteps_per_epoch", 0) or 0),
        flush_on_epoch_boundary=bool(config.get("flush_on_epoch_boundary", False)),
        schedule_step_unit="optimizer",
    )
    effective_schedule_steps = compute_schedule_steps(
        total_iters=int(config["iters"]),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        microsteps_per_epoch=int(config.get("microsteps_per_epoch", 0) or 0),
        flush_on_epoch_boundary=bool(config.get("flush_on_epoch_boundary", False)),
        schedule_step_unit=str(args.lr_schedule_step_unit),
    )
    final_optimizer_step_microbatches = compute_final_optimizer_step_microbatches(
        total_iters=int(config["iters"]),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        microsteps_per_epoch=int(config.get("microsteps_per_epoch", 0) or 0),
        flush_on_epoch_boundary=bool(config.get("flush_on_epoch_boundary", False)),
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
        "profile": {
            "name": str(getattr(args, "profile", "baseline-original")),
            "resolution": getattr(args, "_profile_resolution", None),
        },
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
            "trainable_lora_suffixes": list(trainable_lora_suffixes),
            "num_layers": int(args.num_layers),
            "steps_per_report": int(args.steps_per_report),
            "steps_per_report_step_unit": str(args.steps_per_report_step_unit),
            "steps_per_eval_requested": int(args.steps_per_eval),
            "steps_per_eval": int(config["steps_per_eval"]),
            "save_every": int(config["save_every"]),
            "flush_on_epoch_boundary": bool(config.get("flush_on_epoch_boundary", False)),
            "microsteps_per_epoch": int(config.get("microsteps_per_epoch", 0) or 0),
            "lr_schedule_name": str(args.lr_schedule_name or ""),
            "lr_schedule_end": float(args.lr_schedule_end),
            "lr_warmup_ratio": float(args.lr_warmup_ratio),
            "lr_schedule_step_unit": str(args.lr_schedule_step_unit),
            "total_iters": int(config["iters"]),
            "optimizer_steps": int(total_optimizer_steps),
            "final_optimizer_step_microbatches": int(final_optimizer_step_microbatches),
            "final_grad_accumulation_flush": True,
            "fail_on_runtime_contention": bool(args.fail_on_runtime_contention),
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
            "notebook_parity_json": (
                notebook_parity_artifacts["json_path"] if notebook_parity_artifacts else ""
            ),
            "notebook_parity_markdown": (
                notebook_parity_artifacts["markdown_path"] if notebook_parity_artifacts else ""
            ),
        },
    }
    if notebook_parity_artifacts is not None:
        manifest["notebook_parity"] = notebook_parity_artifacts
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


def maybe_patch_mlx_lora_tokenizer_special_tokens() -> None:
    import mlx_lm.lora as mlx_lora

    if getattr(mlx_lora, "_nemotron_tokenizer_special_tokens_patch", False):
        return

    original_load = mlx_lora.load

    def patched_load(*args: Any, **kwargs: Any) -> Any:
        result = original_load(*args, **kwargs)
        if isinstance(result, tuple):
            values = list(result)
            if len(values) >= 2:
                normalize_tokenizer_for_hf_parity(values[1])
            return tuple(values)
        return result

    mlx_lora.load = patched_load
    mlx_lora._nemotron_tokenizer_special_tokens_patch = True


def maybe_patch_mlx_lora_train_model_runtime_args() -> None:
    import mlx.core as mx
    import mlx.optimizers as optim
    import mlx_lm.lora as mlx_lora
    from mlx_lm.tuner.datasets import CacheDataset
    from mlx_lm.tuner.trainer import TrainingArgs
    from mlx_lm.tuner.utils import build_schedule, linear_to_lora_layers, print_trainable_parameters

    if getattr(mlx_lora, "_nemotron_train_model_runtime_args_patch", False):
        return

    def patched_train_model(
        args: Any,
        model: Any,
        train_set: Any,
        valid_set: Any,
        training_callback: Any = None,
    ) -> Any:
        report_step_unit = str(getattr(args, "steps_per_report_step_unit", "micro")).strip().lower()
        flush_on_epoch_boundary = bool(getattr(args, "flush_on_epoch_boundary", False))
        microsteps_per_epoch = int(getattr(args, "microsteps_per_epoch", 0) or 0)

        mx.random.seed(args.seed)
        model.freeze()
        if args.num_layers > len(model.layers):
            raise ValueError(
                f"Requested to train {args.num_layers} layers but the model only has {len(model.layers)} layers."
            )

        if args.fine_tune_type == "full":
            for layer in model.layers[-max(args.num_layers, 0) :]:
                layer.unfreeze()
            args.lora_parameters = None
        elif args.fine_tune_type in ["lora", "dora"]:
            linear_to_lora_layers(
                model,
                args.num_layers,
                args.lora_parameters,
                use_dora=(args.fine_tune_type == "dora"),
            )
            trainable_lora_suffixes = coerce_string_list(getattr(args, "trainable_lora_suffixes", None))
            if trainable_lora_suffixes:
                matched_by_suffix: Counter[str] = Counter()
                total_lora_modules = 0
                for name, module in model.named_modules():
                    if not hasattr(module, "lora_a") or not hasattr(module, "lora_b"):
                        continue
                    total_lora_modules += 1
                    module.freeze(keys=["lora_a", "lora_b"])
                    for suffix in trainable_lora_suffixes:
                        if name.endswith(suffix):
                            module.unfreeze(keys=["lora_a", "lora_b"])
                            matched_by_suffix[suffix] += 1
                            break
                unmatched_suffixes = [
                    suffix for suffix in trainable_lora_suffixes if matched_by_suffix.get(suffix, 0) <= 0
                ]
                if unmatched_suffixes:
                    raise ValueError(
                        "trainable_lora_suffixes did not match any LoRA modules: "
                        + ", ".join(unmatched_suffixes)
                    )
                print(
                    "LoRA suffix filter: "
                    + json.dumps(
                        {
                            "total_lora_modules": total_lora_modules,
                            "matched_by_suffix": {
                                key: int(value) for key, value in sorted(matched_by_suffix.items())
                            },
                        },
                        ensure_ascii=False,
                    )
                )
        else:
            raise ValueError(f"Received unknown fine-tune-type {args.fine_tune_type}")

        if args.resume_adapter_file is not None:
            print(f"Loading fine-tuned weights from {args.resume_adapter_file}")
            model.load_weights(args.resume_adapter_file, strict=False)

        print_trainable_parameters(model)

        adapter_path = Path(args.adapter_path)
        adapter_path.mkdir(parents=True, exist_ok=True)
        adapter_file = adapter_path / "adapters.safetensors"
        mlx_lora.save_config(vars(args), adapter_path / "adapter_config.json")

        training_args = TrainingArgs(
            batch_size=args.batch_size,
            iters=args.iters,
            val_batches=args.val_batches,
            steps_per_report=args.steps_per_report,
            steps_per_eval=args.steps_per_eval,
            steps_per_save=args.save_every,
            adapter_file=adapter_file,
            max_seq_length=args.max_seq_length,
            grad_checkpoint=args.grad_checkpoint,
            grad_accumulation_steps=args.grad_accumulation_steps,
        )
        setattr(training_args, "steps_per_report_step_unit", report_step_unit)
        setattr(training_args, "flush_on_epoch_boundary", flush_on_epoch_boundary)
        setattr(training_args, "microsteps_per_epoch", microsteps_per_epoch)

        learning_rate = build_schedule(args.lr_schedule) if args.lr_schedule else args.learning_rate
        optimizer_name = args.optimizer.lower()
        optimizer_config = args.optimizer_config.get(optimizer_name, {})
        if optimizer_name == "adam":
            optimizer_class = optim.Adam
        elif optimizer_name == "adamw":
            optimizer_class = optim.AdamW
        elif optimizer_name == "muon":
            optimizer_class = optim.Muon
        elif optimizer_name == "sgd":
            optimizer_class = optim.SGD
        elif optimizer_name == "adafactor":
            optimizer_class = optim.Adafactor
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer_name}")

        optimizer = optimizer_class(learning_rate=learning_rate, **optimizer_config)
        mlx_lora.train(
            model=model,
            args=training_args,
            optimizer=optimizer,
            train_dataset=CacheDataset(train_set),
            val_dataset=CacheDataset(valid_set),
            training_callback=training_callback,
        )

    mlx_lora.train_model = patched_train_model
    mlx_lora._nemotron_train_model_runtime_args_patch = True


def run_build_corrective_stage2_csv(args: argparse.Namespace) -> None:
    binary_delta_path = Path(args.binary_delta_csv).resolve()
    symbol_train_path = Path(args.symbol_train_csv).resolve()
    symbol_watch_path = Path(args.symbol_watch_csv).resolve()
    proxy_v1_path = Path(args.proxy_v1_csv).resolve()
    output_csv = Path(args.output_csv).resolve()
    summary_json = (
        Path(args.summary_json).resolve()
        if args.summary_json is not None
        else output_csv.with_name(f"{output_csv.stem}_summary.json")
    )

    binary_delta_df = pd.read_csv(binary_delta_path)
    validate_training_frame(binary_delta_df, binary_delta_path)
    require_columns(
        binary_delta_df,
        binary_delta_path,
        ["teacher_solver_candidate", "template_subtype", "source_selection_tier", "assistant_style"],
    )
    symbol_source_df = pd.read_csv(symbol_train_path)
    validate_training_frame(symbol_source_df, symbol_train_path)
    symbol_watch_df = pd.read_csv(symbol_watch_path)
    require_columns(symbol_watch_df, symbol_watch_path, ["id", "template_subtype", "selection_tier"])
    proxy_v1_df = pd.read_csv(proxy_v1_path)
    require_columns(
        proxy_v1_df,
        proxy_v1_path,
        ["id", "family_short", "template_subtype", "selection_tier", "leaderboard_proxy_bucket"],
    )

    binary_solvers = args.binary_solver or list(DEFAULT_STAGE2_BINARY_SOLVERS)
    combined_df, summary = build_corrective_stage2_dataframe(
        binary_delta_df=binary_delta_df,
        symbol_source_df=symbol_source_df,
        symbol_watch_df=symbol_watch_df,
        proxy_v1_df=proxy_v1_df,
        binary_solvers=binary_solvers,
        max_symbol_rows=int(args.max_symbol_rows),
        max_answer_only_ratio=float(args.max_answer_only_ratio),
        seed=int(args.seed),
    )
    ensure_dir(output_csv.parent)
    combined_df.to_csv(output_csv, index=False)
    summary["output_csv"] = str(output_csv)
    summary["summary_json"] = str(summary_json)
    summary["source_paths"] = {
        "binary_delta_csv": str(binary_delta_path),
        "symbol_train_csv": str(symbol_train_path),
        "symbol_watch_csv": str(symbol_watch_path),
        "proxy_v1_csv": str(proxy_v1_path),
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def run_build_leaderboard_proxy_v2(args: argparse.Namespace) -> None:
    proxy_v1_path = Path(args.proxy_v1_csv).resolve()
    binary_hard_path = Path(args.binary_hard_csv).resolve()
    symbol_watch_path = Path(args.symbol_watch_csv).resolve()
    output_csv = Path(args.output_csv).resolve()
    summary_json = (
        Path(args.summary_json).resolve()
        if args.summary_json is not None
        else output_csv.with_name(f"{output_csv.stem}_summary.json")
    )

    proxy_v1_df = pd.read_csv(proxy_v1_path)
    require_columns(
        proxy_v1_df,
        proxy_v1_path,
        [
            "id",
            "prompt",
            "answer",
            "family_short",
            "template_subtype",
            "selection_tier",
            "teacher_solver_candidate",
            "leaderboard_proxy_bucket",
        ],
    )
    binary_hard_df = pd.read_csv(binary_hard_path)
    require_columns(
        binary_hard_df,
        binary_hard_path,
        ["id", "prompt", "answer", "family_short", "template_subtype", "selection_tier", "teacher_solver_candidate"],
    )
    symbol_watch_df = pd.read_csv(symbol_watch_path)
    require_columns(
        symbol_watch_df,
        symbol_watch_path,
        ["id", "prompt", "answer", "family_short", "template_subtype", "selection_tier"],
    )

    focus_buckets = args.focus_bucket or list(DEFAULT_PROXY_V2_FOCUS_BUCKETS)
    binary_solvers = args.binary_solver or list(DEFAULT_STAGE2_BINARY_SOLVERS)
    combined_df, summary = build_leaderboard_proxy_v2_dataframe(
        proxy_v1_df=proxy_v1_df,
        binary_hard_df=binary_hard_df,
        symbol_watch_df=symbol_watch_df,
        focus_buckets=focus_buckets,
        binary_solvers=binary_solvers,
        max_binary_hard_rows=int(args.max_binary_hard_rows),
        max_symbol_rows=int(args.max_symbol_rows),
        seed=int(args.seed),
    )
    ensure_dir(output_csv.parent)
    combined_df.to_csv(output_csv, index=False)
    summary["output_csv"] = str(output_csv)
    summary["summary_json"] = str(summary_json)
    summary["source_paths"] = {
        "proxy_v1_csv": str(proxy_v1_path),
        "binary_hard_csv": str(binary_hard_path),
        "symbol_watch_csv": str(symbol_watch_path),
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def run_mlx_lora_training_from_config(config_path: Path) -> None:
    import mlx_lm.lora as mlx_lora

    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    maybe_patch_mlx_chat_dataset_enable_thinking()
    maybe_patch_mlx_trainer_final_accumulation_flush()
    maybe_patch_mlx_lora_tokenizer_special_tokens()
    maybe_patch_mlx_lora_train_model_runtime_args()
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
    runtime_preflight = collect_runtime_preflight(current_pid=os.getpid())
    write_json(run_root / "runtime_preflight.json", runtime_preflight)
    print_runtime_preflight(runtime_preflight)
    competing = [
        row
        for row in runtime_preflight.get("competing_mlx_train_processes", [])
        if isinstance(row, dict) and "pid" in row
    ]
    if args.fail_on_runtime_contention and competing:
        raise RuntimeError(
            "Runtime preflight detected competing MLX/Nemotron train processes. "
            f"Refusing to start {args.run_name} while {len(competing)} other train process(es) are active."
        )
    run_mlx_lora_training_from_config(config_path)
    verify_training_outputs(adapter_dir)
    bundle_manifest = bundle_local_mlx_adapter(run_root, adapter_dir)
    training_result = {
        "created_at": utc_now(),
        "run_root": str(run_root),
        "adapter_dir": str(adapter_dir),
        "adapter_files": summarize_directory(adapter_dir),
        "runtime_preflight_path": str((run_root / "runtime_preflight.json").resolve()),
        "mlx_bundle": bundle_manifest,
    }
    write_json(run_root / "training_result.json", training_result)
    print(json.dumps(training_result, ensure_ascii=False, indent=2))


def run_train_mlx_config(args: argparse.Namespace) -> None:
    run_mlx_lora_training_from_config(Path(args.config).resolve())


def run_audit_notebook_profile(args: argparse.Namespace) -> None:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    train_csv = Path(args.train_csv).resolve()
    df = pd.read_csv(train_csv)
    validate_training_frame(df, train_csv)
    type_samples = resolve_type_samples(args)
    sampled_train_df = sample_training_df(
        df,
        type_samples=type_samples,
        seed=int(args.seed),
    )
    train_records, record_summary = build_chat_records(sampled_train_df)
    lora_keys = resolve_lora_keys(args.lora_key or [], args.lora_key_group or [])
    notebook_parity_artifacts = write_notebook_parity_artifacts(
        run_root=run_root,
        args=args,
        train_csv=train_csv,
        type_samples=type_samples,
        lora_keys=lora_keys,
    )
    profile_spec = get_notebook_profile_spec(str(getattr(args, "profile", "")))
    if profile_spec is None:
        raise ValueError(f"Audit requires a notebook profile, got {getattr(args, 'profile', '')!r}")
    audit_summary = {
        "created_at": utc_now(),
        "run_root": str(run_root),
        "profile": {
            "name": str(getattr(args, "profile", "")),
            "resolution": getattr(args, "_profile_resolution", None),
        },
        "train_csv": str(train_csv),
        "sampled_rows": int(len(sampled_train_df)),
        "record_summary": record_summary,
        "lora_keys": list(lora_keys),
        "notebook_parity": notebook_parity_artifacts,
    }
    write_json(run_root / str(profile_spec["audit_summary_name"]), audit_summary)
    print(json.dumps(audit_summary, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce baseline/nemotron-sft-lora-with-cot-v2 with MLX LoRA using the README.md "
            "submission/evaluation contract as the source of truth."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_shared_train_args(target: argparse.ArgumentParser) -> None:
        target.add_argument(
            "--profile",
            choices=TRAINING_PROFILES,
            default="baseline-original",
            help=(
                "Keep legacy baseline-original defaults, or apply notebook-original / "
                "notebook-current defaults from the tracked baseline notebooks before "
                "explicit CLI overrides."
            ),
        )
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
            help=(
                "Mask prompt tokens from the loss. Legacy baseline-original keeps this on; "
                "use notebook-original/current profiles or --no-mask-prompt for HF notebook parity."
            ),
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
            "--lora-key-group",
            action="append",
            choices=sorted(LORA_KEY_GROUPS),
            default=[],
            help="Add a predefined Nemotron LoRA key group such as broad, attention, or stage-union.",
        )
        target.add_argument(
            "--lora-key",
            action="append",
            default=[],
            help="Override LoRA target keys. Repeat the flag to provide multiple keys.",
        )
        target.add_argument(
            "--trainable-lora-suffix-group",
            action="append",
            choices=sorted(LORA_KEY_GROUPS),
            default=[],
            help="Freeze all LoRA adapter params, then unfreeze only modules in this predefined suffix group.",
        )
        target.add_argument(
            "--trainable-lora-suffix",
            action="append",
            default=[],
            help="Freeze all LoRA adapter params, then unfreeze only modules whose names end with these suffixes.",
        )
        target.add_argument(
            "--num-layers",
            type=int,
            default=-1,
            help="Use -1 to LoRA-wrap all layers, matching the baseline notebook intent.",
        )
        target.add_argument("--steps-per-report", type=int, default=10)
        target.add_argument(
            "--steps-per-report-step-unit",
            choices=REPORT_STEP_UNITS,
            default="micro",
            help="Interpret steps_per_report in optimizer updates (HF logging semantics) or raw microsteps.",
        )
        target.add_argument("--steps-per-eval", type=int, default=200)
        target.add_argument(
            "--save-every",
            type=int,
            default=0,
            help="Save intermediate adapter checkpoints every N microsteps; 0 keeps final-only behavior.",
        )
        target.add_argument(
            "--flush-on-epoch-boundary",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="Flush grad accumulation at each epoch boundary before continuing the next epoch.",
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
        target.add_argument(
            "--fail-on-runtime-contention",
            action="store_true",
            help="Abort if other MLX/Nemotron train processes are already active on this machine.",
        )

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

    audit_notebook_original = subparsers.add_parser(
        "audit-notebook-original",
        help="Audit original notebook parity without launching MLX training.",
    )
    add_shared_train_args(audit_notebook_original)
    audit_notebook_original.set_defaults(
        func=run_audit_notebook_profile,
        profile="notebook-original",
    )

    audit_notebook_current = subparsers.add_parser(
        "audit-notebook-current",
        help="Audit notebook-current parity without launching MLX training.",
    )
    add_shared_train_args(audit_notebook_current)
    audit_notebook_current.set_defaults(
        func=run_audit_notebook_profile,
        profile="notebook-current",
    )

    build_corrective_stage2_csv = subparsers.add_parser(
        "build-corrective-stage2-csv",
        help="Build a narrow Stage 2 corrective training CSV from route-aware binary delta and verified numeric_2x2 symbol rows.",
    )
    build_corrective_stage2_csv.add_argument("--binary-delta-csv", type=Path, default=BINARY_ROUTE_AWARE_DELTA_CSV)
    build_corrective_stage2_csv.add_argument("--symbol-train-csv", type=Path, default=NOTEBOOK_CURRENT_TRAIN_CSV)
    build_corrective_stage2_csv.add_argument("--symbol-watch-csv", type=Path, default=SYMBOL_WATCH_SET_CSV)
    build_corrective_stage2_csv.add_argument("--proxy-v1-csv", type=Path, default=LEADERBOARD_PROXY_V1_SET_CSV)
    build_corrective_stage2_csv.add_argument("--binary-solver", action="append", default=[])
    build_corrective_stage2_csv.add_argument("--max-symbol-rows", type=int, default=24)
    build_corrective_stage2_csv.add_argument("--max-answer-only-ratio", type=float, default=0.0)
    build_corrective_stage2_csv.add_argument("--seed", type=int, default=DEFAULT_SEED)
    build_corrective_stage2_csv.add_argument("--output-csv", type=Path, required=True)
    build_corrective_stage2_csv.add_argument("--summary-json", type=Path, default=None)
    build_corrective_stage2_csv.set_defaults(func=run_build_corrective_stage2_csv)

    build_leaderboard_proxy_v2 = subparsers.add_parser(
        "build-leaderboard-proxy-v2",
        help="Build a hidden-gap watch set focused on safe/bijection/structured-formula regression slices.",
    )
    build_leaderboard_proxy_v2.add_argument("--proxy-v1-csv", type=Path, default=LEADERBOARD_PROXY_V1_SET_CSV)
    build_leaderboard_proxy_v2.add_argument("--binary-hard-csv", type=Path, default=BINARY_HARD_SET_CSV)
    build_leaderboard_proxy_v2.add_argument("--symbol-watch-csv", type=Path, default=SYMBOL_WATCH_SET_CSV)
    build_leaderboard_proxy_v2.add_argument("--focus-bucket", action="append", default=[])
    build_leaderboard_proxy_v2.add_argument("--binary-solver", action="append", default=[])
    build_leaderboard_proxy_v2.add_argument("--max-binary-hard-rows", type=int, default=24)
    build_leaderboard_proxy_v2.add_argument("--max-symbol-rows", type=int, default=12)
    build_leaderboard_proxy_v2.add_argument("--seed", type=int, default=DEFAULT_SEED)
    build_leaderboard_proxy_v2.add_argument("--output-csv", type=Path, required=True)
    build_leaderboard_proxy_v2.add_argument("--summary-json", type=Path, default=None)
    build_leaderboard_proxy_v2.set_defaults(func=run_build_leaderboard_proxy_v2)

    eval_benchmark_csv = subparsers.add_parser(
        "eval-benchmark-csv",
        help="Run deterministic README-style MLX evaluation against a benchmark CSV with prompt/answer rows.",
    )
    eval_benchmark_csv.add_argument("--model-root", type=Path, required=True)
    eval_benchmark_csv.add_argument("--adapter-dir", type=Path, default=None)
    eval_benchmark_csv.add_argument("--benchmark-csv", type=Path, required=True)
    eval_benchmark_csv.add_argument("--output-root", type=Path, required=True)
    eval_benchmark_csv.add_argument("--max-tokens", type=int, default=README_MAX_TOKENS)
    eval_benchmark_csv.add_argument("--temperature", type=float, default=README_TEMPERATURE)
    eval_benchmark_csv.add_argument("--top-p", type=float, default=README_TOP_P)
    eval_benchmark_csv.add_argument("--max-num-seqs", type=int, default=README_MAX_NUM_SEQS)
    eval_benchmark_csv.add_argument("--max-model-len", type=int, default=README_MAX_MODEL_LEN)
    eval_benchmark_csv.add_argument("--prompt-chunk-size", type=int, default=16)
    eval_benchmark_csv.add_argument("--prefill-batch-size", type=int, default=16)
    eval_benchmark_csv.add_argument("--completion-batch-size", type=int, default=16)
    eval_benchmark_csv.add_argument(
        "--eval-enable-thinking",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    eval_benchmark_csv.add_argument(
        "--lazy-load",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    eval_benchmark_csv.add_argument("--force-single-generate", action="store_true")
    eval_benchmark_csv.set_defaults(func=run_eval_benchmark_csv)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    args = parser.parse_args(raw_argv)
    profile_resolution = apply_training_profile(args, raw_argv=raw_argv)
    if profile_resolution is not None:
        args._profile_resolution = profile_resolution
    args.func(args)


if __name__ == "__main__":
    main()
