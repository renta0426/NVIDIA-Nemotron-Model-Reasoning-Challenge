# readme_local320

## Overall

- rows: `320`
- correct: `113`
- accuracy: `0.3531`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 19 | 0.3167 |
| `general_stable_set` | 200 | 88 | 0.4400 |
| `symbol_watch_set` | 60 | 6 | 0.1000 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 19 | 0.3167 |
| `gravity` | 50 | 2 | 0.0400 |
| `roman` | 50 | 38 | 0.7600 |
| `symbol` | 60 | 6 | 0.1000 |
| `text` | 50 | 12 | 0.2400 |
| `unit` | 50 | 36 | 0.7200 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 13 | 0.2826 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 2 | 0.0400 |
| `numeric_2x2` | 40 | 6 | 0.1500 |
| `roman_standard` | 50 | 38 | 0.7600 |
| `text_monoalphabetic` | 50 | 12 | 0.2400 |
| `unit_fixed_ratio` | 50 | 36 | 0.7200 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 9 | 0.2571 |
| `manual_audit_priority` | 50 | 5 | 0.1000 |
| `verified_trace_ready` | 235 | 99 | 0.4213 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `gravity_numeric_rule` | 50 | 2 | 0.0400 |
| `nan` | 75 | 13 | 0.1733 |
| `roman_standard` | 50 | 38 | 0.7600 |
| `symbol_numeric_operator_formula` | 25 | 5 | 0.2000 |
| `text_char_substitution` | 50 | 12 | 0.2400 |
| `unit_numeric_rule` | 50 | 36 | 0.7200 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.6`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.4`
- format_ok_content_wrong_rate: `0.5556`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `nan` | 40 | 12 | 0.3000 |
