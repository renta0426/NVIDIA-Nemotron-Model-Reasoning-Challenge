# v20 corrective corpus v6 frontier sext-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_frontier_sext_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_sext_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_sext_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_sext_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_sext_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README が示す本命 2 軸 **bit manipulation** と **cryptarithm** を、full support budget 側で同時に重ねる比較線
- さらに current `v4` partial residual で残る **`cryptarithm_deduce hypothesis 4`** と **`bit tail 6`** も上乗せし、未特化 tail をほぼ全回収する

## Dataset composition

### Unique rows

- total unique overlay problems: 712
- unique bucket mix は frontier-support full と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 364
- surface_numeric_answer_only: 227
- surface_cryptarithm_answer_only: 358
- surface_unit_tail: 27
- easy_gravity_fragile: 30
- total repeated overlay rows: 3070

### Bundle footprint

- overlay examples: 3070
- total examples: 10898
- total steps: 341
- total tokens: 28700041
- max sequence length: 7971

## Sext-heavy mix

- **38 crypt rule_unknown misses** に `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2`
- **13 bit hypothesis_formed misses** に `BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3`
- **5 equation_numeric_guess misses** に `EQUATION_NUMERIC_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- **8 cryptarithm_guess misses** に `CRYPT_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- **5 unit_conversion misses** に `UNIT_CURRENT_MISS_EXTRA_REPEAT = 2`
- **4 gravity misses** に `GRAVITY_CURRENT_MISS_EXTRA_REPEAT = 2`
- **4 cryptarithm_deduce hypothesis misses** に `CRYPT_DEDUCE_HYPOTHESIS_CURRENT_MISS_EXTRA_REPEAT = 2`
- **6 bit tail misses** に `BIT_TAIL_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_cryptarithm_answer_only 260 -> 358`、`surface_binary_prompt_local_answer_only 291 -> 300`、`surface_binary_structured_answer_only 324 -> 364`、`surface_numeric_answer_only 217 -> 227`、`surface_unit_tail 17 -> 27`、`easy_gravity_fragile 22 -> 30`

## Support budget

- combined measured-support share は **`0.3463`**
- cryptarithm share は **`0.0546`**
- exact binary share は **`0.4815`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 3070`** で **`+171`**
- total tokens は **`28668072 -> 28700041`** で **`+31969`**
- 差分は quint-heavy に `cryptarithm_deduce hypothesis 4件 × repeat 2 = +8 rows` と `bit tail 6件 × repeat 2 = +12 rows` を加えたもの

## Interpretation before training

- full 版では support budget が already 厚いので、この枝の価値は **残り tail を足しても過学習せず additive gain が出るか** に集約される
- もしここが quint-heavy より明確に強ければ、次の mainline 候補は sext-heavy 化する

## Next evaluation gate

- `v20_mlx_v6_frontier_sext_heavy_full_mb1_nobc` を quint-heavy / quad-heavy と measured diff-pack で比較し、**full budget でも残り tail 追加が additive gain か** を見る
