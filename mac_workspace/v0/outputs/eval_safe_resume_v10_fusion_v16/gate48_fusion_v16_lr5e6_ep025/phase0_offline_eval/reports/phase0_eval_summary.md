# phase0_eval_overall

## Overall

- rows: `48`
- correct: `33`
- accuracy: `0.6875`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 8 | 3 | 0.3750 |
| `gravity` | 8 | 8 | 1.0000 |
| `roman` | 8 | 8 | 1.0000 |
| `symbol` | 8 | 3 | 0.3750 |
| `text` | 8 | 4 | 0.5000 |
| `unit` | 8 | 7 | 0.8750 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 8 | 3 | 0.3750 |
| `gravity_half_g_t2` | 8 | 8 | 1.0000 |
| `numeric_2x2` | 8 | 3 | 0.3750 |
| `roman_standard` | 8 | 8 | 1.0000 |
| `text_monoalphabetic` | 8 | 4 | 0.5000 |
| `unit_fixed_ratio` | 8 | 7 | 0.8750 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 8 | 3 | 0.3750 |
| `numeric` | 23 | 18 | 0.7826 |
| `roman` | 8 | 8 | 1.0000 |
| `symbolic` | 1 | 0 | 0.0000 |
| `text_phrase` | 8 | 4 | 0.5000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 2 | 0 | 0.0000 |
| `400-499` | 5 | 2 | 0.4000 |
| `500-599` | 3 | 1 | 0.3333 |
| `<300` | 38 | 30 | 0.7895 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 3 | 1 | 0.3333 |
| `3` | 32 | 27 | 0.8438 |
| `4` | 2 | 2 | 1.0000 |
| `5` | 6 | 1 | 0.1667 |
| `8` | 2 | 1 | 0.5000 |
| `9` | 3 | 1 | 0.3333 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 48 | 33 | 0.6875 |

## Binary metrics

- rows: `8`
- boxed_extraction_success_rate: `0.375`
- regex_exact_rate: `0.375`
- leading_zero_retention_rate: `0.3333`
- format_failure_rate: `0.625`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 8 | 3 | 0.3750 |
