# binary_hard_set

## Overall

- rows: `60`
- correct: `8`
- accuracy: `0.1333`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 8 | 0.1333 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 7 | 0.1522 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 8 | 0.1333 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 4 | 0.1000 |
| `500-599` | 20 | 4 | 0.2000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 2 | 0.1000 |
| `manual_audit_priority` | 20 | 1 | 0.0500 |
| `verified_trace_ready` | 20 | 5 | 0.2500 |

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
