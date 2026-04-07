# general_stable_set

## Overall

- rows: `200`
- correct: `173`
- accuracy: `0.8650`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 48 | 0.9600 |
| `text` | 50 | 32 | 0.6400 |
| `unit` | 50 | 44 | 0.8800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `roman_standard` | 50 | 48 | 0.9600 |
| `text_monoalphabetic` | 50 | 32 | 0.6400 |
| `unit_fixed_ratio` | 50 | 44 | 0.8800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 93 | 0.9300 |
| `roman` | 50 | 48 | 0.9600 |
| `text_phrase` | 50 | 32 | 0.6400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 29 | 0.6591 |
| `<300` | 156 | 144 | 0.9231 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 170 | 0.8854 |
| `4` | 8 | 3 | 0.3750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 173 | 0.8650 |

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
