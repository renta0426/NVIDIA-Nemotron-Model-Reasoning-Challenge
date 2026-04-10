# train_split_with_cot_v3f_one_shot_repair_v1

## Purpose

This CSV is a single-shot training set intended to beat `v3f` without changing the base full-run recipe more than necessary.

The design follows:

1. keep `v3f` broad sampled trunk
2. add binary/symbol corrective rows from verified blind spots
3. add text-heavy repair rows that preserve global character-mapping behavior
4. avoid coarse route-closure rows as the main signal

## Source files

1. `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv`
2. `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_stagefreeze_stage2_corrective_v1.csv`
3. `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified140_binary30proxyo15p5s10_grav15_unit15_rowselect_v1.csv`

## Construction

Base sample counts were materialized with seed `123`:

| type | base rows |
| --- | ---: |
| `Numeral Conversion` | `300` |
| `Gravitational Constant` | `400` |
| `Unit Conversion` | `700` |
| `Text Encryption` | `700` |
| `Bit Manipulation` | `1021` |
| `Equation Transformation` | `200` |

Additional rows:

1. `stage2_corrective_v1`: `218` rows
   - `Bit Manipulation = 209`
   - `Equation Transformation = 9`
   - route-surface lines were stripped or softened before merge
2. `stage25_text_verified140_binary30...`: `170` rows kept
   - `Text Encryption = 140`
   - `Bit Manipulation = 30`
   - `Gravitational Constant` and `Unit Conversion` rows from that file were intentionally excluded to avoid unnecessary easy-family drift

## Final counts

| type | final rows |
| --- | ---: |
| `Numeral Conversion` | `300` |
| `Gravitational Constant` | `400` |
| `Unit Conversion` | `700` |
| `Text Encryption` | `840` |
| `Bit Manipulation` | `1260` |
| `Equation Transformation` | `209` |
| **total** | **`3709`** |

## Intended notebook pairing

Use with:

`cuda-train-data-analysis-v1/proof_first_solver_factory_routing/nemotron-sft-lora-with-cot-v3f-one-shot-repair-v1.ipynb`

That notebook keeps the original v2 full-run recipe but changes:

1. training CSV path
2. type counts to match this prematerialized dataset
3. boxed-only fallback so valid answer-only rows are not dropped

## Score record

Not yet measured in this repository state.

When the run completes, append at least:

1. local320 score
2. leaderboard proxy score
3. specialized563 score
4. Kaggle leaderboard score