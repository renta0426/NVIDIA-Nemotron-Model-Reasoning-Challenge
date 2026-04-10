# readme_local320

## Overall

- rows: `320`
- correct: `213`
- accuracy: `0.6656`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 23 | 0.3833 |
| `general_stable_set` | 200 | 170 | 0.8500 |
| `symbol_watch_set` | 60 | 20 | 0.3333 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 23 | 0.3833 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 20 | 0.3333 |
| `text` | 50 | 20 | 0.4000 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 17 | 0.3696 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 20 | 0.5000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 20 | 0.4000 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 15 | 0.4286 |
| `manual_audit_priority` | 50 | 6 | 0.1200 |
| `verified_trace_ready` | 235 | 192 | 0.8170 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
| `gravity_numeric_rule` | 50 | 50 | 1.0000 |
| `nan` | 75 | 14 | 0.1867 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 19 | 0.7600 |
| `text_char_substitution` | 50 | 20 | 0.4000 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9833`
- leading_zero_retention_rate: `0.6`
- format_failure_rate: `0.0167`
- format_ok_content_wrong_rate: `0.6102`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
| `nan` | 40 | 13 | 0.3250 |
