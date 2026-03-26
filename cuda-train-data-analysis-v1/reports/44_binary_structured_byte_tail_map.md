# cuda-train-data-analysis-v1 binary structured byte tail map

## Purpose

After report 43, map the remaining structured-byte residuals before attempting any further promotion.

## Residual size

- total residual rows with some structured-byte match: `55`
  - `51 manual_audit_priority`
  - `4 exclude_suspect`

## Residual categories

### A. Singleton exact formula, support=1

- `46` rows
- shape:
  - `selection_tier=manual_audit_priority`
  - `bit_structured_formula_match_count=1`
  - `bit_structured_formula_prediction_count=1`
  - `bit_structured_formula_safe_support=1`
- interpretation:
  - the row has one semantic formula inside the current library
  - but that exact formula only appears once across all bit rows
  - report 43 already showed that singleton formulas are unsafe to auto-promote because `8631d7b6` is a concrete counterexample

### B. Same-pred multi-formula rows

- `2` manual rows
- shape:
  - `bit_structured_formula_match_count=2`
  - `bit_structured_formula_prediction_count=1`
- representative IDs:
  - `8b4c71ba`
  - `cc5011ac`
- interpretation:
  - current structured library agrees on the query answer
  - but the reasoning trace is still not unique
  - this is a natural answer-only candidate class if a future consensus rule can be made conservative enough

### C. Ambiguous-pred row

- `1` manual row
- shape:
  - `bit_structured_formula_match_count=2`
  - `bit_structured_formula_prediction_count=2`
- ID:
  - `5a6dd286`
- interpretation:
  - even the query answer is not unique, so this stays manual

### D. Structured mismatch excludes

- `4` rows
- IDs / formulas:
  - `6abc8047` → `ror1`
  - `82d937aa` → `ror1`
  - `fee5976e` → `ror2`
  - `a8ea0e29` → `xor(ror1,shr1)`
- interpretation:
  - these are strong reminders that formula-like fit on the examples is not enough on its own
  - safe promotion must continue to respect gold-backed error checks

## Abstract-family probe

To test whether the `46` singleton formulas hide broader repeated structure, formulas were abstracted by dropping concrete shift indices:

- `rol1`, `rol2`, `rol3` → `rol`
- `shr1`, `shr2`, `shr3` → `shr`
- and similarly for `ror` / `shl`

Then binary formulas were abstracted, e.g.:

- `and(rol2,ror3)` → `and(rol,ror)`
- `xor(rol1,shl2)` → `xor(rol,shl)`

### Repeated zero-error abstract families

Top zero-error abstract families on unique structured-byte matches:

| support_rows | abstract_family |
| ---: | --- |
| 72 | `xor(shl,shr)` |
| 39 | `rol` |
| 26 | `shr` |
| 21 | `xor(rol,shl)` |
| 17 | `or(rol,shr)` |
| 16 | `xor(ror,shl)` |
| 15 | `xor(rol,shr)` |
| 14 | `and(rol,ror)` |
| 14 | `or(ror,shl)` |
| 14 | `or(ror,shr)` |
| 12 | `and(rol,shr)` |
| 12 | `and(ror,shl)` |

### Immediate implication

- `37` of the `46` manual singleton rows belong to abstract families with:
  - support `>= 5`
  - empirical errors `= 0`

This is promising, but it is **not** merged into the main curation rule yet. The current concern is that abstracting away shift indices may still collapse genuinely different transforms, so this needs another conservative check before promotion.

## Current best next step

The next binary experiment should focus on the `46` singleton rows and test whether a stronger abstraction-safe rule exists, for example:

1. abstract family support + no-error
2. same operation type plus bounded shift pattern
3. shared prompt-side evidence beyond the formula name itself

Until that is shown safe, the residual tail should remain manual.
