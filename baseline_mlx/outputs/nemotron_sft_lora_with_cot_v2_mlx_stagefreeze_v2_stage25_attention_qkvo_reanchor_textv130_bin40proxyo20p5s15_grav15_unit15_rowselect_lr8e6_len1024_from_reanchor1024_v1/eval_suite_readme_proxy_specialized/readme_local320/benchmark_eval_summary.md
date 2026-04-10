# readme_local320

## Overall

- rows: `320`
- correct: `229`
- accuracy: `0.7156`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 30 | 0.5000 |
| `general_stable_set` | 200 | 176 | 0.8800 |
| `symbol_watch_set` | 60 | 23 | 0.3833 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 30 | 0.5000 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 23 | 0.3833 |
| `text` | 50 | 28 | 0.5600 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 24 | 0.5217 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 23 | 0.5750 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 28 | 0.5600 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 18 | 0.5143 |
| `manual_audit_priority` | 50 | 10 | 0.2000 |
| `verified_trace_ready` | 235 | 201 | 0.8553 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 12 | 0.6000 |
| `gravity_numeric_rule` | 50 | 49 | 0.9800 |
| `nan` | 75 | 20 | 0.2667 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `symbol_numeric_operator_formula` | 25 | 21 | 0.8400 |
| `text_char_substitution` | 50 | 28 | 0.5600 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `1.0`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.5`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 12 | 0.6000 |
| `nan` | 40 | 18 | 0.4500 |
