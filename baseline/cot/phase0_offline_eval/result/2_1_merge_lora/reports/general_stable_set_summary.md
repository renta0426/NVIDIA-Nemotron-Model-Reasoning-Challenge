# general_stable_set

## Overall

- rows: `200`
- correct: `169`
- accuracy: `0.8450`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 39 | 0.7800 |
| `roman` | 50 | 50 | 1.0000 |
| `text` | 50 | 41 | 0.8200 |
| `unit` | 50 | 39 | 0.7800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 39 | 0.7800 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 41 | 0.8200 |
| `unit_fixed_ratio` | 50 | 39 | 0.7800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 78 | 0.7800 |
| `roman` | 50 | 50 | 1.0000 |
| `text_phrase` | 50 | 41 | 0.8200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 37 | 0.8409 |
| `<300` | 156 | 132 | 0.8462 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 163 | 0.8490 |
| `4` | 8 | 6 | 0.7500 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 169 | 0.8450 |

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
