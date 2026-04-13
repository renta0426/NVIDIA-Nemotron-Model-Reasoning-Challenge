# v20_mlx_repro_v1 results

> Repository note: canonical challenge contract lives in `README.md`.
> This work directory contains a local **MLX** reproduction of the published A-Open v20 SFT pipeline using `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/` as the exact training snapshot.
> Purpose here is score reproduction on MLX, **not** submission.zip export parity.

## Source contract

- Top-level README: `README.md`
- A-Open README: `A-Open-ProgressPrizePublication/README.md`
- Data strategy: `A-Open-ProgressPrizePublication/データ戦略を理解する.md`
- SFT pipeline: `A-Open-ProgressPrizePublication/学習SFTパイプライン.md`
- Exact v20 snapshot: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/`

## Current implementation status

- Script: `v20_mlx_repro_v1/reproduce_v20_mlx_repro.py`
- Style: single-file monolith
- Training data source: exact snapshot `tokens/` + `logprobs/index.jsonl`
- Batch replay: uses recorded epoch0 `step` assignments from snapshot, not re-derived batches
- MLX base model root: `~/.cache/huggingface/hub/models--mlx-community--NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16`

## Verified smoke runs

### 1. prepare smoke

- run_root: `v20_mlx_repro_v1/outputs/smoke_prepare_v20`
- Result: snapshot contract, step plan, shadow model, and run manifest generated successfully

### 2. train smoke

- run_root: `v20_mlx_repro_v1/outputs/smoke_train_v20`
- optimizer_steps: `1/1`
- examples_in_step: `32`
- microbatches_in_step: `2`
- train_loss: `0.3943503541745424`
- step_tokens: `104294`
- elapsed_seconds: `102.3078`
- peak_memory_gb: `288.8066`

### 2b. train smoke (fixed padding)

- run_root: `v20_mlx_repro_v1/outputs/smoke_train_v20_fixedpad`
- optimizer_steps: `1/1`
- examples_in_step: `32`
- microbatches_in_step: `2`
- train_loss: `0.3943503541745424`
- step_tokens: `104294`
- elapsed_seconds: `114.7402`
- peak_memory_gb: `307.9246`
- note: keeps the v20 optimizer batch contract unchanged (`batch_size=32`, `micro_batch_size=16`) while forcing a single train shape at `max_seq_length=8192` to avoid MLX compile-shape cache growth

### 3. eval smoke

- eval_root: `v20_mlx_repro_v1/outputs/smoke_train_v20/aopen_eval`
- eval_limit: `8`
- max_tokens: `512`
- overall_accuracy: `0.125` (`1/8`)

| category | correct | total | accuracy |
| --- | ---: | ---: | ---: |
| bit_manipulation | 0 | 3 | 0.000000 |
| cipher | 0 | 2 | 0.000000 |
| gravity | 0 | 1 | 0.000000 |
| numeral | 1 | 1 | 1.000000 |
| unit_conversion | 0 | 1 | 0.000000 |

## Current live run

- run_root: `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad`
- status: `training in progress`
- latest_observed_step: `7/245`
- latest_train_loss: `0.3535739640982697`
- trained_tokens: `763998`
- latest_elapsed_seconds: `110.2308`
- peak_memory_gb: `307.9588`
- note: switched the exact-snapshot full run from dynamic per-microbatch padding to fixed train padding after host RAM climbed toward the 512 GB ceiling; batch membership/order, LR schedule, LoRA targets, and snapshot inputs remain unchanged

## Assumptions not explicit in the public v20 config

- `lora_alpha = 32`
- `lora_dropout = 0.0`
- `Adam bias_correction = True`

## Next recorded milestone

Run the full 245-step MLX training on the exact v20 snapshot, then run full A-Open evaluation on `data/train.csv` and replace this smoke-only section with the measured end-to-end result.
