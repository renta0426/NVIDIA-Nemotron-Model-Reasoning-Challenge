from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v2_train_registry', MODULE_PATH)
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
        'eligible_pools': '["core", "distill", "format_sharpening"]',
        'hard_score': 8.0,
        'is_holdout_hard': True,
        'roman_query_value': 7.0,
    }
    row.update(overrides)
    return row


def test_distill_filter_format_and_correction_builders(tmp_path: Path, monkeypatch) -> None:
    canonical = pd.DataFrame(
        [
            _canonical_row(id='roman-1'),
            _canonical_row(
                id='gravity-1',
                family='gravity_constant',
                subfamily='g16',
                prompt='For t = 1.00s, distance = 5.00 m\nNow determine the falling distance for t = 4.41s.',
                answer='154.62',
                answer_canonical='154.62',
                answer_type='numeric',
                format_policy='final_answer_colon',
                eligible_pools='["core", "distill"]',
                hard_score=2.0,
                is_holdout_hard=False,
                roman_query_value=float('nan'),
            ),
        ]
    )
    canonical_path = tmp_path / 'canonical.parquet'
    canonical.to_parquet(canonical_path, index=False)

    distill_config_path = tmp_path / 'teacher_distill.yaml'
    distill_config_path.write_text(
        yaml.safe_dump({'target_pools': ['distill'], 'target_styles': ['short', 'answer_only'], 'seed': 99}),
        encoding='utf-8',
    )
    candidates_path = tmp_path / 'distill_candidates.jsonl'
    accepted_path = tmp_path / 'distilled_traces.parquet'
    teacher_registry_path = tmp_path / 'teacher_registry.parquet'

    v2_train.run_build_distill_candidates(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            config_path=str(distill_config_path),
            output_path=str(candidates_path),
        )
    )
    candidate_lines = [json.loads(line) for line in candidates_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    assert len(candidate_lines) == 4

    v2_train.run_filter_distilled_traces(
        SimpleNamespace(
            candidate_path=str(candidates_path),
            output_path=str(accepted_path),
            registry_path=str(teacher_registry_path),
        )
    )
    accepted_df = pd.read_parquet(accepted_path)
    registry_df = pd.read_parquet(teacher_registry_path)
    assert len(accepted_df) == 4
    assert registry_df['selected_for_training'].all()

    synth_format_path = tmp_path / 'synth_format.parquet'
    monkeypatch.setattr(v2_train, 'DEFAULT_SYNTH_FORMAT_OUTPUT_PATH', synth_format_path)
    format_pairs_path = tmp_path / 'format_pairs.parquet'
    v2_train.run_build_format_pairs(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            teacher_traces_path=str(accepted_path),
            config_path=str(v2_train.DEFAULT_FORMAT_SHARPENING_CONFIG_PATH),
            output_path=str(format_pairs_path),
        )
    )
    format_pairs_df = pd.read_parquet(format_pairs_path)
    synth_format_df = pd.read_parquet(synth_format_path)
    assert len(format_pairs_df) == 6
    assert len(synth_format_df) == 6
    assert (format_pairs_df['chosen'] != format_pairs_df['rejected']).all()

    correction_pairs_path = tmp_path / 'correction_pairs.parquet'
    v2_train.run_build_correction_pairs(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            teacher_traces_path=str(accepted_path),
            output_path=str(correction_pairs_path),
        )
    )
    correction_df = pd.read_parquet(correction_pairs_path)
    assert len(correction_df) == 1
    assert correction_df.iloc[0]['chosen_output'] != correction_df.iloc[0]['rejected_output']

    assert v2_train.dedup_hash('roman_numeral', ' VII ', 'prompt') == v2_train.dedup_hash('roman_numeral', 'VII', 'prompt')
