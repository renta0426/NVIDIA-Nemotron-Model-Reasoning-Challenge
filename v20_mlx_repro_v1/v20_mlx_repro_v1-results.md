# v20_mlx_repro_v1 results

> Repository note: canonical challenge contract lives in `README.md`.
> This version is a local MLX reproduction of A-Open v20 using `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/` as the exact training snapshot.
> It does **not** claim submission.zip parity; it measures how closely MLX reproduces the published v20 training/eval behavior.

## Source contract

- Top-level README: `README.md`
- V20 snapshot: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14`

## Run summary

- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad`
- shadow_model_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad/adapter`
- snapshot_contract_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad/snapshot_contract.json`

## Training settings

- backend: `mlx`
- optimizer_steps: `245`
- last_train_loss: `0.16977385855533642`
- last_lr: `8.163265306122547e-07`

## Evaluation result

- evaluation_kind: `adapter_validation`
- evaluation_name: `adapter_validation_stratified_category_317_of_950`
- overall_accuracy: `0.157729` (50/317)

- source_document: `README.md`
- source_document: `A-Open-ProgressPrizePublication/README.md`
- source_document: `A-Open-ProgressPrizePublication/データ戦略を理解する.md`
- source_document: `A-Open-ProgressPrizePublication/学習SFTパイプライン.md`
- source_document: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- validation_sample_size: `950`
- sample_selection_mode: `stratified-category-proportional`
- sample_selection_tag: `stratified_category_317_of_950`
- sample_selection_total: `317` / `950`

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
- shard_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad_validation317_stratified/adapter_validation/shards`
- num_shards: `4`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 0 | 56 | 0.000000 | 17.7% | 0.0% | 0.0% |
| cipher | 0 | 54 | 0.000000 | 17.0% | 0.0% | 0.0% |
| cryptarithm_deduce | 0 | 24 | 0.000000 | 7.6% | 0.0% | 0.0% |
| cryptarithm_guess | 0 | 5 | 0.000000 | 1.6% | 0.0% | 0.0% |
| equation_numeric_deduce | 0 | 16 | 0.000000 | 5.0% | 0.0% | 0.0% |
| equation_numeric_guess | 0 | 2 | 0.000000 | 0.6% | 0.0% | 0.0% |
| gravity | 3 | 53 | 0.056604 | 16.7% | 5.7% | 0.9% |
| numeral | 36 | 50 | 0.720000 | 15.8% | 72.0% | 11.4% |
| unit_conversion | 11 | 57 | 0.192982 | 18.0% | 19.3% | 3.5% |

## Important assumptions

- Training data uses the exact checked-in v20 snapshot `04-08-16-14/tokens` + `logprobs/index.jsonl`, not the current `corpus.jsonl`.
- Optimizer-step grouping uses the recorded `step` assignments from the snapshot, so the MLX run replays the actual v20 batch membership/order.
- MLX-specific assumptions not explicit in the public v20 config: `lora_alpha = 32`, `lora_dropout = 0.0`, `Adam bias_correction = True`.

## Final notes

- Final measured local result for the notebook-style **stratified 317-of-950** validation is **`50/317 = 0.157729`**.
- Strength is still concentrated in `numeral` (`36/50 = 0.72`); every cryptarithm / equation subset remained at `0`.
- During the long sharded run, GPU utilization temporarily collapsed even though memory stayed allocated. `pmset -g therm` showed no thermal/performance warning, and restarting only the shard workers restored GPU saturation, so this looked like a stuck MLX/Metal run state rather than a system-wide protection mode.
- After all four shards finished, the first merge attempt failed with a `sample_selection` scope bug in `run_merge_adapter_validation()`. The single-file monolith was patched, then `merge-adapter-validation` and `postprocess-run` were rerun successfully.
- Separate vMLX / vLLM-MLX engine probes are recorded in `appendix/mlx_faster.md`.

## 2026-04-15 target-fix smoke preflight

- Root-cause investigation showed the previous failed run had only `lm_head` LoRA weights because MLX local module names require the `mixer.` prefix. `default_lora_keys()` was corrected accordingly and now emits a preflight `lora_match_summary.json`.
- Corrected MLX LoRA target match now lines up with the Kaggle/PEFT reproduction log:
  - `q_proj 6`
  - `k_proj 6`
  - `v_proj 6`
  - `o_proj 6`
  - `in_proj 23`
  - `out_proj 23`
  - `up_proj 2967`
  - `down_proj 2967`
  - `lm_head 1`
  - `trainable params 888,154,112` (`2.7356%`)
- A 1-step smoke train at `micro_batch_size=1` succeeded under MLX with this corrected target coverage:
  - run: `v20_mlx_repro_v1_smoke_targetfix_mb1`
  - `train_loss = 0.3835325885531003`
  - `step_tokens = 104262`
  - `elapsed_seconds = 305.9085`
  - `peak_memory_gb = 214.8353`
- The same corrected 888M-trainable setup OOMed at `micro_batch_size=16`, so the corrected full retrain was relaunched as `v20_mlx_repro_v1_fullrun_targetfix_mb1`.

## 2026-04-15 corrected full retrain progress

- source_document: `README.md`
- source_document: `A-Open-ProgressPrizePublication/README.md`
- run: `v20_mlx_repro_v1_fullrun_targetfix_mb1`
- status: `training_in_progress`
- latest_observed_step: `100 / 245`
- latest_train_loss: `0.0011526059979845976`
- latest_trained_tokens: `10845455`
- latest_peak_memory_gb: `221.9409`
- latest_step_elapsed_seconds: `303.7`
- estimated_remaining_hours_from_step100: `12.4`
- current fullrun adapter dir still has only report files (`latest_train_report.json`, `train_report.jsonl`) and no mid-run `adapters.safetensors`, so this launch remains vulnerable until final save.
- During live-run auditing, the waiting `eval300` watcher was found to use `postprocess-run --postprocess-eval-kind adapter_validation`, but the single-file CLI only accepts `adapter-validation`. The stale watcher was stopped and relaunched with the correct hyphenated kind before training completion, so post-smoke merge/postprocess will not fail on that typo.
- Preflight-only failed smoke directories (`v20_mlx_repro_v1_smoke_targetfix`, `_mb2`, `_mb4`, `_mb8`) were deleted during retrain monitoring. The retained artifacts are the successful corrected 1-step smoke run (`6.6 GB`) and the live fullrun root.
