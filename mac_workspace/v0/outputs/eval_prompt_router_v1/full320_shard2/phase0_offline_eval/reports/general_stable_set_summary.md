# general_stable_set

## Overall

- rows: `200`
- correct: `185`
- accuracy: `0.9250`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 49 | 0.9800 |
| `text` | 50 | 36 | 0.7200 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 36 | 0.7200 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 100 | 1.0000 |
| `roman` | 50 | 49 | 0.9800 |
| `text_phrase` | 50 | 36 | 0.7200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 30 | 0.6818 |
| `<300` | 156 | 155 | 0.9936 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 177 | 0.9219 |
| `4` | 8 | 8 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 185 | 0.9250 |

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
