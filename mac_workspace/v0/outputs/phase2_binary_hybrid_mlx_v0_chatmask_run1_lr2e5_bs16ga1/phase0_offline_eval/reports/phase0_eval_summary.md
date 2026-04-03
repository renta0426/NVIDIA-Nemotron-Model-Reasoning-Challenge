# phase0_eval_overall

## Overall

- rows: `320`
- correct: `60`
- accuracy: `0.1875`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 11 | 0.1833 |
| `gravity` | 50 | 3 | 0.0600 |
| `roman` | 50 | 1 | 0.0200 |
| `symbol` | 60 | 12 | 0.2000 |
| `text` | 50 | 0 | 0.0000 |
| `unit` | 50 | 33 | 0.6600 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 8 | 0.1739 |
| `bit_structured_byte_formula` | 14 | 3 | 0.2143 |
| `glyph_len5` | 20 | 0 | 0.0000 |
| `gravity_half_g_t2` | 50 | 3 | 0.0600 |
| `numeric_2x2` | 40 | 12 | 0.3000 |
| `roman_standard` | 50 | 1 | 0.0200 |
| `text_monoalphabetic` | 50 | 0 | 0.0000 |
| `unit_fixed_ratio` | 50 | 33 | 0.6600 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 11 | 0.1833 |
| `numeric` | 136 | 48 | 0.3529 |
| `roman` | 50 | 1 | 0.0200 |
| `symbolic` | 24 | 0 | 0.0000 |
| `text_phrase` | 50 | 0 | 0.0000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `300-399` | 44 | 0 | 0.0000 |
| `400-499` | 40 | 10 | 0.2500 |
| `500-599` | 20 | 1 | 0.0500 |
| `<300` | 216 | 49 | 0.2269 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 1 | 0.0500 |
| `3` | 197 | 40 | 0.2030 |
| `4` | 21 | 6 | 0.2857 |
| `5` | 42 | 3 | 0.0714 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 6 | 0.3750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 35 | 12 | 0.3429 |
| `manual_audit_priority` | 50 | 3 | 0.0600 |
| `verified_trace_ready` | 235 | 45 | 0.1915 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.9167`
- regex_exact_rate: `0.3`
- leading_zero_retention_rate: `0.3`
- format_failure_rate: `0.7`
- format_ok_content_wrong_rate: `0.3889`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 8 | 0.2000 |
| `binary_affine_xor` | 20 | 3 | 0.1500 |
