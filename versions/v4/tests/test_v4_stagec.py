from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v4_train_stagec', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v4_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v4_train
SPEC.loader.exec_module(v4_train)


def _set_v4_outputs(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_EXPERIMENT_LOG_PATH', tmp_path / 'experiment_log.jsonl')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_LOCAL_SCOREBOARD_OUTPUT_PATH', tmp_path / 'local_scoreboard_v4.csv')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_FAMILY_REGRET_OUTPUT_PATH', tmp_path / 'family_regret_v4.csv')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_CANDIDATE_REGISTRY_OUTPUT_PATH', tmp_path / 'candidate_registry_v4.csv')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_SPECIALIST_REGISTRY_OUTPUT_PATH', tmp_path / 'specialist_registry_v4.csv')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_MERGE_REGISTRY_OUTPUT_PATH', tmp_path / 'merge_registry_v4.csv')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_CUDA_REPRO_REGISTRY_OUTPUT_PATH', tmp_path / 'cuda_registry_v4.csv')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_PROMOTION_RULES_OUTPUT_PATH', tmp_path / 'promotion_rules_v4.txt')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_TRAINING_RUNBOOK_OUTPUT_PATH', tmp_path / 'runbook_v4.txt')
    monkeypatch.setattr(v4_train, 'DEFAULT_V4_SUBMISSION_MANIFEST_OUTPUT_PATH', tmp_path / 'submission_manifest_v4.json')


def test_score_candidate_updates_v4_scoreboard(monkeypatch, tmp_path: Path) -> None:
    _set_v4_outputs(monkeypatch, tmp_path)

    adapter_dir = tmp_path / 'adapter_score'
    adapter_dir.mkdir()
    manifest_path = tmp_path / 'candidate_manifest.json'
    manifest_path.write_text(
        json.dumps(
            {
                'version': 'v4',
                'stage': 'c',
                'config_name': 'unit_score',
                'candidate_id': 'cand-score',
                'parent_candidate_id': 'parent-a',
                'model': {'base_model': 'mock-model'},
                'execution': {'adapter_dir': str(adapter_dir)},
            }
        ),
        encoding='utf-8',
    )

    config_path = tmp_path / 'score.yaml'
    config_path.write_text(
        yaml.safe_dump(
            {
                'gate_name': 'serious',
                'datasets': [
                    {'dataset_name': 'shadow_256', 'input_path': str(tmp_path / 'shadow_256.csv'), 'eval_config': 'official_lb'},
                    {'dataset_name': 'hard_shadow_256', 'input_path': str(tmp_path / 'hard_shadow_256.csv'), 'eval_config': 'official_lb'},
                ],
            }
        ),
        encoding='utf-8',
    )

    def fake_eval(candidate, dataset_cfg, gate_name, out_dir):
        out_dir.mkdir(parents=True, exist_ok=True)
        overall = 0.76 if dataset_cfg['dataset_name'] == 'shadow_256' else 0.82
        summary = pd.DataFrame(
            [
                {
                    'run_name': f"{candidate.candidate_id}-{dataset_cfg['dataset_name']}",
                    'overall_acc': overall,
                    'format_fail_rate': 0.02,
                    'extraction_fail_rate': 0.01,
                    'avg_output_len_chars': 88.0,
                    'boxed_rate': 0.91,
                }
            ]
        )
        family_metrics = pd.DataFrame(
            [
                {'family': 'bit_manipulation', 'acc': 0.80, 'format_fail_rate': 0.02},
                {'family': 'text_decryption', 'acc': 0.79, 'format_fail_rate': 0.03},
                {'family': 'symbol_equation', 'acc': 0.86, 'format_fail_rate': 0.01},
            ]
        )
        return summary, family_metrics, pd.DataFrame()

    monkeypatch.setattr(v4_train, 'evaluate_dataset_to_dir_v4', fake_eval)
    monkeypatch.setattr(
        v4_train,
        'lookup_parent_metrics_v4',
        lambda parent_candidate_id, dataset_name: {
            'overall_accuracy': 0.70,
            'hard_split_accuracy': 0.74,
            'format_fail_rate': 0.05,
            'extraction_fail_rate': 0.03,
            'bit_accuracy': 0.70,
            'text_accuracy': 0.70,
            'symbol_accuracy': 0.80,
        },
    )
    monkeypatch.setattr(v4_train, 'write_family_regret_rows_v4', lambda **kwargs: None)

    v4_train.run_score_candidate_v4(
        SimpleNamespace(
            config_path=str(config_path),
            manifest_path=str(manifest_path),
            adapter_path=None,
            candidate_id=None,
            output_root=str(tmp_path / 'eval'),
        )
    )

    scoreboard = pd.read_csv(tmp_path / 'local_scoreboard_v4.csv')
    registry = list(csv.DictReader((tmp_path / 'candidate_registry_v4.csv').open('r', encoding='utf-8')))
    assert list(scoreboard['dataset_name']) == ['shadow_256', 'hard_shadow_256']
    assert registry[0]['candidate_id'] == 'cand-score'
    assert registry[0]['submit_value'] == 'True'


def test_train_merge_and_render_v4_flow(monkeypatch, tmp_path: Path) -> None:
    _set_v4_outputs(monkeypatch, tmp_path)

    rft_pack = tmp_path / 'stage_c_rft_mix_v4.parquet'
    pd.DataFrame(
        [
            {'id': 'row-1', 'prompt': 'Compute 1+1.', 'answer': '2', 'family': 'symbol_equation', 'format_policy': 'boxed'},
            {'id': 'row-2', 'prompt': 'Compute 2+2.', 'answer': '4', 'family': 'symbol_equation', 'format_policy': 'boxed'},
        ]
    ).to_parquet(rft_pack, index=False)

    pref_pack = tmp_path / 'stage_c_preference_mix_v4.parquet'
    pd.DataFrame(
        [
            {'pair_id': 'p1', 'pair_kind': 'format', 'prompt': 'Solve.', 'family': 'symbol_equation', 'chosen_output': r'\boxed{3}', 'rejected_output': '3'},
            {'pair_id': 'p2', 'pair_kind': 'format', 'prompt': 'Invert.', 'family': 'bit_manipulation', 'chosen_output': r'\boxed{101}', 'rejected_output': r'\boxed{111}'},
        ]
    ).to_parquet(pref_pack, index=False)

    rft_cfg = tmp_path / 'rft_stage_c_mlx.yaml'
    rft_cfg.write_text(
        yaml.safe_dump(
            {
                'name': 'rft_stage_c_mlx',
                'runtime_backend': 'mock',
                'base_model': 'mock-model',
                'target_modules': ['q_proj'],
                'lora_r': 32,
                'num_epochs': 1.0,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 1,
            }
        ),
        encoding='utf-8',
    )
    generalist_dir = tmp_path / 'generalist_run'
    v4_train.run_train_stage_c_rft_v4(
        SimpleNamespace(
            config_path=str(rft_cfg),
            train_pack_path=str(rft_pack),
            output_dir=str(generalist_dir),
            candidate_id='cand-generalist',
            parent_candidate_id='v3_stage_a_baseline',
            init_adapter_path=None,
            valid_fold=-1,
            valid_fraction=0.1,
            max_train_rows=None,
            max_valid_rows=None,
            execute=True,
        )
    )

    specialist_cfg = tmp_path / 'specialist_format_mlx.yaml'
    specialist_cfg.write_text(
        yaml.safe_dump(
            {
                'name': 'specialist_format_mlx',
                'runtime_backend': 'mock',
                'base_model': 'mock-model',
                'target_modules': ['q_proj'],
                'pair_kind': 'format',
                'specialist_tag': 'format',
                'lora_r': 32,
                'num_epochs': 1.0,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 1,
            }
        ),
        encoding='utf-8',
    )
    specialist_dir = tmp_path / 'specialist_run'
    v4_train.run_train_specialist_v4(
        SimpleNamespace(
            config_path=str(specialist_cfg),
            pair_data_path=str(pref_pack),
            output_dir=str(specialist_dir),
            candidate_id='cand-specialist',
            parent_candidate_id='v3_stage_a_baseline',
            init_adapter_path=None,
            pair_kind='format',
            specialist_tag='format',
            family_filter=[],
            valid_fold=-1,
            valid_fraction=0.1,
            execute=True,
        )
    )

    merge_cfg = tmp_path / 'generalist_specialist_merge.yaml'
    merge_cfg.write_text(yaml.safe_dump({'weights': {'generalist': 0.75, 'specialist': 0.25}}), encoding='utf-8')
    merge_dir = tmp_path / 'merge_run'
    generalist_manifest = generalist_dir / 'cand-generalist_manifest.json'
    specialist_manifest = specialist_dir / 'cand-specialist_manifest.json'
    v4_train.run_merge_candidates_v4(
        SimpleNamespace(
            config_path=str(merge_cfg),
            generalist_candidate_id=None,
            generalist_manifest_path=str(generalist_manifest),
            generalist_adapter_path=None,
            specialist_candidate_id=None,
            specialist_manifest_path=str(specialist_manifest),
            specialist_adapter_path=None,
            merge_id='merged-candidate',
            output_dir=str(merge_dir),
        )
    )

    compress_cfg = tmp_path / 'rank32_compress.yaml'
    compress_cfg.write_text(yaml.safe_dump({'method': 'noop_same_shape_rank32', 'rank_cap': 32}), encoding='utf-8')
    compressed_dir = tmp_path / 'compressed_adapter'
    merged_adapter_dir = merge_dir / 'adapter_merged-candidate'
    v4_train.run_compress_merge_rank32_v4(
        SimpleNamespace(
            config_path=str(compress_cfg),
            adapter_path=str(merged_adapter_dir),
            output_dir=str(compressed_dir),
        )
    )

    cuda_cfg = tmp_path / 'stage_c_cuda_bf16.yaml'
    cuda_cfg.write_text(yaml.safe_dump({'base_model_name_or_path': 'nvidia/mock-base', 'precision': 'bf16'}), encoding='utf-8')
    repro_spec = tmp_path / 'cuda_reproduction_spec_v4.yaml'
    v4_train.run_render_cuda_repro_spec_v4(
        SimpleNamespace(
            config_path=str(cuda_cfg),
            candidate_id=None,
            manifest_path=str(merge_dir / 'merged-candidate_manifest.json'),
            adapter_path=None,
            output_path=str(repro_spec),
            registry_path=str(tmp_path / 'cuda_registry_v4.csv'),
            submission_manifest_path=str(tmp_path / 'submission_manifest_v4.json'),
        )
    )

    runbook_path = tmp_path / 'runbook_v4.txt'
    promotion_rules_path = tmp_path / 'promotion_rules_v4.txt'
    v4_train.run_write_runbook_v4(
        SimpleNamespace(
            candidate_registry_path=str(tmp_path / 'candidate_registry_v4.csv'),
            promotion_rules_path=str(promotion_rules_path),
            output_path=str(runbook_path),
        )
    )

    merged_manifest = json.loads((merge_dir / 'merged-candidate_manifest.json').read_text(encoding='utf-8'))
    submission_manifest = json.loads((tmp_path / 'submission_manifest_v4.json').read_text(encoding='utf-8'))
    runbook_text = runbook_path.read_text(encoding='utf-8')
    promotion_text = promotion_rules_path.read_text(encoding='utf-8')
    assert merged_manifest['candidate_id'] == 'merged-candidate'
    assert (compressed_dir / 'adapters.safetensors').exists()
    assert submission_manifest['status'] == 'pending_local_gate'
    assert 'bootstrap-v4' in runbook_text
    assert 'train-stage-c-rft' in runbook_text
    assert 'no meaningful local gain -> do not submit' in promotion_text
