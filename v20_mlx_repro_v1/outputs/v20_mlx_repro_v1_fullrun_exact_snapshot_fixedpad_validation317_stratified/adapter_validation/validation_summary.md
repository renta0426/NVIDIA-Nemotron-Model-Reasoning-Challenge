# adapter_validation_stratified_category_317_of_950

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- benchmark_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/data/train.csv`
- model_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_exact_snapshot_fixedpad/adapter`
- overall_accuracy: `0.157729` (50/317)
- max_tokens: `7680`
- max_num_seqs: `4`
- prompt_chunk_size: `4`
- prefill_batch_size: `4`
- completion_batch_size: `4`
- eval_enable_thinking: `True`
- append_boxed_instruction: `False`

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
