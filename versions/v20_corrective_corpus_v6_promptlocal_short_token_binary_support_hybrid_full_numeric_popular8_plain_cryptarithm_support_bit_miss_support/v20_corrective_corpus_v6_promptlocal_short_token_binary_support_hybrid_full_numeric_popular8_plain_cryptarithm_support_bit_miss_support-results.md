# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` に沿って、bit を main upside、cryptarithm を split / concat weakness repair として同時に扱う
- expanded 版で direct bit miss support の設計を固めたうえで、full structured support (`96`) を戻した upper-bound 版も作っておく
- これにより `plain + cryptarithm support + direct bit miss support` の上限挙動を `full replay` と真正面から比較できる

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
- surface_binary_structured_answer_only: 96
- surface_numeric_answer_only: 64
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 703

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
- surface_binary_structured_answer_only: 302
- surface_numeric_answer_only: 192
- surface_cryptarithm_answer_only: 144
- easy_gravity_fragile: 18
- total repeated overlay rows: 2483

### Bundle footprint

- base examples: 7828
- overlay examples: 2483
- total examples: 10311
- total steps: 323
- total tokens: 28557003
- max sequence length: 7971

## Direct bit-miss support lane

- target set は expanded 版と同じ **v4 partial bit miss 18 IDs**
- そのうち **17 IDs** を answer-only support lane に直接予約した
- bucket split は **prompt-local 3 + structured 14**
- **`02a66bcb`** は already-covered exact row として `binary_structured_exact_core` 側に残した
- extra repeat は `surface_boxed_tail_boost` **17 行**で、support 合計は `720 -> 737 repeated` になった

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **96 unique / 302 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 144 repeated**
- overlay token share は prompt-local `0.1218`、structured `0.1318`、numeric `0.0394`、cryptarithm `0.0268`
- combined answer-only support share は **`0.3198`**

## Delta vs full cryptarithm-support base

- `hybrid_full_numeric_popular8_plain_cryptarithm_support` 比で overlay rows は `2466 -> 2483`
- total tokens は `28551534 -> 28557003` で **`+5469`**
- structured support を full のまま維持しつつ、増分は measured bit miss support 17 repeat rows にほぼ限定されている

## Interpretation before training

- これは full replay branch の対照で、**safe replay より広く現行 miss 群へ pressure を載せる** upper-bound direct-support 線
- それでも unique 幅は据え置きなので、bit 側への効き目を比較しやすい

## Next evaluation gate

- `hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support` を `full cryptarithm support` と `full bit replay` に対して measured diff-pack で比較し、**full support 予算下でも replay より direct miss support が勝つか** を判定する
