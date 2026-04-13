#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import threading
from typing import Any, Literal, Protocol, Sequence
import warnings

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, StratifiedKFold
import yaml


SCRIPT_PATH = Path(__file__).resolve()
VERSION_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
RAW_TRAIN_PATH = REPO_ROOT / 'data' / 'train.csv'
RAW_TEST_PATH = REPO_ROOT / 'data' / 'test.csv'

CONF_ROOT = VERSION_ROOT / 'conf'
EVAL_CONF_ROOT = CONF_ROOT / 'eval'
DATA_ROOT = VERSION_ROOT / 'data'
PROCESSED_DIR = DATA_ROOT / 'processed'
EVAL_PACKS_DIR = DATA_ROOT / 'eval_packs'
OUTPUT_ROOT = VERSION_ROOT / 'outputs'
OUTPUT_EVAL_DIR = OUTPUT_ROOT / 'eval'
OUTPUT_REPORTS_DIR = OUTPUT_ROOT / 'reports'
OUTPUT_AUDITS_DIR = OUTPUT_ROOT / 'audits'
TESTS_DIR = VERSION_ROOT / 'tests'
README_PATH = REPO_ROOT / 'README.md'
README_TABLE_KEYS = (
    'max_lora_rank',
    'max_tokens',
    'top_p',
    'temperature',
    'max_num_seqs',
    'gpu_memory_utilization',
    'max_model_len',
)
README_TABLE_VALUE_TYPES = {
    'max_lora_rank': int,
    'max_tokens': int,
    'top_p': float,
    'temperature': float,
    'max_num_seqs': int,
    'gpu_memory_utilization': float,
    'max_model_len': int,
}

OFFICIAL_BOXED_INSTRUCTION = (
    r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
)

BOXED_PATTERN = re.compile(r"\\boxed\{([^}]*)(?:\}|$)")
NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
ROMAN_PATTERN = re.compile(r"^[IVXLCDM]+$", re.IGNORECASE)
FINAL_ANSWER_IS_PATTERN = re.compile(r"(?:The\s+)?Final answer is:\s*([^\n]+)", re.IGNORECASE)
FINAL_ANSWER_COLON_PATTERN = re.compile(r"Final answer\s*[:：]\s*([^\n]+)", re.IGNORECASE)
SUBTRACTIVE_VALUES = {4, 9, 14, 19, 24, 29, 34, 39, 40, 41, 44, 49, 54, 59, 64, 69, 74, 79, 84, 89, 90, 91, 94, 99}

FAMILY_ALIASES = {
    'bit': 'bit_manipulation',
    'bit_manipulation': 'bit_manipulation',
    'gravity': 'gravity_constant',
    'gravity_constant': 'gravity_constant',
    'unit': 'unit_conversion',
    'unit_conversion': 'unit_conversion',
    'text_decrypt': 'text_decryption',
    'text_decryption': 'text_decryption',
    'roman': 'roman_numeral',
    'roman_numeral': 'roman_numeral',
    'symbol_equation': 'symbol_equation',
}

ANSWER_TYPE_ALIASES = {
    'numeric': 'numeric',
    'binary8': 'binary8',
    'roman': 'roman',
    'text_phrase': 'text_phrase',
    'word': 'text_phrase',
    'symbolic': 'symbolic',
}

CLEAN_FORMAT_BUCKETS = {'clean_boxed', 'clean_final_answer'}
RISKY_TEXT_MARKERS = ('}', '{', '\\', '`', '\n', '\r')

ExtractionSource = Literal[
    'boxed',
    'final_answer_is',
    'final_answer_colon',
    'last_number',
    'last_line',
    'not_found',
]

FormatBucket = Literal[
    'clean_boxed',
    'clean_final_answer',
    'boxed_multiple',
    'boxed_empty',
    'boxed_unclosed',
    'boxed_truncated_right_brace',
    'extra_trailing_numbers',
    'last_number_fallback',
    'last_line_fallback',
    'not_found',
]

Family = Literal[
    'bit_manipulation',
    'gravity_constant',
    'unit_conversion',
    'text_decryption',
    'roman_numeral',
    'symbol_equation',
]

AnswerType = Literal[
    'numeric',
    'binary8',
    'roman',
    'text_phrase',
    'symbolic',
]


@dataclass(frozen=True)
class EvalConfig:
    name: str
    max_lora_rank: int
    max_tokens: int
    top_p: float
    temperature: float
    max_num_seqs: int
    gpu_memory_utilization: float
    max_model_len: int
    enable_thinking: bool
    add_generation_prompt: bool
    boxed_instruction: str
    strict_chat_template: bool = True
    n_samples_per_prompt: int = 1
    seed: int = 0
    seed_stride: int = 1
    seed_list: list[int] | None = None


@dataclass(frozen=True)
class PromptRecord:
    id: str
    prompt: str
    answer: str | None = None
    family: Family | None = None
    answer_type: AnswerType | None = None


@dataclass(frozen=True)
class GenerationRecord:
    id: str
    sample_idx: int
    seed: int
    raw_output: str
    raw_output_len_chars: int
    raw_output_num_lines: int
    raw_output_est_tokens: int


@dataclass(frozen=True)
class EvalRow:
    run_name: str
    dataset_name: str
    id: str
    sample_idx: int
    seed: int
    family: str
    answer_type: str
    gold_answer: str
    raw_output: str
    extracted_answer: str
    extraction_source: ExtractionSource
    format_bucket: FormatBucket
    has_boxed: bool
    boxed_count: int
    contains_extra_numbers: bool
    contains_risky_chars: bool
    is_correct: bool
    rendered_prompt_hash: str
    eval_mode: str
    backend_name: str
    raw_output_len_chars: int
    raw_output_num_lines: int
    raw_output_est_tokens: int


@dataclass(frozen=True)
class EvaluationArtifacts:
    row_level: pd.DataFrame
    summary: pd.DataFrame
    family_metrics: pd.DataFrame
    failure_metrics: pd.DataFrame
    out_dir: Path


class GenerationBackend(Protocol):
    backend_name: str

    def generate(
        self,
        rendered_prompts: Sequence[str],
        *,
        max_tokens: int,
        top_p: float,
        temperature: float,
        max_model_len: int,
        seeds: Sequence[int],
        max_num_seqs: int = 1,
    ) -> list[list[GenerationRecord]]:
        ...


class BuiltinCompetitionTokenizer:
    name_or_path = 'builtin-competition-tokenizer'
    revision = 'builtin-fallback-v1'

    def apply_chat_template(
        self,
        messages: list[dict[str, str]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
        enable_thinking: bool,
    ) -> str:
        if tokenize:
            raise ValueError('BuiltinCompetitionTokenizer only supports tokenize=False.')

        rendered: list[str] = []
        for message in messages:
            rendered.append(f"<|{message['role']}|>\n{message['content']}")

        if add_generation_prompt:
            assistant_header = '<|assistant|>'
            if enable_thinking:
                assistant_header += '\n<think>'
            rendered.append(assistant_header)

        return '\n'.join(rendered)


class ReplayBackend:
    backend_name = 'replay'

    def __init__(self, replay_source: pd.DataFrame | Path):
        if isinstance(replay_source, Path):
            self.replay_frame = load_table(replay_source)
        else:
            self.replay_frame = replay_source.copy()
        self.replay_frame = validate_and_prepare_replay_frame(self.replay_frame)

    def generate(
        self,
        rendered_prompts: Sequence[str],
        *,
        max_tokens: int,
        top_p: float,
        temperature: float,
        max_model_len: int,
        seeds: Sequence[int],
        max_num_seqs: int = 1,
    ) -> list[list[GenerationRecord]]:
        del max_tokens, top_p, temperature, max_model_len, max_num_seqs

        expected_prompt_indices = list(range(len(rendered_prompts)))
        actual_prompt_indices = self.replay_frame['prompt_index'].drop_duplicates().tolist()
        if actual_prompt_indices != expected_prompt_indices:
            raise ValueError(
                'Replay backend prompt_index set does not match rendered prompt count: '
                f'expected {expected_prompt_indices}, got {actual_prompt_indices}'
            )

        expected_seeds = [int(seed) for seed in seeds]
        outputs: list[list[GenerationRecord]] = []
        for prompt_index in expected_prompt_indices:
            prompt_rows = (
                self.replay_frame.loc[self.replay_frame['prompt_index'] == prompt_index]
                .sort_values(['sample_idx', 'seed'])
                .reset_index(drop=True)
            )
            actual_seeds = prompt_rows['seed'].astype(int).tolist()
            if actual_seeds != expected_seeds:
                raise ValueError(
                    f'Replay backend seeds for prompt_index={prompt_index} do not match: '
                    f'expected {expected_seeds}, got {actual_seeds}'
                )
            outputs.append(
                [
                    GenerationRecord(
                        id=str(row.id),
                        sample_idx=int(row.sample_idx),
                        seed=int(row.seed),
                        raw_output=str(row.raw_output),
                        raw_output_len_chars=int(row.raw_output_len_chars),
                        raw_output_num_lines=int(row.raw_output_num_lines),
                        raw_output_est_tokens=int(row.raw_output_est_tokens),
                    )
                    for row in prompt_rows.itertuples(index=False)
                ]
            )
        return outputs


def make_generation_record(*, prompt_id: str, sample_idx: int, seed: int, raw_output: str) -> GenerationRecord:
    return GenerationRecord(
        id=str(prompt_id),
        sample_idx=int(sample_idx),
        seed=int(seed),
        raw_output=str(raw_output),
        raw_output_len_chars=len(str(raw_output)),
        raw_output_num_lines=raw_output_num_lines(raw_output),
        raw_output_est_tokens=estimate_output_token_count(raw_output),
    )


class MLXBackend:
    backend_name = 'mlx'
    _MODEL_CACHE: dict[tuple[str, str, bool], tuple[Any, Any]] = {}

    def __init__(
        self,
        *,
        model_path: str,
        adapter_path: str | None = None,
        trust_remote_code: bool = False,
    ):
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.trust_remote_code = trust_remote_code

    def _require_mlx_runtime(self) -> tuple[Any, Any, Any, Any, Any]:
        if not importlib.util.find_spec('mlx_lm'):
            raise RuntimeError(
                'MLXBackend requires mlx-lm, which is not installed in this environment. '
                'Install `mlx-lm` and provide a local MLX-compatible model path to use backend=mlx.'
            )

        import mlx.core as mx  # type: ignore
        from mlx_lm import batch_generate as mlx_batch_generate, generate as mlx_generate, load as mlx_load  # type: ignore
        from mlx_lm.generate import BatchGenerator  # type: ignore
        from mlx_lm.sample_utils import make_sampler as mlx_make_sampler  # type: ignore

        # mlx_lm.batch_generate() can finish generation successfully and then crash while
        # computing throughput stats if the measured elapsed time is zero. Keep evaluation
        # running by clamping those derived TPS fields instead of raising ZeroDivisionError.
        if not getattr(BatchGenerator.stats, '_copilot_zero_time_safe', False):
            def _safe_batch_generator_stats(self: Any) -> Any:
                stats = self._stats
                prompt_time = float(getattr(stats, 'prompt_time', 0.0) or 0.0)
                generation_time = float(getattr(stats, 'generation_time', 0.0) or 0.0)
                stats.prompt_tps = (
                    float(getattr(stats, 'prompt_tokens', 0) or 0) / prompt_time if prompt_time > 0.0 else 0.0
                )
                stats.generation_tps = (
                    float(getattr(stats, 'generation_tokens', 0) or 0) / generation_time
                    if generation_time > 0.0
                    else 0.0
                )
                stats.peak_memory = mx.get_peak_memory() / 1e9
                return stats

            setattr(_safe_batch_generator_stats, '_copilot_zero_time_safe', True)
            BatchGenerator.stats = _safe_batch_generator_stats

        return mx, mlx_load, mlx_generate, mlx_batch_generate, mlx_make_sampler

    def _load_model_and_tokenizer(self) -> tuple[Any, Any]:
        _, mlx_load, _, _, _ = self._require_mlx_runtime()
        cache_key = (self.model_path, self.adapter_path or '', self.trust_remote_code)
        cached = self._MODEL_CACHE.get(cache_key)
        if cached is None:
            tokenizer_config = {'trust_remote_code': True} if self.trust_remote_code else None
            cached = mlx_load(
                self.model_path,
                adapter_path=self.adapter_path,
                tokenizer_config=tokenizer_config,
            )
            self._MODEL_CACHE[cache_key] = cached
        return cached

    @staticmethod
    def _encode_prompt(tokenizer: Any, prompt: str) -> list[int]:
        bos_token = getattr(tokenizer, 'bos_token', None)
        add_special_tokens = bos_token is None or not prompt.startswith(str(bos_token))
        encoded = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
        return list(encoded)

    @staticmethod
    def _resolve_positive_env(name: str, default: int) -> int:
        raw = os.environ.get(name)
        if raw is None or raw == '':
            return max(1, int(default))
        value = int(raw)
        if value < 1:
            raise ValueError(f'{name} must be >= 1, got {value}.')
        return value

    def _resolve_batch_settings(self, *, max_num_seqs: int) -> tuple[int, int, int]:
        prompt_chunk_size = self._resolve_positive_env('MLX_EVAL_PROMPT_CHUNK_SIZE', max(1, int(max_num_seqs)))
        completion_batch_size = self._resolve_positive_env(
            'MLX_EVAL_COMPLETION_BATCH_SIZE',
            max(1, min(int(max_num_seqs), 16)),
        )
        prefill_batch_size = self._resolve_positive_env(
            'MLX_EVAL_PREFILL_BATCH_SIZE',
            max(1, min(completion_batch_size, 16)),
        )
        completion_batch_size = min(completion_batch_size, prompt_chunk_size)
        prefill_batch_size = min(prefill_batch_size, completion_batch_size)
        return prompt_chunk_size, prefill_batch_size, completion_batch_size

    @staticmethod
    def _resolve_nonnegative_float_env(name: str, default: float) -> float:
        raw = os.environ.get(name)
        if raw is None or raw == '':
            return max(0.0, float(default))
        value = float(raw)
        if value < 0:
            raise ValueError(f'{name} must be >= 0, got {value}.')
        return value

    def _generate_batched_greedy(
        self,
        rendered_prompts: Sequence[str],
        *,
        max_tokens: int,
        top_p: float,
        temperature: float,
        seeds: Sequence[int],
        max_num_seqs: int,
    ) -> list[list[GenerationRecord]]:
        mx, _, _, mlx_batch_generate, mlx_make_sampler = self._require_mlx_runtime()
        model, tokenizer = self._load_model_and_tokenizer()
        prompt_tokens = [self._encode_prompt(tokenizer, prompt) for prompt in rendered_prompts]
        prompt_chunk_size, prefill_batch_size, completion_batch_size = self._resolve_batch_settings(
            max_num_seqs=max_num_seqs
        )
        sampler = mlx_make_sampler(temp=temperature, top_p=top_p)
        outputs: list[list[GenerationRecord]] = [[] for _ in rendered_prompts]
        total_prompts = len(prompt_tokens)
        total_chunks = max(1, math.ceil(total_prompts / prompt_chunk_size))
        run_started_at = time.perf_counter()
        heartbeat_sec = self._resolve_nonnegative_float_env('MLX_EVAL_HEARTBEAT_SEC', 60.0)
        for sample_idx, seed in enumerate(seeds):
            mx.random.seed(int(seed))
            for chunk_start in range(0, len(prompt_tokens), prompt_chunk_size):
                chunk_prompts = prompt_tokens[chunk_start : chunk_start + prompt_chunk_size]
                chunk_index = (chunk_start // prompt_chunk_size) + 1
                chunk_started_at = time.perf_counter()
                chunk_end = chunk_start + len(chunk_prompts)
                print(
                    '[MLXBackend] '
                    f'seed={int(seed)} '
                    f'chunk={chunk_index}/{total_chunks} '
                    f'prompts={chunk_start + 1}-{chunk_end}/{total_prompts} '
                    'status=started',
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
                                '[MLXBackend] '
                                f'seed={int(seed)} '
                                f'chunk={chunk_index}/{total_chunks} '
                                f'prompts={chunk_start + 1}-{chunk_end}/{total_prompts} '
                                'status=running '
                                f'chunk_elapsed_sec={chunk_elapsed:.1f} '
                                f'total_elapsed_sec={total_elapsed:.1f}',
                                flush=True,
                            )
                    heartbeat_thread = threading.Thread(target=emit_heartbeat, daemon=True)
                    heartbeat_thread.start()
                try:
                    batch_response = mlx_batch_generate(
                        model,
                        tokenizer,
                        chunk_prompts,
                        max_tokens=max_tokens,
                        sampler=sampler,
                        verbose=False,
                        prefill_batch_size=min(prefill_batch_size, len(chunk_prompts)),
                        completion_batch_size=min(completion_batch_size, len(chunk_prompts)),
                    )
                finally:
                    if heartbeat_thread is not None:
                        heartbeat_stop.set()
                        heartbeat_thread.join()
                for offset, raw_output in enumerate(batch_response.texts):
                    prompt_index = chunk_start + offset
                    outputs[prompt_index].append(
                        make_generation_record(
                            prompt_id=f'prompt-{prompt_index}',
                            sample_idx=sample_idx,
                            seed=int(seed),
                            raw_output=raw_output,
                        )
                    )
                chunk_elapsed = time.perf_counter() - chunk_started_at
                total_elapsed = time.perf_counter() - run_started_at
                stats = getattr(batch_response, 'stats', None)
                stats_suffix = ''
                if stats is not None:
                    stats_suffix = (
                        f", prompt_tps={getattr(stats, 'prompt_tps', 0):.2f}, "
                        f"generation_tps={getattr(stats, 'generation_tps', 0):.2f}, "
                        f"peak_memory_gb={getattr(stats, 'peak_memory', 0):.2f}"
                    )
                print(
                    '[MLXBackend] '
                    f'seed={int(seed)} '
                    f'chunk={chunk_index}/{total_chunks} '
                    f'prompts={chunk_start + 1}-{chunk_end}/{total_prompts} '
                    'status=completed '
                    f'chunk_elapsed_sec={chunk_elapsed:.1f} '
                    f'total_elapsed_sec={total_elapsed:.1f}'
                    f'{stats_suffix}',
                    flush=True,
                )
                mx.clear_cache()
        return outputs

    def _generate_in_process_sequential(
        self,
        rendered_prompts: Sequence[str],
        *,
        max_tokens: int,
        top_p: float,
        temperature: float,
        seeds: Sequence[int],
    ) -> list[list[GenerationRecord]]:
        mx, _, mlx_generate, _, mlx_make_sampler = self._require_mlx_runtime()
        model, tokenizer = self._load_model_and_tokenizer()
        sampler = mlx_make_sampler(temp=temperature, top_p=top_p)
        outputs: list[list[GenerationRecord]] = []
        for prompt_index, prompt in enumerate(rendered_prompts):
            encoded_prompt = self._encode_prompt(tokenizer, prompt)
            prompt_outputs: list[GenerationRecord] = []
            for sample_idx, seed in enumerate(seeds):
                mx.random.seed(int(seed))
                raw_output = mlx_generate(
                    model,
                    tokenizer,
                    encoded_prompt,
                    verbose=False,
                    max_tokens=max_tokens,
                    sampler=sampler,
                )
                prompt_outputs.append(
                    make_generation_record(
                        prompt_id=f'prompt-{prompt_index}',
                        sample_idx=sample_idx,
                        seed=int(seed),
                        raw_output=raw_output,
                    )
                )
            outputs.append(prompt_outputs)
            mx.clear_cache()
        return outputs

    def generate(
        self,
        rendered_prompts: Sequence[str],
        *,
        max_tokens: int,
        top_p: float,
        temperature: float,
        max_model_len: int,
        seeds: Sequence[int],
        max_num_seqs: int = 1,
    ) -> list[list[GenerationRecord]]:
        del max_model_len
        if temperature == 0.0:
            return self._generate_batched_greedy(
                rendered_prompts,
                max_tokens=max_tokens,
                top_p=top_p,
                temperature=temperature,
                seeds=seeds,
                max_num_seqs=max_num_seqs,
            )
        return self._generate_in_process_sequential(
            rendered_prompts,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            seeds=seeds,
        )


class HFBackend:
    backend_name = 'hf'

    def __init__(
        self,
        *,
        model_path: str,
        adapter_path: str | None = None,
        trust_remote_code: bool = False,
    ):
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.trust_remote_code = trust_remote_code

    def generate(
        self,
        rendered_prompts: Sequence[str],
        *,
        max_tokens: int,
        top_p: float,
        temperature: float,
        max_model_len: int,
        seeds: Sequence[int],
        max_num_seqs: int = 1,
    ) -> list[list[GenerationRecord]]:
        del max_model_len, max_num_seqs
        try:
            import torch  # type: ignore
            from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional runtime path
            raise RuntimeError(
                'HFBackend requires transformers and torch, which are not installed in this environment.'
            ) from exc

        tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=self.trust_remote_code)
        model = AutoModelForCausalLM.from_pretrained(self.model_path, trust_remote_code=self.trust_remote_code)

        if self.adapter_path:
            try:
                from peft import PeftModel  # type: ignore
            except ImportError as exc:  # pragma: no cover - optional runtime path
                raise RuntimeError('HFBackend requires peft when --adapter-path is provided.') from exc
            model = PeftModel.from_pretrained(model, self.adapter_path)

        model.eval()
        outputs: list[list[GenerationRecord]] = []
        for prompt_index, prompt in enumerate(rendered_prompts):
            prompt_outputs: list[GenerationRecord] = []
            for sample_idx, seed in enumerate(seeds):
                set_seed(seed)
                inputs = tokenizer(prompt, return_tensors='pt')
                with torch.no_grad():
                    generated = model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=temperature > 0.0,
                        temperature=max(temperature, 1e-6),
                        top_p=top_p,
                    )
                generated_tokens = generated[0][inputs['input_ids'].shape[-1] :]
                raw_output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
                prompt_outputs.append(
                    make_generation_record(
                        prompt_id=f'prompt-{prompt_index}',
                        sample_idx=sample_idx,
                        seed=seed,
                        raw_output=raw_output,
                    )
                )
            outputs.append(prompt_outputs)
        return outputs


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def ensure_version_directories() -> None:
    for path in (
        CONF_ROOT,
        EVAL_CONF_ROOT,
        PROCESSED_DIR,
        EVAL_PACKS_DIR,
        OUTPUT_EVAL_DIR,
        OUTPUT_REPORTS_DIR,
        OUTPUT_AUDITS_DIR,
        TESTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def normalize_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ''
    return str(value)


def ensure_dataframe_columns(frame: pd.DataFrame, required_columns: Sequence[str], *, label: str) -> None:
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f'{label} is missing required columns: {missing}')


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix == '.csv':
        return pd.read_csv(path)
    if path.suffix == '.parquet':
        return pd.read_parquet(path)
    raise ValueError(f'Unsupported table format: {path}')


def save_table(frame: pd.DataFrame, path: Path) -> None:
    ensure_parent(path)
    if path.suffix == '.csv':
        frame.to_csv(path, index=False)
        return
    if path.suffix == '.parquet':
        frame.to_parquet(path, index=False)
        return
    raise ValueError(f'Unsupported table format: {path}')


def load_readme_eval_contract() -> dict[str, int | float]:
    text = README_PATH.read_text(encoding='utf-8')
    contract: dict[str, int | float] = {}
    for key in README_TABLE_KEYS:
        value_type = README_TABLE_VALUE_TYPES[key]
        needle = f'{key}\t'
        for line in text.splitlines():
            if not line.startswith(needle):
                continue
            raw_value = line.split('\t', 1)[1].strip()
            if raw_value == '':
                raise SystemExit(f'Malformed README.md evaluation row for {key}: missing value')
            try:
                contract[key] = value_type(raw_value)
            except ValueError as exc:
                raise SystemExit(f'Malformed README.md evaluation value for {key}: {raw_value!r}') from exc
            break
    missing_keys = [key for key in README_TABLE_KEYS if key not in contract]
    if missing_keys:
        raise SystemExit(f"Missing README.md evaluation rows: {', '.join(missing_keys)}")
    return contract


def verify_official_eval_config_against_readme(eval_config: EvalConfig) -> None:
    contract = load_readme_eval_contract()
    for key in README_TABLE_KEYS:
        expected_value = contract[key]
        actual_value = getattr(eval_config, key)
        if actual_value != expected_value:
            raise SystemExit(
                f'README.md evaluation table mismatch for official_lb.{key}: expected {expected_value}, got {actual_value}'
            )


def load_eval_config(name_or_path: str) -> EvalConfig:
    config_path = Path(name_or_path)
    if not config_path.exists():
        config_path = EVAL_CONF_ROOT / f'{name_or_path}.yaml'
    if not config_path.exists():
        raise FileNotFoundError(f'Evaluation config was not found: {name_or_path}')
    data = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    eval_config = EvalConfig(**data)
    if eval_config.name == 'official_lb':
        verify_official_eval_config_against_readme(eval_config)
    return eval_config


def resolve_mlx_eval_num_shards() -> int:
    raw = os.environ.get('MLX_EVAL_NUM_SHARDS')
    if raw is None or raw == '':
        return 1
    value = int(raw)
    if value < 1:
        raise ValueError(f'MLX_EVAL_NUM_SHARDS must be >= 1, got {value}.')
    return value


def tail_text(path: Path, *, max_chars: int = 4000) -> str:
    if not path.exists():
        return ''
    text = path.read_text(encoding='utf-8', errors='replace')
    return text[-max_chars:]


def resolve_seeds(eval_config: EvalConfig) -> list[int]:
    if eval_config.n_samples_per_prompt < 1:
        raise ValueError('n_samples_per_prompt must be >= 1.')
    if eval_config.seed_list is not None:
        seeds = [int(seed) for seed in eval_config.seed_list]
        if len(seeds) != eval_config.n_samples_per_prompt:
            raise ValueError(
                'seed_list length must match n_samples_per_prompt: '
                f'{len(seeds)} != {eval_config.n_samples_per_prompt}'
            )
        return seeds
    return [eval_config.seed + (index * eval_config.seed_stride) for index in range(eval_config.n_samples_per_prompt)]


def build_user_content(raw_prompt: str, boxed_instruction: str) -> str:
    return raw_prompt + '\n' + boxed_instruction


def apply_competition_chat_template(
    tokenizer: Any,
    user_content: str,
    *,
    enable_thinking: bool,
    add_generation_prompt: bool,
    strict_chat_template: bool = True,
) -> str:
    try:
        return tokenizer.apply_chat_template(
            [{'role': 'user', 'content': user_content}],
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=enable_thinking,
        )
    except (AttributeError, RuntimeError, TypeError, ValueError) as exc:
        if strict_chat_template:
            raise
        warnings.warn(
            f'Chat template fallback triggered: {exc}',
            RuntimeWarning,
            stacklevel=2,
        )
        return user_content


def build_competition_prompt(tokenizer: Any, raw_prompt: str, eval_config: EvalConfig) -> str:
    user_content = build_user_content(raw_prompt, eval_config.boxed_instruction)
    return apply_competition_chat_template(
        tokenizer,
        user_content,
        enable_thinking=eval_config.enable_thinking,
        add_generation_prompt=eval_config.add_generation_prompt,
        strict_chat_template=eval_config.strict_chat_template,
    )


def infer_family(prompt: str) -> Family:
    prompt_lower = prompt.lower()
    if any(token in prompt_lower for token in ('roman numeral', 'roman numerals', 'numeral system', 'write the number')):
        return 'roman_numeral'
    if any(token in prompt_lower for token in ('gravitational constant', 'distance fallen', 'falling distance', 'd = 0.5', 'fall')):
        return 'gravity_constant'
    if 'bit manipulation' in prompt_lower or '8-bit' in prompt_lower or len(re.findall(r'\b[01]{8}\b', prompt)) >= 4:
        return 'bit_manipulation'
    if any(token in prompt_lower for token in ('decrypt', 'decode', 'cipher', 'encoded text')):
        return 'text_decryption'
    if any(token in prompt_lower for token in ('unit conversion', 'measurements', 'convert the following measurement', 'conversion', 'units')):
        return 'unit_conversion'
    return 'symbol_equation'


def normalize_family(value: Any, prompt: str) -> Family:
    text = normalize_text(value).strip().lower()
    if text:
        normalized = FAMILY_ALIASES.get(text)
        if normalized is None:
            raise ValueError(f'Unsupported family value: {value}')
        return normalized  # type: ignore[return-value]
    return infer_family(prompt)


def classify_answer_type(answer: Any) -> AnswerType:
    text = normalize_text(answer).strip()
    if re.fullmatch(r'[01]{8}', text):
        return 'binary8'
    if re.fullmatch(r'-?\d+(?:\.\d+)?', text):
        return 'numeric'
    if ROMAN_PATTERN.fullmatch(text):
        return 'roman'
    if re.fullmatch(r'[A-Za-z ]+', text):
        return 'text_phrase'
    return 'symbolic'


def normalize_answer_type(value: Any, answer: Any) -> AnswerType:
    text = normalize_text(value).strip().lower()
    if text:
        normalized = ANSWER_TYPE_ALIASES.get(text)
        if normalized is None:
            raise ValueError(f'Unsupported answer_type value: {value}')
        return normalized  # type: ignore[return-value]
    return classify_answer_type(answer)


def extract_final_answer_with_source(text: str | None) -> tuple[str, ExtractionSource]:
    if text is None:
        return ('NOT_FOUND', 'not_found')

    boxed_matches = BOXED_PATTERN.findall(text)
    if boxed_matches:
        non_empty = [match.strip() for match in boxed_matches if match.strip()]
        if non_empty:
            return (non_empty[-1], 'boxed')
        return (boxed_matches[-1].strip(), 'boxed')

    final_answer_is_matches = FINAL_ANSWER_IS_PATTERN.findall(text)
    if final_answer_is_matches:
        return (final_answer_is_matches[-1].strip(), 'final_answer_is')

    final_answer_colon_matches = FINAL_ANSWER_COLON_PATTERN.findall(text)
    if final_answer_colon_matches:
        return (final_answer_colon_matches[-1].strip(), 'final_answer_colon')

    number_matches = NUMBER_PATTERN.findall(text)
    if number_matches:
        return (number_matches[-1], 'last_number')

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        return (lines[-1], 'last_line')
    return ('NOT_FOUND', 'not_found')


def extract_final_answer(text: str | None) -> str:
    return extract_final_answer_with_source(text)[0]


def verify(stored_answer: str, predicted: str) -> bool:
    stored_answer = stored_answer.strip()
    predicted = predicted.strip()
    try:
        stored_num = float(stored_answer)
        predicted_num = float(predicted)
    except (TypeError, ValueError):
        return predicted.lower() == stored_answer.lower()
    return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)


def estimate_output_token_count(text: str | None) -> int:
    if not text:
        return 0
    return len(re.findall(r'\S+', text))


def raw_output_num_lines(text: str | None) -> int:
    if not text:
        return 0
    return len(text.splitlines()) or 1


def count_boxed_occurrences(text: str | None) -> int:
    if not text:
        return 0
    return len(BOXED_PATTERN.findall(text))


def detect_extra_trailing_numbers(raw_output: str | None, extracted_answer: str) -> bool:
    if not raw_output or not extracted_answer or extracted_answer == 'NOT_FOUND':
        return False
    last_position = raw_output.rfind(extracted_answer)
    if last_position == -1:
        return False
    suffix = raw_output[last_position + len(extracted_answer) :]
    return bool(NUMBER_PATTERN.search(suffix))


def detect_boxed_unclosed(raw_output: str | None) -> bool:
    if not raw_output:
        return False
    last_box_start = raw_output.rfind(r'\boxed{')
    if last_box_start == -1:
        return False
    return raw_output.find('}', last_box_start) == -1


def detect_boxed_truncated_right_brace(raw_output: str | None) -> bool:
    if not raw_output:
        return False
    last_box_start = raw_output.rfind(r'\boxed{')
    if last_box_start == -1:
        return False
    closing_index = raw_output.find('}', last_box_start)
    if closing_index == -1:
        return False
    trailing_segment = raw_output[closing_index + 1 :].splitlines()[0] if raw_output[closing_index + 1 :] else ''
    return '}' in trailing_segment


def classify_format_bucket(
    raw_output: str | None,
    extracted_answer: str,
    extraction_source: ExtractionSource,
) -> FormatBucket:
    if raw_output is None or not str(raw_output).strip():
        return 'not_found'

    boxed_matches = BOXED_PATTERN.findall(raw_output)
    has_only_empty_boxed = bool(boxed_matches) and all(not match.strip() for match in boxed_matches)
    if extraction_source == 'boxed':
        if has_only_empty_boxed or extracted_answer == '':
            return 'boxed_empty'
        if detect_boxed_unclosed(raw_output):
            return 'boxed_unclosed'
        if len(boxed_matches) > 1:
            return 'boxed_multiple'
        if detect_boxed_truncated_right_brace(raw_output):
            return 'boxed_truncated_right_brace'
        if detect_extra_trailing_numbers(raw_output, extracted_answer):
            return 'extra_trailing_numbers'
        return 'clean_boxed'

    if extraction_source in {'final_answer_is', 'final_answer_colon'}:
        if detect_extra_trailing_numbers(raw_output, extracted_answer):
            return 'extra_trailing_numbers'
        return 'clean_final_answer'

    if extraction_source == 'last_number':
        return 'last_number_fallback'
    if extraction_source == 'last_line':
        return 'last_line_fallback'
    return 'not_found'


def analyze_extraction_risk(answer: str | None) -> dict[str, Any]:
    text = '' if answer is None else str(answer)
    contains_right_brace = '}' in text
    contains_backslash = '\\' in text
    contains_newline = '\n' in text or '\r' in text
    contains_backtick = '`' in text
    contains_control_char = any(ord(char) < 32 and char not in '\n\r\t' for char in text)

    reasons: list[str] = []
    if contains_right_brace:
        reasons.append('contains_right_brace')
    if contains_backslash:
        reasons.append('contains_backslash')
    if contains_newline:
        reasons.append('contains_newline')
    if contains_backtick:
        reasons.append('contains_backtick')
    if contains_control_char:
        reasons.append('contains_control_char')

    return {
        'boxed_safe': not (contains_right_brace or contains_newline or contains_control_char),
        'contains_right_brace': contains_right_brace,
        'contains_backslash': contains_backslash,
        'contains_newline': contains_newline,
        'contains_backtick': contains_backtick,
        'risk_reason': ','.join(reasons) if reasons else 'safe',
    }


def row_contains_risky_chars(gold_answer: str, extracted_answer: str) -> bool:
    values = (gold_answer or '', extracted_answer or '')
    return any(marker in value for value in values for marker in RISKY_TEXT_MARKERS)


def validate_and_prepare_replay_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required_columns = ('prompt_index', 'sample_idx', 'seed', 'raw_output')
    ensure_dataframe_columns(frame, required_columns, label='Replay frame')

    prepared = frame.copy()
    if 'id' not in prepared.columns:
        prepared['id'] = prepared['prompt_index'].map(lambda value: f'prompt-{value}')

    prepared['prompt_index'] = prepared['prompt_index'].astype(int)
    prepared['sample_idx'] = prepared['sample_idx'].astype(int)
    prepared['seed'] = prepared['seed'].astype(int)
    prepared['raw_output'] = prepared['raw_output'].map(normalize_text)
    if 'raw_output_len_chars' not in prepared.columns:
        prepared['raw_output_len_chars'] = prepared['raw_output'].map(len)
    if 'raw_output_num_lines' not in prepared.columns:
        prepared['raw_output_num_lines'] = prepared['raw_output'].map(raw_output_num_lines)
    if 'raw_output_est_tokens' not in prepared.columns:
        prepared['raw_output_est_tokens'] = prepared['raw_output'].map(estimate_output_token_count)
    return prepared.sort_values(['prompt_index', 'sample_idx', 'seed']).reset_index(drop=True)


def build_prompt_records(frame: pd.DataFrame) -> list[PromptRecord]:
    ensure_dataframe_columns(frame, ('id', 'prompt', 'answer'), label='Prompt frame')
    has_family = 'family' in frame.columns
    has_answer_type = 'answer_type' in frame.columns

    records: list[PromptRecord] = []
    for row in frame.itertuples(index=False):
        prompt = normalize_text(row.prompt)
        answer = normalize_text(row.answer)
        family = normalize_family(getattr(row, 'family', None) if has_family else None, prompt)
        answer_type = normalize_answer_type(
            getattr(row, 'answer_type', None) if has_answer_type else None,
            answer,
        )
        records.append(
            PromptRecord(
                id=str(row.id),
                prompt=prompt,
                answer=answer,
                family=family,
                answer_type=answer_type,
            )
        )
    return records


def make_eval_row(
    *,
    run_name: str,
    dataset_name: str,
    prompt_record: PromptRecord,
    generation: GenerationRecord,
    rendered_prompt: str,
    eval_mode: str,
    backend_name: str,
) -> EvalRow:
    extracted_answer, extraction_source = extract_final_answer_with_source(generation.raw_output)
    format_bucket = classify_format_bucket(generation.raw_output, extracted_answer, extraction_source)
    return EvalRow(
        run_name=run_name,
        dataset_name=dataset_name,
        id=prompt_record.id,
        sample_idx=generation.sample_idx,
        seed=generation.seed,
        family=prompt_record.family or infer_family(prompt_record.prompt),
        answer_type=prompt_record.answer_type or classify_answer_type(prompt_record.answer),
        gold_answer=prompt_record.answer or '',
        raw_output=generation.raw_output,
        extracted_answer=extracted_answer,
        extraction_source=extraction_source,
        format_bucket=format_bucket,
        has_boxed=count_boxed_occurrences(generation.raw_output) > 0,
        boxed_count=count_boxed_occurrences(generation.raw_output),
        contains_extra_numbers=detect_extra_trailing_numbers(generation.raw_output, extracted_answer),
        contains_risky_chars=row_contains_risky_chars(prompt_record.answer or '', extracted_answer),
        is_correct=verify(prompt_record.answer or '', extracted_answer),
        rendered_prompt_hash=sha256_text(rendered_prompt),
        eval_mode=eval_mode,
        backend_name=backend_name,
        raw_output_len_chars=generation.raw_output_len_chars,
        raw_output_num_lines=generation.raw_output_num_lines,
        raw_output_est_tokens=generation.raw_output_est_tokens,
    )


def majority_vote_answer(group: pd.DataFrame) -> str:
    answers = group['extracted_answer'].astype(str).tolist()
    counts = Counter(answers)
    first_positions: dict[str, int] = {}
    for position, answer in enumerate(answers):
        first_positions.setdefault(answer, position)
    return sorted(
        counts,
        key=lambda answer: (-counts[answer], first_positions[answer], answer),
    )[0]


def build_prompt_level_frame(row_level: pd.DataFrame) -> pd.DataFrame:
    prompt_rows: list[dict[str, Any]] = []
    for _, group in row_level.groupby('id', sort=True):
        sorted_group = group.sort_values(['sample_idx', 'seed']).reset_index(drop=True)
        gold_answer = str(sorted_group.iloc[0]['gold_answer'])
        majority_answer = majority_vote_answer(sorted_group)
        prompt_rows.append(
            {
                'id': str(sorted_group.iloc[0]['id']),
                'family': str(sorted_group.iloc[0]['family']),
                'gold_answer': gold_answer,
                'majority_answer': majority_answer,
                'majority_is_correct': verify(gold_answer, majority_answer),
                'pass_at_k': bool(sorted_group['is_correct'].any()),
            }
        )
    return pd.DataFrame(prompt_rows)


def aggregate_eval_rows(
    row_level: pd.DataFrame,
    *,
    run_name: str,
    dataset_name: str,
    backend_name: str,
    eval_mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    n_prompts = int(row_level['id'].nunique())
    samples_per_prompt_values = sorted(row_level.groupby('id').size().unique().tolist())
    if len(samples_per_prompt_values) != 1:
        raise ValueError(f'Inconsistent samples per prompt: {samples_per_prompt_values}')
    n_samples_per_prompt = int(samples_per_prompt_values[0])

    prompt_level = build_prompt_level_frame(row_level)

    majority_acc = float('nan')
    pass_at_k = float('nan')
    if n_samples_per_prompt > 1:
        majority_acc = float(prompt_level['majority_is_correct'].mean())
        pass_at_k = float(prompt_level['pass_at_k'].mean())

    summary = pd.DataFrame(
        [
            {
                'run_name': run_name,
                'backend_name': backend_name,
                'eval_mode': eval_mode,
                'dataset_name': dataset_name,
                'n_rows': n_prompts,
                'n_samples_per_prompt': n_samples_per_prompt,
                'overall_acc': float(row_level['is_correct'].mean()),
                'majority_acc': majority_acc,
                'pass_at_k': pass_at_k,
                'extraction_fail_rate': float((row_level['extraction_source'] == 'not_found').mean()),
                'format_fail_rate': float((~row_level['format_bucket'].isin(CLEAN_FORMAT_BUCKETS)).mean()),
                'boxed_rate': float(row_level['has_boxed'].mean()),
                'avg_output_len_chars': float(row_level['raw_output_len_chars'].mean()),
                'timestamp': utc_now(),
            }
        ]
    )

    family_prompt_level = prompt_level.set_index('id')
    family_metrics_rows: list[dict[str, Any]] = []
    for family, family_group in row_level.groupby('family', sort=True):
        prompt_ids = family_group['id'].astype(str).unique().tolist()
        family_prompt_group = family_prompt_level.loc[prompt_ids].reset_index(drop=True)
        family_metrics_rows.append(
            {
                'run_name': run_name,
                'family': family,
                'n': int(len(prompt_ids)),
                'acc': float(family_group['is_correct'].mean()),
                'majority_acc': float(family_prompt_group['majority_is_correct'].mean()) if n_samples_per_prompt > 1 else float('nan'),
                'pass_at_k': float(family_prompt_group['pass_at_k'].mean()) if n_samples_per_prompt > 1 else float('nan'),
                'extraction_fail_rate': float((family_group['extraction_source'] == 'not_found').mean()),
                'format_fail_rate': float((~family_group['format_bucket'].isin(CLEAN_FORMAT_BUCKETS)).mean()),
                'boxed_rate': float(family_group['has_boxed'].mean()),
                'avg_output_len_chars': float(family_group['raw_output_len_chars'].mean()),
            }
        )
    family_metrics = pd.DataFrame(family_metrics_rows).sort_values('family').reset_index(drop=True)

    failure_metrics = (
        row_level.groupby('format_bucket', dropna=False)
        .size()
        .rename('n')
        .reset_index()
        .sort_values(['n', 'format_bucket'], ascending=[False, True])
        .reset_index(drop=True)
    )
    failure_metrics.insert(0, 'run_name', run_name)
    failure_metrics['ratio'] = failure_metrics['n'] / len(row_level)

    return summary, family_metrics, failure_metrics


def evaluate_dataset(
    frame: pd.DataFrame,
    backend: GenerationBackend,
    eval_config: EvalConfig,
    out_dir: Path,
    *,
    tokenizer: Any | None = None,
    run_name: str | None = None,
    dataset_name: str = 'dataset',
) -> EvaluationArtifacts:
    ensure_version_directories()
    tokenizer = tokenizer or BuiltinCompetitionTokenizer()
    run_name = run_name or f'{dataset_name}-{eval_config.name}'
    row_level = _build_row_level_for_evaluation(
        frame,
        backend,
        eval_config,
        out_dir,
        tokenizer=tokenizer,
        run_name=run_name,
        dataset_name=dataset_name,
    )
    summary, family_metrics, failure_metrics = aggregate_eval_rows(
        row_level,
        run_name=run_name,
        dataset_name=dataset_name,
        backend_name=backend.backend_name,
        eval_mode=eval_config.name,
    )

    save_table(row_level, out_dir / 'row_level.parquet')
    save_table(summary, out_dir / 'summary.csv')
    save_table(family_metrics, out_dir / 'family_metrics.csv')
    save_table(failure_metrics, out_dir / 'failure_metrics.csv')

    return EvaluationArtifacts(
        row_level=row_level,
        summary=summary,
        family_metrics=family_metrics,
        failure_metrics=failure_metrics,
        out_dir=out_dir,
    )


def _build_row_level_for_evaluation(
    frame: pd.DataFrame,
    backend: GenerationBackend,
    eval_config: EvalConfig,
    out_dir: Path,
    *,
    tokenizer: Any,
    run_name: str,
    dataset_name: str,
) -> pd.DataFrame:
    if (
        isinstance(backend, MLXBackend)
        and isinstance(tokenizer, BuiltinCompetitionTokenizer)
        and len(frame) > 0
        and resolve_mlx_eval_num_shards() > 1
    ):
        return _build_row_level_via_mlx_shards(
            frame,
            backend,
            eval_config,
            out_dir,
            run_name=run_name,
            dataset_name=dataset_name,
        )

    prompt_records = build_prompt_records(frame)
    rendered_prompts = [build_competition_prompt(tokenizer, record.prompt, eval_config) for record in prompt_records]
    seeds = resolve_seeds(eval_config)
    generations = backend.generate(
        rendered_prompts,
        max_tokens=eval_config.max_tokens,
        top_p=eval_config.top_p,
        temperature=eval_config.temperature,
        max_model_len=eval_config.max_model_len,
        seeds=seeds,
        max_num_seqs=eval_config.max_num_seqs,
    )
    if len(generations) != len(prompt_records):
        raise ValueError(
            f'Backend returned {len(generations)} prompt groups, expected {len(prompt_records)}.'
        )

    rows: list[EvalRow] = []
    for prompt_record, rendered_prompt, samples in zip(prompt_records, rendered_prompts, generations, strict=True):
        if len(samples) != len(seeds):
            raise ValueError(
                f'Prompt id={prompt_record.id} returned {len(samples)} samples, expected {len(seeds)}.'
            )
        for generation in samples:
            rows.append(
                make_eval_row(
                    run_name=run_name,
                    dataset_name=dataset_name,
                    prompt_record=prompt_record,
                    generation=generation,
                    rendered_prompt=rendered_prompt,
                    eval_mode=eval_config.name,
                    backend_name=backend.backend_name,
                )
            )

    return pd.DataFrame([asdict(row) for row in rows]).sort_values(['id', 'sample_idx', 'seed']).reset_index(drop=True)


def _build_row_level_via_mlx_shards(
    frame: pd.DataFrame,
    backend: MLXBackend,
    eval_config: EvalConfig,
    out_dir: Path,
    *,
    run_name: str,
    dataset_name: str,
) -> pd.DataFrame:
    num_shards = min(resolve_mlx_eval_num_shards(), len(frame))
    shard_root = out_dir / '_shards'
    shard_root.mkdir(parents=True, exist_ok=True)
    config_path = shard_root / 'eval_config.yaml'
    config_path.write_text(yaml.safe_dump(asdict(eval_config), sort_keys=False), encoding='utf-8')
    shard_frames = [frame.iloc[shard_index::num_shards].reset_index(drop=True) for shard_index in range(num_shards)]
    shard_specs: list[tuple[int, int, Path, Path]] = []
    launched_processes: list[tuple[int, Path, subprocess.Popen[Any], Any]] = []
    print(
        '[evaluate_dataset] '
        f'launching {num_shards} MLX shard workers '
        f'for dataset={dataset_name} run={run_name}',
        flush=True,
    )
    for shard_index, shard_frame in enumerate(shard_frames):
        shard_input_path = shard_root / f'shard_{shard_index:02d}.parquet'
        shard_out_dir = shard_root / f'out_{shard_index:02d}'
        shard_log_path = shard_root / f'shard_{shard_index:02d}.log'
        save_table(shard_frame, shard_input_path)
        shard_out_dir.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(SCRIPT_PATH),
            'run-eval',
            '--input',
            str(shard_input_path),
            '--config',
            str(config_path),
            '--backend',
            'mlx',
            '--out',
            str(shard_out_dir),
            '--run-name',
            run_name,
            '--dataset-name',
            dataset_name,
            '--model-path',
            backend.model_path,
        ]
        if backend.adapter_path:
            command.extend(['--adapter-path', backend.adapter_path])
        if backend.trust_remote_code:
            command.append('--trust-remote-code')
        worker_env = os.environ.copy()
        worker_env['COMPETITION_TOKENIZER_PATH'] = backend.model_path
        worker_env['PYTHONUNBUFFERED'] = '1'
        worker_env['MLX_EVAL_NUM_SHARDS'] = '1'
        worker_env['MLX_EVAL_SHARD_INDEX'] = str(shard_index)
        print(
            '[evaluate_dataset] '
            f'launching shard={shard_index + 1}/{num_shards} '
            f'rows={len(shard_frame)} '
            f'log={shard_log_path}',
            flush=True,
        )
        log_handle = shard_log_path.open('w', encoding='utf-8')
        process = subprocess.Popen(
            command,
            cwd=str(REPO_ROOT),
            env=worker_env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        shard_specs.append((shard_index, len(shard_frame), shard_out_dir, shard_log_path))
        launched_processes.append((shard_index, shard_log_path, process, log_handle))

    try:
        for shard_index, shard_log_path, process, log_handle in launched_processes:
            return_code = process.wait()
            log_handle.close()
            if return_code != 0:
                raise RuntimeError(
                    'MLX shard evaluation failed: '
                    f'shard={shard_index + 1}/{num_shards} '
                    f'return_code={return_code} '
                    f'log={shard_log_path}\n'
                    f'{tail_text(shard_log_path)}'
                )
            print(
                '[evaluate_dataset] '
                f'completed shard={shard_index + 1}/{num_shards} '
                f'log={shard_log_path}',
                flush=True,
            )
    finally:
        for _, _, process, log_handle in launched_processes:
            if not log_handle.closed:
                log_handle.close()
            if process.poll() is None:
                process.kill()
                process.wait()

    shard_rows: list[pd.DataFrame] = []
    for shard_index, shard_size, shard_out_dir, shard_log_path in shard_specs:
        row_level_path = shard_out_dir / 'row_level.parquet'
        if not row_level_path.exists():
            raise FileNotFoundError(
                'MLX shard evaluation did not produce row_level.parquet: '
                f'shard={shard_index + 1}/{num_shards} '
                f'rows={shard_size} '
                f'log={shard_log_path}'
            )
        shard_rows.append(load_table(row_level_path))

    row_level = pd.concat(shard_rows, ignore_index=True).sort_values(['id', 'sample_idx', 'seed']).reset_index(drop=True)
    row_level['run_name'] = run_name
    row_level['dataset_name'] = dataset_name
    row_level['backend_name'] = backend.backend_name
    row_level['eval_mode'] = eval_config.name
    return row_level


def stable_dataframe_hash(frame: pd.DataFrame, columns: Sequence[str]) -> str:
    subset = frame.loc[:, list(columns)].copy()
    ordered_columns = [column for column in ('id', 'sample_idx', 'seed') if column in subset.columns]
    if ordered_columns:
        subset = subset.sort_values(ordered_columns).reset_index(drop=True)
    subset = subset.fillna('__NA__').astype(str)
    return sha256_text(subset.to_json(orient='records', force_ascii=True))


def build_sample_level_frame(row_level: pd.DataFrame) -> pd.DataFrame:
    columns = [
        'id',
        'sample_idx',
        'seed',
        'raw_output',
        'extracted_answer',
        'is_correct',
        'format_bucket',
        'raw_output_len_chars',
    ]
    return row_level.loc[:, columns].copy()


def build_probe_metrics_frame(
    row_level: pd.DataFrame,
    *,
    det_row_level: pd.DataFrame | None = None,
) -> pd.DataFrame:
    det_answers: dict[str, str] = {}
    if det_row_level is not None:
        det_answers = (
            det_row_level.sort_values(['id', 'sample_idx', 'seed'])
            .drop_duplicates('id')
            .set_index('id')['extracted_answer']
            .astype(str)
            .to_dict()
        )

    probe_rows: list[dict[str, Any]] = []
    for prompt_id, group in row_level.groupby('id', sort=True):
        ordered = group.sort_values(['sample_idx', 'seed']).reset_index(drop=True)
        majority_answer = majority_vote_answer(ordered)
        answer_counts = ordered['extracted_answer'].astype(str).value_counts()
        consensus_rate = float(answer_counts.iloc[0] / len(ordered))
        correct_rows = ordered.loc[ordered['is_correct']]
        det_answer = det_answers.get(str(prompt_id))
        probe_rows.append(
            {
                'run_name': str(ordered.iloc[0]['run_name']),
                'dataset_name': str(ordered.iloc[0]['dataset_name']),
                'backend_name': str(ordered.iloc[0]['backend_name']),
                'eval_mode': str(ordered.iloc[0]['eval_mode']),
                'id': str(prompt_id),
                'family': str(ordered.iloc[0]['family']),
                'answer_type': str(ordered.iloc[0]['answer_type']),
                'gold_answer': str(ordered.iloc[0]['gold_answer']),
                'pass_at_k': bool(ordered['is_correct'].any()),
                'majority_answer': majority_answer,
                'majority_correct': verify(str(ordered.iloc[0]['gold_answer']), majority_answer),
                'consensus_rate': consensus_rate,
                'n_unique_answers': int(ordered['extracted_answer'].astype(str).nunique()),
                'n_correct': int(ordered['is_correct'].sum()),
                'shortest_correct_len_chars': (
                    int(correct_rows['raw_output_len_chars'].min()) if not correct_rows.empty else pd.NA
                ),
                'best_format_correct_exists': bool(
                    ((ordered['is_correct']) & (ordered['format_bucket'].isin(CLEAN_FORMAT_BUCKETS))).any()
                ),
                'det_answer_in_probe_set': (
                    pd.NA if det_answer is None else bool(det_answer in set(ordered['extracted_answer'].astype(str)))
                ),
            }
        )
    return pd.DataFrame(probe_rows).sort_values('id').reset_index(drop=True)


def build_probe_summary_metrics(probe_metrics: pd.DataFrame) -> dict[str, Any]:
    shortest_correct = probe_metrics['shortest_correct_len_chars'].dropna()
    return {
        'pass_at_k': float(probe_metrics['pass_at_k'].mean()),
        'majority_acc': float(probe_metrics['majority_correct'].mean()),
        'mean_consensus_rate': float(probe_metrics['consensus_rate'].mean()),
        'mean_unique_answers': float(probe_metrics['n_unique_answers'].mean()),
        'format_safe_correct_rate': float(probe_metrics['best_format_correct_exists'].mean()),
        'shortest_correct_avg_len': float(shortest_correct.mean()) if not shortest_correct.empty else float('nan'),
    }


def augment_summary_for_probe(summary: pd.DataFrame, probe_metrics: pd.DataFrame) -> pd.DataFrame:
    augmented = summary.copy()
    metrics = build_probe_summary_metrics(probe_metrics)
    for key, value in metrics.items():
        augmented[key] = value
    return augmented


def augment_family_metrics_for_probe(family_metrics: pd.DataFrame, probe_metrics: pd.DataFrame) -> pd.DataFrame:
    aggregated = (
        probe_metrics.groupby('family', sort=True)
        .agg(
            pass_at_k=('pass_at_k', 'mean'),
            majority_acc=('majority_correct', 'mean'),
            mean_consensus_rate=('consensus_rate', 'mean'),
            mean_unique_answers=('n_unique_answers', 'mean'),
            format_safe_correct_rate=('best_format_correct_exists', 'mean'),
            shortest_correct_avg_len=('shortest_correct_len_chars', 'mean'),
        )
        .reset_index()
    )
    merged = family_metrics.drop(columns=['pass_at_k', 'majority_acc'], errors='ignore').merge(
        aggregated,
        on='family',
        how='left',
    )
    return merged.sort_values('family').reset_index(drop=True)


def build_oracle_replay_frame(
    frame: pd.DataFrame,
    *,
    seeds: Sequence[int],
    mode: str = 'official',
) -> pd.DataFrame:
    ensure_dataframe_columns(frame, ('id', 'answer'), label='Oracle replay input')
    records: list[dict[str, Any]] = []
    style_cycle = ['boxed', 'final_answer', 'plain']
    for prompt_index, row in enumerate(frame.itertuples(index=False)):
        answer = normalize_text(row.answer)
        answer_risk = analyze_extraction_risk(answer)
        for sample_idx, seed in enumerate(seeds):
            style = style_cycle[sample_idx % len(style_cycle)] if mode == 'probe' else 'plain'
            if style == 'boxed' and answer_risk['contains_right_brace']:
                style = 'final_answer'
            if style == 'boxed':
                raw_output = f'Working... \\\\boxed{{{answer}}}'
            elif style == 'final_answer':
                raw_output = f'Final answer: {answer}'
            else:
                raw_output = answer
            record = asdict(
                make_generation_record(
                    prompt_id=str(row.id),
                    sample_idx=sample_idx,
                    seed=seed,
                    raw_output=raw_output,
                )
            )
            record['prompt_index'] = prompt_index
            records.append(record)
    return pd.DataFrame(records).sort_values(['prompt_index', 'sample_idx', 'seed']).reset_index(drop=True)


def save_run_manifest(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')


def build_backend_from_args(args: argparse.Namespace) -> GenerationBackend:
    backend_name = getattr(args, 'backend', None)
    if backend_name == 'replay':
        replay_path = getattr(args, 'replay_path', None) or getattr(args, 'replay', None)
        if not replay_path:
            raise ValueError('--replay-path is required when --backend replay is selected.')
        return ReplayBackend(Path(replay_path))
    if backend_name == 'mlx':
        if not getattr(args, 'model_path', None):
            raise ValueError('--model-path is required when --backend mlx is selected.')
        return MLXBackend(
            model_path=str(args.model_path),
            adapter_path=getattr(args, 'adapter_path', None),
            trust_remote_code=bool(getattr(args, 'trust_remote_code', False)),
        )
    if backend_name == 'hf':
        if not getattr(args, 'model_path', None):
            raise ValueError('--model-path is required when --backend hf is selected.')
        return HFBackend(
            model_path=str(args.model_path),
            adapter_path=getattr(args, 'adapter_path', None),
            trust_remote_code=bool(getattr(args, 'trust_remote_code', False)),
        )
    raise ValueError(f'Unsupported backend: {backend_name}')


def run_eval(args: argparse.Namespace) -> None:
    frame = load_table(Path(args.input))
    out_dir = Path(args.out)
    eval_config = load_eval_config(args.config)
    backend = build_backend_from_args(args)
    print(
        '[run_eval] starting',
        f'backend={backend.backend_name}',
        f'rows={len(frame)}',
        f'config={eval_config.name}',
        f'out={out_dir}',
        flush=True,
    )
    tokenizer, tokenizer_name, tokenizer_revision = get_tokenizer(
        tokenizer_path=args.tokenizer_path,
        tokenizer_name=args.tokenizer_name,
        tokenizer_revision=args.tokenizer_revision,
    )
    artifacts = evaluate_dataset(
        frame,
        backend,
        eval_config,
        out_dir,
        tokenizer=tokenizer,
        run_name=args.run_name,
        dataset_name=args.dataset_name,
    )
    save_run_manifest(
        out_dir / 'run_manifest.json',
        {
            'backend': backend.backend_name,
            'config': eval_config.name,
            'dataset_name': args.dataset_name,
            'run_name': args.run_name or f'{args.dataset_name}-{eval_config.name}',
            'tokenizer_name': tokenizer_name,
            'tokenizer_revision': tokenizer_revision,
            'timestamp': utc_now(),
        },
    )
    print(
        'Evaluation completed:',
        f"backend={backend.backend_name}",
        f"rows={len(artifacts.row_level)}",
        f"summary={out_dir / 'summary.csv'}",
    )


def run_probe(args: argparse.Namespace) -> None:
    frame = load_table(Path(args.input))
    out_dir = Path(args.out)
    eval_config = load_eval_config(args.config)
    if eval_config.n_samples_per_prompt < 2:
        raise ValueError('Probe evaluation requires n_samples_per_prompt >= 2.')
    backend = build_backend_from_args(args)
    tokenizer, tokenizer_name, tokenizer_revision = get_tokenizer(
        tokenizer_path=args.tokenizer_path,
        tokenizer_name=args.tokenizer_name,
        tokenizer_revision=args.tokenizer_revision,
    )
    artifacts = evaluate_dataset(
        frame,
        backend,
        eval_config,
        out_dir,
        tokenizer=tokenizer,
        run_name=args.run_name,
        dataset_name=args.dataset_name,
    )
    det_row_level = load_table(Path(args.det_row_level)) if getattr(args, 'det_row_level', None) else None
    sample_level = build_sample_level_frame(artifacts.row_level)
    probe_metrics = build_probe_metrics_frame(artifacts.row_level, det_row_level=det_row_level)
    summary = augment_summary_for_probe(artifacts.summary, probe_metrics)
    family_metrics = augment_family_metrics_for_probe(artifacts.family_metrics, probe_metrics)
    save_table(sample_level, out_dir / 'sample_level.parquet')
    save_table(probe_metrics, out_dir / 'probe_metrics.csv')
    save_table(summary, out_dir / 'summary.csv')
    save_table(family_metrics, out_dir / 'family_metrics.csv')
    save_run_manifest(
        out_dir / 'run_manifest.json',
        {
            'backend': backend.backend_name,
            'config': eval_config.name,
            'dataset_name': args.dataset_name,
            'run_name': args.run_name or f'{args.dataset_name}-{eval_config.name}',
            'tokenizer_name': tokenizer_name,
            'tokenizer_revision': tokenizer_revision,
            'timestamp': utc_now(),
            'probe': True,
        },
    )
    print(
        'Probe evaluation completed:',
        f"backend={backend.backend_name}",
        f"rows={len(artifacts.row_level)}",
        f"probe_metrics={out_dir / 'probe_metrics.csv'}",
    )


def run_build_oracle_replay(args: argparse.Namespace) -> None:
    frame = load_table(Path(args.input))
    eval_config = load_eval_config(args.config)
    mode = args.mode or ('probe' if eval_config.n_samples_per_prompt > 1 else 'official')
    replay_frame = build_oracle_replay_frame(frame, seeds=resolve_seeds(eval_config), mode=mode)
    save_table(replay_frame, Path(args.output))
    print('Oracle replay build completed:', f'rows={len(replay_frame)}', f'output={args.output}')


def get_tokenizer(
    *,
    tokenizer_path: str | None = None,
    tokenizer_name: str | None = None,
    tokenizer_revision: str | None = None,
) -> tuple[Any, str, str]:
    explicit_default_path = os.environ.get('COMPETITION_TOKENIZER_PATH')
    auto_tokenizer_path: str | None = None
    if explicit_default_path:
        auto_tokenizer_path = explicit_default_path
    else:
        model_tokenizer_path = Path('model')
        if model_tokenizer_path.exists() and (model_tokenizer_path / 'tokenizer_config.json').exists():
            auto_tokenizer_path = str(model_tokenizer_path)

    resolved_tokenizer_path = tokenizer_path or auto_tokenizer_path
    resolved_automatically = tokenizer_path is None and resolved_tokenizer_path is not None

    if resolved_tokenizer_path:
        tokenizer_path_obj = Path(resolved_tokenizer_path)
        if not tokenizer_path_obj.exists():
            raise FileNotFoundError(f'Tokenizer path does not exist: {resolved_tokenizer_path}')
        try:
            from transformers import AutoTokenizer  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional runtime path
            if not resolved_automatically:
                raise RuntimeError('transformers is required when --tokenizer-path is provided.') from exc
        else:
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    resolved_tokenizer_path,
                    revision=tokenizer_revision,
                    trust_remote_code=True,
                )
            except OSError as exc:
                if not resolved_automatically:
                    raise
                warnings.warn(
                    f'Automatic tokenizer loading failed for {resolved_tokenizer_path}: {exc}. '
                    'Falling back to BuiltinCompetitionTokenizer.',
                    RuntimeWarning,
                    stacklevel=2,
                )
            else:
                name = tokenizer_name or getattr(tokenizer, 'name_or_path', resolved_tokenizer_path)
                revision = tokenizer_revision or ('auto' if resolved_automatically else 'unspecified')
                return tokenizer, name, revision

    tokenizer = BuiltinCompetitionTokenizer()
    return tokenizer, tokenizer_name or tokenizer.name_or_path, tokenizer_revision or tokenizer.revision


@dataclass(frozen=True)
class ParsedExample:
    inp: str
    out: str


@dataclass(frozen=True)
class ParsedPrompt:
    family: str
    subfamily: str
    answer_type: str
    parse_ok: bool
    confidence: float
    examples: list[ParsedExample]
    query_raw: str | None
    num_examples: int | None
    query_value_float: float | None
    estimated_g: float | None
    estimated_ratio: float | None
    roman_query_value: int | None
    bit_query_binary: str | None
    prompt_len_chars: int
    prompt_len_words: int
    special_chars: str
    contains_right_brace: bool
    contains_backslash: bool
    contains_backtick: bool


def extract_special_chars(text: str) -> str:
    chars = sorted({char for char in text if not char.isalnum() and not char.isspace()})
    return ''.join(chars)


def parse_float(text: str | None) -> float | None:
    if text is None or text == '':
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def median_or_none(values: Sequence[float]) -> float | None:
    numeric_values = sorted(values)
    if not numeric_values:
        return None
    midpoint = len(numeric_values) // 2
    if len(numeric_values) % 2 == 1:
        return float(numeric_values[midpoint])
    return float((numeric_values[midpoint - 1] + numeric_values[midpoint]) / 2)


def bit_query_hamming_bin(bits: str | None) -> str:
    if not bits:
        return 'unknown'
    weight = bits.count('1')
    if weight <= 2:
        return 'low'
    if weight <= 5:
        return 'mid'
    return 'high'


def int_to_bits(value: int) -> str:
    return format(value & 0xFF, '08b')


def detect_bit_fit_family(examples: Sequence[ParsedExample]) -> str:
    if not examples:
        return 'unknown'

    pairs = [(int(example.inp, 2), int(example.out, 2)) for example in examples]
    candidate_names: list[str] = []

    if all(out_value == (~inp_value & 0xFF) for inp_value, out_value in pairs):
        candidate_names.append('not')

    xor_mask = pairs[0][0] ^ pairs[0][1]
    if all((inp_value ^ xor_mask) == out_value for inp_value, out_value in pairs):
        candidate_names.append('xor_mask')

    and_mask = pairs[0][1]
    if all((inp_value & and_mask) == out_value for inp_value, out_value in pairs):
        candidate_names.append('and_mask')

    or_mask = pairs[0][1]
    if all((inp_value | or_mask) == out_value for inp_value, out_value in pairs):
        candidate_names.append('or_mask')

    if all(((inp_value << 1) & 0xFF) == out_value for inp_value, out_value in pairs):
        candidate_names.append('lshift')
    if all((inp_value >> 1) == out_value for inp_value, out_value in pairs):
        candidate_names.append('rshift')
    if all((((inp_value << 1) & 0xFF) | (inp_value >> 7)) == out_value for inp_value, out_value in pairs):
        candidate_names.append('lrot')
    if all(((inp_value >> 1) | ((inp_value & 1) << 7)) == out_value for inp_value, out_value in pairs):
        candidate_names.append('rrot')
    if all(int_to_bits(inp_value)[::-1] == int_to_bits(out_value) for inp_value, out_value in pairs):
        candidate_names.append('reverse')
    if all(int_to_bits(inp_value)[4:] + int_to_bits(inp_value)[:4] == int_to_bits(out_value) for inp_value, out_value in pairs):
        candidate_names.append('nibble_swap')

    if not candidate_names:
        return 'unknown'
    if len(candidate_names) == 1:
        return candidate_names[0]
    return 'multi_fit'


def build_base_prompt_features(prompt: str, answer: str | None) -> dict[str, Any]:
    combined_text = prompt if answer is None else f'{prompt}\n{answer}'
    return {
        'prompt_len_chars': len(prompt),
        'prompt_len_words': len(prompt.split()),
        'special_chars': extract_special_chars(prompt),
        'contains_right_brace': '}' in combined_text,
        'contains_backslash': '\\' in combined_text,
        'contains_backtick': '`' in combined_text,
    }


def parse_roman_prompt(prompt: str, answer: str | None) -> ParsedPrompt:
    examples = [
        ParsedExample(match.group(1), match.group(2))
        for line in prompt.splitlines()
        if (match := re.fullmatch(r'(\d+)\s*->\s*([IVXLCDM]+)', line.strip())) is not None
    ]
    query_match = re.search(r'write the number\s+(\d+)', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    roman_query_value = int(query_raw) if query_raw else None
    base_features = build_base_prompt_features(prompt, answer)
    return ParsedPrompt(
        family='roman_numeral',
        subfamily='subtractive' if roman_query_value in SUBTRACTIVE_VALUES else 'additive',
        answer_type='roman',
        parse_ok=bool(examples) and query_raw is not None,
        confidence=0.99 if examples and query_raw is not None else 0.75,
        examples=examples,
        query_raw=query_raw,
        num_examples=len(examples),
        query_value_float=float(query_raw) if query_raw else None,
        estimated_g=None,
        estimated_ratio=None,
        roman_query_value=roman_query_value,
        bit_query_binary=None,
        **base_features,
    )


def parse_gravity_prompt(prompt: str, answer: str | None) -> ParsedPrompt:
    pattern = re.compile(r'For t =\s*([0-9]+(?:\.[0-9]+)?)s, distance =\s*([0-9]+(?:\.[0-9]+)?)\s*m', re.IGNORECASE)
    examples = [ParsedExample(match.group(1), match.group(2)) for match in pattern.finditer(prompt)]
    query_match = re.search(r'falling distance for t =\s*([0-9]+(?:\.[0-9]+)?)s', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    estimated_g = median_or_none(
        [
            2 * float(example.out) / (float(example.inp) ** 2)
            for example in examples
            if float(example.inp) != 0.0
        ]
    )
    base_features = build_base_prompt_features(prompt, answer)
    return ParsedPrompt(
        family='gravity_constant',
        subfamily=f'g{int(round(estimated_g))}' if estimated_g is not None else 'gravity_rule',
        answer_type='numeric',
        parse_ok=bool(examples) and query_raw is not None,
        confidence=0.99 if examples and query_raw is not None else 0.75,
        examples=examples,
        query_raw=query_raw,
        num_examples=len(examples),
        query_value_float=parse_float(query_raw),
        estimated_g=estimated_g,
        estimated_ratio=None,
        roman_query_value=None,
        bit_query_binary=None,
        **base_features,
    )


def ratio_bin(estimated_ratio: float | None) -> str:
    if estimated_ratio is None:
        return 'unknown'
    if abs(estimated_ratio - 1.8) < 0.05:
        return 'edge'
    if estimated_ratio < 1:
        return 'lt1'
    if estimated_ratio < 2:
        return 'lt2'
    return 'ge2'


def parse_unit_prompt(prompt: str, answer: str | None) -> ParsedPrompt:
    pattern = re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*m becomes\s*([0-9]+(?:\.[0-9]+)?)', re.IGNORECASE)
    examples = [ParsedExample(match.group(1), match.group(2)) for match in pattern.finditer(prompt)]
    query_match = re.search(r'measurement:\s*([0-9]+(?:\.[0-9]+)?)\s*m', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    estimated_ratio = median_or_none(
        [
            float(example.out) / float(example.inp)
            for example in examples
            if float(example.inp) != 0.0
        ]
    )
    base_features = build_base_prompt_features(prompt, answer)
    return ParsedPrompt(
        family='unit_conversion',
        subfamily=f'ratio_{ratio_bin(estimated_ratio)}',
        answer_type='numeric',
        parse_ok=bool(examples) and query_raw is not None,
        confidence=0.99 if examples and query_raw is not None else 0.75,
        examples=examples,
        query_raw=query_raw,
        num_examples=len(examples),
        query_value_float=parse_float(query_raw),
        estimated_g=None,
        estimated_ratio=estimated_ratio,
        roman_query_value=None,
        bit_query_binary=None,
        **base_features,
    )


def parse_bit_prompt(prompt: str, answer: str | None) -> ParsedPrompt:
    examples = [
        ParsedExample(match.group(1), match.group(2))
        for match in re.finditer(r'([01]{8})\s*->\s*([01]{8})', prompt)
    ]
    query_match = re.search(r'output for:\s*([01]{8})', prompt, re.IGNORECASE)
    query_raw = query_match.group(1) if query_match else None
    fit_family = detect_bit_fit_family(examples)
    base_features = build_base_prompt_features(prompt, answer)
    return ParsedPrompt(
        family='bit_manipulation',
        subfamily=fit_family,
        answer_type='binary8',
        parse_ok=bool(examples) and query_raw is not None,
        confidence=0.99 if examples and query_raw is not None else 0.75,
        examples=examples,
        query_raw=query_raw,
        num_examples=len(examples),
        query_value_float=float(int(query_raw, 2)) if query_raw else None,
        estimated_g=None,
        estimated_ratio=None,
        roman_query_value=None,
        bit_query_binary=query_raw,
        **base_features,
    )


def parse_text_prompt(prompt: str, answer: str | None) -> ParsedPrompt:
    examples: list[ParsedExample] = []
    for line in prompt.splitlines():
        stripped = line.strip()
        if '->' not in stripped:
            continue
        left, right = stripped.split('->', 1)
        left = left.strip()
        right = right.strip()
        if left and right:
            examples.append(ParsedExample(left, right))
    query_match = re.search(r'decrypt the following text:\s*(.+)', prompt, re.IGNORECASE)
    query_raw = query_match.group(1).strip() if query_match else None
    answer_type = classify_answer_type(answer)
    base_features = build_base_prompt_features(prompt, answer)
    return ParsedPrompt(
        family='text_decryption',
        subfamily=f'tokens_{len(query_raw.split())}' if query_raw else 'decrypt_rule',
        answer_type=answer_type,
        parse_ok=bool(examples) and query_raw is not None,
        confidence=0.97 if examples and query_raw is not None else 0.7,
        examples=examples,
        query_raw=query_raw,
        num_examples=len(examples),
        query_value_float=None,
        estimated_g=None,
        estimated_ratio=None,
        roman_query_value=None,
        bit_query_binary=None,
        **base_features,
    )


def parse_symbol_prompt(prompt: str, answer: str | None) -> ParsedPrompt:
    examples: list[ParsedExample] = []
    for line in prompt.splitlines():
        stripped = line.strip()
        if not stripped or 'examples:' in stripped.lower() or stripped.lower().startswith('now,'):
            continue
        if '=' not in stripped:
            continue
        left, right = stripped.split('=', 1)
        left = left.strip(' `')
        right = right.strip(' `')
        if left and right:
            examples.append(ParsedExample(left, right))
    query_match = re.search(r'result for:\s*(.+)', prompt, re.IGNORECASE)
    if query_match is None:
        query_match = re.search(r'output for:\s*(.+)', prompt, re.IGNORECASE)
    query_raw = query_match.group(1).strip() if query_match else None
    answer_type = classify_answer_type(answer)
    base_features = build_base_prompt_features(prompt, answer)
    return ParsedPrompt(
        family='symbol_equation',
        subfamily='equation_transduction' if examples else 'symbol_rule',
        answer_type=answer_type,
        parse_ok=bool(examples) and query_raw is not None,
        confidence=0.94 if examples and query_raw is not None else 0.65,
        examples=examples,
        query_raw=query_raw,
        num_examples=len(examples),
        query_value_float=None,
        estimated_g=None,
        estimated_ratio=None,
        roman_query_value=None,
        bit_query_binary=None,
        **base_features,
    )


def parse_prompt(prompt: str, answer: str | None = None) -> ParsedPrompt:
    family = infer_family(prompt)
    if family == 'roman_numeral':
        return parse_roman_prompt(prompt, answer)
    if family == 'gravity_constant':
        return parse_gravity_prompt(prompt, answer)
    if family == 'bit_manipulation':
        return parse_bit_prompt(prompt, answer)
    if family == 'text_decryption':
        return parse_text_prompt(prompt, answer)
    if family == 'unit_conversion':
        return parse_unit_prompt(prompt, answer)
    return parse_symbol_prompt(prompt, answer)


def decimal_places(value: str) -> int:
    text = normalize_text(value).strip()
    if '.' not in text:
        return 0
    return len(text.split('.', 1)[1])


def near_round_boundary(value: str) -> bool:
    text = normalize_text(value).strip()
    if '.' not in text:
        return False
    decimals = text.split('.', 1)[1]
    if len(decimals) < 3:
        return False
    return decimals[2] in {'4', '5', '6'}


def token_length_signature(text: str | None) -> str:
    if not text:
        return 'none'
    return '-'.join(str(len(token)) for token in text.split())


def character_overlap_bin(query_text: str | None, answer_text: str) -> str:
    if not query_text or not answer_text:
        return 'low'
    query_chars = set(query_text.replace(' ', ''))
    answer_chars = set(answer_text.replace(' ', ''))
    union = query_chars | answer_chars
    if not union:
        return 'low'
    ratio = len(query_chars & answer_chars) / len(union)
    if ratio < 0.2:
        return 'low'
    if ratio < 0.5:
        return 'mid'
    return 'high'


def unique_char_ratio(text: str) -> float:
    compact = text.replace(' ', '')
    if not compact:
        return 0.0
    return len(set(compact)) / len(compact)


def has_rare_token(text: str | None) -> bool:
    if not text:
        return False
    tokens = text.split()
    return any(len(token) >= 8 or any(char in token.lower() for char in 'qzxj') for token in tokens)


def is_rare_token_length_pattern(text: str | None) -> bool:
    if not text:
        return False
    lengths = [len(token) for token in text.split()]
    return len(set(lengths)) == len(lengths) and max(lengths, default=0) >= 5


def symbol_query_charset_rarity(query_text: str | None) -> str:
    if not query_text:
        return 'low'
    charset = {char for char in query_text if not char.isalnum() and not char.isspace()}
    if len(charset) >= 4 or any(char in charset for char in {'\\', '`', '{', '}'}):
        return 'high'
    if len(charset) >= 2:
        return 'mid'
    return 'low'


def build_group_signature(parsed: ParsedPrompt, answer_text: str) -> str:
    if parsed.family == 'bit_manipulation':
        return f"{parsed.subfamily}__ex{parsed.num_examples or 0}__qhw{bit_query_hamming_bin(parsed.bit_query_binary)}"
    if parsed.family == 'gravity_constant':
        g_bin = int(round(parsed.estimated_g)) if parsed.estimated_g is not None else 'unknown'
        return f'gbin{g_bin}__dec{decimal_places(answer_text)}'
    if parsed.family == 'unit_conversion':
        query_bin = int((parsed.query_value_float or 0.0) // 10) if parsed.query_value_float is not None else 'unknown'
        return f'rbin{ratio_bin(parsed.estimated_ratio)}__qbin{query_bin}'
    if parsed.family == 'roman_numeral':
        value = parsed.roman_query_value if parsed.roman_query_value is not None else -1
        return f'decade{value // 10 if value >= 0 else "unknown"}__sub{int(value in SUBTRACTIVE_VALUES) if value >= 0 else "unknown"}'
    if parsed.family == 'text_decryption':
        return (
            f'wc{len(answer_text.split())}__'
            f'lensig{token_length_signature(answer_text)}__'
            f'charpat{character_overlap_bin(parsed.query_raw, answer_text)}'
        )
    answer_family = 'numeric' if classify_answer_type(answer_text) == 'numeric' else 'symbolic'
    risk_class = 'risky' if any(char in answer_text for char in ('}', '{', '\\', '`')) else 'safe'
    return f'atype{answer_family}__alen{len(answer_text)}__risk{risk_class}'


def build_public_overlap_pairs(public_df: pd.DataFrame) -> set[tuple[str, str]]:
    return set(zip(public_df['id'].astype(str), public_df['prompt'].astype(str)))


def compute_hard_score(record: dict[str, Any], quantiles: dict[str, dict[str, float]]) -> float:
    family = str(record['family'])
    score = 0.0

    if bool(record['contains_right_brace']):
        score += 2.0
    if bool(record['contains_backslash']):
        score += 1.0

    prompt_p75 = quantiles['prompt_p75'][family]
    prompt_p80 = quantiles['prompt_p80'][family]
    prompt_p90 = quantiles['prompt_p90'][family]
    answer_p10 = quantiles['answer_p10'][family]
    answer_p80 = quantiles['answer_p80'][family]
    answer_p90 = quantiles['answer_p90'][family]
    query_p10 = quantiles['query_p10'].get(family)
    query_p90 = quantiles['query_p90'].get(family)

    if float(record['prompt_len_chars']) >= prompt_p75:
        score += 1.0
    if float(record['answer_len']) <= answer_p10 or float(record['answer_len']) >= answer_p90:
        score += 1.0

    if family == 'bit_manipulation':
        if record['query_raw'] in {'00000000', '11111111', '10101010', '01010101'}:
            score += 2.0
        if int(record['num_examples'] or 0) >= 9:
            score += 1.0
        if record['subfamily'] in {'multi_fit', 'unknown'}:
            score += 2.0
        if float(record['prompt_len_chars']) >= prompt_p90:
            score += 1.0
    elif family == 'gravity_constant':
        query_value = record['query_value_float']
        if query_value is not None and query_p10 is not None and query_p90 is not None and (query_value <= query_p10 or query_value >= query_p90):
            score += 1.0
        if record['g_bin'] == 18:
            score += 1.0
        if int(record['answer_decimal_style']) == 1:
            score += 2.0
        if bool(record['near_round_boundary']):
            score += 1.0
    elif family == 'unit_conversion':
        if record['ratio_bin'] == 'edge':
            score += 1.0
        if bool(record['near_round_boundary']):
            score += 2.0
        query_value = record['query_value_float']
        if query_value is not None and query_p10 is not None and query_p90 is not None and (query_value <= query_p10 or query_value >= query_p90):
            score += 1.0
    elif family == 'roman_numeral':
        roman_value = record['roman_query_value']
        if roman_value in SUBTRACTIVE_VALUES:
            score += 2.0
        if roman_value in {39, 40, 41, 89, 90, 91, 99, 100}:
            score += 1.0
    elif family == 'text_decryption':
        if int(record['answer_word_count']) == 5:
            score += 1.0
        if float(record['answer_len']) >= answer_p80:
            score += 1.0
        if bool(record['rare_token_flag']):
            score += 1.0
        if float(record['unique_char_ratio']) >= 0.8:
            score += 1.0
        if bool(record['token_length_pattern_rare']):
            score += 1.0
    else:
        if any(char in str(record['answer']) for char in ('}', '{', '\\', '`')):
            score += 2.0
        if int(record['answer_len']) in {1, 4}:
            score += 1.0
        has_digit = bool(re.search(r'\d', str(record['answer'])))
        has_symbol = bool(re.search(r'[^A-Za-z0-9\s]', str(record['answer'])))
        if has_digit and has_symbol:
            score += 1.0
        if record['query_charset_rarity'] == 'high':
            score += 1.0

    return score


def assign_risk_bins(metadata_df: pd.DataFrame) -> pd.DataFrame:
    labeled = metadata_df.copy()
    labeled['risk_bin'] = 'risk_mid'
    for family, group in labeled.groupby('family', sort=True):
        ordered = group.sort_values(['hard_score', 'id'], ascending=[True, True]).reset_index()
        bins = pd.qcut(range(len(ordered)), q=3, labels=['risk_low', 'risk_mid', 'risk_high'])
        labeled.loc[ordered['index'], 'risk_bin'] = [str(value) for value in bins]
    return labeled


def build_metadata_frame(train_df: pd.DataFrame, public_df: pd.DataFrame) -> pd.DataFrame:
    public_pairs = build_public_overlap_pairs(public_df)
    records: list[dict[str, Any]] = []

    for row in train_df.itertuples(index=False):
        prompt = normalize_text(row.prompt)
        answer = normalize_text(row.answer)
        parsed = parse_prompt(prompt, answer)
        answer_risk = analyze_extraction_risk(answer)
        records.append(
            {
                'id': str(row.id),
                'prompt': prompt,
                'answer': answer,
                'family': parsed.family,
                'subfamily': parsed.subfamily,
                'answer_type': parsed.answer_type,
                'parse_ok': parsed.parse_ok,
                'parse_confidence': parsed.confidence,
                'num_examples': parsed.num_examples,
                'query_raw': parsed.query_raw,
                'group_signature': build_group_signature(parsed, answer),
                'hard_score': 0.0,
                'risk_bin': 'risk_mid',
                'prompt_len_chars': parsed.prompt_len_chars,
                'prompt_len_words': parsed.prompt_len_words,
                'answer_len': len(answer.strip()),
                'contains_right_brace': parsed.contains_right_brace,
                'contains_backslash': parsed.contains_backslash,
                'contains_backtick': parsed.contains_backtick,
                'is_public_test_overlap': (str(row.id), prompt) in public_pairs,
                'special_chars': parsed.special_chars,
                'query_value_float': parsed.query_value_float,
                'estimated_g': parsed.estimated_g,
                'estimated_ratio': parsed.estimated_ratio,
                'roman_query_value': parsed.roman_query_value,
                'bit_query_binary': parsed.bit_query_binary,
                'fit_family': parsed.subfamily if parsed.family == 'bit_manipulation' else '',
                'query_hamming_bin': bit_query_hamming_bin(parsed.bit_query_binary),
                'g_bin': int(round(parsed.estimated_g)) if parsed.estimated_g is not None else None,
                'answer_decimal_style': decimal_places(answer),
                'ratio_bin': ratio_bin(parsed.estimated_ratio),
                'query_bin': int((parsed.query_value_float or 0.0) // 10) if parsed.query_value_float is not None else None,
                'near_round_boundary': near_round_boundary(answer),
                'answer_word_count': len(answer.split()),
                'token_len_signature': token_length_signature(answer),
                'char_overlap_bin': character_overlap_bin(parsed.query_raw, answer),
                'rare_token_flag': has_rare_token(answer),
                'unique_char_ratio': unique_char_ratio(answer),
                'token_length_pattern_rare': is_rare_token_length_pattern(answer),
                'query_charset_rarity': symbol_query_charset_rarity(parsed.query_raw),
                'boxed_safe': answer_risk['boxed_safe'],
            }
        )

    metadata_df = pd.DataFrame(records).sort_values('id').reset_index(drop=True)
    quantiles = {
        'prompt_p75': metadata_df.groupby('family')['prompt_len_chars'].quantile(0.75).to_dict(),
        'prompt_p80': metadata_df.groupby('family')['prompt_len_chars'].quantile(0.80).to_dict(),
        'prompt_p90': metadata_df.groupby('family')['prompt_len_chars'].quantile(0.90).to_dict(),
        'answer_p10': metadata_df.groupby('family')['answer_len'].quantile(0.10).to_dict(),
        'answer_p80': metadata_df.groupby('family')['answer_len'].quantile(0.80).to_dict(),
        'answer_p90': metadata_df.groupby('family')['answer_len'].quantile(0.90).to_dict(),
        'query_p10': metadata_df.groupby('family')['query_value_float'].quantile(0.10).dropna().to_dict(),
        'query_p90': metadata_df.groupby('family')['query_value_float'].quantile(0.90).dropna().to_dict(),
    }
    metadata_df['hard_score'] = [compute_hard_score(record, quantiles) for record in metadata_df.to_dict('records')]
    metadata_df = assign_risk_bins(metadata_df)
    return metadata_df


def build_manual_audit_frame(metadata_df: pd.DataFrame, *, seed: int = 20260319, per_family: int = 20) -> pd.DataFrame:
    family_frames: list[pd.DataFrame] = []
    for family, group in metadata_df.groupby('family', sort=True):
        hard = group.sort_values(['hard_score', 'id'], ascending=[False, True]).head(10).copy()
        hard['audit_bucket'] = 'hard'
        remaining = group.loc[~group['id'].isin(hard['id'])].copy()
        normal = remaining.sample(n=min(10, len(remaining)), random_state=seed).copy()
        normal['audit_bucket'] = 'normal'
        selected = pd.concat([hard, normal], ignore_index=True)
        family_frames.append(selected)

    audit_df = pd.concat(family_frames, ignore_index=True)
    selected_ids = set(audit_df['id'].astype(str))
    missing_overlaps = metadata_df.loc[
        metadata_df['is_public_test_overlap'] & ~metadata_df['id'].astype(str).isin(selected_ids)
    ].sort_values(['family', 'hard_score', 'id'], ascending=[True, False, True])

    for overlap_row in missing_overlaps.itertuples(index=False):
        family_mask = audit_df['family'] == overlap_row.family
        family_normal = audit_df.loc[family_mask & (audit_df['audit_bucket'] == 'normal')].sort_values(['hard_score', 'id'])
        if family_normal.empty:
            continue
        replace_index = family_normal.index[0]
        replacement = metadata_df.loc[metadata_df['id'] == overlap_row.id].copy()
        replacement['audit_bucket'] = 'public_overlap'
        audit_df = pd.concat([audit_df.drop(index=replace_index), replacement], ignore_index=True)

    audit_df = audit_df.sort_values(['family', 'audit_bucket', 'hard_score', 'id'], ascending=[True, True, False, True]).reset_index(drop=True)
    audit_df['prompt_preview'] = audit_df['prompt'].str.slice(0, 160)
    columns = [
        'id',
        'family',
        'audit_bucket',
        'hard_score',
        'risk_bin',
        'is_public_test_overlap',
        'subfamily',
        'answer_type',
        'num_examples',
        'query_raw',
        'parse_ok',
        'parse_confidence',
        'group_signature',
        'prompt_preview',
        'answer',
    ]
    return audit_df[columns]


def run_build_metadata(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    public_test_path = Path(args.public_test)
    output_path = Path(args.output)
    metadata_df = build_metadata_frame(load_table(input_path), load_table(public_test_path))
    save_table(metadata_df, output_path)
    counts = metadata_df['family'].value_counts().sort_index().to_dict()
    print('Metadata build completed:', f'rows={len(metadata_df)}', f'output={output_path}', f'counts={counts}')


def run_build_family_audit(args: argparse.Namespace) -> None:
    metadata_path = Path(args.metadata)
    output_path = Path(args.output)
    metadata_df = load_table(metadata_path)
    audit_df = build_manual_audit_frame(metadata_df)
    save_table(audit_df, output_path)
    print('Family audit sample completed:', f'rows={len(audit_df)}', f'output={output_path}')


def build_cv_strata(metadata_df: pd.DataFrame) -> pd.Series:
    strata = (
        metadata_df['family'].astype(str)
        + '__'
        + metadata_df['answer_type'].astype(str)
        + '__'
        + metadata_df['risk_bin'].astype(str)
    )
    counts = strata.value_counts()
    return strata.where(strata.map(counts) >= 5, metadata_df['family'].astype(str))


def build_splits_frame(metadata_df: pd.DataFrame) -> pd.DataFrame:
    split_df = metadata_df.copy().sort_values('id').reset_index(drop=True)
    split_df['prompt_hash'] = split_df['prompt'].map(sha256_text)
    split_df['cv5_fold'] = -1
    split_df['is_holdout_hard'] = False

    strata = build_cv_strata(split_df)
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=20260316)
    for fold_idx, (_, valid_index) in enumerate(splitter.split(split_df, strata)):
        split_df.loc[valid_index, 'cv5_fold'] = fold_idx

    for family, family_group in split_df.groupby('family', sort=True):
        ordered = family_group.sort_values(['hard_score', 'prompt_hash', 'id'], ascending=[False, True, True])
        hard_count = max(1, int(round(len(ordered) * 0.20)))
        remainder = ordered.iloc[hard_count:]
        extra_count = min(len(remainder), max(1, int(round(len(ordered) * 0.05))))
        extra = remainder.sample(n=extra_count, random_state=20260317) if extra_count else remainder.head(0)
        selected_ids = pd.Index(ordered.head(hard_count)['id']).append(pd.Index(extra['id']))
        split_df.loc[split_df['id'].isin(selected_ids), 'is_holdout_hard'] = True

    for split_idx in range(3):
        column = f'group_shift_split{split_idx}'
        split_df[column] = 'train'
        for family, family_group in split_df.groupby('family', sort=True):
            group_splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=20260318 + split_idx)
            _, test_index = next(group_splitter.split(family_group, groups=family_group['group_signature'].astype(str)))
            test_ids = family_group.iloc[test_index]['id']
            split_df.loc[split_df['id'].isin(test_ids), column] = 'test'

    return split_df


def allocate_family_counts(frame: pd.DataFrame, total_rows: int) -> dict[str, int]:
    families = sorted(frame['family'].astype(str).unique())
    base = total_rows // len(families)
    remainder = total_rows % len(families)
    counts = {family: base for family in families}
    for family in families[:remainder]:
        counts[family] += 1
    return counts


def sample_family_risk_mix(group: pd.DataFrame, n_rows: int, *, seed: int, prefer_hard: bool = False) -> pd.DataFrame:
    if n_rows >= len(group):
        return group.sort_values(['hard_score', 'id'], ascending=[False, True]).copy()

    selected_frames: list[pd.DataFrame] = []
    risk_order = ['risk_high', 'risk_mid', 'risk_low']
    base = n_rows // len(risk_order)
    remainder = n_rows % len(risk_order)

    for offset, risk_bin in enumerate(risk_order):
        subset = group.loc[group['risk_bin'] == risk_bin]
        if subset.empty:
            continue
        target = base + (1 if offset < remainder else 0)
        target = min(target, len(subset))
        if target == 0:
            continue
        if prefer_hard:
            picked = subset.sort_values(['hard_score', 'id'], ascending=[False, True]).head(target)
        else:
            picked = subset.sample(n=target, random_state=seed + offset)
        selected_frames.append(picked)

    selected = pd.concat(selected_frames, ignore_index=False) if selected_frames else group.head(0)
    if len(selected) < n_rows:
        remaining = group.loc[~group['id'].isin(selected['id'])]
        fill_count = n_rows - len(selected)
        if prefer_hard:
            fill = remaining.sort_values(['hard_score', 'id'], ascending=[False, True]).head(fill_count)
        else:
            fill = remaining.sample(n=fill_count, random_state=seed + 99)
        selected = pd.concat([selected, fill], ignore_index=False)
    return selected.sort_values(['family', 'hard_score', 'id'], ascending=[True, False, True]).head(n_rows)


def build_shadow_pack(frame: pd.DataFrame, n_rows: int, *, seed: int, prefer_hard: bool = False) -> pd.DataFrame:
    allocations = allocate_family_counts(frame, n_rows)
    sampled_frames: list[pd.DataFrame] = []
    for offset, family in enumerate(sorted(allocations)):
        family_group = frame.loc[frame['family'] == family]
        sampled_frames.append(
            sample_family_risk_mix(
                family_group,
                allocations[family],
                seed=seed + offset,
                prefer_hard=prefer_hard,
            )
        )
    return pd.concat(sampled_frames, ignore_index=True).sort_values(['family', 'hard_score', 'id'], ascending=[True, False, True]).reset_index(drop=True)


def write_eval_packs(split_df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for fold_idx in range(5):
        save_table(split_df.loc[split_df['cv5_fold'] == fold_idx].reset_index(drop=True), out_dir / f'cv5_fold{fold_idx}.csv')

    save_table(split_df.loc[split_df['is_holdout_hard']].reset_index(drop=True), out_dir / 'holdout_hard.csv')

    for split_idx in range(3):
        column = f'group_shift_split{split_idx}'
        save_table(split_df.loc[split_df[column] == 'test'].reset_index(drop=True), out_dir / f'group_shift_split{split_idx}.csv')

    clean_pool = split_df.loc[~split_df['is_public_test_overlap']].reset_index(drop=True)
    hard_pool = clean_pool.loc[clean_pool['is_holdout_hard']].reset_index(drop=True)
    save_table(build_shadow_pack(clean_pool, 128, seed=20260320), out_dir / 'shadow_128.csv')
    save_table(build_shadow_pack(clean_pool, 256, seed=20260321), out_dir / 'shadow_256.csv')
    save_table(build_shadow_pack(hard_pool, 256, seed=20260322, prefer_hard=True), out_dir / 'hard_shadow_256.csv')


def run_build_splits(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_path = Path(args.output)
    split_df = build_splits_frame(load_table(input_path))
    save_table(split_df, output_path)
    print('Split build completed:', f'rows={len(split_df)}', f'output={output_path}')


def run_build_shadow_packs(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    out_dir = Path(args.outdir)
    split_df = load_table(input_path)
    write_eval_packs(split_df, out_dir)
    print('Shadow pack build completed:', f'outdir={out_dir}')


def run_replay_eval(args: argparse.Namespace) -> None:
    dataset_path = Path(args.input)
    replay_path = Path(args.replay)
    out_dir = Path(args.out)

    frame = load_table(dataset_path)
    backend = ReplayBackend(replay_path)
    eval_config = load_eval_config(args.config)
    tokenizer, tokenizer_name, tokenizer_revision = get_tokenizer(
        tokenizer_path=args.tokenizer_path,
        tokenizer_name=args.tokenizer_name,
        tokenizer_revision=args.tokenizer_revision,
    )
    artifacts = evaluate_dataset(
        frame,
        backend,
        eval_config,
        out_dir,
        tokenizer=tokenizer,
        run_name=args.run_name,
        dataset_name=args.dataset_name,
    )
    print(
        'Replay evaluation completed:',
        f"rows={len(artifacts.row_level)}",
        f"summary={out_dir / 'summary.csv'}",
        f'tokenizer={tokenizer_name}@{tokenizer_revision}',
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='v1 evaluation foundation CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    metadata_parser = subparsers.add_parser('build-metadata', help='Build train_metadata_v1.parquet')
    metadata_parser.add_argument('--input', default=str(RAW_TRAIN_PATH), help='Train dataset csv/parquet path')
    metadata_parser.add_argument('--public-test', default=str(RAW_TEST_PATH), help='Visible public test csv/parquet path')
    metadata_parser.add_argument('--output', default=str(PROCESSED_DIR / 'train_metadata_v1.parquet'))
    metadata_parser.set_defaults(func=run_build_metadata)

    audit_parser = subparsers.add_parser('build-family-audit', help='Build family parser audit sample CSV')
    audit_parser.add_argument('--metadata', default=str(PROCESSED_DIR / 'train_metadata_v1.parquet'))
    audit_parser.add_argument('--output', default=str(OUTPUT_AUDITS_DIR / 'family_parser_manual_audit_v1.csv'))
    audit_parser.set_defaults(func=run_build_family_audit)

    split_parser = subparsers.add_parser('build-splits', help='Build train_splits_v1.parquet')
    split_parser.add_argument('--input', default=str(PROCESSED_DIR / 'train_metadata_v1.parquet'))
    split_parser.add_argument('--output', default=str(PROCESSED_DIR / 'train_splits_v1.parquet'))
    split_parser.set_defaults(func=run_build_splits)

    shadow_parser = subparsers.add_parser('build-shadow-packs', help='Build cv/holdout/group/shadow eval packs')
    shadow_parser.add_argument('--input', default=str(PROCESSED_DIR / 'train_splits_v1.parquet'))
    shadow_parser.add_argument('--outdir', default=str(EVAL_PACKS_DIR))
    shadow_parser.set_defaults(func=run_build_shadow_packs)

    oracle_parser = subparsers.add_parser('build-oracle-replay', help='Build deterministic replay outputs from gold answers')
    oracle_parser.add_argument('--input', required=True, help='Input csv/parquet with answer column')
    oracle_parser.add_argument('--config', default='official_lb', help='Eval config name or path')
    oracle_parser.add_argument('--output', required=True, help='Replay output parquet/csv path')
    oracle_parser.add_argument('--mode', choices=['official', 'probe'], default=None)
    oracle_parser.set_defaults(func=run_build_oracle_replay)

    eval_parser = subparsers.add_parser('run-eval', help='Run official_det style evaluation')
    eval_parser.add_argument('--input', required=True, help='Prompt dataset csv/parquet path')
    eval_parser.add_argument('--config', default='official_lb', help='Eval config name or path')
    eval_parser.add_argument('--backend', choices=['replay', 'mlx', 'hf'], required=True)
    eval_parser.add_argument('--out', required=True, help='Output directory for evaluator artifacts')
    eval_parser.add_argument('--run-name', default=None, help='Optional run name override')
    eval_parser.add_argument('--dataset-name', default='dataset', help='Dataset name label for reports')
    eval_parser.add_argument('--replay-path', default=None, help='Replay outputs csv/parquet path when backend=replay')
    eval_parser.add_argument('--model-path', default=None, help='Model path for mlx/hf backends')
    eval_parser.add_argument('--adapter-path', default=None, help='Optional adapter path for mlx/hf backends')
    eval_parser.add_argument('--trust-remote-code', action='store_true')
    eval_parser.add_argument('--tokenizer-path', default=None)
    eval_parser.add_argument('--tokenizer-name', default=None)
    eval_parser.add_argument('--tokenizer-revision', default=None)
    eval_parser.set_defaults(func=run_eval)

    probe_parser = subparsers.add_parser('run-probe', help='Run sc_probe style evaluation')
    probe_parser.add_argument('--input', required=True, help='Prompt dataset csv/parquet path')
    probe_parser.add_argument('--config', required=True, help='Probe config name or path')
    probe_parser.add_argument('--backend', choices=['replay', 'mlx', 'hf'], required=True)
    probe_parser.add_argument('--out', required=True, help='Output directory for probe artifacts')
    probe_parser.add_argument('--run-name', default=None, help='Optional run name override')
    probe_parser.add_argument('--dataset-name', default='dataset', help='Dataset name label for reports')
    probe_parser.add_argument('--replay-path', default=None, help='Replay outputs csv/parquet path when backend=replay')
    probe_parser.add_argument('--model-path', default=None, help='Model path for mlx/hf backends')
    probe_parser.add_argument('--adapter-path', default=None, help='Optional adapter path for mlx/hf backends')
    probe_parser.add_argument('--trust-remote-code', action='store_true')
    probe_parser.add_argument('--tokenizer-path', default=None)
    probe_parser.add_argument('--tokenizer-name', default=None)
    probe_parser.add_argument('--tokenizer-revision', default=None)
    probe_parser.add_argument('--det-row-level', default=None, help='Optional row_level.parquet from official_det run')
    probe_parser.set_defaults(func=run_probe)

    replay_parser = subparsers.add_parser('run-replay-eval', help='Run evaluator with ReplayBackend')
    replay_parser.add_argument('--input', required=True, help='Prompt dataset csv/parquet path')
    replay_parser.add_argument('--replay', required=True, help='Replay outputs csv/parquet path')
    replay_parser.add_argument('--config', default='official_lb', help='Eval config name or path')
    replay_parser.add_argument('--out', required=True, help='Output directory for evaluator artifacts')
    replay_parser.add_argument('--run-name', default=None, help='Optional run name override')
    replay_parser.add_argument('--dataset-name', default='dataset', help='Dataset name label for reports')
    replay_parser.add_argument('--tokenizer-path', default=None)
    replay_parser.add_argument('--tokenizer-name', default=None)
    replay_parser.add_argument('--tokenizer-revision', default=None)
    replay_parser.set_defaults(func=run_replay_eval)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
