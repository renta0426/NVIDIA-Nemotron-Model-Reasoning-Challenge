# phase0_eval_overall

## Overall

- rows: `24`
- correct: `14`
- accuracy: `0.5833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 4 | 1 | 0.2500 |
| `gravity` | 4 | 4 | 1.0000 |
| `roman` | 4 | 3 | 0.7500 |
| `symbol` | 4 | 0 | 0.0000 |
| `text` | 4 | 3 | 0.7500 |
| `unit` | 4 | 3 | 0.7500 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 4 | 1 | 0.2500 |
| `gravity_half_g_t2` | 4 | 4 | 1.0000 |
| `numeric_2x2` | 4 | 0 | 0.0000 |
| `roman_standard` | 4 | 3 | 0.7500 |
| `text_monoalphabetic` | 4 | 3 | 0.7500 |
| `unit_fixed_ratio` | 4 | 3 | 0.7500 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 4 | 1 | 0.2500 |
| `numeric` | 12 | 7 | 0.5833 |
| `roman` | 4 | 3 | 0.7500 |
| `text_phrase` | 4 | 3 | 0.7500 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 2 | 1 | 0.5000 |
| `500-599` | 2 | 0 | 0.0000 |
| `<300` | 20 | 13 | 0.6500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 2 | 0 | 0.0000 |
| `3` | 16 | 13 | 0.8125 |
| `5` | 4 | 0 | 0.0000 |
| `8` | 1 | 1 | 1.0000 |
| `9` | 1 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 24 | 14 | 0.5833 |

## Binary metrics

- rows: `4`
- boxed_extraction_success_rate: `0.25`
- regex_exact_rate: `0.5`
- leading_zero_retention_rate: `0.5`
- format_failure_rate: `0.75`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 4 | 1 | 0.2500 |
