from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
import zipfile


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
                prompt_chunk_size=16,
                prefill_batch_size=16,
                completion_batch_size=16,
                force_single_generate=False,
                max_tokens=32,
                max_model_len=stage_waiters.README_MAX_MODEL_LEN,
                model_root=Path("model"),
                adapter_dir=None,
            ),
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
                max_model_len=stage_waiters.README_MAX_MODEL_LEN,
                prompt_chunk_size=8,
                prefill_batch_size=8,
                completion_batch_size=8,
                eval_enable_thinking=True,
                force_single_generate=False,
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
    assert suite_progress["status"] == "completed"
    assert suite_progress["evaluations_completed"] == 1
    assert suite_progress["current_evaluation"] == "readme_local320"
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
