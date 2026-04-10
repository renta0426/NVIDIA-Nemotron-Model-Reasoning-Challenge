# readme_local320

## Overall

- rows: `320`
- correct: `100`
- accuracy: `0.3125`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 14 | 0.2333 |
| `general_stable_set` | 200 | 74 | 0.3700 |
| `symbol_watch_set` | 60 | 12 | 0.2000 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 14 | 0.2333 |
| `gravity` | 50 | 2 | 0.0400 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 12 | 0.2000 |
| `text` | 50 | 1 | 0.0200 |
| `unit` | 50 | 22 | 0.4400 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 12 | 0.2609 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 2 | 0.0400 |
| `numeric_2x2` | 40 | 12 | 0.3000 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 1 | 0.0200 |
| `unit_fixed_ratio` | 50 | 22 | 0.4400 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 7 | 0.2000 |
| `manual_audit_priority` | 50 | 2 | 0.0400 |
| `verified_trace_ready` | 235 | 91 | 0.3872 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
| `gravity_numeric_rule` | 50 | 2 | 0.0400 |
| `nan` | 75 | 6 | 0.0800 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `symbol_numeric_operator_formula` | 25 | 12 | 0.4800 |
| `text_char_substitution` | 50 | 1 | 0.0200 |
| `unit_numeric_rule` | 50 | 22 | 0.4400 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.4`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.6`
- format_ok_content_wrong_rate: `0.5833`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
| `nan` | 40 | 6 | 0.1500 |
