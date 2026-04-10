# readme_local320

## Overall

- rows: `320`
- correct: `204`
- accuracy: `0.6375`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 10 | 0.1667 |
| `general_stable_set` | 200 | 175 | 0.8750 |
| `symbol_watch_set` | 60 | 19 | 0.3167 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 10 | 0.1667 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 19 | 0.3167 |
| `text` | 50 | 26 | 0.5200 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 7 | 0.1522 |
| `bit_structured_byte_formula` | 14 | 3 | 0.2143 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 19 | 0.4750 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 26 | 0.5200 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 9 | 0.2571 |
| `manual_audit_priority` | 50 | 2 | 0.0400 |
| `verified_trace_ready` | 235 | 193 | 0.8213 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 4 | 0.2000 |
| `gravity_numeric_rule` | 50 | 49 | 0.9800 |
| `nan` | 75 | 6 | 0.0800 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 19 | 0.7600 |
| `text_char_substitution` | 50 | 26 | 0.5200 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.25`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.75`
- format_ok_content_wrong_rate: `0.4667`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 4 | 0.2000 |
| `nan` | 40 | 6 | 0.1500 |
