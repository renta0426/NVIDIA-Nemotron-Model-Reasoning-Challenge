# general_stable_set

## Overall

- rows: `200`
- correct: `37`
- accuracy: `0.1850`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 3 | 0.0600 |
| `roman` | 50 | 1 | 0.0200 |
| `text` | 50 | 0 | 0.0000 |
| `unit` | 50 | 33 | 0.6600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 3 | 0.0600 |
| `roman_standard` | 50 | 1 | 0.0200 |
| `text_monoalphabetic` | 50 | 0 | 0.0000 |
| `unit_fixed_ratio` | 50 | 33 | 0.6600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 36 | 0.3600 |
| `roman` | 50 | 1 | 0.0200 |
| `text_phrase` | 50 | 0 | 0.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 0 | 0.0000 |
| `<300` | 156 | 37 | 0.2372 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 37 | 0.1927 |
| `4` | 8 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 37 | 0.1850 |

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
