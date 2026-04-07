# phase0_eval_overall

## Overall

- rows: `200`
- correct: `175`
- accuracy: `0.8750`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 48 | 0.9600 |
| `text` | 50 | 34 | 0.6800 |
| `unit` | 50 | 44 | 0.8800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `roman_standard` | 50 | 48 | 0.9600 |
| `text_monoalphabetic` | 50 | 34 | 0.6800 |
| `unit_fixed_ratio` | 50 | 44 | 0.8800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `numeric` | 100 | 93 | 0.9300 |
| `roman` | 50 | 48 | 0.9600 |
| `text_phrase` | 50 | 34 | 0.6800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 30 | 0.6818 |
| `<300` | 156 | 145 | 0.9295 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `3` | 192 | 169 | 0.8802 |
| `4` | 8 | 6 | 0.7500 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 200 | 175 | 0.8750 |

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
