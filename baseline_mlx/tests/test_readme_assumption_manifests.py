from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATHS = {
    "phase0_offline_eval": REPO_ROOT / "baseline" / "cot" / "phase0_offline_eval" / "build_phase0_offline_eval.py",
    "leaderboard_proxy_dataset": REPO_ROOT
    / "cuda-train-data-analysis-v1"
    / "proof_first_solver_factory_routing"
    / "build_leaderboard_proxy_dataset.py",
    "binary_route_aware_delta": REPO_ROOT
    / "cuda-train-data-analysis-v1"
    / "proof_first_solver_factory_routing"
    / "build_binary_route_aware_delta.py",
    "mlx_v0_phase0": REPO_ROOT / "mac_workspace" / "v0" / "phase2_binary_dsl_mlx_v0.py",
    "mlx_v1_phase0": REPO_ROOT / "mac_workspace" / "v1" / "phase2_binary_dsl_mlx_v1.py",
}


@lru_cache(maxsize=None)
def load_module(module_key: str) -> ModuleType:
    module_path = MODULE_PATHS[module_key]
    spec = importlib.util.spec_from_file_location(f"readme_assumption_{module_key}", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sample_benchmark_rows() -> list[dict[str, object]]:
    return [
        {
            "family_short": "Bit",
            "selection_tier": "verified_trace_ready",
            "template_subtype": "bit_other",
            "binary_focus_bucket": "supported_bijection",
        }
    ]


def write_readme_table(
    tmp_path: Path,
    *,
    overrides: dict[str, str] | None = None,
    omitted_keys: set[str] | None = None,
) -> Path:
    values = {
        "max_lora_rank": "32",
        "max_tokens": "7680",
        "top_p": "1.0",
        "temperature": "0.0",
        "max_num_seqs": "64",
        "gpu_memory_utilization": "0.85",
        "max_model_len": "8192",
    }
    if overrides is not None:
        values.update(overrides)
    omitted = omitted_keys or set()
    readme_path = tmp_path / "README.md"
    lines = ["Overview", "Parameter\tValue"]
    for key, value in values.items():
        if key in omitted:
            continue
        lines.append(f"{key}\t{value}")
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return readme_path


@pytest.mark.parametrize(
    ("module_key", "build_manifest_name"),
    [
        ("phase0_offline_eval", "build_manifest"),
        ("mlx_v0_phase0", "build_phase0_manifest"),
        ("mlx_v1_phase0", "build_phase0_manifest"),
    ],
)
def test_phase0_manifest_builders_include_full_readme_assumptions(
    module_key: str, build_manifest_name: str
) -> None:
    module = load_module(module_key)
    build_manifest = getattr(module, build_manifest_name)
    manifest = build_manifest(
        analysis_csv=Path("analysis.csv"),
        general_rows=sample_benchmark_rows(),
        binary_rows=sample_benchmark_rows(),
        symbol_rows=sample_benchmark_rows(),
        holdouts=[{"holdout_kind": "binary_hard", "fold": 0}],
    )

    assumptions = manifest["readme_eval_assumptions"]
    assert assumptions["temperature"] == 0.0
    assert assumptions["top_p"] == 1.0
    assert assumptions["max_tokens"] == 7680
    assert assumptions["max_num_seqs"] == 64
    assert assumptions["gpu_memory_utilization"] == 0.85
    assert assumptions["max_model_len"] == 8192
    assert manifest["readme_eval_assumptions_verified_from_readme_file"] is True

    report_text = module.render_phase0_report(manifest)
    assert "- gpu_memory_utilization: `0.85`" in report_text


@pytest.mark.parametrize(
    ("module_key", "loader_name", "verify_name", "expected_attr"),
    [
        (
            "phase0_offline_eval",
            "load_readme_eval_assumptions_from_readme",
            "verify_readme_eval_assumptions_file",
            "README_EVAL_ASSUMPTIONS",
        ),
        (
            "leaderboard_proxy_dataset",
            "load_readme_eval_contract_from_readme",
            "verify_readme_eval_contract_file",
            "README_EVAL_CONTRACT",
        ),
        (
            "binary_route_aware_delta",
            "load_readme_eval_contract_from_readme",
            "verify_readme_eval_contract_file",
            "README_EVAL_CONTRACT",
        ),
        (
            "mlx_v0_phase0",
            "load_readme_eval_assumptions_from_readme",
            "verify_readme_eval_assumptions_file",
            "README_EVAL_ASSUMPTIONS",
        ),
        (
            "mlx_v1_phase0",
            "load_readme_eval_assumptions_from_readme",
            "verify_readme_eval_assumptions_file",
            "README_EVAL_ASSUMPTIONS",
        ),
    ],
)
def test_small_readme_assumption_modules_reload_live_readme(
    module_key: str,
    loader_name: str,
    verify_name: str,
    expected_attr: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(module_key)
    monkeypatch.setattr(module, "README_PATH", write_readme_table(tmp_path))
    loader = getattr(module, loader_name)
    verify = getattr(module, verify_name)

    assert loader() == getattr(module, expected_attr)
    assert verify() == getattr(module, expected_attr)


@pytest.mark.parametrize(
    ("module_key", "loader_name"),
    [
        ("phase0_offline_eval", "load_readme_eval_assumptions_from_readme"),
        ("leaderboard_proxy_dataset", "load_readme_eval_contract_from_readme"),
        ("binary_route_aware_delta", "load_readme_eval_contract_from_readme"),
        ("mlx_v0_phase0", "load_readme_eval_assumptions_from_readme"),
        ("mlx_v1_phase0", "load_readme_eval_assumptions_from_readme"),
    ],
)
def test_small_readme_assumption_modules_reject_missing_readme_row(
    module_key: str,
    loader_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(module_key)
    monkeypatch.setattr(
        module,
        "README_PATH",
        write_readme_table(tmp_path, omitted_keys={"gpu_memory_utilization"}),
    )
    loader = getattr(module, loader_name)

    with pytest.raises(SystemExit, match="Missing README.md evaluation rows: gpu_memory_utilization"):
        loader()


@pytest.mark.parametrize(
    ("module_key", "loader_name", "overrides", "message"),
    [
        (
            "phase0_offline_eval",
            "load_readme_eval_assumptions_from_readme",
            {"gpu_memory_utilization": ""},
            "Malformed README.md evaluation row for gpu_memory_utilization: missing value",
        ),
        (
            "leaderboard_proxy_dataset",
            "load_readme_eval_contract_from_readme",
            {"gpu_memory_utilization": ""},
            "Malformed README.md evaluation row for gpu_memory_utilization: missing value",
        ),
        (
            "binary_route_aware_delta",
            "load_readme_eval_contract_from_readme",
            {"gpu_memory_utilization": ""},
            "Malformed README.md evaluation row for gpu_memory_utilization: missing value",
        ),
        (
            "mlx_v0_phase0",
            "load_readme_eval_assumptions_from_readme",
            {"gpu_memory_utilization": ""},
            "Malformed README.md evaluation row for gpu_memory_utilization: missing value",
        ),
        (
            "mlx_v1_phase0",
            "load_readme_eval_assumptions_from_readme",
            {"gpu_memory_utilization": ""},
            "Malformed README.md evaluation row for gpu_memory_utilization: missing value",
        ),
        (
            "phase0_offline_eval",
            "load_readme_eval_assumptions_from_readme",
            {"max_tokens": "oops"},
            "Malformed README.md evaluation value for max_tokens: 'oops'",
        ),
        (
            "leaderboard_proxy_dataset",
            "load_readme_eval_contract_from_readme",
            {"max_tokens": "oops"},
            "Malformed README.md evaluation value for max_tokens: 'oops'",
        ),
        (
            "binary_route_aware_delta",
            "load_readme_eval_contract_from_readme",
            {"max_tokens": "oops"},
            "Malformed README.md evaluation value for max_tokens: 'oops'",
        ),
        (
            "mlx_v0_phase0",
            "load_readme_eval_assumptions_from_readme",
            {"max_tokens": "oops"},
            "Malformed README.md evaluation value for max_tokens: 'oops'",
        ),
        (
            "mlx_v1_phase0",
            "load_readme_eval_assumptions_from_readme",
            {"max_tokens": "oops"},
            "Malformed README.md evaluation value for max_tokens: 'oops'",
        ),
    ],
)
def test_small_readme_assumption_modules_reject_malformed_readme_values(
    module_key: str,
    loader_name: str,
    overrides: dict[str, str],
    message: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(module_key)
    monkeypatch.setattr(
        module,
        "README_PATH",
        write_readme_table(tmp_path, overrides=overrides),
    )
    loader = getattr(module, loader_name)

    with pytest.raises(SystemExit, match=message):
        loader()


@pytest.mark.parametrize(
    ("module_key", "verify_name"),
    [
        ("phase0_offline_eval", "verify_readme_eval_assumptions_file"),
        ("leaderboard_proxy_dataset", "verify_readme_eval_contract_file"),
        ("binary_route_aware_delta", "verify_readme_eval_contract_file"),
        ("mlx_v0_phase0", "verify_readme_eval_assumptions_file"),
        ("mlx_v1_phase0", "verify_readme_eval_assumptions_file"),
    ],
)
def test_small_readme_assumption_modules_reject_readme_value_drift(
    module_key: str,
    verify_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(module_key)
    monkeypatch.setattr(
        module,
        "README_PATH",
        write_readme_table(tmp_path, overrides={"max_tokens": "7000"}),
    )
    verify = getattr(module, verify_name)

    with pytest.raises(SystemExit, match="README.md evaluation table mismatch for max_tokens"):
        verify()


def test_leaderboard_proxy_report_lists_full_readme_constraint_set() -> None:
    module = load_module("leaderboard_proxy_dataset")

    assert module.README_EVAL_CONTRACT["max_tokens"] == 7680
    assert module.README_EVAL_CONTRACT["top_p"] == 1.0
    assert module.README_EVAL_CONTRACT["max_num_seqs"] == 64
    assert module.README_EVAL_CONTRACT["gpu_memory_utilization"] == 0.85
    assert module.README_EVAL_CONTRACT["max_model_len"] == 8192

    summary = module.summarize_proxy(
        [
            {
                "proxy_role": "v3f_only",
                "v3f_is_correct": True,
                "current_is_correct": False,
                "_source_split": "phase0",
                "family_short": "Bit",
                "leaderboard_proxy_bucket": "supported_bijection",
            }
        ],
        {"v3f_only": 1},
    )
    assert summary["readme_eval_contract_verified_from_readme_file"] is True

    report_text = module.render_report(
        {
            "selected_role_counts": {"v3f_only": 1},
            "selected_source_split_counts": {"phase0": 1},
            "selected_family_counts": {"Bit": 1},
            "selected_bucket_counts": {"supported_bijection": 1},
            "proxy_scores": {
                "v3f": {"correct": 1, "rows": 1, "accuracy": 1.0},
                "current": {"correct": 0, "rows": 1, "accuracy": 0.0},
            },
        }
    )
    assert "- max_lora_rank: 32" in report_text
    assert "- max_tokens: 7680" in report_text
    assert "- top_p: 1.0" in report_text
    assert "- max_num_seqs: 64" in report_text
    assert "- gpu_memory_utilization: 0.85" in report_text
    assert "- max_model_len: 8192" in report_text


def test_binary_route_aware_delta_contract_includes_full_readme_eval_keys() -> None:
    module = load_module("binary_route_aware_delta")

    assert module.README_EVAL_CONTRACT["metric"] == "Accuracy"
    assert module.README_EVAL_CONTRACT["max_lora_rank"] == 32
    assert module.README_EVAL_CONTRACT["max_tokens"] == 7680
    assert module.README_EVAL_CONTRACT["temperature"] == 0.0
    assert module.README_EVAL_CONTRACT["top_p"] == 1.0
    assert module.README_EVAL_CONTRACT["max_num_seqs"] == 64
    assert module.README_EVAL_CONTRACT["gpu_memory_utilization"] == 0.85
    assert module.README_EVAL_CONTRACT["max_model_len"] == 8192
