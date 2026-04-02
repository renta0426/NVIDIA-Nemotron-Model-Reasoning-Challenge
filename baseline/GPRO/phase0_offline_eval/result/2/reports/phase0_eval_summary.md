# phase0_eval_overall

## Overall

- rows: `320`
- correct: `224`
- accuracy: `0.7000`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 14 | 0.2333 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 23 | 0.3833 |
| `text` | 50 | 45 | 0.9000 |
| `unit` | 50 | 43 | 0.8600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 14 | 0.3043 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 23 | 0.5750 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 45 | 0.9000 |
| `unit_fixed_ratio` | 50 | 43 | 0.8600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 14 | 0.2333 |
| `numeric` | 136 | 114 | 0.8382 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 45 | 0.9000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 40 | 0.9091 |
| `400-499` | 40 | 10 | 0.2500 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 170 | 0.7870 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 180 | 0.9137 |
| `4` | 21 | 17 | 0.8095 |
| `5` | 42 | 13 | 0.3095 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 5 | 0.3125 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 10 | 0.2857 |
| `manual_audit_priority` | 50 | 3 | 0.0600 |
| `verified_trace_ready` | 235 | 211 | 0.8979 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.2333`
- regex_exact_rate: `0.35`
- leading_zero_retention_rate: `0.3`
- format_failure_rate: `0.7667`
- format_ok_content_wrong_rate: `0.2143`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 4 | 0.1000 |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
