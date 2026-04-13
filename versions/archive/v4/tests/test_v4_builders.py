from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v4_train_builders', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v4_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v4_train
SPEC.loader.exec_module(v4_train)


def _write_preference_source(path: Path) -> None:
    pd.DataFrame(
        [
            {
                'pair_id': 'fmt-1',
                'pair_kind': 'format',
                'source_id': 'src-1',
                'family': 'text_decryption',
                'prompt': 'Decode the text.',
                'chosen_output': r'\boxed{CAB}',
                'rejected_output': 'CAB',
                'chosen_format_bucket': 'clean_boxed',
                'rejected_format_bucket': 'plain',
                'chosen_is_correct': True,
                'rejected_is_correct': True,
                'preference_reason': 'prefer clean formatting',
            },
            {
                'pair_id': 'corr-1',
                'pair_kind': 'correction',
                'source_id': 'src-2',
                'family': 'bit_manipulation',
                'prompt': 'Invert 010.',
                'chosen_output': r'\boxed{101}',
                'rejected_output': r'\boxed{111}',
                'chosen_format_bucket': 'clean_boxed',
                'rejected_format_bucket': 'clean_boxed',
                'chosen_is_correct': True,
                'rejected_is_correct': False,
                'preference_reason': 'prefer correct answer',
            },
        ]
    ).to_parquet(path, index=False)


def test_build_v4_preference_pairs_and_stage_c_mix(tmp_path: Path, monkeypatch) -> None:
    preference_source = tmp_path / 'preference_pairs_v3.parquet'
    _write_preference_source(preference_source)

    canonical_path = tmp_path / 'canonical.parquet'
    pd.DataFrame(
        [
            {
                'id': 'src-1',
                'difficulty_tags': 'format',
                'importance_prior': 1.2,
                'hard_score': 1.0,
                'cv5_fold': 0,
                'format_policy': 'boxed',
            },
            {
                'id': 'src-2',
                'difficulty_tags': 'bit',
                'importance_prior': 2.0,
                'hard_score': 4.0,
                'cv5_fold': 1,
                'format_policy': 'boxed',
            },
        ]
    ).to_parquet(canonical_path, index=False)

    monkeypatch.setattr(v4_train, 'DEFAULT_V2_REAL_CANONICAL_PATH', canonical_path)
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_EXPERIMENT_LOG_PATH', tmp_path / 'experiment_log.jsonl')

    format_cfg = tmp_path / 'preference_format.yaml'
    format_cfg.write_text(yaml.safe_dump({'input_path': str(preference_source), 'pair_kind': 'format'}), encoding='utf-8')
    format_output = tmp_path / 'format_pairs_v4.parquet'
    registry_output = tmp_path / 'preference_registry_v4.parquet'
    v4_train.run_build_format_preferences_v4(
        SimpleNamespace(
            config_path=str(format_cfg),
            input_path=None,
            output_path=str(format_output),
            registry_path=str(registry_output),
        )
    )

    correctness_cfg = tmp_path / 'preference_correctness.yaml'
    correctness_cfg.write_text(
        yaml.safe_dump({'input_path': str(preference_source), 'pair_kind': 'correction', 'allowed_families': ['bit_manipulation']}),
        encoding='utf-8',
    )
    correctness_output = tmp_path / 'correctness_pairs_v4.parquet'
    v4_train.run_build_correctness_preferences_v4(
        SimpleNamespace(
            config_path=str(correctness_cfg),
            input_path=None,
            output_path=str(correctness_output),
            registry_path=str(registry_output),
        )
    )

    format_df = pd.read_parquet(format_output)
    correctness_df = pd.read_parquet(correctness_output)
    registry_df = pd.read_parquet(registry_output)
    assert list(format_df['pair_type'].unique()) == ['format']
    assert list(correctness_df['pair_type'].unique()) == ['correction']
    assert set(registry_df['pair_id']) == {'fmt-1', 'corr-1'}

    rft_rows = [
        {
            'id': 'eq-1',
            'sample_idx': 0,
            'seed': 7,
            'prompt': 'Solve x+2=5.',
            'answer': 'x=3',
            'gold_answer': 'x=3',
            'family': 'symbol_equation',
            'cv5_fold': 0,
            'raw_output': r'\boxed{x=3}',
            'raw_output_len_chars': 12,
            'extracted_answer': 'x=3',
            'format_bucket': 'clean_boxed',
            'contains_extra_numbers': False,
            'is_correct': True,
        },
        {
            'id': 'eq-1',
            'sample_idx': 1,
            'seed': 11,
            'prompt': 'Solve x+2=5.',
            'answer': 'x=3',
            'gold_answer': 'x=3',
            'family': 'symbol_equation',
            'cv5_fold': 0,
            'raw_output': 'Reasoning\n' + r'\boxed{x=3}',
            'raw_output_len_chars': 22,
            'extracted_answer': 'x=3',
            'format_bucket': 'clean_boxed',
            'contains_extra_numbers': False,
            'is_correct': True,
        },
        {
            'id': 'bit-1',
            'sample_idx': 0,
            'seed': 7,
            'prompt': 'Invert 010.',
            'answer': '101',
            'gold_answer': '101',
            'family': 'bit_manipulation',
            'cv5_fold': 1,
            'raw_output': r'\boxed{111}',
            'raw_output_len_chars': 12,
            'extracted_answer': '111',
            'format_bucket': 'clean_boxed',
            'contains_extra_numbers': False,
            'is_correct': False,
        },
    ]
    rft_input = tmp_path / 'rft_candidate_generations_v4.jsonl'
    rft_input.write_text('\n'.join(json.dumps(row) for row in rft_rows) + '\n', encoding='utf-8')
    rft_cfg = tmp_path / 'rft_accept_pool.yaml'
    rft_cfg.write_text(yaml.safe_dump({'dummy': True}), encoding='utf-8')
    accept_pool = tmp_path / 'rft_accept_pool_v4.parquet'
    rft_registry = tmp_path / 'rft_registry_v4.parquet'
    v4_train.run_filter_rft_accept_pool_v4(
        SimpleNamespace(
            config_path=str(rft_cfg),
            input_path=str(rft_input),
            output_path=str(accept_pool),
            registry_path=str(rft_registry),
            audit_output_path=str(tmp_path / 'rft_audit.csv'),
        )
    )

    accept_df = pd.read_parquet(accept_pool)
    registry_rft_df = pd.read_parquet(rft_registry)
    assert len(accept_df) == 1
    assert accept_df.iloc[0]['chosen_output'] == r'\boxed{x=3}'
    assert set(registry_rft_df['status']) == {'accepted', 'rejected'}

    replay_path = tmp_path / 'stage_a_replay.parquet'
    pd.DataFrame(
        [
            {'id': 'replay-1', 'prompt': 'Compute 1+1.', 'answer': '2', 'family': 'symbol_equation', 'format_policy': 'boxed', 'sample_weight': 1.0},
            {'id': 'replay-2', 'prompt': 'Compute 2+2.', 'answer': '4', 'family': 'symbol_equation', 'format_policy': 'boxed', 'sample_weight': 1.0},
            {'id': 'replay-3', 'prompt': 'Compute 3+3.', 'answer': '6', 'family': 'symbol_equation', 'format_policy': 'boxed', 'sample_weight': 1.0},
        ]
    ).to_parquet(replay_path, index=False)

    stage_c_rft_cfg = tmp_path / 'stage_c_rft_mix.yaml'
    stage_c_rft_cfg.write_text(
        yaml.safe_dump({'target_total': 4, 'rft_ratio': 0.5, 'replay_ratio': 0.5, 'replay_source_path': str(replay_path)}),
        encoding='utf-8',
    )
    stage_c_pref_cfg = tmp_path / 'stage_c_preference_mix.yaml'
    stage_c_pref_cfg.write_text(yaml.safe_dump({'target_total_pairs': 2, 'format_ratio': 0.5, 'correctness_ratio': 0.5}), encoding='utf-8')
    rft_mix_output = tmp_path / 'stage_c_rft_mix_v4.parquet'
    pref_mix_output = tmp_path / 'stage_c_preference_mix_v4.parquet'
    v4_train.run_build_stage_c_mix_v4(
        SimpleNamespace(
            rft_config_path=str(stage_c_rft_cfg),
            preference_config_path=str(stage_c_pref_cfg),
            rft_accept_pool_path=str(accept_pool),
            format_pairs_path=str(format_output),
            correctness_pairs_path=str(correctness_output),
            rft_output_path=str(rft_mix_output),
            preference_output_path=str(pref_mix_output),
        )
    )

    rft_mix_df = pd.read_parquet(rft_mix_output)
    pref_mix_df = pd.read_parquet(pref_mix_output)
    assert len(rft_mix_df) >= 2
    assert len(pref_mix_df) == 2
