from __future__ import annotations

import argparse
import gc
import importlib.machinery
import importlib.util
import json
import math
import random
import sys
import time
import types
import zipfile
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence

import pandas as pd
import torch
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, get_cosine_schedule_with_warmup, set_seed


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OFFICIAL_MODEL_REPO = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
DEFAULT_LOCAL_MODEL_DIR = REPO_ROOT / "models" / "nemotron-3-nano-30b-a3b-bf16"
DEFAULT_MODEL_SPEC = str(DEFAULT_LOCAL_MODEL_DIR) if DEFAULT_LOCAL_MODEL_DIR.exists() else DEFAULT_OFFICIAL_MODEL_REPO
DEFAULT_TRAIN_CSV = REPO_ROOT / "baseline" / "cot" / "phase2_binary_dsl" / "artifacts" / "phase2_binary_hybrid_training_data.csv"
PHASE0_BUILD_SCRIPT = REPO_ROOT / "baseline" / "cot" / "phase0_offline_eval" / "build_phase0_offline_eval.py"
DEFAULT_PHASE0_ANALYSIS_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
DEFAULT_PHASE0_PREBUILT_ROOT = REPO_ROOT / "baseline" / "cot" / "phase0_offline_eval" / "artifacts"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "mac_workspace" / "v0" / "outputs"
DEFAULT_LOG_PATH = REPO_ROOT / "mac_workspace" / "v0" / "experiment_log.jsonl"
BOXED_INSTRUCTION = "Please put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`"
EXPECTED_PHASE2_COLUMNS = [
    "id",
    "prompt",
    "answer",
    "generated_cot",
    "label",
    "assistant_style",
    "source_selection_tier",
]
README_MAX_LORA_RANK = 32
README_MAX_TOKENS = 7680
README_TOP_P = 1.0
README_TEMPERATURE = 0.0
README_MAX_NUM_SEQS = 64
README_MAX_MODEL_LEN = 8192
_NON_CUDA_STREAM_PATCHED = False
_MAMBA_RMSNORM_FALLBACK_PATCHED = False


@dataclass(frozen=True)
class DevicePlan:
    name: str
    torch_dtype: torch.dtype


class TokenizedPhase2Dataset(Dataset):
    def __init__(self, items: list[dict[str, list[int]]]) -> None:
        self.items = items

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, list[int]]:
        return self.items[index]


class AssistantOnlyDataCollator:
    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = pad_token_id

    def __call__(self, features: Sequence[dict[str, list[int]]]) -> dict[str, torch.Tensor]:
        max_len = max(len(feature["input_ids"]) for feature in features)
        input_ids_batch: list[list[int]] = []
        attention_batch: list[list[int]] = []
        labels_batch: list[list[int]] = []
        for feature in features:
            pad = max_len - len(feature["input_ids"])
            input_ids_batch.append(feature["input_ids"] + [self.pad_token_id] * pad)
            attention_batch.append(feature["attention_mask"] + [0] * pad)
            labels_batch.append(feature["labels"] + [-100] * pad)
        return {
            "input_ids": torch.tensor(input_ids_batch, dtype=torch.long),
            "attention_mask": torch.tensor(attention_batch, dtype=torch.long),
            "labels": torch.tensor(labels_batch, dtype=torch.long),
        }


class _NullCudaStream:
    pass


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_model_spec(model_spec: str, *, log_path: Path) -> str:
    lowered = model_spec.lower()
    if "mlx" in lowered:
        payload = {
            "event": "model_rejected",
            "reason": "MLX models are prohibited in this repository. Use the official Transformers repo or a local HF snapshot.",
            "model_spec": model_spec,
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        append_jsonl(log_path, payload)
        raise ValueError(payload["reason"])
    path = Path(model_spec)
    if path.exists():
        return str(path.resolve())
    return model_spec


def choose_device(requested: str) -> DevicePlan:
    if requested == "auto":
        if torch.cuda.is_available():
            dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            return DevicePlan("cuda", dtype)
        if torch.backends.mps.is_available():
            return DevicePlan("mps", torch.float16)
        return DevicePlan("cpu", torch.float32)

    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available.")
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        return DevicePlan("cuda", dtype)
    if requested == "mps":
        if not torch.backends.mps.is_available():
            raise RuntimeError("MPS is not available.")
        return DevicePlan("mps", torch.float16)
    if requested == "cpu":
        return DevicePlan("cpu", torch.float32)
    raise ValueError(f"Unsupported device: {requested}")


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    set_seed(seed)


def maybe_empty_cache(device_name: str) -> None:
    if device_name == "cuda":
        torch.cuda.empty_cache()
    elif device_name == "mps":
        torch.mps.empty_cache()


def _device_type(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, torch.device):
        return value.type
    text = str(value)
    if text.startswith("cuda"):
        return "cuda"
    if text.startswith("mps"):
        return "mps"
    if text.startswith("cpu"):
        return "cpu"
    return text


def install_non_cuda_stream_fallback() -> None:
    global _NON_CUDA_STREAM_PATCHED
    if _NON_CUDA_STREAM_PATCHED:
        return

    original_default_stream = torch.cuda.default_stream
    original_stream = torch.cuda.stream

    def safe_default_stream(device: Any = None) -> Any:
        if _device_type(device) not in {None, "cuda"}:
            return _NullCudaStream()
        return original_default_stream(device)

    def safe_stream(stream: Any) -> Any:
        if isinstance(stream, _NullCudaStream):
            return nullcontext()
        return original_stream(stream)

    torch.cuda.default_stream = safe_default_stream
    torch.cuda.stream = safe_stream
    _NON_CUDA_STREAM_PATCHED = True


def fallback_mamba_rmsnorm_fn(
    *,
    x: torch.Tensor,
    weight: torch.Tensor,
    bias: torch.Tensor | None = None,
    z: torch.Tensor | None = None,
    eps: float = 1e-6,
    group_size: int | None = None,
    norm_before_gate: bool = False,
    **_: Any,
) -> torch.Tensor:
    if bias is not None:
        raise NotImplementedError("fallback_mamba_rmsnorm_fn does not support bias")

    input_dtype = x.dtype
    hidden_states = x.to(torch.float32)
    gate = z.to(torch.float32) if isinstance(z, torch.Tensor) else None
    if gate is not None and not norm_before_gate:
        hidden_states = hidden_states * torch.nn.functional.silu(gate)

    hidden_size = hidden_states.shape[-1]
    if group_size is not None and group_size > 0 and hidden_size % group_size == 0:
        grouped = hidden_states.reshape(*hidden_states.shape[:-1], hidden_size // group_size, group_size)
        variance = grouped.pow(2).mean(dim=-1, keepdim=True)
        hidden_states = (grouped * torch.rsqrt(variance + eps)).reshape_as(hidden_states)
    else:
        variance = hidden_states.pow(2).mean(dim=-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + eps)

    hidden_states = hidden_states * weight.to(device=hidden_states.device, dtype=torch.float32)
    if gate is not None and norm_before_gate:
        hidden_states = hidden_states * torch.nn.functional.silu(gate)
    return hidden_states.to(input_dtype)


def install_mamba_rmsnorm_fallback() -> None:
    global _MAMBA_RMSNORM_FALLBACK_PATCHED
    if _MAMBA_RMSNORM_FALLBACK_PATCHED:
        return
    if "mamba_ssm.ops.triton.layernorm_gated" in sys.modules:
        _MAMBA_RMSNORM_FALLBACK_PATCHED = True
        return

    mamba_ssm_module = sys.modules.setdefault("mamba_ssm", types.ModuleType("mamba_ssm"))
    ops_module = sys.modules.setdefault("mamba_ssm.ops", types.ModuleType("mamba_ssm.ops"))
    triton_module = sys.modules.setdefault("mamba_ssm.ops.triton", types.ModuleType("mamba_ssm.ops.triton"))
    layernorm_module = types.ModuleType("mamba_ssm.ops.triton.layernorm_gated")
    layernorm_module.rmsnorm_fn = fallback_mamba_rmsnorm_fn
    mamba_ssm_module.__spec__ = importlib.machinery.ModuleSpec("mamba_ssm", loader=None, is_package=True)
    ops_module.__spec__ = importlib.machinery.ModuleSpec("mamba_ssm.ops", loader=None, is_package=True)
    triton_module.__spec__ = importlib.machinery.ModuleSpec("mamba_ssm.ops.triton", loader=None, is_package=True)
    layernorm_module.__spec__ = importlib.machinery.ModuleSpec(
        "mamba_ssm.ops.triton.layernorm_gated",
        loader=None,
        is_package=False,
    )

    mamba_ssm_module.ops = ops_module
    ops_module.triton = triton_module
    triton_module.layernorm_gated = layernorm_module
    sys.modules["mamba_ssm.ops.triton.layernorm_gated"] = layernorm_module
    _MAMBA_RMSNORM_FALLBACK_PATCHED = True


def install_nemotron_non_cuda_fallbacks(device_name: str) -> None:
    if device_name == "cuda":
        return
    install_non_cuda_stream_fallback()
    install_mamba_rmsnorm_fallback()


def device_map_for(device_name: str) -> dict[str, Any] | None:
    if device_name == "cuda":
        return {"": 0}
    if device_name == "mps":
        return {"": "mps"}
    return None


def load_tokenizer(model_spec: str, *, revision: str | None, local_files_only: bool) -> Any:
    tokenizer = AutoTokenizer.from_pretrained(
        model_spec,
        trust_remote_code=True,
        revision=revision,
        local_files_only=local_files_only,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def patch_nemotron_fast_path() -> list[str]:
    patched: list[str] = []
    for module_name, module in list(sys.modules.items()):
        if "modeling_nemotron_h" not in module_name:
            continue
        if hasattr(module, "is_fast_path_available"):
            module.is_fast_path_available = False
            patched.append(module_name)
    return patched


def load_model(
    model_spec: str,
    *,
    revision: str | None,
    local_files_only: bool,
    device_plan: DevicePlan,
    training: bool,
) -> Any:
    install_nemotron_non_cuda_fallbacks(device_plan.name)
    model_kwargs: dict[str, Any] = {
        "trust_remote_code": True,
        "revision": revision,
        "local_files_only": local_files_only,
        "low_cpu_mem_usage": True,
    }
    if device_plan.name != "cpu":
        model_kwargs["dtype"] = device_plan.torch_dtype
    if device_plan.name == "mps":
        model_kwargs["attn_implementation"] = "eager"
    mapped = device_map_for(device_plan.name)
    if mapped is not None:
        model_kwargs["device_map"] = mapped

    model = AutoModelForCausalLM.from_pretrained(model_spec, **model_kwargs)
    if device_plan.name == "cpu":
        model.to("cpu")
    patched = patch_nemotron_fast_path()
    if patched:
        print(f"Patched Nemotron fast path modules: {patched}")
    if training:
        model.config.use_cache = False
        model.gradient_checkpointing_enable()
    else:
        model.config.use_cache = True
        model.eval()
    return model


def apply_chat_template_safe(
    tokenizer: Any,
    messages: list[dict[str, str]],
    *,
    add_generation_prompt: bool,
    enable_thinking: bool,
) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=enable_thinking,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
        )
    except Exception:
        rendered = []
        for message in messages:
            rendered.append(f"<|{message['role']}|>\n{message['content']}")
        if add_generation_prompt:
            rendered.append("<|assistant|>\n<think>")
        return "\n".join(rendered)


def build_user_message(prompt: str) -> str:
    return prompt + "\n" + BOXED_INSTRUCTION


def render_assistant_message(example: dict[str, str]) -> str:
    assistant_style = str(example["assistant_style"])
    if assistant_style == "trace_boxed":
        return f"{example['generated_cot']}\n\n\\boxed{{{example['answer']}}}"
    if assistant_style == "boxed_only":
        return f"\\boxed{{{example['answer']}}}"
    raise ValueError(f"Unsupported assistant_style: {assistant_style}")


def tokenize_training_row(tokenizer: Any, example: dict[str, str], *, max_seq_len: int) -> dict[str, list[int]]:
    user_message = build_user_message(str(example["prompt"]))
    assistant_message = render_assistant_message(example)
    full_text = apply_chat_template_safe(
        tokenizer,
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ],
        add_generation_prompt=False,
        enable_thinking=True,
    )
    assistant_char_start = full_text.find(assistant_message)
    if assistant_char_start < 0:
        raise ValueError(f"Assistant span not found in rendered chat for row {example['id']}")
    try:
        full_encoded = tokenizer(
            full_text,
            add_special_tokens=False,
            truncation=True,
            max_length=max_seq_len,
            return_offsets_mapping=True,
        )
    except (NotImplementedError, TypeError):
        full_encoded = tokenizer(
            full_text,
            add_special_tokens=False,
            truncation=True,
            max_length=max_seq_len,
        )
    input_ids = list(full_encoded["input_ids"])
    attention_mask = list(full_encoded["attention_mask"])
    offset_mapping = full_encoded.get("offset_mapping")
    assistant_token_start = None
    if offset_mapping:
        for index, (start, _end) in enumerate(offset_mapping):
            if start >= assistant_char_start:
                assistant_token_start = index
                break
    if assistant_token_start is None:
        prefix_text = full_text[:assistant_char_start]
        prefix_ids = tokenizer(
            prefix_text,
            add_special_tokens=False,
            truncation=True,
            max_length=max_seq_len,
        )["input_ids"]
        assistant_token_start = len(prefix_ids)
    if assistant_token_start >= len(input_ids):
        raise ValueError(f"Assistant tokens were truncated out for row {example['id']}")
    labels = [-100] * assistant_token_start + input_ids[assistant_token_start:]
    if len(labels) != len(input_ids):
        raise ValueError(f"Label/input length mismatch for row {example['id']}")
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


def move_batch_to_device(batch: dict[str, torch.Tensor], device_name: str) -> dict[str, torch.Tensor]:
    return {key: value.to(device_name) for key, value in batch.items()}


def load_phase2_frame(train_csv: Path, *, limit_rows: int | None) -> pd.DataFrame:
    frame = pd.read_csv(train_csv)
    if sorted(frame.columns.tolist()) != sorted(EXPECTED_PHASE2_COLUMNS):
        raise ValueError(f"Unexpected CSV columns in {train_csv}: {frame.columns.tolist()}")
    if limit_rows is not None:
        if len(frame) < limit_rows:
            raise ValueError(f"Requested {limit_rows} rows but CSV has only {len(frame)} rows.")
        frame = frame.head(limit_rows).copy()
    return frame


def discover_nemotron_target_modules(model: Any) -> list[str]:
    allowed = {"q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "in_proj", "out_proj"}
    found: set[str] = set()
    for name, module in model.named_modules():
        suffix = name.split(".")[-1]
        if suffix in allowed and hasattr(module, "weight"):
            found.add(suffix)
    required = {"q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj"}
    missing = sorted(required - found)
    if missing:
        raise RuntimeError(f"Missing expected Nemotron target modules: {missing}")
    return sorted(found)


def build_target_modules(model: Any, mode: str) -> str | list[str]:
    if mode == "all-linear":
        return "all-linear"
    if mode == "nemotron-safe":
        return discover_nemotron_target_modules(model)
    raise ValueError(f"Unsupported target_modules_mode: {mode}")


def normalize_adapter_config(
    output_dir: Path,
    *,
    revision: str | None,
    target_modules: str | list[str],
) -> None:
    config_path = output_dir / "adapter_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["base_model_name_or_path"] = DEFAULT_OFFICIAL_MODEL_REPO
    if revision:
        config["revision"] = revision
    else:
        config.pop("revision", None)
    config["bias"] = "none"
    config["use_dora"] = False
    config["modules_to_save"] = None
    config["target_modules"] = target_modules
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def package_submission(output_dir: Path) -> Path:
    required_files = ["adapter_config.json", "adapter_model.safetensors"]
    missing = [name for name in required_files if not (output_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required adapter files: {missing}")
    submission_path = output_dir / "submission.zip"
    with zipfile.ZipFile(submission_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in required_files:
            archive.write(output_dir / name, name)
    return submission_path


def load_phase0_helpers() -> ModuleType:
    spec = importlib.util.spec_from_file_location("phase0_offline_eval_build", PHASE0_BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {PHASE0_BUILD_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_prompts(tokenizer: Any, prompt_series: Sequence[str]) -> list[str]:
    prompts: list[str] = []
    for prompt_text in prompt_series:
        user_content = str(prompt_text) + "\n" + BOXED_INSTRUCTION
        rendered = apply_chat_template_safe(
            tokenizer,
            [{"role": "user", "content": user_content}],
            add_generation_prompt=True,
            enable_thinking=True,
        )
        prompts.append(rendered)
    return prompts


def summarize_scored_rows(helpers: ModuleType, row_level: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "overall": {
            "rows": len(row_level),
            "correct": sum(int(row["is_correct"]) for row in row_level),
            "accuracy": round(
                helpers.safe_div(sum(int(row["is_correct"]) for row in row_level), len(row_level)),
                4,
            ),
        },
        "by_family": helpers.aggregate_counts(row_level, "family_short"),
        "by_template_subtype": helpers.aggregate_counts(row_level, "template_subtype"),
        "by_answer_type": helpers.aggregate_counts(row_level, "answer_type"),
        "by_prompt_len_bucket": helpers.aggregate_counts(row_level, "prompt_len_bucket"),
        "by_num_examples": helpers.aggregate_counts(row_level, "num_examples"),
        "by_selection_tier": helpers.aggregate_counts(row_level, "selection_tier"),
        "binary_metrics": helpers.build_binary_metrics(row_level),
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

    def add_table(title: str, rows: list[dict[str, Any]], key_name: str) -> None:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| {key_name} | rows | correct | accuracy |")
        lines.append("| --- | ---: | ---: | ---: |")
        for row in rows:
            lines.append(f"| `{row[key_name]}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |")
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
    helpers: ModuleType,
    scored_rows: list[dict[str, Any]],
    holdout_rows: list[dict[str, Any]],
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
    buckets: dict[tuple[str, str], dict[str, int]] = {}
    for row in joined:
        key = (row["holdout_kind"], row["fold"])
        if key not in buckets:
            buckets[key] = {"rows": 0, "correct": 0}
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
                "accuracy": round(helpers.safe_div(stats["correct"], stats["rows"]), 4),
            }
        )
    return summary


def prepare_phase0_artifacts(
    helpers: ModuleType,
    *,
    analysis_csv: Path,
    output_root: Path,
    prebuilt_root: Path,
    force_rebuild: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    artifact_root = output_root / "artifacts"
    report_root = output_root / "reports"
    artifact_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    prebuilt_general = prebuilt_root / "general_stable_set.csv"
    prebuilt_binary = prebuilt_root / "binary_hard_set.csv"
    prebuilt_symbol = prebuilt_root / "symbol_watch_set.csv"
    prebuilt_holdouts = prebuilt_root / "binary_holdout_assignments.csv"
    prebuilt_manifest = prebuilt_root / "phase0_eval_manifest.json"
    prebuilt_ready = (
        not force_rebuild
        and prebuilt_general.exists()
        and prebuilt_binary.exists()
        and prebuilt_symbol.exists()
    )

    if prebuilt_ready:
        general_rows = helpers.load_csv_rows(prebuilt_general)
        binary_rows = helpers.load_csv_rows(prebuilt_binary)
        symbol_rows = helpers.load_csv_rows(prebuilt_symbol)
        holdout_rows = helpers.load_csv_rows(prebuilt_holdouts) if prebuilt_holdouts.exists() else []
        if prebuilt_manifest.exists():
            manifest = json.loads(prebuilt_manifest.read_text(encoding="utf-8"))
        else:
            manifest = helpers.build_manifest(
                analysis_csv=analysis_csv,
                general_rows=general_rows,
                binary_rows=binary_rows,
                symbol_rows=symbol_rows,
                holdouts=holdout_rows,
            )
    else:
        analysis_rows = helpers.load_csv_rows(analysis_csv)
        general_rows = helpers.mark_status_rows(helpers.build_general_stable_set(analysis_rows), "general_stable_set")
        binary_rows = helpers.mark_status_rows(helpers.build_binary_hard_set(analysis_rows), "binary_hard_set")
        symbol_rows = helpers.mark_status_rows(helpers.build_symbol_watch_set(analysis_rows), "symbol_watch_set")
        holdout_rows = helpers.build_binary_holdout_assignments(analysis_rows)
        manifest = helpers.build_manifest(
            analysis_csv=analysis_csv,
            general_rows=general_rows,
            binary_rows=binary_rows,
            symbol_rows=symbol_rows,
            holdouts=holdout_rows,
        )

    helpers.write_csv(artifact_root / "general_stable_set.csv", general_rows, helpers.benchmark_columns() + ["benchmark_index"])
    helpers.write_csv(artifact_root / "binary_hard_set.csv", binary_rows, helpers.benchmark_columns() + ["benchmark_index"])
    helpers.write_csv(artifact_root / "symbol_watch_set.csv", symbol_rows, helpers.benchmark_columns() + ["benchmark_index"])
    if holdout_rows:
        helpers.write_csv(
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
    helpers.write_csv(
        artifact_root / "phase0_combined_eval_set.csv",
        general_rows + binary_rows + symbol_rows,
        helpers.benchmark_columns() + ["benchmark_index"],
    )
    helpers.write_json(artifact_root / "phase0_eval_manifest.json", manifest)
    helpers.write_text(report_root / "phase0_eval_manifest.md", helpers.render_phase0_report(manifest))
    return general_rows, binary_rows, symbol_rows, holdout_rows, manifest


def train_command(args: argparse.Namespace) -> None:
    log_path = Path(args.log_path).resolve()
    model_spec = resolve_model_spec(args.model, log_path=log_path)
    train_csv = Path(args.train_csv).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    seed_everything(args.seed)
    device_plan = choose_device(args.device)
    frame = load_phase2_frame(train_csv, limit_rows=args.limit_rows)
    records = frame.to_dict(orient="records")

    append_jsonl(
        log_path,
        {
            "event": "train_start",
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_spec": model_spec,
            "revision": args.revision,
            "device": device_plan.name,
            "train_csv": str(train_csv),
            "rows": len(records),
            "mlx_policy": "disabled",
        },
    )

    print(f"Loading tokenizer from {model_spec}")
    tokenizer = load_tokenizer(model_spec, revision=args.revision, local_files_only=args.local_files_only)

    print(f"Loading model on {device_plan.name}")
    model = load_model(
        model_spec,
        revision=args.revision,
        local_files_only=args.local_files_only,
        device_plan=device_plan,
        training=True,
    )
    target_modules = build_target_modules(model, args.target_modules_mode)
    lora_config = LoraConfig(
        r=args.lora_rank,
        lora_alpha=args.lora_alpha,
        target_modules=target_modules,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        use_dora=False,
        modules_to_save=None,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("Tokenizing training rows")
    tokenized_items = [tokenize_training_row(tokenizer, row, max_seq_len=args.max_seq_len) for row in records]
    dataset = TokenizedPhase2Dataset(tokenized_items)
    collator = AssistantOnlyDataCollator(tokenizer.pad_token_id)
    generator = torch.Generator()
    generator.manual_seed(args.seed)
    train_loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator,
        generator=generator,
    )

    trainable_parameters = [param for param in model.parameters() if param.requires_grad]
    optimizer = AdamW(trainable_parameters, lr=args.learning_rate)
    total_update_steps = math.ceil(len(train_loader) / args.gradient_accumulation_steps) * args.num_epochs
    warmup_steps = math.ceil(total_update_steps * args.warmup_ratio)
    scheduler = get_cosine_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_update_steps,
    )

    metrics_path = output_dir / "training_metrics.jsonl"
    start_time = time.time()
    model.train()
    optimizer.zero_grad(set_to_none=True)
    global_step = 0
    for epoch_index in range(args.num_epochs):
        for batch_index, batch in enumerate(train_loader, start=1):
            moved = move_batch_to_device(batch, device_plan.name)
            outputs = model(**moved)
            loss = outputs.loss
            (loss / args.gradient_accumulation_steps).backward()

            if batch_index % args.gradient_accumulation_steps == 0 or batch_index == len(train_loader):
                torch.nn.utils.clip_grad_norm_(trainable_parameters, args.max_grad_norm)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1
                payload = {
                    "global_step": global_step,
                    "epoch": epoch_index + 1,
                    "loss": float(loss.detach().cpu().item()),
                    "learning_rate": float(scheduler.get_last_lr()[0]),
                }
                append_jsonl(metrics_path, payload)
                if global_step == 1 or global_step % args.logging_steps == 0:
                    print(
                        f"epoch={epoch_index + 1}/{args.num_epochs} "
                        f"step={global_step}/{total_update_steps} "
                        f"loss={payload['loss']:.6f} "
                        f"lr={payload['learning_rate']:.8f}"
                    )
                maybe_empty_cache(device_plan.name)

    print(f"Saving adapter to {output_dir}")
    model.save_pretrained(output_dir, safe_serialization=True)
    tokenizer.save_pretrained(output_dir)
    normalize_adapter_config(output_dir, revision=args.revision, target_modules=target_modules)
    submission_path = package_submission(output_dir)

    elapsed_seconds = round(time.time() - start_time, 2)
    manifest = {
        "phase": "phase2_binary_hybrid_transformers_repro",
        "source_notebook": str(
            REPO_ROOT / "baseline" / "cot" / "phase2_binary_dsl" / "train_rule_based_cot_phase2_binary_dsl.ipynb"
        ),
        "model_spec": model_spec,
        "base_model_name_or_path": DEFAULT_OFFICIAL_MODEL_REPO,
        "revision": args.revision,
        "device": device_plan.name,
        "torch_dtype": str(device_plan.torch_dtype),
        "train_csv": str(train_csv),
        "rows_used": len(records),
        "target_modules_mode": args.target_modules_mode,
        "target_modules": target_modules,
        "lora_rank": args.lora_rank,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "num_epochs": args.num_epochs,
        "batch_size": args.batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "learning_rate": args.learning_rate,
        "max_seq_len": args.max_seq_len,
        "submission_zip": str(submission_path),
        "mlx_policy": "disabled",
        "elapsed_seconds": elapsed_seconds,
    }
    write_json(output_dir / "training_manifest.json", manifest)
    append_jsonl(
        log_path,
        {
            "event": "train_complete",
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "output_dir": str(output_dir),
            "submission_zip": str(submission_path),
            "elapsed_seconds": elapsed_seconds,
        },
    )

    del model
    gc.collect()
    maybe_empty_cache(device_plan.name)


def eval_phase0_command(args: argparse.Namespace) -> None:
    log_path = Path(args.log_path).resolve()
    model_spec = resolve_model_spec(args.model, log_path=log_path)
    adapter_dir = Path(args.adapter_dir).resolve()
    output_root = Path(args.output_root).resolve()
    analysis_csv = Path(args.analysis_csv).resolve()
    prebuilt_root = Path(args.prebuilt_root).resolve()
    required_adapter_files = [adapter_dir / "adapter_config.json", adapter_dir / "adapter_model.safetensors"]
    missing = [str(path) for path in required_adapter_files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Adapter directory is missing required files: {missing}")

    seed_everything(args.seed)
    device_plan = choose_device(args.device)
    helpers = load_phase0_helpers()
    general_rows, binary_rows, symbol_rows, holdout_rows, manifest = prepare_phase0_artifacts(
        helpers,
        analysis_csv=analysis_csv,
        output_root=output_root,
        prebuilt_root=prebuilt_root,
        force_rebuild=args.force_rebuild_phase0,
    )
    benchmark_rows = general_rows + binary_rows + symbol_rows
    if args.limit_rows is not None:
        benchmark_rows = benchmark_rows[: args.limit_rows]

    append_jsonl(
        log_path,
        {
            "event": "phase0_eval_start",
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_spec": model_spec,
            "adapter_dir": str(adapter_dir),
            "device": device_plan.name,
            "rows": len(benchmark_rows),
            "max_new_tokens": args.max_new_tokens,
            "mlx_policy": "disabled",
        },
    )

    print(f"Loading tokenizer from {model_spec}")
    tokenizer = load_tokenizer(model_spec, revision=args.revision, local_files_only=args.local_files_only)
    prompts = build_prompts(tokenizer, [row["prompt"] for row in benchmark_rows])

    print(f"Loading base model on {device_plan.name}")
    base_model = load_model(
        model_spec,
        revision=args.revision,
        local_files_only=args.local_files_only,
        device_plan=device_plan,
        training=False,
    )
    model = PeftModel.from_pretrained(base_model, adapter_dir, is_trainable=False)
    model.eval()

    artifact_root = output_root / "artifacts"
    report_root = output_root / "reports"
    artifact_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    start_time = time.time()
    for index, (row, rendered_prompt) in enumerate(zip(benchmark_rows, prompts), start=1):
        encoded = tokenizer(
            rendered_prompt,
            return_tensors="pt",
            add_special_tokens=False,
        )
        prompt_tokens = int(encoded["input_ids"].shape[-1])
        available_new_tokens = args.max_model_len - prompt_tokens
        if available_new_tokens <= 0:
            raise ValueError(
                f"Prompt for row {row['id']} already consumes {prompt_tokens} tokens, leaving no room under max_model_len={args.max_model_len}."
            )
        encoded = {key: value.to(device_plan.name) for key, value in encoded.items()}
        row_max_new_tokens = min(args.max_new_tokens, available_new_tokens)
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                do_sample=False,
                max_new_tokens=row_max_new_tokens,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
        generated_tokens = generated[0][encoded["input_ids"].shape[-1] :]
        raw_output = tokenizer.decode(generated_tokens, skip_special_tokens=False)
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
                "extracted_answer": helpers.extract_final_answer(raw_output),
            }
        )
        if index == 1 or index % args.logging_steps == 0 or index == len(benchmark_rows):
            print(f"generated {index}/{len(benchmark_rows)} rows")
        maybe_empty_cache(device_plan.name)

    helpers.write_csv(
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

    scored_rows: list[dict[str, Any]] = []
    for row in records:
        derived = helpers.analyze_raw_output(row["raw_output"])
        prediction = derived["extracted_answer"]
        scored_rows.append(
            {
                "benchmark_name": row["benchmark_name"],
                "benchmark_role": row["benchmark_role"],
                "benchmark_index": row["benchmark_index"],
                "id": row["id"],
                "gold_answer": row["expected_answer"],
                "prediction": prediction,
                "is_correct": helpers.verify_answer(row["expected_answer"], prediction),
                "family": row["family"],
                "family_short": row["family_short"],
                "template_subtype": row["template_subtype"],
                "answer_type": row["answer_type"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "selection_tier": row["selection_tier"],
                "num_examples": row["num_examples"],
                "prompt_len_chars": row["prompt_len_chars"],
                "prompt_len_bucket": helpers.prompt_len_bucket(helpers.parse_int(row["prompt_len_chars"], 0)),
                "fallback_type": derived["fallback_type"],
                "format_bucket": derived["format_bucket"],
                "has_boxed": derived["has_boxed"],
                "boxed_count": derived["boxed_count"],
                "raw_output": row["raw_output"],
            }
        )

    summary = summarize_scored_rows(helpers, scored_rows)
    helpers.write_csv(
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
    helpers.write_json(artifact_root / "phase0_eval_summary.json", summary)
    helpers.write_text(report_root / "phase0_eval_summary.md", render_markdown_summary("phase0_eval_summary", summary))

    holdout_summary = build_binary_holdout_accuracy_rows(helpers, scored_rows, holdout_rows)
    if holdout_summary:
        helpers.write_csv(
            artifact_root / "phase0_binary_holdout_accuracy.csv",
            holdout_summary,
            ["holdout_kind", "fold", "rows", "correct", "accuracy"],
        )

    run_manifest = {
        "phase": "phase0_offline_eval_transformers_local",
        "source_notebook": str(
            REPO_ROOT / "baseline" / "cot" / "phase0_offline_eval" / "infer_rule_based_adapter_phase0_offline_eval.ipynb"
        ),
        "engine": "transformers_peft_local",
        "model_spec": model_spec,
        "adapter_dir": str(adapter_dir),
        "device": device_plan.name,
        "torch_dtype": str(device_plan.torch_dtype),
        "rows_evaluated": len(records),
        "max_new_tokens": args.max_new_tokens,
        "max_model_len": args.max_model_len,
        "readme_eval_assumptions": manifest["readme_eval_assumptions"],
        "note": "Notebook benchmark/scoring was cloned, but local generation uses Transformers+PEFT instead of vLLM because this workflow targets local execution.",
        "elapsed_seconds": round(time.time() - start_time, 2),
        "mlx_policy": "disabled",
    }
    write_json(output_root / "phase0_eval_run_manifest.json", run_manifest)
    append_jsonl(
        log_path,
        {
            "event": "phase0_eval_complete",
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "output_root": str(output_root),
            "rows_evaluated": len(records),
            "accuracy": summary["overall"]["accuracy"],
        },
    )

    del model
    del base_model
    gc.collect()
    maybe_empty_cache(device_plan.name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-file local reproduction for Phase 2 binary hybrid training and Phase 0 evaluation. "
            "This script intentionally rejects MLX model paths and uses the official Transformers model directly."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train a Phase 2 binary hybrid LoRA adapter.")
    train_parser.add_argument("--model", default=DEFAULT_MODEL_SPEC)
    train_parser.add_argument("--revision", default=None)
    train_parser.add_argument("--local-files-only", action="store_true")
    train_parser.add_argument("--device", choices=["auto", "cuda", "mps", "cpu"], default="auto")
    train_parser.add_argument("--train-csv", type=Path, default=DEFAULT_TRAIN_CSV)
    train_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "adapter_phase2_binary_hybrid")
    train_parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH)
    train_parser.add_argument("--limit-rows", type=int, default=900)
    train_parser.add_argument("--seed", type=int, default=42)
    train_parser.add_argument("--num-epochs", type=int, default=2)
    train_parser.add_argument("--batch-size", type=int, default=1)
    train_parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    train_parser.add_argument("--learning-rate", type=float, default=1e-4)
    train_parser.add_argument("--warmup-ratio", type=float, default=0.1)
    train_parser.add_argument("--max-grad-norm", type=float, default=1.0)
    train_parser.add_argument("--logging-steps", type=int, default=5)
    train_parser.add_argument("--max-seq-len", type=int, default=2048)
    train_parser.add_argument("--lora-rank", type=int, default=32)
    train_parser.add_argument("--lora-alpha", type=int, default=32)
    train_parser.add_argument("--lora-dropout", type=float, default=0.05)
    train_parser.add_argument("--target-modules-mode", choices=["all-linear", "nemotron-safe"], default="all-linear")

    eval_parser = subparsers.add_parser("eval-phase0", help="Run local Phase 0 offline evaluation with Transformers+PEFT.")
    eval_parser.add_argument("--model", default=DEFAULT_MODEL_SPEC)
    eval_parser.add_argument("--revision", default=None)
    eval_parser.add_argument("--local-files-only", action="store_true")
    eval_parser.add_argument("--device", choices=["auto", "cuda", "mps", "cpu"], default="auto")
    eval_parser.add_argument("--adapter-dir", type=Path, required=True)
    eval_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "phase0_offline_eval")
    eval_parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH)
    eval_parser.add_argument("--analysis-csv", type=Path, default=DEFAULT_PHASE0_ANALYSIS_CSV)
    eval_parser.add_argument("--prebuilt-root", type=Path, default=DEFAULT_PHASE0_PREBUILT_ROOT)
    eval_parser.add_argument("--force-rebuild-phase0", action="store_true")
    eval_parser.add_argument("--limit-rows", type=int, default=None)
    eval_parser.add_argument("--seed", type=int, default=42)
    eval_parser.add_argument("--max-new-tokens", type=int, default=README_MAX_TOKENS)
    eval_parser.add_argument("--max-model-len", type=int, default=README_MAX_MODEL_LEN)
    eval_parser.add_argument("--logging-steps", type=int, default=10)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "lora_rank", README_MAX_LORA_RANK) > README_MAX_LORA_RANK:
        raise ValueError(f"LoRA rank must be <= {README_MAX_LORA_RANK}.")
    try:
        if args.command == "train":
            train_command(args)
            return
        if args.command == "eval-phase0":
            eval_phase0_command(args)
            return
        raise ValueError(f"Unsupported command: {args.command}")
    except Exception as exc:
        append_jsonl(
            Path(getattr(args, "log_path", DEFAULT_LOG_PATH)).resolve(),
            {
                "event": "command_failed",
                "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "command": getattr(args, "command", "unknown"),
                "error_type": exc.__class__.__name__,
                "error": str(exc),
            },
        )
        raise


if __name__ == "__main__":
    main()
