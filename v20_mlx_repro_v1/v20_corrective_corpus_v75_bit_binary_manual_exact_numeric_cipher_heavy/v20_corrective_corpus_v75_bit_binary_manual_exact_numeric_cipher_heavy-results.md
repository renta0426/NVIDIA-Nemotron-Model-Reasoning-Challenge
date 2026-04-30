# v20_corrective_corpus_v75_bit_binary_manual_exact_numeric_cipher_heavy

- created_at: 2026-04-30T10:13:17.264506+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` highlights weak base slices in BIT, cipher, and numeric-style symbol tasks. This branch keeps v69's safe BIT set and simultaneously pushes the numeric and cipher lanes harder.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving the broader v12 manual-heavy BIT base while testing the combined non-BIT pressure ceiling before reintroducing crypt lanes.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v75_bit_binary_manual_exact_numeric_cipher_heavy_mlxdir_mb1_nobc_ckpt20`
- runtime status: `not started`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v12 bit-binary mainline core, including the full manual binary answer-only lane.
- Keep the same exact-safe BIT support as v69 so the new comparison isolates the non-BIT lane combination.
- Raise both `numeric_2x2` and `text_monoalphabetic` repeat density more aggressively than v69 while keeping the existing local numeric/cipher rescue rows fully covered.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_support_unique: 99
- cipher_support_unique: 276
- selected_unique_rows: 1965
- selected_repeated_rows: 9870

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 277
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v75_binary_answer_only_manual_exact_numeric_cipher_heavy: 307
- v75_binary_manual_full: 438
- v75_binary_verified_manual_exact_numeric_cipher_heavy: 7605
- v75_cipher_heavy: 1253
- v75_numeric_heavy: 267

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v75_bit_binary_manual_exact_numeric_cipher_heavy_bundle.jsonl
- base_examples: 7830
- overlay_examples: 9870
- total_examples: 17700
- total_steps: 554
- total_tokens: 30940280
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1965
