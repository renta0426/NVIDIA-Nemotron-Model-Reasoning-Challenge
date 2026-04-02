# cuda-train-data-analysis-v1 overview

- generated_at_utc: `2026-04-01T14:05:52.462676+00:00`
- grounded_in: `README.md`, `try-cuda-train-data-analyst-plan.md`, `try-cuda-train-result.md`, `try-cuda-train.md`
- analyzed_rows: `9500`
- verified_trace_ready: `6486`
- answer_only_keep: `1561`
- manual_audit_priority: `1427`
- exclude_suspect: `26`

## Family summary

| family | rows | parse_ok_rate | verified_trace_ready | answer_only_keep | manual_audit_priority | exclude_suspect | suspect_labels | avg_hard_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 1.0 | 1004 | 445 | 138 | 15 | 15 | 4.2166 |
| gravity_constant | 1597 | 1.0 | 1597 | 0 | 0 | 0 | 0 | 1.0751 |
| roman_numeral | 1576 | 1.0 | 1576 | 0 | 0 | 0 | 0 | 1.1783 |
| symbol_equation | 1555 | 1.0 | 110 | 145 | 1289 | 11 | 11 | 3.1775 |
| text_decryption | 1576 | 1.0 | 605 | 971 | 0 | 0 | 0 | 1.7411 |
| unit_conversion | 1594 | 1.0 | 1594 | 0 | 0 | 0 | 0 | 1.5276 |

## Baseline teacher coverage vs recovered verified coverage

| family | total | baseline_solved | baseline_coverage | recovered_solved | recovered_coverage | delta_solved |
| --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 306 | 0.191 | 1004 | 0.6267 | 698 |
| gravity_constant | 1597 | 0 | 0.0 | 1597 | 1.0 | 1597 |
| roman_numeral | 1576 | 1576 | 1.0 | 1576 | 1.0 | 0 |
| symbol_equation | 1555 | 0 | 0.0 | 110 | 0.0707 | 110 |
| text_decryption | 1576 | 0 | 0.0 | 605 | 0.3839 | 605 |
| unit_conversion | 1594 | 1594 | 1.0 | 1594 | 1.0 | 0 |

## Top template buckets

| family | template_subtype | rows |
| --- | --- | --- |
| gravity_constant | gravity_half_g_t2 | 1597 |
| unit_conversion | unit_fixed_ratio | 1594 |
| roman_numeral | roman_standard | 1576 |
| text_decryption | text_monoalphabetic | 1576 |
| bit_manipulation | bit_structured_byte_formula | 851 |
| symbol_equation | glyph_len5 | 823 |
| symbol_equation | numeric_2x2 | 732 |
| bit_manipulation | bit_other | 652 |
| bit_manipulation | bit_permutation_inversion | 99 |

## Highest-priority manual audit rows

| id | family | template_subtype | hard_score | audit_priority_score | audit_reasons | answer |
| --- | --- | --- | --- | --- | --- | --- |
| 065abaf6 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | &/:\ |
| 3f67321d | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | }"[} |
| 4bb8c6cd | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | ]}\! |
| 50ba5396 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | \]]@ |
| 56efc838 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | }$?( |
| 5a3eaf6f | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | \{}" |
| 71d91445 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | } |
| 9d20c8a7 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | ]]]} |
| a40497f9 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | %]\< |
| a85864a9 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | (\}: |
| b13d511a | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | \&[[ |
| be7101dc | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | \:%# |
| d7e5414c | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | \|%\\ |
| dc240ebd | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | `}:} |
| ec2099f5 | symbol_equation | glyph_len5 | 9.0 | 14.0 | symbol_length_mismatch\|symbol_solver_unverified | :]'\ |
| 069dbaab | bit_manipulation | bit_other | 6.0 | 14.0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00010000 |
| 101410e4 | bit_manipulation | bit_other | 6.0 | 14.0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10001101 |
| 12154247 | bit_manipulation | bit_other | 6.0 | 14.0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10111101 |
| 12e0ac8c | bit_manipulation | bit_other | 6.0 | 14.0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10101001 |
| 2230fad0 | bit_manipulation | bit_other | 6.0 | 14.0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 01001010 |

