# v20_corrective_corpus_v55_bit_binary_affine_boolean4_crypt_deduce_guess_fusion

- created_at: 2026-04-28T17:08:49.083514+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` shows cryptarithm is the hardest family in the base model, and the symbol reports say guess-mode needs explicit training, so this branch adds grouped-exact/small-set `cryptarithm_deduce` plus explicit `cryptarithm_guess` replay.
- local target: current best local300 `0.846667` -> aim for `> 0.9` while checking whether adding guess-mode crypt replay helps more than proof-mode-only v54.
- status: bundle generated; detached queue/watch armed, model score not yet measured.
- planned run name: `v20_mlx_v55_bit_binary_affine_boolean4_crypt_deduce_guess_fusion_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Reuse the same narrow exact `binary_affine_xor` / `boolean4` verified core as v34 for the main bit lane.
- Keep the existing local numeric/cipher rescue rows, then add grouped-exact / small-set `cryptarithm_deduce` answer-only rows plus explicit `cryptarithm_guess` replay.
- Use this branch as the first direct proof-mode vs guess-mode crypt comparison in the queued ladder.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- crypt_deduce_focus_unique: 319
- crypt_guess_support_unique: 140
- selected_unique_rows: 2049
- selected_repeated_rows: 9643

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- cryptarithm_deduce_support: 319
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v55_binary_answer_only_affine_boolean4_crypt_deduce_guess_fusion: 418
- v55_binary_manual_affine_boolean4_crypt_deduce_guess_fusion: 347
- v55_binary_verified_affine_boolean4_crypt_deduce_guess_fusion: 7605
- v55_cipher_guardrail: 10
- v55_crypt_deduce_focus: 777
- v55_crypt_guess_support: 462
- v55_numeric_guess_rescue: 24

## Targeted residual IDs

- local_bit_miss_ids: `000b53cf,012fb81b,01e09228,02a66bcb,034fb629,048cc279,04d8c3e6,05ca617c,06881e47,07e8cf66,0b16458a,0ec17d2e,12fd5b6c,132ec6ae,16db2c74,172d2417`
- local_numeric_guess_miss_ids: `065f9dea,0c0683c3`
- local_cipher_miss_ids: `0184a864`

## Validation

- passed: True
- errors: []
- missing_local_bit_miss_ids: []
- missing_local_numeric_guess_ids: []
- missing_local_cipher_ids: []

## Bundle

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v55_bit_binary_affine_boolean4_crypt_deduce_guess_fusion_bundle.jsonl
- base_examples: 7830
- overlay_examples: 9643
- total_examples: 17473
- total_steps: 547
- total_tokens: 30853125
- max_seq_len: 7971
- retokenized_overlay_problem_count: 2049
