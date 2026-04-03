# general_stable_set

## Overall

- rows: `200`
- correct: `81`
- accuracy: `0.4050`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 31 | 0.6200 |
| `roman` | 50 | 21 | 0.4200 |
| `text` | 50 | 4 | 0.0800 |
| `unit` | 50 | 25 | 0.5000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 31 | 0.6200 |
| `roman_standard` | 50 | 21 | 0.4200 |
| `text_monoalphabetic` | 50 | 4 | 0.0800 |
| `unit_fixed_ratio` | 50 | 25 | 0.5000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 56 | 0.5600 |
| `roman` | 50 | 21 | 0.4200 |
| `text_phrase` | 50 | 4 | 0.0800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 4 | 0.0909 |
| `<300` | 156 | 77 | 0.4936 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 81 | 0.4219 |
| `4` | 8 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 81 | 0.4050 |

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
