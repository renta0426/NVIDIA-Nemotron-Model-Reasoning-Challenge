from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v3_train_bootstrap', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v3_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v3_train
SPEC.loader.exec_module(v3_train)


def test_fixed_model_repo_id_is_pinned() -> None:
    assert v3_train.DEFAULT_MODEL_REPO_ID == 'lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit'


def test_ensure_v3_layout_scaffold_creates_expected_structure(tmp_path: Path) -> None:
    v3_train.ensure_v3_layout_scaffold(tmp_path)

    expected_dirs = (
        tmp_path / 'conf' / 'data',
        tmp_path / 'conf' / 'train',
        tmp_path / 'conf' / 'package',
        tmp_path / 'data' / 'processed',
        tmp_path / 'data' / 'synth',
        tmp_path / 'data' / 'train_packs',
        tmp_path / 'outputs' / 'audits',
        tmp_path / 'outputs' / 'datasets',
        tmp_path / 'outputs' / 'train',
        tmp_path / 'outputs' / 'eval',
        tmp_path / 'outputs' / 'packaging',
        tmp_path / 'outputs' / 'reports',
    )
    for directory in expected_dirs:
        assert directory.is_dir()

    expected_files = (
        tmp_path / 'conf' / 'data' / 'teacher_trace_real.yaml',
        tmp_path / 'conf' / 'data' / 'format_policy_v3.yaml',
        tmp_path / 'conf' / 'data' / 'preference_pairs.yaml',
        tmp_path / 'conf' / 'data' / 'rft_accept_pool.yaml',
        tmp_path / 'conf' / 'data' / 'mix_stage_a_strong.yaml',
        tmp_path / 'conf' / 'data' / 'mix_stage_b_strong.yaml',
        tmp_path / 'conf' / 'train' / 'sft_stage_a_weighted_mlx.yaml',
        tmp_path / 'conf' / 'train' / 'sft_stage_b_weighted_mlx.yaml',
        tmp_path / 'conf' / 'train' / 'sft_stage_a_cuda_bf16.yaml',
        tmp_path / 'conf' / 'package' / 'cuda_submission_smoke.yaml',
    )
    for path in expected_files:
        assert path.exists()

    train_cfg = yaml.safe_load((tmp_path / 'conf' / 'train' / 'sft_stage_a_weighted_mlx.yaml').read_text(encoding='utf-8'))
    package_cfg = yaml.safe_load((tmp_path / 'conf' / 'package' / 'cuda_submission_smoke.yaml').read_text(encoding='utf-8'))
    assert train_cfg['weighted_loss'] is True
    assert package_cfg['submission_zip_name'] == 'submission.zip'


def test_parser_exposes_v3_commands() -> None:
    parser = v3_train.build_parser()

    bootstrap_args = parser.parse_args(['bootstrap-v3'])
    train_args = parser.parse_args(['train-sft'])
    cuda_args = parser.parse_args(['render-cuda-repro-spec', '--train-manifest-path', 'manifest.json'])

    assert bootstrap_args.func is v3_train.run_bootstrap_v3
    assert train_args.func is v3_train.run_train_sft_v3
    assert Path(train_args.config_path).name == 'sft_stage_a_weighted_mlx.yaml'
    assert cuda_args.func is v3_train.run_render_cuda_repro_spec_v3
