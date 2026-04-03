# phase0_eval_overall

## Overall

- rows: `320`
- correct: `200`
- accuracy: `0.6250`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 10 | 0.1667 |
| `gravity` | 50 | 39 | 0.7800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 21 | 0.3500 |
| `text` | 50 | 41 | 0.8200 |
| `unit` | 50 | 39 | 0.7800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 8 | 0.1739 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 39 | 0.7800 |
| `numeric_2x2` | 40 | 21 | 0.5250 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 41 | 0.8200 |
| `unit_fixed_ratio` | 50 | 39 | 0.7800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 10 | 0.1667 |
| `numeric` | 136 | 98 | 0.7206 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 41 | 0.8200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 37 | 0.8409 |
| `400-499` | 40 | 6 | 0.1500 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 153 | 0.7083 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 164 | 0.8325 |
| `4` | 21 | 14 | 0.6667 |
| `5` | 42 | 12 | 0.2857 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 3 | 0.1875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 9 | 0.2571 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 190 | 0.8085 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1333`
- regex_exact_rate: `0.1833`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.8667`
- format_ok_content_wrong_rate: `0.125`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 3 | 0.0750 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
