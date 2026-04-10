# readme_local320

## Overall

- rows: `320`
- correct: `201`
- accuracy: `0.6281`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 15 | 0.2500 |
| `general_stable_set` | 200 | 168 | 0.8400 |
| `symbol_watch_set` | 60 | 18 | 0.3000 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 15 | 0.2500 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 18 | 0.3000 |
| `text` | 50 | 19 | 0.3800 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 11 | 0.2391 |
| `bit_structured_byte_formula` | 14 | 4 | 0.2857 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 18 | 0.4500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 19 | 0.3800 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 11 | 0.3143 |
| `manual_audit_priority` | 50 | 5 | 0.1000 |
| `verified_trace_ready` | 235 | 185 | 0.7872 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 6 | 0.3000 |
| `gravity_numeric_rule` | 50 | 49 | 0.9800 |
| `nan` | 75 | 9 | 0.1200 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 18 | 0.7200 |
| `text_char_substitution` | 50 | 19 | 0.3800 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.6667`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.3333`
- format_ok_content_wrong_rate: `0.625`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 6 | 0.3000 |
| `nan` | 40 | 9 | 0.2250 |
