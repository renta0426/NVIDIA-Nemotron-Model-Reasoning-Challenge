# v20_corrective_corpus_v12_bit_binary_manual_heavy

- created_at: 2026-04-28T09:55:19.384272+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to keep `verified_trace_ready` as the trace core, use `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by combining the full curated binary core with all 87 manual binary rows as answer-only support.
- status: bundle generated and MLX training is running; latest observed step is `91`, and model score is not yet measured.
- planned run name: `v20_mlx_v12_bit_binary_manual_heavy_mlxdir_mb1_nobc_ckpt20`
- runtime status: `running`
- latest observed step: `91`
- retained checkpoints: `0000040_adapters.safetensors / 0000060_adapters.safetensors / 0000080_adapters.safetensors`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the same full curated binary core from `verified_trace_ready` and `answer_only_keep` used by v11.
- Promote all `manual_audit_priority` binary rows only as answer-only support, never as raw manual CoT, to widen hard `bit_other` coverage.
- Keep the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- selected_unique_rows: 1590
- selected_repeated_rows: 4439

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v12_binary_answer_only_curated: 307
- v12_binary_manual_full: 438
- v12_binary_verified_curated: 3672
- v12_cipher_guardrail: 6
- v12_numeric_guess_rescue: 16

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v12_bit_binary_manual_heavy_bundle.jsonl
- base_examples: 7830
- overlay_examples: 4439
- total_examples: 12269
- total_steps: 384
- total_tokens: 29311806
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1590
