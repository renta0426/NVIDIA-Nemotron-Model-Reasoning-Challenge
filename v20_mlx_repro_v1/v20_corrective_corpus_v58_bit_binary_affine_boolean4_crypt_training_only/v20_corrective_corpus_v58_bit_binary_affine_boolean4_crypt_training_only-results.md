# v20_corrective_corpus_v58_bit_binary_affine_boolean4_crypt_training_only

- created_at: 2026-04-28T17:37:13.743948+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` shows cryptarithm is the hardest family in the base model, and the strict audit says the extra full-deduce mass beyond v54 is dominated by `symbol_glyph_training_answer_only`, so this branch isolates that lane without the grouped-exact subset.
- local target: current best local300 `0.846667` -> aim for `> 0.9` while checking whether the broader but weaker training-answer-only crypt lane helps more than the grouped-only v54 control.
- status: bundle generated; detached queue/watch armed, model score not yet measured.
- planned run name: `v20_mlx_v58_bit_binary_affine_boolean4_crypt_training_only_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Reuse the same narrow exact `binary_affine_xor` / `boolean4` verified core as v34 for the main bit lane.
- Keep the existing local numeric/cipher rescue rows, then add only the boxed-safe `symbol_glyph_training_answer_only` cryptarithm-deduce lane.
- Use this branch as the training-only control against v54 grouped-only and v56 full-deduce.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- crypt_training_only_unique: 273
- selected_unique_rows: 1863
- selected_repeated_rows: 8913

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- cryptarithm_deduce_support: 273
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v58_binary_answer_only_affine_boolean4_crypt_training_only: 418
- v58_binary_manual_affine_boolean4_crypt_training_only: 347
- v58_binary_verified_affine_boolean4_crypt_training_only: 7605
- v58_cipher_guardrail: 10
- v58_crypt_training_only: 509
- v58_numeric_guess_rescue: 24

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v58_bit_binary_affine_boolean4_crypt_training_only_bundle.jsonl
- base_examples: 7830
- overlay_examples: 8913
- total_examples: 16743
- total_steps: 524
- total_tokens: 30738064
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1863
