# general_stable_set

## Overall

- rows: `32`
- correct: `29`
- accuracy: `0.9062`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 8 | 8 | 1.0000 |
| `roman` | 8 | 8 | 1.0000 |
| `text` | 8 | 7 | 0.8750 |
| `unit` | 8 | 6 | 0.7500 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 8 | 8 | 1.0000 |
| `roman_standard` | 8 | 8 | 1.0000 |
| `text_monoalphabetic` | 8 | 7 | 0.8750 |
| `unit_fixed_ratio` | 8 | 6 | 0.7500 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 16 | 14 | 0.8750 |
| `roman` | 8 | 8 | 1.0000 |
| `text_phrase` | 8 | 7 | 0.8750 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 2 | 2 | 1.0000 |
| `<300` | 30 | 27 | 0.9000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 32 | 29 | 0.9062 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 32 | 29 | 0.9062 |

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
