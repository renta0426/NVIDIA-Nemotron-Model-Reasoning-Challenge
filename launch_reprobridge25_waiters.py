#!/usr/bin/env python3
"""
Launch missing reprobridge25 waiters.
This script launches three detached background processes for reprobridge25.
"""

import subprocess
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Repository root
REPO_ROOT = Path("/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge")
README_PATH = REPO_ROOT / "README.md"
OUTPUTS_BASE = REPO_ROOT / "baseline_mlx/outputs"
SUMMARY_SCHEMA_VERSION = 2
UV_PYTHON = ["uv", "run", "python"]
MAIN_ENTRYPOINT = str(REPO_ROOT / "main.py")
README_TABLE_KEYS = (
    "max_lora_rank",
    "max_tokens",
    "top_p",
    "temperature",
    "max_num_seqs",
    "gpu_memory_utilization",
    "max_model_len",
)
README_EVAL_CONTRACT: dict[str, Any] = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}
README_SUBMISSION_REQUIRED_FILES = ("adapter_config.json",)
README_SUBMISSION_ARCHIVE_NAME = "submission.zip"
README_SUBMISSION_CONTRACT: dict[str, Any] = {
    "required_files": list(README_SUBMISSION_REQUIRED_FILES),
    "max_lora_rank": 32,
    "single_adapter_submission_zip": True,
    "submission_archive_name": README_SUBMISSION_ARCHIVE_NAME,
}

# Log directory - use /tmp or a session-safe temp location
LOG_DIR = Path("/tmp/reprobridge25_launch_logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)

# Parameters from the task specification
RUN_NAME = "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1"
TRAIN_CSV = "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_v1.csv"
SOURCE_RUN_ROOT = "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1"
WAIT_SUMMARY_PATH = "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json"

# Type samples
TYPE_SAMPLES = {
    "Numeral Conversion": 0,
    "Gravitational Constant": 9,
    "Unit Conversion": 7,
    "Text Encryption": 18,
    "Bit Manipulation": 34,
    "Equation Transformation": 12,
}

# Hyperparameters
LR = "1e-6"
EPOCHS = "0.8"
MAX_SEQ_LENGTH = "1024"
VALID_SHADOW_ROWS = "8"
LORA_KEY_GROUP = "stage-union-exportsafe"
TRAINABLE_LORA_SUFFIX_GROUP = "attention"

# Live poller label
LIVE_POLLER_LABEL = "reprobridge25 raw6 unitedge"

# Results label for postprocess
RESULTS_LABEL = "o30best proxybench reprobridge25 raw6 unitedge v1"

# Extra benchmark CSV
EXTRA_BENCHMARK_CSV = "cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/leaderboard_proxy_v1/artifacts/leaderboard_proxy_v1_set.csv"

# Commit messages
PUBLISH_COMMIT_MSG_LIVE = "Record reprobridge25 raw6-unitedge live progress\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
PUBLISH_COMMIT_MSG_RESULTS = "Record reprobridge25 raw6-unitedge results\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_readme_contract_state(contract: dict[str, Any]) -> dict[str, Any]:
    expected_keys = sorted(README_EVAL_CONTRACT)
    actual_keys = sorted(contract)
    missing_keys = [key for key in expected_keys if key not in contract]
    unexpected_keys = [key for key in actual_keys if key not in README_EVAL_CONTRACT]
    mismatched_keys = [
        key for key in expected_keys if key in contract and contract.get(key) != README_EVAL_CONTRACT[key]
    ]
    return {
        "expected_key_count": len(expected_keys),
        "actual_key_count": len(actual_keys),
        "expected_keys": expected_keys,
        "actual_keys": actual_keys,
        "missing_keys": missing_keys,
        "unexpected_keys": unexpected_keys,
        "mismatched_keys": mismatched_keys,
        "matches_current_readme": not missing_keys and not unexpected_keys and not mismatched_keys,
    }


def load_readme_contract_from_readme() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    contract: dict[str, Any] = {}
    for key in README_TABLE_KEYS:
        expected_value = README_EVAL_CONTRACT[key]
        needle = f"{key}\t"
        for line in text.splitlines():
            if not line.startswith(needle):
                continue
            raw_value = line.split("\t", 1)[1].strip()
            require(raw_value != "", f"Malformed README.md evaluation row for {key}: missing value")
            try:
                if isinstance(expected_value, int) and not isinstance(expected_value, bool):
                    contract[key] = int(raw_value)
                elif isinstance(expected_value, float):
                    contract[key] = float(raw_value)
                else:
                    contract[key] = raw_value
            except ValueError as exc:
                raise SystemExit(f"Malformed README.md evaluation value for {key}: {raw_value!r}") from exc
            break
    missing_keys = [key for key in README_TABLE_KEYS if key not in contract]
    require(not missing_keys, f"Missing README.md evaluation rows: {', '.join(missing_keys)}")
    return contract


def verify_readme_contract_file() -> dict[str, Any]:
    contract = load_readme_contract_from_readme()
    for key in README_TABLE_KEYS:
        expected_value = README_EVAL_CONTRACT[key]
        actual_value = contract.get(key)
        require(
            actual_value == expected_value,
            f"README.md evaluation table mismatch for {key}: expected {expected_value}, got {actual_value}",
        )
    return contract


def load_readme_submission_contract_from_readme() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()
    require(
        "adapter_config.json" in text,
        "README.md submitting contract no longer states that the LoRA adapter must include adapter_config.json.",
    )
    require(
        README_SUBMISSION_ARCHIVE_NAME.lower() in lower_text,
        f"README.md submitting contract no longer states that the submission archive is {README_SUBMISSION_ARCHIVE_NAME}.",
    )
    require(
        "submit a lora adapter" in lower_text,
        "README.md submitting contract no longer states that the submission is a single LoRA adapter.",
    )
    return {
        "required_files": list(README_SUBMISSION_REQUIRED_FILES),
        "max_lora_rank": int(load_readme_contract_from_readme()["max_lora_rank"]),
        "single_adapter_submission_zip": True,
        "submission_archive_name": README_SUBMISSION_ARCHIVE_NAME,
    }


def verify_readme_submission_contract_file() -> dict[str, Any]:
    contract = load_readme_submission_contract_from_readme()
    require(
        int(contract["max_lora_rank"]) == int(README_SUBMISSION_CONTRACT["max_lora_rank"]),
        "README.md submission contract mismatch for max_lora_rank: "
        f"expected {README_SUBMISSION_CONTRACT['max_lora_rank']}, got {contract['max_lora_rank']}",
    )
    require(
        str(contract["submission_archive_name"]) == str(README_SUBMISSION_CONTRACT["submission_archive_name"]),
        "README.md submission contract mismatch for submission_archive_name: "
        f"expected {README_SUBMISSION_CONTRACT['submission_archive_name']}, got {contract['submission_archive_name']}",
    )
    require(
        bool(contract["single_adapter_submission_zip"]) is True,
        "README.md submission contract mismatch for single_adapter_submission_zip: expected true.",
    )
    return contract


def summarize_wait_summary_gate(path: Path) -> dict[str, Any]:
    gate: dict[str, Any] = {"path": str(path)}
    if not path.exists():
        gate.update(
            {
                "exists": False,
                "gate_status": "waiting_for_summary",
                "ready_for_launch": True,
                "created_at": None,
                "readme_contract": None,
                "readme_contract_verified_from_readme_file": None,
                "readme_contract_state": None,
                "evaluations": [],
            }
        )
        return gate
    try:
        payload = load_json(path)
    except FileNotFoundError:
        gate.update(
            {
                "exists": False,
                "gate_status": "waiting_for_summary",
                "ready_for_launch": True,
                "created_at": None,
                "readme_contract": None,
                "readme_contract_verified_from_readme_file": None,
                "readme_contract_state": None,
                "evaluations": [],
            }
        )
        return gate
    except json.JSONDecodeError as exc:
        gate.update(
            {
                "exists": True,
                "gate_status": "existing_summary_parse_error",
                "ready_for_launch": False,
                "error": f"benchmark_eval_suite_summary.json could not be parsed: {exc}",
                "created_at": None,
                "readme_contract": None,
                "readme_contract_verified_from_readme_file": None,
                "readme_contract_state": None,
                "evaluations": [],
            }
        )
        return gate
    if not isinstance(payload, dict):
        gate.update(
            {
                "exists": True,
                "gate_status": "existing_summary_not_json_object",
                "ready_for_launch": False,
                "error": "benchmark_eval_suite_summary.json is not a JSON object",
                "created_at": None,
                "readme_contract": None,
                "readme_contract_verified_from_readme_file": None,
                "readme_contract_state": None,
                "evaluations": [],
            }
        )
        return gate
    evaluations = payload.get("evaluations", [])
    evaluation_excerpt = []
    if isinstance(evaluations, list):
        evaluation_excerpt = [
            {
                "evaluation_name": item.get("evaluation_name"),
                "rows": item.get("rows"),
                "correct": item.get("correct"),
                "accuracy": item.get("accuracy"),
            }
            for item in evaluations
            if isinstance(item, dict)
        ]
    contract = payload.get("readme_contract")
    contract_state = build_readme_contract_state(contract) if isinstance(contract, dict) else None
    verified = payload.get("readme_contract_verified_from_readme_file")
    gate.update(
        {
            "exists": True,
            "created_at": payload.get("created_at"),
            "readme_contract": contract if isinstance(contract, dict) else None,
            "readme_contract_verified_from_readme_file": verified,
            "readme_contract_state": contract_state,
            "evaluations": evaluation_excerpt,
        }
    )
    if not isinstance(contract, dict):
        gate["gate_status"] = "existing_summary_missing_readme_contract"
        gate["ready_for_launch"] = False
        return gate
    if verified is not True:
        gate["gate_status"] = "existing_summary_missing_readme_verification"
        gate["ready_for_launch"] = False
        return gate
    if contract_state is None or contract_state["matches_current_readme"] is not True:
        gate["gate_status"] = "existing_summary_readme_contract_mismatch"
        gate["ready_for_launch"] = False
        return gate
    gate["gate_status"] = "existing_summary_verified"
    gate["ready_for_launch"] = True
    return gate


def verify_wait_summary_gate(wait_summary_gate: dict[str, Any]) -> None:
    require(
        wait_summary_gate.get("ready_for_launch") is True,
        "WAIT_SUMMARY_PATH is not README-verified under the current contract: "
        f"{wait_summary_gate.get('gate_status')}",
    )


def build_launch_summary(
    *,
    launch_status: str,
    existing_processes: list[str],
    launched_waiters: dict[str, dict[str, Any]],
    reprobridge25_processes: list[str],
    active_readme_eval_contract: dict[str, Any],
    active_readme_submission_contract: dict[str, Any],
    wait_summary_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "launch_time": datetime.now().isoformat(),
        "repo_root": str(REPO_ROOT),
        "readme_path": str(README_PATH),
        "log_directory": str(LOG_DIR),
        "launch_status": launch_status,
        "active_readme_eval_contract": active_readme_eval_contract,
        "active_readme_submission_contract": active_readme_submission_contract,
        "wait_summary_gate": wait_summary_gate,
        "existing_process_count": len(existing_processes),
        "existing_processes": existing_processes[:10],
        "launched_waiters": launched_waiters,
        "processes_found": len(reprobridge25_processes),
        "reprobridge25_processes": reprobridge25_processes[:10],
    }


def waiter_result_payload(results: dict[str, tuple[int | None, Path]]) -> dict[str, dict[str, Any]]:
    return {
        "waiter_a": {
            "name": "wait-resume-train-from-path",
            "pid": results["waiter_a"][0],
            "log": str(results["waiter_a"][1]),
            "launched": results["waiter_a"][0] is not None,
        },
        "waiter_b": {
            "name": "poll-live-run-status",
            "pid": results["waiter_b"][0],
            "log": str(results["waiter_b"][1]),
            "launched": results["waiter_b"][0] is not None,
        },
        "waiter_c": {
            "name": "postprocess-run",
            "pid": results["waiter_c"][0],
            "log": str(results["waiter_c"][1]),
            "launched": results["waiter_c"][0] is not None,
        },
    }


def main_command(*args: str) -> list[str]:
    return [*UV_PYTHON, MAIN_ENTRYPOINT, *args]


def check_existing_processes():
    """Check if any reprobridge25 waiter processes already exist."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split('\n')
        reprobridge25_procs = [l for l in lines if 'reprobridge25' in l.lower()]
        return reprobridge25_procs
    except Exception as e:
        print(f"Warning: Could not check existing processes: {e}")
        return []


def launch_waiter_with_nohup(cmd_list, waiter_name):
    """Launch a waiter process using nohup."""
    log_file = LOG_DIR / f"{waiter_name}.log"
    
    # Build nohup command
    nohup_cmd = ['nohup'] + cmd_list
    
    try:
        # Launch with nohup, redirecting stdout and stderr to log file
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                nohup_cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid,  # Create new process group (detach from parent)
                cwd=str(REPO_ROOT)
            )
        
        # Give it a moment to start
        time.sleep(0.5)
        
        # Check if process started successfully
        if process.poll() is None:
            pid = process.pid
            print(f"  ✓ Launched {waiter_name}")
            print(f"    PID: {pid}")
            print(f"    Log: {log_file}")
            return pid, log_file
        else:
            # Process exited immediately
            returncode = process.poll()
            with open(log_file, 'r') as f:
                error_output = f.read()
            print(f"  ✗ Failed to launch {waiter_name}")
            print(f"    Return code: {returncode}")
            print(f"    Error output: {error_output[:500]}")
            return None, log_file
    
    except Exception as e:
        print(f"  ✗ Exception launching {waiter_name}: {e}")
        return None, log_file


def build_type_samples_args():
    """Build type samples arguments for main.py."""
    args = []
    for sample_type, count in TYPE_SAMPLES.items():
        args.extend(['--type-samples', sample_type, str(count)])
    return args


def launch_waiter_a():
    """
    A. wait-resume-train-from-path behind reprobridge24 full-suite summary with free memory >= 150 GB
    """
    print("\nLaunching Waiter A: wait-resume-train-from-path")
    
    cmd = main_command(
        '--action', 'wait-resume-train-from-path',
        '--run-name', RUN_NAME,
        '--train-csv', TRAIN_CSV,
        '--source-run-root', SOURCE_RUN_ROOT,
        '--wait-summary-path', WAIT_SUMMARY_PATH,
        '--memory-requirement-gb', '150',
        '--lr', LR,
        '--epochs', EPOCHS,
        '--max-seq-length', MAX_SEQ_LENGTH,
        '--valid-shadow-rows', VALID_SHADOW_ROWS,
        '--lora-key-group', LORA_KEY_GROUP,
        '--trainable-lora-suffix-group', TRAINABLE_LORA_SUFFIX_GROUP,
    ) + build_type_samples_args()
    
    return launch_waiter_with_nohup(cmd, 'waiter-a-resume-train')


def launch_waiter_b():
    """
    B. wait-for-path prepare_manifest -> poll-live-run-status
    """
    print("\nLaunching Waiter B: wait-for-path prepare_manifest -> poll-live-run-status")
    
    cmd = main_command(
        '--action', 'poll-live-run-status',
        '--run-name', RUN_NAME,
        '--live-poller-label', LIVE_POLLER_LABEL,
    )
    
    return launch_waiter_with_nohup(cmd, 'waiter-b-poll-live-status')


def launch_waiter_c():
    """
    C. wait-for-path prepare_manifest -> postprocess-run
    """
    print("\nLaunching Waiter C: wait-for-path prepare_manifest -> postprocess-run")
    
    cmd = main_command(
        '--action', 'postprocess-run',
        '--run-name', RUN_NAME,
        '--train-csv', TRAIN_CSV,
        '--results-label', RESULTS_LABEL,
        '--extra-benchmark-csv', EXTRA_BENCHMARK_CSV,
        '--publish-commit-msg', PUBLISH_COMMIT_MSG_RESULTS,
    )
    
    return launch_waiter_with_nohup(cmd, 'waiter-c-postprocess')


def verify_processes():
    """Verify that the launched processes are running."""
    print("\n=== Verifying Processes ===")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split('\n')
        reprobridge25_procs = [l for l in lines if 'reprobridge25' in l.lower()]
        
        if reprobridge25_procs:
            print(f"Found {len(reprobridge25_procs)} reprobridge25-related processes:")
            for line in reprobridge25_procs:
                print(f"  {line[:150]}")
        else:
            print("No reprobridge25 processes found in ps output")
        
        return reprobridge25_procs
    except Exception as e:
        print(f"Error verifying processes: {e}")
        return []


def main():
    print("=" * 80)
    print("ReproBridge25 Waiter Recovery Script")
    print(f"Start time: {datetime.now().isoformat()}")
    print("=" * 80)

    active_readme_eval_contract = verify_readme_contract_file()
    active_readme_submission_contract = verify_readme_submission_contract_file()
    wait_summary_gate = summarize_wait_summary_gate(REPO_ROOT / WAIT_SUMMARY_PATH)
    summary_file = LOG_DIR / "launch_summary.json"
    
    # Check for existing processes
    print("\n=== Checking for Existing Processes ===")
    existing = check_existing_processes()
    if existing:
        print(f"Found {len(existing)} existing reprobridge processes:")
        for proc in existing[:5]:  # Show first 5
            print(f"  {proc[:120]}")
        if len(existing) > 5:
            print(f"  ... and {len(existing) - 5} more")
    else:
        print("No reprobridge processes found")

    if wait_summary_gate["ready_for_launch"] is not True:
        summary = build_launch_summary(
            launch_status="blocked_by_wait_summary_gate",
            existing_processes=existing,
            launched_waiters={
                "waiter_a": {
                    "name": "wait-resume-train-from-path",
                    "pid": None,
                    "log": str(LOG_DIR / "waiter-a-resume-train.log"),
                    "launched": False,
                },
                "waiter_b": {
                    "name": "poll-live-run-status",
                    "pid": None,
                    "log": str(LOG_DIR / "waiter-b-poll-live-status.log"),
                    "launched": False,
                },
                "waiter_c": {
                    "name": "postprocess-run",
                    "pid": None,
                    "log": str(LOG_DIR / "waiter-c-postprocess.log"),
                    "launched": False,
                },
            },
            reprobridge25_processes=[],
            active_readme_eval_contract=active_readme_eval_contract,
            active_readme_submission_contract=active_readme_submission_contract,
            wait_summary_gate=wait_summary_gate,
        )
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        verify_wait_summary_gate(wait_summary_gate)
    
    # Launch the three waiters
    print("\n" + "=" * 80)
    print("Launching Waiters")
    print("=" * 80)
    
    results = {}
    results['waiter_a'] = launch_waiter_a()
    results['waiter_b'] = launch_waiter_b()
    results['waiter_c'] = launch_waiter_c()
    
    # Verify they're running
    time.sleep(2)
    procs = verify_processes()
    
    # Write summary to file
    summary = build_launch_summary(
        launch_status="waiters_launched",
        existing_processes=existing,
        launched_waiters=waiter_result_payload(results),
        reprobridge25_processes=procs,
        active_readme_eval_contract=active_readme_eval_contract,
        active_readme_submission_contract=active_readme_submission_contract,
        wait_summary_gate=wait_summary_gate,
    )
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Summary file: {summary_file}")
    print(f"Launched waiters:")
    for name, (pid, log) in results.items():
        status = "✓" if pid else "✗"
        print(f"  {status} {name}: PID={pid if pid else 'FAILED'}")
    print(f"\nLog directory: {LOG_DIR}")
    print(f"End time: {datetime.now().isoformat()}")


if __name__ == '__main__':
    main()
