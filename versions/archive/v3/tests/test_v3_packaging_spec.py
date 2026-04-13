from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_packaging', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def write_submission_contract_readme(tmp_path: Path) -> Path:
    readme_path = tmp_path / 'README.md'
    readme_path.write_text(
        '\n'.join(
            [
                'Evaluation',
                'Submissions are evaluated based on their Accuracy in solving the provided tasks. '
                'The NVIDIA Nemotron-3-Nano-30B model is loaded with your LoRA adapter '
                '(which must include an adapter_config.json) using the vLLM inference engine.',
                'Parameter\tValue',
                'max_lora_rank\t32',
                'max_tokens\t7680',
                'top_p\t1.0',
                'temperature\t0.0',
                'max_num_seqs\t64',
                'gpu_memory_utilization\t0.85',
                'max_model_len\t8192',
                'Submitting',
                'You must submit a LoRA adapter of rank at most 32 for the NVIDIA Nemotron-3-Nano-30B model '
                'packaged into a submission.zip file.',
            ]
        )
        + '\n',
        encoding='utf-8',
    )
    return readme_path


def test_package_peft_and_write_v3_runbook(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(v3_train, 'README_PATH', write_submission_contract_readme(tmp_path))
    adapter_dir = tmp_path / 'adapter'
    adapter_dir.mkdir()
    (adapter_dir / 'adapter_model.safetensors').write_bytes(b'test-weights')
    (adapter_dir / 'adapter_config.json').write_text(
        json.dumps(
            {
                'base_model_name_or_path': 'mock-model',
                'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'r': 16,
            }
        ),
        encoding='utf-8',
    )

    config_path = tmp_path / 'cuda_submission_smoke.yaml'
    config_path.write_text(
        yaml.safe_dump(
            {
                'expected_base_model_name_or_path': 'mock-model',
                'required_files': ['adapter_config.json', 'adapter_model.safetensors'],
                'expected_target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'expected_rank_cap': 32,
                'required_adapter_config_keys': ['base_model_name_or_path', 'target_modules', 'r'],
                'submission_zip_name': 'submission.zip',
            }
        ),
        encoding='utf-8',
    )

    output_dir = tmp_path / 'packaging'
    v3_train.run_package_peft(
        SimpleNamespace(config_path=str(config_path), adapter_dir=str(adapter_dir), output_dir=str(output_dir))
    )

    smoke = json.loads((output_dir / 'peft_smoke_result.json').read_text(encoding='utf-8'))
    submission = json.loads((output_dir / 'submission_manifest.json').read_text(encoding='utf-8'))
    assert smoke['all_required_files_present'] is True
    assert smoke['checks']['rank_ok'] is True
    assert smoke['checks']['target_modules_ok'] is True
    assert smoke['checks']['base_model_ok'] is True
    assert smoke['checks']['submission_zip_ok'] is True
    assert smoke['readme_submission_contract_verified_from_readme_file'] is True
    assert smoke['readme_submission_contract']['submission_archive_name'] == 'submission.zip'
    assert (output_dir / 'submission.zip').exists()
    assert submission['lora_rank'] == 16
    assert 'adapter_config.json' in submission['submission_zip_contents']
    assert submission['readme_submission_contract_verified_from_readme_file'] is True
    assert submission['local_packaging_contract']['submission_zip_name'] == 'submission.zip'

    train_pack_path = tmp_path / 'train_pack.parquet'
    pd.DataFrame([{'prompt': 'p', 'answer': '1'}]).to_parquet(train_pack_path, index=False)
    train_manifest_path = tmp_path / 'train_manifest.json'
    train_manifest_path.write_text(
        json.dumps(
            {
                'stage': 'a',
                'config_name': 'candidate_a',
                'created_at': '2025-01-01T00:00:00Z',
                'data': {'train_pack_path': str(train_pack_path), 'train_records': 1, 'valid_records': 0},
                'adapter': {'lora_r': 32, 'lora_alpha': 32, 'lora_dropout': 0.0, 'target_modules': ['q_proj', 'k_proj']},
                'training': {'learning_rate': 0.0001, 'num_epochs': 2.0, 'max_seq_len': 1024, 'per_device_train_batch_size': 1, 'gradient_accumulation_steps': 8},
                'loss': {'weighted': True, 'final_line_weight': 3.0},
            }
        ),
        encoding='utf-8',
    )
    cuda_config_path = tmp_path / 'cuda_train.yaml'
    cuda_config_path.write_text(
        yaml.safe_dump(
            {
                'base_model_name_or_path': 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-Base',
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'k_proj'],
                'precision': 'bf16',
                'learning_rate': 0.0001,
                'num_epochs': 2.0,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 8,
            }
        ),
        encoding='utf-8',
    )
    cuda_registry_path = tmp_path / 'reports' / 'cuda_registry.csv'
    spec_path = tmp_path / 'reports' / 'cuda_reproduction_spec.yaml'
    v3_train.run_render_cuda_repro_spec_v3(
        SimpleNamespace(
            candidate_id='cand-1',
            train_manifest_path=str(train_manifest_path),
            config_path=str(cuda_config_path),
            output_path=str(spec_path),
            registry_path=str(cuda_registry_path),
            cuda_output_dir='/kaggle/working/cand-1',
            notes='unit-test',
        )
    )
    spec_text = spec_path.read_text(encoding='utf-8')
    assert 'candidate_id: cand-1' in spec_text
    assert 'manual_cuda_execution_required: true' in spec_text
    assert spec_path.with_suffix('.sh').exists()

    candidate_registry_path = tmp_path / 'reports' / 'candidate_registry.csv'
    promotion_rules_path = tmp_path / 'reports' / 'promotion_rules.txt'
    runbook_path = tmp_path / 'reports' / 'runbook.txt'
    v3_train.run_write_runbook_v3(
        SimpleNamespace(
            candidate_registry_path=str(candidate_registry_path),
            promotion_rules_path=str(promotion_rules_path),
            output_path=str(runbook_path),
        )
    )

    with candidate_registry_path.open('r', encoding='utf-8') as handle:
        reader = csv.reader(handle)
        header = next(reader)
    assert header[0] == 'candidate_id'
    runbook_text = runbook_path.read_text(encoding='utf-8')
    promotion_text = promotion_rules_path.read_text(encoding='utf-8')
    assert 'bootstrap-v3' in runbook_text
    assert 'render-cuda-repro-spec' in runbook_text
    assert 'local best update -> queue' in promotion_text


def test_v3_package_peft_rejects_submission_zip_name_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(v3_train, 'README_PATH', write_submission_contract_readme(tmp_path))
    adapter_dir = tmp_path / 'adapter'
    adapter_dir.mkdir()
    (adapter_dir / 'adapter_model.safetensors').write_bytes(b'test-weights')
    (adapter_dir / 'adapter_config.json').write_text(
        json.dumps(
            {
                'base_model_name_or_path': 'mock-model',
                'target_modules': ['q_proj'],
                'r': 16,
            }
        ),
        encoding='utf-8',
    )
    config_path = tmp_path / 'cuda_submission_smoke.yaml'
    config_path.write_text(
        yaml.safe_dump(
            {
                'expected_base_model_name_or_path': 'mock-model',
                'required_files': ['adapter_config.json', 'adapter_model.safetensors'],
                'expected_target_modules': ['q_proj'],
                'expected_rank_cap': 32,
                'required_adapter_config_keys': ['base_model_name_or_path', 'target_modules', 'r'],
                'submission_zip_name': 'submission_v3.zip',
            }
        ),
        encoding='utf-8',
    )

    with pytest.raises(SystemExit, match='submission_zip_name'):
        v3_train.run_package_peft(
            SimpleNamespace(
                config_path=str(config_path),
                adapter_dir=str(adapter_dir),
                output_dir=str(tmp_path / 'packaging'),
            )
        )
