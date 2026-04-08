# Binary Bias Specialized Eval Summary

- rows: `563`
- accuracy: `0.6181`
- starts_check_examples_rate: `0.0`
- contains_so_rule_rate: `1.0`
- contains_constraints_rate: `1.0`
- contains_boxed_literal_rate: `1.0`
- contains_oxed_literal_rate: `1.0`
- gold_anywhere_rate: `0.5471`
- last_bit8_exact_rate: `0.4867`
- mean_raw_output_chars: `625.0`
- mean_bit_fragment_count: `14.61`

## Focus Bucket Accuracy

| v1_focus_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boolean_family` | 60 | 47 | 0.7833 |
| `dominant_structured_abstract` | 90 | 53 | 0.5889 |
| `dominant_structured_safe` | 120 | 74 | 0.6167 |
| `no_solver_answer_only` | 70 | 40 | 0.5714 |
| `no_solver_manual` | 40 | 12 | 0.3000 |
| `rare_byte_transform` | 11 | 11 | 1.0000 |
| `rare_perm_independent` | 7 | 5 | 0.7143 |
| `supported_affine_xor` | 60 | 42 | 0.7000 |
| `supported_bijection` | 50 | 50 | 1.0000 |
| `supported_not_structured` | 55 | 14 | 0.2545 |

## Exposure Band Accuracy

| v1_exposure_band | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `dominant` | 210 | 127 | 0.6048 |
| `rare` | 18 | 16 | 0.8889 |
| `supported` | 225 | 153 | 0.6800 |
| `underrepresented` | 110 | 52 | 0.4727 |
