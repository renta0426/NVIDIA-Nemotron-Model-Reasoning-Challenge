# v20 corrective corpus v6 frontier crypt-fullband-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_crypt_fullband_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_crypt_fullband_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_crypt_fullband_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_crypt_fullband_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_crypt_fullband_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README の cryptarithm 節は split / concat / operator-not-found を大きな弱点として挙げている
- current `v4` partial では crypt residual 全体が **45 misses** まで膨らんでいるので、`ruleunknown-only` ではなく **current crypt full-band 全体** を押す ablation を用意した

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 228
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 348
- total repeated overlay rows: 2891

### Bundle footprint

- overlay examples: 2891
- total examples: 10719
- total steps: 336
- total tokens: 28650996
- max sequence length: 7971

## Crypt current full-band mix

- current `v4` partial の **45 crypt misses** を `CRYPT_V4_CURRENT_FULLBAND_MISS_IDS` として固定
- `surface_cryptarithm_answer_only` に `CRYPT_V4_CURRENT_FULLBAND_MISS_EXTRA_REPEAT = 2` を追加
- repeats は **`260 -> 348`**

## Support budget

- combined measured-support share は **`0.3069`**
- cryptarithm share は **`0.0562`**
- exact binary share は **`0.5105`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2891`** で **`+88`**
- total tokens は **`28639036 -> 28650996`** で **`+11960`**

## Interpretation before training

- これは frontier-support を維持したまま、**current crypt residual 全体** を heavier replay する branch
- `ruleunknown-only` よりも広く効くなら、次の crypt 本線は full-band 側に寄せる
