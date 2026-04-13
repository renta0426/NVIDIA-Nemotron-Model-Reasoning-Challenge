# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `132`
- accuracy: `0.6600`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `leaderboard_proxy_v1_set` | 200 | 132 | 0.6600 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 44 | 0.4783 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 21 | 0.6562 |
| `text` | 20 | 11 | 0.5500 |
| `unit` | 18 | 18 | 1.0000 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 13 | 0.3714 |
| `bit_permutation_inversion` | 26 | 20 | 0.7692 |
| `bit_structured_byte_formula` | 31 | 11 | 0.3548 |
| `glyph_len5` | 5 | 0 | 0.0000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 21 | 0.7778 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 11 | 0.5500 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 11 | 0.4231 |
| `manual_audit_priority` | 18 | 5 | 0.2778 |
| `verified_trace_ready` | 156 | 116 | 0.7436 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 4 | 0.4000 |
| `binary_bit_permutation_bijection` | 24 | 18 | 0.7500 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 4 | 0.4000 |
| `binary_structured_byte_formula_abstract` | 7 | 3 | 0.4286 |
| `binary_structured_byte_not_formula` | 2 | 0 | 0.0000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 3 | 0.3333 |
| `gravity_numeric_rule` | 19 | 19 | 1.0000 |
| `nan` | 37 | 10 | 0.2703 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `symbol_numeric_operator_formula` | 21 | 20 | 0.9524 |
| `text_char_substitution` | 20 | 11 | 0.5500 |
| `unit_numeric_rule` | 18 | 18 | 1.0000 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.9891`
- leading_zero_retention_rate: `0.4`
- format_failure_rate: `0.0109`
- format_ok_content_wrong_rate: `0.5165`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 10 | 4 | 0.4000 |
| `binary_bit_permutation_bijection` | 24 | 18 | 0.7500 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 4 | 0.4000 |
| `binary_structured_byte_formula_abstract` | 7 | 3 | 0.4286 |
| `binary_structured_byte_not_formula` | 2 | 0 | 0.0000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 3 | 0.3333 |
| `nan` | 26 | 9 | 0.3462 |
