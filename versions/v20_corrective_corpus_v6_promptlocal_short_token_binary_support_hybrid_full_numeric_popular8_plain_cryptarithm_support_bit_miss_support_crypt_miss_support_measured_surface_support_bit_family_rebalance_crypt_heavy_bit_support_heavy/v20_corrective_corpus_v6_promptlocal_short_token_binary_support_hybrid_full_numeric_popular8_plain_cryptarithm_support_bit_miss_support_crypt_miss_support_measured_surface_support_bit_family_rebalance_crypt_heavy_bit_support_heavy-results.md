# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance-crypt-heavy-bit-support-heavy results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bit_support_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...bit_family_rebalance_crypt_heavy_bit_support_heavy.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- full budget の `bit_family_rebalance_crypt_heavy` に対して、support-side bit misses 17 rows へだけ extra repeat を戻す upper-bound branch
- exact rebalance / crypt repair の両方を維持しながら、bit support lane が薄すぎて失点するケースを小コストで補う

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
- surface_binary_structured_answer_only: 96
- surface_numeric_answer_only: 64
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 703

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
- surface_binary_structured_answer_only: 330
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 276
- easy_gravity_fragile: 22
- total repeated overlay rows: 2909

### Bundle footprint

- base examples: 7828
- overlay examples: 2909
- total examples: 10737
- total steps: 336
- total tokens: 28670236
- max sequence length: 7971

## Bit-support-heavy mix

- `BIT_V4_PARTIAL_MISS_SUPPORT_BONUS_REPEAT = 3`
- selected bit miss support rows 17 件に対して `surface_short_closure_boost` / `surface_token_skill_boost` をさらに追加
- `surface_binary_prompt_local_answer_only` repeats は `291 -> 297`
- `surface_binary_structured_answer_only` repeats は `302 -> 330`
- crypt-heavy 部分も維持し、`surface_cryptarithm_answer_only` repeats は `276`

## Support budget

- prompt-local support: **96 unique / 297 repeated**
- structured support: **96 unique / 330 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 276 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.3229`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.4987`**

## Delta vs full bit-family-rebalance-crypt-heavy base

- `...bit_family_rebalance_crypt_heavy` 比で overlay rows は `2875 -> 2909`
- total tokens は `28660238 -> 28670236` で **`+9998`**
- 増分は selected bit miss support 17 rows に対する extra boosts `+34`

## Interpretation before training

- full budget では `crypt_heavy` で戻した support shareをさらに少し押し上げる **small hedge branch**
- bit exact / crypt support / bit support の 3 点を同時に押す構成なので、hidden 側でどこが律速でも最小限の保険にはなる

## Next evaluation gate

- `...bit_family_rebalance_crypt_heavy_bit_support_heavy` を `...bit_family_rebalance_crypt_heavy` と measured diff-pack で比較し、**3-way hedge が full budget で有効か** を見る
