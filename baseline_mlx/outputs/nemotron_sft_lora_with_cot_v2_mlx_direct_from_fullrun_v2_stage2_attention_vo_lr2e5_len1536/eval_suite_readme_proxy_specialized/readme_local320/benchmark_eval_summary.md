# readme_local320

## Overall

- rows: `320`
- correct: `206`
- accuracy: `0.6438`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 24 | 0.4000 |
| `general_stable_set` | 200 | 165 | 0.8250 |
| `symbol_watch_set` | 60 | 17 | 0.2833 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 24 | 0.4000 |
| `gravity` | 50 | 48 | 0.9600 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 17 | 0.2833 |
| `text` | 50 | 19 | 0.3800 |
| `unit` | 50 | 48 | 0.9600 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 20 | 0.4348 |
| `bit_structured_byte_formula` | 14 | 4 | 0.2857 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 48 | 0.9600 |
| `numeric_2x2` | 40 | 17 | 0.4250 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 19 | 0.3800 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 13 | 0.3714 |
| `manual_audit_priority` | 50 | 7 | 0.1400 |
| `verified_trace_ready` | 235 | 186 | 0.7915 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 9 | 0.4500 |
| `gravity_numeric_rule` | 50 | 48 | 0.9600 |
| `nan` | 75 | 16 | 0.2133 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 16 | 0.6400 |
| `text_char_substitution` | 50 | 19 | 0.3800 |
| `unit_numeric_rule` | 50 | 48 | 0.9600 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.7`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.3`
- format_ok_content_wrong_rate: `0.5714`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 9 | 0.4500 |
| `nan` | 40 | 15 | 0.3750 |
