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


class RecordingTokenizer:
    def __init__(self):
        self.calls = []

    def apply_chat_template(self, messages, *, tokenize, add_generation_prompt, enable_thinking):
        self.calls.append(
            {
                'messages': messages,
                'tokenize': tokenize,
                'add_generation_prompt': add_generation_prompt,
                'enable_thinking': enable_thinking,
            }
        )
        return (
            'PROMPT::'
            + messages[0]['content']
            + f'::agp={add_generation_prompt}::thinking={enable_thinking}'
        )


class FailingTokenizer:
    def apply_chat_template(self, messages, *, tokenize, add_generation_prompt, enable_thinking):
        raise RuntimeError('template failure')


def test_build_competition_prompt_records_expected_call_shape():
    tokenizer = RecordingTokenizer()
    config = v1.load_eval_config('official_lb')

    rendered = v1.build_competition_prompt(tokenizer, 'solve me', config)

    assert rendered == (
        'PROMPT::solve me\n'
        r'Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`'
        '::agp=True::thinking=True'
    )
    assert tokenizer.calls == [
        {
            'messages': [
                {
                    'role': 'user',
                    'content': (
                        'solve me\n'
                        r'Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`'
                    ),
                }
            ],
            'tokenize': False,
            'add_generation_prompt': True,
            'enable_thinking': True,
        }
    ]


def test_non_strict_prompt_builder_warns_and_falls_back():
    with pytest.warns(RuntimeWarning):
        rendered = v1.apply_competition_chat_template(
            FailingTokenizer(),
            'content',
            enable_thinking=True,
            add_generation_prompt=True,
            strict_chat_template=False,
        )
    assert rendered == 'content'


def test_replay_backend_and_evaluator_write_expected_reports(tmp_path):
    dataset = v1.pd.DataFrame(
        [
            {
                'id': 'prompt-1',
                'prompt': 'Compute 6 * 7.',
                'answer': '42',
                'family': 'symbol_equation',
                'answer_type': 'numeric',
            },
            {
                'id': 'prompt-2',
                'prompt': 'Write the Roman numeral for fourteen.',
                'answer': 'XIV',
                'family': 'roman_numeral',
                'answer_type': 'roman',
            },
        ]
    )
    replay_frame = v1.pd.DataFrame(
        [
            {'prompt_index': 0, 'id': 'prompt-1', 'sample_idx': 0, 'seed': 7, 'raw_output': r'Reasoning... \boxed{42}'},
            {'prompt_index': 0, 'id': 'prompt-1', 'sample_idx': 1, 'seed': 8, 'raw_output': r'Check again. \boxed{42}'},
            {
                'prompt_index': 0,
                'id': 'prompt-1',
                'sample_idx': 2,
                'seed': 9,
                'raw_output': r'Unsure. \boxed{41}' + '\nconfidence 0.91',
            },
            {'prompt_index': 1, 'id': 'prompt-2', 'sample_idx': 0, 'seed': 7, 'raw_output': 'Final answer: XIII'},
            {'prompt_index': 1, 'id': 'prompt-2', 'sample_idx': 1, 'seed': 8, 'raw_output': 'Final answer: XIII'},
            {'prompt_index': 1, 'id': 'prompt-2', 'sample_idx': 2, 'seed': 9, 'raw_output': 'Final answer: XIV'},
        ]
    )

    backend = v1.ReplayBackend(replay_frame)
    config = replace(v1.load_eval_config('official_lb'), n_samples_per_prompt=3, seed=7, seed_stride=1)

    out_dir = tmp_path / 'eval-output'
    artifacts = v1.evaluate_dataset(
        dataset,
        backend,
        config,
        out_dir,
        tokenizer=v1.BuiltinCompetitionTokenizer(),
        run_name='replay-smoke',
        dataset_name='toy-eval',
    )

    row_level = artifacts.row_level
    assert list(row_level['id']) == ['prompt-1', 'prompt-1', 'prompt-1', 'prompt-2', 'prompt-2', 'prompt-2']
    assert list(row_level['extraction_source']) == [
        'boxed',
        'boxed',
        'boxed',
        'final_answer_colon',
        'final_answer_colon',
        'final_answer_colon',
    ]
    assert list(row_level['format_bucket']) == [
        'clean_boxed',
        'clean_boxed',
        'extra_trailing_numbers',
        'clean_final_answer',
        'clean_final_answer',
        'clean_final_answer',
    ]
    assert list(row_level['is_correct']) == [True, True, False, False, False, True]
    assert row_level.loc[row_level['sample_idx'] == 2, 'contains_extra_numbers'].tolist() == [True, False]

    summary = artifacts.summary.iloc[0].to_dict()
    assert summary['run_name'] == 'replay-smoke'
    assert summary['backend_name'] == 'replay'
    assert summary['eval_mode'] == 'official_lb'
    assert summary['dataset_name'] == 'toy-eval'
    assert summary['n_rows'] == 2
    assert summary['n_samples_per_prompt'] == 3
    assert summary['overall_acc'] == pytest.approx(0.5)
    assert summary['majority_acc'] == pytest.approx(0.5)
    assert summary['pass_at_k'] == pytest.approx(1.0)
    assert summary['extraction_fail_rate'] == pytest.approx(0.0)
    assert summary['format_fail_rate'] == pytest.approx(1 / 6)
    assert summary['boxed_rate'] == pytest.approx(0.5)

    family_metrics = artifacts.family_metrics.set_index('family')
    assert family_metrics.loc['symbol_equation', 'acc'] == pytest.approx(2 / 3)
    assert family_metrics.loc['symbol_equation', 'majority_acc'] == pytest.approx(1.0)
    assert family_metrics.loc['roman_numeral', 'acc'] == pytest.approx(1 / 3)
    assert family_metrics.loc['roman_numeral', 'pass_at_k'] == pytest.approx(1.0)

    failure_metrics = artifacts.failure_metrics.set_index('format_bucket')
    assert failure_metrics.loc['clean_final_answer', 'n'] == 3
    assert failure_metrics.loc['clean_boxed', 'n'] == 2
    assert failure_metrics.loc['extra_trailing_numbers', 'n'] == 1
    assert failure_metrics.loc['extra_trailing_numbers', 'ratio'] == pytest.approx(1 / 6)

    assert (out_dir / 'row_level.parquet').exists()
    assert (out_dir / 'summary.csv').exists()
    assert (out_dir / 'family_metrics.csv').exists()
    assert (out_dir / 'failure_metrics.csv').exists()
