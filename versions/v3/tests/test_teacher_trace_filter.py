from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_teacher_filter', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_filter_teacher_traces_logs_strict_rejection_reasons(tmp_path: Path) -> None:
    input_path = tmp_path / 'teacher_generations.jsonl'
    rows = [
        {
            'candidate_id': 'ok',
            'source_id': 'ok',
            'generation_status': 'ok',
            'family': 'gravity_constant',
            'answer': '42',
            'raw_output': 'Reasoning\n\\boxed{42}',
            'target_style': 'short',
            'teacher_name': 'mock',
            'teacher_seed': 1,
        },
        {
            'candidate_id': 'wrong',
            'source_id': 'wrong',
            'generation_status': 'ok',
            'family': 'gravity_constant',
            'answer': '42',
            'raw_output': '\\boxed{41}',
            'target_style': 'short',
            'teacher_name': 'mock',
            'teacher_seed': 1,
        },
        {
            'candidate_id': 'multi',
            'source_id': 'multi',
            'generation_status': 'ok',
            'family': 'gravity_constant',
            'answer': '42',
            'raw_output': '\\boxed{42}\n\\boxed{42}',
            'target_style': 'short',
            'teacher_name': 'mock',
            'teacher_seed': 1,
        },
        {
            'candidate_id': 'unsafe',
            'source_id': 'unsafe',
            'generation_status': 'ok',
            'family': 'symbol_equation',
            'answer': 'A{B',
            'raw_output': '\\boxed{A{B}',
            'target_style': 'short',
            'teacher_name': 'mock',
            'teacher_seed': 1,
        },
        {
            'candidate_id': 'not-last-line',
            'source_id': 'not-last-line',
            'generation_status': 'ok',
            'family': 'gravity_constant',
            'answer': '42',
            'raw_output': '\\boxed{42}\nMore explanation follows.',
            'target_style': 'short',
            'teacher_name': 'mock',
            'teacher_seed': 1,
        },
    ]
    input_path.write_text(''.join(f"{json.dumps(row)}\n" for row in rows), encoding='utf-8')

    registry_path = tmp_path / 'teacher_registry.parquet'
    accepted_path = tmp_path / 'distilled.parquet'
    audit_path = tmp_path / 'audit.csv'
    v3_train.run_filter_teacher_traces(
        SimpleNamespace(
            input_path=str(input_path),
            registry_path=str(registry_path),
            output_path=str(accepted_path),
            audit_output_path=str(audit_path),
        )
    )

    registry = pd.read_parquet(registry_path)
    accepted = pd.read_parquet(accepted_path)
    audit = pd.read_csv(audit_path)

    assert accepted['source_id'].tolist() == ['ok']
    reasons = {row['source_id']: set(str(row['rejection_reason']).split('|')) for _, row in audit.iterrows()}
    assert 'wrong_answer' in reasons['wrong']
    assert 'multiple_boxed' in reasons['multi']
    assert {'unsafe_answer_boxed', 'unsafe_answer_contains_boxed'} & reasons['unsafe']
    assert 'final_answer_not_last_line' in reasons['not-last-line']
    assert set(registry['selected_for_training'].tolist()) == {True, False}
