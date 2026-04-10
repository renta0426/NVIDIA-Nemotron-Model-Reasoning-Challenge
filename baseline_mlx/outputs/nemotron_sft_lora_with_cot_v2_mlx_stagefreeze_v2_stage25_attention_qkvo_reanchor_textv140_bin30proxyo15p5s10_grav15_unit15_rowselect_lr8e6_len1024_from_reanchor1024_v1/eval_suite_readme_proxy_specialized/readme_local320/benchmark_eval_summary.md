# readme_local320

## Overall

- rows: `320`
- correct: `227`
- accuracy: `0.7094`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_hard_set` | 60 | 27 | 0.4500 |
| `general_stable_set` | 200 | 178 | 0.8900 |
| `symbol_watch_set` | 60 | 22 | 0.3667 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 27 | 0.4500 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 22 | 0.3667 |
| `text` | 50 | 28 | 0.5600 |
| `unit` | 50 | 50 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 21 | 0.4565 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 22 | 0.5500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 28 | 0.5600 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 15 | 0.4286 |
| `manual_audit_priority` | 50 | 9 | 0.1800 |
| `verified_trace_ready` | 235 | 203 | 0.8638 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
| `gravity_numeric_rule` | 50 | 50 | 1.0000 |
| `nan` | 75 | 17 | 0.2267 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `symbol_numeric_operator_formula` | 25 | 22 | 0.8800 |
| `text_char_substitution` | 50 | 28 | 0.5600 |
| `unit_numeric_rule` | 50 | 50 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9833`
- leading_zero_retention_rate: `1.0`
- format_failure_rate: `0.0167`
- format_ok_content_wrong_rate: `0.5424`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
| `nan` | 40 | 17 | 0.4250 |
