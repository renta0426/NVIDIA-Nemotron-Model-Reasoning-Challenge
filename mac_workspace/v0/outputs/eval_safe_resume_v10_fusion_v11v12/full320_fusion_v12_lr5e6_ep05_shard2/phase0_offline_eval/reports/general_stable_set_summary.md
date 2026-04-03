# general_stable_set

## Overall

- rows: `200`
- correct: `174`
- accuracy: `0.8700`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 47 | 0.9400 |
| `roman` | 50 | 46 | 0.9200 |
| `text` | 50 | 31 | 0.6200 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 47 | 0.9400 |
| `roman_standard` | 50 | 46 | 0.9200 |
| `text_monoalphabetic` | 50 | 31 | 0.6200 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 97 | 0.9700 |
| `roman` | 50 | 46 | 0.9200 |
| `text_phrase` | 50 | 31 | 0.6200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 25 | 0.5682 |
| `<300` | 156 | 149 | 0.9551 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 170 | 0.8854 |
| `4` | 8 | 4 | 0.5000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 174 | 0.8700 |

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
