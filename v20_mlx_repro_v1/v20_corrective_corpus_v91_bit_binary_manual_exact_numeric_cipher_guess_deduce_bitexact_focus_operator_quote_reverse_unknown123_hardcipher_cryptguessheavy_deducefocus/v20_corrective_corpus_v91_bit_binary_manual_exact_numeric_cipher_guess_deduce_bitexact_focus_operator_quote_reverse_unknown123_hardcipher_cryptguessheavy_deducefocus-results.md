# v20_corrective_corpus_v91_bit_binary_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus

- created_at: 2026-04-30T12:14:21.568503+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` highlights weak base slices in BIT, cipher, numeric-style symbol, `Cryptarithm (Guess)`, and `Cryptarithm (Deduce)`. This branch keeps the v90 heavier guess schedule and isolates whether additional focused deduce replay helps more than guess-heavy alone.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving the stronger v80-v90 stack while probing the weakest `Cryptarithm (Deduce)` slice with a stricter focused tail.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v91_bit_binary_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_mlxdir_mb1_nobc_ckpt20`
- runtime status: `not started`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v12 bit-binary mainline core, the v80 targeted exact-safe BIT replay lane, the v85 combined numeric/cipher hard tail, and the v90 heavier cryptarithm guess lane.
- Add the focused `glyph_len5` cryptarithm deduce rows already used in v88, but now on top of the heavier guess stack.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_support_unique: 99
- cipher_support_unique: 276
- crypt_guess_support_unique: 140
- crypt_deduce_support_unique: 273
- bit_exact_focus_unique: 410
- operator_tail_numeric_unique: 99
- quote_reverse_tail_numeric_unique: 13
- hard_cipher_unknown123_tail_unique: 106
- crypt_guess_heavy_unique: 140
- crypt_deduce_focus_unique: 319
- selected_unique_rows: 2765
- selected_repeated_rows: 14899

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 345
- cryptarithm_deduce_support: 592
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v91_binary_answer_only_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus: 307
- v91_binary_manual_full: 438
- v91_binary_verified_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus: 7605
- v91_bit_exact_focus: 2216
- v91_cipher_heavy: 1253
- v91_cipher_unknown123_hard4_tail: 200
- v91_crypt_deduce_focus: 777
- v91_crypt_deduce_low_ratio: 509
- v91_crypt_guess_heavy_focus: 602
- v91_crypt_guess_light: 462
- v91_numeric_heavy: 267
- v91_numeric_operator_tail: 223
- v91_numeric_quote_reverse_tail: 40

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v91_bit_binary_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_bundle.jsonl
- base_examples: 7830
- overlay_examples: 14899
- total_examples: 22729
- total_steps: 711
- total_tokens: 32145756
- max_seq_len: 7971
- retokenized_overlay_problem_count: 2765
