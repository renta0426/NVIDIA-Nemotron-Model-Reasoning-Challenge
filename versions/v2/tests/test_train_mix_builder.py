from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v2_train_mix_builder', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v2_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v2_train
SPEC.loader.exec_module(v2_train)


def test_build_train_mix_combines_available_sources(tmp_path: Path, monkeypatch) -> None:
    real_df = pd.DataFrame(
        [
            {'id': 'real-1', 'family': 'roman_numeral', 'prompt': 'p1', 'answer': 'I', 'answer_type': 'roman', 'format_policy': 'boxed_final_line', 'train_sample_weight': 1.0},
            {'id': 'real-2', 'family': 'gravity_constant', 'prompt': 'p2', 'answer': '2.00', 'answer_type': 'numeric', 'format_policy': 'final_answer_colon', 'train_sample_weight': 1.2},
            {'id': 'real-3', 'family': 'unit_conversion', 'prompt': 'p3', 'answer': '3.00', 'answer_type': 'numeric', 'format_policy': 'final_answer_colon', 'train_sample_weight': 0.9},
        ]
    )
    real_path = tmp_path / 'real.parquet'
    real_df.to_parquet(real_path, index=False)

    synthetic_registry = pd.DataFrame(
        [
            {'synthetic_id': 'core-1', 'family': 'roman_numeral', 'prompt': 'cp1', 'answer': 'II', 'answer_type': 'roman', 'format_policy': 'boxed_final_line', 'train_sample_weight': 1.1, 'accepted_by': 'all_gates', 'seed': 42},
            {'synthetic_id': 'core-2', 'family': 'gravity_constant', 'prompt': 'cp2', 'answer': '4.00', 'answer_type': 'numeric', 'format_policy': 'final_answer_colon', 'train_sample_weight': 1.1, 'accepted_by': 'all_gates', 'seed': 42},
            {'synthetic_id': 'hard-1', 'family': 'bit_manipulation', 'prompt': 'hp1', 'answer': '00001111', 'answer_type': 'binary8', 'format_policy': 'final_answer_colon', 'train_sample_weight': 1.4, 'accepted_by': 'all_gates', 'seed': 43},
        ]
    )
    synthetic_registry_path = tmp_path / 'synthetic_registry.parquet'
    synthetic_registry.to_parquet(synthetic_registry_path, index=False)

    distill_path = tmp_path / 'distill.parquet'
    pd.DataFrame(
        [{'trace_id': 'trace-1', 'family': 'roman_numeral', 'prompt': 'dp1', 'answer': 'III', 'answer_type': 'roman', 'format_policy': 'boxed_final_line', 'raw_output': 'Final answer: III'}]
    ).to_parquet(distill_path, index=False)
    synth_format_path = tmp_path / 'synth_format.parquet'
    pd.DataFrame(
        [{'pair_id': 'fmt-1', 'family': 'gravity_constant', 'chosen': 'Final answer: 2.00', 'format_policy': 'final_answer_colon'}]
    ).to_parquet(synth_format_path, index=False)
    correction_path = tmp_path / 'correction.parquet'
    pd.DataFrame(
        [{'pair_id': 'corr-1', 'family': 'bit_manipulation', 'prompt': 'bp1', 'chosen_output': 'Final answer: 00001111'}]
    ).to_parquet(correction_path, index=False)

    monkeypatch.setattr(v2_train, 'DEFAULT_DISTILLED_TRACES_OUTPUT_PATH', distill_path)
    monkeypatch.setattr(v2_train, 'DEFAULT_SYNTH_FORMAT_OUTPUT_PATH', synth_format_path)
    monkeypatch.setattr(v2_train, 'DEFAULT_CORRECTION_PAIRS_OUTPUT_PATH', correction_path)

    stage_a_config = tmp_path / 'mix_stage_a.yaml'
    stage_b_config = tmp_path / 'mix_stage_b.yaml'
    stage_a_config.write_text(
        yaml.safe_dump(
            {
                'name': 'stage_a_core',
                'stage': 'a',
                'seed': 11,
                'target_total': 6,
                'mix_ratios': {'real': 0.5, 'core_synth': 0.3333333333, 'distill': 0.1666666667},
                'family_weights': {'roman_numeral': 1.0, 'gravity_constant': 1.2, 'unit_conversion': 0.9},
            }
        ),
        encoding='utf-8',
    )
    stage_b_config.write_text(
        yaml.safe_dump(
            {
                'name': 'stage_b_hardening',
                'stage': 'b',
                'seed': 22,
                'target_total': 6,
                'mix_ratios': {
                    'real': 0.34,
                    'core_synth': 0.16,
                    'hard_synth': 0.17,
                    'format_synth': 0.17,
                    'correction': 0.16,
                },
                'family_weights': {'bit_manipulation': 1.3, 'gravity_constant': 1.1, 'roman_numeral': 1.0},
            }
        ),
        encoding='utf-8',
    )

    stage_a_output = tmp_path / 'stage_a.parquet'
    stage_b_output = tmp_path / 'stage_b.parquet'
    hard_only_output = tmp_path / 'stage_b_hard_only.parquet'
    registry_output = tmp_path / 'train_mix_registry.parquet'

    v2_train.run_build_train_mix(
        SimpleNamespace(
            real_canonical_path=str(real_path),
            synthetic_registry_path=str(synthetic_registry_path),
            stage_a_config_path=str(stage_a_config),
            stage_b_config_path=str(stage_b_config),
            stage_a_output_path=str(stage_a_output),
            stage_b_output_path=str(stage_b_output),
            hard_only_output_path=str(hard_only_output),
            registry_path=str(registry_output),
        )
    )

    stage_a_df = pd.read_parquet(stage_a_output)
    stage_b_df = pd.read_parquet(stage_b_output)
    hard_only_df = pd.read_parquet(hard_only_output)
    registry_df = pd.read_parquet(registry_output)

    assert not stage_a_df.empty
    assert not stage_b_df.empty
    assert set(hard_only_df['source_dataset']) <= {'hard_synth', 'correction'}
    assert {'stage_a_core', 'stage_b_hardening'} <= set(registry_df['mix_name'])
    assert {'real', 'core_synth', 'distill'} <= set(stage_a_df['source_dataset'])
