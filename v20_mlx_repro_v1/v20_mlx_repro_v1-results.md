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

## Important assumptions

- Training data uses the exact checked-in v20 snapshot `04-08-16-14/tokens` + `logprobs/index.jsonl`, not the current `corpus.jsonl`.
- Optimizer-step grouping uses the recorded `step` assignments from the snapshot, so the MLX run replays the actual v20 batch membership/order.
- MLX-specific assumptions not explicit in the public v20 config: `lora_alpha = 32`, `lora_dropout = 0.0`, `Adam bias_correction = True`.

