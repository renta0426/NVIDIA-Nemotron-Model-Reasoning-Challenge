# cuda-train-data-analysis-v1 binary structured byte multi-consensus recovery

## Purpose

Recheck the remaining structured-byte multi-formula rows after report 45 and see whether any of them can be moved from `manual_audit_priority` to a safer tier without pretending the underlying formula is uniquely identified.

## Candidate rule

Promote a row to `answer_only_keep` only if all of the following hold:

- `bit_structured_formula_match_count > 1`
- all matching formulas produce the **same single query prediction**
- that prediction matches gold on train
- at least one of the matching formulas belongs to a previously validated **safe abstract structured-byte family**

This keeps the supervision conservative:

- the underlying exact formula is still ambiguous
- but the query answer is stable inside the structured-formula library
- and at least one matching family already has strong zero-error support elsewhere

## Full-train sweep

The rule was evaluated across all binary rows.

| rule | rows | gold_match_rows | error_rows |
| --- | ---: | ---: | ---: |
| same prediction + any safe exact | 1 | 1 | 0 |
| same prediction + any safe abstract | 2 | 2 | 0 |

The broader `safe abstract` condition is still clean on train and recovers exactly the two previously unresolved same-pred rows.

## Recovered rows

| id | answer | matching_formulas | safe_abstract_hit |
| --- | --- | --- | --- |
| `8b4c71ba` | `11001100` | `or(rol1,ror3)` / `or(ror3,shl1)` | `or(ror,shl)` |
| `cc5011ac` | `11011101` | `or(rol1,shr3)` / `or(shl1,shr3)` | `or(rol,shr)` |

Both rows stay **answer-only**, not `verified`, because their exact structured formula is still non-unique.

## Non-recovered multi row

The only remaining multi-formula row is:

| id | matching_formulas | predictions |
| --- | --- | --- |
| `5a6dd286` | `or(rol1,rol3)` / `or(rol3,shl1)` | `10111101` / `10111100` |

This row still has two different structured predictions, so it remains `manual_audit_priority`.

## Resulting state

After adding this rule:

- overall: `6081 verified / 1107 answer_only / 2286 manual / 26 exclude`
- binary: `599 verified / 22 answer_only / 966 manual / 15 exclude`
- structured-byte residual: `24 rows = 20 manual + 4 exclude`

## Decision

Adopt the rule as `answer_only_keep` only.

It is useful because it recovers the last two same-pred multi-formula rows while still respecting the `README.md` accuracy-first constraint that exact supervision should not be fabricated when the underlying program remains ambiguous.
