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


def test_mlx_backend_raises_clear_error_when_runtime_missing():
    backend = v1.MLXBackend(model_path='missing-model')
    with pytest.raises(RuntimeError, match='mlx-lm'):
        backend.generate(['prompt'], max_tokens=8, top_p=1.0, temperature=0.0, max_model_len=1024, seeds=[0])
