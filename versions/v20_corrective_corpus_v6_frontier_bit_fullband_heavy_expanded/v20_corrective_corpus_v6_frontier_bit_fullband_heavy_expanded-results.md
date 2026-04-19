# v20 corrective corpus v6 frontier bit-fullband-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_bit_fullband_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_bit_fullband_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_bit_fullband_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_bit_fullband_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_bit_fullband_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README は bit manipulation を最重要カテゴリとしている
- current `v4` partial の bit residual 全体は **19 misses** なので、`hypothesis-only` より広く **current bit full-band 全体** を押す ablation を用意した

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 297
- surface_binary_structured_answer_only: 258
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 260
- total repeated overlay rows: 2839

### Bundle footprint

- overlay examples: 2839
- total examples: 10667
- total steps: 334
- total tokens: 28649605
- max sequence length: 7971

## Bit current full-band mix

- current `v4` partial の **19 bit misses** を `BIT_V4_CURRENT_FULLBAND_MISS_IDS` として固定
- `surface_binary_*` に `BIT_V4_CURRENT_FULLBAND_MISS_EXTRA_REPEAT = 2` を追加
- repeats は `surface_binary_prompt_local_answer_only **291 -> 297**`、`surface_binary_structured_answer_only **228 -> 258**`

## Support budget

- combined measured-support share は **`0.3057`**
- cryptarithm share は **`0.0416`**
- exact binary share は **`0.5114`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2839`** で **`+36`**
- total tokens は **`28639036 -> 28649605`** で **`+10569`**

## Interpretation before training

- これは frontier-support を維持したまま、**current bit residual 全体** を heavier replay する branch
- `hypothesis-only` より広く効くなら、bit の次枝は full-band replay が本線になる
