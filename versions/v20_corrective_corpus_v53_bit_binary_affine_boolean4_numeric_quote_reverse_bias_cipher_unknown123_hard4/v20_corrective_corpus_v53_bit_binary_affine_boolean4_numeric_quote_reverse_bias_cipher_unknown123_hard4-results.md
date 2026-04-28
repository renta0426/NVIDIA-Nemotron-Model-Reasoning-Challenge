# v20_corrective_corpus_v53_bit_binary_affine_boolean4_numeric_quote_reverse_bias_cipher_unknown123_hard4

- created_at: 2026-04-28T16:52:37.256739+00:00
- README basis: deterministic boxed-answer evaluation with `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, and `max_model_len=8192`.
- analysis basis: combine `cuda-train-data-analysis-v1/reports/67_aopen_symbol_wall_breakthrough_assessment.md` for low-ratio numeric operator support and `reports/06_text_unknown_notes.md` for safe monoalphabetic completion, but isolate the `"`-only numeric slice, bias repeats toward reverse-oriented rows, and widen cipher to unknown-char `{1,2,3}` with `hard_score >= 4`.
- local target: current best local300 `0.846667` -> aim for `> 0.9` by preserving v34's exact affine/boolean4 bit core and testing whether reverse-biased quote rows plus the unknown123 cipher tail outperform the other quote/star branches.
- status: bundle generated; model score not yet measured.
- planned run name: `v20_mlx_v53_bit_binary_affine_boolean4_numeric_quote_reverse_bias_cipher_unknown123_hard4_mlxdir_mb1_nobc_ckpt20`
- runtime status: `queued`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the checked-in `04-08-16-14` snapshot as the base mass instead of changing the backbone.
- Reuse the same narrow exact `binary_affine_xor` / `boolean4` verified core as v34 for the main bit lane.
- Increase both local numeric/cipher rescue repeats, then add only the `"` numeric operator rows with an extra reverse-oriented repeat bonus and the harder cipher slice widened to `unknown_char_count in {1,2,3}`.
- Use this branch as the unknown123 + reverse counterpart to v51 so the quote lane's full comparison grid is complete.

## Selection

- curated_binary_verified_unique: 1229
- curated_binary_answer_only_unique: 271
- curated_binary_total_unique: 1500
- manual_binary_unique: 87
- numeric_quote_support_unique: 13
- numeric_reverse_bonus_unique: 6
- cipher_unknown123_hard4_support_unique: 106
- selected_unique_rows: 1709
- selected_repeated_rows: 8631

### Unique rows by bucket

- binary_answer_only_support: 271
- binary_manual_support: 87
- binary_verified_core: 1229
- cipher_guardrail: 107
- numeric_guess_rescue: 15

### Repeated rows by source mix

- v53_binary_answer_only_affine_boolean4_numeric_quote_reverse_bias_cipher_unknown123_hard4: 418
- v53_binary_manual_affine_boolean4_numeric_quote_reverse_bias_cipher_unknown123_hard4: 347
- v53_binary_verified_affine_boolean4_numeric_quote_reverse_bias_cipher_unknown123_hard4: 7605
- v53_cipher_numeric_quote_reverse_bias_cipher_unknown123_hard4: 197
- v53_numeric_guess_quote_reverse_bias_cipher_unknown123_hard4: 64

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

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v20_corrective_corpus_v53_bit_binary_affine_boolean4_numeric_quote_reverse_bias_cipher_unknown123_hard4_bundle.jsonl
- base_examples: 7830
- overlay_examples: 8631
- total_examples: 16461
- total_steps: 515
- total_tokens: 30707626
- max_seq_len: 7971
- retokenized_overlay_problem_count: 1709
