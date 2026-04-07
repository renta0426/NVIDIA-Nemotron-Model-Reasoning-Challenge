# phase0_eval_overall

## Overall

- rows: `320`
- correct: `194`
- accuracy: `0.6062`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 47 | 0.9400 |
| `symbol` | 60 | 13 | 0.2167 |
| `text` | 50 | 35 | 0.7000 |
| `unit` | 50 | 45 | 0.9000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 5 | 0.1087 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 13 | 0.3250 |
| `roman_standard` | 50 | 47 | 0.9400 |
| `text_monoalphabetic` | 50 | 35 | 0.7000 |
| `unit_fixed_ratio` | 50 | 45 | 0.9000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |
| `numeric` | 136 | 107 | 0.7868 |
| `roman` | 50 | 47 | 0.9400 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 35 | 0.7000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 32 | 0.7273 |
| `400-499` | 40 | 3 | 0.0750 |
| `500-599` | 20 | 2 | 0.1000 |
| `<300` | 216 | 157 | 0.7269 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 2 | 0.1000 |
| `3` | 197 | 173 | 0.8782 |
| `4` | 21 | 11 | 0.5238 |
| `5` | 42 | 5 | 0.1190 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 5 | 0.1429 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 189 | 0.8043 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0833`
- regex_exact_rate: `0.2167`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.9333`
- format_ok_content_wrong_rate: `0.5`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 0 | 0.0000 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
