# v20 corrective corpus v6 frontier crypt-ruleunknown-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_crypt_ruleunknown_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_crypt_ruleunknown_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_full.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` が繰り返し示す cryptarithm の弱点 **split / concat / operator-not-found** を、full budget 側でも正面から押す比較線
- current MLX `v4` partial 最大 miss band の **`cryptarithm_* / rule_unknown = 38`** を frontier-support 上でさらに heavier にし、bit / numeric frontier raw support を維持したまま crypt residual を削れるか試す

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
- surface_binary_structured_answer_only: 101
- surface_numeric_answer_only: 68
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 712

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
- surface_binary_structured_answer_only: 324
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 334
- easy_gravity_fragile: 22
- total repeated overlay rows: 2973

### Bundle footprint

- base examples: 7828
- overlay examples: 2973
- total examples: 10801
- total steps: 338
- total tokens: 28678263
- max sequence length: 7971

## Crypt rule-unknown heavy mix

- current `v4` partial の **38 rule_unknown crypt misses** を `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_IDS` として固定
- `surface_cryptarithm_answer_only` に対して `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2` を追加し、frontier-support の deduce-heavy + raw frontier の上へ unknown-operator crypt replay をさらに重ねる
- `surface_cryptarithm_answer_only` repeats は **`260 -> 334`**
- structured answer-only / numeric answer-only / frontier raw-support の unique mix は frontier-support full から不変

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **101 unique / 324 repeated**
- numeric support: **68 unique / 217 repeated**
- cryptarithm support: **48 unique / 334 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.3294`**
- cryptarithm share は **`0.0523`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.4940`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 2973`** で **`+74`**
- total tokens は **`28668072 -> 28678263`** で **`+10191`**
- 差分は `surface_cryptarithm_answer_only` の rule_unknown-focused extra repeat に限定される

## Interpretation before training

- full 版では structured support が already 厚いので、この branch の追加効果は **crypt residual だけをさらに削れるか** でほぼ判断できる
- 逆にここで gain が出ないなら、次の本命は crypt repeat ではなく bit hypothesis-formed 側へ寄せるべき

## Next evaluation gate

- `v20_mlx_v6_frontier_crypt_ruleunknown_heavy_full_mb1_nobc` を `...crypt_deduce_heavy_frontier_support` と measured diff-pack で比較し、**frontier-support stacked のまま crypt rule_unknown heavier が clean gain か** を見る
