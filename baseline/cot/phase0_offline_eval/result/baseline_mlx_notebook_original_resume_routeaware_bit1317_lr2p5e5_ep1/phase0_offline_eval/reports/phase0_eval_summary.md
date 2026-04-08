# phase0_eval_overall

## Overall

- rows: `320`
- correct: `142`
- accuracy: `0.4437`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 27 | 0.4500 |
| `gravity` | 50 | 17 | 0.3400 |
| `roman` | 50 | 40 | 0.8000 |
| `symbol` | 60 | 7 | 0.1167 |
| `text` | 50 | 7 | 0.1400 |
| `unit` | 50 | 44 | 0.8800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 21 | 0.4565 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 17 | 0.3400 |
| `numeric_2x2` | 40 | 7 | 0.1750 |
| `roman_standard` | 50 | 40 | 0.8000 |
| `text_monoalphabetic` | 50 | 7 | 0.1400 |
| `unit_fixed_ratio` | 50 | 44 | 0.8800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 27 | 0.4500 |
| `numeric` | 136 | 68 | 0.5000 |
| `roman` | 50 | 40 | 0.8000 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 7 | 0.1400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 7 | 0.1591 |
| `400-499` | 40 | 20 | 0.5000 |
| `500-599` | 20 | 7 | 0.3500 |
| `<300` | 216 | 108 | 0.5000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 7 | 0.3500 |
| `3` | 197 | 108 | 0.5482 |
| `4` | 21 | 2 | 0.0952 |
| `5` | 42 | 5 | 0.1190 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 5 | 0.3846 |
| `9` | 16 | 11 | 0.6875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 10 | 0.2857 |
| `manual_audit_priority` | 50 | 6 | 0.1200 |
| `verified_trace_ready` | 235 | 126 | 0.5362 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.55`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 14 | 0.3500 |
| `binary_affine_xor` | 20 | 13 | 0.6500 |
