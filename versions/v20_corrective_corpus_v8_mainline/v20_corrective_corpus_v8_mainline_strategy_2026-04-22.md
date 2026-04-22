# v20_corrective_corpus_v8_mainline strategy

## 1. Positioning

v8 は micro tuning を止めて、official 0.88 に向けた本命 1 本として組んだ mainline である。

方針は `versions/v20_to_088_reassessment_2026-04-18.md` の更新判断に従う。

- ratio tuning の継続はやらない
- `04-08-16-14` は base snapshot として維持する
- main investment は BIT-core に寄せる
- symbol は broad overlay ではなく exact lane として切り出す
- easy family は regression guardrail だけにする

README.md と A-Open README の根拠は次の 4 点である。

- evaluation は deterministic (`temperature = 0.0`) で boxed-first
- leaderboard の主戦場は bit_manipulation
- tokenization-aware supervision が必要
- symbol は split / concat / text-to-character 系の弱点が強い

## 2. Why v8 is one major run

計算資源制約により細かい分岐 run は行わず、v8 は次の 1 本に絞った。

- BIT-core mainline
- targeted symbol exact lanes
- minimal easy-family guardrail

これは `v7-1` のような token-safe repair run ではない。`v7-1` は raw output repair として有効だったが、public best を更新していない。v8 は frontier teacher を差し替える run である。

## 3. Actual v8 allocation

unique row 配分は次の通り。

- `binary_structured_exact_core`: 224
- `binary_logic_exact`: 88
- `binary_permutation_exact`: 64
- `binary_prompt_local_exact`: 96
- `symbol_numeric_exact`: 48
- `symbol_glyph_exact`: 48
- `surface_numeral_boxed`: 18
- `surface_cipher_boxed`: 4
- `surface_unit_tail`: 4
- `easy_gravity_fragile`: 4

合計 `598` unique rows で、配分は次の通り。

- BIT: `472` (`78.93%`)
- symbol: `96` (`16.05%`)
- guardrail: `30` (`5.02%`)

この比率は、更新済み戦略メモの `75% BIT / 20% symbol / 5% guardrail` の実装形に相当する。

## 4. Data sources

BIT lane の主ソース:

- `cuda-train-data-analysis-v1/artifacts/train_recommended_learning_target_v1.csv`

symbol numeric lane の補助ソース:

- `cuda-train-data-analysis-v1/artifacts/symbol_operator_specific_formula_candidates_v1.csv`
- `cuda-train-data-analysis-v1/artifacts/symbol_manual_prompt_exact_answer_only_candidates_v1.csv`
- `cuda-train-data-analysis-v1/artifacts/symbol_trace_teacher_policy_v1.csv`

symbol glyph lane の補助ソース:

- `cuda-train-data-analysis-v1/artifacts/symbol_glyph_training_answer_only_candidates_v1.csv`
- `cuda-train-data-analysis-v1/artifacts/symbol_glyph_grouped_exact_answer_only_candidates_v1.csv`
- `cuda-train-data-analysis-v1/artifacts/symbol_trace_teacher_policy_v1.csv`

guardrail は `04-08-16-14` base snapshot の fragility prioritization から最小本数だけ取る。

## 5. Hard anchors

binary hard anchors は `15` 件を固定で含めた。

- structured: `012fb81b`, `01e09228`, `0520a6ec`, `0a50c4a8`, `1532c0d1`, `17fd9612`, `59c78e51`, `8e5d6fe6`, `a6192d29`
- logic: `0dd5caf4`, `c30a782a`
- permutation: `b9500f41`, `fa67da07`
- prompt-local: `12fd5b6c`, `2d790c98`

symbol hard anchors も `8` 件を固定で含めた。

- numeric_2x2: `8158a14c`, `878c843c`, `b7b1d1a8`, `e8de8b47`
- glyph_len5: `a85864a9`, `be7101dc`, `d7e5414c`, `dc240ebd`

## 6. Generated outputs

2026-04-22 時点で生成済み。

- bundle path: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v8_mainline_bundle.jsonl`
- base examples: `7828`
- overlay examples: `1183`
- total examples: `9011`
- total tokens: `28199629`
- max seq len: `7971`

artifact は次に出力されている。

- `versions/v20_corrective_corpus_v8_mainline/outputs/v8_mainline_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v8_mainline/outputs/v8_mainline_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v8_mainline/outputs/v8_mainline_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v8_mainline/outputs/v8_mainline_default/artifacts/corrective_overlay_summary.json`

canonical validation は pass している。

## 7. Score record

この commit では data generation までを完了した。

- latest measured reference: `v7-1`
- `v7-1` proxy: `178/200 = 0.8900`
- `v7-1` public: `0.84`
- `v8` local / proxy / official score: 未計測

したがってこの時点の Git 記録としては、v8 は「bundle 生成完了、学習・評価待ち」である。

## 8. Important note

`corrective_overlay_summary.json` 上では `legacy_teacher_answer_mismatch` を含む binary rows も選択されているが、これは意図的である。v8 は legacy reasoning text を再利用せず、prompt と gold answer と verified metadata から短い synthetic supervision を再構成する run であるため、旧 reasoning の boxed answer mismatch を候補除外条件にしていない。
