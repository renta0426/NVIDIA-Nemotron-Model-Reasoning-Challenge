# phase0_eval_overall

## Overall

- rows: `60`
- correct: `19`
- accuracy: `0.3167`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 19 | 0.3167 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 14 | 0.3043 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 19 | 0.3167 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 15 | 0.3750 |
| `500-599` | 20 | 4 | 0.2000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `7` | 11 | 3 | 0.2727 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 8 | 0.5000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 7 | 0.3500 |
| `manual_audit_priority` | 20 | 5 | 0.2500 |
| `verified_trace_ready` | 20 | 7 | 0.3500 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.8333`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.6833`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 12 | 0.3000 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
