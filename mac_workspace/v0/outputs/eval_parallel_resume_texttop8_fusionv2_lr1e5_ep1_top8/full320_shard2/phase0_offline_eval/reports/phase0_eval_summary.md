# phase0_eval_overall

## Overall

- rows: `320`
- correct: `189`
- accuracy: `0.5906`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 48 | 0.9600 |
| `symbol` | 60 | 11 | 0.1833 |
| `text` | 50 | 33 | 0.6600 |
| `unit` | 50 | 43 | 0.8600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 4 | 0.0870 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 11 | 0.2750 |
| `roman_standard` | 50 | 48 | 0.9600 |
| `text_monoalphabetic` | 50 | 33 | 0.6600 |
| `unit_fixed_ratio` | 50 | 43 | 0.8600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |
| `numeric` | 136 | 103 | 0.7574 |
| `roman` | 50 | 48 | 0.9600 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 33 | 0.6600 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 28 | 0.6364 |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 0 | 0.0000 |
| `<300` | 216 | 156 | 0.7222 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 0 | 0.0000 |
| `3` | 197 | 170 | 0.8629 |
| `4` | 21 | 8 | 0.3810 |
| `5` | 42 | 6 | 0.1429 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 5 | 0.1429 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 183 | 0.7787 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1`
- regex_exact_rate: `0.1833`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.9667`
- format_ok_content_wrong_rate: `0.5`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 3 | 0.0750 |
| `binary_affine_xor` | 20 | 2 | 0.1000 |
