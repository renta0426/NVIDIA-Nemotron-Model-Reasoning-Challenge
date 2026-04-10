# readme_local320

## Overall

- rows: `320`
- correct: `210`
- accuracy: `0.6562`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 17 | 0.2833 |
| `general_stable_set` | 200 | 175 | 0.8750 |
| `symbol_watch_set` | 60 | 18 | 0.3000 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 17 | 0.2833 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 18 | 0.3000 |
| `text` | 50 | 25 | 0.5000 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 15 | 0.3261 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 18 | 0.4500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 25 | 0.5000 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 9 | 0.2571 |
| `manual_audit_priority` | 50 | 6 | 0.1200 |
| `verified_trace_ready` | 235 | 195 | 0.8298 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `gravity_numeric_rule` | 50 | 50 | 1.0000 |
| `nan` | 75 | 10 | 0.1333 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 18 | 0.7200 |
| `text_char_substitution` | 50 | 25 | 0.5000 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.8333`
- leading_zero_retention_rate: `0.8`
- format_failure_rate: `0.1667`
- format_ok_content_wrong_rate: `0.66`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `nan` | 40 | 10 | 0.2500 |
