# binary_hard_set

## Overall

- rows: `60`
- correct: `33`
- accuracy: `0.5500`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 33 | 0.5500 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 26 | 0.5652 |
| `bit_structured_byte_formula` | 14 | 7 | 0.5000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 33 | 0.5500 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 25 | 0.6250 |
| `500-599` | 20 | 8 | 0.4000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 8 | 0.4000 |
| `7` | 11 | 4 | 0.3636 |
| `8` | 13 | 7 | 0.5385 |
| `9` | 16 | 14 | 0.8750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 10 | 0.5000 |
| `manual_audit_priority` | 20 | 7 | 0.3500 |
| `verified_trace_ready` | 20 | 16 | 0.8000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.45`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 17 | 0.4250 |
| `binary_affine_xor` | 20 | 16 | 0.8000 |
