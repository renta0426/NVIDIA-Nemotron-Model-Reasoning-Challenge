# phase0_eval_overall

## Overall

- rows: `320`
- correct: `6`
- accuracy: `0.0187`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |
| `gravity` | 50 | 0 | 0.0000 |
| `roman` | 50 | 0 | 0.0000 |
| `symbol` | 60 | 1 | 0.0167 |
| `text` | 50 | 0 | 0.0000 |
| `unit` | 50 | 0 | 0.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 3 | 0.0652 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 0 | 0.0000 |
| `numeric_2x2` | 40 | 1 | 0.0250 |
| `roman_standard` | 50 | 0 | 0.0000 |
| `text_monoalphabetic` | 50 | 0 | 0.0000 |
| `unit_fixed_ratio` | 50 | 0 | 0.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |
| `numeric` | 136 | 1 | 0.0074 |
| `roman` | 50 | 0 | 0.0000 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 0 | 0.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 0 | 0.0000 |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 0 | 0.0000 |
| `<300` | 216 | 1 | 0.0046 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 0 | 0.0000 |
| `3` | 197 | 0 | 0.0000 |
| `4` | 21 | 1 | 0.0476 |
| `5` | 42 | 0 | 0.0000 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 4 | 0.1143 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 2 | 0.0085 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0`
- regex_exact_rate: `0.0`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `1.0`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 4 | 0.1000 |
| `binary_affine_xor` | 20 | 1 | 0.0500 |
