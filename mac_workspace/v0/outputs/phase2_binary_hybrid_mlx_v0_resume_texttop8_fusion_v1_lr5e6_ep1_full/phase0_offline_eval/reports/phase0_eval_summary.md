# phase0_eval_overall

## Overall

- rows: `24`
- correct: `13`
- accuracy: `0.5417`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 4 | 0 | 0.0000 |
| `gravity` | 4 | 3 | 0.7500 |
| `roman` | 4 | 4 | 1.0000 |
| `symbol` | 4 | 1 | 0.2500 |
| `text` | 4 | 1 | 0.2500 |
| `unit` | 4 | 4 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 4 | 0 | 0.0000 |
| `gravity_half_g_t2` | 4 | 3 | 0.7500 |
| `numeric_2x2` | 4 | 1 | 0.2500 |
| `roman_standard` | 4 | 4 | 1.0000 |
| `text_monoalphabetic` | 4 | 1 | 0.2500 |
| `unit_fixed_ratio` | 4 | 4 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 4 | 0 | 0.0000 |
| `numeric` | 12 | 8 | 0.6667 |
| `roman` | 4 | 4 | 1.0000 |
| `text_phrase` | 4 | 1 | 0.2500 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 2 | 0 | 0.0000 |
| `500-599` | 2 | 0 | 0.0000 |
| `<300` | 20 | 13 | 0.6500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 2 | 0 | 0.0000 |
| `3` | 16 | 12 | 0.7500 |
| `5` | 4 | 1 | 0.2500 |
| `8` | 1 | 0 | 0.0000 |
| `9` | 1 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 24 | 13 | 0.5417 |

## Binary metrics

- rows: `4`
- boxed_extraction_success_rate: `0.25`
- regex_exact_rate: `0.0`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `1.0`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 4 | 0 | 0.0000 |
