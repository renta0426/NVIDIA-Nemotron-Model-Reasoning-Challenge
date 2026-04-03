# phase0_eval_overall

## Overall

- rows: `320`
- correct: `193`
- accuracy: `0.6031`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |
| `gravity` | 50 | 48 | 0.9600 |
| `roman` | 50 | 48 | 0.9600 |
| `symbol` | 60 | 13 | 0.2167 |
| `text` | 50 | 35 | 0.7000 |
| `unit` | 50 | 44 | 0.8800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 5 | 0.1087 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 48 | 0.9600 |
| `numeric_2x2` | 40 | 13 | 0.3250 |
| `roman_standard` | 50 | 48 | 0.9600 |
| `text_monoalphabetic` | 50 | 35 | 0.7000 |
| `unit_fixed_ratio` | 50 | 44 | 0.8800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |
| `numeric` | 136 | 105 | 0.7721 |
| `roman` | 50 | 48 | 0.9600 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 35 | 0.7000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 29 | 0.6591 |
| `400-499` | 40 | 2 | 0.0500 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 159 | 0.7361 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 173 | 0.8782 |
| `4` | 21 | 11 | 0.5238 |
| `5` | 42 | 4 | 0.0952 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 8 | 0.2286 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 185 | 0.7872 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1167`
- regex_exact_rate: `0.25`
- leading_zero_retention_rate: `0.1667`
- format_failure_rate: `0.9333`
- format_ok_content_wrong_rate: `0.25`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 0 | 0.0000 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
