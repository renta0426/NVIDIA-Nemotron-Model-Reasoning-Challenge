# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `122`
- accuracy: `0.6100`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `leaderboard_proxy_v1_set` | 200 | 122 | 0.6100 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 39 | 0.4239 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 16 | 0.5000 |
| `text` | 20 | 11 | 0.5500 |
| `unit` | 18 | 18 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 11 | 0.3143 |
| `bit_permutation_inversion` | 26 | 17 | 0.6538 |
| `bit_structured_byte_formula` | 31 | 11 | 0.3548 |
| `glyph_len5` | 5 | 0 | 0.0000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 16 | 0.5926 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 11 | 0.5500 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 10 | 0.3846 |
| `manual_audit_priority` | 18 | 3 | 0.1667 |
| `verified_trace_ready` | 156 | 109 | 0.6987 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 4 | 0.4000 |
| `binary_bit_permutation_bijection` | 24 | 16 | 0.6667 |
| `binary_bit_permutation_independent` | 2 | 1 | 0.5000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 4 | 0.4000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 2 | 0.2222 |
| `gravity_numeric_rule` | 19 | 19 | 1.0000 |
| `nan` | 37 | 8 | 0.2162 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `symbol_numeric_operator_formula` | 21 | 16 | 0.7619 |
| `text_char_substitution` | 20 | 11 | 0.5500 |
| `unit_numeric_rule` | 18 | 18 | 1.0000 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9891`
- leading_zero_retention_rate: `0.3`
- format_failure_rate: `0.0109`
- format_ok_content_wrong_rate: `0.5714`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 4 | 0.4000 |
| `binary_bit_permutation_bijection` | 24 | 16 | 0.6667 |
| `binary_bit_permutation_independent` | 2 | 1 | 0.5000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 4 | 0.4000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 2 | 0.2222 |
| `nan` | 26 | 8 | 0.3077 |
