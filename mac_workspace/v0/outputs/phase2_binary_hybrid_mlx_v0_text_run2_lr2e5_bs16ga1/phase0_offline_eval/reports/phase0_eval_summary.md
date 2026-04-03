# phase0_eval_overall

## Overall

- rows: `320`
- correct: `151`
- accuracy: `0.4719`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 17 | 0.2833 |
| `gravity` | 50 | 9 | 0.1800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 25 | 0.4167 |
| `text` | 50 | 0 | 0.0000 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 13 | 0.2826 |
| `bit_structured_byte_formula` | 14 | 4 | 0.2857 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 9 | 0.1800 |
| `numeric_2x2` | 40 | 25 | 0.6250 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 0 | 0.0000 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 17 | 0.2833 |
| `numeric` | 136 | 83 | 0.6103 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 0 | 0.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 0 | 0.0000 |
| `400-499` | 40 | 13 | 0.3250 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 134 | 0.6204 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 113 | 0.5736 |
| `4` | 21 | 7 | 0.3333 |
| `5` | 42 | 14 | 0.3333 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 5 | 0.3846 |
| `9` | 16 | 6 | 0.3750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 17 | 0.4857 |
| `manual_audit_priority` | 50 | 4 | 0.0800 |
| `verified_trace_ready` | 235 | 130 | 0.5532 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.6667`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.7167`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 11 | 0.2750 |
| `binary_affine_xor` | 20 | 6 | 0.3000 |
