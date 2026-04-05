# phase0_eval_overall

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
| `bit_other` | 46 | 6 | 0.1304 |
| `bit_structured_byte_formula` | 14 | 1 | 0.0714 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 7 | 0.1167 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 6 | 0.1500 |
| `500-599` | 20 | 1 | 0.0500 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 1 | 0.0500 |
| `7` | 11 | 2 | 0.1818 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 3 | 0.1875 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 3 | 0.1500 |
| `manual_audit_priority` | 20 | 1 | 0.0500 |
| `verified_trace_ready` | 20 | 3 | 0.1500 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1333`
- regex_exact_rate: `0.1667`
- leading_zero_retention_rate: `0.1`
- format_failure_rate: `0.9333`
- format_ok_content_wrong_rate: `0.5`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 4 | 0.1000 |
| `binary_affine_xor` | 20 | 3 | 0.1500 |
