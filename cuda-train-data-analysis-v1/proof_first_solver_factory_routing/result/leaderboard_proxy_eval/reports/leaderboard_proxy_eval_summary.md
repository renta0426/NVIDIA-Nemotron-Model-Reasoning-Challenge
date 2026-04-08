# leaderboard_proxy_eval_overall

## Overall

- rows: `200`
- correct: `98`
- accuracy: `0.4900`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 22 | 0.2391 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 15 | 0.4688 |
| `text` | 20 | 5 | 0.2500 |
| `unit` | 18 | 18 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 2 | 0.0571 |
| `bit_permutation_inversion` | 26 | 19 | 0.7308 |
| `bit_structured_byte_formula` | 31 | 1 | 0.0323 |
| `glyph_len5` | 5 | 0 | 0.0000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 15 | 0.5556 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 5 | 0.2500 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 92 | 22 | 0.2391 |
| `numeric` | 62 | 52 | 0.8387 |
| `roman` | 19 | 19 | 1.0000 |
| `symbolic` | 7 | 0 | 0.0000 |
| `text_phrase` | 20 | 5 | 0.2500 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 20 | 5 | 0.2500 |
| `400-499` | 26 | 8 | 0.3077 |
| `500-599` | 66 | 14 | 0.2121 |
| `<300` | 88 | 71 | 0.8068 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 66 | 14 | 0.2121 |
| `3` | 71 | 61 | 0.8592 |
| `4` | 16 | 6 | 0.3750 |
| `5` | 21 | 9 | 0.4286 |
| `7` | 8 | 1 | 0.1250 |
| `8` | 5 | 0 | 0.0000 |
| `9` | 13 | 7 | 0.5385 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 6 | 0.2308 |
| `manual_audit_priority` | 18 | 1 | 0.0556 |
| `verified_trace_ready` | 156 | 91 | 0.5833 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.82`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.7609`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 26 | 2 | 0.0769 |
| `binary_affine_xor` | 10 | 0 | 0.0000 |
| `binary_bit_permutation_bijection` | 24 | 19 | 0.7917 |
| `binary_bit_permutation_independent` | 2 | 0 | 0.0000 |
| `binary_byte_transform` | 1 | 0 | 0.0000 |
| `binary_structured_byte_formula` | 10 | 0 | 0.0000 |
| `binary_structured_byte_formula_abstract` | 7 | 0 | 0.0000 |
| `binary_structured_byte_not_formula` | 2 | 0 | 0.0000 |
| `binary_three_bit_boolean` | 1 | 0 | 0.0000 |
| `binary_two_bit_boolean` | 9 | 1 | 0.1111 |
