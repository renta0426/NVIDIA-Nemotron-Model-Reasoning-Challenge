# Binary Bias Specialized Eval Summary

- rows: `563`
- accuracy: `0.3623`
- starts_check_examples_rate: `0.0`
- contains_so_rule_rate: `0.2078`
- contains_constraints_rate: `0.0018`
- contains_boxed_literal_rate: `0.8206`
- contains_oxed_literal_rate: `0.8206`
- gold_anywhere_rate: `0.5542`
- last_bit8_exact_rate: `0.3659`
- mean_raw_output_chars: `12000.9`
- mean_bit_fragment_count: `77.08`

## Focus Bucket Accuracy

| v1_focus_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boolean_family` | 60 | 33 | 0.5500 |
| `dominant_structured_abstract` | 90 | 22 | 0.2444 |
| `dominant_structured_safe` | 120 | 33 | 0.2750 |
| `no_solver_answer_only` | 70 | 27 | 0.3857 |
| `no_solver_manual` | 40 | 3 | 0.0750 |
| `rare_byte_transform` | 11 | 11 | 1.0000 |
| `rare_perm_independent` | 7 | 3 | 0.4286 |
| `supported_affine_xor` | 60 | 23 | 0.3833 |
| `supported_bijection` | 50 | 47 | 0.9400 |
| `supported_not_structured` | 55 | 2 | 0.0364 |

## Exposure Band Accuracy

| v1_exposure_band | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `dominant` | 210 | 55 | 0.2619 |
| `rare` | 18 | 14 | 0.7778 |
| `supported` | 225 | 105 | 0.4667 |
| `underrepresented` | 110 | 30 | 0.2727 |
