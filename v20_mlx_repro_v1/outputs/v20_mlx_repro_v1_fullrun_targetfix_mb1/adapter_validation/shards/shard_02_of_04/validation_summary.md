# adapter_validation_stratified_category_300_of_950_shard_02_of_04

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- benchmark_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/data/train.csv`
- model_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter`
- overall_accuracy: `0.866667` (65/75)
- max_tokens: `7680`
- max_num_seqs: `4`
- prompt_chunk_size: `4`
- prefill_batch_size: `4`
- completion_batch_size: `4`
- eval_enable_thinking: `True`
- append_boxed_instruction: `False`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 13 | 14 | 0.928571 | 18.7% | 92.9% | 17.3% |
| cipher | 12 | 12 | 1.000000 | 16.0% | 100.0% | 16.0% |
| cryptarithm_deduce | 0 | 7 | 0.000000 | 9.3% | 0.0% | 0.0% |
| cryptarithm_guess | 1 | 1 | 1.000000 | 1.3% | 100.0% | 1.3% |
| equation_numeric_deduce | 2 | 4 | 0.500000 | 5.3% | 50.0% | 2.7% |
| gravity | 14 | 14 | 1.000000 | 18.7% | 100.0% | 18.7% |
| numeral | 11 | 11 | 1.000000 | 14.7% | 100.0% | 14.7% |
| unit_conversion | 12 | 12 | 1.000000 | 16.0% | 100.0% | 16.0% |
