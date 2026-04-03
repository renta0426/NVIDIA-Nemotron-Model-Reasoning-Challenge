# binary_hard_set

## Overall

- rows: `60`
- correct: `17`
- accuracy: `0.2833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 17 | 0.2833 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 13 | 0.2826 |
| `bit_structured_byte_formula` | 14 | 4 | 0.2857 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 17 | 0.2833 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 13 | 0.3250 |
| `500-599` | 20 | 4 | 0.2000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 4 | 0.2000 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 5 | 0.3846 |
| `9` | 16 | 6 | 0.3750 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 7 | 0.3500 |
| `manual_audit_priority` | 20 | 4 | 0.2000 |
| `verified_trace_ready` | 20 | 6 | 0.3000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `1.0`
- regex_exact_rate: `1.0`
- leading_zero_retention_rate: `0.6667`
- format_failure_rate: `0.0`
- format_ok_content_wrong_rate: `0.7167`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 11 | 0.2750 |
| `binary_affine_xor` | 20 | 6 | 0.3000 |
