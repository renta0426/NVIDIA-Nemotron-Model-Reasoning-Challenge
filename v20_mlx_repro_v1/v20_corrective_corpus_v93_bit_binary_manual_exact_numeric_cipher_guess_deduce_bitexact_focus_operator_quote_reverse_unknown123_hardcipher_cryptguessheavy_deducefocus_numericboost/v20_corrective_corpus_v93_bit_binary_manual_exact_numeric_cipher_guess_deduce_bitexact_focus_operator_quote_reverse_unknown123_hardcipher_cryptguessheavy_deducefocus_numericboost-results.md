# v20_corrective_corpus_v93_bit_binary_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_numericboost

- created_at: 2026-04-30T12:25:34.411759+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` highlights especially weak base slices in `Cryptarithm (Guess)`, `Cryptarithm (Deduce)`, and `Equation Numeric (Guess)`. This branch keeps the v91 heavy guess plus focused deduce stack and checks whether extra numeric replay helps on top of that crypt-focused frontier.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving the stronger v80-v91 stack while re-boosting numeric-guess tails without surrendering the new crypt gains.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v93_bit_binary_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_numericboost_mlxdir_mb1_nobc_ckpt20`
- runtime status: `not started`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v12 bit-binary mainline core, the v80 targeted exact-safe BIT replay lane, the v85 combined numeric/cipher hard tail, and the v91 heavier crypt guess plus focused deduce stack.
- Add one more numeric-only pass over operator-tail and quote-reverse rows to directly target the README `Equation Numeric (Guess)` weakness.

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
- operator_tail_numeric_boost_unique: 99
- quote_reverse_tail_numeric_boost_unique: 13
- selected_unique_rows: 2765
- selected_repeated_rows: 15165

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 345
- cryptarithm_deduce_support: 592
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v93_binary_answer_only_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_numericboost: 307
- v93_binary_manual_full: 438
- v93_binary_verified_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_numericboost: 7605
- v93_bit_exact_focus: 2216
- v93_cipher_heavy: 1253
- v93_cipher_unknown123_hard4_tail: 200
- v93_crypt_deduce_focus: 777
- v93_crypt_deduce_low_ratio: 509
- v93_crypt_guess_heavy_focus: 602
- v93_crypt_guess_light: 462
- v93_numeric_heavy: 267
- v93_numeric_operator_tail: 223
- v93_numeric_operator_tail_boost: 226
- v93_numeric_quote_reverse_tail: 40
- v93_numeric_quote_reverse_tail_boost: 40

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v93_bit_binary_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_numericboost_bundle.jsonl
- base_examples: 7830
- overlay_examples: 15165
- total_examples: 22995
- total_steps: 719
- total_tokens: 32189276
- max_seq_len: 7971
- retokenized_overlay_problem_count: 2765
