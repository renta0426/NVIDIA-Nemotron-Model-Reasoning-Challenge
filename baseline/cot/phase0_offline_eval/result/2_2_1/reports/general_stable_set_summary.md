# general_stable_set

## Overall

- rows: `200`
- correct: `176`
- accuracy: `0.8800`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 47 | 0.9400 |
| `roman` | 50 | 50 | 1.0000 |
| `text` | 50 | 36 | 0.7200 |
| `unit` | 50 | 43 | 0.8600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 47 | 0.9400 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 36 | 0.7200 |
| `unit_fixed_ratio` | 50 | 43 | 0.8600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 90 | 0.9000 |
| `roman` | 50 | 50 | 1.0000 |
| `text_phrase` | 50 | 36 | 0.7200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 31 | 0.7045 |
| `<300` | 156 | 145 | 0.9295 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 171 | 0.8906 |
| `4` | 8 | 5 | 0.6250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 176 | 0.8800 |

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
