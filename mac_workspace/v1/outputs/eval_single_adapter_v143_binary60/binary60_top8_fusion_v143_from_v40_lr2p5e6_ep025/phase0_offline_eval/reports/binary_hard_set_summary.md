# binary_hard_set

## Overall

- rows: `60`
- correct: `6`
- accuracy: `0.1000`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 6 | 0.1000 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 5 | 0.1087 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 6 | 0.1000 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 4 | 0.1000 |
| `500-599` | 20 | 2 | 0.1000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 2 | 0.1000 |
| `7` | 11 | 1 | 0.0909 |
| `8` | 13 | 3 | 0.2308 |
| `9` | 16 | 0 | 0.0000 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 1 | 0.0500 |
| `manual_audit_priority` | 20 | 1 | 0.0500 |
| `verified_trace_ready` | 20 | 4 | 0.2000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0833`
- regex_exact_rate: `0.1667`
- leading_zero_retention_rate: `0.0667`
- format_failure_rate: `0.95`
- format_ok_content_wrong_rate: `0.0`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 2 | 0.0500 |
| `binary_affine_xor` | 20 | 4 | 0.2000 |
