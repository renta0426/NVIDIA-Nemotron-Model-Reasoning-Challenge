# phase0_eval_overall

## Overall

- rows: `60`
- correct: `5`
- accuracy: `0.0833`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 5 | 0.0833 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 5 | 0.1087 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 5 | 0.0833 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 3 | 0.0750 |
| `500-599` | 20 | 2 | 0.1000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 2 | 0.1000 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 2 | 0.1250 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 0 | 0.0000 |
| `manual_audit_priority` | 20 | 0 | 0.0000 |
| `verified_trace_ready` | 20 | 5 | 0.2500 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.1667`
- regex_exact_rate: `0.1833`
- leading_zero_retention_rate: `0.1333`
- format_failure_rate: `0.9167`
- format_ok_content_wrong_rate: `0.4`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 0 | 0.0000 |
| `binary_affine_xor` | 20 | 5 | 0.2500 |
