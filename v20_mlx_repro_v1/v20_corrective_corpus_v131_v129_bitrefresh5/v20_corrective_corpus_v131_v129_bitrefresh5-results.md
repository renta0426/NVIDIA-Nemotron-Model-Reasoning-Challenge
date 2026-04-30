# v20_corrective_corpus_v131_v129_bitrefresh5

- created_at: 2026-04-30T15:13:33.922736+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` highlights especially weak base slices in `Bit Manipulation`, `Equation Numeric (Guess)`, `Cryptarithm (Deduce)`, `Cryptarithm (Guess)`, and `Cipher`. This branch keeps the v129 post-fifth numeric frontier and adds one more exact-safe BIT replay pass.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving the broader v129 recovery stack while re-pressuring the README `Bit Manipulation` weakness.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v131_v129_bitrefresh5_mlxdir_mb1_nobc_ckpt20`
- runtime status: `not started`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v12 bit-binary mainline core and the v129 stack that already refreshed post-fifth numeric pressure.
- Add another exact-safe BIT replay so the branch revisits the README `Bit Manipulation` slice after the post-fifth numeric refresh.

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
- crypt_guess_extra_boost_unique: 140
- crypt_deduce_extra_boost_unique: 319
- operator_tail_numeric_boost_unique: 99
- quote_reverse_tail_numeric_boost_unique: 13
- hard_cipher_unknown123_boost_unique: 106
- bit_exact_boost_unique: 410
- selected_unique_rows: 2765
- selected_repeated_rows: 31844

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 345
- cryptarithm_deduce_support: 592
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v101_crypt_deduce_focus_boost: 777
- v103_numeric_operator_tail_boost: 226
- v103_numeric_quote_reverse_tail_boost: 40
- v105_cipher_unknown123_hard4_boost: 244
- v107_bit_exact_boost: 1729
- v109_crypt_deduce_focus_boost: 777
- v111_numeric_operator_tail_boost: 226
- v111_numeric_quote_reverse_tail_boost: 40
- v113_bit_exact_boost: 1729
- v115_crypt_deduce_focus_boost: 777
- v117_numeric_operator_tail_boost: 226
- v117_numeric_quote_reverse_tail_boost: 40
- v119_bit_exact_boost: 1729
- v121_crypt_deduce_focus_boost: 777
- v123_numeric_operator_tail_boost: 226
- v123_numeric_quote_reverse_tail_boost: 40
- v125_bit_exact_boost: 1729
- v127_crypt_deduce_focus_boost: 777
- v129_numeric_operator_tail_boost: 226
- v129_numeric_quote_reverse_tail_boost: 40
- v131_bit_exact_boost: 1729
- v99_binary_answer_only_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_numericcipherboost_bitboost_guessboost: 307
- v99_binary_manual_full: 438
- v99_binary_verified_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_deducefocus_numericcipherboost_bitboost_guessboost: 7605
- v99_bit_exact_boost: 1729
- v99_bit_exact_focus: 2216
- v99_cipher_heavy: 1253
- v99_cipher_unknown123_hard4_boost: 244
- v99_cipher_unknown123_hard4_tail: 200
- v99_crypt_deduce_focus: 777
- v99_crypt_deduce_low_ratio: 509
- v99_crypt_guess_heavy_boost: 602
- v99_crypt_guess_heavy_focus: 602
- v99_crypt_guess_light: 462
- v99_numeric_heavy: 267
- v99_numeric_operator_tail: 223
- v99_numeric_operator_tail_boost: 226
- v99_numeric_quote_reverse_tail: 40
- v99_numeric_quote_reverse_tail_boost: 40

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v131_v129_bitrefresh5_bundle.jsonl
- base_examples: 7830
- overlay_examples: 31844
- total_examples: 39674
- total_steps: 1241
- total_tokens: 36768081
- max_seq_len: 7971
- retokenized_overlay_problem_count: 2765
