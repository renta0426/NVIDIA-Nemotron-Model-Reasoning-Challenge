# phase0_eval_overall

## Overall

- rows: `48`
- correct: `34`
- accuracy: `0.7083`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 8 | 2 | 0.2500 |
| `gravity` | 8 | 8 | 1.0000 |
| `roman` | 8 | 8 | 1.0000 |
| `symbol` | 8 | 1 | 0.1250 |
| `text` | 8 | 7 | 0.8750 |
| `unit` | 8 | 8 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 8 | 2 | 0.2500 |
| `gravity_half_g_t2` | 8 | 8 | 1.0000 |
| `numeric_2x2` | 8 | 1 | 0.1250 |
| `roman_standard` | 8 | 8 | 1.0000 |
| `text_monoalphabetic` | 8 | 7 | 0.8750 |
| `unit_fixed_ratio` | 8 | 8 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 8 | 2 | 0.2500 |
| `numeric` | 23 | 17 | 0.7391 |
| `roman` | 8 | 8 | 1.0000 |
| `symbolic` | 1 | 0 | 0.0000 |
| `text_phrase` | 8 | 7 | 0.8750 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 2 | 2 | 1.0000 |
| `400-499` | 5 | 2 | 0.4000 |
| `500-599` | 3 | 0 | 0.0000 |
| `<300` | 38 | 30 | 0.7895 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 3 | 0 | 0.0000 |
| `3` | 32 | 31 | 0.9688 |
| `4` | 2 | 1 | 0.5000 |
| `5` | 6 | 0 | 0.0000 |
| `8` | 2 | 1 | 0.5000 |
| `9` | 3 | 1 | 0.3333 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 48 | 34 | 0.7083 |

## Binary metrics

- rows: `8`
- boxed_extraction_success_rate: `0.5`
- regex_exact_rate: `0.5`
- leading_zero_retention_rate: `0.3333`
- format_failure_rate: `0.75`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 8 | 2 | 0.2500 |
