# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` の bit / cryptarithm 弱点修正を measured support 化したうえで、current partial に残る surface-side misses も同じ枠組みで押し切る branch
- supportable residuals は **numeric 7 / unit 3 / gravity 4 / cipher 1**。unit は mandatory 3 rows を保持するため 5 miss 全載せではなく slot 残量 3 行に絞った

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
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 206
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 22
- total repeated overlay rows: 2446

### Bundle footprint

- base examples: 7828
- overlay examples: 2446
- total examples: 10274
- total steps: 322
- total tokens: 28536458
- max sequence length: 7971

## Measured-support mix

- bit miss support: **17 rows**
- crypt miss support: **44 rows**
- residual surface support: **15 rows** (`numeric 7 + unit 3 + gravity 4 + cipher 1`)
- `surface_boxed_tail_boost` は **76 rows** で、内訳は `bit 17 + crypt 44 + numeric 7 + unit 3 + gravity 4 + cipher 1`

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **64 unique / 206 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- overlay token share は prompt-local `0.1254`、structured `0.0942`、numeric `0.0405`、cryptarithm `0.0357`、cipher `0.0047`、unit `0.0045`、gravity `0.0066`
- combined measured-support share は **`0.3116`**

## Delta vs expanded bit+crypt miss-support base

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support` 比で overlay rows は `2431 -> 2446`
- total tokens は `28533664 -> 28536458` で **`+2794`**
- 増分は current residual surface misses 15 rows の direct boost にほぼ限定される

## Interpretation before training

- これは current partial の **supportable misses をほぼ全部 surface lane に押し込む** branch
- unit は mandatory set を守りながら slot 残量 3 行だけ measured miss に振っており、guardrail を壊さず residual repair を試せる

## Next evaluation gate

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support` を `bit+crypt miss-support` branch と measured diff-pack で比較し、**residual surface repair まで足す価値があるか** を判定する
