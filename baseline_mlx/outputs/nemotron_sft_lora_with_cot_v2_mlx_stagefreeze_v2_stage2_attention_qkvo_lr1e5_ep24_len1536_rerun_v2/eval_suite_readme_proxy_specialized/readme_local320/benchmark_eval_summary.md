# readme_local320

## Overall

- rows: `320`
- correct: `212`
- accuracy: `0.6625`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 18 | 0.3000 |
| `general_stable_set` | 200 | 175 | 0.8750 |
| `symbol_watch_set` | 60 | 19 | 0.3167 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 18 | 0.3000 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 19 | 0.3167 |
| `text` | 50 | 27 | 0.5400 |
| `unit` | 50 | 48 | 0.9600 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 15 | 0.3261 |
| `bit_structured_byte_formula` | 14 | 3 | 0.2143 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 19 | 0.4750 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 27 | 0.5400 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 11 | 0.3143 |
| `manual_audit_priority` | 50 | 7 | 0.1400 |
| `verified_trace_ready` | 235 | 194 | 0.8255 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `gravity_numeric_rule` | 50 | 50 | 1.0000 |
| `nan` | 75 | 11 | 0.1467 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 19 | 0.7600 |
| `text_char_substitution` | 50 | 27 | 0.5400 |
| `unit_numeric_rule` | 50 | 48 | 0.9600 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.8`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.2`
- format_ok_content_wrong_rate: `0.6458`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
| `nan` | 40 | 11 | 0.2750 |
