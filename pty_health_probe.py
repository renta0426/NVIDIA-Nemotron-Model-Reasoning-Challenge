#!/usr/bin/env python3
"""Probe Darwin PTY health for the repository's runtime blocker.

Usage:
  uv run python pty_health_probe.py
  uv run python pty_health_probe.py --output baseline_mlx/outputs/pty_health_probe.json
  uv run python pty_health_probe.py --output baseline_mlx/outputs/pty_health_probe.json --markdown-output baseline_mlx/outputs/pty_health_probe.md
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


@dataclass
class CommandResult:
    argv: list[str]
    available: bool
    returncode: int | None
    stdout: str
    stderr: str
    resolved_executable: str | None
    note: str | None = None


def run_command(argv: list[str]) -> CommandResult:
    executable = shutil.which(argv[0])
    if executable is None:
        return CommandResult(
            argv=argv,
            available=False,
            returncode=None,
            stdout="",
            stderr="",
            resolved_executable=None,
            note=f"Command not found on PATH: {argv[0]}",
        )

    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return CommandResult(
            argv=argv,
            available=True,
            returncode=None,
            stdout="",
            stderr=str(exc),
            resolved_executable=executable,
            note=f"OSError while running {' '.join(argv)}",
        )

    return CommandResult(
        argv=argv,
        available=True,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        resolved_executable=executable,
    )


def inspect_dev_ptmx() -> dict[str, Any]:
    path = Path("/dev/ptmx")
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
    }

    if not path.exists():
        return result

    stat_result = path.stat()
    result.update(
        {
            "mode": stat.filemode(stat_result.st_mode),
            "is_char_device": stat.S_ISCHR(stat_result.st_mode),
            "major": os.major(stat_result.st_rdev),
            "minor": os.minor(stat_result.st_rdev),
        }
    )
    return result


def parse_sysctl_value(stdout: str) -> str | None:
    line = stdout.strip()
    if not line:
        return None
    _, _, value = line.partition(":")
    if not value:
        return None
    return value.strip()


def summarize_lsof(stdout: str) -> dict[str, Any]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        return {"open_handle_rows": 0}
    if len(lines) == 1:
        return {"open_handle_rows": 0, "header": lines[0]}
    return {
        "open_handle_rows": len(lines) - 1,
        "header": lines[0],
        "sample_rows": lines[1:6],
    }


def build_ptmx_capacity_summary(lsof_summary: dict[str, Any] | None, sysctl_value: str | None) -> dict[str, Any]:
    open_handle_rows = None if lsof_summary is None else lsof_summary.get("open_handle_rows")
    limit = None
    if sysctl_value is not None:
        try:
            limit = int(sysctl_value)
        except ValueError:
            limit = None

    utilization = None
    near_limit = None
    if isinstance(open_handle_rows, int) and isinstance(limit, int) and limit > 0:
        utilization = round(open_handle_rows / limit, 4)
        near_limit = utilization >= 0.9

    return {
        "open_handle_rows": open_handle_rows,
        "limit": limit,
        "utilization": utilization,
        "near_limit": near_limit,
    }


def derive_probe_status(
    ptmx_info: dict[str, Any], openpty_probe: dict[str, Any], ptmx_capacity: dict[str, Any], issues: list[str]
) -> dict[str, str]:
    if not ptmx_info.get("exists", False) or not ptmx_info.get("is_char_device", False):
        return {
            "overall": "blocked",
            "primary_cause": "dev-ptmx-invalid",
        }
    if ptmx_capacity.get("near_limit") is True:
        return {
            "overall": "blocked",
            "primary_cause": "ptmx-near-limit",
        }
    if not openpty_probe.get("success", False):
        return {
            "overall": "blocked",
            "primary_cause": "openpty-failed",
        }
    if issues:
        return {
            "overall": "degraded",
            "primary_cause": "needs-attention",
        }
    return {
        "overall": "healthy",
        "primary_cause": "none",
    }


def probe_openpty() -> dict[str, Any]:
    try:
        master_fd, slave_fd = os.openpty()
    except OSError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    try:
        try:
            slave_name = os.ttyname(slave_fd)
        except OSError as exc:
            return {
                "success": False,
                "error": str(exc),
            }
    finally:
        os.close(master_fd)
        os.close(slave_fd)

    return {
        "success": True,
        "slave_name": slave_name,
    }


def render_markdown_summary(report: dict[str, Any]) -> str:
    dev_ptmx = report.get("dev_ptmx", {})
    openpty_probe = report.get("openpty_probe", {})
    probe_status = report.get("probe_status", {})
    derived = report.get("derived", {})
    lsof_summary = derived.get("lsof_summary") or {}
    ptmx_capacity = derived.get("ptmx_capacity") or {}
    issues = report.get("issues", [])
    recommended_actions = report.get("recommended_actions", [])

    lines = [
        "# PTY health probe summary",
        "",
        f"- platform: `{report.get('platform', 'unknown')}`",
        f"- overall status: `{probe_status.get('overall')}`",
        f"- primary cause: `{probe_status.get('primary_cause')}`",
        f"- /dev/ptmx exists: `{dev_ptmx.get('exists')}`",
        f"- /dev/ptmx char device: `{dev_ptmx.get('is_char_device')}`",
        f"- /dev/ptmx mode: `{dev_ptmx.get('mode')}`",
        f"- os.openpty success: `{openpty_probe.get('success')}`",
        f"- os.openpty detail: `{openpty_probe.get('slave_name') or openpty_probe.get('error')}`",
        f"- kern.tty.ptmx_max: `{derived.get('kern_tty_ptmx_max')}`",
        f"- lsof open_handle_rows: `{lsof_summary.get('open_handle_rows')}`",
        f"- ptmx utilization: `{ptmx_capacity.get('utilization')}`",
        f"- ptmx near_limit: `{ptmx_capacity.get('near_limit')}`",
        "",
        "## Issues",
    ]

    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- none")

    lines.extend(["", "## Recommended actions"])
    if recommended_actions:
        lines.extend(f"1. {action}" for action in recommended_actions)
    else:
        lines.append("1. none")

    return "\n".join(lines) + "\n"


def build_report() -> dict[str, Any]:
    platform_name = platform.system()
    ptmx_info = inspect_dev_ptmx()
    openpty_probe = probe_openpty()
    ls_result = run_command(["ls", "-l", "/dev/ptmx"])
    lsof_result = run_command(["lsof", "/dev/ptmx"])
    sysctl_ptmx_max = run_command(["sysctl", "kern.tty.ptmx_max"])

    issues: list[str] = []
    if platform_name != "Darwin":
        issues.append(
            f"This probe is tuned for Darwin/macOS PTY debugging, but current platform is {platform_name}."
        )
    if not ptmx_info["exists"]:
        issues.append("/dev/ptmx does not exist.")
    elif not ptmx_info.get("is_char_device", False):
        issues.append("/dev/ptmx exists but is not a character device.")
    if not openpty_probe["success"]:
        issues.append("Python os.openpty() failed; inspect openpty_probe.error for details.")

    if not sysctl_ptmx_max.available:
        issues.append("sysctl is unavailable, so kern.tty.ptmx_max could not be inspected.")
    elif sysctl_ptmx_max.returncode != 0:
        issues.append("sysctl kern.tty.ptmx_max failed; inspect stderr for details.")

    if not ls_result.available:
        issues.append("ls is unavailable, so /dev/ptmx permissions could not be inspected.")
    elif ls_result.returncode != 0:
        issues.append("ls -l /dev/ptmx failed; inspect stderr for details.")

    sysctl_value = parse_sysctl_value(sysctl_ptmx_max.stdout)
    lsof_summary = (
        summarize_lsof(lsof_result.stdout)
        if lsof_result.available and lsof_result.returncode in (0, 1)
        else None
    )
    ptmx_capacity = build_ptmx_capacity_summary(lsof_summary, sysctl_value)
    if ptmx_capacity["near_limit"] is True:
        issues.append("Observed /dev/ptmx open handle count is near kern.tty.ptmx_max.")
    probe_status = derive_probe_status(ptmx_info, openpty_probe, ptmx_capacity, issues)

    report = {
        "platform": platform_name,
        "probe_status": probe_status,
        "dev_ptmx": ptmx_info,
        "openpty_probe": openpty_probe,
        "commands": {
            "ls_dev_ptmx": asdict(ls_result),
            "lsof_dev_ptmx": asdict(lsof_result),
            "sysctl_kern_tty_ptmx_max": asdict(sysctl_ptmx_max),
        },
        "derived": {
            "kern_tty_ptmx_max": sysctl_value,
            "lsof_summary": lsof_summary,
            "ptmx_capacity": ptmx_capacity,
        },
        "issues": issues,
        "recommended_actions": [
            "Inspect /dev/ptmx permissions and device-node state from ls -l /dev/ptmx.",
            "Inspect current PTY holders from lsof /dev/ptmx.",
            "Compare the observed load against sysctl kern.tty.ptmx_max.",
            "If PTY allocation still fails, raise the PTY limit persistently or reboot to restore device-node state.",
        ],
    }
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path for the PTY health report.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        help="Optional Markdown output path for a human-readable PTY health summary.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    markdown_summary = render_markdown_summary(report)
    wrote_paths: dict[str, str] = {}

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        wrote_paths["json_output"] = str(args.output)

    if args.markdown_output is not None:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown_summary, encoding="utf-8")
        wrote_paths["markdown_output"] = str(args.markdown_output)

    if wrote_paths:
        if wrote_paths == {"json_output": str(args.output)}:
            print(str(args.output))
        elif wrote_paths == {"markdown_output": str(args.markdown_output)}:
            print(str(args.markdown_output))
        else:
            print(json.dumps(wrote_paths, indent=2, sort_keys=True))
    else:
        print(payload, end="")

    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
