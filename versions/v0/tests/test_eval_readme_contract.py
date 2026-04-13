from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest
import yaml


def load_v0_module():
    module_name = "v0_train"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = Path(__file__).resolve().parents[1] / "code" / "train.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v0 = load_v0_module()


def write_readme(path: Path, overrides: dict[str, str] | None = None, *, omit_keys: set[str] | None = None) -> None:
    override_map = overrides or {}
    omitted = omit_keys or set()
    base_values = {
        "max_lora_rank": "32",
        "max_tokens": "7680",
        "top_p": "1.0",
        "temperature": "0.0",
        "max_num_seqs": "64",
        "gpu_memory_utilization": "0.85",
        "max_model_len": "8192",
    }
    rows = ["Overview", "Parameter\tValue"]
    for key in v0.README_TABLE_KEYS:
        if key in omitted:
            continue
        rows.append(f"{key}\t{override_map.get(key, base_values[key])}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_eval_yaml(path: Path, payload: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def base_official_payload() -> dict[str, object]:
    return {
        "name": "official_lb",
        "max_lora_rank": 32,
        "max_tokens": 7680,
        "top_p": 1.0,
        "temperature": 0.0,
        "max_num_seqs": 64,
        "gpu_memory_utilization": 0.85,
        "max_model_len": 8192,
        "enable_thinking": True,
        "add_generation_prompt": True,
        "boxed_instruction": v0.OFFICIAL_BOXED_INSTRUCTION,
        "strict_chat_template": True,
    }


def test_official_lb_loads_when_config_matches_readme() -> None:
    config = v0.load_eval_config("official_lb")

    assert config.name == "official_lb"
    assert config.max_lora_rank == 32
    assert config.max_tokens == 7680
    assert config.top_p == 1.0
    assert config.temperature == 0.0
    assert config.max_num_seqs == 64
    assert config.gpu_memory_utilization == 0.85
    assert config.max_model_len == 8192


def test_official_lb_rejects_missing_readme_row(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    broken_readme = tmp_path / "README_missing_row.md"
    write_readme(broken_readme, omit_keys={"gpu_memory_utilization"})
    monkeypatch.setattr(v0, "README_PATH", broken_readme)

    with pytest.raises(SystemExit, match="Missing README.md evaluation rows: gpu_memory_utilization"):
        v0.load_eval_config("official_lb")


def test_official_lb_rejects_empty_readme_value(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    broken_readme = tmp_path / "README_empty_value.md"
    write_readme(broken_readme, overrides={"gpu_memory_utilization": ""})
    monkeypatch.setattr(v0, "README_PATH", broken_readme)

    with pytest.raises(
        SystemExit, match="Malformed README.md evaluation row for gpu_memory_utilization: missing value"
    ):
        v0.load_eval_config("official_lb")


def test_official_lb_rejects_malformed_readme_value(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    broken_readme = tmp_path / "README_malformed_value.md"
    write_readme(broken_readme, overrides={"gpu_memory_utilization": "not-a-float"})
    monkeypatch.setattr(v0, "README_PATH", broken_readme)

    with pytest.raises(SystemExit, match="Malformed README.md evaluation value for gpu_memory_utilization"):
        v0.load_eval_config("official_lb")


def test_official_lb_rejects_config_drift_against_readme(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    matching_readme = tmp_path / "README_matching.md"
    write_readme(matching_readme)
    monkeypatch.setattr(v0, "README_PATH", matching_readme)

    drifted_config_path = tmp_path / "official_lb_drifted.yaml"
    payload = base_official_payload()
    payload["max_tokens"] = 1234
    write_eval_yaml(drifted_config_path, payload)

    with pytest.raises(SystemExit, match="README.md evaluation table mismatch for official_lb.max_tokens"):
        v0.load_eval_config(str(drifted_config_path))


def test_non_official_eval_config_skips_readme_guard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    broken_readme = tmp_path / "README_missing_row.md"
    write_readme(broken_readme, omit_keys={"gpu_memory_utilization"})
    monkeypatch.setattr(v0, "README_PATH", broken_readme)

    custom_config_path = tmp_path / "custom_probe.yaml"
    payload = base_official_payload()
    payload["name"] = "custom_probe"
    payload["max_tokens"] = 1234
    write_eval_yaml(custom_config_path, payload)

    config = v0.load_eval_config(str(custom_config_path))

    assert config.name == "custom_probe"
    assert config.max_tokens == 1234
