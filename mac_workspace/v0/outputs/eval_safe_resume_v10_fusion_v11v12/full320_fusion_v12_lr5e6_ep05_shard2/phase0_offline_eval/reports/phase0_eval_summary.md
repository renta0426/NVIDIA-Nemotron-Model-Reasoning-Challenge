# phase0_eval_overall

## Overall

- rows: `320`
- correct: `189`
- accuracy: `0.5906`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 6 | 0.1000 |
| `gravity` | 50 | 47 | 0.9400 |
| `roman` | 50 | 46 | 0.9200 |
| `symbol` | 60 | 9 | 0.1500 |
| `text` | 50 | 31 | 0.6200 |
| `unit` | 50 | 50 | 1.0000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 4 | 0.0870 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 47 | 0.9400 |
| `numeric_2x2` | 40 | 9 | 0.2250 |
| `roman_standard` | 50 | 46 | 0.9200 |
| `text_monoalphabetic` | 50 | 31 | 0.6200 |
| `unit_fixed_ratio` | 50 | 50 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 6 | 0.1000 |
| `numeric` | 136 | 106 | 0.7794 |
| `roman` | 50 | 46 | 0.9200 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 31 | 0.6200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 25 | 0.5682 |
| `400-499` | 40 | 4 | 0.1000 |
| `500-599` | 20 | 2 | 0.1000 |
| `<300` | 216 | 158 | 0.7315 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 2 | 0.1000 |
| `3` | 197 | 171 | 0.8680 |
| `4` | 21 | 10 | 0.4762 |
| `5` | 42 | 2 | 0.0476 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 6 | 0.1714 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 183 | 0.7787 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1167`
- regex_exact_rate: `0.3`
- leading_zero_retention_rate: `0.2333`
- format_failure_rate: `0.9167`
- format_ok_content_wrong_rate: `0.2`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 2 | 0.0500 |
| `binary_affine_xor` | 20 | 4 | 0.2000 |
