# bit_manipulation strong group synthesis reference

## 1. Purpose

This note is a reproducible reference for running large-scale synthetic generation from the `bit_manipulation` strong slice.

It summarizes:

- which groups are safe synthesis seeds
- what the concrete synthesis key is for each group
- whether the generated answer can be verified exactly in code
- how to reproduce the counts from the current artifacts

## 2. Evaluation premise from `README.md`

`README.md` states that this competition is scored by final-answer **Accuracy**, with the model instructed to put the final answer inside `\boxed{}`.

- source: `README.md:31-33`
- implication:
  - synthetic data must preserve **exact final-answer correctness**
  - row/group labels in this repo are **analysis-side operational labels**
  - for synthesis, the important property is: can the hidden transform be forward-executed and then re-validated exactly by code?

## 3. Source of truth files

- summary and high-level counts:
  - `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`
- row ledger:
  - `cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv`
- binary solver implementation:
  - `cuda-train-data-analysis-v1/code/train_data_analysis_v1.py`
- structured-byte recovery reports:
  - `cuda-train-data-analysis-v1/reports/43_binary_structured_byte_formula_recovery.md`
  - `cuda-train-data-analysis-v1/reports/45_binary_structured_byte_abstract_recovery.md`
  - `cuda-train-data-analysis-v1/reports/56_binary_structured_byte_manual_exact_curation.md`

## 4. Definitions used in this note

### 4.1 Strong slice

For `bit_manipulation`, this note uses:

- `selection_tier == verified_trace_ready`

That is the current trace-safe binary core described in the final summary.

Current count:

- total `bit_manipulation`: `1602`
- strong slice: `1004`
- answer-only: `445`
- manual: `138`
- exclude: `15`

### 4.2 Analysis strict key vs synthesis key

For counting patterns, the previous analysis used a solver-specific **analysis strict key**:

- `binary_structured_byte_formula` -> `bit_structured_formula_name`
- `binary_structured_byte_formula_abstract` -> `bit_structured_formula_abstract_family`
- `binary_structured_byte_not_formula` -> `bit_not_structured_formula_name`
- boolean / affine / permutation groups -> `bit_candidate_signature`
- byte transform -> `bit_byte_transform_names`

For actual synthetic generation, use a **synthesis key**:

- always fix **one concrete hidden rule per prompt**
- do **not** mix multiple exact formulas/signatures inside one generated puzzle
- for `binary_structured_byte_formula_abstract`, the synthesis key must be the row's **exact formula**, not the abstract family name alone

## 5. Reproducible strong-group counts

### 5.1 Group counts

Current strong-group breakdown:

| strong group | analysis strict key | patterns | rows |
| --- | --- | ---: | ---: |
| `binary_structured_byte_formula` | `bit_structured_formula_name` | 154 | 446 |
| `binary_structured_byte_formula_abstract` | `bit_structured_formula_abstract_family` | 15 | 152 |
| `binary_structured_byte_not_formula` | `bit_not_structured_formula_name` | 9 | 25 |
| `binary_two_bit_boolean` | `bit_candidate_signature` | 93 | 135 |
| `binary_three_bit_boolean` | `bit_candidate_signature` | 11 | 17 |
| `binary_affine_xor` | `bit_candidate_signature` | 88 | 133 |
| `binary_bit_permutation_bijection` | `bit_candidate_signature` | 14 | 78 |
| `binary_bit_permutation_independent` | `bit_candidate_signature` | 7 | 7 |
| `binary_byte_transform` | `bit_byte_transform_names` | 4 | 11 |
| **Total** |  | **395** | **1004** |

Subtotals:

| super-group | patterns | rows |
| --- | ---: | ---: |
| structured-byte family | 178 | 623 |
| other exact binary solvers | 217 | 381 |
| **Total** | **395** | **1004** |

### 5.2 Reproduction command

Run from repo root:

```bash
uv run python - <<'PY'
import csv
from collections import Counter
from pathlib import Path

path = Path("cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv")
rows = []
with path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["family"] == "bit_manipulation" and row["selection_tier"] == "verified_trace_ready":
            rows.append(row)

def grouped_count(items, key_fn):
    counter = Counter(key_fn(row) for row in items)
    return len(counter), len(items)

groups = [
    ("binary_structured_byte_formula", lambda r: r["bit_structured_formula_name"]),
    ("binary_structured_byte_formula_abstract", lambda r: r["bit_structured_formula_abstract_family"]),
    ("binary_structured_byte_not_formula", lambda r: r["bit_not_structured_formula_name"]),
    ("binary_two_bit_boolean", lambda r: r["bit_candidate_signature"]),
    ("binary_three_bit_boolean", lambda r: r["bit_candidate_signature"]),
    ("binary_affine_xor", lambda r: r["bit_candidate_signature"]),
    ("binary_bit_permutation_bijection", lambda r: r["bit_candidate_signature"]),
    ("binary_bit_permutation_independent", lambda r: r["bit_candidate_signature"]),
    ("binary_byte_transform", lambda r: r["bit_byte_transform_names"]),
]

total_patterns = 0
total_rows = 0
for name, key_fn in groups:
    subset = [row for row in rows if row["teacher_solver_candidate"] == name]
    patterns, count = grouped_count(subset, key_fn)
    total_patterns += patterns
    total_rows += count
    print(f"{name}\tpatterns={patterns}\trows={count}")

print(f"TOTAL\tpatterns={total_patterns}\trows={total_rows}")
PY
```

Expected totals:

- `patterns=395`
- `rows=1004`

## 6. Can each strong group be mass-synthesized?

Yes, with one rule:

> **One generated prompt must contain exactly one concrete hidden transform.**

In other words:

- same solver family across many prompts: **allowed**
- same exact formula/signature reused across many prompts: **allowed**
- different exact rules mixed inside one prompt: **not allowed**

### 6.1 Group-by-group synthesis rule

| strong group | Large-scale synthesis by changing numbers only | Exact code verification | Concrete synthesis key |
| --- | --- | --- | --- |
| `binary_structured_byte_formula` | Yes | Yes | exact `bit_structured_formula_name` |
| `binary_structured_byte_formula_abstract` | Yes, but only if exact formula is fixed | Yes | row-level exact formula, not abstract family only |
| `binary_structured_byte_not_formula` | Yes | Yes | exact `bit_not_structured_formula_name` |
| `binary_two_bit_boolean` | Yes | Yes | exact `bit_candidate_signature` |
| `binary_three_bit_boolean` | Yes | Yes | exact `bit_candidate_signature` |
| `binary_affine_xor` | Yes | Yes | exact `bit_candidate_signature` |
| `binary_bit_permutation_bijection` | Yes | Yes | exact `bit_candidate_signature` |
| `binary_bit_permutation_independent` | Yes | Yes | exact `bit_candidate_signature` |
| `binary_byte_transform` | Yes | Yes | exact `bit_byte_transform_names` |

## 7. Why exact verification is possible

The current code already contains deterministic forward/inference routines for every strong family:

- `infer_bit_independent_answer(...)`
- `infer_bit_bijection_answers(...)`
- `infer_bit_two_bit_boolean_answer(...)`
- `infer_bit_three_bit_boolean_answer(...)`
- `infer_bit_affine_xor_answer(...)`
- `infer_bit_byte_transform_answer(...)`
- `infer_bit_structured_byte_formula_matches(...)`
- `infer_bit_structured_byte_not_formula_matches(...)`

Relevant code locations:

- `cuda-train-data-analysis-v1/code/train_data_analysis_v1.py:1064-1455`
- dispatch and group assignment:
  - `cuda-train-data-analysis-v1/code/train_data_analysis_v1.py:1981-2052`

That means generated data can be checked in two stages:

1. **forward generation**
   - choose a concrete synthesis key
   - sample new input bitstrings
   - compute outputs from the fixed transform
2. **re-validation**
   - run the same infer function on the generated prompt
   - require the intended solver family to recover the same hidden rule / answer

## 8. Structured-byte special note

This is the most important caveat.

### 8.1 `binary_structured_byte_formula`

This is the cleanest synthesis seed:

- the report only promoted rows when exactly one semantic structured-byte formula matched
- that formula had to predict gold
- and the formula had repeated zero-error support

Source:

- `reports/43_binary_structured_byte_formula_recovery.md:31-38`

### 8.2 `binary_structured_byte_formula_abstract`

These rows are still synthesizable, but **do not synthesize at abstract-family-only level**.

Reason:

- report 45 promoted them only when the row still had **one exact formula match**
- the abstract family was used as extra safety evidence
- therefore the synthesis key must still be the row's exact formula

Source:

- `reports/45_binary_structured_byte_abstract_recovery.md:37-45`

### 8.3 Residual status

The report states that the structured-byte residual is no longer a broad repeated family problem.

Source:

- `reports/56_binary_structured_byte_manual_exact_curation.md:84-89`

Implication:

- structured-byte strong rows are already a good synthesis core
- unresolved binary tail should not be mixed into the same synthesis pipeline

## 9. Recommended synthesis protocol

Use the following protocol for mass generation.

1. Pick one strong group.
2. Pick one **concrete synthesis key** inside that group.
3. Keep the natural-language wrapper fixed.
4. Sample fresh 8-bit input values for:
   - prompt examples
   - one query
5. Compute every output with the forward transform.
6. Re-run the corresponding infer solver on the generated prompt.
7. Keep only rows that satisfy all of:
   - exact gold answer match
   - intended solver family still fires
   - no ambiguity for the intended strong path
8. Discard anything that falls into:
   - multi-formula ambiguity
   - same-pred answer-only only
   - conflicting or non-unique solver outputs

## 10. Minimal acceptance checklist

Before adding synthetic rows to training, verify:

- [ ] one prompt contains only one concrete hidden transform
- [ ] gold answer is produced by forward execution
- [ ] the same codebase solver recovers the same answer
- [ ] the row remains in a strong path, not answer-only
- [ ] abstract-family seeds are instantiated as exact formulas before generation

## 11. Bottom line

For large-scale binary synthesis, the current best reusable core is:

- `1004` strong rows
- `395` strict patterns
- all strong groups are code-verifiable
- all strong groups are mass-synthesizable
- but synthesis must operate on **concrete exact rules**, not on loose family names alone

That is especially important for:

- `binary_structured_byte_formula_abstract`
- any solver family with many internal signatures or formulas
