# phase0_eval_overall

## Overall

- rows: `12`
- correct: `7`
- accuracy: `0.5833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 2 | 1 | 0.5000 |
| `gravity` | 2 | 2 | 1.0000 |
| `roman` | 2 | 2 | 1.0000 |
| `symbol` | 2 | 0 | 0.0000 |
| `text` | 2 | 0 | 0.0000 |
| `unit` | 2 | 2 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 2 | 1 | 0.5000 |
| `gravity_half_g_t2` | 2 | 2 | 1.0000 |
| `numeric_2x2` | 2 | 0 | 0.0000 |
| `roman_standard` | 2 | 2 | 1.0000 |
| `text_monoalphabetic` | 2 | 0 | 0.0000 |
| `unit_fixed_ratio` | 2 | 2 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 2 | 1 | 0.5000 |
| `numeric` | 6 | 4 | 0.6667 |
| `roman` | 2 | 2 | 1.0000 |
| `text_phrase` | 2 | 0 | 0.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 1 | 0 | 0.0000 |
| `500-599` | 1 | 1 | 1.0000 |
| `<300` | 10 | 6 | 0.6000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 1 | 1 | 1.0000 |
| `3` | 8 | 6 | 0.7500 |
| `5` | 2 | 0 | 0.0000 |
| `9` | 1 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 12 | 7 | 0.5833 |

## Binary metrics

- rows: `2`
- boxed_extraction_success_rate: `0.5`
- regex_exact_rate: `0.5`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.5`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 2 | 1 | 0.5000 |
