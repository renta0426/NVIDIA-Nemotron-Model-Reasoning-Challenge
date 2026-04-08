# phase0_eval_overall

## Overall

- rows: `320`
- correct: `249`
- accuracy: `0.7781`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 27 | 0.4500 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 24 | 0.4000 |
| `text` | 50 | 49 | 0.9800 |
| `unit` | 50 | 49 | 0.9800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 22 | 0.4783 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 24 | 0.6000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 49 | 0.9800 |
| `unit_fixed_ratio` | 50 | 49 | 0.9800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 27 | 0.4500 |
| `numeric` | 136 | 122 | 0.8971 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 49 | 0.9800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 43 | 0.9773 |
| `400-499` | 40 | 22 | 0.5500 |
| `500-599` | 20 | 5 | 0.2500 |
| `<300` | 216 | 179 | 0.8287 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 5 | 0.2500 |
| `3` | 197 | 192 | 0.9746 |
| `4` | 21 | 16 | 0.7619 |
| `5` | 42 | 14 | 0.3333 |
| `7` | 11 | 5 | 0.4545 |
| `8` | 13 | 7 | 0.5385 |
| `9` | 16 | 10 | 0.6250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 17 | 0.4857 |
| `manual_audit_priority` | 50 | 6 | 0.1200 |
| `verified_trace_ready` | 235 | 226 | 0.9617 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.8667`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.55`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 14 | 0.3500 |
| `binary_affine_xor` | 20 | 13 | 0.6500 |
