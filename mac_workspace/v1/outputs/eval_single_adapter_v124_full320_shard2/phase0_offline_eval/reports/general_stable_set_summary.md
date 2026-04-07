# general_stable_set

## Overall

- rows: `200`
- correct: `176`
- accuracy: `0.8800`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 47 | 0.9400 |
| `text` | 50 | 35 | 0.7000 |
| `unit` | 50 | 45 | 0.9000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `roman_standard` | 50 | 47 | 0.9400 |
| `text_monoalphabetic` | 50 | 35 | 0.7000 |
| `unit_fixed_ratio` | 50 | 45 | 0.9000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 94 | 0.9400 |
| `roman` | 50 | 47 | 0.9400 |
| `text_phrase` | 50 | 35 | 0.7000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 32 | 0.7273 |
| `<300` | 156 | 144 | 0.9231 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 172 | 0.8958 |
| `4` | 8 | 4 | 0.5000 |

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
