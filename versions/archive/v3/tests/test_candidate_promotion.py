from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_candidate_promotion', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_scaffold_runbook_and_ablation_failure_logging(tmp_path: Path) -> None:
    version_root = tmp_path / 'v3'
    v3_train.ensure_v3_layout_scaffold(version_root)
    assert (version_root / 'conf/data/teacher_trace_real.yaml').exists()
    assert (version_root / 'conf/train/sft_stage_a_weighted_mlx.yaml').exists()
    assert (version_root / 'outputs/runtime/active_model.json').exists()

    candidate_registry = tmp_path / 'candidate_registry.csv'
    promotion_rules = tmp_path / 'promotion_rules.txt'
    runbook = tmp_path / 'runbook.txt'
    v3_train.run_write_runbook_v3(
        SimpleNamespace(
            candidate_registry_path=str(candidate_registry),
            promotion_rules_path=str(promotion_rules),
            output_path=str(runbook),
        )
    )
    header = candidate_registry.read_text(encoding='utf-8').splitlines()[0].split(',')
    assert header[0] == 'candidate_id'
    runbook_text = runbook.read_text(encoding='utf-8')
    assert 'bootstrap-v3' in runbook_text
    assert 'render-cuda-repro-spec' in runbook_text
    assert 'package-peft' in runbook_text

    bad_config = tmp_path / 'bad_ablation.yaml'
    bad_config.write_text(
        yaml.safe_dump(
            {
                'name': 'bad_ablation',
                'stage': 'a',
                'runtime_backend': 'mock',
                'base_model': 'mock-model',
                'lora_r': 8,
                'lora_alpha': 8,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj'],
                'weighted_loss': True,
                'num_epochs': 1.0,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 1,
            }
        ),
        encoding='utf-8',
    )
    ablation_output = tmp_path / 'weighted_ablation_v3.csv'
    v3_train.run_ablation_v3(
        SimpleNamespace(
            manifest_path=None,
            config_paths=[str(bad_config)],
            train_pack_path=str(tmp_path / 'missing_train_pack.parquet'),
            output_root=str(tmp_path / 'ablation_runs'),
            execute=True,
            valid_fold=0,
            valid_fraction=0.5,
            max_train_rows=None,
            max_valid_rows=None,
            candidate_registry_path=str(tmp_path / 'candidate_registry_runtime.csv'),
            result_path=None,
            output_path=str(ablation_output),
            run_id='ablation_failure',
            notes='expected failure',
        )
    )
    ablation = pd.read_csv(ablation_output)
    assert ablation.iloc[-1]['status'] == 'failed'
    assert 'FileNotFoundError' in str(ablation.iloc[-1]['failure_reason'])
