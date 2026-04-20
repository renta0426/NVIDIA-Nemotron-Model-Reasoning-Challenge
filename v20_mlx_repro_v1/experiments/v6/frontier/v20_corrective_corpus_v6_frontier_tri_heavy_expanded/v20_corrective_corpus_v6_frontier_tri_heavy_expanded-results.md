# v20 corrective corpus v6 frontier tri-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/frontier/v20_corrective_corpus_v6_frontier_tri_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_tri_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_tri_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_tri_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_tri_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Watcher note (2026-04-20): `v20_mlx_repro_v1/outputs/v6/frontier` 配下で actual grouped-root train/eval watcher を配置し、current frontier-support expanded 完了後に `v20_mlx_v6_frontier_tri_heavy_expanded_mb1_nobc` を auto-launch、train 完了後は adapter-validation / postprocess を自動実行するようにした

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は **bit manipulation** を主戦場、**cryptarithm** を次の大きな改善余地と置いている
- current `v4` partial residual でも最大塊は **`cryptarithm_* / rule_unknown = 38`** と **`bit_manipulation / hypothesis_formed = 13`** で、そこに **`equation_numeric_guess = 5`** が小さく残っている
- そのため個別枝だけでなく **bit + crypt + equation の 3 本を同時に重ねる mainline 候補** を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 258
- surface_numeric_answer_only: 227
- surface_cryptarithm_answer_only: 334
- total repeated overlay rows: 2926

### Bundle footprint

- overlay examples: 2926
- total examples: 10754
- total steps: 337
- total tokens: 28662414
- max sequence length: 7971

## Tri-heavy mix

- **38 crypt rule_unknown misses** に `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2`
- **13 bit hypothesis_formed misses** に `BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3`
- **5 equation_numeric_guess misses** に `EQUATION_NUMERIC_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_cryptarithm_answer_only 260 -> 334`、`surface_binary_prompt_local_answer_only 291 -> 300`、`surface_binary_structured_answer_only 228 -> 258`、`surface_numeric_answer_only 217 -> 227`

## Support budget

- combined measured-support share は **`0.3165`**
- cryptarithm share は **`0.0533`**
- exact binary share は **`0.5034`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2926`** で **`+123`**
- total tokens は **`28639036 -> 28662414`** で **`+23378`**
- これは `crypt_ruleunknown_heavy (+74 rows)` と `bit_hypothesis_heavy (+39 rows)` に、`equation_guess_heavy (+10 rows)` をさらに積んだ差分

## Interpretation before training

- frontier-support 単独よりも、**current residual の上位 3 band を同時に削る** ことを狙う mainline 候補
- `equation_guess_heavy` は差分が軽いので、dual-heavy に対して **ほぼノーリスクで equation tail を拾えるか** を見る枝として意味がある

## Next evaluation gate

- `v20_mlx_v6_frontier_tri_heavy_expanded_mb1_nobc` を frontier-support / dual-heavy / equation_guess の各枝と measured diff-pack で比較し、**equation tail 追加が additive gain か** を見る
