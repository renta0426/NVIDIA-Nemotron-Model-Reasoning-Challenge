# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance-crypt-heavy results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...bit_family_rebalance_crypt_heavy.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- full budget の `bit_family_rebalance` を保ったまま、current 44 crypt misses にだけ heavier repeat を戻す upper-bound branch
- crypt を memorization 方向へ振り過ぎず、top miss slice への support mass 回復が bit gains を相殺しないかを測る

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
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 302
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 276
- easy_gravity_fragile: 22
- total repeated overlay rows: 2875

### Bundle footprint

- base examples: 7828
- overlay examples: 2875
- total examples: 10703
- total steps: 335
- total tokens: 28660238
- max sequence length: 7971

## Crypt-heavy mix

- `CRYPT_V4_PARTIAL_MISS_SUPPORT_BONUS_REPEAT = 3`
- current 44 crypt miss rows に対して `surface_short_closure_boost 44` と `surface_token_skill_boost 44` を追加
- `surface_cryptarithm_answer_only` repeats は `188 -> 276`
- binary rebalance 部分は base branch のまま維持 (`exact_rule_commit_boost 245`)

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **96 unique / 302 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 276 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.3146`**
- cryptarithm share は **`0.0434`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5048`**

## Delta vs full bit-family-rebalance base

- `...bit_family_rebalance` 比で overlay rows は `2787 -> 2875`
- total tokens は `28649430 -> 28660238` で **`+10808`**
- 増分は crypt miss 44 rows に対する extra boosts `+88`

## Interpretation before training

- full budget では `bit_family_rebalance` だけだと support share が `0.3055` に下がるため、crypt-heavy はその一部を crypt へ戻す保険線
- token 増分は still modest なので、bit gains が落ちず crypt だけ改善するなら next mainline 候補になりうる

## Next evaluation gate

- `...bit_family_rebalance_crypt_heavy` を `...bit_family_rebalance` と measured diff-pack で比較し、**full budget で crypt-heavy が top-two miss slice を同時に押せるか** を見る
