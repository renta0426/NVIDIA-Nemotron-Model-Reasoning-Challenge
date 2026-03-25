# cuda-train-data-analysis-v1 symbol '-' 2-digit unsigned cluster hold

## Purpose

Re-read the unresolved round2 `symbol_numeric_same_op` slice with operator `-`, 2-character unsigned answers, and `same_operator_bucket=1`, then decide whether it hides a safe subtraction-like family under the `README.md` accuracy-first metric.

## Scope

- focused current round2 slice:
  - operator `-`
  - answer length `2`
  - answer does **not** embed the operator character
  - `same_operator_bucket=1`
  - `4` rows total
- reviewed rows:
  - `8373daa8`
  - `3383d4ec`
  - `5d834875`
  - `fb3f7b77`
- extra mechanical probe
  - same simple row-local candidate library used on report 34:
    - `abs(x-y)`, `x-y`, `y-x`, `x+y`, `x*y`
    - digitwise subtraction / absolute-difference concatenations
    - digit sums, digit products, digital roots
    - `max/min` of digitwise differences
  - with plain / zero-padded / reversed / stripped-zero / first-digit / last-digit style renderers

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep this `-` 2-digit unsigned slice in `manual_audit_priority`

## Why this slice still stays manual

- every row has only **one** same-operator `-` example, so the prompt evidence is even weaker than the already-rejected `-` 1-digit bucket2 slice
- the single example often looks subtraction-like, but the query answer immediately leaves that family:
  - `8373daa8`: `05-58 = -53`, query `08-23 -> 84`
  - `3383d4ec`: `88-12 = 76`, query `39-72 -> 66`
  - `5d834875`: `34-95 = 201`, query `91-33 -> 25`
  - `fb3f7b77`: `34-39 = -05`, query `46-83 -> 62`
- this is the classic query-only trap:
  - the example suggests one subtraction convention
  - the query answer points somewhere else
  - with only one same-op example, there is no exact prompt evidence to decide which branch is the real family

## Mechanical probe result

- the added row-local scan again found **zero** exact matches for all four rows
- the failures include the most tempting families:
  - plain subtraction / absolute difference
  - zero-padded or reversed subtraction
  - digitwise difference or digitwise absolute difference
  - digit-sum / digit-product compression of subtraction results
- so this slice is not a missed “easy 2-digit subtraction” region either

## Interpretation

These rows are even less constrained than the `-` 1-digit bucket2 slice from report 34. The single same-operator example per row is not enough to anchor the subtraction style, sign behavior, or formatting rule, and the query answers then drift away from the obvious reading. Under the `README.md` accuracy metric, this is another manual-hold cluster rather than a safe promotion source.
