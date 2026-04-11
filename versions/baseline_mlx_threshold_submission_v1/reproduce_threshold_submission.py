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
DEFAULT_BASE_MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"

README_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "max_model_len": 8192,
}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def approx_equal(lhs: float, rhs: float, tol: float = 1e-9) -> bool:
    return math.isclose(lhs, rhs, rel_tol=0.0, abs_tol=tol)


def uv_command(*args: str | Path) -> list[str]:
    return ["uv", "run", "python", str(MONOLITH_PATH), *[str(arg) for arg in args]]


def run_command(command: list[str], *, dry_run: bool) -> None:
    print("$", " ".join(shlex.quote(part) for part in command))
    if dry_run:
        return
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def run_paths(run_root: Path) -> dict[str, Path]:
    return {
        "prepare_manifest": run_root / "prepare_manifest.json",
        "suite_summary": run_root / "eval_suite_readme_proxy_specialized" / "benchmark_eval_suite_summary.json",
        "audit_summary": run_root / "submission_compat_audit" / "submission_compat_audit.json",
        "export_manifest": run_root / "submission_export" / "export_manifest.json",
        "submission_zip": run_root / "submission_export" / "submission.zip",
        "adapter_dir": run_root / "adapter",
        "shadow_model": run_root / "shadow_model",
    }


def maybe_find_evaluation(summary: dict[str, Any], evaluation_name: str) -> dict[str, Any] | None:
    for evaluation in summary.get("evaluations", []):
        if evaluation.get("evaluation_name") == evaluation_name:
            return evaluation
    return None


def find_evaluation(summary: dict[str, Any], evaluation_name: str) -> dict[str, Any]:
    evaluation = maybe_find_evaluation(summary, evaluation_name)
    if evaluation is None:
        raise SystemExit(f"Missing evaluation '{evaluation_name}' in suite summary")
    return evaluation


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
        "Run does not use rank-32 LoRA as required by README.md",
    )


def verify_metric(
    *,
    evaluation_name: str,
    evaluation: dict[str, Any] | None,
    min_accuracy: float | None,
    expected_correct: int | None,
    expected_rows: int | None,
) -> None:
    if evaluation is None:
        require(
            min_accuracy is None and expected_correct is None and expected_rows is None,
            f"Missing required evaluation '{evaluation_name}'",
        )
        return
    actual_accuracy = float(evaluation.get("accuracy"))
    if min_accuracy is not None:
        require(
            actual_accuracy + 1e-9 >= min_accuracy,
            f"{evaluation_name} accuracy {actual_accuracy} is below required minimum {min_accuracy}",
        )
    if expected_correct is not None:
        require(
            int(evaluation.get("correct")) == expected_correct,
            f"{evaluation_name} correct mismatch: expected {expected_correct}, got {evaluation.get('correct')}",
        )
    if expected_rows is not None:
        require(
            int(evaluation.get("rows")) == expected_rows,
            f"{evaluation_name} rows mismatch: expected {expected_rows}, got {evaluation.get('rows')}",
        )


def summarize_run(
    *,
    run_root: Path,
    threshold_label: str,
    min_local_accuracy: float | None,
    min_proxy_accuracy: float | None,
    expected_local_correct: int | None,
    expected_proxy_correct: int | None,
    expected_local_rows: int | None,
    expected_proxy_rows: int | None,
    require_existing_export: bool,
) -> dict[str, Any]:
    require(README_PATH.exists(), f"README.md does not exist: {README_PATH}")
    require(MONOLITH_PATH.exists(), f"Monolith script does not exist: {MONOLITH_PATH}")
    require(run_root.exists(), f"Run root does not exist: {run_root}")

    paths = run_paths(run_root)
    require(paths["prepare_manifest"].exists(), f"Missing prepare manifest: {paths['prepare_manifest']}")
    require(paths["suite_summary"].exists(), f"Missing suite summary: {paths['suite_summary']}")
    require(paths["adapter_dir"].exists(), f"Missing adapter dir: {paths['adapter_dir']}")
    require(paths["shadow_model"].exists(), f"Missing shadow model dir: {paths['shadow_model']}")

    prepare_manifest = load_json(paths["prepare_manifest"])
    suite_summary = load_json(paths["suite_summary"])
    verify_readme_contract(prepare_manifest)

    local_eval = find_evaluation(suite_summary, "readme_local320")
    proxy_eval = maybe_find_evaluation(suite_summary, "leaderboard_proxy_v1_set")

    verify_metric(
        evaluation_name="readme_local320",
        evaluation=local_eval,
        min_accuracy=min_local_accuracy,
        expected_correct=expected_local_correct,
        expected_rows=expected_local_rows,
    )
    verify_metric(
        evaluation_name="leaderboard_proxy_v1_set",
        evaluation=proxy_eval,
        min_accuracy=min_proxy_accuracy,
        expected_correct=expected_proxy_correct,
        expected_rows=expected_proxy_rows,
    )

    payload: dict[str, Any] = {
        "threshold_label": threshold_label,
        "readme_path": str(README_PATH),
        "run_root": str(run_root),
        "prepare_manifest": str(paths["prepare_manifest"]),
        "suite_summary": str(paths["suite_summary"]),
        "adapter_dir": str(paths["adapter_dir"]),
        "shadow_model": str(paths["shadow_model"]),
        "readme_contract": README_CONTRACT,
        "local320": local_eval,
        "leaderboard_proxy_v1_set": proxy_eval,
        "min_local_accuracy": min_local_accuracy,
        "min_proxy_accuracy": min_proxy_accuracy,
        "expected_local_correct": expected_local_correct,
        "expected_proxy_correct": expected_proxy_correct,
    }

    if paths["audit_summary"].exists():
        audit_summary = load_json(paths["audit_summary"])
        payload["existing_audit_summary"] = str(paths["audit_summary"])
        payload["existing_audit_status"] = audit_summary.get("audit_status")
    if paths["export_manifest"].exists():
        export_manifest = load_json(paths["export_manifest"])
        payload["existing_export_manifest"] = str(paths["export_manifest"])
        payload["existing_submission_zip"] = export_manifest.get("zip_path")
        payload["existing_export_valid"] = export_manifest.get("validation", {}).get("valid")
    if paths["submission_zip"].exists():
        payload["existing_submission_zip_size_bytes"] = paths["submission_zip"].stat().st_size

    if require_existing_export:
        require(paths["audit_summary"].exists(), f"Missing existing audit summary: {paths['audit_summary']}")
        require(paths["export_manifest"].exists(), f"Missing existing export manifest: {paths['export_manifest']}")
        require(paths["submission_zip"].exists(), f"Missing existing submission.zip: {paths['submission_zip']}")
        audit_summary = load_json(paths["audit_summary"])
        export_manifest = load_json(paths["export_manifest"])
        require(
            audit_summary.get("audit_status") == "potentially_exportable_2d_only",
            f"Unexpected audit status: {audit_summary.get('audit_status')}",
        )
        require(
            export_manifest.get("validation", {}).get("valid") is True,
            "Existing export manifest is not valid",
        )
        require(
            paths["submission_zip"].stat().st_size > 0,
            f"Existing submission zip is empty: {paths['submission_zip']}",
        )

    return payload


def render_markdown_summary(payload: dict[str, Any]) -> str:
    local320 = payload["local320"]
    proxy = payload.get("leaderboard_proxy_v1_set")
    lines = [
        "# threshold submission summary",
        "",
        f"- threshold_label: `{payload['threshold_label']}`",
        f"- run_root: `{payload['run_root']}`",
        f"- readme_local320: `{local320['correct']}/{local320['rows']} = {local320['accuracy']}`",
    ]
    if proxy is not None:
        lines.append(
            f"- leaderboard_proxy_v1_set: `{proxy['correct']}/{proxy['rows']} = {proxy['accuracy']}`"
        )
    if payload.get("existing_audit_status") is not None:
        lines.append(f"- existing_audit_status: `{payload['existing_audit_status']}`")
    if payload.get("existing_submission_zip") is not None:
        lines.append(f"- existing_submission_zip: `{payload['existing_submission_zip']}`")
    if payload.get("reproduced_submission_zip") is not None:
        lines.append(f"- reproduced_submission_zip: `{payload['reproduced_submission_zip']}`")
    if payload.get("reproduced_validation_valid") is not None:
        lines.append(f"- reproduced_validation_valid: `{payload['reproduced_validation_valid']}`")
    if payload.get("dry_run") is not None:
        lines.append(f"- dry_run: `{payload['dry_run']}`")
    lines.extend(
        [
            "",
            "## README contract",
            "",
            f"- max_lora_rank: `{payload['readme_contract']['max_lora_rank']}`",
            f"- max_tokens: `{payload['readme_contract']['max_tokens']}`",
            f"- top_p: `{payload['readme_contract']['top_p']}`",
            f"- temperature: `{payload['readme_contract']['temperature']}`",
            f"- max_num_seqs: `{payload['readme_contract']['max_num_seqs']}`",
            f"- max_model_len: `{payload['readme_contract']['max_model_len']}`",
        ]
    )
    if payload.get("min_local_accuracy") is not None or payload.get("min_proxy_accuracy") is not None:
        lines.extend(
            [
                "",
                "## Threshold gate",
                "",
                f"- min_local_accuracy: `{payload.get('min_local_accuracy')}`",
                f"- min_proxy_accuracy: `{payload.get('min_proxy_accuracy')}`",
            ]
        )
    return "\n".join(lines)


def write_summary(output_root: Path, mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    summary_payload = {"mode": mode, **payload}
    summary_json = output_root / "threshold_submission_summary.json"
    summary_md = output_root / "threshold_submission_summary.md"
    dump_json(summary_json, summary_payload)
    dump_markdown(summary_md, render_markdown_summary(summary_payload))
    summary_payload["summary_json"] = str(summary_json)
    summary_payload["summary_md"] = str(summary_md)
    return summary_payload


def export_submission(
    *,
    run_root: Path,
    output_root: Path,
    base_model_name_or_path: str,
    dry_run: bool,
) -> dict[str, Any]:
    paths = run_paths(run_root)
    audit_output_root = output_root / "submission_compat_audit"
    export_output_root = output_root / "submission_export"

    run_command(
        uv_command(
            "audit-submission-compat",
            "--adapter-dir",
            paths["adapter_dir"],
            "--output-root",
            audit_output_root,
            "--base-model-name-or-path",
            base_model_name_or_path,
        ),
        dry_run=dry_run,
    )
    run_command(
        uv_command(
            "export-peft-submission",
            "--adapter-dir",
            paths["adapter_dir"],
            "--output-root",
            export_output_root,
            "--reference-model-root",
            paths["shadow_model"],
            "--base-model-name-or-path",
            base_model_name_or_path,
        ),
        dry_run=dry_run,
    )

    payload: dict[str, Any] = {
        "export_output_root": str(export_output_root),
        "dry_run": dry_run,
    }
    if dry_run:
        return payload

    audit_summary = load_json(audit_output_root / "submission_compat_audit.json")
    export_manifest = load_json(export_output_root / "export_manifest.json")
    submission_zip_path = Path(str(export_manifest.get("zip_path", "")))

    require(
        audit_summary.get("audit_status") == "potentially_exportable_2d_only",
        f"Unexpected reproduced audit status: {audit_summary.get('audit_status')}",
    )
    require(export_manifest.get("validation", {}).get("valid") is True, "Reproduced export manifest is not valid")
    require(submission_zip_path.exists(), f"Reproduced submission zip does not exist: {submission_zip_path}")
    require(submission_zip_path.stat().st_size > 0, f"Reproduced submission zip is empty: {submission_zip_path}")

    payload.update(
        {
            "reproduced_audit_summary": str(audit_output_root / "submission_compat_audit.json"),
            "reproduced_audit_status": audit_summary.get("audit_status"),
            "reproduced_export_manifest": str(export_output_root / "export_manifest.json"),
            "reproduced_submission_zip": str(submission_zip_path),
            "reproduced_submission_zip_size_bytes": submission_zip_path.stat().st_size,
            "reproduced_validation_valid": export_manifest.get("validation", {}).get("valid"),
        }
    )
    return payload


def command_verify_run(args: argparse.Namespace) -> int:
    payload = summarize_run(
        run_root=repo_path(args.run_root),
        threshold_label=args.threshold_label,
        min_local_accuracy=args.min_local_accuracy,
        min_proxy_accuracy=args.min_proxy_accuracy,
        expected_local_correct=args.expected_local_correct,
        expected_proxy_correct=args.expected_proxy_correct,
        expected_local_rows=args.expected_local_rows,
        expected_proxy_rows=args.expected_proxy_rows,
        require_existing_export=args.require_existing_export,
    )
    if args.output_root is not None:
        payload = write_summary(repo_path(args.output_root), "verify-run", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def command_promote_threshold(args: argparse.Namespace) -> int:
    run_root = repo_path(args.run_root)
    payload = summarize_run(
        run_root=run_root,
        threshold_label=args.threshold_label,
        min_local_accuracy=args.min_local_accuracy,
        min_proxy_accuracy=args.min_proxy_accuracy,
        expected_local_correct=args.expected_local_correct,
        expected_proxy_correct=args.expected_proxy_correct,
        expected_local_rows=args.expected_local_rows,
        expected_proxy_rows=args.expected_proxy_rows,
        require_existing_export=False,
    )
    payload.update(
        export_submission(
            run_root=run_root,
            output_root=repo_path(args.output_root),
            base_model_name_or_path=args.base_model_name_or_path,
            dry_run=args.dry_run,
        )
    )
    payload = write_summary(repo_path(args.output_root), "promote-threshold", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-file threshold submission pipeline for README.md-compliant Nemotron LoRA runs. "
            "It verifies the Kaggle Evaluation-page contract "
            "(rank<=32, max_tokens=7680, top_p=1.0, temperature=0.0, "
            "max_num_seqs=64, max_model_len=8192) and can regenerate submission.zip "
            "from any completed MLX run root that already has adapter + shadow_model artifacts."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_run = subparsers.add_parser(
        "verify-run",
        help="Verify that a completed run satisfies the README contract and optional score thresholds.",
    )
    verify_run.add_argument("--run-root", type=Path, required=True)
    verify_run.add_argument("--threshold-label", default="threshold-check")
    verify_run.add_argument("--min-local-accuracy", type=float)
    verify_run.add_argument("--min-proxy-accuracy", type=float)
    verify_run.add_argument("--expected-local-correct", type=int)
    verify_run.add_argument("--expected-proxy-correct", type=int)
    verify_run.add_argument("--expected-local-rows", type=int, default=320)
    verify_run.add_argument("--expected-proxy-rows", type=int, default=200)
    verify_run.add_argument(
        "--require-existing-export",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    verify_run.add_argument("--output-root", type=Path)
    verify_run.set_defaults(func=command_verify_run)

    promote = subparsers.add_parser(
        "promote-threshold",
        help="Verify a threshold-eligible run and regenerate submission.zip into a new output root.",
    )
    promote.add_argument("--run-root", type=Path, required=True)
    promote.add_argument("--threshold-label", required=True)
    promote.add_argument("--output-root", type=Path, required=True)
    promote.add_argument("--min-local-accuracy", type=float)
    promote.add_argument("--min-proxy-accuracy", type=float)
    promote.add_argument("--expected-local-correct", type=int)
    promote.add_argument("--expected-proxy-correct", type=int)
    promote.add_argument("--expected-local-rows", type=int, default=320)
    promote.add_argument("--expected-proxy-rows", type=int, default=200)
    promote.add_argument("--base-model-name-or-path", default=DEFAULT_BASE_MODEL_NAME)
    promote.add_argument("--dry-run", action="store_true")
    promote.set_defaults(func=command_promote_threshold)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
