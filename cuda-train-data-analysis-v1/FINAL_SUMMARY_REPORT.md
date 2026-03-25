# cuda-train-data-analysis-v1 Final Summary Report

## 1. Purpose and evaluation context

This folder contains the final outputs of the train-data analysis task requested in `try-cuda-train-data-analyst-plan.md`.

Per `README.md`, the competition score is determined by **accuracy**: the Nemotron model is evaluated on its final boxed answer, and the leaderboard score is the proportion of correct answers. Because of that, this analysis prioritized:

- maximizing trustworthy answer supervision
- separating strong teacher rows from ambiguous rows
- isolating suspicious labels instead of forcing them into training
- producing a clear manual-audit queue for the remaining hard families

No training was run in this workstream. This folder is analysis-only.

## 2. Executive summary

The dataset analysis covered all `9,500` rows from `data/train.csv`.

### Final selection tiers

| selection_tier | rows | share |
| --- | ---: | ---: |
| `verified_trace_ready` | 5,827 | 61.3% |
| `answer_only_keep` | 1,036 | 10.9% |
| `manual_audit_priority` | 2,620 | 27.6% |
| `exclude_suspect` | 17 | 0.2% |

### What this means

- Safe learning core: `5,827 + 1,036 = 6,863` rows (`72.2%`)
- Remaining unresolved/suspicious rows: `2,620 + 17 = 2,637` rows (`27.8%`)
- Bottom line: the result is **good and practically useful**, but **not perfect**

## 3. Family-level final result

| family | total | verified | answer_only | manual | exclude | summary |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `roman_numeral` | 1,576 | 1,576 | 0 | 0 | 0 | Essentially complete |
| `gravity_constant` | 1,597 | 1,597 | 0 | 0 | 0 | Essentially complete |
| `unit_conversion` | 1,594 | 1,594 | 0 | 0 | 0 | Essentially complete |
| `text_decryption` | 1,576 | 605 | 971 | 0 | 0 | All unresolved rows were clean answer-only completions |
| `bit_manipulation` | 1,602 | 381 | 0 | 1,213 | 8 | Major remaining bottleneck |
| `symbol_equation` | 1,555 | 74 | 65 | 1,407 | 9 | Major remaining bottleneck |

### Interpretation

- `roman`, `gravity`, and `unit` are effectively solved for curation purposes.
- `text` is in good shape for accuracy-oriented supervision, but `971` rows are still **answer-only**, not full reasoning-trace teachers.
- The two hard residual families are `bit_manipulation` and `symbol_equation`.

## 4. Main improvements achieved

### 4.1 Binary

Binary coverage improved beyond the earlier baseline by adding multiple rule families:

- bit permutation / inversion
- 2-bit boolean rules
- 3-bit boolean rules
- affine XOR over GF(2)
- simple byte-level transforms (`shift`, `rotate`, `mask`)

Result:

- baseline solved reference: `306`
- final verified binary rows: `381`
- net gain over baseline: `+75`

### 4.2 Text

The biggest curation improvement came from text:

- previously unresolved text rows were not conflicting ciphers
- they were missing 1 to 6 query characters not shown in the in-row examples
- all `971` such rows were cleanly promotable to `answer_only_keep`

Result:

- `605 verified`
- `971 clean answer-only`
- `0 manual`

### 4.3 Symbol

The symbol family split into two distinct subtypes:

- `numeric_2x2`
- `glyph_len5`

For `numeric_2x2`, operator-aware row-local formula search recovered:

- `74 verified`
- `65 answer-only`

For `glyph_len5`:

- `70` rows satisfy a coarse multiset-style mapping hypothesis
- `46` of those also satisfy a global output-order DAG
- these `46` rows are the strongest remaining glyph manual-audit targets

### 4.4 Manual pass1 pack

The highest-priority human review pack is now only `644` rows:

- `448` `symbol_numeric_same_op`
- `150` `binary_low_gap`
- `46` `symbol_glyph_multiset`

That is the shortest path for the next curation pass.

## 5. Final deliverables in this folder

### 5.1 Most important CSV artifacts

| path | purpose |
| --- | --- |
| `artifacts/train_row_analysis_v1.csv` | Full per-row analysis ledger for all 9,500 rows |
| `artifacts/train_recommended_learning_target_v1.csv` | Recommended safe training pool (`verified + answer_only`) |
| `artifacts/train_verified_trace_ready_v1.csv` | Highest-confidence trace-ready teacher rows |
| `artifacts/train_answer_only_keep_v1.csv` | Clean answer-only supervision rows |
| `artifacts/train_manual_audit_priority_v1.csv` | Remaining unresolved rows to inspect |
| `artifacts/train_exclude_suspect_v1.csv` | Rows intentionally excluded due to label/rule mismatch risk |
| `artifacts/manual_pass1_priority_pack_v1.csv` | First manual-review queue |
| `artifacts/teacher_coverage_recovery_v1.csv` | Comparison against prior solved coverage |
| `artifacts/family_summary_v1.csv` | Final family-level result table |
| `artifacts/selection_summary_v1.csv` | Final selection-tier summary |

### 5.2 Important specialist artifacts

| path | purpose |
| --- | --- |
| `artifacts/text_answer_completion_summary_v1.csv` | Breakdown of the 971 text answer-only promotions |
| `artifacts/binary_cluster_summary_v1.csv` | Cluster view of unresolved binary rows |
| `artifacts/symbol_operator_summary_v1.csv` | Operator-level split for numeric symbol rows |
| `artifacts/glyph_multiset_summary_v1.csv` | Coarse glyph feasibility breakdown |
| `artifacts/glyph_query_consistent_v1.csv` | 5 glyph rows whose query+gold still fit the coarse model |
| `artifacts/symbol_tail_probe_summary_v1.csv` | Final tail probes for remaining symbol rows |

## 6. Execution file overview

### `code/train_data_analysis_v1.py`

This is the **single-file implementation** of the whole analysis pipeline.

Major responsibilities:

- import and reuse parser/metadata logic from `versions/v1/code/train.py`
- analyze each row family-by-family
- assign `verified_trace_ready` / `answer_only_keep` / `manual_audit_priority` / `exclude_suspect`
- generate CSV artifacts under `artifacts/`
- generate Markdown reports under `reports/`

Main functions:

- `analyze_bit_row(...)`
- `analyze_text_row(...)`
- `analyze_symbol_row(...)`
- `analyze_row(...)`
- `build_reports(...)`
- `run_analysis(...)`
- `main()`

### Example rerun command

```bash
cd /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.venv/lib/python3.12/site-packages \
python3 cuda-train-data-analysis-v1/code/train_data_analysis_v1.py \
  --repo-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge \
  --out-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/cuda-train-data-analysis-v1
```

## 7. Report-by-report guide

| report | summary |
| --- | --- |
| `reports/00_kickoff.md` | Initial scope, constraints, and setup note |
| `reports/01_overview.md` | Early end-to-end overview and high-priority manual rows |
| `reports/02_hard_family_findings.md` | Binary/text/symbol solver findings |
| `reports/03_curation_recommendations.md` | How to use each selection tier for future training |
| `reports/04_mid_results.md` | Earlier milestone snapshot before later improvements |
| `reports/05_symbol_split_notes.md` | First explicit split of symbol into `numeric_2x2` and `glyph_len5` |
| `reports/06_text_unknown_notes.md` | Final text answer-completion summary |
| `reports/07_binary_cluster_notes.md` | Remaining binary clusters and top manual queue |
| `reports/08_symbol_operator_notes.md` | Numeric operator split plus glyph multiset summary |
| `reports/09_manual_pass1_pack.md` | First practical human-audit pack |
| `reports/10_glyph_probe_notes.md` | Earlier glyph probe note showing failed simple transducer direction |
| `reports/10_glyph_order_probe.md` | Glyph rows consistent with multiset plus order DAG |
| `reports/11_latest_snapshot.md` | Best single snapshot of the final state |
| `reports/12_symbol_tail_probes.md` | Final symbol-tail probes and why remaining rows stay manual |

## 8. Recommended reading order

If you only want the essentials, read in this order:

1. `reports/11_latest_snapshot.md`
2. `artifacts/train_recommended_learning_target_v1.csv`
3. `artifacts/manual_pass1_priority_pack_v1.csv`
4. `reports/12_symbol_tail_probes.md`
5. `code/train_data_analysis_v1.py`

## 9. Validation notes

Validation performed after copying the analysis folder into the repository:

- `python3 -m py_compile cuda-train-data-analysis-v1/code/train_data_analysis_v1.py`
- smoke rerun of the analysis script
- `python3 -m pytest -q -k 'not test_scaffold_runbook_and_ablation_failure_logging'`

Observed result:

- `125 passed, 1 deselected`

The full repository test suite still has one unrelated pre-existing failure:

- `versions/v3/tests/test_candidate_promotion.py::test_scaffold_runbook_and_ablation_failure_logging`

## 10. Final conclusion

This folder should be treated as the final packaged result of the analysis pass.

The most important takeaway is:

- the project now has a **strong safe training core**
- the remaining uncertainty is concentrated, not diffuse
- future effort should focus primarily on `binary` and `symbol`

For accuracy-oriented Nemotron fine-tuning, `artifacts/train_recommended_learning_target_v1.csv` is the key output. For the next manual curation pass, `artifacts/manual_pass1_priority_pack_v1.csv` is the key output.
