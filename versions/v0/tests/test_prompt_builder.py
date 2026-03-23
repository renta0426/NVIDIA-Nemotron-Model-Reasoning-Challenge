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


class RecordingTokenizer:
    def __init__(self):
        self.calls = []

    def apply_chat_template(self, messages, *, tokenize, add_generation_prompt, enable_thinking):
        self.calls.append(
            {
                "messages": messages,
                "tokenize": tokenize,
                "add_generation_prompt": add_generation_prompt,
                "enable_thinking": enable_thinking,
            }
        )
        return (
            "PROMPT::"
            + messages[0]["content"]
            + f"::agp={add_generation_prompt}::thinking={enable_thinking}"
        )


class FailingTokenizer:
    def apply_chat_template(self, messages, *, tokenize, add_generation_prompt, enable_thinking):
        raise RuntimeError("template failure")


def test_build_user_content_matches_metric_newline_and_instruction():
    user_content = v0.build_user_content("problem body", v0.OFFICIAL_BOXED_INSTRUCTION)
    assert user_content == (
        "problem body\n"
        r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
    )


def test_build_competition_prompt_records_expected_call_shape():
    tokenizer = RecordingTokenizer()
    config = v0.load_eval_config("official_lb")

    rendered = v0.build_competition_prompt(tokenizer, "solve me", config)

    assert rendered == (
        "PROMPT::solve me\n"
        r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
        "::agp=True::thinking=True"
    )
    assert tokenizer.calls == [
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "solve me\n"
                        r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
                    ),
                }
            ],
            "tokenize": False,
            "add_generation_prompt": True,
            "enable_thinking": True,
        }
    ]


def test_builtin_tokenizer_snapshot_is_stable():
    tokenizer = v0.BuiltinCompetitionTokenizer()
    config = v0.load_eval_config("official_lb")

    rendered = v0.build_competition_prompt(tokenizer, "x + y", config)

    assert rendered == (
        "<|user|>\n"
        "x + y\n"
        r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
        "\n<|assistant|>\n<think>"
    )


def test_strict_prompt_builder_raises_on_template_failure():
    with pytest.raises(RuntimeError):
        v0.apply_competition_chat_template(
            FailingTokenizer(),
            "content",
            enable_thinking=True,
            add_generation_prompt=True,
            strict_chat_template=True,
        )


def test_non_strict_prompt_builder_warns_and_falls_back():
    with pytest.warns(RuntimeWarning):
        rendered = v0.apply_competition_chat_template(
            FailingTokenizer(),
            "content",
            enable_thinking=True,
            add_generation_prompt=True,
            strict_chat_template=False,
        )
    assert rendered == "content"
