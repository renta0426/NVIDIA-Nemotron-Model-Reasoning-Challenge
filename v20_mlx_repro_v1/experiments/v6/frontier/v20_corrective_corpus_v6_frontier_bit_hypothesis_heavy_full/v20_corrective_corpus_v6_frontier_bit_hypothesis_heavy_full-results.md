# v20 corrective corpus v6 frontier bit-hypothesis-heavy full results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/frontier/v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_full.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_bit_hypothesis_heavy_full_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_bit_hypothesis_heavy_full_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/frontier/v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_full/reproduce_v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_full.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- README が明示する最重要カテゴリ **bit manipulation** に対し、frontier-support full の上へ current residual 最大 bit band をさらに押す比較線
- current `v4` partial の **`bit_manipulation/hypothesis_formed 13`** はすでに selected support へ入っているので、追加 unique ではなく **full budget 上での concentrated repeat** を測る

## Dataset composition

### Unique rows

- binary_structured_exact_core: 152
- binary_logic_exact: 56
- binary_permutation_exact: 40
- binary_prompt_local_exact: 95
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- surface_binary_prompt_local_answer_only: 96
- surface_binary_structured_answer_only: 101
- surface_numeric_answer_only: 68
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 712

### Repeated training rows

- binary_structured_exact_core: 768
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 475
- surface_numeral_boxed: 102
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 354
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 260
- easy_gravity_fragile: 22
- total repeated overlay rows: 2938

### Bundle footprint

- base examples: 7828
- overlay examples: 2938
- total examples: 10766
- total steps: 337
- total tokens: 28679881
- max sequence length: 7971

## Bit hypothesis heavy mix

- current `v4` partial の **13 hypothesis-formed bit misses** を `BIT_V4_PARTIAL_HYPOTHESIS_MISS_IDS` として固定
- 13 IDs は **`surface_binary_prompt_local_answer_only 3`** と **`surface_binary_structured_answer_only 10`** にすでに入っているため、`BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3` で heavier replay する
- `surface_binary_prompt_local_answer_only` repeats は **`291 -> 300`**
- `surface_binary_structured_answer_only` repeats は **`324 -> 354`**

## Support budget

- prompt-local support: **96 unique / 300 repeated**
- structured support: **101 unique / 354 repeated**
- numeric support: **68 unique / 217 repeated**
- cryptarithm support: **48 unique / 260 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.3307`**
- cryptarithm share は **`0.0401`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.4930`**

## Delta vs full frontier-support base

- unique rows は **`712 -> 712`** で不変
- overlay rows は **`2899 -> 2938`** で **`+39`**
- total tokens は **`28668072 -> 28679881`** で **`+11809`**
- 差分は 13 hypothesis-formed bit misses に対する `surface_binary_*` heavy repeat に限定される

## Interpretation before training

- full 版では structured support が already 厚いので、この枝の価値は **bit residual 13 件を実際に削れるか** にほぼ集約される
- ここで gain が出るなら、次は bit rule_unknown / rule_found まで広げるより hypothesis-like family replay を本線にできる

## Next evaluation gate

- `v20_mlx_v6_frontier_bit_hypothesis_heavy_full_mb1_nobc` を `...crypt_deduce_heavy_frontier_support` と measured diff-pack で比較し、**bit residual 13 件への concentrated replay が full budget でも効くか** を見る
