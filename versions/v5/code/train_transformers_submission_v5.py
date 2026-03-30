from __future__ import annotations

import argparse
from contextlib import nullcontext
import gc
import importlib.machinery
import json
import math
import random
import re
import sys
import types
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Any, Iterable
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import torch
from huggingface_hub import snapshot_download
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from torch.nn.utils.rnn import pad_sequence
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, get_cosine_schedule_with_warmup


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / 'README.md').exists() and (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    raise RuntimeError(f'Could not locate repository root from {start}')


REPO_ROOT = find_repo_root(Path(__file__).resolve())
VERSION_ROOT = Path(__file__).resolve().parents[1]

MODEL_ID = 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16'
DEFAULT_MODEL_DIR = REPO_ROOT / 'model'
DEFAULT_CACHE_DIR = REPO_ROOT / 'hf_cache'
DEFAULT_TRAIN_CSV = REPO_ROOT / 'data' / 'train.csv'
DEFAULT_OUTPUT_ROOT = VERSION_ROOT / 'outputs' / 'transformers_submission_v5'
DEFAULT_PROMPT = 'If x + 3 = 10, what is x?'
DEFAULT_SMOKE_MAX_NEW_TOKENS = 256
DEFAULT_PROMPT_INSTRUCTION = (
    '\nPlease put your final answer inside `\\boxed{}`. '
    'For example: `\\boxed{your answer}`'
)

ALLOWED_TARGET_SUFFIXES = (
    'q_proj',
    'k_proj',
    'v_proj',
    'o_proj',
    'up_proj',
    'down_proj',
    'in_proj',
    'out_proj',
)
REQUIRED_CORE_TARGET_SUFFIXES = {
    'q_proj',
    'k_proj',
    'v_proj',
    'o_proj',
    'up_proj',
    'down_proj',
}

README_EVAL_CONTRACT: dict[str, Any] = {
    'base_model': 'NVIDIA Nemotron-3-Nano-30B',
    'max_lora_rank': 32,
    'max_tokens': 7680,
    'top_p': 1.0,
    'temperature': 0.0,
    'max_num_seqs': 64,
    'gpu_memory_utilization': 0.85,
    'max_model_len': 8192,
    'answer_extraction': 'prioritize \\boxed{} content',
    'inference_engine': 'vLLM',
}


@dataclass
class TrainSummary:
    adapter_dir: str
    base_model_id: str
    base_model_path: str
    revision: str
    device: str
    dtype: str
    train_rows: int
    optimizer_steps: int
    target_modules: list[str]
    started_at: str
    completed_at: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if value != value:
        return None
    text = value if isinstance(value, str) else str(value)
    normalized = text.strip()
    if not normalized or normalized.lower() == 'nan':
        return None
    return normalized


def package_versions() -> dict[str, str]:
    names = {
        'transformers': 'transformers',
        'accelerate': 'accelerate',
        'peft': 'peft',
        'torch': 'torch',
        'huggingface_hub': 'huggingface-hub',
        'pandas': 'pandas',
        'sentencepiece': 'sentencepiece',
        'safetensors': 'safetensors',
    }
    resolved: dict[str, str] = {}
    for logical_name, dist_name in names.items():
        try:
            resolved[logical_name] = package_version(dist_name)
        except PackageNotFoundError:
            resolved[logical_name] = 'missing'
    return resolved


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + '\n')


def require_existing_path(path_value: str | Path, *, label: str) -> Path:
    path = Path(path_value)
    if path.exists():
        return path
    raise FileNotFoundError(f'{label} not found: {path}')


def has_complete_transformers_snapshot(model_dir: Path) -> bool:
    if not model_dir.exists() or not model_dir.is_dir():
        return False
    required = (
        'config.json',
        'configuration_nemotron_h.py',
        'modeling_nemotron_h.py',
        'tokenizer.json',
        'tokenizer_config.json',
        'model.safetensors.index.json',
    )
    return all((model_dir / name).exists() for name in required)


def validate_transformers_model_dir(model_dir: Path) -> None:
    if not model_dir.exists() or not model_dir.is_dir():
        raise FileNotFoundError(f'Base model path not found: {model_dir}')

    required = (
        'config.json',
        'tokenizer.json',
        'tokenizer_config.json',
        'model.safetensors.index.json',
    )
    missing = [name for name in required if not (model_dir / name).exists()]
    if missing:
        raise RuntimeError(
            f'Base model path is missing required Transformers files: {model_dir} '
            f'(missing: {missing})'
        )

    config_path = model_dir / 'config.json'
    payload = json.loads(config_path.read_text(encoding='utf-8'))
    quantization = payload.get('quantization') or payload.get('quantization_config')
    if isinstance(quantization, dict) and quantization:
        raise RuntimeError(
            f'Base model path points to a quantized snapshot, which is not allowed for this workflow: '
            f'{model_dir} (quantization={quantization})'
        )

    remote_code_files = (
        'configuration_nemotron_h.py',
        'modeling_nemotron_h.py',
    )
    missing_remote_code = [name for name in remote_code_files if not (model_dir / name).exists()]
    if missing_remote_code:
        raise RuntimeError(
            f'Base model path is missing required Nemotron remote-code files: {model_dir} '
            f'(missing: {missing_remote_code})'
        )


def download_official_snapshot(cache_dir: Path, revision: str) -> Path:
    allow_patterns = [
        '*.json',
        '*.py',
        '*.jinja',
        '*.txt',
        '*.model',
        '*.safetensors',
        'tokenizer*',
        'special_tokens_map.json',
        'chat_template.jinja',
    ]
    local_path = snapshot_download(
        repo_id=MODEL_ID,
        revision=revision,
        cache_dir=str(cache_dir),
        allow_patterns=allow_patterns,
    )
    return Path(local_path)


def resolve_base_model_path(
    *,
    base_model_path: str | None,
    cache_dir: Path,
    revision: str,
    allow_download: bool,
) -> Path:
    requested = normalize_optional_text(base_model_path)
    if requested is not None:
        explicit_path = Path(requested)
        if explicit_path.exists():
            validate_transformers_model_dir(explicit_path)
            return explicit_path.resolve()
        if requested != MODEL_ID:
            raise FileNotFoundError(f'Base model path does not exist: {explicit_path}')
    if has_complete_transformers_snapshot(DEFAULT_MODEL_DIR):
        validate_transformers_model_dir(DEFAULT_MODEL_DIR)
        return DEFAULT_MODEL_DIR.resolve()
    if allow_download or requested == MODEL_ID:
        return download_official_snapshot(cache_dir, revision).resolve()
    raise RuntimeError(
        'Official Transformers BF16 model was not found locally. '
        'Provide --base-model-path or use --download-snapshot.'
    )


def resolve_device(preferred: str) -> str:
    candidate = preferred.strip().lower()
    if candidate == 'auto':
        if torch.backends.mps.is_available():
            return 'mps'
        if torch.cuda.is_available():
            return 'cuda'
        return 'cpu'
    if candidate == 'mps':
        if not torch.backends.mps.is_available():
            raise RuntimeError('MPS is not available on this machine.')
        return 'mps'
    if candidate == 'cuda':
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA is not available on this machine.')
        return 'cuda'
    if candidate == 'cpu':
        return 'cpu'
    raise ValueError(f'Unsupported device: {preferred}')


def resolve_torch_dtype(device: str) -> torch.dtype:
    if device in {'mps', 'cuda'}:
        return torch.float16
    return torch.float32


_NON_CUDA_STREAM_PATCHED = False
_MAMBA_RMSNORM_FALLBACK_PATCHED = False


class _NullCudaStream:
    pass


def _device_type(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, torch.device):
        return value.type
    text = str(value)
    if text.startswith('cuda'):
        return 'cuda'
    if text.startswith('mps'):
        return 'mps'
    if text.startswith('cpu'):
        return 'cpu'
    return text


def install_non_cuda_stream_fallback() -> None:
    global _NON_CUDA_STREAM_PATCHED
    if _NON_CUDA_STREAM_PATCHED:
        return

    original_default_stream = torch.cuda.default_stream
    original_stream = torch.cuda.stream

    def safe_default_stream(device: Any = None) -> Any:
        if _device_type(device) not in {None, 'cuda'}:
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
        raise NotImplementedError('fallback_mamba_rmsnorm_fn does not support bias')

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
    if 'mamba_ssm.ops.triton.layernorm_gated' in sys.modules:
        _MAMBA_RMSNORM_FALLBACK_PATCHED = True
        return

    mamba_ssm_module = sys.modules.setdefault('mamba_ssm', types.ModuleType('mamba_ssm'))
    ops_module = sys.modules.setdefault('mamba_ssm.ops', types.ModuleType('mamba_ssm.ops'))
    triton_module = sys.modules.setdefault('mamba_ssm.ops.triton', types.ModuleType('mamba_ssm.ops.triton'))
    layernorm_module = types.ModuleType('mamba_ssm.ops.triton.layernorm_gated')
    layernorm_module.rmsnorm_fn = fallback_mamba_rmsnorm_fn
    mamba_ssm_module.__spec__ = importlib.machinery.ModuleSpec('mamba_ssm', loader=None, is_package=True)
    ops_module.__spec__ = importlib.machinery.ModuleSpec('mamba_ssm.ops', loader=None, is_package=True)
    triton_module.__spec__ = importlib.machinery.ModuleSpec('mamba_ssm.ops.triton', loader=None, is_package=True)
    layernorm_module.__spec__ = importlib.machinery.ModuleSpec(
        'mamba_ssm.ops.triton.layernorm_gated',
        loader=None,
        is_package=False,
    )

    mamba_ssm_module.ops = ops_module
    ops_module.triton = triton_module
    triton_module.layernorm_gated = layernorm_module
    sys.modules['mamba_ssm.ops.triton.layernorm_gated'] = layernorm_module
    _MAMBA_RMSNORM_FALLBACK_PATCHED = True


def install_nemotron_non_cuda_fallbacks(device: str) -> None:
    if device == 'cuda':
        return
    install_non_cuda_stream_fallback()
    install_mamba_rmsnorm_fallback()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def maybe_apply_chat_template(
    tokenizer: Any,
    messages: list[dict[str, str]],
    *,
    tokenize: bool,
    add_generation_prompt: bool,
    return_tensors: str | None = None,
) -> Any:
    kwargs: dict[str, Any] = {
        'tokenize': tokenize,
        'add_generation_prompt': add_generation_prompt,
    }
    if return_tensors is not None:
        kwargs['return_tensors'] = return_tensors
    try:
        return tokenizer.apply_chat_template(messages, enable_thinking=True, **kwargs)
    except TypeError:
        return tokenizer.apply_chat_template(messages, **kwargs)


def build_training_prompt(raw_prompt: str, prompt_instruction: str) -> str:
    instruction = prompt_instruction.strip()
    return raw_prompt if not instruction else f'{raw_prompt}{instruction}'


def render_answer_completion(answer: str) -> str:
    answer_text = answer.strip()
    if not answer_text:
        raise ValueError('answer text must not be empty')
    return rf'\boxed{{{answer_text}}}'


def extract_boxed_answer(text: str) -> str | None:
    matches = re.findall(r'\\boxed\s*\{([^}]*)\}', text)
    if not matches:
        return None
    answer = matches[-1].strip()
    return answer or None


def load_tokenizer(model_path: Path) -> Any:
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
    if tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_model(
    *,
    model_path: Path,
    device: str,
    dtype: torch.dtype,
    for_training: bool,
) -> Any:
    install_nemotron_non_cuda_fallbacks(device)
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        trust_remote_code=True,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        attn_implementation='eager',
    )
    model.to(device)
    if for_training:
        model.config.use_cache = False
        model.gradient_checkpointing_enable()
    else:
        model.eval()
    return model


def discover_target_modules(model: Any) -> list[str]:
    discovered: set[str] = set()
    for name, module in model.named_modules():
        suffix = name.split('.')[-1]
        if suffix in ALLOWED_TARGET_SUFFIXES and hasattr(module, 'weight'):
            discovered.add(suffix)
    missing = sorted(REQUIRED_CORE_TARGET_SUFFIXES - discovered)
    if missing:
        raise RuntimeError(f'Missing expected Nemotron target modules: {missing}')
    return sorted(discovered)


def format_training_example(tokenizer: Any, prompt: str, answer: str, prompt_instruction: str) -> str:
    messages = [
        {'role': 'user', 'content': build_training_prompt(str(prompt), prompt_instruction)},
        {'role': 'assistant', 'content': render_answer_completion(str(answer))},
    ]
    return str(
        maybe_apply_chat_template(
            tokenizer,
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
    )


def tokenize_training_examples(
    *,
    tokenizer: Any,
    train_csv_path: Path,
    prompt_instruction: str,
    max_length: int,
    max_rows: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    frame = pd.read_csv(train_csv_path)
    if not {'prompt', 'answer'}.issubset(frame.columns):
        raise ValueError("train.csv must contain at least 'prompt' and 'answer' columns.")
    original_rows = len(frame)
    if max_rows > 0:
        frame = frame.head(max_rows).copy()
    frame = frame.reset_index(drop=True)

    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient='records'):
        prompt = normalize_optional_text(row.get('prompt'))
        answer = normalize_optional_text(row.get('answer'))
        if prompt is None or answer is None:
            continue
        text = format_training_example(tokenizer, prompt, answer, prompt_instruction)
        encoded = tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=max_length,
            padding=False,
        )
        input_ids = encoded['input_ids'][0]
        attention_mask = encoded['attention_mask'][0]
        labels = input_ids.clone()
        records.append(
            {
                'input_ids': input_ids,
                'attention_mask': attention_mask,
                'labels': labels,
                'metadata': {
                    'id': normalize_optional_text(row.get('id')),
                    'family': normalize_optional_text(row.get('family')),
                },
            }
        )

    if not records:
        raise RuntimeError('No valid training records were built from train.csv')

    manifest = {
        'input_path': str(train_csv_path),
        'original_rows': original_rows,
        'used_rows': len(records),
        'prompt_instruction': prompt_instruction,
        'max_length': max_length,
        'max_rows': max_rows,
    }
    return records, manifest


def collate_training_batch(examples: list[dict[str, Any]], pad_token_id: int) -> dict[str, torch.Tensor]:
    input_ids = pad_sequence(
        [example['input_ids'] for example in examples],
        batch_first=True,
        padding_value=pad_token_id,
    )
    attention_mask = pad_sequence(
        [example['attention_mask'] for example in examples],
        batch_first=True,
        padding_value=0,
    )
    labels = pad_sequence(
        [example['labels'] for example in examples],
        batch_first=True,
        padding_value=-100,
    )
    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'labels': labels,
    }


def move_batch_to_device(batch: dict[str, torch.Tensor], device: str) -> dict[str, torch.Tensor]:
    return {key: value.to(device) for key, value in batch.items()}


def normalize_adapter_config(
    *,
    adapter_dir: Path,
    revision: str,
    target_modules: list[str],
) -> None:
    config_path = adapter_dir / 'adapter_config.json'
    payload = json.loads(config_path.read_text(encoding='utf-8'))
    payload['base_model_name_or_path'] = MODEL_ID
    payload['revision'] = revision
    payload['bias'] = 'none'
    payload['use_dora'] = False
    payload['modules_to_save'] = None
    payload['target_modules'] = target_modules
    config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def validate_adapter_dir(adapter_dir: Path) -> dict[str, Any]:
    config_path = adapter_dir / 'adapter_config.json'
    weights_path = adapter_dir / 'adapter_model.safetensors'
    if not config_path.exists():
        raise RuntimeError(f'adapter_config.json not found: {config_path}')
    if not weights_path.exists():
        raise RuntimeError(f'adapter_model.safetensors not found: {weights_path}')
    if weights_path.stat().st_size <= 0:
        raise RuntimeError(f'adapter_model.safetensors is empty: {weights_path}')

    payload = json.loads(config_path.read_text(encoding='utf-8'))
    errors: list[str] = []

    if payload.get('base_model_name_or_path') != MODEL_ID:
        errors.append(
            f"base_model_name_or_path must be '{MODEL_ID}', got {payload.get('base_model_name_or_path')!r}"
        )
    rank = payload.get('r')
    if rank is None or int(rank) > README_EVAL_CONTRACT['max_lora_rank']:
        errors.append(f"r must be <= 32, got {rank!r}")
    if payload.get('bias') != 'none':
        errors.append(f"bias must be 'none', got {payload.get('bias')!r}")
    if payload.get('use_dora', False):
        errors.append('use_dora must be false')
    if payload.get('modules_to_save') is not None:
        errors.append(f"modules_to_save must be null/None, got {payload.get('modules_to_save')!r}")

    target_modules = payload.get('target_modules')
    if not isinstance(target_modules, list) or not target_modules:
        errors.append('target_modules must be a non-empty list')
    else:
        unknown = sorted(set(target_modules) - set(ALLOWED_TARGET_SUFFIXES))
        if unknown:
            errors.append(f'unknown target_modules for this Nemotron recipe: {unknown}')

    if errors:
        raise RuntimeError('INVALID ADAPTER:\n- ' + '\n- '.join(errors))

    return {
        'adapter_dir': str(adapter_dir),
        'r': int(rank),
        'target_modules': list(target_modules),
        'base_model_name_or_path': payload.get('base_model_name_or_path'),
        'revision': payload.get('revision'),
        'weights_bytes': weights_path.stat().st_size,
    }


def make_submission_zip(adapter_dir: Path, zip_path: Path) -> dict[str, Any]:
    validate_adapter_dir(adapter_dir)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path_resolved = zip_path.resolve()
    with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as archive:
        for file_path in sorted(adapter_dir.rglob('*')):
            if file_path.is_file() and file_path.resolve() != zip_path_resolved:
                archive.write(file_path, arcname=file_path.relative_to(adapter_dir))
    return {
        'zip_path': str(zip_path),
        'zip_size_bytes': zip_path.stat().st_size,
    }


def train_lora(args: argparse.Namespace) -> TrainSummary:
    started_at = utc_now()
    seed_everything(args.seed)

    cache_dir = Path(args.cache_dir)
    base_model_path = resolve_base_model_path(
        base_model_path=args.base_model_path,
        cache_dir=cache_dir,
        revision=args.revision,
        allow_download=args.download_snapshot,
    )
    train_csv_path = require_existing_path(args.train_csv, label='train csv')
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    device = resolve_device(args.device)
    dtype = resolve_torch_dtype(device)
    tokenizer = load_tokenizer(base_model_path)
    model = load_model(model_path=base_model_path, device=device, dtype=dtype, for_training=True)
    if tokenizer.pad_token_id is not None:
        model.config.pad_token_id = tokenizer.pad_token_id

    target_modules = discover_target_modules(model)

    if args.lora_r > README_EVAL_CONTRACT['max_lora_rank']:
        raise ValueError('This competition requires LoRA rank <= 32.')

    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=target_modules,
        bias='none',
        use_dora=False,
        modules_to_save=None,
    )
    model = get_peft_model(model, peft_config)
    if hasattr(model, 'enable_input_require_grads'):
        model.enable_input_require_grads()
    model.print_trainable_parameters()

    records, data_manifest = tokenize_training_examples(
        tokenizer=tokenizer,
        train_csv_path=train_csv_path,
        prompt_instruction=args.prompt_instruction,
        max_length=args.max_length,
        max_rows=args.max_rows,
    )

    train_loader = DataLoader(
        records,
        batch_size=args.train_batch_size,
        shuffle=True,
        collate_fn=lambda batch: collate_training_batch(batch, tokenizer.pad_token_id),
    )
    micro_steps_per_epoch = len(train_loader)
    target_micro_steps = max(1, math.ceil(micro_steps_per_epoch * args.epochs))
    optimizer_steps_target = max(1, math.ceil(target_micro_steps / args.grad_accum))
    warmup_steps = max(0, int(round(optimizer_steps_target * args.warmup_ratio)))

    optimizer = AdamW(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    if args.lr_schedule_type == 'cosine':
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=optimizer_steps_target,
        )
    else:
        scheduler = None

    manifest_path = output_dir / 'training_manifest.json'
    metrics_path = output_dir / 'training_metrics.jsonl'
    save_json(
        manifest_path,
        {
            'started_at': started_at,
            'base_model_id': MODEL_ID,
            'base_model_path': str(base_model_path),
            'revision': args.revision,
            'device': device,
            'dtype': str(dtype),
            'package_versions': package_versions(),
            'readme_eval_contract': README_EVAL_CONTRACT,
            'train_args': {
                'train_csv': str(train_csv_path),
                'output_dir': str(output_dir),
                'cache_dir': str(cache_dir),
                'max_rows': args.max_rows,
                'max_length': args.max_length,
                'epochs': args.epochs,
                'train_batch_size': args.train_batch_size,
                'grad_accum': args.grad_accum,
                'learning_rate': args.learning_rate,
                'weight_decay': args.weight_decay,
                'max_grad_norm': args.max_grad_norm,
                'warmup_ratio': args.warmup_ratio,
                'lr_schedule_type': args.lr_schedule_type,
                'lora_r': args.lora_r,
                'lora_alpha': args.lora_alpha,
                'lora_dropout': args.lora_dropout,
                'seed': args.seed,
                'prompt_instruction': args.prompt_instruction,
            },
            'target_modules': target_modules,
            'data_manifest': data_manifest,
            'target_micro_steps': target_micro_steps,
            'optimizer_steps_target': optimizer_steps_target,
        },
    )

    model.train()
    optimizer.zero_grad(set_to_none=True)
    micro_step = 0
    optimizer_step = 0
    epoch_index = 0

    while micro_step < target_micro_steps:
        epoch_index += 1
        for batch in train_loader:
            micro_step += 1
            moved = move_batch_to_device(batch, device)
            outputs = model(**moved)
            raw_loss = outputs.loss
            loss = raw_loss / args.grad_accum
            loss.backward()

            should_step = micro_step % args.grad_accum == 0 or micro_step == target_micro_steps
            if should_step:
                if args.max_grad_norm > 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_step += 1

                metric = {
                    'kind': 'train',
                    'created_at': utc_now(),
                    'epoch_index': epoch_index,
                    'micro_step': micro_step,
                    'optimizer_step': optimizer_step,
                    'train_loss': float(raw_loss.detach().cpu().item()),
                    'learning_rate': float(optimizer.param_groups[0]['lr']),
                }
                append_jsonl(metrics_path, metric)
                print(
                    f"optimizer_step={optimizer_step}/{optimizer_steps_target} "
                    f"micro_step={micro_step}/{target_micro_steps} "
                    f"loss={metric['train_loss']:.6f} lr={metric['learning_rate']:.8f}"
                )
                if device == 'mps':
                    torch.mps.empty_cache()

            if micro_step >= target_micro_steps:
                break

    model.save_pretrained(
        str(output_dir),
        safe_serialization=True,
        save_embedding_layers=False,
    )
    normalize_adapter_config(
        adapter_dir=output_dir,
        revision=args.revision,
        target_modules=target_modules,
    )
    validation_summary = validate_adapter_dir(output_dir)
    save_json(output_dir / 'validation_summary.json', validation_summary)

    completed_at = utc_now()
    final_summary = TrainSummary(
        adapter_dir=str(output_dir),
        base_model_id=MODEL_ID,
        base_model_path=str(base_model_path),
        revision=args.revision,
        device=device,
        dtype=str(dtype),
        train_rows=data_manifest['used_rows'],
        optimizer_steps=optimizer_step,
        target_modules=target_modules,
        started_at=started_at,
        completed_at=completed_at,
    )
    save_json(output_dir / 'training_summary.json', asdict(final_summary))

    del model
    gc.collect()
    if device == 'mps':
        torch.mps.empty_cache()

    print(json.dumps(asdict(final_summary), ensure_ascii=False, indent=2))
    return final_summary


def smoke_test_adapter(args: argparse.Namespace) -> dict[str, Any]:
    seed_everything(args.seed)
    adapter_dir = require_existing_path(args.adapter_dir, label='adapter dir')
    cache_dir = Path(args.cache_dir)
    base_model_path = resolve_base_model_path(
        base_model_path=args.base_model_path,
        cache_dir=cache_dir,
        revision=args.revision,
        allow_download=args.download_snapshot,
    )

    device = resolve_device(args.device)
    dtype = resolve_torch_dtype(device)
    tokenizer = load_tokenizer(base_model_path)
    base_model = load_model(model_path=base_model_path, device=device, dtype=dtype, for_training=False)
    model = PeftModel.from_pretrained(base_model, str(adapter_dir), is_trainable=False)
    model.eval()

    prompt = build_training_prompt(args.prompt, args.prompt_instruction)
    input_ids = maybe_apply_chat_template(
        tokenizer,
        [{'role': 'user', 'content': prompt}],
        tokenize=True,
        add_generation_prompt=True,
        return_tensors='pt',
    )
    attention_mask = None
    if isinstance(input_ids, torch.Tensor):
        input_tensor = input_ids
    elif hasattr(input_ids, 'input_ids'):
        input_tensor = input_ids['input_ids']
        attention_mask = input_ids.get('attention_mask')
    elif isinstance(input_ids, dict):
        input_tensor = input_ids['input_ids']
        attention_mask = input_ids.get('attention_mask')
    else:
        raise TypeError(f'Unsupported chat-template return type: {type(input_ids)!r}')
    input_tensor = input_tensor.to(device)
    if attention_mask is not None:
        attention_mask = attention_mask.to(device)

    with torch.no_grad():
        generate_kwargs: dict[str, Any] = {
            'input_ids': input_tensor,
            'max_new_tokens': args.max_new_tokens,
            'do_sample': False,
            'eos_token_id': tokenizer.eos_token_id,
            'pad_token_id': tokenizer.eos_token_id,
        }
        if attention_mask is not None:
            generate_kwargs['attention_mask'] = attention_mask
        generated = model.generate(**generate_kwargs)
    decoded = tokenizer.decode(generated[0], skip_special_tokens=False)
    generated_tokens = generated[0][input_tensor.shape[-1] :]
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=False)
    boxed_answer = extract_boxed_answer(generated_text) or extract_boxed_answer(decoded)

    summary = {
        'adapter_dir': str(adapter_dir),
        'base_model_path': str(base_model_path),
        'revision': args.revision,
        'device': device,
        'max_new_tokens': args.max_new_tokens,
        'prompt': args.prompt,
        'decoded_text': decoded,
        'generated_text': generated_text,
        'boxed_answer': boxed_answer,
        'has_boxed_answer': boxed_answer is not None,
        'prompt_token_count': int(input_tensor.shape[-1]),
        'generated_token_count': int(generated_tokens.shape[-1]),
        'created_at': utc_now(),
    }
    save_json(Path(adapter_dir) / 'smoke_test_summary.json', summary)

    del model
    del base_model
    gc.collect()
    if device == 'mps':
        torch.mps.empty_cache()

    print(generated_text)
    if boxed_answer is None and not getattr(args, 'allow_missing_boxed', False):
        raise ValueError(
            'Smoke test completed but no \\boxed{} answer was found in the generated text. '
            'Increase --max-new-tokens or inspect smoke_test_summary.json.'
        )
    return summary


def run_validation_command(args: argparse.Namespace) -> dict[str, Any]:
    summary = validate_adapter_dir(require_existing_path(args.adapter_dir, label='adapter dir'))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def run_make_submission_command(args: argparse.Namespace) -> dict[str, Any]:
    adapter_dir = require_existing_path(args.adapter_dir, label='adapter dir')
    zip_path = Path(args.zip_path)
    if zip_path.name != 'submission.zip':
        raise ValueError(f'zip filename must be submission.zip, got {zip_path.name}')
    summary = make_submission_zip(adapter_dir, zip_path)
    save_json(adapter_dir / 'submission_zip_summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def run_all(args: argparse.Namespace) -> dict[str, Any]:
    train_args = argparse.Namespace(**vars(args))
    train_summary = train_lora(train_args)

    smoke_args = argparse.Namespace(
        adapter_dir=train_summary.adapter_dir,
        cache_dir=args.cache_dir,
        revision=args.revision,
        prompt=args.smoke_prompt,
        max_new_tokens=args.max_new_tokens,
        prompt_instruction=args.prompt_instruction,
        base_model_path=args.base_model_path,
        download_snapshot=args.download_snapshot,
        device=args.device,
        seed=args.seed,
        allow_missing_boxed=args.allow_missing_boxed,
    )
    smoke_summary = smoke_test_adapter(smoke_args)

    validation_summary = validate_adapter_dir(Path(train_summary.adapter_dir))

    zip_path = Path(args.zip_path)
    zip_summary = make_submission_zip(Path(train_summary.adapter_dir), zip_path)

    combined = {
        'train_summary': asdict(train_summary),
        'smoke_summary': smoke_summary,
        'validation_summary': validation_summary,
        'zip_summary': zip_summary,
    }
    save_json(Path(train_summary.adapter_dir) / 'run_all_summary.json', combined)
    print(json.dumps(combined, ensure_ascii=False, indent=2))
    return combined


def add_shared_model_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--base-model-path', type=str, default=str(DEFAULT_MODEL_DIR))
    parser.add_argument('--cache-dir', type=str, default=str(DEFAULT_CACHE_DIR))
    parser.add_argument('--revision', type=str, default='main')
    parser.add_argument('--download-snapshot', action='store_true')
    parser.add_argument('--device', type=str, default='auto', choices=('auto', 'mps', 'cuda', 'cpu'))


def add_train_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--train-csv', type=str, default=str(DEFAULT_TRAIN_CSV))
    parser.add_argument('--output-dir', type=str, required=True)
    parser.add_argument('--max-rows', type=int, default=0)
    parser.add_argument('--max-length', type=int, default=1024)
    parser.add_argument('--epochs', type=float, default=1.0)
    parser.add_argument('--train-batch-size', type=int, default=1)
    parser.add_argument('--grad-accum', type=int, default=4)
    parser.add_argument('--learning-rate', type=float, default=2e-4)
    parser.add_argument('--weight-decay', type=float, default=0.0)
    parser.add_argument('--max-grad-norm', type=float, default=1.0)
    parser.add_argument('--warmup-ratio', type=float, default=0.1)
    parser.add_argument('--lr-schedule-type', type=str, default='cosine', choices=('cosine', 'constant'))
    parser.add_argument('--lora-r', type=int, default=16)
    parser.add_argument('--lora-alpha', type=int, default=32)
    parser.add_argument('--lora-dropout', type=float, default=0.0)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--prompt-instruction', type=str, default=DEFAULT_PROMPT_INSTRUCTION)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            'Single-file Transformers + PEFT LoRA pipeline for README-compatible '
            'NVIDIA Nemotron submission work.'
        )
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    train_parser = subparsers.add_parser('train-lora', help='Train a LoRA adapter from data/train.csv')
    add_shared_model_args(train_parser)
    add_train_args(train_parser)

    smoke_parser = subparsers.add_parser('smoke-test', help='Run a local generation smoke test with a saved adapter')
    add_shared_model_args(smoke_parser)
    smoke_parser.add_argument('--adapter-dir', type=str, required=True)
    smoke_parser.add_argument('--prompt', type=str, default=DEFAULT_PROMPT)
    smoke_parser.add_argument('--max-new-tokens', type=int, default=DEFAULT_SMOKE_MAX_NEW_TOKENS)
    smoke_parser.add_argument('--seed', type=int, default=42)
    smoke_parser.add_argument('--prompt-instruction', type=str, default=DEFAULT_PROMPT_INSTRUCTION)
    smoke_parser.add_argument('--allow-missing-boxed', action='store_true')

    validate_parser = subparsers.add_parser(
        'validate-submission',
        help='Validate adapter_config.json against README/vLLM submission constraints',
    )
    validate_parser.add_argument('--adapter-dir', type=str, required=True)

    zip_parser = subparsers.add_parser('make-submission', help='Create submission.zip from a validated adapter dir')
    zip_parser.add_argument('--adapter-dir', type=str, required=True)
    zip_parser.add_argument('--zip-path', type=str, default='submission.zip')

    run_all_parser = subparsers.add_parser(
        'run-all',
        help='Train, smoke-test, validate, and produce submission.zip in one command',
    )
    add_shared_model_args(run_all_parser)
    add_train_args(run_all_parser)
    run_all_parser.add_argument('--smoke-prompt', type=str, default=DEFAULT_PROMPT)
    run_all_parser.add_argument('--max-new-tokens', type=int, default=DEFAULT_SMOKE_MAX_NEW_TOKENS)
    run_all_parser.add_argument('--zip-path', type=str, default='submission.zip')
    run_all_parser.add_argument('--allow-missing-boxed', action='store_true')

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == 'train-lora':
        train_lora(args)
        return
    if args.command == 'smoke-test':
        smoke_test_adapter(args)
        return
    if args.command == 'validate-submission':
        run_validation_command(args)
        return
    if args.command == 'make-submission':
        run_make_submission_command(args)
        return
    if args.command == 'run-all':
        run_all(args)
        return
    raise ValueError(f'Unsupported command: {args.command}')


if __name__ == '__main__':
    main()
