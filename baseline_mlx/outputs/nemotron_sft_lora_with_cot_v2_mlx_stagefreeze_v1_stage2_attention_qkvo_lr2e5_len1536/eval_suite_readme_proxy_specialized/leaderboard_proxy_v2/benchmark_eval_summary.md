# leaderboard_proxy_v2

## Overall

- rows: `84`
- correct: `30`
- accuracy: `0.3571`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `leaderboard_proxy_v2_set` | 84 | 30 | 0.3571 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 73 | 27 | 0.3699 |
| `symbol` | 11 | 3 | 0.2727 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 28 | 11 | 0.3929 |
| `bit_permutation_inversion` | 24 | 8 | 0.3333 |
| `bit_structured_byte_formula` | 21 | 8 | 0.3810 |
| `numeric_2x2` | 11 | 3 | 0.2727 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 2 | 1 | 0.5000 |
| `verified_trace_ready` | 82 | 29 | 0.3537 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 28 | 11 | 0.3929 |
| `binary_bit_permutation_bijection` | 24 | 8 | 0.3333 |
| `binary_structured_byte_formula` | 10 | 4 | 0.4000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `nan` | 2 | 1 | 0.5000 |
| `symbol_numeric_operator_formula` | 11 | 3 | 0.2727 |

## Binary metrics

- rows: `73`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.5205`
- leading_zero_retention_rate: `0.0333`
- format_failure_rate: `0.4795`
- format_ok_content_wrong_rate: `0.5263`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 28 | 11 | 0.3929 |
| `binary_bit_permutation_bijection` | 24 | 8 | 0.3333 |
| `binary_structured_byte_formula` | 10 | 4 | 0.4000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `nan` | 2 | 1 | 0.5000 |
