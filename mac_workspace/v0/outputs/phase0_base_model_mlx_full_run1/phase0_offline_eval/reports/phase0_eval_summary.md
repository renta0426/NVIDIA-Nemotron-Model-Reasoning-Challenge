# phase0_eval_overall

## Overall

- rows: `320`
- correct: `171`
- accuracy: `0.5344`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 9 | 0.1500 |
| `gravity` | 50 | 29 | 0.5800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 20 | 0.3333 |
| `text` | 50 | 33 | 0.6600 |
| `unit` | 50 | 30 | 0.6000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 8 | 0.1739 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 29 | 0.5800 |
| `numeric_2x2` | 40 | 20 | 0.5000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 33 | 0.6600 |
| `unit_fixed_ratio` | 50 | 30 | 0.6000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 9 | 0.1500 |
| `numeric` | 136 | 79 | 0.5809 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 33 | 0.6600 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 28 | 0.6364 |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 134 | 0.6204 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 137 | 0.6954 |
| `4` | 21 | 14 | 0.6667 |
| `5` | 42 | 11 | 0.2619 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 8 | 0.2286 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 162 | 0.6894 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1167`
- regex_exact_rate: `0.2167`
- leading_zero_retention_rate: `0.2667`
- format_failure_rate: `0.8833`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 2 | 0.0500 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
