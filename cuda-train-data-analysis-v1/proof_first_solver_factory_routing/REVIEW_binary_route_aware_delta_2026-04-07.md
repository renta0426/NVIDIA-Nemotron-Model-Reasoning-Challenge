# Review: binary_route_aware_delta.csv (2026-04-07)

## Scope

- Target: `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/artifacts/binary_route_aware_delta.csv`
- Goal: full-dataset reinspection for hallucination-like content, CoT contradictions, route/header mismatch, answer leakage, and source-ledger inconsistency.
- README.md evaluation contract referenced during review: Accuracy metric, boxed-answer-priority extraction, temperature 0.0, max_tokens 7680, max_lora_rank 32.

## Method

- Loaded all 197 rows from the delta CSV.
- Cross-checked each row against `cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv`.
- Cross-checked exact-route rows against seed configs from `cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1_1/generate_bit_synth_exact_trace_cot_v1_1.py`.
- Revalidated full exact traces with the helper's canonical `validate_seed_row(...)` logic.
- Revalidated sanitized exact traces with the builder's `validate_sanitized_exact_cot(...)` logic.
- Revalidated coarse rows against the fixed closure-only template.
- Rechecked route header lines, boxed extraction consistency, answer leakage inside `<think>`, duplicate ids, assistant_style counts, and route count totals against the manifest.

## Result

- Rows inspected: 197
- Duplicate ids: 0
- Validation failures: 0
- Manifest row count match: yes
- Manifest assistant_style_counts match: yes
- Manifest route_label_counts match: yes

## Coverage Summary

- `route_closure_only`: 80
- `route_trace_full`: 106
- `route_trace_sanitized`: 11

- `bit_manipulation`: 80
- `bit_manipulation.binary_affine_xor`: 54
- `bit_manipulation.binary_bit_permutation_bijection`: 30
- `bit_manipulation.binary_bit_permutation_independent`: 1
- `bit_manipulation.binary_byte_transform`: 6
- `bit_manipulation.binary_structured_byte_formula_abstract`: 2
- `bit_manipulation.binary_three_bit_boolean`: 4
- `bit_manipulation.binary_two_bit_boolean`: 20

## Review Conclusion

- No material findings in the current `binary_route_aware_delta.csv` after full reinspection.
- At the row-integrity level, no hallucination-like unsupported route content, no detectable CoT contradiction against the encoded solver rule, and no answer leakage inside `<think>` were found.

## Residual Risk

- This review verifies dataset-row integrity, not downstream training behavior.
- It does not prove that the added rows improve local eval or leaderboard score; that requires the next training/eval work unit.