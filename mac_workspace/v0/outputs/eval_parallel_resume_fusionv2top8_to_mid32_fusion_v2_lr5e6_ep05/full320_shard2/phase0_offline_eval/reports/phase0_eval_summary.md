# phase0_eval_overall

## Overall

- rows: `320`
- correct: `176`
- accuracy: `0.5500`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 4 | 0.0667 |
| `gravity` | 50 | 41 | 0.8200 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 10 | 0.1667 |
| `text` | 50 | 27 | 0.5400 |
| `unit` | 50 | 44 | 0.8800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 3 | 0.0652 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 41 | 0.8200 |
| `numeric_2x2` | 40 | 10 | 0.2500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 27 | 0.5400 |
| `unit_fixed_ratio` | 50 | 44 | 0.8800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 4 | 0.0667 |
| `numeric` | 136 | 94 | 0.6912 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 27 | 0.5400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 23 | 0.5227 |
| `400-499` | 40 | 2 | 0.0500 |
| `500-599` | 20 | 2 | 0.1000 |
| `<300` | 216 | 149 | 0.6898 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 2 | 0.1000 |
| `3` | 197 | 161 | 0.8173 |
| `4` | 21 | 4 | 0.1905 |
| `5` | 42 | 7 | 0.1667 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 2 | 0.0571 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 174 | 0.7404 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0833`
- regex_exact_rate: `0.1333`
- leading_zero_retention_rate: `0.1333`
- format_failure_rate: `0.9667`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 1 | 0.0250 |
| `binary_affine_xor` | 20 | 3 | 0.1500 |
