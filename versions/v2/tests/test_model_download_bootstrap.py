from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
SPEC = importlib.util.spec_from_file_location('v2_train', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
v2_train = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v2_train
SPEC.loader.exec_module(v2_train)


def test_fixed_model_repo_id_is_pinned() -> None:
    assert v2_train.DEFAULT_MODEL_REPO_ID == 'lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit'


def test_default_model_directory_uses_local_name() -> None:
    spec = v2_train.ModelDownloadSpec(local_name='custom-model-name')
    assert v2_train.default_model_directory(spec).name == 'custom-model-name'


def test_build_model_manifest_collects_file_stats(tmp_path: Path) -> None:
    snapshot_dir = tmp_path / 'snapshot'
    snapshot_dir.mkdir()
    (snapshot_dir / 'config.json').write_text('{}', encoding='utf-8')
    (snapshot_dir / 'weights.safetensors').write_bytes(b'abcde')
    spec = v2_train.ModelDownloadSpec()

    manifest = v2_train.build_model_manifest(spec, snapshot_dir)

    assert manifest['repo_id'] == v2_train.DEFAULT_MODEL_REPO_ID
    assert manifest['file_count'] == 2
    assert manifest['total_size_bytes'] == 7
    assert manifest['snapshot_dir'] == str(snapshot_dir.resolve())


def test_default_lms_model_path_uses_repo_structure(tmp_path: Path) -> None:
    path = v2_train.default_lms_model_path(
        v2_train.DEFAULT_MODEL_REPO_ID,
        models_root=tmp_path,
    )

    assert path == tmp_path / 'lmstudio-community' / 'NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit'


def test_ensure_lms_model_symlink_creates_link(tmp_path: Path) -> None:
    snapshot_dir = tmp_path / 'snapshot'
    snapshot_dir.mkdir()

    link = v2_train.ensure_lms_model_symlink(
        snapshot_dir,
        v2_train.DEFAULT_MODEL_REPO_ID,
        models_root=tmp_path / 'models',
    )

    assert link.is_symlink()
    assert link.resolve() == snapshot_dir.resolve()


def test_upsert_registry_entry_replaces_same_repo_and_name() -> None:
    base = {
        'repo_id': v2_train.DEFAULT_MODEL_REPO_ID,
        'local_name': v2_train.DEFAULT_LOCAL_MODEL_NAME,
        'revision': None,
        'snapshot_dir': '/tmp/old',
    }
    replacement = {
        'repo_id': v2_train.DEFAULT_MODEL_REPO_ID,
        'local_name': v2_train.DEFAULT_LOCAL_MODEL_NAME,
        'revision': None,
        'snapshot_dir': '/tmp/new',
    }

    updated = v2_train.upsert_registry_entry([base], replacement)

    assert len(updated) == 1
    assert updated[0]['snapshot_dir'] == '/tmp/new'


def test_resolve_active_model_directory_reads_manifest(tmp_path: Path) -> None:
    snapshot_dir = tmp_path / 'model'
    snapshot_dir.mkdir()
    active_manifest = tmp_path / 'active_model.json'
    v2_train.save_json_file(
        active_manifest,
        {
            'repo_id': v2_train.DEFAULT_MODEL_REPO_ID,
            'local_name': v2_train.DEFAULT_LOCAL_MODEL_NAME,
            'snapshot_dir': str(snapshot_dir),
        },
    )

    resolved = v2_train.resolve_active_model_directory(active_manifest)

    assert resolved == snapshot_dir


def test_parser_includes_smoke_model_command() -> None:
    parser = v2_train.build_parser()

    args = parser.parse_args(['smoke-model'])

    assert args.command == 'smoke-model'
    assert args.runtime == 'auto'
    assert args.max_tokens == 8
