# phase0_eval_overall

## Overall

- rows: `200`
- correct: `144`
- accuracy: `0.7200`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 25 | 0.5000 |
| `roman` | 50 | 50 | 1.0000 |
| `text` | 50 | 36 | 0.7200 |
| `unit` | 50 | 33 | 0.6600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 25 | 0.5000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 36 | 0.7200 |
| `unit_fixed_ratio` | 50 | 33 | 0.6600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 58 | 0.5800 |
| `roman` | 50 | 50 | 1.0000 |
| `text_phrase` | 50 | 36 | 0.7200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 32 | 0.7273 |
| `<300` | 156 | 112 | 0.7179 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 138 | 0.7188 |
| `4` | 8 | 6 | 0.7500 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 144 | 0.7200 |

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
