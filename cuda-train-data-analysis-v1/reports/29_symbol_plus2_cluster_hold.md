# cuda-train-data-analysis-v1 symbol '+' 2-digit cluster hold

## Purpose

Re-read the main round2 `symbol_numeric_same_op` clusters with operator `+` and 2-digit answers, and decide whether any prompt-evidenced reusable family is safe enough to promote under the `README.md` accuracy-first evaluation.

## Scope

- focused unresolved `+` answer length `2` slice: `19` rows
- mapped top buckets from `reports/20_symbol_round2_cluster_map.md`
  - bucket `1`: `10` rows
  - bucket `2`: `7` rows
- higher-shot rows re-read:
  - `ed561f79` (`3` same-operator examples)
  - `93481650` (`4` same-operator examples)

Representative IDs re-read:

- bucket 1: `3013265c`, `30c0d5a2`, `49578b02`, `4a569495`, `4cf073bf`
- bucket 2: `2423926d`, `c81411a2`, `d033513f`, `2e2d60b2`, `3937cbf8`
- higher-shot rows: `ed561f79`, `93481650`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep the current `+` 2-digit round2 slice in `manual_audit_priority`

## Why these clusters still stay manual

- many bucket `1` / `2` rows expose only `1-2` same-operator `+` examples, so the formatting rule is underdetermined from the prompt alone
- the reviewed prompts do not stabilize around a single exact family:
  - some rows show ordinary-looking sums (`93+01 = 94`, `23+52 = 75`)
  - others show short non-standard outputs (`02+79 = 611`, `88+93 = 621`, `82+88 = 611`)
  - even within the same prompt family, the query answer can switch back to 2 digits without any clear prompt-evidenced reason
- even the superficially simplest row is still unsafe:
  - `4cf073bf` shows `93+01 = 94` and query answer `08`
  - this looks like ordinary addition, but the prompt never demonstrates whether `+` outputs are zero-padded to two digits or left unpadded when the sum is a single digit
  - promoting it would therefore rely on a query-only formatting guess rather than exact prompt evidence
- high-shot rows provide strong negative evidence:
  - `ed561f79`: `91+67 = 59`, `87+24 = 021`, `67+67 = 251`
  - `93481650`: `82+64 = 47`, `21+25 = 46`, `87+73 = 511`
  - these rows mix 2-digit and 3-digit `+` outputs inside the same prompt, so there is no reusable exact formatter
- a direct scan of the `+` 2-digit slice finds `4 / 19` rows whose same-operator examples already mix output lengths within the prompt, confirming that formatter instability is not anecdotal
- under the `README.md` metric, query-only or weakly inferred promotion would be riskier than keeping the rows manual

## Interpretation

The `+` 2-digit region is not a clean “small-answer” counterpart of the `+` 3-digit family. It still mixes ordinary sums with row-local formatting transforms, and even the high-shot rows do not unify them into one exact prompt-evidenced rule. This makes the slice another round2 manual-hold candidate rather than a safe promotion source.
