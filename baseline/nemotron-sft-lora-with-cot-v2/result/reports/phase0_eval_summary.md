# phase0_eval_overall

## Overall

- rows: `320`
- correct: `249`
- accuracy: `0.7781`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 29 | 0.4833 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 22 | 0.3667 |
| `text` | 50 | 49 | 0.9800 |
| `unit` | 50 | 49 | 0.9800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 24 | 0.5217 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 22 | 0.5500 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 49 | 0.9800 |
| `unit_fixed_ratio` | 50 | 49 | 0.9800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 29 | 0.4833 |
| `numeric` | 136 | 120 | 0.8824 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 49 | 0.9800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 43 | 0.9773 |
| `400-499` | 40 | 21 | 0.5250 |
| `500-599` | 20 | 8 | 0.4000 |
| `<300` | 216 | 177 | 0.8194 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 8 | 0.4000 |
| `3` | 197 | 191 | 0.9695 |
| `4` | 21 | 16 | 0.7619 |
| `5` | 42 | 13 | 0.3095 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 6 | 0.4615 |
| `9` | 16 | 11 | 0.6875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 16 | 0.4571 |
| `manual_audit_priority` | 50 | 7 | 0.1400 |
| `verified_trace_ready` | 235 | 226 | 0.9617 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.8333`
- regex_exact_rate: `0.8333`
- leading_zero_retention_rate: `0.8333`
- format_failure_rate: `0.1667`
- format_ok_content_wrong_rate: `0.44`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 15 | 0.3750 |
| `binary_affine_xor` | 20 | 14 | 0.7000 |
