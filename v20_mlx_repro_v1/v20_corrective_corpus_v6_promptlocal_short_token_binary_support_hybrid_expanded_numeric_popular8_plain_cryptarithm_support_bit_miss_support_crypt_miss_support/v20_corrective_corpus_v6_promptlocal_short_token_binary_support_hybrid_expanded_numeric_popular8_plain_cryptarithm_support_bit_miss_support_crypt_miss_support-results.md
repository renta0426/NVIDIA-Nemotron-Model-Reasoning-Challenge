# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` は、bit を main upside、cryptarithm を split / concat weakness と位置づけている
- `v20_mlx_v4_mainline_mb1_nobc` の current partial (`547` rows completed) では miss が **bit 18 / cryptarithm 44** に集中している
- 既に追加した `bit_miss_support` は bit miss 群へ direct support を入れられたため、次は同じ measured-support 発想を glyph_len5 cryptarithm lane にも拡張する

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
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 18
- total repeated overlay rows: 2431

### Bundle footprint

- base examples: 7828
- overlay examples: 2431
- total examples: 10259
- total steps: 321
- total tokens: 28533664
- max sequence length: 7971

## Measured-support mix

- bit miss direct support: **17 selected** (`prompt-local 3 + structured 14`)
- crypt miss direct support: **44 selected**, all `glyph_len5 / answer_only_keep`
- boost rows は `surface_boxed_tail_boost` **61 行**で、内訳は `bit 17 + crypt 44`
- crypt miss 44 行は current partial miss set の全件で、残る crypt lane 4 slots は generic support fill に回る

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **64 unique / 206 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- overlay token share は prompt-local `0.1259`、structured `0.0945`、numeric `0.0408`、cryptarithm `0.0358`
- combined answer-only support share は **`0.2970`**

## Delta vs expanded bit-miss-support base

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support` 比で overlay rows は `2387 -> 2431`
- total tokens は `28527967 -> 28533664` で **`+5697`**
- 増分は **crypt miss 44 行への extra repeat** が中心で、bit miss pressure と他 lane 幅は維持している

## Interpretation before training

- これは `bit_miss_support` の次段で、**README が強調する glyph split / concat weakness に measured miss targeting を直結**した branch
- unique 幅を増やさず current miss 群へ pressure を集中できるため、surface memorization ではなく miss repair の比較として扱いやすい

## Next evaluation gate

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support` を `bit_miss_support` と `bit_replay` 系へ measured diff-pack で比較し、**bit+crypt の measured support 併用が hidden 寄りに効くか**を判定する
