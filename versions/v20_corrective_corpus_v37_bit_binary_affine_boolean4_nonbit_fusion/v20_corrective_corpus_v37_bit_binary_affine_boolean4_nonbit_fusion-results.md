# v20_corrective_corpus_v37_bit_binary_affine_boolean4_nonbit_fusion

- created_at: 2026-04-28T15:19:07.072496+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: combine `cuda-train-data-analysis-v1/reports/67_aopen_symbol_wall_breakthrough_assessment.md` for low-ratio `equation_numeric_guess` operator support and `reports/06_text_unknown_notes.md` for low-risk monoalphabetic answer-completion support, while preserving the exact bit-other core from `reports/60_binary_exact_disambiguation_and_boolean4_recovery.md`.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving v34's exact affine/boolean4 bit core and fusing both broader non-BIT residual lanes in one branch.
- status: bundle generated and queued behind the active v11/v12 pair plus the queued v13/v14/v15/v16/v17/v18/v19/v20/v21/v22/v23/v24/v25/v26/v27/v28/v29/v30/v31/v32/v33/v34/v35/v36 follow-ups; model score not yet measured.
- planned run name: `v20_mlx_v37_bit_binary_affine_boolean4_nonbit_fusion_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `queued waiting_for_slot (active=2 require_started=0 any_ready=1)`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Reuse the same narrow exact `binary_affine_xor` / `boolean4` verified core as v34 for the main bit lane.
- Increase the local numeric and cipher rescue repeats together, then add the low-ratio broader `*` / `"` numeric-operator support from v35 plus the `unknown_char_count = 2` monoalphabetic support slice from v36.
- Use this branch to test whether the remaining local non-BIT misses want the combined prior rather than an isolated numeric-only or cipher-only support lane.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_operator_support_unique: 99
- cipher_unknown2_support_unique: 276
- selected_unique_rows: 1965
- selected_repeated_rows: 9209

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 277
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v37_binary_answer_only_affine_boolean4_nonbit_fusion: 418
- v37_binary_manual_affine_boolean4_nonbit_fusion: 347
- v37_binary_verified_affine_boolean4_nonbit_fusion: 7605
- v37_cipher_nonbit_fusion: 653
- v37_numeric_guess_nonbit_fusion: 186

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v37_bit_binary_affine_boolean4_nonbit_fusion_bundle.jsonl
- base_examples: 7830
- overlay_examples: 9209
- total_examples: 17039
- total_steps: 533
- total_tokens: 30815362
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1965
