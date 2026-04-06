# general_stable_set

## Overall

- rows: `200`
- correct: `192`
- accuracy: `0.9600`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `text` | 50 | 42 | 0.8400 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 42 | 0.8400 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 100 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `text_phrase` | 50 | 42 | 0.8400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 36 | 0.8182 |
| `<300` | 156 | 156 | 1.0000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 184 | 0.9583 |
| `4` | 8 | 8 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 192 | 0.9600 |

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
