# binary_hard_set

## Overall

- rows: `60`
- correct: `7`
- accuracy: `0.1167`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 7 | 0.1167 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 7 | 0.1522 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 7 | 0.1167 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 4 | 0.1000 |
| `500-599` | 20 | 3 | 0.1500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 3 | 0.1500 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 2 | 0.1538 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 0 | 0.0000 |
| `manual_audit_priority` | 20 | 1 | 0.0500 |
| `verified_trace_ready` | 20 | 6 | 0.3000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1833`
- regex_exact_rate: `0.2`
- leading_zero_retention_rate: `0.2`
- format_failure_rate: `0.8667`
- format_ok_content_wrong_rate: `0.25`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 1 | 0.0250 |
| `binary_affine_xor` | 20 | 6 | 0.3000 |
