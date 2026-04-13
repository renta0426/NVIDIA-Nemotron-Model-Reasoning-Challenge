from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v4_train_bootstrap', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v4_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v4_train
SPEC.loader.exec_module(v4_train)


def test_ensure_v4_layout_scaffold_creates_expected_structure(tmp_path: Path) -> None:
    v4_train.ensure_v4_layout_scaffold(tmp_path)

    expected_dirs = (
        tmp_path / 'conf' / 'data',
        tmp_path / 'conf' / 'train',
        tmp_path / 'conf' / 'eval',
        tmp_path / 'conf' / 'merge',
        tmp_path / 'conf' / 'package',
        tmp_path / 'data' / 'preference',
        tmp_path / 'data' / 'rft',
        tmp_path / 'data' / 'train_packs',
        tmp_path / 'outputs' / 'handoff',
        tmp_path / 'outputs' / 'reports',
        tmp_path / 'outputs' / 'train',
    )
    for directory in expected_dirs:
        assert directory.is_dir()

    expected_files = (
        tmp_path / 'conf' / 'data' / 'preference_format.yaml',
        tmp_path / 'conf' / 'data' / 'preference_correctness.yaml',
        tmp_path / 'conf' / 'data' / 'rft_accept_pool.yaml',
        tmp_path / 'conf' / 'data' / 'stage_c_rft_mix.yaml',
        tmp_path / 'conf' / 'data' / 'stage_c_preference_mix.yaml',
        tmp_path / 'conf' / 'train' / 'rft_stage_c_mlx.yaml',
        tmp_path / 'conf' / 'train' / 'dpo_format_mlx.yaml',
        tmp_path / 'conf' / 'eval' / 'candidate_score_serious.yaml',
        tmp_path / 'conf' / 'merge' / 'generalist_specialist_merge.yaml',
        tmp_path / 'conf' / 'package' / 'cuda_submission_smoke.yaml',
        tmp_path / 'data' / 'processed' / 'candidate_registry_v4.csv',
        tmp_path / 'outputs' / 'reports' / 'local_scoreboard_v4.csv',
    )
    for path in expected_files:
        assert path.exists()

    package_cfg = yaml.safe_load((tmp_path / 'conf' / 'package' / 'cuda_submission_smoke.yaml').read_text(encoding='utf-8'))
    eval_cfg = yaml.safe_load((tmp_path / 'conf' / 'eval' / 'candidate_score_serious.yaml').read_text(encoding='utf-8'))
    assert package_cfg['submission_zip_name'] == 'submission.zip'
    assert [dataset['dataset_name'] for dataset in eval_cfg['datasets']] == ['shadow_256', 'hard_shadow_256']


def test_parser_exposes_v4_commands() -> None:
    parser = v4_train.build_parser()

    bootstrap_args = parser.parse_args(['bootstrap-v4'])
    score_args = parser.parse_args(['score-candidate', '--candidate-id', 'v3_stage_a_baseline'])
    train_args = parser.parse_args(['train-stage-c-rft', '--output-dir', 'tmp-run'])
    merge_args = parser.parse_args(
        [
            'merge-candidates',
            '--output-dir',
            'tmp-merge',
            '--generalist-manifest-path',
            'generalist.json',
            '--specialist-manifest-path',
            'specialist.json',
        ]
    )

    assert bootstrap_args.func is v4_train.run_bootstrap_v4
    assert score_args.func is v4_train.run_score_candidate_v4
    assert train_args.func is v4_train.run_train_stage_c_rft_v4
    assert merge_args.func is v4_train.run_merge_candidates_v4
    assert Path(train_args.config_path).name == 'rft_stage_c_mlx.yaml'
