# v20_mlx_v4_mainline_submission_repro results

## Status

- Created: `2026-04-19T04:19:56.145322+00:00`
- Source run: `v20_mlx_v4_mainline_mb1_nobc`
- Source adapter dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_v4_mainline_mb1_nobc/adapter`
- Reference model root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_v4_mainline_mb1_nobc/shadow_model`
- Output root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/experiments/submission/v20_mlx_v4_mainline_submission_repro/outputs/v20_mlx_v4_mainline_submission_repro`
- submission.zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/experiments/submission/v20_mlx_v4_mainline_submission_repro/outputs/v20_mlx_v4_mainline_submission_repro/submission.zip`
- submission.zip size: `3277112238` bytes

## README contract

- max_lora_rank: `32`
- required files: `adapter_config.json, adapter_model.safetensors`
- archive name: `submission.zip`
- base_model_name_or_path: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`

## Source scores

- validation: `813/950 = 0.8558`
- proxy: `179/200 = 0.8950`
- public leaderboard: `0.85 x3, 0.86 x2`

## Export summary

- rank: `32`
- lora_alpha: `32.0`
- lora_dropout: `0.0`
- target_modules regex: `(^lm_head$|.*\.(q_proj|k_proj|v_proj|o_proj|in_proj|out_proj|up_proj|down_proj)$)`
- converted_tensor_count: `12010`
- validation.valid: `True`

## submission.zip members

- `adapter_config.json`
- `adapter_model.safetensors`

## Interpretation

- `README.md` の契約どおり、提出物は `submission.zip` 1個に `adapter_config.json` と `adapter_model.safetensors` だけを同梱する形で固定した。
- `v20_mlx_v4_mainline_mb1_nobc` は corrective 系列で最良の public 観測 run なので、この single-file export を今後の提出再現ラインとして使う。
