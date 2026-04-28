# v20_corrective_corpus_v31_bit_binary_verified_bitother_exact

- created_at: 2026-04-28T14:19:33.676480+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `cuda-train-data-analysis-v1/reports/60_binary_exact_disambiguation_and_boolean4_recovery.md` says the remaining manual bit tail is not exact-safe, while the audited verified gains came from `binary_affine_xor` plus boolean exact recovery, so the safest next branch is to push that verified bit_other exact lane harder.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by emphasizing audited verified bit_other exact rows (`affine` / `boolean2` / `boolean3` / `boolean4`) instead of leaning even harder on unresolved manual bridge mass.
- status: bundle generated and queued behind the active v11/v12 pair plus the queued v13/v14/v15/v16/v17/v18/v19/v20/v21/v22/v23/v24/v25/v26/v27/v28/v29/v30 follow-ups; model score not yet measured.
- planned run name: `v20_mlx_v31_bit_binary_verified_bitother_exact_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `queued waiting_for_slot (active=2 require_started=0 any_ready=1)`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v30.
- Push the audited verified exact `bit_other` lane hardest, especially rows backed by `binary_affine_xor` and the recovered boolean exact libraries.
- Keep local miss families active, but make answer-only/manual bridge replay lighter than the v27-v30 tail-heavy branches.
- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.
- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- selected_unique_rows: 1590
- selected_repeated_rows: 9570

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v31_binary_answer_only_bitother_exact: 628
- v31_binary_manual_bitother_exact: 435
- v31_binary_verified_bitother_exact: 8485
- v31_cipher_guardrail: 6
- v31_numeric_guess_rescue: 16

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v31_bit_binary_verified_bitother_exact_bundle.jsonl
- base_examples: 7830
- overlay_examples: 9570
- total_examples: 17400
- total_steps: 545
- total_tokens: 31060111
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1590
