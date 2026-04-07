# phase0_eval_overall

## Overall

- rows: `320`
- correct: `293`
- accuracy: `0.9156`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 54 | 0.9000 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 39 | 0.6500 |
| `text` | 50 | 50 | 1.0000 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 40 | 0.8696 |
| `bit_structured_byte_formula` | 14 | 14 | 1.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 39 | 0.9750 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 50 | 1.0000 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 54 | 0.9000 |
| `numeric` | 136 | 136 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 3 | 0.1250 |
| `text_phrase` | 50 | 50 | 1.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 44 | 1.0000 |
| `400-499` | 40 | 39 | 0.9750 |
| `500-599` | 20 | 15 | 0.7500 |
| `<300` | 216 | 195 | 0.9028 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 15 | 0.7500 |
| `3` | 197 | 197 | 1.0000 |
| `4` | 21 | 20 | 0.9524 |
| `5` | 42 | 22 | 0.5238 |
| `7` | 11 | 10 | 0.9091 |
| `8` | 13 | 13 | 1.0000 |
| `9` | 16 | 16 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 35 | 1.0000 |
| `manual_audit_priority` | 50 | 23 | 0.4600 |
| `verified_trace_ready` | 235 | 235 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.1`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 34 | 0.8500 |
| `binary_affine_xor` | 20 | 20 | 1.0000 |
