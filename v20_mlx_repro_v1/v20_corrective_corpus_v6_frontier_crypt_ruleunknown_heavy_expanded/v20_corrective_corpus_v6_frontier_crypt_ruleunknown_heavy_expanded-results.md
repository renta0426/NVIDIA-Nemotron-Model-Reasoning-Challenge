# v20 corrective corpus v6 frontier crypt-ruleunknown-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_crypt_ruleunknown_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_crypt_ruleunknown_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_crypt_ruleunknown_heavy_expanded.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は cryptarithm の律速を **split / concat weakness** と見ており、特に deduce/guess の `operator not found` 側を leaderboard で取り切れていない
- current MLX `v4` partial でも最大の塊は **`cryptarithm_deduce/rule_unknown 33` + `cryptarithm_guess/rule_unknown 5` = 38 misses** なので、frontier-support の上に **rule_unknown-only heavier repeat** を重ねる stacked branch にした

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
- surface_cryptarithm_answer_only: 334
- easy_gravity_fragile: 22
- total repeated overlay rows: 2877

### Bundle footprint

- base examples: 7828
- overlay examples: 2877
- total examples: 10705
- total steps: 335
- total tokens: 28649227
- max sequence length: 7971

## Crypt rule-unknown heavy mix

- current `v4` partial の **38 rule_unknown crypt misses** を `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_IDS` として固定
- `surface_cryptarithm_answer_only` に対して `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2` を追加し、frontier-support の crypt deduce pressure の上にさらに rule_unknown を重ねる
- この 38 IDs は deduce/guess の `operator not found` 側だけに寄っており、README の concat / reverse-concat 仮説と整合する
- `surface_cryptarithm_answer_only` repeats は **`260 -> 334`**

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **69 unique / 228 repeated**
- numeric support: **68 unique / 217 repeated**
- cryptarithm support: **48 unique / 334 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.3054`**
- cryptarithm share は **`0.0541`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5116`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2877`** で **`+74`**
- total tokens は **`28639036 -> 28649227`** で **`+10191`**
- 差分はほぼ `surface_cryptarithm_answer_only` の rule_unknown-focused extra repeat だけで、bit / numeric frontier raw support は据え置き

## Interpretation before training

- これは frontier-support を維持したまま、**cryptarithm の `rule_unknown` failure band を heavier replay で押す** branch
- unknown-operator crypt が本当に current bottleneck なら、frontier-support 単独よりも crypt residual を削れるはず

## Next evaluation gate

- `v20_mlx_v6_frontier_crypt_ruleunknown_heavy_expanded_mb1_nobc` を `...crypt_deduce_heavy_frontier_support` と measured diff-pack で比較し、**unrecommended frontier support を維持したまま crypt rule_unknown を heavier にする価値があるか** を見る
