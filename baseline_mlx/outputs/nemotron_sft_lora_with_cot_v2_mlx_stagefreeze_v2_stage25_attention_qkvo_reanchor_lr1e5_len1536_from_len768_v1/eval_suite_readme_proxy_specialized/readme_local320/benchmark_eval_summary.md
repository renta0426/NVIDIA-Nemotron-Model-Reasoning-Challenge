# readme_local320

## Overall

- rows: `320`
- correct: `220`
- accuracy: `0.6875`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 20 | 0.3333 |
| `general_stable_set` | 200 | 178 | 0.8900 |
| `symbol_watch_set` | 60 | 22 | 0.3667 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 20 | 0.3333 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 22 | 0.3667 |
| `text` | 50 | 29 | 0.5800 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 15 | 0.3261 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 22 | 0.5500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 29 | 0.5800 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 13 | 0.3714 |
| `manual_audit_priority` | 50 | 7 | 0.1400 |
| `verified_trace_ready` | 235 | 200 | 0.8511 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
| `gravity_numeric_rule` | 50 | 49 | 0.9800 |
| `nan` | 75 | 13 | 0.1733 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 21 | 0.8400 |
| `text_char_substitution` | 50 | 29 | 0.5800 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9333`
- leading_zero_retention_rate: `0.4`
- format_failure_rate: `0.0667`
- format_ok_content_wrong_rate: `0.6429`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
| `nan` | 40 | 12 | 0.3000 |
