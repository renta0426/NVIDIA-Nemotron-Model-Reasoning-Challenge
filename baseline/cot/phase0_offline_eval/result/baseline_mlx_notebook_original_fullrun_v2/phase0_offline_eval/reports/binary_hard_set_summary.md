# binary_hard_set

## Overall

- rows: `60`
- correct: `26`
- accuracy: `0.4333`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 26 | 0.4333 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 19 | 0.4130 |
| `bit_structured_byte_formula` | 14 | 7 | 0.5000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 26 | 0.4333 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 21 | 0.5250 |
| `500-599` | 20 | 5 | 0.2500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 5 | 0.2500 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 6 | 0.4615 |
| `9` | 16 | 11 | 0.6875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 9 | 0.4500 |
| `manual_audit_priority` | 20 | 7 | 0.3500 |
| `verified_trace_ready` | 20 | 10 | 0.5000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.5667`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 16 | 0.4000 |
| `binary_affine_xor` | 20 | 10 | 0.5000 |
