# adapter_validation_stratified_category_300_of_950_shard_03_of_04

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- benchmark_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/data/train.csv`
- model_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter`
- overall_accuracy: `0.813333` (61/75)
- max_tokens: `7680`
- max_num_seqs: `4`
- prompt_chunk_size: `4`
- prefill_batch_size: `4`
- completion_batch_size: `4`
- eval_enable_thinking: `True`
- append_boxed_instruction: `False`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 7 | 11 | 0.636364 | 14.7% | 63.6% | 9.3% |
| cipher | 14 | 14 | 1.000000 | 18.7% | 100.0% | 18.7% |
| cryptarithm_deduce | 0 | 6 | 0.000000 | 8.0% | 0.0% | 0.0% |
| cryptarithm_guess | 0 | 1 | 0.000000 | 1.3% | 0.0% | 0.0% |
| equation_numeric_deduce | 3 | 6 | 0.500000 | 8.0% | 50.0% | 4.0% |
| gravity | 13 | 13 | 1.000000 | 17.3% | 100.0% | 17.3% |
| numeral | 10 | 10 | 1.000000 | 13.3% | 100.0% | 13.3% |
| unit_conversion | 14 | 14 | 1.000000 | 18.7% | 100.0% | 18.7% |
