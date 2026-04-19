# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- expanded 版の comprehensive surface repair を full structured support 予算へそのまま持ち込む upper-bound branch
- bit / crypt / numeric / easy surface misses を一体で支えつつ、structured support `96` を維持する

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
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 302
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 22
- total repeated overlay rows: 2542

### Bundle footprint

- base examples: 7828
- overlay examples: 2542
- total examples: 10370
- total steps: 325
- total tokens: 28565494
- max sequence length: 7971

## Measured-support mix

- bit miss support: **17 rows**
- crypt miss support: **44 rows**
- residual surface support: **15 rows** (`numeric 7 + unit 3 + gravity 4 + cipher 1`)
- `surface_boxed_tail_boost` は **76 rows** で、内訳は expanded 版と同じ

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **96 unique / 302 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- overlay token share は prompt-local `0.1204`、structured `0.1302`、numeric `0.0422`、cryptarithm `0.0343`、cipher `0.0046`、unit `0.0045`、gravity `0.0064`
- combined measured-support share は **`0.3426`**

## Delta vs full bit+crypt miss-support base

- `hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support` 比で overlay rows は `2527 -> 2542`
- total tokens は `28562700 -> 28565494` で **`+2794`**
- 増分は expanded 版と同じく current residual surface misses 15 rows の direct boost に集中している

## Interpretation before training

- これは current partial の supportable misses を full budget 下でまとめて支える upper-bound 線
- replay や generic support より measured repair 色が強く、hidden 側でも surface取りこぼしが残っている場合の保険になる

## Next evaluation gate

- `hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support` を `full bit+crypt miss-support` と measured diff-pack で比較し、**full budget で residual surface support まで足す価値があるか** を判定する
