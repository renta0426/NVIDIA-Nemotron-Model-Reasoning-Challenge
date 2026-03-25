# cuda-train-data-analysis-v1 binary tail clusters hold

## Purpose

Re-read the remaining smaller round2 `binary_low_gap` clusters after the top three, and decide whether any of these tail slices contain a safe deterministic subset worth promoting or excluding under the `README.md` accuracy-first metric.

## Scope

- remaining binary round2 tail clusters from `reports/22_binary_round2_cluster_map.md`, especially the slices with:
  - `bit_multi_candidate_positions >= 1`, or
  - `bit_no_candidate_positions = 0` but multiple candidate rules still competing
- representative rows re-read:
  - `24b60af3` from the `7 examples / 1 no-candidate / 2 multi-candidate` cluster
  - `034fb629` from the `9 examples / 1 no-candidate / 2 multi-candidate` cluster
  - `26c83e22` from the `8 examples / 1 no-candidate / 2 multi-candidate` cluster
  - `9984fc0f` from the `7 examples / 0 no-candidate / 2 multi-candidate` cluster
  - `9238e8d6` from the `7 examples / 1 no-candidate / 1 multi-candidate` cluster

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep the remaining binary tail clusters in `manual_audit_priority`

## Why these tail clusters still stay manual

- structurally, these slices are **more ambiguous** than the top three binary clusters already held in reports 27, 30, and 37
- the top three clusters had `bit_multi_candidate_positions = 0` and still failed to yield a unique solver family or a safe exclusion path
- these tail clusters are worse:
  - several output positions admit multiple competing local rules
  - some rows have no missing positions at all, but still remain unresolved because the surviving candidate rules disagree
  - none of the representative rows shows `bit_affine_unique`, `bit_boolean2_unique`, `bit_boolean3_unique`, or `bit_byte_transform_unique`
- there is still no safe exclusion signal:
  - no unique affine mismatch
  - no multi-solver consensus mismatch
  - no deterministic byte-transform winner

## Representative evidence

### `24b60af3`

- signature: `o3=[none]`, with two-way ambiguity on `o4` and `o5`
- prompt examples already look close to a local shift/XOR-like family, but the unresolved and multi-candidate positions prevent exact closure

### `034fb629`

- signature: one missing output bit plus two positions that can be explained by either direct-copy or inverted-copy candidates
- this is more ambiguous than the earlier “single floating bit” clusters, not less

### `26c83e22`

- signature: one missing output bit plus a pair of symmetric copy/invert alternatives in the middle of the byte
- the query row therefore does not support safe promotion into any exact solver family

### `9984fc0f`

- signature: `bit_no_candidate_positions = 0`, yet two positions still have competing rules
- this is important negative evidence: even when every bit has *some* candidate, the row still does not collapse to one deterministic transform

### `9238e8d6`

- signature: one missing bit and one multi-candidate bit
- the prompt looks locally structured, but the ambiguity still survives through the query, leaving no safe promotion or exclusion path

## Interpretation

The remaining binary tail clusters are not “the easy leftovers after the top three.” They are the opposite: smaller, but structurally *more* ambiguous. Once the top three no-multi-candidate clusters failed to produce a safe subset, these tail clusters became even lower ROI. Under the `README.md` accuracy metric, the correct move is to keep them manual until a genuinely broader binary family is discovered.
