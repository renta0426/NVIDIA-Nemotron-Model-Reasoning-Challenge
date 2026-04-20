# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `154`
- accuracy: `0.7700`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 54 | 0.5870 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 24 | 0.7500 |
| `text` | 20 | 20 | 1.0000 |
| `unit` | 18 | 18 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 17 | 0.4857 |
| `bit_permutation_inversion` | 26 | 21 | 0.8077 |
| `bit_structured_byte_formula` | 31 | 16 | 0.5161 |
| `glyph_len5` | 5 | 1 | 0.2000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 23 | 0.8519 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 20 | 1.0000 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 92 | 54 | 0.5870 |
| `numeric` | 62 | 58 | 0.9355 |
| `roman` | 19 | 19 | 1.0000 |
| `symbolic` | 7 | 3 | 0.4286 |
| `text_phrase` | 20 | 20 | 1.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 20 | 20 | 1.0000 |
| `400-499` | 26 | 17 | 0.6538 |
| `500-599` | 66 | 37 | 0.5606 |
| `<300` | 88 | 80 | 0.9091 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 66 | 37 | 0.5606 |
| `3` | 71 | 70 | 0.9859 |
| `4` | 16 | 15 | 0.9375 |
| `5` | 21 | 15 | 0.7143 |
| `7` | 8 | 6 | 0.7500 |
| `8` | 5 | 4 | 0.8000 |
| `9` | 13 | 7 | 0.5385 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 18 | 0.6923 |
| `manual_audit_priority` | 18 | 7 | 0.3889 |
| `verified_trace_ready` | 156 | 129 | 0.8269 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `0.8587`
- regex_exact_rate: `0.7826`
- leading_zero_retention_rate: `0.68`
- format_failure_rate: `0.2174`
- format_ok_content_wrong_rate: `0.25`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 26 | 14 | 0.5385 |
| `binary_affine_xor` | 10 | 7 | 0.7000 |
| `binary_bit_permutation_bijection` | 24 | 19 | 0.7917 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 1 | 1.0000 |
| `binary_structured_byte_formula` | 10 | 3 | 0.3000 |
| `binary_structured_byte_formula_abstract` | 7 | 3 | 0.4286 |
| `binary_structured_byte_not_formula` | 2 | 1 | 0.5000 |
| `binary_three_bit_boolean` | 1 | 0 | 0.0000 |
| `binary_two_bit_boolean` | 9 | 4 | 0.4444 |
