# Binary Bias Specialized Eval Summary

- rows: `563`
- accuracy: `0.508`
- starts_check_examples_rate: `0.0`
- contains_so_rule_rate: `0.0`
- contains_constraints_rate: `0.0`
- contains_boxed_literal_rate: `1.0`
- contains_oxed_literal_rate: `1.0`
- gold_anywhere_rate: `0.3588`
- last_bit8_exact_rate: `0.3588`
- mean_raw_output_chars: `25.0`
- mean_bit_fragment_count: `1.0`

## Focus Bucket Accuracy

| v1_focus_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boolean_family` | 60 | 47 | 0.7833 |
| `dominant_structured_abstract` | 90 | 41 | 0.4556 |
| `dominant_structured_safe` | 120 | 64 | 0.5333 |
| `no_solver_answer_only` | 70 | 31 | 0.4429 |
| `no_solver_manual` | 40 | 12 | 0.3000 |
| `rare_byte_transform` | 11 | 9 | 0.8182 |
| `rare_perm_independent` | 7 | 3 | 0.4286 |
| `supported_affine_xor` | 60 | 31 | 0.5167 |
| `supported_bijection` | 50 | 33 | 0.6600 |
| `supported_not_structured` | 55 | 15 | 0.2727 |

## Exposure Band Accuracy

| v1_exposure_band | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `dominant` | 210 | 105 | 0.5000 |
| `rare` | 18 | 12 | 0.6667 |
| `supported` | 225 | 126 | 0.5600 |
| `underrepresented` | 110 | 43 | 0.3909 |
