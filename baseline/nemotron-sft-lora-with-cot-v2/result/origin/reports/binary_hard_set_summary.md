# binary_hard_set

## Overall

- rows: `60`
- correct: `29`
- accuracy: `0.4833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 29 | 0.4833 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 24 | 0.5217 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 29 | 0.4833 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 21 | 0.5250 |
| `500-599` | 20 | 8 | 0.4000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 8 | 0.4000 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 6 | 0.4615 |
| `9` | 16 | 11 | 0.6875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 8 | 0.4000 |
| `manual_audit_priority` | 20 | 7 | 0.3500 |
| `verified_trace_ready` | 20 | 14 | 0.7000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.8333`
- regex_exact_rate: `0.8333`
- leading_zero_retention_rate: `0.8333`
- format_failure_rate: `0.1667`
- format_ok_content_wrong_rate: `0.44`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 15 | 0.3750 |
| `binary_affine_xor` | 20 | 14 | 0.7000 |
