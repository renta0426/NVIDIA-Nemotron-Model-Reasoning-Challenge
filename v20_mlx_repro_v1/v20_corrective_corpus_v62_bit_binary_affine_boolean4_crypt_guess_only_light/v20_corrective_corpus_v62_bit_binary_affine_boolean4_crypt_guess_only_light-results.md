# v20_corrective_corpus_v62_bit_binary_affine_boolean4_crypt_guess_only_light

- created_at: 2026-04-28T17:58:58.905232+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` shows `Cryptarithm (Guess)` is the hardest slice, and report 67 says explicit answer-conditioned operator-semantics replay may help accuracy even if strict identifiability remains unsolved, so this branch isolates lighter guess-only replay.
- local target: current best local300 `0.846667` -> aim for `> 0.9` while testing whether pure guess replay helps without any added cryptarithm-deduce mass.
- status: bundle generated; MLX training is intentionally paused to reduce host RAM, latest observed step is `1`, and model score is not yet measured.
- planned run name: `v20_mlx_v62_bit_binary_affine_boolean4_crypt_guess_only_light_mlxdir_mb1_nobc_ckpt20`
- runtime status: `paused`
- latest observed step: `1`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Reuse the same narrow exact `binary_affine_xor` / `boolean4` verified core as v34 for the main bit lane.
- Keep the existing local numeric/cipher rescue rows, then add only lighter explicit `cryptarithm_guess` replay.
- Use this branch as the guess-only light control against v63 and the mixed branches.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- crypt_guess_support_unique: 140
- selected_unique_rows: 1730
- selected_repeated_rows: 8866

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 1
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v62_binary_answer_only_affine_boolean4_crypt_guess_only_light: 418
- v62_binary_manual_affine_boolean4_crypt_guess_only_light: 347
- v62_binary_verified_affine_boolean4_crypt_guess_only_light: 7605
- v62_cipher_guardrail: 10
- v62_crypt_guess_light: 462
- v62_numeric_guess_rescue: 24

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v62_bit_binary_affine_boolean4_crypt_guess_only_light_bundle.jsonl
- base_examples: 7830
- overlay_examples: 8866
- total_examples: 16696
- total_steps: 523
- total_tokens: 30733894
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1730
