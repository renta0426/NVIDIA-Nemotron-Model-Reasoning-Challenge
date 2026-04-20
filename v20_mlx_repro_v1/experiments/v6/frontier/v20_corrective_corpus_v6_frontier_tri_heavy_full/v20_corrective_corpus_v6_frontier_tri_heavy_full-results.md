# v20 corrective corpus v6 frontier tri-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/frontier/v20_corrective_corpus_v6_frontier_tri_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_tri_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_tri_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_tri_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_tri_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README が示す本命 2 軸 **bit manipulation** と **cryptarithm** を、full support budget 側で同時に重ねる比較線
- さらに current `v4` partial residual で残る **`equation_numeric_guess 5`** も小さく上乗せし、**38 crypt rule_unknown + 13 bit hypothesis_formed + 5 equation guess** をまとめて押す

## Dataset composition

### Unique rows

- total unique overlay problems: 712
- unique bucket mix は frontier-support full と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 354
- surface_numeric_answer_only: 227
- surface_cryptarithm_answer_only: 334
- total repeated overlay rows: 3022

### Bundle footprint

- overlay examples: 3022
- total examples: 10850
- total steps: 340
- total tokens: 28691450
- max sequence length: 7971

## Tri-heavy mix

- **38 crypt rule_unknown misses** に `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2`
- **13 bit hypothesis_formed misses** に `BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3`
- **5 equation_numeric_guess misses** に `EQUATION_NUMERIC_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_cryptarithm_answer_only 260 -> 334`、`surface_binary_prompt_local_answer_only 291 -> 300`、`surface_binary_structured_answer_only 324 -> 354`、`surface_numeric_answer_only 217 -> 227`

## Support budget

- combined measured-support share は **`0.3397`**
- cryptarithm share は **`0.0515`**
- exact binary share は **`0.4863`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 3022`** で **`+123`**
- total tokens は **`28668072 -> 28691450`** で **`+23378`**
- 差分は `crypt_ruleunknown_heavy` と `bit_hypothesis_heavy` の同時加算に、`equation_guess_heavy` を加えたもの

## Interpretation before training

- full 版では support budget が already 厚いので、この枝の価値は **上位 3 residual band を同時に押したときに additive gain が出るか** に集約される
- もしここが dual-heavy より明確に強ければ、次の mainline 候補は tri-heavy 化する

## Next evaluation gate

- `v20_mlx_v6_frontier_tri_heavy_full_mb1_nobc` を frontier-support / dual-heavy / equation_guess と measured diff-pack で比較し、**full budget でも equation tail 追加が clean gain か** を見る
