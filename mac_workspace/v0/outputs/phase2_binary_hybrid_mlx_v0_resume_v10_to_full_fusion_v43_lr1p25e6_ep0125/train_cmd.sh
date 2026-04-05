#!/bin/bash
set -euo pipefail
"/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/.venv/bin/python3" "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v0/phase2_binary_dsl_mlx_v0.py" train-mlx-config --config "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_resume_v10_to_full_fusion_v43_lr1p25e6_ep0125/mlx_lora_config.yaml"
