# leaderboard_proxy_v1_set

## Overall

- rows: `200`
- correct: `173`
- accuracy: `0.8650`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 92 | 74 | 0.8043 |
| `gravity` | 19 | 19 | 1.0000 |
| `roman` | 19 | 19 | 1.0000 |
| `symbol` | 32 | 23 | 0.7188 |
| `text` | 20 | 20 | 1.0000 |
| `unit` | 18 | 18 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 35 | 28 | 0.8000 |
| `bit_permutation_inversion` | 26 | 23 | 0.8846 |
| `bit_structured_byte_formula` | 31 | 23 | 0.7419 |
| `glyph_len5` | 5 | 1 | 0.2000 |
| `gravity_half_g_t2` | 19 | 19 | 1.0000 |
| `numeric_2x2` | 27 | 22 | 0.8148 |
| `roman_standard` | 19 | 19 | 1.0000 |
| `text_monoalphabetic` | 20 | 20 | 1.0000 |
| `unit_fixed_ratio` | 18 | 18 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 92 | 74 | 0.8043 |
| `numeric` | 62 | 58 | 0.9355 |
| `roman` | 19 | 19 | 1.0000 |
| `symbolic` | 7 | 2 | 0.2857 |
| `text_phrase` | 20 | 20 | 1.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 20 | 20 | 1.0000 |
| `400-499` | 26 | 21 | 0.8077 |
| `500-599` | 66 | 53 | 0.8030 |
| `<300` | 88 | 79 | 0.8977 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 66 | 53 | 0.8030 |
| `3` | 71 | 70 | 0.9859 |
| `4` | 16 | 15 | 0.9375 |
| `5` | 21 | 14 | 0.6667 |
| `7` | 8 | 5 | 0.6250 |
| `8` | 5 | 3 | 0.6000 |
| `9` | 13 | 13 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 26 | 20 | 0.7692 |
| `manual_audit_priority` | 18 | 8 | 0.4444 |
| `verified_trace_ready` | 156 | 145 | 0.9295 |

## Binary metrics

- rows: `92`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `1.0`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.1957`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 26 | 18 | 0.6923 |
| `binary_affine_xor` | 10 | 10 | 1.0000 |
| `binary_bit_permutation_bijection` | 24 | 22 | 0.9167 |
| `binary_bit_permutation_independent` | 2 | 1 | 0.5000 |
| `binary_byte_transform` | 1 | 1 | 1.0000 |
| `binary_structured_byte_formula` | 10 | 8 | 0.8000 |
| `binary_structured_byte_formula_abstract` | 7 | 3 | 0.4286 |
| `binary_structured_byte_not_formula` | 2 | 2 | 1.0000 |
| `binary_three_bit_boolean` | 1 | 1 | 1.0000 |
| `binary_two_bit_boolean` | 9 | 8 | 0.8889 |
