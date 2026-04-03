#!/bin/bash
set -euo pipefail
"/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/.venv/bin/python3" -m mlx_lm lora --config "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_text_prepare_smoke/mlx_lora_config.yaml"
