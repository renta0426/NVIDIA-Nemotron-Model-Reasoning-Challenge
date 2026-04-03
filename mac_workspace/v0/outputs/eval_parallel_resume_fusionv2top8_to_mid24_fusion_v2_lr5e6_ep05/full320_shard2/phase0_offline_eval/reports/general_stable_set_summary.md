# general_stable_set

## Overall

- rows: `200`
- correct: `172`
- accuracy: `0.8600`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 47 | 0.9400 |
| `text` | 50 | 28 | 0.5600 |
| `unit` | 50 | 47 | 0.9400 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `roman_standard` | 50 | 47 | 0.9400 |
| `text_monoalphabetic` | 50 | 28 | 0.5600 |
| `unit_fixed_ratio` | 50 | 47 | 0.9400 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 97 | 0.9700 |
| `roman` | 50 | 47 | 0.9400 |
| `text_phrase` | 50 | 28 | 0.5600 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 25 | 0.5682 |
| `<300` | 156 | 147 | 0.9423 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 167 | 0.8698 |
| `4` | 8 | 5 | 0.6250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 172 | 0.8600 |

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
