# v20_mlx_repro_v1 results

> Repository note: canonical challenge contract lives in `README.md`.
> This version is a local MLX reproduction of A-Open v20 using `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/` as the exact training snapshot.
> It does **not** claim submission.zip parity; it measures how closely MLX reproduces the published v20 training/eval behavior.

## Source contract

- Top-level README: `README.md`
- V20 snapshot: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14`

## Run summary

- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1`
- shadow_model_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter`
- snapshot_contract_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/snapshot_contract.json`

## Training settings

- backend: `mlx`
- optimizer_steps: `245`
- last_train_loss: `0.00030877206662561054`
- last_lr: `8.163265306122547e-07`

## Evaluation result

- evaluation_kind: `adapter_validation`
- evaluation_name: `adapter_validation_stratified_category_300_of_950`
- overall_accuracy: `0.82` (246/300)

- source_document: `README.md`
- source_document: `A-Open-ProgressPrizePublication/README.md`
- source_document: `A-Open-ProgressPrizePublication/データ戦略を理解する.md`
- source_document: `A-Open-ProgressPrizePublication/学習SFTパイプライン.md`
- source_document: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- validation_sample_size: `950`
- sample_selection_mode: `stratified-category-proportional`
- sample_selection_tag: `stratified_category_300_of_950`
- sample_selection_total: `300` / `950`

## Eval settings

- max_tokens: `7680`
- max_num_seqs: `4`
- prompt_chunk_size: `4`
- prefill_batch_size: `4`
- completion_batch_size: `4`
- eval_enable_thinking: `True`
- eval_shards: `4`

## Prompt policy

- append_boxed_instruction: `False`
- enable_thinking: `True`

## Eval aggregation

- mode: `sharded`
- shard_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter_validation/shards`
- num_shards: `4`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 37 | 53 | 0.698113 | 17.7% | 69.8% | 12.3% |
| cipher | 50 | 51 | 0.980392 | 17.0% | 98.0% | 16.7% |
| cryptarithm_deduce | 0 | 23 | 0.000000 | 7.7% | 0.0% | 0.0% |
| cryptarithm_guess | 1 | 5 | 0.200000 | 1.7% | 20.0% | 0.3% |
| equation_numeric_deduce | 7 | 15 | 0.466667 | 5.0% | 46.7% | 2.3% |
| equation_numeric_guess | 0 | 2 | 0.000000 | 0.7% | 0.0% | 0.0% |
| gravity | 50 | 50 | 1.000000 | 16.7% | 100.0% | 16.7% |
| numeral | 47 | 47 | 1.000000 | 15.7% | 100.0% | 15.7% |
| unit_conversion | 54 | 54 | 1.000000 | 18.0% | 100.0% | 18.0% |

## Post-eval notes

- Final MLX reproduced run on `adapter_validation_stratified_category_300_of_950`: **`246 / 300 = 0.82`**
- Strong families:
  - `gravity = 50 / 50`
  - `numeral = 47 / 47`
  - `unit_conversion = 54 / 54`
  - `cipher = 50 / 51`
- Main loss buckets:
  - `cryptarithm_deduce = 0 / 23`
  - `equation_numeric_guess = 0 / 2`
  - `cryptarithm_guess = 1 / 5`
  - `equation_numeric_deduce = 7 / 15`
  - `bit_manipulation = 37 / 53`
- Publication deterministic reasoners benchmarked directly on the same 300-row subset reached **`257 / 300 = 0.856667`**.
- Reasoner-over-model gains were concentrated in `equation_numeric_deduce` (`7 -> 15` correct), with smaller gains in `bit_manipulation` (`37 -> 39`) and `cipher` (`50 -> 51`), while both model and reasoners remained weak on `cryptarithm_*` and `equation_numeric_guess`.
- When the published first-950 notebook ratios are projected onto this exact 300-row subset, the expected counts are roughly `gravity 50`, `numeral 47`, `unit_conversion 54`, `cipher 49.74`, `bit_manipulation 46.73`, `equation_numeric_deduce 13.12`, `cryptarithm_deduce 1.94`, `cryptarithm_guess 1.07`, `equation_numeric_guess 0`. The MLX run is therefore close on the easy families and `cipher`, while the real reproduction gap is concentrated in `bit_manipulation` and `equation_numeric_deduce`.
- All `8/8` current `equation_numeric_deduce` misses in `validation.csv` were long incomplete generations with **no** `\boxed{}` and **no** closing `</think>`, so the visible failure mode there is truncation / runaway reasoning rather than answer-extraction loss.
- However, a same-weights **no-thinking** probe on those exact `8` failed `equation_numeric_deduce` rows recovered **`0 / 8`**; outputs collapsed to short wrong answers (average `24.5` chars) instead of the long truncated traces. This means the long-thinking behavior changes how the failure appears, but turning thinking off does **not** rescue the missing skill.
- A same-weights **no-thinking** probe on the exact `16` failed `bit_manipulation` rows likewise recovered **`0 / 16`** (average `822.1` chars, median `102.5`), so the main bit losses also persist without the long-thinking path.
- On the full focus slice (`bit_manipulation + equation_numeric_deduce`, `68` rows total) the same-weights **no-thinking** ablation collapsed from baseline **`44 / 68`** to **`4 / 68`**. Category-wise that is `bit_manipulation 37 / 53 -> 3 / 53` and `equation_numeric_deduce 7 / 15 -> 1 / 15`.
- That full-slice ablation produced **`0` improved rows**, **`40` regressed rows**, and only **`28` unchanged rows**. So `enable_thinking=True` is not the reason these categories underperform; if anything it is preserving a large amount of capability that disappears when thinking is disabled.
- One nuance from the available source logs: the checked-in v20 snapshot config says `micro_batch_size = 16`, but the user's PEFT replay log with the already-matched target modules / trainable params reports `local_micro_batch_size = 1` together with `optimizer_kind = paged_adamw_8bit`. So micro-batch mismatch alone is **not** the cleanest confirmed explanation; the strongest confirmed training-side difference is now the optimizer/backend path (`paged_adamw_8bit`/PEFT or Tinker versus MLX `optim.Adam`).
- Current diagnosis: the dominant residual is more consistent with **training / weight divergence** from the original v20 path than with MLX eval extraction bugs or thinking-mode verbosity alone. Thinking still matters as a secondary inference-behavior factor for `equation_numeric_deduce`, because it turns short wrong answers into long unfinished traces, but the ablation shows it is net-helpful rather than the core cause of the gap.
- Status note: the completed full train for this version is still **`v20_mlx_repro_v1_fullrun_targetfix_mb1`**, i.e. the MLX `optim.Adam` path recorded in `run_manifest.json`. A full retrain that closes the remaining optimizer/backend gap to the available source evidence (`backend=tinker` and/or `optimizer_kind=paged_adamw_8bit`) has **not** been run yet. Under `README.md`, this gap is an open **v20 strict-reproduction** task, not a challenge-format compliance blocker.

## Important assumptions

- Training data uses the exact checked-in v20 snapshot `04-08-16-14/tokens` + `logprobs/index.jsonl`, not the current `corpus.jsonl`.
- Optimizer-step grouping uses the recorded `step` assignments from the snapshot, so the MLX run replays the actual v20 batch membership/order.
- MLX-specific assumptions not explicit in the public v20 config: `lora_alpha = 32`, `lora_dropout = 0.0`, `Adam bias_correction = True`.
