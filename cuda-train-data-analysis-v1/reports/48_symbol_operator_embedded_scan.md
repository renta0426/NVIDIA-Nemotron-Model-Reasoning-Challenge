# cuda-train-data-analysis-v1 symbol operator-embedded scan

## Purpose

Recheck the unresolved `numeric_2x2` symbol rows whose answers embed the operator character itself, because report 41 only ruled out broader templates on the **digit-only** residual slice.

## What was scanned

Two exploratory directions were tested on the current manual numeric queue:

1. **operator-suffixed numeric renderers**
   - `suffix_zpad2`
   - `suffix_abs_zpad2`
   - `suffix_always_abs`
   - `suffix_if_negative`
2. **operator-prefixed absolute-difference string template**
   - `op_prefix_abs_diff_2d` = `op + diff_t + diff_o`

These were checked against each row's same-operator examples and then evaluated on the query answer.

## Result

- safe new recoveries: `0`
- safe new excludes: `0`

No clean repeated operator-embedded family survived the `README.md` accuracy-first standard.

## Near-miss family: `op_prefix_abs_diff_2d`

This was the closest candidate.

### Full support

- support rows: `31`
- gold-match rows: `15`
- error rows: `16`

So it is **not** a zero-error family.

### Interesting unresolved rows

The family exactly predicts the current gold answer for these manual rows:

| id | query | answer |
| --- | --- | --- |
| `81c7ba7a` | `90?76` | `?14` |
| `2dd48cac` | `22-27` | `-05` |
| `45dbc1cc` | `98-63` | `-35` |
| `4cb5e927` | `69-49` | `-20` |

But it also has a direct contradictory row in the same residual area:

| id | query | gold | family_prediction |
| --- | --- | --- | --- |
| `8c1529e1` | `65-18` | `-52` | `-47` |

This one mismatch is enough to block safe promotion of the whole low-shot family.

## Interpretation

The exploratory scan confirms that operator-embedded outputs are **not completely random**. There is a real cross-operator pattern around prefixed absolute-difference formatting, but it is contaminated by hard contradictions, so it cannot yet be turned into a trustworthy promotion rule.

In other words:

- there is useful structure here
- but not enough structure to auto-label safely
- the current residual still needs operator-local manual reasoning rather than a reusable exact family

## Decision

Do **not** modify the main analysis logic from this scan.

Keep the operator-embedded residual rows in `manual_audit_priority` until a cleaner subfamily or a stronger exclusion rule is found.
