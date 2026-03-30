# phase0_eval_overall

## Overall

- rows: `320`
- correct: `225`
- accuracy: `0.7031`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 12 | 0.2000 |
| `gravity` | 50 | 46 | 0.9200 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 25 | 0.4167 |
| `text` | 50 | 45 | 0.9000 |
| `unit` | 50 | 48 | 0.9600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 10 | 0.2174 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 46 | 0.9200 |
| `numeric_2x2` | 40 | 25 | 0.6250 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 45 | 0.9000 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 12 | 0.2000 |
| `numeric` | 136 | 118 | 0.8676 |
| `roman` | 50 | 49 | 0.9800 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 45 | 0.9000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 39 | 0.8864 |
| `400-499` | 40 | 8 | 0.2000 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 174 | 0.8056 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 182 | 0.9239 |
| `4` | 21 | 17 | 0.8095 |
| `5` | 42 | 14 | 0.3333 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 3 | 0.1875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 13 | 0.3714 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 211 | 0.8979 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.2167`
- regex_exact_rate: `0.25`
- leading_zero_retention_rate: `0.2333`
- format_failure_rate: `0.7833`
- format_ok_content_wrong_rate: `0.1538`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 4 | 0.1000 |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
