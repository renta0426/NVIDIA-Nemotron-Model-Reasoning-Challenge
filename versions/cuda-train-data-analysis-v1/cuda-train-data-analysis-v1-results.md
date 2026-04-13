# cuda-train-data-analysis-v1 results log

## 2026-04-12 strict promotion audit

Re-run command:

```bash
uv run python cuda-train-data-analysis-v1/code/train_data_analysis_v1.py \
  --repo-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge \
  --out-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/cuda-train-data-analysis-v1
```

`README.md` premise used for the audit:

- competition metric is final-answer `Accuracy`
- this analysis ledger still distinguishes `verified_trace_ready` from `answer_only_keep`
- `verified` promotion must remain stronger than plain final-answer supervision

Initial broad run:

- `bit_manipulation = 1522 / 1602 = 95.01% verified`
- strict audit rejected that exact-disambiguation rule as too broad

Corrected audited result:

| scope | total | verified | answer_only | manual | exclude | note |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| overall selection tiers | 9500 | 6711 | 2652 | 113 | 24 | from `artifacts/selection_summary_v1.csv` |
| `bit_manipulation` | 1602 | 1229 | 271 | 87 | 15 | `76.72%` verified |

Net binary verified gain versus the committed baseline:

- `+225 verified` total
- `binary_four_bit_boolean`: `+9`
- `binary_manual_exact_reverified`: `+62`
- `binary_exact_disambiguation_verified`: `+154`

Fresh temp rerun reproduced the same key artifacts byte-for-byte:

- `selection_summary_v1.csv`: `4eeff30a045ffac0f19541a289977c89d9de224969c5ab866d6eeedff357ab19`
- `train_row_analysis_v1.csv`: `f0130417b26584407cf94a0f62941f7102f5294c92439d2abc1b7cb1534409d6`
- `binary_exact_disambiguation_verified_v1.csv`: `4d1cd05bae491aeaf8ff02f1632bc00c21fb101620e941638c997c2edfbfc32a`
- `binary_manual_exact_reverified_v1.csv`: `674344dbcd2cee41d54340371aa2861d23875b4d9c4d82f29924245942067ad4`
- `binary_four_bit_boolean_verified_v1.csv`: `2a0d85722d5daf97b7cd4b758a0c1b4ef36ecd19f859dd21d03292afa666a2b8`

Primary evidence:

- `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`
- `cuda-train-data-analysis-v1/reports/60_binary_exact_disambiguation_and_boolean4_recovery.md`
- `cuda-train-data-analysis-v1/reports/61_binary_promotion_audit.md`
- `cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv`
- `cuda-train-data-analysis-v1/artifacts/selection_summary_v1.csv`
