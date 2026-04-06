#!/bin/bash
set -euo pipefail
"/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/.venv/bin/python3" "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v0/phase2_binary_dsl_mlx_v0.py" train-mlx-config --config "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_strong_baseline_cot_v2_v86_structured_anchor_v1_chat_bs1ga8_lr1e4_ep2/mlx_lora_config.yaml"
