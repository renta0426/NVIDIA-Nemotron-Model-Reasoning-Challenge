from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v4_train_packaging', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v4_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v4_train
SPEC.loader.exec_module(v4_train)


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


def test_v4_package_peft_surfaces_verified_readme_submission_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(v4_train, 'README_PATH', write_submission_contract_readme(tmp_path))
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
    v4_train.run_package_peft(
        SimpleNamespace(config_path=str(config_path), adapter_dir=str(adapter_dir), output_dir=str(output_dir))
    )

    smoke = json.loads((output_dir / 'peft_smoke_result.json').read_text(encoding='utf-8'))
    submission = json.loads((output_dir / 'submission_manifest_v4.json').read_text(encoding='utf-8'))
    assert smoke['checks']['submission_zip_ok'] is True
    assert smoke['readme_submission_contract_verified_from_readme_file'] is True
    assert smoke['readme_submission_contract']['submission_archive_name'] == 'submission.zip'
    assert smoke['local_packaging_contract']['submission_zip_name'] == 'submission.zip'
    assert (output_dir / 'submission.zip').exists()
    assert submission['version'] == 'v4'
    assert submission['readme_submission_contract_verified_from_readme_file'] is True
    assert submission['local_packaging_contract']['submission_zip_name'] == 'submission.zip'
    assert 'adapter_config.json' in submission['submission_zip_contents']


def test_v4_package_peft_rejects_submission_zip_name_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(v4_train, 'README_PATH', write_submission_contract_readme(tmp_path))
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
                'submission_zip_name': 'submission_v4.zip',
            }
        ),
        encoding='utf-8',
    )

    with pytest.raises(SystemExit, match='submission_zip_name'):
        v4_train.run_package_peft(
            SimpleNamespace(
                config_path=str(config_path),
                adapter_dir=str(adapter_dir),
                output_dir=str(tmp_path / 'packaging'),
            )
        )
