# V1 Results

## Source of truth

この `v1` 系列のローカル判定も **`README.md` の Evaluation 節**を唯一の基準にする。

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

metric は **`\boxed{}` 優先抽出 → heuristic fallback → last numeric fallback** を使う。

## Reproduced prompt-router-v6 bundle

- single-file main: `mac_workspace/v1/phase2_binary_dsl_mlx_v1.py`
- local reference bundle: `mac_workspace/v1/reference/`
  - `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_training_data.csv`
  - `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`
  - `baseline/cot/phase0_offline_eval/artifacts/*`
  - `baseline/cot/phase2_1_2_merge_lora/artifacts/phase2_1_2_binary_specialist_training_data.csv`
  - `baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_training_data.csv`
  - `cuda-train-data-analysis-v1/artifacts/` の prompt-local / symbol solver / benchmark build に必要な CSV 群
- reproduced eval outputs: `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/`

## Current best local pipeline

| pipeline | local320 | gate24 | binary | gravity | roman | symbol | text | unit | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `prompt-router-v6-repro` | **293/320 = 0.9156** | **24/24 = 1.0000** | `54/60` | `50/50` | `50/50` | `39/60` | `50/50` | `50/50` | `v1` single-file + local reference bundle から actual rerun で `v0` score を再現 |

補足:

- `v1` rerun は `v0` の 3 adapter を入力として使い、**`v0` actual と完全一致**した。
  - general: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_resume_v10_to_full_fusion_v40_lr1p25e6_ep0125/adapter`
  - reasoning: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_text_run3_lr2e5_top8_bs16ga1/adapter`
  - specialist: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_focus_v1_text_full_bs16ga1/adapter`
- full320 fallback は **47 行すべて solver**
  - `binary_formula_consensus_solver = 35`
  - `symbol_numeric_zero_error_solver = 12`
- binary は **`54/60`**、内訳は `bit_other = 40/46`, `bit_structured_byte_formula = 14/14`
- symbol は `numeric_2x2 = 39/40`, `glyph_len5 = 0/20`
- artifact source of truth:
  - `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/gate24/phase0_offline_eval/artifacts/phase0_eval_summary.json`
  - `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/full320_shard2/phase0_offline_eval/artifacts/phase0_eval_summary.json`
