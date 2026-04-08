# general_stable_set

## Overall

- rows: `200`
- correct: `108`
- accuracy: `0.5400`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 17 | 0.3400 |
| `roman` | 50 | 40 | 0.8000 |
| `text` | 50 | 7 | 0.1400 |
| `unit` | 50 | 44 | 0.8800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 17 | 0.3400 |
| `roman_standard` | 50 | 40 | 0.8000 |
| `text_monoalphabetic` | 50 | 7 | 0.1400 |
| `unit_fixed_ratio` | 50 | 44 | 0.8800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 61 | 0.6100 |
| `roman` | 50 | 40 | 0.8000 |
| `text_phrase` | 50 | 7 | 0.1400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 7 | 0.1591 |
| `<300` | 156 | 101 | 0.6474 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 107 | 0.5573 |
| `4` | 8 | 1 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 108 | 0.5400 |

## Binary metrics

- rows: `0`
- boxed_extraction_success_rate: `0.0`
- regex_exact_rate: `0.0`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
