# phase0_eval_overall

## Overall

- rows: `320`
- correct: `196`
- accuracy: `0.6125`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 19 | 0.3167 |
| `gravity` | 50 | 39 | 0.7800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 17 | 0.2833 |
| `text` | 50 | 21 | 0.4200 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 13 | 0.2826 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 39 | 0.7800 |
| `numeric_2x2` | 40 | 17 | 0.4250 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 21 | 0.4200 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 19 | 0.3167 |
| `numeric` | 136 | 105 | 0.7721 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 21 | 0.4200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 20 | 0.4545 |
| `400-499` | 40 | 16 | 0.4000 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 157 | 0.7269 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 160 | 0.8122 |
| `4` | 21 | 8 | 0.3810 |
| `5` | 42 | 9 | 0.2143 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 5 | 0.3846 |
| `9` | 16 | 9 | 0.5625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 14 | 0.4000 |
| `manual_audit_priority` | 50 | 5 | 0.1000 |
| `verified_trace_ready` | 235 | 177 | 0.7532 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.6833`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 13 | 0.3250 |
| `binary_affine_xor` | 20 | 6 | 0.3000 |
