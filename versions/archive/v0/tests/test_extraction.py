from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


def load_v0_module():
    module_name = "v0_train"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = Path(__file__).resolve().parents[1] / "code" / "train.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v0 = load_v0_module()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (r"The answer is \boxed{42}", "42"),
        ("The final answer is: 3.14", "3.14"),
        ("Final answer: 7", "7"),
        ("Candidates are 2, 4, and 9", "9"),
        (r"\boxed{1} ignored \boxed{2}", "2"),
        (r"\boxed{}", ""),
        (r"\boxed{abc", "abc"),
        (r"Risky answer \boxed{a}b}", "a"),
        ("No digits here\nlast non-empty line", "last non-empty line"),
        (None, "NOT_FOUND"),
    ],
)
def test_extract_final_answer_metric_faithful(text, expected):
    assert v0.extract_final_answer(text) == expected
