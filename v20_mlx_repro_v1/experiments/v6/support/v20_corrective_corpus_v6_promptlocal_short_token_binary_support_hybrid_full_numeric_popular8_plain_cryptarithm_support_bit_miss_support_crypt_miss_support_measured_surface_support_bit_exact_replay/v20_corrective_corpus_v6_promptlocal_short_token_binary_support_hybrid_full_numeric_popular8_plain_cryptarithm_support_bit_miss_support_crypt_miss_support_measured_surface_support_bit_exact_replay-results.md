# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-exact-replay results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_exact_replay_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...measured_surface_support_bit_exact_replay.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- expanded 版と同じく、full structured support 予算を維持したまま **teacher-correct な bit exact replay だけ** を最小コストで重ねる upper-bound ablation
- exact replay として実際に通ったのは同じく **3 IDs** (`02a66bcb`, `053f87d3`, `0b56b953`) のみ

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

- binary_structured_exact_core: 624
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 300
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 22
- total repeated overlay rows: 2546

### Bundle footprint

- base examples: 7828
- overlay examples: 2546
- total examples: 10374
- total steps: 325
- total tokens: 28566679
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
- structured support: **96 unique / 300 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- overlay token share は prompt-local `0.1202`、structured `0.1294`、numeric `0.0404`、cryptarithm `0.0342`、cipher `0.0045`、unit `0.0045`、gravity `0.0064`
- combined measured-support share は **`0.3396`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.4568`**

## Delta vs full measured-surface-support base

- `...measured_surface_support` 比で overlay rows は `2542 -> 2546`
- total tokens は `28565494 -> 28566679` で **`+1185`**
- `binary_structured_exact_core` repeats は `618 -> 624`、`surface_binary_structured_answer_only` は `302 -> 300`
- expanded 版と同様に、**2 行を support から exact replay へ寄せて、3 exact IDs に +6 exact variants を与えた結果、正味 +4 rows** の小差分 branch

## Interpretation before training

- full budget でも exact replay として使える mass が小さいため、これは本命より **cheap upper-bound ablation** の性格が強い
- 逆にここで bit miss が動かなければ、次は replay ではなく broader family rebalance か teacher-correct source の再設計へ進む根拠になる

## Next evaluation gate

- `...measured_surface_support_bit_exact_replay` を `...measured_surface_support` と measured diff-pack で比較し、**3-ID exact replay が full budget でも bit slice を押すか** を判定する
