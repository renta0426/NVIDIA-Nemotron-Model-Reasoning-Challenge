# v8_parallel_variants results

## Why v8 exists

- Root `README.md` fixes the evaluation contract at `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, and `max_model_len=8192`.
- `v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc` remains the retained MLX best at `254/300 = 0.846667`.
- Residual non-crypt misses are still concentrated in bit manipulation (`16`), cipher (`1`), and equation numeric guess (`2`).
- v7 already attacks the exact 19 miss IDs. v8 broadens the support mix with three complementary bundles from one single-file generator.

## Variant overview

| Variant | Overlay examples | Total steps | Total tokens | Bundle |
| --- | ---: | ---: | ---: | ---: |
| `bit_family_rebalance_broadbase` | 1626 | 296 | 28427151 | 247.75 MB |
| `symbol_cipher_recovery_mix` | 2423 | 321 | 28469263 | 248.39 MB |
| `hybrid_bridge` | 1710 | 299 | 28329344 | 246.91 MB |

## bit_family_rebalance_broadbase

Miss-family bit rebalance plus prompt-local support. Directly repeats the 19 known non-crypt misses, then broadens to verified/answer-only rows from the same bit abstract families and bit_prompt_local_exact_formula pool.

### Bundle stats

| Field | Value |
| --- | ---: |
| Base examples | 7828 |
| Overlay examples | 1626 |
| Total examples | 9454 |
| Base steps | 245 |
| Overlay steps | 51 |
| Total steps | 296 |
| Total tokens | 28427151 |
| Max sequence length | 7971 |
| Bundle size | 247.75 MB |
| Direct teacher-match IDs | 3 |

### Variant spec

| Knob | Value |
| --- | ---: |
| direct_answer_only_repeats | 24 |
| direct_reasoning_repeats | 8 |
| bit_verified_repeats | 4 |
| bit_answer_only_repeats | 2 |
| prompt_local_verified_repeats | 2 |
| prompt_local_answer_only_repeats | 1 |
| numeric_common_repeats | 0 |
| numeric_rare_repeats | 0 |
| cipher_verified_repeats | 0 |
| cipher_answer_only_repeats | 0 |

### Overlay by lane

| Lane | Examples |
| --- | ---: |
| bit_family_support | 866 |
| bit_prompt_local_support | 280 |
| direct_miss | 480 |

### Overlay by category

| Category | Examples |
| --- | ---: |
| bit_manipulation | 1546 |
| symbol_equation | 48 |
| text_decryption | 32 |

### Overlay by style

| Style | Examples |
| --- | ---: |
| answer_only | 1602 |
| reasoning | 24 |

### Bundle path

`A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/bit_family_rebalance_broadbase_bundle.jsonl`

### Status

- Bundle generated: YES
- MLX training: `v20_mlx_v8_bit_family_rebalance_broadbase_mlxdir_mb1_nobc_ckpt20` is now running under `v20_mlx_repro_v1/outputs/v8/` with detached supervisor, checkpoint cap (`save_every_steps=20`, `max_saved_checkpoints=3`), and README-style local300 watcher armed (`step 10` observed after manifest fix; first checkpoint not yet reached)
- local300 score: TBD

## symbol_cipher_recovery_mix

Keep direct miss pressure, then add broad answer-only stabilization for numeric_2x2 same-op-zero rows and the full text_decryption family.

### Bundle stats

| Field | Value |
| --- | ---: |
| Base examples | 7828 |
| Overlay examples | 2423 |
| Total examples | 10251 |
| Base steps | 245 |
| Overlay steps | 76 |
| Total steps | 321 |
| Total tokens | 28469263 |
| Max sequence length | 7971 |
| Bundle size | 248.39 MB |
| Direct teacher-match IDs | 3 |

### Variant spec

| Knob | Value |
| --- | ---: |
| direct_answer_only_repeats | 32 |
| direct_reasoning_repeats | 10 |
| bit_verified_repeats | 0 |
| bit_answer_only_repeats | 0 |
| prompt_local_verified_repeats | 0 |
| prompt_local_answer_only_repeats | 0 |
| numeric_common_repeats | 2 |
| numeric_rare_repeats | 1 |
| cipher_verified_repeats | 1 |
| cipher_answer_only_repeats | 1 |

### Overlay by lane

| Lane | Examples |
| --- | ---: |
| cipher_support | 1575 |
| direct_miss | 638 |
| numeric_same_op_zero_support | 210 |

### Overlay by category

| Category | Examples |
| --- | ---: |
| bit_manipulation | 532 |
| symbol_equation | 274 |
| text_decryption | 1617 |

### Overlay by style

| Style | Examples |
| --- | ---: |
| answer_only | 2393 |
| reasoning | 30 |

### Bundle path

`A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/symbol_cipher_recovery_mix_bundle.jsonl`

### Status

- Bundle generated: YES
- MLX training: NOT YET STARTED
- launch note: held back for now because concurrent `v7 + v8` runs leave only ~9% free system memory, while both observed MLX runs report ~221.94 GB peak memory; a detached queue will auto-launch this variant once one active run finishes
- local300 score: TBD

## hybrid_bridge

Balanced bridge run: moderate direct miss repeats, lighter bit-family rebalance, numeric same-op-zero support, and verified text_decryption answer-only stabilization.

### Bundle stats

| Field | Value |
| --- | ---: |
| Base examples | 7828 |
| Overlay examples | 1710 |
| Total examples | 9538 |
| Base steps | 245 |
| Overlay steps | 54 |
| Total steps | 299 |
| Total tokens | 28329344 |
| Max sequence length | 7971 |
| Bundle size | 246.91 MB |
| Direct teacher-match IDs | 3 |

### Variant spec

| Knob | Value |
| --- | ---: |
| direct_answer_only_repeats | 20 |
| direct_reasoning_repeats | 6 |
| bit_verified_repeats | 2 |
| bit_answer_only_repeats | 1 |
| prompt_local_verified_repeats | 1 |
| prompt_local_answer_only_repeats | 1 |
| numeric_common_repeats | 1 |
| numeric_rare_repeats | 1 |
| cipher_verified_repeats | 1 |
| cipher_answer_only_repeats | 0 |

### Overlay by lane

| Lane | Examples |
| --- | ---: |
| bit_family_support | 433 |
| bit_prompt_local_support | 140 |
| cipher_support | 605 |
| direct_miss | 398 |
| numeric_same_op_zero_support | 134 |

### Overlay by category

| Category | Examples |
| --- | ---: |
| bit_manipulation | 905 |
| symbol_equation | 174 |
| text_decryption | 631 |

### Overlay by style

| Style | Examples |
| --- | ---: |
| answer_only | 1692 |
| reasoning | 18 |

### Bundle path

`A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/hybrid_bridge_bundle.jsonl`

### Status

- Bundle generated: YES
- MLX training: NOT YET STARTED
- launch note: held back for now because concurrent `v7 + v8` runs leave only ~9% free system memory, while both observed MLX runs report ~221.94 GB peak memory; a detached queue will auto-launch this variant once a later slot opens
- local300 score: TBD

## Generated

2026-04-23T14:42:37Z
