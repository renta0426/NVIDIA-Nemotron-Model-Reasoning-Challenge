# readme_local320

## Overall

- rows: `320`
- correct: `217`
- accuracy: `0.6781`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 27 | 0.4500 |
| `general_stable_set` | 200 | 168 | 0.8400 |
| `symbol_watch_set` | 60 | 22 | 0.3667 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 27 | 0.4500 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 22 | 0.3667 |
| `text` | 50 | 19 | 0.3800 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 21 | 0.4565 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 22 | 0.5500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 19 | 0.3800 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 16 | 0.4571 |
| `manual_audit_priority` | 50 | 8 | 0.1600 |
| `verified_trace_ready` | 235 | 193 | 0.8213 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 11 | 0.5500 |
| `gravity_numeric_rule` | 50 | 49 | 0.9800 |
| `nan` | 75 | 17 | 0.2267 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 21 | 0.8400 |
| `text_char_substitution` | 50 | 19 | 0.3800 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9667`
- leading_zero_retention_rate: `1.0`
- format_failure_rate: `0.0333`
- format_ok_content_wrong_rate: `0.5345`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 11 | 0.5500 |
| `nan` | 40 | 16 | 0.4000 |
