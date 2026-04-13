from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATHS = {
    'official_first': REPO_ROOT / 'versions' / 'v4' / 'code' / 'train_official_first_best_v4_minimal.py',
    'best_notebook': REPO_ROOT / 'versions' / 'v4' / 'code' / 'train_best_notebook_sft_v4_minimal.py',
}
EXPECTED_TABLE_KEYS = (
    'max_lora_rank',
    'max_tokens',
    'top_p',
    'temperature',
    'max_num_seqs',
    'gpu_memory_utilization',
    'max_model_len',
)
BASE_README_VALUES = {
    'max_lora_rank': '32',
    'max_tokens': '7680',
    'top_p': '1.0',
    'temperature': '0.0',
    'max_num_seqs': '64',
    'gpu_memory_utilization': '0.85',
    'max_model_len': '8192',
}


@lru_cache(maxsize=None)
def load_module(module_key: str) -> ModuleType:
    module_path = MODULE_PATHS[module_key]
    spec = importlib.util.spec_from_file_location(f'v4_minimal_{module_key}', module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_readme(path: Path, overrides: dict[str, str] | None = None, *, omit_keys: set[str] | None = None) -> None:
    override_map = overrides or {}
    omitted = omit_keys or set()
    rows = ['Overview', 'Parameter\tValue']
    for key in EXPECTED_TABLE_KEYS:
        if key in omitted:
            continue
        rows.append(f"{key}\t{override_map.get(key, BASE_README_VALUES[key])}")
    path.write_text('\n'.join(rows) + '\n', encoding='utf-8')


@pytest.mark.parametrize('module_key', ['official_first', 'best_notebook'])
def test_v4_minimal_scripts_track_expected_readme_table_keys(module_key: str) -> None:
    module = load_module(module_key)

    assert module.README_TABLE_KEYS == EXPECTED_TABLE_KEYS
    assert module.load_readme_contract_from_readme() == {
        key: module.README_EVAL_CONTRACT[key] for key in EXPECTED_TABLE_KEYS
    }


@pytest.mark.parametrize('module_key', ['official_first', 'best_notebook'])
def test_v4_minimal_scripts_reject_missing_readme_row(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    broken_readme = tmp_path / f'{module_key}_missing_row_README.md'
    write_readme(broken_readme, omit_keys={'gpu_memory_utilization'})
    monkeypatch.setattr(module, 'README_PATH', broken_readme)

    with pytest.raises(SystemExit, match='Missing README.md evaluation rows: gpu_memory_utilization'):
        module.load_readme_contract_from_readme()


@pytest.mark.parametrize('module_key', ['official_first', 'best_notebook'])
def test_v4_minimal_scripts_reject_empty_readme_value(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    broken_readme = tmp_path / f'{module_key}_empty_value_README.md'
    write_readme(broken_readme, overrides={'gpu_memory_utilization': ''})
    monkeypatch.setattr(module, 'README_PATH', broken_readme)

    with pytest.raises(
        SystemExit, match='Malformed README.md evaluation row for gpu_memory_utilization: missing value'
    ):
        module.load_readme_contract_from_readme()


@pytest.mark.parametrize('module_key', ['official_first', 'best_notebook'])
def test_v4_minimal_scripts_reject_malformed_readme_value(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    broken_readme = tmp_path / f'{module_key}_malformed_value_README.md'
    write_readme(broken_readme, overrides={'gpu_memory_utilization': 'not-a-float'})
    monkeypatch.setattr(module, 'README_PATH', broken_readme)

    with pytest.raises(SystemExit, match='Malformed README.md evaluation value for gpu_memory_utilization'):
        module.load_readme_contract_from_readme()


@pytest.mark.parametrize('module_key', ['official_first', 'best_notebook'])
def test_v4_minimal_scripts_verify_readme_contract_file_rejects_value_drift(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    drifted_readme = tmp_path / f'{module_key}_drifted_README.md'
    write_readme(drifted_readme, overrides={'max_tokens': '1234'})
    monkeypatch.setattr(module, 'README_PATH', drifted_readme)

    with pytest.raises(SystemExit, match='README.md evaluation table mismatch for max_tokens'):
        module.verify_readme_contract_file()


def test_v4_best_notebook_manifest_surfaces_verified_readme_contract() -> None:
    module = load_module('best_notebook')
    contract = {key: module.README_EVAL_CONTRACT[key] for key in EXPECTED_TABLE_KEYS}

    manifest = module.prepare_manifest(
        candidate_id='candidate',
        config_name='cfg',
        base_model='model',
        train_pack_path=Path('pack.parquet'),
        train_records=1,
        valid_records=0,
        split_strategy='disabled',
        cfg={},
        adapter_dir=Path('adapter'),
        metrics_path=Path('metrics.jsonl'),
        skipped_rows=0,
        prompt_instruction='prompt',
        readme_eval_contract=contract,
    )

    assert manifest['readme_eval_contract'] == contract
    assert manifest['readme_contract_verified_from_readme_file'] is True


def test_v4_official_first_stage_manifest_surfaces_verified_readme_contract() -> None:
    module = load_module('official_first')
    contract = {key: module.README_EVAL_CONTRACT[key] for key in EXPECTED_TABLE_KEYS}

    manifest = module.build_stage_manifest(
        candidate_id='candidate',
        pipeline_role='generalist',
        config_name='cfg',
        base_model='model',
        train_pack_path=Path('pack.parquet'),
        train_records=1,
        valid_records=0,
        split_strategy='disabled',
        cfg={},
        adapter_dir=Path('adapter'),
        metrics_path=Path('metrics.jsonl'),
        skipped_rows=0,
        prompt_instruction='prompt',
        readme_eval_contract=contract,
    )

    assert manifest['readme_eval_contract'] == contract
    assert manifest['readme_contract_verified_from_readme_file'] is True
