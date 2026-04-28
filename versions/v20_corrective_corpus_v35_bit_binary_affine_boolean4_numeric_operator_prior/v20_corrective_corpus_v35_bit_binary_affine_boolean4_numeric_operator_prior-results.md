# v20_corrective_corpus_v35_bit_binary_affine_boolean4_numeric_operator_prior

- created_at: 2026-04-28T15:10:41.952754+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `cuda-train-data-analysis-v1/reports/67_aopen_symbol_wall_breakthrough_assessment.md` says `equation_numeric_guess` can help accuracy when answer-conditioned operator semantics are mixed at low ratio, while `reports/61_symbol_numeric_guess_global_exact_scan.md` says there is no hidden strict exact promotion left.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by keeping v34's exact affine/boolean4 bit core while adding low-ratio operator-specific numeric support for the unresolved `*` and `"` query operators.
- status: bundle generated and queued behind the active v11/v12 pair plus the queued v13/v14/v15/v16/v17/v18/v19/v20/v21/v22/v23/v24/v25/v26/v27/v28/v29/v30/v31/v32/v33/v34 follow-ups; model score not yet measured.
- planned run name: `v20_mlx_v35_bit_binary_affine_boolean4_numeric_operator_prior_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `queued waiting_for_slot (active=2 require_started=0 any_ready=1)`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Reuse the same narrow exact `binary_affine_xor` / `boolean4` verified core as v34 for the main bit lane.
- Increase only the local numeric rescue repeats and add a low-ratio broader support slice for `numeric_2x2` answer-only rows whose query operator matches the unresolved local operators (`*` and `"`).
- Keep the cipher lane narrow so this branch isolates numeric-operator prior effects rather than broad text support.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_operator_support_unique: 99
- selected_unique_rows: 1689
- selected_repeated_rows: 8564

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v35_binary_answer_only_affine_boolean4_numeric_operator_prior: 418
- v35_binary_manual_affine_boolean4_numeric_operator_prior: 347
- v35_binary_verified_affine_boolean4_numeric_operator_prior: 7605
- v35_cipher_guardrail: 8
- v35_numeric_guess_operator_prior: 186

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v35_bit_binary_affine_boolean4_numeric_operator_prior_bundle.jsonl
- base_examples: 7830
- overlay_examples: 8564
- total_examples: 16394
- total_steps: 513
- total_tokens: 30688941
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1689
