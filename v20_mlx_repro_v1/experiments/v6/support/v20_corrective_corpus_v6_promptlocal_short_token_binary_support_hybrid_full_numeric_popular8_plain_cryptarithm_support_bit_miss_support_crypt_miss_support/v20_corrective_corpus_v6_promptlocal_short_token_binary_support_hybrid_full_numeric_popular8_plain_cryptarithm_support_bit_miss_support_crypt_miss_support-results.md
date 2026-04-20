# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` の bit / cryptarithm priorities をそのまま full support 予算へ持ち込む upper-bound branch
- expanded 版で measured bit+crypt support の配管を固めたうえで、structured support `96` を維持する full 版も並走させて比較する

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
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 18
- total repeated overlay rows: 2527

### Bundle footprint

- base examples: 7828
- overlay examples: 2527
- total examples: 10355
- total steps: 324
- total tokens: 28562700
- max sequence length: 7971

## Measured-support mix

- bit miss direct support: **17 selected** (`prompt-local 3 + structured 14`)
- crypt miss direct support: **44 selected**, all `glyph_len5 / answer_only_keep`
- boost rows は `surface_boxed_tail_boost` **61 行**で、内訳は `bit 17 + crypt 44`
- full structured support (`96`) を維持したまま、crypt lane の current miss targeting を同時に有効化している

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **96 unique / 302 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- overlay token share は prompt-local `0.1208`、structured `0.1307`、numeric `0.0391`、cryptarithm `0.0344`
- combined answer-only support share は **`0.3250`**

## Delta vs full bit-miss-support base

- `hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support` 比で overlay rows は `2483 -> 2527`
- total tokens は `28557003 -> 28562700` で **`+5697`**
- 増分は expanded 版と同じく **crypt miss 44 行への extra repeat** が中心で、full structured support 予算を保ったまま crypt miss targeting を追加している

## Interpretation before training

- これは full `bit_miss_support` の強化版で、**bit と cryptarithm の live misses を同時に direct support 化する upper-bound 線**
- replay より miss 集中度が高く、generic crypt support より measured repair 色が強い

## Next evaluation gate

- `hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support` を `full bit_miss_support` と `full bit_replay` に対して measured diff-pack で比較し、**full support 予算で bit+crypt measured support 併用が最有力か**を判定する
