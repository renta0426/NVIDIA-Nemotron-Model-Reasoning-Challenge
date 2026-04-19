# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance-crypt-heavy-bit-support-heavy results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...bit_family_rebalance_crypt_heavy_bit_support_heavy.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `bit_family_rebalance_crypt_heavy` の top-2 miss slice pushを維持したまま、current bit misses のうち support lane に入っている 17 rows にだけ extra repeat を戻す branch
- README が強調する bit 主戦場に対して、exact rebalance と crypt repair を保ったまま **bit support-side misses** の保険を掛ける

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
- surface_binary_prompt_local_answer_only: 297
- surface_binary_structured_answer_only: 234
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 276
- easy_gravity_fragile: 22
- total repeated overlay rows: 2813

### Bundle footprint

- base examples: 7828
- overlay examples: 2813
- total examples: 10641
- total steps: 333
- total tokens: 28641200
- max sequence length: 7971

## Bit-support-heavy mix

- `BIT_V4_PARTIAL_MISS_SUPPORT_BONUS_REPEAT = 3`
- selected bit miss support rows 17 件に対して `surface_short_closure_boost` / `surface_token_skill_boost` をさらに追加
- `surface_binary_prompt_local_answer_only` repeats は `291 -> 297`
- `surface_binary_structured_answer_only` repeats は `206 -> 234`
- crypt-heavy 部分も維持し、`surface_cryptarithm_answer_only` repeats は `276`

## Support budget

- prompt-local support: **96 unique / 297 repeated**
- structured support: **64 unique / 234 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 276 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.2986`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5167`**

## Delta vs expanded bit-family-rebalance-crypt-heavy base

- `...bit_family_rebalance_crypt_heavy` 比で overlay rows は `2779 -> 2813`
- total tokens は `28631202 -> 28641200` で **`+9998`**
- 増分は selected bit miss support 17 rows に対する extra boosts `+34` に一致する

## Interpretation before training

- これは `bit_family_rebalance_crypt_heavy` の上に積む **small hedge branch**
- top-2 miss slice を保ったまま support-side bit misses にだけ少量の extra mass を戻すので、bit exact rebalance が answer-surface を削りすぎる場合の保険になる

## Next evaluation gate

- `...bit_family_rebalance_crypt_heavy_bit_support_heavy` を `...bit_family_rebalance_crypt_heavy` と measured diff-pack で比較し、**bit/crypt 同時押しを維持したまま support-side bit misses が減るか** を見る
