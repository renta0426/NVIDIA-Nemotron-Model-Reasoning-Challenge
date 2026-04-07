# binary_hard_set

## Overall

- rows: `60`
- correct: `54`
- accuracy: `0.9000`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 54 | 0.9000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 40 | 0.8696 |
| `bit_structured_byte_formula` | 14 | 14 | 1.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 54 | 0.9000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 39 | 0.9750 |
| `500-599` | 20 | 15 | 0.7500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 15 | 0.7500 |
| `7` | 11 | 10 | 0.9091 |
| `8` | 13 | 13 | 1.0000 |
| `9` | 16 | 16 | 1.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 20 | 1.0000 |
| `manual_audit_priority` | 20 | 14 | 0.7000 |
| `verified_trace_ready` | 20 | 20 | 1.0000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.1`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 34 | 0.8500 |
| `binary_affine_xor` | 20 | 20 | 1.0000 |
