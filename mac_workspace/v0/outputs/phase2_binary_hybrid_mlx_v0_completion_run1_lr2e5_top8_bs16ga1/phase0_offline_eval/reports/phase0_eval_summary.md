# phase0_eval_overall

## Overall

- rows: `320`
- correct: `97`
- accuracy: `0.3031`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |
| `gravity` | 50 | 31 | 0.6200 |
| `roman` | 50 | 21 | 0.4200 |
| `symbol` | 60 | 11 | 0.1833 |
| `text` | 50 | 4 | 0.0800 |
| `unit` | 50 | 25 | 0.5000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 4 | 0.0870 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 31 | 0.6200 |
| `numeric_2x2` | 40 | 11 | 0.2750 |
| `roman_standard` | 50 | 21 | 0.4200 |
| `text_monoalphabetic` | 50 | 4 | 0.0800 |
| `unit_fixed_ratio` | 50 | 25 | 0.5000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |
| `numeric` | 136 | 67 | 0.4926 |
| `roman` | 50 | 21 | 0.4200 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 4 | 0.0800 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 4 | 0.0909 |
| `400-499` | 40 | 4 | 0.1000 |
| `500-599` | 20 | 1 | 0.0500 |
| `<300` | 216 | 88 | 0.4074 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 1 | 0.0500 |
| `3` | 197 | 82 | 0.4162 |
| `4` | 21 | 6 | 0.2857 |
| `5` | 42 | 4 | 0.0952 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 6 | 0.1714 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 91 | 0.3872 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0`
- regex_exact_rate: `0.1167`
- leading_zero_retention_rate: `0.1`
- format_failure_rate: `1.0`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 2 | 0.0500 |
| `binary_affine_xor` | 20 | 3 | 0.1500 |
