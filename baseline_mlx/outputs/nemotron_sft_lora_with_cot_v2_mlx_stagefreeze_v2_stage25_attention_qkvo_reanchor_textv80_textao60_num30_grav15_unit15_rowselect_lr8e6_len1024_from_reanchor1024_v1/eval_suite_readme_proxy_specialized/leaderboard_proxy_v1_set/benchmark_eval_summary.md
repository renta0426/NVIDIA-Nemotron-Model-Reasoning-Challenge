# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `119`
- accuracy: `0.5950`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `leaderboard_proxy_v1_set` | 200 | 119 | 0.5950 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 34 | 0.3696 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 17 | 0.5312 |
| `text` | 20 | 12 | 0.6000 |
| `unit` | 18 | 18 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 10 | 0.2857 |
| `bit_permutation_inversion` | 26 | 14 | 0.5385 |
| `bit_structured_byte_formula` | 31 | 10 | 0.3226 |
| `glyph_len5` | 5 | 0 | 0.0000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 17 | 0.6296 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 12 | 0.6000 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 11 | 0.4231 |
| `manual_audit_priority` | 18 | 4 | 0.2222 |
| `verified_trace_ready` | 156 | 104 | 0.6667 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 3 | 0.3000 |
| `binary_bit_permutation_bijection` | 24 | 12 | 0.5000 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 1 | 1.0000 |
| `binary_structured_byte_formula` | 10 | 2 | 0.2000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `binary_three_bit_boolean` | 1 | 0 | 0.0000 |
| `binary_two_bit_boolean` | 9 | 1 | 0.1111 |
| `gravity_numeric_rule` | 19 | 19 | 1.0000 |
| `nan` | 37 | 11 | 0.2973 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `symbol_numeric_operator_formula` | 21 | 16 | 0.7619 |
| `text_char_substitution` | 20 | 12 | 0.6000 |
| `unit_numeric_rule` | 18 | 18 | 1.0000 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.8152`
- leading_zero_retention_rate: `0.3`
- format_failure_rate: `0.1848`
- format_ok_content_wrong_rate: `0.5867`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 3 | 0.3000 |
| `binary_bit_permutation_bijection` | 24 | 12 | 0.5000 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 1 | 1.0000 |
| `binary_structured_byte_formula` | 10 | 2 | 0.2000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `binary_three_bit_boolean` | 1 | 0 | 0.0000 |
| `binary_two_bit_boolean` | 9 | 1 | 0.1111 |
| `nan` | 26 | 10 | 0.3846 |
