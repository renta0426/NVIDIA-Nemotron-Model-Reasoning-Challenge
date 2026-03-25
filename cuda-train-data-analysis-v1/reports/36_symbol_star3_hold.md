# cuda-train-data-analysis-v1 symbol '*' 3-digit cluster hold

## Purpose

Re-read the unresolved round2 `symbol_numeric_same_op` slice with operator `*`, 3-character answers, and `same_operator_bucket=1`, then decide whether a small product-like family can be promoted safely under the `README.md` accuracy-first metric.

## Scope

- focused current round2 slice:
  - operator `*`
  - answer length `3`
  - answer does **not** embed the operator character
  - `same_operator_bucket=1`
  - `4` rows total
- reviewed rows:
  - `c0f32a1e`
  - `026106f5`
  - `620c2521`
  - `759cbdde`
- extra mechanical probe
  - brute-force simple product-like candidates over:
    - `x*y`, `x+y`, `|x-y|`
    - pairwise digit products / sums / absolute differences
    - digit-sum, digit-product, digital-root compressions of the product
  - with plain / zero-padded / reversed / sliced renderers

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep this `*` 3-digit slice in `manual_audit_priority`

## Why this slice still stays manual

- every row has only **one** same-operator `*` example, so the prompt evidence is extremely low-shot
- the single example per row does not stabilize around one reusable multiplication-style family:
  - `c0f32a1e`: `18*29 = 2547`, query `92*02 -> 085`
  - `026106f5`: `31*15 = 46`, query `75*97 -> 631`
  - `620c2521`: `54*78 = 6193`, query `85*11 -> 936`
  - `759cbdde`: `18*04 = 121`, query `84*46 -> 211`
- even before any formal scan, these rows already disagree on basic behavior:
  - sometimes the example answer is 4 digits, sometimes 2 or 3
  - sometimes the query answer is shorter than the example, sometimes longer
  - the slice therefore does not look like one missing formatter branch of ordinary multiplication

## Mechanical probe result

- the added product-style scan found **zero** exact matches across all four rows
- rejected candidates include:
  - plain product with or without zero-padding
  - reversed product digits
  - pairwise digit-product concatenations
  - pairwise digit-sum / digit-difference concatenations
  - digit-sum / digit-product / digital-root compression of `x*y`
- so this slice is not a missed “small multiplication” family either

## Interpretation

The `*` 3-digit cluster is another low-shot operator-specific dead end. It looks tempting because the answers are short and there are only 4 rows, but the prompt evidence is too thin and too inconsistent to support a safe reusable family. Under the `README.md` accuracy metric, manual hold is safer than inventing a product-like heuristic from one example per row.
