# phase0_eval_overall

## Overall

- rows: `320`
- correct: `215`
- accuracy: `0.6719`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 26 | 0.4333 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 15 | 0.2500 |
| `text` | 50 | 25 | 0.5000 |
| `unit` | 50 | 49 | 0.9800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 19 | 0.4130 |
| `bit_structured_byte_formula` | 14 | 7 | 0.5000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 15 | 0.3750 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 25 | 0.5000 |
| `unit_fixed_ratio` | 50 | 49 | 0.9800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 26 | 0.4333 |
| `numeric` | 136 | 113 | 0.8309 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 25 | 0.5000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 23 | 0.5227 |
| `400-499` | 40 | 21 | 0.5250 |
| `500-599` | 20 | 5 | 0.2500 |
| `<300` | 216 | 166 | 0.7685 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 5 | 0.2500 |
| `3` | 197 | 172 | 0.8731 |
| `4` | 21 | 7 | 0.3333 |
| `5` | 42 | 10 | 0.2381 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 6 | 0.4615 |
| `9` | 16 | 11 | 0.6875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 14 | 0.4000 |
| `manual_audit_priority` | 50 | 7 | 0.1400 |
| `verified_trace_ready` | 235 | 194 | 0.8255 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.5667`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 16 | 0.4000 |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
