# cuda-train-data-analysis-v1 latest snapshot

- generated_at_utc: `2026-04-01T14:05:52.481700+00:00`
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

## Current pass1 manual pack

| audit_focus | family | rows |
| --- | --- | --- |
| symbol_numeric_same_op | symbol_equation | 330 |
| symbol_glyph_multiset | symbol_equation | 46 |
| binary_low_gap | bit_manipulation | 6 |

## Key changes in this snapshot

- `text_decryption`: all 971 previously manual rows are now `answer_only_keep` via clean gold-answer completion of missing monoalphabetic mappings.
- `bit_manipulation`: the structured-byte library now keeps the conservative repeated formula family while spanning `shl/shr` through shifts `1..7`; selected `choose`/`majority` families and second-pass not-structured formulas recover a larger exact slice.
- `bit_manipulation`: for training safety, structured binary promotions are re-audited under leave-one-out support. Rows whose evidence depends on the row itself or on prompt-exact singleton curation are retained only as `answer_only_keep`, not as trace-ready teachers.
- `bit_manipulation`: ternary-varset hybrid consensus was rechecked under the same unique-output gate and stays zero-gain on current train; inverted ternary hybrid candidates remain disabled because they destabilized existing answer-only consensus rows during validation.
- `symbol_equation/numeric_2x2`: manual curation pass1 now covers exact prompt-backed rules (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`, `comp99_abs_diff_2d`), further shrinking the unresolved symbol-numeric queue.
- `symbol_equation/numeric_2x2`: `38` query-only arithmetic lookalikes were rechecked; the remaining slice still stays manual (`38` same-op conflicts, `0` format ambiguities).
- `symbol_equation/glyph_len5`: 70 rows satisfy multiset mapping and 46 also satisfy a global output-order DAG, but exact examples-only rechecks still yield `0` unique query strings (`33` query-unseen, `12` ambiguous-multiset, `1` ambiguous-order, `0` no-multiset), so glyph rows stay manual.

