# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `124`
- accuracy: `0.6200`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `leaderboard_proxy_v1_set` | 200 | 124 | 0.6200 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 39 | 0.4239 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 20 | 0.6250 |
| `text` | 20 | 9 | 0.4500 |
| `unit` | 18 | 18 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 12 | 0.3429 |
| `bit_permutation_inversion` | 26 | 20 | 0.7692 |
| `bit_structured_byte_formula` | 31 | 7 | 0.2258 |
| `glyph_len5` | 5 | 0 | 0.0000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 20 | 0.7407 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 9 | 0.4500 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 11 | 0.4231 |
| `manual_audit_priority` | 18 | 2 | 0.1111 |
| `verified_trace_ready` | 156 | 111 | 0.7115 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 5 | 0.5000 |
| `binary_bit_permutation_bijection` | 24 | 18 | 0.7500 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 3 | 0.3000 |
| `binary_structured_byte_formula_abstract` | 7 | 1 | 0.1429 |
| `binary_structured_byte_not_formula` | 2 | 0 | 0.0000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 3 | 0.3333 |
| `gravity_numeric_rule` | 19 | 19 | 1.0000 |
| `nan` | 37 | 7 | 0.1892 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `symbol_numeric_operator_formula` | 21 | 19 | 0.9048 |
| `text_char_substitution` | 20 | 9 | 0.4500 |
| `unit_numeric_rule` | 18 | 18 | 1.0000 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9674`
- leading_zero_retention_rate: `0.48`
- format_failure_rate: `0.0326`
- format_ok_content_wrong_rate: `0.5618`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 5 | 0.5000 |
| `binary_bit_permutation_bijection` | 24 | 18 | 0.7500 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 3 | 0.3000 |
| `binary_structured_byte_formula_abstract` | 7 | 1 | 0.1429 |
| `binary_structured_byte_not_formula` | 2 | 0 | 0.0000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 3 | 0.3333 |
| `nan` | 26 | 6 | 0.2308 |
