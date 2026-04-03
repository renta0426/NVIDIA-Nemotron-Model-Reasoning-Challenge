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

## 9. Program-trace SFT base for LoRA-only training

For LoRA-only SFT, not every strong row should immediately become a CoT teacher.

Reason:

- a row can have a **unique answer**
- while still lacking a **unique executable procedure**

That distinction matters if the goal is to teach the model:

- not merely `rule label -> answer`
- but the actual operation sequence that maps query input to final output

### 9.1 Correction to the earlier preliminary count

The earlier working estimate was `819` rows.

After a stricter re-check of the `binary_bit_permutation_independent` slice, the exact-trace-safe base is:

- **`817` rows**, not `819`

Why the correction happened:

- two `binary_bit_permutation_independent` rows still contain multi-source ambiguity in `bit_candidate_signature`
- they produce a unique query answer
- but they do **not** provide a unique copy/invert mapping for every output bit

For CoT teacher construction, those two rows should be excluded from the exact procedural base.

### 9.2 Exact-trace-safe counts by group

These are the rows that can be used **as-is** as program-trace teachers.

| strong group | exact-trace-safe rows | trace-safe condition |
| --- | ---: | --- |
| `binary_structured_byte_formula` | 446 | one exact structured-byte formula |
| `binary_structured_byte_formula_abstract` | 152 | one exact formula, abstract family only as extra evidence |
| `binary_structured_byte_not_formula` | 25 | one exact NOT-extended structured formula |
| `binary_byte_transform` | 11 | one transform name only |
| `binary_affine_xor` | 107 | `affine_free_var_counts` all zero |
| `binary_bit_permutation_bijection` | 71 | `bijection_search_explored == 1` |
| `binary_bit_permutation_independent` | 5 | every output slot has exactly one source in `bit_candidate_signature` |
| **Total** | **817** |  |

These strong rows are **not** exact-trace-safe as-is:

| group | rows | why excluded from exact CoT base |
| --- | ---: | --- |
| `binary_two_bit_boolean` | 135 | answer can be unique while boolean operation is not unique |
| `binary_three_bit_boolean` | 17 | same issue at 3-input boolean level |
| `binary_affine_xor` | 26 | answer unique on query, but affine free variables remain |
| `binary_bit_permutation_bijection` | 7 | multiple bijections collapse to the same answer |
| `binary_bit_permutation_independent` | 2 | multiple source mappings collapse to the same answer |

### 9.3 Reproduction command for the exact-trace-safe base

Run from repo root:

```bash
uv run python - <<'PY'
import csv
import json
import re
from collections import Counter
from pathlib import Path

path = Path("cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv")
rows = []
with path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["family"] == "bit_manipulation" and row["selection_tier"] == "verified_trace_ready":
            rows.append(row)

def parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        return {}

def parse_signature_counts(signature):
    counts = []
    for match in re.finditer(r"o\d+=\[([^\]]*)\]", signature):
        inner = match.group(1).strip()
        counts.append(0 if inner == "" else len([x for x in inner.split(",") if x]))
    return counts

safe = []
for row in rows:
    cand = row["teacher_solver_candidate"]
    meta = parse_json(row["family_analysis_json"])
    ok = False

    if cand in {
        "binary_structured_byte_formula",
        "binary_structured_byte_formula_abstract",
        "binary_structured_byte_not_formula",
    }:
        ok = True
    elif cand == "binary_byte_transform":
        names = [x for x in row["bit_byte_transform_names"].split("|") if x]
        ok = len(names) == 1
    elif cand == "binary_affine_xor":
        free = meta.get("affine_free_var_counts", [])
        ok = bool(free) and all(v == 0 for v in free)
    elif cand == "binary_bit_permutation_bijection":
        ok = meta.get("bijection_search_explored", 0) == 1
    elif cand == "binary_bit_permutation_independent":
        counts = parse_signature_counts(row["bit_candidate_signature"])
        ok = bool(counts) and all(v == 1 for v in counts)

    if ok:
        safe.append(row)

counter = Counter(row["teacher_solver_candidate"] for row in safe)
print("TOTAL_SAFE", len(safe))
for name, count in sorted(counter.items()):
    print(name, count)
PY
```

Expected result:

- `TOTAL_SAFE 817`

## 10. How the CoT should be taught

For this `817`-row base, the recommended teacher is not free-form prose.

Use a **canonical program trace**:

1. infer the exact hidden rule from examples
2. show `1-2` short example checks that support that rule
3. restate the rule in explicit executable form
4. apply that rule to the query input
5. output the final binary answer

### 10.1 Recommended trace style

Use a short deterministic trace such as:

```text
<think>
Check examples:
- 11010000 -> 10101101 because shl1=10100000, shr4=00001101, xor=10101101
- 11011111 -> 10110011 because shl1=10111110, shr4=00001101, xor=10110011
So the rule is xor(shl1,shr4).
Query x = 10110110
shl1(x) = 01101100
shr4(x) = 00001011
xor(shl1(x), shr4(x)) = 01100111
Final answer = 01100111
</think>
\boxed{01100111}
```

Guidelines:

- prefer **program notation** over loose natural-language explanation
- keep step order fixed across all rows in the same group
- always include a short **rule-identification prefix** from `1-2` representative examples
- name the exact transform that generated the row
- avoid narrative filler
- avoid abstract family names in place of executable rules
- do not dump all prompt examples into the trace; the goal is short evidence, not full replay

### 10.2 Why this is preferable to answer-only SFT

If the model sees only `(problem, answer)`, it can overfit to surface patterns.

If the model sees `(problem, exact program trace, answer)`, it can instead learn:

- how to infer the transform from examples
- how to execute that transform on a fresh query

That matches the `README.md` evaluation setup better than answer memorization because final scoring depends on the produced answer, while the CoT acts as a training scaffold for internalizing the operation.

### 10.3 Worked example: automatic CoT generation

A concrete example from the current strong slice:

- row id: `04d492a9`
- strong group: `binary_structured_byte_formula`
- exact rule: `xor(shl1,shr4)`
- query: `10011111`
- gold answer: `00110111`

The important point is that the Python side does **not** write free-form reasoning from scratch.

Instead it does:

1. detect the exact rule from the examples
2. choose `1-2` representative examples and serialize short verification lines
3. execute that exact rule on the query
4. serialize the whole sequence into a canonical trace template

Pseudo-code:

```python
def shl(bits: str, k: int) -> str:
    return format((int(bits, 2) << k) & 0xFF, "08b")

def shr(bits: str, k: int) -> str:
    return format((int(bits, 2) >> k) & 0xFF, "08b")

def xor_bits(left: str, right: str) -> str:
    return format(int(left, 2) ^ int(right, 2), "08b")

def emit_cot_for_structured_formula(
    formula_name: str,
    support_examples: list[tuple[str, str]],
    query_bits: str,
) -> str:
    if formula_name != "xor(shl1,shr4)":
        raise ValueError("This worked example is specialized to one exact formula.")

    support_lines = []
    for input_bits, output_bits in support_examples[:2]:
        shl1_support = shl(input_bits, 1)
        shr4_support = shr(input_bits, 4)
        recomputed = xor_bits(shl1_support, shr4_support)
        support_lines.append(
            f"- {input_bits} -> {output_bits} because "
            f"shl1={shl1_support}, shr4={shr4_support}, xor={recomputed}"
        )

    shl1_value = shl(query_bits, 1)
    shr4_value = shr(query_bits, 4)
    answer = xor_bits(shl1_value, shr4_value)

    return f"""<think>
Check examples:
{chr(10).join(support_lines)}
So the rule is xor(shl1,shr4).
Query x = {query_bits}
shl1(x) = {shl1_value}
shr4(x) = {shr4_value}
xor(shl1(x), shr4(x)) = {answer}
Final answer = {answer}
</think>
\\boxed{{{answer}}}"""
```

For this row, the generated CoT becomes:

```text
<think>
Check examples:
- 11010000 -> 10101101 because shl1=10100000, shr4=00001101, xor=10101101
- 11011111 -> 10110011 because shl1=10111110, shr4=00001101, xor=10110011
So the rule is xor(shl1,shr4).
Query x = 10011111
shl1(x) = 00111110
shr4(x) = 00001001
xor(shl1(x), shr4(x)) = 00110111
Final answer = 00110111
</think>
\boxed{00110111}
```

Why this is the right pattern for large-scale synthesis:

- the trace now teaches **rule identification from examples** as well as query execution
- the trace is generated from the **same executable rule** that creates the answer
- every intermediate value is programmatically recoverable
- the final answer can be re-checked by the same solver family
- the trace teaches the model to **apply an operation to the query**, not just to memorize `(prompt, answer)`

For other exact-trace-safe groups, only the trace template changes:

- structured-byte groups:
  - emit source transforms and the final composition
- affine exact:
  - emit the recovered GF(2) equations and then substitute query bits
- bijection / independent exact:
  - emit the mapping table and then read off each output bit
- byte transform:
  - emit the concrete transform name and parameter, then apply it once

## 11. Group-by-group CoT construction policy

This section describes how to generate the teacher CoT for each exact-trace-safe strong group.

Unless noted otherwise, every group below should follow the same high-level shape:

1. show `1-2` short example checks that pin down the rule
2. state the exact executable rule
3. execute the rule on the query
4. emit the final boxed answer

### 11.1 `binary_structured_byte_formula` (`446`)

**Use as CoT base:** Yes

**Why safe:**

- report 43 requires exactly one semantic structured-byte formula
- that formula predicts gold
- and the formula has repeated zero-error support

**Teacher payload to emit:**

1. `1-2` example checks proving the exact formula
2. exact formula name from `bit_structured_formula_name`
3. query byte `x`
4. each intermediate source transform in the formula
5. final composition result

**Canonical trace shape:**

```text
Check examples:
- <example 1 verification line>
- <example 2 verification line>
So the rule is <exact formula name>.
Query x = <8-bit query>
<source_1>(x) = <8-bit>
<source_2>(x) = <8-bit>
...
<formula>(...) = <8-bit>
Final answer = <8-bit>
```

**Good examples of exact trace content:**

- `xor(shl2,shr1)`
- `or(ror2,shl3)`
- `choose(shl5,shr3,rol1)`
- `majority(ror3,shl1,shr2)`

**Verification rule:**

- re-run `infer_bit_structured_byte_formula_matches(...)`
- require exactly one exact formula match
- require that exact formula to be the same formula written in the trace

### 11.2 `binary_structured_byte_formula_abstract` (`152`)

**Use as CoT base:** Yes

**Important constraint:**

- do **not** teach the abstract family alone
- teach the row's **exact formula**

**Why safe:**

- report 45 still assumes one exact formula match for the row
- the abstract family is only extra confidence evidence

**Teacher payload to emit:**

1. exact formula name from `bit_structured_formula_name`
2. optional metadata field outside the CoT: abstract family name
3. query execution steps exactly as in section 11.1

**Do not emit this as trace:**

```text
So the rule is xor(rol,shr).
```

by itself.

Instead emit:

```text
So the rule is xor(rol1,shr3).
```

or whatever exact formula generated that row.

**Verification rule:**

- same as `binary_structured_byte_formula`
- abstract family may be logged in metadata, but not used as the executable trace body

### 11.3 `binary_structured_byte_not_formula` (`25`)

**Use as CoT base:** Yes

**Why safe:**

- the row has one exact NOT-extended formula

**Teacher payload to emit:**

1. exact formula from `bit_not_structured_formula_name`
2. explicit expansion of every `not(...)` source
3. final composition result

**Canonical trace shape:**

```text
Check examples:
- <example 1 verification line>
- <example 2 verification line>
So the rule is xor(not(shl2), shl6).
Query x = <8-bit query>
shl2(x) = <8-bit>
not(shl2(x)) = <8-bit>
shl6(x) = <8-bit>
xor(not(shl2(x)), shl6(x)) = <8-bit>
Final answer = <8-bit>
```

**Verification rule:**

- re-run `infer_bit_structured_byte_not_formula_matches(...)`
- require one exact formula and exact agreement

### 11.4 `binary_byte_transform` (`11`)

**Use as CoT base:** Yes

**Why safe:**

- only one transform name survives in `bit_byte_transform_names`

**Teacher payload to emit:**

1. transform name
2. transform parameter if any
3. direct application to query

**Canonical trace shape:**

```text
Check examples:
- <example 1 verification line>
- <example 2 verification line>
So the rule is rshift by 1.
Query x = <8-bit query>
rshift_1(x) = <8-bit>
Final answer = <8-bit>
```

or

```text
Check examples:
- <example 1 verification line>
- <example 2 verification line>
So the rule is or_mask with mask <8-bit mask>.
Query x = <8-bit query>
x OR mask = <8-bit>
Final answer = <8-bit>
```

**Implementation note:**

- for mask-based transforms, export the concrete mask during synthetic generation

**Verification rule:**

- re-run `infer_bit_byte_transform_answer(...)`
- require one transform name and exact agreement

### 11.5 `binary_affine_xor` exact subset (`107`)

**Use as CoT base:** Yes

**Why only subset:**

- only rows with `affine_free_var_counts == [0, ..., 0]` have a unique affine map
- the other `26` rows are answer-unique only

**Teacher payload to emit:**

1. eight explicit output equations over GF(2)
2. query substitution into each equation
3. concatenated output byte

**Canonical trace shape:**

```text
Check examples:
- <example 1 verification line>
- <example 2 verification line>
So the rule is:
o1 = i2 xor i5
o2 = i1 xor 1
o3 = i4
...
Query x = <8-bit query>
o1 = <bit> xor <bit> = <bit>
o2 = <bit> xor 1 = <bit>
...
Output byte = <8-bit>
Final answer = <8-bit>
```

**Important implementation note:**

- the current row ledger stores `affine_free_var_counts`
- but it does **not** store the solved coefficient vectors
- therefore the synthetic data builder should extend the GF(2) solver to export the final affine coefficients for each output bit

**Verification rule:**

- solve the affine system again from examples
- require zero free variables on every output bit
- require the re-solved equations to match the emitted trace

### 11.6 `binary_bit_permutation_bijection` exact subset (`71`)

**Use as CoT base:** Yes

**Why only subset:**

- use only rows with `bijection_search_explored == 1`
- the other `7` rows have multiple bijections that collapse to the same answer

**Teacher payload to emit:**

1. full output-to-input permutation table
2. inversion flag per output bit if present
3. query execution by table lookup

**Canonical trace shape:**

```text
Check examples:
- <example 1 verification line>
- <example 2 verification line>
So the rule is:
o1 <- i8
o2 <- i1
o3 <- not(i2)
...
Query x = <8-bit query>
o1 = i8 = <bit>
o2 = i1 = <bit>
o3 = not(i2) = <bit>
...
Output byte = <8-bit>
Final answer = <8-bit>
```

**Verification rule:**

- re-run the bijection search
- require exactly one complete bijection assignment
- require the emitted mapping table to be that assignment

### 11.7 `binary_bit_permutation_independent` exact subset (`5`)

**Use as CoT base:** Yes

**Why only subset:**

- use only rows whose `bit_candidate_signature` has exactly one candidate in every output slot
- two rows were removed from the preliminary count because they still had multi-source ambiguity

**Teacher payload to emit:**

1. one copy/invert rule per output bit
2. query execution by slot

**Canonical trace shape:**

```text
Check examples:
- <example 1 verification line>
- <example 2 verification line>
So the rule is:
o1 <- not(i3)
o2 <- not(i3)
o3 <- i1
...
Query x = <8-bit query>
o1 = not(i3) = <bit>
o2 = not(i3) = <bit>
o3 = i1 = <bit>
...
Output byte = <8-bit>
Final answer = <8-bit>
```

**Verification rule:**

- parse `bit_candidate_signature`
- require one candidate only in every output slot
- require query execution from that mapping table to match gold

## 12. Recommended synthesis + CoT pipeline

Use the following protocol for mass generation.

1. Pick one exact-trace-safe group from the `817`-row base.
2. Pick one **concrete synthesis key** inside that group.
3. Keep one prompt to one exact hidden rule.
4. Sample fresh 8-bit inputs for examples and one query.
5. Compute outputs by forward execution.
6. Export a **canonical program trace** in the group-specific format above, including the short rule-identification prefix from `1-2` examples.
7. Re-run the corresponding solver on the generated prompt.
8. Keep only rows that satisfy all of:
   - exact gold answer match
   - intended solver family still fires
   - intended exact rule is uniquely recovered
   - emitted CoT matches that exact rule
9. Discard anything that falls into:
   - multi-formula ambiguity
   - answer-only uniqueness without procedural uniqueness
   - conflicting solver outputs

## 13. Minimal acceptance checklist

Before adding synthetic rows to training, verify:

- [ ] one prompt contains only one concrete hidden transform
- [ ] gold answer is produced by forward execution
- [ ] the same codebase solver recovers the same answer
- [ ] the same codebase solver recovers the same **procedure**
- [ ] the emitted CoT uses executable exact rules, not abstract family names
- [ ] the row belongs to the `817` exact-trace-safe base or an equivalently re-generated exact-rule slice

## 14. Bottom line

For large-scale binary problem-answer-CoT generation, the best current reusable base is:

- `1004` strong rows for answer-level supervision
- `817` exact-trace-safe rows for **LoRA-only procedural CoT supervision**
- `395` strict patterns in the broader strong slice
- all `817` rows can be turned into executable, code-verifiable program traces

Operationally:

- use the `817` rows as the direct seed for problem-answer-CoT generation
- do **not** use the remaining `187` strong-but-trace-ambiguous rows as-is for exact CoT
- if those `187` rows are needed later, regenerate them from fixed exact rules first

## 15. Post-generation strict quality gate

Generated synthetic rows should **not** go directly into training.

Every candidate row should pass a deterministic quality gate before it is accepted into the final problem-answer-CoT corpus.

This is especially important because:

- `README.md` scoring depends on the final extracted answer
- the metric prioritizes `\boxed{}` extraction
- our training goal is stronger than answer correctness alone: we also want the emitted CoT to encode the **same exact executable procedure**

### 15.1 Required row schema for quality checking

The generated dataset should store at least the following columns:

| column | purpose |
| --- | --- |
| `synthetic_id` | unique row id |
| `strong_group` | one of the exact-trace-safe groups |
| `exact_rule` | concrete executable rule used to generate the row |
| `prompt` | final training prompt |
| `answer` | gold binary answer |
| `teacher_response` | full CoT plus final `\boxed{}` |
| `query_bits` | query input in 8-bit form |
| `support_examples_json` | the `1-2` representative examples used in the trace prefix |
| `all_examples_json` | all prompt examples as structured data |
| `trace_metadata_json` | exact intermediate values or resolved mapping/equation data used by the renderer |

For `binary_affine_xor`, `binary_bit_permutation_bijection`, and `binary_bit_permutation_independent`, `trace_metadata_json` should include the exact executable object that was rendered into the CoT:

- affine equations
- full bijection mapping
- full independent copy/invert mapping

Without that metadata, exact byte-identical CoT re-rendering is not possible.

### 15.2 Quality-gate order

Run checks in the following order.

1. **Schema check**
   - required columns exist
   - JSON fields parse successfully
   - `answer` and `query_bits` are valid 8-bit strings

2. **Metric-format check**
   - exactly one non-empty `\boxed{...}` appears in `teacher_response`
   - `teacher_response.rstrip().endswith(f"\\boxed{{{answer}}}")`
   - the notebook-style answer extractor returns exactly `answer`

3. **Forward-answer check**
   - recompute the answer from `exact_rule` and `query_bits`
   - require the recomputed answer to equal `answer`

4. **Solver-recovery check**
   - re-run the corresponding solver on `all_examples_json + query_bits`
   - require the intended strong group to fire again
   - require the intended exact rule to be recovered again

5. **Procedure-uniqueness check**
   - require the row to remain in the exact-trace-safe subset
   - reject anything that collapses only at answer level but not at procedure level

6. **Canonical-render check**
   - re-render the expected CoT from `strong_group + exact_rule + support_examples_json + trace_metadata_json + query_bits + answer`
   - require **byte-identical equality**:
     - `teacher_response == render_teacher_response(row)`

7. **Dataset-level checks**
   - remove exact duplicates
   - reject degenerate rows with repeated prompt/example content
   - review group / rule balance so one easy exact rule does not dominate the final corpus

### 15.3 Group-specific acceptance rules

Use the following strict acceptance rules after generation.

| group | strict acceptance rule |
| --- | --- |
| `binary_structured_byte_formula` | `infer_bit_structured_byte_formula_matches(...)` returns exactly one match and it is `(exact_rule, answer)` |
| `binary_structured_byte_formula_abstract` | same as above; abstract family may be logged but exact rule must still be unique |
| `binary_structured_byte_not_formula` | `infer_bit_structured_byte_not_formula_matches(...)` returns exactly one match and it is `(exact_rule, answer)` |
| `binary_byte_transform` | `infer_bit_byte_transform_answer(...)` returns `answer` and exactly one transform name matching `exact_rule` |
| `binary_affine_xor` | `infer_bit_affine_xor_answer(...)` returns `answer` and `affine_free_var_counts` are all zero |
| `binary_bit_permutation_bijection` | bijection solver returns exactly one query answer and `bijection_search_explored == 1`; emitted mapping must equal `trace_metadata_json` |
| `binary_bit_permutation_independent` | independent solver returns `answer` and every output slot has exactly one source; emitted mapping must equal `trace_metadata_json` |

### 15.4 Canonical-render principle

The strongest check is not a loose regex check on the CoT text.

Instead:

1. generate `teacher_response` from structured metadata
2. later, regenerate the same response from the same metadata
3. require the two strings to be identical

This eliminates silent formatting drift such as:

- missing `Check examples:` block
- wrong support example order
- wrong intermediate value in one line
- extra text after the final `\boxed{}`
- abstract-family wording where exact-rule wording was required

### 15.5 Recommended rejection reasons

Write every failed row to a rejected artifact with one of these reasons:

- `missing_required_column`
- `json_parse_error`
- `invalid_bitstring`
- `bad_boxed_count`
- `final_box_not_terminal`
- `metric_extraction_mismatch`
- `forward_answer_mismatch`
- `solver_family_mismatch`
- `exact_rule_mismatch`
- `procedure_not_unique`
- `canonical_render_mismatch`
- `duplicate_row`
- `balance_overflow`

### 15.6 Reproducible validation command template

The following command is a reproducible template for post-generation QC.

It assumes a generated CSV with the schema above and reuses the notebook-style answer extraction rule plus the existing binary solvers.

```bash
uv run python - <<'PY'
import csv
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

CSV_PATH = Path("cuda-train-data-analysis-v1/artifacts/generated_bit_cot_candidates_v1.csv")
MODULE_PATH = Path("cuda-train-data-analysis-v1/code/train_data_analysis_v1.py")

spec = importlib.util.spec_from_file_location("train_data_analysis_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

REQUIRED_COLUMNS = [
    "synthetic_id",
    "strong_group",
    "exact_rule",
    "prompt",
    "answer",
    "teacher_response",
    "query_bits",
    "support_examples_json",
    "all_examples_json",
    "trace_metadata_json",
]

def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"
    matches = re.findall(r'\\boxed\\{([^}]*)(?:\\}|$)', text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    patterns = [
        r'The final answer is:\\s*([^\\n]+)',
        r'Final answer is:\\s*([^\\n]+)',
        r'Final answer\\s*[:：]\\s*([^\\n]+)',
        r'final answer\\s*[:：]\\s*([^\\n]+)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1].strip()
    matches = re.findall(r'-?\\d+(?:\\.\\d+)?', text)
    if matches:
        return matches[-1]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"

def count_non_empty_boxed(text: str) -> int:
    return sum(1 for match in re.findall(r'\\boxed\\{([^}]*)\\}', text) if match.strip())

def parse_examples(raw: str):
    data = json.loads(raw)
    return [(item[0], item[1]) for item in data]

def validate_exact_group(row: dict) -> tuple[bool, str]:
    group = row["strong_group"]
    exact_rule = row["exact_rule"]
    answer = row["answer"]
    query_bits = row["query_bits"]
    examples = parse_examples(row["all_examples_json"])

    if group == "binary_structured_byte_formula":
        matches = mod.infer_bit_structured_byte_formula_matches(examples, query_bits)
        return (len(matches) == 1 and matches[0] == (exact_rule, answer), "solver")

    if group == "binary_structured_byte_formula_abstract":
        matches = mod.infer_bit_structured_byte_formula_matches(examples, query_bits)
        return (len(matches) == 1 and matches[0] == (exact_rule, answer), "solver")

    if group == "binary_structured_byte_not_formula":
        matches = mod.infer_bit_structured_byte_not_formula_matches(examples, query_bits)
        return (len(matches) == 1 and matches[0] == (exact_rule, answer), "solver")

    if group == "binary_byte_transform":
        predicted, names = mod.infer_bit_byte_transform_answer(examples, query_bits)
        return (predicted == answer and len(names) == 1 and names[0] == exact_rule, "solver")

    if group == "binary_affine_xor":
        predicted, free_vars = mod.infer_bit_affine_xor_answer(examples, query_bits)
        return (predicted == answer and free_vars and all(v == 0 for v in free_vars), "solver")

    if group == "binary_bit_permutation_bijection":
        candidate_sets = mod.build_bit_candidate_sets(examples)
        answers, explored = mod.infer_bit_bijection_answers(candidate_sets, query_bits)
        return (answer in answers and len(answers) == 1 and explored == 1, "solver")

    if group == "binary_bit_permutation_independent":
        candidate_sets = mod.build_bit_candidate_sets(examples)
        predicted, choice_counts = mod.infer_bit_independent_answer(candidate_sets, query_bits)
        return (predicted == answer and choice_counts and all(v == 1 for v in choice_counts), "solver")

    return (False, "unknown_group")

def render_teacher_response(row: dict) -> str:
    # This function must be the same canonical renderer used during generation.
    # The QC rule is: render_teacher_response(row) must match teacher_response byte-for-byte.
    raise NotImplementedError("Use the same canonical renderer as the generation pipeline.")

accepted = []
rejected = []
seen = set()
reason_counter = Counter()

with CSV_PATH.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    if reader.fieldnames is None:
        raise ValueError("CSV has no header.")
    missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for row in reader:
        reason = None

        key = (
            row["strong_group"],
            row["exact_rule"],
            row["query_bits"],
            row["answer"],
            row["teacher_response"],
        )
        if key in seen:
            reason = "duplicate_row"
        seen.add(key)

        if reason is None:
            try:
                json.loads(row["support_examples_json"])
                json.loads(row["all_examples_json"])
                json.loads(row["trace_metadata_json"])
            except Exception:
                reason = "json_parse_error"

        if reason is None:
            if not re.fullmatch(r"[01]{8}", row["query_bits"]) or not re.fullmatch(r"[01]{8}", row["answer"]):
                reason = "invalid_bitstring"

        if reason is None:
            text = row["teacher_response"]
            if count_non_empty_boxed(text) != 1:
                reason = "bad_boxed_count"
            elif not text.rstrip().endswith(f"\\boxed{{{row['answer']}}}"):
                reason = "final_box_not_terminal"
            elif extract_final_answer(text) != row["answer"]:
                reason = "metric_extraction_mismatch"

        if reason is None:
            ok, _ = validate_exact_group(row)
            if not ok:
                reason = "solver_family_mismatch"

        if reason is None:
            try:
                expected = render_teacher_response(row)
                if row["teacher_response"] != expected:
                    reason = "canonical_render_mismatch"
            except NotImplementedError:
                reason = "canonical_render_mismatch"

        if reason is None:
            accepted.append(row)
        else:
            row["reject_reason"] = reason
            rejected.append(row)
            reason_counter[reason] += 1

print("accepted", len(accepted))
print("rejected", len(rejected))
print("reject_reasons", dict(reason_counter))
PY
```

### 15.7 Expected QC artifacts

After the gate, write:

- `generated_bit_cot_accepted_v1.csv`
- `generated_bit_cot_rejected_v1.csv`
- `generated_bit_cot_quality_summary_v1.json`

The summary JSON should include:

- accepted row count
- rejected row count
- reject reasons histogram
- per-group accepted counts
- per-exact-rule accepted counts
- duplicate count

### 15.8 Practical bottom line

The final training corpus should be:

- generated from the `817` exact-trace-safe base
- accepted only after exact solver recovery
- accepted only after notebook-compatible `\boxed{}` extraction succeeds
- accepted only after byte-identical canonical CoT re-rendering succeeds

If any of these fail, the row should be rejected even if the final answer looks correct.
