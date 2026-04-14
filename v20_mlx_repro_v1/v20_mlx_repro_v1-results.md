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
  - `--max-num-seqs 4`
  - `--prompt-chunk-size 4`
  - `--prefill-batch-size 4`
  - `--completion-batch-size 4`
- resume status at relaunch:
  - shard `0`: `1/238`
  - shard `1`: `5/238`
  - shard `2`: `2/237`
  - shard `3`: `1/237`
- checkpoint behavior update:
  - the first 4-shard relaunch still checkpointed only chunk-level contiguous prefixes, so long `enable_thinking=True` generations could hide progress until an entire 4-row chunk finished
  - the monolith was then updated to persist `row_index_within_shard` in the shard checkpoint CSV and resume from the completed-index set instead of the prefix length
  - the current live 4-shard run is therefore a **finer-checkpoint relaunch** on the same root, preserving old rows and allowing per-row progress inside each chunk
- parallelism note:
  - an **8-shard** relaunch was attempted after the single-process throughput benchmark, but free pages collapsed into a near-OOM range immediately after startup, so it was aborted before any useful checkpoint was written
  - a **6-shard** relaunch restored memory headroom, but still did not finish the first `4-row` chunk on any shard after a long wait, so it was slower in practice than the already-proven 4-shard path
  - the live run therefore returned to **4-shard / 4x4**, which had already shown real checkpoint progress

## Throughput benchmark before final relaunch

- To choose the local MLX evaluation settings for the 950-row notebook validation, the exact fullrun adapter was benchmarked on the same first `4` rows under three deterministic settings:

| config | max_num_seqs | prompt_chunk_size | prefill | completion | elapsed_seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| seq1 | 1 | 1 | 1 | 1 | 800 |
| seq2 | 2 | 2 | 2 | 2 | 785 |
| seq4 | 4 | 4 | 4 | 4 | 659 |

- Result: `seq4` was clearly best on the same workload, so the live 950-row run was relaunched from the existing shard checkpoints with `4x4` batching instead of `1x1`.

### Token throughput on the same 4-row benchmark

- README evaluation contract reference: `max_tokens=7680`, `max_model_len=8192`, `temperature=0.0`, `top_p=1.0`, `max_num_seqs=64`.
- Benchmark prompt policy matched the notebook reproduction path: `enable_thinking=True` and **no boxed-answer suffix**.
- The first 4 validation rows used for this benchmark had `824` prompt tokens in total after chat templating.
- All 4 generations hit the `max_tokens=7680` cap, so each run generated exactly `30,720` output tokens total.

| config | elapsed_seconds | prompt_tokens_total | output_tokens_total | output_tok_per_sec | total_tok_per_sec | avg_output_tok_per_row |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| seq1 | 800 | 824 | 30720 | 38.40 | 39.43 | 7680 |
| seq2 | 785 | 824 | 30720 | 39.13 | 40.18 | 7680 |
| seq4 | 659 | 824 | 30720 | 46.62 | 47.87 | 7680 |

- Interpretation: under the current non-quantized MLX setup, the best measured single-process notebook-style benchmark here is about **46.6 output tok/s** aggregate at `4x4`, or about **11.65 output tok/s per row** when 4 requests are batched together.
- A later live-sample recount over the first `53` completed rows of the real 950-row run showed why wall-clock progress is still slow even after finer checkpointing:
  - average output length: `6602.85` tokens
  - median output length: `7680` tokens
  - `45/53` rows had already hit the `7680` cap
  - only `8/53` rows finished at `<= 2000` output tokens
- So the bottleneck is not just MLX BF16 inference speed; the notebook-style `enable_thinking=True` generations themselves frequently expand all the way to the README contract cap.

## Checkpoint schema repair during live eval

- After the first row-index checkpoint relaunch, shard-local `validation_records_checkpoint.csv` files were found to have a **mixed schema**:
  - legacy rows from the prefix-based checkpoint path still used the old 8-column header
  - new per-row checkpoint appends wrote 9 columns with `row_index_within_shard`
- This would have broken a later restart or any direct CSV parsing, so the monolith was hardened to:
  - load validation CSVs with `csv.reader` instead of `pandas.read_csv`
  - accept legacy 8-column rows, final `validation.csv` rows, and mixed 8/9-column checkpoint files
  - rewrite shard checkpoint files to the normalized 9-column schema before appending new rows
- The live 4-shard run was then stopped, repaired, and resumed successfully from:
  - shard `0`: `11/238`
  - shard `1`: `16/238`
  - shard `2`: `13/237`
  - shard `3`: `13/237`

## Pivot from 950 rows to a stratified 317-row subset

- User-directed change: the exact notebook-style 950-row validation was projected to take too long on the current non-quantized MLX path, so the live target was changed from the full first `950` rows to a **category-proportional one-third subset** of that same notebook population.
- The monolith now supports this with:
  - `--validation-subset-size`
  - `--validation-subset-mode stratified-category-proportional`
- Selection policy:
  - start from `train.csv.head(950)` exactly as the notebook does
  - re-detect categories from prompt text with the notebook-compatible classifier
  - allocate integer per-category subset counts by proportional largest-remainder rounding
  - choose rows deterministically and evenly within each category bucket, then restore original global row order
- The resulting `317`-row subset preserves the first-950 category mix as:

| category | first_950 | stratified_317 |
| --- | ---: | ---: |
| bit_manipulation | 169 | 56 |
| cipher | 162 | 54 |
| cryptarithm_deduce | 71 | 24 |
| cryptarithm_guess | 14 | 5 |
| equation_numeric_deduce | 48 | 16 |
| equation_numeric_guess | 7 | 2 |
| gravity | 159 | 53 |
| numeral | 149 | 50 |
| unit_conversion | 171 | 57 |

- Live run switched to:
  - run root: `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad_validation317_stratified/`
  - eval shape: `6-shard / 4x4`
  - notebook prompt policy unchanged: `enable_thinking=True`, no boxed suffix

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
