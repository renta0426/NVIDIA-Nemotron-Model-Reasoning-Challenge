#!/bin/bash
set -euo pipefail
"/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/.venv/bin/python3" "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py" train-mlx-config --config "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv140_bin30proxyo15p5s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/mlx_lora_config.yaml"
