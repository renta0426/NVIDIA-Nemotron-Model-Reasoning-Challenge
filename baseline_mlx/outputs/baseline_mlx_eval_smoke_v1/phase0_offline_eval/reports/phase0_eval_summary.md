# phase0_eval_overall

## Overall

- rows: `6`
- correct: `4`
- accuracy: `0.6667`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 1 | 1 | 1.0000 |
| `gravity` | 1 | 1 | 1.0000 |
| `roman` | 1 | 1 | 1.0000 |
| `symbol` | 1 | 0 | 0.0000 |
| `text` | 1 | 0 | 0.0000 |
| `unit` | 1 | 1 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 1 | 1 | 1.0000 |
| `gravity_half_g_t2` | 1 | 1 | 1.0000 |
| `numeric_2x2` | 1 | 0 | 0.0000 |
| `roman_standard` | 1 | 1 | 1.0000 |
| `text_monoalphabetic` | 1 | 0 | 0.0000 |
| `unit_fixed_ratio` | 1 | 1 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 1 | 1 | 1.0000 |
| `numeric` | 3 | 2 | 0.6667 |
| `roman` | 1 | 1 | 1.0000 |
| `text_phrase` | 1 | 0 | 0.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `500-599` | 1 | 1 | 1.0000 |
| `<300` | 5 | 3 | 0.6000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 1 | 1 | 1.0000 |
| `3` | 4 | 3 | 0.7500 |
| `5` | 1 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 6 | 4 | 0.6667 |

## Binary metrics

- rows: `1`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 1 | 1 | 1.0000 |
