# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `176`
- accuracy: `0.8800`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 77 | 0.8370 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 23 | 0.7188 |
| `text` | 20 | 20 | 1.0000 |
| `unit` | 18 | 18 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 28 | 0.8000 |
| `bit_permutation_inversion` | 26 | 25 | 0.9615 |
| `bit_structured_byte_formula` | 31 | 24 | 0.7742 |
| `glyph_len5` | 5 | 1 | 0.2000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 22 | 0.8148 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 20 | 1.0000 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 92 | 77 | 0.8370 |
| `numeric` | 62 | 58 | 0.9355 |
| `roman` | 19 | 19 | 1.0000 |
| `symbolic` | 7 | 2 | 0.2857 |
| `text_phrase` | 20 | 20 | 1.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 20 | 20 | 1.0000 |
| `400-499` | 26 | 24 | 0.9231 |
| `500-599` | 66 | 53 | 0.8030 |
| `<300` | 88 | 79 | 0.8977 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 66 | 53 | 0.8030 |
| `3` | 71 | 70 | 0.9859 |
| `4` | 16 | 15 | 0.9375 |
| `5` | 21 | 14 | 0.6667 |
| `7` | 8 | 7 | 0.8750 |
| `8` | 5 | 4 | 0.8000 |
| `9` | 13 | 13 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 21 | 0.8077 |
| `manual_audit_priority` | 18 | 8 | 0.4444 |
| `verified_trace_ready` | 156 | 147 | 0.9423 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `0.9891`
- regex_exact_rate: `0.9891`
- leading_zero_retention_rate: `0.98`
- format_failure_rate: `0.0109`
- format_ok_content_wrong_rate: `0.1538`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 26 | 19 | 0.7308 |
| `binary_affine_xor` | 10 | 10 | 1.0000 |
| `binary_bit_permutation_bijection` | 24 | 23 | 0.9583 |
| `binary_bit_permutation_independent` | 2 | 2 | 1.0000 |
| `binary_byte_transform` | 1 | 1 | 1.0000 |
| `binary_structured_byte_formula` | 10 | 7 | 0.7000 |
| `binary_structured_byte_formula_abstract` | 7 | 4 | 0.5714 |
| `binary_structured_byte_not_formula` | 2 | 2 | 1.0000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 8 | 0.8889 |
