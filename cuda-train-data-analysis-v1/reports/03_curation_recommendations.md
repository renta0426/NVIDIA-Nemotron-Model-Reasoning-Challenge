# cuda-train-data-analysis-v1 curation recommendations

## Selection tier summary

| selection_tier | family | rows |
| --- | --- | --- |
| verified_trace_ready | gravity_constant | 1597 |
| verified_trace_ready | unit_conversion | 1594 |
| verified_trace_ready | roman_numeral | 1576 |
| manual_audit_priority | symbol_equation | 1304 |
| answer_only_keep | text_decryption | 971 |
| manual_audit_priority | bit_manipulation | 966 |
| verified_trace_ready | text_decryption | 605 |
| verified_trace_ready | bit_manipulation | 599 |
| answer_only_keep | symbol_equation | 130 |
| verified_trace_ready | symbol_equation | 110 |
| answer_only_keep | bit_manipulation | 22 |
| exclude_suspect | bit_manipulation | 15 |
| exclude_suspect | symbol_equation | 11 |

## Recommended data policy for the next `try-cuda-train.md` revision

- `verified_trace_ready` は `<think> ... </think> \boxed{}` の蒸留用コア学習データにする。
- `answer_only_keep` は answer-only / terse-boxed 補助学習データに限定し、verified trace と混ぜる比率を抑える。
- `manual_audit_priority` は family ごとに目視監査し、通過分だけ `verified_trace_ready` か `answer_only_keep` に昇格させる。
- `exclude_suspect` は現時点では学習から外す。規則と答えが衝突しており、ラベル誤りや parser 想定外の可能性がある。

