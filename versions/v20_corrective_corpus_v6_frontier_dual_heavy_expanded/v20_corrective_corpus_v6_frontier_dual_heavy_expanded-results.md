# v20 corrective corpus v6 frontier dual-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_dual_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_dual_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_dual_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_dual_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_dual_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は **bit manipulation** を主戦場、**cryptarithm** を次の大きな改善余地と置いている
- current `v4` partial residual でも最大塊は **`cryptarithm_* / rule_unknown = 38`** と **`bit_manipulation / hypothesis_formed = 13`** なので、個別枝だけでなく **両方を同時に重ねる mainline 候補** を先に作る

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 258
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 334
- total repeated overlay rows: 2916

### Bundle footprint

- overlay examples: 2916
- total examples: 10744
- total steps: 337
- total tokens: 28661036
- max sequence length: 7971

## Dual-heavy mix

- **38 crypt rule_unknown misses** に `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2`
- **13 bit hypothesis_formed misses** に `BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3`
- repeats は `surface_cryptarithm_answer_only 260 -> 334`、`surface_binary_prompt_local_answer_only 291 -> 300`、`surface_binary_structured_answer_only 228 -> 258`

## Support budget

- combined measured-support share は **`0.3154`**
- cryptarithm share は **`0.0533`**
- exact binary share は **`0.5043`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2916`** で **`+113`**
- total tokens は **`28639036 -> 28661036`** で **`+22000`**
- これは `crypt_ruleunknown_heavy (+74 rows)` と `bit_hypothesis_heavy (+39 rows)` を同時に積んだ差分

## Interpretation before training

- frontier-support 単独よりも、**current residual の上位 2 band を同時に削る** ことを狙う mainline 候補
- 個別枝が小さく効いても combined でより素直に gain する可能性がある

## Next evaluation gate

- `v20_mlx_v6_frontier_dual_heavy_expanded_mb1_nobc` を frontier-support / crypt_ruleunknown / bit_hypothesis の各枝と measured diff-pack で比較し、**同時加算が clean gain か** を見る
