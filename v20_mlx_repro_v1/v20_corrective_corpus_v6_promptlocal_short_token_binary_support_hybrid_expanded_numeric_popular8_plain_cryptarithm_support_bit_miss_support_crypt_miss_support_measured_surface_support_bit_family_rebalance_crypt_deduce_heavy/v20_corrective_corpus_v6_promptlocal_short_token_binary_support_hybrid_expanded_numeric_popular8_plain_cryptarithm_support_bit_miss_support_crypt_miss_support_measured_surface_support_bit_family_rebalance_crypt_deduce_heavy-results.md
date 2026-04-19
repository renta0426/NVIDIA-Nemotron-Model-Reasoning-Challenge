# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance-crypt-deduce-heavy results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...bit_family_rebalance_crypt_deduce_heavy.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `bit_family_rebalance` の binary push を保ちつつ、README 上の次律速である **cryptarithm** のうち live partial で支配的な `cryptarithm_deduce 36 miss` だけへ heavier repeat を戻す branch
- `cryptarithm_guess 8 miss` は unique coverage のまま残し、**guess rows まで盛る価値があるか** を `crypt_heavy` と切り分ける sibling ablation

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
- surface_cryptarithm_answer_only: 260
- easy_gravity_fragile: 22
- total repeated overlay rows: 2763

### Bundle footprint

- base examples: 7828
- overlay examples: 2763
- total examples: 10591
- total steps: 332
- total tokens: 28629224
- max sequence length: 7971

## Crypt-deduce-heavy mix

- `CRYPT_V4_PARTIAL_MISS_SUPPORT_BONUS_REPEAT = 1` を維持しつつ、`CRYPT_V4_PARTIAL_DEDUCE_MISS_EXTRA_REPEAT = 2` を `cryptarithm_deduce 36 ids` にだけ追加
- current 44 crypt miss rows のうち deduce 36 件だけに `surface_short_closure_boost 36` と `surface_token_skill_boost 36` を追加
- `surface_cryptarithm_answer_only` repeats は `188 -> 260`
- `surface_boxed_tail_boost 44` は base branch のまま維持し、guess 8 件には extra repeat を載せない

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **64 unique / 206 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 260 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.2879`**
- cryptarithm share は **`0.0426`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5245`**

## Delta vs expanded bit-family-rebalance base

- `...bit_family_rebalance` 比で overlay rows は `2691 -> 2763`
- total tokens は `28620394 -> 28629224` で **`+8830`**
- 増分は `cryptarithm_deduce 36 ids * extra 2 repeats = +72 rows` に対応し、`crypt_heavy (+88 rows)` より一段軽い

## Interpretation before training

- これは `bit_family_rebalance` の binary push を保ちながら、crypt support の extra mass を **dominant deduce slice** に絞る branch
- `crypt_heavy` より token 増分が小さいので、guess-side memorization cost を避けつつ deduce だけ改善できるなら本命になりうる

## Next evaluation gate

- `...bit_family_rebalance_crypt_deduce_heavy` を `...bit_family_rebalance` と `...bit_family_rebalance_crypt_heavy` の両方と measured diff-pack で比較し、**guess まで盛らずに deduce だけ押した方が高EVか** を見る
