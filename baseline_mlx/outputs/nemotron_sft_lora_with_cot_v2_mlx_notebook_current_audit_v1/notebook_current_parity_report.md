# Notebook current parity report

- status: **no_clear_omissions**
- notebook: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2.ipynb`
- profile: `notebook-current`

## Core checks

| check | status | expected | actual | note |
| --- | --- | --- | --- | --- |
| train_csv | aligned | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv` | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv` |  |
| type_samples | aligned | `{'Numeral Conversion': 300, 'Gravitational Constant': 400, 'Unit Conversion': 700, 'Text Encryption': 700, 'Bit Manipulation': 1021, 'Equation Transformation': 200}` | `{'Numeral Conversion': 300, 'Gravitational Constant': 400, 'Unit Conversion': 700, 'Text Encryption': 700, 'Bit Manipulation': 1021, 'Equation Transformation': 200}` |  |
| seed | aligned | `123` | `123` |  |
| batch_size | aligned | `1` | `1` |  |
| grad_accumulation_steps | aligned | `8` | `8` |  |
| num_epochs | aligned | `2.0` | `2.0` |  |
| learning_rate | aligned | `0.0001` | `0.0001` |  |
| lr_scheduler | aligned | `cosine` | `cosine_decay` | MLX cosine_decay is the notebook cosine equivalent. |
| warmup_ratio | aligned | `0.05` | `0.05` |  |
| max_seq_length | aligned | `4096` | `4096` |  |
| logging_steps | aligned | `10` | `10` |  |
| save_strategy | aligned | `no` | `0` | MLX save_every<=0 means final-only save, matching save_strategy='no'. |
| lora_rank | aligned | `32` | `32` |  |
| lora_alpha | aligned | `32.0` | `32.0` |  |
| lora_dropout | aligned | `0.05` | `0.05` |  |

## LoRA target mapping

- status: **aligned**
- required generic keys: `['mixer.down_proj', 'mixer.in_proj', 'mixer.out_proj', 'mixer.up_proj']`
- missing generic keys: `[]`
- extra MLX equivalents: `['mixer.shared_experts.down_proj', 'mixer.shared_experts.up_proj', 'mixer.switch_mlp.fc1', 'mixer.switch_mlp.fc2']`
- note: MLX keys must cover the notebook's in/out/up/down projection intent; extra switch/shared-expert keys are intentional Nemotron-H MoE mappings.

## MLX scaffolding

- `valid_shadow_rows`: HF notebook has no validation loop; MLX uses a tiny shadow validation set only for observability.
- `steps_per_eval`: steps_per_eval<=0 resolves to total_iters so there are no intermediate validations.
- `lr_schedule_step_unit`: Optimizer-step scheduling is required for notebook parity under mlx_lm grad accumulation.
- `shadow_model`: MLX load path uses a patched shadow_model to avoid tokenizer/runtime mismatches.
- `final_grad_accumulation_flush`: MLX trainer is patched so the final partial accumulation matches notebook optimizer-step count.

## Clear omissions

- none
