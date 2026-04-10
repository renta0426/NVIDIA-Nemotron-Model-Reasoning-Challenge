# readme_local320

## Overall

- rows: `320`
- correct: `72`
- accuracy: `0.2250`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 10 | 0.1667 |
| `general_stable_set` | 200 | 52 | 0.2600 |
| `symbol_watch_set` | 60 | 10 | 0.1667 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 10 | 0.1667 |
| `gravity` | 50 | 6 | 0.1200 |
| `roman` | 50 | 38 | 0.7600 |
| `symbol` | 60 | 10 | 0.1667 |
| `text` | 50 | 0 | 0.0000 |
| `unit` | 50 | 8 | 0.1600 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 7 | 0.1522 |
| `bit_structured_byte_formula` | 14 | 3 | 0.2143 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 6 | 0.1200 |
| `numeric_2x2` | 40 | 10 | 0.2500 |
| `roman_standard` | 50 | 38 | 0.7600 |
| `text_monoalphabetic` | 50 | 0 | 0.0000 |
| `unit_fixed_ratio` | 50 | 8 | 0.1600 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 4 | 0.1143 |
| `manual_audit_priority` | 50 | 5 | 0.1000 |
| `verified_trace_ready` | 235 | 63 | 0.2681 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 2 | 0.1000 |
| `gravity_numeric_rule` | 50 | 6 | 0.1200 |
| `nan` | 75 | 8 | 0.1067 |
| `roman_standard` | 50 | 38 | 0.7600 |
| `symbol_numeric_operator_formula` | 25 | 10 | 0.4000 |
| `text_char_substitution` | 50 | 0 | 0.0000 |
| `unit_numeric_rule` | 50 | 8 | 0.1600 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.4667`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.5333`
- format_ok_content_wrong_rate: `0.6786`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 2 | 0.1000 |
| `nan` | 40 | 8 | 0.2000 |
