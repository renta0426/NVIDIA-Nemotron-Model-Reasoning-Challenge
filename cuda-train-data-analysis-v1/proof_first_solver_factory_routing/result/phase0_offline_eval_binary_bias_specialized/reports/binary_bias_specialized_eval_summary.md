# Binary Bias Specialized Eval Summary

- rows: `563`
- accuracy: `0.4156`
- starts_check_examples_rate: `0.0`
- contains_so_rule_rate: `1.0`
- contains_constraints_rate: `1.0`
- contains_boxed_literal_rate: `1.0`
- contains_oxed_literal_rate: `1.0`
- gold_anywhere_rate: `0.4156`
- last_bit8_exact_rate: `0.4156`
- mean_raw_output_chars: `369.0`
- mean_bit_fragment_count: `1.0`

## Focus Bucket Accuracy

| v1_focus_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boolean_family` | 60 | 36 | 0.6000 |
| `dominant_structured_abstract` | 90 | 32 | 0.3556 |
| `dominant_structured_safe` | 120 | 48 | 0.4000 |
| `no_solver_answer_only` | 70 | 26 | 0.3714 |
| `no_solver_manual` | 40 | 6 | 0.1500 |
| `rare_byte_transform` | 11 | 10 | 0.9091 |
| `rare_perm_independent` | 7 | 5 | 0.7143 |
| `supported_affine_xor` | 60 | 25 | 0.4167 |
| `supported_bijection` | 50 | 42 | 0.8400 |
| `supported_not_structured` | 55 | 4 | 0.0727 |

## Exposure Band Accuracy

| v1_exposure_band | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `dominant` | 210 | 80 | 0.3810 |
| `rare` | 18 | 15 | 0.8333 |
| `supported` | 225 | 107 | 0.4756 |
| `underrepresented` | 110 | 32 | 0.2909 |
