# cuda-train-data-analysis-v1 symbol '-' 1-digit bucket2 hold

## Purpose

Re-read the unresolved `symbol_numeric_same_op` cluster with operator `-`, 1-character unsigned answers, and `same_operator_bucket=2`, then decide whether this seemingly simple slice can be promoted safely under the `README.md` accuracy-first metric.

## Scope

- focused current round2 slice:
  - operator `-`
  - answer length `1`
  - answer does **not** embed the operator character
  - `same_operator_bucket=2`
  - `4` rows total
- reviewed rows:
  - `333d93ec`
  - `3b2e0cc3`
  - `58fed63a`
  - `b73d0898`
- extra mechanical probe
  - brute-force simple row-local subtraction-style candidates over:
    - `abs(x-y)`, `x-y`, `y-x`, `x+y`, `x*y`
    - digitwise absolute-difference concatenation / reversal
    - digit sums, digit products, digital roots
    - `max/min` of digitwise differences
  - with lightweight renderers such as plain, zero-padded, reversed, stripped-zero, first-digit, last-digit

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep this `-` 1-digit bucket2 slice in `manual_audit_priority`

## Why this cluster looked promising

- every row has exactly `2` same-operator `-` examples, which is stronger than the many `1`-shot dead-end rows elsewhere in round2
- the answers are only `1` character long, so at first glance the slice looks less exposed to padding ambiguity than the larger `+` / `*` / sign-embedded `-` regions
- some examples even imitate familiar subtraction-like families:
  - `63-52 = 11`
  - `57-36 = 21`

## Why it still fails exact recovery

### `333d93ec`

- examples:
  - `86-28 = 41`
  - `63-52 = 11`
- query:
  - `44-73 -> 7`
- `63-52 = 11` superficially matches digitwise absolute difference, but `86-28 = 41` does not, and the query answer `7` breaks both plain subtraction and the digitwise-difference reading

### `3b2e0cc3`

- examples:
  - `57-36 = 21`
  - `63-53 = 1`
- query:
  - `57-38 -> 8`
- the examples tempt two conflicting readings:
  - `57-36 = 21` looks like plain `abs(x-y)`
  - `63-53 = 1` looks like `10` with an unexplained trailing-zero drop
- either way, the query answer `8` does not stay inside the same family

### `58fed63a`

- examples:
  - `06-65 = 4`
  - `86-72 = 41`
- query:
  - `11-39 -> 5`
- this row mixes three incompatible renderings:
  - a 1-digit output from `06-65`
  - a reversed-looking 2-digit output from `86-72`
  - another unrelated 1-digit query answer
- there is no exact subtraction-derived rule that keeps all three aligned

### `b73d0898`

- examples:
  - `36-71 = 21`
  - `56-62 = 31`
- query:
  - `41-15 -> 9`
- the examples already disagree with ordinary subtraction and with digitwise absolute difference, and the query answer introduces yet another mismatch

## Mechanical probe result

- the added row-local scan found **zero** exact matches on all three points (two examples plus query) for all four rows
- importantly, even the most tempting candidates failed:
  - plain `abs(x-y)` / `x-y`
  - digitwise absolute-difference concatenation
  - reversed 2-digit subtraction outputs
  - digit-sum / digit-product / digital-root compression
- so this slice is not a missed “easy subtraction” family hiding just outside the current solver

## Interpretation

This cluster is a good example of why short answers alone are not enough. The 4 rows looked attractive because they had two same-operator examples each and no explicit sign handling, but exact re-reading plus the simple row-local probe showed that they still do not share one prompt-backed subtraction family. Under the `README.md` accuracy metric, it is safer to keep them manual than to promote a query-only or half-fitting subtraction heuristic.
