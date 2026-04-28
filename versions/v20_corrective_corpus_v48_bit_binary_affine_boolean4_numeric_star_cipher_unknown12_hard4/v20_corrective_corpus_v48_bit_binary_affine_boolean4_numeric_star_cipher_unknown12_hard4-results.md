# v20_corrective_corpus_v48_bit_binary_affine_boolean4_numeric_star_cipher_unknown12_hard4

- created_at: 2026-04-28T16:22:10.400377+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: combine `cuda-train-data-analysis-v1/reports/67_aopen_symbol_wall_breakthrough_assessment.md` for low-ratio numeric operator support and `reports/06_text_unknown_notes.md` for safe monoalphabetic completion, but isolate the `*`-only numeric slice while keeping cipher at unknown-char `{1,2}` with `hard_score >= 4`.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving v34's exact affine/boolean4 bit core and comparing unknown12 vs unknown123 on the star-only numeric lane.
- status: bundle generated; detached score/progress watchers armed; queued behind `v47`.
- planned run name: `v20_mlx_v48_bit_binary_affine_boolean4_numeric_star_cipher_unknown12_hard4_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `queue waiting (active=2 require_started=0 any_ready=1)`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Reuse the same narrow exact `binary_affine_xor` / `boolean4` verified core as v34 for the main bit lane.
- Increase both local numeric/cipher rescue repeats, then add the `*`-only numeric operator slice with the harder cipher slice restricted to `unknown_char_count in {1,2}`.
- Use this branch to isolate whether the extra unknown=3 cipher rows from v46/v47 are helping or just adding noise.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_star_support_unique: 86
- cipher_unknown12_hard4_support_unique: 93
- selected_unique_rows: 1769
- selected_repeated_rows: 8686

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 94
- numeric_guess_rescue: 88

### Repeated rows by source mix

- v48_binary_answer_only_affine_boolean4_numeric_star_cipher_unknown12_hard4: 418
- v48_binary_manual_affine_boolean4_numeric_star_cipher_unknown12_hard4: 347
- v48_binary_verified_affine_boolean4_numeric_star_cipher_unknown12_hard4: 7605
- v48_cipher_numeric_star_cipher_unknown12_hard4: 164
- v48_numeric_guess_star_cipher_unknown12_hard4: 152

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v48_bit_binary_affine_boolean4_numeric_star_cipher_unknown12_hard4_bundle.jsonl
- base_examples: 7830
- overlay_examples: 8686
- total_examples: 16516
- total_steps: 517
- total_tokens: 30715723
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1769
