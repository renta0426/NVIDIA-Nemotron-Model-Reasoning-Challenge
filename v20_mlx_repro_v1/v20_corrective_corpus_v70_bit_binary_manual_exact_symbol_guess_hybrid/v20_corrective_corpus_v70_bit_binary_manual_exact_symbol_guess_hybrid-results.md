# v20_corrective_corpus_v70_bit_binary_manual_exact_symbol_guess_hybrid

- created_at: 2026-04-30T09:52:18.450233+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` highlights weak base slices in BIT, cipher, numeric-style symbol tasks, and especially `Cryptarithm (Guess)`. This branch keeps v69's safe BIT/symbol set and adds a light explicit guess replay lane.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving the broader v12 manual-heavy BIT base, keeping v69's denser numeric/cipher support, and testing whether a light cryptarithm_guess lane helps without shifting too much mass away from BIT.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v70_bit_binary_manual_exact_symbol_guess_hybrid_mlxdir_mb1_nobc_ckpt20`
- runtime status: `not started`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v12 bit-binary mainline core, including the full manual binary answer-only lane.
- Keep the same exact-safe BIT, `numeric_2x2`, and `text_monoalphabetic` support used in v69 so the new comparison isolates the added `cryptarithm_guess` lane.
- Add a light boxed-safe `cryptarithm_guess` replay lane because `README.md` shows that slice starts at `0/164` on the base model.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_support_unique: 99
- cipher_support_unique: 276
- crypt_guess_support_unique: 140
- selected_unique_rows: 2105
- selected_repeated_rows: 10004

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 277
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v70_binary_answer_only_manual_exact_symbol_guess_hybrid: 307
- v70_binary_manual_full: 438
- v70_binary_verified_manual_exact_symbol_guess_hybrid: 7605
- v70_cipher_symbol_guess_hybrid: 963
- v70_crypt_guess_light: 462
- v70_numeric_symbol_guess_hybrid: 229

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v70_bit_binary_manual_exact_symbol_guess_hybrid_bundle.jsonl
- base_examples: 7830
- overlay_examples: 10004
- total_examples: 17834
- total_steps: 558
- total_tokens: 30948508
- max_seq_len: 7971
- retokenized_overlay_problem_count: 2105
