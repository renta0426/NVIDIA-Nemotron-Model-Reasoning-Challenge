# binary_hard_set

## Overall

- rows: `60`
- correct: `27`
- accuracy: `0.4500`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 27 | 0.4500 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 21 | 0.4565 |
| `bit_structured_byte_formula` | 14 | 6 | 0.4286 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 27 | 0.4500 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 20 | 0.5000 |
| `500-599` | 20 | 7 | 0.3500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 7 | 0.3500 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 5 | 0.3846 |
| `9` | 16 | 11 | 0.6875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 8 | 0.4000 |
| `manual_audit_priority` | 20 | 6 | 0.3000 |
| `verified_trace_ready` | 20 | 13 | 0.6500 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.55`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 14 | 0.3500 |
| `binary_affine_xor` | 20 | 13 | 0.6500 |
