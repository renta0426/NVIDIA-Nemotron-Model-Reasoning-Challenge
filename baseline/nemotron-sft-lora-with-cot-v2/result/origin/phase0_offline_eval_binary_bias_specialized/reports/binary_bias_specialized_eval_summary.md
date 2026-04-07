# Binary Bias Specialized Eval Summary

- rows: `563`
- accuracy: `0.3375`
- starts_check_examples_rate: `0.0`
- contains_so_rule_rate: `0.151`
- contains_constraints_rate: `0.0`
- contains_boxed_literal_rate: `0.8064`
- contains_oxed_literal_rate: `0.8064`
- gold_anywhere_rate: `0.5222`
- last_bit8_exact_rate: `0.341`
- mean_raw_output_chars: `12138.7`
- mean_bit_fragment_count: `72.85`

## Focus Bucket Accuracy

| v1_focus_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boolean_family` | 60 | 32 | 0.5333 |
| `dominant_structured_abstract` | 90 | 19 | 0.2111 |
| `dominant_structured_safe` | 120 | 35 | 0.2917 |
| `no_solver_answer_only` | 70 | 21 | 0.3000 |
| `no_solver_manual` | 40 | 4 | 0.1000 |
| `rare_byte_transform` | 11 | 11 | 1.0000 |
| `rare_perm_independent` | 7 | 2 | 0.2857 |
| `supported_affine_xor` | 60 | 18 | 0.3000 |
| `supported_bijection` | 50 | 45 | 0.9000 |
| `supported_not_structured` | 55 | 3 | 0.0545 |

## Exposure Band Accuracy

| v1_exposure_band | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `dominant` | 210 | 54 | 0.2571 |
| `rare` | 18 | 13 | 0.7222 |
| `supported` | 225 | 98 | 0.4356 |
| `underrepresented` | 110 | 25 | 0.2273 |
