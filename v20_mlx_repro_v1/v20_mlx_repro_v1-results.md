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

## Validation notebook pivot

- User-directed change: the 9500-row full `eval-aopen` path was stopped because it was too heavy for quick comparison, and the evaluation target was switched to `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`.
- Notebook contract now reproduced in the monolith:
  - dataset: `data/train.csv.head(950)`
  - prompt rendering: tokenizer chat template with `enable_thinking=True`
  - prompt content: **no boxed-answer suffix is appended**
  - scoring artifacts: `validation.csv`, `results.csv`, `mistakes/*.csv`
  - extra notebook signal: `minlogprob` per row is recorded
- The single-file script now includes:
  - `eval-adapter-validation`
  - `merge-adapter-validation`
  - `postprocess-run --postprocess-eval-kind adapter-validation`
- Smoke validation on `v20_mlx_repro_v1/outputs/smoke_train_v20_fixedpad` succeeded for the first `2` rows, producing notebook-style `validation.csv` / `results.csv` with `minlogprob`.

## Current live run

- run_root: `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad`
- status: `training complete; adapter-validation notebook reproduction running`
- latest_observed_step: `245/245`
- latest_train_loss: `0.16977385855533642`
- trained_tokens: `26576637`
- total_elapsed_seconds: `27014.2653`
- peak_memory_gb: `307.9588`
- live eval target: `adapter-validation-notebook.ipynb` first `950` rows
- live eval config:
  - `--eval-enable-thinking`
  - `--validation-sample-size 950`
  - `--eval-shards 4`
  - `--max-num-seqs 1`
  - `--prompt-chunk-size 1`
  - `--prefill-batch-size 1`
  - `--completion-batch-size 1`
- note: an earlier `4 prompts/chunk` attempt made shard progress invisible for too long, so the live run was restarted at `1 row/chunk` to get checkpoint-visible forward progress without changing the notebook scoring contract.

## Eval robustness update

- Full `eval-aopen` already had checkpoint/resume, shard merge, and `postprocess-run` support.
- The new notebook-validation path now has the same operational features:
  - shard-local checkpoint CSVs
  - resumable `validation_progress.json`
  - shard merge into root `adapter_validation/`
  - tracked results refresh through `postprocess-run`
- This keeps the implementation in the same single Python file while making long `enable_thinking=True` validation runs restartable.

## Assumptions not explicit in the public v20 config

- `lora_alpha = 32`
- `lora_dropout = 0.0`
- `Adam bias_correction = True`

## Next recorded milestone

Wait for the 4 shard-local notebook validation runs to finish, merge them into the root `adapter_validation/` summary, refresh `v20_mlx_repro_v1-results.{md,json}`, and replace this progress log with the measured 950-row result.
