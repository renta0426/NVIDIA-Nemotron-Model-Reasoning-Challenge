# Proof-First Solver Factory Routing Plan

## 1. 目的

今回の discussion で一番価値があるのは、問題を family ごとの solver に先にルーティングし、その family 専用の短い検証付き手順で解くという発想である。

ただし、そのままの長い自己言及テンプレートを学習させるのは避ける。

README.md の評価は最終 answer の Accuracy であり、しかも boxed 抽出が最優先である。したがって、このアプローチを repo へ積極的に取り込む場合の本質は次の 3 点にある。

1. モデルに family routing を覚えさせる
2. family ごとに最短の executable trace へ落とす
3. boxed final answer を絶対に壊さないようにする

この plan では、この方針を Proof-First Solver Factory Routing と呼ぶ。

## 2. README.md 前提での設計要求

README.md から外せない前提は以下である。

1. スコアは最終 answer の Accuracy で決まる
2. final answer は boxed 抽出が最優先で評価される
3. 推論は temperature 0.0 で固定される
4. max_tokens 7680 の範囲で安定して閉じる必要がある

したがって routing の学習は、分類精度そのものよりも、最終的に正しい boxed answer へ安定して到達するための中間 scaffold として設計する必要がある。

## 2.1 baseline v2 適合前提

この plan は baseline v2 を置き換えるためのものではなく、baseline v2 に差分注入するための plan として読む。

現状の最良系は `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv` 学習版であり、小規模評価では

1. binary `0.4833`
2. symbol `0.3667`
3. gravity `1.0000`
4. roman `1.0000`
5. text `0.9800`
6. unit `0.9800`

という分布である。

したがって、この plan の狙いは easy family を作り直すことではなく、v2 の broad strength を維持したまま binary と symbol の content error を削ることにある。

特に重要なのは、v2 binary が `boxed_extraction_success_rate = 0.8333` まで到達している点である。

この値は binary family に対してかなり強い資産であり、routing 導入で最初に守るべきものはこの boxed close の習慣である。

## 2.2 この plan の成功条件

v2 適合の観点では、成功条件は次の順で評価する。

1. binary boxed extraction success を落とさない
2. binary の format_ok_content_wrong を下げる
3. symbol numeric_2x2 を引き上げる
4. roman、gravity、text、unit の既存高精度を維持する

つまり「route-aware にしたかどうか」自体は目的ではなく、v2 の勝ち筋を崩さず hard family の中身を改善できたかどうかが目的である。

## 3. discussion から借りるべき核

今回の discussion から積極的に取り込むべき核は次である。

### 3.1 family first

最初に問題タイプを判定し、その後に専用 solver へ入る。

これは本 repo の family ledger と自然に整合する。既に row ledger には family、template_subtype、teacher_solver_candidate があるため、routing 信号の教師源は十分に存在する。

### 3.2 wrapper non-essential

Alice in Wonderland 風の wrapper や decorative wording を本質とみなさず、I/O 例から hidden transform を読む。

特に symbol 系では、operator token を直接信じないという姿勢が有効である。

### 3.3 prove first

rule を採用する前に、例で成り立つことを短く確認する。

discussion の強い点はここで、単なる family 名の宣言ではなく、例との整合確認を経て solver を lock する流れにある。

### 3.4 answer formatting as contract

最終 boxed answer を厳格な出力契約として扱う。

これは README.md と完全に整合する。

## 4. discussion から借りない方がよい部分

そのまま採用すると危険な部分も明確である。

### 4.1 長い自己言及 preamble

I am a reasoning model から始まる長い自己言及は、token を無駄に消費し、出力の終端品質も悪化させやすい。

本 repo の既存知見でも、効いているのは correct-only teacher と boxed closing の安定化であり、巨大 preamble ではない。

### 4.2 binary の過度な単純化

binary を per-bit boolean decomposition へほぼ還元するのは危険である。

本 repo では bit_manipulation に対して permutation、bijection、2-bit boolean、3-bit boolean、GF(2) affine XOR、byte transform、structured byte formula、not-formula、hybrid consensus まで必要だった。

したがって binary へ discussion の routing を取り込む場合も、route label は binary 一段ではなく、内部 solver family まで落とす必要がある。

### 4.3 underdetermined row への trace 捏造

answer_only_keep や manual_audit_priority に対して、discussion 的なもっともらしい trace を一括で付けるのは危険である。

本 repo の ledger が意味しているのは、answer が使えても procedure が一意とは限らない、ということである。

## 5. この repo における積極的な取り込み方

今回のアプローチを積極的に盛り込むなら、最も重要なのは long CoT を真似ることではなく、既存の ledger と synthetic pipeline に routing field を明示的に差し込むことである。

ただし差し込み先は、新しい単独コーパスではなく baseline v2 の既存 training distribution とする。

言い換えると、この plan の基本戦略は replacement ではなく augmentation である。

### 5.1 基本方針

1. baseline v2 の既存 rows は原則温存する
2. verified_trace_ready は route plus executable trace の差分教師として追加する
3. answer_only_keep は route plus closure-only あるいは query-commit の補助教師として低比率で追加する
4. manual_audit_priority は raw のまま trace 化しない
5. exclude_suspect は完全除外する

特に hard family への routing 導入では、既存 v2 の boxed behavior を壊しやすい full replacement を避け、v2 notebook 互換の生成形式に寄せる。

### 5.2 route は自然文ではなく canonical field として扱う

推奨するのは、長い自然文による自己申告ではなく、短い固定書式の route declaration である。

例:

- Route: symbol_equation.numeric_2x2
- Route: bit_manipulation.binary_structured_byte_formula

これにより、モデルは route token を学びやすくなり、余分な narrative を減らせる。

ただし、discussion の主眼は hard family である bit_manipulation と symbol_equation にある。

したがって本 plan では、route の強制導入対象を一律全 family に広げない。

基本ルールは次の通りとする。

1. bit_manipulation と symbol_equation.numeric_2x2 には explicit route を積極導入する
2. text_decryption は verified slice に限って optional に route を付ける
3. roman_numeral、unit_conversion、gravity_constant は初期段階では route 必須にしない
4. easy family への coarse route は、全体 mixed corpus の安定化が必要になった段階で少量導入する

つまり route は「全 family を均等に飾るタグ」ではなく、「hard family で誤ルーティングを減らすための強い教師」と位置付ける。

### 5.3 prove-first は 1 から 2 行の evidence に圧縮する

discussion の思想は維持しつつ、証明部分は極小化する。

例:

- Check ex1 and ex2: same ratio holds
- Check ex1 and ex2: same operator behavior fits BA_DC|mul|rev
- Check ex1 and ex2: xor(shl1,shr4) matches both

この evidence は family lock の根拠として十分であり、全例 replay は不要である。

ここで重要なのは、evidence を追加しても boxed close の終端位置を遠ざけすぎないことだ。

v2 適合の観点では、proof-first は「長い説明を増やす技法」ではなく、「内容誤りを減らす最小限の solver lock」として設計する。

### 5.4 solve 部分は executable trace に統一する

solve は family ごとに自然文ではなく executable な中間表現へ固定する。

例:

- rate = out / in
- parse roman then rebuild
- map chars then decode query
- formula = xor(shl1,shr4)
- apply rule to query

これは既存の bit synthetic exact-trace 方針とも整合する。

ただし v2 適合では、assistant text 全体の style shift を大きくしないことが重要である。

したがって solve は `<think>` 専用形式へ一気に切り替えるのではなく、既存 v2 notebook と互換な no final answer leak、no inline box の short trace として導入する方が安全である。

## 5.5 baseline v2 に対する不変条件

v2 に混ぜる際の不変条件をここで固定する。

1. baseline v2 の既存 rows は削らない
2. 新規 route-aware rows でも `generated_cot` に最終 answer を plain text で書かない
3. 新規 route-aware rows でも `generated_cot` に `\boxed{}` を書かない
4. 既存 notebook の boxed 付与ロジックを変えずに使える形にする
5. hard family の追加比率は段階的に上げ、全体分布を一気に傾けない
6. easy family の coarse route 導入は後段の微調整に留める

この 6 条件を満たさない案は、routing の内容が良くても v2 互換案としては不採用とする。

## 6. family 別の実装方針

### 6.1 roman_numeral

最も取り込みやすい family である。

ただしこの family は既に solved / verified が飽和しているため、discussion を取り込む主戦場ではない。

route を先頭に置くこと自体は可能だが、初期実装では必須にしない。

もし導入するなら、全 family mixed corpus の coarse calibration 用の薄い slice に留める。

推奨 trace 骨格:

1. Route
2. Direction lock
3. Decompose or parse
4. Round-trip verify
5. Final boxed answer

### 6.2 unit_conversion

discussion の rate-first 発想をほぼそのまま採用できる。

ただしこの family も現在は verified が飽和しており、hard family routing の主対象ではない。

長い preamble は不要で、固定比率の evidence を 1 から 2 例だけ示し、query 適用へ進む。

route 付き synthetic を作るとしても、bit / symbol 用 route token を過学習させないためのバランス調整用途に限る。

### 6.3 gravity_constant

unit_conversion とほぼ同型に扱う。

違いは rate が out per t squared である点だけなので、router 上は family を分け、trace は同じ骨格でよい。

ただし優先度は low とし、初期の route-aware 実装対象からは外してよい。

### 6.4 text_decryption

verified 605 行は route plus char-map trace にできる。

answer_only 971 行は query に必要文字が examples に不足している clean answer-only slice なので、完全 trace へ上げず、次のいずれかに留める。

1. Route plus closure-only
2. Route plus minimal commit
3. Boxed-only closure

ここで trace を捏造しないことが重要である。

text は hard family の中では secondary target とみなし、bit / symbol の後に route 導入する。

### 6.5 symbol_equation.numeric_2x2

discussion の恩恵が最も大きい family である。

積極導入すべきポイントは次である。

1. operator symbol を直接信用しない
2. same-op だけでなく output behavior から rule family を読む
3. decorative operator swap を adversarial variation として学習させる

ここでは synthetic data 側で、同一 exact rule を複数 operator token で包んだ prompt を意図的に生成する価値がある。

つまり学習目標は、operator token classification ではなく、example output pattern matching にすることだ。

ただし trace 教師化は verified と strong answer-only に限る。same_operator_example_count が 0 の numeric tail は final-answer supervision に留め、procedure teacher へは上げない。

v2 適合の観点では、symbol は binary よりもさらに保守的に混ぜる。

理由は次の通り。

1. current symbol accuracy は低いが、glyph_len5 が大きく混ざる family でもある
2. operator-decorrelation は numeric_2x2 には効くが、symbol 全体へ広げるとノイズになりうる
3. v2 の broad score を守るには、numeric verified と narrow answer-only に限定して薄く差分注入する方が安全である

### 6.6 symbol_equation.glyph_len5

この slice は latent rule の一意化ができていないため、discussion 的な solver trace を積極導入する対象ではない。

ここは route teacher を作るとしても shallow に留める。

推奨:

1. Equation symbolic という coarse route のみ
2. final-answer supervision のみ
3. synthetic CoT は作らない

### 6.7 bit_manipulation

既存の bit synthetic 路線を核にしつつ、discussion の routing を前置する形が最適である。

現在の bit_synth_exact_trace_cot_v1 と v1.1 は executable trace 側はかなり強いが、family routing を明示的に学ばせる設計ではない。

ここに追加したいのは次の 2 層である。

1. coarse route: bit_manipulation
2. exact route: binary_structured_byte_formula, binary_affine_xor, binary_bit_permutation_bijection など

推奨 trace 骨格:

1. Route: bit_manipulation.<exact solver family>
2. Check examples: 1 から 2 行
3. So the rule is <exact executable rule>
4. Query execution
5. Final boxed answer

これなら discussion の factory 発想と、既存 exact-trace generator の両方を維持できる。

ただし v2 に混ぜる順番は重要である。

最初の対象は `bit_structured_byte_formula`、`binary_structured_byte_formula_abstract`、`binary_structured_byte_not_formula` の verified 強 slice に限る。

理由は、current v2 の最大ボトルネックが structured binary であり、同時に boxed behavior を壊さずに内容改善を狙える最も筋の良い差分だからである。

二段目で affine や permutation を足し、二値 boolean や ambiguity を含む slice はさらに後ろへ回す。

## 7. synthetic data 設計への具体的な差し込み点

### 7.1 新しい supervision 軸

今後の合成データでは、既存の answer と generated_cot 以外に、概念上は次の軸を持たせるべきである。

1. route_label
2. route_granularity
3. solver_lock_evidence_style
4. closure_style

最低限、生成時メタデータとして保持し、assistant message には短くシリアライズする。

### 7.2 推奨 style mixture

family や tier に応じて style を混ぜる。

ただし v2 適合では、style mixture は hard family 差分行に限って使い、base v2 全体の style を一斉変更しない。

#### verified_trace_ready

- route_trace_full
- route_trace_short
- route_query_commit

#### answer_only_keep

- route_closure_only
- boxed_only_closure
- route_query_commit

#### manual_audit_priority

- 使用しない

### 7.2.1 v2 適合の混合ルール

mixed corpus は次の順で増やす。

1. base v2 を固定する
2. binary verified route-aware rows を少量追加する
3. binary boxed success が維持されることを確認する
4. その後に symbol numeric verified rows を少量追加する
5. answer_only route rows は最後に低比率で追加する

ここでの原則は、hard family の改善量より先に boxed stability を見ることだ。

### 7.3 推奨 assistant skeleton

full style:

1. Route
2. Check examples
3. Solver lock
4. Query apply
5. Constraints line
6. boxed answer

short style:

1. Route
2. Solver lock
3. Query apply
4. boxed answer

closure-only style:

1. Route
2. Final answer contract
3. boxed answer

ただし v2 に直接混ぜる行では、assistant skeleton は notebook 互換の都合上「generated_cot に boxed answer を持たせない」形式へ変換して保持する。

したがって学習データ生成時の内部 skeleton と、notebook へ渡す実際の `generated_cot` 形式は分けて考える。

## 8. discussion を本当に活かす synthetic 施策

### 8.1 route-only pretraining slice を作る

solve 全体を出させる前に、問題文から family を見抜く短い supervision を混ぜる価値がある。

ただし別タスク化しすぎると本番 prompt と乖離するため、最終的な assistant message の最初の 1 行だけに route を入れる形がよい。

### 8.2 adversarial wrapper augmentation

discussion の価値は wrapper 無視にある。

したがって synthetic では、意味のない framing sentence、operator token variation、question wording variation を加えても同一 hidden rule が維持される augmentation を行う価値が高い。

特に symbol_equation.numeric_2x2 と text_decryption で効く可能性が高い。

### 8.3 operator decorrelation augmentation

numeric_2x2 では同一 rule に対して複数 operator token を割り当てた synthetic prompt を作り、operator token への過剰依存を減らす。

これは discussion の whole point of the factory design と最も直接につながる施策である。

### 8.4 route-consistent mixed-style training

同じ exact rule でも、full trace、short trace、query-commit、closure-only を混ぜる。

目的は 2 つある。

1. 長い trace に依存しすぎないこと
2. boxed close の終端品質を上げること

ただし v2 適合では、mixed-style の導入順も保守的にする。

1. まず `route_trace_short` と `route_query_commit` を使う
2. `route_trace_full` は verified 強 slice に限る
3. `route_closure_only` は answer-only 補助に限定する
4. boxed-only 補助は既存 v1.1 の style mixture と競合しない比率で入れる

## 9. 既存資産との接続

### 9.1 そのまま使えるもの

1. train_row_analysis_v1.csv の family と tier
2. train_verified_trace_ready_v1.csv
3. train_answer_only_keep_v1.csv
4. bit_synth_exact_trace_cot_v1
5. bit_synth_exact_trace_cot_v1_1
6. baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv
7. baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v2.csv
8. baseline/nemotron-sft-lora-with-cot-v2/TRAIN_SPLIT_WITH_COT_V2_STRATEGY.md

### 9.2 追加すべきもの

1. route serialization rule
2. family 別 canonical route templates
3. operator-decorrelation synthetic generator for numeric_2x2
4. wrapper augmentation policy
5. route-aware QC

### 9.3 QC で新しく見るべき点

1. route label と actual solver family が一致するか
2. evidence line が fake になっていないか
3. closure style でも boxed extraction が壊れないか
4. final answer が trace 内へ漏れていないか
5. family 間の mix が偏りすぎていないか
6. binary boxed_extraction_success_rate が v2 基準から悪化していないか
7. binary leading_zero_retention_rate が v2 基準から悪化していないか
8. non-binary high-accuracy family が劣化していないか

## 9.4 v2 適合 QC の主要指標

この plan を v2 に混ぜる際は、少なくとも以下を毎回比較する。

1. overall accuracy
2. binary accuracy
3. symbol accuracy
4. binary boxed_extraction_success_rate
5. binary format_failure_rate
6. binary format_ok_content_wrong_rate
7. gravity / roman / text / unit accuracy

判断ルールは次の通り。

1. binary accuracy が少し伸びても boxed success が大きく落ちる案は不採用
2. binary boxed success が維持され、format_ok_content_wrong が下がる案を最優先する
3. symbol 改善のために easy family が崩れる案は不採用

## 10. 実装優先順位

### Phase 1

baseline v2 互換の binary route-aware augmentation を作る。

理由:

1. exact executable seed が既にある
2. QC の仕組みも既にある
3. structured binary は v2 の最大ボトルネックである
4. boxed success 0.8333 を維持したまま内容改善を狙える

この段階では、base v2 を残したまま structured verified binary の route-aware short trace を差分追加する。

### Phase 2

binary affine / permutation の route-aware verified augmentation を必要なら追加する。

前提条件は、Phase 1 で boxed success が維持されること。

### Phase 3

symbol_equation.numeric_2x2 に operator-decorrelation synthetic を導入する。

ここが discussion の strongest lift 候補である。

### Phase 4

text_decryption verified slice に route_trace、answer-only slice に route_closure_only を導入する。

### Phase 5

roman、unit、gravity の route_trace_short synthetic を必要なら少量作る。

目的は easy family を強く改善することではなく、mixed corpus 内で coarse family route token を完全に欠落させないことにある。

### Phase 6

全 family を混ぜた route-aware mixed corpus を作る。

## 11. 期待される改善仮説

### 11.1 何が改善するか

1. family の誤ルーティングが減る
2. symbol で operator token への過学習が減る
3. binary で exact solver family の呼び分けが安定する
4. boxed close の失敗率が減る

ただし v2 適合の初期フェーズでは、最も現実的な期待値は次である。

1. boxed close は維持
2. binary の content error だけを減らす
3. symbol numeric を限定的に引き上げる

つまり最初から boxed failure 改善を狙うというより、already good な boxed behavior を保持したまま hard family の内容改善を狙う。

### 11.2 何は改善しないか

1. glyph_len5 の latent rule 未解決問題
2. answer-only row の procedure 一意性不足
3. solver library に存在しない genuinely new family

したがって、この approach は万能 solver ではなく、既存 repo がすでに持つ rule inventory をモデル内部へルータ付きで蒸留する手段と位置付けるべきである。

## 12. 最初の具体的成果物

この plan に基づく最初の実装対象は次である。

1. baseline v2 互換の binary route-aware augmentation spec
2. route serialization specification
3. binary boxed-preservation QC memo
4. numeric_2x2 operator-decorrelation synthesis memo
5. family-balanced route-aware training mix memo

## 13. 一言でまとめると

discussion の価値は、長い CoT ではなく、proof-first な family routing をモデルに学ばせる発想にある。

本 repo ではそれを、ledger で安全性が確認された row と exact synthetic seed に限定して、baseline v2 の boxed behavior を壊さない short route declaration plus executable trace の差分教師として混ぜるのが最も筋がよい。