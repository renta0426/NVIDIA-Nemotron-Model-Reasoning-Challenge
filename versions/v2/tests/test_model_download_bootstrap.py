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
