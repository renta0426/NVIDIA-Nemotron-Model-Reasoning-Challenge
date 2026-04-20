# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance-crypt-deduce-heavy-frontier-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...bit_family_rebalance_crypt_deduce_heavy_frontier_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- Competition README が許容する **data filtering / curation** の一環として、`train_recommended_learning_target_v1.csv` から外れている raw frontier を small support lane として再導入する branch
- `A-Open-ProgressPrizePublication/README.md` が強調する **bit_manipulation** と **equation** の hard slice に合わせ、current partial で実際に落ちている unrecommended miss `0ec17d2e` (bit, `rule_unknown`) と `00d8b3db` (numeric deduce, `hypothesis_formed`) を mandatory にしつつ、同じ未推奨 pool から少量 fill する

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
- surface_binary_structured_answer_only: 69
- surface_numeric_answer_only: 68
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 680

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
- surface_binary_structured_answer_only: 228
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 260
- easy_gravity_fragile: 22
- total repeated overlay rows: 2803

### Bundle footprint

- base examples: 7828
- overlay examples: 2803
- total examples: 10631
- total steps: 333
- total tokens: 28639036
- max sequence length: 7971

## Frontier raw-support mix

- `surface_binary_structured_answer_only` に **`+5 unique slots`**、`surface_numeric_answer_only` に **`+4 unique slots`** を追加
- selected frontier raw support は **9 unique rows** で、内訳は `problem_status_rule_unknown 7` と `problem_status_hypothesis_formed 2`
- current partial unrecommended misses **`0ec17d2e`** と **`00d8b3db`** は `current_frontier_miss_support` として mandatory で含める
- repeat は `FRONTIER_RAW_SUPPORT_BONUS_REPEAT = 1`、current miss 2 件には `FRONTIER_RAW_CURRENT_MISS_EXTRA_REPEAT = 2` を追加
- `surface_binary_structured_answer_only` repeats は `206 -> 228`、`surface_numeric_answer_only` repeats は `199 -> 217`

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **69 unique / 228 repeated**
- numeric support: **68 unique / 217 repeated**
- cryptarithm support: **48 unique / 260 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.2966`**
- cryptarithm share は **`0.0421`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5181`**

## Delta vs expanded crypt-deduce-heavy base

- `...crypt_deduce_heavy` 比で unique rows は `671 -> 680`
- overlay rows は `2763 -> 2803`
- total tokens は `28629224 -> 28639036` で **`+9812`**
- 増分は unrecommended frontier raw-support 9 rows の追加と extra repeat に対応する

## Interpretation before training

- `crypt_deduce_heavy` の deduce-only crypt push を保ったまま、**curated target table の外にある residual miss frontier** を raw answer-only で薄く拾う branch
- 過度な overfit を避けるため small fill に留めており、これで `0ec17d2e` / `00d8b3db` のような frontier を cheap に回収できるかを測る

## Next evaluation gate

- `...crypt_deduce_heavy_frontier_support` を `...crypt_deduce_heavy` と measured diff-pack で比較し、**unrecommended frontier raw-support が bit/numeric frontier を拾うか、それとも単なる memorization ノイズに終わるか** を見る
