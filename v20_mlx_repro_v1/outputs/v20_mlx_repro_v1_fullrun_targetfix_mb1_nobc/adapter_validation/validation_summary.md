# adapter_validation_stratified_category_300_of_950

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- benchmark_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/data/train.csv`
- model_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc/adapter`
- overall_accuracy: `0.846667` (254/300)
- max_tokens: `7680`
- max_num_seqs: `4`
- prompt_chunk_size: `4`
- prefill_batch_size: `4`
- completion_batch_size: `4`
- eval_enable_thinking: `True`
- append_boxed_instruction: `False`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 37 | 53 | 0.698113 | 17.7% | 69.8% | 12.3% |
| cipher | 50 | 51 | 0.980392 | 17.0% | 98.0% | 16.7% |
| cryptarithm_deduce | 0 | 23 | 0.000000 | 7.7% | 0.0% | 0.0% |
| cryptarithm_guess | 1 | 5 | 0.200000 | 1.7% | 20.0% | 0.3% |
| equation_numeric_deduce | 15 | 15 | 1.000000 | 5.0% | 100.0% | 5.0% |
| equation_numeric_guess | 0 | 2 | 0.000000 | 0.7% | 0.0% | 0.0% |
| gravity | 50 | 50 | 1.000000 | 16.7% | 100.0% | 16.7% |
| numeral | 47 | 47 | 1.000000 | 15.7% | 100.0% | 15.7% |
| unit_conversion | 54 | 54 | 1.000000 | 18.0% | 100.0% | 18.0% |
