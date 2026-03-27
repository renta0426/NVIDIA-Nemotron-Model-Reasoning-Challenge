from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import yaml


VERSION_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = VERSION_ROOT.parents[1]

DEFAULT_MODEL_REPO_ID = 'mlx-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16'
DEFAULT_LOCAL_MODEL_PATH = REPO_ROOT / 'model'
DEFAULT_TRAIN_CSV_PATH = REPO_ROOT / 'data' / 'train.csv'

DEFAULT_BOXED_PROMPT_INSTRUCTION = r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
OFFICIAL_FIRST_BEST_CONFIG_NAME = 'official_first_best_97_03_minimal'
OFFICIAL_FIRST_BEST_NOTES = (
    'Minimal standalone reproduction of the current README-faithful official-first BF16 pipeline: '
    'full-data official-long lowlr SFT + full-data official-long ultralowlr SFT + 97/3 LoRA merge.'
)

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

GENERALIST_CONFIG: dict[str, Any] = {
    'name': 'official_first_best_generalist_lowlr',
    'lora_r': 32,
    'lora_alpha': 16,
    'lora_dropout': 0.05,
    'learning_rate': 1.0e-4,
    'num_epochs': 1.0,
    'max_seq_len': 1024,
    'per_device_train_batch_size': 1,
    'gradient_accumulation_steps': 4,
    'num_layers': -1,
    'weighted_loss': False,
    'mask_prompt': False,
    'optimizer': 'adamw',
    'max_grad_norm': 1.0,
    'lr_schedule_type': 'cosine',
    'warmup_ratio': 0.1,
    'prompt_instruction': DEFAULT_BOXED_PROMPT_INSTRUCTION,
    'seed': 42,
    'notes': 'Generalist branch for the current official-first best pipeline: full train.csv, official boxed instruction, LR=1e-4.',
}

SPECIALIST_CONFIG: dict[str, Any] = {
    'name': 'official_first_best_specialist_ultralowlr',
    'lora_r': 32,
    'lora_alpha': 16,
    'lora_dropout': 0.05,
    'learning_rate': 5.0e-5,
    'num_epochs': 1.0,
    'max_seq_len': 1024,
    'per_device_train_batch_size': 1,
    'gradient_accumulation_steps': 4,
    'num_layers': -1,
    'weighted_loss': False,
    'mask_prompt': False,
    'optimizer': 'adamw',
    'max_grad_norm': 1.0,
    'lr_schedule_type': 'cosine',
    'warmup_ratio': 0.1,
    'prompt_instruction': DEFAULT_BOXED_PROMPT_INSTRUCTION,
    'seed': 42,
    'notes': 'Specialist branch for the current official-first best pipeline: full train.csv, official boxed instruction, LR=5e-5.',
}

DEFAULT_GENERALIST_WEIGHT = 0.97
DEFAULT_SPECIALIST_WEIGHT = 0.03


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


def require_existing_path(path_value: str | Path, *, label: str) -> Path:
    path = Path(path_value)
    if path.exists():
        return path
    raise FileNotFoundError(f'{label} not found: {path}')


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + '\n')


def split_repo_id(repo_id: str) -> tuple[str, str]:
    parts = repo_id.split('/', 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f'Invalid repo id: {repo_id}')
    return parts[0], parts[1]


def default_lms_models_root() -> Path:
    return Path.home() / '.lmstudio' / 'models'


def default_lms_model_path(repo_id: str) -> Path:
    publisher, artifact = split_repo_id(repo_id)
    return default_lms_models_root() / publisher / artifact


def huggingface_snapshot_root_for_repo(repo_id: str) -> Path:
    safe_repo = repo_id.replace('/', '--')
    return Path.home() / '.cache' / 'huggingface' / 'hub' / f'models--{safe_repo}' / 'snapshots'


def has_complete_mlx_snapshot(model_dir: Path) -> bool:
    if not model_dir.exists() or not model_dir.is_dir():
        return False
    if any(model_dir.glob('model-*.safetensors')):
        return True
    if (model_dir / 'model.safetensors').exists():
        return True
    index_path = model_dir / 'model.safetensors.index.json'
    if not index_path.exists():
        return False
    try:
        payload = json.loads(index_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return False
    weight_map = payload.get('weight_map')
    if not isinstance(weight_map, dict) or not weight_map:
        return False
    shard_names = {str(value) for value in weight_map.values() if value}
    return bool(shard_names) and all((model_dir / shard_name).exists() for shard_name in shard_names)


def resolve_preferred_mlx_model_path() -> str | None:
    candidate_paths = [DEFAULT_LOCAL_MODEL_PATH, default_lms_model_path(DEFAULT_MODEL_REPO_ID)]
    snapshot_root = huggingface_snapshot_root_for_repo(DEFAULT_MODEL_REPO_ID)
    if snapshot_root.exists():
        candidate_paths.extend(sorted(path for path in snapshot_root.iterdir() if path.is_dir()))
    for candidate in candidate_paths:
        if has_complete_mlx_snapshot(candidate):
            return str(candidate.resolve())
    return None


def resolve_base_model(base_model_value: Any) -> str:
    requested = normalize_optional_text(base_model_value)
    if requested not in {None, 'model', str(DEFAULT_LOCAL_MODEL_PATH), DEFAULT_MODEL_REPO_ID}:
        path = Path(requested)
        return str(path) if path.exists() else requested
    preferred = resolve_preferred_mlx_model_path()
    if preferred is not None:
        return preferred
    raise RuntimeError(
        'BF16 MLX model is required and no complete local snapshot was found. '
        'Run `uv run python download_bf16_mlx_model.py` to materialize the model into `model/`.'
    )


def resolve_prompt_instruction(value: Any, *, default: str = DEFAULT_BOXED_PROMPT_INSTRUCTION) -> str:
    normalized = normalize_optional_text(value)
    return normalized if normalized is not None else default


def build_training_prompt(raw_prompt: str, prompt_instruction: str) -> str:
    instruction = prompt_instruction.strip()
    return raw_prompt if not instruction else f'{raw_prompt}\n{instruction}'


def render_answer_completion(answer: str) -> str:
    answer_text = answer.strip()
    if not answer_text:
        raise ValueError('answer text must not be empty')
    return rf'\boxed{{{answer_text}}}'


def build_notebook_pack(
    *,
    input_path: str | Path,
    output_path: str | Path,
    base_model: str,
    prompt_instruction: str,
    subsample_size: int,
    subsample_seed: int,
) -> dict[str, Any]:
    import pandas as pd
    from transformers import AutoTokenizer

    source_path = require_existing_path(input_path, label='baseline train csv')
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(source_path)
    original_rows = len(frame)
    if subsample_size > 0 and len(frame) > subsample_size:
        frame = frame.sample(n=subsample_size, random_state=subsample_seed).reset_index(drop=True)

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token

    def render_row(row: dict[str, Any]) -> str:
        prompt = normalize_optional_text(row.get('prompt'))
        answer = normalize_optional_text(row.get('answer'))
        if prompt is None or answer is None:
            raise ValueError('baseline notebook rows must include prompt and answer')
        messages = [
            {'role': 'user', 'content': build_training_prompt(prompt, prompt_instruction)},
            {'role': 'assistant', 'content': render_answer_completion(answer)},
        ]
        return str(tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False))

    frame['format_policy'] = 'boxed'
    frame['source_dataset'] = 'baseline_notebook'
    frame['prompt_instruction'] = prompt_instruction
    frame['text'] = [render_row(row) for row in frame.to_dict(orient='records')]
    frame.to_parquet(target_path, index=False)

    return {
        'input_path': str(source_path),
        'output_path': str(target_path),
        'original_rows': original_rows,
        'output_rows': len(frame),
        'subsample_size': subsample_size,
        'subsample_seed': subsample_seed,
        'prompt_instruction': prompt_instruction,
        'base_model': base_model,
    }


def split_training_frame(frame: Any, *, valid_fraction: float, seed: int) -> tuple[Any, Any, str]:
    if frame.empty:
        return frame.copy(), frame.copy(), 'empty'
    if valid_fraction <= 0.0:
        return frame.copy(), frame.iloc[0:0].copy(), 'disabled'
    shuffled = frame.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    if len(shuffled) <= 1:
        return shuffled.copy(), shuffled.iloc[0:0].copy(), 'single_row'
    valid_size = max(1, int(round(len(shuffled) * valid_fraction)))
    valid_size = min(valid_size, len(shuffled) - 1)
    valid_df = shuffled.iloc[:valid_size].copy()
    train_df = shuffled.iloc[valid_size:].copy()
    return train_df, valid_df, f'random_fraction={valid_fraction}'


def maybe_limit_rows(frame: Any, *, max_rows: int | None, seed: int) -> Any:
    if max_rows is None or len(frame) <= max_rows:
        return frame
    return frame.sample(n=max_rows, random_state=seed).reset_index(drop=True)


def build_training_records(frame: Any) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    skipped = 0
    for row in frame.to_dict(orient='records'):
        text = normalize_optional_text(row.get('text'))
        if text is None:
            skipped += 1
            continue
        records.append(
            {
                'text': text,
                'metadata': {
                    'id': normalize_optional_text(row.get('id')),
                    'family': normalize_optional_text(row.get('family')),
                    'source_dataset': normalize_optional_text(row.get('source_dataset')) or 'baseline_notebook',
                },
            }
        )
    return records, skipped


def resolve_optimizer_steps(cfg: dict[str, Any], *, total_iters: int) -> int:
    grad_accumulation_steps = max(1, int(cfg.get('gradient_accumulation_steps', 1)))
    return max(1, math.ceil(max(int(total_iters), 1) / grad_accumulation_steps))


def build_mlx_lr_schedule_config(cfg: dict[str, Any], *, total_iters: int) -> dict[str, Any] | None:
    schedule_type = normalize_optional_text(cfg.get('lr_schedule_type'))
    if schedule_type is None:
        return None
    if schedule_type in {'cosine', 'cosine_decay'}:
        optimizer_steps = resolve_optimizer_steps(cfg, total_iters=total_iters)
        warmup_steps = max(0, int(round(float(cfg.get('warmup_ratio', 0.0)) * optimizer_steps)))
        return {
            'name': 'cosine_decay',
            'arguments': [float(cfg.get('learning_rate', 1e-4)), optimizer_steps],
            'warmup': warmup_steps,
        }
    raise ValueError(f'Unsupported MLX lr_schedule_type: {schedule_type}')


def build_mlx_optimizer(optim_module: Any, cfg: dict[str, Any], *, total_iters: int, default_learning_rate: float) -> Any:
    from mlx_lm.tuner.utils import build_schedule

    learning_rate: Any = float(cfg.get('learning_rate', default_learning_rate))
    lr_schedule = build_mlx_lr_schedule_config(cfg, total_iters=total_iters)
    if lr_schedule is not None:
        learning_rate = build_schedule(lr_schedule)
    optimizer_name = str(cfg.get('optimizer', 'adam')).strip().lower()
    if optimizer_name == 'adam':
        return optim_module.Adam(learning_rate=learning_rate)
    if optimizer_name == 'adamw':
        return optim_module.AdamW(learning_rate=learning_rate)
    if optimizer_name == 'sgd':
        return optim_module.SGD(learning_rate=learning_rate)
    if optimizer_name == 'adafactor':
        return optim_module.Adafactor(learning_rate=learning_rate)
    if optimizer_name == 'muon':
        return optim_module.Muon(learning_rate=learning_rate)
    raise ValueError(f'Unsupported optimizer: {optimizer_name}')


def build_stage_manifest(
    *,
    candidate_id: str,
    pipeline_role: str,
    config_name: str,
    base_model: str,
    train_pack_path: str | Path,
    train_records: int,
    valid_records: int,
    split_strategy: str,
    cfg: dict[str, Any],
    adapter_dir: Path,
    metrics_path: Path,
    skipped_rows: int,
    prompt_instruction: str,
) -> dict[str, Any]:
    return {
        'version': 'v4',
        'created_at': utc_now(),
        'candidate_id': candidate_id,
        'parent_candidate_id': None,
        'recipe_type': 'sft',
        'pipeline_role': pipeline_role,
        'config_name': config_name,
        'notes': normalize_optional_text(cfg.get('notes')),
        'model': {'base_model': base_model},
        'data': {
            'train_pack_path': str(train_pack_path),
            'train_records': train_records,
            'valid_records': valid_records,
            'split_strategy': split_strategy,
            'skipped_rows': skipped_rows,
            'prompt_instruction': prompt_instruction,
        },
        'training': {
            'learning_rate': float(cfg.get('learning_rate', 1e-4)),
            'num_epochs': float(cfg.get('num_epochs', 1.0)),
            'max_seq_len': int(cfg.get('max_seq_len', 1024)),
            'per_device_train_batch_size': int(cfg.get('per_device_train_batch_size', 1)),
            'gradient_accumulation_steps': int(cfg.get('gradient_accumulation_steps', 4)),
            'iters': int(cfg.get('iters', 1)),
            'mask_prompt': bool(cfg.get('mask_prompt', False)),
            'optimizer': str(cfg.get('optimizer', 'adamw')),
            'num_layers': int(cfg.get('num_layers', 16)),
            'optimizer_steps': resolve_optimizer_steps(cfg, total_iters=int(cfg.get('iters', 1))),
            'max_grad_norm': float(cfg.get('max_grad_norm', 0.0)),
            'lr_schedule_type': normalize_optional_text(cfg.get('lr_schedule_type')),
            'warmup_ratio': float(cfg.get('warmup_ratio', 0.0)),
        },
        'execution': {'adapter_dir': str(adapter_dir), 'metrics_path': str(metrics_path)},
        'loss': {
            'weighted': bool(cfg.get('weighted_loss', False)),
            'final_line_weight': float(cfg.get('final_line_weight', 1.0)),
            'answer_span_weights': dict(cfg.get('answer_span_weights', {})),
        },
        'readme_eval_contract': README_EVAL_CONTRACT,
    }


def render_mock_adapter(*, adapter_dir: Path, base_model: str, cfg: dict[str, Any], result_path: Path) -> dict[str, Any]:
    import numpy as np
    from safetensors.numpy import save_file

    adapter_dir.mkdir(parents=True, exist_ok=True)
    save_file({'layers.0.q_proj.lora_a': np.zeros((2, 2), dtype=np.float32)}, str(adapter_dir / 'adapters.safetensors'))
    save_json(
        adapter_dir / 'adapter_config.json',
        {
            'base_model_name_or_path': base_model,
            'fine_tune_type': 'lora',
            'num_layers': int(cfg.get('num_layers', 16)),
            'lora_parameters': {
                'rank': int(cfg.get('lora_r', 32)),
                'dropout': float(cfg.get('lora_dropout', 0.0)),
                'scale': float(cfg.get('lora_alpha', 32)),
            },
            'target_modules': list(cfg.get('target_modules', [])),
            'weighted_loss': False,
            'mask_prompt': bool(cfg.get('mask_prompt', False)),
            'optimizer': str(cfg.get('optimizer', 'adamw')),
            'max_grad_norm': float(cfg.get('max_grad_norm', 0.0)),
            'prompt_instruction': resolve_prompt_instruction(cfg.get('prompt_instruction')),
            'rationale_weight': float(cfg.get('rationale_weight', 1.0)),
            'final_line_weight': float(cfg.get('final_line_weight', 3.0)),
            'answer_span_weights': dict(cfg.get('answer_span_weights', {})),
            'parent_adapter_path': '',
        },
    )
    return {
        'status': 'rendered_only',
        'created_at': utc_now(),
        'metrics_path': str(result_path.with_name(result_path.stem.replace('_result', '_metrics') + '.jsonl')),
        'adapter_dir': str(adapter_dir),
        'final_train_loss': 0.0,
        'final_val_loss': 0.0,
        'peak_memory_gb': 0.0,
    }


def execute_training(
    *,
    train_records: list[dict[str, Any]],
    valid_records: list[dict[str, Any]],
    cfg: dict[str, Any],
    base_model: str,
    adapter_dir: Path,
    metrics_path: Path,
) -> dict[str, Any]:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    import numpy as np
    from mlx.utils import tree_flatten, tree_map
    from mlx_lm import load as mlx_load
    from mlx_lm.tuner import TrainingArgs, train as tuner_train
    from mlx_lm.tuner.datasets import CacheDataset
    from mlx_lm.tuner.utils import linear_to_lora_layers, print_trainable_parameters
    from mlx_lm.utils import save_config

    mask_prompt = bool(cfg.get('mask_prompt', False))

    class MetricsCallback:
        def __init__(self) -> None:
            self.last_train_loss: float | None = None
            self.last_val_loss: float | None = None
            self.peak_memory: float | None = None

        def on_train_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_train_loss = float(payload.get('train_loss')) if payload.get('train_loss') is not None else None
            self.peak_memory = float(payload.get('peak_memory')) if payload.get('peak_memory') is not None else self.peak_memory
            append_jsonl(metrics_path, {'kind': 'train', 'created_at': utc_now(), **payload})

        def on_val_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_val_loss = float(payload.get('val_loss')) if payload.get('val_loss') is not None else None
            append_jsonl(metrics_path, {'kind': 'val', 'created_at': utc_now(), **payload})

    class TextDataset:
        def __init__(self, data: list[dict[str, Any]], tokenizer: Any) -> None:
            self._data = data
            self.tokenizer = tokenizer

        def __getitem__(self, index: int) -> dict[str, Any]:
            return self._data[index]

        def process(self, datum: dict[str, Any]) -> tuple[list[int], int, list[float]]:
            raw_text = normalize_optional_text(datum.get('text'))
            if raw_text is None:
                raise ValueError('official-first minimal training expects pre-rendered `text` records')
            tokens = list(self.tokenizer.encode(raw_text, add_special_tokens=False))
            return tokens, 0, [1.0] * len(tokens)

        def __len__(self) -> int:
            return len(self._data)

    def iterate_batches(dataset: Any, batch_size: int, max_seq_length: int, loop: bool = False, seed: int | None = None, comm_group: Any = None):
        idx = sorted(range(len(dataset)), key=lambda sample_index: len(dataset[sample_index][0]))
        if len(dataset) < batch_size:
            raise ValueError(f'Dataset must have at least batch_size={batch_size} examples but only has {len(dataset)}.')
        if comm_group is not None:
            offset = comm_group.rank()
            step = comm_group.size()
        else:
            offset = 0
            step = 1
        if batch_size % step != 0:
            raise ValueError('The batch size must be divisible by the number of workers')
        batch_idx = [idx[i + offset : i + offset + batch_size : step] for i in range(0, len(idx) - batch_size + 1, batch_size)]
        if seed is not None:
            np.random.seed(seed)
        while True:
            indices = np.random.permutation(len(batch_idx))
            for batch_index in indices:
                batch = [dataset[item_index] for item_index in batch_idx[batch_index]]
                token_lists, offsets, weight_lists = zip(*batch)
                lengths = [len(tokens) for tokens in token_lists]
                pad_to = 32
                max_length = min(1 + pad_to * ((max(lengths) + pad_to - 1) // pad_to), max_seq_length)
                batch_arr = np.zeros((batch_size // step, max_length), np.int32)
                weight_arr = np.ones((batch_size // step, max_length), np.float32)
                packed_lengths: list[tuple[int, int]] = []
                for row_index in range(batch_size // step):
                    truncated_length = min(lengths[row_index], max_seq_length)
                    batch_arr[row_index, :truncated_length] = token_lists[row_index][:truncated_length]
                    weight_arr[row_index, :truncated_length] = weight_lists[row_index][:truncated_length]
                    packed_lengths.append((int(offsets[row_index]), truncated_length))
                yield mx.array(batch_arr), mx.array(packed_lengths), mx.array(weight_arr)
            if not loop:
                break

    def loss_fn(model: Any, batch: Any, lengths: Any, token_weights: Any) -> tuple[Any, Any]:
        inputs = batch[:, :-1]
        targets = batch[:, 1:]
        logits = model(inputs)
        steps = mx.arange(1, targets.shape[1] + 1)
        if mask_prompt:
            active_mask = mx.logical_and(steps >= lengths[:, 0:1], steps <= lengths[:, 1:])
        else:
            active_mask = steps <= lengths[:, 1:]
        weights = token_weights[:, 1:] * active_mask.astype(token_weights.dtype)
        ntoks = weights.astype(mx.float32).sum()
        ce = nn.losses.cross_entropy(logits, targets) * weights
        denom = mx.maximum(ntoks, mx.array(1.0, dtype=mx.float32))
        return ce.astype(mx.float32).sum() / denom, ntoks

    def clip_gradient_tree(grad: Any, max_grad_norm: float) -> Any:
        if max_grad_norm <= 0:
            return grad
        squared_norm = None
        for _, value in tree_flatten(grad):
            if value is None:
                continue
            value_f32 = value.astype(mx.float32)
            term = (value_f32 * value_f32).sum()
            squared_norm = term if squared_norm is None else squared_norm + term
        if squared_norm is None:
            return grad
        grad_norm = mx.sqrt(squared_norm)
        clip_scale = mx.minimum(
            mx.array(1.0, dtype=mx.float32),
            mx.array(float(max_grad_norm), dtype=mx.float32) / (grad_norm + 1e-6),
        )
        return tree_map(lambda value: value * clip_scale if value is not None else None, grad)

    class GradientClippedOptimizer:
        def __init__(self, base_optimizer: Any, max_grad_norm: float) -> None:
            self._base_optimizer = base_optimizer
            self._max_grad_norm = float(max_grad_norm)

        @property
        def state(self) -> Any:
            return self._base_optimizer.state

        @property
        def learning_rate(self) -> Any:
            return self._base_optimizer.learning_rate

        def update(self, model: Any, grad: Any) -> Any:
            return self._base_optimizer.update(model, clip_gradient_tree(grad, self._max_grad_norm))

    callback = MetricsCallback()
    model, tokenizer = mlx_load(base_model)
    model.freeze()
    linear_to_lora_layers(
        model,
        int(cfg.get('num_layers', -1)),
        {
            'rank': int(cfg.get('lora_r', 32)),
            'dropout': float(cfg.get('lora_dropout', 0.0)),
            'scale': float(cfg.get('lora_alpha', 32)),
        },
    )
    print_trainable_parameters(model)
    adapter_dir.mkdir(parents=True, exist_ok=True)
    save_config(
        {
            'base_model_name_or_path': base_model,
            'fine_tune_type': 'lora',
            'num_layers': int(cfg.get('num_layers', -1)),
            'lora_parameters': {
                'rank': int(cfg.get('lora_r', 32)),
                'dropout': float(cfg.get('lora_dropout', 0.0)),
                'scale': float(cfg.get('lora_alpha', 32)),
            },
            'target_modules': list(cfg.get('target_modules', [])),
            'weighted_loss': False,
            'mask_prompt': mask_prompt,
            'optimizer': str(cfg.get('optimizer', 'adamw')),
            'max_grad_norm': float(cfg.get('max_grad_norm', 0.0)),
            'prompt_instruction': resolve_prompt_instruction(cfg.get('prompt_instruction')),
            'rationale_weight': float(cfg.get('rationale_weight', 1.0)),
            'final_line_weight': float(cfg.get('final_line_weight', 3.0)),
            'answer_span_weights': dict(cfg.get('answer_span_weights', {})),
            'parent_adapter_path': '',
        },
        adapter_dir / 'adapter_config.json',
    )
    optimizer = build_mlx_optimizer(
        optim,
        cfg,
        total_iters=int(cfg.get('iters', 1)),
        default_learning_rate=1e-4,
    )
    max_grad_norm = float(cfg.get('max_grad_norm', 0.0))
    if max_grad_norm > 0:
        optimizer = GradientClippedOptimizer(optimizer, max_grad_norm=max_grad_norm)
    training_args = TrainingArgs(
        batch_size=int(cfg.get('per_device_train_batch_size', 1)),
        iters=int(cfg.get('iters', 1)),
        val_batches=int(cfg.get('val_batches', -1)),
        steps_per_report=int(cfg.get('steps_per_report', 1)),
        steps_per_eval=int(cfg.get('steps_per_eval', max(1, int(cfg.get('iters', 1)) // 2))),
        steps_per_save=int(cfg.get('save_every', max(1, int(cfg.get('iters', 1))))),
        adapter_file=str(adapter_dir / 'adapters.safetensors'),
        max_seq_length=int(cfg.get('max_seq_len', 1024)),
        grad_checkpoint=bool(cfg.get('grad_checkpoint', False)),
        grad_accumulation_steps=int(cfg.get('gradient_accumulation_steps', 4)),
    )
    train_set = CacheDataset(TextDataset(train_records, tokenizer))
    valid_set = CacheDataset(TextDataset(valid_records, tokenizer)) if valid_records else None
    tuner_train(
        model=model,
        optimizer=optimizer,
        train_dataset=train_set,
        val_dataset=valid_set,
        args=training_args,
        loss=loss_fn,
        iterate_batches=iterate_batches,
        training_callback=callback,
    )
    return {
        'status': 'completed',
        'created_at': utc_now(),
        'metrics_path': str(metrics_path),
        'adapter_dir': str(adapter_dir),
        'final_train_loss': callback.last_train_loss,
        'final_val_loss': callback.last_val_loss,
        'peak_memory_gb': callback.peak_memory,
    }


def compute_stage_iters(cfg: dict[str, Any], *, train_record_count: int) -> int:
    effective_train_rows = max(train_record_count, 1)
    return max(
        1,
        int(
            effective_train_rows
            * float(cfg.get('num_epochs', 1.0))
            // max(int(cfg.get('per_device_train_batch_size', 1)), 1)
        ),
    )


def run_training_stage(
    *,
    stage_name: str,
    stage_candidate_id: str,
    stage_cfg_template: dict[str, Any],
    base_model: str,
    prompt_instruction: str,
    pack_output_path: Path,
    train_records: list[dict[str, Any]],
    valid_records: list[dict[str, Any]],
    split_strategy: str,
    skipped_rows: int,
    output_dir: Path,
    execute: bool,
) -> dict[str, Any]:
    stage_output_dir = output_dir / stage_name
    stage_output_dir.mkdir(parents=True, exist_ok=True)
    config_output_path = stage_output_dir / f'{stage_candidate_id}_config.yaml'
    manifest_path = stage_output_dir / f'{stage_candidate_id}_manifest.json'
    result_path = stage_output_dir / f'{stage_candidate_id}_result.json'
    metrics_path = stage_output_dir / f'{stage_candidate_id}_metrics.jsonl'
    adapter_dir = stage_output_dir / f'adapter_{stage_candidate_id}'

    cfg = dict(stage_cfg_template)
    cfg['base_model'] = base_model
    cfg['prompt_instruction'] = prompt_instruction
    cfg['iters'] = compute_stage_iters(cfg, train_record_count=len(train_records))
    config_output_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding='utf-8')

    manifest = build_stage_manifest(
        candidate_id=stage_candidate_id,
        pipeline_role=stage_name,
        config_name=str(cfg['name']),
        base_model=base_model,
        train_pack_path=pack_output_path,
        train_records=len(train_records),
        valid_records=len(valid_records),
        split_strategy=split_strategy,
        cfg=cfg,
        adapter_dir=adapter_dir,
        metrics_path=metrics_path,
        skipped_rows=skipped_rows,
        prompt_instruction=prompt_instruction,
    )
    save_json(manifest_path, manifest)

    if execute:
        result = execute_training(
            train_records=train_records,
            valid_records=valid_records,
            cfg=cfg,
            base_model=base_model,
            adapter_dir=adapter_dir,
            metrics_path=metrics_path,
        )
    else:
        result = render_mock_adapter(adapter_dir=adapter_dir, base_model=base_model, cfg=cfg, result_path=result_path)
    save_json(result_path, result)

    return {
        'stage_name': stage_name,
        'candidate_id': stage_candidate_id,
        'config': cfg,
        'config_output_path': str(config_output_path),
        'manifest_path': str(manifest_path),
        'result_path': str(result_path),
        'metrics_path': str(metrics_path),
        'adapter_dir': str(adapter_dir),
        'result': result,
    }


def load_adapter_tensors(adapter_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    from safetensors.numpy import load_file

    config_path = require_existing_path(adapter_dir / 'adapter_config.json', label='adapter config')
    tensors_path = require_existing_path(adapter_dir / 'adapters.safetensors', label='adapter safetensors')
    config = json.loads(config_path.read_text(encoding='utf-8'))
    tensors = load_file(str(tensors_path))
    return config, tensors


def merge_adapters(
    *,
    generalist_adapter_dir: Path,
    specialist_adapter_dir: Path,
    output_adapter_dir: Path,
    generalist_candidate_id: str,
    specialist_candidate_id: str,
    generalist_weight: float,
    specialist_weight: float,
) -> dict[str, Any]:
    import numpy as np
    from safetensors.numpy import save_file

    generalist_config, generalist_tensors = load_adapter_tensors(generalist_adapter_dir)
    _, specialist_tensors = load_adapter_tensors(specialist_adapter_dir)

    merged_tensors: dict[str, Any] = {}
    for key, tensor in generalist_tensors.items():
        specialist_value = specialist_tensors.get(key)
        if specialist_value is None:
            merged_tensors[key] = tensor
            continue
        merged_value = generalist_weight * tensor.astype(np.float32) + specialist_weight * specialist_value.astype(np.float32)
        merged_tensors[key] = merged_value.astype(tensor.dtype)
    for key, tensor in specialist_tensors.items():
        if key not in merged_tensors:
            merged_tensors[key] = tensor

    output_adapter_dir.mkdir(parents=True, exist_ok=True)
    save_file(merged_tensors, str(output_adapter_dir / 'adapters.safetensors'))
    merged_config = dict(generalist_config)
    merged_config['merge_sources'] = [generalist_candidate_id, specialist_candidate_id]
    merged_config['merge_weights'] = {'generalist': generalist_weight, 'specialist': specialist_weight}
    save_json(output_adapter_dir / 'adapter_config.json', merged_config)
    return {
        'adapter_dir': str(output_adapter_dir),
        'adapter_config_path': str(output_adapter_dir / 'adapter_config.json'),
        'generalist_weight': generalist_weight,
        'specialist_weight': specialist_weight,
        'merge_sources': [generalist_candidate_id, specialist_candidate_id],
        'rank': int(merged_config.get('r', merged_config.get('lora_parameters', {}).get('rank', 32))),
    }


def run_pipeline(args: argparse.Namespace) -> None:
    import pandas as pd

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_id = normalize_optional_text(args.candidate_id) or 'v5_official_first_best_97_03_minimal_run1'
    generalist_candidate_id = f'{candidate_id}_generalist'
    specialist_candidate_id = f'{candidate_id}_specialist'

    pack_output_path = Path(args.pack_output_path) if args.pack_output_path else output_dir / f'{candidate_id}_train_pack.parquet'
    pack_summary_path = output_dir / f'{candidate_id}_pack_summary.json'
    pipeline_manifest_path = output_dir / f'{candidate_id}_pipeline_manifest.json'
    pipeline_result_path = output_dir / f'{candidate_id}_pipeline_result.json'
    final_adapter_dir = output_dir / f'adapter_{candidate_id}'

    base_model = resolve_base_model(args.base_model)
    prompt_instruction = resolve_prompt_instruction(None)
    pack_summary = build_notebook_pack(
        input_path=args.input_path,
        output_path=pack_output_path,
        base_model=base_model,
        prompt_instruction=prompt_instruction,
        subsample_size=int(args.subsample_size),
        subsample_seed=int(args.subsample_seed),
    )
    save_json(pack_summary_path, pack_summary)

    train_pack_df = pd.read_parquet(pack_output_path)
    split_seed = int(GENERALIST_CONFIG.get('seed', 42))
    train_df, valid_df, split_strategy = split_training_frame(
        train_pack_df,
        valid_fraction=float(args.valid_fraction),
        seed=split_seed,
    )
    train_df = maybe_limit_rows(train_df, max_rows=args.max_train_rows, seed=split_seed)
    valid_df = maybe_limit_rows(valid_df, max_rows=args.max_valid_rows, seed=split_seed)
    train_records, skipped_train = build_training_records(train_df)
    valid_records, skipped_valid = build_training_records(valid_df)
    skipped_rows = skipped_train + skipped_valid

    generalist_stage = run_training_stage(
        stage_name='generalist',
        stage_candidate_id=generalist_candidate_id,
        stage_cfg_template=GENERALIST_CONFIG,
        base_model=base_model,
        prompt_instruction=prompt_instruction,
        pack_output_path=pack_output_path,
        train_records=train_records,
        valid_records=valid_records,
        split_strategy=split_strategy,
        skipped_rows=skipped_rows,
        output_dir=output_dir,
        execute=bool(args.execute),
    )
    specialist_stage = run_training_stage(
        stage_name='specialist',
        stage_candidate_id=specialist_candidate_id,
        stage_cfg_template=SPECIALIST_CONFIG,
        base_model=base_model,
        prompt_instruction=prompt_instruction,
        pack_output_path=pack_output_path,
        train_records=train_records,
        valid_records=valid_records,
        split_strategy=split_strategy,
        skipped_rows=skipped_rows,
        output_dir=output_dir,
        execute=bool(args.execute),
    )

    merge_summary = merge_adapters(
        generalist_adapter_dir=Path(generalist_stage['adapter_dir']),
        specialist_adapter_dir=Path(specialist_stage['adapter_dir']),
        output_adapter_dir=final_adapter_dir,
        generalist_candidate_id=generalist_candidate_id,
        specialist_candidate_id=specialist_candidate_id,
        generalist_weight=float(args.generalist_weight),
        specialist_weight=float(args.specialist_weight),
    )

    pipeline_manifest = {
        'version': 'v4',
        'created_at': utc_now(),
        'candidate_id': candidate_id,
        'parent_candidate_id': generalist_candidate_id,
        'recipe_type': 'official_first_best_pipeline',
        'config_name': OFFICIAL_FIRST_BEST_CONFIG_NAME,
        'notes': OFFICIAL_FIRST_BEST_NOTES,
        'model': {'base_model': base_model},
        'data': {
            'train_pack_path': str(pack_output_path),
            'train_records': len(train_records),
            'valid_records': len(valid_records),
            'split_strategy': split_strategy,
            'skipped_rows': skipped_rows,
            'prompt_instruction': prompt_instruction,
        },
        'stages': {
            'generalist': {
                'candidate_id': generalist_stage['candidate_id'],
                'manifest_path': generalist_stage['manifest_path'],
                'result_path': generalist_stage['result_path'],
                'adapter_dir': generalist_stage['adapter_dir'],
                'config_output_path': generalist_stage['config_output_path'],
                'training': {
                    'learning_rate': float(generalist_stage['config']['learning_rate']),
                    'num_epochs': float(generalist_stage['config']['num_epochs']),
                    'iters': int(generalist_stage['config']['iters']),
                },
            },
            'specialist': {
                'candidate_id': specialist_stage['candidate_id'],
                'manifest_path': specialist_stage['manifest_path'],
                'result_path': specialist_stage['result_path'],
                'adapter_dir': specialist_stage['adapter_dir'],
                'config_output_path': specialist_stage['config_output_path'],
                'training': {
                    'learning_rate': float(specialist_stage['config']['learning_rate']),
                    'num_epochs': float(specialist_stage['config']['num_epochs']),
                    'iters': int(specialist_stage['config']['iters']),
                },
            },
        },
        'merge': merge_summary,
        'readme_eval_contract': README_EVAL_CONTRACT,
    }
    save_json(pipeline_manifest_path, pipeline_manifest)

    pipeline_result = {
        'status': 'completed' if args.execute else 'rendered_only',
        'created_at': utc_now(),
        'candidate_id': candidate_id,
        'pack_summary_path': str(pack_summary_path),
        'generalist': generalist_stage['result'],
        'specialist': specialist_stage['result'],
        'merge': merge_summary,
        'readme_eval_contract': README_EVAL_CONTRACT,
        'next_step': (
            'Score the merged adapter with the README-faithful official_lb settings, '
            'because this pipeline was chosen against the Kaggle evaluation contract in README.md.'
        ),
    }
    save_json(pipeline_result_path, pipeline_result)

    print(
        json.dumps(
            {
                'candidate_id': candidate_id,
                'pack_summary': pack_summary,
                'pipeline_manifest_path': str(pipeline_manifest_path),
                'pipeline_result_path': str(pipeline_result_path),
                'final_adapter_dir': str(final_adapter_dir),
                'generalist_manifest_path': generalist_stage['manifest_path'],
                'specialist_manifest_path': specialist_stage['manifest_path'],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            'Minimal standalone trainer for the current README-faithful official-first BF16 best pipeline '
            '(official-long lowlr generalist + official-long ultralowlr specialist + 97/3 merge).'
        )
    )
    parser.add_argument(
        '--output-dir',
        default=str(VERSION_ROOT / 'outputs' / 'train' / 'official_first_best_minimal_run1'),
        help='Output directory for stage manifests, metrics, configs, and final merged adapter artifacts.',
    )
    parser.add_argument('--candidate-id', default='v5_official_first_best_97_03_minimal_run1')
    parser.add_argument('--input-path', default=str(DEFAULT_TRAIN_CSV_PATH))
    parser.add_argument('--pack-output-path')
    parser.add_argument('--base-model', default='model')
    parser.add_argument('--subsample-size', type=int, default=0)
    parser.add_argument('--subsample-seed', type=int, default=42)
    parser.add_argument('--valid-fraction', type=float, default=0.0)
    parser.add_argument('--max-train-rows', type=int)
    parser.add_argument('--max-valid-rows', type=int)
    parser.add_argument('--generalist-weight', type=float, default=DEFAULT_GENERALIST_WEIGHT)
    parser.add_argument('--specialist-weight', type=float, default=DEFAULT_SPECIALIST_WEIGHT)
    parser.add_argument('--execute', action='store_true', help='Run actual MLX BF16 LoRA training for both SFT stages and then merge them.')
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    run_pipeline(args)


if __name__ == '__main__':
    main()
