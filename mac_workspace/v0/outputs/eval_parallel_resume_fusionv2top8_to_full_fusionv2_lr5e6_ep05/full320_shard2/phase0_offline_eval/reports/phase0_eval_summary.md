# phase0_eval_overall

## Overall

- rows: `320`
- correct: `181`
- accuracy: `0.5656`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 8 | 0.1333 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 49 | 0.9800 |
| `symbol` | 60 | 21 | 0.3500 |
| `text` | 50 | 29 | 0.5800 |
| `unit` | 50 | 24 | 0.4800 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 7 | 0.1522 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 21 | 0.5250 |
| `roman_standard` | 50 | 49 | 0.9800 |
| `text_monoalphabetic` | 50 | 29 | 0.5800 |
| `unit_fixed_ratio` | 50 | 24 | 0.4800 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 8 | 0.1333 |
| `numeric` | 136 | 94 | 0.6912 |
| `roman` | 50 | 49 | 0.9800 |
| `symbolic` | 24 | 1 | 0.0417 |
| `text_phrase` | 50 | 29 | 0.5800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 26 | 0.5909 |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 3 | 0.1500 |
| `<300` | 216 | 147 | 0.6806 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `3` | 197 | 150 | 0.7614 |
| `4` | 21 | 12 | 0.5714 |
| `5` | 42 | 11 | 0.2619 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 3 | 0.1875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 9 | 0.2571 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 171 | 0.7277 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.05`
- regex_exact_rate: `0.2167`
- leading_zero_retention_rate: `0.1333`
- format_failure_rate: `0.95`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 2 | 0.0500 |
| `binary_affine_xor` | 20 | 6 | 0.3000 |
