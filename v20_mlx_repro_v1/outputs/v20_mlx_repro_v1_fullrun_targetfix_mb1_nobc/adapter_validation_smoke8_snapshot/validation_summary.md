# adapter_validation_stratified_category_8_of_950

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- benchmark_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/data/train.csv`
- model_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc/adapter`
- overall_accuracy: `0.75` (6/8)
- max_tokens: `7680`
- max_num_seqs: `16`
- prompt_chunk_size: `16`
- prefill_batch_size: `8`
- completion_batch_size: `8`
- eval_enable_thinking: `True`
- append_boxed_instruction: `False`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 1 | 2 | 0.500000 | 25.0% | 50.0% | 12.5% |
| cipher | 1 | 1 | 1.000000 | 12.5% | 100.0% | 12.5% |
| cryptarithm_deduce | 0 | 1 | 0.000000 | 12.5% | 0.0% | 0.0% |
| gravity | 1 | 1 | 1.000000 | 12.5% | 100.0% | 12.5% |
| numeral | 1 | 1 | 1.000000 | 12.5% | 100.0% | 12.5% |
| unit_conversion | 2 | 2 | 1.000000 | 25.0% | 100.0% | 25.0% |
