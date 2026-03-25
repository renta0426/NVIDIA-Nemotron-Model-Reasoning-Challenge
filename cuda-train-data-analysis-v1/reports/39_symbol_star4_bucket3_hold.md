# cuda-train-data-analysis-v1 symbol '*' 4-digit bucket3 hold

## Purpose

Re-read the remaining round2 `symbol_numeric_same_op` slice with operator `*`, 4-character answers, and `same_operator_bucket=3`, then decide whether this higher-shot residual contains a safe product-like family under the `README.md` accuracy-first metric.

## Scope

- focused current round2 slice:
  - operator `*`
  - answer length `4`
  - answer does **not** embed the operator character
  - `same_operator_bucket=3`
  - `4` rows total
- reviewed rows:
  - `40c53743`
  - `68b9b9a8`
  - `850dc715`
  - `a9deb8b5`
- extra mechanical probe
  - brute-force simple product-like candidates over:
    - `x*y`, `x+y`, `|x-y|`
    - pairwise digit-product / digit-sum / digit-difference concatenations
    - digit-sum, digit-product, digital-root compressions of the product
  - with plain / zero-padded / reversed / sliced renderers

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep this `*` 4-digit bucket3 slice in `manual_audit_priority`

## Why this slice still stays manual

- unlike the earlier `*` 4-digit bucket1/2 report, these rows do have `3` same-operator examples each, so they were worth a dedicated re-check
- even with that extra evidence, the prompts still do not stabilize around one reusable family:
  - `40c53743`: `49*58 = 1997`, `22*17 = 3651`, `69*08 = 1867`, query `24*88 -> 7963`
  - `68b9b9a8`: `73*37 = 1072`, `16*82 = 8071`, `84*78 = 6714`, query `45*18 -> 4734`
  - `850dc715`: `43*32 = 187`, `17*14 = 0192`, `69*56 = 9326`, query `96*68 -> 3395`
  - `a9deb8b5`: `91*76 = 2721`, `84*44 = 1112`, `68*97 = 3976`, query `75*32 -> 0131`
- the examples mix 3-digit and 4-digit outputs, and the 4-digit rows themselves do not line up with one obvious multiplication-derived rendering

## Mechanical probe result

- the added product-style scan found **zero** exact matches for all four rows
- rejected candidates include:
  - plain or reversed `x*y`
  - pairwise digit-product concatenations
  - pairwise digit-sum / digit-difference concatenations
  - digit-sum / digit-product / digital-root compression of `x*y`
- so this slice is not a hidden high-shot counterpart of any currently plausible simple product family

## Interpretation

The `*` 4-digit bucket3 slice looked like the last meaningful `*` residual because it had three same-operator examples per row, but even this stronger evidence base does not collapse into a safe family. Under the `README.md` accuracy metric, it remains a manual-hold cluster rather than a promotion source.
