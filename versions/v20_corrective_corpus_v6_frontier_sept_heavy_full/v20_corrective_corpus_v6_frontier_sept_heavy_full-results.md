# v20 corrective corpus v6 frontier sept-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_sept_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_sept_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_sept_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_sept_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_sept_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README の equation 節は operator not found や multiplication/division/absolute difference 仮説の扱いが性能に効くと明示している
- full budget 側でも **equation deduce tail 3件** を薄く足し、残り domain-tail をできるだけ取りこぼさない比較線を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 712
- unique bucket mix は frontier-support full と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 364
- surface_numeric_answer_only: 233
- surface_cryptarithm_answer_only: 358
- surface_unit_tail: 27
- easy_gravity_fragile: 30
- total repeated overlay rows: 3076

### Bundle footprint

- overlay examples: 3076
- total examples: 10904
- total steps: 342
- total tokens: 28700921
- max sequence length: 7971

## Sept-heavy mix

- sext-heavy の全成分に加えて、**3 equation deduce tail misses** に `EQUATION_DEDUCE_TAIL_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_numeric_answer_only 227 -> 233` のみ増える

## Support budget

- combined measured-support share は **`0.3469`**
- cryptarithm share は **`0.0546`**
- exact binary share は **`0.4810`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 3076`** で **`+177`**
- total tokens は **`28668072 -> 28700921`** で **`+32849`**
- 差分は sext-heavy に `equation deduce tail 3件 × repeat 2 = +6 rows` を加えたもの

## Interpretation before training

- full 版では support budget が already 厚いので、この枝の価値は **equation deduce tail が最後に additive gain するか** に集約される
- sext-heavy に対して **+6 rows / +880 tokens** なので、過度な分布シフトは起こしにくい

## Next evaluation gate

- `v20_mlx_v6_frontier_sept_heavy_full_mb1_nobc` を sext-heavy / quint-heavy と measured diff-pack で比較し、**full budget でも equation deduce tail 追加が additive gain か** を見る
