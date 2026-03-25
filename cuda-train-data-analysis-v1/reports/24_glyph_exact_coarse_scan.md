# cuda-train-data-analysis-v1 glyph exact coarse enumeration

## Purpose

Recheck the 46 round2 `glyph_len5` rows under the **strictest version of the current coarse glyph abstraction**: each input character either drops out or maps to exactly one output character, and output character order must be globally consistent with the example outputs.

## Decision

- rows checked: `46`
- `query_has_unseen_chars`: `33`
- `ambiguous_multiset`: `12`
- `ambiguous_order`: `1`
- `no_example_only_multiset`: `0`
- `unique_string`: `0`
- gold-matching unique strings: `0`
- promoted rows: `0`
- newly excluded rows: `0`

## Breakdown

| exact_coarse_status | multiset_unique | order_unique | rows |
| --- | --- | --- | --- |
| query_has_unseen_chars | False | False | 33 |
| ambiguous_multiset | False | False | 12 |
| ambiguous_order | True | False | 1 |

## Non-trivial rows under the exact coarse model

| id | exact_coarse_status | answer | predicted_answer | query_raw | predicted_multiset_json |
| --- | --- | --- | --- | --- | --- |
| 5c9f274a | ambiguous_multiset | :[`` |  | }:*?: |  |
| 0d4b2baa | ambiguous_multiset | :(\|# |  | :(*\|# |  |
| ae6be599 | ambiguous_multiset | #` |  | $?+]$ |  |
| 771472d6 | ambiguous_multiset | -'? |  | ?'-\\ |  |
| 177f0c22 | ambiguous_multiset | /> |  | >?-#[ |  |
| 58eadc55 | ambiguous_multiset | !# |  | @@\|@` |  |
| 6c7f24b7 | ambiguous_multiset | ^ |  | $'-^$ |  |
| 76587d66 | ambiguous_multiset | ] |  | ]`-]> |  |
| 86ccbdf7 | ambiguous_multiset | :\| |  | \|?-?` |  |
| 42bde66c | ambiguous_multiset | >) |  | #<+#/ |  |
| d3c1d2fb | ambiguous_multiset | )/ |  | ^:!]# |  |
| 28b0ff48 | ambiguous_multiset | '] |  | \|^-^^ |  |
| c9780577 | ambiguous_order | )? |  | \{+{\| | {"?": 1, "]": 3} |

## Query rows with unseen symbols

| id | answer | query_raw | glyph_query_unseen_chars |
| --- | --- | --- | --- |
| e401ee4f | ^^@} | [<*"> | <[ |
| eb1a62f7 | >!>} | )}*>) | * |
| f4f92956 | (`)) | ()"%} | "%( |
| 8962872b | %`& | ``?`\ | ` |
| 9fdb18b7 | ^} | \|%-^^ | - |
| be7a9eb1 | []`' | ?]&[] | ? |
| e582df31 | }@ | "'?]@ | @ |
| 02664ad5 | :}' | !}-(! | !( |
| 1d10ccaf | <({& | <(*{& | & |
| 24b2d8eb | /[:` | `!*/[ | !/ |
| 26a2a1b8 | (: | (\#</ | \ |
| 51352792 | `"<` | "/*\|" | * |
| 52f499f4 | $[^% | /(>}@ | ( |
| 64553a64 | }#' | !@"`/ | !/ |
| 97abca56 | `#:: | (:*`' | '(*` |
| a77be9fa | [" | {>\|$[ | >{ |
| afdb7326 | %\ | @^%(^ | @^ |
| c9e16aff | ]:(] | (]*]: | * |
| fc137acd | ^^{> | )#*[` | #` |
| 0625f633 | @@// | ))*!( | * |
| 3b7148f6 | &&$ | &)+)\ | &+ |
| 93e6d0c0 | ^< | ^\|(>^ | > |
| b4b73143 | >\: | >!%!/ | > |
| 1a28140b | %`& | "[*#/ | / |
| 2d624cab | ![)] | >)`#' | >` |
| 2e1b9d84 | ]>" | [`+'} | } |
| 82c9f137 | &% | {&-?# | & |
| 0dce4039 | -@/ | )!-#> | > |
| c69b17bf | ?) | )^-$) | ^ |
| dc93896e | [?< | ?<+// | + |

Interpretation: even after strengthening the current glyph abstraction to an exact examples-only enumeration, the round2 glyph slice still yields **zero** safe recoveries. Most rows immediately fail because the query introduces symbols that never appear in the examples; the rest remain ambiguous or structurally inconsistent. Under the `README.md` accuracy metric, this is negative evidence against trusting the current coarse glyph family as supervision.

