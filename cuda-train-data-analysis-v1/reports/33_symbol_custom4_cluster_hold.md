# cuda-train-data-analysis-v1 symbol 4-digit custom-operator cluster hold

## Purpose

Re-read the remaining small round2 `symbol_numeric_same_op` clusters whose answers are 4-character numeric strings under custom operators, and decide whether any exact prompt-backed reusable family is safe enough to promote under the `README.md` accuracy-first metric.

## Scope

- focused current unresolved custom-operator slices with 4-character answers
  - `!`: `4` rows (`379d18b7`, `3b7e71b2`, `1cb4d524`, `7ecdae14`)
  - `"`: `3` rows (`5f5a73ff`, `ddb9aafd`, `10ff9431`)
  - `$`: `4` rows (`cee07c09`, `6bd59a1f`, `9f2fae58`, `bd4c584a`)
  - `%`: `5` rows (`3acfa7a4`, `ce507d39`, `3b51288b`, `69197d42`, `6c9e4485`)
  - `[`: `3` rows (`4f660f4b`, `61766c6f`, `b3f9a15c`)
- extra mechanical probe
  - left-pad same-operator examples to 4 digits where needed
  - test a simple digit-template library over raw digits, pair sums/differences/products, pairwise min/max, and 2-digit `x / y / x+y / |x-y| / x*y` digit slices

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep all five custom-operator slices in `manual_audit_priority`

## Why these slices still stay manual

- same-operator evidence is still low-shot on most rows, usually only `1-2` direct examples for the query operator
- even before looking for a reusable family, the prompts already show unstable rendering:
  - `!`: `05!84 = 0042`, `82!61 = 844`, `43!93 = 7231`
  - `"`: `61"82 = 844`, `47"28 = 8606`, `15"03 = 0351`
  - `$`: `74$02 = 939`, `76$06 = 9104`, `41$63 = 305`
  - `%`: `54%27 = 0423`, `73%71 = 926`, `44%92 = 6721`, `21%22 = 462`
  - `[`: `86[91 = 2921`, `98[13 = 9572`, `32[35 = 0221`
- that means the unresolved rows are not just “missing one formatter branch”; the example evidence itself mixes 3-digit and 4-digit outputs, often without enough repetition to tell whether the padding rule is real or accidental

## Mechanical template probe result

- the simple digit-template scan found **no** full 4-digit template that explains the current same-operator example pool for `!`, `"`, `$`, or `%`
- `[` showed only one trivial position-level coincidence (`prod_d2` on the third digit after zero-padding), but the other three positions still failed, so there is no usable full-string family there either
- this matters because several of these rows look superficially tempting from the query answer alone; the probe confirms that they do not collapse to one safe low-complexity family

## Cluster-by-cluster verdict

### `!` (`4` rows)

- representative rows:
  - `379d18b7`: `05!84 = 0042`, query `22!64 -> 2101`
  - `1cb4d524`: `58!05 = 0524`, `71!56 = 5011`, `82!61 = 844`, query `74!88 -> 6314`
  - `7ecdae14`: `95!51 = 688`, `43!93 = 7231`, `95!14 = 0242`, query `17!32 -> 4361`
- the same operator already mixes zero-padded 4-digit, bare 3-digit, and other 4-digit transforms, so there is no exact reusable family

### `"` (`3` rows)

- representative rows:
  - `ddb9aafd`: `15"03 = 0351`, query `55"18 -> 5544`
  - `10ff9431`: `47"28 = 8606`, `79"05 = 0584`, query `02"68 -> 0271`
- the example pool is too small and too heterogeneous to justify a promotion; no simple digit template matches all observed outputs

### `$` (`4` rows)

- representative rows:
  - `6bd59a1f`: `74$02 = 939`, `41$63 = 305`, query `82$15 -> 7241`
  - `9f2fae58`: `76$06 = 9104`, `93$23 = 7421`, query `88$13 -> 7272`
  - `bd4c584a`: `33$77 = 1452`, `87$95 = 2064`, query `02$79 -> 0491`
- low-shot prompt evidence and mixed output widths make these rows another query-tempting but promotion-unsafe slice

### `%` (`5` rows)

- `%` is the largest of these small custom-operator families, but it still does not stabilize:
  - `44%92 = 6721`, query `45%92 -> 6651`
  - `54%27 = 0423`, `73%71 = 926`, query `85%92 -> 2861`
  - `19%38 = 3557`, `21%22 = 462`, `12%21 = 252`, query `95%05 -> 0592`
- the added template scan is especially useful here: even with the extra evidence volume, no simple cross-row digit family survives

### `[` (`3` rows)

- representative rows:
  - `4f660f4b`: `86[91 = 2921`, query `76[86 -> 6554`
  - `61766c6f`: `98[13 = 9572`, query `46[34 -> 2572`
  - `b3f9a15c`: `32[35 = 0221`, query `85[56 -> 1773`
- this slice has only one same-operator example per row, so even though the outputs all have 4 digits, the family is still underdetermined from the prompt alone

## Interpretation

These five clusters are the 4-digit counterpart of the earlier small custom-operator dead ends: visually regular enough to invite overfitting, but still too low-shot and too format-unstable to support safe supervision. Under the `README.md` accuracy metric, keeping them manual is safer than inventing a family from query-only fit or from a weak digitwise coincidence.
