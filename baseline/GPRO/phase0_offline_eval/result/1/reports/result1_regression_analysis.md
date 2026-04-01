# GPRO Step1 Notebook Run `result/1` 回帰分析レポート

## 対象

- 学習 Notebook: `baseline/GPRO/step1_binary_answer_only/train_gpro_step1_binary_answer_only.ipynb`
- 評価結果: `baseline/GPRO/phase0_offline_eval/result/1/artifacts/*`
- 比較基準: `baseline/cot/phase0_offline_eval/result/{0,1,2}`

## 先に結論

今回の `baseline/GPRO/phase0_offline_eval/result/1` は、かなり明確に回帰しています。

ただし、結論は「Notebook 版が壊れている」とまではまだ言えません。  
むしろ静的に見る限り、**この結果は Step1 の設計そのものと整合的**です。

1. `train_gpro_step1_binary_answer_only.ipynb` は公式 base model から開始している。
2. 学習データは `binary-only` で、`step1_binary_answer_only_manifest.json` 上 `1285` 行のうち `1125` 行 (`87.55%`) が `boxed_only`。
3. `plan-base.md` でも Step1 は **binary specialist の warm start** として位置付けられており、単体で general benchmark を守る前提ではない。
4. したがって、今回の full benchmark 劣化には **想定内の catastrophic forgetting** がかなり含まれている。

ただし同時に、**Step1 自身の目的である「short exact boxed 8-bit への寄せ」も十分には達成できていません。**  
binary の `boxed_extraction_success_rate` は `0.1167` で、比較対象の `baseline/cot/result/1` の `0.2167` より悪化しています。

## README 基準での見方

`README.md` の評価説明では、最終回答は `\boxed{}` を優先抽出し、そこが使えない場合に他の heuristic や最後の数値へ fallback します。  
この repo の offline eval も同じ方針で、`boxed` の中身をそのまま取り出し、数値として `float()` 変換できない場合は不正解になります。

この前提だと、次の 3 種類は全部スコアを落とします。

- `\boxed{}` が出ない
- `\boxed{94.72\text{ m}}` のように box 内に単位や余計な文字が入る
- 長い推論の末に box を閉じず、最後の中間計算値だけが `last_number` として拾われる

今回の `result/1` は、まさにこの 3 つが混ざって起きています。

## 比較サマリ

| run | overall | binary | gravity | symbol | text | unit | roman |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `GPRO/result/1` | 0.6125 | 0.1667 | 0.7200 | 0.3833 | 0.7800 | 0.7600 | 1.0000 |
| `COT/result/0` | 0.6750 | 0.1833 | 0.8600 | 0.4333 | 0.7400 | 0.9800 | 1.0000 |
| `COT/result/1` | 0.7031 | 0.2000 | 0.9200 | 0.4167 | 0.9000 | 0.9600 | 0.9800 |
| `COT/result/2` | 0.7094 | 0.2167 | 0.9400 | 0.4000 | 0.8600 | 1.0000 | 1.0000 |

重要なのは、`plan-base.md` の `result/0 -> result/1 -> result/2` は **今回の GPRO フォルダではなく、`baseline/cot/phase0_offline_eval/result/*` を参照している**ことです。  
そのため、`plan-base.md` にある「result/1 は伸びた」という記述を今回の `baseline/GPRO/.../result/1` にそのまま当てると比較を取り違えます。

## 主要所見

### 1. full benchmark での general 劣化は大きい

`baseline/cot/result/1` 比での差分は次の通りです。

- overall: `0.7031 -> 0.6125` (`-0.0906`)
- binary: `0.2000 -> 0.1667` (`-0.0333`)
- gravity: `0.9200 -> 0.7200` (`-0.2000`)
- symbol: `0.4167 -> 0.3833` (`-0.0334`)
- text: `0.9000 -> 0.7800` (`-0.1200`)
- unit: `0.9600 -> 0.7600` (`-0.2000`)

roman だけは落ちていませんが、それ以外はほぼ全面的に悪化しています。

これは Notebook 実装ミスの可能性もゼロではないものの、まずは **binary-only warm start を単体で評価した副作用** と見るのが自然です。

### 2. それでも binary の Step1 目的は未達

Step1 の意図は `plan-base.md` 上、

- `boxed only` を多数派にする
- 長い `<think>` を避ける
- action space を `\boxed{[01]{8}}` 近傍へ寄せる

でした。

しかし実測は逆方向です。

| metric | `GPRO/result/1` | `COT/result/1` |
| --- | ---: | ---: |
| binary accuracy | 0.1667 | 0.2000 |
| boxed_extraction_success_rate | 0.1167 | 0.2167 |
| regex_exact_rate | 0.1667 | 0.2500 |
| leading_zero_retention_rate | 0.2000 | 0.2333 |
| format_failure_rate | 0.8833 | 0.7833 |

binary 60 問のうち、

- `53/60` が `\boxed{}` なし
- その `53/60` は `last_number` fallback
- よく出る誤答は `1`, `0`, `3`, `8` などの一桁 collapse

でした。

つまり、**「短い exact boxed byte に寄せる」はまだできていません。**

### 3. binary の tier 別でも改善していない

binary hard set の tier 別成績は以下です。

| tier | `GPRO/result/1` | `COT/result/1` |
| --- | ---: | ---: |
| `verified_trace_ready` | `7/20 = 0.3500` | `8/20 = 0.4000` |
| `answer_only_keep` | `2/20 = 0.1000` | `3/20 = 0.1500` |
| `manual_audit_priority` | `1/20 = 0.0500` | `1/20 = 0.0500` |

Step1 が重点的に効いてほしい `verified_trace_ready` と `answer_only_keep` ですら改善していません。

### 4. gravity の大半は「推論崩壊」ではなく「boxed 内フォーマット事故」

gravity は `36/50` まで落ちていますが、ここはかなり重要です。

誤答 14 件のうち 13 件は、

- `\boxed{94.72\text{ m}}`
- `\boxed{24.63\text{ m}}`

のように、**値そのものは gold と数値的に近いのに box 内へ `\text{ m}` を混ぜたせいで offline eval が落としている**ケースでした。

単純に box 内から数値だけを抜く仮想修正では、gravity は

- `36/50 -> 49/50`

まで戻ります。  
したがって gravity の悪化は主に reasoning ではなく **output formatting の事故** です。

### 5. text / unit / symbol は general formatting drift が強い

`baseline/cot/result/1` と比べると、no-box 率がかなり悪化しています。

| family | no-box rate (`GPRO/result/1`) | no-box rate (`COT/result/1`) |
| --- | ---: | ---: |
| binary | 0.8833 | 0.7833 |
| text | 0.2200 | 0.0200 |
| unit | 0.2400 | 0.0200 |
| symbol | 0.3833 | 0.4000 |

特に text と unit は、もともと box をかなり安定して閉じられていたのに、Notebook run では長い推論のあとに最終 answer を box 化できず、`last_number` fallback に流れるケースが激増しています。

代表例:

- `50f2caf4` (`text`): expected `dragon draws in valley` に対し prediction `5`
- `16fa37e8` (`unit`): expected `10.14` に対し prediction `7000`
- `34f18cf1` (`unit`): expected `39.20` に対し prediction `1.47`

これは reasoning というより **completion termination の崩れ** です。

### 6. 出力はむしろ長くなっている

Step1 は本来 short exact output を狙っていますが、`raw_output` の文字数平均はむしろ伸びています。

| family | mean raw_output chars (`GPRO/result/1`) | mean raw_output chars (`COT/result/1`) |
| --- | ---: | ---: |
| binary | 17077 | 15256 |
| symbol | 18572 | 13469 |
| text | 12699 | 7157 |
| unit | 9828 | 2573 |

とくに text / unit / symbol の長文化が顕著です。  
`plan-base.md` が警戒していた **long-output collapse** がそのまま出ています。

## 代表的な failure pattern

### binary

`0f7be6a8`

- gold: `01000000`
- GPRO prediction: `0`
- 原因: 長い bit 推論のあと `\boxed{}` を閉じず、最後の中間数値だけが `last_number` で拾われた

### gravity

`565bc498`

- gold: `94.71`
- GPRO prediction: `94.72\\text{ m}`
- 原因: reasoning はほぼ正しいが、box 内に単位を混ぜたため scoring 上は不利

### unit

`16fa37e8`

- gold: `10.14`
- GPRO prediction: `7000`
- 原因: 長い計算文の途中数値が最後に残り、final boxed answer が定着していない

## 何が最もありそうか

現時点の尤もらしい説明を強い順に並べると次の通りです。

### A. 主因は「Step1 を standalone adapter として full benchmark 評価したこと」

これはかなり強いです。

- Notebook は base model から binary-only 学習
- `plan-base.md` は Step1 を warm start と位置付け
- その後に ORPO / GRPO / G+B merge を想定

なので、**general benchmark の防御が落ちるのはむしろ自然**です。

### B. Step1 の boxed discipline 自体も弱い

ただしこれも同時に事実です。

- binary で `boxed_extraction_success_rate` が改善していない
- no-box 率は `88.33%`
- `1`, `0`, `3` などの collapse が多い

つまり「binary specialist warm start としてもまだ readiness 不足」です。

### C. Notebook 固有の実装バグは、静的比較だけでは断定できない

Notebook 側の設定を見る限り、

- `MODEL_PATH = kagglehub.model_download(...)`
- binary-only dataset の読込
- assistant-only LoRA 学習

という主要部分は script と整合的です。

少なくとも今回の artifacts だけからは、**Notebook だけが別物を学習した**という強い証拠は見えていません。  
もしバグがあるとしても、export / inference / chat template / generation 側の subtler issue の可能性が高いです。

## 暫定判定

今回の `result/1` は「何かおかしい」という直感自体は正しいです。  
ただしその中身は 2 層に分けて考えるべきです。

1. **想定内の悪化**  
   Step1 を単独で full benchmark に出したことによる general 側の catastrophic forgetting。

2. **想定外の悪化**  
   Step1 本来の目的である binary の `short exact boxed 8-bit` への寄せすら十分に達成できていないこと。

したがって、この run から言えるのは次です。

> **Notebook 版が壊れているとまではまだ断定できない。**  
> ただし **この Step1 run は submission 候補でも general anchor 候補でもなく、binary warm start としても box-discipline が弱い。**

## 次に確認すべき点

次フェーズで真っ先に見る価値が高いのは以下です。

1. Notebook の export / inference で chat template や generation 設定が script 想定と一致しているか
2. binary holdout に対して `^\s*(<think>...</think>)?\s*\\boxed{[01]{8}}\s*$` の strict 終端率を直接測ること
3. general eval を見る前に、Step1 を **binary specialist 単体の readiness** として判定すること
4. non-binary 系では `\boxed{94.72\text{ m}}` のような unit 混入を禁止する出力規律を入れること

