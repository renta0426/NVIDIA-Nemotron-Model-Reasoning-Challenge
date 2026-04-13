#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path("/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge")
README_PATH = Path(__file__).resolve().parent / "README.md"
UV_PYTHON = ["uv", "run", "python"]
PIPELINE_RELPATH = Path("baseline_mlx") / "reproduce_nemotron_sft_lora_with_cot_v2_mlx.py"
PIPELINE_PATH = REPO_ROOT / PIPELINE_RELPATH
THRESHOLD_SCRIPT_RELPATH = (
    Path("versions") / "baseline_mlx_threshold_submission_v1" / "reproduce_threshold_submission.py"
)
THRESHOLD_SCRIPT_PATH = REPO_ROOT / THRESHOLD_SCRIPT_RELPATH
RETIRE_TARGETS = {
    "reprobridge23_text3bit1num8raw5unitedge": "reprobridge23",
}
REQUIRED_COMMAND = "reproduce_nemotron_sft_lora_with_cot_v2_mlx.py"
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

RUN31 = (
    "baseline_mlx/outputs/"
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "o30best_proxybench30ao_reprobridge31_text3bit1num8raw12unitedge_lr1e6_len1024_from_proxybench_v1"
)
RUN32 = (
    "baseline_mlx/outputs/"
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "o30best_proxybench30ao_reprobridge32_text3bit1num8raw13nounit_lr1e6_len1024_from_proxybench_v1"
)

RUN30_SUITE = (
    REPO_ROOT
    / "baseline_mlx/outputs/"
    / "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
      "o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1/"
      "eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json"
)
RUN27 = (
    "baseline_mlx/outputs/"
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1"
)
RUN28 = (
    "baseline_mlx/outputs/"
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1"
)
RUN29 = (
    "baseline_mlx/outputs/"
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1"
)
RUN30 = (
    "baseline_mlx/outputs/"
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1"
)
RUN31_PREPARE = REPO_ROOT / RUN31 / "prepare_manifest.json"
RUN31_SUITE = REPO_ROOT / RUN31 / "eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json"
RUN32_PREPARE = REPO_ROOT / RUN32 / "prepare_manifest.json"
RUN32_SUITE = REPO_ROOT / RUN32 / "eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json"

WAITERS31 = Path("/tmp/reprobridge31_waiters")
WAITERS32 = Path("/tmp/reprobridge32_waiters")
TRAIN_SPLIT_CSV = REPO_ROOT / "baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv"
ANALYSIS_CSV = REPO_ROOT / "cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv"
TRAIN_SPLIT_SOURCE = "baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv"
RULE_BASED_SOURCE = "baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv"
BEST_SELECTOR_SUMMARY = REPO_ROOT / "baseline_mlx/outputs/best_submission_candidate_proxybench_auto/poll_best_submission_summary.json"
TYPE_TO_BUCKET = {
    "Bit Manipulation": "Bit",
    "Text Encryption": "Text",
    "Gravitational Constant": "Gravity",
    "Unit Conversion": "Unit",
    "Equation Transformation": "Equation",
}


@dataclass(frozen=True)
class FollowupStep:
    step_name: str
    base_dataset_rel: str
    base_summary_rel: str
    output_dataset_rel: str
    output_summary_rel: str
    remove_id: str
    add_id: str
    strategy: str
    rationale: str
    source_bridge_label: str
    bridge_family_status: str
    remove_note_key: str
    add_note_key: str


FOLLOWUP_STEPS = (
    FollowupStep(
        step_name="reprobridge33",
        base_dataset_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge32_text3bit1num8raw13nounit_v1.csv"
        ),
        base_summary_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge32_text3bit1num8raw13nounit_v1_summary.json"
        ),
        output_dataset_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge33_text3bit1num8raw14nounit_v1.csv"
        ),
        output_summary_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge33_text3bit1num8raw14nounit_v1_summary.json"
        ),
        remove_id="8c6a158e",
        add_id="27cec7a9",
        strategy="raw14_no_unit_from_reprobridge32",
        rationale=(
            "start from reprobridge32, remove the remaining rule-based symbolic outlier 8c6a158e, "
            "and swap in the stable train_split numeric_2x2 row 27cec7a9 to continue the no-unit branch "
            "with a verified_trace_ready equation core"
        ),
        source_bridge_label="reprobridge32 raw13 nounit",
        bridge_family_status=(
            "The bridge family remains on the no-unit branch while replacing the last rule-based symbolic "
            "equation outlier with a stable train_split numeric row."
        ),
        remove_note_key="removed_rule_based_symbolic_row",
        add_note_key="added_train_split_numeric_row",
    ),
    FollowupStep(
        step_name="reprobridge34",
        base_dataset_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge33_text3bit1num8raw14nounit_v1.csv"
        ),
        base_summary_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge33_text3bit1num8raw14nounit_v1_summary.json"
        ),
        output_dataset_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1.csv"
        ),
        output_summary_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1_summary.json"
        ),
        remove_id="db6a5663",
        add_id="2af7134e",
        strategy="raw15_no_unit_from_reprobridge33",
        rationale=(
            "start from reprobridge33, remove the last remaining rule-based numeric exception db6a5663, "
            "and swap in the next train_split verified_trace_ready numeric_2x2 row 2af7134e to deepen the "
            "no-unit continuation with an all-train_split equation frontier"
        ),
        source_bridge_label="reprobridge33 raw14 nounit",
        bridge_family_status=(
            "The bridge family stays on the no-unit branch and removes the final rule-based equation exception "
            "from this continuation path."
        ),
        remove_note_key="removed_rule_based_numeric_row",
        add_note_key="added_train_split_numeric_row",
    ),
    FollowupStep(
        step_name="reprobridge35",
        base_dataset_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1.csv"
        ),
        base_summary_rel=(
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1_summary.json"
        ),
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
        rationale=(
            "start from reprobridge34, replace the weaker concat_xy verified_trace_ready numeric_2x2 row "
            "1c48f9aa with the unused train_split row 6b393b81 to keep the no-unit branch while slightly "
            "improving operator consistency after stronger hard-score upgrades were exhausted"
        ),
        source_bridge_label="reprobridge34 raw15 nounit",
        bridge_family_status=(
            "The bridge family stays on the no-unit branch and begins same-tier lateral refreshes because "
            "the stronger verified_trace_ready equation upgrades are already exhausted in this frontier."
        ),
        remove_note_key="removed_weaker_concat_xy_row",
        add_note_key="added_higher_consistency_concat_xy_row",
    ),
    FollowupStep(
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
        rationale=(
            "start from reprobridge35, replace the lower-consistency concat_yx verified_trace_ready "
            "numeric_2x2 row 27cec7a9 with the unused train_split row 552e14d7 to continue the no-unit "
            "lateral refresh while preserving the all-train_split equation mix"
        ),
        source_bridge_label="reprobridge35 raw16 nounit",
        bridge_family_status=(
            "The bridge family remains on the no-unit branch and continues same-tier equation refreshes "
            "instead of introducing new unit anchors or lower-confidence operator shifts."
        ),
        remove_note_key="removed_lower_consistency_concat_yx_row",
        add_note_key="added_higher_consistency_concat_yx_row",
    ),
)
RUN_STATUS_ROOTS = {
    "reprobridge23": (
        "baseline_mlx/outputs/"
        "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
        "o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1"
    ),
    "reprobridge24": (
        "baseline_mlx/outputs/"
        "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
        "o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1"
    ),
    "reprobridge25": (
        "baseline_mlx/outputs/"
        "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
        "o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1"
    ),
    "reprobridge26": (
        "baseline_mlx/outputs/"
        "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
        "o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1"
    ),
    "reprobridge27": RUN27,
    "reprobridge28": RUN28,
    "reprobridge29": RUN29,
    "reprobridge30": RUN30,
    "reprobridge31": RUN31,
    "reprobridge32": RUN32,
}
RUN_STATUS_ARTIFACTS = {
    "reprobridge27": {
        "dataset_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_v1.csv"
        ),
        "summary_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_v1_summary.json"
        ),
    },
    "reprobridge28": {
        "dataset_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_v1.csv"
        ),
        "summary_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_v1_summary.json"
        ),
    },
    "reprobridge29": {
        "dataset_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_v1.csv"
        ),
        "summary_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_v1_summary.json"
        ),
    },
    "reprobridge30": {
        "dataset_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_v1.csv"
        ),
        "summary_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_v1_summary.json"
        ),
    },
    "reprobridge31": {
        "dataset_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge31_text3bit1num8raw12unitedge_v1.csv"
        ),
        "summary_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge31_text3bit1num8raw12unitedge_v1_summary.json"
        ),
    },
    "reprobridge32": {
        "dataset_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge32_text3bit1num8raw13nounit_v1.csv"
        ),
        "summary_rel": (
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/"
            "stage25_o30best_proxybench30ao_reprobridge32_text3bit1num8raw13nounit_v1_summary.json"
        ),
    },
}
EXPECTED_WAITERS = ("launcher", "live", "postprocess", "threshold075", "threshold080")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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
            if raw_value == "":
                raise SystemExit(f"Malformed README.md evaluation row for {key}: missing value")
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
    if missing_keys:
        raise SystemExit(f"Missing README.md evaluation rows: {', '.join(missing_keys)}")
    return contract


def verify_readme_contract_file() -> dict[str, Any]:
    contract = load_readme_contract_from_readme()
    for key in README_TABLE_KEYS:
        expected_value = README_EVAL_CONTRACT[key]
        actual_value = contract.get(key)
        if actual_value != expected_value:
            raise SystemExit(
                f"README.md evaluation table mismatch for {key}: expected {expected_value}, got {actual_value}"
            )
    return contract


def load_readme_submission_contract_from_readme() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()
    if "adapter_config.json" not in text:
        raise SystemExit(
            "README.md submitting contract no longer states that the LoRA adapter must include adapter_config.json."
        )
    if README_SUBMISSION_ARCHIVE_NAME.lower() not in lower_text:
        raise SystemExit(
            f"README.md submitting contract no longer states that the submission archive is {README_SUBMISSION_ARCHIVE_NAME}."
        )
    if "submit a lora adapter" not in lower_text:
        raise SystemExit("README.md submitting contract no longer states that the submission is a single LoRA adapter.")
    return {
        "required_files": list(README_SUBMISSION_REQUIRED_FILES),
        "max_lora_rank": int(load_readme_contract_from_readme()["max_lora_rank"]),
        "single_adapter_submission_zip": True,
        "submission_archive_name": README_SUBMISSION_ARCHIVE_NAME,
    }


def verify_readme_submission_contract_file() -> dict[str, Any]:
    contract = load_readme_submission_contract_from_readme()
    if int(contract["max_lora_rank"]) != int(README_SUBMISSION_CONTRACT["max_lora_rank"]):
        raise SystemExit(
            "README.md submission contract mismatch for max_lora_rank: "
            f"expected {README_SUBMISSION_CONTRACT['max_lora_rank']}, got {contract['max_lora_rank']}"
        )
    if str(contract["submission_archive_name"]) != str(README_SUBMISSION_CONTRACT["submission_archive_name"]):
        raise SystemExit(
            "README.md submission contract mismatch for submission_archive_name: "
            f"expected {README_SUBMISSION_CONTRACT['submission_archive_name']}, got {contract['submission_archive_name']}"
        )
    if bool(contract["single_adapter_submission_zip"]) is not True:
        raise SystemExit("README.md submission contract mismatch for single_adapter_submission_zip: expected true.")
    return contract


def tail_text(path: Path, max_lines: int = 5) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return lines[-max_lines:]


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    if not fieldnames:
        raise ValueError(f"Missing CSV header: {path}")
    return fieldnames, rows


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_row_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["id"]: row for row in rows}


def project_row(row: dict[str, str], fieldnames: list[str]) -> dict[str, str]:
    return {field: row.get(field, "") for field in fieldnames}


def load_analysis_index(target_ids: set[str]) -> dict[str, dict[str, str]]:
    with ANALYSIS_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = {
            row["id"]: row
            for row in reader
            if row.get("id") in target_ids
        }
    missing = sorted(target_ids - set(rows))
    if missing:
        raise KeyError(f"Missing analysis rows: {missing}")
    return rows


def detail_from_analysis(row: dict[str, str]) -> dict[str, str]:
    return {
        "family": row.get("family", ""),
        "subfamily": row.get("subfamily", ""),
        "template_subtype": row.get("template_subtype", ""),
        "selection_tier": row.get("selection_tier", ""),
        "hard_score": row.get("hard_score", ""),
        "answer_only_ready": row.get("answer_only_ready", ""),
    }


def compute_mix(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {bucket: 0 for bucket in TYPE_TO_BUCKET.values()}
    for row in rows:
        row_type = row.get("type", "")
        if row_type not in TYPE_TO_BUCKET:
            raise ValueError(f"Unexpected row type {row_type!r} in output dataset")
        counts[TYPE_TO_BUCKET[row_type]] += 1
    return counts


def remaining_unit_rows(rows: list[dict[str, str]]) -> list[str]:
    return [row["id"] for row in rows if row.get("type") == "Unit Conversion"]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def materialize_followup_step(
    step: FollowupStep,
    source_index: dict[str, dict[str, str]],
    analysis_index: dict[str, dict[str, str]],
    dry_run: bool,
) -> dict[str, object]:
    base_dataset_path = REPO_ROOT / step.base_dataset_rel
    output_dataset_path = REPO_ROOT / step.output_dataset_rel
    base_summary_path = REPO_ROOT / step.base_summary_rel
    output_summary_path = REPO_ROOT / step.output_summary_rel

    fieldnames, base_rows = read_csv_rows(base_dataset_path)
    base_index = build_row_index(base_rows)
    if step.remove_id not in base_index:
        raise KeyError(f"{step.remove_id} is not present in {base_dataset_path}")
    if step.add_id in base_index:
        raise ValueError(f"{step.add_id} already exists in {base_dataset_path}")

    add_row = project_row(source_index[step.add_id], fieldnames)
    output_rows: list[dict[str, str]] = []
    replaced = False
    for row in base_rows:
        if row["id"] == step.remove_id:
            output_rows.append(add_row)
            replaced = True
        else:
            output_rows.append(row)
    if not replaced:
        raise RuntimeError(f"Failed to replace {step.remove_id} in {base_dataset_path}")

    base_summary = load_json(base_summary_path)
    notes = base_summary.get("notes")
    base_notes = notes if isinstance(notes, dict) else {}
    mix = compute_mix(output_rows)
    summary = {
        "created_at": now_iso(),
        "base_dataset": step.base_dataset_rel,
        "output_dataset": step.output_dataset_rel,
        "strategy": step.strategy,
        "rationale": step.rationale,
        "removed_rows": [step.remove_id],
        "added_rows": [step.add_id],
        "removed_row_details": {
            step.remove_id: detail_from_analysis(analysis_index[step.remove_id]),
        },
        "added_row_details": {
            step.add_id: detail_from_analysis(analysis_index[step.add_id]),
        },
        "resulting_mix": mix,
        "notes": {
            step.remove_note_key: [step.remove_id],
            step.add_note_key: [step.add_id],
            "remaining_unit_rows_include": remaining_unit_rows(output_rows),
            "bridge_family_status": step.bridge_family_status,
            "row_source_files": {
                step.add_id: TRAIN_SPLIT_SOURCE,
            },
            "source_bridge_rows": [
                step.source_bridge_label,
            ],
            "cot_sources": base_notes.get(
                "cot_sources",
                [TRAIN_SPLIT_SOURCE, RULE_BASED_SOURCE],
            ),
        },
    }

    if not dry_run:
        write_csv_rows(output_dataset_path, fieldnames, output_rows)
        output_summary_path.parent.mkdir(parents=True, exist_ok=True)
        output_summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return {
        "step_name": step.step_name,
        "base_dataset": step.base_dataset_rel,
        "output_dataset": step.output_dataset_rel,
        "output_summary": step.output_summary_rel,
        "removed_rows": [step.remove_id],
        "added_rows": [step.add_id],
        "resulting_mix": mix,
        "dry_run": dry_run,
    }


def materialize_followups(step_name: str, dry_run: bool) -> list[dict[str, object]]:
    selected_steps = [
        step for step in FOLLOWUP_STEPS
        if step_name == "all" or step.step_name == step_name
    ]
    target_ids = {
        row_id
        for step in selected_steps
        for row_id in (step.remove_id, step.add_id)
    }
    _, source_rows = read_csv_rows(TRAIN_SPLIT_CSV)
    source_index = build_row_index(source_rows)
    missing_source = sorted(target_ids - set(source_index))
    if missing_source:
        raise KeyError(f"Missing train_split rows: {missing_source}")
    analysis_index = load_analysis_index(target_ids)
    return [
        materialize_followup_step(
            step=step,
            source_index=source_index,
            analysis_index=analysis_index,
            dry_run=dry_run,
        )
        for step in selected_steps
    ]


def summarize_waiter_dir(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
            "files": [],
            "logs": {},
            "pids": {},
            "missing_waiters": list(EXPECTED_WAITERS),
        }
    entries = sorted(child.name for child in path.iterdir())
    logs: dict[str, object] = {}
    pid_rows: dict[str, object] = {}
    for child in path.iterdir():
        if child.suffix == ".log":
            logs[child.name] = {
                "path": str(child),
                "tail": tail_text(child),
            }
        if child.suffix == ".pid":
            waiter_name = child.stem
            raw_pid = child.read_text(encoding="utf-8").strip()
            try:
                pid = int(raw_pid)
            except ValueError:
                pid = None
            log_path = path / f"{waiter_name}.log"
            pid_rows[waiter_name] = {
                "path": str(child),
                "pid": pid,
                "pid_alive": is_pid_alive(pid) if isinstance(pid, int) and pid > 0 else False,
                "log_path": str(log_path),
                "log_exists": log_path.exists(),
            }
    missing_waiters = [
        waiter_name for waiter_name in EXPECTED_WAITERS
        if waiter_name not in pid_rows
    ]
    return {
        "exists": True,
        "path": str(path),
        "files": entries,
        "logs": logs,
        "pids": pid_rows,
        "missing_waiters": missing_waiters,
    }


def summarize_progress_file(path: Path) -> dict[str, object] | None:
    payload = load_json_if_exists(path)
    if payload is None:
        return None
    keys = (
        "recorded_at",
        "status",
        "evaluation_name",
        "rows_total",
        "rows_completed",
        "chunks_total",
        "chunks_completed",
        "correct",
        "accuracy",
        "evaluations_total",
        "evaluations_completed",
        "current_evaluation",
        "current_rows_total",
        "current_rows_completed",
        "current_chunks_total",
        "current_chunks_completed",
    )
    return {key: payload[key] for key in keys if key in payload}


def summarize_suite_summary(path: Path) -> dict[str, object] | None:
    payload = load_json_if_exists(path)
    if payload is None:
        return None
    summary: dict[str, object] = {"created_at": payload.get("created_at")}
    if isinstance(payload.get("readme_contract"), dict):
        summary["readme_contract"] = payload.get("readme_contract")
    if "readme_contract_verified_from_readme_file" in payload:
        summary["readme_contract_verified_from_readme_file"] = payload.get(
            "readme_contract_verified_from_readme_file"
        )
    evaluations = payload.get("evaluations", [])
    if not isinstance(evaluations, list):
        summary["evaluations"] = []
        return summary
    summary["evaluations"] = [
        {
            "evaluation_name": item.get("evaluation_name"),
            "rows": item.get("rows"),
            "correct": item.get("correct"),
            "accuracy": item.get("accuracy"),
        }
        for item in evaluations
        if isinstance(item, dict)
    ]
    return summary


def summarize_postprocess(path: Path) -> dict[str, object] | None:
    payload = load_json_if_exists(path)
    if payload is None:
        return None
    steps = payload.get("steps", {})
    summarized_steps: dict[str, object] = {}
    if isinstance(steps, dict):
        for step_name, step_payload in steps.items():
            if isinstance(step_payload, dict):
                summarized_steps[step_name] = {
                    key: step_payload.get(key)
                    for key in ("status", "output_root", "audit_status", "selection_status")
                    if key in step_payload
                }
    return {
        "recorded_at": payload.get("recorded_at"),
        "steps": summarized_steps,
    }


def summarize_submission_audit(path: Path) -> dict[str, object] | None:
    payload = load_json_if_exists(path)
    if payload is None:
        return None
    summary = {
        key: payload.get(key)
        for key in (
            "created_at",
            "audit_status",
            "peft_export_ready",
            "blocked_reasons",
            "base_model_name_or_path",
            "tensor_count",
        )
        if key in payload
    }
    if isinstance(payload.get("readme_submission_contract"), dict):
        summary["readme_submission_contract"] = payload.get("readme_submission_contract")
    if "readme_submission_contract_verified_from_readme_file" in payload:
        summary["readme_submission_contract_verified_from_readme_file"] = payload.get(
            "readme_submission_contract_verified_from_readme_file"
        )
    return summary


def summarize_export_manifest(path: Path) -> dict[str, object] | None:
    payload = load_json_if_exists(path)
    if payload is None:
        return None
    summary = {
        key: payload.get(key)
        for key in (
            "created_at",
            "zip_path",
            "zip_size_bytes",
            "converted_tensor_count",
            "base_model_name_or_path",
        )
        if key in payload
    }
    validation = payload.get("validation")
    if isinstance(validation, dict):
        summary["validation"] = {
            key: validation.get(key)
            for key in ("valid", "missing_keys", "unexpected_keys", "shape_mismatches")
            if key in validation
        }
    if isinstance(payload.get("readme_submission_contract"), dict):
        summary["readme_submission_contract"] = payload.get("readme_submission_contract")
    if "readme_submission_contract_verified_from_readme_file" in payload:
        summary["readme_submission_contract_verified_from_readme_file"] = payload.get(
            "readme_submission_contract_verified_from_readme_file"
        )
    return summary


def missing_postprocess_artifacts(run_payload: dict[str, object]) -> list[str]:
    missing: list[str] = []
    if run_payload.get("suite_summary") is None:
        missing.append("suite_summary")
    if run_payload.get("audit_summary_exists") is not True:
        missing.append("audit_summary")
    if run_payload.get("export_manifest_exists") is not True:
        missing.append("export_manifest")
    if run_payload.get("submission_zip_exists") is not True:
        missing.append("submission_zip")
    if run_payload.get("recorded_run_result_exists") is not True:
        missing.append("recorded_run_result")
    return missing


def summarize_artifact_readme_verification(run_payload: dict[str, object]) -> dict[str, object]:
    suite_summary = run_payload.get("suite_summary")
    audit_summary = run_payload.get("audit_summary")
    export_manifest = run_payload.get("export_manifest")
    return {
        "suite_readme_contract_verified": (
            suite_summary.get("readme_contract_verified_from_readme_file")
            if isinstance(suite_summary, dict)
            else None
        ),
        "audit_readme_submission_contract_verified": (
            audit_summary.get("readme_submission_contract_verified_from_readme_file")
            if isinstance(audit_summary, dict)
            else None
        ),
        "export_readme_submission_contract_verified": (
            export_manifest.get("readme_submission_contract_verified_from_readme_file")
            if isinstance(export_manifest, dict)
            else None
        ),
    }


def missing_readme_contract_verifications(run_payload: dict[str, object]) -> list[str]:
    verification = summarize_artifact_readme_verification(run_payload)
    suite_summary = run_payload.get("suite_summary")
    audit_summary = run_payload.get("audit_summary")
    export_manifest = run_payload.get("export_manifest")
    missing: list[str] = []
    if suite_summary is not None and verification["suite_readme_contract_verified"] is not True:
        missing.append("suite_readme_contract_verification")
    if audit_summary is not None and verification["audit_readme_submission_contract_verified"] is not True:
        missing.append("audit_readme_submission_contract_verification")
    if export_manifest is not None and verification["export_readme_submission_contract_verified"] is not True:
        missing.append("export_readme_submission_contract_verification")
    return missing


def summarize_gate_state(
    readme_local320_progress: dict[str, object] | None,
    proxy_progress: dict[str, object] | None,
    suite_summary: dict[str, object] | None,
) -> dict[str, object]:
    accuracy = None
    local_status = None
    if isinstance(readme_local320_progress, dict):
        local_status = readme_local320_progress.get("status")
        raw_accuracy = readme_local320_progress.get("accuracy")
        if isinstance(raw_accuracy, (int, float)):
            accuracy = float(raw_accuracy)
    if accuracy is None and isinstance(suite_summary, dict):
        evaluations = suite_summary.get("evaluations", [])
        if isinstance(evaluations, list):
            for item in evaluations:
                if not isinstance(item, dict):
                    continue
                if item.get("evaluation_name") != "readme_local320":
                    continue
                raw_accuracy = item.get("accuracy")
                if isinstance(raw_accuracy, (int, float)):
                    accuracy = float(raw_accuracy)
                break
    if local_status != "completed":
        gate_status = "unknown_until_local320_complete"
    elif accuracy is None:
        gate_status = "completed_without_accuracy"
    elif accuracy >= 0.80:
        gate_status = "meets_local080"
    elif accuracy >= 0.75:
        gate_status = "meets_local075"
    else:
        gate_status = "below_local075"
    proxy_started = isinstance(proxy_progress, dict)
    if isinstance(suite_summary, dict) and suite_summary.get("evaluations"):
        phase = "suite_completed"
    elif proxy_started:
        phase = "proxy_v1_running"
    elif isinstance(readme_local320_progress, dict):
        phase = "local320_running"
    else:
        phase = "pre_eval_or_training"
    return {
        "local320_accuracy": accuracy,
        "local320_status": local_status,
        "gate_status": gate_status,
        "dead_on_local320": gate_status == "below_local075",
        "proxy_started": proxy_started,
        "phase": phase,
    }


def summarize_artifact_status(run_name: str) -> dict[str, object] | None:
    artifact_paths = RUN_STATUS_ARTIFACTS.get(run_name)
    if artifact_paths is None:
        return None
    dataset_rel = artifact_paths["dataset_rel"]
    summary_rel = artifact_paths["summary_rel"]
    dataset_path = REPO_ROOT / dataset_rel
    summary_path = REPO_ROOT / summary_rel
    summary_payload = load_json_if_exists(summary_path)
    summary_excerpt = None
    if isinstance(summary_payload, dict):
        summary_excerpt = {
            key: summary_payload.get(key)
            for key in (
                "created_at",
                "base_dataset",
                "output_dataset",
                "strategy",
                "removed_rows",
                "added_rows",
                "resulting_mix",
            )
            if key in summary_payload
        }
    return {
        "dataset_path": str(dataset_path),
        "dataset_exists": dataset_path.exists(),
        "summary_path": str(summary_path),
        "summary_exists": summary_path.exists(),
        "summary": summary_excerpt,
    }


def summarize_followup_step(step: FollowupStep) -> dict[str, object]:
    base_dataset_path = REPO_ROOT / step.base_dataset_rel
    base_summary_path = REPO_ROOT / step.base_summary_rel
    output_dataset_path = REPO_ROOT / step.output_dataset_rel
    output_summary_path = REPO_ROOT / step.output_summary_rel
    missing_inputs: list[str] = []
    if not base_dataset_path.exists():
        missing_inputs.append("base_dataset")
    if not base_summary_path.exists():
        missing_inputs.append("base_summary")
    output_dataset_exists = output_dataset_path.exists()
    output_summary_exists = output_summary_path.exists()
    materialized = output_dataset_exists and output_summary_exists
    ready_to_materialize = not missing_inputs and not materialized
    output_summary_excerpt = None
    if output_summary_exists:
        output_summary_payload = load_json_if_exists(output_summary_path)
        if isinstance(output_summary_payload, dict):
            output_summary_excerpt = {
                key: output_summary_payload.get(key)
                for key in ("created_at", "strategy", "removed_rows", "added_rows", "resulting_mix")
                if key in output_summary_payload
            }
    return {
        "step_name": step.step_name,
        "base_dataset": step.base_dataset_rel,
        "base_exists": base_dataset_path.exists(),
        "base_summary": step.base_summary_rel,
        "base_summary_exists": base_summary_path.exists(),
        "output_dataset": step.output_dataset_rel,
        "output_exists": output_dataset_exists,
        "output_summary": step.output_summary_rel,
        "output_summary_exists": output_summary_exists,
        "output_summary_excerpt": output_summary_excerpt,
        "remove_id": step.remove_id,
        "add_id": step.add_id,
        "missing_inputs": missing_inputs,
        "ready_to_materialize": ready_to_materialize,
        "materialized": materialized,
    }


def summarize_run_status(run_name: str, run_root_rel: str) -> dict[str, object]:
    run_root = REPO_ROOT / run_root_rel
    suite_root = run_root / "eval_suite_readme_proxy_specialized"
    audit_path = run_root / "submission_compat_audit" / "submission_compat_audit.json"
    export_manifest_path = run_root / "submission_export" / "export_manifest.json"
    submission_zip_path = run_root / "submission_export" / "submission.zip"
    suite_summary = summarize_suite_summary(suite_root / "benchmark_eval_suite_summary.json")
    suite_progress = summarize_progress_file(suite_root / "benchmark_eval_suite_progress.json")
    readme_local320_progress = summarize_progress_file(
        suite_root / "readme_local320/benchmark_eval_progress.json"
    )
    proxy_progress = summarize_progress_file(
        suite_root / "leaderboard_proxy_v1_set/benchmark_eval_progress.json"
    )
    run_payload = {
        "run_root": str(run_root),
        "exists": run_root.exists(),
        "artifact_status": summarize_artifact_status(run_name),
        "training_result_exists": (run_root / "training_result.json").exists(),
        "prepare_manifest_exists": (run_root / "prepare_manifest.json").exists(),
        "audit_summary_exists": audit_path.exists(),
        "audit_summary": summarize_submission_audit(audit_path),
        "export_manifest_exists": export_manifest_path.exists(),
        "export_manifest": summarize_export_manifest(export_manifest_path),
        "submission_zip_exists": submission_zip_path.exists(),
        "suite_summary": suite_summary,
        "suite_progress": suite_progress,
        "readme_local320_progress": readme_local320_progress,
        "readme_local320_summary": load_json_if_exists(
            suite_root / "readme_local320/benchmark_eval_summary.json"
        ),
        "proxy_progress": proxy_progress,
        "gate_state": summarize_gate_state(
            readme_local320_progress=readme_local320_progress,
            proxy_progress=proxy_progress,
            suite_summary=suite_summary,
        ),
        "postprocess_manifest": summarize_postprocess(run_root / "postprocess_manifest.json"),
        "recorded_run_result_exists": (run_root / "recorded_run_result.json").exists(),
    }
    run_payload["missing_postprocess_artifacts"] = missing_postprocess_artifacts(run_payload)
    run_payload["artifact_readme_verification"] = summarize_artifact_readme_verification(run_payload)
    run_payload["missing_readme_contract_verifications"] = missing_readme_contract_verifications(run_payload)
    return run_payload


def summarize_best_selector() -> dict[str, object] | None:
    payload = load_json_if_exists(BEST_SELECTOR_SUMMARY)
    if payload is None:
        return None
    manifest = payload.get("selection_manifest", {})
    selected = manifest.get("selected_candidate", {}) if isinstance(manifest, dict) else {}
    return {
        "recorded_at": payload.get("recorded_at"),
        "status": payload.get("status"),
        "latest_iteration": payload.get("iterations", [])[-1] if payload.get("iterations") else None,
        "candidate_count": manifest.get("candidate_count") if isinstance(manifest, dict) else None,
        "eligible_candidate_count": manifest.get("eligible_candidate_count") if isinstance(manifest, dict) else None,
        "selected_candidate": {
            key: selected.get(key)
            for key in (
                "run_name",
                "run_root",
                "audit_status",
                "peft_export_ready",
                "eligible",
            )
            if isinstance(selected, dict) and key in selected
        },
        "selected_metrics": {
            metric: selected.get(metric)
            for metric in ("local320", "general_stable", "proxy_v1")
            if isinstance(selected, dict) and metric in selected
        },
    }


def build_status_report() -> dict[str, object]:
    active_readme_eval_contract = verify_readme_contract_file()
    active_readme_submission_contract = verify_readme_submission_contract_file()
    runs = {
        name: summarize_run_status(name, run_root_rel)
        for name, run_root_rel in RUN_STATUS_ROOTS.items()
    }
    followup_steps = [summarize_followup_step(step) for step in FOLLOWUP_STEPS]
    waiters = {
        "reprobridge31": summarize_waiter_dir(WAITERS31),
        "reprobridge32": summarize_waiter_dir(WAITERS32),
    }
    artifact_only_runs = [
        name
        for name, payload in runs.items()
        if isinstance(payload, dict)
        and payload.get("exists") is False
        and isinstance(payload.get("artifact_status"), dict)
        and (
            payload["artifact_status"].get("dataset_exists") is True
            or payload["artifact_status"].get("summary_exists") is True
        )
    ]
    dead_local320_runs = [
        name
        for name, payload in runs.items()
        if isinstance(payload, dict)
        and isinstance(payload.get("gate_state"), dict)
        and payload["gate_state"].get("dead_on_local320") is True
    ]
    dead_local320_pending_suite = [
        name
        for name, payload in runs.items()
        if isinstance(payload, dict)
        and isinstance(payload.get("gate_state"), dict)
        and payload["gate_state"].get("dead_on_local320") is True
        and payload.get("suite_summary") is None
    ]
    dead_local320_proxy_active_runs = [
        name
        for name, payload in runs.items()
        if isinstance(payload, dict)
        and isinstance(payload.get("gate_state"), dict)
        and payload["gate_state"].get("dead_on_local320") is True
        and payload["gate_state"].get("phase") == "proxy_v1_running"
    ]
    stale_waiter_runs = [
        name
        for name, waiter_payload in waiters.items()
        if isinstance(waiter_payload, dict)
        and waiter_payload.get("exists") is True
        and isinstance(runs.get(name), dict)
        and runs[name].get("exists") is False
    ]
    training_completed_pending_postprocess_runs = [
        name
        for name, payload in runs.items()
        if isinstance(payload, dict)
        and payload.get("exists") is True
        and payload.get("training_result_exists") is True
        and isinstance(payload.get("missing_postprocess_artifacts"), list)
        and len(payload["missing_postprocess_artifacts"]) > 0
    ]
    submission_ready_runs = [
        name
        for name, payload in runs.items()
        if isinstance(payload, dict)
        and payload.get("exists") is True
        and payload.get("suite_summary") is not None
        and payload.get("audit_summary_exists") is True
        and payload.get("export_manifest_exists") is True
        and payload.get("submission_zip_exists") is True
        and payload.get("recorded_run_result_exists") is True
        and isinstance(payload.get("audit_summary"), dict)
        and payload["audit_summary"].get("peft_export_ready") is True
        and isinstance(payload.get("export_manifest"), dict)
        and isinstance(payload["export_manifest"].get("validation"), dict)
        and payload["export_manifest"]["validation"].get("valid") is True
        and isinstance(payload.get("missing_readme_contract_verifications"), list)
        and len(payload["missing_readme_contract_verifications"]) == 0
    ]
    stale_readme_contract_runs = [
        name
        for name, payload in runs.items()
        if isinstance(payload, dict)
        and isinstance(payload.get("missing_readme_contract_verifications"), list)
        and len(payload["missing_readme_contract_verifications"]) > 0
    ]
    ready_followup_steps = [
        step["step_name"]
        for step in followup_steps
        if step.get("ready_to_materialize") is True
    ]
    blocked_followup_steps = [
        step["step_name"]
        for step in followup_steps
        if step.get("materialized") is not True
        and isinstance(step.get("missing_inputs"), list)
        and len(step["missing_inputs"]) > 0
    ]
    materialized_followup_steps = [
        step["step_name"]
        for step in followup_steps
        if step.get("materialized") is True
    ]
    return {
        "generated_at": now_iso(),
        "active_readme_eval_contract": active_readme_eval_contract,
        "active_readme_submission_contract": active_readme_submission_contract,
        "runs": runs,
        "artifact_only_runs": artifact_only_runs,
        "dead_local320_runs": dead_local320_runs,
        "dead_local320_pending_suite": dead_local320_pending_suite,
        "dead_local320_proxy_active_runs": dead_local320_proxy_active_runs,
        "stale_waiter_runs": stale_waiter_runs,
        "training_completed_pending_postprocess_runs": training_completed_pending_postprocess_runs,
        "submission_ready_runs": submission_ready_runs,
        "stale_readme_contract_runs": stale_readme_contract_runs,
        "ready_followup_steps": ready_followup_steps,
        "blocked_followup_steps": blocked_followup_steps,
        "materialized_followup_steps": materialized_followup_steps,
        "waiters": waiters,
        "best_submission_selector": summarize_best_selector(),
        "followup_steps": followup_steps,
    }


def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def ps_rows() -> list[tuple[int, str]]:
    output = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True)
    rows: list[tuple[int, str]] = []
    for line in output.splitlines():
        raw = line.strip()
        if not raw:
            continue
        try:
            pid_text, command = raw.split(None, 1)
        except ValueError:
            continue
        rows.append((int(pid_text), command))
    return rows


def retire_dead_lanes() -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    for pid, command in ps_rows():
        if pid == os.getpid():
            continue
        if REQUIRED_COMMAND not in command:
            continue
        for target, lane_label in RETIRE_TARGETS.items():
            if target in command:
                matches.append({"lane": lane_label, "pid": pid, "command": command})
                break
    for row in matches:
        os.kill(int(row["pid"]), signal.SIGTERM)
    return matches


def start_detached(waiters_dir: Path, log_name: str, argv: list[str]) -> dict[str, object]:
    waiters_dir.mkdir(parents=True, exist_ok=True)
    log_path = waiters_dir / f"{log_name}.log"
    pid_path = waiters_dir / f"{log_name}.pid"
    with log_path.open("a", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            argv,
            cwd=str(REPO_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
    pid_path.write_text(f"{proc.pid}\n", encoding="utf-8")
    return {
        "status": "started",
        "pid": proc.pid,
        "pid_path": str(pid_path),
        "log_path": str(log_path),
    }


def ensure_waiter(waiters_dir: Path, log_name: str, argv: list[str]) -> dict[str, object]:
    pid_path = waiters_dir / f"{log_name}.pid"
    log_path = waiters_dir / f"{log_name}.log"
    if pid_path.exists():
        try:
            pid = int(pid_path.read_text(encoding="utf-8").strip())
        except ValueError:
            pid = -1
        if pid > 0 and is_pid_alive(pid):
            return {
                "status": "already_running",
                "pid": pid,
                "pid_path": str(pid_path),
                "log_path": str(log_path),
            }
    return start_detached(waiters_dir, log_name, argv)


def wait_and_exec(waiters_dir: Path, log_name: str, wait_file: Path, argv: list[str]) -> int:
    waiters_dir.mkdir(parents=True, exist_ok=True)
    log_path = waiters_dir / f"{log_name}.log"
    pid_path = waiters_dir / f"{log_name}.pid"
    pid_path.write_text(f"{os.getpid()}\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {log_name} waiter started pid={os.getpid()}\n"
        )
        log_file.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] waiting for {wait_file}\n"
        )
        log_file.flush()
        while not wait_file.exists():
            time.sleep(60)
            log_file.write(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] still waiting for {wait_file}\n"
            )
            log_file.flush()
        log_file.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] dependency satisfied; launching command\n"
        )
        log_file.flush()
        proc = subprocess.Popen(
            argv,
            cwd=str(REPO_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
        return proc.wait()


def waiter_wrapper(waiters_dir: Path, log_name: str, wait_file: Path, argv: list[str]) -> list[str]:
    return [
        sys.executable,
        __file__,
        "--waiter",
        str(waiters_dir),
        log_name,
        str(wait_file),
        *argv,
    ]


def threshold_inline_code(run_root_rel: str, threshold_label: str, min_local: str, out_name: str) -> str:
    return (
        "import json, subprocess; "
        "from pathlib import Path; "
        f"repo=Path({str(REPO_ROOT)!r}); "
        f"run_root=repo/{run_root_rel!r}; "
        "summary=json.loads((run_root/'eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json').read_text()); "
        "evals={item['evaluation_name']: item for item in summary.get('evaluations', [])}; "
        "local=float(evals['readme_local320']['accuracy']); "
        "proxy=float(evals['leaderboard_proxy_v1_set']['accuracy']); "
        f"out_root=repo/'baseline_mlx/outputs/{out_name}'; "
        f"label={threshold_label!r}; "
        f"min_local={min_local!r}; "
        f"script=Path({str(THRESHOLD_SCRIPT_PATH)!r}); "
        "print(json.dumps({'run': run_root.name, 'threshold_label': label, 'local': local, 'proxy': proxy}, ensure_ascii=False)); "
        "subprocess.run(['uv','run','python',str(script),'promote-threshold','--run-root',str(run_root),'--threshold-label',label,'--min-local-accuracy',min_local,'--min-proxy-accuracy','0.65','--output-root',str(out_root)], check=True) "
        "if (not out_root.exists() and local >= float(min_local) and proxy >= 0.65) else None"
    )


def arm_reprobridge31() -> dict[str, object]:
    waiters: dict[str, object] = {}
    waiters["launcher"] = ensure_waiter(
        WAITERS31,
        "launcher",
        UV_PYTHON
        + [
            str(PIPELINE_PATH),
            "wait-resume-train-from-path",
            "--profile",
            "notebook-current",
            "--source-run-root",
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1",
            "--wait-path",
            str(RUN30_SUITE.relative_to(REPO_ROOT)),
            "--expected-kind",
            "file",
            "--poll-seconds",
            "60",
            "--min-free-gb",
            "150",
            "--output-root",
            "baseline_mlx/outputs",
            "--run-name",
            Path(RUN31).name,
            "--train-csv",
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge31_text3bit1num8raw12unitedge_v1.csv",
            "--type-sample",
            "Numeral Conversion=0",
            "--type-sample",
            "Gravitational Constant=9",
            "--type-sample",
            "Unit Conversion=1",
            "--type-sample",
            "Text Encryption=18",
            "--type-sample",
            "Bit Manipulation=34",
            "--type-sample",
            "Equation Transformation=18",
            "--valid-shadow-rows",
            "8",
            "--learning-rate",
            "1e-6",
            "--num-epochs",
            "0.8",
            "--max-seq-length",
            "1024",
            "--lora-key-group",
            "stage-union-exportsafe",
            "--trainable-lora-suffix-group",
            "attention",
            "--skip-if-target-started",
        ],
    )
    waiters["live"] = ensure_waiter(
        WAITERS31,
        "live",
        waiter_wrapper(
            WAITERS31,
            "live",
            RUN31_PREPARE,
            UV_PYTHON
            + [
                str(PIPELINE_PATH),
                "poll-live-run-status",
                "--run-root",
                RUN31,
                "--label",
                "reprobridge31 raw12 unitedge",
                "--poll-seconds",
                "60",
                "--no-stop-on-training-result",
                "--run-publish-results-md",
                "--publish-commit-message",
                "Record reprobridge31 raw12-unitedge live progress",
            ],
        ),
    )
    waiters["postprocess"] = ensure_waiter(
        WAITERS31,
        "postprocess",
        waiter_wrapper(
            WAITERS31,
            "postprocess",
            RUN31_PREPARE,
            UV_PYTHON
            + [
                str(PIPELINE_PATH),
                "postprocess-run",
                "--run-root",
                RUN31,
                "--label",
                "o30best proxybench reprobridge31 raw12 unitedge v1",
                "--wait-for-training-result",
                "--poll-seconds",
                "60",
                "--skip-existing-steps",
                "--extra-benchmark-csv",
                "cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/leaderboard_proxy_v1/artifacts/leaderboard_proxy_v1_set.csv",
                "--run-record-run-result",
                "--run-package-best-submission",
                "--results-md",
                "versions/baseline_mlx/baseline_mlx-results.md",
                "--run-publish-results-md",
                "--publish-commit-message",
                "Record reprobridge31 raw12-unitedge results",
            ],
        ),
    )
    waiters["threshold075"] = ensure_waiter(
        WAITERS31,
        "threshold075",
        waiter_wrapper(
            WAITERS31,
            "threshold075",
            RUN31_SUITE,
            UV_PYTHON
            + [
                "-c",
                threshold_inline_code(
                    RUN31,
                    "local-ge-0.75",
                    "0.75",
                    "threshold_submission_reprobridge31_local_ge_075_v1",
                ),
            ],
        ),
    )
    waiters["threshold080"] = ensure_waiter(
        WAITERS31,
        "threshold080",
        waiter_wrapper(
            WAITERS31,
            "threshold080",
            RUN31_SUITE,
            UV_PYTHON
            + [
                "-c",
                threshold_inline_code(
                    RUN31,
                    "local-ge-0.80",
                    "0.80",
                    "threshold_submission_reprobridge31_local_ge_080_v1",
                ),
            ],
        ),
    )
    return waiters


def arm_reprobridge32() -> dict[str, object]:
    waiters: dict[str, object] = {}
    waiters["launcher"] = ensure_waiter(
        WAITERS32,
        "launcher",
        UV_PYTHON
        + [
            str(PIPELINE_PATH),
            "wait-resume-train-from-path",
            "--profile",
            "notebook-current",
            "--source-run-root",
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1",
            "--wait-path",
            str(RUN31_SUITE.relative_to(REPO_ROOT)),
            "--expected-kind",
            "file",
            "--poll-seconds",
            "60",
            "--min-free-gb",
            "150",
            "--output-root",
            "baseline_mlx/outputs",
            "--run-name",
            Path(RUN32).name,
            "--train-csv",
            "baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge32_text3bit1num8raw13nounit_v1.csv",
            "--type-sample",
            "Numeral Conversion=0",
            "--type-sample",
            "Gravitational Constant=9",
            "--type-sample",
            "Unit Conversion=0",
            "--type-sample",
            "Text Encryption=18",
            "--type-sample",
            "Bit Manipulation=34",
            "--type-sample",
            "Equation Transformation=19",
            "--valid-shadow-rows",
            "8",
            "--learning-rate",
            "1e-6",
            "--num-epochs",
            "0.8",
            "--max-seq-length",
            "1024",
            "--lora-key-group",
            "stage-union-exportsafe",
            "--trainable-lora-suffix-group",
            "attention",
            "--skip-if-target-started",
        ],
    )
    waiters["live"] = ensure_waiter(
        WAITERS32,
        "live",
        waiter_wrapper(
            WAITERS32,
            "live",
            RUN32_PREPARE,
            UV_PYTHON
            + [
                str(PIPELINE_PATH),
                "poll-live-run-status",
                "--run-root",
                RUN32,
                "--label",
                "reprobridge32 raw13 nounit",
                "--poll-seconds",
                "60",
                "--no-stop-on-training-result",
                "--run-publish-results-md",
                "--publish-commit-message",
                "Record reprobridge32 raw13-nounit live progress",
            ],
        ),
    )
    waiters["postprocess"] = ensure_waiter(
        WAITERS32,
        "postprocess",
        waiter_wrapper(
            WAITERS32,
            "postprocess",
            RUN32_PREPARE,
            UV_PYTHON
            + [
                str(PIPELINE_PATH),
                "postprocess-run",
                "--run-root",
                RUN32,
                "--label",
                "o30best proxybench reprobridge32 raw13 nounit v1",
                "--wait-for-training-result",
                "--poll-seconds",
                "60",
                "--skip-existing-steps",
                "--extra-benchmark-csv",
                "cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/leaderboard_proxy_v1/artifacts/leaderboard_proxy_v1_set.csv",
                "--run-record-run-result",
                "--run-package-best-submission",
                "--results-md",
                "versions/baseline_mlx/baseline_mlx-results.md",
                "--run-publish-results-md",
                "--publish-commit-message",
                "Record reprobridge32 raw13-nounit results",
            ],
        ),
    )
    waiters["threshold075"] = ensure_waiter(
        WAITERS32,
        "threshold075",
        waiter_wrapper(
            WAITERS32,
            "threshold075",
            RUN32_SUITE,
            UV_PYTHON
            + [
                "-c",
                threshold_inline_code(
                    RUN32,
                    "local-ge-0.75",
                    "0.75",
                    "threshold_submission_reprobridge32_local_ge_075_v1",
                ),
            ],
        ),
    )
    waiters["threshold080"] = ensure_waiter(
        WAITERS32,
        "threshold080",
        waiter_wrapper(
            WAITERS32,
            "threshold080",
            RUN32_SUITE,
            UV_PYTHON
            + [
                "-c",
                threshold_inline_code(
                    RUN32,
                    "local-ge-0.80",
                    "0.80",
                    "threshold_submission_reprobridge32_local_ge_080_v1",
                ),
            ],
        ),
    )
    return waiters


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Retire dead bridge lanes, arm reprobridge31/32 waiters, or materialize "
            "reprobridge33-36 follow-up artifacts."
        ),
    )
    parser.add_argument(
        "--status-report",
        action="store_true",
        help=(
            "Print a consolidated JSON status report for reprobridge23-32, waiters, and the "
            "best-submission selector, including artifact-only, submission-ready, "
            "training-complete-but-postprocess-pending run lists, per-run "
            "missing-postprocess-artifact details, and followup-step materialization readiness."
        ),
    )
    parser.add_argument(
        "--materialize-followups",
        action="store_true",
        help="Materialize reprobridge33-36 follow-up artifacts instead of running waiter recovery.",
    )
    parser.add_argument(
        "--followup-step",
        choices=("reprobridge33", "reprobridge34", "reprobridge35", "reprobridge36", "all"),
        default="all",
        help="Which follow-up no-unit artifact from reprobridge33-36 to materialize when --materialize-followups is set.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print the planned work without writing files.",
    )
    return parser.parse_args(argv)


def main() -> int:
    if len(sys.argv) >= 5 and sys.argv[1] == "--waiter":
        waiters_dir = Path(sys.argv[2])
        log_name = sys.argv[3]
        wait_file = Path(sys.argv[4])
        argv = sys.argv[5:]
        return wait_and_exec(waiters_dir, log_name, wait_file, argv)

    args = parse_args(sys.argv[1:])
    if args.status_report:
        payload = build_status_report()
    elif args.materialize_followups:
        payload = {
            "materialize_followups": materialize_followups(
                step_name=args.followup_step,
                dry_run=args.dry_run,
            ),
        }
    else:
        payload = {
            "retired_dead_lane_matches": retire_dead_lanes(),
            "reprobridge31": arm_reprobridge31(),
            "reprobridge32": arm_reprobridge32(),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
