# phase0_eval_overall

## Overall

- rows: `24`
- correct: `20`
- accuracy: `0.8333`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 4 | 3 | 0.7500 |
| `gravity` | 4 | 4 | 1.0000 |
| `roman` | 4 | 4 | 1.0000 |
| `symbol` | 4 | 3 | 0.7500 |
| `text` | 4 | 2 | 0.5000 |
| `unit` | 4 | 4 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 4 | 3 | 0.7500 |
| `gravity_half_g_t2` | 4 | 4 | 1.0000 |
| `numeric_2x2` | 4 | 3 | 0.7500 |
| `roman_standard` | 4 | 4 | 1.0000 |
| `text_monoalphabetic` | 4 | 2 | 0.5000 |
| `unit_fixed_ratio` | 4 | 4 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 4 | 3 | 0.7500 |
| `numeric` | 12 | 11 | 0.9167 |
| `roman` | 4 | 4 | 1.0000 |
| `text_phrase` | 4 | 2 | 0.5000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 2 | 2 | 1.0000 |
| `500-599` | 2 | 1 | 0.5000 |
| `<300` | 20 | 17 | 0.8500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 2 | 1 | 0.5000 |
| `3` | 16 | 14 | 0.8750 |
| `5` | 4 | 3 | 0.7500 |
| `8` | 1 | 1 | 1.0000 |
| `9` | 1 | 1 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 24 | 20 | 0.8333 |

## Binary metrics

- rows: `4`
- boxed_extraction_success_rate: `0.75`
- regex_exact_rate: `0.75`
- leading_zero_retention_rate: `0.5`
- format_failure_rate: `0.25`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 4 | 3 | 0.7500 |
