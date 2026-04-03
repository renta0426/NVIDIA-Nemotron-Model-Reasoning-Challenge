# phase0_eval_overall

## Overall

- rows: `48`
- correct: `28`
- accuracy: `0.5833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 8 | 5 | 0.6250 |
| `gravity` | 8 | 1 | 0.1250 |
| `roman` | 8 | 8 | 1.0000 |
| `symbol` | 8 | 6 | 0.7500 |
| `text` | 8 | 0 | 0.0000 |
| `unit` | 8 | 8 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 8 | 5 | 0.6250 |
| `gravity_half_g_t2` | 8 | 1 | 0.1250 |
| `numeric_2x2` | 8 | 6 | 0.7500 |
| `roman_standard` | 8 | 8 | 1.0000 |
| `text_monoalphabetic` | 8 | 0 | 0.0000 |
| `unit_fixed_ratio` | 8 | 8 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 8 | 5 | 0.6250 |
| `numeric` | 23 | 14 | 0.6087 |
| `roman` | 8 | 8 | 1.0000 |
| `symbolic` | 1 | 1 | 1.0000 |
| `text_phrase` | 8 | 0 | 0.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 2 | 0 | 0.0000 |
| `400-499` | 5 | 3 | 0.6000 |
| `500-599` | 3 | 2 | 0.6667 |
| `<300` | 38 | 23 | 0.6053 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 3 | 2 | 0.6667 |
| `3` | 32 | 17 | 0.5312 |
| `4` | 2 | 2 | 1.0000 |
| `5` | 6 | 4 | 0.6667 |
| `8` | 2 | 2 | 1.0000 |
| `9` | 3 | 1 | 0.3333 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 48 | 28 | 0.5833 |

## Binary metrics

- rows: `8`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `1.0`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.375`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 8 | 5 | 0.6250 |
