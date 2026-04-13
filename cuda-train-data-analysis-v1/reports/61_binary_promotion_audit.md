# cuda-train-data-analysis-v1 binary promotion audit

## Purpose

Perform a strict reproducibility and validity audit of the recent `bit_manipulation` promotions.

The central question was not just "can the code reproduce the larger verified count?", but "does that larger count still satisfy the repo's stricter `verified_trace_ready` standard after an adversarial review?"

## README-grounded audit criterion

`README.md` says the competition metric is final-answer `Accuracy`.

That matters because:

- `answer_only_keep` can still be useful for final-answer supervision
- but `verified_trace_ready` in this repo is a stricter operational label for trace-style teacher generation
- so rows that are only "good enough for final-answer supervision" must not be left in `verified_trace_ready`

## What failed the strict audit

The first broad exact-disambiguation pass promoted rows whenever one exact library looked unique or dominant locally.

An independent recomputation across the full exact-library union showed that this was too permissive:

- initial broad exact-disambiguation rows: `447`
- audited rows that still collapse to one overall `(formula, prediction)` pair: `154`
- rows removed from `verified_trace_ready` by the audit: `293`

So the corrected rule is now:

> only keep exact-disambiguation promotions when `structured + not_structured + stage1 + stage2` together still imply one overall exact `(formula, prediction)` pair.

## Corrected audited result

Final audited `bit_manipulation` ledger:

| tier | rows |
| --- | ---: |
| `verified_trace_ready` | 1229 |
| `answer_only_keep` | 271 |
| `manual_audit_priority` | 87 |
| `exclude_suspect` | 15 |

Coverage:

- `1229 / 1602 = 76.72% verified`

Net gain versus the committed baseline:

- `binary_four_bit_boolean`: `+9`
- `binary_manual_exact_reverified`: `+62`
- `binary_exact_disambiguation_verified`: `+154`
- total: `+225 verified`

## Fresh rerun reproducibility check

The corrected analysis was rerun into:

- repo output: `cuda-train-data-analysis-v1/`
- fresh temp output: `tmp_runtime_env/promotion_audit_repro_corrected/`

The key artifacts matched byte-for-byte.

| artifact | SHA256 |
| --- | --- |
| `selection_summary_v1.csv` | `4eeff30a045ffac0f19541a289977c89d9de224969c5ab866d6eeedff357ab19` |
| `train_row_analysis_v1.csv` | `f0130417b26584407cf94a0f62941f7102f5294c92439d2abc1b7cb1534409d6` |
| `binary_exact_disambiguation_verified_v1.csv` | `4d1cd05bae491aeaf8ff02f1632bc00c21fb101620e941638c997c2edfbfc32a` |
| `binary_manual_exact_reverified_v1.csv` | `674344dbcd2cee41d54340371aa2861d23875b4d9c4d82f29924245942067ad4` |
| `binary_four_bit_boolean_verified_v1.csv` | `2a0d85722d5daf97b7cd4b758a0c1b4ef36ecd19f859dd21d03292afa666a2b8` |

The temp rerun also reproduced the same selection-tier totals:

- `verified_trace_ready = 6711`
- `answer_only_keep = 2652`
- `manual_audit_priority = 113`
- `exclude_suspect = 24`

## Bottom line

The corrected pipeline is reproducible, but the earlier `95.01% verified` claim was not strict enough.

After the audit, the defensible audited result is:

- `bit_manipulation = 1229 verified / 271 answer_only / 87 manual / 15 exclude`
- `verified coverage = 76.72%`
