# v20_corrective_corpus_v8_mainline

- created_at: 2026-04-22T10:45:58+00:00
- strategy note: versions/v20_to_088_reassessment_2026-04-18.md
- README basis: deterministic boxed-answer evaluation, bit_manipulation as primary score source, tokenization-aware supervision, and symbol exact-transduction weaknesses called out in the A-Open note.
- status: bundle generated; model score not yet measured.

## Strategy

- One major run only: BIT-core mainline with targeted symbol exact lanes and minimal easy-family guardrails.
- Allocation target: roughly 75-80% BIT, 15-20% symbol, <=5% guardrail.
- Latest reference run remains v7-1; v8 here is a new data-generation branch, not a score claim.

## Selected Unique Rows

- binary_structured_exact_core: 224
- binary_logic_exact: 88
- binary_permutation_exact: 64
- binary_prompt_local_exact: 96
- symbol_numeric_exact: 48
- symbol_glyph_exact: 48
- surface_numeral_boxed: 18
- surface_cipher_boxed: 4
- surface_unit_tail: 4
- easy_gravity_fragile: 4

## Allocation Check

- bit_unique: 472 (78.93%)
- symbol_unique: 96 (16.05%)
- guardrail_unique: 30 (5.02%)
- total_unique: 598

## Hard Anchors

- binary_hard_hits: 15
- symbol_hard_hits: 8

## Bundle

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v8_mainline_bundle.jsonl
- base_examples: 7828
- overlay_examples: 1183
- total_examples: 9011
- total_tokens: 28199629
- max_seq_len: 7971

## Canonical Validation

- passed: True
- errors: []
