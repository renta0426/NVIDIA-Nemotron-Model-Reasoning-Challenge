# phase0_eval_overall

## Overall

- rows: `320`
- correct: `193`
- accuracy: `0.6031`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 10 | 0.1667 |
| `gravity` | 50 | 35 | 0.7000 |
| `roman` | 50 | 50 | 1.0000 |
| `symbol` | 60 | 25 | 0.4167 |
| `text` | 50 | 39 | 0.7800 |
| `unit` | 50 | 34 | 0.6800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 10 | 0.2174 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 35 | 0.7000 |
| `numeric_2x2` | 40 | 25 | 0.6250 |
| `roman_standard` | 50 | 50 | 1.0000 |
| `text_monoalphabetic` | 50 | 39 | 0.7800 |
| `unit_fixed_ratio` | 50 | 34 | 0.6800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 10 | 0.1667 |
| `numeric` | 136 | 93 | 0.6838 |
| `roman` | 50 | 50 | 1.0000 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 39 | 0.7800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 33 | 0.7500 |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 5 | 0.2500 |
| `<300` | 216 | 150 | 0.6944 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 5 | 0.2500 |
| `3` | 197 | 154 | 0.7817 |
| `4` | 21 | 16 | 0.7619 |
| `5` | 42 | 13 | 0.3095 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 3 | 0.2308 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 12 | 0.3429 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 180 | 0.7660 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1833`
- regex_exact_rate: `0.3167`
- leading_zero_retention_rate: `0.3333`
- format_failure_rate: `0.8167`
- format_ok_content_wrong_rate: `0.2727`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 3 | 0.0750 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
