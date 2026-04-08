# Leaderboard Proxy V1 Report

## 1. Purpose

This proxy dataset is an engineered local benchmark built from existing Phase0 and specialized row-level outputs. It is not claimed to be the real leaderboard hidden half. Its purpose is narrower: reproduce the observed rank-order gap between v3f and the current proof-first route-aware run using a repository-tracked local score.

## 2. README-Aligned Constraints

- metric: Accuracy
- boxed-first extraction: True
- temperature: 0.0
- final artifact target: single submit-compatible LoRA in submission.zip

## 3. Proxy Construction Rule

The dataset is built from three disjoint row roles:

- v3f_only: rows where v3f is correct and current is wrong
- both_correct: rows where both models are correct
- both_wrong: rows where both models are wrong

Current-only rows are intentionally excluded so the proxy preserves the observed leaderboard ordering.

## 4. Selected Counts

| role | rows |
| --- | ---: |
| `v3f_only` | 31 |
| `both_correct` | 112 |
| `both_wrong` | 57 |

| source_split | rows |
| --- | ---: |
| `phase0` | 110 |
| `specialized` | 90 |

| family_short | rows |
| --- | ---: |
| `binary` | 92 |
| `gravity` | 19 |
| `roman` | 19 |
| `symbol` | 32 |
| `text` | 20 |
| `unit` | 18 |

| leaderboard_proxy_bucket | rows |
| --- | ---: |
| `symbol:numeric_2x2` | 27 |
| `supported_bijection` | 24 |
| `text:text_monoalphabetic` | 20 |
| `gravity:gravity_half_g_t2` | 19 |
| `roman:roman_standard` | 19 |
| `unit:unit_fixed_ratio` | 18 |
| `dominant_structured_safe` | 12 |
| `boolean_family` | 10 |
| `supported_affine_xor` | 10 |
| `dominant_structured_abstract` | 9 |
| `no_solver_answer_only` | 9 |
| `no_solver_manual` | 7 |
| `supported_not_structured` | 6 |
| `symbol:glyph_len5` | 5 |
| `binary:bit_other` | 2 |
| `rare_perm_independent` | 2 |
| `rare_byte_transform` | 1 |

## 5. Measured Proxy Scores

| run | correct / rows | accuracy |
| --- | ---: | ---: |
| `v3f` | `143 / 200` | `0.7150` |
| `current` | `112 / 200` | `0.5600` |

## 6. Interpretation

If a future candidate beats the current route-aware run on this proxy while preserving Phase0 corrected accuracy, it is a stronger submit candidate than one that only improves local320 or specialized563.

