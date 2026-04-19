# v20 corrective corpus v6 frontier bit-hypothesis-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_bit_hypothesis_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_bit_hypothesis_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_bit_hypothesis_heavy_expanded.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は最重要カテゴリを **bit manipulation** と置き、トップ解はここを最大化すべきだと明示している
- current `v4` partial の residual bit misses では **`bit_manipulation/hypothesis_formed = 13`** が最大塊で、しかも全件がすでに selected support に入っているため、今回は **unique 拡張ではなく targeted heavy repeat** で押す

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
- surface_binary_structured_answer_only: 69
- surface_numeric_answer_only: 68
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 680

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
- surface_binary_structured_answer_only: 258
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 260
- easy_gravity_fragile: 22
- total repeated overlay rows: 2842

### Bundle footprint

- base examples: 7828
- overlay examples: 2842
- total examples: 10670
- total steps: 334
- total tokens: 28650845
- max sequence length: 7971

## Bit hypothesis heavy mix

- current `v4` partial の **13 hypothesis-formed bit misses** を `BIT_V4_PARTIAL_HYPOTHESIS_MISS_IDS` として固定
- 13 IDs は **`surface_binary_prompt_local_answer_only 3`** と **`surface_binary_structured_answer_only 10`** にすでに入っているので、`BIT_V4_PARTIAL_HYPOTHESIS_MISS_EXTRA_REPEAT = 3` でそのまま heavier replay する
- `surface_binary_prompt_local_answer_only` repeats は **`291 -> 300`**
- `surface_binary_structured_answer_only` repeats は **`228 -> 258`**

## Support budget

- prompt-local support: **96 unique / 300 repeated**
- structured support: **69 unique / 258 repeated**
- numeric support: **68 unique / 217 repeated**
- cryptarithm support: **48 unique / 260 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.3068`**
- cryptarithm share は **`0.0415`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5106`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2842`** で **`+39`**
- total tokens は **`28639036 -> 28650845`** で **`+11809`**
- 差分は 13 hypothesis-formed bit misses に対する `surface_binary_*` heavy repeat に限定される

## Interpretation before training

- これは frontier-support を維持したまま、**current bit residual の中で最も太い hypothesis_formed band** だけを濃く学習させる branch
- frontier-support や crypt-heavy 系で gain が出ても bit residual が残るなら、この枝が次の clean gain 候補になる

## Next evaluation gate

- `v20_mlx_v6_frontier_bit_hypothesis_heavy_expanded_mb1_nobc` を `...crypt_deduce_heavy_frontier_support` と measured diff-pack で比較し、**13 bit hypothesis misses への concentrated replay が clean gain か** を見る
