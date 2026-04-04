# phase0_eval_overall

## Overall

- rows: `320`
- correct: `189`
- accuracy: `0.5906`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 27 | 0.4500 |
| `gravity` | 50 | 42 | 0.8400 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 17 | 0.2833 |
| `text` | 50 | 21 | 0.4200 |
| `unit` | 50 | 32 | 0.6400 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 21 | 0.4565 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 42 | 0.8400 |
| `numeric_2x2` | 40 | 17 | 0.4250 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 21 | 0.4200 |
| `unit_fixed_ratio` | 50 | 32 | 0.6400 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 27 | 0.4500 |
| `numeric` | 136 | 90 | 0.6618 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 21 | 0.4200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 20 | 0.4545 |
| `400-499` | 40 | 19 | 0.4750 |
| `500-599` | 20 | 8 | 0.4000 |
| `<300` | 216 | 142 | 0.6574 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 8 | 0.4000 |
| `3` | 197 | 142 | 0.7208 |
| `4` | 21 | 10 | 0.4762 |
| `5` | 42 | 10 | 0.2381 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 5 | 0.3846 |
| `9` | 16 | 10 | 0.6250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 14 | 0.4000 |
| `manual_audit_priority` | 50 | 6 | 0.1200 |
| `verified_trace_ready` | 235 | 169 | 0.7191 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.8`
- format_failure_rate: `1.0`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 15 | 0.3750 |
| `binary_affine_xor` | 20 | 12 | 0.6000 |
