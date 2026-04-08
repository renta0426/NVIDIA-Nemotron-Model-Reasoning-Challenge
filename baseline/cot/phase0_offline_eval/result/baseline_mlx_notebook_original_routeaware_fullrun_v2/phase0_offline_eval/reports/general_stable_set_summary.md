# general_stable_set

## Overall

- rows: `200`
- correct: `132`
- accuracy: `0.6600`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 15 | 0.3000 |
| `roman` | 50 | 40 | 0.8000 |
| `text` | 50 | 29 | 0.5800 |
| `unit` | 50 | 48 | 0.9600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 15 | 0.3000 |
| `roman_standard` | 50 | 40 | 0.8000 |
| `text_monoalphabetic` | 50 | 29 | 0.5800 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 63 | 0.6300 |
| `roman` | 50 | 40 | 0.8000 |
| `text_phrase` | 50 | 29 | 0.5800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 28 | 0.6364 |
| `<300` | 156 | 104 | 0.6667 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 129 | 0.6719 |
| `4` | 8 | 3 | 0.3750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 132 | 0.6600 |

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
