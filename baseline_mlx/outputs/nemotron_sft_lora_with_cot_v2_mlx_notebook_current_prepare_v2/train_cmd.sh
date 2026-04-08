#!/bin/bash
set -euo pipefail
"/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/.venv/bin/python3" "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py" train-mlx-config --config "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_current_prepare_v2/mlx_lora_config.yaml"
