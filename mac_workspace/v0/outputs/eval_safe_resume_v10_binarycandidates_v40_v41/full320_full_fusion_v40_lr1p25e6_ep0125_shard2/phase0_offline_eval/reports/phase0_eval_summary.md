# phase0_eval_overall

## Overall

- rows: `320`
- correct: `205`
- accuracy: `0.6406`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 9 | 0.1500 |
| `gravity` | 50 | 47 | 0.9400 |
| `roman` | 50 | 48 | 0.9600 |
| `symbol` | 60 | 12 | 0.2000 |
| `text` | 50 | 41 | 0.8200 |
| `unit` | 50 | 48 | 0.9600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 9 | 0.1957 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 47 | 0.9400 |
| `numeric_2x2` | 40 | 12 | 0.3000 |
| `roman_standard` | 50 | 48 | 0.9600 |
| `text_monoalphabetic` | 50 | 41 | 0.8200 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 9 | 0.1500 |
| `numeric` | 136 | 107 | 0.7868 |
| `roman` | 50 | 48 | 0.9600 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 41 | 0.8200 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 35 | 0.7955 |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 161 | 0.7454 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 179 | 0.9086 |
| `4` | 21 | 12 | 0.5714 |
| `5` | 42 | 5 | 0.1190 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 3 | 0.1875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 6 | 0.1714 |
| `manual_audit_priority` | 50 | 0 | 0.0000 |
| `verified_trace_ready` | 235 | 199 | 0.8468 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1667`
- regex_exact_rate: `0.1167`
- leading_zero_retention_rate: `0.1667`
- format_failure_rate: `0.9`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 1 | 0.0250 |
| `binary_affine_xor` | 20 | 8 | 0.4000 |
