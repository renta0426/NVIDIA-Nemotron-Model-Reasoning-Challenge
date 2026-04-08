# phase0_eval_overall

## Overall

- rows: `320`
- correct: `189`
- accuracy: `0.5906`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 15 | 0.2500 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 18 | 0.3000 |
| `text` | 50 | 10 | 0.2000 |
| `unit` | 50 | 47 | 0.9400 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 10 | 0.2174 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 18 | 0.4500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 10 | 0.2000 |
| `unit_fixed_ratio` | 50 | 47 | 0.9400 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 15 | 0.2500 |
| `numeric` | 136 | 113 | 0.8309 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 10 | 0.2000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 10 | 0.2273 |
| `400-499` | 40 | 12 | 0.3000 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 164 | 0.7593 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 157 | 0.7970 |
| `4` | 21 | 7 | 0.3333 |
| `5` | 42 | 10 | 0.2381 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 3 | 0.2308 |
| `9` | 16 | 8 | 0.5000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 14 | 0.4000 |
| `manual_audit_priority` | 50 | 4 | 0.0800 |
| `verified_trace_ready` | 235 | 171 | 0.7277 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9333`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.75`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 10 | 0.2500 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
