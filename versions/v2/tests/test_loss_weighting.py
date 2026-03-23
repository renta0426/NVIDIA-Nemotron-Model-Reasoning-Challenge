from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v2_train_loss_weighting', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v2_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v2_train
SPEC.loader.exec_module(v2_train)


def test_loss_weight_helpers_detect_answer_spans() -> None:
    text = 'Reasoning here\nFinal answer: 42'
    span = v2_train.detect_final_answer_span(text, 'gravity_constant')
    assert span is not None
    assert text[span[0] : span[1]] == '42'

    boxed_text = 'Work shown\n\\boxed{IV}'
    boxed_span = v2_train.detect_final_answer_span(boxed_text, 'roman_numeral')
    assert boxed_span is not None
    assert boxed_text[boxed_span[0] : boxed_span[1]] == 'IV'

    weighted = v2_train.compute_loss_weights(text, 'gravity_constant', weighted=True)
    assert weighted[-1] == v2_train.get_answer_span_weight('gravity_constant')
    assert weighted[0] == 1.0
    assert v2_train.compute_loss_weights(text, 'gravity_constant', weighted=False) == [1.0] * len(text.split())
    assert v2_train.get_answer_span_weight('symbol_equation') == 6.0


def test_run_train_sft_writes_manifest_and_command(tmp_path: Path) -> None:
    train_pack_path = tmp_path / 'train_pack.parquet'
    pd.DataFrame([{'prompt': 'p1', 'answer': 'a1'}, {'prompt': 'p2', 'answer': 'a2'}]).to_parquet(train_pack_path, index=False)

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
    v2_train.run_train_sft(
        SimpleNamespace(
            stage='a',
            config_path=str(config_path),
            train_pack_path=str(train_pack_path),
            output_dir=str(output_dir),
        )
    )

    manifest = json.loads((output_dir / 'sft_a_unit_test_weighted_manifest.json').read_text(encoding='utf-8'))
    command = (output_dir / 'sft_a_unit_test_weighted_cmd.sh').read_text(encoding='utf-8')
    assert manifest['data']['num_rows'] == 2
    assert manifest['loss']['weighted'] is True
    assert '--data' in command
