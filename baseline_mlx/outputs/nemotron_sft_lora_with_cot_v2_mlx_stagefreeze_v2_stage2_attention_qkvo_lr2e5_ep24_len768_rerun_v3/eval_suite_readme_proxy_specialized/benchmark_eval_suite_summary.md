# benchmark_eval_suite

- benchmark_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/mac_workspace/v1/reference/baseline/cot/phase0_offline_eval/artifacts`
- model_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3/adapter`

| evaluation_name | rows | correct | accuracy | output_root |
| --- | ---: | ---: | ---: | --- |
| `readme_local320` | 320 | 218 | 0.6813 | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3/eval_suite_readme_proxy_specialized/readme_local320` |
| `leaderboard_proxy_v2` | 84 | 33 | 0.3929 | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3/eval_suite_readme_proxy_specialized/leaderboard_proxy_v2` |
| `binary_bias_specialized_set` | 563 | 158 | 0.2806 | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3/eval_suite_readme_proxy_specialized/binary_bias_specialized_set` |
