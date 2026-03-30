# rule_based_adapter_readme_inference_samples_rule_base-600

## Overall

- rows: `30`
- correct: `25`
- accuracy: `0.8333`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 10 | 5 | 0.5000 |
| `gravity` | 4 | 4 | 1.0000 |
| `roman` | 4 | 4 | 1.0000 |
| `symbol` | 4 | 4 | 1.0000 |
| `text` | 4 | 4 | 1.0000 |
| `unit` | 4 | 4 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 6 | 2 | 0.3333 |
| `bit_permutation_inversion` | 3 | 2 | 0.6667 |
| `bit_structured_byte_formula` | 1 | 1 | 1.0000 |
| `gravity_half_g_t2` | 4 | 4 | 1.0000 |
| `numeric_2x2` | 4 | 4 | 1.0000 |
| `roman_standard` | 4 | 4 | 1.0000 |
| `text_monoalphabetic` | 4 | 4 | 1.0000 |
| `unit_fixed_ratio` | 4 | 4 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 10 | 5 | 0.5000 |
| `numeric` | 12 | 12 | 1.0000 |
| `roman` | 4 | 4 | 1.0000 |
| `text_phrase` | 4 | 4 | 1.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 4 | 4 | 1.0000 |
| `400-499` | 6 | 6 | 1.0000 |
| `500-599` | 8 | 3 | 0.3750 |
| `<300` | 12 | 12 | 1.0000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 8 | 3 | 0.3750 |
| `4` | 4 | 4 | 1.0000 |
| `5` | 16 | 16 | 1.0000 |
| `8` | 1 | 1 | 1.0000 |
| `9` | 1 | 1 | 1.0000 |

## Binary metrics

- rows: `10`
- boxed_extraction_success_rate: `0.5`
- regex_exact_rate: `0.5`
- leading_zero_retention_rate: `0.5`
- format_failure_rate: `0.5`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 1 | 0 | 0.0000 |
| `binary_affine_xor` | 4 | 1 | 0.2500 |
| `binary_bit_permutation_bijection` | 3 | 2 | 0.6667 |
| `binary_byte_transform` | 1 | 1 | 1.0000 |
| `binary_structured_byte_formula` | 1 | 1 | 1.0000 |
