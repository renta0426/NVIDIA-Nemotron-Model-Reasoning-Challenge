# phase0_eval_overall

## Overall

- rows: `320`
- correct: `170`
- accuracy: `0.5312`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 33 | 0.5500 |
| `gravity` | 50 | 15 | 0.3000 |
| `roman` | 50 | 40 | 0.8000 |
| `symbol` | 60 | 5 | 0.0833 |
| `text` | 50 | 29 | 0.5800 |
| `unit` | 50 | 48 | 0.9600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 26 | 0.5652 |
| `bit_structured_byte_formula` | 14 | 7 | 0.5000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 15 | 0.3000 |
| `numeric_2x2` | 40 | 5 | 0.1250 |
| `roman_standard` | 50 | 40 | 0.8000 |
| `text_monoalphabetic` | 50 | 29 | 0.5800 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 33 | 0.5500 |
| `numeric` | 136 | 68 | 0.5000 |
| `roman` | 50 | 40 | 0.8000 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 29 | 0.5800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 28 | 0.6364 |
| `400-499` | 40 | 25 | 0.6250 |
| `500-599` | 20 | 8 | 0.4000 |
| `<300` | 216 | 109 | 0.5046 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 8 | 0.4000 |
| `3` | 197 | 130 | 0.6599 |
| `4` | 21 | 5 | 0.2381 |
| `5` | 42 | 2 | 0.0476 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 7 | 0.5385 |
| `9` | 16 | 14 | 0.8750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 12 | 0.3429 |
| `manual_audit_priority` | 50 | 7 | 0.1400 |
| `verified_trace_ready` | 235 | 151 | 0.6426 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.45`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 17 | 0.4250 |
| `binary_affine_xor` | 20 | 16 | 0.8000 |
