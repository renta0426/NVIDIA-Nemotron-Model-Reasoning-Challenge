# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `133`
- accuracy: `0.6650`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 42 | 0.4565 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 19 | 0.5938 |
| `text` | 20 | 17 | 0.8500 |
| `unit` | 18 | 17 | 0.9444 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 8 | 0.2286 |
| `bit_permutation_inversion` | 26 | 24 | 0.9231 |
| `bit_structured_byte_formula` | 31 | 10 | 0.3226 |
| `glyph_len5` | 5 | 0 | 0.0000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 19 | 0.7037 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 17 | 0.8500 |
| `unit_fixed_ratio` | 18 | 17 | 0.9444 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 92 | 42 | 0.4565 |
| `numeric` | 62 | 54 | 0.8710 |
| `roman` | 19 | 19 | 1.0000 |
| `symbolic` | 7 | 1 | 0.1429 |
| `text_phrase` | 20 | 17 | 0.8500 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 20 | 17 | 0.8500 |
| `400-499` | 26 | 19 | 0.7308 |
| `500-599` | 66 | 23 | 0.3485 |
| `<300` | 88 | 74 | 0.8409 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 66 | 23 | 0.3485 |
| `3` | 71 | 66 | 0.9296 |
| `4` | 16 | 13 | 0.8125 |
| `5` | 21 | 12 | 0.5714 |
| `7` | 8 | 4 | 0.5000 |
| `8` | 5 | 3 | 0.6000 |
| `9` | 13 | 12 | 0.9231 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 9 | 0.3462 |
| `manual_audit_priority` | 18 | 1 | 0.0556 |
| `verified_trace_ready` | 156 | 123 | 0.7885 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.82`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.5435`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 26 | 5 | 0.1923 |
| `binary_affine_xor` | 10 | 3 | 0.3000 |
| `binary_bit_permutation_bijection` | 24 | 24 | 1.0000 |
| `binary_bit_permutation_independent` | 2 | 0 | 0.0000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 5 | 0.5000 |
| `binary_structured_byte_formula_abstract` | 7 | 2 | 0.2857 |
| `binary_structured_byte_not_formula` | 2 | 0 | 0.0000 |
| `binary_three_bit_boolean` | 1 | 0 | 0.0000 |
| `binary_two_bit_boolean` | 9 | 3 | 0.3333 |
