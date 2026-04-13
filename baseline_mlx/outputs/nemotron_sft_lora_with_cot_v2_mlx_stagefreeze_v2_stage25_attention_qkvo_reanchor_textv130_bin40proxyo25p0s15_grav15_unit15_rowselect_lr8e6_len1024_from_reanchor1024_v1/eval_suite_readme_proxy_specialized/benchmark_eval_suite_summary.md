# benchmark_eval_suite

- benchmark_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/phase0_offline_eval/artifacts`
- model_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo25p0s15_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo25p0s15_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/adapter`

| evaluation_name | rows | correct | accuracy | output_root |
| --- | ---: | ---: | ---: | --- |
| `readme_local320` | 320 | 225 | 0.7031 | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo25p0s15_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/readme_local320` |
| `leaderboard_proxy_v1_set` | 200 | 124 | 0.6200 | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo25p0s15_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set` |
