# binary_hard_set

## Overall

- rows: `60`
- correct: `15`
- accuracy: `0.2500`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 15 | 0.2500 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 10 | 0.2174 |
| `bit_structured_byte_formula` | 14 | 5 | 0.3571 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 15 | 0.2500 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 12 | 0.3000 |
| `500-599` | 20 | 3 | 0.1500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 3 | 0.2308 |
| `9` | 16 | 8 | 0.5000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 6 | 0.3000 |
| `manual_audit_priority` | 20 | 4 | 0.2000 |
| `verified_trace_ready` | 20 | 5 | 0.2500 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.9333`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.75`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 10 | 0.2500 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
