# general_stable_set

## Overall

- rows: `200`
- correct: `174`
- accuracy: `0.8700`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `text` | 50 | 25 | 0.5000 |
| `unit` | 50 | 49 | 0.9800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 25 | 0.5000 |
| `unit_fixed_ratio` | 50 | 49 | 0.9800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 99 | 0.9900 |
| `roman` | 50 | 50 | 1.0000 |
| `text_phrase` | 50 | 25 | 0.5000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 23 | 0.5227 |
| `<300` | 156 | 151 | 0.9679 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 171 | 0.8906 |
| `4` | 8 | 3 | 0.3750 |

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
