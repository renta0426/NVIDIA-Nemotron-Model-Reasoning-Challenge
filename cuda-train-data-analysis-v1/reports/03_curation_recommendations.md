# cuda-train-data-analysis-v1 curation recommendations

## Selection tier summary

| selection_tier | family | rows |
| --- | --- | --- |
| verified_trace_ready | gravity_constant | 1597 |
| verified_trace_ready | unit_conversion | 1594 |
| verified_trace_ready | roman_numeral | 1576 |
| answer_only_keep | symbol_equation | 1410 |
| verified_trace_ready | bit_manipulation | 1004 |
| answer_only_keep | text_decryption | 971 |
| verified_trace_ready | text_decryption | 605 |
| answer_only_keep | bit_manipulation | 445 |
| manual_audit_priority | bit_manipulation | 138 |
| verified_trace_ready | symbol_equation | 110 |
| manual_audit_priority | symbol_equation | 26 |
| exclude_suspect | bit_manipulation | 15 |
| exclude_suspect | symbol_equation | 9 |

## Recommended data policy for the next `try-cuda-train.md` revision

- `verified_trace_ready` は `<think> ... </think> \boxed{}` の蒸留用コア学習データにする。
- `answer_only_keep` は answer-only / terse-boxed 補助学習データに限定し、verified trace と混ぜる比率を抑える。
- `bit_manipulation` の structured-byte 系は leave-one-out 再監査を通した行だけを `verified_trace_ready` に残し、自己支持に依存する singleton / prompt-exact 行は `answer_only_keep` に落とす。
- `manual_audit_priority` は family ごとに目視監査し、通過分だけ `verified_trace_ready` か `answer_only_keep` に昇格させる。
- `exclude_suspect` は現時点では学習から外す。規則と答えが衝突しており、ラベル誤りや parser 想定外の可能性がある。

