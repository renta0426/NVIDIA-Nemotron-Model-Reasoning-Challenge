# v20 corrective corpus v6 frontier bit-fullband-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_bit_fullband_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_bit_fullband_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_bit_fullband_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_bit_fullband_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_bit_fullband_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README が強調する bit manipulation 主戦場に対し、current bit residual 全体 **19 misses** を full budget 側で押す比較線
- `hypothesis-only` 13件より広く、rule_found / rule_unknown 側までまとめて replay する

## Dataset composition

### Unique rows

- total unique overlay problems: 712
- unique bucket mix は frontier-support full と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 297
- surface_binary_structured_answer_only: 354
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 260
- total repeated overlay rows: 2935

### Bundle footprint

- overlay examples: 2935
- total examples: 10763
- total steps: 337
- total tokens: 28678641
- max sequence length: 7971

## Bit current full-band mix

- current `v4` partial の **19 bit misses** を `BIT_V4_CURRENT_FULLBAND_MISS_IDS` として固定
- `surface_binary_*` に `BIT_V4_CURRENT_FULLBAND_MISS_EXTRA_REPEAT = 2` を追加
- repeats は `surface_binary_prompt_local_answer_only **291 -> 297**`、`surface_binary_structured_answer_only **324 -> 354**`

## Support budget

- combined measured-support share は **`0.3297`**
- cryptarithm share は **`0.0401`**
- exact binary share は **`0.4937`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 2935`** で **`+36`**
- total tokens は **`28668072 -> 28678641`** で **`+10569`**

## Interpretation before training

- `hypothesis-only` より広く current bit residual 全体を押す ablation
- full budget で gain が出るなら、bit residual は narrower hypothesis focus より full-band replay の方が自然だと判断できる
