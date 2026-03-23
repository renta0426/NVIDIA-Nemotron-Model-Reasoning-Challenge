from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import random
import sys

import pytest


def load_v1_module():
    module_name = 'v1_train'
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v1 = load_v1_module()
FIXTURE_PATH = Path(__file__).resolve().parents[1] / 'data' / 'processed' / 'extraction_fixtures_v1.jsonl'


def load_fixtures():
    return [json.loads(line) for line in FIXTURE_PATH.read_text(encoding='utf-8').splitlines() if line.strip()]


FIXTURES = load_fixtures()


def failure_message(case, extracted, source, bucket):
    return (
        f"case_id={case['case_id']}\n"
        f"raw_output={case['raw_output']!r}\n"
        f"expected_extracted={case['expected_extracted']!r}\n"
        f"actual_extracted={extracted!r}\n"
        f"expected_source={case['expected_source']!r}\n"
        f"actual_source={source!r}\n"
        f"expected_bucket={case['expected_bucket']!r}\n"
        f"actual_bucket={bucket!r}"
    )


@pytest.mark.parametrize('case', FIXTURES, ids=[case['case_id'] for case in FIXTURES])
def test_extraction_fixture_cases(case):
    extracted, source = v1.extract_final_answer_with_source(case['raw_output'])
    bucket = v1.classify_format_bucket(case['raw_output'], extracted, source)

    message = failure_message(case, extracted, source, bucket)
    assert extracted == case['expected_extracted'], message
    assert source == case['expected_source'], message
    assert bucket == case['expected_bucket'], message


def test_extraction_fixture_inventory_is_large_enough():
    assert len(FIXTURES) >= 30


@pytest.mark.parametrize(
    ('answer', 'expected'),
    [
        ('42', {'boxed_safe': True, 'risk_reason': 'safe'}),
        ('a}', {'boxed_safe': False, 'risk_reason': 'contains_right_brace'}),
        (r'a\\b', {'boxed_safe': True, 'risk_reason': 'contains_backslash'}),
        ('line1\nline2', {'boxed_safe': False, 'risk_reason': 'contains_newline'}),
        ('`tick`', {'boxed_safe': True, 'risk_reason': 'contains_backtick'}),
    ],
)
def test_analyze_extraction_risk_flags_expected_conditions(answer, expected):
    result = v1.analyze_extraction_risk(answer)
    assert result['boxed_safe'] is expected['boxed_safe']
    assert expected['risk_reason'] in result['risk_reason']


def test_extraction_fuzz_cases_do_not_crash_and_return_known_labels():
    rng = random.Random(0)
    wrappers = [
        lambda answer: rf'Reasoning... \\boxed{{{answer}}}',
        lambda answer: f'Final answer: {answer}',
        lambda answer: f'prefix\n{answer}',
    ]
    alphabet = list('Ab90 {}\\`') + ['\n']
    valid_sources = {'boxed', 'final_answer_is', 'final_answer_colon', 'last_number', 'last_line', 'not_found'}
    valid_buckets = {
        'clean_boxed',
        'clean_final_answer',
        'boxed_multiple',
        'boxed_empty',
        'boxed_unclosed',
        'boxed_truncated_right_brace',
        'extra_trailing_numbers',
        'last_number_fallback',
        'last_line_fallback',
        'not_found',
    }

    for idx in range(250):
        length = rng.randint(0, 8)
        answer = ''.join(rng.choice(alphabet) for _ in range(length))
        raw_output = None if rng.random() < 0.05 else rng.choice(wrappers)(answer)
        try:
            extracted, source = v1.extract_final_answer_with_source(raw_output)
            bucket = v1.classify_format_bucket(raw_output, extracted, source)
        except Exception as exc:  # pragma: no cover - explicit failure path
            pytest.fail(f'fuzz case {idx} crashed for raw_output={raw_output!r}: {exc}')

        assert source in valid_sources
        assert bucket in valid_buckets
        assert extracted is not None
