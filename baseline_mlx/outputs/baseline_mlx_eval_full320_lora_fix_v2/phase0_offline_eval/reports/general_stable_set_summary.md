# general_stable_set

## Overall

- rows: `200`
- correct: `156`
- accuracy: `0.7800`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `text` | 50 | 9 | 0.1800 |
| `unit` | 50 | 48 | 0.9600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 9 | 0.1800 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 97 | 0.9700 |
| `roman` | 50 | 50 | 1.0000 |
| `text_phrase` | 50 | 9 | 0.1800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 8 | 0.1818 |
| `<300` | 156 | 148 | 0.9487 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 155 | 0.8073 |
| `4` | 8 | 1 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 156 | 0.7800 |

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
