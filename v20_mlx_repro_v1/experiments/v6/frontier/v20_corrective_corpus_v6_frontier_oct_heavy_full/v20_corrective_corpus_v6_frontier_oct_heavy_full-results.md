# v20 corrective corpus v6 frontier oct-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/frontier/v20_corrective_corpus_v6_frontier_oct_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_oct_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_oct_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_oct_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_oct_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README は `cipher` を **100.0%** solve 可能帯として記録している
- full budget 側でも、未特化で残っていた **cipher 1件** だけを足す最終比較線を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 712
- unique bucket mix は frontier-support full と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 364
- surface_numeric_answer_only: 233
- surface_cryptarithm_answer_only: 358
- surface_cipher_boxed: 21
- surface_unit_tail: 27
- easy_gravity_fragile: 30
- total repeated overlay rows: 3078

### Bundle footprint

- overlay examples: 3078
- total examples: 10906
- total steps: 342
- total tokens: 28701236
- max sequence length: 7971

## Oct-heavy mix

- sept-heavy の全成分に加えて、**1 cipher miss** に `CIPHER_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_cipher_boxed 19 -> 21` のみ増える

## Support budget

- combined measured-support share は **`0.3472`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 3078`** で **`+179`**
- total tokens は **`28668072 -> 28701236`** で **`+33164`**
- 差分は sept-heavy に `cipher 1件 × repeat 2 = +2 rows` を加えたもの

## Interpretation before training

- oct-heavy は **current partial miss の最後の 1件** を足した最終 branch
- sept-heavy に対して **+2 rows / +315 tokens** なので、過学習リスクは極小

## Next evaluation gate

- `v20_mlx_v6_frontier_oct_heavy_full_mb1_nobc` を sept-heavy / sext-heavy と measured diff-pack で比較し、**full budget でも cipher 1件追加が additive gain か** を見る
