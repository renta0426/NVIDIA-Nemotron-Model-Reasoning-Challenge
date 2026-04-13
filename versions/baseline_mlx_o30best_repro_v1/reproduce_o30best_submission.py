#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
MONOLITH_PATH = REPO_ROOT / "baseline_mlx" / "reproduce_nemotron_sft_lora_with_cot_v2_mlx.py"

SOURCE_RESUME_RUN_NAME = (
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "lr1e5_len1024_from_len768_v1"
)
BEST_RUN_NAME = (
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1"
)
BEST_DATASET_STEM = "stage25_text_verified130_binary40proxyo30p0s10_grav15_unit15_rowselect_v1"
FULL_REPRO_RUN_NAME = (
    "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_"
    "textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1"
)
BASE_MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"

BEST_RUN_ROOT = REPO_ROOT / "baseline_mlx" / "outputs" / BEST_RUN_NAME
SOURCE_RESUME_RUN_ROOT = REPO_ROOT / "baseline_mlx" / "outputs" / SOURCE_RESUME_RUN_NAME
ARTIFACT_ROOT = REPO_ROOT / "baseline_mlx" / "outputs" / "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts"
BEST_DATASET_CSV = ARTIFACT_ROOT / f"{BEST_DATASET_STEM}.csv"
BEST_DATASET_SUMMARY_JSON = ARTIFACT_ROOT / f"{BEST_DATASET_STEM}_summary.json"
BEST_PREPARE_MANIFEST = BEST_RUN_ROOT / "prepare_manifest.json"
BEST_SUITE_SUMMARY = BEST_RUN_ROOT / "eval_suite_readme_proxy_specialized" / "benchmark_eval_suite_summary.json"
BEST_AUDIT_SUMMARY = BEST_RUN_ROOT / "submission_compat_audit" / "submission_compat_audit.json"
BEST_EXPORT_MANIFEST = BEST_RUN_ROOT / "submission_export" / "export_manifest.json"
BEST_SUBMISSION_ZIP = BEST_RUN_ROOT / "submission_export" / "submission.zip"
RESULTS_MD = REPO_ROOT / "versions" / "baseline_mlx" / "baseline_mlx-results.md"
LEADERBOARD_PROXY_CSV = (
    REPO_ROOT
    / "cuda-train-data-analysis-v1"
    / "proof_first_solver_factory_routing"
    / "result"
    / "leaderboard_proxy_v1"
    / "artifacts"
    / "leaderboard_proxy_v1_set.csv"
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
EXPECTED_LOCAL = {"correct": 231, "rows": 320, "accuracy": 231 / 320}
EXPECTED_PROXY = {"correct": 130, "rows": 200, "accuracy": 130 / 200}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def approx_equal(lhs: float, rhs: float, tol: float = 1e-9) -> bool:
    return math.isclose(lhs, rhs, rel_tol=0.0, abs_tol=tol)


def format_inline_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def build_exportability_fields(
    audit_summary: dict[str, Any],
    export_manifest: dict[str, Any],
    *,
    prefix: str = "",
) -> dict[str, Any]:
    key_prefix = f"{prefix}_" if prefix else ""
    return {
        f"{key_prefix}audit_status": audit_summary.get("audit_status"),
        f"{key_prefix}peft_export_ready": audit_summary.get("peft_export_ready") is True,
        f"{key_prefix}validation_valid": export_manifest.get("validation", {}).get("valid"),
    }


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


def run_command(command: list[str], dry_run: bool = False) -> None:
    print("$", " ".join(shlex.quote(part) for part in command))
    if dry_run:
        return
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def find_evaluation(summary: dict[str, Any], evaluation_name: str) -> dict[str, Any]:
    for evaluation in summary.get("evaluations", []):
        if evaluation.get("evaluation_name") == evaluation_name:
            return evaluation
    raise SystemExit(f"Missing evaluation '{evaluation_name}' in {BEST_SUITE_SUMMARY}")


def verify_readme_contract(prepare_manifest: dict[str, Any]) -> None:
    contract = prepare_manifest.get("readme_contract", {})
    for key, expected_value in README_CONTRACT.items():
        actual_value = contract.get(key)
        require(
            actual_value == expected_value,
            f"README contract mismatch for {key}: expected {expected_value}, got {actual_value}",
        )
    require(
        prepare_manifest.get("training", {}).get("lora_rank") == README_CONTRACT["max_lora_rank"],
        "o30best run does not use rank-32 LoRA as required by README.md",
    )


def verify_evaluation(
    evaluation: dict[str, Any],
    *,
    expected_name: str,
    expected_correct: int,
    expected_rows: int,
    expected_accuracy: float,
    accuracy_tolerance: float = 1e-4,
) -> None:
    require(evaluation.get("evaluation_name") == expected_name, f"Unexpected evaluation name: {evaluation}")
    require(evaluation.get("correct") == expected_correct, f"{expected_name} correct mismatch: {evaluation}")
    require(evaluation.get("rows") == expected_rows, f"{expected_name} rows mismatch: {evaluation}")
    actual_accuracy = float(evaluation.get("accuracy"))
    require(
        approx_equal(actual_accuracy, expected_accuracy, tol=accuracy_tolerance),
        f"{expected_name} accuracy mismatch: expected {expected_accuracy}, got {actual_accuracy}",
    )


def verify_best_run() -> dict[str, Any]:
    for required_path in (
        README_PATH,
        MONOLITH_PATH,
        SOURCE_RESUME_RUN_ROOT,
        BEST_RUN_ROOT,
        BEST_DATASET_CSV,
        BEST_DATASET_SUMMARY_JSON,
        BEST_PREPARE_MANIFEST,
        BEST_SUITE_SUMMARY,
        BEST_AUDIT_SUMMARY,
        BEST_EXPORT_MANIFEST,
        BEST_SUBMISSION_ZIP,
    ):
        require(required_path.exists(), f"Required path does not exist: {required_path}")

    verify_readme_contract_file()
    prepare_manifest = load_json(BEST_PREPARE_MANIFEST)
    suite_summary = load_json(BEST_SUITE_SUMMARY)
    audit_summary = load_json(BEST_AUDIT_SUMMARY)
    export_manifest = load_json(BEST_EXPORT_MANIFEST)
    dataset_summary = load_json(BEST_DATASET_SUMMARY_JSON)
    prepare_manifest_contract = dict(prepare_manifest.get("readme_contract", {}))

    verify_readme_contract(prepare_manifest)

    local_eval = find_evaluation(suite_summary, "readme_local320")
    proxy_eval = find_evaluation(suite_summary, "leaderboard_proxy_v1_set")
    verify_evaluation(
        local_eval,
        expected_name="readme_local320",
        expected_correct=EXPECTED_LOCAL["correct"],
        expected_rows=EXPECTED_LOCAL["rows"],
        expected_accuracy=EXPECTED_LOCAL["accuracy"],
    )
    verify_evaluation(
        proxy_eval,
        expected_name="leaderboard_proxy_v1_set",
        expected_correct=EXPECTED_PROXY["correct"],
        expected_rows=EXPECTED_PROXY["rows"],
        expected_accuracy=EXPECTED_PROXY["accuracy"],
    )

    require(
        audit_summary.get("peft_export_ready") is True,
        f"Submission audit is not export-ready: status={audit_summary.get('audit_status')!r}",
    )
    require(export_manifest.get("validation", {}).get("valid") is True, "Export manifest is not valid")
    require(export_manifest.get("zip_path") == str(BEST_SUBMISSION_ZIP), "Best run zip path changed unexpectedly")
    require(BEST_SUBMISSION_ZIP.stat().st_size > 0, f"Submission zip is empty: {BEST_SUBMISSION_ZIP}")
    require(
        dataset_summary.get("requested_rows", {}).get("binary_bit_other_rows") == 30,
        "o30best repro expects 30 binary other rows",
    )
    require(
        dataset_summary.get("requested_rows", {}).get("binary_bit_permutation_rows") == 0,
        "o30best repro expects zero permutation rows",
    )
    require(
        dataset_summary.get("requested_rows", {}).get("binary_bit_structured_rows") == 10,
        "o30best repro expects 10 structured binary rows",
    )
    require(
        dataset_summary.get("binary_leading_zero_preferred") is False,
        "o30best repro expects non-leading-zero-preferred binary selection",
    )

    return {
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "readme_path": str(README_PATH),
        "readme_contract_verified_from_readme_file": True,
        "best_run_root": str(BEST_RUN_ROOT),
        "source_resume_run_root": str(SOURCE_RESUME_RUN_ROOT),
        "dataset_csv": str(BEST_DATASET_CSV),
        "dataset_summary_json": str(BEST_DATASET_SUMMARY_JSON),
        "readme_contract": README_CONTRACT,
        "validated_prepare_manifest_readme_contract": prepare_manifest_contract,
        "readme_contract_state": build_readme_contract_state(prepare_manifest_contract),
        "local320": local_eval,
        "leaderboard_proxy_v1_set": proxy_eval,
        **build_exportability_fields(audit_summary, export_manifest),
        "submission_zip": str(BEST_SUBMISSION_ZIP),
        "submission_zip_size_bytes": BEST_SUBMISSION_ZIP.stat().st_size,
    }


def write_summary(output_root: Path, mode: str, extra: dict[str, Any]) -> Path:
    summary_path = output_root / "o30best_repro_summary.json"
    payload = {"mode": mode, **verify_best_run(), **extra}
    dump_json(summary_path, payload)
    markdown_path = output_root / "o30best_repro_summary.md"
    dump_markdown(markdown_path, render_markdown_summary(payload))
    return summary_path


def render_markdown_summary(payload: dict[str, Any]) -> str:
    local320 = payload["local320"]
    proxy = payload["leaderboard_proxy_v1_set"]
    lines = [
        "# o30/p0/s10 local-best repro summary",
        "",
        f"- mode: `{payload['mode']}`",
        f"- source run: `{payload['best_run_root']}`",
        f"- readme_local320: `{local320['correct']}/{local320['rows']} = {local320['accuracy']}`",
        f"- leaderboard_proxy_v1_set: `{proxy['correct']}/{proxy['rows']} = {proxy['accuracy']}`",
        f"- audit_status: `{payload['audit_status']}`",
        f"- peft_export_ready: `{payload['peft_export_ready']}`",
        f"- validation_valid: `{payload['validation_valid']}`",
        f"- submission_zip: `{payload['submission_zip']}`",
        f"- submission_zip_size_bytes: `{payload['submission_zip_size_bytes']}`",
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
    ]
    if payload.get("reproduced_submission_zip"):
        lines.extend(
            [
                "",
                "## Re-exported artifact",
                "",
                f"- reproduced_audit_status: `{payload.get('reproduced_audit_status')}`",
                f"- reproduced_peft_export_ready: `{payload.get('reproduced_peft_export_ready')}`",
                f"- reproduced_submission_zip: `{payload['reproduced_submission_zip']}`",
                f"- reproduced_validation_valid: `{payload.get('reproduced_validation_valid')}`",
            ]
        )
    note_parts: list[str] = []
    if payload.get("peft_export_ready") is True and payload.get("validation_valid") is not None:
        note_parts.append(
            f"source exportability from peft_export_ready={payload['peft_export_ready']} "
            f"and validation_valid={payload['validation_valid']}"
        )
    if (
        payload.get("reproduced_peft_export_ready") is True
        and payload.get("reproduced_validation_valid") is not None
    ):
        note_parts.append(
            "reproduced exportability from "
            f"reproduced_peft_export_ready={payload['reproduced_peft_export_ready']} "
            f"and reproduced_validation_valid={payload['reproduced_validation_valid']}"
        )
    if note_parts:
        lines.append(
            "- exportability_note: treat `audit_status` values as legacy compatibility labels; "
            + "; ".join(note_parts)
            + "."
        )
    if payload.get("repro_run_root"):
        lines.extend(
            [
                "",
                "## Full reproduce target",
                "",
                f"- repro_run_root: `{payload['repro_run_root']}`",
                f"- dataset_csv: `{payload['dataset_csv']}`",
                f"- dataset_summary_json: `{payload['dataset_summary_json']}`",
            ]
        )
    return "\n".join(lines)


def command_verify(args: argparse.Namespace) -> int:
    metadata = verify_best_run()
    if args.output_root is not None:
        output_root = repo_path(args.output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        summary_path = write_summary(output_root, "verify", {})
        metadata["summary_path"] = str(summary_path)
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


def command_export_existing(args: argparse.Namespace) -> int:
    output_root = repo_path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    audit_output_root = output_root / "submission_compat_audit"
    export_output_root = output_root / "submission_export"

    run_command(
        uv_command(
            "audit-submission-compat",
            "--adapter-dir",
            BEST_RUN_ROOT / "adapter",
            "--output-root",
            audit_output_root,
            "--base-model-name-or-path",
            BASE_MODEL_NAME,
        ),
        dry_run=args.dry_run,
    )
    run_command(
        uv_command(
            "export-peft-submission",
            "--adapter-dir",
            BEST_RUN_ROOT / "adapter",
            "--output-root",
            export_output_root,
            "--reference-model-root",
            BEST_RUN_ROOT / "shadow_model",
            "--base-model-name-or-path",
            BASE_MODEL_NAME,
        ),
        dry_run=args.dry_run,
    )

    extra: dict[str, Any] = {"export_output_root": str(export_output_root)}
    if not args.dry_run:
        audit_summary = load_json(audit_output_root / "submission_compat_audit.json")
        export_manifest = load_json(export_output_root / "export_manifest.json")
        extra["reproduced_audit_summary"] = str(audit_output_root / "submission_compat_audit.json")
        extra["reproduced_export_manifest"] = str(export_output_root / "export_manifest.json")
        extra["reproduced_submission_zip"] = export_manifest.get("zip_path")
        extra["reproduced_zip_size_bytes"] = export_manifest.get("zip_size_bytes")
        extra.update(build_exportability_fields(audit_summary, export_manifest, prefix="reproduced"))
    summary_path = write_summary(output_root, "export-existing", extra)
    print(json.dumps({"summary_path": str(summary_path), **extra}, indent=2, sort_keys=True))
    return 0


def command_full_reproduce(args: argparse.Namespace) -> int:
    dataset_csv = repo_path(args.dataset_csv)
    dataset_summary_json = repo_path(args.dataset_summary_json)
    output_root = repo_path(args.output_root)
    run_name = args.run_name
    run_root = output_root / run_name

    run_command(
        uv_command(
            "build-text-binary-reanchor-csv",
            "--output-csv",
            dataset_csv,
            "--summary-json",
            dataset_summary_json,
            "--text-verified-rows",
            "130",
            "--binary-bit-other-rows",
            "30",
            "--binary-bit-permutation-rows",
            "0",
            "--binary-bit-structured-rows",
            "10",
            "--gravity-rows",
            "15",
            "--unit-rows",
            "15",
        ),
        dry_run=args.dry_run,
    )
    run_command(
        uv_command(
            "resume-train-from-run",
            "--profile",
            "notebook-current",
            "--source-run-root",
            SOURCE_RESUME_RUN_ROOT,
            "--train-csv",
            dataset_csv,
            "--output-root",
            output_root,
            "--run-name",
            run_name,
            "--learning-rate",
            "8e-6",
            "--num-epochs",
            "0.45",
            "--max-seq-length",
            "1024",
            "--valid-shadow-rows",
            "1",
            "--type-sample",
            "Text Encryption=130",
            "--type-sample",
            "Bit Manipulation=40",
            "--type-sample",
            "Gravitational Constant=15",
            "--type-sample",
            "Unit Conversion=15",
            "--type-sample",
            "Numeral Conversion=0",
            "--type-sample",
            "Equation Transformation=0",
            "--lora-key-group",
            "stage-union-exportsafe",
            "--trainable-lora-suffix-group",
            "attention",
            "--skip-if-target-started",
        ),
        dry_run=args.dry_run,
    )
    run_command(
        uv_command(
            "postprocess-run",
            "--run-root",
            run_root,
            "--label",
            "o30/p0/s10 local-best repro v1",
            "--wait-for-training-result",
            "--poll-seconds",
            "60",
            "--extra-benchmark-csv",
            LEADERBOARD_PROXY_CSV,
            "--run-record-run-result",
            "--run-package-best-submission",
            "--results-md",
            repo_path(args.results_md),
            "--run-publish-results-md" if args.run_publish_results_md else "--no-run-publish-results-md",
            "--publish-commit-message",
            args.publish_commit_message,
        ),
        dry_run=args.dry_run,
    )

    extra = {
        "repro_run_root": str(run_root),
        "dataset_csv": str(dataset_csv),
        "dataset_summary_json": str(dataset_summary_json),
        "dry_run": args.dry_run,
    }
    if not args.dry_run:
        audit_output_root = run_root / "submission_compat_audit"
        export_output_root = run_root / "submission_export"
        audit_summary = load_json(audit_output_root / "submission_compat_audit.json")
        export_manifest = load_json(export_output_root / "export_manifest.json")
        extra["reproduced_audit_summary"] = str(audit_output_root / "submission_compat_audit.json")
        extra["reproduced_export_manifest"] = str(export_output_root / "export_manifest.json")
        extra["reproduced_submission_zip"] = export_manifest.get("zip_path")
        extra["reproduced_zip_size_bytes"] = export_manifest.get("zip_size_bytes")
        extra.update(build_exportability_fields(audit_summary, export_manifest, prefix="reproduced"))
    summary_path = write_summary(repo_path(args.summary_output_root), "full-reproduce", extra)
    print(json.dumps({"summary_path": str(summary_path), **extra}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-file reproduction pipeline for the current o30/p0/s10 MLX local/proxy best run. "
            "This wrapper keeps the README.md submission contract front-and-center: "
            "rank<=32, submission.zip output, and evaluation parameters "
            "max_tokens=7680, top_p=1.0, temperature=0.0, max_num_seqs=64, "
            "gpu_memory_utilization=0.85, max_model_len=8192."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="Verify the tracked o30best run and optionally write a summary.")
    verify.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "baseline_mlx" / "outputs" / "o30best_local_best_repro_verify_v1",
    )
    verify.set_defaults(func=command_verify)

    export_existing = subparsers.add_parser(
        "export-existing",
        help="Re-run audit/export on the completed o30best run and regenerate submission.zip.",
    )
    export_existing.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "baseline_mlx" / "outputs" / "o30best_local_best_repro_export_v1",
    )
    export_existing.add_argument("--dry-run", action="store_true")
    export_existing.set_defaults(func=command_export_existing)

    full_reproduce = subparsers.add_parser(
        "full-reproduce",
        help="Rebuild the o30best dataset, rerun the short train, and postprocess the full suite.",
    )
    full_reproduce.add_argument(
        "--dataset-csv",
        type=Path,
        default=ARTIFACT_ROOT / f"{BEST_DATASET_STEM}_repro_v1.csv",
    )
    full_reproduce.add_argument(
        "--dataset-summary-json",
        type=Path,
        default=ARTIFACT_ROOT / f"{BEST_DATASET_STEM}_repro_v1_summary.json",
    )
    full_reproduce.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "baseline_mlx" / "outputs",
    )
    full_reproduce.add_argument("--run-name", default=FULL_REPRO_RUN_NAME)
    full_reproduce.add_argument(
        "--summary-output-root",
        type=Path,
        default=REPO_ROOT / "baseline_mlx" / "outputs" / "o30best_local_best_repro_full_v1",
    )
    full_reproduce.add_argument("--results-md", type=Path, default=RESULTS_MD)
    full_reproduce.add_argument(
        "--run-publish-results-md",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    full_reproduce.add_argument(
        "--publish-commit-message",
        default="Record o30/p0/s10 local-best repro full rerun results",
    )
    full_reproduce.add_argument("--dry-run", action="store_true")
    full_reproduce.set_defaults(func=command_full_reproduce)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
