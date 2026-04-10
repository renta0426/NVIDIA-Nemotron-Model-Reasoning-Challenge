# readme_local320

## Overall

- rows: `320`
- correct: `209`
- accuracy: `0.6531`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 19 | 0.3167 |
| `general_stable_set` | 200 | 170 | 0.8500 |
| `symbol_watch_set` | 60 | 20 | 0.3333 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 19 | 0.3167 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 20 | 0.3333 |
| `text` | 50 | 22 | 0.4400 |
| `unit` | 50 | 49 | 0.9800 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 14 | 0.3043 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 20 | 0.5000 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 22 | 0.4400 |
| `unit_fixed_ratio` | 50 | 49 | 0.9800 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 13 | 0.3714 |
| `manual_audit_priority` | 50 | 5 | 0.1000 |
| `verified_trace_ready` | 235 | 191 | 0.8128 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
| `gravity_numeric_rule` | 50 | 50 | 1.0000 |
| `nan` | 75 | 11 | 0.1467 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `symbol_numeric_operator_formula` | 25 | 20 | 0.8000 |
| `text_char_substitution` | 50 | 22 | 0.4400 |
| `unit_numeric_rule` | 50 | 49 | 0.9800 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.7`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.3`
- format_ok_content_wrong_rate: `0.619`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
| `nan` | 40 | 11 | 0.2750 |
