# binary_bias_specialized_set

## Overall

- rows: `563`
- correct: `158`
- accuracy: `0.2806`

## By benchmark

| benchmark_name | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_bias_specialized_set` | 563 | 158 | 0.2806 |

## By family

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 563 | 158 | 0.2806 |

## By template subtype

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 218 | 63 | 0.2890 |
| `bit_permutation_inversion` | 62 | 22 | 0.3548 |
| `bit_structured_byte_formula` | 283 | 73 | 0.2580 |

## By selection tier

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 150 | 39 | 0.2600 |
| `manual_audit_priority` | 40 | 12 | 0.3000 |
| `verified_trace_ready` | 373 | 107 | 0.2869 |

## By teacher solver candidate

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 60 | 18 | 0.3000 |
| `binary_bit_permutation_bijection` | 50 | 19 | 0.3800 |
| `binary_bit_permutation_independent` | 7 | 1 | 0.1429 |
| `binary_byte_transform` | 11 | 3 | 0.2727 |
| `binary_structured_byte_formula` | 87 | 25 | 0.2874 |
| `binary_structured_byte_formula_abstract` | 73 | 18 | 0.2466 |
| `binary_structured_byte_not_formula` | 25 | 6 | 0.2400 |
| `binary_three_bit_boolean` | 14 | 8 | 0.5714 |
| `binary_two_bit_boolean` | 46 | 9 | 0.1957 |
| `nan` | 190 | 51 | 0.2684 |

## Binary metrics

- rows: `563`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `0.5968`
- leading_zero_retention_rate: `0.0702`
- format_failure_rate: `0.4032`
- format_ok_content_wrong_rate: `0.6518`

## Binary solver family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 60 | 18 | 0.3000 |
| `binary_bit_permutation_bijection` | 50 | 19 | 0.3800 |
| `binary_bit_permutation_independent` | 7 | 1 | 0.1429 |
| `binary_byte_transform` | 11 | 3 | 0.2727 |
| `binary_structured_byte_formula` | 87 | 25 | 0.2874 |
| `binary_structured_byte_formula_abstract` | 73 | 18 | 0.2466 |
| `binary_structured_byte_not_formula` | 25 | 6 | 0.2400 |
| `binary_three_bit_boolean` | 14 | 8 | 0.5714 |
| `binary_two_bit_boolean` | 46 | 9 | 0.1957 |
| `nan` | 190 | 51 | 0.2684 |
