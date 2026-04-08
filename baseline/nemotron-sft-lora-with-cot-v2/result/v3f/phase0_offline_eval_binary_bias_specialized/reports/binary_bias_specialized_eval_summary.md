# Binary Bias Specialized Eval Summary

- rows: `563`
- accuracy: `0.4227`
- starts_check_examples_rate: `0.0`
- contains_so_rule_rate: `0.0`
- contains_constraints_rate: `0.0`
- contains_boxed_literal_rate: `1.0`
- contains_oxed_literal_rate: `1.0`
- gold_anywhere_rate: `0.4227`
- last_bit8_exact_rate: `0.4227`
- mean_raw_output_chars: `258.6`
- mean_bit_fragment_count: `1.0`

## Focus Bucket Accuracy

| v1_focus_bucket | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boolean_family` | 60 | 37 | 0.6167 |
| `dominant_structured_abstract` | 90 | 28 | 0.3111 |
| `dominant_structured_safe` | 120 | 53 | 0.4417 |
| `no_solver_answer_only` | 70 | 26 | 0.3714 |
| `no_solver_manual` | 40 | 6 | 0.1500 |
| `rare_byte_transform` | 11 | 10 | 0.9091 |
| `rare_perm_independent` | 7 | 4 | 0.5714 |
| `supported_affine_xor` | 60 | 26 | 0.4333 |
| `supported_bijection` | 50 | 47 | 0.9400 |
| `supported_not_structured` | 55 | 1 | 0.0182 |

## Exposure Band Accuracy

| v1_exposure_band | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `dominant` | 210 | 81 | 0.3857 |
| `rare` | 18 | 14 | 0.7778 |
| `supported` | 225 | 111 | 0.4933 |
| `underrepresented` | 110 | 32 | 0.2909 |
