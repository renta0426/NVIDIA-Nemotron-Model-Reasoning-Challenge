# v20_corrective_corpus_v196_v194_ciphercrypt16

- created_at: 2026-04-30T19:01:25.566529+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` highlights especially weak base slices in `Cipher`, `Equation Numeric (Guess)`, `Cryptarithm (Guess)`, `Cryptarithm (Deduce)`, and `Bit Manipulation`. This branch keeps the v194 post-fifteenth-crypt frontier and adds one more hard-cipher replay pass.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving the broader v194 recovery stack while re-pressuring the README `Cipher` weakness.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v196_v194_ciphercrypt16_mlxdir_mb1_nobc_ckpt20`
- runtime status: `not started`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v12 bit-binary mainline core and the v194 stack that already replayed the latest cryptarithm guess pass.
- Add another hard-cipher replay so the branch revisits the README `Cipher` slice after the fifteenth crypt refresh.

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
- selected_repeated_rows: 57384

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 345
- cryptarithm_deduce_support: 592
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 101

### Repeated rows by source mix

- v100_binary_answer_only_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_trainingdeduce_numericcipherboost_bitboost_deducefocusboost: 307
- v100_binary_manual_full: 438
- v100_binary_verified_manual_exact_numeric_cipher_guess_deduce_bitexact_focus_operator_quote_reverse_unknown123_hardcipher_cryptguessheavy_trainingdeduce_numericcipherboost_bitboost_deducefocusboost: 7605
- v100_bit_exact_boost: 1729
- v100_bit_exact_focus: 2216
- v100_cipher_heavy: 1253
- v100_cipher_unknown123_hard4_boost: 244
- v100_cipher_unknown123_hard4_tail: 200
- v100_crypt_deduce_focus_boost: 777
- v100_crypt_deduce_low_ratio: 509
- v100_crypt_guess_heavy_focus: 602
- v100_crypt_guess_light: 462
- v100_crypt_training_focus: 509
- v100_numeric_heavy: 267
- v100_numeric_operator_tail: 223
- v100_numeric_operator_tail_boost: 226
- v100_numeric_quote_reverse_tail: 40
- v100_numeric_quote_reverse_tail_boost: 40
- v102_crypt_guess_heavy_boost: 602
- v104_cipher_unknown123_hard4_boost: 244
- v106_numeric_operator_tail_boost: 226
- v106_numeric_quote_reverse_tail_boost: 40
- v108_bit_exact_boost: 1729
- v110_crypt_guess_heavy_boost: 602
- v112_cipher_unknown123_hard4_boost: 244
- v114_bit_exact_boost: 1729
- v116_crypt_guess_heavy_boost: 602
- v118_cipher_unknown123_hard4_boost: 244
- v120_bit_exact_boost: 1729
- v122_crypt_guess_heavy_boost: 602
- v124_cipher_unknown123_hard4_boost: 244
- v126_bit_exact_boost: 1729
- v128_crypt_guess_heavy_boost: 602
- v130_cipher_unknown123_hard4_boost: 244
- v132_bit_exact_boost: 1729
- v134_crypt_guess_heavy_boost: 602
- v136_cipher_unknown123_hard4_boost: 244
- v138_bit_exact_boost: 1729
- v140_crypt_guess_heavy_boost: 602
- v142_cipher_unknown123_hard4_boost: 244
- v144_bit_exact_boost: 1729
- v146_crypt_guess_heavy_boost: 602
- v148_cipher_unknown123_hard4_boost: 244
- v150_bit_exact_boost: 1729
- v152_crypt_guess_heavy_boost: 602
- v154_cipher_unknown123_hard4_boost: 244
- v156_bit_exact_boost: 1729
- v158_crypt_guess_heavy_boost: 602
- v160_cipher_unknown123_hard4_boost: 244
- v162_bit_exact_boost: 1729
- v164_crypt_guess_heavy_boost: 602
- v166_cipher_unknown123_hard4_boost: 244
- v168_bit_exact_boost: 1729
- v170_crypt_guess_heavy_boost: 602
- v172_cipher_unknown123_hard4_boost: 244
- v174_bit_exact_boost: 1729
- v176_crypt_guess_heavy_boost: 602
- v178_cipher_unknown123_hard4_boost: 244
- v180_bit_exact_boost: 1729
- v182_crypt_guess_heavy_boost: 602
- v184_cipher_unknown123_hard4_boost: 244
- v186_bit_exact_boost: 1729
- v188_crypt_guess_heavy_boost: 602
- v190_cipher_unknown123_hard4_boost: 244
- v192_bit_exact_boost: 1729
- v194_crypt_guess_heavy_boost: 602
- v196_cipher_unknown123_hard4_boost: 244

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v196_v194_ciphercrypt16_bundle.jsonl
- base_examples: 7830
- overlay_examples: 57384
- total_examples: 65214
- total_steps: 2039
- total_tokens: 44168545
- max_seq_len: 7971
- retokenized_overlay_problem_count: 2765
