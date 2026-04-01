# phase0_eval_overall

## Overall

- rows: `320`
- correct: `196`
- accuracy: `0.6125`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 10 | 0.1667 |
| `gravity` | 50 | 36 | 0.7200 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 23 | 0.3833 |
| `text` | 50 | 39 | 0.7800 |
| `unit` | 50 | 38 | 0.7600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 9 | 0.1957 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 36 | 0.7200 |
| `numeric_2x2` | 40 | 23 | 0.5750 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 39 | 0.7800 |
| `unit_fixed_ratio` | 50 | 38 | 0.7600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 10 | 0.1667 |
| `numeric` | 136 | 96 | 0.7059 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 39 | 0.7800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 35 | 0.7955 |
| `400-499` | 40 | 6 | 0.1500 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 151 | 0.6991 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 158 | 0.8020 |
| `4` | 21 | 16 | 0.7619 |
| `5` | 42 | 12 | 0.2857 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 0 | 0.0000 |
| `9` | 16 | 4 | 0.2500 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 12 | 0.3429 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 183 | 0.7787 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1167`
- regex_exact_rate: `0.1667`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.8833`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 3 | 0.0750 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
