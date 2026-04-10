# readme_local320

## Overall

- rows: `320`
- correct: `217`
- accuracy: `0.6781`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 27 | 0.4500 |
| `general_stable_set` | 200 | 171 | 0.8550 |
| `symbol_watch_set` | 60 | 19 | 0.3167 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 27 | 0.4500 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 19 | 0.3167 |
| `text` | 50 | 22 | 0.4400 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 20 | 0.4348 |
| `bit_structured_byte_formula` | 14 | 7 | 0.5000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 19 | 0.4750 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 22 | 0.4400 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 14 | 0.4000 |
| `manual_audit_priority` | 50 | 9 | 0.1800 |
| `verified_trace_ready` | 235 | 194 | 0.8255 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
| `gravity_numeric_rule` | 50 | 50 | 1.0000 |
| `nan` | 75 | 18 | 0.2400 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `symbol_numeric_operator_formula` | 25 | 18 | 0.7200 |
| `text_char_substitution` | 50 | 22 | 0.4400 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9667`
- leading_zero_retention_rate: `0.8`
- format_failure_rate: `0.0333`
- format_ok_content_wrong_rate: `0.5345`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
| `nan` | 40 | 17 | 0.4250 |
