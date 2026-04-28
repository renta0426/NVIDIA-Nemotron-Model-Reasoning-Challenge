# v20_corrective_corpus_v33_bit_binary_verified_bitother_structured_promptlocal

- created_at: 2026-04-28T14:38:09.948017+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `cuda-train-data-analysis-v1/reports/60_binary_exact_disambiguation_and_boolean4_recovery.md` says verified exact bit_other gains are the safe binary expansion, while `FINAL_SUMMARY_REPORT.md` still points to structured-byte and prompt-local verified lanes as major support pools.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by combining verified exact bit_other replay with stronger structured-byte and prompt-local verified pressure, while still keeping unresolved manual bridge mass lighter than v27-v30.
- status: bundle generated and queued behind the active v11/v12 pair plus the queued v13/v14/v15/v16/v17/v18/v19/v20/v21/v22/v23/v24/v25/v26/v27/v28/v29/v30/v31/v32 follow-ups; model score not yet measured.
- planned run name: `v20_mlx_v33_bit_binary_verified_bitother_structured_promptlocal_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `queued waiting_for_slot (active=2 require_started=0 any_ready=1)`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v32.
- Push the audited verified exact `bit_other` lane hard, especially `binary_affine_xor` and recovered boolean exact rows.
- Re-raise `bit_structured_byte_formula` and `bit_prompt_local_exact_formula` verified replay so the branch sits between v23/v24 precision and v31 exact-bitother emphasis.
- Keep answer-only/manual bridge replay lighter than the tail-heavy branches so the run stays precision-oriented.
- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- selected_unique_rows: 1590
- selected_repeated_rows: 10340

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v33_binary_answer_only_bitother_structured_promptlocal: 734
- v33_binary_manual_bitother_structured_promptlocal: 347
- v33_binary_verified_bitother_structured_promptlocal: 9237
- v33_cipher_guardrail: 6
- v33_numeric_guess_rescue: 16

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v33_bit_binary_verified_bitother_structured_promptlocal_bundle.jsonl
- base_examples: 7830
- overlay_examples: 10340
- total_examples: 18170
- total_steps: 569
- total_tokens: 31297811
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1590
