# phase0_eval_overall

## Overall

- rows: `320`
- correct: `209`
- accuracy: `0.6531`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 8 | 0.1333 |
| `gravity` | 50 | 47 | 0.9400 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 25 | 0.4167 |
| `text` | 50 | 36 | 0.7200 |
| `unit` | 50 | 43 | 0.8600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 8 | 0.1739 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 1 | 0.0500 |
| `gravity_half_g_t2` | 50 | 47 | 0.9400 |
| `numeric_2x2` | 40 | 24 | 0.6000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 36 | 0.7200 |
| `unit_fixed_ratio` | 50 | 43 | 0.8600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 8 | 0.1333 |
| `numeric` | 136 | 113 | 0.8309 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 2 | 0.0833 |
| `text_phrase` | 50 | 36 | 0.7200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 31 | 0.7045 |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 170 | 0.7870 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 172 | 0.8731 |
| `4` | 21 | 14 | 0.6667 |
| `5` | 42 | 15 | 0.3571 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 3 | 0.1875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 10 | 0.2857 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 198 | 0.8426 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1667`
- regex_exact_rate: `0.2167`
- leading_zero_retention_rate: `0.2667`
- format_failure_rate: `0.8333`
- format_ok_content_wrong_rate: `0.2`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 1 | 0.0250 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
