# v20_corrective_corpus_v11_bit_binary_mainline

- created_at: 2026-04-28T09:25:06.079405+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` says to use `verified_trace_ready` as the trace core, mix `answer_only_keep` conservatively, and avoid raw `manual_audit_priority` CoT promotion.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by boosting the 16 observed BIT misses plus the 2 numeric-guess and 1 cipher residuals.
- status: bundle generated and MLX training is running; latest observed step is `16`, and model score is not yet measured.
- planned run name: `v20_mlx_v11_bit_binary_mainline_mlxdir_mb1_nobc_ckpt20`
- runtime status: `running`
- latest observed step: `16`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Strengthen nearly all curated binary rows by taking all `bit_manipulation` rows from `verified_trace_ready` and `answer_only_keep`.
- Upweight the 16 observed local BIT misses explicitly instead of relying only on family-level ratio tuning.
- Backfill any uncovered local BIT miss with an answer-only `manual_audit_priority` rescue row instead of promoting raw manual CoT.
- Add only the narrow residual non-BIT rescue lane: `equation_numeric_guess` 2 IDs and `cipher` 1 ID.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- selected_unique_rows: 1504
- selected_repeated_rows: 4009

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_rescue: 1
- binary_verified_core: 1229
- cipher_guardrail: 1
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v11_binary_answer_only_curated: 307
- v11_binary_manual_rescue: 8
- v11_binary_verified_curated: 3672
- v11_cipher_guardrail: 6
- v11_numeric_guess_rescue: 16

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v11_bit_binary_mainline_bundle.jsonl
- base_examples: 7830
- overlay_examples: 4009
- total_examples: 11839
- total_steps: 371
- total_tokens: 29176594
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1504
