# leaderboard_proxy_v2

## Overall

- rows: `84`
- correct: `33`
- accuracy: `0.3929`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `leaderboard_proxy_v2_set` | 84 | 33 | 0.3929 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 73 | 24 | 0.3288 |
| `symbol` | 11 | 9 | 0.8182 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 28 | 10 | 0.3571 |
| `bit_permutation_inversion` | 24 | 8 | 0.3333 |
| `bit_structured_byte_formula` | 21 | 6 | 0.2857 |
| `numeric_2x2` | 11 | 9 | 0.8182 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 2 | 0 | 0.0000 |
| `verified_trace_ready` | 82 | 33 | 0.4024 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 28 | 10 | 0.3571 |
| `binary_bit_permutation_bijection` | 24 | 8 | 0.3333 |
| `binary_structured_byte_formula` | 10 | 3 | 0.3000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `nan` | 2 | 0 | 0.0000 |
| `symbol_numeric_operator_formula` | 11 | 9 | 0.8182 |

## Binary metrics

- rows: `73`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.6712`
- leading_zero_retention_rate: `0.1`
- format_failure_rate: `0.3288`
- format_ok_content_wrong_rate: `0.5714`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 28 | 10 | 0.3571 |
| `binary_bit_permutation_bijection` | 24 | 8 | 0.3333 |
| `binary_structured_byte_formula` | 10 | 3 | 0.3000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `nan` | 2 | 0 | 0.0000 |
