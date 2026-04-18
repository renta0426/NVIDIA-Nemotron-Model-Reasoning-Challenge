# cuda-train-data-analysis-v1 overview

- generated_at_utc: `2026-04-18T07:36:50.809905+00:00`
- grounded_in: `README.md`, `try-cuda-train-data-analyst-plan.md`, `try-cuda-train-result.md`, `try-cuda-train.md`
- analyzed_rows: `9500`
- verified_trace_ready: `6711`
- answer_only_keep: `2652`
- manual_audit_priority: `113`
- exclude_suspect: `24`

## Family summary

| family | rows | parse_ok_rate | verified_trace_ready | answer_only_keep | manual_audit_priority | exclude_suspect | suspect_labels | avg_hard_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 1.0 | 1229 | 271 | 87 | 15 | 15 | 4.2166 |
| gravity_constant | 1597 | 1.0 | 1597 | 0 | 0 | 0 | 0 | 1.0751 |
| roman_numeral | 1576 | 1.0 | 1576 | 0 | 0 | 0 | 0 | 1.1783 |
| symbol_equation | 1555 | 1.0 | 110 | 1410 | 26 | 9 | 9 | 3.1775 |
| text_decryption | 1576 | 1.0 | 605 | 971 | 0 | 0 | 0 | 1.7411 |
| unit_conversion | 1594 | 1.0 | 1594 | 0 | 0 | 0 | 0 | 1.5276 |

## Baseline teacher coverage vs recovered verified coverage

| family | total | baseline_solved | baseline_coverage | recovered_solved | recovered_coverage | delta_solved |
| --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 306 | 0.191 | 1229 | 0.7672 | 923 |
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
| bit_manipulation | bit_structured_byte_formula | 830 |
| symbol_equation | glyph_len5 | 823 |
| symbol_equation | numeric_2x2 | 732 |
| bit_manipulation | bit_other | 532 |
| bit_manipulation | bit_prompt_local_exact_formula | 142 |
| bit_manipulation | bit_permutation_inversion | 98 |

## Highest-priority manual audit rows

| id | family | template_subtype | hard_score | audit_priority_score | audit_reasons | answer |
| --- | --- | --- | --- | --- | --- | --- |
| 069dbaab | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00010000 |
| 101410e4 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10001101 |
| 12154247 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10111101 |
| 2230fad0 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 01001010 |
| 257e7158 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00001001 |
| 264b2118 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00010100 |
| 2841d283 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10010111 |
| 44fb2f96 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 11001110 |
| 45ae41c8 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 11011101 |
| 512e1118 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 11111110 |
| 5d060d45 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00000000 |
| 8211fd2f | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10111111 |
| 8631d7b6 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00000000 |
| 9b1761fb | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10000000 |
| a8f2c2b9 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10011111 |
| b61afd75 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00101101 |
| d2503f8b | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 00111010 |
| d2fc4490 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 01010110 |
| e612387f | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 01011001 |
| fcbb35e3 | bit_manipulation | bit_other | 6.0 | 14.5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_ambiguous\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous | 10101101 |

