#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.metadata as importlib_metadata
import json
import sys
import types
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from safetensors.numpy import load_file, save_file


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ADAPTER_DIR = (
    REPO_ROOT
    / "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2/mlx_adapter_bundle"
)
DEFAULT_REFERENCE_MODEL_ROOT = (
    REPO_ROOT
    / "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2/shadow_model"
)
DEFAULT_OUTPUT_ROOT = (
    REPO_ROOT
    / "mlx_to_peft_exporter/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2_peft_export"
)
DEFAULT_BASE_MODEL_NAME_OR_PATH = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
README_PATH = REPO_ROOT / "README.md"
README_REQUIRED_FILES = ("adapter_config.json", "adapter_model.safetensors")
README_MAX_LORA_RANK = 32
README_SUBMISSION_ARCHIVE_NAME = "submission.zip"
TARGET_MODULE_ORDER = ("q_proj", "k_proj", "v_proj", "o_proj", "in_proj", "out_proj", "up_proj", "down_proj")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_readme_submission_contract_from_readme() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()
    if "adapter_config.json" not in text:
        raise SystemExit(
            "README.md submitting contract no longer states that the LoRA adapter must include adapter_config.json."
        )
    if README_SUBMISSION_ARCHIVE_NAME.lower() not in lower_text:
        raise SystemExit(
            f"README.md submitting contract no longer states that the submission archive is {README_SUBMISSION_ARCHIVE_NAME}."
        )
    if "submit a lora adapter" not in lower_text:
        raise SystemExit("README.md submitting contract no longer states that the submission is a single LoRA adapter.")
    max_lora_rank: int | None = None
    for line in text.splitlines():
        if not line.startswith("max_lora_rank\t"):
            continue
        raw_value = line.split("\t", 1)[1].strip()
        if raw_value == "":
            raise SystemExit("Malformed README.md evaluation row for max_lora_rank: missing value")
        try:
            max_lora_rank = int(raw_value)
        except ValueError as exc:
            raise SystemExit(f"Malformed README.md evaluation value for max_lora_rank: {raw_value!r}") from exc
        break
    if max_lora_rank is None:
        raise SystemExit("Missing README.md evaluation rows: max_lora_rank")
    return {
        "required_files": list(README_REQUIRED_FILES),
        "max_lora_rank": max_lora_rank,
        "single_adapter_submission_zip": True,
        "submission_archive_name": README_SUBMISSION_ARCHIVE_NAME,
    }


def verify_readme_submission_contract_file() -> dict[str, Any]:
    contract = load_readme_submission_contract_from_readme()
    if int(contract["max_lora_rank"]) != README_MAX_LORA_RANK:
        raise SystemExit(
            f"README.md submission contract mismatch for max_lora_rank: expected {README_MAX_LORA_RANK}, got {contract['max_lora_rank']}"
        )
    if str(contract["submission_archive_name"]) != README_SUBMISSION_ARCHIVE_NAME:
        raise SystemExit(
            "README.md submission contract mismatch for submission_archive_name: "
            f"expected {README_SUBMISSION_ARCHIVE_NAME}, got {contract['submission_archive_name']}"
        )
    if bool(contract["single_adapter_submission_zip"]) is not True:
        raise SystemExit("README.md submission contract mismatch for single_adapter_submission_zip: expected true.")
    return contract


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


def extract_lora_hparams(adapter_config: dict[str, Any]) -> tuple[int, float, float, list[str]]:
    lora_parameters = adapter_config.get("lora_parameters")
    if not isinstance(lora_parameters, dict):
        raise ValueError("adapter_config.json does not contain a valid lora_parameters object.")
    try:
        rank = int(lora_parameters["rank"])
    except Exception as exc:
        raise ValueError(f"Invalid lora rank in adapter_config.json: {lora_parameters.get('rank')}") from exc
    try:
        alpha = float(lora_parameters.get("scale", rank))
    except Exception as exc:
        raise ValueError(f"Invalid lora scale in adapter_config.json: {lora_parameters.get('scale')}") from exc
    try:
        dropout = float(lora_parameters.get("dropout", 0.0))
    except Exception as exc:
        raise ValueError(f"Invalid lora dropout in adapter_config.json: {lora_parameters.get('dropout')}") from exc
    raw_keys = lora_parameters.get("keys", [])
    if not isinstance(raw_keys, list) or not all(isinstance(item, str) for item in raw_keys):
        raise ValueError("adapter_config.json lora_parameters.keys must be a list of strings.")
    return rank, alpha, dropout, raw_keys


def build_target_modules_regex(mlx_keys: list[str]) -> str:
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
    if not terminals:
        raise ValueError("Could not derive PEFT target_modules regex from MLX adapter keys.")
    return ".*\\.(" + "|".join(terminals) + ")$"


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


def classify_source_tensor(key: str) -> str:
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


def map_mlx_tensor_to_peft_entries(key: str, value: np.ndarray) -> list[tuple[str, np.ndarray]]:
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


def convert_mlx_adapter_to_peft_tensors(
    tensors: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]], dict[str, Any]]:
    converted: dict[str, np.ndarray] = {}
    conversion_preview: list[dict[str, Any]] = []
    source_rank_counts: dict[int, int] = {}
    source_family_counts: dict[str, int] = {}
    for source_key, value in sorted(tensors.items()):
        source_rank_counts[value.ndim] = source_rank_counts.get(value.ndim, 0) + 1
        family = classify_source_tensor(source_key)
        source_family_counts[family] = source_family_counts.get(family, 0) + 1
        mapped_entries = map_mlx_tensor_to_peft_entries(source_key, value)
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


def validate_converted_tensors(
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


def resolve_reference_model_root(args: argparse.Namespace, adapter_config: dict[str, Any]) -> Path:
    if args.reference_model_root is not None:
        return Path(args.reference_model_root).resolve()
    configured_model_root = adapter_config.get("model")
    if isinstance(configured_model_root, str) and configured_model_root.strip():
        return Path(configured_model_root).resolve()
    return DEFAULT_REFERENCE_MODEL_ROOT.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a Nemotron MLX adapter bundle (adapter_config.json + adapters.safetensors) "
            "into a PEFT/vLLM-compatible submission.zip."
        )
    )
    parser.add_argument(
        "--source-adapter-dir",
        type=Path,
        default=DEFAULT_SOURCE_ADAPTER_DIR,
        help="Directory containing adapter_config.json and adapters.safetensors.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where submission_adapter/, submission.zip, and export_manifest.json are written.",
    )
    parser.add_argument(
        "--reference-model-root",
        type=Path,
        default=None,
        help="Optional local Nemotron base model root used only for meta-device PEFT shape validation.",
    )
    parser.add_argument(
        "--base-model-name-or-path",
        default=DEFAULT_BASE_MODEL_NAME_OR_PATH,
        help="base_model_name_or_path to write into the PEFT adapter_config.json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    readme_submission_contract = verify_readme_submission_contract_file()
    source_adapter_dir = Path(args.source_adapter_dir).resolve()
    output_root = ensure_dir(Path(args.output_root).resolve())
    submission_dir = ensure_dir(output_root / "submission_adapter")

    adapter_config_path = source_adapter_dir / "adapter_config.json"
    adapter_weights_path = source_adapter_dir / "adapters.safetensors"
    if not adapter_config_path.exists():
        raise FileNotFoundError(f"Missing adapter_config.json: {adapter_config_path}")
    if not adapter_weights_path.exists():
        raise FileNotFoundError(f"Missing adapters.safetensors: {adapter_weights_path}")

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
    target_modules = build_target_modules_regex(list(source_tensors.keys()))

    reference_model_root = resolve_reference_model_root(args, adapter_config)
    if not reference_model_root.exists():
        raise FileNotFoundError(f"Reference model root does not exist: {reference_model_root}")

    converted_tensors, conversion_preview, source_summary = convert_mlx_adapter_to_peft_tensors(source_tensors)
    reference_shapes = build_reference_peft_shapes(
        reference_model_root=reference_model_root,
        target_modules=target_modules,
        rank=rank,
        alpha=alpha,
        dropout=dropout,
    )
    validation = validate_converted_tensors(converted_tensors, reference_shapes)
    if not validation["valid"]:
        raise ValueError(
            "Converted PEFT tensors do not match the Nemotron meta reference: "
            f"missing={validation['missing_key_count']} "
            f"unexpected={validation['unexpected_key_count']} "
            f"shape_mismatches={validation['shape_mismatch_count']}"
        )

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

    submission_zip_path = output_root / "submission.zip"
    with zipfile.ZipFile(submission_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(output_adapter_config_path, "adapter_config.json")
        archive.write(output_adapter_model_path, "adapter_model.safetensors")

    manifest = {
        "created_at": utc_now(),
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
    }
    write_json(output_root / "export_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
