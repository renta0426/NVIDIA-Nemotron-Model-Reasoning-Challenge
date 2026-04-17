#!/bin/bash
set -euo pipefail
cd '/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge'
uv \
  run \
  python \
  v20_mlx_repro_v1/reproduce_v20_mlx_repro.py \
  train \
  --model-root \
  /Users/mac-studio/.cache/huggingface/hub/models--mlx-community--NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16 \
  --output-root \
  v20_mlx_repro_v1/outputs \
  --run-name \
  v20_mlx_v4_bundle_train_smoke1 \
  --training-bundle-path \
  A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v4_mainline_bundle.jsonl \
  --seed \
  123 \
  --batch-size \
  32 \
  --micro-batch-size \
  1 \
  --learning-rate \
  0.0002 \
  --max-seq-length \
  8192 \
  --fixed-train-padding \
  --lora-rank \
  32 \
  --lora-alpha \
  32.0 \
  --lora-dropout \
  0.0 \
  --beta1 \
  0.9 \
  --beta2 \
  0.95 \
  --eps \
  1e-08 \
  --weight-decay \
  0.0 \
  --no-bias-correction \
  --steps-per-report \
  1 \
  --save-every-steps \
  0 \
  --max-optimizer-steps \
  1
