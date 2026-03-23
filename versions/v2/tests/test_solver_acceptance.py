from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v2_train_solver_acceptance', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v2_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v2_train
SPEC.loader.exec_module(v2_train)


def _canonical_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        'id': 'row',
        'family': 'roman_numeral',
        'subfamily': 'base',
        'prompt': '11 -> XI\nNow convert 7.',
        'answer': 'VII',
        'answer_canonical': 'VII',
        'answer_type': 'roman',
        'format_policy': 'boxed_final_line',
        'generator_ready': True,
        'estimated_g': float('nan'),
        'estimated_ratio': float('nan'),
        'roman_query_value': float('nan'),
        'bit_query_binary': float('nan'),
        'query_raw': '7',
        'num_examples': 3,
        'difficulty_tags': '["medium"]',
        'format_risk_flags': '{}',
        'importance_prior': 0.7,
        'train_sample_weight': 1.2,
        'eligible_pools': '["core", "distill"]',
    }
    row.update(overrides)
    return row


def test_solver_registry_and_synthetic_builders(tmp_path: Path) -> None:
    canonical = pd.DataFrame(
        [
            _canonical_row(id='roman-1', family='roman_numeral', query_raw='7', roman_query_value=7.0, answer='VII', answer_canonical='VII'),
            _canonical_row(
                id='gravity-1',
                family='gravity_constant',
                answer_type='numeric',
                prompt='For t = 1.00s, distance = 5.00 m\nNow determine the falling distance for t = 4.41s.',
                answer='154.62',
                answer_canonical='154.62',
                format_policy='final_answer_colon',
                estimated_g=15.9,
                query_raw='4.41',
            ),
            _canonical_row(
                id='unit-1',
                family='unit_conversion',
                answer_type='numeric',
                prompt='10.08 m becomes 6.69\nNow convert 25.09 m',
                answer='16.65',
                answer_canonical='16.65',
                format_policy='final_answer_colon',
                estimated_ratio=0.6635983263,
                query_raw='25.09',
            ),
            _canonical_row(
                id='bit-1',
                family='bit_manipulation',
                answer_type='binary8',
                prompt='Examples:\n00000000 -> 11111111\n00001111 -> 11110000\n11110000 -> 00001111\nNow determine the output for: 00110011',
                answer='11001100',
                answer_canonical='11001100',
                format_policy='final_answer_colon',
                bit_query_binary='00110011',
                query_raw='00110011',
            ),
        ]
    )
    canonical_path = tmp_path / 'canonical.parquet'
    canonical.to_parquet(canonical_path, index=False)

    solver_registry_path = tmp_path / 'solver_registry.json'
    v2_train.run_build_solver_registry(
        SimpleNamespace(real_canonical_path=str(canonical_path), output_path=str(solver_registry_path))
    )
    registry = json.loads(solver_registry_path.read_text(encoding='utf-8'))
    assert registry['family_stats']['roman_numeral']['generator_ready'] == 1
    assert registry['families']['bit_manipulation']['support'] == 'exact_fit'

    synth_core_config = tmp_path / 'synth_core.yaml'
    synth_hard_config = tmp_path / 'synth_hard.yaml'
    synth_config = {
        'seed': 42,
        'max_per_parent': 2,
        'families_enabled': {
            'roman_numeral': True,
            'gravity_constant': True,
            'unit_conversion': True,
            'bit_manipulation': True,
        },
    }
    synth_core_config.write_text(yaml.safe_dump(synth_config), encoding='utf-8')
    synth_config['seed'] = 43
    synth_hard_config.write_text(yaml.safe_dump(synth_config), encoding='utf-8')

    synth_core_output = tmp_path / 'synth_core.parquet'
    synth_hard_output = tmp_path / 'synth_hard.parquet'
    synthetic_registry_path = tmp_path / 'synthetic_registry.parquet'

    v2_train.run_build_synth_core(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            solver_registry_path=str(solver_registry_path),
            config_path=str(synth_core_config),
            output_path=str(synth_core_output),
            registry_path=str(synthetic_registry_path),
        )
    )
    core_df = pd.read_parquet(synth_core_output)
    core_registry = pd.read_parquet(synthetic_registry_path)
    assert not core_df.empty
    assert set(core_df['accepted_by']) == {'all_gates'}
    assert core_registry['dedup_hash'].is_unique

    v2_train.run_build_synth_hard(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            solver_registry_path=str(solver_registry_path),
            config_path=str(synth_hard_config),
            output_path=str(synth_hard_output),
            registry_path=str(synthetic_registry_path),
        )
    )
    hard_df = pd.read_parquet(synth_hard_output)
    combined_registry = pd.read_parquet(synthetic_registry_path)
    assert not hard_df.empty
    assert len(combined_registry) >= len(core_registry)
    assert set(hard_df['family']) <= {'roman_numeral', 'gravity_constant', 'unit_conversion', 'bit_manipulation'}


def test_parser_wires_new_functions() -> None:
    parser = v2_train.build_parser()
    assert parser.parse_args(['build-real-canonical']).func is v2_train.run_build_real_canonical
    assert parser.parse_args(['build-synth-core']).func is v2_train.run_build_synth_core
    assert parser.parse_args(['train-sft']).func is v2_train.run_train_sft
