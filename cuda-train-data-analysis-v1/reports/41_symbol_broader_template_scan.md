# cuda-train-data-analysis-v1 broader symbol template scan

## Purpose

Move beyond cluster-by-cluster manual reading and test whether the remaining digit-only `symbol_numeric_same_op` manual rows hide any broader exact family that appears across multiple rows at once under the `README.md` accuracy-first metric.

## Scope

- input slice:
  - remaining `audit_focus = symbol_numeric_same_op` rows from `artifacts/manual_pass1_priority_pack_v1.csv`
  - restricted to digit-only answers and digit-only same-operator examples
- candidate library:
  - `x+y`, `|x-y|`, `x*y`
  - zero-padded / reversed renderings of the above
  - pairwise digit-product, digit-sum, and digit-absolute-difference concatenations
  - 4-way one-digit templates built from pairwise sums/products/differences modulo 10

## Decision

- new broader-family recoveries: `0`
- decision: no repeated exact template survived the broader cross-row scan

## Result

- the scan tested the remaining digit-only manual rows against a moderately wide template library and found:
  - `template_count_with_hits = 0`
- in other words, none of the tested exact templates matched even **two** remaining manual rows end-to-end on:
  - all same-operator examples, and
  - the query answer

## Interpretation

This is strong negative evidence. After the earlier cluster-first manual passes and the targeted low-shot hold reports, the remaining symbol residual does not appear to hide another simple repeated arithmetic/string template of the kind already recovered for `concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`, or `comp99_abs_diff_2d`. If symbol is going to move further, it likely needs either:

- a broader non-simple family hypothesis, or
- a cross-operator abstraction that is not expressible as a small digit-template library.
