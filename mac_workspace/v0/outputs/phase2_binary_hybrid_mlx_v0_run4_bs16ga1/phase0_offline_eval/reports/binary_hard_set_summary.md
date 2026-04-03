# binary_hard_set

## Overall

- rows: `60`
- correct: `5`
- accuracy: `0.0833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 3 | 0.0652 |
| `bit_structured_byte_formula` | 14 | 2 | 0.1429 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 5 | 0.1250 |
| `500-599` | 20 | 0 | 0.0000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 0 | 0.0000 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 4 | 0.2000 |
| `manual_audit_priority` | 20 | 0 | 0.0000 |
| `verified_trace_ready` | 20 | 1 | 0.0500 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0`
- regex_exact_rate: `0.0`
- leading_zero_retention_rate: `0.0`
- format_failure_rate: `1.0`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 4 | 0.1000 |
| `binary_affine_xor` | 20 | 1 | 0.0500 |
