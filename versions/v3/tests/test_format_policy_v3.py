from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_format_policy', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_format_policy_uses_boxed_for_safe_and_final_answer_for_unsafe() -> None:
    assert v3_train.select_v3_format_policy('42', 'gravity_constant') == 'boxed'
    assert v3_train.render_v3_final_answer('42', 'gravity_constant') == r'\boxed{42}'
    assert v3_train.select_v3_format_policy('A{B', 'symbol_equation') == 'final_answer'
    assert v3_train.render_v3_final_answer('A{B', 'symbol_equation') == 'Final answer: A{B'


def test_audit_format_writes_row_level_reasons(tmp_path: Path) -> None:
    input_path = tmp_path / 'teacher_registry.parquet'
    pd.DataFrame(
        [
            {
                'trace_id': 'ok',
                'family': 'gravity_constant',
                'answer': '42',
                'boxed_policy': 'boxed',
                'raw_output': '\\boxed{42}',
            },
            {
                'trace_id': 'bad',
                'family': 'gravity_constant',
                'answer': '42',
                'boxed_policy': 'boxed',
                'raw_output': '\\boxed{41}',
            },
        ]
    ).to_parquet(input_path, index=False)

    output_path = tmp_path / 'format_audit.csv'
    v3_train.run_audit_format(
        SimpleNamespace(
            input_path=str(input_path),
            real_canonical_path=str(input_path),
            teacher_traces_path=str(input_path),
            text_column='raw_output',
            answer_column='answer',
            family_column='family',
            policy_column='boxed_policy',
            output_path=str(output_path),
        )
    )

    audit = pd.read_csv(output_path)
    assert 'rejection_reason' in audit.columns
    assert set(audit['row_id']) == {'ok', 'bad'}
    bad_reason = audit.loc[audit['row_id'] == 'bad', 'rejection_reason'].iloc[0]
    assert 'wrong_answer' in bad_reason
