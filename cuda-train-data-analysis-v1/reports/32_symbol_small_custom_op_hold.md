# cuda-train-data-analysis-v1 symbol small custom-operator cluster hold

## Purpose

Re-read the current small unresolved `numeric_2x2` custom-operator clusters with 3-character answers and decide whether any exact prompt-backed reusable family exists under the `README.md` accuracy-first metric.

## Scope

- focused current round2 clusters from `reports/20_symbol_round2_cluster_map.md`
  - `$` answer_len=`3`, same_operator_bucket=`1`: `4` rows
  - `@` answer_len=`3`, same_operator_bucket=`2`: `4` rows
  - `}` answer_len=`3`, same_operator_bucket=`1`: `4` rows
  - `&` answer_len=`3`, same_operator_bucket=`1`: `3` rows
- representative rows re-read:
  - `$`: `50630ad8`, `ef6bc241`, `11f62c83`, `db4383f3`
  - `@`: `286135d3`, `518d8529`, `bf4bd858`, `e4b6ce82`
  - `}`: `e9afa4a0`, `17c98340`, `912c6ea5`, `b3ae7f39`
  - `&`: `2c8e2e06`, `1d92ba5d`, `bc7f14d1`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep these small custom-operator clusters in `manual_audit_priority`

## Cluster-by-cluster verdict

### `$` bucket1 (`4` rows)

- the cluster does not stabilize around one exact family
- examples already disagree on output style:
  - `03$01 = 02`
  - `92$58 = $65`
  - `86$91 = 78`
  - `01$97 = 197`
- query answers (`$85`, `$55`, `951`, `175`) therefore cannot be unified by one reusable prompt-backed formatter

### `@` bucket2 (`4` rows)

- same-operator examples mix plain numeric outputs, operator-prefixed outputs, and longer transforms inside the same slice
- representative evidence:
  - `64@61 = 03`, `21@05 = @83`
  - `95@84 = 601`, `06@89 = 751`
  - `13@04 = 0421`, `53@71 = 595`
- because the prompt evidence itself switches format families, there is no exact reusable rule to promote

### `}` bucket1 (`4` rows)

- one row (`e9afa4a0`) superficially fits an operator-prefix absolute-difference rendering: `26}35 = }9`, query `13}64 -> }51`
- however the cluster as a whole does not support a stable family:
  - `94}26 = 111`
  - `56}46 = 921`
  - `29}46 = 651`
- current solver output also shows ambiguity on nearby rows (`candidate_prediction_count = 2` on the multi-shot cases), so the slice stays manual

### `&` bucket1 (`3` rows)

- outputs again mix incompatible styles:
  - `53&45 = 8`
  - `13&59 = 621`
  - `67&31 = 98`
- query answers (`&52`, `511`, `151`) therefore have no single prompt-backed renderer

## Important note on the apparent prefix family

- a cross-row scan confirms that `operator + abs_diff` / operator-prefix absolute-difference formatting is **not** a brand-new family hidden in these clusters
- the current solver already captures exact prompt-backed versions of that family, which is why rows such as `4c57a53f`, `7ef4d5d6`, `8c6a158e`, and `a04ecffd` are already `verified_trace_ready`
- the unresolved small-cluster rows stay manual because they are ambiguous or conflict with other equally plausible renderers, not because the prefix family itself was missing

## Interpretation

These small custom-operator clusters are classic low-volume dead ends: each one contains just enough local regularity to look tempting, but not enough exact prompt evidence to justify safe promotion. Under the `README.md` accuracy metric, treating them as reusable supervision would be riskier than leaving them manual.
