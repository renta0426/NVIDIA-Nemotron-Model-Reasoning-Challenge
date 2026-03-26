# cuda-train-data-analysis-v1 symbol prefix-always-abs tail recovery

## Purpose

Re-read the last remaining manual `numeric_2x2` rows that still had:

- at least `2` same-operator examples
- a gold-matching candidate under the existing arithmetic library
- unresolved ambiguity only because the library could not distinguish
  `prefix_always_abs` from nearby non-prefixed variants automatically

## Recovered rows

### 1. `31eb8247` (`"`)

Prompt examples:

- `16"59 = "43`
- `59"63 = "4`

Both same-op examples show the same operator-local answer pattern:

- take the absolute difference
- always prefix the operator character
- do not zero-pad

Query:

- `25"13` → `"12`

Decision:

- move to `answer_only_keep`
- not `verified`, because the prompt fixes the final string but not a unique symbolic trace beyond absolute-difference style answer rendering

### 2. `4c57a53f` (`[`)

Prompt examples:

- `67[45 = [22`
- `17[87 = [70`

Again, both same-op examples support:

- absolute difference
- operator always prefixed
- no zero-padding

Query:

- `37[33` → `[4`

Decision:

- move to `answer_only_keep`
- keep at answer-only strength for the same reason as above

## Exhaustion note

After promoting these two rows, the current symbol tail no longer contains any manual `numeric_2x2` row that simultaneously satisfies:

- gold answer appears in the current prompt-backed candidate set
- `same_operator_example_count >= 2`

What remains in the gold-hit slice is now only `8` single-example rows, which are too thin to promote safely under the `README.md` accuracy-first policy.

Representative remaining single-example traps:

- `55f19327`
- `64fe405e`
- `74fff108`
- `81c7ba7a`
- `45dbc1cc`

## Counts after this pass

- overall: `6086 verified / 1151 answer_only / 2236 manual / 27 exclude`
- symbol: `110 verified / 145 answer_only / 1289 manual / 11 exclude`
- pass1 manual pack: `493 rows`
  - `330` `symbol_numeric_same_op`
  - `117` `binary_low_gap`
  - `46` `symbol_glyph_multiset`
- current symbol round2 core: `280 rows`

## Artifact

- `artifacts/symbol_manual_prompt_exact_answer_only_candidates_v1.csv`

## Decision

Adopt `31eb8247` and `4c57a53f` as the last clean multi-example answer-only recoveries in the current symbol tail.

This closes the present prompt-backed `same_operator_example_count >= 2` symbol sweep.  
Further gains will require either:

- genuinely new operator-specific families, or
- accepting much thinner single-example evidence, which the current policy rejects.
