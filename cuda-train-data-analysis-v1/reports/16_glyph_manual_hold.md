# cuda-train-data-analysis-v1 glyph manual hold

## Decision

- pass1 glyph rows reviewed: `46`
- rows promoted: `0`
- rows newly excluded: `0`
- decision: keep all glyph pass1 rows in `manual_audit_priority`.

## Why they stay manual

- every pass1 glyph row still carries `symbol_length_mismatch|symbol_solver_unverified`.
- the strongest 5 rows in `glyph_query_consistent_v1.csv` only show that query+gold is compatible with the coarse multiset+order model; they do **not** make the model unique.
- per `README.md`, leaderboard score is direct final-answer accuracy, so teaching non-unique glyph hypotheses is riskier than leaving these rows manual.

## Glyph query-consistent rows

| id | hard_score | answer | query_raw | audit_reasons |
| --- | --- | --- | --- | --- |
| f4f92956 | 7.0 | (`)) | ()"%} | symbol_length_mismatch\|symbol_solver_unverified |
| 64553a64 | 5.0 | }#' | !@"`/ | symbol_length_mismatch\|symbol_solver_unverified |
| 97abca56 | 5.0 | `#:: | (:*`' | symbol_length_mismatch\|symbol_solver_unverified |
| a77be9fa | 5.0 | [" | {>\|$[ | symbol_length_mismatch\|symbol_solver_unverified |
| afdb7326 | 5.0 | %\ | @^%(^ | symbol_length_mismatch\|symbol_solver_unverified |

## Top glyph pass1 rows

| id | hard_score | answer | query_raw | audit_reasons |
| --- | --- | --- | --- | --- |
| 5c9f274a | 7.0 | :[`` | }:*?: | symbol_length_mismatch\|symbol_solver_unverified |
| e401ee4f | 7.0 | ^^@} | [<*"> | symbol_length_mismatch\|symbol_solver_unverified |
| eb1a62f7 | 7.0 | >!>} | )}*>) | symbol_length_mismatch\|symbol_solver_unverified |
| f4f92956 | 7.0 | (`)) | ()"%} | symbol_length_mismatch\|symbol_solver_unverified |
| 8962872b | 6.0 | %`& | ``?`\ | symbol_length_mismatch\|symbol_solver_unverified |
| 9fdb18b7 | 6.0 | ^} | \|%-^^ | symbol_length_mismatch\|symbol_solver_unverified |
| be7a9eb1 | 6.0 | []`' | ?]&[] | symbol_length_mismatch\|symbol_solver_unverified |
| e582df31 | 6.0 | }@ | "'?]@ | symbol_length_mismatch\|symbol_solver_unverified |
| 02664ad5 | 5.0 | :}' | !}-(! | symbol_length_mismatch\|symbol_solver_unverified |
| 0d4b2baa | 5.0 | :(\|# | :(*\|# | symbol_length_mismatch\|symbol_solver_unverified |
| 1d10ccaf | 5.0 | <({& | <(*{& | symbol_length_mismatch\|symbol_solver_unverified |
| 24b2d8eb | 5.0 | /[:` | `!*/[ | symbol_length_mismatch\|symbol_solver_unverified |
| 26a2a1b8 | 5.0 | (: | (\#</ | symbol_length_mismatch\|symbol_solver_unverified |
| 51352792 | 5.0 | `"<` | "/*\|" | symbol_length_mismatch\|symbol_solver_unverified |
| 52f499f4 | 5.0 | $[^% | /(>}@ | symbol_length_mismatch\|symbol_solver_unverified |
| 64553a64 | 5.0 | }#' | !@"`/ | symbol_length_mismatch\|symbol_solver_unverified |
| 97abca56 | 5.0 | `#:: | (:*`' | symbol_length_mismatch\|symbol_solver_unverified |
| a77be9fa | 5.0 | [" | {>\|$[ | symbol_length_mismatch\|symbol_solver_unverified |
| ae6be599 | 5.0 | #` | $?+]$ | symbol_length_mismatch\|symbol_solver_unverified |
| afdb7326 | 5.0 | %\ | @^%(^ | symbol_length_mismatch\|symbol_solver_unverified |
| c9e16aff | 5.0 | ]:(] | (]*]: | symbol_length_mismatch\|symbol_solver_unverified |
| fc137acd | 5.0 | ^^{> | )#*[` | symbol_length_mismatch\|symbol_solver_unverified |
| 0625f633 | 4.0 | @@// | ))*!( | symbol_length_mismatch\|symbol_solver_unverified |
| 3b7148f6 | 4.0 | &&$ | &)+)\ | symbol_length_mismatch\|symbol_solver_unverified |
| 771472d6 | 4.0 | -'? | ?'-\\ | symbol_length_mismatch\|symbol_solver_unverified |
| 93e6d0c0 | 4.0 | ^< | ^\|(>^ | symbol_length_mismatch\|symbol_solver_unverified |
| b4b73143 | 4.0 | >\: | >!%!/ | symbol_length_mismatch\|symbol_solver_unverified |
| 177f0c22 | 3.0 | /> | >?-#[ | symbol_length_mismatch\|symbol_solver_unverified |
| 1a28140b | 3.0 | %`& | "[*#/ | symbol_length_mismatch\|symbol_solver_unverified |
| 2d624cab | 3.0 | ![)] | >)`#' | symbol_length_mismatch\|symbol_solver_unverified |
| 2e1b9d84 | 3.0 | ]>" | [`+'} | symbol_length_mismatch\|symbol_solver_unverified |
| 58eadc55 | 3.0 | !# | @@\|@` | symbol_length_mismatch\|symbol_solver_unverified |
| 6c7f24b7 | 3.0 | ^ | $'-^$ | symbol_length_mismatch\|symbol_solver_unverified |
| 76587d66 | 3.0 | ] | ]`-]> | symbol_length_mismatch\|symbol_solver_unverified |
| 82c9f137 | 3.0 | &% | {&-?# | symbol_length_mismatch\|symbol_solver_unverified |
| 86ccbdf7 | 3.0 | :\| | \|?-?` | symbol_length_mismatch\|symbol_solver_unverified |
| c9780577 | 3.0 | )? | \{+{\| | symbol_length_mismatch\|symbol_solver_unverified |
| 0dce4039 | 2.0 | -@/ | )!-#> | symbol_length_mismatch\|symbol_solver_unverified |
| 42bde66c | 2.0 | >) | #<+#/ | symbol_length_mismatch\|symbol_solver_unverified |
| c69b17bf | 2.0 | ?) | )^-$) | symbol_length_mismatch\|symbol_solver_unverified |

Interpretation: even the best glyph candidates remain underdetermined. They are suitable for future human reasoning work, but not for safe automatic promotion or exclusion in the current pass.

