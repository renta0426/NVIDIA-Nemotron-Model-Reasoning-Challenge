# v20 corrective corpus v6 frontier crypt-fullband-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_crypt_fullband_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_crypt_fullband_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_crypt_fullband_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_crypt_fullband_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_crypt_fullband_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README の cryptarithm weakness を full budget 側でも current residual 全体に対して測る比較線
- current `v4` partial の **45 crypt misses** をまとめて押し、`ruleunknown-only` より広い replay が効くかを見る

## Dataset composition

### Unique rows

- total unique overlay problems: 712
- unique bucket mix は frontier-support full と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 324
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 348
- total repeated overlay rows: 2987

### Bundle footprint

- overlay examples: 2987
- total examples: 10815
- total steps: 339
- total tokens: 28680032
- max sequence length: 7971

## Crypt current full-band mix

- current `v4` partial の **45 crypt misses** を `CRYPT_V4_CURRENT_FULLBAND_MISS_IDS` として固定
- `surface_cryptarithm_answer_only` に `CRYPT_V4_CURRENT_FULLBAND_MISS_EXTRA_REPEAT = 2` を追加
- repeats は **`260 -> 348`**

## Support budget

- combined measured-support share は **`0.3308`**
- cryptarithm share は **`0.0542`**
- exact binary share は **`0.4929`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 2987`** で **`+88`**
- total tokens は **`28668072 -> 28680032`** で **`+11960`**

## Interpretation before training

- `ruleunknown-only` では拾い切れない crypt hypothesis/guess tail が効くかを確かめる branch
- full budget で gain が出れば、crypt の本命は current full-band replay に寄せる価値がある
