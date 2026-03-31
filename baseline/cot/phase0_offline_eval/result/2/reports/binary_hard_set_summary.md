# binary_hard_set

## Overall

- rows: `60`
- correct: `13`
- accuracy: `0.2167`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 13 | 0.2167 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 13 | 0.2826 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 13 | 0.2167 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 9 | 0.2250 |
| `500-599` | 20 | 4 | 0.2000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 4 | 0.3077 |
| `9` | 16 | 4 | 0.2500 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 2 | 0.1000 |
| `manual_audit_priority` | 20 | 4 | 0.2000 |
| `verified_trace_ready` | 20 | 7 | 0.3500 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.2`
- regex_exact_rate: `0.35`
- leading_zero_retention_rate: `0.4`
- format_failure_rate: `0.8`
- format_ok_content_wrong_rate: `0.25`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 6 | 0.1500 |
| `binary_affine_xor` | 20 | 7 | 0.3500 |
