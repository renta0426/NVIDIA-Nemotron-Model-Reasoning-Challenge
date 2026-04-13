#!/bin/bash
cd "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge"
uv run python materialize_reprobridges.py 2>&1
exit_code=$?
echo "Script execution completed with exit code: $exit_code"
exit $exit_code
