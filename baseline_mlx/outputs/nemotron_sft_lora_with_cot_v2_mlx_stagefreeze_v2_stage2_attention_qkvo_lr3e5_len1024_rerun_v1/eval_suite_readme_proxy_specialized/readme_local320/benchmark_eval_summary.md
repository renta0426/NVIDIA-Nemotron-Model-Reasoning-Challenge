# readme_local320

## Overall

- rows: `320`
- correct: `74`
- accuracy: `0.2313`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 12 | 0.2000 |
| `general_stable_set` | 200 | 54 | 0.2700 |
| `symbol_watch_set` | 60 | 8 | 0.1333 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 12 | 0.2000 |
| `gravity` | 50 | 13 | 0.2600 |
| `roman` | 50 | 32 | 0.6400 |
| `symbol` | 60 | 8 | 0.1333 |
| `text` | 50 | 0 | 0.0000 |
| `unit` | 50 | 9 | 0.1800 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 10 | 0.2174 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 13 | 0.2600 |
| `numeric_2x2` | 40 | 8 | 0.2000 |
| `roman_standard` | 50 | 32 | 0.6400 |
| `text_monoalphabetic` | 50 | 0 | 0.0000 |
| `unit_fixed_ratio` | 50 | 9 | 0.1800 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 5 | 0.1429 |
| `manual_audit_priority` | 50 | 2 | 0.0400 |
| `verified_trace_ready` | 235 | 67 | 0.2851 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `gravity_numeric_rule` | 50 | 13 | 0.2600 |
| `nan` | 75 | 5 | 0.0667 |
| `roman_standard` | 50 | 32 | 0.6400 |
| `symbol_numeric_operator_formula` | 25 | 8 | 0.3200 |
| `text_char_substitution` | 50 | 0 | 0.0000 |
| `unit_numeric_rule` | 50 | 9 | 0.1800 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.2833`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.7167`
- format_ok_content_wrong_rate: `0.7059`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `nan` | 40 | 5 | 0.1250 |
