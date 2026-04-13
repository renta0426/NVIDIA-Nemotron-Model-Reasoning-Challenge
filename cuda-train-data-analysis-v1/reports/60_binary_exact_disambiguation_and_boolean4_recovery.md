# cuda-train-data-analysis-v1 binary exact disambiguation and boolean4 recovery

## Purpose

Document the **audited** recovery result for `bit_manipulation`.

The first broad exact-disambiguation attempt temporarily reached `1522 / 1602` verified, but a strict re-audit showed that many of those rows were only unique inside one exact library, not across the full exact-library union. Per `README.md`, the competition metric is final-answer `Accuracy`, but this ledger's `verified_trace_ready` tier is stricter: the prompt must still support an executable exact rule strongly enough to justify trace-style supervision.

## Baseline before this pass

Committed baseline for `bit_manipulation`:

| tier | rows |
| --- | ---: |
| `verified_trace_ready` | 1004 |
| `answer_only_keep` | 445 |
| `manual_audit_priority` | 138 |
| `exclude_suspect` | 15 |

The original target was `1522 / 1602` verified rows (`95.01%`), but that number did **not** survive the strict audit.

## Added recovery passes

### 1. Four-bit boolean dispatch

`infer_bit_four_bit_boolean_answer(...)` already existed in `code/train_data_analysis_v1.py`, but it was not wired into the teacher dispatch.

After enabling it:

- net gain versus the committed baseline: `+9 verified`
- source tiers: `answer_only 7 + manual 2`
- artifact: `artifacts/binary_four_bit_boolean_verified_v1.csv`

Note: the artifact contains `38` current boolean4 verified rows because `29` of them were already verified before this pass.

### 2. Late manual exact reread

Prompt-backed exact rows that were still stuck in `answer_only_keep` or `manual_audit_priority` were re-evaluated after the leave-one-out safety pass.

- net gain versus the committed baseline: `+62 verified`
- source tiers: `answer_only 60 + manual 2`
- artifact: `artifacts/binary_manual_exact_reverified_v1.csv`

This late exact pass also captured the two additional majority rows identified during audit:

- `5791e7c4` -> `majority(nibble_swap,shl6,shr6)`
- `ea10e59c` -> `majority(rol1,shl5,shr1)`

### 3. Audited exact disambiguation across binary libraries

After the strict re-audit, exact disambiguation is now limited to rows where the full union of:

- `structured`
- `not_structured`
- `stage1`
- `stage2`

collapses to **one overall `(formula, prediction)` pair**.

Audited net gain versus the committed baseline:

- `+154 verified`
- source tiers: `answer_only 107 + manual 47`
- decision rule: `154 overall_unique_exact_formula`
- source libraries: `stage2 142`, `structured 9`, `not_structured 3`
- artifact: `artifacts/binary_exact_disambiguation_verified_v1.csv`

The broader initial exact-disambiguation attempt had produced `447` rows, so the audit removed `293` rows from `verified_trace_ready`.

## Final result

Audited final `bit_manipulation` ledger:

| tier | rows |
| --- | ---: |
| `verified_trace_ready` | 1229 |
| `answer_only_keep` | 271 |
| `manual_audit_priority` | 87 |
| `exclude_suspect` | 15 |

Verified rate:

- `1229 / 1602 = 76.72%`

Net change versus the committed baseline:

- `+225 verified`
- `-174 answer_only`
- `-51 manual`
- `exclude` unchanged at `15`

## Remaining hold slice

The remaining `87` manual rows are:

- `86` `bit_other`
- `1` `bit_permutation_inversion`

They were intentionally left unresolved because they still do not admit a stable unique exact family under:

- permutation
- boolean2 / boolean3 / boolean4
- affine xor
- byte transform
- structured / not-structured / stage1 / stage2 exact-library disambiguation

So the residual is no longer a broad missed family, but it is also **not** thin enough to claim a 95% trace-safe binary core after audit.

## Artifacts and follow-up references

- `artifacts/selection_summary_v1.csv`
- `artifacts/train_row_analysis_v1.csv`
- `artifacts/binary_four_bit_boolean_verified_v1.csv`
- `artifacts/binary_manual_exact_reverified_v1.csv`
- `artifacts/binary_exact_disambiguation_verified_v1.csv`
- `reports/61_binary_promotion_audit.md`
- `FINAL_SUMMARY_REPORT.md`
