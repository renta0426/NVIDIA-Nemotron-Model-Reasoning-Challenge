# cuda-train-data-analysis-v1 symbol colon manual exact answer-only

## Purpose

Re-read the remaining `:` operator tail after report 55 and recover only the rows where the prompt itself already fixes a reliable **answer-level** rule, even though the full symbolic trace is still too thin or not uniquely oriented.

This pass stays conservative:

- promote to `answer_only_keep`, not `verified_trace_ready`
- do not rely on query-only fits
- leave rows with no `:` examples or with unresolved single-example ambiguity in manual

## Recovered rows

### 1. `094bf548` → exact abs-diff answer level

Prompt examples:

- `27:81 = 54`
- `52:57 = 5`
- `25:81 = 56`

These examples all support the same answer-level behavior:

- output is the plain absolute difference of the two 2-digit numbers

Query:

- `80:32` → `48`

Decision:

- move to `answer_only_keep`
- not `verified`, because the prompt still does not distinguish every equivalent reasoning trace/orientation variant; it only makes the final answer reliable

### 2. `904e3a54` → exact negative-prefix family, positive branch on query

Prompt examples:

- `27:29 = :2`
- `49:99 = :50`

These examples support the operator-local family:

- compute `x - y`
- prefix the operator only when the result is negative

Query:

- `76:10` → `66`

Decision:

- move to `answer_only_keep`
- not `verified`, because the prompt examples only expose the negative branch directly; the positive query branch is still an answer-level extension rather than a fully demonstrated trace

## Rows intentionally left manual

Representative holds:

- `55f19327`: only one `:` example (`20:20 = 0`), too weak to separate `mod`-like and difference-like interpretations
- `d1bd7478`: one `:` example (`88:77 = 11`) is compatible with abs-diff, but still too thin for safe promotion
- `5144897d`: one `:` example points at a modulo-like rule, but the row remains too underdetermined for safe exclusion
- `1861c08f`, `35672155`, `806eba07`: same-op examples exist, but the current formula library still does not identify a stable reusable family
- no-example rows such as `275db7d4`, `a361a1b7`, `cc735e46`, `0f8452df`, `f971f8dd` remain manual because the query answer alone is not admissible evidence under the `README.md` accuracy-first policy

## Counts after this pass

- overall: `6086 verified / 1149 answer_only / 2238 manual / 27 exclude`
- symbol: `110 verified / 143 answer_only / 1291 manual / 11 exclude`
- pass1 manual pack: `495 rows`
  - `332` `symbol_numeric_same_op`
  - `117` `binary_low_gap`
  - `46` `symbol_glyph_multiset`

## Artifact

- `artifacts/symbol_manual_prompt_exact_answer_only_candidates_v1.csv`

## Decision

Adopt only the two prompt-exact `:` rows above.

The broader `:` tail is still mixed:

- some rows have no same-op evidence at all
- some are single-example traps
- some likely belong to new custom families outside the current arithmetic template set
