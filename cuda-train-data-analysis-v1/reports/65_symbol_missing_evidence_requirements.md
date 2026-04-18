# cuda-train-data-analysis-v1 symbol missing evidence requirements

README.md 基準では評価は final boxed answer accuracy だが、ここで扱う `verified_trace_ready` は prompt-only の trace teacher であり、**gold が合っていること**と**trace-safe に昇格できること**は別である。  
`reports/32_symbol_strict_prompt_audit.md` の row-level strict audit を、今回「何が足りないから verified に上がらないのか」という観点で再整理した。

## Current prompt-only ceiling

- `symbol_equation` total: `1,555`
- current strict prompt-safe verified: `110`
- 90% target: `1,400`
- category ceiling without `cryptarithm_guess`: `1,391 / 1,555 = 89.45%`

したがって、現行 strict 定義のまま 90% に届くには、少なくとも `cryptarithm_guess` から `9` 行以上を **外部仮定なしで** verified に上げる必要がある。

## Missing evidence by public problem category

| problem category | current strict blocker | rows | what is missing for verified promotion |
| --- | --- | --- | --- |
| `equation_numeric_deduce` | `needs_cross_row_evidence` | `275 answer_only + 14 manual` | same-op examples はあるが current exact DSL で一意 spec にならない。verified には **追加の区別用 same-op witness** か、current DSL 外の family を正当化する **authoritative semantics** が要る。 |
| `equation_numeric_deduce` | `support_below_verified_threshold` | `114` | unique local rule はあるが current gate (`same_operator_example_count >= 2`) に届かない。strict prompt-only のままなら **もう 1 本以上の same-op witness** が必要。 |
| `equation_numeric_deduce` | `prompt_ambiguous` | `47 answer_only + 8 manual` | 複数の prompt-consistent exact rule が残っている。verified には **alternative rules を潰す distinguishing example** が必要。 |
| `equation_numeric_deduce` | `prompt_exact_conflict` | `15 answer_only + 4 manual + 9 exclude` | current exact family では gold と衝突する。verified には **gold 修正** か、current solver family では欠けていることを示す **公式 semantics / generator trace** が必要。 |
| `equation_numeric_guess` | `unseen_query_operator` | `108` | query operator が examples に出ない。verified には **query operator を拘束する witness example** か、operator semantics を固定する **official source** が必要。 |
| `equation_numeric_guess` | `prompt_exact_conflict / prompt_ambiguous` | `27 + 1` | operator identity を捨てた global exact scan でも gold-safe unique spec にならない。verified には **row-level generator semantics** か **gold 修正** が必要。 |
| `cryptarithm_deduce` | `unseen_query_operator` | `306` | query 側の operator meaning が prompt で未拘束。verified には **同 operator の prompt witness** または **official operator map** が必要。 |
| `cryptarithm_deduce` | `latent_rule_nonunique` | `353 + 76 + 2 tail` | coarse multiset/order では answer-only に置けても latent rule が一意にならない。verified には **witness-complete examples** か **generator-side latent rule proof** が必要。 |
| `cryptarithm_guess` | `unseen_query_operator` | `164` | 90% ceiling を破るための唯一の追加 tranche だが、現状は query operator 未出で strict prompt-only では全滅。verified には **official generator semantics**, **signed latent-program manifest**, もしくは **query operator を含む追加 examples** が必須。 |

## What does *not* count as sufficient evidence

- gold answer が自然に見えること
- query answer だけが既知 family に似ていること
- public winner code の fallback (`abs-diff`, `concat`) が当たること
- corpus を眺めると同じ operator に見える、という非公式推定
- LLM の CoT でそれらしく説明できること

これらは answer-only supervision の保持根拠にはなっても、prompt-only `verified_trace_ready` の根拠にはならない。

## Practical implication

1. `equation_numeric_deduce` は、strict prompt-only を保つなら **追加 same-op witness の不足** が主因。
2. `equation_numeric_guess` と `cryptarithm_guess` は、strict prompt-only を保つなら **unseen query operator semantics の不足** が主因。
3. `cryptarithm_deduce` は、query operator 未出に加えて **latent rule non-identifiability** が大きい。
4. よって 90% 未達は「solver をもう少し賢くすれば埋まる残差」ではなく、主に **witness / semantics / label provenance の不足** による。

## Conclusion

現行 strict verified 定義のままでは、

- `equation_numeric_deduce` には **same-op witness の追加**
- `equation_numeric_guess` / `cryptarithm_guess` には **official operator semantics**
- `cryptarithm_deduce` には **latent rule を一意化する witness-complete examples か generator proof**

が必要である。  
特に 90% 達成の鍵である `cryptarithm_guess` `164` 行は、現状公開されている prompt と public code だけでは strict verified tranche に変換できない。
