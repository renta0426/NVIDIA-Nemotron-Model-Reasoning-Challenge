# cuda-train-data-analysis-v1 overview

- generated_at_utc: `2026-03-25T21:22:34.351887+00:00`
- grounded_in: `README.md`, `try-cuda-train-data-analyst-plan.md`, `try-cuda-train-result.md`, `try-cuda-train.md`
- analyzed_rows: `9500`
- verified_trace_ready: `5863`
- answer_only_keep: `1085`
- manual_audit_priority: `2522`
- exclude_suspect: `30`

## Family summary

| family | rows | parse_ok_rate | verified_trace_ready | answer_only_keep | manual_audit_priority | exclude_suspect | suspect_labels | avg_hard_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 1.0 | 381 | 0 | 1202 | 19 | 19 | 4.2166 |
| gravity_constant | 1597 | 1.0 | 1597 | 0 | 0 | 0 | 0 | 1.0751 |
| roman_numeral | 1576 | 1.0 | 1576 | 0 | 0 | 0 | 0 | 1.1783 |
| symbol_equation | 1555 | 1.0 | 110 | 114 | 1320 | 11 | 11 | 3.1775 |
| text_decryption | 1576 | 1.0 | 605 | 971 | 0 | 0 | 0 | 1.7411 |
| unit_conversion | 1594 | 1.0 | 1594 | 0 | 0 | 0 | 0 | 1.5276 |

## Baseline teacher coverage vs recovered verified coverage

| family | total | baseline_solved | baseline_coverage | recovered_solved | recovered_coverage | delta_solved |
| --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 306 | 0.191 | 381 | 0.2378 | 75 |
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
| bit_manipulation | bit_other | 1498 |
| symbol_equation | glyph_len5 | 823 |
| symbol_equation | numeric_2x2 | 732 |
| bit_manipulation | bit_permutation_inversion | 104 |

## Highest-priority manual audit rows

| id | family | template_subtype | hard_score | audit_priority_score | audit_reasons | answer |
| --- | --- | --- | --- | --- | --- | --- |
| 4ac6f0cb | bit_manipulation | bit_other | 8.0 | 15.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous | 10100101 |
| 885c8b51 | bit_manipulation | bit_other | 8.0 | 15.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous | 00000001 |
| 97e7a57f | bit_manipulation | bit_other | 7.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous | 01010000 |
| b9e9dc9f | bit_manipulation | bit_other | 7.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous | 00000000 |
| f922f81c | bit_manipulation | bit_other | 7.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous | 00000000 |
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

