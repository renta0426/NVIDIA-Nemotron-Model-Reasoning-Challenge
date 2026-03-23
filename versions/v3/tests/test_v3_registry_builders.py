from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_registry', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def _canonical_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        'id': 'row',
        'family': 'symbol_equation',
        'subfamily': 'base',
        'prompt': 'If x + 2 = 5, solve for x.',
        'answer': 'x=3',
        'answer_canonical': 'x=3',
        'answer_type': 'equation',
        'format_policy': 'boxed',
        'hard_score': 8.0,
        'is_holdout_hard': True,
    }
    row.update(overrides)
    return row


def test_teacher_filtering_and_registry_builders(tmp_path: Path) -> None:
    canonical = pd.DataFrame(
        [
            _canonical_row(id='eq-1'),
            _canonical_row(
                id='gravity-1',
                family='gravity_constant',
                subfamily='g16',
                prompt='For t = 1.00s, distance = 5.00 m\nNow determine the falling distance for t = 2.00s.',
                answer='19.62',
                answer_canonical='19.62',
                answer_type='numeric',
                format_policy='boxed',
                hard_score=2.0,
                is_holdout_hard=False,
            ),
        ]
    )
    canonical_path = tmp_path / 'canonical.parquet'
    canonical.to_parquet(canonical_path, index=False)

    candidate_config_path = tmp_path / 'teacher_trace_real.yaml'
    candidate_config_path.write_text(
        yaml.safe_dump(
            {
                'teacher_name': v3_train.DEFAULT_MODEL_REPO_ID,
                'seed': 99,
                'target_styles': ['short', 'long'],
                'style_samples': {'short': 1, 'long': 1},
                'hard_family_styles': ['short'],
                'hard_family_sample_count': 2,
            }
        ),
        encoding='utf-8',
    )
    candidates_path = tmp_path / 'teacher_candidates.jsonl'
    teacher_registry_path = tmp_path / 'teacher_registry.parquet'
    accepted_path = tmp_path / 'distilled_traces.parquet'

    v3_train.run_build_teacher_trace_candidates(
        SimpleNamespace(
            config_path=str(candidate_config_path),
            input_path=str(canonical_path),
            output_path=str(candidates_path),
            max_rows=None,
        )
    )
    candidate_lines = [json.loads(line) for line in candidates_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    assert len(candidate_lines) == 5

    generated_path = tmp_path / 'teacher_generations.jsonl'
    rendered: list[dict[str, object]] = []
    for row in candidate_lines:
        generated = dict(row)
        generated['generation_status'] = 'ok'
        if row['source_id'] == 'eq-1' and row['target_style'] == 'short' and row['teacher_seed'] == 99:
            generated['raw_output'] = 'Quick solve\n\\boxed{x=3}'
        elif row['source_id'] == 'eq-1' and row['target_style'] == 'short':
            generated['raw_output'] = 'Wrong path\n\\boxed{x=4}'
        elif row['source_id'] == 'eq-1':
            generated['raw_output'] = 'Line 1\nLine 2 with extra detail\n\\boxed{x=3}'
        else:
            generated['raw_output'] = 'Compute carefully\n\\boxed{19.62}'
        rendered.append(generated)
    v3_train.write_jsonl(generated_path, rendered)

    v3_train.run_filter_teacher_traces(
        SimpleNamespace(
            input_path=str(generated_path),
            output_path=str(accepted_path),
            registry_path=str(teacher_registry_path),
        )
    )
    accepted_df = pd.read_parquet(accepted_path)
    registry_df = pd.read_parquet(teacher_registry_path)
    assert len(accepted_df) == 4
    assert {'strict_pass', 'wrong_answer'} <= set(registry_df['selection_reason'])

    format_audit_path = tmp_path / 'format_audit.csv'
    v3_train.run_audit_format(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            teacher_traces_path=str(teacher_registry_path),
            output_path=str(format_audit_path),
        )
    )
    audit_df = pd.read_csv(format_audit_path)
    assert not audit_df.empty

    format_pairs_path = tmp_path / 'format_pairs.parquet'
    v3_train.run_build_format_pairs(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            teacher_traces_path=str(teacher_registry_path),
            config_path=str(v3_train.DEFAULT_V3_FORMAT_POLICY_CONFIG_PATH),
            output_path=str(format_pairs_path),
        )
    )
    format_pairs_df = pd.read_parquet(format_pairs_path)
    assert not format_pairs_df.empty
    assert (format_pairs_df['chosen_output'] != format_pairs_df['rejected_output']).all()

    bootstrap_correction_path = tmp_path / 'bootstrap_correction.parquet'
    pd.DataFrame(
        [
            {
                'source_id': 'eq-1',
                'family': 'symbol_equation',
                'prompt': 'If x + 2 = 5, solve for x.',
                'chosen_extracted_answer': 'x=3',
                'rejected_output': '\\boxed{x=4}',
                'error_family_tag': 'symbol_equation',
                'error_subtype': 'symbol:wrong_value',
                'source_eval_run': 'unit_test',
            }
        ]
    ).to_parquet(bootstrap_correction_path, index=False)
    correction_pairs_path = tmp_path / 'correction_pairs.parquet'
    v3_train.run_build_correction_pairs(
        SimpleNamespace(
            real_canonical_path=str(canonical_path),
            teacher_traces_path=str(teacher_registry_path),
            bootstrap_pairs_path=str(bootstrap_correction_path),
            output_path=str(correction_pairs_path),
        )
    )
    correction_df = pd.read_parquet(correction_pairs_path)
    assert len(correction_df) == 1
    assert correction_df.iloc[0]['chosen_output'] != correction_df.iloc[0]['rejected_output']

    preference_config_path = tmp_path / 'preference.yaml'
    preference_config_path.write_text(yaml.safe_dump({'brevity_margin_chars': 5}), encoding='utf-8')
    preference_pairs_path = tmp_path / 'preference_pairs.parquet'
    v3_train.run_build_preference_pairs(
        SimpleNamespace(
            config_path=str(preference_config_path),
            format_pairs_path=str(format_pairs_path),
            correction_pairs_path=str(correction_pairs_path),
            teacher_traces_path=str(teacher_registry_path),
            output_path=str(preference_pairs_path),
        )
    )
    preference_df = pd.read_parquet(preference_pairs_path)
    assert {'format', 'correction', 'brevity', 'consensus'} <= set(preference_df['pair_kind'])

    rft_config_path = tmp_path / 'rft.yaml'
    rft_config_path.write_text(yaml.safe_dump({'max_trace_tokens_est': 96}), encoding='utf-8')
    rft_output_path = tmp_path / 'rft_accept_pool.parquet'
    v3_train.run_build_rft_accept_pool(
        SimpleNamespace(
            config_path=str(rft_config_path),
            teacher_traces_path=str(teacher_registry_path),
            output_path=str(rft_output_path),
        )
    )
    rft_df = pd.read_parquet(rft_output_path)
    assert not rft_df.empty
    assert rft_df['accept_id'].str.startswith('rft_').all()
    assert v3_train.dedup_hash('symbol_equation', ' x=3 ', 'prompt') == v3_train.dedup_hash('symbol_equation', 'x=3', 'prompt')
