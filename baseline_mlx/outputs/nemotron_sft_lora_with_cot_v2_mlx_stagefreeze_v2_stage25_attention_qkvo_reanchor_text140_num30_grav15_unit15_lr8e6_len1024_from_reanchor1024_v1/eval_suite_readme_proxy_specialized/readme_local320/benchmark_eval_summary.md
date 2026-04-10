# readme_local320

## Overall

- rows: `320`
- correct: `214`
- accuracy: `0.6687`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 20 | 0.3333 |
| `general_stable_set` | 200 | 174 | 0.8700 |
| `symbol_watch_set` | 60 | 20 | 0.3333 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 20 | 0.3333 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 20 | 0.3333 |
| `text` | 50 | 25 | 0.5000 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 15 | 0.3261 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 20 | 0.5000 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 25 | 0.5000 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 12 | 0.3429 |
| `manual_audit_priority` | 50 | 8 | 0.1600 |
| `verified_trace_ready` | 235 | 194 | 0.8255 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `gravity_numeric_rule` | 50 | 50 | 1.0000 |
| `nan` | 75 | 14 | 0.1867 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `symbol_numeric_operator_formula` | 25 | 19 | 0.7600 |
| `text_char_substitution` | 50 | 25 | 0.5000 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.95`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.05`
- format_ok_content_wrong_rate: `0.6491`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `nan` | 40 | 13 | 0.3250 |
