from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
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
    write_benchmark_eval_summary(proxy_root, rows=proxy_rows, correct=proxy_correct)
    write_benchmark_eval_summary(specialized_root, rows=specialized_rows, correct=specialized_correct)

    (run_root / "eval_suite_readme_proxy_specialized" / "benchmark_eval_suite_summary.json").write_text(
        json.dumps(
            {
                "evaluations": [
                    {"evaluation_name": "readme_local320", "output_root": str(local320_root.resolve())},
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
