# v20_corrective_corpus_v30_bit_binary_family_structured_manual_balance

- created_at: 2026-04-28T13:58:32.411077+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says unresolved bit tail mass is concentrated in `bit_structured_byte_formula` answer-only rows and `bit_other` answer-only/manual rows, so a balanced bridge should target exactly those lanes.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by balancing v26-style verified family+structured replay with a mid-strength structured/manual bridge between v28 and v29.
- status: bundle generated and queued behind the active v11/v12 pair plus the queued v13/v14/v15/v16/v17/v18/v19/v20/v21/v22/v23/v24/v25/v26/v27/v28/v29 follow-ups; model score not yet measured.
- planned run name: `v20_mlx_v30_bit_binary_family_structured_manual_balance_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `queued waiting_for_slot (active=2 require_started=0 any_ready=1)`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11-v29.
- Keep local miss families plus structured/prompt-local exact rows as the verified core.
- Balance the tail bridge between v28 and v29: more structured/bit_other support than v27, but less extreme than either tail-only branch.
- Keep all `manual_audit_priority` binary rows as answer-only support, never as raw manual CoT.
- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- selected_unique_rows: 1590
- selected_repeated_rows: 10281

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v30_binary_answer_only_family_structured_manual_balance: 897
- v30_binary_manual_family_structured_manual_balance: 608
- v30_binary_verified_family_structured_manual_balance: 8754
- v30_cipher_guardrail: 6
- v30_numeric_guess_rescue: 16

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v30_bit_binary_family_structured_manual_balance_bundle.jsonl
- base_examples: 7830
- overlay_examples: 10281
- total_examples: 18111
- total_steps: 567
- total_tokens: 31253267
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1590
