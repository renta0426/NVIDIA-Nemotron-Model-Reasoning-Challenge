#!/bin/bash
set -euo pipefail
"/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/.venv/bin/python3" "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v1/phase2_binary_dsl_mlx_v1.py" train-mlx-config --config "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v1/outputs/resume_v40_to_top8_fusion_v147_chat_lr2p5e6_ep025/mlx_lora_config.yaml"
