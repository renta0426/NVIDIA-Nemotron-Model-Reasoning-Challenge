# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は、bit 系を leaderboard 改善の主戦場として扱い、cryptarithm には split / concat weakness があると明示している
- `v20_corrective_corpus_v4_mainline` の live MLX partial でも失点は `bit_manipulation` と `cryptarithm_deduce` に集中している
- 既存の replay branch は safe に押せる measured bit rows が 5 行しかなく、bit 側の圧力としては弱かった
- そこで今回は `plain + cryptarithm support` を土台に、**current v4 partial bit misses 18 行を direct support 観点で再配分**する比較線を追加した

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
- surface_binary_structured_answer_only: 64
- surface_numeric_answer_only: 64
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 671

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 206
- surface_numeric_answer_only: 192
- surface_cryptarithm_answer_only: 144
- easy_gravity_fragile: 18
- total repeated overlay rows: 2387

### Bundle footprint

- base examples: 7828
- overlay examples: 2387
- total examples: 10215
- total steps: 320
- total tokens: 28527967
- max sequence length: 7971

## Direct bit-miss support lane

- target set は **v4 partial bit miss 18 IDs**
- そのうち **17 IDs** を answer-only support lane に直接予約した
- bucket split は **prompt-local 3 + structured 14**
- 残り **`02a66bcb`** は support に回さず、既存の `binary_structured_exact_core` exact lane 側で保持した
- extra repeat は `surface_boxed_tail_boost` として **17 行**だけ追加され、support 合計は `480 -> 497 repeated` になった

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **64 unique / 206 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 144 repeated**
- overlay token share は prompt-local `0.1269`、structured `0.0953`、numeric `0.0411`、cryptarithm `0.0279`
- combined answer-only support share は **`0.2912`**

## Delta vs expanded cryptarithm-support base

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support` 比で overlay rows は `2370 -> 2387`
- total tokens は `28523182 -> 28527967` で **`+4785`**
- 増分はほぼ **measured bit miss support 17 repeat rows** のみで、numeric / cryptarithm lane の幅は維持している

## Interpretation before training

- これは replay 5行 branch の代替であり、**現に落としている bit miss 群を answer-only lane で直接 surface stabilization する** 比較線
- 一方で support 幅そのものは大きく増やしておらず、`plain + cryptarithm support` の配分をほぼ保ったまま measured pressure だけを載せている

## Next evaluation gate

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support` を `plain_cryptarithm_support` と `plain_cryptarithm_support_bit_replay` の両方と measured diff-pack で比較し、**direct support と safe replay のどちらが bit 実失点に効くか**を判定する
