#!/usr/bin/env python3
import subprocess
import sys

files = [
    "discussion/Competition Metric Bug: verify method fails for Binary String Problem (?).md",
    "nvidia-nemotron-metric.ipynb",
    "nvidia-nemotron-submission-demo.ipynb",
    "baseline_mlx/tests/test_single_file_stage_waiters.py",
    "versions/baseline_mlx/baseline_mlx-results.md"
]

try:
    result = subprocess.run(
        ["git", "--no-pager", "diff", "--"] + files,
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
