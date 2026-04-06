# general_stable_set

## Overall

- rows: `200`
- correct: `178`
- accuracy: `0.8900`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 48 | 0.9600 |
| `roman` | 50 | 47 | 0.9400 |
| `text` | 50 | 41 | 0.8200 |
| `unit` | 50 | 42 | 0.8400 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 48 | 0.9600 |
| `roman_standard` | 50 | 47 | 0.9400 |
| `text_monoalphabetic` | 50 | 41 | 0.8200 |
| `unit_fixed_ratio` | 50 | 42 | 0.8400 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 90 | 0.9000 |
| `roman` | 50 | 47 | 0.9400 |
| `text_phrase` | 50 | 41 | 0.8200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 36 | 0.8182 |
| `<300` | 156 | 142 | 0.9103 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 170 | 0.8854 |
| `4` | 8 | 8 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 178 | 0.8900 |

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
