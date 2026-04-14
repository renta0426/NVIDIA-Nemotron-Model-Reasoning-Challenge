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
- status: `training complete; A-Open eval running`
- latest_observed_step: `245/245`
- latest_train_loss: `0.16977385855533642`
- trained_tokens: `26576637`
- total_elapsed_seconds: `27014.2653`
- peak_memory_gb: `307.9588`
- note: switched the exact-snapshot full run from dynamic per-microbatch padding to fixed train padding after host RAM climbed toward the 512 GB ceiling; batch membership/order, LR schedule, LoRA targets, and snapshot inputs remain unchanged

## Eval robustness update

- Full `eval-aopen` now checkpoints chunk-level progress into `aopen_eval/benchmark_eval_records_checkpoint.csv`.
- If the 9500-row evaluation is interrupted, rerunning the same command resumes from the recorded row count instead of restarting from zero.
- If `benchmark_eval_summary.json` already exists with `benchmark_eval_progress.json.status == complete`, the script returns that summary immediately instead of recomputing.
- `postprocess-run` can now rebuild the tracked `v20_mlx_repro_v1-results.{md,json}` files from an existing run's `training_result.json` and `benchmark_eval_summary.json`.
- The script now also supports sharded eval via `--eval-shards`, `--eval-shard-index`, and `merge-aopen-eval`, while keeping the implementation in this single file.

## Eval execution log

- The first full-eval resume attempt stayed at the existing root checkpoint `16/9500` while running a single high-concurrency chunk (`max_num_seqs=64`, `prompt_chunk_size=64`), so wall-clock throughput was judged too poor to keep.
- A first shard-parallel retry with **6 shard workers** at `max_num_seqs=16`, `prompt_chunk_size=16`, `prefill=16`, `completion=16` also produced `0/6` shard summaries after roughly 44 minutes, so the bottleneck was no longer just batch size.
- Inspecting the MLX chat template showed:
  - `--eval-enable-thinking` leaves the assistant prompt open at `<think>`
  - `--no-eval-enable-thinking` closes it as `<think></think>` before generation starts
- That made `--no-eval-enable-thinking` the most likely explanation for the long local generations, so a direct benchmark was run before changing the full eval again.
- Probe result on the first `4` training rows with `--no-eval-enable-thinking --max-num-seqs 4 --prompt-chunk-size 4`:
  - accuracy: `1/4 = 0.25`
  - `boxed_found: 4/4`
  - output char length: `min=15`, `median=16`, `max=15359`
- Probe result on the first `16` training rows with the same no-thinking settings:
  - no-thinking accuracy: `5/16 = 0.3125`
  - previous thinking accuracy on the same 16 rows: `2/16 = 0.125`
  - `boxed_found: 16/16`
  - output char length: `min=11`, `median=15`, `max=15359`
- Important correction: the competition metric notebook (`nvidia-nemotron-metric.ipynb`) applies the tokenizer chat template with `enable_thinking=True`, so the no-thinking run is **not** the canonical reproduction target.
- Therefore the no-thinking shard run is retained only as a **local diagnostic experiment** and was archived to:
  - `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad/aopen_eval/shards_nothinking_experiment_20260414-090605/`
- The current live evaluation has been reset to the **canonical metric-aligned configuration**:
  - `--eval-enable-thinking`
  - `--eval-shards 6`
  - `--max-num-seqs 4`
  - `--prompt-chunk-size 4`
  - `--prefill-batch-size 4`
  - `--completion-batch-size 4`
- Active canonical shard outputs now live under `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad/aopen_eval/shards/`.
- The waiter process now polls for `6/6` canonical shard summaries, then runs `merge-aopen-eval -> postprocess-run -> git commit/push`.
- Immediate canonical status after the restart: all 6 shards launched cleanly and resumed from `0`, with full evaluation size still `9500` rows split as `1584 / 1584 / 1583 / 1583 / 1583 / 1583`.

## Assumptions not explicit in the public v20 config

- `lora_alpha = 32`
- `lora_dropout = 0.0`
- `Adam bias_correction = True`

## Next recorded milestone

Wait for the 6 shard-local A-Open eval runs to finish, merge them into the root `aopen_eval/` summary, refresh `v20_mlx_repro_v1-results.{md,json}`, and replace this progress log with the measured end-to-end result.
