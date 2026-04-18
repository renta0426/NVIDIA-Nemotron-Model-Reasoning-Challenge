# cuda-train-data-analysis-v1 latest snapshot

- generated_at_utc: `2026-04-18T07:36:50.831264+00:00`
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

## Current pass1 manual pack

| audit_focus | family | rows |
| --- | --- | --- |
| symbol_numeric_same_op | symbol_equation | 26 |
| binary_low_gap | bit_manipulation | 5 |

## Key changes in this snapshot

- `text_decryption`: all 971 previously manual rows are now `answer_only_keep` via clean gold-answer completion of missing monoalphabetic mappings.
- `bit_manipulation`: the structured-byte library now keeps the conservative repeated formula family while spanning `shl/shr` through shifts `1..7`; selected `choose`/`majority` families and second-pass not-structured formulas recover a larger exact slice.
- `bit_manipulation`: for training safety, structured binary promotions are re-audited under leave-one-out support. Rows whose evidence depends on the row itself or on prompt-exact singleton curation are retained only as `answer_only_keep`, not as trace-ready teachers.
- `bit_manipulation`: ternary-varset hybrid consensus was rechecked under the same unique-output gate and stays zero-gain on current train; inverted ternary hybrid candidates remain disabled because they destabilized existing answer-only consensus rows during validation.
- `symbol_equation/numeric_2x2`: manual curation pass1 now covers exact prompt-backed rules (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`, `comp99_abs_diff_2d`), further shrinking the unresolved symbol-numeric queue.
- `symbol_equation/numeric_2x2`: remaining non-suspect rows with `same_operator_example_count = 0` now move to `answer_only_keep` as raw final-answer supervision (`136` rows), because README evaluation is final-answer accuracy and there is no same-op evidence to justify trace promotion anyway.
- `symbol_equation/numeric_2x2`: `1` query-only arithmetic lookalikes were rechecked; the remaining slice still stays manual (`1` same-op conflicts, `0` format ambiguities).
- `symbol_equation/glyph_len5`: 70 rows satisfy multiset mapping and 46 also satisfy a global output-order DAG, but exact examples-only rechecks still yield no unique latent rule for the residual glyph slice. With no concrete suspect signal, the remaining glyph rows now stay only as answer-only training labels (`470` rows), not as trace-ready teachers.
- `symbol_equation`: prompt-only strict audit now records why rows fail verification (`unseen_query_operator=108`, `prompt_ambiguous=56`, `prompt_exact_conflict=55`, `support_gap=114`) without changing the existing tiers.
- `symbol_equation`: synthetic trace policy now separates `prompt_verified_trace=110` from `synthetic_trace_hypothesis=1368` and `no_trace_teacher=77`; gold-based candidate selection is required on `1254` rows, so these traces stay explicitly non-verified.

