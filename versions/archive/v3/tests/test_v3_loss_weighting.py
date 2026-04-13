from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_loss_weighting', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


class DummyTokenizer:
    def encode(self, text: str, add_special_tokens: bool = False) -> list[str]:
        del add_special_tokens
        return text.replace('\n', ' \n ').split()


def test_loss_weight_helpers_detect_answer_spans() -> None:
    text = 'Reasoning here\nFinal answer: 42'
    span = v3_train.detect_final_answer_span(text, 'gravity_constant')
    assert span is not None
    assert text[span[0] : span[1]] == '42'
    final_line = v3_train.detect_final_line_span(text)
    assert final_line is not None
    assert text[final_line[0] : final_line[1]] == 'Final answer: 42'

    boxed_text = 'Work shown\n\\boxed{IV}'
    boxed_span = v3_train.detect_final_answer_span(boxed_text, 'roman_numeral')
    assert boxed_span is not None
    assert boxed_text[boxed_span[0] : boxed_span[1]] == 'IV'

    weights = v3_train._build_completion_token_weights(
        DummyTokenizer(),
        text,
        'gravity_constant',
        {'rationale_weight': 1.0, 'final_line_weight': 3.0, 'answer_span_weights': {'gravity_constant': 4.0}},
    )
    assert weights[0] == 1.0
    assert weights[-1] == 4.0
    assert any(weight >= 3.0 for weight in weights[1:])
    assert v3_train.get_answer_span_weight('symbol_equation') == 6.0


def test_run_train_sft_v3_writes_manifest_and_result(tmp_path: Path) -> None:
    train_pack_path = tmp_path / 'train_pack.parquet'
    pd.DataFrame(
        [
            {'prompt': 'p1', 'answer': '12.34', 'cv5_fold': 0, 'family': 'gravity_constant', 'format_policy': 'boxed'},
            {'prompt': 'p2', 'answer': 'IV', 'cv5_fold': 1, 'family': 'roman_numeral', 'format_policy': 'boxed'},
        ]
    ).to_parquet(train_pack_path, index=False)

    config_path = tmp_path / 'train.yaml'
    config_path.write_text(
        yaml.safe_dump(
            {
                'name': 'unit_test_weighted',
                'stage': 'a',
                'train_pack_path': str(train_pack_path),
                'base_model': 'mock-model',
                'lora_r': 32,
                'lora_alpha': 32,
                'target_modules': ['q_proj', 'v_proj'],
                'learning_rate': 0.0001,
                'num_epochs': 2.0,
                'per_device_train_batch_size': 1,
                'weighted_loss': True,
                'final_line_weight': 4.0,
                'answer_span_weights': {'gravity_constant': 4.0},
            }
        ),
        encoding='utf-8',
    )

    output_dir = tmp_path / 'outputs'
    dataset_dir = tmp_path / 'dataset'
    v3_train.run_train_sft_v3(
        SimpleNamespace(
            stage='a',
            config_path=str(config_path),
            train_pack_path=str(train_pack_path),
            dataset_dir=str(dataset_dir),
            valid_fold=0,
            valid_fraction=0.05,
            max_train_rows=None,
            max_valid_rows=None,
            execute=False,
            output_dir=str(output_dir),
        )
    )

    manifest = json.loads((output_dir / 'sft_a_unit_test_weighted_manifest.json').read_text(encoding='utf-8'))
    command = (output_dir / 'sft_a_unit_test_weighted_cmd.sh').read_text(encoding='utf-8')
    result = json.loads((output_dir / 'sft_a_unit_test_weighted_result.json').read_text(encoding='utf-8'))
    mlx_config = yaml.safe_load((output_dir / 'sft_a_unit_test_weighted_mlx.yaml').read_text(encoding='utf-8'))
    assert manifest['data']['num_rows'] == 2
    assert manifest['data']['train_records'] == 1
    assert manifest['data']['valid_records'] == 1
    assert manifest['loss']['weighted'] is True
    assert manifest['data']['dataset_dir'] == str(dataset_dir)
    assert result['status'] == 'rendered_only'
    assert 'python -m mlx_lm lora' in command
    assert '--config' in command
    assert mlx_config['data'] == str(dataset_dir)
    assert (dataset_dir / 'train.jsonl').exists()
    assert (dataset_dir / 'valid.jsonl').exists()
