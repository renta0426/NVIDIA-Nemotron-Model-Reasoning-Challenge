#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import shlex
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
MONOLITH_PATH = REPO_ROOT / "baseline_mlx" / "reproduce_nemotron_sft_lora_with_cot_v2_mlx.py"
SELF_RELPATH = Path("versions") / "v3f_submission_line_v1" / "reproduce_v3f_submission_line.py"
SELF_PATH = REPO_ROOT / SELF_RELPATH
RESULTS_MD = REPO_ROOT / "versions" / "baseline_mlx" / "baseline_mlx-results.md"
BASE_MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"

SOURCE_BASE_RUN_ROOT = (
    REPO_ROOT / "baseline_mlx" / "outputs" / "nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2"
)
STAGE1_DATASET_CSV = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "artifacts"
    / "train_split_with_cot_v3f_safe_plus_notformula.csv"
)
SPECIALIZED_CSV = (
    REPO_ROOT
    / "baseline"
    / "cot"
    / "phase0_offline_eval"
    / "artifacts"
    / "binary_bias_specialized_set.csv"
)
CORRECTION_MD = (
    REPO_ROOT
    / "cuda-train-data-analysis-v1"
    / "proof_first_solver_factory_routing"
    / "result"
    / "LEADERBOARD_GAP_INVESTIGATION_2026-04-09.md"
)
STRATEGY_MD = (
    REPO_ROOT
    / "baseline"
    / "single_lora_stage_freeze_unfreeze"
    / "plan.md"
)
ARTIFACT_ROOT = REPO_ROOT / "baseline_mlx" / "outputs" / "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v3_artifacts"
DEFAULT_RUN_SUITE_SUMMARY_RELPATH = (
    Path("eval_suite_readme_proxy_specialized") / "benchmark_eval_suite_summary.json"
)
DEFAULT_RUN_AUDIT_RELPATH = Path("submission_compat_audit") / "submission_compat_audit.json"
DEFAULT_RUN_EXPORT_RELPATH = Path("submission_export") / "export_manifest.json"
DEFAULT_RUN_RECORDED_RESULT_RELPATH = Path("recorded_run_result.json")

STAGE1_RUN_NAME = (
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v3_stage1_broad_exportsafe_v3f_union_from_fullrun_v2"
)
STAGE2_DATASET_STEM = "stagefreeze_v3_v3f_corrective_qkvo_proxyv2_v1"
PROXY_V2_STEM = "stagefreeze_v3_v3f_leaderboard_proxy_v2_v1"
STAGE2_RUN_NAME = (
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v3_stage2_attention_qkvo_"
    "v3f_proxyv2_corrective_lr2e5_len1536_from_stage1_v1"
)

PROXY_V2_CSV = ARTIFACT_ROOT / f"{PROXY_V2_STEM}.csv"
PROXY_V2_SUMMARY_JSON = ARTIFACT_ROOT / f"{PROXY_V2_STEM}_summary.json"
STAGE2_DATASET_CSV = ARTIFACT_ROOT / f"{STAGE2_DATASET_STEM}.csv"
STAGE2_DATASET_SUMMARY_JSON = ARTIFACT_ROOT / f"{STAGE2_DATASET_STEM}_summary.json"
HISTORICAL_ATTENTION_WARNING_RUN_ROOT = (
    REPO_ROOT / "baseline_mlx" / "outputs" / "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3"
)
HISTORICAL_ATTENTION_WARNING_SUMMARY_JSON = (
    HISTORICAL_ATTENTION_WARNING_RUN_ROOT
    / "eval_suite_readme_proxy_specialized"
    / "benchmark_eval_suite_summary.json"
)

README_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}
SUMMARY_SCHEMA_VERSION = 2
EXPECTED_SUBMISSION_ADAPTER_CONFIG = {
    "peft_type": "LORA",
    "task_type": "CAUSAL_LM",
    "inference_mode": True,
}
EXPECTED_RECORDED_EVAL_ASSUMPTIONS = {
    "temperature": README_CONTRACT["temperature"],
    "top_p": README_CONTRACT["top_p"],
    "max_tokens": README_CONTRACT["max_tokens"],
    "max_num_seqs": README_CONTRACT["max_num_seqs"],
    "max_model_len": README_CONTRACT["max_model_len"],
    "eval_enable_thinking": True,
}
REQUIRED_STAGE2_EVALUATIONS = {
    "readme_local320": {
        "required_component_benchmarks": ["general_stable_set", "binary_hard_set", "symbol_watch_set"],
    },
    "leaderboard_proxy_v2": {
        "required_component_benchmarks": [],
    },
    "binary_bias_specialized_set": {
        "required_component_benchmarks": [],
    },
}

V3F_ANCHORS = {
    "stored_phase0_local320": {"correct": 249, "rows": 320, "accuracy": 249 / 320},
    "corrected_phase0_local320": {"correct": 240, "rows": 320, "accuracy": 240 / 320},
    "proxy_actual": {"correct": 133, "rows": 200, "accuracy": 133 / 200},
    "specialized563": {"correct": 238, "rows": 563, "accuracy": 238 / 563},
    "supported_not_structured": {"correct": 1, "rows": 55, "accuracy": 1 / 55},
    "binary_structured_byte_not_formula": {"correct": 1, "rows": 25, "accuracy": 1 / 25},
}
PROMPT_ROUTER_V6_BLUEPRINT = {
    "local320": {"correct": 293, "rows": 320, "accuracy": 293 / 320},
    "binary60": {"correct": 54, "rows": 60, "accuracy": 54 / 60},
    "gain_vs_v5": {"gain": 23, "loss": 0},
    "solver_fallback_counts": {
        "binary_formula_consensus_solver": 35,
        "symbol_numeric_zero_error_solver": 12,
    },
    "binary_gain_breakdown": {
        "answer_only_keep": 10,
        "manual_audit_priority": 8,
        "verified_trace_ready": 5,
    },
    "submission_compatible": False,
}
SINGLE_ADAPTER_TRANSFER_PRIORS = {
    "primary_failure_mode": "format_ok_content_wrong",
    "primary_lane": "exact-route verified rows",
    "helper_lane": "low-ratio answer-only",
    "bit_other_answer_only_keep_overlap_rows": 52,
    "portable_new_signal_centers_on": [
        "bit_other manual_audit_priority",
        "bit_other verified_trace_ready",
    ],
    "avoid_repeating": [
        "coarse route_closure_only expansion",
        "answer_only_keep duplicates already present in the current phase2 train CSV",
    ],
}

PROXY_V2_FOCUS_BUCKETS = (
    "dominant_structured_safe",
    "dominant_structured_abstract",
    "supported_not_structured",
    "supported_affine_xor",
    "supported_bijection",
)
STAGE2_BINARY_SOLVERS = (
    "binary_affine_xor",
    "binary_bit_permutation_bijection",
    "binary_structured_byte_formula",
    "binary_structured_byte_formula_abstract",
    "binary_structured_byte_not_formula",
)
DEFAULT_STAGE1_LORA_KEY_GROUP = "stage-union-exportsafe"
DEFAULT_STAGE1_TRAINABLE_LORA_SUFFIX_GROUP = "broad-exportsafe"
DEFAULT_STAGE2_LORA_KEY_GROUP = "stage-union-exportsafe"
DEFAULT_STAGE2_TRAINABLE_LORA_SUFFIX_GROUP = "attention"
DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO = 0.0
DEFAULT_STAGE2_MANUAL_AUDIT_TEMPLATE_SUBTYPES = ("bit_other",)
DEFAULT_STAGE2_MATRIX_PROFILE_NAMES = (
    "attention-short-default",
    "attention-short-noanswer",
    "attention-short-manual",
)
DEFAULT_STAGE2_CANDIDATE_GATES = {
    "min_local320_accuracy": 215 / 320,
    "min_general_stable_accuracy": 0.96,
    "min_proxy_v2_accuracy": 0.50,
    "min_specialized_accuracy": 0.42,
    "require_exportable": True,
}
_MONOLITH_SUBMISSION_HELPERS: ModuleType | None = None
STAGE2_PROFILE_LIBRARY: dict[str, dict[str, Any]] = {
    "attention-short-default": {
        "description": "Plan-aligned narrow attention-only corrective phase.",
        "stage2_lora_key_group": "stage-union-exportsafe",
        "stage2_trainable_lora_suffix_group": "attention",
        "stage2_learning_rate": 2e-5,
        "stage2_num_epochs": 0.75,
        "stage2_max_seq_length": 1536,
        "stage2_max_symbol_rows": 9,
        "stage2_max_answer_only_ratio": 0.05,
        "stage2_max_manual_audit_ratio": DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO,
    },
    "attention-short-noanswer": {
        "description": "Exact-route-first attention-only corrective phase with no answer-only helper rows.",
        "stage2_lora_key_group": "stage-union-exportsafe",
        "stage2_trainable_lora_suffix_group": "attention",
        "stage2_learning_rate": 2e-5,
        "stage2_num_epochs": 0.75,
        "stage2_max_seq_length": 1536,
        "stage2_max_symbol_rows": 9,
        "stage2_max_answer_only_ratio": 0.0,
        "stage2_max_manual_audit_ratio": DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO,
    },
    "attention-short-manual": {
        "description": "Exact-route-first attention-only lane with a small bit_other manual-audit helper slice for portable prompt-router-v6 signal transfer.",
        "stage2_lora_key_group": "stage-union-exportsafe",
        "stage2_trainable_lora_suffix_group": "attention",
        "stage2_learning_rate": 2e-5,
        "stage2_num_epochs": 0.75,
        "stage2_max_seq_length": 1536,
        "stage2_max_symbol_rows": 9,
        "stage2_max_answer_only_ratio": 0.0,
        "stage2_max_manual_audit_ratio": 0.10,
    },
    "attention-short-lowlr": {
        "description": "Same narrow attention-only phase with lower LR for drift-sensitive comparisons.",
        "stage2_lora_key_group": "stage-union-exportsafe",
        "stage2_trainable_lora_suffix_group": "attention",
        "stage2_learning_rate": 1e-5,
        "stage2_num_epochs": 0.75,
        "stage2_max_seq_length": 1536,
        "stage2_max_symbol_rows": 9,
        "stage2_max_answer_only_ratio": 0.05,
        "stage2_max_manual_audit_ratio": DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO,
    },
    "union-short-exploratory": {
        "description": "Exploratory exportsafe union corrective phase for post-recovery comparisons.",
        "stage2_lora_key_group": "stage-union-exportsafe",
        "stage2_trainable_lora_suffix_group": "stage-union-exportsafe",
        "stage2_learning_rate": 1e-5,
        "stage2_num_epochs": 0.5,
        "stage2_max_seq_length": 1536,
        "stage2_max_symbol_rows": 9,
        "stage2_max_answer_only_ratio": 0.05,
        "stage2_max_manual_audit_ratio": DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO,
    },
    "attention-vo-historical": {
        "description": "VO-only historical branch retained as a controlled exploratory lane.",
        "stage2_lora_key_group": "stage-union-exportsafe",
        "stage2_trainable_lora_suffix_group": "attention-vo",
        "stage2_learning_rate": 2e-5,
        "stage2_num_epochs": 3.6,
        "stage2_max_seq_length": 1536,
        "stage2_max_symbol_rows": 9,
        "stage2_max_answer_only_ratio": 0.05,
        "stage2_max_manual_audit_ratio": DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO,
    },
}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def repo_relpath(value: str | Path) -> str:
    path = repo_path(value)
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def approx_equal(lhs: float, rhs: float, tol: float = 1e-6) -> bool:
    return math.isclose(lhs, rhs, rel_tol=0.0, abs_tol=tol)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def format_inline_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def build_readme_contract_state(contract: dict[str, Any]) -> dict[str, Any]:
    expected_keys = sorted(README_CONTRACT)
    actual_keys = sorted(contract)
    missing_keys = [key for key in expected_keys if key not in contract]
    unexpected_keys = [key for key in actual_keys if key not in README_CONTRACT]
    mismatched_keys = [
        key for key in expected_keys if key in contract and contract.get(key) != README_CONTRACT[key]
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
    for key, expected_value in README_CONTRACT.items():
        needle = f"{key}\t"
        for line in text.splitlines():
            if line.startswith(needle):
                parts = line.split("\t", 1)
                require(len(parts) == 2, f"Malformed README.md evaluation row for {key}: {line!r}")
                raw_value = parts[1].strip()
                require(raw_value != "", f"Malformed README.md evaluation row for {key}: missing value")
                try:
                    if isinstance(expected_value, int) and not isinstance(expected_value, bool):
                        contract[key] = int(raw_value)
                    else:
                        contract[key] = float(raw_value)
                except ValueError as exc:
                    raise SystemExit(f"Malformed README.md evaluation value for {key}: {raw_value!r}") from exc
                break
    missing_keys = [key for key in README_CONTRACT if key not in contract]
    require(
        not missing_keys,
        f"Missing README.md evaluation rows: {', '.join(missing_keys)}",
    )
    return contract


def verify_readme_contract_file() -> dict[str, Any]:
    contract = load_readme_contract_from_readme()
    for key, expected_value in README_CONTRACT.items():
        actual_value = contract.get(key)
        require(
            actual_value == expected_value,
            f"README.md evaluation table mismatch for {key}: expected {expected_value}, got {actual_value}",
        )
    return contract


def uv_command(*args: str | Path) -> list[str]:
    return ["uv", "run", "python", str(MONOLITH_PATH), *[str(arg) for arg in args]]


def self_uv_command(*args: str | Path) -> list[str]:
    return ["uv", "run", "python", str(SELF_PATH), *[str(arg) for arg in args]]


def run_command(command: list[str], dry_run: bool) -> None:
    print("$", " ".join(shlex.quote(part) for part in command))
    if dry_run:
        return
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_monolith_submission_helpers() -> ModuleType:
    global _MONOLITH_SUBMISSION_HELPERS
    if _MONOLITH_SUBMISSION_HELPERS is None:
        spec = importlib.util.spec_from_file_location(
            "v3f_submission_line_monolith_submission_helpers",
            MONOLITH_PATH,
        )
        require(spec is not None and spec.loader is not None, f"Unable to load monolith from {MONOLITH_PATH}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _MONOLITH_SUBMISSION_HELPERS = module
    return _MONOLITH_SUBMISSION_HELPERS


def parse_metric_cell(cell: str) -> dict[str, Any]:
    match = re.fullmatch(r"(\d+)/(\d+)\s*=\s*([0-9.]+)", cell.strip())
    require(match is not None, f"Unexpected metric cell: {cell!r}")
    correct, rows, accuracy = match.groups()
    return {"correct": int(correct), "rows": int(rows), "accuracy": float(accuracy)}


def parse_correction_rows() -> dict[str, Any]:
    text = CORRECTION_MD.read_text(encoding="utf-8")
    corrected_match = re.search(
        r"\| `v3f` \| `(?P<stored>[^`]+)` \| `(?P<corrected>[^`]+)` \| `(?P<binary>[^`]+)` \|",
        text,
    )
    proxy_match = re.search(
        r"\| `v3f` \| `(?P<design>143/200 = 0\.7150)` \| `(?P<actual>133/200 = 0\.6650)` \|",
        text,
    )
    require(corrected_match is not None, f"Missing corrected v3f row in {CORRECTION_MD}")
    require(proxy_match is not None, f"Missing proxy v3f row in {CORRECTION_MD}")
    return {
        "stored_phase0_local320": parse_metric_cell(corrected_match.group("stored")),
        "corrected_phase0_local320": parse_metric_cell(corrected_match.group("corrected")),
        "corrected_binary_hard": parse_metric_cell(corrected_match.group("binary")),
        "proxy_design": parse_metric_cell(proxy_match.group("design")),
        "proxy_actual": parse_metric_cell(proxy_match.group("actual")),
    }


def find_evaluation(summary: dict[str, Any], evaluation_name: str) -> dict[str, Any]:
    for evaluation in summary.get("evaluations", []):
        if evaluation.get("evaluation_name") == evaluation_name:
            return evaluation
    raise SystemExit(f"Missing evaluation {evaluation_name!r} in historical summary")


def verify_metric(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    require(actual["correct"] == expected["correct"], f"{label} correct mismatch: {actual}")
    require(actual["rows"] == expected["rows"], f"{label} rows mismatch: {actual}")
    require(
        approx_equal(float(actual["accuracy"]), float(expected["accuracy"]), tol=1e-4),
        f"{label} accuracy mismatch: {actual}",
    )


def build_summary() -> dict[str, Any]:
    for path in (
        README_PATH,
        MONOLITH_PATH,
        SOURCE_BASE_RUN_ROOT,
        STAGE1_DATASET_CSV,
        SPECIALIZED_CSV,
        CORRECTION_MD,
        STRATEGY_MD,
        HISTORICAL_ATTENTION_WARNING_SUMMARY_JSON,
    ):
        require(path.exists(), f"Required path does not exist: {path}")

    verify_readme_contract_file()
    correction_rows = parse_correction_rows()
    historical_attention_summary = load_json(HISTORICAL_ATTENTION_WARNING_SUMMARY_JSON)
    historical_attention_local320 = find_evaluation(historical_attention_summary, "readme_local320")
    historical_attention_proxy_v2 = find_evaluation(historical_attention_summary, "leaderboard_proxy_v2")
    historical_attention_specialized = find_evaluation(historical_attention_summary, "binary_bias_specialized_set")
    verify_metric(correction_rows["stored_phase0_local320"], V3F_ANCHORS["stored_phase0_local320"], "stored_phase0")
    verify_metric(
        correction_rows["corrected_phase0_local320"],
        V3F_ANCHORS["corrected_phase0_local320"],
        "corrected_phase0",
    )
    verify_metric(correction_rows["proxy_actual"], V3F_ANCHORS["proxy_actual"], "proxy_actual")

    return {
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "readme_path": str(README_PATH),
        "readme_contract_verified_from_readme_file": True,
        "monolith_path": str(MONOLITH_PATH),
        "results_md": str(RESULTS_MD),
        "source_base_run_root": str(SOURCE_BASE_RUN_ROOT),
        "stage1_dataset_csv": str(STAGE1_DATASET_CSV),
        "stage1_run_name": STAGE1_RUN_NAME,
        "stage2_dataset_csv": str(STAGE2_DATASET_CSV),
        "stage2_dataset_summary_json": str(STAGE2_DATASET_SUMMARY_JSON),
        "proxy_v2_csv": str(PROXY_V2_CSV),
        "proxy_v2_summary_json": str(PROXY_V2_SUMMARY_JSON),
        "specialized_csv": str(SPECIALIZED_CSV),
        "stage2_run_name": STAGE2_RUN_NAME,
        "base_model_name_or_path": BASE_MODEL_NAME,
        "readme_contract": README_CONTRACT,
        "readme_contract_state": build_readme_contract_state(README_CONTRACT),
        "v3f_anchors": V3F_ANCHORS,
        "prompt_router_v6_blueprint": PROMPT_ROUTER_V6_BLUEPRINT,
        "single_adapter_transfer_priors": SINGLE_ADAPTER_TRANSFER_PRIORS,
        "correction_rows": correction_rows,
        "proxy_v2_focus_buckets": list(PROXY_V2_FOCUS_BUCKETS),
        "stage2_binary_solvers": list(STAGE2_BINARY_SOLVERS),
        "stage2_profile_matrix": build_stage2_profile_matrix(),
        "stage2_candidate_gate_defaults": dict(DEFAULT_STAGE2_CANDIDATE_GATES),
        "stage2_export_defaults": {
            key: str(value)
            for key, value in resolve_stage2_export_paths(
                run_root=REPO_ROOT / "baseline_mlx" / "outputs" / STAGE2_RUN_NAME,
                adapter_dir=None,
                output_root=None,
                reference_model_root=None,
            ).items()
        },
        "historical_attention_only_warning": {
            "run_root": str(HISTORICAL_ATTENTION_WARNING_RUN_ROOT),
            "readme_local320": historical_attention_local320,
            "leaderboard_proxy_v2": historical_attention_proxy_v2,
            "binary_bias_specialized_set": historical_attention_specialized,
        },
        "stage1_config": {
            "profile": "notebook-current",
            "lora_key_group": DEFAULT_STAGE1_LORA_KEY_GROUP,
            "trainable_lora_suffix_group": DEFAULT_STAGE1_TRAINABLE_LORA_SUFFIX_GROUP,
            "learning_rate": 1e-4,
            "num_epochs": 2.0,
            "max_seq_length": 4096,
            "valid_shadow_rows": 1,
        },
        "stage2_config": {
            "profile": "notebook-current",
            "lora_key_group": DEFAULT_STAGE2_LORA_KEY_GROUP,
            "trainable_lora_suffix_group": DEFAULT_STAGE2_TRAINABLE_LORA_SUFFIX_GROUP,
            "learning_rate": 2e-5,
            "num_epochs": 0.75,
            "max_seq_length": 1536,
            "valid_shadow_rows": 1,
            "max_symbol_rows": 9,
            "max_answer_only_ratio": 0.05,
            "max_manual_audit_ratio": DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO,
            "manual_audit_template_subtypes": list(DEFAULT_STAGE2_MANUAL_AUDIT_TEMPLATE_SUBTYPES),
        },
        "next_repair_priorities": [
            "preserve broad easy-family stability from the v3f-style broad trunk",
            "treat format_ok_content_wrong as the primary binary failure mode instead of only policing boxed formatting",
            "prioritize exact-route verified rows and keep answer-only as a low-ratio helper lane rather than expanding coarse route_closure_only data",
            "prioritize bit_other manual_audit_priority and verified_trace_ready signals before duplicating answer_only_keep rows already present in the current phase2 train CSV",
            "repair supported_not_structured instead of only over-optimizing supported_bijection",
            "repair binary_structured_byte_formula_abstract drift and binary_structured_byte_not_formula content misses",
            "keep the final artifact submission-compatible as a single rank-32 adapter",
        ],
    }


def render_markdown_summary(payload: dict[str, Any]) -> str:
    anchors = payload["v3f_anchors"]
    blueprint = payload["prompt_router_v6_blueprint"]
    transfer_priors = payload["single_adapter_transfer_priors"]
    lines = [
        "# v3f submission line v1",
        "",
        f"- script: `{Path(__file__).resolve()}`",
        f"- source_base_run_root: `{payload['source_base_run_root']}`",
        f"- stage1_dataset_csv: `{payload['stage1_dataset_csv']}`",
        f"- stage2_dataset_csv: `{payload['stage2_dataset_csv']}`",
        f"- proxy_v2_csv: `{payload['proxy_v2_csv']}`",
        "",
        "## Verified v3f anchors",
        "",
        f"- stored_phase0_local320: `{anchors['stored_phase0_local320']['correct']}/{anchors['stored_phase0_local320']['rows']} = {anchors['stored_phase0_local320']['accuracy']}`",
        f"- corrected_phase0_local320: `{anchors['corrected_phase0_local320']['correct']}/{anchors['corrected_phase0_local320']['rows']} = {anchors['corrected_phase0_local320']['accuracy']}`",
        f"- proxy_actual: `{anchors['proxy_actual']['correct']}/{anchors['proxy_actual']['rows']} = {anchors['proxy_actual']['accuracy']}`",
        f"- specialized563: `{anchors['specialized563']['correct']}/{anchors['specialized563']['rows']} = {anchors['specialized563']['accuracy']}`",
        f"- supported_not_structured: `{anchors['supported_not_structured']['correct']}/{anchors['supported_not_structured']['rows']} = {anchors['supported_not_structured']['accuracy']}`",
        f"- binary_structured_byte_not_formula: `{anchors['binary_structured_byte_not_formula']['correct']}/{anchors['binary_structured_byte_not_formula']['rows']} = {anchors['binary_structured_byte_not_formula']['accuracy']}`",
        "",
        "## Stage layout",
        "",
        f"- stage1_run_name: `{payload['stage1_run_name']}`",
        f"- stage1_trainable: `{payload['stage1_config']['trainable_lora_suffix_group']}`",
        f"- stage2_run_name: `{payload['stage2_run_name']}`",
        f"- stage2_trainable: `{payload['stage2_config']['trainable_lora_suffix_group']}`",
        f"- proxy_v2_focus_buckets: `{', '.join(payload['proxy_v2_focus_buckets'])}`",
        f"- stage2_binary_solvers: `{', '.join(payload['stage2_binary_solvers'])}`",
        f"- stage2_max_answer_only_ratio: `{payload['stage2_config']['max_answer_only_ratio']}`",
        f"- stage2_max_manual_audit_ratio: `{payload['stage2_config']['max_manual_audit_ratio']}`",
        f"- stage2_manual_audit_template_subtypes: `{', '.join(payload['stage2_config']['manual_audit_template_subtypes'])}`",
        f"- shared_stage1_launch: `{payload['stage2_profile_matrix']['stage2_profiles'][0]['stage1_launch_command']}`",
        f"- default_stage2_matrix_profiles: `{', '.join(payload['stage2_profile_matrix']['default_stage2_profiles'])}`",
        f"- all_stage2_profiles: `{', '.join(profile['profile_name'] for profile in payload['stage2_profile_matrix']['stage2_profiles'])}`",
        f"- stage2_candidate_gate_defaults: `{payload['stage2_candidate_gate_defaults']}`",
        f"- stage2_matrix_command: `{' '.join(shlex.quote(part) for part in self_uv_command('launch-stage2-matrix', '--dry-run'))}`",
        f"- stage2_matrix_all_profiles_command: `{' '.join(shlex.quote(part) for part in self_uv_command('launch-stage2-matrix', '--all-profiles', '--dry-run'))}`",
        f"- stage2_candidate_audit_command: `{payload['stage2_profile_matrix']['matrix_candidate_audit_command']}`",
        f"- stage2_candidate_audit_all_profiles_command: `{payload['stage2_profile_matrix']['matrix_candidate_audit_all_profiles_command']}`",
        f"- stage2_matrix_best_submission_command: `{' '.join(shlex.quote(part) for part in self_uv_command('package-stage2-matrix-best-submission', '--dry-run'))}`",
        f"- stage2_matrix_best_submission_all_profiles_command: `{' '.join(shlex.quote(part) for part in self_uv_command('package-stage2-matrix-best-submission', '--all-profiles', '--dry-run'))}`",
        f"- stage2_export_command: `{' '.join(shlex.quote(part) for part in self_uv_command('export-stage2-submission', '--run-root', 'baseline_mlx/outputs/' + payload['stage2_run_name']))}`",
        "",
        "## Historical caution",
        "",
        f"- nearby attention-only run: `{payload['historical_attention_only_warning']['run_root']}`",
        f"- nearby readme_local320: `{payload['historical_attention_only_warning']['readme_local320']['correct']}/{payload['historical_attention_only_warning']['readme_local320']['rows']} = {payload['historical_attention_only_warning']['readme_local320']['accuracy']}`",
        f"- nearby leaderboard_proxy_v2: `{payload['historical_attention_only_warning']['leaderboard_proxy_v2']['correct']}/{payload['historical_attention_only_warning']['leaderboard_proxy_v2']['rows']} = {payload['historical_attention_only_warning']['leaderboard_proxy_v2']['accuracy']}`",
        f"- nearby binary_bias_specialized_set: `{payload['historical_attention_only_warning']['binary_bias_specialized_set']['correct']}/{payload['historical_attention_only_warning']['binary_bias_specialized_set']['rows']} = {payload['historical_attention_only_warning']['binary_bias_specialized_set']['accuracy']}`",
        "",
        "## prompt-router-v6 blueprint",
        "",
        f"- local320: `{blueprint['local320']['correct']}/{blueprint['local320']['rows']} = {blueprint['local320']['accuracy']}`",
        f"- binary60: `{blueprint['binary60']['correct']}/{blueprint['binary60']['rows']} = {blueprint['binary60']['accuracy']}`",
        f"- v5 gain/loss: `+{blueprint['gain_vs_v5']['gain']} / -{blueprint['gain_vs_v5']['loss']}`",
        f"- fallback counts: `binary_formula_consensus_solver={blueprint['solver_fallback_counts']['binary_formula_consensus_solver']}`, `symbol_numeric_zero_error_solver={blueprint['solver_fallback_counts']['symbol_numeric_zero_error_solver']}`",
        f"- binary gain breakdown: `answer_only_keep={blueprint['binary_gain_breakdown']['answer_only_keep']}`, `manual_audit_priority={blueprint['binary_gain_breakdown']['manual_audit_priority']}`, `verified_trace_ready={blueprint['binary_gain_breakdown']['verified_trace_ready']}`",
        f"- submission_compatible: `{blueprint['submission_compatible']}`",
        "",
        "## Single-adapter transfer priors",
        "",
        f"- primary_failure_mode: `{transfer_priors['primary_failure_mode']}`",
        f"- primary_lane: `{transfer_priors['primary_lane']}`",
        f"- helper_lane: `{transfer_priors['helper_lane']}`",
        f"- bit_other_answer_only_keep_overlap_rows: `{transfer_priors['bit_other_answer_only_keep_overlap_rows']}`",
        f"- portable_new_signal_centers_on: `{', '.join(transfer_priors['portable_new_signal_centers_on'])}`",
        f"- avoid_repeating: `{', '.join(transfer_priors['avoid_repeating'])}`",
        "",
        "## README contract",
        "",
        f"- max_lora_rank: `{payload['readme_contract']['max_lora_rank']}`",
        f"- max_tokens: `{payload['readme_contract']['max_tokens']}`",
        f"- top_p: `{payload['readme_contract']['top_p']}`",
        f"- temperature: `{payload['readme_contract']['temperature']}`",
        f"- max_num_seqs: `{payload['readme_contract']['max_num_seqs']}`",
        f"- gpu_memory_utilization: `{payload['readme_contract']['gpu_memory_utilization']}`",
        f"- max_model_len: `{payload['readme_contract']['max_model_len']}`",
        "",
        "## README contract state",
        "",
        f"- summary_schema_version: `{payload['summary_schema_version']}`",
        f"- verified_from_readme_file: `{payload['readme_contract_verified_from_readme_file']}`",
        f"- matches_current_readme: `{payload['readme_contract_state']['matches_current_readme']}`",
        f"- contract_key_count: `{payload['readme_contract_state']['actual_key_count']}/{payload['readme_contract_state']['expected_key_count']}`",
        f"- missing_keys: `{format_inline_list(payload['readme_contract_state']['missing_keys'])}`",
        f"- unexpected_keys: `{format_inline_list(payload['readme_contract_state']['unexpected_keys'])}`",
        f"- mismatched_keys: `{format_inline_list(payload['readme_contract_state']['mismatched_keys'])}`",
        "",
        "## Next repair priorities",
        "",
        *[f"- {item}" for item in payload["next_repair_priorities"]],
    ]
    return "\n".join(lines)


def write_summary(output_root: Path, mode: str, extra: dict[str, Any]) -> Path:
    payload = {"mode": mode, **build_summary(), **extra}
    summary_json = output_root / "v3f_submission_line_summary.json"
    summary_md = output_root / "v3f_submission_line_summary.md"
    dump_json(summary_json, payload)
    dump_markdown(summary_md, render_markdown_summary(payload))
    return summary_json


def stage2_type_samples(summary_json_path: Path) -> list[str]:
    summary = load_json(summary_json_path)
    type_counts = summary.get("type_counts", {})
    bit_rows = int(type_counts.get("Bit Manipulation", 0))
    equation_rows = int(type_counts.get("Equation Transformation", 0))
    require(bit_rows > 0, f"Stage2 summary does not contain Bit Manipulation rows: {summary_json_path}")
    require(equation_rows > 0, f"Stage2 summary does not contain Equation Transformation rows: {summary_json_path}")
    return [
        f"Text Encryption=0",
        f"Bit Manipulation={bit_rows}",
        f"Gravitational Constant=0",
        f"Unit Conversion=0",
        f"Numeral Conversion=0",
        f"Equation Transformation={equation_rows}",
    ]


def resolve_stage2_type_samples(
    *,
    explicit_type_samples: list[str] | None,
    dataset_summary_json: str | Path | None,
) -> list[str]:
    if explicit_type_samples:
        return [str(item) for item in explicit_type_samples]
    require(
        dataset_summary_json is not None,
        "Stage2 type samples require either --type-sample overrides or --dataset-summary-json.",
    )
    summary_json_path = repo_path(dataset_summary_json)
    require(
        summary_json_path.exists(),
        f"Missing Stage2 summary json: {summary_json_path}. Run build-stage2-artifacts first or pass --type-sample.",
    )
    return stage2_type_samples(summary_json_path)


def resolve_stage2_export_paths(
    *,
    run_root: str | Path,
    adapter_dir: str | Path | None,
    output_root: str | Path | None,
    reference_model_root: str | Path | None,
) -> dict[str, Path]:
    run_root_path = repo_path(run_root)
    return {
        "run_root": run_root_path,
        "adapter_dir": repo_path(adapter_dir) if adapter_dir is not None else run_root_path / "adapter",
        "output_root": repo_path(output_root) if output_root is not None else run_root_path / "submission_export",
        "reference_model_root": repo_path(reference_model_root)
        if reference_model_root is not None
        else run_root_path / "shadow_model",
    }


def resolve_stage2_profile_artifact_paths(profile_name: str) -> dict[str, Path]:
    slug = profile_name.replace("-", "_")
    stage2_stem = f"{STAGE2_DATASET_STEM}_{slug}"
    proxy_stem = f"{PROXY_V2_STEM}_{slug}"
    return {
        "stage2_dataset_csv": ARTIFACT_ROOT / f"{stage2_stem}.csv",
        "stage2_dataset_summary_json": ARTIFACT_ROOT / f"{stage2_stem}_summary.json",
        "proxy_v2_csv": ARTIFACT_ROOT / f"{proxy_stem}.csv",
        "proxy_v2_summary_json": ARTIFACT_ROOT / f"{proxy_stem}_summary.json",
    }


def build_stage2_profile_matrix() -> dict[str, Any]:
    stage1_command = self_uv_command("launch-stage1", "--run-name", STAGE1_RUN_NAME)
    profiles: list[dict[str, Any]] = []
    for profile_name, profile in STAGE2_PROFILE_LIBRARY.items():
        stage2_run_name = f"{STAGE2_RUN_NAME}_{profile_name}"
        artifact_paths = resolve_stage2_profile_artifact_paths(profile_name)
        artifact_build_command = self_uv_command(
            "build-stage2-artifacts",
            "--output-csv",
            repo_relpath(artifact_paths["stage2_dataset_csv"]),
            "--summary-json",
            repo_relpath(artifact_paths["stage2_dataset_summary_json"]),
            "--proxy-v2-csv",
            repo_relpath(artifact_paths["proxy_v2_csv"]),
            "--proxy-v2-summary-json",
            repo_relpath(artifact_paths["proxy_v2_summary_json"]),
            "--max-symbol-rows",
            str(profile["stage2_max_symbol_rows"]),
            "--max-answer-only-ratio",
            str(profile["stage2_max_answer_only_ratio"]),
            "--max-manual-audit-ratio",
            str(profile["stage2_max_manual_audit_ratio"]),
        )
        launch_command = self_uv_command(
            "launch-stage2-linked",
            "--train-csv",
            repo_relpath(artifact_paths["stage2_dataset_csv"]),
            "--dataset-summary-json",
            repo_relpath(artifact_paths["stage2_dataset_summary_json"]),
            "--stage2-run-name",
            stage2_run_name,
            "--stage2-lora-key-group",
            str(profile["stage2_lora_key_group"]),
            "--stage2-trainable-lora-suffix-group",
            str(profile["stage2_trainable_lora_suffix_group"]),
            "--stage2-learning-rate",
            str(profile["stage2_learning_rate"]),
            "--stage2-num-epochs",
            str(profile["stage2_num_epochs"]),
            "--stage2-max-seq-length",
            str(profile["stage2_max_seq_length"]),
        )
        postprocess_command = self_uv_command(
            "postprocess-stage2",
            "--run-root",
            str(Path("baseline_mlx") / "outputs" / stage2_run_name),
            "--label",
            f"v3f stage2 {profile_name}",
            "--proxy-v2-csv",
            repo_relpath(artifact_paths["proxy_v2_csv"]),
            "--max-tokens",
            str(README_CONTRACT["max_tokens"]),
            "--temperature",
            str(README_CONTRACT["temperature"]),
            "--top-p",
            str(README_CONTRACT["top_p"]),
            "--max-num-seqs",
            str(README_CONTRACT["max_num_seqs"]),
            "--gpu-memory-utilization",
            str(README_CONTRACT["gpu_memory_utilization"]),
            "--max-model-len",
            str(README_CONTRACT["max_model_len"]),
            "--eval-enable-thinking",
        )
        export_command = self_uv_command(
            "export-stage2-submission",
            "--run-root",
            str(Path("baseline_mlx") / "outputs" / stage2_run_name),
        )
        profiles.append(
            {
                "profile_name": profile_name,
                "stage2_run_name": stage2_run_name,
                "stage2_dataset_csv": repo_relpath(artifact_paths["stage2_dataset_csv"]),
                "stage2_dataset_summary_json": repo_relpath(artifact_paths["stage2_dataset_summary_json"]),
                "proxy_v2_csv": repo_relpath(artifact_paths["proxy_v2_csv"]),
                "proxy_v2_summary_json": repo_relpath(artifact_paths["proxy_v2_summary_json"]),
                "stage2_manual_audit_template_subtypes": list(DEFAULT_STAGE2_MANUAL_AUDIT_TEMPLATE_SUBTYPES),
                **profile,
                "artifact_build_command": " ".join(
                    shlex.quote(part) for part in artifact_build_command
                ),
                "stage1_launch_command": " ".join(shlex.quote(part) for part in stage1_command),
                "stage2_linked_command": " ".join(shlex.quote(part) for part in launch_command),
                "postprocess_command": " ".join(shlex.quote(part) for part in postprocess_command),
                "export_command": " ".join(shlex.quote(part) for part in export_command),
            }
        )
    return {
        "script": str(Path(__file__).resolve()),
        "readme_contract": README_CONTRACT,
        "shared_stage1_run_name": STAGE1_RUN_NAME,
        "default_stage2_profiles": list(DEFAULT_STAGE2_MATRIX_PROFILE_NAMES),
        "stage2_candidate_gate_defaults": dict(DEFAULT_STAGE2_CANDIDATE_GATES),
        "matrix_all_profiles_command": " ".join(
            shlex.quote(part) for part in self_uv_command("launch-stage2-matrix", "--all-profiles")
        ),
        "matrix_candidate_audit_command": " ".join(
            shlex.quote(part) for part in self_uv_command("write-stage2-candidate-audit")
        ),
        "matrix_candidate_audit_all_profiles_command": " ".join(
            shlex.quote(part)
            for part in self_uv_command("write-stage2-candidate-audit", "--all-profiles")
        ),
        "matrix_best_submission_command": " ".join(
            shlex.quote(part) for part in self_uv_command("package-stage2-matrix-best-submission")
        ),
        "matrix_best_submission_all_profiles_command": " ".join(
            shlex.quote(part)
            for part in self_uv_command("package-stage2-matrix-best-submission", "--all-profiles")
        ),
        "stage2_profiles": profiles,
        "notes": [
            "Run these profiles in parallel only after PTY/shell execution recovers.",
            "Each profile now owns its own build-stage2-artifacts command and artifact paths, so the matrix can compare data-mix settings as well as LoRA hyperparameters.",
            "Launch Stage1 once, then arm multiple Stage2 profiles against the shared Stage1 run.",
            "attention-short-default remains the plan-aligned default lane.",
            "attention-short-noanswer is the exact-route-first comparison lane derived from the prompt-router-v6 transfer audit.",
            "attention-short-manual is the small manual_audit_priority comparison lane for portable prompt-router-v6 signal transfer.",
            "Use write-stage2-candidate-audit before package-stage2-matrix-best-submission to capture static gate state in Git-visible JSON/Markdown.",
            "launch-stage2-matrix and package-stage2-matrix-best-submission default to the default/noanswer/manual trio; exploratory lanes stay opt-in.",
            "union-short-exploratory and attention-vo-historical are exploratory comparisons, not proven winning recipes.",
        ],
    }


def render_stage2_profile_matrix_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# v3f stage2 profile matrix",
        "",
        f"- script: `{payload['script']}`",
        f"- default_stage2_profiles: `{', '.join(payload['default_stage2_profiles'])}`",
        f"- stage2_candidate_gate_defaults: `{payload['stage2_candidate_gate_defaults']}`",
        f"- matrix_all_profiles_command: `{payload['matrix_all_profiles_command']}`",
        f"- matrix_candidate_audit_command: `{payload['matrix_candidate_audit_command']}`",
        f"- matrix_candidate_audit_all_profiles_command: `{payload['matrix_candidate_audit_all_profiles_command']}`",
        f"- matrix_best_submission_command: `{payload['matrix_best_submission_command']}`",
        f"- matrix_best_submission_all_profiles_command: `{payload['matrix_best_submission_all_profiles_command']}`",
        "",
        "## Profiles",
        "",
    ]
    for profile in payload["stage2_profiles"]:
        lines.extend(
            [
                f"### {profile['profile_name']}",
                "",
                f"- description: {profile['description']}",
                f"- stage2_dataset_csv: `{profile['stage2_dataset_csv']}`",
                f"- stage2_dataset_summary_json: `{profile['stage2_dataset_summary_json']}`",
                f"- proxy_v2_csv: `{profile['proxy_v2_csv']}`",
                f"- stage2_lora_key_group: `{profile['stage2_lora_key_group']}`",
                f"- stage2_trainable_lora_suffix_group: `{profile['stage2_trainable_lora_suffix_group']}`",
                f"- stage2_learning_rate: `{profile['stage2_learning_rate']}`",
                f"- stage2_num_epochs: `{profile['stage2_num_epochs']}`",
                f"- stage2_max_seq_length: `{profile['stage2_max_seq_length']}`",
                f"- stage2_max_symbol_rows: `{profile['stage2_max_symbol_rows']}`",
                f"- stage2_max_answer_only_ratio: `{profile['stage2_max_answer_only_ratio']}`",
                f"- stage2_max_manual_audit_ratio: `{profile['stage2_max_manual_audit_ratio']}`",
                f"- stage2_manual_audit_template_subtypes: `{', '.join(profile['stage2_manual_audit_template_subtypes'])}`",
                f"- artifact_build_command: `{profile['artifact_build_command']}`",
                f"- stage1_launch_command: `{profile['stage1_launch_command']}`",
                f"- stage2_linked_command: `{profile['stage2_linked_command']}`",
                f"- postprocess_command: `{profile['postprocess_command']}`",
                f"- export_command: `{profile['export_command']}`",
                "",
            ]
        )
    lines.extend(["## Notes", "", *[f"- {note}" for note in payload["notes"]]])
    return "\n".join(lines)


def command_verify(args: argparse.Namespace) -> int:
    print(json.dumps(build_summary(), indent=2, sort_keys=True))
    return 0


def command_write_summary(args: argparse.Namespace) -> int:
    summary_path = write_summary(repo_path(args.output_root), "write-summary", {})
    print(summary_path)
    return 0


def command_write_stage2_matrix(args: argparse.Namespace) -> int:
    output_root = repo_path(args.output_root)
    payload = build_stage2_profile_matrix()
    summary_json = output_root / "v3f_stage2_profile_matrix.json"
    summary_md = output_root / "v3f_stage2_profile_matrix.md"
    dump_json(summary_json, payload)
    dump_markdown(summary_md, render_stage2_profile_matrix_markdown(payload))
    print(summary_json)
    return 0


def command_export_stage2_submission(args: argparse.Namespace) -> int:
    export_paths = resolve_stage2_export_paths(
        run_root=args.run_root,
        adapter_dir=getattr(args, "adapter_dir", None),
        output_root=getattr(args, "output_root", None),
        reference_model_root=getattr(args, "reference_model_root", None),
    )
    command = uv_command(
        "export-peft-submission",
        "--adapter-dir",
        export_paths["adapter_dir"],
        "--output-root",
        export_paths["output_root"],
        "--reference-model-root",
        export_paths["reference_model_root"],
        "--base-model-name-or-path",
        args.base_model_name_or_path,
    )
    run_command(command, dry_run=args.dry_run)
    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "export-stage2-submission",
        {
            "dry_run": args.dry_run,
            "stage2_export_run_root": str(export_paths["run_root"]),
            "stage2_export_adapter_dir": str(export_paths["adapter_dir"]),
            "stage2_export_output_root": str(export_paths["output_root"]),
            "stage2_export_reference_model_root": str(export_paths["reference_model_root"]),
            "base_model_name_or_path": args.base_model_name_or_path,
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def select_stage2_profiles(
    profile_names: list[str] | None = None,
    *,
    all_profiles: bool = False,
) -> list[dict[str, Any]]:
    payload = build_stage2_profile_matrix()
    profiles = payload["stage2_profiles"]
    require(not (profile_names and all_profiles), "Use either explicit --profile values or --all-profiles, not both.")
    if all_profiles:
        requested_names = [profile["profile_name"] for profile in profiles]
    else:
        requested_names = list(profile_names) if profile_names else list(DEFAULT_STAGE2_MATRIX_PROFILE_NAMES)
    by_name = {profile["profile_name"]: profile for profile in profiles}
    missing = [name for name in requested_names if name not in by_name]
    require(not missing, f"Unknown Stage2 profile(s): {', '.join(missing)}")
    return [by_name[name] for name in requested_names]


def stage2_run_root_from_profile(profile: dict[str, Any]) -> Path:
    return REPO_ROOT / "baseline_mlx" / "outputs" / str(profile["stage2_run_name"])


def empty_score_row() -> dict[str, Any]:
    return {"rows": 0, "correct": 0, "accuracy": 0.0}


def format_score_row(row: dict[str, Any]) -> str:
    return f"{int(row.get('correct', 0))}/{int(row.get('rows', 0))}={float(row.get('accuracy', 0.0)):.4f}"


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    return load_json(path) if path.exists() else None


def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw_values = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        raw_values = [str(item) for item in value]
    else:
        raw_values = [str(value)]
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in raw_values:
        item = str(raw).strip()
        if not item or item in seen:
            continue
        seen.add(item)
        normalized.append(item)
    return normalized


def inspect_submission_zip(zip_path: Path) -> dict[str, Any]:
    if not zip_path.exists():
        return {
            "submission_zip_valid": False,
            "submission_zip_required_files_present": False,
            "submission_adapter_config_present": False,
            "submission_adapter_config_valid": False,
            "submission_adapter_peft_type": "",
            "submission_adapter_peft_type_matches_expected": False,
            "submission_adapter_base_model_name_or_path": "",
            "submission_adapter_base_model_matches_expected": False,
            "submission_adapter_task_type": "",
            "submission_adapter_task_type_matches_expected": False,
            "submission_adapter_inference_mode": None,
            "submission_adapter_inference_mode_matches_expected": False,
            "submission_adapter_target_modules": [],
            "submission_adapter_target_modules_count": 0,
            "submission_adapter_target_modules_nonempty": False,
            "submission_adapter_model_size_bytes": None,
            "submission_adapter_model_nonempty": False,
            "submission_adapter_rank": None,
            "submission_rank_within_readme_limit": False,
            "submission_zip_blocked_reasons": ["submission.zip is missing."],
        }
    blocked_reasons: list[str] = []
    required_files = {"adapter_config.json", "adapter_model.safetensors"}
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                blocked_reasons.append(f"submission.zip failed CRC check for {bad_member}.")
            member_names = [info.filename for info in archive.infolist() if not info.is_dir()]
            names = set(member_names)
            unsafe_member_paths = sorted(
                name
                for name in member_names
                if PurePosixPath(name).is_absolute()
                or ".." in PurePosixPath(name).parts
                or "\\" in name
            )
            if unsafe_member_paths:
                blocked_reasons.append(
                    "submission.zip contains unsafe member path(s): " + ", ".join(unsafe_member_paths)
                )
            extra_safetensors_members = sorted(
                name for name in member_names if name.endswith(".safetensors") and name != "adapter_model.safetensors"
            )
            if extra_safetensors_members:
                blocked_reasons.append(
                    "submission.zip contains extra safetensors payload(s): " + ", ".join(extra_safetensors_members)
                )
            duplicate_adapter_config_members = sorted(
                name
                for name in member_names
                if PurePosixPath(name).name == "adapter_config.json" and name != "adapter_config.json"
            )
            if duplicate_adapter_config_members:
                blocked_reasons.append(
                    "submission.zip contains duplicate adapter_config.json path(s): "
                    + ", ".join(duplicate_adapter_config_members)
                )
            duplicate_required_members = sorted(
                f"{name} x{member_names.count(name)}" for name in sorted(required_files) if member_names.count(name) > 1
            )
            if duplicate_required_members:
                blocked_reasons.append(
                    "submission.zip contains duplicate required member entries: "
                    + ", ".join(duplicate_required_members)
                )
            missing_required = sorted(required_files - names)
            if missing_required:
                blocked_reasons.append(
                    "submission.zip missing required file(s): " + ", ".join(missing_required)
                )
            adapter_config_present = "adapter_config.json" in names
            adapter_model_size_bytes: int | None = None
            if "adapter_model.safetensors" in names:
                try:
                    adapter_model_size_bytes = archive.getinfo("adapter_model.safetensors").file_size
                except KeyError:
                    adapter_model_size_bytes = None
                if not (adapter_model_size_bytes is not None and adapter_model_size_bytes > 0):
                    blocked_reasons.append("adapter_model.safetensors inside submission.zip is empty.")
            adapter_config_payload: dict[str, Any] | None = None
            adapter_peft_type = ""
            adapter_base_model_name_or_path = ""
            adapter_task_type = ""
            adapter_inference_mode: bool | None = None
            adapter_target_modules: list[str] = []
            adapter_rank: int | None = None
            if adapter_config_present:
                try:
                    adapter_config_payload = json.loads(archive.read("adapter_config.json").decode("utf-8"))
                except Exception as exc:
                    blocked_reasons.append(f"adapter_config.json is not valid JSON inside submission.zip: {exc}")
                if isinstance(adapter_config_payload, dict):
                    adapter_peft_type = str(adapter_config_payload.get("peft_type", "")).strip()
                    if adapter_peft_type != str(EXPECTED_SUBMISSION_ADAPTER_CONFIG["peft_type"]):
                        blocked_reasons.append(
                            "adapter_config.json peft_type "
                            f"{adapter_peft_type!r} does not match expected {EXPECTED_SUBMISSION_ADAPTER_CONFIG['peft_type']!r}."
                        )
                    adapter_base_model_name_or_path = str(
                        adapter_config_payload.get("base_model_name_or_path", "")
                    ).strip()
                    if adapter_base_model_name_or_path != BASE_MODEL_NAME:
                        blocked_reasons.append(
                            "adapter_config.json base_model_name_or_path "
                            f"{adapter_base_model_name_or_path!r} does not match expected {BASE_MODEL_NAME!r}."
                        )
                    adapter_task_type = str(adapter_config_payload.get("task_type", "")).strip()
                    if adapter_task_type != str(EXPECTED_SUBMISSION_ADAPTER_CONFIG["task_type"]):
                        blocked_reasons.append(
                            "adapter_config.json task_type "
                            f"{adapter_task_type!r} does not match expected {EXPECTED_SUBMISSION_ADAPTER_CONFIG['task_type']!r}."
                        )
                    raw_inference_mode = adapter_config_payload.get("inference_mode")
                    adapter_inference_mode = raw_inference_mode if isinstance(raw_inference_mode, bool) else None
                    if adapter_inference_mode is not bool(EXPECTED_SUBMISSION_ADAPTER_CONFIG["inference_mode"]):
                        blocked_reasons.append(
                            "adapter_config.json inference_mode "
                            f"{raw_inference_mode!r} does not match expected {EXPECTED_SUBMISSION_ADAPTER_CONFIG['inference_mode']!r}."
                        )
                    adapter_target_modules = normalize_string_list(adapter_config_payload.get("target_modules"))
                    if not adapter_target_modules:
                        blocked_reasons.append("adapter_config.json target_modules is missing or empty.")
                    try:
                        adapter_rank = int(adapter_config_payload.get("r"))
                    except Exception:
                        blocked_reasons.append("adapter_config.json does not contain an integer LoRA rank `r`.")
                    else:
                        if adapter_rank <= 0:
                            blocked_reasons.append("adapter_config.json has non-positive LoRA rank `r`.")
                        elif adapter_rank > int(README_CONTRACT["max_lora_rank"]):
                            blocked_reasons.append(
                                f"adapter_config.json rank {adapter_rank} exceeds README max_lora_rank={README_CONTRACT['max_lora_rank']}."
                            )
            return {
                "submission_zip_valid": not blocked_reasons,
                "submission_zip_required_files_present": not missing_required,
                "submission_adapter_config_present": adapter_config_present,
                "submission_adapter_config_valid": isinstance(adapter_config_payload, dict),
                "submission_adapter_peft_type": adapter_peft_type if isinstance(adapter_config_payload, dict) else "",
                "submission_adapter_peft_type_matches_expected": (
                    isinstance(adapter_config_payload, dict)
                    and adapter_peft_type == str(EXPECTED_SUBMISSION_ADAPTER_CONFIG["peft_type"])
                ),
                "submission_adapter_base_model_name_or_path": (
                    adapter_base_model_name_or_path if isinstance(adapter_config_payload, dict) else ""
                ),
                "submission_adapter_base_model_matches_expected": (
                    isinstance(adapter_config_payload, dict)
                    and adapter_base_model_name_or_path == BASE_MODEL_NAME
                ),
                "submission_adapter_task_type": adapter_task_type if isinstance(adapter_config_payload, dict) else "",
                "submission_adapter_task_type_matches_expected": (
                    isinstance(adapter_config_payload, dict)
                    and adapter_task_type == str(EXPECTED_SUBMISSION_ADAPTER_CONFIG["task_type"])
                ),
                "submission_adapter_inference_mode": adapter_inference_mode,
                "submission_adapter_inference_mode_matches_expected": (
                    isinstance(adapter_config_payload, dict)
                    and adapter_inference_mode is bool(EXPECTED_SUBMISSION_ADAPTER_CONFIG["inference_mode"])
                ),
                "submission_adapter_target_modules": list(adapter_target_modules),
                "submission_adapter_target_modules_count": len(adapter_target_modules),
                "submission_adapter_target_modules_nonempty": bool(adapter_target_modules),
                "submission_adapter_model_size_bytes": adapter_model_size_bytes,
                "submission_adapter_model_nonempty": (
                    adapter_model_size_bytes is not None and adapter_model_size_bytes > 0
                ),
                "submission_adapter_rank": adapter_rank,
                "submission_rank_within_readme_limit": (
                    adapter_rank is not None
                    and 0 < adapter_rank <= int(README_CONTRACT["max_lora_rank"])
                ),
                "submission_zip_blocked_reasons": blocked_reasons,
            }
    except zipfile.BadZipFile as exc:
        blocked_reasons.append(f"submission.zip is not a valid ZIP archive: {exc}")
    except Exception as exc:
        blocked_reasons.append(f"submission.zip could not be inspected: {exc}")
    return {
        "submission_zip_valid": False,
        "submission_zip_required_files_present": False,
        "submission_adapter_config_present": False,
        "submission_adapter_config_valid": False,
        "submission_adapter_peft_type": "",
        "submission_adapter_peft_type_matches_expected": False,
        "submission_adapter_base_model_name_or_path": "",
        "submission_adapter_base_model_matches_expected": False,
        "submission_adapter_task_type": "",
        "submission_adapter_task_type_matches_expected": False,
        "submission_adapter_inference_mode": None,
        "submission_adapter_inference_mode_matches_expected": False,
        "submission_adapter_target_modules": [],
        "submission_adapter_target_modules_count": 0,
        "submission_adapter_target_modules_nonempty": False,
        "submission_adapter_model_size_bytes": None,
        "submission_adapter_model_nonempty": False,
        "submission_adapter_rank": None,
        "submission_rank_within_readme_limit": False,
        "submission_zip_blocked_reasons": blocked_reasons,
    }


def build_stage2_candidate_artifact_state(
    run_root: Path,
    *,
    suite_summary_relpath: Path,
    audit_relpath: Path,
    export_relpath: Path,
    expected_stage2_train_csv: Path | None = None,
) -> dict[str, Any]:
    recorded_run_result_path = run_root / DEFAULT_RUN_RECORDED_RESULT_RELPATH
    suite_summary_path = run_root / suite_summary_relpath
    audit_summary_path = run_root / audit_relpath
    prepare_manifest_path = run_root / "prepare_manifest.json"
    training_result_path = run_root / "training_result.json"
    export_manifest_path = run_root / export_relpath
    export_manifest: dict[str, Any] | None = None
    export_manifest_blocked_reasons: list[str] = []
    if export_manifest_path.exists():
        try:
            raw_export_manifest = load_json(export_manifest_path)
        except Exception as exc:
            export_manifest_blocked_reasons.append(f"export_manifest.json could not be parsed: {exc}")
        else:
            if not isinstance(raw_export_manifest, dict):
                export_manifest_blocked_reasons.append("export_manifest.json is not a JSON object.")
            else:
                export_manifest = raw_export_manifest
    else:
        export_manifest_blocked_reasons.append("export_manifest.json is missing.")
    export_manifest_valid = bool(export_manifest.get("validation", {}).get("valid")) if isinstance(export_manifest, dict) else False
    export_manifest_converted_tensor_count: int | None = None
    if isinstance(export_manifest, dict):
        try:
            export_manifest_converted_tensor_count = int(export_manifest.get("converted_tensor_count"))
        except Exception:
            export_manifest_converted_tensor_count = None
    export_manifest_target_modules = normalize_string_list(
        export_manifest.get("target_modules") if isinstance(export_manifest, dict) else None
    )
    export_manifest_base_model_name_or_path = (
        str(export_manifest.get("base_model_name_or_path", "")).strip()
        if isinstance(export_manifest, dict)
        else ""
    )
    export_manifest_zip_path_text = ""
    if isinstance(export_manifest, dict):
        export_manifest_zip_path_text = str(export_manifest.get("zip_path", "")).strip()
    export_manifest_zip_path = (
        Path(export_manifest_zip_path_text).resolve() if export_manifest_zip_path_text else None
    )
    export_manifest_zip_size_bytes: int | None = None
    if isinstance(export_manifest, dict):
        try:
            export_manifest_zip_size_bytes = int(export_manifest.get("zip_size_bytes"))
        except Exception:
            export_manifest_zip_size_bytes = None
    expected_export_zip_path = (run_root / export_relpath.parent / "submission.zip").resolve()
    if isinstance(export_manifest, dict) and not export_manifest_valid:
        export_manifest_blocked_reasons.append("export_manifest.json validation.valid is false.")
    if isinstance(export_manifest, dict) and not (
        export_manifest_converted_tensor_count is not None and export_manifest_converted_tensor_count > 0
    ):
        export_manifest_blocked_reasons.append("export_manifest.json converted_tensor_count is missing or non-positive.")
    if isinstance(export_manifest, dict) and not export_manifest_target_modules:
        export_manifest_blocked_reasons.append("export_manifest.json target_modules is missing or empty.")
    if isinstance(export_manifest, dict) and export_manifest_base_model_name_or_path != BASE_MODEL_NAME:
        export_manifest_blocked_reasons.append(
            "export_manifest.json base_model_name_or_path "
            f"{export_manifest_base_model_name_or_path!r} does not match expected {BASE_MODEL_NAME!r}."
        )
    if isinstance(export_manifest, dict):
        if not export_manifest_zip_path_text:
            export_manifest_blocked_reasons.append("export_manifest.json zip_path is missing.")
        elif export_manifest_zip_path != expected_export_zip_path:
            export_manifest_blocked_reasons.append(
                "export_manifest.json zip_path "
                f"{str(export_manifest_zip_path)!r} does not match expected {str(expected_export_zip_path)!r}."
            )
        if not (export_manifest_zip_size_bytes is not None and export_manifest_zip_size_bytes > 0):
            export_manifest_blocked_reasons.append("export_manifest.json zip_size_bytes is missing or non-positive.")
    export_zip_path = expected_export_zip_path
    submission_zip_size_bytes = export_zip_path.stat().st_size if export_zip_path.exists() else None
    prepare_manifest_inspection = inspect_prepare_manifest_artifact(
        prepare_manifest_path,
        expected_train_csv=expected_stage2_train_csv,
    )
    training_result_inspection = inspect_training_result_artifact(training_result_path)
    zip_inspection = inspect_submission_zip(export_zip_path)
    recorded_eval_assumptions = inspect_recorded_eval_assumptions(recorded_run_result_path)
    suite_summary_inspection = inspect_suite_summary_artifact(suite_summary_path)
    audit_summary_inspection = inspect_submission_audit_artifact(audit_summary_path)
    audit_summary_blocked_reasons = list(audit_summary_inspection["audit_summary_blocked_reasons"])
    export_manifest_target_modules_match_submission = (
        bool(export_manifest_target_modules)
        and bool(zip_inspection["submission_adapter_target_modules"])
        and export_manifest_target_modules == list(zip_inspection["submission_adapter_target_modules"])
    )
    if (
        isinstance(export_manifest, dict)
        and bool(export_manifest_target_modules)
        and bool(zip_inspection["submission_adapter_target_modules"])
        and not export_manifest_target_modules_match_submission
    ):
        export_manifest_blocked_reasons.append(
            "export_manifest.json target_modules does not match submission.zip adapter_config.json target_modules."
        )
    export_manifest_zip_path_matches_expected = (
        export_manifest_zip_path is not None and export_manifest_zip_path == expected_export_zip_path
    )
    export_manifest_zip_size_matches_submission = (
        export_manifest_zip_size_bytes is not None
        and submission_zip_size_bytes is not None
        and export_manifest_zip_size_bytes == submission_zip_size_bytes
    )
    if (
        isinstance(export_manifest, dict)
        and export_manifest_zip_size_bytes is not None
        and submission_zip_size_bytes is not None
        and not export_manifest_zip_size_matches_submission
    ):
        export_manifest_blocked_reasons.append(
            "export_manifest.json zip_size_bytes does not match the actual submission.zip size."
        )
    audit_summary_target_modules_match_submission = (
        bool(audit_summary_inspection["audit_summary_preview_target_modules"])
        and bool(zip_inspection["submission_adapter_target_modules"])
        and list(audit_summary_inspection["audit_summary_preview_target_modules"])
        == list(zip_inspection["submission_adapter_target_modules"])
    )
    if (
        bool(audit_summary_inspection["audit_summary_preview_target_modules"])
        and bool(zip_inspection["submission_adapter_target_modules"])
        and not audit_summary_target_modules_match_submission
    ):
        audit_summary_blocked_reasons.append(
            "submission_compat_audit.json peft_adapter_config_preview.target_modules does not match submission.zip adapter_config.json target_modules."
        )
    audit_summary_target_modules_match_export_manifest = (
        bool(audit_summary_inspection["audit_summary_preview_target_modules"])
        and bool(export_manifest_target_modules)
        and list(audit_summary_inspection["audit_summary_preview_target_modules"]) == list(export_manifest_target_modules)
    )
    if (
        bool(audit_summary_inspection["audit_summary_preview_target_modules"])
        and bool(export_manifest_target_modules)
        and not audit_summary_target_modules_match_export_manifest
    ):
        audit_summary_blocked_reasons.append(
            "submission_compat_audit.json peft_adapter_config_preview.target_modules does not match export_manifest.json target_modules."
        )
    audit_summary_preview_rank_matches_submission = (
        audit_summary_inspection["audit_summary_preview_rank"] is not None
        and zip_inspection["submission_adapter_rank"] is not None
        and int(audit_summary_inspection["audit_summary_preview_rank"]) == int(zip_inspection["submission_adapter_rank"])
    )
    if (
        audit_summary_inspection["audit_summary_preview_rank"] is not None
        and zip_inspection["submission_adapter_rank"] is not None
        and not audit_summary_preview_rank_matches_submission
    ):
        audit_summary_blocked_reasons.append(
            "submission_compat_audit.json peft_adapter_config_preview.r does not match submission.zip adapter_config.json r."
        )
    audit_summary_base_model_matches_submission = (
        bool(audit_summary_inspection["audit_summary_base_model_name_or_path"])
        and bool(zip_inspection["submission_adapter_base_model_name_or_path"])
        and str(audit_summary_inspection["audit_summary_base_model_name_or_path"])
        == str(zip_inspection["submission_adapter_base_model_name_or_path"])
    )
    if (
        bool(audit_summary_inspection["audit_summary_base_model_name_or_path"])
        and bool(zip_inspection["submission_adapter_base_model_name_or_path"])
        and not audit_summary_base_model_matches_submission
    ):
        audit_summary_blocked_reasons.append(
            "submission_compat_audit.json base_model_name_or_path does not match submission.zip adapter_config.json base_model_name_or_path."
        )
    audit_summary_inspection = dict(audit_summary_inspection)
    audit_summary_inspection.update(
        {
            "audit_summary_valid": not audit_summary_blocked_reasons,
            "audit_summary_blocked_reasons": audit_summary_blocked_reasons,
            "audit_summary_target_modules_match_submission": audit_summary_target_modules_match_submission,
            "audit_summary_target_modules_match_export_manifest": audit_summary_target_modules_match_export_manifest,
            "audit_summary_preview_rank_matches_submission": audit_summary_preview_rank_matches_submission,
            "audit_summary_base_model_matches_submission": audit_summary_base_model_matches_submission,
        }
    )
    checks = {
        "prepare_manifest": prepare_manifest_path.exists(),
        "training_result": training_result_path.exists(),
        "suite_summary": (run_root / suite_summary_relpath).exists(),
        "audit_summary": (run_root / audit_relpath).exists(),
        "export_manifest": (run_root / export_relpath).exists(),
        "submission_zip": export_zip_path.exists(),
    }
    return {
        "run_root_exists": run_root.exists(),
        "prepare_manifest_exists": checks["prepare_manifest"],
        "training_result_exists": checks["training_result"],
        "suite_summary_exists": checks["suite_summary"],
        "audit_summary_exists": checks["audit_summary"],
        "export_manifest_exists": checks["export_manifest"],
        "submission_zip_exists": checks["submission_zip"],
        "recorded_run_result_exists": recorded_run_result_path.exists(),
        **prepare_manifest_inspection,
        **training_result_inspection,
        "export_manifest_valid": export_manifest_valid,
        "export_manifest_converted_tensor_count": export_manifest_converted_tensor_count,
        "export_manifest_has_converted_tensors": (
            export_manifest_converted_tensor_count is not None and export_manifest_converted_tensor_count > 0
        ),
        "export_manifest_target_modules": list(export_manifest_target_modules),
        "export_manifest_target_modules_count": len(export_manifest_target_modules),
        "export_manifest_target_modules_nonempty": bool(export_manifest_target_modules),
        "export_manifest_target_modules_match_submission": export_manifest_target_modules_match_submission,
        "export_manifest_base_model_name_or_path": export_manifest_base_model_name_or_path,
        "export_manifest_base_model_matches_expected": (
            isinstance(export_manifest, dict)
            and export_manifest_base_model_name_or_path == BASE_MODEL_NAME
        ),
        "export_manifest_zip_path": str(export_manifest_zip_path) if export_manifest_zip_path is not None else "",
        "export_manifest_zip_path_matches_expected": (
            isinstance(export_manifest, dict) and export_manifest_zip_path_matches_expected
        ),
        "export_manifest_zip_size_bytes": export_manifest_zip_size_bytes,
        "export_manifest_zip_size_matches_submission": (
            isinstance(export_manifest, dict) and export_manifest_zip_size_matches_submission
        ),
        "export_manifest_blocked_reasons": export_manifest_blocked_reasons,
        "expected_export_zip_path": str(expected_export_zip_path),
        "export_zip_path": str(export_zip_path),
        "submission_zip_size_bytes": submission_zip_size_bytes,
        **suite_summary_inspection,
        **audit_summary_inspection,
        **recorded_eval_assumptions,
        **zip_inspection,
        "missing_artifacts": [name for name, exists in checks.items() if not exists],
    }


def inspect_profile_summary_artifact(summary_path: Path, *, expected_output_csv: Path) -> dict[str, Any]:
    blocked_reasons: list[str] = []
    if not summary_path.exists():
        return {
            "summary_exists": False,
            "summary_valid": False,
            "rows": None,
            "output_csv": "",
            "output_csv_matches_expected": False,
            "blocked_reasons": [f"{summary_path.name} is missing."],
        }
    try:
        payload = load_json(summary_path)
    except Exception as exc:
        return {
            "summary_exists": True,
            "summary_valid": False,
            "rows": None,
            "output_csv": "",
            "output_csv_matches_expected": False,
            "blocked_reasons": [f"{summary_path.name} could not be parsed: {exc}"],
        }
    if not isinstance(payload, dict):
        return {
            "summary_exists": True,
            "summary_valid": False,
            "rows": None,
            "output_csv": "",
            "output_csv_matches_expected": False,
            "blocked_reasons": [f"{summary_path.name} is not a JSON object."],
        }
    rows: int | None = None
    try:
        rows = int(payload.get("rows"))
    except Exception:
        blocked_reasons.append(f"{summary_path.name} rows is missing or not an integer.")
    else:
        if rows <= 0:
            blocked_reasons.append(f"{summary_path.name} rows must be positive.")
    output_csv_text = str(payload.get("output_csv", "")).strip()
    output_csv_matches_expected = (
        bool(output_csv_text) and repo_path(output_csv_text).resolve() == expected_output_csv.resolve()
    )
    if not output_csv_matches_expected:
        blocked_reasons.append(
            f"{summary_path.name} output_csv does not match expected artifact {repo_relpath(expected_output_csv)}."
        )
    return {
        "summary_exists": True,
        "summary_valid": not blocked_reasons,
        "rows": rows,
        "output_csv": output_csv_text,
        "output_csv_matches_expected": output_csv_matches_expected,
        "blocked_reasons": blocked_reasons,
    }


def inspect_recorded_eval_assumptions(recorded_run_result_path: Path) -> dict[str, Any]:
    if not recorded_run_result_path.exists():
        return {
            "recorded_eval_assumptions_present": False,
            "recorded_eval_assumptions": {},
            "recorded_eval_contract_matches_readme": None,
            "recorded_eval_contract_mismatches": [],
        }
    try:
        payload = load_json(recorded_run_result_path)
    except Exception as exc:
        return {
            "recorded_eval_assumptions_present": False,
            "recorded_eval_assumptions": {},
            "recorded_eval_contract_matches_readme": False,
            "recorded_eval_contract_mismatches": [f"recorded_run_result.json could not be parsed: {exc}"],
        }
    if not isinstance(payload, dict):
        return {
            "recorded_eval_assumptions_present": False,
            "recorded_eval_assumptions": {},
            "recorded_eval_contract_matches_readme": False,
            "recorded_eval_contract_mismatches": ["recorded_run_result.json is not a JSON object."],
        }
    raw_assumptions = payload.get("readme_eval_assumptions")
    if not isinstance(raw_assumptions, dict):
        return {
            "recorded_eval_assumptions_present": False,
            "recorded_eval_assumptions": {},
            "recorded_eval_contract_matches_readme": None,
            "recorded_eval_contract_mismatches": [],
        }
    mismatches: list[str] = []
    normalized_assumptions = dict(raw_assumptions)
    for key, expected_value in EXPECTED_RECORDED_EVAL_ASSUMPTIONS.items():
        if key not in raw_assumptions:
            continue
        actual_value = raw_assumptions[key]
        if actual_value != expected_value:
            mismatches.append(
                f"recorded_run_result.json readme_eval_assumptions[{key!r}]={actual_value!r} "
                f"does not match expected {expected_value!r}."
            )
    return {
        "recorded_eval_assumptions_present": True,
        "recorded_eval_assumptions": normalized_assumptions,
        "recorded_eval_contract_matches_readme": not mismatches,
        "recorded_eval_contract_mismatches": mismatches,
    }


def inspect_benchmark_eval_summary(
    summary_path: Path,
    *,
    expected_name: str,
    required_component_benchmarks: list[str],
) -> dict[str, Any]:
    blocked_reasons: list[str] = []
    if not summary_path.exists():
        return {
            "summary_exists": False,
            "summary_valid": False,
            "overall_rows": None,
            "blocked_reasons": [f"{expected_name} benchmark_eval_summary.json is missing."],
        }
    try:
        payload = load_json(summary_path)
    except Exception as exc:
        return {
            "summary_exists": True,
            "summary_valid": False,
            "overall_rows": None,
            "blocked_reasons": [f"{expected_name} benchmark_eval_summary.json could not be parsed: {exc}"],
        }
    if not isinstance(payload, dict):
        return {
            "summary_exists": True,
            "summary_valid": False,
            "overall_rows": None,
            "blocked_reasons": [f"{expected_name} benchmark_eval_summary.json is not a JSON object."],
        }
    actual_name = str(payload.get("evaluation_name", "")).strip()
    if actual_name != expected_name:
        blocked_reasons.append(
            f"{expected_name} benchmark_eval_summary.json evaluation_name {actual_name!r} does not match expected {expected_name!r}."
        )
    overall_rows: int | None = None
    overall = payload.get("overall")
    if not isinstance(overall, dict):
        blocked_reasons.append(f"{expected_name} benchmark_eval_summary.json overall is missing.")
    else:
        try:
            overall_rows = int(overall.get("rows"))
        except Exception:
            blocked_reasons.append(f"{expected_name} benchmark_eval_summary.json overall.rows is missing or invalid.")
        else:
            if overall_rows <= 0:
                blocked_reasons.append(f"{expected_name} benchmark_eval_summary.json overall.rows must be positive.")
    by_benchmark_map: dict[str, dict[str, Any]] = {}
    for row in payload.get("by_benchmark", []):
        if not isinstance(row, dict):
            continue
        name = str(row.get("benchmark_name", "")).strip()
        if name:
            by_benchmark_map[name] = row
    for benchmark_name in required_component_benchmarks:
        row = by_benchmark_map.get(benchmark_name)
        if not isinstance(row, dict):
            blocked_reasons.append(
                f"{expected_name} benchmark_eval_summary.json missing by_benchmark entry {benchmark_name!r}."
            )
            continue
        try:
            benchmark_rows = int(row.get("rows"))
        except Exception:
            blocked_reasons.append(
                f"{expected_name} benchmark_eval_summary.json by_benchmark[{benchmark_name!r}].rows is invalid."
            )
        else:
            if benchmark_rows <= 0:
                blocked_reasons.append(
                    f"{expected_name} benchmark_eval_summary.json by_benchmark[{benchmark_name!r}].rows must be positive."
                )
    return {
        "summary_exists": True,
        "summary_valid": not blocked_reasons,
        "overall_rows": overall_rows,
        "blocked_reasons": blocked_reasons,
    }


def inspect_suite_summary_artifact(suite_summary_path: Path) -> dict[str, Any]:
    blocked_reasons: list[str] = []
    if not suite_summary_path.exists():
        return {
            "suite_summary_valid": False,
            "suite_summary_required_evaluations_present": False,
            "suite_summary_eval_summaries_valid": False,
            "suite_summary_required_evaluation_rows": {},
            "suite_summary_blocked_reasons": [f"{suite_summary_path.name} is missing."],
        }
    try:
        payload = load_json(suite_summary_path)
    except Exception as exc:
        return {
            "suite_summary_valid": False,
            "suite_summary_required_evaluations_present": False,
            "suite_summary_eval_summaries_valid": False,
            "suite_summary_required_evaluation_rows": {},
            "suite_summary_blocked_reasons": [f"{suite_summary_path.name} could not be parsed: {exc}"],
        }
    if not isinstance(payload, dict):
        return {
            "suite_summary_valid": False,
            "suite_summary_required_evaluations_present": False,
            "suite_summary_eval_summaries_valid": False,
            "suite_summary_required_evaluation_rows": {},
            "suite_summary_blocked_reasons": [f"{suite_summary_path.name} is not a JSON object."],
        }
    evaluations_by_name: dict[str, dict[str, Any]] = {}
    for row in payload.get("evaluations", []):
        if not isinstance(row, dict):
            continue
        name = str(row.get("evaluation_name", "")).strip()
        output_root = str(row.get("output_root", "")).strip()
        if name and output_root:
            evaluations_by_name[name] = row
    required_rows: dict[str, int | None] = {}
    child_blocked_reasons: list[str] = []
    for evaluation_name, spec in REQUIRED_STAGE2_EVALUATIONS.items():
        evaluation_row = evaluations_by_name.get(evaluation_name)
        if not isinstance(evaluation_row, dict):
            blocked_reasons.append(f"{suite_summary_path.name} missing evaluation {evaluation_name!r}.")
            required_rows[evaluation_name] = None
            continue
        output_root = repo_path(str(evaluation_row.get("output_root", ""))).resolve()
        eval_summary = inspect_benchmark_eval_summary(
            output_root / "benchmark_eval_summary.json",
            expected_name=evaluation_name,
            required_component_benchmarks=list(spec["required_component_benchmarks"]),
        )
        required_rows[evaluation_name] = eval_summary["overall_rows"]
        child_blocked_reasons.extend(str(reason) for reason in eval_summary["blocked_reasons"])
    combined_blocked_reasons = blocked_reasons + child_blocked_reasons
    return {
        "suite_summary_valid": not combined_blocked_reasons,
        "suite_summary_required_evaluations_present": not blocked_reasons,
        "suite_summary_eval_summaries_valid": not child_blocked_reasons,
        "suite_summary_required_evaluation_rows": required_rows,
        "suite_summary_blocked_reasons": combined_blocked_reasons,
    }


def inspect_submission_audit_artifact(audit_summary_path: Path) -> dict[str, Any]:
    default_state = {
        "audit_summary_valid": False,
        "audit_summary_status": "",
        "audit_summary_status_present": False,
        "audit_summary_status_detail": "",
        "audit_summary_peft_export_ready": False,
        "audit_summary_base_model_name_or_path": "",
        "audit_summary_base_model_matches_expected": False,
        "audit_summary_preview_peft_type": "",
        "audit_summary_preview_peft_type_matches_expected": False,
        "audit_summary_preview_rank": None,
        "audit_summary_preview_rank_within_readme_limit": False,
        "audit_summary_preview_target_modules": [],
        "audit_summary_preview_target_modules_nonempty": False,
        "audit_summary_preview_inference_mode": None,
        "audit_summary_preview_inference_mode_matches_expected": False,
        "audit_summary_readme_contract_required_files_present": False,
        "audit_summary_readme_contract_max_rank_matches_expected": False,
        "audit_summary_readme_contract_single_adapter_matches_expected": False,
        "audit_summary_blocked_reasons": [],
    }
    blocked_reasons: list[str] = []
    if not audit_summary_path.exists():
        return default_state | {"audit_summary_blocked_reasons": [f"{audit_summary_path.name} is missing."]}
    try:
        payload = load_json(audit_summary_path)
    except Exception as exc:
        return default_state | {
            "audit_summary_blocked_reasons": [f"{audit_summary_path.name} could not be parsed: {exc}"]
        }
    if not isinstance(payload, dict):
        return default_state | {"audit_summary_blocked_reasons": [f"{audit_summary_path.name} is not a JSON object."]}
    audit_status = str(payload.get("audit_status", "")).strip()
    audit_status_detail = str(payload.get("audit_status_detail", "")).strip()
    raw_peft_export_ready = payload.get("peft_export_ready")
    peft_export_ready = raw_peft_export_ready if isinstance(raw_peft_export_ready, bool) else False
    if not isinstance(raw_peft_export_ready, bool):
        blocked_reasons.append(f"{audit_summary_path.name} peft_export_ready is missing or invalid.")
    elif not peft_export_ready:
        blocked_reasons.append(f"{audit_summary_path.name} peft_export_ready is false.")
    base_model_name_or_path = str(payload.get("base_model_name_or_path", "")).strip()
    if base_model_name_or_path != BASE_MODEL_NAME:
        blocked_reasons.append(
            f"{audit_summary_path.name} base_model_name_or_path {base_model_name_or_path!r} does not match expected {BASE_MODEL_NAME!r}."
        )
    try:
        unsupported_tensor_count = int(payload.get("unsupported_tensor_count"))
    except Exception:
        unsupported_tensor_count = None
        blocked_reasons.append(f"{audit_summary_path.name} unsupported_tensor_count is missing or invalid.")
    else:
        if unsupported_tensor_count != 0:
            blocked_reasons.append(f"{audit_summary_path.name} unsupported_tensor_count must be 0.")
    preview = payload.get("peft_adapter_config_preview")
    if not isinstance(preview, dict):
        preview = {}
        blocked_reasons.append(f"{audit_summary_path.name} peft_adapter_config_preview is missing.")
    preview_peft_type = str(preview.get("peft_type", "")).strip()
    if preview and preview_peft_type != str(EXPECTED_SUBMISSION_ADAPTER_CONFIG["peft_type"]):
        blocked_reasons.append(
            f"{audit_summary_path.name} peft_adapter_config_preview.peft_type {preview_peft_type!r} does not match expected {EXPECTED_SUBMISSION_ADAPTER_CONFIG['peft_type']!r}."
        )
    preview_base_model_name_or_path = str(preview.get("base_model_name_or_path", "")).strip()
    if preview and preview_base_model_name_or_path != BASE_MODEL_NAME:
        blocked_reasons.append(
            f"{audit_summary_path.name} peft_adapter_config_preview.base_model_name_or_path {preview_base_model_name_or_path!r} does not match expected {BASE_MODEL_NAME!r}."
        )
    try:
        preview_rank = int(preview.get("r")) if preview else None
    except Exception:
        preview_rank = None
        blocked_reasons.append(f"{audit_summary_path.name} peft_adapter_config_preview.r is missing or invalid.")
    else:
        if preview_rank is not None and not (0 < preview_rank <= int(README_CONTRACT["max_lora_rank"])):
            blocked_reasons.append(
                f"{audit_summary_path.name} peft_adapter_config_preview.r {preview_rank} exceeds README max_lora_rank={README_CONTRACT['max_lora_rank']}."
            )
    preview_target_modules = normalize_string_list(preview.get("target_modules") if preview else None)
    if preview and not preview_target_modules:
        blocked_reasons.append(f"{audit_summary_path.name} peft_adapter_config_preview.target_modules is missing or empty.")
    raw_preview_inference_mode = preview.get("inference_mode") if preview else None
    preview_inference_mode = raw_preview_inference_mode if isinstance(raw_preview_inference_mode, bool) else None
    if preview and preview_inference_mode is not bool(EXPECTED_SUBMISSION_ADAPTER_CONFIG["inference_mode"]):
        blocked_reasons.append(
            f"{audit_summary_path.name} peft_adapter_config_preview.inference_mode {raw_preview_inference_mode!r} does not match expected {EXPECTED_SUBMISSION_ADAPTER_CONFIG['inference_mode']!r}."
        )
    readme_submission_contract = payload.get("readme_submission_contract")
    required_files_present = False
    max_rank_matches_expected = False
    single_adapter_submission_zip_matches_expected = False
    if not isinstance(readme_submission_contract, dict):
        blocked_reasons.append(f"{audit_summary_path.name} readme_submission_contract is missing.")
    else:
        required_files = set(normalize_string_list(readme_submission_contract.get("required_files")))
        required_files_present = {"adapter_config.json", "adapter_model.safetensors"}.issubset(required_files)
        if not required_files_present:
            blocked_reasons.append(
                f"{audit_summary_path.name} readme_submission_contract.required_files is missing README-required packaged files."
            )
        try:
            max_rank_matches_expected = int(readme_submission_contract.get("max_lora_rank")) == int(
                README_CONTRACT["max_lora_rank"]
            )
        except Exception:
            max_rank_matches_expected = False
        if not max_rank_matches_expected:
            blocked_reasons.append(
                f"{audit_summary_path.name} readme_submission_contract.max_lora_rank does not match README max_lora_rank={README_CONTRACT['max_lora_rank']}."
            )
        single_adapter_submission_zip_matches_expected = (
            readme_submission_contract.get("single_adapter_submission_zip") is True
        )
        if not single_adapter_submission_zip_matches_expected:
            blocked_reasons.append(
                f"{audit_summary_path.name} readme_submission_contract.single_adapter_submission_zip must be true."
            )
    return {
        "audit_summary_valid": not blocked_reasons,
        "audit_summary_status": audit_status,
        "audit_summary_status_present": bool(audit_status),
        "audit_summary_status_detail": audit_status_detail,
        "audit_summary_peft_export_ready": peft_export_ready,
        "audit_summary_base_model_name_or_path": base_model_name_or_path,
        "audit_summary_base_model_matches_expected": base_model_name_or_path == BASE_MODEL_NAME,
        "audit_summary_preview_peft_type": preview_peft_type,
        "audit_summary_preview_peft_type_matches_expected": (
            preview_peft_type == str(EXPECTED_SUBMISSION_ADAPTER_CONFIG["peft_type"])
        ),
        "audit_summary_preview_rank": preview_rank,
        "audit_summary_preview_rank_within_readme_limit": (
            preview_rank is not None and 0 < preview_rank <= int(README_CONTRACT["max_lora_rank"])
        ),
        "audit_summary_preview_target_modules": list(preview_target_modules),
        "audit_summary_preview_target_modules_nonempty": bool(preview_target_modules),
        "audit_summary_preview_inference_mode": preview_inference_mode,
        "audit_summary_preview_inference_mode_matches_expected": (
            preview_inference_mode is bool(EXPECTED_SUBMISSION_ADAPTER_CONFIG["inference_mode"])
        ),
        "audit_summary_readme_contract_required_files_present": required_files_present,
        "audit_summary_readme_contract_max_rank_matches_expected": max_rank_matches_expected,
        "audit_summary_readme_contract_single_adapter_matches_expected": (
            single_adapter_submission_zip_matches_expected
        ),
        "audit_summary_blocked_reasons": blocked_reasons,
    }


def inspect_prepare_manifest_artifact(
    prepare_manifest_path: Path,
    *,
    expected_train_csv: Path | None = None,
) -> dict[str, Any]:
    if not prepare_manifest_path.exists():
        return {
            "prepare_manifest_valid": False,
            "prepare_manifest_base_model_name_or_path": "",
            "prepare_manifest_base_model_matches_expected": False,
            "prepare_manifest_train_csv": "",
            "prepare_manifest_expected_train_csv": (
                str(expected_train_csv.resolve()) if expected_train_csv is not None else ""
            ),
            "prepare_manifest_train_csv_matches_expected": expected_train_csv is None,
            "prepare_manifest_training_lora_rank": None,
            "prepare_manifest_training_lora_rank_within_readme_limit": False,
            "prepare_manifest_training_lora_keys": [],
            "prepare_manifest_training_lora_keys_nonempty": False,
            "prepare_manifest_training_trainable_suffixes": [],
            "prepare_manifest_training_trainable_suffixes_nonempty": False,
            "prepare_manifest_readme_contract_matches_expected": False,
            "prepare_manifest_blocked_reasons": [f"{prepare_manifest_path.name} is missing."],
        }
    try:
        payload = load_json(prepare_manifest_path)
    except Exception as exc:
        return {
            "prepare_manifest_valid": False,
            "prepare_manifest_base_model_name_or_path": "",
            "prepare_manifest_base_model_matches_expected": False,
            "prepare_manifest_train_csv": "",
            "prepare_manifest_expected_train_csv": (
                str(expected_train_csv.resolve()) if expected_train_csv is not None else ""
            ),
            "prepare_manifest_train_csv_matches_expected": expected_train_csv is None,
            "prepare_manifest_training_lora_rank": None,
            "prepare_manifest_training_lora_rank_within_readme_limit": False,
            "prepare_manifest_training_lora_keys": [],
            "prepare_manifest_training_lora_keys_nonempty": False,
            "prepare_manifest_training_trainable_suffixes": [],
            "prepare_manifest_training_trainable_suffixes_nonempty": False,
            "prepare_manifest_readme_contract_matches_expected": False,
            "prepare_manifest_blocked_reasons": [f"{prepare_manifest_path.name} could not be parsed: {exc}"],
        }
    if not isinstance(payload, dict):
        return {
            "prepare_manifest_valid": False,
            "prepare_manifest_base_model_name_or_path": "",
            "prepare_manifest_base_model_matches_expected": False,
            "prepare_manifest_train_csv": "",
            "prepare_manifest_expected_train_csv": (
                str(expected_train_csv.resolve()) if expected_train_csv is not None else ""
            ),
            "prepare_manifest_train_csv_matches_expected": expected_train_csv is None,
            "prepare_manifest_training_lora_rank": None,
            "prepare_manifest_training_lora_rank_within_readme_limit": False,
            "prepare_manifest_training_lora_keys": [],
            "prepare_manifest_training_lora_keys_nonempty": False,
            "prepare_manifest_training_trainable_suffixes": [],
            "prepare_manifest_training_trainable_suffixes_nonempty": False,
            "prepare_manifest_readme_contract_matches_expected": False,
            "prepare_manifest_blocked_reasons": [f"{prepare_manifest_path.name} is not a JSON object."],
        }
    blocked_reasons: list[str] = []
    base_model_name_or_path = str(payload.get("base_model_name_or_path", "")).strip()
    if base_model_name_or_path != BASE_MODEL_NAME:
        blocked_reasons.append(
            f"{prepare_manifest_path.name} base_model_name_or_path {base_model_name_or_path!r} does not match expected {BASE_MODEL_NAME!r}."
        )
    train_csv = str(payload.get("train_csv", "")).strip()
    if not train_csv:
        blocked_reasons.append(f"{prepare_manifest_path.name} train_csv is missing.")
    expected_train_csv_resolved = expected_train_csv.resolve() if expected_train_csv is not None else None
    prepare_manifest_train_csv_matches_expected = expected_train_csv_resolved is None
    if train_csv and expected_train_csv_resolved is not None:
        resolved_prepare_manifest_train_csv = repo_path(train_csv).resolve()
        prepare_manifest_train_csv_matches_expected = (
            resolved_prepare_manifest_train_csv == expected_train_csv_resolved
        )
        if not prepare_manifest_train_csv_matches_expected:
            blocked_reasons.append(
                f"{prepare_manifest_path.name} train_csv {str(resolved_prepare_manifest_train_csv)!r} does not match expected "
                f"{str(expected_train_csv_resolved)!r}."
            )
    training = payload.get("training")
    if not isinstance(training, dict):
        training = {}
        blocked_reasons.append(f"{prepare_manifest_path.name} training section is missing.")
    try:
        training_lora_rank = int(training.get("lora_rank")) if training else None
    except Exception:
        training_lora_rank = None
        blocked_reasons.append(f"{prepare_manifest_path.name} training.lora_rank is missing or invalid.")
    else:
        if training_lora_rank is not None and not (0 < training_lora_rank <= int(README_CONTRACT["max_lora_rank"])):
            blocked_reasons.append(
                f"{prepare_manifest_path.name} training.lora_rank {training_lora_rank} exceeds README max_lora_rank={README_CONTRACT['max_lora_rank']}."
            )
    training_lora_keys = normalize_string_list(training.get("lora_keys") if training else None)
    if training == {} or not training_lora_keys:
        blocked_reasons.append(f"{prepare_manifest_path.name} training.lora_keys is missing or empty.")
    training_trainable_suffixes = normalize_string_list(
        training.get("trainable_lora_suffixes") if training else None
    )
    if training == {} or not training_trainable_suffixes:
        blocked_reasons.append(f"{prepare_manifest_path.name} training.trainable_lora_suffixes is missing or empty.")
    readme_contract = payload.get("readme_contract")
    readme_contract_matches_expected = True
    if not isinstance(readme_contract, dict):
        readme_contract_matches_expected = False
        blocked_reasons.append(f"{prepare_manifest_path.name} readme_contract is missing.")
    else:
        for key, expected_value in README_CONTRACT.items():
            if key not in readme_contract:
                readme_contract_matches_expected = False
                blocked_reasons.append(f"{prepare_manifest_path.name} readme_contract[{key!r}] is missing.")
                continue
            if readme_contract[key] != expected_value:
                readme_contract_matches_expected = False
                blocked_reasons.append(
                    f"{prepare_manifest_path.name} readme_contract[{key!r}]={readme_contract[key]!r} does not match expected {expected_value!r}."
                )
    return {
        "prepare_manifest_valid": not blocked_reasons,
        "prepare_manifest_base_model_name_or_path": base_model_name_or_path,
        "prepare_manifest_base_model_matches_expected": base_model_name_or_path == BASE_MODEL_NAME,
        "prepare_manifest_train_csv": train_csv,
        "prepare_manifest_expected_train_csv": (
            str(expected_train_csv_resolved) if expected_train_csv_resolved is not None else ""
        ),
        "prepare_manifest_train_csv_matches_expected": prepare_manifest_train_csv_matches_expected,
        "prepare_manifest_training_lora_rank": training_lora_rank,
        "prepare_manifest_training_lora_rank_within_readme_limit": (
            training_lora_rank is not None and 0 < training_lora_rank <= int(README_CONTRACT["max_lora_rank"])
        ),
        "prepare_manifest_training_lora_keys": list(training_lora_keys),
        "prepare_manifest_training_lora_keys_nonempty": bool(training_lora_keys),
        "prepare_manifest_training_trainable_suffixes": list(training_trainable_suffixes),
        "prepare_manifest_training_trainable_suffixes_nonempty": bool(training_trainable_suffixes),
        "prepare_manifest_readme_contract_matches_expected": readme_contract_matches_expected,
        "prepare_manifest_blocked_reasons": blocked_reasons,
    }


def inspect_training_result_artifact(training_result_path: Path) -> dict[str, Any]:
    if not training_result_path.exists():
        return {
            "training_result_valid": False,
            "training_result_adapter_files_present": False,
            "training_result_adapter_config_size_bytes": None,
            "training_result_adapters_size_bytes": None,
            "training_result_latest_train_iteration": None,
            "training_result_latest_optimizer_step": None,
            "training_result_blocked_reasons": [f"{training_result_path.name} is missing."],
        }
    try:
        payload = load_json(training_result_path)
    except Exception as exc:
        return {
            "training_result_valid": False,
            "training_result_adapter_files_present": False,
            "training_result_adapter_config_size_bytes": None,
            "training_result_adapters_size_bytes": None,
            "training_result_latest_train_iteration": None,
            "training_result_latest_optimizer_step": None,
            "training_result_blocked_reasons": [f"{training_result_path.name} could not be parsed: {exc}"],
        }
    if not isinstance(payload, dict):
        return {
            "training_result_valid": False,
            "training_result_adapter_files_present": False,
            "training_result_adapter_config_size_bytes": None,
            "training_result_adapters_size_bytes": None,
            "training_result_latest_train_iteration": None,
            "training_result_latest_optimizer_step": None,
            "training_result_blocked_reasons": [f"{training_result_path.name} is not a JSON object."],
        }
    blocked_reasons: list[str] = []
    adapter_files = payload.get("adapter_files")
    adapter_files_by_name: dict[str, dict[str, Any]] = {}
    if isinstance(adapter_files, list):
        for row in adapter_files:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name", "")).strip()
            if name:
                adapter_files_by_name[name] = row
    adapter_config_row = adapter_files_by_name.get("adapter_config.json")
    adapters_row = adapter_files_by_name.get("adapters.safetensors")
    adapter_files_present = adapter_config_row is not None and adapters_row is not None
    if not adapter_files_present:
        blocked_reasons.append(
            f"{training_result_path.name} adapter_files is missing adapter_config.json or adapters.safetensors."
        )
    adapter_config_size_bytes = None
    if isinstance(adapter_config_row, dict):
        try:
            adapter_config_size_bytes = int(adapter_config_row.get("size_bytes"))
        except Exception:
            adapter_config_size_bytes = None
        if not (adapter_config_size_bytes is not None and adapter_config_size_bytes > 0):
            blocked_reasons.append(f"{training_result_path.name} adapter_config.json size_bytes is missing or non-positive.")
    adapters_size_bytes = None
    if isinstance(adapters_row, dict):
        try:
            adapters_size_bytes = int(adapters_row.get("size_bytes"))
        except Exception:
            adapters_size_bytes = None
        if not (adapters_size_bytes is not None and adapters_size_bytes > 0):
            blocked_reasons.append(f"{training_result_path.name} adapters.safetensors size_bytes is missing or non-positive.")
    latest_train_report = payload.get("latest_train_report")
    latest_train_iteration = None
    latest_optimizer_step = None
    if not isinstance(latest_train_report, dict):
        blocked_reasons.append(f"{training_result_path.name} latest_train_report is missing.")
    else:
        try:
            latest_train_iteration = int(latest_train_report.get("iteration"))
        except Exception:
            latest_train_iteration = None
            blocked_reasons.append(f"{training_result_path.name} latest_train_report.iteration is missing or invalid.")
        else:
            if latest_train_iteration <= 0:
                blocked_reasons.append(f"{training_result_path.name} latest_train_report.iteration must be positive.")
        try:
            latest_optimizer_step = int(latest_train_report.get("optimizer_step"))
        except Exception:
            latest_optimizer_step = None
            blocked_reasons.append(f"{training_result_path.name} latest_train_report.optimizer_step is missing or invalid.")
        else:
            if latest_optimizer_step <= 0:
                blocked_reasons.append(f"{training_result_path.name} latest_train_report.optimizer_step must be positive.")
    return {
        "training_result_valid": not blocked_reasons,
        "training_result_adapter_files_present": adapter_files_present,
        "training_result_adapter_config_size_bytes": adapter_config_size_bytes,
        "training_result_adapters_size_bytes": adapters_size_bytes,
        "training_result_latest_train_iteration": latest_train_iteration,
        "training_result_latest_optimizer_step": latest_optimizer_step,
        "training_result_blocked_reasons": blocked_reasons,
    }


def build_stage2_profile_artifact_state(profile_name: str) -> dict[str, Any]:
    artifact_paths = resolve_stage2_profile_artifact_paths(profile_name)
    checks = {
        "stage2_dataset_csv": artifact_paths["stage2_dataset_csv"].exists(),
        "stage2_dataset_summary_json": artifact_paths["stage2_dataset_summary_json"].exists(),
        "proxy_v2_csv": artifact_paths["proxy_v2_csv"].exists(),
        "proxy_v2_summary_json": artifact_paths["proxy_v2_summary_json"].exists(),
    }
    stage2_dataset_csv_size_bytes = (
        artifact_paths["stage2_dataset_csv"].stat().st_size if checks["stage2_dataset_csv"] else None
    )
    proxy_v2_csv_size_bytes = artifact_paths["proxy_v2_csv"].stat().st_size if checks["proxy_v2_csv"] else None
    stage2_dataset_summary = inspect_profile_summary_artifact(
        artifact_paths["stage2_dataset_summary_json"],
        expected_output_csv=artifact_paths["stage2_dataset_csv"],
    )
    proxy_v2_summary = inspect_profile_summary_artifact(
        artifact_paths["proxy_v2_summary_json"],
        expected_output_csv=artifact_paths["proxy_v2_csv"],
    )
    invalid_profile_artifacts: list[str] = []
    if checks["stage2_dataset_csv"] and not (stage2_dataset_csv_size_bytes is not None and stage2_dataset_csv_size_bytes > 0):
        invalid_profile_artifacts.append("stage2_dataset_csv_empty")
    if checks["proxy_v2_csv"] and not (proxy_v2_csv_size_bytes is not None and proxy_v2_csv_size_bytes > 0):
        invalid_profile_artifacts.append("proxy_v2_csv_empty")
    if bool(stage2_dataset_summary["summary_exists"]):
        invalid_profile_artifacts.extend(
            [
                f"stage2_dataset_summary:{reason}"
                for reason in stage2_dataset_summary["blocked_reasons"]
            ]
        )
    if bool(proxy_v2_summary["summary_exists"]):
        invalid_profile_artifacts.extend(
            [
                f"proxy_v2_summary:{reason}"
                for reason in proxy_v2_summary["blocked_reasons"]
            ]
        )
    stage2_dataset_ready = (
        checks["stage2_dataset_csv"]
        and stage2_dataset_csv_size_bytes is not None
        and stage2_dataset_csv_size_bytes > 0
        and bool(stage2_dataset_summary["summary_valid"])
    )
    proxy_v2_ready = (
        checks["proxy_v2_csv"]
        and proxy_v2_csv_size_bytes is not None
        and proxy_v2_csv_size_bytes > 0
        and bool(proxy_v2_summary["summary_valid"])
    )
    return {
        "stage2_dataset_csv": repo_relpath(artifact_paths["stage2_dataset_csv"]),
        "stage2_dataset_summary_json": repo_relpath(artifact_paths["stage2_dataset_summary_json"]),
        "proxy_v2_csv": repo_relpath(artifact_paths["proxy_v2_csv"]),
        "proxy_v2_summary_json": repo_relpath(artifact_paths["proxy_v2_summary_json"]),
        "stage2_dataset_csv_exists": checks["stage2_dataset_csv"],
        "stage2_dataset_summary_json_exists": checks["stage2_dataset_summary_json"],
        "proxy_v2_csv_exists": checks["proxy_v2_csv"],
        "proxy_v2_summary_json_exists": checks["proxy_v2_summary_json"],
        "stage2_dataset_csv_size_bytes": stage2_dataset_csv_size_bytes,
        "stage2_dataset_csv_nonempty": (
            stage2_dataset_csv_size_bytes is not None and stage2_dataset_csv_size_bytes > 0
        ),
        "stage2_dataset_summary_valid": bool(stage2_dataset_summary["summary_valid"]),
        "stage2_dataset_summary_rows": stage2_dataset_summary["rows"],
        "stage2_dataset_summary_output_csv_matches": bool(stage2_dataset_summary["output_csv_matches_expected"]),
        "proxy_v2_csv_size_bytes": proxy_v2_csv_size_bytes,
        "proxy_v2_csv_nonempty": proxy_v2_csv_size_bytes is not None and proxy_v2_csv_size_bytes > 0,
        "proxy_v2_summary_valid": bool(proxy_v2_summary["summary_valid"]),
        "proxy_v2_summary_rows": proxy_v2_summary["rows"],
        "proxy_v2_summary_output_csv_matches": bool(proxy_v2_summary["output_csv_matches_expected"]),
        "build_stage2_artifacts_needed": not (stage2_dataset_ready and proxy_v2_ready),
        "missing_profile_artifacts": [name for name, exists in checks.items() if not exists],
        "invalid_profile_artifacts": invalid_profile_artifacts,
    }


def determine_stage2_profile_next_step(
    *,
    shared_stage1_run_root_exists: bool,
    profile_artifact_state: dict[str, Any],
    run_artifact_state: dict[str, Any],
    eligible: bool,
) -> str:
    if bool(profile_artifact_state["build_stage2_artifacts_needed"]):
        return "build-stage2-artifacts"
    if not shared_stage1_run_root_exists:
        return "launch-stage1"
    if (
        not bool(run_artifact_state["prepare_manifest_exists"])
        or bool(run_artifact_state.get("prepare_manifest_blocked_reasons"))
        or not bool(run_artifact_state["training_result_exists"])
        or bool(run_artifact_state.get("training_result_blocked_reasons"))
    ):
        return "launch-stage2-linked"
    if (
        not bool(run_artifact_state["suite_summary_exists"])
        or bool(run_artifact_state.get("suite_summary_blocked_reasons"))
        or not bool(run_artifact_state["audit_summary_exists"])
        or bool(run_artifact_state.get("audit_summary_blocked_reasons"))
    ):
        return "postprocess-stage2"
    if (
        not bool(run_artifact_state["export_manifest_exists"])
        or bool(run_artifact_state["export_manifest_blocked_reasons"])
        or not bool(run_artifact_state["export_manifest_valid"])
        or not bool(run_artifact_state["export_manifest_has_converted_tensors"])
        or not bool(run_artifact_state["submission_zip_exists"])
        or bool(run_artifact_state["submission_zip_blocked_reasons"])
        or not bool(run_artifact_state["export_manifest_base_model_matches_expected"])
        or not bool(run_artifact_state["submission_zip_valid"])
        or not bool(run_artifact_state["submission_adapter_base_model_matches_expected"])
        or not bool(run_artifact_state["submission_rank_within_readme_limit"])
    ):
        return "export-stage2-submission"
    if eligible:
        return "package-stage2-matrix-best-submission"
    return "review-gate-failures"


def render_stage2_candidate_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# v3f stage2 candidate audit",
        "",
        f"- recorded_at: `{payload['recorded_at']}`",
        f"- script: `{payload['script']}`",
        f"- shared_stage1_run_root: `{payload['shared_stage1_run_root']}`",
        f"- shared_stage1_run_root_exists: `{payload['shared_stage1_run_root_exists']}`",
        f"- selected_stage2_profiles: `{', '.join(payload['selected_stage2_profiles'])}`",
        f"- all_profiles: `{payload['all_profiles']}`",
        f"- used_default_stage2_profiles: `{payload['used_default_stage2_profiles']}`",
        f"- candidate_count: `{payload['candidate_count']}`",
        f"- loaded_candidate_count: `{payload['loaded_candidate_count']}`",
        f"- eligible_candidate_count: `{payload['eligible_candidate_count']}`",
        f"- gates: `{payload['gates']}`",
        "",
    ]
    selected = payload.get("selected_candidate")
    if isinstance(selected, dict):
        lines.extend(
            [
                "## Selected candidate",
                "",
                f"- profile: `{selected['profile_name']}`",
                f"- run_root: `{selected['run_root']}`",
                f"- local320: `{format_score_row(selected['local320'])}`",
                f"- general_stable: `{format_score_row(selected['general_stable'])}`",
                f"- leaderboard_proxy_v2: `{format_score_row(selected['proxy_v2'])}`",
                f"- binary_bias_specialized_set: `{format_score_row(selected['specialized'])}`",
                f"- peft_export_ready: `{selected['peft_export_ready']}`",
                f"- build_stage2_artifacts_needed: `{selected['build_stage2_artifacts_needed']}`",
                f"- stage2_dataset_csv_nonempty: `{selected['stage2_dataset_csv_nonempty']}`",
                f"- stage2_dataset_summary_valid: `{selected['stage2_dataset_summary_valid']}`",
                f"- stage2_dataset_summary_rows: `{selected['stage2_dataset_summary_rows']}`",
                f"- proxy_v2_csv_nonempty: `{selected['proxy_v2_csv_nonempty']}`",
                f"- proxy_v2_summary_valid: `{selected['proxy_v2_summary_valid']}`",
                f"- proxy_v2_summary_rows: `{selected['proxy_v2_summary_rows']}`",
                f"- prepare_manifest_valid: `{selected['prepare_manifest_valid']}`",
                f"- prepare_manifest_train_csv_matches_expected: `{selected['prepare_manifest_train_csv_matches_expected']}`",
                f"- training_result_valid: `{selected['training_result_valid']}`",
                f"- training_result_latest_optimizer_step: `{selected['training_result_latest_optimizer_step']}`",
                f"- suite_summary_valid: `{selected['suite_summary_valid']}`",
                f"- suite_summary_required_evaluations_present: `{selected['suite_summary_required_evaluations_present']}`",
                f"- suite_summary_eval_summaries_valid: `{selected['suite_summary_eval_summaries_valid']}`",
                f"- audit_summary_valid: `{selected['audit_summary_valid']}`",
                f"- audit_summary_peft_export_ready: `{selected['audit_summary_peft_export_ready']}`",
                f"- audit_summary_preview_rank: `{selected['audit_summary_preview_rank']}`",
                f"- audit_summary_preview_rank_matches_submission: `{selected['audit_summary_preview_rank_matches_submission']}`",
                f"- audit_summary_target_modules_match_submission: `{selected['audit_summary_target_modules_match_submission']}`",
                f"- audit_summary_readme_contract_single_adapter_matches_expected: `{selected['audit_summary_readme_contract_single_adapter_matches_expected']}`",
                f"- recorded_eval_assumptions_present: `{selected['recorded_eval_assumptions_present']}`",
                f"- recorded_eval_contract_matches_readme: `{selected['recorded_eval_contract_matches_readme']}`",
                f"- recommended_next_step: `{selected['recommended_next_step']}`",
                f"- export_manifest_valid: `{selected['export_manifest_valid']}`",
                f"- export_manifest_converted_tensor_count: `{selected['export_manifest_converted_tensor_count']}`",
                f"- export_manifest_has_converted_tensors: `{selected['export_manifest_has_converted_tensors']}`",
                f"- export_manifest_target_modules_count: `{selected['export_manifest_target_modules_count']}`",
                f"- export_manifest_target_modules_nonempty: `{selected['export_manifest_target_modules_nonempty']}`",
                f"- export_manifest_target_modules_match_submission: `{selected['export_manifest_target_modules_match_submission']}`",
                f"- export_manifest_base_model_name_or_path: `{selected['export_manifest_base_model_name_or_path']}`",
                f"- export_manifest_base_model_matches_expected: `{selected['export_manifest_base_model_matches_expected']}`",
                f"- export_manifest_zip_path_matches_expected: `{selected['export_manifest_zip_path_matches_expected']}`",
                f"- export_manifest_zip_size_matches_submission: `{selected['export_manifest_zip_size_matches_submission']}`",
                f"- submission_zip_valid: `{selected['submission_zip_valid']}`",
                f"- submission_adapter_peft_type: `{selected['submission_adapter_peft_type']}`",
                f"- submission_adapter_peft_type_matches_expected: `{selected['submission_adapter_peft_type_matches_expected']}`",
                f"- submission_adapter_base_model_name_or_path: `{selected['submission_adapter_base_model_name_or_path']}`",
                f"- submission_adapter_base_model_matches_expected: `{selected['submission_adapter_base_model_matches_expected']}`",
                f"- submission_adapter_task_type: `{selected['submission_adapter_task_type']}`",
                f"- submission_adapter_task_type_matches_expected: `{selected['submission_adapter_task_type_matches_expected']}`",
                f"- submission_adapter_inference_mode: `{selected['submission_adapter_inference_mode']}`",
                f"- submission_adapter_inference_mode_matches_expected: `{selected['submission_adapter_inference_mode_matches_expected']}`",
                f"- submission_adapter_target_modules_count: `{selected['submission_adapter_target_modules_count']}`",
                f"- submission_adapter_target_modules_nonempty: `{selected['submission_adapter_target_modules_nonempty']}`",
                f"- submission_adapter_model_size_bytes: `{selected['submission_adapter_model_size_bytes']}`",
                f"- submission_adapter_model_nonempty: `{selected['submission_adapter_model_nonempty']}`",
                f"- submission_adapter_rank: `{selected['submission_adapter_rank']}`",
                f"- submission_rank_within_readme_limit: `{selected['submission_rank_within_readme_limit']}`",
                f"- submission_zip_exists: `{selected['submission_zip_exists']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Candidates",
            "",
            "| profile | run_root_exists | stage2_artifacts_ready | local320 | general_stable | proxy_v2 | specialized | exportable | eligible | recommended_next_step | missing_profile_artifacts | missing_run_artifacts |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for candidate in payload["candidates"]:
        missing_profile = (
            ", ".join(candidate["missing_profile_artifacts"]) if candidate["missing_profile_artifacts"] else "-"
        )
        missing_run = ", ".join(candidate["missing_artifacts"]) if candidate["missing_artifacts"] else "-"
        lines.append(
            f"| `{candidate['profile_name']}` | `{candidate['run_root_exists']}` | "
            f"`{not candidate['build_stage2_artifacts_needed']}` | "
            f"{format_score_row(candidate['local320'])} | "
            f"{format_score_row(candidate['general_stable'])} | {format_score_row(candidate['proxy_v2'])} | "
            f"{format_score_row(candidate['specialized'])} | `{candidate['peft_export_ready']}` | "
            f"`{candidate['eligible']}` | `{candidate['recommended_next_step']}` | `{missing_profile}` | `{missing_run}` |"
        )
    failing_candidates = [candidate for candidate in payload["candidates"] if candidate["gate_failures"]]
    if failing_candidates:
        lines.extend(["", "## Gate failures", ""])
        for candidate in failing_candidates:
            lines.append(f"### {candidate['profile_name']}")
            lines.append("")
            lines.append(f"- run_root: `{candidate['run_root']}`")
            lines.append(f"- build_stage2_artifacts_needed: `{candidate['build_stage2_artifacts_needed']}`")
            if candidate["missing_profile_artifacts"]:
                lines.append(f"- missing_profile_artifacts: `{candidate['missing_profile_artifacts']}`")
            if candidate["invalid_profile_artifacts"]:
                lines.append(f"- invalid_profile_artifacts: `{candidate['invalid_profile_artifacts']}`")
            if candidate["prepare_manifest_blocked_reasons"]:
                lines.append(f"- prepare_manifest_blocked_reasons: `{candidate['prepare_manifest_blocked_reasons']}`")
            if candidate["training_result_blocked_reasons"]:
                lines.append(f"- training_result_blocked_reasons: `{candidate['training_result_blocked_reasons']}`")
            if candidate["suite_summary_blocked_reasons"]:
                lines.append(f"- suite_summary_blocked_reasons: `{candidate['suite_summary_blocked_reasons']}`")
            if candidate["audit_summary_blocked_reasons"]:
                lines.append(f"- audit_summary_blocked_reasons: `{candidate['audit_summary_blocked_reasons']}`")
            if candidate["recorded_eval_contract_mismatches"]:
                lines.append(f"- recorded_eval_contract_mismatches: `{candidate['recorded_eval_contract_mismatches']}`")
            if candidate["export_manifest_blocked_reasons"]:
                lines.append(f"- export_manifest_blocked_reasons: `{candidate['export_manifest_blocked_reasons']}`")
            if candidate["submission_zip_blocked_reasons"]:
                lines.append(f"- submission_zip_blocked_reasons: `{candidate['submission_zip_blocked_reasons']}`")
            for reason in candidate["gate_failures"]:
                lines.append(f"- {reason}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def command_write_stage2_candidate_audit(args: argparse.Namespace) -> int:
    selected_profiles = select_stage2_profiles(
        list(getattr(args, "profile", [])),
        all_profiles=bool(getattr(args, "all_profiles", False)),
    )
    require(selected_profiles, "No Stage2 profiles selected.")
    monolith = load_monolith_submission_helpers()
    gates = monolith.build_submission_candidate_gates(args)
    shared_stage1_run_root = REPO_ROOT / "baseline_mlx" / "outputs" / STAGE1_RUN_NAME
    shared_stage1_run_root_exists = shared_stage1_run_root.exists()
    candidates: list[dict[str, Any]] = []
    loaded_candidates: list[dict[str, Any]] = []
    suite_summary_relpath = Path(args.suite_summary_relpath)
    audit_relpath = Path(args.audit_relpath)
    export_relpath = Path(args.export_relpath)

    for profile in selected_profiles:
        run_root = stage2_run_root_from_profile(profile)
        profile_artifact_state = build_stage2_profile_artifact_state(profile["profile_name"])
        artifact_state = build_stage2_candidate_artifact_state(
            run_root,
            suite_summary_relpath=suite_summary_relpath,
            audit_relpath=audit_relpath,
            export_relpath=export_relpath,
            expected_stage2_train_csv=repo_path(profile_artifact_state["stage2_dataset_csv"]),
        )
        try:
            payload = monolith.load_run_result_payload(
                run_root=run_root,
                label=profile["profile_name"],
                suite_summary_relpath=suite_summary_relpath,
                audit_relpath=audit_relpath,
                export_relpath=export_relpath,
            )
            candidate = monolith.build_submission_candidate_from_payload(payload)
            eligible, reasons = monolith.evaluate_submission_candidate(candidate, gates=gates)
            reasons = list(reasons)
            reasons.extend(str(item) for item in artifact_state["prepare_manifest_blocked_reasons"])
            reasons.extend(str(item) for item in artifact_state["training_result_blocked_reasons"])
            reasons.extend(str(item) for item in artifact_state["suite_summary_blocked_reasons"])
            reasons.extend(str(item) for item in artifact_state["audit_summary_blocked_reasons"])
            reasons.extend(str(item) for item in artifact_state["export_manifest_blocked_reasons"])
            reasons.extend(str(item) for item in artifact_state["submission_zip_blocked_reasons"])
            eligible = (
                bool(eligible)
                and not artifact_state["prepare_manifest_blocked_reasons"]
                and not artifact_state["training_result_blocked_reasons"]
                and not artifact_state["suite_summary_blocked_reasons"]
                and not artifact_state["audit_summary_blocked_reasons"]
                and not artifact_state["export_manifest_blocked_reasons"]
                and not artifact_state["submission_zip_blocked_reasons"]
            )
            candidate_row = {
                "profile_name": profile["profile_name"],
                "description": profile["description"],
                "stage2_run_name": profile["stage2_run_name"],
                "run_root": str(run_root),
                "load_status": "loaded",
                "eligible": bool(eligible),
                "gate_failures": list(reasons),
                "local320": dict(candidate["local320"]),
                "general_stable": dict(candidate["general_stable"]),
                "proxy_v1": dict(candidate["proxy_v1"]),
                "proxy_v2": dict(candidate["proxy_v2"]),
                "specialized": dict(candidate["specialized"]),
                "binary_hard": dict(candidate["binary_hard"]),
                "symbol_watch": dict(candidate["symbol_watch"]),
                "audit_status": str(candidate["audit_status"]),
                "peft_export_ready": candidate["peft_export_ready"] is True,
                "has_export_manifest": bool(candidate["has_export_manifest"]),
                "train_csv": str(candidate["train_csv"]),
                "trainable_lora_suffixes": list(candidate["trainable_lora_suffixes"]),
                "lora_keys": list(candidate["lora_keys"]),
                "sort_key": list(monolith.candidate_selection_sort_key(candidate)),
                **profile_artifact_state,
                **artifact_state,
            }
            candidate_row["recommended_next_step"] = determine_stage2_profile_next_step(
                shared_stage1_run_root_exists=shared_stage1_run_root_exists,
                profile_artifact_state=profile_artifact_state,
                run_artifact_state=artifact_state,
                eligible=bool(candidate_row["eligible"]),
            )
            loaded_candidates.append(candidate_row)
        except FileNotFoundError as exc:
            empty = (
                monolith.make_empty_score_row()
                if hasattr(monolith, "make_empty_score_row")
                else empty_score_row()
            )
            candidate_row = {
                "profile_name": profile["profile_name"],
                "description": profile["description"],
                "stage2_run_name": profile["stage2_run_name"],
                "run_root": str(run_root),
                "load_status": "missing_artifacts",
                "eligible": False,
                "gate_failures": [str(exc)],
                "local320": dict(empty),
                "general_stable": dict(empty),
                "proxy_v1": dict(empty),
                "proxy_v2": dict(empty),
                "specialized": dict(empty),
                "binary_hard": dict(empty),
                "symbol_watch": dict(empty),
                "audit_status": "",
                "peft_export_ready": False,
                "has_export_manifest": bool(artifact_state["export_manifest_exists"]),
                "train_csv": "",
                "trainable_lora_suffixes": [],
                "lora_keys": [],
                "sort_key": [0.0] * 7,
                **profile_artifact_state,
                **artifact_state,
            }
            candidate_row["recommended_next_step"] = determine_stage2_profile_next_step(
                shared_stage1_run_root_exists=shared_stage1_run_root_exists,
                profile_artifact_state=profile_artifact_state,
                run_artifact_state=artifact_state,
                eligible=False,
            )
        candidates.append(candidate_row)

    sorted_loaded_candidates = sorted(
        loaded_candidates,
        key=lambda candidate: tuple(float(value) for value in candidate["sort_key"]),
        reverse=True,
    )
    eligible_candidates = [candidate for candidate in sorted_loaded_candidates if candidate["eligible"]]
    payload = {
        "recorded_at": utc_now(),
        "script": str(Path(__file__).resolve()),
        "gates": gates,
        "shared_stage1_run_root": str(shared_stage1_run_root),
        "shared_stage1_run_root_exists": shared_stage1_run_root_exists,
        "all_profiles": bool(getattr(args, "all_profiles", False)),
        "used_default_stage2_profiles": not bool(getattr(args, "profile", []))
        and not bool(getattr(args, "all_profiles", False)),
        "selected_stage2_profiles": [profile["profile_name"] for profile in selected_profiles],
        "candidate_count": len(candidates),
        "loaded_candidate_count": len(sorted_loaded_candidates),
        "eligible_candidate_count": len(eligible_candidates),
        "selected_candidate": eligible_candidates[0] if eligible_candidates else None,
        "candidates": candidates,
        "top_candidates": sorted_loaded_candidates[:5],
        "suite_summary_relpath": str(suite_summary_relpath),
        "audit_relpath": str(audit_relpath),
        "export_relpath": str(export_relpath),
    }
    output_root = repo_path(args.output_root)
    summary_json = output_root / "v3f_stage2_candidate_audit.json"
    summary_md = output_root / "v3f_stage2_candidate_audit.md"
    dump_json(summary_json, payload)
    dump_markdown(summary_md, render_stage2_candidate_audit_markdown(payload))
    print(summary_json)
    return 0


def command_launch_stage2_matrix(args: argparse.Namespace) -> int:
    selected_profiles = select_stage2_profiles(
        list(getattr(args, "profile", [])),
        all_profiles=bool(getattr(args, "all_profiles", False)),
    )
    require(selected_profiles, "No Stage2 profiles selected.")
    build_commands = [profile["artifact_build_command"] for profile in selected_profiles]
    launched_commands: list[str] = []

    if not args.skip_build_stage2_artifacts:
        for build_command in build_commands:
            run_command(shlex.split(build_command), dry_run=args.dry_run)

    if not args.skip_stage1:
        stage1_command = selected_profiles[0]["stage1_launch_command"]
        launched_commands.append(stage1_command)
        run_command(shlex.split(stage1_command), dry_run=args.dry_run)

    for profile in selected_profiles:
        launched_commands.append(profile["stage2_linked_command"])
        run_command(shlex.split(profile["stage2_linked_command"]), dry_run=args.dry_run)
        if not args.skip_postprocess:
            launched_commands.append(profile["postprocess_command"])
            run_command(shlex.split(profile["postprocess_command"]), dry_run=args.dry_run)

    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "launch-stage2-matrix",
        {
            "dry_run": args.dry_run,
            "skip_build_stage2_artifacts": args.skip_build_stage2_artifacts,
            "skip_stage1": args.skip_stage1,
            "skip_postprocess": args.skip_postprocess,
            "all_profiles": bool(getattr(args, "all_profiles", False)),
            "used_default_stage2_profiles": not bool(getattr(args, "profile", []))
            and not bool(getattr(args, "all_profiles", False)),
            "selected_stage2_profiles": [profile["profile_name"] for profile in selected_profiles],
            "matrix_build_commands": build_commands,
            "matrix_launch_commands": launched_commands,
            "matrix_export_commands": [profile["export_command"] for profile in selected_profiles],
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def command_package_stage2_matrix_best_submission(args: argparse.Namespace) -> int:
    selected_profiles = select_stage2_profiles(
        list(getattr(args, "profile", [])),
        all_profiles=bool(getattr(args, "all_profiles", False)),
    )
    require(selected_profiles, "No Stage2 profiles selected.")
    candidate_run_roots = [stage2_run_root_from_profile(profile) for profile in selected_profiles]
    command = uv_command(
        "package-best-submission",
        "--output-root",
        repo_path(args.output_root),
        "--results-md",
        repo_path(args.results_md),
        "--base-model-name-or-path",
        args.base_model_name_or_path,
        "--min-local320-accuracy",
        str(args.min_local320_accuracy),
        "--min-general-stable-accuracy",
        str(args.min_general_stable_accuracy),
        "--min-proxy-v2-accuracy",
        str(args.min_proxy_v2_accuracy),
        "--min-specialized-accuracy",
        str(args.min_specialized_accuracy),
        "--require-exportable" if args.require_exportable else "--no-require-exportable",
        "--export-if-missing" if args.export_if_missing else "--no-export-if-missing",
        "--update-results-md" if args.update_results_md else "--no-update-results-md",
    )
    for run_root in candidate_run_roots:
        command.extend(["--candidate-run-root", str(run_root)])
    run_command(command, dry_run=args.dry_run)

    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "package-stage2-matrix-best-submission",
        {
            "dry_run": args.dry_run,
            "all_profiles": bool(getattr(args, "all_profiles", False)),
            "used_default_stage2_profiles": not bool(getattr(args, "profile", []))
            and not bool(getattr(args, "all_profiles", False)),
            "selected_stage2_profiles": [profile["profile_name"] for profile in selected_profiles],
            "candidate_run_roots": [str(run_root) for run_root in candidate_run_roots],
            "best_submission_output_root": str(repo_path(args.output_root)),
            "base_model_name_or_path": args.base_model_name_or_path,
            "require_exportable": args.require_exportable,
            "export_if_missing": args.export_if_missing,
            "update_results_md": args.update_results_md,
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def command_build_stage2_artifacts(args: argparse.Namespace) -> int:
    output_csv = repo_path(args.output_csv)
    output_summary = repo_path(args.summary_json)
    proxy_csv = repo_path(args.proxy_v2_csv)
    proxy_summary = repo_path(args.proxy_v2_summary_json)

    proxy_command = uv_command(
        "build-leaderboard-proxy-v2",
        "--output-csv",
        proxy_csv,
        "--summary-json",
        proxy_summary,
        "--max-binary-hard-rows",
        "24",
        "--max-symbol-rows",
        "11",
    )
    for focus_bucket in PROXY_V2_FOCUS_BUCKETS:
        proxy_command.extend(["--focus-bucket", focus_bucket])
    for solver in STAGE2_BINARY_SOLVERS:
        proxy_command.extend(["--binary-solver", solver])
    run_command(proxy_command, dry_run=args.dry_run)

    corrective_command = uv_command(
        "build-corrective-stage2-csv",
        "--output-csv",
        output_csv,
        "--summary-json",
        output_summary,
        "--max-symbol-rows",
        str(args.max_symbol_rows),
        "--max-answer-only-ratio",
        str(args.max_answer_only_ratio),
        "--max-manual-audit-ratio",
        str(args.max_manual_audit_ratio),
    )
    for solver in STAGE2_BINARY_SOLVERS:
        corrective_command.extend(["--binary-solver", solver])
    run_command(corrective_command, dry_run=args.dry_run)

    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "build-stage2-artifacts",
        {
            "dry_run": args.dry_run,
            "built_stage2_dataset_csv": str(output_csv),
            "built_stage2_dataset_summary_json": str(output_summary),
            "built_proxy_v2_csv": str(proxy_csv),
            "built_proxy_v2_summary_json": str(proxy_summary),
            "max_answer_only_ratio": float(args.max_answer_only_ratio),
            "max_manual_audit_ratio": float(args.max_manual_audit_ratio),
            "manual_audit_template_subtypes": list(DEFAULT_STAGE2_MANUAL_AUDIT_TEMPLATE_SUBTYPES),
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def command_launch_stage1(args: argparse.Namespace) -> int:
    output_root = repo_path(args.output_root)
    run_command(
        uv_command(
            "resume-train-from-run",
            "--profile",
            "notebook-current",
            "--source-run-root",
            repo_path(args.source_run_root),
            "--train-csv",
            repo_path(args.train_csv),
            "--output-root",
            output_root,
            "--run-name",
            args.run_name,
            "--learning-rate",
            str(args.learning_rate),
            "--num-epochs",
            str(args.num_epochs),
            "--max-seq-length",
            str(args.max_seq_length),
            "--valid-shadow-rows",
            str(args.valid_shadow_rows),
            "--lora-key-group",
            str(args.lora_key_group),
            "--trainable-lora-suffix-group",
            str(args.trainable_lora_suffix_group),
            "--skip-if-target-started",
        ),
        dry_run=args.dry_run,
    )
    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "launch-stage1",
        {
            "dry_run": args.dry_run,
            "launched_stage1_run_root": str(output_root / args.run_name),
            "stage1_lora_key_group": str(args.lora_key_group),
            "stage1_trainable_lora_suffix_group": str(args.trainable_lora_suffix_group),
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def command_launch_stage2(args: argparse.Namespace) -> int:
    output_root = repo_path(args.output_root)
    type_samples = resolve_stage2_type_samples(
        explicit_type_samples=getattr(args, "type_sample", None),
        dataset_summary_json=getattr(args, "dataset_summary_json", None),
    )
    command = uv_command(
        "resume-train-from-run",
        "--profile",
        "notebook-current",
        "--source-run-root",
        repo_path(args.source_run_root),
        "--train-csv",
        repo_path(args.train_csv),
        "--output-root",
        output_root,
        "--run-name",
        args.run_name,
        "--learning-rate",
        str(args.learning_rate),
        "--num-epochs",
        str(args.num_epochs),
        "--max-seq-length",
        str(args.max_seq_length),
        "--valid-shadow-rows",
        str(args.valid_shadow_rows),
        "--lora-key-group",
        str(args.lora_key_group),
        "--trainable-lora-suffix-group",
        str(args.trainable_lora_suffix_group),
        "--skip-if-target-started",
    )
    for type_sample in type_samples:
        command.extend(["--type-sample", type_sample])
    run_command(command, dry_run=args.dry_run)
    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "launch-stage2",
        {
            "dry_run": args.dry_run,
            "launched_stage2_run_root": str(output_root / args.run_name),
            "stage2_type_samples": type_samples,
            "stage2_lora_key_group": str(args.lora_key_group),
            "stage2_trainable_lora_suffix_group": str(args.trainable_lora_suffix_group),
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def command_launch_stage2_linked(args: argparse.Namespace) -> int:
    output_root = repo_path(args.output_root)
    type_samples = resolve_stage2_type_samples(
        explicit_type_samples=getattr(args, "type_sample", None),
        dataset_summary_json=getattr(args, "dataset_summary_json", None),
    )
    command = uv_command(
        "wait-train-from-run",
        "--profile",
        "notebook-current",
        "--source-run-root",
        repo_path(args.source_run_root),
        "--train-csv",
        repo_path(args.train_csv),
        "--output-root",
        output_root,
        "--run-name",
        args.run_name,
        "--learning-rate",
        str(args.learning_rate),
        "--num-epochs",
        str(args.num_epochs),
        "--max-seq-length",
        str(args.max_seq_length),
        "--valid-shadow-rows",
        str(args.valid_shadow_rows),
        "--poll-seconds",
        str(args.poll_seconds),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--lora-key-group",
        str(args.lora_key_group),
        "--trainable-lora-suffix-group",
        str(args.trainable_lora_suffix_group),
        "--skip-if-target-started",
    )
    if args.min_free_percent is not None:
        command.extend(["--min-free-percent", str(args.min_free_percent)])
    if args.min_free_gb is not None:
        command.extend(["--min-free-gb", str(args.min_free_gb)])
    for type_sample in type_samples:
        command.extend(["--type-sample", type_sample])
    run_command(command, dry_run=args.dry_run)
    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "launch-stage2-linked",
        {
            "dry_run": args.dry_run,
            "linked_stage2_source_run_root": str(repo_path(args.source_run_root)),
            "linked_stage2_run_root": str(output_root / args.run_name),
            "stage2_type_samples": type_samples,
            "wait_poll_seconds": float(args.poll_seconds),
            "wait_timeout_seconds": float(args.timeout_seconds),
            "min_free_percent": args.min_free_percent,
            "min_free_gb": args.min_free_gb,
            "stage2_lora_key_group": str(args.lora_key_group),
            "stage2_trainable_lora_suffix_group": str(args.trainable_lora_suffix_group),
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def command_run_full_pipeline(args: argparse.Namespace) -> int:
    output_root = repo_path(args.output_root)
    stage1_run_root = output_root / args.stage1_run_name
    stage2_run_root = output_root / args.stage2_run_name
    proxy_csv = repo_path(args.proxy_v2_csv)
    proxy_summary = repo_path(args.proxy_v2_summary_json)
    stage2_dataset_csv = repo_path(args.stage2_dataset_csv)
    stage2_dataset_summary_json = repo_path(args.stage2_dataset_summary_json)

    proxy_command = uv_command(
        "build-leaderboard-proxy-v2",
        "--output-csv",
        proxy_csv,
        "--summary-json",
        proxy_summary,
        "--max-binary-hard-rows",
        "24",
        "--max-symbol-rows",
        "11",
    )
    for focus_bucket in PROXY_V2_FOCUS_BUCKETS:
        proxy_command.extend(["--focus-bucket", focus_bucket])
    for solver in STAGE2_BINARY_SOLVERS:
        proxy_command.extend(["--binary-solver", solver])
    run_command(proxy_command, dry_run=args.dry_run)

    corrective_command = uv_command(
        "build-corrective-stage2-csv",
        "--output-csv",
        stage2_dataset_csv,
        "--summary-json",
        stage2_dataset_summary_json,
        "--max-symbol-rows",
        str(args.stage2_max_symbol_rows),
        "--max-answer-only-ratio",
        str(args.stage2_max_answer_only_ratio),
        "--max-manual-audit-ratio",
        str(args.stage2_max_manual_audit_ratio),
    )
    for solver in STAGE2_BINARY_SOLVERS:
        corrective_command.extend(["--binary-solver", solver])
    run_command(corrective_command, dry_run=args.dry_run)

    stage1_command = uv_command(
        "resume-train-from-run",
        "--profile",
        "notebook-current",
        "--source-run-root",
        repo_path(args.stage1_source_run_root),
        "--train-csv",
        repo_path(args.stage1_train_csv),
        "--output-root",
        output_root,
        "--run-name",
        args.stage1_run_name,
        "--learning-rate",
        str(args.stage1_learning_rate),
        "--num-epochs",
        str(args.stage1_num_epochs),
        "--max-seq-length",
        str(args.stage1_max_seq_length),
        "--valid-shadow-rows",
        str(args.stage1_valid_shadow_rows),
        "--lora-key-group",
        str(args.stage1_lora_key_group),
        "--trainable-lora-suffix-group",
        str(args.stage1_trainable_lora_suffix_group),
        "--skip-if-target-started",
    )
    run_command(stage1_command, dry_run=args.dry_run)

    type_samples = resolve_stage2_type_samples(
        explicit_type_samples=getattr(args, "type_sample", None),
        dataset_summary_json=stage2_dataset_summary_json,
    )
    stage2_command = uv_command(
        "wait-train-from-run",
        "--profile",
        "notebook-current",
        "--source-run-root",
        stage1_run_root,
        "--train-csv",
        stage2_dataset_csv,
        "--output-root",
        output_root,
        "--run-name",
        args.stage2_run_name,
        "--learning-rate",
        str(args.stage2_learning_rate),
        "--num-epochs",
        str(args.stage2_num_epochs),
        "--max-seq-length",
        str(args.stage2_max_seq_length),
        "--valid-shadow-rows",
        str(args.stage2_valid_shadow_rows),
        "--poll-seconds",
        str(args.stage2_poll_seconds),
        "--timeout-seconds",
        str(args.stage2_timeout_seconds),
        "--lora-key-group",
        str(args.stage2_lora_key_group),
        "--trainable-lora-suffix-group",
        str(args.stage2_trainable_lora_suffix_group),
        "--skip-if-target-started",
    )
    if args.stage2_min_free_percent is not None:
        stage2_command.extend(["--min-free-percent", str(args.stage2_min_free_percent)])
    if args.stage2_min_free_gb is not None:
        stage2_command.extend(["--min-free-gb", str(args.stage2_min_free_gb)])
    for type_sample in type_samples:
        stage2_command.extend(["--type-sample", type_sample])
    run_command(stage2_command, dry_run=args.dry_run)

    postprocess_command = uv_command(
        "postprocess-run",
        "--run-root",
        stage2_run_root,
        "--label",
        args.label,
        "--wait-for-training-result",
        "--poll-seconds",
        str(args.postprocess_poll_seconds),
        "--max-tokens",
        str(getattr(args, "max_tokens", README_CONTRACT["max_tokens"])),
        "--temperature",
        str(getattr(args, "temperature", README_CONTRACT["temperature"])),
        "--top-p",
        str(getattr(args, "top_p", README_CONTRACT["top_p"])),
        "--max-num-seqs",
        str(getattr(args, "max_num_seqs", README_CONTRACT["max_num_seqs"])),
        "--gpu-memory-utilization",
        str(getattr(args, "gpu_memory_utilization", README_CONTRACT["gpu_memory_utilization"])),
        "--max-model-len",
        str(getattr(args, "max_model_len", README_CONTRACT["max_model_len"])),
        "--eval-enable-thinking" if getattr(args, "eval_enable_thinking", True) else "--no-eval-enable-thinking",
        "--extra-benchmark-csv",
        proxy_csv,
        "--extra-benchmark-csv",
        repo_path(args.specialized_csv),
        "--run-record-run-result",
        "--results-md",
        repo_path(args.results_md),
        "--run-publish-results-md" if args.run_publish_results_md else "--no-run-publish-results-md",
        "--publish-commit-message",
        args.publish_commit_message,
        "--run-package-best-submission" if args.run_package_best_submission else "--no-run-package-best-submission",
        "--min-local320-accuracy",
        str(args.min_local320_accuracy),
        "--min-general-stable-accuracy",
        str(args.min_general_stable_accuracy),
        "--min-proxy-v2-accuracy",
        str(args.min_proxy_v2_accuracy),
        "--min-specialized-accuracy",
        str(args.min_specialized_accuracy),
    )
    run_command(postprocess_command, dry_run=args.dry_run)

    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "run-full-pipeline",
        {
            "dry_run": args.dry_run,
            "full_pipeline_stage1_run_root": str(stage1_run_root),
            "full_pipeline_stage2_run_root": str(stage2_run_root),
            "built_proxy_v2_csv": str(proxy_csv),
            "built_proxy_v2_summary_json": str(proxy_summary),
            "built_stage2_dataset_csv": str(stage2_dataset_csv),
            "built_stage2_dataset_summary_json": str(stage2_dataset_summary_json),
            "stage2_max_answer_only_ratio": float(args.stage2_max_answer_only_ratio),
            "stage2_max_manual_audit_ratio": float(args.stage2_max_manual_audit_ratio),
            "stage2_manual_audit_template_subtypes": list(DEFAULT_STAGE2_MANUAL_AUDIT_TEMPLATE_SUBTYPES),
            "stage2_type_samples": type_samples,
            "stage1_lora_key_group": str(args.stage1_lora_key_group),
            "stage1_trainable_lora_suffix_group": str(args.stage1_trainable_lora_suffix_group),
            "stage2_lora_key_group": str(args.stage2_lora_key_group),
            "stage2_trainable_lora_suffix_group": str(args.stage2_trainable_lora_suffix_group),
            "run_publish_results_md": args.run_publish_results_md,
            "run_package_best_submission": args.run_package_best_submission,
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def command_postprocess_stage2(args: argparse.Namespace) -> int:
    command = uv_command(
        "postprocess-run",
        "--run-root",
        repo_path(args.run_root),
        "--label",
        args.label,
        "--wait-for-training-result",
        "--poll-seconds",
        str(args.poll_seconds),
        "--max-tokens",
        str(getattr(args, "max_tokens", README_CONTRACT["max_tokens"])),
        "--temperature",
        str(getattr(args, "temperature", README_CONTRACT["temperature"])),
        "--top-p",
        str(getattr(args, "top_p", README_CONTRACT["top_p"])),
        "--max-num-seqs",
        str(getattr(args, "max_num_seqs", README_CONTRACT["max_num_seqs"])),
        "--gpu-memory-utilization",
        str(getattr(args, "gpu_memory_utilization", README_CONTRACT["gpu_memory_utilization"])),
        "--max-model-len",
        str(getattr(args, "max_model_len", README_CONTRACT["max_model_len"])),
        "--eval-enable-thinking" if getattr(args, "eval_enable_thinking", True) else "--no-eval-enable-thinking",
        "--extra-benchmark-csv",
        repo_path(args.proxy_v2_csv),
        "--extra-benchmark-csv",
        repo_path(args.specialized_csv),
        "--run-record-run-result",
        "--results-md",
        repo_path(args.results_md),
        "--run-publish-results-md" if args.run_publish_results_md else "--no-run-publish-results-md",
        "--publish-commit-message",
        args.publish_commit_message,
        "--run-package-best-submission" if args.run_package_best_submission else "--no-run-package-best-submission",
        "--min-local320-accuracy",
        str(args.min_local320_accuracy),
        "--min-general-stable-accuracy",
        str(args.min_general_stable_accuracy),
        "--min-proxy-v2-accuracy",
        str(args.min_proxy_v2_accuracy),
        "--min-specialized-accuracy",
        str(args.min_specialized_accuracy),
    )
    run_command(command, dry_run=args.dry_run)
    summary_path = write_summary(
        repo_path(args.summary_output_root),
        "postprocess-stage2",
        {
            "dry_run": args.dry_run,
            "postprocess_run_root": str(repo_path(args.run_root)),
            "run_publish_results_md": args.run_publish_results_md,
            "run_package_best_submission": args.run_package_best_submission,
        },
    )
    print(json.dumps({"summary_path": str(summary_path)}, indent=2, sort_keys=True))
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Single-file README-aligned wrapper for the v3f-style submission-compatible stage-freeze line."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="Verify the local v3f blueprint assets and print the summary JSON.")
    verify.set_defaults(func=command_verify)

    write_summary_parser = subparsers.add_parser("write-summary", help="Write JSON/Markdown summary files for this line.")
    write_summary_parser.add_argument("--output-root", default=str(Path(__file__).resolve().parent))
    write_summary_parser.set_defaults(func=command_write_summary)

    write_stage2_matrix = subparsers.add_parser(
        "write-stage2-matrix",
        help="Write JSON/Markdown launch recipes for parallel Stage2 corrective profiles.",
    )
    write_stage2_matrix.add_argument("--output-root", default=str(Path(__file__).resolve().parent))
    write_stage2_matrix.set_defaults(func=command_write_stage2_matrix)

    write_stage2_candidate_audit = subparsers.add_parser(
        "write-stage2-candidate-audit",
        help="Write a Git-visible static gate audit for selected Stage2 matrix profiles before package-stage2-matrix-best-submission.",
    )
    write_stage2_candidate_audit.add_argument("--profile", action="append", default=[])
    write_stage2_candidate_audit.add_argument("--all-profiles", action="store_true")
    write_stage2_candidate_audit.add_argument("--output-root", default=str(Path(__file__).resolve().parent))
    write_stage2_candidate_audit.add_argument(
        "--suite-summary-relpath",
        type=Path,
        default=DEFAULT_RUN_SUITE_SUMMARY_RELPATH,
    )
    write_stage2_candidate_audit.add_argument(
        "--audit-relpath",
        type=Path,
        default=DEFAULT_RUN_AUDIT_RELPATH,
    )
    write_stage2_candidate_audit.add_argument(
        "--export-relpath",
        type=Path,
        default=DEFAULT_RUN_EXPORT_RELPATH,
    )
    write_stage2_candidate_audit.add_argument(
        "--min-local320-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_local320_accuracy"],
    )
    write_stage2_candidate_audit.add_argument(
        "--min-general-stable-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_general_stable_accuracy"],
    )
    write_stage2_candidate_audit.add_argument(
        "--min-proxy-v2-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_proxy_v2_accuracy"],
    )
    write_stage2_candidate_audit.add_argument(
        "--min-specialized-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_specialized_accuracy"],
    )
    write_stage2_candidate_audit.add_argument(
        "--require-exportable",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["require_exportable"],
    )
    write_stage2_candidate_audit.set_defaults(func=command_write_stage2_candidate_audit)

    launch_stage2_matrix = subparsers.add_parser(
        "launch-stage2-matrix",
        help="Launch shared Stage1 once and then arm multiple Stage2 linked/postprocess profile lanes. Defaults to the curated default/noanswer/manual trio unless --profile or --all-profiles is set.",
    )
    launch_stage2_matrix.add_argument("--profile", action="append", default=[])
    launch_stage2_matrix.add_argument("--all-profiles", action="store_true")
    launch_stage2_matrix.add_argument("--skip-build-stage2-artifacts", action="store_true")
    launch_stage2_matrix.add_argument("--skip-stage1", action="store_true")
    launch_stage2_matrix.add_argument("--skip-postprocess", action="store_true")
    launch_stage2_matrix.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    launch_stage2_matrix.add_argument("--dry-run", action="store_true")
    launch_stage2_matrix.set_defaults(func=command_launch_stage2_matrix)

    package_stage2_matrix_best_submission = subparsers.add_parser(
        "package-stage2-matrix-best-submission",
        help="Package the best README-compatible submission.zip from selected Stage2 matrix profiles. Defaults to the curated default/noanswer/manual trio unless --profile or --all-profiles is set.",
    )
    package_stage2_matrix_best_submission.add_argument("--profile", action="append", default=[])
    package_stage2_matrix_best_submission.add_argument("--all-profiles", action="store_true")
    package_stage2_matrix_best_submission.add_argument(
        "--output-root",
        default=str(REPO_ROOT / "baseline_mlx" / "outputs" / "v3f_stage2_matrix_best_submission"),
    )
    package_stage2_matrix_best_submission.add_argument("--results-md", default=str(RESULTS_MD))
    package_stage2_matrix_best_submission.add_argument("--base-model-name-or-path", default=BASE_MODEL_NAME)
    package_stage2_matrix_best_submission.add_argument(
        "--min-local320-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_local320_accuracy"],
    )
    package_stage2_matrix_best_submission.add_argument(
        "--min-general-stable-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_general_stable_accuracy"],
    )
    package_stage2_matrix_best_submission.add_argument(
        "--min-proxy-v2-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_proxy_v2_accuracy"],
    )
    package_stage2_matrix_best_submission.add_argument(
        "--min-specialized-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_specialized_accuracy"],
    )
    package_stage2_matrix_best_submission.add_argument(
        "--require-exportable",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["require_exportable"],
    )
    package_stage2_matrix_best_submission.add_argument(
        "--export-if-missing", action=argparse.BooleanOptionalAction, default=True
    )
    package_stage2_matrix_best_submission.add_argument(
        "--update-results-md", action=argparse.BooleanOptionalAction, default=False
    )
    package_stage2_matrix_best_submission.add_argument(
        "--summary-output-root", default=str(Path(__file__).resolve().parent)
    )
    package_stage2_matrix_best_submission.add_argument("--dry-run", action="store_true")
    package_stage2_matrix_best_submission.set_defaults(func=command_package_stage2_matrix_best_submission)

    export_stage2_submission = subparsers.add_parser(
        "export-stage2-submission",
        help="Export a Stage2 MLX adapter into a README-compatible submission.zip using derived run-root paths.",
    )
    export_stage2_submission.add_argument(
        "--run-root",
        default=str(REPO_ROOT / "baseline_mlx" / "outputs" / STAGE2_RUN_NAME),
    )
    export_stage2_submission.add_argument("--adapter-dir", default=None)
    export_stage2_submission.add_argument("--output-root", default=None)
    export_stage2_submission.add_argument("--reference-model-root", default=None)
    export_stage2_submission.add_argument("--base-model-name-or-path", default=BASE_MODEL_NAME)
    export_stage2_submission.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    export_stage2_submission.add_argument("--dry-run", action="store_true")
    export_stage2_submission.set_defaults(func=command_export_stage2_submission)

    build_stage2 = subparsers.add_parser(
        "build-stage2-artifacts",
        help="Build the v3f proxy_v2 watch set and the narrow Stage2 corrective dataset.",
    )
    build_stage2.add_argument("--output-csv", default=str(STAGE2_DATASET_CSV))
    build_stage2.add_argument("--summary-json", default=str(STAGE2_DATASET_SUMMARY_JSON))
    build_stage2.add_argument("--proxy-v2-csv", default=str(PROXY_V2_CSV))
    build_stage2.add_argument("--proxy-v2-summary-json", default=str(PROXY_V2_SUMMARY_JSON))
    build_stage2.add_argument("--max-symbol-rows", type=int, default=9)
    build_stage2.add_argument("--max-answer-only-ratio", type=float, default=0.05)
    build_stage2.add_argument("--max-manual-audit-ratio", type=float, default=DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO)
    build_stage2.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    build_stage2.add_argument("--dry-run", action="store_true")
    build_stage2.set_defaults(func=command_build_stage2_artifacts)

    launch_stage1 = subparsers.add_parser(
        "launch-stage1",
        help="Launch the broad exportsafe Stage1 trunk from the notebook-original fullrun root.",
    )
    launch_stage1.add_argument("--source-run-root", default=str(SOURCE_BASE_RUN_ROOT))
    launch_stage1.add_argument("--train-csv", default=str(STAGE1_DATASET_CSV))
    launch_stage1.add_argument("--output-root", default=str(REPO_ROOT / "baseline_mlx" / "outputs"))
    launch_stage1.add_argument("--run-name", default=STAGE1_RUN_NAME)
    launch_stage1.add_argument("--learning-rate", type=float, default=1e-4)
    launch_stage1.add_argument("--num-epochs", type=float, default=2.0)
    launch_stage1.add_argument("--max-seq-length", type=int, default=4096)
    launch_stage1.add_argument("--valid-shadow-rows", type=int, default=1)
    launch_stage1.add_argument("--lora-key-group", default=DEFAULT_STAGE1_LORA_KEY_GROUP)
    launch_stage1.add_argument(
        "--trainable-lora-suffix-group",
        default=DEFAULT_STAGE1_TRAINABLE_LORA_SUFFIX_GROUP,
    )
    launch_stage1.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    launch_stage1.add_argument("--dry-run", action="store_true")
    launch_stage1.set_defaults(func=command_launch_stage1)

    launch_stage2 = subparsers.add_parser(
        "launch-stage2",
        help="Launch the attention-only Stage2 corrective run from the completed Stage1 root.",
    )
    launch_stage2.add_argument(
        "--source-run-root",
        default=str(REPO_ROOT / "baseline_mlx" / "outputs" / STAGE1_RUN_NAME),
    )
    launch_stage2.add_argument("--train-csv", default=str(STAGE2_DATASET_CSV))
    launch_stage2.add_argument("--dataset-summary-json", default=str(STAGE2_DATASET_SUMMARY_JSON))
    launch_stage2.add_argument("--output-root", default=str(REPO_ROOT / "baseline_mlx" / "outputs"))
    launch_stage2.add_argument("--run-name", default=STAGE2_RUN_NAME)
    launch_stage2.add_argument("--learning-rate", type=float, default=2e-5)
    launch_stage2.add_argument("--num-epochs", type=float, default=0.75)
    launch_stage2.add_argument("--max-seq-length", type=int, default=1536)
    launch_stage2.add_argument("--valid-shadow-rows", type=int, default=1)
    launch_stage2.add_argument("--lora-key-group", default=DEFAULT_STAGE2_LORA_KEY_GROUP)
    launch_stage2.add_argument(
        "--trainable-lora-suffix-group",
        default=DEFAULT_STAGE2_TRAINABLE_LORA_SUFFIX_GROUP,
    )
    launch_stage2.add_argument("--type-sample", action="append", default=[])
    launch_stage2.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    launch_stage2.add_argument("--dry-run", action="store_true")
    launch_stage2.set_defaults(func=command_launch_stage2)

    launch_stage2_linked = subparsers.add_parser(
        "launch-stage2-linked",
        help="Arm Stage2 in advance with wait-train-from-run so it starts automatically after Stage1 completes.",
    )
    launch_stage2_linked.add_argument(
        "--source-run-root",
        default=str(REPO_ROOT / "baseline_mlx" / "outputs" / STAGE1_RUN_NAME),
    )
    launch_stage2_linked.add_argument("--train-csv", default=str(STAGE2_DATASET_CSV))
    launch_stage2_linked.add_argument("--dataset-summary-json", default=str(STAGE2_DATASET_SUMMARY_JSON))
    launch_stage2_linked.add_argument("--output-root", default=str(REPO_ROOT / "baseline_mlx" / "outputs"))
    launch_stage2_linked.add_argument("--run-name", default=STAGE2_RUN_NAME)
    launch_stage2_linked.add_argument("--learning-rate", type=float, default=2e-5)
    launch_stage2_linked.add_argument("--num-epochs", type=float, default=0.75)
    launch_stage2_linked.add_argument("--max-seq-length", type=int, default=1536)
    launch_stage2_linked.add_argument("--valid-shadow-rows", type=int, default=1)
    launch_stage2_linked.add_argument("--lora-key-group", default=DEFAULT_STAGE2_LORA_KEY_GROUP)
    launch_stage2_linked.add_argument(
        "--trainable-lora-suffix-group",
        default=DEFAULT_STAGE2_TRAINABLE_LORA_SUFFIX_GROUP,
    )
    launch_stage2_linked.add_argument("--poll-seconds", type=float, default=60.0)
    launch_stage2_linked.add_argument("--timeout-seconds", type=float, default=0.0)
    launch_stage2_linked.add_argument("--min-free-percent", type=float, default=None)
    launch_stage2_linked.add_argument("--min-free-gb", type=float, default=None)
    launch_stage2_linked.add_argument("--type-sample", action="append", default=[])
    launch_stage2_linked.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    launch_stage2_linked.add_argument("--dry-run", action="store_true")
    launch_stage2_linked.set_defaults(func=command_launch_stage2_linked)

    run_full_pipeline = subparsers.add_parser(
        "run-full-pipeline",
        help="Build Stage2 artifacts, launch Stage1, arm linked Stage2, and start postprocess in one single-file command.",
    )
    run_full_pipeline.add_argument("--output-root", default=str(REPO_ROOT / "baseline_mlx" / "outputs"))
    run_full_pipeline.add_argument("--stage1-source-run-root", default=str(SOURCE_BASE_RUN_ROOT))
    run_full_pipeline.add_argument("--stage1-train-csv", default=str(STAGE1_DATASET_CSV))
    run_full_pipeline.add_argument("--stage1-run-name", default=STAGE1_RUN_NAME)
    run_full_pipeline.add_argument("--stage1-learning-rate", type=float, default=1e-4)
    run_full_pipeline.add_argument("--stage1-num-epochs", type=float, default=2.0)
    run_full_pipeline.add_argument("--stage1-max-seq-length", type=int, default=4096)
    run_full_pipeline.add_argument("--stage1-valid-shadow-rows", type=int, default=1)
    run_full_pipeline.add_argument("--stage1-lora-key-group", default=DEFAULT_STAGE1_LORA_KEY_GROUP)
    run_full_pipeline.add_argument(
        "--stage1-trainable-lora-suffix-group",
        default=DEFAULT_STAGE1_TRAINABLE_LORA_SUFFIX_GROUP,
    )
    run_full_pipeline.add_argument("--proxy-v2-csv", default=str(PROXY_V2_CSV))
    run_full_pipeline.add_argument("--proxy-v2-summary-json", default=str(PROXY_V2_SUMMARY_JSON))
    run_full_pipeline.add_argument("--stage2-dataset-csv", default=str(STAGE2_DATASET_CSV))
    run_full_pipeline.add_argument("--stage2-dataset-summary-json", default=str(STAGE2_DATASET_SUMMARY_JSON))
    run_full_pipeline.add_argument("--stage2-max-symbol-rows", type=int, default=9)
    run_full_pipeline.add_argument("--stage2-max-answer-only-ratio", type=float, default=0.05)
    run_full_pipeline.add_argument(
        "--stage2-max-manual-audit-ratio",
        type=float,
        default=DEFAULT_STAGE2_MAX_MANUAL_AUDIT_RATIO,
    )
    run_full_pipeline.add_argument("--stage2-run-name", default=STAGE2_RUN_NAME)
    run_full_pipeline.add_argument("--stage2-learning-rate", type=float, default=2e-5)
    run_full_pipeline.add_argument("--stage2-num-epochs", type=float, default=0.75)
    run_full_pipeline.add_argument("--stage2-max-seq-length", type=int, default=1536)
    run_full_pipeline.add_argument("--stage2-valid-shadow-rows", type=int, default=1)
    run_full_pipeline.add_argument("--stage2-lora-key-group", default=DEFAULT_STAGE2_LORA_KEY_GROUP)
    run_full_pipeline.add_argument(
        "--stage2-trainable-lora-suffix-group",
        default=DEFAULT_STAGE2_TRAINABLE_LORA_SUFFIX_GROUP,
    )
    run_full_pipeline.add_argument("--stage2-poll-seconds", type=float, default=60.0)
    run_full_pipeline.add_argument("--stage2-timeout-seconds", type=float, default=0.0)
    run_full_pipeline.add_argument("--stage2-min-free-percent", type=float, default=None)
    run_full_pipeline.add_argument("--stage2-min-free-gb", type=float, default=None)
    run_full_pipeline.add_argument("--type-sample", action="append", default=[])
    run_full_pipeline.add_argument("--specialized-csv", default=str(SPECIALIZED_CSV))
    run_full_pipeline.add_argument("--label", default="v3f submission line v1")
    run_full_pipeline.add_argument("--postprocess-poll-seconds", type=int, default=60)
    run_full_pipeline.add_argument("--max-tokens", type=int, default=README_CONTRACT["max_tokens"])
    run_full_pipeline.add_argument("--temperature", type=float, default=README_CONTRACT["temperature"])
    run_full_pipeline.add_argument("--top-p", type=float, default=README_CONTRACT["top_p"])
    run_full_pipeline.add_argument("--max-num-seqs", type=int, default=README_CONTRACT["max_num_seqs"])
    run_full_pipeline.add_argument(
        "--gpu-memory-utilization", type=float, default=README_CONTRACT["gpu_memory_utilization"]
    )
    run_full_pipeline.add_argument("--max-model-len", type=int, default=README_CONTRACT["max_model_len"])
    run_full_pipeline.add_argument("--eval-enable-thinking", action=argparse.BooleanOptionalAction, default=True)
    run_full_pipeline.add_argument("--results-md", default=str(RESULTS_MD))
    run_full_pipeline.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    run_full_pipeline.add_argument(
        "--min-local320-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_local320_accuracy"],
    )
    run_full_pipeline.add_argument(
        "--min-general-stable-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_general_stable_accuracy"],
    )
    run_full_pipeline.add_argument(
        "--min-proxy-v2-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_proxy_v2_accuracy"],
    )
    run_full_pipeline.add_argument(
        "--min-specialized-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_specialized_accuracy"],
    )
    run_full_pipeline.add_argument("--publish-commit-message", default="Record v3f submission line results")
    run_full_pipeline.add_argument("--dry-run", action="store_true")
    run_full_pipeline.add_argument("--run-publish-results-md", action=argparse.BooleanOptionalAction, default=False)
    run_full_pipeline.add_argument(
        "--run-package-best-submission",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    run_full_pipeline.set_defaults(func=command_run_full_pipeline)

    postprocess_stage2 = subparsers.add_parser(
        "postprocess-stage2",
        help="Run the README local320 + proxy_v2 + specialized suite, then record/publish/package if requested.",
    )
    postprocess_stage2.add_argument(
        "--run-root",
        default=str(REPO_ROOT / "baseline_mlx" / "outputs" / STAGE2_RUN_NAME),
    )
    postprocess_stage2.add_argument("--proxy-v2-csv", default=str(PROXY_V2_CSV))
    postprocess_stage2.add_argument("--specialized-csv", default=str(SPECIALIZED_CSV))
    postprocess_stage2.add_argument("--label", default="v3f submission line v1")
    postprocess_stage2.add_argument("--poll-seconds", type=int, default=60)
    postprocess_stage2.add_argument("--max-tokens", type=int, default=README_CONTRACT["max_tokens"])
    postprocess_stage2.add_argument("--temperature", type=float, default=README_CONTRACT["temperature"])
    postprocess_stage2.add_argument("--top-p", type=float, default=README_CONTRACT["top_p"])
    postprocess_stage2.add_argument("--max-num-seqs", type=int, default=README_CONTRACT["max_num_seqs"])
    postprocess_stage2.add_argument(
        "--gpu-memory-utilization", type=float, default=README_CONTRACT["gpu_memory_utilization"]
    )
    postprocess_stage2.add_argument("--max-model-len", type=int, default=README_CONTRACT["max_model_len"])
    postprocess_stage2.add_argument("--eval-enable-thinking", action=argparse.BooleanOptionalAction, default=True)
    postprocess_stage2.add_argument("--results-md", default=str(RESULTS_MD))
    postprocess_stage2.add_argument("--summary-output-root", default=str(Path(__file__).resolve().parent))
    postprocess_stage2.add_argument(
        "--min-local320-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_local320_accuracy"],
    )
    postprocess_stage2.add_argument(
        "--min-general-stable-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_general_stable_accuracy"],
    )
    postprocess_stage2.add_argument(
        "--min-proxy-v2-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_proxy_v2_accuracy"],
    )
    postprocess_stage2.add_argument(
        "--min-specialized-accuracy",
        type=float,
        default=DEFAULT_STAGE2_CANDIDATE_GATES["min_specialized_accuracy"],
    )
    postprocess_stage2.add_argument("--publish-commit-message", default="Record v3f submission line results")
    postprocess_stage2.add_argument("--dry-run", action="store_true")
    postprocess_stage2.add_argument("--run-publish-results-md", action=argparse.BooleanOptionalAction, default=False)
    postprocess_stage2.add_argument(
        "--run-package-best-submission",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    postprocess_stage2.set_defaults(func=command_postprocess_stage2)

    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
