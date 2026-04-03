# phase0_eval_overall

## Overall

- rows: `320`
- correct: `188`
- accuracy: `0.5875`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 7 | 0.1167 |
| `gravity` | 50 | 50 | 1.0000 |
| `roman` | 50 | 47 | 0.9400 |
| `symbol` | 60 | 9 | 0.1500 |
| `text` | 50 | 28 | 0.5600 |
| `unit` | 50 | 47 | 0.9400 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 6 | 0.1304 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 50 | 1.0000 |
| `numeric_2x2` | 40 | 9 | 0.2250 |
| `roman_standard` | 50 | 47 | 0.9400 |
| `text_monoalphabetic` | 50 | 28 | 0.5600 |
| `unit_fixed_ratio` | 50 | 47 | 0.9400 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 7 | 0.1167 |
| `numeric` | 136 | 106 | 0.7794 |
| `roman` | 50 | 47 | 0.9400 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 28 | 0.5600 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 25 | 0.5682 |
| `400-499` | 40 | 6 | 0.1500 |
| `500-599` | 20 | 1 | 0.0500 |
| `<300` | 216 | 156 | 0.7222 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 1 | 0.0500 |
| `3` | 197 | 167 | 0.8477 |
| `4` | 21 | 8 | 0.3810 |
| `5` | 42 | 6 | 0.1429 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 4 | 0.1143 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 183 | 0.7787 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1333`
- regex_exact_rate: `0.1167`
- leading_zero_retention_rate: `0.1`
- format_failure_rate: `0.9667`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 4 | 0.1000 |
| `binary_affine_xor` | 20 | 3 | 0.1500 |
