# phase0_eval_overall

## Overall

- rows: `320`
- correct: `187`
- accuracy: `0.5844`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 4 | 0.0667 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 48 | 0.9600 |
| `symbol` | 60 | 10 | 0.1667 |
| `text` | 50 | 32 | 0.6400 |
| `unit` | 50 | 44 | 0.8800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 4 | 0.0870 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 10 | 0.2500 |
| `roman_standard` | 50 | 48 | 0.9600 |
| `text_monoalphabetic` | 50 | 32 | 0.6400 |
| `unit_fixed_ratio` | 50 | 44 | 0.8800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 4 | 0.0667 |
| `numeric` | 136 | 103 | 0.7574 |
| `roman` | 50 | 48 | 0.9600 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 32 | 0.6400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 29 | 0.6591 |
| `400-499` | 40 | 2 | 0.0500 |
| `500-599` | 20 | 2 | 0.1000 |
| `<300` | 216 | 154 | 0.7130 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 2 | 0.1000 |
| `3` | 197 | 170 | 0.8629 |
| `4` | 21 | 11 | 0.5238 |
| `5` | 42 | 2 | 0.0476 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 0 | 0.0000 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 6 | 0.1714 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 181 | 0.7702 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1333`
- regex_exact_rate: `0.0833`
- leading_zero_retention_rate: `0.1333`
- format_failure_rate: `0.9667`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 0 | 0.0000 |
| `binary_affine_xor` | 20 | 4 | 0.2000 |
