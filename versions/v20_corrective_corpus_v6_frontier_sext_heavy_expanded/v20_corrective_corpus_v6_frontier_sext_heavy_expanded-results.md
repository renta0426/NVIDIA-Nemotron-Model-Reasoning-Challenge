# v20 corrective corpus v6 frontier sext-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_sext_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_sext_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_sext_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_sext_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_sext_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は **bit manipulation** を主戦場、**cryptarithm** を次の大きな改善余地と置いている
- current `v4` partial residual では、quint-heavy で未特化だった **`cryptarithm_deduce / hypothesis_formed = 4`** と **`bit_manipulation / (rule_found + rule_unknown) = 6`** が残る
- README は bit manipulation を主戦場と置いており、cryptarithm も deduce/guess をまとめて前進させる必要があるため、残り tail を **quint-heavy の上にそのまま積む** 比較線を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 258
- surface_numeric_answer_only: 227
- surface_cryptarithm_answer_only: 358
- surface_unit_tail: 27
- easy_gravity_fragile: 30
- total repeated overlay rows: 2974

### Bundle footprint

- overlay examples: 2974
- total examples: 10802
- total steps: 338
- total tokens: 28671005
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
- repeats は `surface_cryptarithm_answer_only 260 -> 358`、`surface_binary_prompt_local_answer_only 291 -> 300`、`surface_binary_structured_answer_only 228 -> 268`、`surface_numeric_answer_only 217 -> 227`、`surface_unit_tail 17 -> 27`、`easy_gravity_fragile 22 -> 30`

## Support budget

- combined measured-support share は **`0.3235`**
- cryptarithm share は **`0.0565`**
- exact binary share は **`0.4983`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2974`** で **`+171`**
- total tokens は **`28639036 -> 28671005`** で **`+31969`**
- これは quint-heavy に `cryptarithm_deduce hypothesis 4件 × repeat 2 = +8 rows` と `bit tail 6件 × repeat 2 = +12 rows` を追加した差分

## Interpretation before training

- sext-heavy は **current residual の未特化 tail をほぼ全回収した additive branch**
- quint-heavy に対して **+18 rows / +3905 tokens** の軽差分で、残りの crypt/bit tail を押したときに clean gain が出るかを見る

## Next evaluation gate

- `v20_mlx_v6_frontier_sext_heavy_expanded_mb1_nobc` を quint-heavy / quad-heavy と measured diff-pack で比較し、**残り tail 追加が additive gain か** を見る
