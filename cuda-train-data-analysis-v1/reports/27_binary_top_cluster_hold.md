# cuda-train-data-analysis-v1 binary top cluster hold

## Purpose

Re-read the largest round2 `binary_low_gap` cluster and decide whether it contains any safe deterministic subset worth promoting or excluding under the `README.md` accuracy-first evaluation.

## Scope

- top cluster from `reports/22_binary_round2_cluster_map.md`
  - `num_examples = 7`
  - `bit_no_candidate_positions = 1`
  - `bit_multi_candidate_positions = 0`
  - `bit_boolean2_unique = False`
  - `bit_boolean3_unique = False`
  - `bit_affine_unique = False`
  - `bit_byte_transform_unique = False`
  - `rows = 34`

Representative IDs re-read:

- `0b23aa7c`, `0cfc74d4`, `114a7439`, `12897b38`, `21fa96be`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep this top binary cluster in `manual_audit_priority`

## Why this cluster still stays manual

- unlike the already excluded affine mismatch rows, this cluster does **not** have a unique winning family
- the rows are low-gap only in the weak sense that exactly one output bit position has no candidate rule; they do **not** show a deterministic affine / boolean / byte-transform resolution
- there is no `has_affine_mismatch` signal here, so the cluster cannot be safely excluded as “solver says gold is wrong”
- earlier residual scans already found `0` multi-solver consensus mismatches beyond the 11 excluded affine rows, so there is no safe exclusion path left in this slice either
- the remaining ambiguity suggests broader non-local or circuit-like binary rules rather than another easy recoverable subset

## Interpretation

This 34-row cluster is the canonical example of why round2 binary remains lower ROI than round2 symbol. It is unresolved because no current solver family wins, not because multiple strong families agree on a wrong answer. That makes both promotion and exclusion unsafe, so the cluster stays manual.
