# phase0_eval_overall

## Overall

- rows: `320`
- correct: `181`
- accuracy: `0.5656`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 6 | 0.1000 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 13 | 0.2167 |
| `text` | 50 | 17 | 0.3400 |
| `unit` | 50 | 45 | 0.9000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 5 | 0.1087 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 13 | 0.3250 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 17 | 0.3400 |
| `unit_fixed_ratio` | 50 | 45 | 0.9000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 6 | 0.1000 |
| `numeric` | 136 | 108 | 0.7941 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 17 | 0.3400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 15 | 0.3409 |
| `400-499` | 40 | 3 | 0.0750 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 160 | 0.7407 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 161 | 0.8173 |
| `4` | 21 | 10 | 0.4762 |
| `5` | 42 | 4 | 0.0952 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 6 | 0.1714 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 174 | 0.7404 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1`
- regex_exact_rate: `0.2333`
- leading_zero_retention_rate: `0.1`
- format_failure_rate: `0.9667`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 2 | 0.0500 |
| `binary_affine_xor` | 20 | 4 | 0.2000 |
