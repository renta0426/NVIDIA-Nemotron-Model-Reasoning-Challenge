# phase0_eval_overall

## Overall

- rows: `60`
- correct: `4`
- accuracy: `0.0667`

## Family accuracy

| family_short | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 60 | 4 | 0.0667 |

## Template subtype accuracy

| template_subtype | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `bit_other` | 46 | 4 | 0.0870 |
| `bit_structured_byte_formula` | 14 | 0 | 0.0000 |

## Answer type accuracy

| answer_type | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `binary8` | 60 | 4 | 0.0667 |

## Prompt length buckets

| prompt_len_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `400-499` | 40 | 2 | 0.0500 |
| `500-599` | 20 | 2 | 0.1000 |

## Num examples

| num_examples | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `10` | 20 | 2 | 0.1000 |
| `7` | 11 | 0 | 0.0000 |
| `8` | 13 | 1 | 0.0769 |
| `9` | 16 | 1 | 0.0625 |

## Selection tier accuracy

| selection_tier | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `answer_only_keep` | 20 | 0 | 0.0000 |
| `manual_audit_priority` | 20 | 0 | 0.0000 |
| `verified_trace_ready` | 20 | 4 | 0.2000 |

## Binary metrics

- rows: `60`
- boxed_extraction_success_rate: `0.0833`
- regex_exact_rate: `0.1833`
- leading_zero_retention_rate: `0.1667`
- format_failure_rate: `0.9333`
- format_ok_content_wrong_rate: `0.25`

### Binary solver-family accuracy

| teacher_solver_candidate | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `` | 40 | 0 | 0.0000 |
| `binary_affine_xor` | 20 | 4 | 0.2000 |
