from __future__ import annotations

import csv
import importlib.util
import json
import numpy as np
import os
import re
import shlex
import subprocess
import sys
import warnings
from pathlib import Path
from types import ModuleType, SimpleNamespace
import zipfile


MODULE_PATH = Path(__file__).resolve().parents[1] / "reproduce_nemotron_sft_lora_with_cot_v2_mlx.py"
SPEC = importlib.util.spec_from_file_location("baseline_mlx_stage_waiters", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
stage_waiters = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stage_waiters
SPEC.loader.exec_module(stage_waiters)

RECOVERY_MODULE_PATH = Path(__file__).resolve().parents[2] / "launch_reprobridge31_32_recovery.py"
RECOVERY_SPEC = importlib.util.spec_from_file_location("reprobridge31_32_recovery", RECOVERY_MODULE_PATH)
assert RECOVERY_SPEC is not None and RECOVERY_SPEC.loader is not None
recovery_hub = importlib.util.module_from_spec(RECOVERY_SPEC)
sys.modules[RECOVERY_SPEC.name] = recovery_hub
RECOVERY_SPEC.loader.exec_module(recovery_hub)

REPROBRIDGE25_WAITERS_MODULE_PATH = Path(__file__).resolve().parents[2] / "launch_reprobridge25_waiters.py"
REPROBRIDGE25_WAITERS_SPEC = importlib.util.spec_from_file_location(
    "launch_reprobridge25_waiters", REPROBRIDGE25_WAITERS_MODULE_PATH
)
assert REPROBRIDGE25_WAITERS_SPEC is not None and REPROBRIDGE25_WAITERS_SPEC.loader is not None
reprobridge25_waiters = importlib.util.module_from_spec(REPROBRIDGE25_WAITERS_SPEC)
sys.modules[REPROBRIDGE25_WAITERS_SPEC.name] = reprobridge25_waiters
REPROBRIDGE25_WAITERS_SPEC.loader.exec_module(reprobridge25_waiters)

ROOT_MAIN_MODULE_PATH = Path(__file__).resolve().parents[2] / "main.py"
ROOT_MAIN_SPEC = importlib.util.spec_from_file_location("repo_root_main", ROOT_MAIN_MODULE_PATH)
assert ROOT_MAIN_SPEC is not None and ROOT_MAIN_SPEC.loader is not None
root_main = importlib.util.module_from_spec(ROOT_MAIN_SPEC)
sys.modules[ROOT_MAIN_SPEC.name] = root_main
ROOT_MAIN_SPEC.loader.exec_module(root_main)

PTY_HEALTH_PROBE_MODULE_PATH = Path(__file__).resolve().parents[2] / "pty_health_probe.py"
PTY_HEALTH_PROBE_SPEC = importlib.util.spec_from_file_location("repo_root_pty_health_probe", PTY_HEALTH_PROBE_MODULE_PATH)
assert PTY_HEALTH_PROBE_SPEC is not None and PTY_HEALTH_PROBE_SPEC.loader is not None
pty_health_probe = importlib.util.module_from_spec(PTY_HEALTH_PROBE_SPEC)
sys.modules[PTY_HEALTH_PROBE_SPEC.name] = pty_health_probe
PTY_HEALTH_PROBE_SPEC.loader.exec_module(pty_health_probe)

BINARY40_WRAPPER_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_binary40_repro_v1"
    / "reproduce_binary40_submission.py"
)
BINARY40_WRAPPER_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_binary40_repro_v1", BINARY40_WRAPPER_MODULE_PATH
)
assert BINARY40_WRAPPER_SPEC is not None and BINARY40_WRAPPER_SPEC.loader is not None
binary40_wrapper = importlib.util.module_from_spec(BINARY40_WRAPPER_SPEC)
sys.modules[BINARY40_WRAPPER_SPEC.name] = binary40_wrapper
BINARY40_WRAPPER_SPEC.loader.exec_module(binary40_wrapper)

O30BEST_WRAPPER_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_o30best_repro_v1"
    / "reproduce_o30best_submission.py"
)
O30BEST_WRAPPER_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_o30best_repro_v1", O30BEST_WRAPPER_MODULE_PATH
)
assert O30BEST_WRAPPER_SPEC is not None and O30BEST_WRAPPER_SPEC.loader is not None
o30best_wrapper = importlib.util.module_from_spec(O30BEST_WRAPPER_SPEC)
sys.modules[O30BEST_WRAPPER_SPEC.name] = o30best_wrapper
O30BEST_WRAPPER_SPEC.loader.exec_module(o30best_wrapper)

O30BEST_PROXYBENCH_WRAPPER_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_o30best_proxybench_repro_v1"
    / "reproduce_o30best_proxybench_submission.py"
)
O30BEST_PROXYBENCH_WRAPPER_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_o30best_proxybench_repro_v1", O30BEST_PROXYBENCH_WRAPPER_MODULE_PATH
)
assert O30BEST_PROXYBENCH_WRAPPER_SPEC is not None and O30BEST_PROXYBENCH_WRAPPER_SPEC.loader is not None
o30best_proxybench_wrapper = importlib.util.module_from_spec(O30BEST_PROXYBENCH_WRAPPER_SPEC)
sys.modules[O30BEST_PROXYBENCH_WRAPPER_SPEC.name] = o30best_proxybench_wrapper
O30BEST_PROXYBENCH_WRAPPER_SPEC.loader.exec_module(o30best_proxybench_wrapper)

THRESHOLD_WRAPPER_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_threshold_submission_v1"
    / "reproduce_threshold_submission.py"
)
THRESHOLD_WRAPPER_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_threshold_submission_v1", THRESHOLD_WRAPPER_MODULE_PATH
)
assert THRESHOLD_WRAPPER_SPEC is not None and THRESHOLD_WRAPPER_SPEC.loader is not None
threshold_wrapper = importlib.util.module_from_spec(THRESHOLD_WRAPPER_SPEC)
sys.modules[THRESHOLD_WRAPPER_SPEC.name] = threshold_wrapper
THRESHOLD_WRAPPER_SPEC.loader.exec_module(threshold_wrapper)

V3F_AUDIT_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "v3f_exportable_audit_v1"
    / "reproduce_v3f_exportable_audit.py"
)
V3F_AUDIT_SPEC = importlib.util.spec_from_file_location("v3f_exportable_audit_v1", V3F_AUDIT_MODULE_PATH)
assert V3F_AUDIT_SPEC is not None and V3F_AUDIT_SPEC.loader is not None
v3f_audit = importlib.util.module_from_spec(V3F_AUDIT_SPEC)
sys.modules[V3F_AUDIT_SPEC.name] = v3f_audit
V3F_AUDIT_SPEC.loader.exec_module(v3f_audit)

V3F_SUBMISSION_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "v3f_submission_line_v1"
    / "reproduce_v3f_submission_line.py"
)
V3F_SUBMISSION_SPEC = importlib.util.spec_from_file_location("v3f_submission_line_v1", V3F_SUBMISSION_MODULE_PATH)
assert V3F_SUBMISSION_SPEC is not None and V3F_SUBMISSION_SPEC.loader is not None
v3f_submission = importlib.util.module_from_spec(V3F_SUBMISSION_SPEC)
sys.modules[V3F_SUBMISSION_SPEC.name] = v3f_submission
V3F_SUBMISSION_SPEC.loader.exec_module(v3f_submission)

BINARY40_REPRO_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_binary40_repro_v1"
    / "reproduce_binary40_submission.py"
)
BINARY40_REPRO_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_binary40_repro_v1", BINARY40_REPRO_MODULE_PATH
)
assert BINARY40_REPRO_SPEC is not None and BINARY40_REPRO_SPEC.loader is not None
binary40_repro = importlib.util.module_from_spec(BINARY40_REPRO_SPEC)
sys.modules[BINARY40_REPRO_SPEC.name] = binary40_repro
BINARY40_REPRO_SPEC.loader.exec_module(binary40_repro)

O30BEST_REPRO_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_o30best_repro_v1"
    / "reproduce_o30best_submission.py"
)
O30BEST_REPRO_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_o30best_repro_v1", O30BEST_REPRO_MODULE_PATH
)
assert O30BEST_REPRO_SPEC is not None and O30BEST_REPRO_SPEC.loader is not None
o30best_repro = importlib.util.module_from_spec(O30BEST_REPRO_SPEC)
sys.modules[O30BEST_REPRO_SPEC.name] = o30best_repro
O30BEST_REPRO_SPEC.loader.exec_module(o30best_repro)

O30BEST_PROXYBENCH_REPRO_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_o30best_proxybench_repro_v1"
    / "reproduce_o30best_proxybench_submission.py"
)
O30BEST_PROXYBENCH_REPRO_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_o30best_proxybench_repro_v1", O30BEST_PROXYBENCH_REPRO_MODULE_PATH
)
assert O30BEST_PROXYBENCH_REPRO_SPEC is not None and O30BEST_PROXYBENCH_REPRO_SPEC.loader is not None
o30best_proxybench_repro = importlib.util.module_from_spec(O30BEST_PROXYBENCH_REPRO_SPEC)
sys.modules[O30BEST_PROXYBENCH_REPRO_SPEC.name] = o30best_proxybench_repro
O30BEST_PROXYBENCH_REPRO_SPEC.loader.exec_module(o30best_proxybench_repro)

THRESHOLD_SUBMISSION_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "versions"
    / "baseline_mlx_threshold_submission_v1"
    / "reproduce_threshold_submission.py"
)
THRESHOLD_SUBMISSION_SPEC = importlib.util.spec_from_file_location(
    "baseline_mlx_threshold_submission_v1", THRESHOLD_SUBMISSION_MODULE_PATH
)
assert THRESHOLD_SUBMISSION_SPEC is not None and THRESHOLD_SUBMISSION_SPEC.loader is not None
threshold_submission = importlib.util.module_from_spec(THRESHOLD_SUBMISSION_SPEC)
sys.modules[THRESHOLD_SUBMISSION_SPEC.name] = threshold_submission
THRESHOLD_SUBMISSION_SPEC.loader.exec_module(threshold_submission)

THRESHOLD_FRONTIER_RUN_ROOT = (
    Path(__file__).resolve().parents[2]
    / "baseline_mlx"
    / "outputs"
    / "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1"
)


def assert_summary_contract_state_payload(payload: dict[str, object]) -> None:
    state = payload["readme_contract_state"]
    assert payload["summary_schema_version"] == 2
    assert payload["readme_contract_verified_from_readme_file"] is True
    assert payload["validated_prepare_manifest_readme_contract"] == payload["readme_contract"]
    assert state["matches_current_readme"] is True
    assert state["missing_keys"] == []
    assert state["unexpected_keys"] == []
    assert state["mismatched_keys"] == []
    assert state["actual_key_count"] == state["expected_key_count"]


def assert_module_rejects_malformed_readme(module: ModuleType, loader: callable, tmp_path: Path) -> None:
    malformed_readme = tmp_path / f"{module.__name__}_README.md"
    malformed_readme.write_text(
        "\n".join(
            [
                "Overview",
                "Parameter\tValue",
                "max_lora_rank\t32",
                "max_tokens\t7680",
                "top_p\t1.0",
                "temperature\t0.0",
                "max_num_seqs\t64",
                "gpu_memory_utilization\t",
                "max_model_len\t8192",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    original_readme_path = module.README_PATH
    try:
        module.README_PATH = malformed_readme
        try:
            loader()
            raise AssertionError("Expected malformed README to raise SystemExit")
        except SystemExit as exc:
            assert "Malformed README.md evaluation row for gpu_memory_utilization: missing value" in str(exc)
    finally:
        module.README_PATH = original_readme_path


def assert_module_rejects_missing_readme_row(module: ModuleType, loader: callable, tmp_path: Path) -> None:
    malformed_readme = tmp_path / f"{module.__name__}_missing_row_README.md"
    malformed_readme.write_text(
        "\n".join(
            [
                "Overview",
                "Parameter\tValue",
                "max_lora_rank\t32",
                "max_tokens\t7680",
                "top_p\t1.0",
                "temperature\t0.0",
                "max_num_seqs\t64",
                "max_model_len\t8192",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    original_readme_path = module.README_PATH
    try:
        module.README_PATH = malformed_readme
        try:
            loader()
            raise AssertionError("Expected missing README row to raise SystemExit")
        except SystemExit as exc:
            assert "Missing README.md evaluation rows: gpu_memory_utilization" in str(exc)
    finally:
        module.README_PATH = original_readme_path


def write_submission_contract_readme(
    tmp_path: Path,
    *,
    max_lora_rank: str = "32",
    include_adapter_config_clause: bool = True,
    include_submission_zip_clause: bool = True,
    include_single_adapter_clause: bool = True,
) -> Path:
    evaluation_line = (
        "Submissions are evaluated based on their Accuracy in solving the provided tasks. "
        "The NVIDIA Nemotron-3-Nano-30B model is loaded with your LoRA adapter"
    )
    if include_adapter_config_clause:
        evaluation_line += " (which must include an adapter_config.json)"
    evaluation_line += " using the vLLM inference engine."
    if include_single_adapter_clause:
        submitting_line = (
            "You must submit a LoRA adapter of rank at most "
            f"{max_lora_rank} for the NVIDIA Nemotron-3-Nano-30B model"
        )
    else:
        submitting_line = (
            "You must submit LoRA adapters of rank at most "
            f"{max_lora_rank} for the NVIDIA Nemotron-3-Nano-30B model"
        )
    if include_submission_zip_clause:
        submitting_line += " packaged into a submission.zip file."
    else:
        submitting_line += " packaged into an archive file."
    readme_path = tmp_path / "submission_contract_README.md"
    readme_path.write_text(
        "\n".join(
            [
                "Evaluation",
                evaluation_line,
                "Parameter\tValue",
                f"max_lora_rank\t{max_lora_rank}",
                "max_tokens\t7680",
                "top_p\t1.0",
                "temperature\t0.0",
                "max_num_seqs\t64",
                "gpu_memory_utilization\t0.85",
                "max_model_len\t8192",
                "Submitting",
                submitting_line,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return readme_path


def make_source_run(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_run = tmp_path / "source_run"
    shadow_model_dir = source_run / "shadow_model"
    adapter_dir = source_run / "adapter"
    shadow_model_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)
    adapter_file = adapter_dir / "adapters.safetensors"
    adapter_file.write_bytes(b"adapter")
    (source_run / "training_result.json").write_text("{}", encoding="utf-8")
    (source_run / "prepare_manifest.json").write_text(
        json.dumps(
            {
                "shadow_model_dir": str(shadow_model_dir.resolve()),
                "artifacts": {"adapter_dir": str(adapter_dir.resolve())},
            }
        ),
        encoding="utf-8",
    )
    return source_run, shadow_model_dir.resolve(), adapter_file.resolve()


def init_git_repo_with_results_md(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True, capture_output=True, text=True)
    results_md = repo_root / "versions" / "baseline_mlx" / "baseline_mlx-results.md"
    results_md.parent.mkdir(parents=True, exist_ok=True)
    results_md.write_text("initial\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "versions/baseline_mlx/baseline_mlx-results.md"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial ledger"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return repo_root, results_md


def init_git_repo_with_remote_results_md(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    remote_root = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote_root)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote_root)], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True)
    return repo_root, results_md, remote_root


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_wait_train_args(source_run: Path, output_root: Path, run_name: str, **overrides) -> SimpleNamespace:
    payload = {
        "source_run_root": source_run,
        "output_root": output_root,
        "run_name": run_name,
        "poll_seconds": 0.1,
        "timeout_seconds": 1.0,
        "wait_status_json": None,
        "min_free_percent": None,
        "min_free_gb": None,
        "skip_if_target_started": True,
        "dry_run": True,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def test_build_corrective_stage2_dataframe_includes_manual_audit_rows() -> None:
    binary_delta_df = stage_waiters.pd.DataFrame(
        [
            {
                "id": "bin_v1",
                "prompt": "p1",
                "answer": "1",
                "type": "Bit Manipulation",
                "generated_cot": "cot1",
                "source_selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_affine_xor",
                "template_subtype": "bit_other",
                "assistant_style": "boxed_only_done",
            },
            {
                "id": "bin_v2",
                "prompt": "p2",
                "answer": "2",
                "type": "Bit Manipulation",
                "generated_cot": "cot2",
                "source_selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_structured_byte_formula",
                "template_subtype": "bit_structured_byte_formula",
                "assistant_style": "boxed_only_done",
            },
            {
                "id": "bin_m1",
                "prompt": "p3",
                "answer": "3",
                "type": "Bit Manipulation",
                "generated_cot": "cot3",
                "source_selection_tier": "manual_audit_priority",
                "teacher_solver_candidate": "binary_affine_xor",
                "template_subtype": "bit_other",
                "assistant_style": "boxed_only_done",
            },
            {
                "id": "bin_m2",
                "prompt": "p3b",
                "answer": "33",
                "type": "Bit Manipulation",
                "generated_cot": "cot3b",
                "source_selection_tier": "manual_audit_priority",
                "teacher_solver_candidate": "binary_structured_byte_formula",
                "template_subtype": "bit_structured_byte_formula",
                "assistant_style": "boxed_only_done",
            },
            {
                "id": "bin_a1",
                "prompt": "p4",
                "answer": "4",
                "type": "Bit Manipulation",
                "generated_cot": "cot4",
                "source_selection_tier": "answer_only_keep",
                "teacher_solver_candidate": "binary_affine_xor",
                "template_subtype": "bit_other",
                "assistant_style": "boxed_only",
            },
        ]
    )
    symbol_source_df = stage_waiters.pd.DataFrame(
        [
            {
                "id": "sym1",
                "prompt": "sp1",
                "answer": "5",
                "type": "Equation Transformation",
                "generated_cot": "scot1",
            }
        ]
    )
    symbol_watch_df = stage_waiters.pd.DataFrame(
        [{"id": "sym1", "template_subtype": "numeric_2x2", "selection_tier": "verified_trace_ready"}]
    )
    proxy_v1_df = stage_waiters.pd.DataFrame(
        [
            {
                "id": "sym1",
                "family_short": "symbol",
                "template_subtype": "numeric_2x2",
                "selection_tier": "verified_trace_ready",
            }
        ]
    )

    combined, summary = stage_waiters.build_corrective_stage2_dataframe(
        binary_delta_df=binary_delta_df,
        symbol_source_df=symbol_source_df,
        symbol_watch_df=symbol_watch_df,
        proxy_v1_df=proxy_v1_df,
        binary_solvers=["binary_affine_xor", "binary_structured_byte_formula"],
        max_symbol_rows=1,
        max_answer_only_ratio=0.0,
        max_manual_audit_ratio=0.5,
        seed=7,
    )

    assert set(combined["id"].astype(str)) == {"bin_v1", "bin_v2", "bin_m1", "sym1"}
    assert summary["binary_verified_rows"] == 2
    assert summary["binary_manual_audit_rows"] == 1
    assert summary["binary_answer_only_rows"] == 0
    assert summary["symbol_rows"] == 1
    assert summary["max_manual_audit_ratio"] == 0.5
    assert summary["manual_audit_template_subtypes"] == ["bit_other"]
    assert summary["binary_solver_counts"] == {
        "binary_affine_xor": 2,
        "binary_structured_byte_formula": 1,
    }
    assert summary["binary_verified_solver_counts"] == {
        "binary_affine_xor": 1,
        "binary_structured_byte_formula": 1,
    }
    assert summary["binary_helper_solver_counts"] == {"binary_affine_xor": 1}
    assert summary["binary_selection_tier_counts"] == {
        "manual_audit_priority": 1,
        "verified_trace_ready": 2,
    }


def test_build_corrective_stage2_dataframe_respects_solver_filter_for_helper_rows() -> None:
    binary_delta_df = stage_waiters.pd.DataFrame(
        [
            {
                "id": "bin_v_affine",
                "prompt": "pv1",
                "answer": "1",
                "type": "Bit Manipulation",
                "generated_cot": "cotv1",
                "source_selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_affine_xor",
                "template_subtype": "bit_other",
                "assistant_style": "boxed_only_done",
            },
            {
                "id": "bin_a_affine",
                "prompt": "pa1",
                "answer": "2",
                "type": "Bit Manipulation",
                "generated_cot": "cota1",
                "source_selection_tier": "answer_only_keep",
                "teacher_solver_candidate": "binary_affine_xor",
                "template_subtype": "bit_other",
                "assistant_style": "boxed_only",
            },
            {
                "id": "bin_a_structured",
                "prompt": "pa2",
                "answer": "3",
                "type": "Bit Manipulation",
                "generated_cot": "cota2",
                "source_selection_tier": "answer_only_keep",
                "teacher_solver_candidate": "binary_structured_byte_formula",
                "template_subtype": "bit_structured_byte_formula",
                "assistant_style": "boxed_only",
            },
            {
                "id": "bin_m_affine",
                "prompt": "pm1",
                "answer": "4",
                "type": "Bit Manipulation",
                "generated_cot": "cotm1",
                "source_selection_tier": "manual_audit_priority",
                "teacher_solver_candidate": "binary_affine_xor",
                "template_subtype": "bit_other",
                "assistant_style": "boxed_only_done",
            },
            {
                "id": "bin_m_structured",
                "prompt": "pm2",
                "answer": "5",
                "type": "Bit Manipulation",
                "generated_cot": "cotm2",
                "source_selection_tier": "manual_audit_priority",
                "teacher_solver_candidate": "binary_structured_byte_formula",
                "template_subtype": "bit_other",
                "assistant_style": "boxed_only_done",
            },
        ]
    )

    combined, summary = stage_waiters.build_corrective_stage2_dataframe(
        binary_delta_df=binary_delta_df,
        symbol_source_df=stage_waiters.pd.DataFrame(columns=["id", "prompt", "answer", "type", "generated_cot"]),
        symbol_watch_df=stage_waiters.pd.DataFrame(columns=["id", "template_subtype", "selection_tier"]),
        proxy_v1_df=stage_waiters.pd.DataFrame(columns=["id", "family_short", "template_subtype", "selection_tier"]),
        binary_solvers=["binary_affine_xor"],
        max_symbol_rows=0,
        max_answer_only_ratio=0.5,
        max_manual_audit_ratio=0.5,
        seed=11,
    )

    assert set(combined["id"].astype(str)) == {"bin_v_affine", "bin_a_affine", "bin_m_affine"}
    assert summary["binary_verified_rows"] == 1
    assert summary["binary_answer_only_rows"] == 1
    assert summary["binary_manual_audit_rows"] == 1
    assert summary["symbol_rows"] == 0


def build_wait_resume_from_path_args(
    source_run: Path,
    output_root: Path,
    run_name: str,
    wait_path: Path,
    **overrides,
) -> SimpleNamespace:
    payload = {
        "source_run_root": source_run,
        "output_root": output_root,
        "run_name": run_name,
        "wait_path": wait_path,
        "expected_kind": "file",
        "poll_seconds": 0.1,
        "timeout_seconds": 1.0,
        "wait_status_json": None,
        "min_free_percent": None,
        "min_free_gb": None,
        "skip_if_target_started": True,
        "dry_run": True,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def build_wait_free_memory_args(**overrides) -> SimpleNamespace:
    payload = {
        "min_free_percent": None,
        "min_free_gb": 150.0,
        "poll_seconds": 0.1,
        "timeout_seconds": 1.0,
        "status_json": None,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def build_postprocess_args(run_root: Path, summary_json: Path, **overrides) -> SimpleNamespace:
    payload = {
        "run_root": run_root,
        "label": None,
        "wait_for_training_result": False,
        "poll_seconds": 0.1,
        "timeout_seconds": 1.0,
        "summary_json": summary_json,
        "dry_run": True,
        "skip_existing_steps": True,
        "run_eval_suite": True,
        "benchmark_root": stage_waiters.PHASE0_OFFLINE_EVAL_ARTIFACT_ROOT,
        "extra_benchmark_csv": None,
        "suite_output_root": None,
        "max_tokens": stage_waiters.README_MAX_TOKENS,
        "temperature": stage_waiters.README_TEMPERATURE,
        "top_p": stage_waiters.README_TOP_P,
        "max_num_seqs": stage_waiters.README_MAX_NUM_SEQS,
        "gpu_memory_utilization": stage_waiters.README_GPU_MEMORY_UTILIZATION,
        "max_model_len": stage_waiters.README_MAX_MODEL_LEN,
        "prompt_chunk_size": 16,
        "prefill_batch_size": 16,
        "completion_batch_size": 16,
        "eval_enable_thinking": True,
        "lazy_load": True,
        "force_single_generate": False,
        "run_audit_submission": True,
        "audit_output_root": None,
        "run_export_submission": True,
        "export_output_root": None,
        "export_only_if_ready": True,
        "reference_model_root": None,
        "run_record_run_result": True,
        "results_md": stage_waiters.DEFAULT_RESULTS_MD,
        "run_package_best_submission": False,
        "run_publish_results_md": False,
        "publish_commit_message": None,
        "publish_push": True,
        "publish_dry_run": False,
        "repo_root": stage_waiters.REPO_ROOT,
        "publish_lock_dir": stage_waiters.DEFAULT_RESULTS_GIT_LOCK_DIR,
        "publish_lock_poll_seconds": 0.1,
        "publish_lock_timeout_seconds": 1.0,
        "search_root": stage_waiters.DEFAULT_OUTPUT_ROOT,
        "candidate_run_root": None,
        "best_submission_output_root": stage_waiters.DEFAULT_OUTPUT_ROOT / "best_submission_candidate_auto",
        "min_local320_accuracy": stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_LOCAL320_ACCURACY,
        "min_general_stable_accuracy": stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_GENERAL_STABLE_ACCURACY,
        "min_proxy_v2_accuracy": 0.0,
        "min_specialized_accuracy": 0.0,
        "require_exportable": True,
        "export_if_missing": True,
        "update_results_md": True,
        "base_model_name_or_path": stage_waiters.BASE_MODEL_NAME,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def write_benchmark_eval_summary(
    output_root: Path,
    *,
    rows: int,
    correct: int,
    by_benchmark: list[dict[str, object]] | None = None,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    output_root.joinpath("benchmark_eval_summary.json").write_text(
        json.dumps(
            {
                "overall": {
                    "rows": rows,
                    "correct": correct,
                    "accuracy": correct / rows if rows else 0.0,
                },
                "by_benchmark": by_benchmark or [],
            }
        ),
        encoding="utf-8",
    )


def make_candidate_run(
    tmp_path: Path,
    *,
    run_name: str,
    local320_correct: int,
    local320_rows: int = 320,
    general_stable_correct: int = 96,
    general_stable_rows: int = 100,
    proxy_v1_correct: int = 120,
    proxy_v1_rows: int = 200,
    proxy_correct: int = 70,
    proxy_rows: int = 84,
    specialized_correct: int = 300,
    specialized_rows: int = 563,
    export_ready: bool = True,
) -> Path:
    run_root = tmp_path / run_name
    adapter_dir = run_root / "adapter"
    submission_dir = run_root / "submission_export" / "submission_adapter"
    adapter_dir.mkdir(parents=True)
    submission_dir.mkdir(parents=True)
    (adapter_dir / "adapters.safetensors").write_bytes(b"adapter")
    (submission_dir / "adapter_config.json").write_text("{}", encoding="utf-8")
    (submission_dir / "adapter_model.safetensors").write_bytes(b"adapter")
    zip_path = run_root / "submission_export" / "submission.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("adapter_config.json", "{}")
        archive.writestr("adapter_model.safetensors", "adapter")

    local320_root = run_root / "eval_suite_readme_proxy_specialized" / "readme_local320"
    proxy_v1_root = run_root / "eval_suite_readme_proxy_specialized" / "leaderboard_proxy_v1_set"
    proxy_root = run_root / "eval_suite_readme_proxy_specialized" / "leaderboard_proxy_v2"
    specialized_root = run_root / "eval_suite_readme_proxy_specialized" / "binary_bias_specialized_set"
    write_benchmark_eval_summary(
        local320_root,
        rows=local320_rows,
        correct=local320_correct,
        by_benchmark=[
            {
                "benchmark_name": "general_stable_set",
                "rows": general_stable_rows,
                "correct": general_stable_correct,
                "accuracy": general_stable_correct / general_stable_rows,
            },
            {
                "benchmark_name": "binary_hard_set",
                "rows": 160,
                "correct": 80,
                "accuracy": 0.5,
            },
            {
                "benchmark_name": "symbol_watch_set",
                "rows": 60,
                "correct": 58,
                "accuracy": 58 / 60,
            },
        ],
    )
    write_benchmark_eval_summary(proxy_v1_root, rows=proxy_v1_rows, correct=proxy_v1_correct)
    write_benchmark_eval_summary(proxy_root, rows=proxy_rows, correct=proxy_correct)
    write_benchmark_eval_summary(specialized_root, rows=specialized_rows, correct=specialized_correct)

    (run_root / "eval_suite_readme_proxy_specialized" / "benchmark_eval_suite_summary.json").write_text(
        json.dumps(
            {
                "evaluations": [
                    {"evaluation_name": "readme_local320", "output_root": str(local320_root.resolve())},
                    {"evaluation_name": "leaderboard_proxy_v1_set", "output_root": str(proxy_v1_root.resolve())},
                    {"evaluation_name": "leaderboard_proxy_v2", "output_root": str(proxy_root.resolve())},
                    {
                        "evaluation_name": "binary_bias_specialized_set",
                        "output_root": str(specialized_root.resolve()),
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (run_root / "prepare_manifest.json").write_text(
        json.dumps(
            {
                "train_csv": "train.csv",
                "sampling": {"sampled_rows": 128},
                "training": {
                    "optimizer_steps": 16,
                    "learning_rate": 2e-5,
                    "max_seq_length": 1536,
                    "trainable_lora_suffixes": ["mixer.q_proj", "mixer.k_proj"],
                    "lora_keys": ["mixer.q_proj", "mixer.k_proj"],
                },
            }
        ),
        encoding="utf-8",
    )
    (run_root / "training_result.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
    (run_root / "submission_compat_audit" / "submission_compat_audit.json").parent.mkdir(parents=True, exist_ok=True)
    (run_root / "submission_compat_audit" / "submission_compat_audit.json").write_text(
        json.dumps(
            {
                "audit_status": "potentially_exportable_2d_only" if export_ready else "blocked",
                "peft_export_ready": export_ready,
            }
        ),
        encoding="utf-8",
    )
    (run_root / "submission_export" / "export_manifest.json").write_text(
        json.dumps(
            {
                "zip_path": str(zip_path.resolve()),
                "zip_size_bytes": zip_path.stat().st_size,
                "submission_dir": str(submission_dir.resolve()),
                "validation": {"valid": True},
            }
        ),
        encoding="utf-8",
    )
    return run_root


def make_live_progress_run(
    parent_root: Path,
    *,
    run_name: str,
    progress_source: str = "latest_train_report",
    runtime_pid: int | None = None,
) -> Path:
    run_root = parent_root / run_name
    adapter_dir = run_root / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    resolved_runtime_pid = os.getpid() if runtime_pid is None else runtime_pid
    (run_root / "runtime_preflight.json").write_text(
        json.dumps({"current_pid": resolved_runtime_pid}),
        encoding="utf-8",
    )
    (run_root / "prepare_manifest.json").write_text(
        json.dumps(
            {
                "created_at": "2026-04-09T02:00:00+00:00",
                "train_csv": "train.csv",
                "sampling": {"sampled_rows": 3321},
                "training": {
                    "optimizer_steps": 832,
                    "learning_rate": 1e-4,
                    "max_seq_length": 4096,
                    "trainable_lora_suffixes": ["mixer.in_proj", "mixer.out_proj"],
                },
            }
        ),
        encoding="utf-8",
    )
    latest_payload = {
        "event": "train",
        "logged_at": "2026-04-09T02:10:00+00:00",
        "iteration": 3200,
        "optimizer_step": 400,
        "train_loss": 0.436,
        "learning_rate": 6.105e-05,
        "iterations_per_second": 0.400,
        "tokens_per_second": 245.351,
        "trained_tokens": 1900181,
        "peak_memory": 82.620,
        "steps_per_report_step_unit": "optimizer",
    }
    if progress_source == "latest_train_report":
        (adapter_dir / "latest_train_report.json").write_text(json.dumps(latest_payload), encoding="utf-8")
    elif progress_source == "console_log":
        (run_root / "console.log").write_text(
            "Iter 3200 (Opt 400): Train loss 0.436, Learning Rate 6.105e-05, "
            "It/sec 0.400, Tokens/sec 245.351, Trained Tokens 1900181, Peak mem 82.620 GB\n",
            encoding="utf-8",
        )
    elif progress_source == "eval_suite_progress":
        (adapter_dir / "latest_train_report.json").write_text(json.dumps(latest_payload), encoding="utf-8")
        (run_root / "training_result.json").write_text(
            json.dumps(
                {
                    "created_at": "2026-04-09T02:12:00+00:00",
                    "latest_train_report": latest_payload,
                }
            ),
            encoding="utf-8",
        )
        suite_root = run_root / stage_waiters.DEFAULT_RUN_SUITE_PROGRESS_RELPATH.parent
        eval_root = suite_root / "readme_local320"
        eval_root.mkdir(parents=True, exist_ok=True)
        (suite_root / "benchmark_eval_suite_progress.json").write_text(
            json.dumps(
                {
                    "recorded_at": "2026-04-09T02:30:00+00:00",
                    "status": "running",
                    "output_root": str(suite_root),
                    "evaluations_total": 2,
                    "evaluations_completed": 0,
                    "current_evaluation": "readme_local320",
                    "current_rows_total": 320,
                    "current_rows_completed": 288,
                    "current_chunks_total": 20,
                    "current_chunks_completed": 18,
                    "completed_evaluations": [],
                }
            ),
            encoding="utf-8",
        )
        (eval_root / "benchmark_eval_progress.json").write_text(
            json.dumps(
                {
                    "recorded_at": "2026-04-09T02:30:00+00:00",
                    "status": "running",
                    "evaluation_name": "readme_local320",
                    "output_root": str(eval_root),
                    "rows_total": 320,
                    "rows_completed": 288,
                    "chunks_total": 20,
                    "chunks_completed": 18,
                    "correct": 204,
                    "accuracy": 0.6375,
                }
            ),
            encoding="utf-8",
        )
    else:
        raise ValueError(f"Unsupported progress source: {progress_source}")
    return run_root


def make_switch_mlp_export_source_tensors() -> dict[str, np.ndarray]:
    return {
        "backbone.layers.0.mixer.in_proj.lora_a": np.arange(6, dtype=np.float32).reshape(2, 3),
        "backbone.layers.0.mixer.in_proj.lora_b": np.arange(8, dtype=np.float32).reshape(2, 4),
        "backbone.layers.0.mixer.switch_mlp.fc1.lora_a": np.arange(12, dtype=np.float32).reshape(2, 2, 3),
        "backbone.layers.0.mixer.switch_mlp.fc2.lora_b": np.arange(16, dtype=np.float32).reshape(2, 4, 2),
    }


def make_switch_mlp_export_adapter_config() -> dict[str, object]:
    return {
        "fine_tune_type": "lora",
        "lora_parameters": {
            "rank": 2,
            "scale": 4.0,
            "dropout": 0.0,
            "keys": [
                "mixer.in_proj",
                "mixer.switch_mlp.fc1",
                "mixer.switch_mlp.fc2",
            ],
        },
    }


def make_switch_mlp_reference_shapes() -> dict[str, tuple[int, ...]]:
    return {
        "base_model.model.backbone.layers.0.mixer.in_proj.lora_A.weight": (3, 2),
        "base_model.model.backbone.layers.0.mixer.in_proj.lora_B.weight": (4, 2),
        "base_model.model.backbone.layers.0.mixer.experts.0.up_proj.lora_A.weight": (2, 3),
        "base_model.model.backbone.layers.0.mixer.experts.1.up_proj.lora_A.weight": (2, 3),
        "base_model.model.backbone.layers.0.mixer.experts.0.down_proj.lora_B.weight": (4, 2),
        "base_model.model.backbone.layers.0.mixer.experts.1.down_proj.lora_B.weight": (4, 2),
    }


def test_resolve_source_run_resume_paths_uses_prepare_manifest(tmp_path: Path) -> None:
    source_run, expected_shadow_model_dir, expected_adapter_file = make_source_run(tmp_path)

    shadow_model_dir, adapter_file = stage_waiters.resolve_source_run_resume_paths(source_run)

    assert shadow_model_dir == expected_shadow_model_dir
    assert adapter_file == expected_adapter_file


def test_wait_train_from_run_dry_run_writes_wait_and_resume_manifests(tmp_path: Path) -> None:
    source_run, expected_shadow_model_dir, expected_adapter_file = make_source_run(tmp_path)
    output_root = tmp_path / "output"

    stage_waiters.run_wait_train_from_run(
        build_wait_train_args(source_run=source_run, output_root=output_root, run_name="stage2_attention")
    )

    run_root = output_root / "stage2_attention"
    wait_manifest = json.loads((run_root / "wait_for_source_training_result.json").read_text(encoding="utf-8"))
    resume_manifest = json.loads((run_root / "resume_from_run_manifest.json").read_text(encoding="utf-8"))
    assert wait_manifest["exists"] is True
    assert wait_manifest["is_file"] is True
    assert resume_manifest["dry_run"] is True
    assert resume_manifest["target_existing_marker"] == ""
    assert resume_manifest["resolved_model_root"] == str(expected_shadow_model_dir)
    assert resume_manifest["resolved_resume_adapter_file"] == str(expected_adapter_file)


def test_wait_train_from_run_skips_if_target_already_started(tmp_path: Path) -> None:
    source_run, _, _ = make_source_run(tmp_path)
    output_root = tmp_path / "output"
    run_root = output_root / "stage2_attention"
    run_root.mkdir(parents=True)
    existing_marker = run_root / "resume_from_run_manifest.json"
    existing_marker.write_text("{}", encoding="utf-8")

    stage_waiters.run_wait_train_from_run(
        build_wait_train_args(source_run=source_run, output_root=output_root, run_name="stage2_attention")
    )

    wait_manifest = json.loads((run_root / "wait_for_source_training_result.json").read_text(encoding="utf-8"))
    assert wait_manifest["status"] == "skipped_existing_target"
    assert wait_manifest["target_existing_marker"] == str(existing_marker.resolve())


def test_resume_train_from_run_real_launch_ignores_prior_dry_run_marker(tmp_path: Path) -> None:
    source_run, expected_shadow_model_dir, expected_adapter_file = make_source_run(tmp_path)
    output_root = tmp_path / "output"
    run_name = "stage2_attention_after_dry_run"
    run_root = output_root / run_name

    dry_run_args = SimpleNamespace(
        source_run_root=source_run,
        output_root=output_root,
        run_name=run_name,
        skip_if_target_started=True,
        dry_run=True,
    )
    stage_waiters.run_resume_train_from_run(dry_run_args)

    calls: dict[str, str] = {}
    original_run_train = stage_waiters.run_train
    try:
        def fake_run_train(args: SimpleNamespace) -> None:
            calls["model_root"] = str(args.model_root)
            calls["resume_adapter_file"] = str(args.resume_adapter_file)

        stage_waiters.run_train = fake_run_train
        real_args = SimpleNamespace(
            source_run_root=source_run,
            output_root=output_root,
            run_name=run_name,
            skip_if_target_started=True,
            dry_run=False,
        )
        stage_waiters.run_resume_train_from_run(real_args)
    finally:
        stage_waiters.run_train = original_run_train

    resume_manifest = json.loads((run_root / "resume_from_run_manifest.json").read_text(encoding="utf-8"))
    assert calls["model_root"] == str(expected_shadow_model_dir)
    assert calls["resume_adapter_file"] == str(expected_adapter_file)
    assert resume_manifest["dry_run"] is False
    assert resume_manifest["target_existing_marker"] == ""


def test_wait_resume_train_from_path_dry_run_writes_wait_and_resume_manifests(tmp_path: Path) -> None:
    source_run, _, expected_adapter_file = make_source_run(tmp_path)
    output_root = tmp_path / "output"
    trigger_path = tmp_path / "trigger.json"
    trigger_path.write_text("{}", encoding="utf-8")

    stage_waiters.run_wait_resume_train_from_path(
        build_wait_resume_from_path_args(
            source_run=source_run,
            output_root=output_root,
            run_name="stage2_attention_vo",
            wait_path=trigger_path,
        )
    )

    run_root = output_root / "stage2_attention_vo"
    wait_manifest = json.loads((run_root / "wait_for_trigger_path.json").read_text(encoding="utf-8"))
    resume_manifest = json.loads((run_root / "resume_from_run_manifest.json").read_text(encoding="utf-8"))
    assert wait_manifest["path"] == str(trigger_path.resolve())
    assert wait_manifest["source_run_root"] == str(source_run.resolve())
    assert resume_manifest["resolved_resume_adapter_file"] == str(expected_adapter_file)
    assert resume_manifest["target_existing_marker"] == ""


def test_wait_resume_train_from_path_skips_if_target_already_started(tmp_path: Path) -> None:
    source_run, _, _ = make_source_run(tmp_path)
    output_root = tmp_path / "output"
    trigger_path = tmp_path / "trigger.json"
    trigger_path.write_text("{}", encoding="utf-8")
    run_root = output_root / "stage2_attention_vo"
    run_root.mkdir(parents=True)
    existing_marker = run_root / "resume_from_run_manifest.json"
    existing_marker.write_text("{}", encoding="utf-8")

    stage_waiters.run_wait_resume_train_from_path(
        build_wait_resume_from_path_args(
            source_run=source_run,
            output_root=output_root,
            run_name="stage2_attention_vo",
            wait_path=trigger_path,
        )
    )

    wait_manifest = json.loads((run_root / "wait_for_trigger_path.json").read_text(encoding="utf-8"))
    assert wait_manifest["status"] == "skipped_existing_target"
    assert wait_manifest["target_existing_marker"] == str(existing_marker.resolve())


def test_wait_for_free_memory_writes_status_json(tmp_path: Path) -> None:
    status_json = tmp_path / "wait_for_free_memory.json"
    snapshots = iter(
        [
            {
                "system_free_percent": 20,
                "free_system_memory_gb": 180.0,
                "physmem_unused_gb": 100.0,
                "memory_gate_free_gb": 100.0,
            },
            {
                "system_free_percent": 33,
                "free_system_memory_gb": 170.0,
                "physmem_unused_gb": 160.0,
                "memory_gate_free_gb": 160.0,
            },
        ]
    )
    original_collect = stage_waiters.collect_memory_pressure_snapshot
    original_sleep = stage_waiters.time.sleep
    try:
        stage_waiters.collect_memory_pressure_snapshot = lambda: next(snapshots)
        stage_waiters.time.sleep = lambda _: None
        stage_waiters.run_wait_for_free_memory(
            build_wait_free_memory_args(
                status_json=status_json,
                min_free_percent=30.0,
                min_free_gb=150.0,
            )
        )
    finally:
        stage_waiters.collect_memory_pressure_snapshot = original_collect
        stage_waiters.time.sleep = original_sleep

    result = json.loads(status_json.read_text(encoding="utf-8"))
    assert result["status"] == "ready"
    assert result["min_free_percent"] == 30.0
    assert result["min_free_gb"] == 150.0
    assert result["memory_pressure"]["system_free_percent"] == 33
    assert result["memory_pressure"]["free_system_memory_gb"] == 170.0
    assert result["memory_pressure"]["physmem_unused_gb"] == 160.0
    assert result["memory_pressure"]["memory_gate_free_gb"] == 160.0


def test_collect_memory_pressure_snapshot_uses_conservative_top_unused() -> None:
    original_run_text_command = stage_waiters._run_text_command

    def fake_run_text_command(command: tuple[str, ...] | list[str]) -> tuple[int, str]:
        normalized = tuple(command)
        if normalized == ("memory_pressure",):
            return (
                0,
                "System-wide memory free percentage: 74%\n",
            )
        if normalized == ("sysctl", "-n", "hw.memsize"):
            return (0, "549755813888\n")
        if normalized == ("top", "-l", "1"):
            return (
                0,
                "\n".join(
                    [
                        "Processes: 1435 total, 2 running, 1433 sleeping, 6111 threads",
                        "PhysMem: 318G used (191G wired, 1103M compressor), 193G unused.",
                    ]
                ),
            )
        raise AssertionError(f"Unexpected command: {normalized}")

    try:
        stage_waiters._run_text_command = fake_run_text_command
        snapshot = stage_waiters.collect_memory_pressure_snapshot()
    finally:
        stage_waiters._run_text_command = original_run_text_command

    assert snapshot["system_free_percent"] == 74
    assert snapshot["free_system_memory_gb"] > 400.0
    assert snapshot["physmem_unused_gb"] == 193.0
    assert snapshot["memory_gate_free_gb"] == 193.0


def test_wait_resume_train_from_path_records_memory_wait_result(tmp_path: Path) -> None:
    source_run, _, expected_adapter_file = make_source_run(tmp_path)
    output_root = tmp_path / "output"
    trigger_path = tmp_path / "trigger.json"
    trigger_path.write_text("{}", encoding="utf-8")
    original_wait_for_free_memory = stage_waiters.wait_for_free_memory
    try:
        stage_waiters.wait_for_free_memory = lambda **kwargs: {
            "status": "ready",
            "min_free_percent": kwargs.get("min_free_percent"),
            "min_free_gb": kwargs.get("min_free_gb"),
            "memory_pressure": {
                "system_free_percent": 35,
                "free_system_memory_gb": 180.0,
            },
        }
        stage_waiters.run_wait_resume_train_from_path(
            build_wait_resume_from_path_args(
                source_run=source_run,
                output_root=output_root,
                run_name="stage2_attention_memory_gated",
                wait_path=trigger_path,
                min_free_gb=150.0,
            )
        )
    finally:
        stage_waiters.wait_for_free_memory = original_wait_for_free_memory

    run_root = output_root / "stage2_attention_memory_gated"
    wait_manifest = json.loads((run_root / "wait_for_trigger_path.json").read_text(encoding="utf-8"))
    resume_manifest = json.loads((run_root / "resume_from_run_manifest.json").read_text(encoding="utf-8"))
    assert wait_manifest["memory_wait_result"]["status"] == "ready"
    assert wait_manifest["memory_wait_result"]["min_free_gb"] == 150.0
    assert resume_manifest["resolved_resume_adapter_file"] == str(expected_adapter_file)


def test_postprocess_run_dry_run_writes_summary_without_loading_model(tmp_path: Path) -> None:
    run_root = tmp_path / "completed_run"
    shadow_model_dir = run_root / "shadow_model"
    adapter_dir = run_root / "adapter"
    shadow_model_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "adapters.safetensors").write_bytes(b"adapter")
    (run_root / "training_result.json").write_text("{}", encoding="utf-8")
    (run_root / "prepare_manifest.json").write_text(
        json.dumps(
            {
                "shadow_model_dir": str(shadow_model_dir.resolve()),
                "artifacts": {"adapter_dir": str(adapter_dir.resolve())},
            }
        ),
        encoding="utf-8",
    )
    summary_json = tmp_path / "postprocess_summary.json"

    stage_waiters.run_postprocess_run(build_postprocess_args(run_root=run_root, summary_json=summary_json))

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["dry_run"] is True
    assert summary["steps"]["dry_run"]["status"] == "completed"
    assert summary["model_root"] == str(shadow_model_dir.resolve())
    assert summary["adapter_dir"] == str(adapter_dir.resolve())
    assert summary["suite_summary_relpath"] == str(stage_waiters.DEFAULT_RUN_SUITE_SUMMARY_RELPATH)
    assert summary["audit_relpath"] == str(stage_waiters.DEFAULT_RUN_AUDIT_RELPATH)
    assert summary["export_relpath"] == str(stage_waiters.DEFAULT_RUN_EXPORT_RELPATH)


def test_postprocess_run_skips_existing_steps_without_reinvoking_pipeline(tmp_path: Path) -> None:
    run_root = make_candidate_run(
        tmp_path,
        run_name="completed_run",
        local320_correct=224,
        proxy_correct=72,
        specialized_correct=320,
    )
    shadow_model_dir = run_root / "shadow_model"
    shadow_model_dir.mkdir(parents=True, exist_ok=True)
    recorded_result = {"recorded_at": "2026-04-09T01:54:31Z"}
    (run_root / "recorded_run_result.json").write_text(json.dumps(recorded_result), encoding="utf-8")
    prepare_manifest = json.loads((run_root / "prepare_manifest.json").read_text(encoding="utf-8"))
    prepare_manifest["shadow_model_dir"] = str(shadow_model_dir.resolve())
    prepare_manifest["artifacts"] = {"adapter_dir": str((run_root / "adapter").resolve())}
    (run_root / "prepare_manifest.json").write_text(json.dumps(prepare_manifest), encoding="utf-8")
    summary_json = tmp_path / "postprocess_skip_summary.json"

    original_eval = stage_waiters.run_eval_benchmark_suite
    original_audit = stage_waiters.run_audit_submission_compat
    original_export = stage_waiters.run_export_peft_submission
    original_record = stage_waiters.run_record_run_result
    try:
        stage_waiters.run_eval_benchmark_suite = lambda _args: (_ for _ in ()).throw(AssertionError("eval reran"))
        stage_waiters.run_audit_submission_compat = (
            lambda _args: (_ for _ in ()).throw(AssertionError("audit reran"))
        )
        stage_waiters.run_export_peft_submission = (
            lambda _args: (_ for _ in ()).throw(AssertionError("export reran"))
        )
        stage_waiters.run_record_run_result = lambda _args: (_ for _ in ()).throw(AssertionError("record reran"))

        stage_waiters.run_postprocess_run(
            build_postprocess_args(
                run_root=run_root,
                summary_json=summary_json,
                dry_run=False,
                run_package_best_submission=False,
            )
        )
    finally:
        stage_waiters.run_eval_benchmark_suite = original_eval
        stage_waiters.run_audit_submission_compat = original_audit
        stage_waiters.run_export_peft_submission = original_export
        stage_waiters.run_record_run_result = original_record

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["dry_run"] is False
    assert summary["steps"]["eval_suite"]["status"] == "skipped_existing"
    assert summary["steps"]["audit_submission"]["status"] == "skipped_existing"
    assert summary["steps"]["export_submission"]["status"] == "skipped_existing"
    assert summary["steps"]["record_run_result"]["status"] == "skipped_existing"
    assert summary["steps"]["record_run_result"]["recorded_at"] == recorded_result["recorded_at"]


def test_record_run_result_accepts_legacy_prepare_manifest_without_trainable_suffixes(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    run_root = make_candidate_run(
        repo_root / "baseline_mlx" / "outputs",
        run_name="legacy_run",
        local320_correct=220,
        proxy_v1_correct=123,
    )

    prepare_manifest_path = run_root / "prepare_manifest.json"
    prepare_manifest = json.loads(prepare_manifest_path.read_text(encoding="utf-8"))
    training = prepare_manifest["training"]
    training.pop("trainable_lora_suffixes", None)
    training.pop("lora_keys", None)
    prepare_manifest_path.write_text(json.dumps(prepare_manifest), encoding="utf-8")

    stage_waiters.run_record_run_result(
        SimpleNamespace(
            run_root=run_root,
            results_md=results_md,
            label="legacy proxy record",
            suite_summary_relpath=Path("eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json"),
            audit_relpath=Path("submission_compat_audit/submission_compat_audit.json"),
            export_relpath=Path("submission_export/export_manifest.json"),
        )
    )

    recorded = json.loads((run_root / "recorded_run_result.json").read_text(encoding="utf-8"))
    assert recorded["run_name"] == "legacy_run"
    assert recorded["evaluation_payloads"]["leaderboard_proxy_v1_set"]["overall"]["correct"] == 123
    assert recorded["local320_components"]["general_stable_set"]["correct"] == 96
    ledger = results_md.read_text(encoding="utf-8")
    assert "trainable_lora_suffixes: `[]`" in ledger
    assert "leaderboard_proxy_v1_set: `123/200 = 0.6150`" in ledger


def test_postprocess_run_persists_eval_suite_running_state_before_invocation(tmp_path: Path) -> None:
    run_root = tmp_path / "completed_run"
    shadow_model_dir = run_root / "shadow_model"
    adapter_dir = run_root / "adapter"
    shadow_model_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)
    (adapter_dir / "adapters.safetensors").write_bytes(b"adapter")
    (run_root / "training_result.json").write_text("{}", encoding="utf-8")
    (run_root / "prepare_manifest.json").write_text(
        json.dumps(
            {
                "shadow_model_dir": str(shadow_model_dir.resolve()),
                "artifacts": {"adapter_dir": str(adapter_dir.resolve())},
            }
        ),
        encoding="utf-8",
    )
    summary_json = tmp_path / "postprocess_running_summary.json"

    original_eval = stage_waiters.run_eval_benchmark_suite
    try:
        def fake_eval(_args) -> None:
            summary = json.loads(summary_json.read_text(encoding="utf-8"))
            assert summary["steps"]["eval_suite"]["status"] == "running"
            assert summary["steps"]["eval_suite"]["progress_relpath"] == str(
                Path("eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json")
            )

        stage_waiters.run_eval_benchmark_suite = fake_eval
        stage_waiters.run_postprocess_run(
            build_postprocess_args(
                run_root=run_root,
                summary_json=summary_json,
                dry_run=False,
                skip_existing_steps=False,
                run_audit_submission=False,
                run_export_submission=False,
                run_record_run_result=False,
                run_package_best_submission=False,
            )
        )
    finally:
        stage_waiters.run_eval_benchmark_suite = original_eval

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["suite_progress_relpath"] == str(
        Path("eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json")
    )
    assert summary["steps"]["eval_suite"]["status"] == "completed"
    assert summary["steps"]["eval_suite"]["progress_relpath"] == str(
        Path("eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json")
    )


def test_evaluate_benchmark_rows_falls_back_to_evaluation_name_for_missing_benchmark_name() -> None:
    fake_mlx_lm = ModuleType("mlx_lm")
    fake_sample_utils = ModuleType("mlx_lm.sample_utils")
    original_mlx_lm = sys.modules.get("mlx_lm")
    original_sample_utils = sys.modules.get("mlx_lm.sample_utils")

    fake_mlx_lm.batch_generate = lambda *_args, **_kwargs: SimpleNamespace(texts=["reasoning... \\boxed{42}"])
    fake_mlx_lm.generate = lambda *_args, **_kwargs: "reasoning... \\boxed{42}"
    fake_sample_utils.make_sampler = lambda **_kwargs: object()
    progress_events: list[dict[str, object]] = []

    class FakeTokenizer:
        bos_token = None

        def apply_chat_template(
            self,
            messages,
            *,
            tokenize: bool = False,
            add_generation_prompt: bool = True,
            enable_thinking: bool = True,
        ):
            assert tokenize is False
            assert add_generation_prompt is True
            assert enable_thinking is True
            return messages[0]["content"]

        def encode(self, prompt: str, *, add_special_tokens: bool = True) -> list[int]:
            assert isinstance(prompt, str)
            assert isinstance(add_special_tokens, bool)
            return [1, 2, 3]

    sys.modules["mlx_lm"] = fake_mlx_lm
    sys.modules["mlx_lm.sample_utils"] = fake_sample_utils
    try:
        records, scored_rows, summary = stage_waiters.evaluate_benchmark_rows(
            model=object(),
            tokenizer=FakeTokenizer(),
            benchmark_rows=[{"id": "row-1", "prompt": "Solve 6*7", "answer": "42"}],
            evaluation_name="stage2_suite",
            source_paths=[Path("dummy.csv")],
            args=SimpleNamespace(
                eval_enable_thinking=True,
                temperature=0.0,
                top_p=1.0,
                max_num_seqs=64,
                gpu_memory_utilization=stage_waiters.README_GPU_MEMORY_UTILIZATION,
                prompt_chunk_size=16,
                prefill_batch_size=16,
                completion_batch_size=16,
                force_single_generate=False,
                max_tokens=32,
                max_model_len=stage_waiters.README_MAX_MODEL_LEN,
                model_root=Path("model"),
                adapter_dir=None,
            ),
            progress_callback=lambda payload: progress_events.append(dict(payload)),
        )
    finally:
        if original_mlx_lm is None:
            sys.modules.pop("mlx_lm", None)
        else:
            sys.modules["mlx_lm"] = original_mlx_lm
        if original_sample_utils is None:
            sys.modules.pop("mlx_lm.sample_utils", None)
        else:
            sys.modules["mlx_lm.sample_utils"] = original_sample_utils

    assert records[0]["benchmark_name"] == "stage2_suite"
    assert scored_rows[0]["is_correct"] is True
    assert summary["overall"]["accuracy"] == 1.0
    assert progress_events[0]["correct"] == 0
    assert progress_events[0]["accuracy"] == 0.0
    assert progress_events[1]["rows_completed"] == 1
    assert progress_events[1]["correct"] == 1
    assert progress_events[1]["accuracy"] == 1.0
    assert progress_events[2]["status"] == "scored"
    assert progress_events[2]["correct"] == 1


def test_build_readme_eval_assumptions_includes_gpu_memory_utilization() -> None:
    payload = stage_waiters.build_readme_eval_assumptions(
        SimpleNamespace(
            temperature=stage_waiters.README_TEMPERATURE,
            top_p=stage_waiters.README_TOP_P,
            max_tokens=stage_waiters.README_MAX_TOKENS,
            max_num_seqs=stage_waiters.README_MAX_NUM_SEQS,
            gpu_memory_utilization=stage_waiters.README_GPU_MEMORY_UTILIZATION,
            max_model_len=stage_waiters.README_MAX_MODEL_LEN,
            eval_enable_thinking=True,
        )
    )

    assert payload["gpu_memory_utilization"] == stage_waiters.README_GPU_MEMORY_UTILIZATION


def test_stage_waiters_load_readme_contract_from_readme_matches_constant() -> None:
    assert stage_waiters.load_readme_contract_from_readme() == stage_waiters.README_EVAL_CONTRACT


def test_stage_waiters_load_readme_contract_from_readme_rejects_missing_value(tmp_path: Path) -> None:
    assert_module_rejects_malformed_readme(stage_waiters, stage_waiters.load_readme_contract_from_readme, tmp_path)


def test_stage_waiters_load_readme_contract_from_readme_rejects_missing_row(tmp_path: Path) -> None:
    assert_module_rejects_missing_readme_row(stage_waiters, stage_waiters.load_readme_contract_from_readme, tmp_path)


def test_stage_waiters_verify_readme_contract_file_rejects_value_drift(tmp_path: Path) -> None:
    drifted_readme = tmp_path / "stage_waiters_drifted_README.md"
    drifted_readme.write_text(
        "\n".join(
            [
                "Overview",
                "Parameter\tValue",
                "max_lora_rank\t32",
                "max_tokens\t7000",
                "top_p\t1.0",
                "temperature\t0.0",
                "max_num_seqs\t64",
                "gpu_memory_utilization\t0.85",
                "max_model_len\t8192",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    original_readme_path = stage_waiters.README_PATH
    try:
        stage_waiters.README_PATH = drifted_readme
        try:
            stage_waiters.verify_readme_contract_file()
            raise AssertionError("Expected drifted README to raise SystemExit")
        except SystemExit as exc:
            assert "README.md evaluation table mismatch for max_tokens" in str(exc)
    finally:
        stage_waiters.README_PATH = original_readme_path


def test_stage_waiters_load_readme_submission_contract_from_readme_matches_expected(tmp_path: Path) -> None:
    original_readme_path = stage_waiters.README_PATH
    try:
        stage_waiters.README_PATH = write_submission_contract_readme(tmp_path)
        assert stage_waiters.load_readme_submission_contract_from_readme() == stage_waiters.README_SUBMISSION_CONTRACT
    finally:
        stage_waiters.README_PATH = original_readme_path


def test_stage_waiters_load_readme_submission_contract_from_readme_rejects_missing_adapter_config_clause(
    tmp_path: Path,
) -> None:
    original_readme_path = stage_waiters.README_PATH
    try:
        stage_waiters.README_PATH = write_submission_contract_readme(
            tmp_path,
            include_adapter_config_clause=False,
        )
        try:
            stage_waiters.load_readme_submission_contract_from_readme()
            raise AssertionError("Expected missing adapter_config clause to raise SystemExit")
        except SystemExit as exc:
            assert "adapter must include adapter_config.json" in str(exc)
    finally:
        stage_waiters.README_PATH = original_readme_path


def test_stage_waiters_verify_readme_submission_contract_file_rejects_missing_submission_zip_clause(
    tmp_path: Path,
) -> None:
    original_readme_path = stage_waiters.README_PATH
    try:
        stage_waiters.README_PATH = write_submission_contract_readme(
            tmp_path,
            include_submission_zip_clause=False,
        )
        try:
            stage_waiters.verify_readme_submission_contract_file()
            raise AssertionError("Expected missing submission.zip clause to raise SystemExit")
        except SystemExit as exc:
            assert "submission archive is submission.zip" in str(exc)
    finally:
        stage_waiters.README_PATH = original_readme_path


def test_stage_waiters_verify_readme_submission_contract_file_rejects_max_rank_drift(tmp_path: Path) -> None:
    original_readme_path = stage_waiters.README_PATH
    try:
        stage_waiters.README_PATH = write_submission_contract_readme(tmp_path, max_lora_rank="64")
        try:
            stage_waiters.verify_readme_submission_contract_file()
            raise AssertionError("Expected max_lora_rank drift to raise SystemExit")
        except SystemExit as exc:
            assert "submission contract mismatch for max_lora_rank" in str(exc)
    finally:
        stage_waiters.README_PATH = original_readme_path


def test_reprobridge25_waiters_readme_contract_loaders_match_expected(tmp_path: Path) -> None:
    original_readme_path = reprobridge25_waiters.README_PATH
    try:
        reprobridge25_waiters.README_PATH = write_submission_contract_readme(tmp_path)
        assert reprobridge25_waiters.verify_readme_contract_file() == reprobridge25_waiters.README_EVAL_CONTRACT
        assert (
            reprobridge25_waiters.verify_readme_submission_contract_file()
            == reprobridge25_waiters.README_SUBMISSION_CONTRACT
        )
    finally:
        reprobridge25_waiters.README_PATH = original_readme_path


def test_reprobridge25_waiters_summarize_wait_summary_gate_accepts_verified_summary(tmp_path: Path) -> None:
    summary_path = tmp_path / "benchmark_eval_suite_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T17:00:00+00:00",
                "readme_contract": reprobridge25_waiters.README_EVAL_CONTRACT,
                "readme_contract_verified_from_readme_file": True,
                "evaluations": [
                    {
                        "evaluation_name": "readme_local320",
                        "rows": 320,
                        "correct": 227,
                        "accuracy": 0.7094,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    gate = reprobridge25_waiters.summarize_wait_summary_gate(summary_path)

    assert gate["exists"] is True
    assert gate["gate_status"] == "existing_summary_verified"
    assert gate["ready_for_launch"] is True
    assert gate["readme_contract_verified_from_readme_file"] is True
    assert gate["readme_contract_state"]["matches_current_readme"] is True
    reprobridge25_waiters.verify_wait_summary_gate(gate)


def test_reprobridge25_waiters_verify_wait_summary_gate_rejects_unverified_existing_summary(
    tmp_path: Path,
) -> None:
    summary_path = tmp_path / "benchmark_eval_suite_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T17:00:00+00:00",
                "readme_contract": reprobridge25_waiters.README_EVAL_CONTRACT,
                "evaluations": [
                    {
                        "evaluation_name": "readme_local320",
                        "rows": 320,
                        "correct": 227,
                        "accuracy": 0.7094,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    gate = reprobridge25_waiters.summarize_wait_summary_gate(summary_path)

    assert gate["gate_status"] == "existing_summary_missing_readme_verification"
    assert gate["ready_for_launch"] is False
    assert gate["readme_contract_state"]["matches_current_readme"] is True
    try:
        reprobridge25_waiters.verify_wait_summary_gate(gate)
        raise AssertionError("Expected stale wait summary gate to raise SystemExit")
    except SystemExit as exc:
        assert "WAIT_SUMMARY_PATH is not README-verified" in str(exc)


def test_reprobridge25_waiters_build_launch_summary_includes_readme_gate(tmp_path: Path) -> None:
    gate = reprobridge25_waiters.summarize_wait_summary_gate(tmp_path / "missing_summary.json")
    summary = reprobridge25_waiters.build_launch_summary(
        launch_status="blocked_by_wait_summary_gate",
        existing_processes=["proc-a", "proc-b"],
        launched_waiters={
            "waiter_a": {"name": "wait-resume-train-from-path", "pid": None, "log": "/tmp/a.log", "launched": False},
            "waiter_b": {"name": "poll-live-run-status", "pid": None, "log": "/tmp/b.log", "launched": False},
            "waiter_c": {"name": "postprocess-run", "pid": None, "log": "/tmp/c.log", "launched": False},
        },
        reprobridge25_processes=[],
        active_readme_eval_contract=reprobridge25_waiters.README_EVAL_CONTRACT,
        active_readme_submission_contract=reprobridge25_waiters.README_SUBMISSION_CONTRACT,
        wait_summary_gate=gate,
    )

    assert summary["summary_schema_version"] == 2
    assert summary["launch_status"] == "blocked_by_wait_summary_gate"
    assert summary["active_readme_eval_contract"] == reprobridge25_waiters.README_EVAL_CONTRACT
    assert summary["active_readme_submission_contract"] == reprobridge25_waiters.README_SUBMISSION_CONTRACT
    assert summary["wait_summary_gate"]["gate_status"] == "waiting_for_summary"
    assert summary["existing_process_count"] == 2


def test_reprobridge25_waiters_launch_commands_use_uv_run_python() -> None:
    captured: list[tuple[list[str], str]] = []
    original_launcher = reprobridge25_waiters.launch_waiter_with_nohup

    try:
        def fake_launcher(cmd_list: list[str], waiter_name: str) -> tuple[int | None, Path]:
            captured.append((cmd_list, waiter_name))
            return 123, Path(f"/tmp/{waiter_name}.log")

        reprobridge25_waiters.launch_waiter_with_nohup = fake_launcher
        reprobridge25_waiters.launch_waiter_a()
        reprobridge25_waiters.launch_waiter_b()
        reprobridge25_waiters.launch_waiter_c()
    finally:
        reprobridge25_waiters.launch_waiter_with_nohup = original_launcher

    assert [name for _, name in captured] == [
        "waiter-a-resume-train",
        "waiter-b-poll-live-status",
        "waiter-c-postprocess",
    ]
    assert all(command[:4] == ["uv", "run", "python", reprobridge25_waiters.MAIN_ENTRYPOINT] for command, _ in captured)
    assert captured[0][0][4:8] == ["--action", "wait-resume-train-from-path", "--run-name", reprobridge25_waiters.RUN_NAME]
    assert captured[1][0][4:8] == ["--action", "poll-live-run-status", "--run-name", reprobridge25_waiters.RUN_NAME]
    assert captured[2][0][4:8] == ["--action", "postprocess-run", "--run-name", reprobridge25_waiters.RUN_NAME]


def test_root_main_legacy_actions_match_reprobridge25_waiter_actions() -> None:
    captured: list[list[str]] = []
    original_launcher = reprobridge25_waiters.launch_waiter_with_nohup

    try:
        def fake_launcher(cmd_list: list[str], waiter_name: str) -> tuple[int | None, Path]:
            captured.append(cmd_list)
            return 123, Path(f"/tmp/{waiter_name}.log")

        reprobridge25_waiters.launch_waiter_with_nohup = fake_launcher
        reprobridge25_waiters.launch_waiter_a()
        reprobridge25_waiters.launch_waiter_b()
        reprobridge25_waiters.launch_waiter_c()
    finally:
        reprobridge25_waiters.launch_waiter_with_nohup = original_launcher

    waiter_actions = {command[5] for command in captured}
    assert waiter_actions == set(root_main.LEGACY_ACTIONS)


def test_root_main_root_only_actions_stay_separate_from_legacy_waiters() -> None:
    assert set(root_main.LEGACY_ACTIONS).isdisjoint(root_main.ROOT_ONLY_ACTIONS)
    assert root_main.ROOT_ONLY_ACTIONS == ("pty-health-probe",)


def test_materialize_shell_wrappers_target_existing_uv_python_entrypoints() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    materialize_script = (repo_root / "materialize.sh").read_text(encoding="utf-8")
    exec_script = (repo_root / "exec_materialize.sh").read_text(encoding="utf-8")
    run_script = (repo_root / "run_materialize.sh").read_text(encoding="utf-8")

    assert "uv run python materialize_reprobridges.py" in materialize_script
    assert "uv run python materialize_reprobridges.py" in exec_script
    assert "uv run python materialize_reprobridges.py" in run_script
    assert "exit_code=$?" in run_script
    assert "exit $exit_code" in run_script
    assert (repo_root / "materialize_reprobridges.py").exists()


def test_root_shell_wrappers_use_uv_python_and_existing_targets() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    root_shell_scripts = sorted(path for path in repo_root.iterdir() if path.is_file() and path.suffix == ".sh")

    assert root_shell_scripts
    for script_path in root_shell_scripts:
        script = script_path.read_text(encoding="utf-8")
        assert "python3" not in script
        assert "/usr/bin/python3" not in script
        for line in script.splitlines():
            stripped = line.strip()
            if not stripped.startswith("uv run python "):
                continue
            target = stripped.split()[3]
            assert target.endswith(".py")
            assert (repo_root / target).exists()


def test_repo_root_test_named_python_scripts_are_real_tests() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    temp_debug_scripts = sorted(path.name for path in repo_root.glob("temp_test_*.py") if path.is_file())
    assert not temp_debug_scripts

    root_test_modules = sorted(path for path in repo_root.glob("test_*.py") if path.is_file())
    for path in root_test_modules:
        script = path.read_text(encoding="utf-8")
        looks_like_real_test = (
            "def test_" in script
            or "class Test" in script
            or "import pytest" in script
            or "from pytest" in script
            or "import unittest" in script
            or "from unittest" in script
        )
        assert looks_like_real_test, (
            f"{path.name} looks like a scratch script, not a real test module; "
            "move debug probes out of the repo root or turn them into proper tests."
        )


def test_legacy_materialize_python_wrappers_delegate_to_canonical_main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    canonical_script = (repo_root / "materialize_reprobridges.py").read_text(encoding="utf-8")
    direct_script = (repo_root / "direct_exec_materialize.py").read_text(encoding="utf-8")

    assert "def run_materialization(" in canonical_script
    assert "def render_materialization_output(" in canonical_script
    assert "def main(" in canonical_script
    assert "def write_capture_payload(" in canonical_script
    assert "def main_with_output_capture(" in canonical_script
    assert "raise SystemExit(main())" in canonical_script

    for filename in ("do_materialize.py", "materialize_reprobridge.py", "temp_execute_runner.py"):
        script = (repo_root / filename).read_text(encoding="utf-8")
        assert "from materialize_reprobridges import main" in script
        assert "raise SystemExit(main())" in script

    assert "from materialize_reprobridges import main_with_output_capture" in direct_script
    assert "raise SystemExit(main_with_output_capture())" in direct_script


def test_build_reference_peft_lora_shapes_uses_peft_state_dict(monkeypatch) -> None:
    class FakeTensor:
        def __init__(self, shape: tuple[int, ...]) -> None:
            self.shape = shape

    class DummyContext:
        def __enter__(self) -> None:
            return None

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    captured: dict[str, object] = {}
    fake_accelerate = ModuleType("accelerate")
    fake_accelerate.init_empty_weights = lambda: DummyContext()

    fake_peft = ModuleType("peft")
    fake_peft.LoraConfig = lambda **kwargs: kwargs
    fake_peft.TaskType = SimpleNamespace(CAUSAL_LM="CAUSAL_LM")

    class FakePeftModel:
        def state_dict(self) -> dict[str, FakeTensor]:
            return {
                "base_model.model.backbone.layers.0.mixer.in_proj.lora_A.default.weight": FakeTensor((4, 2)),
            }

    def fake_get_peft_model(model, peft_config):
        captured["target_modules"] = peft_config["target_modules"]
        return FakePeftModel()

    fake_peft.get_peft_model = fake_get_peft_model
    fake_peft.get_peft_model_state_dict = lambda _model: {
        "base_model.model.backbone.layers.0.mixer.in_proj.lora_A.weight": FakeTensor((4, 2)),
        "base_model.model.backbone.layers.0.mixer.in_proj.lora_B.weight": FakeTensor((2, 4)),
    }

    fake_transformers = ModuleType("transformers")

    class FakeAutoConfig:
        @staticmethod
        def from_pretrained(*_args, **_kwargs):
            return object()

    class FakeAutoModelForCausalLM:
        @staticmethod
        def from_config(*_args, **_kwargs):
            return object()

    fake_transformers.AutoConfig = FakeAutoConfig
    fake_transformers.AutoModelForCausalLM = FakeAutoModelForCausalLM

    monkeypatch.setattr(stage_waiters, "ensure_nemotron_meta_import_stubs", lambda: None)
    monkeypatch.setitem(sys.modules, "accelerate", fake_accelerate)
    monkeypatch.setitem(sys.modules, "peft", fake_peft)
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    shapes = stage_waiters.build_reference_peft_lora_shapes(
        reference_model_root=Path("/tmp/fake-model-root"),
        target_modules=r".*\.(in_proj)$",
        rank=2,
        alpha=4.0,
        dropout=0.0,
    )

    assert shapes == {
        "base_model.model.backbone.layers.0.mixer.in_proj.lora_A.weight": (4, 2),
        "base_model.model.backbone.layers.0.mixer.in_proj.lora_B.weight": (2, 4),
    }
    assert captured["target_modules"] == r".*\.(in_proj)$"


def test_convert_mlx_adapter_to_peft_tensors_supports_routed_expert_switch_mlp_and_standard_peft_keys() -> None:
    converted, conversion_preview, source_summary = stage_waiters.convert_mlx_adapter_to_peft_tensors(
        make_switch_mlp_export_source_tensors()
    )

    assert "base_model.model.backbone.layers.0.mixer.in_proj.lora_A.weight" in converted
    assert "base_model.model.backbone.layers.0.mixer.in_proj.lora_B.weight" in converted
    assert "base_model.model.backbone.layers.0.mixer.experts.0.up_proj.lora_A.weight" in converted
    assert "base_model.model.backbone.layers.0.mixer.experts.1.down_proj.lora_B.weight" in converted
    assert all(".default." not in key for key in converted)
    assert tuple(converted["base_model.model.backbone.layers.0.mixer.in_proj.lora_A.weight"].shape) == (3, 2)
    assert tuple(converted["base_model.model.backbone.layers.0.mixer.in_proj.lora_B.weight"].shape) == (4, 2)
    assert tuple(converted["base_model.model.backbone.layers.0.mixer.experts.0.up_proj.lora_A.weight"].shape) == (2, 3)
    assert tuple(converted["base_model.model.backbone.layers.0.mixer.experts.1.down_proj.lora_B.weight"].shape) == (4, 2)
    assert source_summary["source_tensor_rank_counts"] == [
        {"tensor_rank": 2, "tensor_count": 2},
        {"tensor_rank": 3, "tensor_count": 2},
    ]
    assert any(row["target_key"].endswith("lora_A.weight") for row in conversion_preview)


def test_build_peft_target_modules_regex_includes_attention_projection_terminals() -> None:
    regex = stage_waiters.build_peft_target_modules_regex(
        [
            "backbone.layers.0.mixer.q_proj.lora_a",
            "backbone.layers.0.mixer.k_proj.lora_a",
            "backbone.layers.0.mixer.v_proj.lora_b",
            "backbone.layers.0.mixer.o_proj.lora_b",
        ]
    )

    assert regex == r".*\.(q_proj|k_proj|v_proj|o_proj)$"


def test_run_audit_submission_compat_treats_supported_switch_mlp_3d_as_exportable(
    tmp_path: Path, monkeypatch
) -> None:
    source_tensors = make_switch_mlp_export_source_tensors()
    adapter_dir = tmp_path / "adapter"
    output_root = tmp_path / "audit"
    model_root = tmp_path / "model"
    adapter_dir.mkdir()
    model_root.mkdir()
    captured_json: dict[str, object] = {}

    fake_safetensors = ModuleType("safetensors")
    fake_safetensors_numpy = ModuleType("safetensors.numpy")
    fake_safetensors_numpy.load_file = lambda _path: source_tensors

    monkeypatch.setitem(sys.modules, "safetensors", fake_safetensors)
    monkeypatch.setitem(sys.modules, "safetensors.numpy", fake_safetensors_numpy)
    monkeypatch.setattr(stage_waiters, "verify_training_outputs", lambda _path: None)
    monkeypatch.setattr(
        stage_waiters,
        "load_json",
        lambda path, default=None: (
            make_switch_mlp_export_adapter_config() if Path(path).name == "adapter_config.json" else default
        ),
    )
    monkeypatch.setattr(stage_waiters, "write_json", lambda path, payload: captured_json.setdefault(path.name, payload))
    monkeypatch.setattr(stage_waiters, "write_text", lambda _path, _text: None)
    monkeypatch.setattr(
        stage_waiters,
        "build_reference_peft_lora_shapes",
        lambda **_kwargs: make_switch_mlp_reference_shapes(),
    )
    monkeypatch.setattr(
        stage_waiters,
        "get_effective_readme_submission_contract",
        lambda _args: stage_waiters.README_SUBMISSION_CONTRACT,
    )
    monkeypatch.setattr(stage_waiters, "readme_submission_contract_verified_from_file", lambda _args: True)

    stage_waiters.run_audit_submission_compat(
        SimpleNamespace(
            adapter_dir=adapter_dir,
            output_root=output_root,
            base_model_name_or_path=stage_waiters.BASE_MODEL_NAME,
            reference_model_root=model_root,
        )
    )

    payload = captured_json["submission_compat_audit.json"]
    assert payload["peft_export_ready"] is True
    assert payload["audit_status"] == "potentially_exportable_2d_only"
    assert payload["blocked_reasons"] == []
    assert payload["unsupported_tensor_count"] == 0
    assert payload["target_modules"] == r".*\.(in_proj|up_proj|down_proj)$"
    assert payload["reference_validation"]["valid"] is True
    assert payload["converted_tensor_count"] == len(make_switch_mlp_reference_shapes())


def test_build_submission_candidate_from_payload_requires_boolean_peft_export_ready() -> None:
    payload = {
        "run_name": "demo-run",
        "run_root": "baseline_mlx/outputs/demo-run",
        "label": "demo",
        "prepare_manifest": {
            "train_csv": "train.csv",
            "training": {
                "trainable_lora_suffixes": ["mixer.out_proj"],
                "lora_keys": ["mixer.out_proj"],
            },
        },
        "evaluation_payloads": {
            "readme_local320": {"overall": {"rows": 320, "correct": 230, "accuracy": 230 / 320}},
            "leaderboard_proxy_v1_set": {"overall": {"rows": 200, "correct": 120, "accuracy": 0.60}},
            "leaderboard_proxy_v2": {"overall": {"rows": 84, "correct": 54, "accuracy": 54 / 84}},
            "binary_bias_specialized_set": {"overall": {"rows": 563, "correct": 320, "accuracy": 320 / 563}},
        },
        "local320_components": {
            "general_stable_set": {"rows": 200, "correct": 190, "accuracy": 0.95},
            "binary_hard_set": {"rows": 60, "correct": 40, "accuracy": 40 / 60},
            "symbol_watch_set": {"rows": 60, "correct": 50, "accuracy": 50 / 60},
        },
        "audit_summary": {
            "audit_status": "potentially_exportable_2d_only",
            "peft_export_ready": "true",
        },
        "export_manifest": {"zip_path": "submission.zip"},
    }

    candidate = stage_waiters.build_submission_candidate_from_payload(payload)

    assert candidate["audit_status"] == "potentially_exportable_2d_only"
    assert candidate["peft_export_ready"] is False


def test_export_peft_submission_artifacts_supports_switch_mlp_3d(tmp_path: Path, monkeypatch) -> None:
    source_tensors = make_switch_mlp_export_source_tensors()
    adapter_dir = tmp_path / "adapter"
    output_root = tmp_path / "export"
    model_root = tmp_path / "model"
    adapter_dir.mkdir()
    model_root.mkdir()
    captured_saved: dict[str, dict[str, np.ndarray]] = {}

    fake_safetensors = ModuleType("safetensors")
    fake_safetensors_numpy = ModuleType("safetensors.numpy")
    fake_safetensors_numpy.load_file = lambda _path: source_tensors

    def fake_save_file(payload: dict[str, np.ndarray], path: str) -> None:
        captured_saved["tensors"] = dict(payload)
        Path(path).write_bytes(b"fake-safetensors")

    fake_safetensors_numpy.save_file = fake_save_file

    monkeypatch.setitem(sys.modules, "safetensors", fake_safetensors)
    monkeypatch.setitem(sys.modules, "safetensors.numpy", fake_safetensors_numpy)
    monkeypatch.setattr(stage_waiters, "verify_training_outputs", lambda _path: None)
    monkeypatch.setattr(
        stage_waiters,
        "load_json",
        lambda path, default=None: (
            make_switch_mlp_export_adapter_config() if Path(path).name == "adapter_config.json" else default
        ),
    )
    monkeypatch.setattr(
        stage_waiters,
        "build_reference_peft_lora_shapes",
        lambda **_kwargs: make_switch_mlp_reference_shapes(),
    )

    manifest = stage_waiters.export_peft_submission_artifacts(
        adapter_dir=adapter_dir,
        output_root=output_root,
        reference_model_root=model_root,
        base_model_name_or_path=stage_waiters.BASE_MODEL_NAME,
        readme_submission_contract=stage_waiters.README_SUBMISSION_CONTRACT,
        readme_submission_contract_verified_from_readme_file=True,
    )

    saved_tensors = captured_saved["tensors"]
    assert manifest["validation"]["valid"] is True
    assert manifest["target_modules"] == r".*\.(in_proj|up_proj|down_proj)$"
    assert manifest["converted_tensor_count"] == len(make_switch_mlp_reference_shapes())
    assert manifest["source_tensor_summary"]["source_tensor_count"] == len(source_tensors)
    assert "base_model.model.backbone.layers.0.mixer.experts.0.up_proj.lora_A.weight" in saved_tensors
    assert all(".default." not in key for key in saved_tensors)

    adapter_payload = json.loads((output_root / "submission_adapter" / "adapter_config.json").read_text(encoding="utf-8"))
    assert adapter_payload["target_modules"] == r".*\.(in_proj|up_proj|down_proj)$"
    with zipfile.ZipFile(output_root / "submission.zip") as archive:
        assert sorted(archive.namelist()) == ["adapter_config.json", "adapter_model.safetensors"]


def test_postprocess_run_skips_export_when_audit_ready_flag_is_non_boolean(tmp_path: Path) -> None:
    run_root = make_candidate_run(
        tmp_path,
        run_name="non_boolean_export_gate",
        local320_correct=224,
        proxy_correct=72,
        specialized_correct=320,
    )
    shadow_model_dir = run_root / "shadow_model"
    shadow_model_dir.mkdir(parents=True, exist_ok=True)
    prepare_manifest = json.loads((run_root / "prepare_manifest.json").read_text(encoding="utf-8"))
    prepare_manifest["shadow_model_dir"] = str(shadow_model_dir.resolve())
    prepare_manifest["artifacts"] = {"adapter_dir": str((run_root / "adapter").resolve())}
    (run_root / "prepare_manifest.json").write_text(json.dumps(prepare_manifest), encoding="utf-8")
    (run_root / "submission_compat_audit" / "submission_compat_audit.json").write_text(
        json.dumps(
            {
                "audit_status": "potentially_exportable_2d_only",
                "peft_export_ready": "true",
            }
        ),
        encoding="utf-8",
    )
    summary_json = tmp_path / "postprocess_non_boolean_export_gate_summary.json"

    original_export = stage_waiters.run_export_peft_submission
    try:
        stage_waiters.run_export_peft_submission = (
            lambda _args: (_ for _ in ()).throw(AssertionError("export ran"))
        )
        stage_waiters.run_postprocess_run(
            build_postprocess_args(
                run_root=run_root,
                summary_json=summary_json,
                dry_run=False,
                skip_existing_steps=False,
                run_eval_suite=False,
                run_audit_submission=False,
                run_record_run_result=False,
                run_package_best_submission=False,
            )
        )
    finally:
        stage_waiters.run_export_peft_submission = original_export

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["steps"]["audit_submission"]["status"] == "skipped"
    assert summary["steps"]["export_submission"]["status"] == "skipped"
    assert summary["steps"]["export_submission"]["reason"] == "submission audit is not export-ready"
    assert summary["steps"]["export_submission"]["audit_status"] == "potentially_exportable_2d_only"


def test_root_main_translates_legacy_wait_resume_action() -> None:
    argv = [
        "--action",
        "wait-resume-train-from-path",
        "--run-name",
        "demo-run",
        "--train-csv",
        "train.csv",
        "--source-run-root",
        "source-run",
        "--wait-summary-path",
        "summary.json",
        "--memory-requirement-gb",
        "150",
        "--lr",
        "1e-6",
        "--epochs",
        "0.8",
        "--max-seq-length",
        "1024",
        "--valid-shadow-rows",
        "8",
        "--lora-key-group",
        "stage-union-exportsafe",
        "--trainable-lora-suffix-group",
        "attention",
        "--type-samples",
        "Bit Manipulation",
        "34",
        "--type-samples",
        "Text Encryption",
        "18",
    ]

    translated = root_main.translate_legacy_action_args(argv)

    assert translated == [
        "wait-resume-train-from-path",
        "--run-name",
        "demo-run",
        "--train-csv",
        "train.csv",
        "--source-run-root",
        "source-run",
        "--wait-path",
        "summary.json",
        "--min-free-gb",
        "150",
        "--learning-rate",
        "1e-6",
        "--num-epochs",
        "0.8",
        "--max-seq-length",
        "1024",
        "--valid-shadow-rows",
        "8",
        "--lora-key-group",
        "stage-union-exportsafe",
        "--trainable-lora-suffix-group",
        "attention",
        "--type-sample",
        "Bit Manipulation=34",
        "--type-sample",
        "Text Encryption=18",
    ]


def test_root_main_translates_legacy_poll_live_action() -> None:
    translated = root_main.translate_legacy_action_args(
        [
            "--action",
            "poll-live-run-status",
            "--run-name",
            "demo-run",
            "--live-poller-label",
            "demo label",
        ]
    )

    assert translated == [
        "poll-live-run-status",
        "--run-root",
        str(root_main.DEFAULT_OUTPUT_ROOT / "demo-run"),
        "--label",
        "demo label",
    ]


def test_root_main_translates_legacy_postprocess_action() -> None:
    translated = root_main.translate_legacy_action_args(
        [
            "--action",
            "postprocess-run",
            "--run-name",
            "demo-run",
            "--train-csv",
            "train.csv",
            "--results-label",
            "demo results",
            "--extra-benchmark-csv",
            "proxy.csv",
            "--publish-commit-msg",
            "Record results",
        ]
    )

    assert translated == [
        "postprocess-run",
        "--run-root",
        str(root_main.DEFAULT_OUTPUT_ROOT / "demo-run"),
        "--label",
        "demo results",
        "--extra-benchmark-csv",
        "proxy.csv",
        "--run-publish-results-md",
        "--publish-commit-message",
        "Record results",
    ]


def test_root_main_passes_through_monolith_args() -> None:
    argv = ["postprocess-run", "--run-root", "/tmp/demo-run"]
    assert root_main.translate_legacy_action_args(argv) == argv


def test_root_main_passes_through_root_only_action_args() -> None:
    argv = [
        "--action",
        "pty-health-probe",
        "--output",
        "probe.json",
        "--markdown-output",
        "probe.md",
    ]
    assert root_main.translate_legacy_action_args(argv) == argv


def test_root_main_main_delegates_translated_args() -> None:
    captured: dict[str, object] = {}
    original = root_main.baseline_mlx_main
    try:
        root_main.baseline_mlx_main = lambda argv: captured.setdefault("argv", list(argv))
        root_main.main(
            [
                "--action",
                "poll-live-run-status",
                "--run-name",
                "demo-run",
                "--live-poller-label",
                "demo label",
            ]
        )
    finally:
        root_main.baseline_mlx_main = original

    assert captured["argv"] == [
        "poll-live-run-status",
        "--run-root",
        str(root_main.DEFAULT_OUTPUT_ROOT / "demo-run"),
        "--label",
        "demo label",
    ]


def test_root_main_run_root_only_action_delegates_to_pty_health_probe() -> None:
    captured: dict[str, object] = {}
    original = root_main.pty_health_probe_main

    try:
        def fake_probe_main(argv):
            captured["argv"] = list(argv)
            return 0

        root_main.pty_health_probe_main = fake_probe_main
        exit_code = root_main.run_root_only_action(
            [
                "--action",
                "pty-health-probe",
                "--output",
                "probe.json",
                "--markdown-output",
                "probe.md",
            ]
        )
    finally:
        root_main.pty_health_probe_main = original

    assert exit_code == 0
    assert captured["argv"] == [
        "--output",
        "probe.json",
        "--markdown-output",
        "probe.md",
    ]


def test_root_main_main_exits_with_pty_health_probe_status() -> None:
    original = root_main.pty_health_probe_main

    try:
        root_main.pty_health_probe_main = lambda argv: 7
        try:
            root_main.main(["--action", "pty-health-probe"])
        except SystemExit as exc:
            assert exc.code == 7
        else:
            raise AssertionError("Expected SystemExit for root-only PTY probe action")
    finally:
        root_main.pty_health_probe_main = original


def test_recovery_command_targets_exist_and_use_absolute_paths() -> None:
    assert recovery_hub.PIPELINE_PATH.exists()
    assert recovery_hub.THRESHOLD_SCRIPT_PATH.exists()
    assert v3f_submission.SELF_PATH == v3f_submission.REPO_ROOT / v3f_submission.SELF_RELPATH
    assert v3f_submission.SELF_PATH.exists()

    captured: list[tuple[str, list[str]]] = []
    original_ensure_waiter = recovery_hub.ensure_waiter
    try:
        def fake_ensure_waiter(waiters_dir: Path, log_name: str, argv: list[str]) -> dict[str, object]:
            captured.append((log_name, list(argv)))
            return {"status": "captured", "argv": list(argv)}

        recovery_hub.ensure_waiter = fake_ensure_waiter
        recovery_hub.arm_reprobridge31()
        recovery_hub.arm_reprobridge32()
    finally:
        recovery_hub.ensure_waiter = original_ensure_waiter

    for log_name, argv in captured:
        if log_name in {"launcher", "live", "postprocess"}:
            assert argv[:4] == ["uv", "run", "python", str(recovery_hub.PIPELINE_PATH)]
        if log_name in {"threshold075", "threshold080"}:
            assert argv[:4] == ["uv", "run", "python", "-c"]
            assert str(recovery_hub.THRESHOLD_SCRIPT_PATH) in argv[4]


def test_active_submission_wrappers_point_to_existing_readme_and_monolith() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    expected_readme = repo_root / "README.md"
    expected_monolith = MODULE_PATH.resolve()

    for module in (
        binary40_wrapper,
        o30best_wrapper,
        o30best_proxybench_wrapper,
        threshold_wrapper,
    ):
        assert module.README_PATH == expected_readme
        assert module.README_PATH.exists()
        assert module.MONOLITH_PATH == expected_monolith
        assert module.MONOLITH_PATH.exists()


def test_active_submission_wrappers_gate_on_peft_export_ready_not_legacy_audit_status() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    for relpath in (
        "versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py",
        "versions/baseline_mlx_o30best_repro_v1/reproduce_o30best_submission.py",
        "versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py",
        "versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py",
    ):
        text = (repo_root / relpath).read_text(encoding="utf-8")
        assert "peft_export_ready" in text
        assert '== "potentially_exportable_2d_only"' not in text


def test_active_audit_gate_surfaces_avoid_legacy_status_compares_and_truthy_coercions() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    forbidden_fragments = (
        '== "potentially_exportable_2d_only"',
        '!= "potentially_exportable_2d_only"',
        "README-compatible 2D-only audit",
        'bool(candidate["peft_export_ready"])',
        "bool(row['peft_export_ready'])",
        'bool(row["peft_export_ready"])',
        'bool(audit_summary.get("peft_export_ready"))',
        "bool(audit_summary.get('peft_export_ready'))",
        'get("peft_export_ready", False)',
        "get('peft_export_ready', False)",
    )
    for relpath in (
        "baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py",
        "versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py",
        "launch_reprobridge31_32_recovery.py",
        "versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py",
        "versions/baseline_mlx_o30best_repro_v1/reproduce_o30best_submission.py",
        "versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py",
        "versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py",
    ):
        text = (repo_root / relpath).read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            assert fragment not in text, f"{relpath} still contains forbidden audit gating fragment: {fragment}"


def test_followup_steps_form_a_repo_relative_continuation_chain() -> None:
    step_names = [step.step_name for step in recovery_hub.FOLLOWUP_STEPS]
    output_dataset_rels = []
    output_summary_rels = []

    assert step_names == ["reprobridge33", "reprobridge34", "reprobridge35", "reprobridge36"]
    assert len(set(step_names)) == len(step_names)

    for step in recovery_hub.FOLLOWUP_STEPS:
        for relpath in (
            step.base_dataset_rel,
            step.base_summary_rel,
            step.output_dataset_rel,
            step.output_summary_rel,
        ):
            path = Path(relpath)
            assert not path.is_absolute()
            assert ".." not in path.parts
            assert len(path.parts) >= 4
            assert path.parts[:2] == ("baseline_mlx", "outputs")
        assert f"{step.step_name}_" in step.output_dataset_rel
        assert step.output_dataset_rel.endswith("_v1.csv")
        assert step.output_summary_rel == step.output_dataset_rel.replace(".csv", "_summary.json")
        assert step.base_summary_rel == step.base_dataset_rel.replace(".csv", "_summary.json")
        output_dataset_rels.append(step.output_dataset_rel)
        output_summary_rels.append(step.output_summary_rel)

    for index in range(1, len(recovery_hub.FOLLOWUP_STEPS)):
        prev_step = recovery_hub.FOLLOWUP_STEPS[index - 1]
        step = recovery_hub.FOLLOWUP_STEPS[index]
        assert step.base_dataset_rel == prev_step.output_dataset_rel
        assert step.base_summary_rel == prev_step.output_summary_rel

    first_step = recovery_hub.FOLLOWUP_STEPS[0]
    assert "reprobridge32_" in first_step.base_dataset_rel
    assert "reprobridge32_" in first_step.base_summary_rel

    assert len(set(output_dataset_rels)) == len(output_dataset_rels)
    assert len(set(output_summary_rels)) == len(output_summary_rels)


def test_active_version_directories_have_git_visible_markdown_ledgers() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    versions_root = repo_root / "versions"
    active_version_dirs = sorted(
        path.name for path in versions_root.iterdir() if path.is_dir() and path.name != "archive"
    )

    assert active_version_dirs

    for version_name in active_version_dirs:
        version_dir = versions_root / version_name
        candidate_ledgers = [
            version_dir / "RESULT.md",
            version_dir / f"{version_name}-results.md",
        ]
        existing_ledgers = [ledger for ledger in candidate_ledgers if ledger.exists()]
        assert existing_ledgers, f"Missing Git-visible markdown ledger for {version_name}"
        for ledger in existing_ledgers:
            assert ledger.suffix == ".md"
            text = ledger.read_text(encoding="utf-8").strip()
            lower_text = text.lower()
            assert text, f"Empty ledger: {ledger}"
            assert "readme" in lower_text, f"Ledger must stay README-visible: {ledger}"
            assert (
                re.search(r"\b\d+/\d+\s*=", text) is not None
                or "measured score:" in lower_text
                or "overall_accuracy" in lower_text
            ), f"Ledger must preserve score/status visibility: {ledger}"
            script_paths = {
                repo_root / candidate
                for match in re.findall(r"[A-Za-z0-9_./-]+\.py", text)
                for candidate in [Path(match)]
                if not candidate.is_absolute()
                and ".." not in candidate.parts
                and "tests" not in candidate.parts
            }
            assert any(path.is_file() for path in script_paths), f"Ledger must preserve script lineage: {ledger}"


def test_current_repro_result_ledgers_explain_legacy_audit_status() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    for relpath in (
        "versions/baseline_mlx_binary40_repro_v1/RESULT.md",
        "versions/baseline_mlx_o30best_repro_v1/RESULT.md",
        "versions/baseline_mlx_o30best_proxybench_repro_v1/RESULT.md",
    ):
        text = (repo_root / relpath).read_text(encoding="utf-8")
        assert "potentially_exportable_2d_only" in text
        assert "peft_export_ready" in text
        assert "legacy compatibility label" in text
        assert "regenerated_submission_valid" in text


def test_threshold_result_ledger_exposes_live_exportability_signals() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    text = (
        repo_root
        / "versions/baseline_mlx_threshold_submission_v1/baseline_mlx_threshold_submission_v1-results.md"
    ).read_text(encoding="utf-8")
    assert "existing_peft_export_ready" in text
    assert "existing_validation_valid" in text
    assert "reproduced_peft_export_ready" in text
    assert "reproduced_validation_valid" in text
    assert "live README-facing exportability signals" in text
    assert "- existing_export_valid:" not in text


def test_threshold_wrapper_does_not_reintroduce_existing_export_valid_alias() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    text = (
        repo_root / "versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py"
    ).read_text(encoding="utf-8")

    assert "existing_validation_valid" in text
    assert "existing_export_valid" not in text


def test_archive_version_directories_have_git_visible_markdown_ledgers() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    archive_root = repo_root / "versions" / "archive"
    archive_version_dirs = sorted(path.name for path in archive_root.iterdir() if path.is_dir())

    assert archive_version_dirs

    for version_name in archive_version_dirs:
        ledger = archive_root / version_name / f"{version_name}-results.md"
        assert ledger.exists(), f"Missing archive markdown ledger for {version_name}"
        text = ledger.read_text(encoding="utf-8").strip()
        lower_text = text.lower()
        assert text, f"Empty archive ledger: {ledger}"
        assert "readme" in lower_text, f"Archive ledger must stay README-visible: {ledger}"
        assert (
            re.search(r"\b\d+/\d+\s*=", text) is not None
            or "measured score:" in lower_text
            or "overall_accuracy" in lower_text
        ), f"Archive ledger must preserve score/status visibility: {ledger}"
        script_paths = {
            repo_root / candidate
            for match in re.findall(r"[A-Za-z0-9_./-]+\.py", text)
            for candidate in [Path(match)]
            if not candidate.is_absolute()
            and ".." not in candidate.parts
            and "tests" not in candidate.parts
        }
        assert any(path.is_file() for path in script_paths), f"Archive ledger must preserve script lineage: {ledger}"


def test_late_version_ledgers_keep_git_visible_score_placeholders_until_outputs_exist() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    versions_root = repo_root / "versions"

    for version_name in ("v5", "v5-1", "v6", "v7"):
        version_dir = versions_root / version_name
        ledger = version_dir / f"{version_name}-results.md"
        outputs_dir = version_dir / "outputs"
        text = ledger.read_text(encoding="utf-8")
        lower_text = text.lower()

        assert "readme" in lower_text, f"Late-version ledger must stay README-visible: {ledger}"
        assert "submission.zip" in lower_text, f"Late-version ledger must stay submission-visible: {ledger}"
        assert "measured score:" in lower_text, f"Late-version ledger must keep a measured score line: {ledger}"
        assert "recording rule" in lower_text, f"Late-version ledger must explain how scores get recorded: {ledger}"

        if not outputs_dir.exists():
            assert (
                "not recorded in the current git-visible snapshot" in lower_text
            ), f"Late-version ledger without outputs must keep the Git-visible placeholder: {ledger}"
            assert (
                f"current repo snapshot has no `{version_dir.relative_to(repo_root) / 'outputs'}/` tree".lower()
                in lower_text
            ), f"Late-version ledger must explain the missing outputs tree: {ledger}"


def test_historical_plan_docs_keep_readme_contract_note() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    plan_paths = [
        repo_root / "versions" / "v0" / "v0-plan.md",
        repo_root / "versions" / "v1" / "v1-plam.md",
        repo_root / "versions" / "v2" / "v2-plam.md",
        repo_root / "versions" / "v3" / "v3-plam.md",
        repo_root / "versions" / "v4" / "v4-plam.md",
        repo_root / "versions" / "archive" / "v1" / "v1-plan.md",
        repo_root / "versions" / "archive" / "v4" / "v4-plan.md",
        repo_root / "versions" / "archive" / "v7" / "v7-plan.md",
        repo_root / "versions" / "archive" / "v8" / "v8-plan.md",
    ]

    for plan_path in plan_paths:
        text = plan_path.read_text(encoding="utf-8")
        header = "\n".join(text.splitlines()[:12]).lower()
        assert "historical plan note:" in header, f"Missing historical contract note: {plan_path}"
        assert "readme.md" in header, f"Missing README contract reference: {plan_path}"
        assert "submission.zip" in header, f"Missing submission contract reference: {plan_path}"


def test_root_resources_guide_starts_with_readme_contract_note() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    guide_path = repo_root / "How to Get Started + Nemotron Model Reasoning Challenge Resources.md"
    header = "\n".join(guide_path.read_text(encoding="utf-8").splitlines()[:8]).lower()

    assert "competition contract note:" in header
    assert "readme.md" in header
    assert "submission.zip" in header
    assert "max_tokens = 7680" in header
    assert "max_num_seqs = 64" in header
    assert "gpu_memory_utilization = 0.85" in header


def test_transformers_guide_starts_with_readme_contract_note() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    guide_path = repo_root / "how-to-get-started-transformers.md"
    header = "\n".join(guide_path.read_text(encoding="utf-8").splitlines()[:10]).lower()

    assert "competition contract note" in header
    assert "readme.md" in header
    assert "submission.zip" in header
    assert "max_tokens = 7680" in header
    assert "max_num_seqs = 64" in header
    assert "gpu_memory_utilization = 0.85" in header


def test_root_model_card_carries_non_authoritative_contract_note() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    guide_path = repo_root / "README-Nemotron-3-Nano-30B-A3B-BF16.md"
    header = "\n".join(guide_path.read_text(encoding="utf-8").splitlines()[:45]).lower()

    assert "repository note:" in header
    assert "upstream/reference model card snapshot" in header
    assert "readme.md" in header
    assert "submission.zip" in header
    assert "max_tokens = 7680" in header
    assert "gpu_memory_utilization = 0.85" in header


def test_root_pty_health_probe_stays_repo_tracked_and_actionable() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "pty_health_probe.py"
    text = script_path.read_text(encoding="utf-8")
    lower_text = text.lower()

    assert "uv run python pty_health_probe.py" in text
    assert "/dev/ptmx" in text
    assert "lsof" in text
    assert "kern.tty.ptmx_max" in text
    assert "os.openpty" in text
    assert "--markdown-output" in text
    assert "recommended_actions" in text
    assert "subprocess.run" in text
    assert "shell=True" not in text
    assert "diagnose" in lower_text and "pty" in lower_text


def test_root_pty_health_probe_parse_sysctl_value_handles_expected_shapes() -> None:
    assert pty_health_probe.parse_sysctl_value("") is None
    assert pty_health_probe.parse_sysctl_value("kern.tty.ptmx_max: 127\n") == "127"
    assert pty_health_probe.parse_sysctl_value("kern.tty.ptmx_max") is None


def test_root_pty_health_probe_summarize_lsof_counts_open_rows() -> None:
    assert pty_health_probe.summarize_lsof("") == {"open_handle_rows": 0}
    assert pty_health_probe.summarize_lsof("COMMAND PID USER\n") == {
        "open_handle_rows": 0,
        "header": "COMMAND PID USER",
    }
    assert pty_health_probe.summarize_lsof(
        "COMMAND PID USER\npython 1 me\npython 2 me\n"
    ) == {
        "open_handle_rows": 2,
        "header": "COMMAND PID USER",
        "sample_rows": ["python 1 me", "python 2 me"],
    }


def test_root_pty_health_probe_build_ptmx_capacity_summary_handles_missing_limit() -> None:
    assert pty_health_probe.build_ptmx_capacity_summary({"open_handle_rows": 5}, None) == {
        "open_handle_rows": 5,
        "limit": None,
        "utilization": None,
        "near_limit": None,
    }
    assert pty_health_probe.build_ptmx_capacity_summary({"open_handle_rows": 5}, "not-an-int") == {
        "open_handle_rows": 5,
        "limit": None,
        "utilization": None,
        "near_limit": None,
    }


def test_root_pty_health_probe_build_ptmx_capacity_summary_computes_utilization() -> None:
    assert pty_health_probe.build_ptmx_capacity_summary({"open_handle_rows": 114}, "127") == {
        "open_handle_rows": 114,
        "limit": 127,
        "utilization": 0.8976,
        "near_limit": False,
    }
    assert pty_health_probe.build_ptmx_capacity_summary({"open_handle_rows": 120}, "127") == {
        "open_handle_rows": 120,
        "limit": 127,
        "utilization": 0.9449,
        "near_limit": True,
    }


def test_root_pty_health_probe_derive_probe_status_distinguishes_primary_causes() -> None:
    assert pty_health_probe.derive_probe_status(
        {"exists": False, "is_char_device": False},
        {"success": False},
        {"near_limit": None},
        ["missing /dev/ptmx"],
    ) == {
        "overall": "blocked",
        "primary_cause": "dev-ptmx-invalid",
    }
    assert pty_health_probe.derive_probe_status(
        {"exists": True, "is_char_device": True},
        {"success": True},
        {"near_limit": True},
        ["ptmx near limit"],
    ) == {
        "overall": "blocked",
        "primary_cause": "ptmx-near-limit",
    }
    assert pty_health_probe.derive_probe_status(
        {"exists": True, "is_char_device": True},
        {"success": False},
        {"near_limit": False},
        ["openpty failed"],
    ) == {
        "overall": "blocked",
        "primary_cause": "openpty-failed",
    }
    assert pty_health_probe.derive_probe_status(
        {"exists": True, "is_char_device": True},
        {"success": True},
        {"near_limit": False},
        ["sysctl failed"],
    ) == {
        "overall": "degraded",
        "primary_cause": "needs-attention",
    }
    assert pty_health_probe.derive_probe_status(
        {"exists": True, "is_char_device": True},
        {"success": True},
        {"near_limit": False},
        [],
    ) == {
        "overall": "healthy",
        "primary_cause": "none",
    }


def test_root_pty_health_probe_probe_openpty_reports_failure(monkeypatch) -> None:
    def fake_openpty():
        raise OSError("posix_openpt failed: Device not configured")

    monkeypatch.setattr(pty_health_probe.os, "openpty", fake_openpty)
    result = pty_health_probe.probe_openpty()

    assert result == {
        "success": False,
        "error": "posix_openpt failed: Device not configured",
    }


def test_root_pty_health_probe_probe_openpty_reports_success(monkeypatch) -> None:
    closed_fds: list[int] = []

    monkeypatch.setattr(pty_health_probe.os, "openpty", lambda: (101, 202))
    monkeypatch.setattr(pty_health_probe.os, "ttyname", lambda fd: f"/dev/pts/{fd}")
    monkeypatch.setattr(pty_health_probe.os, "close", closed_fds.append)

    result = pty_health_probe.probe_openpty()

    assert result == {
        "success": True,
        "slave_name": "/dev/pts/202",
    }
    assert closed_fds == [101, 202]


def test_root_pty_health_probe_probe_openpty_reports_ttyname_failure(monkeypatch) -> None:
    closed_fds: list[int] = []

    monkeypatch.setattr(pty_health_probe.os, "openpty", lambda: (101, 202))

    def fake_ttyname(_fd: int) -> str:
        raise OSError("ttyname failed")

    monkeypatch.setattr(pty_health_probe.os, "ttyname", fake_ttyname)
    monkeypatch.setattr(pty_health_probe.os, "close", closed_fds.append)

    result = pty_health_probe.probe_openpty()

    assert result == {
        "success": False,
        "error": "ttyname failed",
    }
    assert closed_fds == [101, 202]


def test_root_pty_health_probe_build_report_collects_expected_fields(monkeypatch) -> None:
    monkeypatch.setattr(pty_health_probe.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(
        pty_health_probe,
        "inspect_dev_ptmx",
        lambda: {
            "path": "/dev/ptmx",
            "exists": True,
            "is_char_device": True,
            "mode": "crw-rw-rw-",
            "major": 16,
            "minor": 2,
        },
    )
    monkeypatch.setattr(pty_health_probe, "probe_openpty", lambda: {"success": True, "slave_name": "/dev/pts/3"})

    def fake_run_command(argv: list[str]):
        command = tuple(argv)
        if command == ("ls", "-l", "/dev/ptmx"):
            return pty_health_probe.CommandResult(
                argv=list(command),
                available=True,
                returncode=0,
                stdout="crw-rw-rw-  1 root  wheel   16,   2 /dev/ptmx\n",
                stderr="",
                resolved_executable="/bin/ls",
            )
        if command == ("lsof", "/dev/ptmx"):
            return pty_health_probe.CommandResult(
                argv=list(command),
                available=True,
                returncode=0,
                stdout="COMMAND PID USER\npython 101 me\n",
                stderr="",
                resolved_executable="/usr/sbin/lsof",
            )
        if command == ("sysctl", "kern.tty.ptmx_max"):
            return pty_health_probe.CommandResult(
                argv=list(command),
                available=True,
                returncode=0,
                stdout="kern.tty.ptmx_max: 127\n",
                stderr="",
                resolved_executable="/usr/sbin/sysctl",
            )
        raise AssertionError(f"Unexpected command: {argv}")

    monkeypatch.setattr(pty_health_probe, "run_command", fake_run_command)

    report = pty_health_probe.build_report()

    assert report["platform"] == "Darwin"
    assert report["probe_status"] == {
        "overall": "healthy",
        "primary_cause": "none",
    }
    assert report["dev_ptmx"]["exists"] is True
    assert report["openpty_probe"]["success"] is True
    assert report["derived"]["kern_tty_ptmx_max"] == "127"
    assert report["derived"]["lsof_summary"]["open_handle_rows"] == 1
    assert report["derived"]["ptmx_capacity"] == {
        "open_handle_rows": 1,
        "limit": 127,
        "utilization": 0.0079,
        "near_limit": False,
    }
    assert report["issues"] == []
    assert report["recommended_actions"]


def test_root_pty_health_probe_render_markdown_summary_surfaces_contract_fields() -> None:
    markdown = pty_health_probe.render_markdown_summary(
        {
            "platform": "Darwin",
            "probe_status": {
                "overall": "blocked",
                "primary_cause": "openpty-failed",
            },
            "dev_ptmx": {
                "exists": True,
                "is_char_device": True,
                "mode": "crw-rw-rw-",
            },
            "openpty_probe": {
                "success": False,
                "error": "posix_openpt failed: Device not configured",
            },
            "derived": {
                "kern_tty_ptmx_max": "127",
                "lsof_summary": {"open_handle_rows": 5},
                "ptmx_capacity": {
                    "open_handle_rows": 5,
                    "limit": 127,
                    "utilization": 0.0394,
                    "near_limit": False,
                },
            },
            "issues": ["Python os.openpty() failed; inspect openpty_probe.error for details."],
            "recommended_actions": [
                "Inspect /dev/ptmx permissions and device-node state from ls -l /dev/ptmx.",
                "Inspect current PTY holders from lsof /dev/ptmx.",
            ],
        }
    )

    lower_markdown = markdown.lower()
    assert "# pty health probe summary" in lower_markdown
    assert "overall status" in lower_markdown
    assert "primary cause" in lower_markdown
    assert "/dev/ptmx exists" in lower_markdown
    assert "os.openpty success" in lower_markdown
    assert "kern.tty.ptmx_max" in markdown
    assert "lsof open_handle_rows" in markdown
    assert "ptmx utilization" in markdown
    assert "ptmx near_limit" in markdown
    assert "## Issues" in markdown
    assert "## Recommended actions" in markdown
    assert "posix_openpt failed: Device not configured" in markdown


def test_root_pty_health_probe_build_report_flags_near_limit(monkeypatch) -> None:
    monkeypatch.setattr(pty_health_probe.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(
        pty_health_probe,
        "inspect_dev_ptmx",
        lambda: {
            "path": "/dev/ptmx",
            "exists": True,
            "is_char_device": True,
            "mode": "crw-rw-rw-",
            "major": 16,
            "minor": 2,
        },
    )
    monkeypatch.setattr(pty_health_probe, "probe_openpty", lambda: {"success": True, "slave_name": "/dev/pts/7"})

    def fake_run_command(argv: list[str]):
        command = tuple(argv)
        if command == ("ls", "-l", "/dev/ptmx"):
            return pty_health_probe.CommandResult(
                argv=list(command),
                available=True,
                returncode=0,
                stdout="crw-rw-rw-  1 root  wheel   16,   2 /dev/ptmx\n",
                stderr="",
                resolved_executable="/bin/ls",
            )
        if command == ("lsof", "/dev/ptmx"):
            rows = "\n".join(f"python {index} me" for index in range(120))
            return pty_health_probe.CommandResult(
                argv=list(command),
                available=True,
                returncode=0,
                stdout=f"COMMAND PID USER\n{rows}\n",
                stderr="",
                resolved_executable="/usr/sbin/lsof",
            )
        if command == ("sysctl", "kern.tty.ptmx_max"):
            return pty_health_probe.CommandResult(
                argv=list(command),
                available=True,
                returncode=0,
                stdout="kern.tty.ptmx_max: 127\n",
                stderr="",
                resolved_executable="/usr/sbin/sysctl",
            )
        raise AssertionError(f"Unexpected command: {argv}")

    monkeypatch.setattr(pty_health_probe, "run_command", fake_run_command)

    report = pty_health_probe.build_report()

    assert report["probe_status"] == {
        "overall": "blocked",
        "primary_cause": "ptmx-near-limit",
    }
    assert report["derived"]["ptmx_capacity"]["near_limit"] is True
    assert "Observed /dev/ptmx open handle count is near kern.tty.ptmx_max." in report["issues"]


def test_root_pty_health_probe_main_writes_json_report(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "pty_probe.json"
    monkeypatch.setattr(
        pty_health_probe,
        "parse_args",
        lambda _argv=None: SimpleNamespace(output=output_path, markdown_output=None),
    )
    monkeypatch.setattr(
        pty_health_probe,
        "build_report",
        lambda: {
            "issues": [],
            "recommended_actions": ["inspect"],
            "platform": "Darwin",
            "probe_status": {"overall": "healthy", "primary_cause": "none"},
            "dev_ptmx": {},
            "openpty_probe": {},
            "derived": {},
        },
    )

    exit_code = pty_health_probe.main()

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["platform"] == "Darwin"
    assert payload["issues"] == []


def test_root_pty_health_probe_main_returns_nonzero_when_issues_exist(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "pty_probe.json"
    monkeypatch.setattr(
        pty_health_probe,
        "parse_args",
        lambda _argv=None: SimpleNamespace(output=output_path, markdown_output=None),
    )
    monkeypatch.setattr(
        pty_health_probe,
        "build_report",
        lambda: {
            "issues": ["openpty failed"],
            "recommended_actions": ["reboot"],
            "platform": "Darwin",
            "probe_status": {"overall": "blocked", "primary_cause": "openpty-failed"},
            "dev_ptmx": {},
            "openpty_probe": {},
            "derived": {},
        },
    )

    exit_code = pty_health_probe.main()

    assert exit_code == 1
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["issues"] == ["openpty failed"]


def test_root_pty_health_probe_main_writes_markdown_summary(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "pty_probe.json"
    markdown_path = tmp_path / "pty_probe.md"
    monkeypatch.setattr(
        pty_health_probe,
        "parse_args",
        lambda _argv=None: SimpleNamespace(output=output_path, markdown_output=markdown_path),
    )
    monkeypatch.setattr(
        pty_health_probe,
        "build_report",
        lambda: {
            "platform": "Darwin",
            "probe_status": {"overall": "healthy", "primary_cause": "none"},
            "dev_ptmx": {"exists": True, "is_char_device": True, "mode": "crw-rw-rw-"},
            "openpty_probe": {"success": True, "slave_name": "/dev/pts/3"},
            "derived": {
                "kern_tty_ptmx_max": "127",
                "lsof_summary": {"open_handle_rows": 1},
                "ptmx_capacity": {
                    "open_handle_rows": 1,
                    "limit": 127,
                    "utilization": 0.0079,
                    "near_limit": False,
                },
            },
            "issues": [],
            "recommended_actions": ["Inspect /dev/ptmx permissions and device-node state from ls -l /dev/ptmx."],
        },
    )

    exit_code = pty_health_probe.main()

    assert exit_code == 0
    assert output_path.exists()
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# PTY health probe summary" in markdown
    assert "kern.tty.ptmx_max" in markdown


def test_root_markdown_files_stay_readme_visible() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    root_markdown_files = sorted(
        path for path in repo_root.iterdir() if path.is_file() and path.suffix == ".md"
    )

    assert root_markdown_files
    for markdown_path in root_markdown_files:
        text = markdown_path.read_text(encoding="utf-8").strip()
        assert text, f"Empty root markdown file: {markdown_path}"
        if markdown_path.name in {"README.md", "AGENTS.md"}:
            continue
        header = "\n".join(text.splitlines()[:48]).lower()
        assert "readme.md" in header, f"Root markdown must stay README-visible near the top: {markdown_path}"
        assert "submission.zip" in header, (
            f"Root markdown must surface the active submission artifact near the top: {markdown_path}"
        )
        assert (
            "repository note:" in header or "competition contract note:" in header
        ), f"Root markdown must open with a contract note: {markdown_path}"


def test_nested_baseline_ledger_keeps_readme_contract_note() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    ledger_path = repo_root / "baseline_mlx" / "baseline_mlx" / "baseline_mlx-results.md"
    header = "\n".join(ledger_path.read_text(encoding="utf-8").splitlines()[:16]).lower()

    assert "readme.md" in header
    assert "submission.zip" in header
    assert "max_tokens = 7680" in header
    assert "max_num_seqs = 64" in header


def test_discussion_docs_keep_readme_context() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    discussion_paths = sorted((repo_root / "discussion").rglob("*.md"))

    for discussion_path in discussion_paths:
        header = "\n".join(discussion_path.read_text(encoding="utf-8").splitlines()[:12]).lower()
        assert "readme.md" in header, f"Metric discussion must point back to README.md: {discussion_path}"
        assert "max_tokens = 7680" in header, (
            f"Discussion doc must surface README evaluation values: {discussion_path}"
        )
        assert "max_num_seqs = 64" in header, (
            f"Discussion doc must surface README evaluation values: {discussion_path}"
        )
        assert "submission.zip" in header, (
            f"Discussion doc must surface active submission artifact name: {discussion_path}"
        )


def test_high_risk_reference_docs_keep_readme_context() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    reference_paths = [
        repo_root / "BF16_SINGLEFILE_REPRO_SUMMARY_2026-03-27.md",
        repo_root / "DATA_ANALYSIS_REPORT.md",
        repo_root / "target_modules_fact_record_2026-04-08.md",
    ]

    for reference_path in reference_paths:
        header = "\n".join(reference_path.read_text(encoding="utf-8").splitlines()[:14]).lower()
        assert "readme.md" in header, f"Reference doc must point back to README.md: {reference_path}"
        assert "submission.zip" in header, (
            f"Reference doc must surface active submission artifact name: {reference_path}"
        )
        assert "max_tokens = 7680" in header, (
            f"Reference doc must surface README evaluation values: {reference_path}"
        )
        assert "max_num_seqs = 64" in header, (
            f"Reference doc must surface README evaluation values: {reference_path}"
        )


def test_root_notebooks_carry_readme_contract_notes() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    notebook_paths = sorted(path for path in repo_root.iterdir() if path.is_file() and path.suffix == ".ipynb")

    assert notebook_paths
    for notebook_path in notebook_paths:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        assert "cells" in notebook, f"Notebook missing 'cells' key: {notebook_path}"
        assert notebook["cells"], f"Notebook has empty cells array: {notebook_path}"
        first_cell = notebook["cells"][0]
        assert first_cell["cell_type"] == "markdown", (
            f"Root notebook must start with a markdown repository note: {notebook_path}"
        )
        header = "".join(first_cell["source"]).lower()
        assert "repository note" in header, f"Root notebook must start with repository note: {notebook_path}"
        assert "readme.md" in header, f"Root notebook must point back to README.md: {notebook_path}"
        assert "submission.zip" in header, (
            f"Root notebook must surface active submission artifact name: {notebook_path}"
        )
        assert "max_tokens = 7680" in header, (
            f"Root notebook must surface README evaluation values: {notebook_path}"
        )
        assert "max_num_seqs = 64" in header, (
            f"Root notebook must surface README evaluation values: {notebook_path}"
        )


def test_discussion_notebooks_carry_readme_contract_notes() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    notebook_paths = sorted((repo_root / "discussion").rglob("*.ipynb"))

    assert notebook_paths
    for notebook_path in notebook_paths:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        assert "cells" in notebook, f"Notebook missing 'cells' key: {notebook_path}"
        assert notebook["cells"], f"Notebook has empty cells array: {notebook_path}"
        first_cell = notebook["cells"][0]
        assert first_cell["cell_type"] == "markdown", (
            f"Discussion notebook must start with a markdown repository note: {notebook_path}"
        )
        header = "".join(first_cell["source"]).lower()
        assert "repository note" in header, (
            f"Discussion notebook must start with repository note: {notebook_path}"
        )
        assert "readme.md" in header, (
            f"Discussion notebook must point back to README.md: {notebook_path}"
        )
        assert "submission.zip" in header, (
            f"Discussion notebook must surface active submission artifact name: {notebook_path}"
        )
        assert "max_tokens = 7680" in header, (
            f"Discussion notebook must surface README evaluation values: {notebook_path}"
        )
        assert "max_num_seqs = 64" in header, (
            f"Discussion notebook must surface README evaluation values: {notebook_path}"
        )


def test_active_non_archive_files_do_not_use_historical_submission_zip_names() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    versions_root = repo_root / "versions"
    pattern = re.compile(r"submission_v[0-9][0-9_\-]*\.zip")
    allowed_markdown = {
        versions_root / "baseline_mlx" / "baseline_mlx-results.md",
    }

    offending_code = []
    for path in versions_root.rglob("*.py"):
        if "archive" in path.parts or "tests" in path.parts or "__pycache__" in path.parts:
            continue
        if pattern.search(path.read_text(encoding="utf-8")):
            offending_code.append(path)

    offending_markdown = []
    for path in versions_root.rglob("*.md"):
        if "archive" in path.parts or "__pycache__" in path.parts:
            continue
        if path in allowed_markdown:
            continue
        if pattern.search(path.read_text(encoding="utf-8")):
            offending_markdown.append(path)

    assert not offending_code, f"Historical submission_v*.zip naming leaked into active code: {offending_code}"
    assert not offending_markdown, (
        "Historical submission_v*.zip naming leaked into active non-archive markdown: "
        f"{offending_markdown}"
    )


def test_run_eval_benchmark_suite_writes_progress_files(tmp_path: Path) -> None:
    benchmark_root = tmp_path / "benchmarks"
    benchmark_root.mkdir(parents=True)
    for filename in stage_waiters.REFERENCE_PHASE0_BENCHMARK_FILES:
        (benchmark_root / filename).write_text(
            "id,prompt,answer,prompt_len_chars\nrow-1,What is 1+1?,2,12\n",
            encoding="utf-8",
        )

    output_root = tmp_path / "suite_output"
    model_root = tmp_path / "model_root"
    adapter_dir = tmp_path / "adapter_dir"
    model_root.mkdir()
    adapter_dir.mkdir()

    fake_mlx_lm = ModuleType("mlx_lm")
    original_mlx_lm = sys.modules.get("mlx_lm")
    original_normalize = stage_waiters.normalize_tokenizer_for_hf_parity
    original_eval = stage_waiters.evaluate_benchmark_rows
    original_write_outputs = stage_waiters.write_benchmark_eval_outputs

    fake_mlx_lm.load = lambda *_args, **_kwargs: (object(), object())

    def fake_evaluate_benchmark_rows(
        *,
        model,
        tokenizer,
        benchmark_rows,
        evaluation_name,
        source_paths,
        args,
        progress_callback=None,
    ):
        assert model is not None
        assert tokenizer is not None
        assert source_paths
        if progress_callback is not None:
            progress_callback(
                {
                    "status": "running",
                    "evaluation_name": evaluation_name,
                    "rows_total": len(benchmark_rows),
                    "rows_completed": 0,
                    "chunks_total": 1,
                    "chunks_completed": 0,
                }
            )
            progress_callback(
                {
                    "status": "scored",
                    "evaluation_name": evaluation_name,
                    "rows_total": len(benchmark_rows),
                    "rows_completed": len(benchmark_rows),
                    "chunks_total": 1,
                    "chunks_completed": 1,
                    "correct": len(benchmark_rows),
                    "accuracy": 1.0,
                }
            )
        payload = {
            "overall": {
                "rows": len(benchmark_rows),
                "correct": len(benchmark_rows),
                "accuracy": 1.0,
            }
        }
        return [], [], payload

    try:
        sys.modules["mlx_lm"] = fake_mlx_lm
        stage_waiters.normalize_tokenizer_for_hf_parity = lambda _tokenizer: None
        stage_waiters.evaluate_benchmark_rows = fake_evaluate_benchmark_rows
        stage_waiters.write_benchmark_eval_outputs = lambda **_kwargs: None

        stage_waiters.run_eval_benchmark_suite(
            SimpleNamespace(
                benchmark_root=benchmark_root,
                output_root=output_root,
                model_root=model_root,
                adapter_dir=adapter_dir,
                extra_benchmark_csv=[],
                lazy_load=True,
                max_tokens=stage_waiters.README_MAX_TOKENS,
                temperature=stage_waiters.README_TEMPERATURE,
                top_p=stage_waiters.README_TOP_P,
                max_num_seqs=8,
                gpu_memory_utilization=stage_waiters.README_GPU_MEMORY_UTILIZATION,
                max_model_len=stage_waiters.README_MAX_MODEL_LEN,
                prompt_chunk_size=8,
                prefill_batch_size=8,
                completion_batch_size=8,
                eval_enable_thinking=True,
                force_single_generate=False,
                _verified_readme_contract=dict(stage_waiters.README_EVAL_CONTRACT),
                _readme_contract_verified_from_readme_file=True,
            )
        )
    finally:
        if original_mlx_lm is None:
            sys.modules.pop("mlx_lm", None)
        else:
            sys.modules["mlx_lm"] = original_mlx_lm
        stage_waiters.normalize_tokenizer_for_hf_parity = original_normalize
        stage_waiters.evaluate_benchmark_rows = original_eval
        stage_waiters.write_benchmark_eval_outputs = original_write_outputs

    suite_progress = json.loads(
        (output_root / "benchmark_eval_suite_progress.json").read_text(encoding="utf-8")
    )
    suite_summary = json.loads(
        (output_root / "benchmark_eval_suite_summary.json").read_text(encoding="utf-8")
    )
    assert suite_progress["status"] == "completed"
    assert suite_progress["evaluations_completed"] == 1
    assert suite_progress["current_evaluation"] == "readme_local320"
    assert suite_summary["readme_contract"] == stage_waiters.README_EVAL_CONTRACT
    assert suite_summary["readme_contract_verified_from_readme_file"] is True
    eval_progress = json.loads(
        (output_root / "readme_local320" / "benchmark_eval_progress.json").read_text(encoding="utf-8")
    )
    assert eval_progress["status"] == "completed"
    assert eval_progress["rows_total"] == 3
    assert eval_progress["rows_completed"] == 3
    assert eval_progress["accuracy"] == 1.0


def test_build_text_reanchor_csv_joins_row_analysis_with_train_rows(tmp_path: Path) -> None:
    source_train_csv = tmp_path / "source_train.csv"
    row_analysis_csv = tmp_path / "row_analysis.csv"
    output_csv = tmp_path / "text_reanchor.csv"
    summary_json = tmp_path / "text_reanchor_summary.json"

    write_csv_rows(
        source_train_csv,
        stage_waiters.EXPECTED_COLUMNS,
        [
            {"id": "tv1", "prompt": "p", "answer": "a", "type": "Text Encryption", "generated_cot": "cot"},
            {"id": "tv2", "prompt": "p", "answer": "a", "type": "Text Encryption", "generated_cot": "cot"},
            {"id": "ta1", "prompt": "p", "answer": "a", "type": "Text Encryption", "generated_cot": "cot"},
            {"id": "n1", "prompt": "p", "answer": "a", "type": "Numeral Conversion", "generated_cot": "cot"},
            {"id": "g1", "prompt": "p", "answer": "a", "type": "Gravitational Constant", "generated_cot": "cot"},
            {"id": "u1", "prompt": "p", "answer": "a", "type": "Unit Conversion", "generated_cot": "cot"},
            {"id": "unused", "prompt": "p", "answer": "a", "type": "Equation Transformation", "generated_cot": "cot"},
        ],
    )
    write_csv_rows(
        row_analysis_csv,
        ["id", "family", "template_subtype", "selection_tier"],
        [
            {
                "id": "tv1",
                "family": "text_decryption",
                "template_subtype": "text_monoalphabetic",
                "selection_tier": "verified_trace_ready",
            },
            {
                "id": "tv2",
                "family": "text_decryption",
                "template_subtype": "text_monoalphabetic",
                "selection_tier": "verified_trace_ready",
            },
            {
                "id": "ta1",
                "family": "text_decryption",
                "template_subtype": "text_monoalphabetic",
                "selection_tier": "answer_only_keep",
            },
            {
                "id": "n1",
                "family": "roman_numeral",
                "template_subtype": "roman_standard",
                "selection_tier": "verified_trace_ready",
            },
            {
                "id": "g1",
                "family": "gravity_constant",
                "template_subtype": "gravity_half_g_t2",
                "selection_tier": "verified_trace_ready",
            },
            {
                "id": "u1",
                "family": "unit_conversion",
                "template_subtype": "unit_fixed_ratio",
                "selection_tier": "verified_trace_ready",
            },
            {
                "id": "unused",
                "family": "symbol_equation",
                "template_subtype": "numeric_2x2",
                "selection_tier": "verified_trace_ready",
            },
        ],
    )

    stage_waiters.run_build_text_reanchor_csv(
        SimpleNamespace(
            source_train_csv=source_train_csv,
            row_analysis_csv=row_analysis_csv,
            text_verified_rows=2,
            text_answer_only_rows=1,
            numeral_rows=1,
            gravity_rows=1,
            unit_rows=1,
            seed=123,
            output_csv=output_csv,
            summary_json=summary_json,
        )
    )

    with output_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 6
    assert {row["id"] for row in rows} == {"tv1", "tv2", "ta1", "n1", "g1", "u1"}

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["resolved_rows"] == {
        "text_verified_rows": 2,
        "text_answer_only_rows": 1,
        "numeral_rows": 1,
        "gravity_rows": 1,
        "unit_rows": 1,
    }
    assert summary["type_counts"] == {
        "Gravitational Constant": 1,
        "Numeral Conversion": 1,
        "Text Encryption": 3,
        "Unit Conversion": 1,
    }


def test_build_text_binary_reanchor_csv_joins_proxy_binary_rows(tmp_path: Path) -> None:
    source_train_csv = tmp_path / "source_train.csv"
    row_analysis_csv = tmp_path / "row_analysis.csv"
    output_csv = tmp_path / "text_binary_reanchor.csv"
    summary_json = tmp_path / "text_binary_reanchor_summary.json"

    write_csv_rows(
        source_train_csv,
        stage_waiters.EXPECTED_COLUMNS,
        [
            {"id": "tv1", "prompt": "p", "answer": "a", "type": "Text Encryption", "generated_cot": "cot"},
            {"id": "tv2", "prompt": "p", "answer": "a", "type": "Text Encryption", "generated_cot": "cot"},
            {"id": "b1", "prompt": "p", "answer": "a", "type": "Bit Manipulation", "generated_cot": "cot"},
            {"id": "b2", "prompt": "p", "answer": "a", "type": "Bit Manipulation", "generated_cot": "cot"},
            {"id": "b3", "prompt": "p", "answer": "a", "type": "Bit Manipulation", "generated_cot": "cot"},
            {"id": "g1", "prompt": "p", "answer": "a", "type": "Gravitational Constant", "generated_cot": "cot"},
            {"id": "u1", "prompt": "p", "answer": "a", "type": "Unit Conversion", "generated_cot": "cot"},
            {"id": "unused", "prompt": "p", "answer": "a", "type": "Numeral Conversion", "generated_cot": "cot"},
        ],
    )
    write_csv_rows(
        row_analysis_csv,
        ["id", "family", "template_subtype", "selection_tier", "teacher_solver_candidate"],
        [
            {
                "id": "tv1",
                "family": "text_decryption",
                "template_subtype": "text_monoalphabetic",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "text_char_substitution",
            },
            {
                "id": "tv2",
                "family": "text_decryption",
                "template_subtype": "text_monoalphabetic",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "text_char_substitution",
            },
            {
                "id": "b1",
                "family": "bit_manipulation",
                "template_subtype": "bit_other",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_two_bit_boolean",
            },
            {
                "id": "b2",
                "family": "bit_manipulation",
                "template_subtype": "bit_permutation_inversion",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_bit_permutation_bijection",
            },
            {
                "id": "b3",
                "family": "bit_manipulation",
                "template_subtype": "bit_structured_byte_formula",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_structured_byte_formula",
            },
            {
                "id": "g1",
                "family": "gravity_constant",
                "template_subtype": "gravity_half_g_t2",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "gravity_numeric_rule",
            },
            {
                "id": "u1",
                "family": "unit_conversion",
                "template_subtype": "unit_fixed_ratio",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "unit_numeric_rule",
            },
            {
                "id": "unused",
                "family": "roman_numeral",
                "template_subtype": "roman_standard",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "roman_standard",
            },
        ],
    )

    stage_waiters.run_build_text_binary_reanchor_csv(
        SimpleNamespace(
            source_train_csv=source_train_csv,
            row_analysis_csv=row_analysis_csv,
            text_verified_rows=2,
            binary_bit_other_rows=1,
            binary_bit_permutation_rows=1,
            binary_bit_structured_rows=1,
            gravity_rows=1,
            unit_rows=1,
            prefer_binary_leading_zero=False,
            seed=123,
            output_csv=output_csv,
            summary_json=summary_json,
        )
    )

    with output_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 7
    assert {row["id"] for row in rows} == {"tv1", "tv2", "b1", "b2", "b3", "g1", "u1"}

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["resolved_rows"] == {
        "text_verified_rows": 2,
        "binary_bit_other_rows": 1,
        "binary_bit_permutation_rows": 1,
        "binary_bit_structured_rows": 1,
        "gravity_rows": 1,
        "unit_rows": 1,
    }
    assert summary["type_counts"] == {
        "Bit Manipulation": 3,
        "Gravitational Constant": 1,
        "Text Encryption": 2,
        "Unit Conversion": 1,
    }
    assert summary["template_subtype_counts"] == {
        "bit_other": 1,
        "bit_permutation_inversion": 1,
        "bit_structured_byte_formula": 1,
        "gravity_half_g_t2": 1,
        "text_monoalphabetic": 2,
        "unit_fixed_ratio": 1,
    }
    assert summary["teacher_solver_candidate_counts"] == {
        "binary_bit_permutation_bijection": 1,
        "binary_structured_byte_formula": 1,
        "binary_two_bit_boolean": 1,
        "gravity_numeric_rule": 1,
        "text_char_substitution": 2,
        "unit_numeric_rule": 1,
    }
    assert summary["binary_leading_zero_preferred"] is False
    assert summary["binary_leading_zero_pool_rows"] == {
        "binary_bit_other_rows": 0,
        "binary_bit_permutation_rows": 0,
        "binary_bit_structured_rows": 0,
    }
    assert summary["binary_leading_zero_selected_rows"] == {
        "binary_bit_other_rows": 0,
        "binary_bit_permutation_rows": 0,
        "binary_bit_structured_rows": 0,
    }


def test_build_text_binary_reanchor_csv_prefers_binary_leading_zero_rows(tmp_path: Path) -> None:
    source_train_csv = tmp_path / "source_train.csv"
    row_analysis_csv = tmp_path / "row_analysis.csv"
    output_csv = tmp_path / "text_binary_reanchor_lz.csv"
    summary_json = tmp_path / "text_binary_reanchor_lz_summary.json"

    write_csv_rows(
        source_train_csv,
        stage_waiters.EXPECTED_COLUMNS,
        [
            {"id": "tv1", "prompt": "p", "answer": "AZ", "type": "Text Encryption", "generated_cot": "cot"},
            {"id": "bo_lz", "prompt": "p", "answer": "0011", "type": "Bit Manipulation", "generated_cot": "cot"},
            {"id": "bo_plain", "prompt": "p", "answer": "1111", "type": "Bit Manipulation", "generated_cot": "cot"},
            {"id": "bs_lz", "prompt": "p", "answer": "0101", "type": "Bit Manipulation", "generated_cot": "cot"},
            {"id": "bs_plain", "prompt": "p", "answer": "1100", "type": "Bit Manipulation", "generated_cot": "cot"},
            {"id": "g1", "prompt": "p", "answer": "4.9", "type": "Gravitational Constant", "generated_cot": "cot"},
            {"id": "u1", "prompt": "p", "answer": "12", "type": "Unit Conversion", "generated_cot": "cot"},
        ],
    )
    write_csv_rows(
        row_analysis_csv,
        ["id", "family", "template_subtype", "selection_tier", "teacher_solver_candidate"],
        [
            {
                "id": "tv1",
                "family": "text_decryption",
                "template_subtype": "text_monoalphabetic",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "text_char_substitution",
            },
            {
                "id": "bo_lz",
                "family": "bit_manipulation",
                "template_subtype": "bit_other",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_two_bit_boolean",
            },
            {
                "id": "bo_plain",
                "family": "bit_manipulation",
                "template_subtype": "bit_other",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_affine_xor",
            },
            {
                "id": "bs_lz",
                "family": "bit_manipulation",
                "template_subtype": "bit_structured_byte_formula",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_structured_byte_formula",
            },
            {
                "id": "bs_plain",
                "family": "bit_manipulation",
                "template_subtype": "bit_structured_byte_formula",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "binary_structured_byte_formula_abstract",
            },
            {
                "id": "g1",
                "family": "gravity_constant",
                "template_subtype": "gravity_half_g_t2",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "gravity_numeric_rule",
            },
            {
                "id": "u1",
                "family": "unit_conversion",
                "template_subtype": "unit_fixed_ratio",
                "selection_tier": "verified_trace_ready",
                "teacher_solver_candidate": "unit_numeric_rule",
            },
        ],
    )

    stage_waiters.run_build_text_binary_reanchor_csv(
        SimpleNamespace(
            source_train_csv=source_train_csv,
            row_analysis_csv=row_analysis_csv,
            text_verified_rows=1,
            binary_bit_other_rows=1,
            binary_bit_permutation_rows=0,
            binary_bit_structured_rows=1,
            gravity_rows=1,
            unit_rows=1,
            prefer_binary_leading_zero=True,
            seed=123,
            output_csv=output_csv,
            summary_json=summary_json,
        )
    )

    with output_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    selected_ids = {row["id"] for row in rows}
    assert "bo_lz" in selected_ids
    assert "bo_plain" not in selected_ids
    assert "bs_lz" in selected_ids
    assert "bs_plain" not in selected_ids

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["binary_leading_zero_preferred"] is True
    assert summary["binary_leading_zero_pool_rows"] == {
        "binary_bit_other_rows": 1,
        "binary_bit_permutation_rows": 0,
        "binary_bit_structured_rows": 1,
    }
    assert summary["binary_leading_zero_selected_rows"] == {
        "binary_bit_other_rows": 1,
        "binary_bit_permutation_rows": 0,
        "binary_bit_structured_rows": 1,
    }


def test_package_best_submission_selects_best_exportable_candidate(tmp_path: Path) -> None:
    weaker = make_candidate_run(
        tmp_path,
        run_name="candidate_weaker",
        local320_correct=216,
        proxy_correct=50,
        specialized_correct=280,
    )
    stronger = make_candidate_run(
        tmp_path,
        run_name="candidate_stronger",
        local320_correct=224,
        proxy_correct=72,
        specialized_correct=320,
    )
    output_root = tmp_path / "best_submission"
    results_md = tmp_path / "results.md"

    stage_waiters.run_package_best_submission(
        SimpleNamespace(
            search_root=tmp_path,
            candidate_run_root=[weaker, stronger],
            output_root=output_root,
            results_md=results_md,
            suite_summary_relpath=stage_waiters.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
            audit_relpath=stage_waiters.DEFAULT_RUN_AUDIT_RELPATH,
            export_relpath=stage_waiters.DEFAULT_RUN_EXPORT_RELPATH,
            min_local320_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_LOCAL320_ACCURACY,
            min_general_stable_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_GENERAL_STABLE_ACCURACY,
            min_proxy_v2_accuracy=0.0,
            min_specialized_accuracy=0.0,
            require_exportable=True,
            export_if_missing=False,
            update_results_md=False,
            base_model_name_or_path=stage_waiters.BASE_MODEL_NAME,
        )
    )

    selection = json.loads((output_root / "selection_manifest.json").read_text(encoding="utf-8"))
    assert selection["status"] == "selected_candidate"
    assert selection["eligible_candidate_count"] == 2
    assert selection["selected_run_root"] == str(stronger.resolve())
    assert (output_root / "submission.zip").exists()
    assert (output_root / "submission_adapter" / "adapter_config.json").exists()
    assert json.loads((output_root / "selected_suite_summary.json").read_text(encoding="utf-8"))["evaluations"][0][
        "evaluation_name"
    ] == "readme_local320"


def test_package_best_submission_reports_no_eligible_candidate(tmp_path: Path) -> None:
    make_candidate_run(
        tmp_path,
        run_name="candidate_blocked",
        local320_correct=224,
        export_ready=False,
    )
    output_root = tmp_path / "best_submission"

    stage_waiters.run_package_best_submission(
        SimpleNamespace(
            search_root=tmp_path,
            candidate_run_root=None,
            output_root=output_root,
            results_md=tmp_path / "results.md",
            suite_summary_relpath=stage_waiters.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
            audit_relpath=stage_waiters.DEFAULT_RUN_AUDIT_RELPATH,
            export_relpath=stage_waiters.DEFAULT_RUN_EXPORT_RELPATH,
            min_local320_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_LOCAL320_ACCURACY,
            min_general_stable_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_GENERAL_STABLE_ACCURACY,
            min_proxy_v2_accuracy=0.0,
            min_specialized_accuracy=0.0,
            require_exportable=True,
            export_if_missing=False,
            update_results_md=False,
            base_model_name_or_path=stage_waiters.BASE_MODEL_NAME,
        )
    )

    selection = json.loads((output_root / "selection_manifest.json").read_text(encoding="utf-8"))
    assert selection["status"] == "no_eligible_candidate"
    assert selection["eligible_candidate_count"] == 0
    assert selection["selected_run_root"] == ""
    assert not (output_root / "submission.zip").exists()


def test_package_best_submission_uses_proxy_v1_tiebreak(tmp_path: Path) -> None:
    weaker_proxy_v1 = make_candidate_run(
        tmp_path,
        run_name="candidate_weaker_proxy_v1",
        local320_correct=224,
        proxy_v1_correct=110,
        proxy_correct=72,
        specialized_correct=320,
    )
    stronger_proxy_v1 = make_candidate_run(
        tmp_path,
        run_name="candidate_stronger_proxy_v1",
        local320_correct=224,
        proxy_v1_correct=130,
        proxy_correct=72,
        specialized_correct=320,
    )
    output_root = tmp_path / "best_submission_proxy_v1"

    stage_waiters.run_package_best_submission(
        SimpleNamespace(
            search_root=tmp_path,
            candidate_run_root=[weaker_proxy_v1, stronger_proxy_v1],
            output_root=output_root,
            results_md=tmp_path / "results.md",
            suite_summary_relpath=stage_waiters.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
            audit_relpath=stage_waiters.DEFAULT_RUN_AUDIT_RELPATH,
            export_relpath=stage_waiters.DEFAULT_RUN_EXPORT_RELPATH,
            min_local320_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_LOCAL320_ACCURACY,
            min_general_stable_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_GENERAL_STABLE_ACCURACY,
            min_proxy_v2_accuracy=0.0,
            min_specialized_accuracy=0.0,
            require_exportable=True,
            export_if_missing=False,
            update_results_md=False,
            base_model_name_or_path=stage_waiters.BASE_MODEL_NAME,
        )
    )

    selection = json.loads((output_root / "selection_manifest.json").read_text(encoding="utf-8"))
    assert selection["selected_run_root"] == str(stronger_proxy_v1.resolve())
    assert selection["selected_candidate"]["proxy_v1"]["correct"] == 130


def test_publish_results_md_commits_modified_results_file(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    results_md.write_text("updated\n", encoding="utf-8")
    summary_json = tmp_path / "publish_summary.json"

    stage_waiters.run_publish_results_md(
        SimpleNamespace(
            repo_root=repo_root,
            results_md=results_md,
            commit_message="Record temp results",
            push=False,
            dry_run=False,
            summary_json=summary_json,
            lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
            lock_poll_seconds=0.1,
            lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "committed"
    latest_message = subprocess.run(
        ["git", "log", "--format=%B", "-1"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Record temp results" in latest_message
    assert stage_waiters.COPILOT_COAUTHORED_BY_TRAILER in latest_message


def test_publish_results_md_reports_no_changes(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    summary_json = tmp_path / "publish_no_changes_summary.json"

    stage_waiters.run_publish_results_md(
        SimpleNamespace(
            repo_root=repo_root,
            results_md=results_md,
            commit_message="Record temp results",
            push=False,
            dry_run=False,
            summary_json=summary_json,
            lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
            lock_poll_seconds=0.1,
            lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "no_changes"
    commit_count = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert commit_count == "1"


def test_publish_results_md_clears_empty_stale_lock_dir(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    results_md.write_text("updated\n", encoding="utf-8")
    summary_json = tmp_path / "publish_stale_empty_lock_summary.json"
    lock_dir = repo_root / ".git" / ".nemotron_ledger_lock"
    lock_dir.mkdir()

    stage_waiters.run_publish_results_md(
        SimpleNamespace(
            repo_root=repo_root,
            results_md=results_md,
            commit_message="Record temp results",
            push=False,
            dry_run=False,
            summary_json=summary_json,
            lock_dir=lock_dir,
            lock_poll_seconds=0.1,
            lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "committed"
    assert summary["cleared_stale_lock_count"] == 1
    assert not lock_dir.exists()


def test_publish_results_md_clears_dead_owner_lock_dir(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    results_md.write_text("updated\n", encoding="utf-8")
    summary_json = tmp_path / "publish_stale_owner_lock_summary.json"
    lock_dir = repo_root / ".git" / ".nemotron_ledger_lock"
    lock_dir.mkdir()
    stage_waiters.write_json(
        lock_dir / stage_waiters.DEFAULT_RESULTS_GIT_LOCK_OWNER_FILENAME,
        {
            "pid": 999999,
            "created_at": stage_waiters.utc_now(),
            "command": "publish-results-md",
        },
    )

    stage_waiters.run_publish_results_md(
        SimpleNamespace(
            repo_root=repo_root,
            results_md=results_md,
            commit_message="Record temp results",
            push=False,
            dry_run=False,
            summary_json=summary_json,
            lock_dir=lock_dir,
            lock_poll_seconds=0.1,
            lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "committed"
    assert summary["cleared_stale_lock_count"] == 1
    assert not lock_dir.exists()


def test_publish_results_md_retries_git_add_after_index_lock(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    results_md.write_text("updated\n", encoding="utf-8")
    summary_json = tmp_path / "publish_index_lock_retry_summary.json"

    original_run_git = stage_waiters.run_git_text_command
    original_sleep = stage_waiters.time.sleep
    add_attempts = {"count": 0}
    sleep_calls: list[float] = []

    try:
        def fake_run_git(repo_root_arg: Path, args: tuple[str, ...] | list[str]):
            if tuple(args[:1]) == ("add",):
                add_attempts["count"] += 1
                if add_attempts["count"] == 1:
                    return (
                        128,
                        "fatal: Unable to create '/tmp/repo/.git/index.lock': File exists.\n"
                        "Another git process seems to be running in this repository.",
                    )
            return original_run_git(repo_root_arg, args)

        stage_waiters.run_git_text_command = fake_run_git
        stage_waiters.time.sleep = lambda seconds: sleep_calls.append(float(seconds))

        stage_waiters.run_publish_results_md(
            SimpleNamespace(
                repo_root=repo_root,
                results_md=results_md,
                commit_message="Record temp results",
                push=False,
                dry_run=False,
                summary_json=summary_json,
                lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
                lock_poll_seconds=0.1,
                lock_timeout_seconds=1.0,
            )
        )
    finally:
        stage_waiters.run_git_text_command = original_run_git
        stage_waiters.time.sleep = original_sleep

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "committed"
    assert summary["add_retry_count"] == 1
    assert add_attempts["count"] == 2
    assert sleep_calls == [1.0]


def test_publish_results_md_retries_git_commit_after_index_lock(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    results_md.write_text("updated\n", encoding="utf-8")
    summary_json = tmp_path / "publish_commit_index_lock_retry_summary.json"

    original_run_git = stage_waiters.run_git_text_command
    original_sleep = stage_waiters.time.sleep
    commit_attempts = {"count": 0}
    sleep_calls: list[float] = []

    try:
        def fake_run_git(repo_root_arg: Path, args: tuple[str, ...] | list[str]):
            if tuple(args[:1]) == ("commit",):
                commit_attempts["count"] += 1
                if commit_attempts["count"] == 1:
                    return (
                        128,
                        "fatal: Unable to create '/tmp/repo/.git/index.lock': File exists.\n"
                        "Another git process seems to be running in this repository.",
                    )
            return original_run_git(repo_root_arg, args)

        stage_waiters.run_git_text_command = fake_run_git
        stage_waiters.time.sleep = lambda seconds: sleep_calls.append(float(seconds))

        stage_waiters.run_publish_results_md(
            SimpleNamespace(
                repo_root=repo_root,
                results_md=results_md,
                commit_message="Record temp results",
                push=False,
                dry_run=False,
                summary_json=summary_json,
                lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
                lock_poll_seconds=0.1,
                lock_timeout_seconds=1.0,
            )
        )
    finally:
        stage_waiters.run_git_text_command = original_run_git
        stage_waiters.time.sleep = original_sleep

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "committed"
    assert summary["commit_retry_count"] == 1
    assert commit_attempts["count"] == 2
    assert sleep_calls == [1.0]


def test_publish_results_md_retries_after_remote_advances(tmp_path: Path) -> None:
    repo_root, results_md, remote_root = init_git_repo_with_remote_results_md(tmp_path)
    other_root = tmp_path / "other"
    subprocess.run(["git", "clone", str(remote_root), str(other_root)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "remote@example.com"], cwd=other_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Remote User"], cwd=other_root, check=True, capture_output=True, text=True)
    remote_note = other_root / "remote-note.txt"
    remote_note.write_text("remote change\n", encoding="utf-8")
    subprocess.run(["git", "add", "remote-note.txt"], cwd=other_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Remote note"], cwd=other_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push"], cwd=other_root, check=True, capture_output=True, text=True)

    results_md.write_text("updated after remote\n", encoding="utf-8")
    summary_json = tmp_path / "publish_retry_summary.json"

    stage_waiters.run_publish_results_md(
        SimpleNamespace(
            repo_root=repo_root,
            results_md=results_md,
            commit_message="Record temp results",
            push=True,
            dry_run=False,
            summary_json=summary_json,
            lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
            lock_poll_seconds=0.1,
            lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "pushed"
    assert "push_retry" in summary
    assert summary["push_retry"]["upstream_ref"].startswith("origin/")
    remote_head = subprocess.run(
        ["git", "rev-parse", "@{upstream}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    local_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert remote_head == local_head
    log_subjects = subprocess.run(
        ["git", "log", "--format=%s", "--max-count=5"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Record temp results" in log_subjects
    assert "Remote note" in log_subjects


def test_record_live_run_status_prefers_latest_train_report(tmp_path: Path) -> None:
    run_root = make_live_progress_run(tmp_path, run_name="live_progress_latest")
    results_md = tmp_path / "results.md"
    summary_json = tmp_path / "record_live_summary.json"

    stage_waiters.run_record_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-broad",
            results_md=results_md,
            summary_json=summary_json,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "training"
    assert summary["live_progress"]["progress_source"] == "latest_train_report"
    ledger = results_md.read_text(encoding="utf-8")
    assert "### Live progress: `live_progress_latest`" in ledger
    assert "- optimizer_progress: `400/832 = 48.08%`" in ledger
    assert "- source: `latest_train_report`" in ledger


def test_record_live_run_status_falls_back_to_console_log(tmp_path: Path) -> None:
    run_root = make_live_progress_run(
        tmp_path,
        run_name="live_progress_console",
        progress_source="console_log",
    )
    results_md = tmp_path / "results.md"
    summary_json = tmp_path / "record_live_console_summary.json"

    stage_waiters.run_record_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-exportsafe",
            results_md=results_md,
            summary_json=summary_json,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "training"
    assert summary["live_progress"]["progress_source"] == "console_log"
    assert summary["live_progress"]["optimizer_step"] == 400
    assert "- source: `console_log`" in results_md.read_text(encoding="utf-8")


def test_extract_console_train_progress_accepts_micro_step_logs(tmp_path: Path) -> None:
    run_root = tmp_path / "live_progress_micro"
    run_root.mkdir()
    (run_root / "console.log").write_text(
        "Iter 3200: Train loss 0.436, Learning Rate 6.105e-05, "
        "It/sec 0.400, Tokens/sec 245.351, Trained Tokens 1900181, Peak mem 82.620 GB\n",
        encoding="utf-8",
    )

    live_progress = stage_waiters.extract_console_train_progress(run_root)

    assert live_progress is not None
    assert live_progress["progress_source"] == "console_log"
    assert live_progress["iteration"] == 3200
    assert live_progress["steps_per_report_step_unit"] == "micro"
    assert "optimizer_step" not in live_progress

    markdown = stage_waiters.render_live_run_status_markdown(
        {
            "run_name": "live_progress_micro",
            "status": "training",
            "label": "live-micro",
            "status_observed_at": live_progress["observed_at"],
            "run_root": str(run_root),
            "prepare_manifest": {
                "train_csv": "train.csv",
                "sampling": {"sampled_rows": 3321},
                "training": {
                    "optimizer_steps": 832,
                    "learning_rate": 1e-4,
                    "max_seq_length": 4096,
                    "trainable_lora_suffixes": ["mixer.in_proj"],
                },
            },
            "live_progress": live_progress,
        }
    )

    assert "optimizer_progress: `n/a (latest log reports micro step 3200)`" in markdown
    assert "steps_per_report_step_unit: `micro`" in markdown
    assert "optimizer_step: `n/a (micro-step log)`" in markdown


def test_record_live_run_status_prefers_eval_suite_progress_after_training(tmp_path: Path) -> None:
    run_root = make_live_progress_run(
        tmp_path,
        run_name="live_progress_eval",
        progress_source="eval_suite_progress",
    )
    results_md = tmp_path / "results.md"
    summary_json = tmp_path / "record_live_eval_summary.json"

    stage_waiters.run_record_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-eval",
            results_md=results_md,
            summary_json=summary_json,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "evaluating"
    assert summary["live_progress"]["progress_kind"] == "evaluation"
    assert summary["live_progress"]["progress_source"] == "benchmark_eval_suite_progress"
    assert summary["live_progress"]["current_evaluation"] == "readme_local320"
    assert summary["live_progress"]["current_rows_completed"] == 288
    ledger = results_md.read_text(encoding="utf-8")
    assert "#### Latest evaluation progress" in ledger
    assert "- current_evaluation: `readme_local320`" in ledger
    assert "- current_rows_progress: `288/320 = 90.00%`" in ledger
    assert "- suite_evaluations: `0/2 = 0.00%`" in ledger


def test_record_live_run_status_lists_completed_evaluation_scores(tmp_path: Path) -> None:
    run_root = make_live_progress_run(
        tmp_path,
        run_name="live_progress_eval_completed",
        progress_source="eval_suite_progress",
    )
    suite_progress_path = run_root / stage_waiters.DEFAULT_RUN_SUITE_PROGRESS_RELPATH
    suite_payload = json.loads(suite_progress_path.read_text(encoding="utf-8"))
    suite_payload.update(
        {
            "evaluations_completed": 1,
            "current_evaluation": "leaderboard_proxy_v1_set",
            "current_rows_total": 200,
            "current_rows_completed": 32,
            "current_chunks_total": 13,
            "current_chunks_completed": 2,
            "completed_evaluations": [
                {
                    "evaluation_name": "readme_local320",
                    "rows": 320,
                    "correct": 227,
                    "accuracy": 227 / 320,
                }
            ],
        }
    )
    suite_progress_path.write_text(json.dumps(suite_payload), encoding="utf-8")
    proxy_eval_root = suite_progress_path.parent / "leaderboard_proxy_v1_set"
    proxy_eval_root.mkdir(parents=True, exist_ok=True)
    (proxy_eval_root / "benchmark_eval_progress.json").write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-09T02:40:00+00:00",
                "status": "running",
                "evaluation_name": "leaderboard_proxy_v1_set",
                "output_root": str(proxy_eval_root),
                "rows_total": 200,
                "rows_completed": 32,
                "chunks_total": 13,
                "chunks_completed": 2,
                "correct": 20,
                "accuracy": 0.625,
            }
        ),
        encoding="utf-8",
    )
    results_md = tmp_path / "results.md"
    summary_json = tmp_path / "record_live_eval_completed_summary.json"

    stage_waiters.run_record_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-eval-completed",
            results_md=results_md,
            summary_json=summary_json,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "evaluating"
    assert summary["live_progress"]["current_evaluation"] == "leaderboard_proxy_v1_set"
    assert summary["live_progress"]["completed_evaluation_rows"] == [
        {
            "evaluation_name": "readme_local320",
            "rows": 320,
            "correct": 227,
            "accuracy": 227 / 320,
        }
    ]
    ledger = results_md.read_text(encoding="utf-8")
    assert "- completed_evaluations: `['readme_local320']`" in ledger
    assert "- completed_evaluation_scores: `readme_local320 227/320 = 0.7094`" in ledger


def test_record_live_run_status_marks_stopped_when_runtime_pid_is_dead(tmp_path: Path) -> None:
    run_root = make_live_progress_run(
        tmp_path,
        run_name="live_progress_stopped",
        progress_source="console_log",
        runtime_pid=999999,
    )
    results_md = tmp_path / "results.md"
    summary_json = tmp_path / "record_live_stopped_summary.json"

    stage_waiters.run_record_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-stopped",
            results_md=results_md,
            summary_json=summary_json,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "stopped"
    ledger = results_md.read_text(encoding="utf-8")
    assert "- status: `stopped`" in ledger
    assert "- runtime_pid_alive: `False`" in ledger


def test_record_live_run_status_preserves_auto_result_when_recorded(tmp_path: Path) -> None:
    run_root = make_candidate_run(
        tmp_path,
        run_name="live_progress_recorded",
        local320_correct=224,
    )
    (run_root / "recorded_run_result.json").write_text(
        json.dumps({"recorded_at": "2026-04-10T06:00:00+00:00"}),
        encoding="utf-8",
    )
    results_md = tmp_path / "results.md"
    summary_json = tmp_path / "record_live_recorded_summary.json"

    stage_waiters.run_record_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-recorded",
            results_md=results_md,
            summary_json=summary_json,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "recorded"
    ledger = results_md.read_text(encoding="utf-8")
    assert "### Auto result: `live_progress_recorded`" in ledger
    assert "- readme_local320: `224/320 = 0.7000`" in ledger


def test_poll_live_run_status_commits_progress_update(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    run_root = make_live_progress_run(repo_root, run_name="live_progress_polled")
    summary_json = tmp_path / "poll_live_summary.json"

    stage_waiters.run_poll_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-polled",
            results_md=results_md,
            summary_json=summary_json,
            poll_seconds=0.1,
            max_iterations=1,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
            stop_on_training_result=True,
            run_publish_results_md=True,
            publish_commit_message=None,
            publish_push=False,
            publish_dry_run=False,
            repo_root=repo_root,
            publish_lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
            publish_lock_poll_seconds=0.1,
            publish_lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "max_iterations_reached"
    assert summary["iterations"][0]["changed"] is True
    assert summary["iterations"][0]["publish_results_md"]["status"] == "committed"
    latest_message = subprocess.run(
        ["git", "log", "--format=%B", "-1"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Record live progress for live_progress_polled" in latest_message
    assert "### Live progress: `live_progress_polled`" in results_md.read_text(encoding="utf-8")


def test_poll_live_run_status_does_not_stop_while_evaluating(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    run_root = make_live_progress_run(
        repo_root,
        run_name="live_progress_eval_polled",
        progress_source="eval_suite_progress",
    )
    summary_json = tmp_path / "poll_live_eval_summary.json"

    stage_waiters.run_poll_live_run_status(
        SimpleNamespace(
            run_root=run_root,
            label="live-eval-polled",
            results_md=results_md,
            summary_json=summary_json,
            poll_seconds=0.1,
            max_iterations=1,
            max_log_bytes=stage_waiters.DEFAULT_LIVE_PROGRESS_MAX_LOG_BYTES,
            stop_on_training_result=True,
            run_publish_results_md=False,
            publish_commit_message=None,
            publish_push=False,
            publish_dry_run=False,
            repo_root=repo_root,
            publish_lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
            publish_lock_poll_seconds=0.1,
            publish_lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "max_iterations_reached"
    assert summary["latest"]["status"] == "evaluating"
    assert summary["iterations"][0]["publish_results_md"]["status"] == "skipped"


def test_poll_best_submission_selects_candidate_and_publishes_results_md(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    selected = make_candidate_run(
        repo_root,
        run_name="candidate_selected",
        local320_correct=224,
        proxy_correct=72,
        specialized_correct=320,
    )
    output_root = repo_root / "best_submission"
    summary_json = tmp_path / "poll_summary.json"

    stage_waiters.run_poll_best_submission(
        SimpleNamespace(
            search_root=repo_root,
            candidate_run_root=[selected],
            output_root=output_root,
            results_md=results_md,
            suite_summary_relpath=stage_waiters.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
            audit_relpath=stage_waiters.DEFAULT_RUN_AUDIT_RELPATH,
            export_relpath=stage_waiters.DEFAULT_RUN_EXPORT_RELPATH,
            min_local320_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_LOCAL320_ACCURACY,
            min_general_stable_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_GENERAL_STABLE_ACCURACY,
            min_proxy_v2_accuracy=0.0,
            min_specialized_accuracy=0.0,
            require_exportable=True,
            export_if_missing=False,
            update_results_md=True,
            base_model_name_or_path=stage_waiters.BASE_MODEL_NAME,
            poll_seconds=0.1,
            max_iterations=1,
            summary_json=summary_json,
            run_publish_results_md=True,
            publish_commit_message=None,
            publish_push=False,
            publish_dry_run=False,
            repo_root=repo_root,
            publish_lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
            publish_lock_poll_seconds=0.1,
            publish_lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "selected_candidate"
    assert summary["selection_manifest"]["selected_run_root"] == str(selected.resolve())
    assert summary["publish_results_md"]["status"] == "committed"
    latest_message = subprocess.run(
        ["git", "log", "--format=%B", "-1"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Promote best submission candidate" in latest_message


def test_poll_best_submission_can_continue_after_selection(tmp_path: Path) -> None:
    repo_root, results_md = init_git_repo_with_results_md(tmp_path)
    selected = make_candidate_run(
        repo_root,
        run_name="candidate_selected",
        local320_correct=224,
        proxy_correct=72,
        specialized_correct=320,
    )
    output_root = repo_root / "best_submission_continuing"
    summary_json = tmp_path / "poll_summary_continue.json"

    stage_waiters.run_poll_best_submission(
        SimpleNamespace(
            search_root=repo_root,
            candidate_run_root=[selected],
            output_root=output_root,
            results_md=results_md,
            suite_summary_relpath=stage_waiters.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
            audit_relpath=stage_waiters.DEFAULT_RUN_AUDIT_RELPATH,
            export_relpath=stage_waiters.DEFAULT_RUN_EXPORT_RELPATH,
            min_local320_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_LOCAL320_ACCURACY,
            min_general_stable_accuracy=stage_waiters.DEFAULT_BEST_SUBMISSION_MIN_GENERAL_STABLE_ACCURACY,
            min_proxy_v2_accuracy=0.0,
            min_specialized_accuracy=0.0,
            require_exportable=True,
            export_if_missing=False,
            update_results_md=True,
            base_model_name_or_path=stage_waiters.BASE_MODEL_NAME,
            poll_seconds=0.1,
            max_iterations=2,
            continue_after_selection=True,
            summary_json=summary_json,
            run_publish_results_md=True,
            publish_commit_message=None,
            publish_push=False,
            publish_dry_run=False,
            repo_root=repo_root,
            publish_lock_dir=repo_root / ".git" / ".nemotron_ledger_lock",
            publish_lock_poll_seconds=0.1,
            publish_lock_timeout_seconds=1.0,
        )
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "selected_candidate"
    assert summary["continue_after_selection"] is True
    assert len(summary["iterations"]) == 2
    assert summary["iterations"][0]["selection_status"] == "selected_candidate"
    assert summary["iterations"][1]["selection_status"] == "selected_candidate"
    assert summary["selection_manifest"]["selected_run_root"] == str(selected.resolve())
    assert (output_root / "submission.zip").exists()


def test_recovery_summarize_waiter_dir_reports_missing_waiters_and_pid_liveness(tmp_path: Path) -> None:
    waiters_dir = tmp_path / "reprobridge31_waiters"
    waiters_dir.mkdir(parents=True)
    (waiters_dir / "live.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")
    (waiters_dir / "live.log").write_text("live waiter still running\n", encoding="utf-8")
    (waiters_dir / "threshold075.pid").write_text("not-a-pid\n", encoding="utf-8")
    (waiters_dir / "threshold075.log").write_text("waiting for suite summary\n", encoding="utf-8")

    summary = recovery_hub.summarize_waiter_dir(waiters_dir)

    assert summary["exists"] is True
    assert summary["pids"]["live"]["pid"] == os.getpid()
    assert summary["pids"]["live"]["pid_alive"] is True
    assert summary["pids"]["threshold075"]["pid"] is None
    assert summary["pids"]["threshold075"]["pid_alive"] is False
    assert set(summary["missing_waiters"]) == {"launcher", "postprocess", "threshold080"}
    assert summary["logs"]["live.log"]["tail"] == ["live waiter still running"]


def test_recovery_build_status_report_includes_bridge26_and_waiter_details(tmp_path: Path) -> None:
    run_root = tmp_path / "outputs" / "reprobridge26"
    suite_root = run_root / "eval_suite_readme_proxy_specialized"
    readme_root = suite_root / "readme_local320"
    readme_root.mkdir(parents=True)
    (run_root / "prepare_manifest.json").write_text("{}", encoding="utf-8")
    (run_root / "training_result.json").write_text("{}", encoding="utf-8")
    (suite_root / "benchmark_eval_suite_progress.json").write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-12T05:22:00+00:00",
                "status": "running",
                "evaluations_total": 2,
                "evaluations_completed": 0,
                "current_evaluation": "readme_local320",
                "current_rows_total": 320,
                "current_rows_completed": 32,
                "current_chunks_total": 20,
                "current_chunks_completed": 2,
            }
        ),
        encoding="utf-8",
    )
    (readme_root / "benchmark_eval_progress.json").write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-12T05:22:00+00:00",
                "status": "running",
                "evaluation_name": "readme_local320",
                "rows_total": 320,
                "rows_completed": 32,
                "chunks_total": 20,
                "chunks_completed": 2,
                "correct": 28,
                "accuracy": 0.875,
            }
        ),
        encoding="utf-8",
    )

    waiters31 = tmp_path / "reprobridge31_waiters"
    waiters31.mkdir(parents=True)
    (waiters31 / "live.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")
    (waiters31 / "live.log").write_text("live waiter running\n", encoding="utf-8")

    selector_path = tmp_path / "best_submission" / "poll_best_submission_summary.json"
    selector_path.parent.mkdir(parents=True)
    selector_path.write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-12T05:23:00+00:00",
                "status": "selected_candidate_continuing",
                "iterations": [
                    {
                        "iteration": 4,
                        "recorded_at": "2026-04-12T05:23:00+00:00",
                        "selection_status": "selected_candidate",
                    }
                ],
                "selection_manifest": {
                    "candidate_count": 3,
                    "eligible_candidate_count": 1,
                    "selected_candidate": {
                        "run_name": "candidate_a",
                        "run_root": "/tmp/candidate_a",
                        "local320": {"rows": 320, "correct": 235, "accuracy": 0.7344},
                        "general_stable": {"rows": 200, "correct": 183, "accuracy": 0.915},
                        "proxy_v1": {"rows": 200, "correct": 131, "accuracy": 0.655},
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {"reprobridge26": "outputs/reprobridge26"}
        recovery_hub.WAITERS31 = waiters31
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = selector_path
        recovery_hub.FOLLOWUP_STEPS = ()

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert "reprobridge26" in report["runs"]
    assert report["runs"]["reprobridge26"]["prepare_manifest_exists"] is True
    assert report["runs"]["reprobridge26"]["training_result_exists"] is True
    assert report["runs"]["reprobridge26"]["suite_progress"]["current_rows_completed"] == 32
    assert report["runs"]["reprobridge26"]["gate_state"]["local320_accuracy"] == 0.875
    assert report["runs"]["reprobridge26"]["gate_state"]["gate_status"] == "unknown_until_local320_complete"
    assert report["runs"]["reprobridge26"]["gate_state"]["phase"] == "local320_running"
    assert report["waiters"]["reprobridge31"]["pids"]["live"]["pid_alive"] is True
    assert set(report["waiters"]["reprobridge31"]["missing_waiters"]) == {
        "launcher",
        "postprocess",
        "threshold075",
        "threshold080",
    }
    assert report["waiters"]["reprobridge32"]["exists"] is False
    assert report["best_submission_selector"]["latest_iteration"]["iteration"] == 4
    assert report["best_submission_selector"]["candidate_count"] == 3
    assert report["runs"]["reprobridge26"]["audit_summary"] is None
    assert report["runs"]["reprobridge26"]["export_manifest"] is None
    assert report["runs"]["reprobridge26"]["submission_zip_exists"] is False
    assert report["runs"]["reprobridge26"]["missing_postprocess_artifacts"] == [
        "suite_summary",
        "audit_summary",
        "export_manifest",
        "submission_zip",
        "recorded_run_result",
    ]
    assert report["training_completed_pending_postprocess_runs"] == ["reprobridge26"]
    assert report["submission_ready_runs"] == []


def test_recovery_build_status_report_lists_dead_local320_pending_suite(tmp_path: Path) -> None:
    run_root = tmp_path / "outputs" / "reprobridge24"
    suite_root = run_root / "eval_suite_readme_proxy_specialized"
    readme_root = suite_root / "readme_local320"
    proxy_root = suite_root / "leaderboard_proxy_v1_set"
    proxy_root.mkdir(parents=True)
    readme_root.mkdir(parents=True, exist_ok=True)
    (readme_root / "benchmark_eval_progress.json").write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-12T05:34:00+00:00",
                "status": "completed",
                "evaluation_name": "readme_local320",
                "rows_total": 320,
                "rows_completed": 320,
                "chunks_total": 20,
                "chunks_completed": 20,
                "correct": 233,
                "accuracy": 0.7281,
            }
        ),
        encoding="utf-8",
    )
    (proxy_root / "benchmark_eval_progress.json").write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-12T05:34:00+00:00",
                "status": "running",
                "evaluation_name": "leaderboard_proxy_v1_set",
                "rows_total": 200,
                "rows_completed": 0,
                "chunks_total": 13,
                "chunks_completed": 0,
                "correct": 0,
                "accuracy": 0.0,
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {"reprobridge24": "outputs/reprobridge24"}
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = ()

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert report["runs"]["reprobridge24"]["gate_state"]["dead_on_local320"] is True
    assert report["runs"]["reprobridge24"]["gate_state"]["phase"] == "proxy_v1_running"
    assert report["dead_local320_runs"] == ["reprobridge24"]
    assert report["dead_local320_pending_suite"] == ["reprobridge24"]
    assert report["dead_local320_proxy_active_runs"] == ["reprobridge24"]


def test_recovery_build_status_report_includes_artifact_only_run_state(tmp_path: Path) -> None:
    artifact_root = (
        tmp_path
        / "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts"
    )
    artifact_root.mkdir(parents=True, exist_ok=True)
    dataset_path = (
        artifact_root
        / "stage25_o30best_proxybench30ao_reprobridge31_text3bit1num8raw12unitedge_v1.csv"
    )
    summary_path = (
        artifact_root
        / "stage25_o30best_proxybench30ao_reprobridge31_text3bit1num8raw12unitedge_v1_summary.json"
    )
    dataset_path.write_text("id,prompt,answer,type,generated_cot\n", encoding="utf-8")
    summary_path.write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T04:30:00+00:00",
                "base_dataset": "artifact_base.csv",
                "output_dataset": "artifact_out.csv",
                "strategy": "raw12_unitedge",
                "removed_rows": ["old_id"],
                "added_rows": ["new_id"],
                "resulting_mix": {
                    "Bit": 34,
                    "Text": 18,
                    "Gravity": 9,
                    "Unit": 1,
                    "Equation": 18,
                },
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {"reprobridge31": "outputs/reprobridge31"}
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS31.mkdir(parents=True, exist_ok=True)
        (recovery_hub.WAITERS31 / "live.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")
        (recovery_hub.WAITERS31 / "live.log").write_text("waiting\n", encoding="utf-8")
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = ()

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    run_payload = report["runs"]["reprobridge31"]
    assert run_payload["exists"] is False
    assert run_payload["artifact_status"]["dataset_exists"] is True
    assert run_payload["artifact_status"]["summary_exists"] is True
    assert run_payload["artifact_status"]["summary"]["strategy"] == "raw12_unitedge"
    assert run_payload["artifact_status"]["summary"]["added_rows"] == ["new_id"]
    assert report["artifact_only_runs"] == ["reprobridge31"]
    assert report["stale_waiter_runs"] == ["reprobridge31"]


def test_recovery_build_status_report_lists_multiple_artifact_only_bridge_runs(tmp_path: Path) -> None:
    artifact_root = tmp_path / "baseline_mlx" / "outputs" / "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts"
    artifact_root.mkdir(parents=True)
    dataset27 = (
        artifact_root
        / "stage25_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_v1.csv"
    )
    summary27 = (
        artifact_root
        / "stage25_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_v1_summary.json"
    )
    dataset30 = (
        artifact_root
        / "stage25_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_v1.csv"
    )
    summary30 = (
        artifact_root
        / "stage25_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_v1_summary.json"
    )
    dataset27.write_text("id,prompt,answer,type,generated_cot\n", encoding="utf-8")
    summary27.write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T03:01:41+00:00",
                "strategy": "raw8_plus_unitedge_from_reprobridge26",
                "removed_rows": ["dae6dea8"],
                "added_rows": ["8c6a158e"],
                "resulting_mix": {
                    "Bit": 34,
                    "Text": 18,
                    "Gravity": 9,
                    "Unit": 5,
                    "Equation": 14,
                },
            }
        ),
        encoding="utf-8",
    )
    dataset30.write_text("id,prompt,answer,type,generated_cot\n", encoding="utf-8")
    summary30.write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T03:18:00+00:00",
                "strategy": "raw11_unitedge_from_reprobridge29",
                "removed_rows": ["95e8326c"],
                "added_rows": ["2f485a40"],
                "resulting_mix": {
                    "Bit": 34,
                    "Text": 18,
                    "Gravity": 9,
                    "Unit": 2,
                    "Equation": 17,
                },
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {
            "reprobridge27": "outputs/reprobridge27",
            "reprobridge30": "outputs/reprobridge30",
        }
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = ()

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert report["artifact_only_runs"] == ["reprobridge27", "reprobridge30"]
    assert report["runs"]["reprobridge27"]["artifact_status"]["summary"]["strategy"] == (
        "raw8_plus_unitedge_from_reprobridge26"
    )
    assert report["runs"]["reprobridge30"]["artifact_status"]["summary"]["added_rows"] == ["2f485a40"]
    assert report["stale_waiter_runs"] == []
    assert report["training_completed_pending_postprocess_runs"] == []
    assert report["submission_ready_runs"] == []


def test_recovery_build_status_report_lists_submission_ready_runs(tmp_path: Path) -> None:
    run_root = tmp_path / "outputs" / "reprobridge27"
    suite_root = run_root / "eval_suite_readme_proxy_specialized"
    suite_root.mkdir(parents=True)
    (run_root / "training_result.json").write_text("{}", encoding="utf-8")
    (run_root / "recorded_run_result.json").write_text("{}", encoding="utf-8")
    (run_root / "submission_export").mkdir(parents=True)
    (run_root / "submission_compat_audit").mkdir(parents=True)
    (run_root / "submission_export" / "submission.zip").write_bytes(b"zip")
    (run_root / "submission_export" / "export_manifest.json").write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T08:55:22.788994+00:00",
                "zip_path": str(run_root / "submission_export" / "submission.zip"),
                "zip_size_bytes": 3,
                "converted_tensor_count": 232,
                "base_model_name_or_path": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
                "readme_submission_contract": recovery_hub.README_SUBMISSION_CONTRACT,
                "readme_submission_contract_verified_from_readme_file": True,
                "validation": {
                    "valid": True,
                    "missing_keys": [],
                    "unexpected_keys": [],
                    "shape_mismatches": [],
                },
            }
        ),
        encoding="utf-8",
    )
    (run_root / "submission_compat_audit" / "submission_compat_audit.json").write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T08:55:18.873777+00:00",
                "audit_status": "potentially_exportable_2d_only",
                "peft_export_ready": True,
                "blocked_reasons": [],
                "base_model_name_or_path": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
                "tensor_count": 232,
                "readme_submission_contract": recovery_hub.README_SUBMISSION_CONTRACT,
                "readme_submission_contract_verified_from_readme_file": True,
            }
        ),
        encoding="utf-8",
    )
    (suite_root / "benchmark_eval_suite_summary.json").write_text(
        json.dumps(
            {
                "readme_contract": recovery_hub.README_EVAL_CONTRACT,
                "readme_contract_verified_from_readme_file": True,
                "evaluations": [
                    {"evaluation_name": "readme_local320", "rows": 320, "correct": 227, "accuracy": 0.7094},
                    {"evaluation_name": "leaderboard_proxy_v1_set", "rows": 200, "correct": 129, "accuracy": 0.645},
                ]
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {"reprobridge27": "outputs/reprobridge27"}
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = ()

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert report["runs"]["reprobridge27"]["audit_summary_exists"] is True
    assert report["runs"]["reprobridge27"]["export_manifest_exists"] is True
    assert report["runs"]["reprobridge27"]["submission_zip_exists"] is True
    assert report["runs"]["reprobridge27"]["audit_summary"]["peft_export_ready"] is True
    assert report["runs"]["reprobridge27"]["export_manifest"]["validation"]["valid"] is True
    assert report["runs"]["reprobridge27"]["artifact_readme_verification"] == {
        "suite_readme_contract_verified": True,
        "audit_readme_submission_contract_verified": True,
        "export_readme_submission_contract_verified": True,
    }
    assert report["runs"]["reprobridge27"]["missing_postprocess_artifacts"] == []
    assert report["runs"]["reprobridge27"]["missing_readme_contract_verifications"] == []
    assert report["active_readme_eval_contract"] == recovery_hub.README_EVAL_CONTRACT
    assert report["active_readme_submission_contract"] == recovery_hub.README_SUBMISSION_CONTRACT
    assert report["training_completed_pending_postprocess_runs"] == []
    assert report["submission_ready_runs"] == ["reprobridge27"]
    assert report["stale_readme_contract_runs"] == []


def test_recovery_build_status_report_marks_unverified_contract_artifacts_as_stale(tmp_path: Path) -> None:
    run_root = tmp_path / "outputs" / "reprobridge27"
    suite_root = run_root / "eval_suite_readme_proxy_specialized"
    suite_root.mkdir(parents=True)
    (run_root / "training_result.json").write_text("{}", encoding="utf-8")
    (run_root / "recorded_run_result.json").write_text("{}", encoding="utf-8")
    (run_root / "submission_export").mkdir(parents=True)
    (run_root / "submission_compat_audit").mkdir(parents=True)
    (run_root / "submission_export" / "submission.zip").write_bytes(b"zip")
    (run_root / "submission_export" / "export_manifest.json").write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T08:55:22.788994+00:00",
                "zip_path": str(run_root / "submission_export" / "submission.zip"),
                "zip_size_bytes": 3,
                "converted_tensor_count": 232,
                "base_model_name_or_path": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
                "validation": {
                    "valid": True,
                    "missing_keys": [],
                    "unexpected_keys": [],
                    "shape_mismatches": [],
                },
            }
        ),
        encoding="utf-8",
    )
    (run_root / "submission_compat_audit" / "submission_compat_audit.json").write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T08:55:18.873777+00:00",
                "audit_status": "potentially_exportable_2d_only",
                "peft_export_ready": True,
                "blocked_reasons": [],
                "base_model_name_or_path": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
                "tensor_count": 232,
            }
        ),
        encoding="utf-8",
    )
    (suite_root / "benchmark_eval_suite_summary.json").write_text(
        json.dumps(
            {
                "evaluations": [
                    {"evaluation_name": "readme_local320", "rows": 320, "correct": 227, "accuracy": 0.7094},
                    {"evaluation_name": "leaderboard_proxy_v1_set", "rows": 200, "correct": 129, "accuracy": 0.645},
                ]
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {"reprobridge27": "outputs/reprobridge27"}
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = ()

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert report["runs"]["reprobridge27"]["artifact_readme_verification"] == {
        "suite_readme_contract_verified": None,
        "audit_readme_submission_contract_verified": None,
        "export_readme_submission_contract_verified": None,
    }
    assert report["runs"]["reprobridge27"]["missing_readme_contract_verifications"] == [
        "suite_readme_contract_verification",
        "audit_readme_submission_contract_verification",
        "export_readme_submission_contract_verification",
    ]
    assert report["submission_ready_runs"] == []
    assert report["stale_readme_contract_runs"] == ["reprobridge27"]


def test_recovery_build_status_report_marks_suite_complete_without_export_as_pending_postprocess(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "outputs" / "reprobridge28"
    suite_root = run_root / "eval_suite_readme_proxy_specialized"
    suite_root.mkdir(parents=True)
    (run_root / "training_result.json").write_text("{}", encoding="utf-8")
    (suite_root / "benchmark_eval_suite_summary.json").write_text(
        json.dumps(
            {
                "evaluations": [
                    {"evaluation_name": "readme_local320", "rows": 320, "correct": 228, "accuracy": 0.7125},
                    {"evaluation_name": "leaderboard_proxy_v1_set", "rows": 200, "correct": 126, "accuracy": 0.63},
                ]
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {"reprobridge28": "outputs/reprobridge28"}
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = ()

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert report["runs"]["reprobridge28"]["gate_state"]["phase"] == "suite_completed"
    assert report["runs"]["reprobridge28"]["missing_postprocess_artifacts"] == [
        "audit_summary",
        "export_manifest",
        "submission_zip",
        "recorded_run_result",
    ]
    assert report["training_completed_pending_postprocess_runs"] == ["reprobridge28"]
    assert report["submission_ready_runs"] == []


def test_recovery_build_status_report_includes_followup_artifact_outputs(tmp_path: Path) -> None:
    dataset_rel = "baseline_mlx/outputs/followups/reprobridge33.csv"
    summary_rel = "baseline_mlx/outputs/followups/reprobridge33_summary.json"
    (tmp_path / dataset_rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / dataset_rel).write_text("id,prompt,answer,type,generated_cot\n", encoding="utf-8")
    (tmp_path / summary_rel).write_text(
        json.dumps(
            {
                "created_at": "2026-04-12T06:00:00+00:00",
                "strategy": "raw14_no_unit_from_reprobridge32",
                "removed_rows": ["old_id"],
                "added_rows": ["new_id"],
                "resulting_mix": {"Bit": 34, "Text": 18, "Gravity": 9, "Unit": 0, "Equation": 19},
            }
        ),
        encoding="utf-8",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {}
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = (
            recovery_hub.FollowupStep(
                step_name="reprobridge33",
                base_dataset_rel="baseline_mlx/outputs/followups/base.csv",
                base_summary_rel="baseline_mlx/outputs/followups/base_summary.json",
                output_dataset_rel=dataset_rel,
                output_summary_rel=summary_rel,
                remove_id="old_id",
                add_id="new_id",
                strategy="raw14_no_unit_from_reprobridge32",
                rationale="test rationale",
                source_bridge_label="reprobridge32 raw13 nounit",
                bridge_family_status="test status",
                remove_note_key="removed_row",
                add_note_key="added_row",
            ),
        )

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert report["runs"] == {}
    assert report["artifact_only_runs"] == []
    assert report["ready_followup_steps"] == []
    assert report["blocked_followup_steps"] == []
    assert report["materialized_followup_steps"] == ["reprobridge33"]
    assert report["followup_steps"] == [
        {
            "step_name": "reprobridge33",
            "base_dataset": "baseline_mlx/outputs/followups/base.csv",
            "base_exists": False,
            "base_summary": "baseline_mlx/outputs/followups/base_summary.json",
            "base_summary_exists": False,
            "output_dataset": dataset_rel,
            "output_exists": True,
            "output_summary": summary_rel,
            "output_summary_exists": True,
            "output_summary_excerpt": {
                "created_at": "2026-04-12T06:00:00+00:00",
                "strategy": "raw14_no_unit_from_reprobridge32",
                "removed_rows": ["old_id"],
                "added_rows": ["new_id"],
                "resulting_mix": {"Bit": 34, "Text": 18, "Gravity": 9, "Unit": 0, "Equation": 19},
            },
            "remove_id": "old_id",
            "add_id": "new_id",
            "missing_inputs": ["base_dataset", "base_summary"],
            "ready_to_materialize": False,
            "materialized": True,
        }
    ]


def test_recovery_build_status_report_marks_followup_readiness_chain(tmp_path: Path) -> None:
    base34_csv = (
        "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
        "stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1.csv"
    )
    base34_summary = (
        "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
        "stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1_summary.json"
    )
    (tmp_path / base34_csv).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / base34_csv).write_text("id,prompt,answer,type,generated_cot\n", encoding="utf-8")
    (tmp_path / base34_summary).write_text('{"created_at":"2026-04-12T06:00:00+00:00"}', encoding="utf-8")

    original_repo_root = recovery_hub.REPO_ROOT
    original_run_status_roots = recovery_hub.RUN_STATUS_ROOTS
    original_waiters31 = recovery_hub.WAITERS31
    original_waiters32 = recovery_hub.WAITERS32
    original_selector_summary = recovery_hub.BEST_SELECTOR_SUMMARY
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.RUN_STATUS_ROOTS = {}
        recovery_hub.WAITERS31 = tmp_path / "reprobridge31_waiters"
        recovery_hub.WAITERS32 = tmp_path / "reprobridge32_waiters"
        recovery_hub.BEST_SELECTOR_SUMMARY = tmp_path / "missing_selector.json"
        recovery_hub.FOLLOWUP_STEPS = (
            recovery_hub.FollowupStep(
                step_name="reprobridge35",
                base_dataset_rel=base34_csv,
                base_summary_rel=base34_summary,
                output_dataset_rel=(
                    "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
                    "stage25_o30best_proxybench30ao_reprobridge35_text3bit1num8raw16nounit_v1.csv"
                ),
                output_summary_rel=(
                    "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
                    "stage25_o30best_proxybench30ao_reprobridge35_text3bit1num8raw16nounit_v1_summary.json"
                ),
                remove_id="1c48f9aa",
                add_id="6b393b81",
                strategy="raw16_no_unit_lateral_refresh_from_reprobridge34",
                rationale="test rationale",
                source_bridge_label="reprobridge34 raw15 nounit",
                bridge_family_status="test status",
                remove_note_key="removed_row",
                add_note_key="added_row",
            ),
            recovery_hub.FollowupStep(
                step_name="reprobridge36",
                base_dataset_rel=(
                    "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
                    "stage25_o30best_proxybench30ao_reprobridge35_text3bit1num8raw16nounit_v1.csv"
                ),
                base_summary_rel=(
                    "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
                    "stage25_o30best_proxybench30ao_reprobridge35_text3bit1num8raw16nounit_v1_summary.json"
                ),
                output_dataset_rel=(
                    "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
                    "stage25_o30best_proxybench30ao_reprobridge36_text3bit1num8raw17nounit_v1.csv"
                ),
                output_summary_rel=(
                    "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
                    "stage25_o30best_proxybench30ao_reprobridge36_text3bit1num8raw17nounit_v1_summary.json"
                ),
                remove_id="27cec7a9",
                add_id="552e14d7",
                strategy="raw17_no_unit_lateral_refresh_from_reprobridge35",
                rationale="test rationale",
                source_bridge_label="reprobridge35 raw16 nounit",
                bridge_family_status="test status",
                remove_note_key="removed_row",
                add_note_key="added_row",
            ),
        )

        report = recovery_hub.build_status_report()
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.RUN_STATUS_ROOTS = original_run_status_roots
        recovery_hub.WAITERS31 = original_waiters31
        recovery_hub.WAITERS32 = original_waiters32
        recovery_hub.BEST_SELECTOR_SUMMARY = original_selector_summary
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert report["ready_followup_steps"] == ["reprobridge35"]
    assert report["blocked_followup_steps"] == ["reprobridge36"]
    assert report["materialized_followup_steps"] == []
    assert report["followup_steps"][0]["ready_to_materialize"] is True
    assert report["followup_steps"][0]["missing_inputs"] == []
    assert report["followup_steps"][0]["output_summary_excerpt"] is None
    assert report["followup_steps"][1]["ready_to_materialize"] is False
    assert report["followup_steps"][1]["missing_inputs"] == ["base_dataset", "base_summary"]
    assert report["followup_steps"][1]["output_summary_excerpt"] is None


def test_recovery_parse_args_accepts_new_followup_steps() -> None:
    args35 = recovery_hub.parse_args(["--materialize-followups", "--followup-step", "reprobridge35"])
    args36 = recovery_hub.parse_args(["--materialize-followups", "--followup-step", "reprobridge36"])

    assert args35.materialize_followups is True
    assert args35.followup_step == "reprobridge35"
    assert args36.followup_step == "reprobridge36"


def test_recovery_summarize_gate_state_marks_dead_local320_after_completion() -> None:
    gate_state = recovery_hub.summarize_gate_state(
        readme_local320_progress={
            "status": "completed",
            "accuracy": 0.7281,
        },
        proxy_progress={
            "status": "running",
            "rows_completed": 0,
        },
        suite_summary=None,
    )

    assert gate_state["gate_status"] == "below_local075"
    assert gate_state["dead_on_local320"] is True
    assert gate_state["proxy_started"] is True
    assert gate_state["phase"] == "proxy_v1_running"


def test_recovery_materialize_followups_writes_replaced_dataset_and_summary(tmp_path: Path) -> None:
    train_split_csv = tmp_path / "train_split_with_cot.csv"
    analysis_csv = tmp_path / "train_row_analysis_v1.csv"
    base_dataset = tmp_path / "base_dataset.csv"
    base_summary = tmp_path / "base_summary.json"
    output_dataset = tmp_path / "output_dataset.csv"
    output_summary = tmp_path / "output_summary.json"

    fieldnames = ["id", "type", "prompt", "answer", "generated_cot"]
    write_csv_rows(
        train_split_csv,
        fieldnames,
        [
            {
                "id": "row_old",
                "type": "Unit Conversion",
                "prompt": "old prompt",
                "answer": "1",
                "generated_cot": "old cot",
            },
            {
                "id": "row_new",
                "type": "Equation Transformation",
                "prompt": "new prompt",
                "answer": "2",
                "generated_cot": "new cot",
            },
            {
                "id": "row_keep",
                "type": "Bit Manipulation",
                "prompt": "keep prompt",
                "answer": "3",
                "generated_cot": "keep cot",
            },
        ],
    )
    write_csv_rows(
        base_dataset,
        fieldnames,
        [
            {
                "id": "row_old",
                "type": "Unit Conversion",
                "prompt": "old prompt",
                "answer": "1",
                "generated_cot": "old cot",
            },
            {
                "id": "row_keep",
                "type": "Bit Manipulation",
                "prompt": "keep prompt",
                "answer": "3",
                "generated_cot": "keep cot",
            },
        ],
    )
    base_summary.write_text(
        json.dumps({"notes": {"cot_sources": ["baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv"]}}),
        encoding="utf-8",
    )
    write_csv_rows(
        analysis_csv,
        [
            "id",
            "family",
            "subfamily",
            "template_subtype",
            "selection_tier",
            "hard_score",
            "answer_only_ready",
        ],
        [
            {
                "id": "row_old",
                "family": "unit",
                "subfamily": "old",
                "template_subtype": "ratio",
                "selection_tier": "bridge",
                "hard_score": "6.0",
                "answer_only_ready": "true",
            },
            {
                "id": "row_new",
                "family": "equation",
                "subfamily": "new",
                "template_subtype": "verified_trace_ready",
                "selection_tier": "bridge",
                "hard_score": "3.0",
                "answer_only_ready": "true",
            },
        ],
    )

    step = recovery_hub.FollowupStep(
        step_name="reprobridge33",
        base_dataset_rel="base_dataset.csv",
        base_summary_rel="base_summary.json",
        output_dataset_rel="output_dataset.csv",
        output_summary_rel="output_summary.json",
        remove_id="row_old",
        add_id="row_new",
        strategy="unit_to_equation",
        rationale="swap the remaining unit row for the next equation row",
        source_bridge_label="bridge32",
        bridge_family_status="Unit row removed for equation continuation.",
        remove_note_key="removed_unit_row",
        add_note_key="added_equation_row",
    )

    original_repo_root = recovery_hub.REPO_ROOT
    original_train_split_csv = recovery_hub.TRAIN_SPLIT_CSV
    original_analysis_csv = recovery_hub.ANALYSIS_CSV
    original_followup_steps = recovery_hub.FOLLOWUP_STEPS
    try:
        recovery_hub.REPO_ROOT = tmp_path
        recovery_hub.TRAIN_SPLIT_CSV = train_split_csv
        recovery_hub.ANALYSIS_CSV = analysis_csv
        recovery_hub.FOLLOWUP_STEPS = (step,)

        results = recovery_hub.materialize_followups(step_name="reprobridge33", dry_run=False)
    finally:
        recovery_hub.REPO_ROOT = original_repo_root
        recovery_hub.TRAIN_SPLIT_CSV = original_train_split_csv
        recovery_hub.ANALYSIS_CSV = original_analysis_csv
        recovery_hub.FOLLOWUP_STEPS = original_followup_steps

    assert results[0]["step_name"] == "reprobridge33"
    output_rows = list(csv.DictReader(output_dataset.open("r", encoding="utf-8", newline="")))
    assert [row["id"] for row in output_rows] == ["row_new", "row_keep"]

    summary = json.loads(output_summary.read_text(encoding="utf-8"))
    assert summary["removed_rows"] == ["row_old"]
    assert summary["added_rows"] == ["row_new"]
    assert summary["resulting_mix"]["Unit"] == 0
    assert summary["resulting_mix"]["Equation"] == 1
    assert summary["notes"]["remaining_unit_rows_include"] == []


def test_v3f_exportable_audit_summary_matches_corrected_lineage() -> None:
    summary = v3f_audit.build_summary()

    assert summary["summary_schema_version"] == 2
    assert summary["readme_contract_verified_from_readme_file"] is True
    assert summary["readme_contract"]["max_lora_rank"] == 32
    assert summary["readme_contract_state"]["matches_current_readme"] is True
    assert summary["phase0_readme_contract_state"]["matches_current_readme"] is True
    assert summary["proxy_readme_contract_state"]["matches_current_readme"] is True
    assert summary["specialized_readme_contract_state"]["matches_current_readme"] is True
    assert summary["stored_phase0_local320"]["correct"] == 249
    assert summary["corrected_phase0_local320"]["correct"] == 240
    assert summary["proxy_actual"]["correct"] == 133
    assert summary["specialized563"]["correct"] == 238
    assert summary["supported_not_structured_bucket"]["correct"] == 1
    assert summary["binary_structured_byte_not_formula_teacher"]["correct"] == 1
    assert summary["submission_compatibility"]["readme_submission_compatible"] is False
    assert "not claimed to be PEFT/vLLM submission-compatible" in summary["submission_compatibility"]["bundle_note"]


def test_v3f_exportable_audit_write_summary_emits_json_and_markdown(tmp_path: Path) -> None:
    summary_path = v3f_audit.write_summary(tmp_path)

    assert summary_path == tmp_path / "v3f_exportable_audit_summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    markdown = (tmp_path / "v3f_exportable_audit_summary.md").read_text(encoding="utf-8")

    assert payload["summary_schema_version"] == 2
    assert payload["readme_contract_verified_from_readme_file"] is True
    assert payload["proxy_readme_contract_state"]["matches_current_readme"] is True
    assert payload["corrected_phase0_local320"]["correct"] == 240
    assert payload["proxy_actual"]["accuracy"] == 0.665
    assert "supported_not_structured" in markdown
    assert "binary_structured_byte_not_formula" in markdown
    assert "summary_schema_version" in markdown
    assert "phase0_manifest_matches_current_readme" in markdown
    assert "verified_from_readme_file" in markdown


def test_v3f_exportable_audit_build_readme_contract_state_reports_missing_keys() -> None:
    state = v3f_audit.build_readme_contract_state(
        {
            "max_tokens": 7680,
            "top_p": 1.0,
            "temperature": 0.0,
            "max_num_seqs": 64,
            "max_model_len": 8192,
        },
        max_lora_rank_required=False,
    )

    assert state["matches_current_readme"] is False
    assert state["missing_keys"] == ["gpu_memory_utilization"]
    assert state["unexpected_keys"] == []


def test_v3f_exportable_audit_build_readme_contract_state_allows_optional_max_lora_rank() -> None:
    state = v3f_audit.build_readme_contract_state(
        dict(v3f_audit.README_CONTRACT),
        max_lora_rank_required=False,
    )

    assert state["matches_current_readme"] is True
    assert state["missing_keys"] == []
    assert state["unexpected_keys"] == []


def test_binary40_repro_summary_schema_tracks_readme_contract(tmp_path: Path) -> None:
    summary_path = binary40_repro.write_summary(tmp_path, "verify", {})
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    markdown = (tmp_path / "binary40_repro_summary.md").read_text(encoding="utf-8")

    assert_summary_contract_state_payload(payload)
    assert payload["readme_contract"] == binary40_repro.README_CONTRACT
    assert payload["peft_export_ready"] is True
    assert payload["validation_valid"] is True
    assert "summary_schema_version" in markdown
    assert "matches_current_readme" in markdown
    assert "verified_from_readme_file" in markdown
    assert "peft_export_ready" in markdown
    assert "validation_valid" in markdown
    assert "exportability_note" in markdown


def test_binary40_repro_build_readme_contract_state_reports_missing_keys() -> None:
    state = binary40_repro.build_readme_contract_state(
        {
            "max_lora_rank": 32,
            "max_tokens": 7680,
            "top_p": 1.0,
            "temperature": 0.0,
            "max_num_seqs": 64,
            "max_model_len": 8192,
        }
    )

    assert state["matches_current_readme"] is False
    assert state["missing_keys"] == ["gpu_memory_utilization"]
    assert state["unexpected_keys"] == []


def test_binary40_repro_load_readme_contract_from_readme_matches_constant() -> None:
    assert binary40_repro.load_readme_contract_from_readme() == binary40_repro.README_CONTRACT


def test_o30best_repro_summary_schema_tracks_readme_contract(tmp_path: Path) -> None:
    summary_path = o30best_repro.write_summary(tmp_path, "verify", {})
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    markdown = (tmp_path / "o30best_repro_summary.md").read_text(encoding="utf-8")

    assert_summary_contract_state_payload(payload)
    assert payload["readme_contract"] == o30best_repro.README_CONTRACT
    assert payload["peft_export_ready"] is True
    assert payload["validation_valid"] is True
    assert "summary_schema_version" in markdown
    assert "matches_current_readme" in markdown
    assert "verified_from_readme_file" in markdown
    assert "peft_export_ready" in markdown
    assert "validation_valid" in markdown
    assert "exportability_note" in markdown


def test_o30best_repro_build_readme_contract_state_reports_missing_keys() -> None:
    state = o30best_repro.build_readme_contract_state(
        {
            "max_lora_rank": 32,
            "max_tokens": 7680,
            "top_p": 1.0,
            "temperature": 0.0,
            "max_num_seqs": 64,
            "max_model_len": 8192,
        }
    )

    assert state["matches_current_readme"] is False
    assert state["missing_keys"] == ["gpu_memory_utilization"]
    assert state["unexpected_keys"] == []


def test_o30best_repro_load_readme_contract_from_readme_matches_constant() -> None:
    assert o30best_repro.load_readme_contract_from_readme() == o30best_repro.README_CONTRACT


def test_o30best_proxybench_repro_summary_schema_tracks_readme_contract(tmp_path: Path) -> None:
    summary_path = o30best_proxybench_repro.write_summary(tmp_path, "verify", {})
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    markdown = (tmp_path / "o30best_proxybench_repro_summary.md").read_text(encoding="utf-8")

    assert_summary_contract_state_payload(payload)
    assert payload["readme_contract"] == o30best_proxybench_repro.README_CONTRACT
    assert payload["peft_export_ready"] is True
    assert payload["validation_valid"] is True
    assert "summary_schema_version" in markdown
    assert "matches_current_readme" in markdown
    assert "verified_from_readme_file" in markdown
    assert "peft_export_ready" in markdown
    assert "validation_valid" in markdown
    assert "exportability_note" in markdown


def test_active_repro_wrappers_export_existing_summary_records_reproduced_exportability_signals(
    tmp_path: Path, monkeypatch
) -> None:
    cases = (
        ("binary40", binary40_repro, "binary40_repro_summary"),
        ("o30best", o30best_repro, "o30best_repro_summary"),
        ("o30best_proxybench", o30best_proxybench_repro, "o30best_proxybench_repro_summary"),
    )

    for case_name, module, summary_stem in cases:
        output_root = tmp_path / case_name
        audit_output_root = output_root / "submission_compat_audit"
        export_output_root = output_root / "submission_export"
        audit_output_root.mkdir(parents=True, exist_ok=True)
        export_output_root.mkdir(parents=True, exist_ok=True)
        submission_zip = export_output_root / "submission.zip"
        submission_zip.write_bytes(b"zip")
        (audit_output_root / "submission_compat_audit.json").write_text(
            json.dumps(
                {
                    "audit_status": "potentially_exportable_2d_only",
                    "peft_export_ready": True,
                }
            ),
            encoding="utf-8",
        )
        (export_output_root / "export_manifest.json").write_text(
            json.dumps(
                {
                    "zip_path": str(submission_zip),
                    "zip_size_bytes": 3,
                    "validation": {"valid": True},
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(module, "run_command", lambda _command, *, dry_run: None)

        exit_code = module.command_export_existing(
            SimpleNamespace(output_root=output_root, dry_run=False)
        )
        assert exit_code == 0

        summary_path = output_root / f"{summary_stem}.json"
        markdown_path = output_root / f"{summary_stem}.md"
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        markdown = markdown_path.read_text(encoding="utf-8")

        assert payload["reproduced_audit_status"] == "potentially_exportable_2d_only"
        assert payload["reproduced_peft_export_ready"] is True
        assert payload["reproduced_validation_valid"] is True
        assert "reproduced_audit_status" in markdown
        assert "reproduced_peft_export_ready" in markdown
        assert "reproduced_validation_valid" in markdown
        assert "exportability_note" in markdown


def test_o30best_proxybench_repro_build_readme_contract_state_reports_missing_keys() -> None:
    state = o30best_proxybench_repro.build_readme_contract_state(
        {
            "max_lora_rank": 32,
            "max_tokens": 7680,
            "top_p": 1.0,
            "temperature": 0.0,
            "max_num_seqs": 64,
            "max_model_len": 8192,
        }
    )

    assert state["matches_current_readme"] is False
    assert state["missing_keys"] == ["gpu_memory_utilization"]
    assert state["unexpected_keys"] == []


def test_o30best_proxybench_repro_load_readme_contract_from_readme_matches_constant() -> None:
    assert o30best_proxybench_repro.load_readme_contract_from_readme() == o30best_proxybench_repro.README_CONTRACT


def test_threshold_submission_summary_schema_tracks_readme_contract(tmp_path: Path) -> None:
    payload = threshold_submission.summarize_run(
        run_root=THRESHOLD_FRONTIER_RUN_ROOT,
        threshold_label="local-ge-0.70",
        min_local_accuracy=0.70,
        min_proxy_accuracy=0.65,
        expected_local_correct=235,
        expected_proxy_correct=131,
        expected_local_rows=320,
        expected_proxy_rows=200,
        require_existing_export=False,
    )
    summary_payload = threshold_submission.write_summary(tmp_path, "verify-run", payload)
    markdown = (tmp_path / "threshold_submission_summary.md").read_text(encoding="utf-8")

    assert_summary_contract_state_payload(summary_payload)
    assert summary_payload["readme_contract"] == threshold_submission.README_CONTRACT
    assert summary_payload["existing_peft_export_ready"] is True
    assert summary_payload["existing_validation_valid"] is True
    assert "existing_export_valid" not in summary_payload
    assert "summary_schema_version" in markdown
    assert "matches_current_readme" in markdown
    assert "verified_from_readme_file" in markdown
    assert "existing_peft_export_ready" in markdown
    assert "exportability_note" in markdown
    assert "- existing_export_valid:" not in markdown


def test_threshold_submission_export_submission_records_reproduced_peft_export_ready(
    tmp_path: Path, monkeypatch
) -> None:
    run_root = tmp_path / "run"
    (run_root / "adapter").mkdir(parents=True, exist_ok=True)
    (run_root / "shadow_model").mkdir(parents=True, exist_ok=True)
    output_root = tmp_path / "output"
    audit_output_root = output_root / "submission_compat_audit"
    export_output_root = output_root / "submission_export"
    audit_output_root.mkdir(parents=True, exist_ok=True)
    export_output_root.mkdir(parents=True, exist_ok=True)
    submission_zip = export_output_root / "submission.zip"
    submission_zip.write_bytes(b"zip")
    (audit_output_root / "submission_compat_audit.json").write_text(
        json.dumps(
            {
                "audit_status": "potentially_exportable_2d_only",
                "peft_export_ready": True,
            }
        ),
        encoding="utf-8",
    )
    (export_output_root / "export_manifest.json").write_text(
        json.dumps({"zip_path": str(submission_zip), "validation": {"valid": True}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(threshold_submission, "run_command", lambda _command, *, dry_run: None)

    payload = threshold_submission.export_submission(
        run_root=run_root,
        output_root=output_root,
        base_model_name_or_path=threshold_submission.DEFAULT_BASE_MODEL_NAME,
        dry_run=False,
    )

    assert payload["reproduced_audit_status"] == "potentially_exportable_2d_only"
    assert payload["reproduced_peft_export_ready"] is True
    assert payload["reproduced_validation_valid"] is True


def test_threshold_submission_build_readme_contract_state_reports_missing_keys() -> None:
    state = threshold_submission.build_readme_contract_state(
        {
            "max_lora_rank": 32,
            "max_tokens": 7680,
            "top_p": 1.0,
            "temperature": 0.0,
            "max_num_seqs": 64,
            "max_model_len": 8192,
        }
    )

    assert state["matches_current_readme"] is False
    assert state["missing_keys"] == ["gpu_memory_utilization"]
    assert state["unexpected_keys"] == []


def test_threshold_submission_load_readme_contract_from_readme_matches_constant() -> None:
    assert threshold_submission.load_readme_contract_from_readme() == threshold_submission.README_CONTRACT


def test_v3f_exportable_audit_parse_args_accepts_write_summary_output_root() -> None:
    args = v3f_audit.parse_args(["write-summary", "--output-root", "custom-output"])

    assert args.command == "write-summary"
    assert args.output_root == "custom-output"


def test_v3f_exportable_audit_load_readme_contract_from_readme_matches_constant() -> None:
    assert v3f_audit.load_readme_contract_from_readme(max_lora_rank_required=True) == v3f_audit.README_CONTRACT


def test_v3f_submission_line_summary_targets_supported_not_structured_gap() -> None:
    summary = v3f_submission.build_summary()
    markdown = v3f_submission.render_markdown_summary(summary)

    assert summary["summary_schema_version"] == 2
    assert summary["readme_contract_verified_from_readme_file"] is True
    assert summary["readme_contract"]["max_lora_rank"] == 32
    assert summary["readme_contract_state"]["matches_current_readme"] is True
    assert summary["v3f_anchors"]["corrected_phase0_local320"]["correct"] == 240
    assert summary["v3f_anchors"]["proxy_actual"]["correct"] == 133
    assert summary["v3f_anchors"]["supported_not_structured"]["correct"] == 1
    assert "supported_not_structured" in summary["proxy_v2_focus_buckets"]
    assert summary["proxy_v2_focus_buckets"][:3] == [
        "dominant_structured_safe",
        "dominant_structured_abstract",
        "supported_not_structured",
    ]
    assert "binary_structured_byte_not_formula" in summary["stage2_binary_solvers"]
    assert summary["stage1_config"]["trainable_lora_suffix_group"] == "broad-exportsafe"
    assert summary["stage2_config"]["trainable_lora_suffix_group"] == "attention"
    assert summary["stage2_config"]["lora_key_group"] == "stage-union-exportsafe"
    assert summary["stage2_config"]["num_epochs"] == 0.75
    assert summary["stage2_config"]["max_answer_only_ratio"] == 0.05
    assert summary["stage2_config"]["max_manual_audit_ratio"] == 0.0
    assert summary["stage2_config"]["manual_audit_template_subtypes"] == ["bit_other"]
    assert summary["stage2_candidate_gate_defaults"] == v3f_submission.DEFAULT_STAGE2_CANDIDATE_GATES
    assert summary["base_model_name_or_path"] == v3f_submission.BASE_MODEL_NAME
    assert summary["readme_contract"]["gpu_memory_utilization"] == 0.85
    assert summary["stage2_export_defaults"]["adapter_dir"].endswith(f"{v3f_submission.STAGE2_RUN_NAME}/adapter")
    assert summary["stage2_export_defaults"]["reference_model_root"].endswith(
        f"{v3f_submission.STAGE2_RUN_NAME}/shadow_model"
    )
    assert "package-stage2-matrix-best-submission" in summary["stage2_profile_matrix"]["matrix_best_submission_command"]
    assert "--all-profiles" in summary["stage2_profile_matrix"]["matrix_all_profiles_command"]
    assert "write-stage2-candidate-audit" in summary["stage2_profile_matrix"]["matrix_candidate_audit_command"]
    assert "--all-profiles" in summary["stage2_profile_matrix"]["matrix_candidate_audit_all_profiles_command"]
    assert "--all-profiles" in summary["stage2_profile_matrix"]["matrix_best_submission_all_profiles_command"]
    assert summary["stage2_profile_matrix"]["default_stage2_profiles"] == [
        "attention-short-default",
        "attention-short-noanswer",
        "attention-short-manual",
    ]
    assert "stage2_candidate_audit_command" in markdown
    assert "stage2_candidate_audit_all_profiles_command" in markdown
    assert "stage2_matrix_all_profiles_command" in markdown
    assert "stage2_matrix_best_submission_all_profiles_command" in markdown
    assert "summary_schema_version" in markdown
    assert "verified_from_readme_file" in markdown
    assert summary["historical_attention_only_warning"]["readme_local320"]["correct"] == 218
    assert summary["historical_attention_only_warning"]["leaderboard_proxy_v2"]["correct"] == 33
    assert summary["historical_attention_only_warning"]["binary_bias_specialized_set"]["correct"] == 158
    assert summary["prompt_router_v6_blueprint"]["local320"]["correct"] == 293
    assert summary["prompt_router_v6_blueprint"]["binary_gain_breakdown"]["manual_audit_priority"] == 8
    assert summary["prompt_router_v6_blueprint"]["submission_compatible"] is False
    assert summary["single_adapter_transfer_priors"]["primary_failure_mode"] == "format_ok_content_wrong"
    assert summary["single_adapter_transfer_priors"]["bit_other_answer_only_keep_overlap_rows"] == 52
    assert summary["single_adapter_transfer_priors"]["portable_new_signal_centers_on"] == [
        "bit_other manual_audit_priority",
        "bit_other verified_trace_ready",
    ]
    assert any(
        "format_ok_content_wrong" in item for item in summary["next_repair_priorities"]
    )
    assert any(
        "manual_audit_priority" in item and "verified_trace_ready" in item
        for item in summary["next_repair_priorities"]
    )


def test_v3f_submission_line_build_readme_contract_state_reports_missing_keys() -> None:
    state = v3f_submission.build_readme_contract_state(
        {
            "max_lora_rank": 32,
            "max_tokens": 7680,
            "top_p": 1.0,
            "temperature": 0.0,
            "max_num_seqs": 64,
            "max_model_len": 8192,
        }
    )

    assert state["matches_current_readme"] is False
    assert state["missing_keys"] == ["gpu_memory_utilization"]
    assert state["unexpected_keys"] == []


def test_v3f_submission_line_load_readme_contract_from_readme_matches_constant() -> None:
    assert v3f_submission.load_readme_contract_from_readme() == v3f_submission.README_CONTRACT


def test_summary_wrappers_load_readme_contract_from_readme_rejects_missing_value(tmp_path: Path) -> None:
    for module, loader in (
        (binary40_repro, lambda: binary40_repro.load_readme_contract_from_readme()),
        (o30best_repro, lambda: o30best_repro.load_readme_contract_from_readme()),
        (o30best_proxybench_repro, lambda: o30best_proxybench_repro.load_readme_contract_from_readme()),
        (threshold_submission, lambda: threshold_submission.load_readme_contract_from_readme()),
        (v3f_audit, lambda: v3f_audit.load_readme_contract_from_readme(max_lora_rank_required=True)),
        (v3f_submission, lambda: v3f_submission.load_readme_contract_from_readme()),
    ):
        assert_module_rejects_malformed_readme(module, loader, tmp_path)


def test_summary_wrappers_load_readme_contract_from_readme_rejects_missing_row(tmp_path: Path) -> None:
    for module, loader in (
        (binary40_repro, lambda: binary40_repro.load_readme_contract_from_readme()),
        (o30best_repro, lambda: o30best_repro.load_readme_contract_from_readme()),
        (o30best_proxybench_repro, lambda: o30best_proxybench_repro.load_readme_contract_from_readme()),
        (threshold_submission, lambda: threshold_submission.load_readme_contract_from_readme()),
        (v3f_audit, lambda: v3f_audit.load_readme_contract_from_readme(max_lora_rank_required=True)),
        (v3f_submission, lambda: v3f_submission.load_readme_contract_from_readme()),
    ):
        assert_module_rejects_missing_readme_row(module, loader, tmp_path)


def test_v3f_submission_stage2_type_samples_reflect_summary_counts(tmp_path: Path) -> None:
    summary_json = tmp_path / "stage2_summary.json"
    summary_json.write_text(
        json.dumps({"type_counts": {"Bit Manipulation": 42, "Equation Transformation": 9}}),
        encoding="utf-8",
    )

    assert v3f_submission.stage2_type_samples(summary_json) == [
        "Text Encryption=0",
        "Bit Manipulation=42",
        "Gravitational Constant=0",
        "Unit Conversion=0",
        "Numeral Conversion=0",
        "Equation Transformation=9",
    ]


def test_v3f_submission_resolve_stage2_type_samples_prefers_explicit_override(tmp_path: Path) -> None:
    assert v3f_submission.resolve_stage2_type_samples(
        explicit_type_samples=["Bit Manipulation=34", "Equation Transformation=8"],
        dataset_summary_json=tmp_path / "missing.json",
    ) == ["Bit Manipulation=34", "Equation Transformation=8"]


def test_v3f_submission_build_stage2_artifacts_dry_run_wires_proxy_focus_and_solvers(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    result = v3f_submission.command_build_stage2_artifacts(
        SimpleNamespace(
            output_csv=tmp_path / "stage2.csv",
            summary_json=tmp_path / "stage2_summary.json",
            proxy_v2_csv=tmp_path / "proxy_v2.csv",
            proxy_v2_summary_json=tmp_path / "proxy_v2_summary.json",
            max_symbol_rows=9,
            max_answer_only_ratio=0.0,
            max_manual_audit_ratio=0.1,
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 2
    proxy_call, corrective_call = calls
    assert proxy_call[1] is True
    assert corrective_call[1] is True
    assert "build-leaderboard-proxy-v2" in proxy_call[0]
    assert "supported_not_structured" in proxy_call[0]
    assert "build-corrective-stage2-csv" in corrective_call[0]
    assert "binary_structured_byte_not_formula" in corrective_call[0]
    assert "--max-manual-audit-ratio" in corrective_call[0]
    assert corrective_call[0][corrective_call[0].index("--max-manual-audit-ratio") + 1] == "0.1"

    summary = json.loads(
        (tmp_path / "summary" / "v3f_submission_line_summary.json").read_text(encoding="utf-8")
    )
    assert summary["manual_audit_template_subtypes"] == ["bit_other"]


def test_v3f_submission_launch_stage2_dry_run_uses_attention_and_type_samples(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    dataset_summary_json = tmp_path / "stage2_dataset_summary.json"
    dataset_summary_json.write_text(
        json.dumps({"type_counts": {"Bit Manipulation": 42, "Equation Transformation": 9}}),
        encoding="utf-8",
    )

    result = v3f_submission.command_launch_stage2(
        SimpleNamespace(
            source_run_root=tmp_path / "stage1_source",
            train_csv=tmp_path / "stage2_dataset.csv",
            dataset_summary_json=dataset_summary_json,
            output_root=tmp_path / "outputs",
            run_name="stage2_attention_test",
            learning_rate=2e-5,
            num_epochs=3.6,
            max_seq_length=1536,
            valid_shadow_rows=1,
            lora_key_group="stage-union-exportsafe",
            trainable_lora_suffix_group="attention",
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 1
    command, dry_run = calls[0]
    assert dry_run is True
    assert "resume-train-from-run" in command
    assert command[command.index("--trainable-lora-suffix-group") + 1] == "attention"
    assert "Bit Manipulation=42" in command
    assert "Equation Transformation=9" in command
    assert "Text Encryption=0" in command

    summary = json.loads(
        (tmp_path / "summary" / "v3f_submission_line_summary.json").read_text(encoding="utf-8")
    )
    assert summary["stage2_type_samples"] == [
        "Text Encryption=0",
        "Bit Manipulation=42",
        "Gravitational Constant=0",
        "Unit Conversion=0",
        "Numeral Conversion=0",
        "Equation Transformation=9",
    ]


def test_v3f_submission_launch_stage2_linked_dry_run_uses_waiter_command(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    dataset_summary_json = tmp_path / "stage2_dataset_summary.json"
    dataset_summary_json.write_text(
        json.dumps({"type_counts": {"Bit Manipulation": 34, "Equation Transformation": 8}}),
        encoding="utf-8",
    )

    result = v3f_submission.command_launch_stage2_linked(
        SimpleNamespace(
            source_run_root=tmp_path / "stage1_run",
            train_csv=tmp_path / "stage2_dataset.csv",
            dataset_summary_json=dataset_summary_json,
            output_root=tmp_path / "outputs",
            run_name="stage2_linked_test",
            learning_rate=2e-5,
            num_epochs=3.6,
            max_seq_length=1536,
            valid_shadow_rows=1,
            lora_key_group="stage-union-exportsafe",
            trainable_lora_suffix_group="attention",
            poll_seconds=60.0,
            timeout_seconds=0.0,
            min_free_percent=None,
            min_free_gb=150.0,
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 1
    command, dry_run = calls[0]
    assert dry_run is True
    assert "wait-train-from-run" in command
    assert command[command.index("--trainable-lora-suffix-group") + 1] == "attention"
    assert command[command.index("--min-free-gb") + 1] == "150.0"
    assert "Bit Manipulation=34" in command
    assert "Equation Transformation=8" in command

    summary = json.loads(
        (tmp_path / "summary" / "v3f_submission_line_summary.json").read_text(encoding="utf-8")
    )
    assert summary["linked_stage2_source_run_root"] == str((tmp_path / "stage1_run").resolve())
    assert summary["min_free_gb"] == 150.0


def test_v3f_submission_run_full_pipeline_dry_run_wires_all_steps(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    result = v3f_submission.command_run_full_pipeline(
        SimpleNamespace(
            output_root=tmp_path / "outputs",
            stage1_source_run_root=tmp_path / "source_fullrun",
            stage1_train_csv=tmp_path / "stage1_dataset.csv",
            stage1_run_name="stage1_full_test",
            stage1_learning_rate=1e-4,
            stage1_num_epochs=2.0,
            stage1_max_seq_length=4096,
            stage1_valid_shadow_rows=1,
            stage1_lora_key_group="stage-union-exportsafe",
            stage1_trainable_lora_suffix_group="broad-exportsafe",
            proxy_v2_csv=tmp_path / "proxy_v2.csv",
            proxy_v2_summary_json=tmp_path / "proxy_v2_summary.json",
            stage2_dataset_csv=tmp_path / "stage2_dataset.csv",
            stage2_dataset_summary_json=tmp_path / "stage2_dataset_summary.json",
            stage2_max_symbol_rows=9,
            stage2_max_answer_only_ratio=0.0,
            stage2_max_manual_audit_ratio=0.1,
            stage2_run_name="stage2_full_test",
            stage2_learning_rate=2e-5,
            stage2_num_epochs=3.6,
            stage2_max_seq_length=1536,
            stage2_valid_shadow_rows=1,
            stage2_lora_key_group="stage-union-exportsafe",
            stage2_trainable_lora_suffix_group="attention",
            stage2_poll_seconds=60.0,
            stage2_timeout_seconds=0.0,
            stage2_min_free_percent=None,
            stage2_min_free_gb=150.0,
            type_sample=[
                "Text Encryption=0",
                "Bit Manipulation=34",
                "Gravitational Constant=0",
                "Unit Conversion=0",
                "Numeral Conversion=0",
                "Equation Transformation=8",
            ],
            specialized_csv=tmp_path / "specialized.csv",
            label="full pipeline dry run",
            postprocess_poll_seconds=60,
            results_md=tmp_path / "results.md",
            summary_output_root=tmp_path / "summary",
            min_local320_accuracy=215 / 320,
            min_general_stable_accuracy=0.96,
            min_proxy_v2_accuracy=0.5,
            min_specialized_accuracy=0.42,
            publish_commit_message="Record v3f submission line results",
            dry_run=True,
            run_publish_results_md=False,
            run_package_best_submission=False,
        )
    )

    assert result == 0
    assert len(calls) == 5
    assert "build-leaderboard-proxy-v2" in calls[0][0]
    assert "build-corrective-stage2-csv" in calls[1][0]
    assert "--max-manual-audit-ratio" in calls[1][0]
    assert "resume-train-from-run" in calls[2][0]
    assert "wait-train-from-run" in calls[3][0]
    assert "postprocess-run" in calls[4][0]
    assert "Bit Manipulation=34" in calls[3][0]
    assert "Equation Transformation=8" in calls[3][0]
    assert calls[4][0][calls[4][0].index("--max-tokens") + 1] == "7680"
    assert calls[4][0][calls[4][0].index("--max-num-seqs") + 1] == "64"
    assert calls[4][0][calls[4][0].index("--gpu-memory-utilization") + 1] == "0.85"
    assert calls[4][0][calls[4][0].index("--max-model-len") + 1] == "8192"
    assert "--eval-enable-thinking" in calls[4][0]

    summary = json.loads(
        (tmp_path / "summary" / "v3f_submission_line_summary.json").read_text(encoding="utf-8")
    )
    assert summary["mode"] == "run-full-pipeline"
    assert summary["full_pipeline_stage1_run_root"] == str((tmp_path / "outputs" / "stage1_full_test").resolve())
    assert summary["full_pipeline_stage2_run_root"] == str((tmp_path / "outputs" / "stage2_full_test").resolve())
    assert summary["stage2_type_samples"][1] == "Bit Manipulation=34"
    assert summary["stage2_trainable_lora_suffix_group"] == "attention"
    assert summary["stage2_max_manual_audit_ratio"] == 0.1
    assert summary["stage2_manual_audit_template_subtypes"] == ["bit_other"]


def test_v3f_submission_parse_args_accepts_full_pipeline_type_samples() -> None:
    args = v3f_submission.parse_args(
        ["run-full-pipeline", "--dry-run", "--type-sample", "Bit Manipulation=34", "--type-sample", "Equation Transformation=8"]
    )

    assert args.command == "run-full-pipeline"
    assert args.dry_run is True
    assert args.type_sample == ["Bit Manipulation=34", "Equation Transformation=8"]


def test_v3f_submission_parse_args_accepts_manual_audit_ratios() -> None:
    args = v3f_submission.parse_args(
        [
            "run-full-pipeline",
            "--stage2-max-manual-audit-ratio",
            "0.1",
            "--dry-run",
        ]
    )

    assert args.command == "run-full-pipeline"
    assert args.stage2_max_manual_audit_ratio == 0.1
    assert args.dry_run is True


def test_v3f_submission_parse_args_accepts_stage2_group_overrides() -> None:
    args = v3f_submission.parse_args(
        [
            "run-full-pipeline",
            "--stage2-lora-key-group",
            "stage-union",
            "--stage2-trainable-lora-suffix-group",
            "stage-union-exportsafe",
        ]
    )

    assert args.stage2_lora_key_group == "stage-union"
    assert args.stage2_trainable_lora_suffix_group == "stage-union-exportsafe"


def test_v3f_submission_parse_args_accepts_build_stage2_manual_ratio() -> None:
    args = v3f_submission.parse_args(
        [
            "build-stage2-artifacts",
            "--max-manual-audit-ratio",
            "0.1",
            "--dry-run",
        ]
    )

    assert args.command == "build-stage2-artifacts"
    assert args.max_manual_audit_ratio == 0.1
    assert args.dry_run is True


def test_v3f_submission_parse_args_accepts_write_stage2_candidate_audit_all_profiles() -> None:
    args = v3f_submission.parse_args(
        [
            "write-stage2-candidate-audit",
            "--all-profiles",
            "--min-proxy-v2-accuracy",
            "0.55",
        ]
    )

    assert args.command == "write-stage2-candidate-audit"
    assert args.all_profiles is True
    assert args.min_proxy_v2_accuracy == 0.55


def test_v3f_submission_write_stage2_matrix_emits_profiles(tmp_path: Path) -> None:
    result = v3f_submission.command_write_stage2_matrix(SimpleNamespace(output_root=tmp_path))

    assert result == 0
    payload = json.loads((tmp_path / "v3f_stage2_profile_matrix.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "v3f_stage2_profile_matrix.md").read_text(encoding="utf-8")

    profile_names = [item["profile_name"] for item in payload["stage2_profiles"]]
    assert payload["default_stage2_profiles"] == [
        "attention-short-default",
        "attention-short-noanswer",
        "attention-short-manual",
    ]
    assert payload["stage2_candidate_gate_defaults"] == v3f_submission.DEFAULT_STAGE2_CANDIDATE_GATES
    assert "attention-short-default" in profile_names
    assert "attention-short-noanswer" in profile_names
    assert "attention-short-manual" in profile_names
    assert "union-short-exploratory" in profile_names
    assert "attention-vo-historical" in profile_names
    expected_prefix = " ".join(
        shlex.quote(part) for part in ["uv", "run", "python", str(v3f_submission.SELF_PATH)]
    )
    assert payload["stage2_profiles"][0]["artifact_build_command"].startswith(expected_prefix)
    assert payload["stage2_profiles"][0]["stage1_launch_command"].startswith(expected_prefix)
    assert payload["stage2_profiles"][0]["stage2_linked_command"].startswith(expected_prefix)
    assert payload["stage2_profiles"][0]["postprocess_command"].startswith(expected_prefix)
    assert payload["stage2_profiles"][0]["export_command"].startswith(expected_prefix)
    assert f"- stage2_matrix_command: `{expected_prefix} launch-stage2-matrix --dry-run`" in markdown
    assert f"- stage2_matrix_all_profiles_command: `{expected_prefix} launch-stage2-matrix --all-profiles --dry-run`" in markdown
    assert (
        f"- stage2_export_command: `{expected_prefix} export-stage2-submission --run-root "
        f"baseline_mlx/outputs/{payload['stage2_run_name']}`"
    ) in markdown
    assert (
        f"- stage2_matrix_best_submission_command: `{expected_prefix} "
        "package-stage2-matrix-best-submission --dry-run`"
    ) in markdown
    assert (
        f"- stage2_matrix_best_submission_all_profiles_command: `{expected_prefix} "
        "package-stage2-matrix-best-submission --all-profiles --dry-run`"
    ) in markdown
    assert "build-stage2-artifacts" in payload["stage2_profiles"][0]["artifact_build_command"]
    assert "launch-stage1" in payload["stage2_profiles"][0]["stage1_launch_command"]
    assert "launch-stage2-linked" in payload["stage2_profiles"][0]["stage2_linked_command"]
    assert "postprocess-stage2" in payload["stage2_profiles"][0]["postprocess_command"]
    assert "--gpu-memory-utilization" in payload["stage2_profiles"][0]["postprocess_command"]
    assert "export-stage2-submission" in payload["stage2_profiles"][0]["export_command"]
    noanswer_profile = next(
        item for item in payload["stage2_profiles"] if item["profile_name"] == "attention-short-noanswer"
    )
    assert noanswer_profile["stage2_max_answer_only_ratio"] == 0.0
    assert "--max-answer-only-ratio 0.0" in noanswer_profile["artifact_build_command"]
    manual_profile = next(
        item for item in payload["stage2_profiles"] if item["profile_name"] == "attention-short-manual"
    )
    assert manual_profile["stage2_max_manual_audit_ratio"] == 0.1
    assert manual_profile["stage2_manual_audit_template_subtypes"] == ["bit_other"]
    assert "bit_other manual-audit helper slice" in manual_profile["description"]
    assert "--max-manual-audit-ratio 0.1" in manual_profile["artifact_build_command"]
    assert payload["matrix_all_profiles_command"].startswith(expected_prefix)
    assert "write-stage2-candidate-audit" in payload["matrix_candidate_audit_command"]
    assert payload["matrix_candidate_audit_command"].startswith(expected_prefix)
    assert "--all-profiles" in payload["matrix_candidate_audit_all_profiles_command"]
    assert payload["matrix_candidate_audit_all_profiles_command"].startswith(expected_prefix)
    assert "package-stage2-matrix-best-submission" in payload["matrix_best_submission_command"]
    assert payload["matrix_best_submission_command"].startswith(expected_prefix)
    assert "--all-profiles" in payload["matrix_all_profiles_command"]
    assert "--all-profiles" in payload["matrix_best_submission_all_profiles_command"]
    assert payload["matrix_best_submission_all_profiles_command"].startswith(expected_prefix)
    assert "matrix_candidate_audit_command" in markdown
    assert "matrix_candidate_audit_all_profiles_command" in markdown
    assert "v3f stage2 profile matrix" in markdown.lower()


def test_v3f_submission_select_stage2_profiles_defaults_include_manual_lane() -> None:
    profiles = v3f_submission.select_stage2_profiles()

    assert [profile["profile_name"] for profile in profiles] == [
        "attention-short-default",
        "attention-short-noanswer",
        "attention-short-manual",
    ]


def test_v3f_submission_select_stage2_profiles_rejects_profile_and_all_profiles() -> None:
    try:
        v3f_submission.select_stage2_profiles(["attention-short-default"], all_profiles=True)
    except SystemExit as exc:
        assert "either explicit --profile values or --all-profiles" in str(exc)
    else:
        raise AssertionError("Expected mixed Stage2 profile selection to fail")


def test_v3f_submission_select_stage2_profiles_all_profiles_returns_inventory() -> None:
    profiles = v3f_submission.select_stage2_profiles(all_profiles=True)

    assert [profile["profile_name"] for profile in profiles] == [
        "attention-short-default",
        "attention-short-noanswer",
        "attention-short-manual",
        "attention-short-lowlr",
        "union-short-exploratory",
        "attention-vo-historical",
    ]


def test_v3f_submission_candidate_artifact_state_uses_export_relpath_sibling_zip(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    custom_zip = run_root / "custom_export" / "submission.zip"
    custom_zip.parent.mkdir(parents=True, exist_ok=True)
    custom_zip.write_text("zip-placeholder", encoding="utf-8")

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=Path("custom_export/export_manifest.json"),
    )

    assert state["submission_zip_exists"] is True
    assert state["submission_zip_valid"] is False
    assert state["export_zip_path"] == str(custom_zip.resolve())
    assert any("export_manifest.json is missing" in reason for reason in state["export_manifest_blocked_reasons"])
    assert any("valid ZIP archive" in reason for reason in state["submission_zip_blocked_reasons"])
    assert "export_manifest" in state["missing_artifacts"]


def test_v3f_submission_inspect_submission_zip_reports_missing_file(tmp_path: Path) -> None:
    state = v3f_submission.inspect_submission_zip(tmp_path / "missing.zip")

    assert state["submission_zip_valid"] is False
    assert state["submission_zip_required_files_present"] is False
    assert state["submission_adapter_config_present"] is False
    assert state["submission_adapter_model_size_bytes"] is None
    assert state["submission_adapter_model_nonempty"] is False
    assert state["submission_rank_within_readme_limit"] is False
    assert state["submission_zip_blocked_reasons"] == ["submission.zip is missing."]


def test_v3f_submission_inspect_submission_zip_enforces_readme_rank(tmp_path: Path) -> None:
    zip_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 64,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")

    state = v3f_submission.inspect_submission_zip(zip_path)

    assert state["submission_zip_valid"] is False
    assert state["submission_adapter_config_present"] is True
    assert state["submission_adapter_config_valid"] is True
    assert state["submission_adapter_peft_type"] == "LORA"
    assert state["submission_adapter_peft_type_matches_expected"] is True
    assert state["submission_adapter_base_model_name_or_path"] == v3f_submission.BASE_MODEL_NAME
    assert state["submission_adapter_base_model_matches_expected"] is True
    assert state["submission_adapter_task_type"] == "CAUSAL_LM"
    assert state["submission_adapter_task_type_matches_expected"] is True
    assert state["submission_adapter_inference_mode"] is True
    assert state["submission_adapter_inference_mode_matches_expected"] is True
    assert state["submission_adapter_target_modules"] == ["out_proj"]
    assert state["submission_adapter_target_modules_count"] == 1
    assert state["submission_adapter_target_modules_nonempty"] is True
    assert state["submission_adapter_model_size_bytes"] == len("tensor-bytes")
    assert state["submission_adapter_model_nonempty"] is True
    assert state["submission_adapter_rank"] == 64
    assert state["submission_rank_within_readme_limit"] is False
    assert any("max_lora_rank" in reason for reason in state["submission_zip_blocked_reasons"])


def test_v3f_submission_inspect_submission_zip_requires_expected_base_model(tmp_path: Path) -> None:
    zip_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": "wrong/model",
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")

    state = v3f_submission.inspect_submission_zip(zip_path)

    assert state["submission_zip_valid"] is False
    assert state["submission_adapter_config_valid"] is True
    assert state["submission_adapter_rank"] == 16
    assert state["submission_rank_within_readme_limit"] is True
    assert state["submission_adapter_base_model_name_or_path"] == "wrong/model"
    assert state["submission_adapter_base_model_matches_expected"] is False
    assert state["submission_adapter_target_modules"] == ["out_proj"]
    assert state["submission_adapter_target_modules_nonempty"] is True
    assert state["submission_adapter_model_size_bytes"] == len("tensor-bytes")
    assert state["submission_adapter_model_nonempty"] is True
    assert any("base_model_name_or_path" in reason for reason in state["submission_zip_blocked_reasons"])


def test_v3f_submission_inspect_submission_zip_requires_nonempty_adapter_weights(tmp_path: Path) -> None:
    zip_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "")

    state = v3f_submission.inspect_submission_zip(zip_path)

    assert state["submission_zip_valid"] is False
    assert state["submission_adapter_model_size_bytes"] == 0
    assert state["submission_adapter_model_nonempty"] is False
    assert any("adapter_model.safetensors" in reason for reason in state["submission_zip_blocked_reasons"])


def test_v3f_submission_inspect_submission_zip_requires_lora_peft_contract(tmp_path: Path) -> None:
    zip_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "IA3",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "SEQ_CLS",
                    "inference_mode": False,
                    "target_modules": [],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")

    state = v3f_submission.inspect_submission_zip(zip_path)

    assert state["submission_zip_valid"] is False
    assert state["submission_adapter_peft_type"] == "IA3"
    assert state["submission_adapter_peft_type_matches_expected"] is False
    assert state["submission_adapter_task_type"] == "SEQ_CLS"
    assert state["submission_adapter_task_type_matches_expected"] is False
    assert state["submission_adapter_inference_mode"] is False
    assert state["submission_adapter_inference_mode_matches_expected"] is False
    assert state["submission_adapter_target_modules"] == []
    assert state["submission_adapter_target_modules_count"] == 0
    assert state["submission_adapter_target_modules_nonempty"] is False
    assert any("peft_type" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("task_type" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("inference_mode" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("target_modules" in reason for reason in state["submission_zip_blocked_reasons"])


def test_v3f_submission_inspect_submission_zip_rejects_extra_safetensors_payloads(tmp_path: Path) -> None:
    zip_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")
        archive.writestr("adapters.safetensors", "unexpected-second-adapter")

    state = v3f_submission.inspect_submission_zip(zip_path)

    assert state["submission_zip_valid"] is False
    assert state["submission_adapter_config_valid"] is True
    assert state["submission_adapter_model_nonempty"] is True
    assert state["submission_rank_within_readme_limit"] is True
    assert any("extra safetensors payload" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("adapters.safetensors" in reason for reason in state["submission_zip_blocked_reasons"])


def test_v3f_submission_inspect_submission_zip_rejects_duplicate_or_unsafe_member_paths(tmp_path: Path) -> None:
    zip_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")
        archive.writestr("nested/adapter_config.json", "{}")
        archive.writestr("../rogue_adapter.safetensors", "rogue")

    state = v3f_submission.inspect_submission_zip(zip_path)

    assert state["submission_zip_valid"] is False
    assert state["submission_adapter_config_valid"] is True
    assert state["submission_adapter_model_nonempty"] is True
    assert any("unsafe member path" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("duplicate adapter_config.json path" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("../rogue_adapter.safetensors" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("nested/adapter_config.json" in reason for reason in state["submission_zip_blocked_reasons"])


def test_v3f_submission_inspect_submission_zip_rejects_duplicate_required_member_entries(tmp_path: Path) -> None:
    zip_path = tmp_path / "submission.zip"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "adapter_config.json",
                json.dumps(
                    {
                        "peft_type": "LORA",
                        "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                        "task_type": "CAUSAL_LM",
                        "inference_mode": True,
                        "target_modules": ["out_proj"],
                        "r": 16,
                    }
                ),
            )
            archive.writestr(
                "adapter_config.json",
                json.dumps(
                    {
                        "peft_type": "LORA",
                        "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                        "task_type": "CAUSAL_LM",
                        "inference_mode": True,
                        "target_modules": ["out_proj"],
                        "r": 16,
                    }
                ),
            )
            archive.writestr("adapter_model.safetensors", "tensor-bytes")

    state = v3f_submission.inspect_submission_zip(zip_path)

    assert state["submission_zip_valid"] is False
    assert state["submission_adapter_config_valid"] is True
    assert state["submission_adapter_model_nonempty"] is True
    assert any("duplicate required member entries" in reason for reason in state["submission_zip_blocked_reasons"])
    assert any("adapter_config.json x2" in reason for reason in state["submission_zip_blocked_reasons"])


def test_v3f_submission_inspect_recorded_eval_assumptions_surfaces_readme_drift(tmp_path: Path) -> None:
    recorded_run_result = tmp_path / "recorded_run_result.json"
    recorded_run_result.write_text(
        json.dumps(
            {
                "readme_eval_assumptions": {
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "max_tokens": 7680,
                    "max_num_seqs": 8,
                    "max_model_len": 8192,
                    "eval_enable_thinking": True,
                }
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.inspect_recorded_eval_assumptions(recorded_run_result)

    assert state["recorded_eval_assumptions_present"] is True
    assert state["recorded_eval_assumptions"]["max_num_seqs"] == 8
    assert state["recorded_eval_contract_matches_readme"] is False
    assert any("max_num_seqs" in reason for reason in state["recorded_eval_contract_mismatches"])


def _write_minimal_valid_run_metadata(run_root: Path, *, train_csv: Path | None = None) -> None:
    resolved_train_csv = (train_csv or (run_root / "train.csv")).resolve()
    (run_root / "prepare_manifest.json").parent.mkdir(parents=True, exist_ok=True)
    (run_root / "prepare_manifest.json").write_text(
        json.dumps(
            {
                "train_csv": str(resolved_train_csv),
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                "readme_contract": dict(v3f_submission.README_CONTRACT),
                "training": {
                    "lora_rank": 16,
                    "lora_keys": ["mixer.out_proj"],
                    "trainable_lora_suffixes": ["mixer.out_proj"],
                },
            }
        ),
        encoding="utf-8",
    )
    (run_root / "training_result.json").write_text(
        json.dumps(
            {
                "adapter_files": [
                    {"name": "adapter_config.json", "size_bytes": 128},
                    {"name": "adapters.safetensors", "size_bytes": 1024},
                ],
                "latest_train_report": {
                    "iteration": 10,
                    "optimizer_step": 2,
                },
            }
        ),
        encoding="utf-8",
    )


def test_v3f_submission_inspect_prepare_manifest_artifact_requires_readme_contract(tmp_path: Path) -> None:
    prepare_manifest = tmp_path / "prepare_manifest.json"
    prepare_manifest.write_text(
        json.dumps(
            {
                "train_csv": "",
                "base_model_name_or_path": "wrong/model",
                "readme_contract": {"max_lora_rank": 64},
                "training": {
                    "lora_rank": 64,
                    "lora_keys": [],
                    "trainable_lora_suffixes": [],
                },
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.inspect_prepare_manifest_artifact(prepare_manifest)

    assert state["prepare_manifest_valid"] is False
    assert state["prepare_manifest_base_model_matches_expected"] is False
    assert state["prepare_manifest_train_csv"] == ""
    assert state["prepare_manifest_training_lora_rank"] == 64
    assert state["prepare_manifest_training_lora_rank_within_readme_limit"] is False
    assert state["prepare_manifest_training_lora_keys_nonempty"] is False
    assert state["prepare_manifest_training_trainable_suffixes_nonempty"] is False
    assert state["prepare_manifest_readme_contract_matches_expected"] is False
    assert any("base_model_name_or_path" in reason for reason in state["prepare_manifest_blocked_reasons"])
    assert any("train_csv is missing" in reason for reason in state["prepare_manifest_blocked_reasons"])
    assert any("training.lora_rank 64 exceeds" in reason for reason in state["prepare_manifest_blocked_reasons"])
    assert any("training.lora_keys is missing or empty" in reason for reason in state["prepare_manifest_blocked_reasons"])
    assert any(
        "training.trainable_lora_suffixes is missing or empty" in reason
        for reason in state["prepare_manifest_blocked_reasons"]
    )
    assert any("readme_contract['max_tokens']" in reason for reason in state["prepare_manifest_blocked_reasons"])


def test_v3f_submission_inspect_prepare_manifest_artifact_requires_expected_train_csv(tmp_path: Path) -> None:
    prepare_manifest = tmp_path / "prepare_manifest.json"
    wrong_train_csv = tmp_path / "wrong.csv"
    expected_train_csv = tmp_path / "expected.csv"
    prepare_manifest.write_text(
        json.dumps(
            {
                "train_csv": str(wrong_train_csv),
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                "readme_contract": dict(v3f_submission.README_CONTRACT),
                "training": {
                    "lora_rank": 16,
                    "lora_keys": ["mixer.out_proj"],
                    "trainable_lora_suffixes": ["mixer.out_proj"],
                },
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.inspect_prepare_manifest_artifact(
        prepare_manifest,
        expected_train_csv=expected_train_csv,
    )

    assert state["prepare_manifest_valid"] is False
    assert state["prepare_manifest_train_csv"] == str(wrong_train_csv)
    assert state["prepare_manifest_expected_train_csv"] == str(expected_train_csv.resolve())
    assert state["prepare_manifest_train_csv_matches_expected"] is False
    assert any("train_csv" in reason and "does not match expected" in reason for reason in state["prepare_manifest_blocked_reasons"])


def test_v3f_submission_inspect_prepare_manifest_artifact_accepts_repo_relative_train_csv(
    tmp_path: Path, monkeypatch
) -> None:
    prepare_manifest = tmp_path / "prepare_manifest.json"
    expected_train_csv = tmp_path / "artifacts" / "stage2.csv"
    monkeypatch.setattr(v3f_submission, "REPO_ROOT", tmp_path)
    prepare_manifest.write_text(
        json.dumps(
            {
                "train_csv": "artifacts/stage2.csv",
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                "readme_contract": dict(v3f_submission.README_CONTRACT),
                "training": {
                    "lora_rank": 16,
                    "lora_keys": ["mixer.out_proj"],
                    "trainable_lora_suffixes": ["mixer.out_proj"],
                },
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.inspect_prepare_manifest_artifact(
        prepare_manifest,
        expected_train_csv=expected_train_csv,
    )

    assert state["prepare_manifest_valid"] is True
    assert state["prepare_manifest_train_csv"] == "artifacts/stage2.csv"
    assert state["prepare_manifest_train_csv_matches_expected"] is True
    assert state["prepare_manifest_blocked_reasons"] == []


def test_v3f_submission_inspect_training_result_artifact_requires_adapter_files_and_progress(tmp_path: Path) -> None:
    training_result = tmp_path / "training_result.json"
    training_result.write_text(
        json.dumps(
            {
                "adapter_files": [
                    {"name": "adapter_config.json", "size_bytes": 0},
                    {"name": "adapters.safetensors", "size_bytes": 0},
                ],
                "latest_train_report": {
                    "iteration": 0,
                    "optimizer_step": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.inspect_training_result_artifact(training_result)

    assert state["training_result_valid"] is False
    assert state["training_result_adapter_files_present"] is True
    assert state["training_result_adapter_config_size_bytes"] == 0
    assert state["training_result_adapters_size_bytes"] == 0
    assert state["training_result_latest_train_iteration"] == 0
    assert state["training_result_latest_optimizer_step"] == 0
    assert any("adapter_config.json size_bytes is missing or non-positive" in reason for reason in state["training_result_blocked_reasons"])
    assert any("adapters.safetensors size_bytes is missing or non-positive" in reason for reason in state["training_result_blocked_reasons"])
    assert any("latest_train_report.iteration must be positive" in reason for reason in state["training_result_blocked_reasons"])
    assert any("latest_train_report.optimizer_step must be positive" in reason for reason in state["training_result_blocked_reasons"])


def test_v3f_submission_determine_next_step_returns_launch_stage2_for_invalid_run_metadata() -> None:
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state={
                "prepare_manifest_exists": True,
                "prepare_manifest_blocked_reasons": ["prepare invalid"],
                "training_result_exists": True,
                "training_result_blocked_reasons": [],
                "suite_summary_exists": True,
                "suite_summary_blocked_reasons": [],
                "audit_summary_exists": True,
                "audit_summary_blocked_reasons": [],
                "export_manifest_exists": True,
                "export_manifest_blocked_reasons": [],
                "submission_zip_exists": True,
                "submission_zip_blocked_reasons": [],
            },
            eligible=False,
        )
        == "launch-stage2-linked"
    )
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state={
                "prepare_manifest_exists": True,
                "prepare_manifest_blocked_reasons": [],
                "training_result_exists": True,
                "training_result_blocked_reasons": ["training invalid"],
                "suite_summary_exists": True,
                "suite_summary_blocked_reasons": [],
                "audit_summary_exists": True,
                "audit_summary_blocked_reasons": [],
                "export_manifest_exists": True,
                "export_manifest_blocked_reasons": [],
                "submission_zip_exists": True,
                "submission_zip_blocked_reasons": [],
            },
            eligible=False,
        )
        == "launch-stage2-linked"
    )


def test_v3f_submission_candidate_artifact_state_surfaces_invalid_run_metadata(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    (run_root / "prepare_manifest.json").parent.mkdir(parents=True, exist_ok=True)
    (run_root / "prepare_manifest.json").write_text("{}", encoding="utf-8")
    (run_root / "training_result.json").write_text("{}", encoding="utf-8")

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["prepare_manifest_exists"] is True
    assert state["prepare_manifest_valid"] is False
    assert state["training_result_exists"] is True
    assert state["training_result_valid"] is False
    assert any("train_csv is missing" in reason for reason in state["prepare_manifest_blocked_reasons"])
    assert any("adapter_files is missing" in reason for reason in state["training_result_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state,
            eligible=False,
        )
        == "launch-stage2-linked"
    )


def test_v3f_submission_candidate_artifact_state_requires_matching_profile_train_csv(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root, train_csv=tmp_path / "wrong.csv")

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
        expected_stage2_train_csv=tmp_path / "expected.csv",
    )

    assert state["prepare_manifest_valid"] is False
    assert state["prepare_manifest_train_csv_matches_expected"] is False
    assert state["prepare_manifest_expected_train_csv"] == str((tmp_path / "expected.csv").resolve())
    assert any("train_csv" in reason and "does not match expected" in reason for reason in state["prepare_manifest_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state,
            eligible=False,
        )
        == "launch-stage2-linked"
    )


def test_v3f_submission_candidate_artifact_state_flags_export_manifest_base_model_mismatch(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    export_zip = run_root / "submission_export" / "submission.zip"
    export_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(export_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")
    (run_root / "submission_export" / "export_manifest.json").write_text(
        json.dumps(
            {
                "zip_path": str(export_zip),
                "zip_size_bytes": export_zip.stat().st_size,
                "validation": {"valid": True},
                "converted_tensor_count": 2,
                "target_modules": ["out_proj"],
                "base_model_name_or_path": "wrong/model",
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["export_manifest_valid"] is True
    assert state["export_manifest_converted_tensor_count"] == 2
    assert state["export_manifest_has_converted_tensors"] is True
    assert state["export_manifest_target_modules"] == ["out_proj"]
    assert state["export_manifest_target_modules_nonempty"] is True
    assert state["export_manifest_target_modules_match_submission"] is True
    assert state["export_manifest_base_model_name_or_path"] == "wrong/model"
    assert state["export_manifest_base_model_matches_expected"] is False
    assert state["export_manifest_zip_path_matches_expected"] is True
    assert state["export_manifest_zip_size_matches_submission"] is True
    assert any("base_model_name_or_path" in reason for reason in state["export_manifest_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state
            | {
                "prepare_manifest_exists": True,
                "training_result_exists": True,
                "suite_summary_exists": True,
                "suite_summary_blocked_reasons": [],
                "audit_summary_exists": True,
                "audit_summary_blocked_reasons": [],
            },
            eligible=False,
        )
        == "export-stage2-submission"
    )


def test_v3f_submission_candidate_artifact_state_requires_valid_export_manifest(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    export_zip = run_root / "submission_export" / "submission.zip"
    export_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(export_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")
    (run_root / "submission_export" / "export_manifest.json").write_text(
        json.dumps(
            {
                "zip_path": str(export_zip),
                "zip_size_bytes": export_zip.stat().st_size,
                "validation": {"valid": False},
                "converted_tensor_count": 0,
                "target_modules": ["out_proj"],
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["export_manifest_valid"] is False
    assert state["export_manifest_converted_tensor_count"] == 0
    assert state["export_manifest_has_converted_tensors"] is False
    assert state["export_manifest_target_modules"] == ["out_proj"]
    assert state["export_manifest_target_modules_nonempty"] is True
    assert state["export_manifest_target_modules_match_submission"] is True
    assert state["export_manifest_base_model_matches_expected"] is True
    assert state["export_manifest_zip_path_matches_expected"] is True
    assert state["export_manifest_zip_size_matches_submission"] is True
    assert any("validation.valid is false" in reason for reason in state["export_manifest_blocked_reasons"])
    assert any("converted_tensor_count" in reason for reason in state["export_manifest_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state
            | {
                "prepare_manifest_exists": True,
                "training_result_exists": True,
                "suite_summary_exists": True,
                "suite_summary_blocked_reasons": [],
                "audit_summary_exists": True,
                "audit_summary_blocked_reasons": [],
            },
            eligible=False,
        )
        == "export-stage2-submission"
    )


def test_v3f_submission_candidate_artifact_state_requires_export_manifest_zip_consistency(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    export_zip = run_root / "submission_export" / "submission.zip"
    export_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(export_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")
    wrong_zip = run_root / "elsewhere" / "submission.zip"
    wrong_zip.parent.mkdir(parents=True, exist_ok=True)
    wrong_zip.write_bytes(b"not-the-real-export")
    (run_root / "submission_export" / "export_manifest.json").write_text(
        json.dumps(
            {
                "zip_path": str(wrong_zip),
                "zip_size_bytes": export_zip.stat().st_size + 1,
                "validation": {"valid": True},
                "converted_tensor_count": 2,
                "target_modules": ["out_proj"],
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["export_manifest_valid"] is True
    assert state["export_manifest_zip_path"] == str(wrong_zip.resolve())
    assert state["export_manifest_zip_path_matches_expected"] is False
    assert state["export_manifest_zip_size_bytes"] == export_zip.stat().st_size + 1
    assert state["export_manifest_zip_size_matches_submission"] is False
    assert state["expected_export_zip_path"] == str(export_zip.resolve())
    assert state["export_zip_path"] == str(export_zip.resolve())
    assert state["submission_zip_valid"] is True
    assert any("zip_path" in reason for reason in state["export_manifest_blocked_reasons"])
    assert any("zip_size_bytes does not match" in reason for reason in state["export_manifest_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state
            | {
                "prepare_manifest_exists": True,
                "training_result_exists": True,
                "suite_summary_exists": True,
                "suite_summary_blocked_reasons": [],
                "audit_summary_exists": True,
                "audit_summary_blocked_reasons": [],
            },
            eligible=False,
        )
        == "export-stage2-submission"
    )


def test_v3f_submission_candidate_artifact_state_requires_matching_target_modules(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    export_zip = run_root / "submission_export" / "submission.zip"
    export_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(export_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["q_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")
    (run_root / "submission_export" / "export_manifest.json").write_text(
        json.dumps(
            {
                "zip_path": str(export_zip),
                "zip_size_bytes": export_zip.stat().st_size,
                "validation": {"valid": True},
                "converted_tensor_count": 2,
                "target_modules": ["out_proj"],
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["export_manifest_target_modules"] == ["out_proj"]
    assert state["export_manifest_target_modules_nonempty"] is True
    assert state["submission_adapter_target_modules"] == ["q_proj"]
    assert state["submission_adapter_target_modules_nonempty"] is True
    assert state["export_manifest_target_modules_match_submission"] is False
    assert any("target_modules does not match" in reason for reason in state["export_manifest_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state
            | {
                "prepare_manifest_exists": True,
                "training_result_exists": True,
                "suite_summary_exists": True,
                "suite_summary_blocked_reasons": [],
                "audit_summary_exists": True,
                "audit_summary_blocked_reasons": [],
            },
            eligible=False,
        )
        == "export-stage2-submission"
    )


def test_v3f_submission_candidate_artifact_state_requires_valid_suite_summary(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    suite_summary = run_root / "eval_suite_readme_proxy_specialized" / "benchmark_eval_suite_summary.json"
    suite_summary.parent.mkdir(parents=True, exist_ok=True)
    suite_summary.write_text(
        json.dumps(
            {
                "evaluations": [
                    {
                        "evaluation_name": "readme_local320",
                        "output_root": str(run_root / "eval_suite_readme_proxy_specialized" / "readme_local320"),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (
        run_root
        / "eval_suite_readme_proxy_specialized"
        / "readme_local320"
        / "benchmark_eval_summary.json"
    ).parent.mkdir(parents=True, exist_ok=True)
    (
        run_root
        / "eval_suite_readme_proxy_specialized"
        / "readme_local320"
        / "benchmark_eval_summary.json"
    ).write_text(
        json.dumps(
            {
                "evaluation_name": "readme_local320",
                "overall": {"rows": 320, "correct": 220, "accuracy": 220 / 320},
                "by_benchmark": [
                    {"benchmark_name": "general_stable_set", "rows": 200, "correct": 180, "accuracy": 0.9}
                ],
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["suite_summary_exists"] is True
    assert state["suite_summary_valid"] is False
    assert state["suite_summary_required_evaluations_present"] is False
    assert state["suite_summary_eval_summaries_valid"] is False
    assert state["suite_summary_required_evaluation_rows"]["readme_local320"] == 320
    assert state["suite_summary_required_evaluation_rows"]["leaderboard_proxy_v2"] is None
    assert any("missing evaluation 'leaderboard_proxy_v2'" in reason for reason in state["suite_summary_blocked_reasons"])
    assert any("missing evaluation 'binary_bias_specialized_set'" in reason for reason in state["suite_summary_blocked_reasons"])
    assert any("missing by_benchmark entry 'binary_hard_set'" in reason for reason in state["suite_summary_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state
            | {
                "prepare_manifest_exists": True,
                "training_result_exists": True,
                "audit_summary_exists": True,
                "audit_summary_blocked_reasons": [],
            },
            eligible=False,
        )
        == "postprocess-stage2"
    )


def test_v3f_submission_candidate_artifact_state_requires_valid_audit_summary(tmp_path: Path) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    audit_summary = run_root / "submission_compat_audit" / "submission_compat_audit.json"
    audit_summary.parent.mkdir(parents=True, exist_ok=True)
    audit_summary.write_text(
        json.dumps(
            {
                "audit_status": "",
                "peft_export_ready": False,
                "base_model_name_or_path": "wrong/model",
                "unsupported_tensor_count": 3,
                "peft_adapter_config_preview": {
                    "peft_type": "IA3",
                    "base_model_name_or_path": "wrong/model",
                    "r": 64,
                    "target_modules": [],
                    "inference_mode": False,
                },
                "readme_submission_contract": {
                    "required_files": ["adapter_config.json"],
                    "max_lora_rank": 64,
                },
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["audit_summary_exists"] is True
    assert state["audit_summary_valid"] is False
    assert state["audit_summary_peft_export_ready"] is False
    assert state["audit_summary_base_model_matches_expected"] is False
    assert state["audit_summary_preview_peft_type"] == "IA3"
    assert state["audit_summary_preview_peft_type_matches_expected"] is False
    assert state["audit_summary_preview_rank"] == 64
    assert state["audit_summary_preview_rank_within_readme_limit"] is False
    assert state["audit_summary_preview_target_modules_nonempty"] is False
    assert state["audit_summary_preview_inference_mode"] is False
    assert state["audit_summary_preview_inference_mode_matches_expected"] is False
    assert state["audit_summary_readme_contract_required_files_present"] is False
    assert state["audit_summary_readme_contract_max_rank_matches_expected"] is False
    assert state["audit_summary_readme_contract_single_adapter_matches_expected"] is False
    assert any("peft_export_ready is false" in reason for reason in state["audit_summary_blocked_reasons"])
    assert any("unsupported_tensor_count must be 0" in reason for reason in state["audit_summary_blocked_reasons"])
    assert any("single_adapter_submission_zip must be true" in reason for reason in state["audit_summary_blocked_reasons"])
    assert (
        v3f_submission.determine_stage2_profile_next_step(
            shared_stage1_run_root_exists=True,
            profile_artifact_state={"build_stage2_artifacts_needed": False},
            run_artifact_state=state
            | {
                "prepare_manifest_exists": True,
                "training_result_exists": True,
                "suite_summary_exists": True,
                "suite_summary_blocked_reasons": [],
            },
            eligible=False,
        )
        == "postprocess-stage2"
    )


def test_v3f_submission_inspect_submission_audit_artifact_accepts_missing_legacy_audit_status(
    tmp_path: Path,
) -> None:
    audit_summary = tmp_path / "submission_compat_audit.json"
    audit_summary.write_text(
        json.dumps(
            {
                "peft_export_ready": True,
                "audit_status_detail": "validated_peft_reference_match",
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                "unsupported_tensor_count": 0,
                "peft_adapter_config_preview": {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "r": 16,
                    "target_modules": ["out_proj"],
                    "inference_mode": True,
                },
                "readme_submission_contract": {
                    "required_files": ["adapter_config.json", "adapter_model.safetensors"],
                    "max_lora_rank": 32,
                    "single_adapter_submission_zip": True,
                },
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.inspect_submission_audit_artifact(audit_summary)

    assert state["audit_summary_valid"] is True
    assert state["audit_summary_status"] == ""
    assert state["audit_summary_status_present"] is False
    assert state["audit_summary_status_detail"] == "validated_peft_reference_match"
    assert state["audit_summary_peft_export_ready"] is True
    assert state["audit_summary_blocked_reasons"] == []


def test_v3f_submission_inspect_submission_audit_artifact_rejects_non_boolean_peft_export_ready(
    tmp_path: Path,
) -> None:
    audit_summary = tmp_path / "submission_compat_audit.json"
    audit_summary.write_text(
        json.dumps(
            {
                "audit_status": "potentially_exportable_2d_only",
                "peft_export_ready": "true",
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                "unsupported_tensor_count": 0,
                "peft_adapter_config_preview": {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "r": 16,
                    "target_modules": ["out_proj"],
                    "inference_mode": True,
                },
                "readme_submission_contract": {
                    "required_files": ["adapter_config.json", "adapter_model.safetensors"],
                    "max_lora_rank": 32,
                    "single_adapter_submission_zip": True,
                },
            }
        ),
        encoding="utf-8",
    )

    state = v3f_submission.inspect_submission_audit_artifact(audit_summary)

    assert state["audit_summary_valid"] is False
    assert state["audit_summary_status"] == "potentially_exportable_2d_only"
    assert state["audit_summary_status_present"] is True
    assert state["audit_summary_peft_export_ready"] is False
    assert any("peft_export_ready is missing or invalid" in reason for reason in state["audit_summary_blocked_reasons"])


def test_v3f_submission_candidate_artifact_state_defaults_single_adapter_audit_flag_when_audit_missing(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["audit_summary_exists"] is False
    assert state["audit_summary_readme_contract_single_adapter_matches_expected"] is False
    assert any("submission_compat_audit.json is missing" in reason for reason in state["audit_summary_blocked_reasons"])


def test_v3f_submission_candidate_artifact_state_defaults_single_adapter_audit_flag_when_audit_unparseable(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    audit_summary = run_root / "submission_compat_audit" / "submission_compat_audit.json"
    audit_summary.parent.mkdir(parents=True, exist_ok=True)
    audit_summary.write_text("{not-json", encoding="utf-8")

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["audit_summary_exists"] is True
    assert state["audit_summary_valid"] is False
    assert state["audit_summary_readme_contract_single_adapter_matches_expected"] is False
    assert any(
        "submission_compat_audit.json could not be parsed" in reason for reason in state["audit_summary_blocked_reasons"]
    )


def test_v3f_submission_candidate_artifact_state_defaults_single_adapter_audit_flag_when_audit_not_object(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "candidate"
    _write_minimal_valid_run_metadata(run_root)
    audit_summary = run_root / "submission_compat_audit" / "submission_compat_audit.json"
    audit_summary.parent.mkdir(parents=True, exist_ok=True)
    audit_summary.write_text(json.dumps(["not-an-object"]), encoding="utf-8")

    state = v3f_submission.build_stage2_candidate_artifact_state(
        run_root,
        suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
        audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
        export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
    )

    assert state["audit_summary_exists"] is True
    assert state["audit_summary_valid"] is False
    assert state["audit_summary_readme_contract_single_adapter_matches_expected"] is False
    assert any(
        "submission_compat_audit.json is not a JSON object" in reason for reason in state["audit_summary_blocked_reasons"]
    )


def test_v3f_submission_profile_artifact_state_tracks_missing_inputs(tmp_path: Path, monkeypatch) -> None:
    artifact_root = tmp_path / "artifacts"
    present_paths = {
        "stage2_dataset_csv": artifact_root / "stage2.csv",
        "stage2_dataset_summary_json": artifact_root / "stage2_summary.json",
        "proxy_v2_csv": artifact_root / "proxy.csv",
        "proxy_v2_summary_json": artifact_root / "proxy_summary.json",
    }
    present_paths["stage2_dataset_csv"].parent.mkdir(parents=True, exist_ok=True)
    present_paths["stage2_dataset_csv"].write_text("id,prompt,completion\n1,a,b\n", encoding="utf-8")
    present_paths["proxy_v2_csv"].write_text("id,prompt\n1,a\n", encoding="utf-8")
    present_paths["stage2_dataset_summary_json"].write_text(
        json.dumps({"rows": 1, "output_csv": str(present_paths["stage2_dataset_csv"])}),
        encoding="utf-8",
    )
    present_paths["proxy_v2_summary_json"].write_text(
        json.dumps({"rows": 1, "output_csv": str(present_paths["proxy_v2_csv"])}),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        v3f_submission,
        "resolve_stage2_profile_artifact_paths",
        lambda profile_name: present_paths if profile_name == "ready" else {
            "stage2_dataset_csv": artifact_root / "missing_stage2.csv",
            "stage2_dataset_summary_json": artifact_root / "missing_stage2_summary.json",
            "proxy_v2_csv": artifact_root / "missing_proxy.csv",
            "proxy_v2_summary_json": artifact_root / "missing_proxy_summary.json",
        },
    )

    ready = v3f_submission.build_stage2_profile_artifact_state("ready")
    missing = v3f_submission.build_stage2_profile_artifact_state("missing")

    assert ready["build_stage2_artifacts_needed"] is False
    assert ready["missing_profile_artifacts"] == []
    assert ready["invalid_profile_artifacts"] == []
    assert ready["stage2_dataset_csv_nonempty"] is True
    assert ready["stage2_dataset_summary_valid"] is True
    assert ready["stage2_dataset_summary_rows"] == 1
    assert ready["stage2_dataset_summary_output_csv_matches"] is True
    assert ready["proxy_v2_csv_nonempty"] is True
    assert ready["proxy_v2_summary_valid"] is True
    assert ready["proxy_v2_summary_rows"] == 1
    assert ready["proxy_v2_summary_output_csv_matches"] is True
    assert missing["build_stage2_artifacts_needed"] is True
    assert "stage2_dataset_csv" in missing["missing_profile_artifacts"]
    assert "proxy_v2_summary_json" in missing["missing_profile_artifacts"]


def test_v3f_submission_profile_artifact_state_rejects_invalid_content(tmp_path: Path, monkeypatch) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_paths = {
        "stage2_dataset_csv": artifact_root / "stage2.csv",
        "stage2_dataset_summary_json": artifact_root / "stage2_summary.json",
        "proxy_v2_csv": artifact_root / "proxy.csv",
        "proxy_v2_summary_json": artifact_root / "proxy_summary.json",
    }
    artifact_paths["stage2_dataset_csv"].parent.mkdir(parents=True, exist_ok=True)
    artifact_paths["stage2_dataset_csv"].write_text("", encoding="utf-8")
    artifact_paths["proxy_v2_csv"].write_text("id,prompt\n1,a\n", encoding="utf-8")
    artifact_paths["stage2_dataset_summary_json"].write_text(
        json.dumps({"rows": 0, "output_csv": str(artifact_root / "wrong.csv")}),
        encoding="utf-8",
    )
    artifact_paths["proxy_v2_summary_json"].write_text("[]", encoding="utf-8")

    monkeypatch.setattr(v3f_submission, "resolve_stage2_profile_artifact_paths", lambda profile_name: artifact_paths)

    state = v3f_submission.build_stage2_profile_artifact_state("invalid")

    assert state["build_stage2_artifacts_needed"] is True
    assert state["missing_profile_artifacts"] == []
    assert state["stage2_dataset_csv_nonempty"] is False
    assert state["stage2_dataset_summary_valid"] is False
    assert state["stage2_dataset_summary_rows"] == 0
    assert state["stage2_dataset_summary_output_csv_matches"] is False
    assert state["proxy_v2_csv_nonempty"] is True
    assert state["proxy_v2_summary_valid"] is False
    assert state["proxy_v2_summary_rows"] is None
    assert state["proxy_v2_summary_output_csv_matches"] is False
    assert any("stage2_dataset_csv_empty" == reason for reason in state["invalid_profile_artifacts"])
    assert any("rows must be positive" in reason for reason in state["invalid_profile_artifacts"])
    assert any("output_csv does not match expected artifact" in reason for reason in state["invalid_profile_artifacts"])
    assert any("is not a JSON object" in reason for reason in state["invalid_profile_artifacts"])


def test_v3f_submission_write_stage2_candidate_audit_rejects_profile_and_all_profiles(
    tmp_path: Path,
) -> None:
    try:
        v3f_submission.command_write_stage2_candidate_audit(
            SimpleNamespace(
                profile=["attention-short-default"],
                all_profiles=True,
                output_root=tmp_path / "audit",
                suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
                audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
                export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
                min_local320_accuracy=v3f_submission.DEFAULT_STAGE2_CANDIDATE_GATES["min_local320_accuracy"],
                min_general_stable_accuracy=v3f_submission.DEFAULT_STAGE2_CANDIDATE_GATES[
                    "min_general_stable_accuracy"
                ],
                min_proxy_v2_accuracy=v3f_submission.DEFAULT_STAGE2_CANDIDATE_GATES["min_proxy_v2_accuracy"],
                min_specialized_accuracy=v3f_submission.DEFAULT_STAGE2_CANDIDATE_GATES[
                    "min_specialized_accuracy"
                ],
                require_exportable=v3f_submission.DEFAULT_STAGE2_CANDIDATE_GATES["require_exportable"],
            )
        )
    except SystemExit as exc:
        assert "either explicit --profile values or --all-profiles" in str(exc)
    else:
        raise AssertionError("Expected mixed write-stage2-candidate-audit selection to fail")


def test_v3f_submission_write_stage2_candidate_audit_emits_gate_status(tmp_path: Path, monkeypatch) -> None:
    fake_repo_root = tmp_path / "repo"
    (fake_repo_root / "baseline_mlx" / "outputs" / v3f_submission.STAGE1_RUN_NAME).mkdir(
        parents=True,
        exist_ok=True,
    )
    run_roots = {
        "attention-short-default": tmp_path / "runs" / "attention-short-default",
        "attention-short-noanswer": tmp_path / "runs" / "attention-short-noanswer",
    }
    profile_artifacts = {
        "attention-short-default": {
            "stage2_dataset_csv": tmp_path / "profile_artifacts" / "default_stage2.csv",
            "stage2_dataset_summary_json": tmp_path / "profile_artifacts" / "default_stage2_summary.json",
            "proxy_v2_csv": tmp_path / "profile_artifacts" / "default_proxy.csv",
            "proxy_v2_summary_json": tmp_path / "profile_artifacts" / "default_proxy_summary.json",
        },
        "attention-short-noanswer": {
            "stage2_dataset_csv": tmp_path / "profile_artifacts" / "missing_stage2.csv",
            "stage2_dataset_summary_json": tmp_path / "profile_artifacts" / "missing_stage2_summary.json",
            "proxy_v2_csv": tmp_path / "profile_artifacts" / "missing_proxy.csv",
            "proxy_v2_summary_json": tmp_path / "profile_artifacts" / "missing_proxy_summary.json",
        },
    }
    for path in profile_artifacts["attention-short-default"].values():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".csv":
            path.write_text("id,prompt,completion\n1,a,b\n", encoding="utf-8")
        else:
            matching_csv = (
                profile_artifacts["attention-short-default"]["stage2_dataset_csv"]
                if "stage2_dataset" in path.name
                else profile_artifacts["attention-short-default"]["proxy_v2_csv"]
            )
            path.write_text(
                json.dumps({"rows": 1, "output_csv": str(matching_csv)}),
                encoding="utf-8",
            )
    export_zip = run_roots["attention-short-default"] / "submission_export" / "submission.zip"
    export_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(export_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "adapter_config.json",
            json.dumps(
                {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "task_type": "CAUSAL_LM",
                    "inference_mode": True,
                    "target_modules": ["out_proj"],
                    "r": 16,
                }
            ),
        )
        archive.writestr("adapter_model.safetensors", "tensor-bytes")
    _write_minimal_valid_run_metadata(
        run_roots["attention-short-default"],
        train_csv=profile_artifacts["attention-short-default"]["stage2_dataset_csv"],
    )
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "benchmark_eval_suite_summary.json"
    ).parent.mkdir(parents=True, exist_ok=True)
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "benchmark_eval_suite_summary.json"
    ).write_text(
        json.dumps(
            {
                "evaluations": [
                    {
                        "evaluation_name": "readme_local320",
                        "output_root": str(
                            run_roots["attention-short-default"]
                            / "eval_suite_readme_proxy_specialized"
                            / "readme_local320"
                        ),
                    },
                    {
                        "evaluation_name": "leaderboard_proxy_v2",
                        "output_root": str(
                            run_roots["attention-short-default"]
                            / "eval_suite_readme_proxy_specialized"
                            / "leaderboard_proxy_v2"
                        ),
                    },
                    {
                        "evaluation_name": "binary_bias_specialized_set",
                        "output_root": str(
                            run_roots["attention-short-default"]
                            / "eval_suite_readme_proxy_specialized"
                            / "binary_bias_specialized_set"
                        ),
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "readme_local320"
        / "benchmark_eval_summary.json"
    ).parent.mkdir(parents=True, exist_ok=True)
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "readme_local320"
        / "benchmark_eval_summary.json"
    ).write_text(
        json.dumps(
            {
                "evaluation_name": "readme_local320",
                "overall": {"rows": 320, "correct": 230, "accuracy": 230 / 320},
                "by_benchmark": [
                    {"benchmark_name": "general_stable_set", "rows": 200, "correct": 194, "accuracy": 0.97},
                    {"benchmark_name": "binary_hard_set", "rows": 60, "correct": 45, "accuracy": 0.75},
                    {"benchmark_name": "symbol_watch_set", "rows": 60, "correct": 48, "accuracy": 0.80},
                ],
            }
        ),
        encoding="utf-8",
    )
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "leaderboard_proxy_v2"
        / "benchmark_eval_summary.json"
    ).parent.mkdir(parents=True, exist_ok=True)
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "leaderboard_proxy_v2"
        / "benchmark_eval_summary.json"
    ).write_text(
        json.dumps(
            {
                "evaluation_name": "leaderboard_proxy_v2",
                "overall": {"rows": 100, "correct": 55, "accuracy": 0.55},
                "by_benchmark": [],
            }
        ),
        encoding="utf-8",
    )
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "binary_bias_specialized_set"
        / "benchmark_eval_summary.json"
    ).parent.mkdir(parents=True, exist_ok=True)
    (
        run_roots["attention-short-default"]
        / "eval_suite_readme_proxy_specialized"
        / "binary_bias_specialized_set"
        / "benchmark_eval_summary.json"
    ).write_text(
        json.dumps(
            {
                "evaluation_name": "binary_bias_specialized_set",
                "overall": {"rows": 100, "correct": 43, "accuracy": 0.43},
                "by_benchmark": [],
            }
        ),
        encoding="utf-8",
    )
    (
        run_roots["attention-short-default"]
        / "submission_compat_audit"
        / "submission_compat_audit.json"
    ).parent.mkdir(parents=True, exist_ok=True)
    (
        run_roots["attention-short-default"]
        / "submission_compat_audit"
        / "submission_compat_audit.json"
    ).write_text(
        json.dumps(
            {
                "audit_status": "potentially_exportable_2d_only",
                "peft_export_ready": True,
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                "unsupported_tensor_count": 0,
                "peft_adapter_config_preview": {
                    "peft_type": "LORA",
                    "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
                    "r": 16,
                    "target_modules": ["out_proj"],
                    "inference_mode": True,
                },
                "readme_submission_contract": {
                    "required_files": ["adapter_config.json", "adapter_model.safetensors"],
                    "max_lora_rank": 32,
                    "single_adapter_submission_zip": True,
                },
            }
        ),
        encoding="utf-8",
    )
    (
        run_roots["attention-short-default"]
        / "submission_export"
        / "export_manifest.json"
    ).write_text(
        json.dumps(
            {
                "zip_path": str(export_zip),
                "zip_size_bytes": export_zip.stat().st_size,
                "validation": {"valid": True},
                "converted_tensor_count": 2,
                "target_modules": ["out_proj"],
                "base_model_name_or_path": v3f_submission.BASE_MODEL_NAME,
            }
        ),
        encoding="utf-8",
    )
    (run_roots["attention-short-default"] / "recorded_run_result.json").write_text(
        json.dumps(
            {
                "readme_eval_assumptions": {
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "max_tokens": 7680,
                    "max_num_seqs": 64,
                    "max_model_len": 8192,
                    "eval_enable_thinking": True,
                }
            }
        ),
        encoding="utf-8",
    )
    (run_roots["attention-short-noanswer"] / "prepare_manifest.json").parent.mkdir(parents=True, exist_ok=True)
    (run_roots["attention-short-noanswer"] / "prepare_manifest.json").write_text("{}", encoding="utf-8")

    candidate_payloads = {
        "attention-short-default": {
            "run_name": "attention-short-default",
            "run_root": str(run_roots["attention-short-default"]),
            "label": "attention-short-default",
            "train_csv": "stage2.csv",
            "trainable_lora_suffixes": ["out_proj"],
            "lora_keys": ["layers.0.out_proj"],
            "local320": {"rows": 320, "correct": 230, "accuracy": 230 / 320},
            "general_stable": {"rows": 100, "correct": 97, "accuracy": 0.97},
            "proxy_v1": {"rows": 100, "correct": 60, "accuracy": 0.60},
            "proxy_v2": {"rows": 100, "correct": 55, "accuracy": 0.55},
            "specialized": {"rows": 100, "correct": 43, "accuracy": 0.43},
            "binary_hard": {"rows": 100, "correct": 75, "accuracy": 0.75},
            "symbol_watch": {"rows": 100, "correct": 80, "accuracy": 0.80},
            "audit_status": "aligned",
            "peft_export_ready": True,
            "has_export_manifest": True,
        }
    }

    def fake_stage2_run_root_from_profile(profile: dict[str, object]) -> Path:
        return run_roots[str(profile["profile_name"])]

    def fake_resolve_stage2_profile_artifact_paths(profile_name: str) -> dict[str, Path]:
        return profile_artifacts[profile_name]

    def fake_load_run_result_payload(
        *,
        run_root: Path,
        label: str,
        suite_summary_relpath: Path,
        audit_relpath: Path,
        export_relpath: Path,
    ) -> dict[str, object]:
        if not (run_root / "training_result.json").exists():
            raise FileNotFoundError(f"Missing training result: {run_root / 'training_result.json'}")
        return {"candidate": candidate_payloads[run_root.name]}

    def fake_build_submission_candidate_from_payload(payload: dict[str, object]) -> dict[str, object]:
        return dict(payload["candidate"])

    def fake_build_submission_candidate_gates(args: SimpleNamespace) -> dict[str, object]:
        return {
            "min_local320_accuracy": float(args.min_local320_accuracy),
            "min_general_stable_accuracy": float(args.min_general_stable_accuracy),
            "min_proxy_v2_accuracy": float(args.min_proxy_v2_accuracy),
            "min_specialized_accuracy": float(args.min_specialized_accuracy),
            "require_exportable": bool(args.require_exportable),
        }

    def fake_evaluate_submission_candidate(
        candidate: dict[str, object],
        *,
        gates: dict[str, object],
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        if gates["require_exportable"] and not candidate["peft_export_ready"]:
            reasons.append("adapter is not submission-exportable under the README-compatible PEFT audit")
        if float(candidate["local320"]["accuracy"]) < float(gates["min_local320_accuracy"]):
            reasons.append("local320 gate failed")
        if float(candidate["general_stable"]["accuracy"]) < float(gates["min_general_stable_accuracy"]):
            reasons.append("general_stable gate failed")
        if float(candidate["proxy_v2"]["accuracy"]) < float(gates["min_proxy_v2_accuracy"]):
            reasons.append("proxy_v2 gate failed")
        if float(candidate["specialized"]["accuracy"]) < float(gates["min_specialized_accuracy"]):
            reasons.append("specialized gate failed")
        return (not reasons), reasons

    def fake_candidate_selection_sort_key(candidate: dict[str, object]) -> tuple[float, ...]:
        return (
            float(candidate["local320"]["accuracy"]),
            float(candidate["general_stable"]["accuracy"]),
            float(candidate["proxy_v1"]["accuracy"]),
            float(candidate["proxy_v2"]["accuracy"]),
            float(candidate["specialized"]["accuracy"]),
            float(candidate["binary_hard"]["accuracy"]),
            float(candidate["symbol_watch"]["accuracy"]),
        )

    fake_module = SimpleNamespace(
        build_submission_candidate_gates=fake_build_submission_candidate_gates,
        load_run_result_payload=fake_load_run_result_payload,
        build_submission_candidate_from_payload=fake_build_submission_candidate_from_payload,
        evaluate_submission_candidate=fake_evaluate_submission_candidate,
        candidate_selection_sort_key=fake_candidate_selection_sort_key,
        make_empty_score_row=lambda: {"rows": 0, "correct": 0, "accuracy": 0.0},
    )
    monkeypatch.setattr(v3f_submission, "load_monolith_submission_helpers", lambda: fake_module)
    monkeypatch.setattr(v3f_submission, "REPO_ROOT", fake_repo_root)
    monkeypatch.setattr(v3f_submission, "stage2_run_root_from_profile", fake_stage2_run_root_from_profile)
    monkeypatch.setattr(
        v3f_submission,
        "resolve_stage2_profile_artifact_paths",
        fake_resolve_stage2_profile_artifact_paths,
    )

    result = v3f_submission.command_write_stage2_candidate_audit(
        SimpleNamespace(
            profile=["attention-short-default", "attention-short-noanswer"],
            all_profiles=False,
            output_root=tmp_path / "audit",
            suite_summary_relpath=v3f_submission.DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
            audit_relpath=v3f_submission.DEFAULT_RUN_AUDIT_RELPATH,
            export_relpath=v3f_submission.DEFAULT_RUN_EXPORT_RELPATH,
            min_local320_accuracy=215 / 320,
            min_general_stable_accuracy=0.96,
            min_proxy_v2_accuracy=0.50,
            min_specialized_accuracy=0.42,
            require_exportable=True,
        )
    )

    assert result == 0
    payload = json.loads((tmp_path / "audit" / "v3f_stage2_candidate_audit.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "audit" / "v3f_stage2_candidate_audit.md").read_text(encoding="utf-8")

    assert payload["selected_candidate"]["profile_name"] == "attention-short-default"
    assert payload["shared_stage1_run_root_exists"] is True
    assert payload["eligible_candidate_count"] == 1
    assert payload["used_default_stage2_profiles"] is False
    assert payload["selected_stage2_profiles"] == ["attention-short-default", "attention-short-noanswer"]
    selected = next(item for item in payload["candidates"] if item["profile_name"] == "attention-short-default")
    assert selected["build_stage2_artifacts_needed"] is False
    assert selected["invalid_profile_artifacts"] == []
    assert selected["stage2_dataset_csv_nonempty"] is True
    assert selected["stage2_dataset_summary_valid"] is True
    assert selected["stage2_dataset_summary_rows"] == 1
    assert selected["proxy_v2_csv_nonempty"] is True
    assert selected["proxy_v2_summary_valid"] is True
    assert selected["proxy_v2_summary_rows"] == 1
    assert selected["prepare_manifest_valid"] is True
    assert selected["prepare_manifest_train_csv_matches_expected"] is True
    assert selected["prepare_manifest_training_lora_rank"] == 16
    assert selected["prepare_manifest_training_lora_keys_nonempty"] is True
    assert selected["prepare_manifest_training_trainable_suffixes_nonempty"] is True
    assert selected["training_result_valid"] is True
    assert selected["training_result_adapter_files_present"] is True
    assert selected["training_result_latest_optimizer_step"] == 2
    assert selected["suite_summary_valid"] is True
    assert selected["suite_summary_required_evaluations_present"] is True
    assert selected["suite_summary_eval_summaries_valid"] is True
    assert selected["suite_summary_required_evaluation_rows"] == {
        "readme_local320": 320,
        "leaderboard_proxy_v2": 100,
        "binary_bias_specialized_set": 100,
    }
    assert selected["suite_summary_blocked_reasons"] == []
    assert selected["peft_export_ready"] is True
    assert selected["audit_summary_valid"] is True
    assert selected["audit_summary_peft_export_ready"] is True
    assert selected["audit_summary_preview_rank"] == 16
    assert selected["audit_summary_preview_rank_matches_submission"] is True
    assert selected["audit_summary_target_modules_match_submission"] is True
    assert selected["audit_summary_readme_contract_single_adapter_matches_expected"] is True
    assert selected["audit_summary_blocked_reasons"] == []
    assert selected["recorded_eval_assumptions_present"] is True
    assert selected["recorded_eval_contract_matches_readme"] is True
    assert selected["recorded_eval_contract_mismatches"] == []
    assert selected["recommended_next_step"] == "package-stage2-matrix-best-submission"
    assert selected["export_manifest_valid"] is True
    assert selected["export_manifest_converted_tensor_count"] == 2
    assert selected["export_manifest_has_converted_tensors"] is True
    assert selected["export_manifest_target_modules"] == ["out_proj"]
    assert selected["export_manifest_target_modules_count"] == 1
    assert selected["export_manifest_target_modules_nonempty"] is True
    assert selected["export_manifest_target_modules_match_submission"] is True
    assert selected["export_manifest_base_model_name_or_path"] == v3f_submission.BASE_MODEL_NAME
    assert selected["export_manifest_base_model_matches_expected"] is True
    assert selected["export_manifest_zip_path_matches_expected"] is True
    assert selected["export_manifest_zip_size_matches_submission"] is True
    assert selected["submission_zip_valid"] is True
    assert selected["submission_adapter_peft_type"] == "LORA"
    assert selected["submission_adapter_peft_type_matches_expected"] is True
    assert selected["submission_adapter_base_model_name_or_path"] == v3f_submission.BASE_MODEL_NAME
    assert selected["submission_adapter_base_model_matches_expected"] is True
    assert selected["submission_adapter_task_type"] == "CAUSAL_LM"
    assert selected["submission_adapter_task_type_matches_expected"] is True
    assert selected["submission_adapter_inference_mode"] is True
    assert selected["submission_adapter_inference_mode_matches_expected"] is True
    assert selected["submission_adapter_target_modules"] == ["out_proj"]
    assert selected["submission_adapter_target_modules_count"] == 1
    assert selected["submission_adapter_target_modules_nonempty"] is True
    assert selected["submission_adapter_model_size_bytes"] == len("tensor-bytes")
    assert selected["submission_adapter_model_nonempty"] is True
    assert selected["submission_adapter_rank"] == 16
    assert selected["submission_rank_within_readme_limit"] is True
    assert selected["submission_zip_exists"] is True
    missing = next(item for item in payload["candidates"] if item["profile_name"] == "attention-short-noanswer")
    assert missing["build_stage2_artifacts_needed"] is True
    assert missing["invalid_profile_artifacts"] == []
    assert missing["suite_summary_valid"] is False
    assert missing["recorded_eval_assumptions_present"] is False
    assert missing["recorded_eval_contract_matches_readme"] is None
    assert missing["recommended_next_step"] == "build-stage2-artifacts"
    assert "stage2_dataset_csv" in missing["missing_profile_artifacts"]
    assert missing["load_status"] == "missing_artifacts"
    assert missing["prepare_manifest_exists"] is True
    assert missing["prepare_manifest_valid"] is False
    assert any("prepare_manifest.json" in item for item in missing["prepare_manifest_blocked_reasons"])
    assert "training_result" in missing["missing_artifacts"]
    assert any("Missing prepare manifest" in item for item in missing["gate_failures"])
    assert any("Missing training result" in item for item in missing["gate_failures"])
    assert "v3f stage2 candidate audit" in markdown.lower()
    assert "recommended_next_step" in markdown
    assert "stage2_artifacts_ready" in markdown
    assert "run_root_exists" in markdown
    assert "prepare_manifest_valid" in markdown
    assert "prepare_manifest_train_csv_matches_expected" in markdown
    assert "training_result_valid" in markdown
    assert "audit_summary_readme_contract_single_adapter_matches_expected" in markdown
    assert "export_manifest_zip_path_matches_expected" in markdown
    assert "export_manifest_zip_size_matches_submission" in markdown
    assert "attention-short-noanswer" in markdown


def test_v3f_submission_launch_stage2_matrix_dry_run_defaults_to_curated_trio(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    result = v3f_submission.command_launch_stage2_matrix(
        SimpleNamespace(
            profile=[],
            all_profiles=False,
            skip_build_stage2_artifacts=True,
            skip_stage1=False,
            skip_postprocess=True,
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 4
    assert "launch-stage1" in calls[0][0]
    assert "launch-stage2-linked" in calls[1][0]
    assert "launch-stage2-linked" in calls[2][0]
    assert "launch-stage2-linked" in calls[3][0]

    summary = json.loads((tmp_path / "summary" / "v3f_submission_line_summary.json").read_text(encoding="utf-8"))
    assert summary["mode"] == "launch-stage2-matrix"
    assert summary["used_default_stage2_profiles"] is True
    assert summary["all_profiles"] is False
    assert summary["selected_stage2_profiles"] == [
        "attention-short-default",
        "attention-short-noanswer",
        "attention-short-manual",
    ]


def test_v3f_submission_launch_stage2_matrix_rejects_profile_and_all_profiles(tmp_path: Path) -> None:
    try:
        v3f_submission.command_launch_stage2_matrix(
            SimpleNamespace(
                profile=["attention-short-default"],
                all_profiles=True,
                skip_build_stage2_artifacts=False,
                skip_stage1=False,
                skip_postprocess=False,
                summary_output_root=tmp_path / "summary",
                dry_run=True,
            )
        )
    except SystemExit as exc:
        assert "either explicit --profile values or --all-profiles" in str(exc)
    else:
        raise AssertionError("Expected mixed launch-stage2-matrix selection to fail")


def test_v3f_submission_launch_stage2_matrix_dry_run_arms_multiple_profiles(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    result = v3f_submission.command_launch_stage2_matrix(
        SimpleNamespace(
            profile=["attention-short-default", "attention-short-noanswer"],
            all_profiles=False,
            skip_build_stage2_artifacts=False,
            skip_stage1=False,
            skip_postprocess=False,
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 7
    assert calls[0][1] is True
    assert "build-stage2-artifacts" in calls[0][0]
    assert "--max-answer-only-ratio" in calls[0][0]
    assert "build-stage2-artifacts" in calls[1][0]
    assert "launch-stage1" in calls[2][0]
    assert "launch-stage2-linked" in calls[3][0]
    assert "postprocess-stage2" in calls[4][0]
    assert "launch-stage2-linked" in calls[5][0]
    assert "postprocess-stage2" in calls[6][0]

    summary = json.loads((tmp_path / "summary" / "v3f_submission_line_summary.json").read_text(encoding="utf-8"))
    assert summary["mode"] == "launch-stage2-matrix"
    assert summary["used_default_stage2_profiles"] is False
    assert summary["all_profiles"] is False
    assert summary["selected_stage2_profiles"] == ["attention-short-default", "attention-short-noanswer"]
    assert summary["skip_build_stage2_artifacts"] is False
    assert len(summary["matrix_build_commands"]) == 2
    assert len(summary["matrix_export_commands"]) == 2


def test_v3f_submission_package_stage2_matrix_best_submission_dry_run(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    result = v3f_submission.command_package_stage2_matrix_best_submission(
        SimpleNamespace(
            profile=["attention-short-default", "union-short-exploratory"],
            all_profiles=False,
            output_root=tmp_path / "best_submission",
            results_md=tmp_path / "results.md",
            base_model_name_or_path=v3f_submission.BASE_MODEL_NAME,
            min_local320_accuracy=215 / 320,
            min_general_stable_accuracy=0.96,
            min_proxy_v2_accuracy=0.50,
            min_specialized_accuracy=0.42,
            require_exportable=True,
            export_if_missing=True,
            update_results_md=False,
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 1
    command, dry_run = calls[0]
    assert dry_run is True
    assert "package-best-submission" in command
    assert command[command.index("--output-root") + 1] == str(tmp_path / "best_submission")
    assert command[command.index("--results-md") + 1] == str(tmp_path / "results.md")
    candidate_values = [command[index + 1] for index, value in enumerate(command) if value == "--candidate-run-root"]
    assert len(candidate_values) == 2
    assert any(value.endswith("attention-short-default") for value in candidate_values)
    assert any(value.endswith("union-short-exploratory") for value in candidate_values)

    summary = json.loads((tmp_path / "summary" / "v3f_submission_line_summary.json").read_text(encoding="utf-8"))
    assert summary["mode"] == "package-stage2-matrix-best-submission"
    assert summary["used_default_stage2_profiles"] is False
    assert summary["all_profiles"] is False
    assert summary["selected_stage2_profiles"] == ["attention-short-default", "union-short-exploratory"]
    assert len(summary["candidate_run_roots"]) == 2


def test_v3f_submission_export_stage2_submission_dry_run_derives_paths(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    run_root = tmp_path / "stage2_run"
    result = v3f_submission.command_export_stage2_submission(
        SimpleNamespace(
            run_root=run_root,
            adapter_dir=None,
            output_root=None,
            reference_model_root=None,
            base_model_name_or_path=v3f_submission.BASE_MODEL_NAME,
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 1
    command, dry_run = calls[0]
    assert dry_run is True
    assert "export-peft-submission" in command
    assert command[command.index("--adapter-dir") + 1] == str(run_root / "adapter")
    assert command[command.index("--output-root") + 1] == str(run_root / "submission_export")
    assert command[command.index("--reference-model-root") + 1] == str(run_root / "shadow_model")
    assert command[command.index("--base-model-name-or-path") + 1] == v3f_submission.BASE_MODEL_NAME


def test_v3f_submission_launch_stage2_linked_dry_run_allows_group_override(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run_command(command: list[str], dry_run: bool) -> None:
        calls.append((command, dry_run))

    monkeypatch.setattr(v3f_submission, "run_command", fake_run_command)

    result = v3f_submission.command_launch_stage2_linked(
        SimpleNamespace(
            source_run_root=tmp_path / "stage1_run",
            train_csv=tmp_path / "stage2_dataset.csv",
            dataset_summary_json=tmp_path / "missing.json",
            output_root=tmp_path / "outputs",
            run_name="stage2_union_test",
            learning_rate=2e-5,
            num_epochs=0.75,
            max_seq_length=1536,
            valid_shadow_rows=1,
            lora_key_group="stage-union",
            trainable_lora_suffix_group="stage-union-exportsafe",
            poll_seconds=60.0,
            timeout_seconds=0.0,
            min_free_percent=None,
            min_free_gb=None,
            type_sample=["Bit Manipulation=34", "Equation Transformation=8"],
            summary_output_root=tmp_path / "summary",
            dry_run=True,
        )
    )

    assert result == 0
    assert len(calls) == 1
    command, dry_run = calls[0]
    assert dry_run is True
    assert command[command.index("--lora-key-group") + 1] == "stage-union"
    assert command[command.index("--trainable-lora-suffix-group") + 1] == "stage-union-exportsafe"


def test_v3f_submission_parse_args_accepts_write_stage2_matrix() -> None:
    args = v3f_submission.parse_args(["write-stage2-matrix", "--output-root", "matrix-output"])

    assert args.command == "write-stage2-matrix"
    assert args.output_root == "matrix-output"


def test_v3f_submission_parse_args_accepts_launch_stage2_matrix() -> None:
    args = v3f_submission.parse_args(
        [
            "launch-stage2-matrix",
            "--profile",
            "attention-short-default",
            "--profile",
            "union-short-exploratory",
            "--skip-postprocess",
            "--dry-run",
        ]
    )

    assert args.command == "launch-stage2-matrix"
    assert args.profile == ["attention-short-default", "union-short-exploratory"]
    assert args.all_profiles is False
    assert args.skip_postprocess is True
    assert args.dry_run is True


def test_v3f_submission_parse_args_accepts_launch_stage2_matrix_all_profiles() -> None:
    args = v3f_submission.parse_args(["launch-stage2-matrix", "--all-profiles", "--dry-run"])

    assert args.command == "launch-stage2-matrix"
    assert args.all_profiles is True
    assert args.profile == []
    assert args.dry_run is True


def test_v3f_submission_parse_args_accepts_package_stage2_matrix_best_submission() -> None:
    args = v3f_submission.parse_args(
        [
            "package-stage2-matrix-best-submission",
            "--profile",
            "attention-short-default",
            "--profile",
            "union-short-exploratory",
            "--no-update-results-md",
            "--dry-run",
        ]
    )

    assert args.command == "package-stage2-matrix-best-submission"
    assert args.profile == ["attention-short-default", "union-short-exploratory"]
    assert args.all_profiles is False
    assert args.update_results_md is False
    assert args.dry_run is True


def test_v3f_submission_parse_args_accepts_package_stage2_matrix_best_submission_all_profiles() -> None:
    args = v3f_submission.parse_args(
        ["package-stage2-matrix-best-submission", "--all-profiles", "--dry-run"]
    )

    assert args.command == "package-stage2-matrix-best-submission"
    assert args.all_profiles is True
    assert args.profile == []
    assert args.dry_run is True


def test_v3f_submission_parse_args_accepts_export_stage2_submission() -> None:
    args = v3f_submission.parse_args(
        ["export-stage2-submission", "--run-root", "baseline_mlx/outputs/custom_stage2", "--dry-run"]
    )

    assert args.command == "export-stage2-submission"
    assert args.run_root == "baseline_mlx/outputs/custom_stage2"
    assert args.dry_run is True


def test_monolith_build_corrective_stage2_parser_accepts_manual_ratio() -> None:
    args = stage_waiters.build_parser().parse_args(
        [
            "build-corrective-stage2-csv",
            "--output-csv",
            "artifacts/stage2.csv",
            "--max-manual-audit-ratio",
            "0.1",
        ]
    )

    assert args.command == "build-corrective-stage2-csv"
    assert args.max_manual_audit_ratio == 0.1
