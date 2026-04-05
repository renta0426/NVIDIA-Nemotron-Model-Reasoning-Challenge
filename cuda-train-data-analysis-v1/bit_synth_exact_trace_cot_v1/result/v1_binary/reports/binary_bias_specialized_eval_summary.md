# Binary Bias Specialized Eval Summary

- rows: `563`
- accuracy: `0.3925`
- starts_check_examples_rate: `1.0`
- contains_so_rule_rate: `1.0`
- contains_constraints_rate: `1.0`
- contains_boxed_literal_rate: `0.0`
- contains_oxed_literal_rate: `1.0`
- gold_anywhere_rate: `0.5524`
- last_bit8_exact_rate: `0.3925`
- mean_raw_output_chars: `510.2`
- mean_bit_fragment_count: `12.05`

## Focus Bucket Accuracy

| v1_focus_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boolean_family` | 60 | 30 | 0.5000 |
| `dominant_structured_abstract` | 90 | 33 | 0.3667 |
| `dominant_structured_safe` | 120 | 48 | 0.4000 |
| `no_solver_answer_only` | 70 | 18 | 0.2571 |
| `no_solver_manual` | 40 | 3 | 0.0750 |
| `rare_byte_transform` | 11 | 11 | 1.0000 |
| `rare_perm_independent` | 7 | 3 | 0.4286 |
| `supported_affine_xor` | 60 | 29 | 0.4833 |
| `supported_bijection` | 50 | 44 | 0.8800 |
| `supported_not_structured` | 55 | 2 | 0.0364 |

## Exposure Band Accuracy

| v1_exposure_band | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `dominant` | 210 | 81 | 0.3857 |
| `rare` | 18 | 14 | 0.7778 |
| `supported` | 225 | 105 | 0.4667 |
| `underrepresented` | 110 | 21 | 0.1909 |
