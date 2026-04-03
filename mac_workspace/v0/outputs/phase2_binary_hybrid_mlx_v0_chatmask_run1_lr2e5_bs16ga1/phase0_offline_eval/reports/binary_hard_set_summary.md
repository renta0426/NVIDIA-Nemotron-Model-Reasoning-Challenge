# binary_hard_set

## Overall

- rows: `60`
- correct: `11`
- accuracy: `0.1833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 11 | 0.1833 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 8 | 0.1739 |
| `bit_structured_byte_formula` | 14 | 3 | 0.2143 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 11 | 0.1833 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 10 | 0.2500 |
| `500-599` | 20 | 1 | 0.0500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 1 | 0.0500 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 6 | 0.3750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 5 | 0.2500 |
| `manual_audit_priority` | 20 | 3 | 0.1500 |
| `verified_trace_ready` | 20 | 3 | 0.1500 |

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
