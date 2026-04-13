from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATHS = {
    "v5": REPO_ROOT / "versions" / "v5" / "code" / "train_transformers_submission_v5.py",
    "v5_1": REPO_ROOT / "versions" / "v5-1" / "code" / "train_transformers_submission_v5_1.py",
    "v6": REPO_ROOT / "versions" / "v6" / "code" / "train_transformers_submission_v6.py",
    "v7": REPO_ROOT / "versions" / "v7" / "code" / "train_transformers_submission_v7.py",
}
EXPECTED_TABLE_KEYS = (
    "max_lora_rank",
    "max_tokens",
    "top_p",
    "temperature",
    "max_num_seqs",
    "gpu_memory_utilization",
    "max_model_len",
)
BASE_README_VALUES = {
    "max_lora_rank": "32",
    "max_tokens": "7680",
    "top_p": "1.0",
    "temperature": "0.0",
    "max_num_seqs": "64",
    "gpu_memory_utilization": "0.85",
    "max_model_len": "8192",
}
EXPECTED_SUBMISSION_CONTRACT = {
    "required_files": ["adapter_config.json", "adapter_model.safetensors"],
    "max_lora_rank": 32,
    "single_adapter_submission_zip": True,
    "submission_archive_name": "submission.zip",
}


@lru_cache(maxsize=None)
def load_module(module_key: str) -> ModuleType:
    module_path = MODULE_PATHS[module_key]
    spec = importlib.util.spec_from_file_location(f"late_submission_{module_key}", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_readme(path: Path, overrides: dict[str, str] | None = None, *, omit_keys: set[str] | None = None) -> None:
    override_map = overrides or {}
    omitted = omit_keys or set()
    rows = [
        "Evaluation",
        "Submissions are evaluated based on their Accuracy in solving the provided tasks. The NVIDIA Nemotron-3-Nano-30B model is loaded with your LoRA adapter (which must include an adapter_config.json) using the vLLM inference engine.",
        "Parameter\tValue",
    ]
    for key in EXPECTED_TABLE_KEYS:
        if key in omitted:
            continue
        value = override_map.get(key, BASE_README_VALUES[key])
        rows.append(f"{key}\t{value}")
    rows.extend(
        [
            "Submitting",
            "You must submit a LoRA adapter of rank at most 32 for the NVIDIA Nemotron-3-Nano-30B model packaged into a submission.zip file.",
        ]
    )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_track_expected_readme_table_keys(module_key: str) -> None:
    module = load_module(module_key)

    assert module.README_TABLE_KEYS == EXPECTED_TABLE_KEYS
    assert module.load_readme_contract_from_readme() == {
        key: module.README_EVAL_CONTRACT[key] for key in EXPECTED_TABLE_KEYS
    }


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_reject_missing_readme_row(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    broken_readme = tmp_path / f"{module_key}_missing_row_README.md"
    write_readme(broken_readme, omit_keys={"gpu_memory_utilization"})
    monkeypatch.setattr(module, "README_PATH", broken_readme)

    with pytest.raises(SystemExit, match="Missing README.md evaluation rows: gpu_memory_utilization"):
        module.load_readme_contract_from_readme()


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_reject_empty_readme_value(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    broken_readme = tmp_path / f"{module_key}_empty_value_README.md"
    write_readme(broken_readme, overrides={"gpu_memory_utilization": ""})
    monkeypatch.setattr(module, "README_PATH", broken_readme)

    with pytest.raises(
        SystemExit, match="Malformed README.md evaluation row for gpu_memory_utilization: missing value"
    ):
        module.load_readme_contract_from_readme()


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_reject_malformed_readme_value(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    broken_readme = tmp_path / f"{module_key}_malformed_value_README.md"
    write_readme(broken_readme, overrides={"gpu_memory_utilization": "not-a-float"})
    monkeypatch.setattr(module, "README_PATH", broken_readme)

    with pytest.raises(SystemExit, match="Malformed README.md evaluation value for gpu_memory_utilization"):
        module.load_readme_contract_from_readme()


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_verify_readme_contract_file_rejects_value_drift(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    drifted_readme = tmp_path / f"{module_key}_drifted_README.md"
    write_readme(drifted_readme, overrides={"max_tokens": "1234"})
    monkeypatch.setattr(module, "README_PATH", drifted_readme)

    with pytest.raises(SystemExit, match="README.md evaluation table mismatch for max_tokens"):
        module.verify_readme_contract_file()


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_load_readme_submission_contract_from_readme(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    readme_path = tmp_path / f"{module_key}_submission_README.md"
    write_readme(readme_path)
    monkeypatch.setattr(module, "README_PATH", readme_path)

    assert module.load_readme_submission_contract_from_readme() == EXPECTED_SUBMISSION_CONTRACT


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_reject_missing_submission_zip_clause(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    readme_path = tmp_path / f"{module_key}_submission_missing_zip_README.md"
    write_readme(readme_path)
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8").replace("submission.zip file.", "archive file."),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "README_PATH", readme_path)

    with pytest.raises(SystemExit, match="submission archive is submission.zip"):
        module.verify_readme_submission_contract_file()


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_reject_missing_adapter_config_clause(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    readme_path = tmp_path / f"{module_key}_submission_missing_adapter_config_README.md"
    write_readme(readme_path)
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8").replace(
            " (which must include an adapter_config.json)", ""
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "README_PATH", readme_path)

    with pytest.raises(SystemExit, match="adapter must include adapter_config.json"):
        module.load_readme_submission_contract_from_readme()


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_make_submission_zip_surfaces_verified_submission_contract(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    readme_path = tmp_path / f"{module_key}_submission_surface_README.md"
    write_readme(readme_path)
    monkeypatch.setattr(module, "README_PATH", readme_path)

    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    (adapter_dir / "adapter_model.safetensors").write_bytes(b"weights")
    (adapter_dir / "adapter_config.json").write_text(
        (
            '{"base_model_name_or_path": "'
            + module.MODEL_ID
            + '", "target_modules": ["q_proj"], "r": 16, "bias": "none", "use_dora": false, "modules_to_save": null}\n'
        ),
        encoding="utf-8",
    )

    summary = module.make_submission_zip(adapter_dir, tmp_path / "submission.zip")
    assert summary["readme_submission_contract_verified_from_readme_file"] is True
    assert summary["readme_submission_contract"] == EXPECTED_SUBMISSION_CONTRACT
    assert "adapter_config.json" in summary["zip_entries"]
    assert summary["validation_summary"]["readme_submission_contract_verified_from_readme_file"] is True


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_make_submission_zip_rejects_zip_name_drift(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    readme_path = tmp_path / f"{module_key}_submission_zip_drift_README.md"
    write_readme(readme_path)
    monkeypatch.setattr(module, "README_PATH", readme_path)

    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    (adapter_dir / "adapter_model.safetensors").write_bytes(b"weights")
    (adapter_dir / "adapter_config.json").write_text(
        (
            '{"base_model_name_or_path": "'
            + module.MODEL_ID
            + '", "target_modules": ["q_proj"], "r": 16, "bias": "none", "use_dora": false, "modules_to_save": null}\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="zip filename must be submission.zip"):
        module.make_submission_zip(adapter_dir, tmp_path / f"{module_key}.zip")


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_validate_adapter_dir_rejects_non_integer_rank(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    readme_path = tmp_path / f"{module_key}_submission_bad_rank_README.md"
    write_readme(readme_path)
    monkeypatch.setattr(module, "README_PATH", readme_path)

    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    (adapter_dir / "adapter_model.safetensors").write_bytes(b"weights")
    (adapter_dir / "adapter_config.json").write_text(
        (
            '{"base_model_name_or_path": "'
            + module.MODEL_ID
            + '", "target_modules": ["q_proj"], "r": "oops", "bias": "none", "use_dora": false, "modules_to_save": null}\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="r must be an integer"):
        module.validate_adapter_dir(adapter_dir)


@pytest.mark.parametrize("module_key", ["v5", "v5_1", "v6", "v7"])
def test_late_submission_scripts_validate_adapter_dir_rejects_non_positive_rank(
    module_key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module(module_key)
    readme_path = tmp_path / f"{module_key}_submission_zero_rank_README.md"
    write_readme(readme_path)
    monkeypatch.setattr(module, "README_PATH", readme_path)

    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    (adapter_dir / "adapter_model.safetensors").write_bytes(b"weights")
    (adapter_dir / "adapter_config.json").write_text(
        (
            '{"base_model_name_or_path": "'
            + module.MODEL_ID
            + '", "target_modules": ["q_proj"], "r": 0, "bias": "none", "use_dora": false, "modules_to_save": null}\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="r must be between 1 and 32"):
        module.validate_adapter_dir(adapter_dir)
