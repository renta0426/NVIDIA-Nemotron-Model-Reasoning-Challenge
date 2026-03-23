from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_weighted_runtime', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_weighted_helpers_and_mock_runtime_execution(tmp_path: Path) -> None:
    text = 'Reasoning here\nFinal answer: 42'
    span = v3_train.detect_final_answer_span(text, 'gravity_constant')
    assert span is not None
    assert text[span[0] : span[1]] == '42'
    weights = v3_train.compute_loss_weights(text, 'gravity_constant', weighted=True)
    assert weights[-1] == v3_train.get_answer_span_weight('gravity_constant')

    train_pack_path = tmp_path / 'train_pack.parquet'
    pd.DataFrame(
        [
            {'id': 'p1', 'prompt': 'Prompt 1', 'answer': '42', 'family': 'gravity_constant', 'cv5_fold': 0},
            {'id': 'p2', 'prompt': 'Prompt 2', 'answer': '43', 'family': 'gravity_constant', 'cv5_fold': 1},
        ]
    ).to_parquet(train_pack_path, index=False)

    config_path = tmp_path / 'weighted_mock.yaml'
    config_path.write_text(
        yaml.safe_dump(
            {
                'name': 'weighted_mock',
                'stage': 'a',
                'train_pack_path': str(train_pack_path),
                'base_model': 'mock-model',
                'runtime_backend': 'mock',
                'lora_r': 8,
                'lora_alpha': 16,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'v_proj'],
                'learning_rate': 1e-4,
                'num_epochs': 1.0,
                'max_seq_len': 256,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 1,
                'weighted_loss': True,
                'rationale_weight': 1.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {'gravity_constant': 4.0},
            }
        ),
        encoding='utf-8',
    )

    output_dir = tmp_path / 'outputs'
    dataset_dir = tmp_path / 'dataset'
    candidate_registry = tmp_path / 'candidate_registry.csv'
    v3_train.run_train_sft_v3(
        SimpleNamespace(
            stage='a',
            config_path=str(config_path),
            train_pack_path=str(train_pack_path),
            dataset_dir=str(dataset_dir),
            valid_fold=0,
            valid_fraction=0.5,
            max_train_rows=None,
            max_valid_rows=None,
            execute=True,
            output_dir=str(output_dir),
            candidate_id='mock_candidate',
            candidate_registry_path=str(candidate_registry),
        )
    )

    manifest = json.loads((output_dir / 'sft_a_weighted_mock_manifest.json').read_text(encoding='utf-8'))
    result = json.loads((output_dir / 'sft_a_weighted_mock_result.json').read_text(encoding='utf-8'))
    assert manifest['execution']['supports_runtime_execution'] is True
    assert result['status'] == 'completed'
    assert (output_dir / 'adapter_a_weighted_mock' / 'adapters.safetensors').exists()
    registry = pd.read_csv(candidate_registry)
    assert registry.iloc[-1]['candidate_id'] == 'mock_candidate'
    assert registry.iloc[-1]['status'] == 'completed'
