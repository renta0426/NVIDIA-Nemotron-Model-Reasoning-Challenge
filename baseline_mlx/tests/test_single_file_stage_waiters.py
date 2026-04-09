from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace


MODULE_PATH = Path(__file__).resolve().parents[1] / "reproduce_nemotron_sft_lora_with_cot_v2_mlx.py"
SPEC = importlib.util.spec_from_file_location("baseline_mlx_stage_waiters", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
stage_waiters = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stage_waiters
SPEC.loader.exec_module(stage_waiters)


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


def build_wait_train_args(source_run: Path, output_root: Path, run_name: str, **overrides) -> SimpleNamespace:
    payload = {
        "source_run_root": source_run,
        "output_root": output_root,
        "run_name": run_name,
        "poll_seconds": 0.1,
        "timeout_seconds": 1.0,
        "wait_status_json": None,
        "skip_if_target_started": True,
        "dry_run": True,
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
        "run_eval_suite": True,
        "benchmark_root": stage_waiters.PHASE0_OFFLINE_EVAL_ARTIFACT_ROOT,
        "extra_benchmark_csv": None,
        "suite_output_root": None,
        "max_tokens": stage_waiters.README_MAX_TOKENS,
        "temperature": stage_waiters.README_TEMPERATURE,
        "top_p": stage_waiters.README_TOP_P,
        "max_num_seqs": stage_waiters.README_MAX_NUM_SEQS,
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
        "results_md": stage_waiters.REPO_ROOT / "versions" / "baseline_mlx" / "baseline_mlx-results.md",
        "run_package_best_submission": False,
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
