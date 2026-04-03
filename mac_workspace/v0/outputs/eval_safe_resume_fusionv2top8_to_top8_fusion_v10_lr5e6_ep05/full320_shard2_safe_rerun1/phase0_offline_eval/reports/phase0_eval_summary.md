# phase0_eval_overall

## Overall

- rows: `320`
- correct: `200`
- accuracy: `0.6250`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 8 | 0.1333 |
| `gravity` | 50 | 49 | 0.9800 |
| `roman` | 50 | 48 | 0.9600 |
| `symbol` | 60 | 10 | 0.1667 |
| `text` | 50 | 37 | 0.7400 |
| `unit` | 50 | 48 | 0.9600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 7 | 0.1522 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 49 | 0.9800 |
| `numeric_2x2` | 40 | 10 | 0.2500 |
| `roman_standard` | 50 | 48 | 0.9600 |
| `text_monoalphabetic` | 50 | 37 | 0.7400 |
| `unit_fixed_ratio` | 50 | 48 | 0.9600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 8 | 0.1333 |
| `numeric` | 136 | 107 | 0.7868 |
| `roman` | 50 | 48 | 0.9600 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 37 | 0.7400 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 31 | 0.7045 |
| `400-499` | 40 | 4 | 0.1000 |
| `500-599` | 20 | 4 | 0.2000 |
| `<300` | 216 | 161 | 0.7454 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `3` | 197 | 176 | 0.8934 |
| `4` | 21 | 11 | 0.5238 |
| `5` | 42 | 5 | 0.1190 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 4 | 0.1143 |
| `manual_audit_priority` | 50 | 1 | 0.0200 |
| `verified_trace_ready` | 235 | 195 | 0.8298 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1667`
- regex_exact_rate: `0.2`
- leading_zero_retention_rate: `0.2333`
- format_failure_rate: `0.9`
- format_ok_content_wrong_rate: `0.3333`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 3 | 0.0750 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
