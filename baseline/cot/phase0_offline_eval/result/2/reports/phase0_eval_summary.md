# phase0_eval_overall

## Overall

- rows: `320`
- correct: `227`
- accuracy: `0.7094`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 13 | 0.2167 |
| `gravity` | 50 | 47 | 0.9400 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 24 | 0.4000 |
| `text` | 50 | 43 | 0.8600 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 13 | 0.2826 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 47 | 0.9400 |
| `numeric_2x2` | 40 | 24 | 0.6000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 43 | 0.8600 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 13 | 0.2167 |
| `numeric` | 136 | 120 | 0.8824 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 43 | 0.8600 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 37 | 0.8409 |
| `400-499` | 40 | 9 | 0.2250 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 177 | 0.8194 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 186 | 0.9442 |
| `4` | 21 | 15 | 0.7143 |
| `5` | 42 | 13 | 0.3095 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 4 | 0.2500 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 11 | 0.3143 |
| `manual_audit_priority` | 50 | 4 | 0.0800 |
| `verified_trace_ready` | 235 | 212 | 0.9021 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.2`
- regex_exact_rate: `0.35`
- leading_zero_retention_rate: `0.4`
- format_failure_rate: `0.8`
- format_ok_content_wrong_rate: `0.25`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 6 | 0.1500 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
