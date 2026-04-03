# phase0_eval_overall

## Overall

- rows: `320`
- correct: `169`
- accuracy: `0.5281`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |
| `gravity` | 50 | 40 | 0.8000 |
| `roman` | 50 | 47 | 0.9400 |
| `symbol` | 60 | 10 | 0.1667 |
| `text` | 50 | 20 | 0.4000 |
| `unit` | 50 | 47 | 0.9400 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 5 | 0.1087 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 40 | 0.8000 |
| `numeric_2x2` | 40 | 10 | 0.2500 |
| `roman_standard` | 50 | 47 | 0.9400 |
| `text_monoalphabetic` | 50 | 20 | 0.4000 |
| `unit_fixed_ratio` | 50 | 47 | 0.9400 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |
| `numeric` | 136 | 97 | 0.7132 |
| `roman` | 50 | 47 | 0.9400 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 20 | 0.4000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 15 | 0.3409 |
| `400-499` | 40 | 2 | 0.0500 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 149 | 0.6898 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 150 | 0.7614 |
| `4` | 21 | 11 | 0.5238 |
| `5` | 42 | 3 | 0.0714 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 4 | 0.1143 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 165 | 0.7021 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0667`
- regex_exact_rate: `0.2`
- leading_zero_retention_rate: `0.1667`
- format_failure_rate: `0.95`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 0 | 0.0000 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
