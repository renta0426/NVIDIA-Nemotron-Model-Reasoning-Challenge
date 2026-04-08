# phase0_eval_overall

## Overall

- rows: `320`
- correct: `194`
- accuracy: `0.6062`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 18 | 0.3000 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 20 | 0.3333 |
| `text` | 50 | 9 | 0.1800 |
| `unit` | 50 | 48 | 0.9600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 12 | 0.2609 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 20 | 0.5000 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 9 | 0.1800 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 18 | 0.3000 |
| `numeric` | 136 | 117 | 0.8603 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 9 | 0.1800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 8 | 0.1818 |
| `400-499` | 40 | 15 | 0.3750 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 168 | 0.7778 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 156 | 0.7919 |
| `4` | 21 | 10 | 0.4762 |
| `5` | 42 | 10 | 0.2381 |
| `7` | 11 | 3 | 0.2727 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 8 | 0.5000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 15 | 0.4286 |
| `manual_audit_priority` | 50 | 5 | 0.1000 |
| `verified_trace_ready` | 235 | 174 | 0.7404 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.8667`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.7`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 13 | 0.3250 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
