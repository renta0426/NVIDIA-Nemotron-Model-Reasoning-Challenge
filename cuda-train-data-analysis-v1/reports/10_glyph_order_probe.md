# cuda-train-data-analysis-v1 glyph order probe notes

## Glyph summary

| glyph_multiset_possible | glyph_order_acyclic | selection_tier | rows |
| --- | --- | --- | --- |
| False | False | answer_only_keep | 378 |
| False | True | answer_only_keep | 375 |
| True | True | answer_only_keep | 46 |
| True | False | answer_only_keep | 24 |

- `glyph_multiset_possible`: `70` rows
- `glyph_multiset_possible && glyph_order_acyclic`: `46` rows

Interpretation: these rows already admit both a multiset-style character contribution hypothesis and a globally consistent output ordering over symbols. They are the strongest `glyph_len5` manual-audit candidates because only mapping/order unification remains unresolved.

## Top glyph order-compatible rows

| id | hard_score | answer | query_raw | audit_reasons |
| --- | --- | --- | --- | --- |
| 5c9f274a | 7.0 | :[`` | }:*?: |  |
| e401ee4f | 7.0 | ^^@} | [<*"> |  |
| eb1a62f7 | 7.0 | >!>} | )}*>) |  |
| f4f92956 | 7.0 | (`)) | ()"%} |  |
| 8962872b | 6.0 | %`& | ``?`\ |  |
| 9fdb18b7 | 6.0 | ^} | \|%-^^ |  |
| be7a9eb1 | 6.0 | []`' | ?]&[] |  |
| e582df31 | 6.0 | }@ | "'?]@ |  |
| 02664ad5 | 5.0 | :}' | !}-(! |  |
| 0d4b2baa | 5.0 | :(\|# | :(*\|# |  |
| 1d10ccaf | 5.0 | <({& | <(*{& |  |
| 24b2d8eb | 5.0 | /[:` | `!*/[ |  |
| 26a2a1b8 | 5.0 | (: | (\#</ |  |
| 51352792 | 5.0 | `"<` | "/*\|" |  |
| 52f499f4 | 5.0 | $[^% | /(>}@ |  |
| 64553a64 | 5.0 | }#' | !@"`/ |  |
| 97abca56 | 5.0 | `#:: | (:*`' |  |
| a77be9fa | 5.0 | [" | {>\|$[ |  |
| ae6be599 | 5.0 | #` | $?+]$ |  |
| afdb7326 | 5.0 | %\ | @^%(^ |  |
| c9e16aff | 5.0 | ]:(] | (]*]: |  |
| fc137acd | 5.0 | ^^{> | )#*[` |  |
| 0625f633 | 4.0 | @@// | ))*!( |  |
| 3b7148f6 | 4.0 | &&$ | &)+)\ |  |
| 771472d6 | 4.0 | -'? | ?'-\\ |  |
| 93e6d0c0 | 4.0 | ^< | ^\|(>^ |  |
| b4b73143 | 4.0 | >\: | >!%!/ |  |
| 177f0c22 | 3.0 | /> | >?-#[ |  |
| 1a28140b | 3.0 | %`& | "[*#/ |  |
| 2d624cab | 3.0 | ![)] | >)`#' |  |
| 2e1b9d84 | 3.0 | ]>" | [`+'} |  |
| 58eadc55 | 3.0 | !# | @@\|@` |  |
| 6c7f24b7 | 3.0 | ^ | $'-^$ |  |
| 76587d66 | 3.0 | ] | ]`-]> |  |
| 82c9f137 | 3.0 | &% | {&-?# |  |
| 86ccbdf7 | 3.0 | :\| | \|?-?` |  |
| c9780577 | 3.0 | )? | \{+{\| |  |
| 0dce4039 | 2.0 | -@/ | )!-#> |  |
| 42bde66c | 2.0 | >) | #<+#/ |  |
| c69b17bf | 2.0 | ?) | )^-$) |  |

