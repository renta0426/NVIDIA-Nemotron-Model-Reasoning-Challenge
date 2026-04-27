# v20_mlx_repro_v1 results

> Repository note: canonical challenge contract lives in `README.md`.
> This version is a local MLX training/evaluation runner for A-Open v20-style Nemotron LoRA experiments.
> It does **not** claim submission.zip parity; it measures local behavior under the README-grounded evaluation contract.

## Source contract

- Top-level README: `README.md`
- V20 snapshot: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14`
- training_source_type: `single_file_bundle`

## Run summary

- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v7/v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20`
- shadow_model_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v7/v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v7/v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20/adapter`
- snapshot_contract_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v7/v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20/snapshot_contract.json`
- run_manifest_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v7/v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20/run_manifest.json`

## Training settings

- backend: `mlx`
- training_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v7_targeted_miss_recovery_bundle.jsonl`
- optimizer_steps: `265`
- last_train_loss: `1.0338541269302368`
- last_lr: `7.547169811320753e-07`
- train_cmd_path: `v20_mlx_repro_v1/outputs/v7/v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20/train_cmd.sh`
- training_micro_batch_size: `1`
- lora_rank: `32`
- adam_bias_correction: `False`

## Evaluation result

- evaluation_kind: `adapter_validation`
- evaluation_name: `adapter_validation_stratified_category_300_of_950`
- overall_accuracy: `0.096667` (29/300)

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
- max_num_seqs: `64`
- prompt_chunk_size: `1`
- prefill_batch_size: `1`
- completion_batch_size: `1`
- eval_enable_thinking: `False`
- eval_shards: `4`

## Prompt policy

- append_boxed_instruction: `False`
- enable_thinking: `False`

## Eval aggregation

- mode: `sharded`
- shard_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v7/v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20/adapter_validation/shards`
- num_shards: `4`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 2 | 53 | 0.037736 | 17.7% | 3.8% | 0.7% |
| cipher | 0 | 51 | 0.000000 | 17.0% | 0.0% | 0.0% |
| cryptarithm_deduce | 0 | 23 | 0.000000 | 7.7% | 0.0% | 0.0% |
| cryptarithm_guess | 0 | 5 | 0.000000 | 1.7% | 0.0% | 0.0% |
| equation_numeric_deduce | 2 | 15 | 0.133333 | 5.0% | 13.3% | 0.7% |
| equation_numeric_guess | 0 | 2 | 0.000000 | 0.7% | 0.0% | 0.0% |
| gravity | 1 | 50 | 0.020000 | 16.7% | 2.0% | 0.3% |
| numeral | 19 | 47 | 0.404255 | 15.7% | 40.4% | 6.3% |
| unit_conversion | 5 | 54 | 0.092593 | 18.0% | 9.3% | 1.7% |

## Important assumptions

- Training data uses the exact checked-in v20 snapshot `04-08-16-14/tokens` + `logprobs/index.jsonl`, not the current `corpus.jsonl`.
- Optimizer-step grouping uses the recorded `step` assignments from the snapshot, so the MLX run replays the actual v20 batch membership/order.
- MLX-specific assumptions not explicit in the public v20 config: `lora_alpha = 32.0`, `lora_dropout = 0.0`, `Adam bias_correction = False`.

