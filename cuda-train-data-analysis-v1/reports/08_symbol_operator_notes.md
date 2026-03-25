# cuda-train-data-analysis-v1 symbol operator audit notes

## Symbol numeric operator summary

| template_subtype | symbol_query_operator | selection_tier | symbol_numeric_formula_name | rows |
| --- | --- | --- | --- | --- |
| glyph_len5 |  | manual_audit_priority |  | 823 |
| numeric_2x2 | + | manual_audit_priority |  | 90 |
| numeric_2x2 | - | manual_audit_priority |  | 88 |
| numeric_2x2 | * | manual_audit_priority |  | 73 |
| numeric_2x2 | / | manual_audit_priority |  | 17 |
| numeric_2x2 | @ | manual_audit_priority |  | 14 |
| numeric_2x2 | % | manual_audit_priority |  | 13 |
| numeric_2x2 | : | manual_audit_priority |  | 13 |
| numeric_2x2 | ! | manual_audit_priority |  | 12 |
| numeric_2x2 | [ | manual_audit_priority |  | 12 |
| numeric_2x2 | ^ | manual_audit_priority |  | 12 |
| numeric_2x2 | ` | manual_audit_priority |  | 12 |
| numeric_2x2 | { | manual_audit_priority |  | 12 |
| numeric_2x2 | " | manual_audit_priority |  | 11 |
| numeric_2x2 | $ | manual_audit_priority |  | 11 |
| numeric_2x2 | + | answer_only_keep | concat_yx | 11 |
| numeric_2x2 | < | manual_audit_priority |  | 10 |
| numeric_2x2 | } | manual_audit_priority |  | 10 |
| numeric_2x2 | ) | manual_audit_priority |  | 9 |
| numeric_2x2 | + | verified_trace_ready | concat_yx | 9 |
| numeric_2x2 | \ | manual_audit_priority |  | 9 |
| numeric_2x2 | # | manual_audit_priority |  | 7 |
| numeric_2x2 | & | manual_audit_priority |  | 7 |
| numeric_2x2 | * | answer_only_keep | concat_yx | 7 |
| numeric_2x2 | > | manual_audit_priority |  | 7 |
| numeric_2x2 | ? | manual_audit_priority |  | 7 |
| numeric_2x2 | ] | manual_audit_priority |  | 7 |
| numeric_2x2 | ' | manual_audit_priority |  | 6 |
| numeric_2x2 | * | verified_trace_ready | concat_yx | 6 |
| numeric_2x2 | \| | manual_audit_priority |  | 5 |
| numeric_2x2 | ( | manual_audit_priority |  | 4 |
| numeric_2x2 | - | answer_only_keep | abs_diff_2d | 4 |
| numeric_2x2 | - | manual_audit_priority | comp99_abs_diff_2d | 4 |
| numeric_2x2 | ( | verified_trace_ready | x_minus_y | 3 |
| numeric_2x2 | * | exclude_suspect | x_plus_y | 3 |
| numeric_2x2 | + | answer_only_keep | x_plus_y | 3 |
| numeric_2x2 | - | answer_only_keep | comp99_abs_diff_2d | 3 |
| numeric_2x2 | - | verified_trace_ready | x_minus_y | 3 |
| numeric_2x2 | ? | verified_trace_ready | concat_xy | 3 |
| numeric_2x2 | { | verified_trace_ready | concat_xy | 3 |

## Glyph multiset summary

| glyph_multiset_possible | glyph_order_acyclic | selection_tier | rows |
| --- | --- | --- | --- |
| False | False | manual_audit_priority | 378 |
| False | True | manual_audit_priority | 375 |
| True | True | manual_audit_priority | 46 |
| True | False | manual_audit_priority | 24 |

## Top symbol manual-audit queue

| id | template_subtype | symbol_query_operator | symbol_same_operator_example_count | hard_score | answer | query_raw |
| --- | --- | --- | --- | --- | --- | --- |
| 5c9f274a | glyph_len5 |  | 0 | 7.0 | :[`` | }:*?: |
| e401ee4f | glyph_len5 |  | 0 | 7.0 | ^^@} | [<*"> |
| eb1a62f7 | glyph_len5 |  | 0 | 7.0 | >!>} | )}*>) |
| f4f92956 | glyph_len5 |  | 0 | 7.0 | (`)) | ()"%} |
| 8962872b | glyph_len5 |  | 0 | 6.0 | %`& | ``?`\ |
| 9fdb18b7 | glyph_len5 |  | 0 | 6.0 | ^} | \|%-^^ |
| be7a9eb1 | glyph_len5 |  | 0 | 6.0 | []`' | ?]&[] |
| e582df31 | glyph_len5 |  | 0 | 6.0 | }@ | "'?]@ |
| 02664ad5 | glyph_len5 |  | 0 | 5.0 | :}' | !}-(! |
| 0d4b2baa | glyph_len5 |  | 0 | 5.0 | :(\|# | :(*\|# |
| 1d10ccaf | glyph_len5 |  | 0 | 5.0 | <({& | <(*{& |
| 24b2d8eb | glyph_len5 |  | 0 | 5.0 | /[:` | `!*/[ |
| 26a2a1b8 | glyph_len5 |  | 0 | 5.0 | (: | (\#</ |
| 51352792 | glyph_len5 |  | 0 | 5.0 | `"<` | "/*\|" |
| 52f499f4 | glyph_len5 |  | 0 | 5.0 | $[^% | /(>}@ |
| 64553a64 | glyph_len5 |  | 0 | 5.0 | }#' | !@"`/ |
| 97abca56 | glyph_len5 |  | 0 | 5.0 | `#:: | (:*`' |
| a77be9fa | glyph_len5 |  | 0 | 5.0 | [" | {>\|$[ |
| ae6be599 | glyph_len5 |  | 0 | 5.0 | #` | $?+]$ |
| afdb7326 | glyph_len5 |  | 0 | 5.0 | %\ | @^%(^ |
| c9e16aff | glyph_len5 |  | 0 | 5.0 | ]:(] | (]*]: |
| fc137acd | glyph_len5 |  | 0 | 5.0 | ^^{> | )#*[` |
| 0625f633 | glyph_len5 |  | 0 | 4.0 | @@// | ))*!( |
| 3b7148f6 | glyph_len5 |  | 0 | 4.0 | &&$ | &)+)\ |
| 771472d6 | glyph_len5 |  | 0 | 4.0 | -'? | ?'-\\ |

Observation: `numeric_2x2` is not one template; it splits by operator, and some operators are already recoverable with row-local formula search while `glyph_len5` remains structurally unsolved.
