from __future__ import annotations

import importlib.util
from pathlib import Path
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


@pytest.mark.parametrize(
    ('prompt', 'answer', 'expected_family', 'expected_query', 'expected_examples', 'expected_answer_type'),
    [
        (
            """In Alice's Wonderland, numbers are secretly converted into a different numeral system. Some examples are given below:\n11 -> XI\n15 -> XV\n94 -> XCIV\n19 -> XIX\nNow, write the number 38 in the Wonderland numeral system.""",
            'XXXVIII',
            'roman_numeral',
            '38',
            4,
            'roman',
        ),
        (
            """In Alice's Wonderland, the gravitational constant has been secretly changed. Here are some example observations:\nFor t = 1.00s, distance = 10.00 m\nFor t = 2.00s, distance = 40.00 m\nNow, determine the falling distance for t = 3.00s given d = 0.5*g*t^2.""",
            '90.00',
            'gravity_constant',
            '3.00',
            2,
            'numeric',
        ),
        (
            """In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers.\nHere are some examples of input -> output:\n00000000 -> 11111111\n11110000 -> 00001111\nNow, determine the output for: 10101010""",
            '01010101',
            'bit_manipulation',
            '10101010',
            2,
            'binary8',
        ),
        (
            """In Alice's Wonderland, secret encryption rules are used on text. Here are some examples:\nabc def -> cat dog\nghi jkl -> owl fox\nNow, decrypt the following text: mno pqr""",
            'tea cup',
            'text_decryption',
            'mno pqr',
            2,
            'text_phrase',
        ),
        (
            """In Alice's Wonderland, a secret unit conversion is applied to measurements. For example:\n10.00 m becomes 20.00\n25.00 m becomes 50.00\nNow, convert the following measurement: 13.50 m""",
            '27.00',
            'unit_conversion',
            '13.50',
            2,
            'numeric',
        ),
        (
            """In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:\n`!*[{ = '"[\n\\'*'> = ![@\nNow, determine the result for: [[-!'""",
            '@&',
            'symbol_equation',
            "[[-!'",
            2,
            'symbolic',
        ),
    ],
)
def test_parse_prompt_detects_expected_family_and_structure(
    prompt,
    answer,
    expected_family,
    expected_query,
    expected_examples,
    expected_answer_type,
):
    parsed = v1.parse_prompt(prompt, answer)

    assert parsed.family == expected_family
    assert parsed.query_raw == expected_query
    assert parsed.num_examples == expected_examples
    assert parsed.answer_type == expected_answer_type
    assert parsed.parse_ok is True
    assert parsed.confidence >= 0.94 or expected_family in {'text_decryption', 'symbol_equation'}
