from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_cuda_packaging', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_render_cuda_repro_spec_and_package_peft(tmp_path: Path) -> None:
    train_output_root = tmp_path / 'train_outputs'
    train_output_root.mkdir(parents=True)
    v3_train.TRAIN_OUTPUT_ROOT = train_output_root

    train_pack_path = tmp_path / 'stage_a.parquet'
    pd.DataFrame([{'id': 'a', 'prompt': 'p', 'answer': '42', 'family': 'gravity_constant', 'source_dataset': 'real'}]).to_parquet(train_pack_path, index=False)
    manifest_path = train_output_root / 'candidate_a' / 'sft_a_candidate_manifest.json'
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(
            {
                'candidate_id': 'cand1',
                'stage': 'a',
                'config_name': 'candidate',
                'data': {'train_pack_path': str(train_pack_path), 'train_records': 1, 'valid_records': 0, 'style_distribution': {'format_safe': 1.0}},
                'adapter': {'lora_r': 16, 'lora_alpha': 32, 'lora_dropout': 0.0, 'target_modules': ['q_proj', 'v_proj']},
                'training': {'learning_rate': 1e-4, 'num_epochs': 1.0, 'max_seq_len': 256, 'per_device_train_batch_size': 1, 'gradient_accumulation_steps': 1},
                'loss': {'weighted': True, 'final_line_weight': 3.0, 'answer_span_weights': {'gravity_constant': 4.0}},
            }
        ),
        encoding='utf-8',
    )

    candidate_registry = tmp_path / 'candidate_registry.csv'
    pd.DataFrame([{'candidate_id': 'cand1'}]).to_csv(candidate_registry, index=False)
    cuda_config = tmp_path / 'cuda.yaml'
    cuda_config.write_text(
        yaml.safe_dump(
            {
                'base_model_name_or_path': v3_train.DEFAULT_SUBMISSION_BASE_MODEL,
                'lora_r': 16,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'v_proj'],
                'precision': 'bf16',
            }
        ),
        encoding='utf-8',
    )
    spec_path = tmp_path / 'cuda_spec.yaml'
    cuda_registry = tmp_path / 'cuda_registry.csv'

    v3_train.run_render_cuda_repro_spec_v3(
        SimpleNamespace(
            candidate_id='cand1',
            candidate_registry_path=str(candidate_registry),
            train_manifest_path=None,
            config_path=str(cuda_config),
            output_path=str(spec_path),
            registry_path=str(cuda_registry),
            cuda_output_dir='/kaggle/working/cand1',
            notes='',
        )
    )

    spec = yaml.safe_load(spec_path.read_text(encoding='utf-8'))
    assert spec['candidate_id'] == 'cand1'
    assert spec['train_pack_sha256']
    assert spec['base_model_name_or_path'] == v3_train.DEFAULT_SUBMISSION_BASE_MODEL
    registry = pd.read_csv(cuda_registry)
    assert registry.iloc[-1]['status'] == 'pending_manual_cuda'

    adapter_dir = tmp_path / 'adapter'
    adapter_dir.mkdir()
    (adapter_dir / 'adapter_model.safetensors').write_bytes(b'test-weights')
    (adapter_dir / 'adapter_config.json').write_text(
        json.dumps(
            {
                'base_model_name_or_path': v3_train.DEFAULT_SUBMISSION_BASE_MODEL,
                'target_modules': ['q_proj', 'v_proj'],
                'r': 16,
            }
        ),
        encoding='utf-8',
    )
    package_config = tmp_path / 'package.yaml'
    package_config.write_text(
        yaml.safe_dump(
            {
                'expected_base_model_name_or_path': v3_train.DEFAULT_SUBMISSION_BASE_MODEL,
                'required_files': ['adapter_config.json', 'adapter_model.safetensors'],
                'expected_target_modules': ['q_proj', 'v_proj'],
                'expected_rank_cap': 32,
                'required_adapter_config_keys': ['base_model_name_or_path', 'target_modules', 'r'],
                'submission_zip_name': 'submission_v3.zip',
            }
        ),
        encoding='utf-8',
    )
    packaging_dir = tmp_path / 'packaging'
    v3_train.run_package_peft(SimpleNamespace(config_path=str(package_config), adapter_dir=str(adapter_dir), output_dir=str(packaging_dir)))

    smoke = json.loads((packaging_dir / 'peft_smoke_result.json').read_text(encoding='utf-8'))
    submission = json.loads((packaging_dir / 'submission_manifest_v3.json').read_text(encoding='utf-8'))
    assert smoke['checks']['submission_zip_ok'] is True
    assert (packaging_dir / 'submission_v3.zip').exists()
    assert submission['lora_rank'] == 16
