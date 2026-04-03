# phase0_eval_overall

## Overall

- rows: `48`
- correct: `38`
- accuracy: `0.7917`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 8 | 2 | 0.2500 |
| `gravity` | 8 | 8 | 1.0000 |
| `roman` | 8 | 8 | 1.0000 |
| `symbol` | 8 | 4 | 0.5000 |
| `text` | 8 | 8 | 1.0000 |
| `unit` | 8 | 8 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 8 | 2 | 0.2500 |
| `gravity_half_g_t2` | 8 | 8 | 1.0000 |
| `numeric_2x2` | 8 | 4 | 0.5000 |
| `roman_standard` | 8 | 8 | 1.0000 |
| `text_monoalphabetic` | 8 | 8 | 1.0000 |
| `unit_fixed_ratio` | 8 | 8 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 8 | 2 | 0.2500 |
| `numeric` | 23 | 20 | 0.8696 |
| `roman` | 8 | 8 | 1.0000 |
| `symbolic` | 1 | 0 | 0.0000 |
| `text_phrase` | 8 | 8 | 1.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 2 | 2 | 1.0000 |
| `400-499` | 5 | 1 | 0.2000 |
| `500-599` | 3 | 1 | 0.3333 |
| `<300` | 38 | 34 | 0.8947 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 3 | 1 | 0.3333 |
| `3` | 32 | 32 | 1.0000 |
| `4` | 2 | 2 | 1.0000 |
| `5` | 6 | 2 | 0.3333 |
| `8` | 2 | 1 | 0.5000 |
| `9` | 3 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 48 | 38 | 0.7917 |

## Binary metrics

- rows: `8`
- boxed_extraction_success_rate: `0.125`
- regex_exact_rate: `0.5`
- leading_zero_retention_rate: `0.3333`
- format_failure_rate: `0.875`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 8 | 2 | 0.2500 |
