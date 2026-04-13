# Notebook parity report

- status: **mismatches_found**
- notebook: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2.ipynb`
- profile: `notebook-current`

## Core checks

| check | status | expected | actual | note |
| --- | --- | --- | --- | --- |
| train_csv | mismatch | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv` | `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_verifiedswap22_sym9_v1.csv` |  |
| type_samples | mismatch | `{'Numeral Conversion': 300, 'Gravitational Constant': 400, 'Unit Conversion': 700, 'Text Encryption': 700, 'Bit Manipulation': 1021, 'Equation Transformation': 200}` | `{'Numeral Conversion': 0, 'Gravitational Constant': 15, 'Unit Conversion': 15, 'Text Encryption': 15, 'Bit Manipulation': 26, 'Equation Transformation': 9}` |  |
| seed | aligned | `123` | `123` |  |
| batch_size | aligned | `1` | `1` |  |
| grad_accumulation_steps | aligned | `8` | `8` |  |
| num_epochs | mismatch | `2.0` | `0.8` |  |
| learning_rate | mismatch | `0.0001` | `1e-06` |  |
| lr_scheduler | aligned | `cosine` | `cosine_decay` | MLX cosine_decay is the notebook cosine equivalent. |
| warmup_ratio | aligned | `0.05` | `0.05` |  |
| optimizer_steps | mismatch | `832` | `8` | Notebook parity requires flushing grad accumulation at each epoch boundary, not only at the final global remainder. |
| max_seq_length | mismatch | `4096` | `1024` |  |
| logging_steps | aligned | `10 optimizer` | `10 optimizer` | HF logging_steps counts optimizer updates, not raw microsteps. |
| save_strategy | aligned | `no` | `0` | MLX save_every<=0 means final-only save, matching save_strategy='no'. |
| mask_prompt | aligned | `False` | `False` | HF notebook does not enable assistant_only_loss/completion_only_loss here; MLX parity should therefore keep mask_prompt=False. |
| lora_rank | aligned | `32` | `32` |  |
| lora_alpha | aligned | `32.0` | `32.0` |  |
| lora_dropout | aligned | `0.05` | `0.05` |  |

## LoRA target mapping

- status: **mismatch**
- required generic keys: `['mixer.down_proj', 'mixer.in_proj', 'mixer.out_proj', 'mixer.up_proj']`
- missing generic keys: `['mixer.down_proj', 'mixer.up_proj']`
- extra MLX equivalents: `['mixer.k_proj', 'mixer.o_proj', 'mixer.q_proj', 'mixer.shared_experts.down_proj', 'mixer.shared_experts.up_proj', 'mixer.v_proj']`
- note: MLX keys must cover the notebook's in/out/up/down projection intent; extra switch/shared-expert keys are intentional Nemotron-H MoE mappings.

## MLX scaffolding

- `valid_shadow_rows`: HF notebook has no validation loop; MLX uses a tiny shadow validation set only for observability.
- `steps_per_eval`: steps_per_eval<=0 resolves to total_iters so there are no intermediate validations.
- `lr_schedule_step_unit`: Optimizer-step scheduling is required for notebook parity under mlx_lm grad accumulation.
- `shadow_model`: MLX load path uses a patched shadow_model to avoid tokenizer/runtime mismatches.
- `tokenizer_special_tokens`: MLX training load normalizes eos_token_ids and sets pad_token=eos_token when absent, matching the HF log alignment to eos/pad token id 11.
- `final_grad_accumulation_flush`: MLX trainer is patched so the final partial accumulation matches notebook optimizer-step count.

## Clear omissions

- `['train_csv', 'type_samples', 'num_epochs', 'learning_rate', 'optimizer_steps', 'max_seq_length', 'lora_target_coverage']`
