# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...measured_surface_support_bit_family_rebalance.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `README.md` / `A-Open-ProgressPrizePublication/README.md` が強調する **bit_manipulation 主戦場** に合わせ、measured-surface-support の上で binary exact lane 自体を miss-heavy family へ再配分する branch
- current partial bit misses 18 件は `choose(shl,shr,rol) / majority(ror,shl,shr) / majority(rol,shl,shr) / binary_prompt_local_stage2_unique_exact` に偏っており、`xor(shl,shr)` へ寄り過ぎた exact lane をほどいて family reweight する

## Dataset composition

### Unique rows

- binary_structured_exact_core: 152
- binary_logic_exact: 56
- binary_permutation_exact: 40
- binary_prompt_local_exact: 95
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- surface_binary_prompt_local_answer_only: 96
- surface_binary_structured_answer_only: 64
- surface_numeric_answer_only: 64
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 671

### Repeated training rows

- binary_structured_exact_core: 768
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 475
- surface_numeral_boxed: 102
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 206
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 22
- total repeated overlay rows: 2691

### Bundle footprint

- base examples: 7828
- overlay examples: 2691
- total examples: 10519
- total steps: 330
- total tokens: 28620394
- max sequence length: 7971

## Bit-family rebalance

- structured family target counts:
  - `choose(shl,shr,rol) 24`
  - `majority(ror,shl,shr) 22`
  - `majority(rol,shl,shr) 22`
  - `choose(shl,shr,ror) 20`
  - `choose(shl,shr,nibble_swap) 10`
  - `or(rol,shl) 8`
  - `or(rol,shr) 6`
  - `xor(ror,shl) 4`
  - `or(ror,shr) 2`
  - `xor(shl,shr) 32`
- mandatory anchors により `choose(ror,nibble_swap,shl) 1` と `choose(rol,ror,shr) 1` も保持
- selected structured family countsは target どおりで、base の `xor(shl,shr) 58` を **32** まで圧縮した
- prompt-local exact は `binary_prompt_local_stage2_unique_exact` **95 rows** を維持し、family-wide repeat bonus を追加

## Repeat mix

- binary rebalance bonus により `exact_rule_commit_boost` が **245** rows 追加
- `binary_structured_exact_core` repeats は `618 -> 768`
- `binary_prompt_local_exact` repeats は `380 -> 475`
- `surface_boxed_tail_boost` は measured-surface base と同じ **76 rows**

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **64 unique / 206 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- overlay token share は prompt-local `0.1119`、structured `0.0841`、numeric `0.0377`、cryptarithm `0.0319`、cipher `0.0042`、unit `0.0042`、gravity `0.0059`
- combined measured-support share は **`0.2799`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5304`**

## Delta vs expanded measured-surface-support base

- `...measured_surface_support` 比で overlay rows は `2446 -> 2691`
- total tokens は `28536458 -> 28620394` で **`+83936`**
- 増分はほぼ binary exact lane の repeat bonus (`+150 structured +95 prompt-local = +245`) に由来する
- unique rows は同じ `671` のままなので、これは **selection rebalance + repeat reweight** の branch

## Interpretation before training

- bit miss family に対しては `bit_exact_replay` よりはるかに mass が大きく、teacher-correct pool も十分ある
- 一方で support share は base `0.3116` から `0.2799` へ下がるため、surface gains を崩さず binary exact を押し戻せるかが焦点になる

## Next evaluation gate

- `...measured_surface_support_bit_family_rebalance` を `...measured_surface_support` と measured diff-pack で比較し、**bit family rebalance が crypt/surface を壊さず bit slice を押せるか** を見る
