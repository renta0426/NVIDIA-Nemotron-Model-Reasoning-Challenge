# submission_compat_audit

- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3/adapter`
- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- base_model_name_or_path: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`

## Tensor rank counts

| tensor_rank | tensor_count |
| ---: | ---: |
| 2 | 232 |

## Module family counts

| module_family | tensor_count |
| --- | ---: |
| `attention` | 48 |
| `mamba` | 92 |
| `shared_experts` | 92 |

## PEFT adapter_config preview

- peft_type: `LORA`
- base_model_name_or_path: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`
- r: `32`
- lora_alpha: `32.0`
- lora_dropout: `0.05`
- bias: `none`
- use_dora: `False`
- modules_to_save: `None`
- inference_mode: `True`
- target_modules: `['mixer.in_proj', 'mixer.out_proj', 'mixer.shared_experts.up_proj', 'mixer.shared_experts.down_proj', 'mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`
