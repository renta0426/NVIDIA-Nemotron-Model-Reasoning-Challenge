from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v2_train_packaging', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v2_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v2_train
SPEC.loader.exec_module(v2_train)


def test_package_peft_and_write_runbook(tmp_path: Path) -> None:
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

    config_path = tmp_path / 'peft_smoke.yaml'
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
    v2_train.run_package_peft(
        SimpleNamespace(config_path=str(config_path), adapter_dir=str(adapter_dir), output_dir=str(output_dir))
    )

    smoke = json.loads((output_dir / 'peft_smoke_result.json').read_text(encoding='utf-8'))
    submission = json.loads((output_dir / 'submission_manifest.json').read_text(encoding='utf-8'))
    assert smoke['all_required_files_present'] is True
    assert smoke['checks']['rank_ok'] is True
    assert smoke['checks']['target_modules_ok'] is True
    assert smoke['checks']['base_model_ok'] is True
    assert smoke['checks']['submission_zip_ok'] is True
    assert (output_dir / 'submission.zip').exists()
    assert submission['lora_rank'] == 16
    assert 'adapter_config.json' in submission['submission_zip_contents']

    candidate_registry_path = tmp_path / 'reports' / 'candidate_registry.csv'
    promotion_rules_path = tmp_path / 'reports' / 'promotion_rules.txt'
    runbook_path = tmp_path / 'reports' / 'runbook.txt'
    v2_train.run_write_runbook(
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
    assert 'build-real-canonical' in runbook_text
    assert 'run-probe --config sc_probe_k8' in runbook_text
    assert 'Daily Score' in promotion_text
    assert 'weekly_score improves by at least +0.003' in promotion_text
