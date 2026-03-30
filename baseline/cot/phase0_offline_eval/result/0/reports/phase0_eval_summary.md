# phase0_eval_overall

## Overall

- rows: `320`
- correct: `216`
- accuracy: `0.6750`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 11 | 0.1833 |
| `gravity` | 50 | 43 | 0.8600 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 26 | 0.4333 |
| `text` | 50 | 37 | 0.7400 |
| `unit` | 50 | 49 | 0.9800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 10 | 0.2174 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 43 | 0.8600 |
| `numeric_2x2` | 40 | 26 | 0.6500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 37 | 0.7400 |
| `unit_fixed_ratio` | 50 | 49 | 0.9800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 11 | 0.1833 |
| `numeric` | 136 | 117 | 0.8603 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 37 | 0.7400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 31 | 0.7045 |
| `400-499` | 40 | 8 | 0.2000 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 174 | 0.8056 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 179 | 0.9086 |
| `4` | 21 | 13 | 0.6190 |
| `5` | 42 | 13 | 0.3095 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 3 | 0.1875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 14 | 0.4000 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 201 | 0.8553 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.2167`
- regex_exact_rate: `0.25`
- leading_zero_retention_rate: `0.3`
- format_failure_rate: `0.7833`
- format_ok_content_wrong_rate: `0.1538`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 4 | 0.1000 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
