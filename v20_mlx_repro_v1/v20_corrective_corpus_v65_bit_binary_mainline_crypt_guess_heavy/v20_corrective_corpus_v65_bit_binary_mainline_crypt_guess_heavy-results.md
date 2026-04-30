# v20_corrective_corpus_v65_bit_binary_mainline_crypt_guess_heavy

- created_at: 2026-04-28T20:52:10.905341+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: `README.md` shows `Cryptarithm (Guess)` is the hardest slice, so this branch keeps the broader v11 bit mainline and adds heavier explicit guess replay.
- local target: current best local300 `0.846667` -> aim for `> 0.9` while testing whether a broader bit-focused base plus heavy crypt guess replay outperforms both plain v11 and the narrower v63 control.
- status: bundle generated; detached queue/watch armed, model score not yet measured.
- planned run name: `v20_mlx_v65_bit_binary_mainline_crypt_guess_heavy_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Retain the broader v11 bit-binary mainline core that already covers the local BIT / numeric_guess / cipher residual lane.
- Add heavier explicit `cryptarithm_guess` replay because `README.md` shows that slice starts at `0/164` on the base model.
- Use this branch as the broad-bit plus guess-heavy comparator against plain v11 and the narrower v63 guess-only control.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- crypt_guess_support_unique: 140
- selected_unique_rows: 1644
- selected_repeated_rows: 4611

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_rescue: 1
- binary_verified_core: 1229
- cipher_guardrail: 1
- cryptarithm_guess_support: 140
- numeric_guess_rescue: 2

### Repeated rows by source mix

- v65_binary_answer_only_mainline: 307
- v65_binary_manual_rescue: 8
- v65_binary_verified_mainline: 3672
- v65_cipher_guardrail: 6
- v65_crypt_guess_heavy: 602
- v65_numeric_guess_rescue: 16

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v65_bit_binary_mainline_crypt_guess_heavy_bundle.jsonl
- base_examples: 7830
- overlay_examples: 4611
- total_examples: 12441
- total_steps: 390
- total_tokens: 29269418
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1644
