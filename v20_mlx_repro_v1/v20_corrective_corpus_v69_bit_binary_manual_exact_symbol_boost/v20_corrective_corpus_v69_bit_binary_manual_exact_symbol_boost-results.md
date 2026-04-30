# v20_corrective_corpus_v69_bit_binary_manual_exact_symbol_boost

- created_at: 2026-04-30T09:46:57.813566+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` highlights weak base slices in BIT, cipher, and numeric-style symbol tasks, while `cuda-train-data-analysis-v1` says safer BIT gains come from audited affine/boolean exact rows plus controlled `numeric_2x2` / `text_monoalphabetic` support. This branch keeps v68's safe set and only raises nonbit supervision density.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving the broader v12 manual-heavy BIT base, keeping v68's exact-safe bit weighting, and boosting numeric/cipher symbol support density without changing the unique support set.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v69_bit_binary_manual_exact_symbol_boost_mlxdir_mb1_nobc_ckpt20`
- runtime status: `not started`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v12 bit-binary mainline core, including the full manual binary answer-only lane.
- Keep the same audited exact-safe BIT and symbol/cipher support rows as v68 so the comparison isolates supervision density rather than row selection.
- Raise `numeric_2x2` and `text_monoalphabetic` repeat density above v68 while keeping the existing local numeric/cipher rescue rows fully covered.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_support_unique: 99
- cipher_support_unique: 276
- selected_unique_rows: 1965
- selected_repeated_rows: 9542

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 277
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v69_binary_answer_only_manual_exact_symbol_boost: 307
- v69_binary_manual_full: 438
- v69_binary_verified_manual_exact_symbol_boost: 7605
- v69_cipher_symbol_boost: 963
- v69_numeric_symbol_boost: 229

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v69_bit_binary_manual_exact_symbol_boost_bundle.jsonl
- base_examples: 7830
- overlay_examples: 9542
- total_examples: 17372
- total_steps: 544
- total_tokens: 30877279
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1965
