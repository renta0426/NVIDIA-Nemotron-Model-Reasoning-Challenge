from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import sys

import pytest


def load_v1_module():
    module_name = 'v1_train'
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v1 = load_v1_module()


def make_det_dataset():
    return v1.pd.DataFrame(
        [
            {
                'id': 'p1',
                'prompt': 'Compute 6 * 7.',
                'answer': '42',
                'family': 'symbol_equation',
                'answer_type': 'numeric',
            },
            {
                'id': 'p2',
                'prompt': 'Write the Roman numeral for fourteen.',
                'answer': 'XIV',
                'family': 'roman_numeral',
                'answer_type': 'roman',
            },
        ]
    )


def make_det_replay():
    return v1.pd.DataFrame(
        [
            {'prompt_index': 0, 'id': 'p1', 'sample_idx': 0, 'seed': 0, 'raw_output': r'\\boxed{42}'},
            {'prompt_index': 1, 'id': 'p2', 'sample_idx': 0, 'seed': 0, 'raw_output': 'Final answer: XIV'},
        ]
    )


def test_replay_eval_is_deterministic(tmp_path):
    dataset = make_det_dataset()
    replay = make_det_replay()
    backend = v1.ReplayBackend(replay)
    config = v1.load_eval_config('official_lb')

    first = v1.evaluate_dataset(dataset, backend, config, tmp_path / 'run1', run_name='det-1', dataset_name='shadow')
    second = v1.evaluate_dataset(dataset, v1.ReplayBackend(replay), config, tmp_path / 'run2', run_name='det-2', dataset_name='shadow')

    assert v1.stable_dataframe_hash(first.row_level, ['id', 'sample_idx', 'seed', 'raw_output']) == v1.stable_dataframe_hash(
        second.row_level,
        ['id', 'sample_idx', 'seed', 'raw_output'],
    )
    assert v1.stable_dataframe_hash(first.row_level, ['id', 'sample_idx', 'seed', 'extracted_answer']) == v1.stable_dataframe_hash(
        second.row_level,
        ['id', 'sample_idx', 'seed', 'extracted_answer'],
    )


def test_mlx_backend_raises_clear_error_when_runtime_missing(monkeypatch):
    original_find_spec = v1.importlib.util.find_spec

    def fake_find_spec(name: str, *args, **kwargs):
        if name == 'mlx_lm':
            return None
        return original_find_spec(name, *args, **kwargs)

    monkeypatch.setattr(v1.importlib.util, 'find_spec', fake_find_spec)
    backend = v1.MLXBackend(model_path='missing-model')
    with pytest.raises(RuntimeError, match='mlx-lm'):
        backend.generate(['prompt'], max_tokens=8, top_p=1.0, temperature=0.0, max_model_len=1024, seeds=[0])


def test_mlx_backend_greedy_path_batches_prompts_and_duplicates_seed_outputs(monkeypatch):
    class FakeMXRandom:
        def __init__(self):
            self.seed_calls = []

        def seed(self, value):
            self.seed_calls.append(value)

    class FakeMX:
        def __init__(self):
            self.random = FakeMXRandom()
            self.clear_cache_calls = 0

        def clear_cache(self):
            self.clear_cache_calls += 1

    class FakeTokenizer:
        bos_token = None

        def encode(self, text, add_special_tokens=True):
            return [len(text), 1 if add_special_tokens else 0]

    class FakeBatchResponse:
        def __init__(self, texts):
            self.texts = texts

    fake_mx = FakeMX()
    batch_calls = []

    def fake_batch_generate(model, tokenizer, prompts, **kwargs):
        batch_calls.append({'prompts': prompts, 'kwargs': kwargs})
        return FakeBatchResponse([f'batched:{prompt[0]}' for prompt in prompts])

    def fake_make_sampler(*, temp, top_p):
        return {'temp': temp, 'top_p': top_p}

    monkeypatch.setattr(v1.MLXBackend, '_require_mlx_runtime', lambda self: (fake_mx, None, None, fake_batch_generate, fake_make_sampler))
    monkeypatch.setattr(v1.MLXBackend, '_load_model_and_tokenizer', lambda self: ('model', FakeTokenizer()))
    monkeypatch.setenv('MLX_EVAL_PROMPT_CHUNK_SIZE', '2')
    monkeypatch.setenv('MLX_EVAL_PREFILL_BATCH_SIZE', '2')
    monkeypatch.setenv('MLX_EVAL_COMPLETION_BATCH_SIZE', '2')

    backend = v1.MLXBackend(model_path='fake-model', adapter_path='fake-adapter')
    outputs = backend.generate(
        ['a', 'bb', 'ccc'],
        max_tokens=32,
        top_p=1.0,
        temperature=0.0,
        max_model_len=8192,
        seeds=[11, 12],
        max_num_seqs=64,
    )

    assert [len(call['prompts']) for call in batch_calls] == [2, 1, 2, 1]
    assert batch_calls[0]['kwargs']['prefill_batch_size'] == 2
    assert batch_calls[0]['kwargs']['completion_batch_size'] == 2
    assert fake_mx.random.seed_calls == [11, 12]
    assert fake_mx.clear_cache_calls == 4
    assert [[row.raw_output for row in group] for group in outputs] == [
        ['batched:1', 'batched:1'],
        ['batched:2', 'batched:2'],
        ['batched:3', 'batched:3'],
    ]
    assert [[row.seed for row in group] for group in outputs] == [[11, 12], [11, 12], [11, 12]]


def test_mlx_backend_sampling_path_reseeds_and_generates_in_process(monkeypatch):
    class FakeMXRandom:
        def __init__(self):
            self.current_seed = None
            self.seed_calls = []

        def seed(self, value):
            self.current_seed = value
            self.seed_calls.append(value)

    class FakeMX:
        def __init__(self):
            self.random = FakeMXRandom()
            self.clear_cache_calls = 0

        def clear_cache(self):
            self.clear_cache_calls += 1

    class FakeTokenizer:
        bos_token = None

        def encode(self, text, add_special_tokens=True):
            return [len(text), 1 if add_special_tokens else 0]

    fake_mx = FakeMX()
    generate_calls = []

    def fake_generate(model, tokenizer, prompt, **kwargs):
        generate_calls.append({'prompt': list(prompt), 'kwargs': kwargs, 'seed': fake_mx.random.current_seed})
        return f"seed={fake_mx.random.current_seed};prompt={prompt[0]}"

    def fake_make_sampler(*, temp, top_p):
        return {'temp': temp, 'top_p': top_p}

    monkeypatch.setattr(v1.MLXBackend, '_require_mlx_runtime', lambda self: (fake_mx, None, fake_generate, None, fake_make_sampler))
    monkeypatch.setattr(v1.MLXBackend, '_load_model_and_tokenizer', lambda self: ('model', FakeTokenizer()))

    backend = v1.MLXBackend(model_path='fake-model')
    outputs = backend.generate(
        ['hello', 'world'],
        max_tokens=16,
        top_p=0.9,
        temperature=0.7,
        max_model_len=2048,
        seeds=[3, 4],
        max_num_seqs=64,
    )

    assert fake_mx.random.seed_calls == [3, 4, 3, 4]
    assert len(generate_calls) == 4
    assert all(call['kwargs']['sampler'] == {'temp': 0.7, 'top_p': 0.9} for call in generate_calls)
    assert [[row.raw_output for row in group] for group in outputs] == [
        ['seed=3;prompt=5', 'seed=4;prompt=5'],
        ['seed=3;prompt=5', 'seed=4;prompt=5'],
    ]
    assert fake_mx.clear_cache_calls == 2
