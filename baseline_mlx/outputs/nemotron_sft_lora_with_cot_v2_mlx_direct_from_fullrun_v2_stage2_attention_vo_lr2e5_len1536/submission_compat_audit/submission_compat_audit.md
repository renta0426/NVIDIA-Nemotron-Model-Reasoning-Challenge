# submission_compat_audit

- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_vo_lr2e5_len1536/adapter`
- audit_status: `blocked_routed_expert_3d_tensors`
- peft_export_ready: `False`
- base_model_name_or_path: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`

## Blocked reasons

- MLX adapter contains non-2D LoRA tensors; PEFT/vLLM-equivalent export is not claimed without a verified mapping.
- switch_mlp routed-expert tensors are 3D in this adapter, so the current single-file pipeline blocks submission export instead of guessing a PEFT layout.

## Tensor rank counts

| tensor_rank | tensor_count |
| ---: | ---: |
| 2 | 232 |
| 3 | 92 |

## Module family counts

| module_family | tensor_count |
| --- | ---: |
| `attention` | 48 |
| `mamba` | 92 |
| `shared_experts` | 92 |
| `switch_mlp` | 92 |

## Unsupported tensor examples

| key | shape |
| --- | --- |
| `backbone.layers.1.mixer.switch_mlp.fc1.lora_a` | `[128, 32, 2688]` |
| `backbone.layers.3.mixer.switch_mlp.fc1.lora_a` | `[128, 32, 2688]` |
| `backbone.layers.6.mixer.switch_mlp.fc1.lora_a` | `[128, 32, 2688]` |
| `backbone.layers.6.mixer.switch_mlp.fc2.lora_b` | `[128, 2688, 32]` |
| `backbone.layers.8.mixer.switch_mlp.fc1.lora_b` | `[128, 1856, 32]` |
| `backbone.layers.8.mixer.switch_mlp.fc1.lora_a` | `[128, 32, 2688]` |
| `backbone.layers.8.mixer.switch_mlp.fc2.lora_a` | `[128, 32, 1856]` |
| `backbone.layers.10.mixer.switch_mlp.fc1.lora_b` | `[128, 1856, 32]` |
| `backbone.layers.1.mixer.switch_mlp.fc2.lora_a` | `[128, 32, 1856]` |
| `backbone.layers.10.mixer.switch_mlp.fc2.lora_a` | `[128, 32, 1856]` |
| `backbone.layers.13.mixer.switch_mlp.fc1.lora_b` | `[128, 1856, 32]` |
| `backbone.layers.8.mixer.switch_mlp.fc2.lora_b` | `[128, 2688, 32]` |

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
- target_modules: `['mixer.in_proj', 'mixer.out_proj', 'mixer.switch_mlp.fc1', 'mixer.switch_mlp.fc2', 'mixer.shared_experts.up_proj', 'mixer.shared_experts.down_proj', 'mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`
