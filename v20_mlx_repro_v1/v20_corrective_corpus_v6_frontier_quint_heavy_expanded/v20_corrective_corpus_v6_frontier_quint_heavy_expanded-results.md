# v20 corrective corpus v6 frontier quint-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_frontier_quint_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_quint_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_quint_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_quint_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_quint_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は **bit manipulation** を主戦場、**cryptarithm** を次の大きな改善余地と置いている
- current `v4` partial residual では **`unit_conversion / rule_found = 5`** と **`gravity / rule_found = 4`** も easy-task tail として残っている
- README は **Unit conversion / Gravity を 100% solve rate 目標** と明言し、さらに **post-finetuning で easy tasks を 100% に寄せる** ことを次課題に置いている
- そのため quad-heavy に加えて **current scalar tail 9件** も重ね、**bit + crypt + equation + crypt_guess + scalar easy-task repair** を同時に押す mainline 候補を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 258
- surface_numeric_answer_only: 227
- surface_cryptarithm_answer_only: 350
- surface_unit_tail: 27
- easy_gravity_fragile: 30
- total repeated overlay rows: 2956

### Bundle footprint

- overlay examples: 2956
- total examples: 10784
- total steps: 338
- total tokens: 28667100
- max sequence length: 7971

## Quint-heavy mix

- **38 crypt rule_unknown misses** に `CRYPT_V4_PARTIAL_RULE_UNKNOWN_MISS_EXTRA_REPEAT = 2`
- **13 bit hypothesis_formed misses** に `BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3`
- **5 equation_numeric_guess misses** に `EQUATION_NUMERIC_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- **8 cryptarithm_guess misses** に `CRYPT_GUESS_CURRENT_MISS_EXTRA_REPEAT = 2`
- **5 unit_conversion misses** に `UNIT_CURRENT_MISS_EXTRA_REPEAT = 2`
- **4 gravity misses** に `GRAVITY_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_cryptarithm_answer_only 260 -> 350`、`surface_binary_prompt_local_answer_only 291 -> 300`、`surface_binary_structured_answer_only 228 -> 258`、`surface_numeric_answer_only 217 -> 227`、`surface_unit_tail 17 -> 27`、`easy_gravity_fragile 22 -> 30`

## Support budget

- combined measured-support share は **`0.3204`**
- cryptarithm share は **`0.0555`**
- exact binary share は **`0.5006`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2956`** で **`+153`**
- total tokens は **`28639036 -> 28667100`** で **`+28064`**
- これは quad-heavy に `unit_conversion 5件 × repeat 2 = +10 rows` と `gravity 4件 × repeat 2 = +8 rows` を追加した差分

## Interpretation before training

- README が easy-task perfection を明示しているので、quint-heavy は **hard residual を維持したまま easy tail を取りこぼさないか** を見る枝
- quad-heavy に対して **+18 rows / +2548 tokens** の軽差分で、unit/gravity を 100% 側へ寄せられるかを見る additive ablation でもある

## Next evaluation gate

- `v20_mlx_v6_frontier_quint_heavy_expanded_mb1_nobc` を quad-heavy / tri-heavy と measured diff-pack で比較し、**easy-task tail repair が additive gain か** を見る
