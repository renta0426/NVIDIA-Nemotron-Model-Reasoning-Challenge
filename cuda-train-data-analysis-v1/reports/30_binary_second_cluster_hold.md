# cuda-train-data-analysis-v1 binary second cluster hold

## Purpose

Re-read the second-largest round2 `binary_low_gap` cluster and decide whether it contains any safe deterministic subset worth promoting or excluding under the `README.md` accuracy-first evaluation.

## Scope

- second-largest cluster from `reports/22_binary_round2_cluster_map.md`
  - `num_examples = 8`
  - `bit_no_candidate_positions = 1`
  - `bit_multi_candidate_positions = 0`
  - `bit_boolean2_unique = False`
  - `bit_boolean3_unique = False`
  - `bit_affine_unique = False`
  - `bit_byte_transform_unique = False`
  - `rows = 29`

Representative IDs re-read:

- `07434d56`, `07d1cd39`, `0c88a3dc`, `0f1bc0ff`, `132ec6ae`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep this second binary cluster in `manual_audit_priority`

## Why this cluster still stays manual

- just like the top 34-row binary cluster, this slice has **zero unique winning family** across affine / boolean / byte-transform solvers
- each row is low-gap only in the weak sense that exactly one output bit position remains undetermined; the missing bit does not concentrate into one clean reusable subfamily
- there is still no `has_affine_mismatch` or multi-solver consensus mismatch signal, so there is no safe exclusion path either
- representative rows show partial local structure, but it breaks before becoming a reusable exact rule:
  - `07434d56`: one output bit remains unconstrained
  - `07d1cd39`: a rotation-like pattern appears on part of the byte, but does not close uniquely
  - `132ec6ae`: the first 7 bits look closer to XOR-like behavior, while the last bit remains unexplained
- this is exactly the kind of ambiguity that the current binary solvers cannot safely collapse into supervision under the `README.md` accuracy metric

## Interpretation

The second-largest binary cluster reinforces the same conclusion as the first: low-gap residuals are not enough by themselves. Without a unique solver family or a consensus mismatch, these rows are ambiguous rather than safely recoverable. They stay manual.
