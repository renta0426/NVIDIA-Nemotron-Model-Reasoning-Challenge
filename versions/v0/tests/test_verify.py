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
    ("stored_answer", "predicted", "expected"),
    [
        ("1.00", "1", True),
        ("0.0099", "0.01", True),
        ("XIV", "xiv", True),
        ("0101", "101", True),
        ("abc", "ABC", True),
        ("1,000", "1000", False),
    ],
)
def test_verify_metric_faithful(stored_answer, predicted, expected):
    assert v0.verify(stored_answer, predicted) is expected
