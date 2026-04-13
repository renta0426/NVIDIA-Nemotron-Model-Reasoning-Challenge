#!/usr/bin/env python3
"""Compatibility shim for legacy root-level actions and repo root helpers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "baseline_mlx" / "outputs"
LEGACY_ACTIONS = (
    "wait-resume-train-from-path",
    "poll-live-run-status",
    "postprocess-run",
)
ROOT_ONLY_ACTIONS = ("pty-health-probe",)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from baseline_mlx.reproduce_nemotron_sft_lora_with_cot_v2_mlx import main as baseline_mlx_main
from pty_health_probe import main as pty_health_probe_main


def run_root_from_name(run_name: str) -> Path:
    return DEFAULT_OUTPUT_ROOT / run_name


def build_legacy_action_parser(action: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="main.py")
    parser.add_argument("--action", choices=LEGACY_ACTIONS, required=True)
    parser.add_argument("--run-name", required=True)

    if action == "wait-resume-train-from-path":
        parser.add_argument("--train-csv", required=True)
        parser.add_argument("--source-run-root", required=True)
        parser.add_argument("--wait-summary-path", required=True)
        parser.add_argument("--memory-requirement-gb", required=True)
        parser.add_argument("--lr", required=True)
        parser.add_argument("--epochs", required=True)
        parser.add_argument("--max-seq-length", required=True)
        parser.add_argument("--valid-shadow-rows", required=True)
        parser.add_argument("--lora-key-group", action="append", default=[])
        parser.add_argument("--trainable-lora-suffix-group", action="append", default=[])
        parser.add_argument("--type-samples", action="append", nargs=2, metavar=("TYPE", "COUNT"), default=[])
        return parser

    if action == "poll-live-run-status":
        parser.add_argument("--live-poller-label", default=None)
        return parser

    if action == "postprocess-run":
        parser.add_argument("--train-csv", default=None)
        parser.add_argument("--results-label", default=None)
        parser.add_argument("--extra-benchmark-csv", action="append", default=[])
        parser.add_argument("--publish-commit-msg", default=None)
        return parser

    raise SystemExit(f"Unsupported legacy action: {action}")


def build_root_only_action_parser(action: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="main.py")
    parser.add_argument("--action", choices=ROOT_ONLY_ACTIONS, required=True)

    if action == "pty-health-probe":
        parser.add_argument("--output", type=Path, default=None)
        parser.add_argument("--markdown-output", type=Path, default=None)
        return parser

    raise SystemExit(f"Unsupported root-only action: {action}")


def translate_type_samples(entries: Sequence[Sequence[str]]) -> list[str]:
    translated: list[str] = []
    for puzzle_type, count in entries:
        translated.extend(["--type-sample", f"{puzzle_type}={count}"])
    return translated


def translate_legacy_action_args(argv: Sequence[str]) -> list[str]:
    raw_argv = list(argv)
    if not raw_argv or raw_argv[0] != "--action":
        return raw_argv

    bootstrap = argparse.ArgumentParser(add_help=False)
    bootstrap.add_argument("--action", required=True)
    bootstrap_args, _ = bootstrap.parse_known_args(raw_argv)
    if bootstrap_args.action not in LEGACY_ACTIONS:
        return raw_argv
    args = build_legacy_action_parser(bootstrap_args.action).parse_args(raw_argv)

    if args.action == "wait-resume-train-from-path":
        translated = [
            args.action,
            "--run-name",
            args.run_name,
            "--train-csv",
            args.train_csv,
            "--source-run-root",
            args.source_run_root,
            "--wait-path",
            args.wait_summary_path,
            "--min-free-gb",
            args.memory_requirement_gb,
            "--learning-rate",
            args.lr,
            "--num-epochs",
            args.epochs,
            "--max-seq-length",
            args.max_seq_length,
            "--valid-shadow-rows",
            args.valid_shadow_rows,
        ]
        for value in args.lora_key_group:
            translated.extend(["--lora-key-group", value])
        for value in args.trainable_lora_suffix_group:
            translated.extend(["--trainable-lora-suffix-group", value])
        translated.extend(translate_type_samples(args.type_samples))
        return translated

    if args.action == "poll-live-run-status":
        translated = [
            args.action,
            "--run-root",
            str(run_root_from_name(args.run_name)),
        ]
        if args.live_poller_label:
            translated.extend(["--label", args.live_poller_label])
        return translated

    if args.action == "postprocess-run":
        translated = [
            args.action,
            "--run-root",
            str(run_root_from_name(args.run_name)),
        ]
        if args.results_label:
            translated.extend(["--label", args.results_label])
        for value in args.extra_benchmark_csv:
            translated.extend(["--extra-benchmark-csv", value])
        if args.publish_commit_msg:
            translated.append("--run-publish-results-md")
            translated.extend(["--publish-commit-message", args.publish_commit_msg])
        return translated

    raise SystemExit(f"Unsupported legacy action: {args.action}")


def run_root_only_action(argv: Sequence[str]) -> int | None:
    raw_argv = list(argv)
    if not raw_argv or raw_argv[0] != "--action":
        return None

    bootstrap = argparse.ArgumentParser(add_help=False)
    bootstrap.add_argument("--action", required=True)
    bootstrap_args, _ = bootstrap.parse_known_args(raw_argv)
    if bootstrap_args.action not in ROOT_ONLY_ACTIONS:
        return None

    args = build_root_only_action_parser(bootstrap_args.action).parse_args(raw_argv)
    if args.action == "pty-health-probe":
        forwarded: list[str] = []
        if args.output is not None:
            forwarded.extend(["--output", str(args.output)])
        if args.markdown_output is not None:
            forwarded.extend(["--markdown-output", str(args.markdown_output)])
        return pty_health_probe_main(forwarded)

    raise SystemExit(f"Unsupported root-only action: {args.action}")


def main(argv: Sequence[str] | None = None) -> None:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    root_only_exit_code = run_root_only_action(raw_argv)
    if root_only_exit_code is not None:
        raise SystemExit(root_only_exit_code)
    baseline_mlx_main(translate_legacy_action_args(raw_argv))


if __name__ == "__main__":
    main()
