from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_mix_builder', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_build_train_mix_combines_available_sources_and_logs_rejections(tmp_path: Path) -> None:
    real_df = pd.DataFrame(
        [
            {'id': 'real-1', 'family': 'roman_numeral', 'prompt': 'p1', 'answer': 'I', 'answer_type': 'roman', 'format_policy': 'boxed', 'train_sample_weight': 1.0},
            {'id': 'real-2', 'family': 'gravity_constant', 'prompt': 'p2', 'answer': '2.00', 'answer_type': 'numeric', 'format_policy': 'boxed', 'train_sample_weight': 1.2},
        ]
    )
    real_path = tmp_path / 'real.parquet'
    real_df.to_parquet(real_path, index=False)

    core_df = pd.DataFrame(
        [
            {'source_id': 'core-1', 'family': 'roman_numeral', 'prompt': 'cp1', 'answer': 'II', 'answer_type': 'roman', 'format_policy': 'boxed', 'train_sample_weight': 1.1},
            {'source_id': 'core-2', 'family': 'gravity_constant', 'prompt': 'cp2', 'answer': '4.00', 'answer_type': 'numeric', 'format_policy': 'boxed', 'train_sample_weight': 1.1},
        ]
    )
    core_path = tmp_path / 'core.parquet'
    core_df.to_parquet(core_path, index=False)

    hard_path = tmp_path / 'hard.parquet'
    pd.DataFrame(
        [{'source_id': 'hard-1', 'family': 'bit_manipulation', 'prompt': 'hp1', 'answer': '00001111', 'answer_type': 'binary8', 'format_policy': 'boxed', 'train_sample_weight': 1.4}]
    ).to_parquet(hard_path, index=False)

    distill_path = tmp_path / 'distill.parquet'
    pd.DataFrame(
        [
            {
                'source_id': 'distill-1',
                'trace_id': 'trace-1',
                'family': 'roman_numeral',
                'prompt': 'dp1',
                'answer': 'III',
                'answer_type': 'roman',
                'format_policy': 'boxed',
                'target_text': 'Reasoning only',
            }
        ]
    ).to_parquet(distill_path, index=False)
    format_path = tmp_path / 'format.parquet'
    pd.DataFrame(
        [{'pair_id': 'fmt-1', 'family': 'gravity_constant', 'prompt': 'fp1', 'answer': '2.00', 'chosen_output': '\\boxed{2.00}', 'format_policy': 'boxed'}]
    ).to_parquet(format_path, index=False)
    correction_path = tmp_path / 'correction.parquet'
    pd.DataFrame(
        [{'pair_id': 'corr-1', 'family': 'bit_manipulation', 'prompt': 'bp1', 'chosen_output': '\\boxed{00001111}', 'format_policy': 'boxed'}]
    ).to_parquet(correction_path, index=False)

    stage_a_config = tmp_path / 'mix_stage_a.yaml'
    stage_b_config = tmp_path / 'mix_stage_b.yaml'
    stage_a_config.write_text(
        yaml.safe_dump(
            {
                'name': 'stage_a_core',
                'stage': 'a',
                'seed': 11,
                'target_total': 6,
                'mix_ratios': {'real': 0.34, 'core_synth': 0.33, 'distill': 0.33},
                'family_weights': {'roman_numeral': 1.0, 'gravity_constant': 1.2},
                'weight_profile_name': 'unit_test',
                'rationale_weight': 1.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {'roman_numeral': 4.0, 'gravity_constant': 4.0},
                'drop_invalid_weighted_rows': True,
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
                'target_total': 10,
                'mix_ratios': {
                    'real': 0.20,
                    'core_synth': 0.20,
                    'hard_synth': 0.20,
                    'format': 0.20,
                    'correction': 0.20,
                },
                'family_weights': {'bit_manipulation': 1.3, 'gravity_constant': 1.1, 'roman_numeral': 1.0},
                'weight_profile_name': 'unit_test',
                'rationale_weight': 1.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {'bit_manipulation': 5.0, 'gravity_constant': 4.0, 'roman_numeral': 4.0},
                'drop_invalid_weighted_rows': True,
            }
        ),
        encoding='utf-8',
    )

    stage_a_output = tmp_path / 'stage_a.parquet'
    stage_b_output = tmp_path / 'stage_b.parquet'
    registry_output = tmp_path / 'train_mix_registry.parquet'

    v3_train.run_build_train_mix_v3(
        SimpleNamespace(
            real_canonical_path=str(real_path),
            core_synth_path=str(core_path),
            hard_synth_path=str(hard_path),
            distilled_traces_path=str(distill_path),
            format_pairs_path=str(format_path),
            correction_pairs_path=str(correction_path),
            stage_a_config_path=str(stage_a_config),
            stage_b_config_path=str(stage_b_config),
            stage_a_output_path=str(stage_a_output),
            stage_b_output_path=str(stage_b_output),
            registry_path=str(registry_output),
        )
    )

    stage_a_df = pd.read_parquet(stage_a_output)
    stage_b_df = pd.read_parquet(stage_b_output)
    registry_df = pd.read_parquet(registry_output)

    assert not stage_a_df.empty
    assert not stage_b_df.empty
    assert {'stage_a_core', 'stage_b_hardening'} <= set(registry_df['mix_name'])
    assert {'real', 'core_synth'} <= set(stage_a_df['source_dataset'])
    assert {'real', 'core_synth', 'hard_synth', 'format', 'correction'} <= set(stage_b_df['source_dataset'])
    rejected = registry_df.loc[registry_df['selected_for_stage'].fillna(False) == False]
    assert not rejected.empty
    assert 'missing_final_span' in set(rejected['rejection_reason'])
    assert registry_df['is_weighted'].all()
