# v20_corrective_corpus_v8_mainline bundle audit

## Conclusion

`v20_corrective_corpus_v8_mainline_bundle.jsonl` は、現時点の v8 戦略を満たしており、`v7` 系で問題になった tokenstream / bundle construction bug は確認されなかった。

今回の監査では、単なる件数確認ではなく、overlay `1183` 例すべてについて artifact 側の `prompt` / `completion_text` から再 token 化した `tokens` / `mask` が bundle 本体と完全一致することまで確認した。

## Strategy compliance

戦略メモ `v20_corrective_corpus_v8_mainline_strategy_2026-04-22.md` の主張に対し、実生成物は次の通り一致している。

- unique rows: `598`
- repeated overlay rows: `1183`
- base examples: `7828`
- total examples: `9011`
- total tokens: `28199629`

bucket 配分も一致している。

- `binary_structured_exact_core`: `224`
- `binary_logic_exact`: `88`
- `binary_permutation_exact`: `64`
- `binary_prompt_local_exact`: `96`
- `symbol_numeric_exact`: `48`
- `symbol_glyph_exact`: `48`
- `surface_numeral_boxed`: `18`
- `surface_cipher_boxed`: `4`
- `surface_unit_tail`: `4`
- `easy_gravity_fragile`: `4`

allocation は次の通りで、戦略メモの `75-80% BIT / 15-20% symbol / <=5% guardrail` に収まっている。

- BIT: `472` (`78.93%`)
- symbol: `96` (`16.05%`)
- guardrail: `30` (`5.02%`)

hard anchor も戦略どおり含まれている。

- binary hard hits: `15`
- symbol hard hits: `8`

## Bundle integrity checks

次の checks を実施し、すべて pass した。

### 1. summary / bundle / artifacts の件数整合

- `corrective_overlay_summary.json` の `selected_unique_rows` と `corrective_overlay_unique.jsonl` の行数が一致
- `selected_repeated_rows` と `corrective_overlay_repeated.jsonl` の行数が一致
- bundle manifest / summary / 実 bundle 行数が一致

### 2. base snapshot payload integrity

- bundle 中の `base_snapshot` 例 `7828` 件が、`04-08-16-14` base snapshot の filtered rows と 1:1 で一致
- 各 base example の `tokens` / `mask` / `num_loss_tokens` が snapshot payload と完全一致

### 3. overlay 1:1 mapping integrity

- `corrective_overlay_repeated.jsonl` の全 row に対して bundle 側の `(source_problem_id, overlay_instance)` が一意に存在
- duplicate overlay key は `0`
- unique id duplicate は `0`
- repeated overlay key duplicate は `0`

### 4. retokenization integrity

generator 内の `tokenize_overlay_example()` を使って、overlay `1183` 件すべてを再 token 化した。

結果:

- payload mismatch: `0`
- source tag mismatch: `0`
- bucket mismatch: `0`
- assistant style mismatch: `0`
- mask length mismatch: `0`
- `sum(mask) != num_loss_tokens`: `0`
- token/mask hash mismatch: `0`

これは overlay payload が artifact text から deterministically 再構成できることを意味する。

## v7-like bug probe

`v7` 問題の本質は、overlay text 自体よりも tokenstream construction が壊れうる点だった。これに対して v8 では次を確認した。

- overlay rows は全件 `source = corrective_overlay`
- overlay rows は全件 `segment = synthetic.jsonl`
- `retokenized_overlay_example_count = 1183` で repeated overlay rows 数と一致
- `retokenized_overlay_problem_count` が repeated overlay IDs の distinct count と一致
- `retokenized_overlay_problem_ids` が repeated overlay IDs の集合と一致

したがって、v8 bundle には `v7` のような「text は合っているが token payload が崩れている」兆候は見つからなかった。

## Important nuance

`legacy_teacher_answer_mismatch` source tag が binary 側に残っている row はあるが、これは bug ではない。v8 は legacy reasoning text をそのまま bundle に載せているのではなく、prompt・gold answer・verified metadata から短い synthetic supervision を再構成して retokenize している。

よって、旧 reasoning の boxed answer mismatch は「旧 trace を信用しない」という印であり、今回の bundle integrity failure ではない。

## Audit result

学習前監査としての結論は次の通り。

1. v8 コーパスは、現在の戦略メモに対して count / allocation / hard anchor の各面で整合している。
2. bundle 本体は base snapshot / overlay artifacts と token-level で整合している。
3. `v7` 型の tokenstream bug を示す証拠は今回の bundle では見つからなかった。
4. したがって、少なくとも data generation / bundle construction の観点では、v8 は学習に進めてよい状態にある。