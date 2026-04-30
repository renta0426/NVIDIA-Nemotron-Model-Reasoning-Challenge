# v20_corrective_corpus_v11_stable_frontier results

- created_at: 2026-04-30T08:48:12+00:00
- README basis: README.md deterministic boxed-answer Accuracy contract.
- strategy note: versions/v11_stable_frontier_strategy_2026-04-30.md
- status: data generated and strategy-validated; model score not yet measured.

## Data Change Scale

- v10 overlay examples: `811`
- v11 overlay examples: `3499`
- overlay delta: `2688`
- base examples reused from v10 bundle: `7828`
- total examples: `11327`
- overlay share of total examples: `0.3089`

## V11 Lanes

- lane1_exact_program_trace_synthesis: `3094`
- lane2_hard_row_slot_table_closure: `68`
- lane4_answer_only_stabilizer: `226`
- lane5_surface_guardrail: `111`

## Source Mix

- v11_affine_program_trace_synth: `192`
- v11_answer_only_stabilizer: `226`
- v11_exact_program_trace_synth: `2750`
- v11_hard_row_slot_table_closure: `68`
- v11_mapping_program_trace_synth: `152`
- v11_surface_guardrail_from_v10: `111`

## Detailed Selection

- executable formula families: `456` unique formulas -> `2750` synthetic rows
- hard-row exact slot closure: `68` rows; skipped without supported executable formula: `['0245b9bb', '06881e47', '069dbaab', '0ec17d2e', '12154247', '132ec6ae', '14a72508', 'b9500f41']`
- affine XOR synthesis: `96` seed rows -> `192` rows
- bit mapping synthesis: `76` seed rows -> `152` rows
- answer-only stabilizers: `220` source problems -> `226` rows
- v10 surface guardrails retained after boxed normalization: `111` rows

## V10 Comparison

- overlay size multiplier vs v10: `4.31x`
- v10 source mix:
  - v10_manual_frontier: `48`
  - v10_numeral_surface_synth: `1`
  - v10_verified_frontier: `385`
  - v4_public_base: `318`
  - v6_binary_donor: `27`
  - v6_cipher_guardrail_donor: `6`
  - v6_gravity_guardrail_donor: `6`
  - v6_numeral_surface_donor: `10`
  - v6_symbol_prefix_donor: `4`
  - v6_unit_guardrail_donor: `6`
- v11 source mix:
  - v11_affine_program_trace_synth: `192`
  - v11_answer_only_stabilizer: `226`
  - v11_exact_program_trace_synth: `2750`
  - v11_hard_row_slot_table_closure: `68`
  - v11_mapping_program_trace_synth: `152`
  - v11_surface_guardrail_from_v10: `111`

## Validation

- passed: `True`
- errors: `[]`
- forbidden completion terms: none in accepted rows
- manual full-CoT rows: none in accepted rows
- bundle path: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v11_stable_frontier_bundle.jsonl`
- max sequence length: `7971`

## Strategy Fit

- Replaced v10 short answer/rule-name frontier supervision with executable BIT program traces.
- Kept manual no-solver rows out of full-CoT; they appear only as answer-only anchors when present.
- Kept narrow surface guardrails from v10 instead of broad symbol/glyph CoT.
- Generated a non-micro overlay change: thousands of new examples, not a few row edits.

## Bundle

- total_tokens: `29749477`
- total_masked_tokens: `2138027`
- total_unmasked_tokens: `27611450`
- total_steps: `355`
- category_counts: `{'bit_manipulation': 4956, 'cipher': 1670, 'cryptarithm_deduce': 639, 'cryptarithm_guess': 154, 'equation_numeric_deduce': 664, 'equation_numeric_guess': 126, 'gravity': 1073, 'numeral': 777, 'symbol_equation': 97, 'text_decryption': 87, 'unit_conversion': 1084}`
