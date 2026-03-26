# cuda-train-data-analysis-v1 latest snapshot

- generated_at_utc: `2026-03-26T00:33:34.795095+00:00`
- verified_trace_ready: `6081`
- answer_only_keep: `1105`
- manual_audit_priority: `2288`
- exclude_suspect: `26`

## Family summary

| family | rows | parse_ok_rate | verified_trace_ready | answer_only_keep | manual_audit_priority | exclude_suspect | suspect_labels | avg_hard_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_manipulation | 1602 | 1.0 | 599 | 20 | 968 | 15 | 19 | 4.2166 |
| gravity_constant | 1597 | 1.0 | 1597 | 0 | 0 | 0 | 0 | 1.0751 |
| roman_numeral | 1576 | 1.0 | 1576 | 0 | 0 | 0 | 0 | 1.1783 |
| symbol_equation | 1555 | 1.0 | 110 | 114 | 1320 | 11 | 11 | 3.1775 |
| text_decryption | 1576 | 1.0 | 605 | 971 | 0 | 0 | 0 | 1.7411 |
| unit_conversion | 1594 | 1.0 | 1594 | 0 | 0 | 0 | 0 | 1.5276 |

## Current pass1 manual pack

| audit_focus | family | rows |
| --- | --- | --- |
| symbol_numeric_same_op | symbol_equation | 361 |
| binary_low_gap | bit_manipulation | 118 |
| symbol_glyph_multiset | symbol_equation | 46 |

## Key changes in this snapshot

- `text_decryption`: all 971 previously manual rows are now `answer_only_keep` via clean gold-answer completion of missing monoalphabetic mappings.
- `bit_manipulation`: added simple byte-transform recovery (`shift`, `rotate`, `mask`) and recovered 11 extra verified rows; current pass1 also excludes 11 low-gap affine mismatches whose unique rule conflicts with the gold label.
- `symbol_equation/numeric_2x2`: manual curation pass1 now covers exact prompt-backed rules (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`, `comp99_abs_diff_2d`), further shrinking the unresolved symbol-numeric queue.
- `symbol_equation/numeric_2x2`: `43` query-only arithmetic lookalikes were rechecked; the remaining slice still stays manual (`38` same-op conflicts, `5` format ambiguities).
- `symbol_equation/glyph_len5`: 70 rows satisfy multiset mapping and 46 also satisfy a global output-order DAG, but exact examples-only rechecks still yield `0` unique query strings (`33` query-unseen, `12` ambiguous-multiset, `1` ambiguous-order, `0` no-multiset), so glyph rows stay manual.

