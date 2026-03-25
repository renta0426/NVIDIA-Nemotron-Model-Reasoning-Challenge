# cuda-train-data-analysis-v1 symbol '*' 4-digit cluster hold

## Purpose

Re-read the top two round2 `symbol_numeric_same_op` clusters with operator `*` and 4-digit answers, and decide whether any prompt-evidenced reusable family is safe enough to promote under the `README.md` accuracy-first evaluation.

## Scope

- cluster A: `*`, answer length `4`, `same_operator_bucket=1` -> `22` rows
- cluster B: `*`, answer length `4`, `same_operator_bucket=2` -> `17` rows
- total rows in this focused hold decision: `39`

Representative IDs re-read:

- cluster A: `2d3e809c`, `5d44a0b2`, `dd626fd0`, `15a1d279`, `418895f5`
- cluster B: `1580f498`, `4d39d098`, `837af955`, `88fe5a52`, `98bb54f7`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep both top `*` 4-digit clusters in `manual_audit_priority`

## Why these clusters still stay manual

- the raw prompts mix `+`, `-`, and `*`, and most rows expose only `1-2` same-operator `*` examples
- prior derived-template probes already found `0` safe recoveries for the wider `*` 4-digit slice (`reports/18_symbol_next_safe_scan.md`)
- the representative prompts do not reveal a reusable exact family:
  - `68*91 = 5361`
  - `16*34 = 4262`
  - `84*85 = 5872`
  - `72*93 = 3501`
  - `47*04 = 9592`
  - `09*42 = 1612`
  - `12*99 = 9702`
  - `04*64 = 0481`
  - `49*95 = 5455`
  - `48*02 = 9761`
- these outputs do not line up under a shared arithmetic/digit-template rule that is exact, prompt-evidenced, and reusable across rows
- under the `README.md` metric, query-only or weakly inferred promotion would be riskier than keeping the rows manual

## Interpretation

The top `*` 4-digit clusters remain the largest unresolved round2 symbol buckets, but this pass finds no safe subset to peel off. Future work should prioritize different operator-specific hypotheses or keep these rows for strict human-only curation.
