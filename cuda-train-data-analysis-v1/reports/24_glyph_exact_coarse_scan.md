# cuda-train-data-analysis-v1 glyph exact coarse enumeration

## Purpose

Recheck the 46 round2 `glyph_len5` rows under the **strictest version of the current coarse glyph abstraction**: each input character either drops out or maps to exactly one output character, and output character order must be globally consistent with the example outputs.

## Decision

- rows checked: `0`
- `query_has_unseen_chars`: `0`
- `ambiguous_multiset`: `0`
- `ambiguous_order`: `0`
- `no_example_only_multiset`: `0`
- `unique_string`: `0`
- gold-matching unique strings: `0`
- promoted rows: `0`
- newly excluded rows: `0`

## Breakdown

| exact_coarse_status | multiset_unique | order_unique | rows |
| --- | --- | --- | --- |

## Non-trivial rows under the exact coarse model

| id | exact_coarse_status | answer | predicted_answer | query_raw | predicted_multiset_json |
| --- | --- | --- | --- | --- | --- |

## Query rows with unseen symbols

| id | answer | query_raw | glyph_query_unseen_chars |
| --- | --- | --- | --- |

Interpretation: even after strengthening the current glyph abstraction to an exact examples-only enumeration, the round2 glyph slice still yields **zero** safe recoveries. Most rows immediately fail because the query introduces symbols that never appear in the examples; the rest remain ambiguous or structurally inconsistent. Under the `README.md` accuracy metric, this is negative evidence against trusting the current coarse glyph family as supervision.

