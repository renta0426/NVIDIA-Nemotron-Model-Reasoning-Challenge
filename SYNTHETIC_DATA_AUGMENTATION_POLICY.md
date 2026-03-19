# NVIDIA Nemotron Challenge 合成データ増強ポリシー

## 目的

この文書は、`DATA_ANALYSIS_REPORT.md` と `README.md` を土台に、NVIDIA Nemotron Model Reasoning Challenge 向けに **合成データをどう作るべきか** を整理した方針書です。

狙いは単純な「件数増し」ではありません。このベンチマークは短コンテキスト・強テンプレート・混合出力型なので、雑に合成データを足すと、分布を壊して hidden test で弱くなる可能性が高いです。

したがって本方針は、次の順で重視します。

1. hidden test に近い分布を守ること
2. ラベルの正しさを solver ベースで保証すること
3. 出力形式の安定性を守ること
4. 実データだけの validation で改善を確認すること

## README / 分析レポートから確定している前提

`README.md` と `DATA_ANALYSIS_REPORT.md` から、少なくとも次が前提になります。

- 最終提出物は `Nemotron-3-Nano-30B` 用の LoRA adapter。
- 評価は Accuracy。
- 評価時は最終回答を `\boxed{}` に入れるよう促されるが、採点側は boxed 抽出とヒューリスティック抽出を併用する。
- visible `test.csv` は本番評価用ではなく、しかも `train.csv` と重複するサンプル。
- `train.csv` は 9,500 行で、6 種類のテンプレートがほぼ均衡。
- prompt は短く、長文読解ではなく **rule induction** に近い。
- answer は単一形式ではなく、数値 / 8bit binary / ローマ数字 / 複数語テキスト / 記号列が混在する。

この構造から言えるのは、合成データの価値は「自然言語の多様さ」より **テンプレート整合性・規則の正しさ・出力 canonicalization** に強く依存する、ということです。

## なぜ雑な合成データが危険か

このデータでは、次のような合成はほぼ確実にノイズになります。

- テンプレートを崩した自由文問題を混ぜる
- LLM に prompt と answer を丸投げしてラベル検証しない
- 出力形式を原データより自由にしてしまう
- 実データの 5 倍、10 倍の件数を一気に混ぜる
- visible `test.csv` を validation の代わりに使う

特に危険なのは、**正しそうに見えるが hidden test の分布とズレた合成**です。このベンチマークは open-ended QA ではなく、かなり閉じた合成タスク群なので、分布外の多様化はそのまま性能劣化に繋がりやすいです。

## データセットの規定として守るべき大枠

### 1. 合成データは「実データの代用品」ではなく「補強材」として扱う

元の `train.csv` はすでに 6 系列がかなり均衡です。したがって、合成データの主目的は全体件数の水増しではなく、次のいずれかに限定すべきです。

- in-distribution な追加サンプルで汎化を少し厚くする
- 苦手テンプレートに hard case を追加する
- 出力形式が壊れやすいケースを集中的に増やす
- curriculum の後段で specialist 的に使う

### 2. validation は必ず「実データのみ」で作る

合成データを混ぜた validation は、改善判定を壊します。最低でも以下を守るべきです。

- `train_real`: 実データ学習用
- `valid_real`: 実データのみの検証用
- `train_synth`: 合成データ学習用

評価の主指標は常に `valid_real` に置きます。合成 validation は補助指標に留めます。

### 3. 合成データは template-aware に管理する

このベンチマークは 6 種類の強テンプレートに分かれるため、`template_family` を必須メタデータにします。さらに `symbol_equation` は実質 2 亜種あるので、`template_subfamily` も持たせるべきです。

- `bit_manipulation`
- `gravity_constant`
- `unit_conversion`
- `text_decryption`
- `roman_numeral`
- `symbol_equation_numeric`
- `symbol_equation_symbolic`

### 4. ラベルは「もっともらしさ」ではなく「再計算可能性」で保証する

合成ラベルは原則として次のどちらかでなければいけません。

- プログラムで規則を定義し、例示行と query 答えを同じ solver で生成する
- 生成された候補を、別 solver / validator で再計算して一致確認する

LLM が自然文 wrapper を作るのは構いませんが、**最終 answer を LLM のみで決める方式は禁止**です。

## 合成データ 1 件あたりの必須スキーマ

最低限、各行に次の情報を持たせるべきです。

| フィールド | 必須 | 役割 |
| --- | --- | --- |
| `synthetic_id` | 必須 | 一意 ID |
| `template_family` | 必須 | 6 系列のどれか |
| `template_subfamily` | 推奨 | 亜種管理。特に `symbol_equation` で重要 |
| `prompt` | 必須 | 学習に使う最終 prompt |
| `answer` | 必須 | canonical な正解文字列 |
| `answer_type` | 必須 | `numeric`, `binary8`, `roman`, `text_phrase`, `symbolic` など |
| `generator_type` | 必須 | `programmatic`, `teacher_proposed+solver_verified` など |
| `generator_version` | 必須 | 生成器の版管理 |
| `rule_spec` | 必須 | どんな変換規則で作ったかを再現できる情報 |
| `difficulty_tags` | 推奨 | `boundary`, `rounding`, `brace_risk`, `hard_rule` など |
| `seed` | 必須 | 再生成用の seed |
| `dedup_hash` | 必須 | exact / near-dup 検査用 |
| `format_risk_flags` | 推奨 | `contains_right_brace`, `contains_backslash` など |
| `split_policy` | 必須 | `train_only` を明示 |
| `accepted_by` | 必須 | どの validator を通したか |

ポイントは、**後で削除・再生成できる状態**を保つことです。合成データは一度入れたら終わりではなく、悪い generator を切り戻せる必要があります。

## 守るべき分布上の制約

`DATA_ANALYSIS_REPORT.md` と追加確認から、少なくとも次の制約は強いです。

| 系列 | 実データ件数 | prompt 中央文字数 | 例示数 | answer 形式 |
| --- | ---: | ---: | ---: | --- |
| bit manipulation | 1,602 | 489 | 7-10 | 常に 8bit binary |
| gravity constant | 1,597 | 319 | 3-5 | 数値、小数 1-2 桁 |
| unit conversion | 1,594 | 223 | 3-5 | 数値、常に小数 2 桁 |
| text decryption | 1,576 | 370 | 3-5 | 英語 3-5 語 |
| roman numeral | 1,576 | 219 | 3-5 | 常にローマ数字 |
| symbol equation | 1,555 | 195 | 3-5 | 記号列または整数 |

このため、合成データでは原則として次を守ります。

- prompt 長を大きく伸ばしすぎない
- 例示数をテンプレートごとの範囲から外しすぎない
- answer 型をテンプレートに対して一貫させる
- 6 系列の存在比を把握したうえで増強する

## テンプレート別の詳細規定

### 1. Bit manipulation

#### 実データの特徴

- query も answer も常に 8bit。
- query は 256 通りすべてが観測される。
- prompt は最長クラスで、例示数も多い。
- 例示 I/O は 7-10 個。

#### 生成方針

- 8bit 固定を崩さない。
- 規則は bitwise / shift / rotate / mask 系の **決定的関数**として定義する。
- 例示と query で同一規則を使う。
- query だけ難しくして例示を簡単にしすぎない。

#### 望ましい難化軸

- 操作の合成数を増やす
- rotate と shift の取り違えを誘う設定
- XOR / AND / OR の組み合わせ
- Hamming weight の極端な入力
- `00000000`, `11111111` 付近の境界

#### 禁止事項

- 8bit 以外の長さ
- 自然言語説明だけ複雑にして規則自体は曖昧な問題
- 例示から一意に規則を復元できない問題

### 2. Gravity constant

#### 実データの特徴

- `d = 0.5 * g * t^2` が明示される。
- query の `t` はおおむね `1.0` から `5.0`。
- answer は小数で、**約 90% が小数第 2 位**、残りが小数第 1 位。
- query 側から逆算した `g` は概ね `4.91` から `19.58`。

#### 生成方針

- 物理式は固定し、変えるのは `g` と観測例だけにする。
- 3-5 個の観測例すべてで同一 `g` を使う。
- query `t` の範囲は原則 `1.0-5.0` に留める。
- 小数桁数は実データ比率を保ち、2 桁中心で構成する。

#### 望ましい難化軸

- `t` が近い観測例を並べて ratio shortcut を使いにくくする
- `g` をレンジ端に寄せる
- 1 桁小数 answer を混ぜる
- 丸め誤差が出やすい値を増やす

#### 禁止事項

- 式自体を変える
- 負の時間や不自然な単位を混ぜる
- 例示ごとに別の `g` を使う

### 3. Unit conversion

#### 実データの特徴

- 3-5 例。
- query 値は概ね `5.0` から `49.89`。
- answer は常に小数第 2 位。
- query と answer から逆算した変換比はおおむね `0.50` から `2.00`。

#### 生成方針

- 各問題で変換比は 1 つに固定する。
- 出力は常に小数第 2 位に正規化する。
- 測定値レンジは原データ近傍に保つ。

#### 望ましい難化軸

- 変換比を `0.5` 付近や `2.0` 付近に寄せる
- 丸めで差が出やすい小数を増やす
- 例示値を query に近づけ、見た目の単純補間を効きにくくする

#### 禁止事項

- 単位名や表記を勝手に増やす
- 小数桁数を可変にする
- 比率が問題内で変わる設定

### 4. Text decryption

#### 実データの特徴

- query と answer は常に同じ語数。
- 語数は 3-5 語で、中央値は 4 語。
- answer 側語彙はかなり閉じており、確認範囲では約 77 語。
- answer 文字数中央値は約 25。

#### 生成方針

- まず平文 phrase を閉じた語彙から作る。
- その後、可逆な暗号規則で query を作る。
- phrase 長は 3-5 語に固定する。
- query / answer の語数一致を必須検査にする。

#### 望ましい難化軸

- 同一語を複数 phrase で再利用して letter mapping を学習させる
- 3 語と 5 語を意図的に混ぜる
- 似た語形を増やして shortcut を難しくする

#### 禁止事項

- 自由生成の長文英文
- 語数不一致
- validator が復号不能な暗号規則

### 5. Roman numeral

#### 実データの特徴

- query の数値範囲は `1-100`。
- answer は常にローマ数字。
- 3-5 例で非常にクリーン。

#### 生成方針

- 数値範囲は原則 `1-100` に留める。
- subtractive notation を含む通常のローマ数字規則に従う。
- answer は大文字ローマ数字に統一する。

#### 望ましい難化軸

- `4`, `9`, `40`, `90`, `94`, `99`, `100` 近辺を厚くする
- subtractive / additive の境界ケースを増やす

#### 禁止事項

- `100` を大きく超える値
- 小文字や別記法
- 規則が揺れる独自 numeral system 化

### 6. Symbol equation

#### 実データの特徴

- query 長はほぼ常に 5 文字。
- answer 長は 1-4 文字。
- `687` 件が整数 answer、`868` 件が記号列 answer。
- query / answer で使われる alphabet は 36 文字程度の閉じた記号集合。
- `{` を含む answer が 88 件、`}` が 94 件、`\\` が 85 件、`` ` `` が 79 件あり、整形事故リスクが現実に存在する。

#### 生成方針

- 最初から `numeric` と `symbolic` の 2 亜種に分けて生成する。
- query 長 5、answer 長 1-4 を基本に守る。
- 使用文字集合は観測 alphabet 近辺に制限する。
- escape-sensitive 文字を含む場合は `format_risk_flags` を必須化する。

#### 望ましい難化軸

- 記号位置依存の変換
- 数字混在
- 出力長が短いが判別しにくい変換
- `}`, `\\`, `` ` `` を含む metric 危険ケース

#### 禁止事項

- query 長や alphabet を大きく逸脱する設定
- 文字エスケープで壊れる prompt
- numeric / symbolic の亜種を混ぜた曖昧ラベル

## 生成方式の優先順位

合成データの作り方は、次の順で優先すべきです。

### A. Programmatic generator + exact solver

最優先です。特に `bit`, `gravity`, `unit`, `roman` は原則これで作れます。

利点:

- ラベルが壊れにくい
- 再現可能
- 難易度制御がしやすい

### B. Teacher proposes wrapper / surface form, solver verifies label

`text_decryption` や `symbol_equation` の一部では有効です。ただし teacher は **自然文 wrapper や候補ルール提案**までに留め、最終 answer は validator が確定します。

### C. Teacher-only generation

原則非推奨です。使うなら exploratory pool に限定し、本学習用データには入れないほうが安全です。

## 受け入れ判定 (acceptance gates)

合成データは、少なくとも以下を通過したものだけを採用します。

1. **Rule consistency**  
   例示行と query answer が同一 rule spec で再現できること。

2. **Format validity**  
   answer が template ごとの canonical 形式に一致すること。

3. **Length validity**  
   prompt 長、例示数、answer 長が許容範囲内にあること。

4. **Template validity**  
   intended template と prompt 実体が一致していること。

5. **Dedup validity**  
   実データとの exact duplicate ではないこと。

6. **Near-dup validity**  
   テンプレート内で表面差分だけの焼き直しになっていないこと。

7. **Risk flagging**  
   `}`, `\\`, `` ` `` など採点・整形事故を起こしやすい answer は必ず flag を付けること。

8. **Real-val usefulness**  
   小規模 pilot で `valid_real` を悪化させないこと。

## dedup / leakage 方針

### exact dedup

最低限、次は reject します。

- `prompt` 完全一致
- `prompt + answer` 完全一致
- 同一 `rule_spec` + 同一 query の再生成

### near-dup

テンプレートが強いデータなので、near-dup も重要です。推奨は以下です。

- テンプレートごとに normalized prompt similarity を見る
- query 値だけ変えたほぼ同型 prompt を過剰投入しない
- 同じ rule から大量派生した場合は subsample する

特に `unit_conversion` と `gravity_constant` は、比率や `g` が近いだけの row を大量投入すると、実質的に同じ問題を増やすだけになりやすいです。

## 合成データの推奨構成

合成データは 1 つの塊ではなく、少なくとも次の 2 プールに分けるのがよいです。

### Pool A: Core in-distribution synth

目的:

- 原データ分布の近傍でロバスト性を増す

方針:

- 6 系列の大枠比率を崩しすぎない
- 各テンプレートの表面形式を保つ
- answer 型分布も大きく崩さない

### Pool B: Hard / risk-focused synth

目的:

- 苦手テンプレート
- 出力フォーマット危険ケース
- 境界値と丸め

方針:

- `bit_manipulation`, `text_decryption`, `symbol_equation` を厚めにする
- `gravity_constant`, `unit_conversion`, `roman_numeral` は境界ケース中心に少量追加
- curriculum 後段または specialist 段階で使う

この 2 つを同じ比率で常時混ぜるのではなく、**初期は Pool A、後段で Pool B を強める**のが安全です。

## 推奨する最初の実験順

### 実験 1: 小さな Core synth

- 実データの 20-30% 程度まで
- 6 系列の比率は大きく崩さない
- まずは real-only validation を改善できるか確認

### 実験 2: Hard / risk synth の後段注入

- `bit`, `text`, `symbol` 中心
- brace / backslash / rounding / boundary を明示タグ管理
- 学習後半だけ混ぜる

### 実験 3: テンプレート別 specialist 用 synth

- generalist adapter には薄く
- specialist 段階では template-specific synth を濃く
- ただし最終評価は必ず real-only validation

## 学習との接続方針

合成データは、学習時にも次の扱いを推奨します。

- 実データと同じ重みで最初から大量混合しない
- `source = real/synth` を追跡できるようにする
- まず real warmup、次に balanced synth、最後に hard synth を使う
- 過学習確認は template ごとの精度で見る

このデータでは answer formatting が重要なので、合成データでも **canonical answer を別フィールドで保持**し、実際の学習 target 文字列とは切り分けられるようにしておくと安全です。

特に `symbol_equation` では `}` を含む answer があるため、boxed 抽出前提の surface form をそのままラベルに焼き込むと、採点器との相性問題を再生産する可能性があります。

## 98GB / 48GB GPU を見た運用メモ

この文書はデータ方針が主題ですが、運用上は次も重要です。

- 98GB 環境では複数の synth pool を持って curriculum を試しやすい
- 48GB A6000 では dataset 全量倍増より、**後段 sampling** や **hard subset 再学習** のほうが現実的
- 合成データは「全部読み込む前提」で増やすより、「選んで当てる前提」で作るほうがよい

つまり、GPU に余裕があっても **データを無制限に増やすべきではない** というのが基本姿勢です。

## やってはいけないこと

- freeform LLM だけで answer を作る
- 実データより長い説明文や別世界観を大量に混ぜる
- ローマ数字や binary の canonical form を崩す
- visible `test.csv` で良く見えるから採用する
- synthetic-only で精度が上がったことを根拠にする
- 1 generator で大量生産し、generator bias を見ない

## 結論

このベンチマークにおける合成データの価値は、量より **規定の厳しさ** にあります。

良い合成データとは、

- 原データの 6 テンプレート構造を守り
- 各テンプレートの answer 形式と長さを守り
- solver で正しさを再計算でき
- 実データだけの validation で改善が確認できる

ものです。

逆に、分布を壊し、ラベルを曖昧にし、出力 canonicalization を緩める合成データは、件数が多くても価値が低いです。

したがって今後の方針は、**「まず厳密な generator を作り、小さく検証し、効いたプールだけ段階的に採用する」** を基本線にするのが最も安全です。
