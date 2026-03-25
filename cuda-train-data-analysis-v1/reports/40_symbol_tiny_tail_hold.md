# cuda-train-data-analysis-v1 symbol tiny-tail hold

## Purpose

Review the remaining singleton / doubleton round2 `symbol_numeric_same_op` operator tails after the larger dedicated passes, and decide whether these tiny residual slices should stay manual under the `README.md` accuracy-first metric.

## Scope

- remaining tiny operator tails from `artifacts/symbol_round2_cluster_summary_v1.csv`
- focus on the region where cluster size has collapsed to `1-2` rows per operator/length/bucket slice
- representative rows re-read across several operators:
  - `9b9e024b` (`#`)
  - `d204b9cc` (`)`)
  - `01cd504a` (`/`)
  - `76b79a0c` (`@`)
  - `14905278` (`<`)
  - `6e6f8d9c` (`?`)
  - `5787c3d0` (`^`)
  - `6cd73bdd` (`{`)

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep the remaining singleton / doubleton symbol tails in `manual_audit_priority`

## Why these tails still stay manual

- by construction, these slices are even lower-evidence than the 3-row and 4-row clusters already held in reports 32–39
- many of them expose only a single same-operator example per row, so there is no exact prompt-backed way to choose between competing renderings
- the spot-checked operators already show how heterogeneous the region is:
  - `9b9e024b`: `88#67 = 461`, query `23#29 -> 421`
  - `d204b9cc`: `49)04 = 431`, query `75)57 -> 231`
  - `01cd504a`: `82/15 = 8241`, query `85/77 -> 6644`
  - `76b79a0c`: `42@14 = 489`, query `23@19 -> 2192`
  - `14905278`: `27<97 = 8865`, query `38<56 -> 5935`
  - `6e6f8d9c`: `14?48 = 421`, query `49?66 -> 951`
  - `5787c3d0`: `51^49 = ^2`, query `85^86 -> ^1`
- `6cd73bdd`: `29{89 = 6109`, `58{62 = 0122`, query `37{28 -> 6895`
- this is not one hidden family; it is a long tail of operator-local transforms with too little within-operator evidence to justify safe supervision

## Interpretation

At this stage, the remaining symbol residual is no longer dominated by medium-sized reusable clusters. It is mostly a tiny-tail problem: many operator-local mini-slices, each with too little exact prompt evidence. Under the `README.md` accuracy metric, the safe policy is to keep these tails manual until a broader family hypothesis appears that can explain several of them at once.
