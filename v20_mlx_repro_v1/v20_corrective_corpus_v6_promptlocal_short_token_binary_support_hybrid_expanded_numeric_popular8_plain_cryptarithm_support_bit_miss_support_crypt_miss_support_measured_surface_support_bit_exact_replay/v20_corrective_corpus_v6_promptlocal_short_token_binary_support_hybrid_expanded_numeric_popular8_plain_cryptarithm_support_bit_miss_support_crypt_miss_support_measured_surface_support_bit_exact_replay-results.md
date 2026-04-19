# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-exact-replay results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...measured_surface_support_bit_exact_replay.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` の binary weakness に対し、measured surface-support base の上へ **verified exact として再利用できる current partial bit misses** だけを exact replay する upper-bound ablation
- ただし teacher-correctness 制約により、partial miss 18 件のうち exact replay として通ったのは **3 IDs** (`02a66bcb`, `053f87d3`, `0b56b953`) のみ

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

- binary_structured_exact_core: 624
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 204
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 22
- total repeated overlay rows: 2450

### Bundle footprint

- base examples: 7828
- overlay examples: 2450
- total examples: 10278
- total steps: 322
- total tokens: 28537757
- max sequence length: 7971

## Exact-replay mix

- exact replay selected: **3 IDs**
  - `02a66bcb` → `binary_structured_exact_core`
  - `053f87d3` → `binary_structured_exact_core`
  - `0b56b953` → `binary_structured_exact_core`
- exact replay bonus: **`+2` binary variants per selected ID**
- resulting binary boosts: `exact_rule_commit_boost 3` and `exact_closure_commit_boost 3`

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **64 unique / 204 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- overlay token share は prompt-local `0.1251`、structured `0.0935`、numeric `0.0421`、cryptarithm `0.0356`、cipher `0.0047`、unit `0.0047`、gravity `0.0066`
- combined measured-support share は **`0.3123`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.4756`**

## Delta vs expanded measured-surface-support base

- `...measured_surface_support` 比で overlay rows は `2446 -> 2450`
- total tokens は `28536458 -> 28537757` で **`+1299`**
- `binary_structured_exact_core` repeats は `618 -> 624`、`surface_binary_structured_answer_only` は `206 -> 204`
- つまり **2 行が structured support から exact replay 側へ寄り、3 exact IDs に +6 exact variants を与えた結果、正味 +4 rows** の小差分 branch

## Interpretation before training

- current partial の残 bit gap に対しては筋の良い correction だが、teacher-correctness 制約が強く **effective replay mass はかなり小さい**
- したがってこれは本命というより、`measured_surface_support` の後ろに置く **cheap upper-bound ablation** として扱う

## Next evaluation gate

- `...measured_surface_support_bit_exact_replay` を `...measured_surface_support` と measured diff-pack で比較し、**3-ID exact replay でも bit miss が動くか** を見る
