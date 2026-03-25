# cuda-train-data-analysis-v1 symbol '+' 3-digit cluster hold

## Purpose

Re-read the main round2 `symbol_numeric_same_op` clusters with operator `+` and 3-digit answers, and decide whether any prompt-evidenced reusable family is safe enough to promote under the `README.md` accuracy-first evaluation.

## Scope

- mapped top clusters from `reports/20_symbol_round2_cluster_map.md`
  - bucket `1`: `14` rows
  - bucket `2`: `14` rows
  - bucket `3`: `8` rows
- additional high-shot spot-check: `same_operator_example_count=4` rows `2bc2a65a`, `691f2f76`

Representative IDs re-read:

- bucket 1: `4dbec546`, `56343b77`, `a7454fdb`, `1f0674b0`, `25f2f2cd`
- bucket 2: `50c0b6f8`, `5fe8d710`, `912d2b79`, `94bf323a`, `1497f970`
- bucket 3: `0819520a`, `163db2d8`, `3ec77e36`, `1f4c8169`, `59b2cbbf`
- high-shot rows: `2bc2a65a`, `691f2f76`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep the current `+` 3-digit round2 buckets in `manual_audit_priority`

## Why these clusters still stay manual

- prior derived-template probes already found `0` safe recoveries for the wider `+` 3-digit slice (`reports/18_symbol_next_safe_scan.md`)
- bucket `1` rows expose only `1` same-operator `+` example, so there is not enough prompt evidence to infer a deterministic formatter at all
- bucket `2` rows still fail reuse:
  - some rows keep 3-digit outputs across their `+` examples, but the computation rule remains unidentified
  - other rows already contradict a stable formatter by mixing 2-digit and 3-digit `+` outputs inside the same prompt
- bucket `3` is the clearest negative evidence:
  - `0819520a`: `87+18 = 061`, `06+02 = 18`, `86+39 = 261`
  - `163db2d8`: `97+14 = 021`, `01+26 = 27`, `19+89 = 981`
  - `3ec77e36`: `75+51 = 27`, `68+37 = 951`, `87+28 = 061`
  - these rows show variable result lengths within the same prompt, proving the rule depends on operand-local behavior that is not recoverable as one simple reusable family
- even the two `4`-shot rows stay incompatible with a shared exact family:
  - `2bc2a65a`: `88+81 = 601`, `16+56 = 621`, `51+17 = 68`, `85+43 = 29`
  - `691f2f76`: `65+55 = 111`, `15+04 = 19`, `03+34 = 37`, `13+44 = 57`
- across the reviewed rows, some `+` examples look like plain sums, while others look like row-local digitwise/carry formatting variants; the formatting behavior is not stable enough to define one prompt-evidenced reusable family
- under the `README.md` metric, query-only or weakly inferred promotion would be riskier than keeping the rows manual

## Interpretation

The `+` 3-digit region still looks like one of the main round2 symbol bottlenecks, but this pass finds no safe subset to peel off. Future work should test different operator-specific formatting hypotheses or keep these rows for strict human-only curation.
