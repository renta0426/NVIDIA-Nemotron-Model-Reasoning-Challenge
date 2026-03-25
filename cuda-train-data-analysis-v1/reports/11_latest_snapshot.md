# cuda-train-data-analysis-v1 latest snapshot

- generated_at_utc: `2026-03-25T17:21:15.663824+00:00`
- verified_trace_ready: `5862`
- answer_only_keep: `1075`
- manual_audit_priority: `2545`
- exclude_suspect: `18`

## Family summary

| family | rows | parse_ok_rate | verified_trace_ready | answer_only_keep | manual_audit_priority | exclude_suspect | suspect_labels | avg_hard_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 1.0 | 381 | 0 | 1213 | 8 | 8 | 4.2166 |
| gravity_constant | 1597 | 1.0 | 1597 | 0 | 0 | 0 | 0 | 1.0751 |
| roman_numeral | 1576 | 1.0 | 1576 | 0 | 0 | 0 | 0 | 1.1783 |
| symbol_equation | 1555 | 1.0 | 109 | 104 | 1332 | 10 | 10 | 3.1775 |
| text_decryption | 1576 | 1.0 | 605 | 971 | 0 | 0 | 0 | 1.7411 |
| unit_conversion | 1594 | 1.0 | 1594 | 0 | 0 | 0 | 0 | 1.5276 |

## Current pass1 manual pack

| audit_focus | family | rows |
| --- | --- | --- |
| symbol_numeric_same_op | symbol_equation | 373 |
| binary_low_gap | bit_manipulation | 150 |
| symbol_glyph_multiset | symbol_equation | 46 |

## Key changes in this snapshot

- `text_decryption`: all 971 previously manual rows are now `answer_only_keep` via clean gold-answer completion of missing monoalphabetic mappings.
- `bit_manipulation`: added simple byte-transform recovery (`shift`, `rotate`, `mask`) and recovered 11 extra verified rows.
- `symbol_equation/numeric_2x2`: manual curation pass1 now covers exact string-template rules (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`), shrinking the next symbol-numeric pass1 queue to 373 rows.
- `symbol_equation/glyph_len5`: 70 rows satisfy multiset mapping; 46 of them also satisfy a global output-order DAG and remain the sharpest glyph audit candidates.

