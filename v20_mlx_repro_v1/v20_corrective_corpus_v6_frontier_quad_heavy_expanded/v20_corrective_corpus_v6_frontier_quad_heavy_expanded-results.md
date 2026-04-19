# v20 corrective corpus v6 frontier quad-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_frontier_quad_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_quad_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_quad_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_quad_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_quad_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は **bit manipulation** を主戦場、**cryptarithm** を次の大きな改善余地と置いている
- current `v4` partial residual でも最大塊は **`cryptarithm_* / rule_unknown = 38`** と **`bit_manipulation / hypothesis_formed = 13`** で、README が改善必要帯として強調する **`cryptarithm_guess`** も **8件** 残っている
- そのため tri-heavy に加えて **current `cryptarithm_guess` tail 8件** も重ね、**bit + crypt deduce + equation guess + crypt guess** を同時に押す mainline 候補を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 258
- surface_numeric_answer_only: 227
- surface_cryptarithm_answer_only: 350
- total repeated overlay rows: 2942

### Bundle footprint

- overlay examples: 2942
- total examples: 10770
- total steps: 337
- total tokens: 28664552
- max sequence length: 7971

## Quad-heavy mix

- **38 crypt rule_unknown misses** に `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2`
- **13 bit hypothesis_formed misses** に `BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3`
- **5 equation_numeric_guess misses** に `EQUATION_NUMERIC_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- **8 cryptarithm_guess misses** に `CRYPT_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_cryptarithm_answer_only 260 -> 350`、`surface_binary_prompt_local_answer_only 291 -> 300`、`surface_binary_structured_answer_only 228 -> 258`、`surface_numeric_answer_only 217 -> 227`

## Support budget

- combined measured-support share は **`0.3183`**
- cryptarithm share は **`0.0557`**
- exact binary share は **`0.5021`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2942`** で **`+139`**
- total tokens は **`28639036 -> 28664552`** で **`+25516`**
- これは tri-heavy 差分に、`cryptarithm_guess` tail **8件 × repeat 2 = +16 rows** をさらに積んだ差分

## Interpretation before training

- README が **「top solutions will need to make significant progress on cryptarithm」「this requires training the model to make guesses」** と書いているので、quad-heavy はその方針を current miss 帯へ直接当てる枝
- tri-heavy に対して **ほぼ軽差分で crypt guess tail を拾えるか** を見る additive ablation でもある

## Next evaluation gate

- `v20_mlx_v6_frontier_quad_heavy_expanded_mb1_nobc` を tri-heavy / crypt_ruleunknown / equation_guess と measured diff-pack で比較し、**crypt guess tail 追加が additive gain か** を見る
