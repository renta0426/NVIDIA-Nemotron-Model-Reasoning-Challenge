#!/usr/bin/env python3
"""Canonical reprobridge33/34 materialization entrypoint."""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path("/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge")
DEFAULT_OUTPUT_PATH = REPO_ROOT / "materialize_results_output.json"
DEFAULT_ERROR_PATH = REPO_ROOT / "materialize_error.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from launch_reprobridge31_32_recovery import materialize_followups


def run_materialization(
    step_name: str = "all",
    dry_run: bool = False,
) -> list[dict[str, object]]:
    return materialize_followups(step_name=step_name, dry_run=dry_run)


def render_materialization_output(
    step_name: str = "all",
    dry_run: bool = False,
) -> str:
    return json.dumps(
        run_materialization(step_name=step_name, dry_run=dry_run),
        ensure_ascii=False,
        indent=2,
    )


def main() -> int:
    print(render_materialization_output(step_name="all", dry_run=False))
    return 0


def write_capture_payload(path: Path, payload_text: str, label: str) -> bool:
    try:
        path.write_text(payload_text + "\n", encoding="utf-8")
    except OSError as exc:
        write_error = {
            "error": f"Failed to write {label} capture file {path}: {exc}",
            "type": type(exc).__name__,
            "traceback": traceback.format_exc(),
        }
        print(json.dumps(write_error, ensure_ascii=False, indent=2), file=sys.stderr)
        return False
    print(f"[{label.capitalize()} also saved to: {path}]", file=sys.stderr)
    return True


def main_with_output_capture(
    *,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    error_path: Path = DEFAULT_ERROR_PATH,
) -> int:
    try:
        output_text = render_materialization_output(step_name="all", dry_run=False)
    except Exception as exc:
        error_payload = {
            "error": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc(),
        }
        error_text = json.dumps(error_payload, ensure_ascii=False, indent=2)
        write_capture_payload(error_path, error_text, "error")
        print(error_text)
        return 1

    if not write_capture_payload(output_path, output_text, "output"):
        return 1
    print(output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
