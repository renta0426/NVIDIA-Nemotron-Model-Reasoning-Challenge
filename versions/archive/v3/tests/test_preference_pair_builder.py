from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_preference_pairs', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_build_preference_pairs_includes_format_correction_brevity_and_consensus(tmp_path: Path) -> None:
    format_pairs_path = tmp_path / 'format_pairs.parquet'
    correction_pairs_path = tmp_path / 'correction_pairs.parquet'
    teacher_path = tmp_path / 'teacher_registry.parquet'
    config_path = tmp_path / 'preference.yaml'
    output_path = tmp_path / 'preference_pairs.parquet'
    audit_path = tmp_path / 'preference_pairs.csv'

    pd.DataFrame(
        [
            {
                'pair_id': 'fmt1',
                'source_id': 'src1',
                'family': 'gravity_constant',
                'prompt': 'Prompt 1',
                'chosen_output': '\\boxed{42}',
                'rejected_output': '42',
                'chosen_format_bucket': 'clean_boxed',
                'rejected_format_bucket': 'last_line_fallback',
                'pair_kind': 'clean_vs_dirty',
            }
        ]
    ).to_parquet(format_pairs_path, index=False)
    pd.DataFrame(
        [
            {
                'pair_id': 'corr1',
                'source_id': 'src2',
                'family': 'gravity_constant',
                'prompt': 'Prompt 2',
                'chosen_output': '\\boxed{42}',
                'rejected_output': '\\boxed{41}',
                'error_subtype': 'gravity:rounding_miss',
            }
        ]
    ).to_parquet(correction_pairs_path, index=False)
    pd.DataFrame(
        [
            {
                'trace_id': 't1',
                'source_id': 'src3',
                'family': 'gravity_constant',
                'prompt': 'Prompt 3',
                'raw_output': '\\boxed{42}',
                'format_bucket': 'clean_boxed',
                'selected_for_training': True,
                'is_correct': True,
                'trace_len_tokens_est': 1,
                'trace_len_chars': 11,
            },
            {
                'trace_id': 't2',
                'source_id': 'src3',
                'family': 'gravity_constant',
                'prompt': 'Prompt 3',
                'raw_output': 'Reasoning line one.\nReasoning line two.\n\\boxed{42}',
                'format_bucket': 'clean_boxed',
                'selected_for_training': True,
                'is_correct': True,
                'trace_len_tokens_est': 8,
                'trace_len_chars': 48,
            },
            {
                'trace_id': 't3',
                'source_id': 'src3',
                'family': 'gravity_constant',
                'prompt': 'Prompt 3',
                'raw_output': '\\boxed{41}',
                'format_bucket': 'clean_boxed',
                'selected_for_training': False,
                'is_correct': False,
                'trace_len_tokens_est': 1,
                'trace_len_chars': 11,
            },
        ]
    ).to_parquet(teacher_path, index=False)
    config_path.write_text(yaml.safe_dump({'brevity_margin_chars': 5}), encoding='utf-8')

    v3_train.run_build_preference_pairs(
        SimpleNamespace(
            config_path=str(config_path),
            format_pairs_path=str(format_pairs_path),
            correction_pairs_path=str(correction_pairs_path),
            teacher_traces_path=str(teacher_path),
            output_path=str(output_path),
            audit_output_path=str(audit_path),
        )
    )

    pairs = pd.read_parquet(output_path)
    assert {'format', 'correction', 'brevity', 'consensus'} <= set(pairs['pair_kind'])
    assert (pairs['pair_kind'] == 'format').sum() == 1
    assert (pairs['pair_kind'] == 'correction').sum() == 1
