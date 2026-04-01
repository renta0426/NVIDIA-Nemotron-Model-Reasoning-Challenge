from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata as importlib_metadata
import json
import math
import random
import shutil
import subprocess
import sys
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


def select_shadow_validation_records(
    records: Sequence[dict[str, Any]],
    *,
    valid_rows: int,
    seed: int,
) -> list[dict[str, Any]]:
    if not records:
        raise ValueError("Training records are empty")
    valid_rows = max(1, min(valid_rows, len(records)))
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
        "mask_prompt": True,
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
            f'"{sys.executable}" -m mlx_lm lora --config "{config_path}"',
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
    train_records = build_phase2_chat_records(source_rows)
    valid_records = select_shadow_validation_records(
        train_records,
        valid_rows=int(args.valid_shadow_rows),
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
        "dataset": {
            "dataset_dir": str(dataset_dir),
            "train_rows": len(train_records),
            "valid_rows": len(valid_records),
            "valid_strategy": f"shadow_sample={int(args.valid_shadow_rows)}",
        },
        "training": {
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


def run_prepare_train(args: argparse.Namespace) -> None:
    manifest = prepare_training_run(args)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def run_train(args: argparse.Namespace) -> None:
    manifest = prepare_training_run(args)
    run_root = Path(manifest["run_root"])
    adapter_dir = Path(manifest["artifacts"]["adapter_dir"])
    config_path = Path(manifest["artifacts"]["config_path"])
    command = [sys.executable, "-m", "mlx_lm", "lora", "--config", str(config_path)]
    print("Running MLX LoRA training:")
    print(" ".join(command))
    subprocess.run(command, cwd=str(REPO_ROOT), check=True)
    verify_training_outputs(adapter_dir)
    training_result = {
        "created_at": utc_now(),
        "run_root": str(run_root),
        "adapter_dir": str(adapter_dir),
        "adapter_files": summarize_directory(adapter_dir),
    }
    write_json(run_root / "training_result.json", training_result)
    print(json.dumps(training_result, ensure_ascii=False, indent=2))


def run_phase0_eval(args: argparse.Namespace) -> None:
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler

    adapter_dir = Path(args.adapter_path).resolve()
    if not adapter_dir.exists():
        raise FileNotFoundError(f"Adapter directory does not exist: {adapter_dir}")
    verify_training_outputs(adapter_dir)

    run_root = adapter_dir.parent
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

    model, tokenizer = load(str(shadow_model_dir), adapter_path=str(adapter_dir), lazy=bool(args.lazy_load))
    sampler = make_sampler(
        temp=float(args.temperature),
        top_p=float(args.top_p) if 0.0 < float(args.top_p) < 1.0 else 0.0,
    )

    prompts = build_prompts(tokenizer, [str(row["prompt"]) for row in benchmark_rows])
    records: list[dict[str, Any]] = []
    for index, (row, rendered_prompt) in enumerate(zip(benchmark_rows, prompts), start=1):
        raw_output = generate(
            model,
            tokenizer,
            prompt=rendered_prompt,
            verbose=False,
            max_tokens=int(args.max_tokens),
            sampler=sampler,
        )
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
        if int(args.progress_every) > 0 and (
            index == 1
            or index % int(args.progress_every) == 0
            or index == len(benchmark_rows)
        ):
            print(f"[phase0-eval] completed {index}/{len(benchmark_rows)} rows")

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
        render_markdown_summary("phase0_eval_overall", overall_summary),
    )
    if binary_holdout_accuracy:
        write_csv_rows(
            artifact_root / "phase0_binary_holdout_accuracy.csv",
            binary_holdout_accuracy,
            ["holdout_kind", "fold", "rows", "correct", "accuracy"],
        )
    for benchmark_name, payload in by_benchmark_summary.items():
        write_json(artifact_root / f"{benchmark_name}_summary.json", payload)
        write_text(report_root / f"{benchmark_name}_summary.md", render_markdown_summary(benchmark_name, payload))

    print(json.dumps(summary_payload["overall"], ensure_ascii=False, indent=2))


def add_common_train_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--train-csv", type=Path, default=DEFAULT_TRAIN_CSV)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-name", type=str, default=DEFAULT_RUN_NAME)
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

    phase0_eval = subparsers.add_parser("eval-phase0", help="Run phase0-style offline evaluation with MLX generation.")
    phase0_eval.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    phase0_eval.add_argument("--adapter-path", type=Path, required=True)
    phase0_eval.add_argument("--phase0-prebuilt-root", type=Path, default=DEFAULT_PHASE0_PREBUILT_ROOT)
    phase0_eval.add_argument("--phase0-analysis-csv", type=Path, default=DEFAULT_PHASE0_ANALYSIS_CSV)
    phase0_eval.add_argument("--rebuild-phase0", action="store_true")
    phase0_eval.add_argument("--max-samples", type=int, default=None)
    phase0_eval.add_argument("--max-tokens", type=int, default=README_MAX_TOKENS)
    phase0_eval.add_argument("--temperature", type=float, default=README_TEMPERATURE)
    phase0_eval.add_argument("--top-p", type=float, default=README_TOP_P)
    phase0_eval.add_argument("--progress-every", type=int, default=10)
    phase0_eval.add_argument("--lazy-load", action="store_true")
    phase0_eval.add_argument("--force-shadow-model", action="store_true")
    phase0_eval.set_defaults(func=run_phase0_eval)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
