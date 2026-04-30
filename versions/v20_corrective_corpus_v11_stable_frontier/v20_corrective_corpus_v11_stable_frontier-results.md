# v20_corrective_corpus_v11_stable_frontier results

- created_at: 2026-04-30T08:42:01+00:00
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
