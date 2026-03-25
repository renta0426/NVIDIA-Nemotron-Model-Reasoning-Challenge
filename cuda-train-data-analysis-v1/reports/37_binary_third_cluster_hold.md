# cuda-train-data-analysis-v1 binary third cluster hold

## Purpose

Re-read the third-largest round2 `binary_low_gap` cluster and decide whether it contains any safe deterministic subset worth promoting or excluding under the `README.md` accuracy-first evaluation.

## Scope

- third-largest cluster from `reports/22_binary_round2_cluster_map.md`
  - `num_examples = 9`
  - `bit_no_candidate_positions = 1`
  - `bit_multi_candidate_positions = 0`
  - `bit_boolean2_unique = False`
  - `bit_boolean3_unique = False`
  - `bit_affine_unique = False`
  - `bit_byte_transform_unique = False`
  - `rows = 17`

Representative IDs re-read:

- `06667a93`, `0a1326f4`, `20052c2f`, `368f20dd`, `3ebd80e6`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep this third binary cluster in `manual_audit_priority`

## Why this cluster still stays manual

- like the top 34-row and second 29-row binary clusters, this slice still has **zero unique winning family** across affine / boolean / byte-transform solvers
- each row remains low-gap only in the weak sense that one output bit position has no current candidate rule; that does **not** become a safe family by itself
- there is still no `has_affine_mismatch` or multi-solver consensus mismatch signal, so there is no safe exclusion path either
- the representative rows show several different “almost-structured” patterns rather than one shared residual:
  - `06667a93`: seven positions look close to a right-shift / rotation-like mapping, but the first output bit still floats
  - `0a1326f4`: another shift-like fragment appears, but the unconstrained bit moves to a different position
  - `20052c2f`: a near-cyclic pattern holds for seven bits, yet the last bit still has no deterministic closure
  - `368f20dd`: partial reuse appears, but the signature also duplicates one source bit and leaves a middle position unresolved
  - `3ebd80e6`: the row mixes inversion-like mappings with one unconstrained output bit, so it is not even the same residual shape as the simpler shift-like cases
- this spread matters: the missing bit does not concentrate into one clean reusable subfamily, so the cluster is not a hidden “single broken byte transform”

## Interpretation

The third binary cluster extends the same lesson as reports 27 and 30. These low-gap residuals are structured enough to tempt over-interpretation, but not structured enough to yield a unique safe solver or a safe exclusion signal. Under the `README.md` accuracy metric, the correct move is still to keep them manual.
