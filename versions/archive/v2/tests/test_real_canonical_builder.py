from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v2_train_real_canonical', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v2_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v2_train
SPEC.loader.exec_module(v2_train)


def _base_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        'id': 'base',
        'prompt': 'placeholder',
        'answer': '0',
        'family': 'roman_numeral',
        'subfamily': 'base',
        'answer_type': 'roman',
        'parse_ok': True,
        'num_examples': 4,
        'query_raw': '1',
        'group_signature': 'sig',
        'hard_score': 1.0,
        'risk_bin': 'risk_low',
        'contains_right_brace': False,
        'contains_backslash': False,
        'contains_backtick': False,
        'estimated_g': float('nan'),
        'estimated_ratio': float('nan'),
        'roman_query_value': float('nan'),
        'bit_query_binary': float('nan'),
        'query_hamming_bin': 'mid',
        'g_bin': float('nan'),
        'answer_decimal_style': 2,
        'ratio_bin': 'unknown',
        'near_round_boundary': False,
        'boxed_safe': True,
        'is_holdout_hard': False,
    }
    row.update(overrides)
    return row


def test_build_real_canonical_writes_expected_columns(tmp_path: Path) -> None:
    splits = pd.DataFrame(
        [
            _base_row(
                id='roman-1',
                prompt='11 -> XI\nNow, write the number 38 in Roman numerals.',
                answer='xxxviii',
                family='roman_numeral',
                subfamily='additive',
                answer_type='roman',
                query_raw='38',
                roman_query_value=38.0,
                group_signature='decade3__sub0',
            ),
            _base_row(
                id='gravity-1',
                prompt='For t = 1.00s, distance = 5.00 m\nNow, determine the falling distance for t = 4.41s.',
                answer='154.62',
                family='gravity_constant',
                subfamily='g16',
                answer_type='numeric',
                query_raw='4.41',
                estimated_g=15.9,
                g_bin=16.0,
                hard_score=8.0,
                risk_bin='risk_high',
                near_round_boundary=True,
                is_holdout_hard=True,
                group_signature='gbin16__dec2',
            ),
            _base_row(
                id='unit-1',
                prompt='10.08 m becomes 6.69\nNow, convert the following measurement: 25.09 m',
                answer='16.65',
                family='unit_conversion',
                subfamily='ratio_lt1',
                answer_type='numeric',
                query_raw='25.09',
                estimated_ratio=0.6635983263,
                ratio_bin='lt1',
                group_signature='rbinlt1__qbin2',
            ),
            _base_row(
                id='bit-1',
                prompt='Examples:\n00000000 -> 11111111\n00001111 -> 11110000\n11110000 -> 00001111\nNow, determine the output for: 00110011',
                answer='11001100',
                family='bit_manipulation',
                subfamily='not',
                answer_type='binary8',
                query_raw='00110011',
                bit_query_binary='00110011',
                query_hamming_bin='mid',
                group_signature='unknown__ex3__qhwmid',
            ),
        ]
    )
    metadata = pd.DataFrame({'id': splits['id']})
    splits_path = tmp_path / 'splits.parquet'
    metadata_path = tmp_path / 'metadata.parquet'
    output_path = tmp_path / 'real_canonical.parquet'
    splits.to_parquet(splits_path, index=False)
    metadata.to_parquet(metadata_path, index=False)

    args = SimpleNamespace(
        splits_path=str(splits_path),
        metadata_path=str(metadata_path),
        train_csv_path=str(tmp_path / 'train.csv'),
        config_path=str(v2_train.DEFAULT_REAL_CANONICAL_CONFIG_PATH),
        output_path=str(output_path),
    )

    v2_train.run_build_real_canonical(args)
    result = pd.read_parquet(output_path)

    assert len(result) == 4
    assert set(result['source_kind']) == {'real'}
    assert result['importance_prior'].between(0.0, 1.0).all()
    assert result['importance_prior'].max() == 1.0

    roman = result.loc[result['family'] == 'roman_numeral'].iloc[0]
    assert roman['answer_canonical'] == 'XXXVIII'
    assert roman['format_policy'] == 'boxed_final_line'

    gravity = result.loc[result['family'] == 'gravity_constant'].iloc[0]
    gravity_tags = json.loads(gravity['difficulty_tags'])
    assert {'very_hard', 'holdout_hard', 'near_round_boundary', 'risky'} <= set(gravity_tags)
    assert gravity['generator_ready']

    unit = result.loc[result['family'] == 'unit_conversion'].iloc[0]
    assert {'core', 'distill', 'format_sharpening'} <= set(json.loads(unit['eligible_pools']))

    bit = result.loc[result['family'] == 'bit_manipulation'].iloc[0]
    assert bit['answer_canonical'] == '11001100'
    assert bool(bit['generator_ready']) is True
    assert len(bit['rule_spec_hash']) == 16
    assert bit['train_sample_weight'] > 0
