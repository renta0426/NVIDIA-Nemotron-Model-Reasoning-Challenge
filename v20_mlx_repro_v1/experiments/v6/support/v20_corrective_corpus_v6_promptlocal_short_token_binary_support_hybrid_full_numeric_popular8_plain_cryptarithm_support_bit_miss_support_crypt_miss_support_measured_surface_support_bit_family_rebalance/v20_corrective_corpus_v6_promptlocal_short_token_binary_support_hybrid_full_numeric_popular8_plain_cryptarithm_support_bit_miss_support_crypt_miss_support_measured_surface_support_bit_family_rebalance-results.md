# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...measured_surface_support_bit_family_rebalance.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功

## README-grounded motivation

- expanded 版と同じく、README の **bit 主戦場** に合わせて full structured support 予算の上から binary exact lane を miss-heavy family へ組み替える upper-bound branch
- support lane は維持しつつ、binary exact の repeat mass を大きく戻して bit slice の押し上げ余地を見る

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

- binary_structured_exact_core: 768
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 475
- surface_numeral_boxed: 102
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 302
- surface_numeric_answer_only: 199
- surface_cryptarithm_answer_only: 188
- easy_gravity_fragile: 22
- total repeated overlay rows: 2787

### Bundle footprint

- base examples: 7828
- overlay examples: 2787
- total examples: 10615
- total steps: 333
- total tokens: 28649430
- max sequence length: 7971

## Bit-family rebalance

- structured family target counts:
  - `choose(shl,shr,rol) 24`
  - `majority(ror,shl,shr) 22`
  - `majority(rol,shl,shr) 22`
  - `choose(shl,shr,ror) 20`
  - `choose(shl,shr,nibble_swap) 10`
  - `or(rol,shl) 8`
  - `or(rol,shr) 6`
  - `xor(ror,shl) 4`
  - `or(ror,shr) 2`
  - `xor(shl,shr) 32`
- mandatory anchors により `choose(ror,nibble_swap,shl) 1` と `choose(rol,ror,shr) 1` も保持
- prompt-local exact は `binary_prompt_local_stage2_unique_exact` **95 rows** を維持し、family-wide repeat bonus を追加

## Repeat mix

- binary rebalance bonus により `exact_rule_commit_boost` が **245** rows 追加
- `binary_structured_exact_core` repeats は `618 -> 768`
- `binary_prompt_local_exact` repeats は `380 -> 475`
- `surface_boxed_tail_boost` は base と同じ **76 rows**

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **96 unique / 302 repeated**
- numeric support: **64 unique / 199 repeated**
- cryptarithm support: **48 unique / 188 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- overlay token share は prompt-local `0.1079`、structured `0.1168`、numeric `0.0363`、cryptarithm `0.0307`、cipher `0.0041`、unit `0.0040`、gravity `0.0057`
- combined measured-support share は **`0.3055`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5115`**

## Delta vs full measured-surface-support base

- `...measured_surface_support` 比で overlay rows は `2542 -> 2787`
- total tokens は `28565494 -> 28649430` で **`+83936`**
- 増分は expanded 版と同じく binary exact lane の repeat bonus (`+150 structured +95 prompt-local = +245`)
- unique rows は同じ `703` のままなので、full 版でも **selection rebalance + repeat reweight** だけを見られる

## Interpretation before training

- `bit_exact_replay` の 3-ID ablation と違い、こちらは miss-heavy family 全体を teacher-correct pool から押し込む branch
- full budget でも support share は `0.3426 -> 0.3055` と下がるので、surface gains を保ったまま bit を押し返せるかが主要判定点

## Next evaluation gate

- `...measured_surface_support_bit_family_rebalance` を `...measured_surface_support` と measured diff-pack で比較し、**full budget での binary exact rebalance が bit slice を押せるか** を判定する
