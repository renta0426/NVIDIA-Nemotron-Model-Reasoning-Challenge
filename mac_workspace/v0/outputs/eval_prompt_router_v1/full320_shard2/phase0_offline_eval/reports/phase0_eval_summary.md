# phase0_eval_overall

## Overall

- rows: `320`
- correct: `245`
- accuracy: `0.7656`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 31 | 0.5167 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 29 | 0.4833 |
| `text` | 50 | 36 | 0.7200 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 25 | 0.5435 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 29 | 0.7250 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 36 | 0.7200 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 31 | 0.5167 |
| `numeric` | 136 | 127 | 0.9338 |
| `roman` | 50 | 49 | 0.9800 |
| `symbolic` | 24 | 2 | 0.0833 |
| `text_phrase` | 50 | 36 | 0.7200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 30 | 0.6818 |
| `400-499` | 40 | 22 | 0.5500 |
| `500-599` | 20 | 9 | 0.4500 |
| `<300` | 216 | 184 | 0.8519 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 9 | 0.4500 |
| `3` | 197 | 181 | 0.9188 |
| `4` | 21 | 18 | 0.8571 |
| `5` | 42 | 15 | 0.3571 |
| `7` | 11 | 5 | 0.4545 |
| `8` | 13 | 7 | 0.5385 |
| `9` | 16 | 10 | 0.6250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 24 | 0.6857 |
| `manual_audit_priority` | 50 | 6 | 0.1200 |
| `verified_trace_ready` | 235 | 215 | 0.9149 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.8667`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.4833`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 16 | 0.4000 |
| `binary_affine_xor` | 20 | 15 | 0.7500 |
