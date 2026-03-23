from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import sys

import pandas as pd
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


def make_probe_dataset():
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


def make_probe_replay():
    return v1.pd.DataFrame(
        [
            {'prompt_index': 0, 'id': 'p1', 'sample_idx': 0, 'seed': 1001, 'raw_output': r'\\boxed{42}'},
            {'prompt_index': 0, 'id': 'p1', 'sample_idx': 1, 'seed': 1002, 'raw_output': 'Final answer: 42'},
            {'prompt_index': 0, 'id': 'p1', 'sample_idx': 2, 'seed': 1003, 'raw_output': '42'},
            {'prompt_index': 0, 'id': 'p1', 'sample_idx': 3, 'seed': 1004, 'raw_output': 'Final answer: 41'},
            {'prompt_index': 1, 'id': 'p2', 'sample_idx': 0, 'seed': 1001, 'raw_output': 'Final answer: XIII'},
            {'prompt_index': 1, 'id': 'p2', 'sample_idx': 1, 'seed': 1002, 'raw_output': 'Final answer: XIII'},
            {'prompt_index': 1, 'id': 'p2', 'sample_idx': 2, 'seed': 1003, 'raw_output': 'XIV'},
            {'prompt_index': 1, 'id': 'p2', 'sample_idx': 3, 'seed': 1004, 'raw_output': 'XV'},
        ]
    )


def make_det_row_level():
    return pd.DataFrame(
        [
            {'id': 'p1', 'sample_idx': 0, 'seed': 0, 'extracted_answer': '42'},
            {'id': 'p2', 'sample_idx': 0, 'seed': 0, 'extracted_answer': 'XIV'},
        ]
    )


def test_probe_metrics_and_reproducibility(tmp_path):
    dataset = make_probe_dataset()
    replay = make_probe_replay()
    config = v1.load_eval_config('sc_probe_k4')

    run1 = v1.evaluate_dataset(
        dataset,
        v1.ReplayBackend(replay),
        config,
        tmp_path / 'probe1',
        run_name='probe-1',
        dataset_name='shadow',
    )
    probe1 = v1.build_probe_metrics_frame(run1.row_level, det_row_level=make_det_row_level())
    sample1 = v1.build_sample_level_frame(run1.row_level)

    run2 = v1.evaluate_dataset(
        dataset,
        v1.ReplayBackend(replay),
        config,
        tmp_path / 'probe2',
        run_name='probe-2',
        dataset_name='shadow',
    )
    probe2 = v1.build_probe_metrics_frame(run2.row_level, det_row_level=make_det_row_level())

    assert v1.stable_dataframe_hash(sample1, ['id', 'sample_idx', 'seed', 'extracted_answer']) == v1.stable_dataframe_hash(
        v1.build_sample_level_frame(run2.row_level),
        ['id', 'sample_idx', 'seed', 'extracted_answer'],
    )
    assert v1.stable_dataframe_hash(probe1, ['id', 'majority_answer', 'pass_at_k']) == v1.stable_dataframe_hash(
        probe2,
        ['id', 'majority_answer', 'pass_at_k'],
    )

    probe_by_id = probe1.set_index('id')
    assert probe_by_id.loc['p1', 'pass_at_k']
    assert probe_by_id.loc['p1', 'majority_answer'] == '42'
    assert probe_by_id.loc['p1', 'majority_correct']
    assert probe_by_id.loc['p1', 'det_answer_in_probe_set']
    assert probe_by_id.loc['p1', 'n_correct'] == 3
    assert probe_by_id.loc['p2', 'pass_at_k']
    assert probe_by_id.loc['p2', 'majority_answer'] in {'XIII', 'XIV'}

    summary = v1.augment_summary_for_probe(run1.summary, probe1).iloc[0].to_dict()
    assert summary['pass_at_k'] == pytest.approx(1.0)
    assert summary['majority_acc'] == pytest.approx(0.5)
    assert summary['mean_consensus_rate'] == pytest.approx(0.625)
    assert summary['format_safe_correct_rate'] == pytest.approx(0.5)

    family_metrics = v1.augment_family_metrics_for_probe(run1.family_metrics, probe1)
    assert set(family_metrics.columns) >= {'mean_consensus_rate', 'format_safe_correct_rate', 'shortest_correct_avg_len'}


def test_oracle_replay_avoids_boxed_for_answers_with_closing_brace():
    dataset = v1.pd.DataFrame(
        [
            {
                'id': 'unsafe',
                'prompt': 'Transform symbols.',
                'answer': '+}',
            }
        ]
    )
    replay = v1.build_oracle_replay_frame(dataset, seeds=[1001, 1002, 1003], mode='probe')
    assert replay.loc[0, 'raw_output'] == 'Final answer: +}'
    assert not replay['raw_output'].str.contains(r'\\\\boxed\{\+\}\}', regex=True).any()
