# phase0_eval_overall

## Overall

- rows: `48`
- correct: `35`
- accuracy: `0.7292`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 8 | 3 | 0.3750 |
| `gravity` | 8 | 8 | 1.0000 |
| `roman` | 8 | 8 | 1.0000 |
| `symbol` | 8 | 3 | 0.3750 |
| `text` | 8 | 7 | 0.8750 |
| `unit` | 8 | 6 | 0.7500 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 8 | 3 | 0.3750 |
| `gravity_half_g_t2` | 8 | 8 | 1.0000 |
| `numeric_2x2` | 8 | 3 | 0.3750 |
| `roman_standard` | 8 | 8 | 1.0000 |
| `text_monoalphabetic` | 8 | 7 | 0.8750 |
| `unit_fixed_ratio` | 8 | 6 | 0.7500 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 8 | 3 | 0.3750 |
| `numeric` | 23 | 16 | 0.6957 |
| `roman` | 8 | 8 | 1.0000 |
| `symbolic` | 1 | 1 | 1.0000 |
| `text_phrase` | 8 | 7 | 0.8750 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 2 | 2 | 1.0000 |
| `400-499` | 5 | 2 | 0.4000 |
| `500-599` | 3 | 1 | 0.3333 |
| `<300` | 38 | 30 | 0.7895 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 3 | 1 | 0.3333 |
| `3` | 32 | 29 | 0.9062 |
| `4` | 2 | 1 | 0.5000 |
| `5` | 6 | 2 | 0.3333 |
| `8` | 2 | 1 | 0.5000 |
| `9` | 3 | 1 | 0.3333 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 48 | 35 | 0.7292 |

## Binary metrics

- rows: `8`
- boxed_extraction_success_rate: `0.125`
- regex_exact_rate: `0.5`
- leading_zero_retention_rate: `0.3333`
- format_failure_rate: `0.875`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 8 | 3 | 0.3750 |
