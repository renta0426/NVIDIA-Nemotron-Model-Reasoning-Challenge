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

## 2.2 本 plan で固定するデータスナップショット

この repo では、train 台帳に関する数値が 2 系統存在する。

1. broad snapshot
2. strict training handoff snapshot

前者は `artifacts/selection_summary_v1.csv` および `reports/11_latest_snapshot.md` に対応し、

1. `verified_trace_ready = 6486`
2. `answer_only_keep = 2826`
3. `manual_audit_priority = 164`
4. `exclude_suspect = 24`

である。

後者は `TRAIN_ROW_ANALYSIS_V1_PROVENANCE.md` に対応し、

1. `verified_trace_ready = 6086`
2. `answer_only_keep = 1151`
3. `manual_audit_priority = 2236`
4. `exclude_suspect = 27`

である。

この plan では両者を混同しない。

使い分けは次の通りとする。

1. trace teacher と exact route teacher の基準は strict training handoff snapshot を使う
2. answer-only の拡張余地と manual rescue opportunity の見積もりには broad snapshot も参照する
3. 数値を本文に書くときは、strict 由来か broad 由来かを明示する

これにより、`6486/2826/164/24` と `6086/1151/2236/27` の不整合を放置せず、用途別に整合化する。

## 2.3 この plan の成功条件

v2 適合の観点では、成功条件は次の順で評価する。

1. binary boxed extraction success を `0.8333` 未満へ落とさない
2. binary の format_ok_content_wrong を下げる
3. symbol 全体を引き上げ、その内訳として numeric_2x2 と glyph_len5 の両方に改善ルートを持つ
4. fake trace を増やさずに manual 由来の answer supervision を増やす
5. roman、gravity、text、unit の既存高精度を維持する

つまり「route-aware にしたかどうか」自体は目的ではなく、v2 の勝ち筋を崩さず hard family の中身を改善できたかどうかが目的である。

## 2.4 binary metric bug への運用前提

README.md の現在の評価契約は boxed 抽出優先だが、discussion では binary string が `float()` 経由で decimal 扱いされ、相対誤差 1% tolerance に落ちる可能性が報告されている。

Kaggle Staff は investigate 中なので、この plan では binary を 2 つの見方で同時管理する。

1. official-current proxy: 現在見えている metric 実装に近い proxy
2. exact-string binary correctness: 本来守るべき exact 8-bit string と leading zero の正しさ

したがって binary 改善案は、metric bug に依存して score を稼ぐ前提を置かない。

優先順位は次の通りとする。

1. exact 8-bit string correctness を上げる
2. leading zero を落とさない
3. そのうえで official-current proxy でも悪化しないことを確認する

もし Kaggle 側で bug fix が入った場合でも、この運用なら binary 方針を作り直さずに済む。

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

ただし、これは manual row を一切学習に使わないという意味ではない。

重要なのは、

1. unique trace が無い row に unique trace を書かない
2. 追加検証で query answer だけが一意に潰れる row は answer-only として救済する

であって、manual pool 自体を全放棄することではない。

## 5. この repo における積極的な取り込み方

今回のアプローチを積極的に盛り込むなら、最も重要なのは long CoT を真似ることではなく、既存の ledger と synthetic pipeline に routing field を明示的に差し込むことである。

ただし差し込み先は、新しい単独コーパスではなく baseline v2 の既存 training distribution とする。

言い換えると、この plan の基本戦略は replacement ではなく augmentation である。

### 5.1 基本方針

1. baseline v2 の既存 rows は原則温存する
2. verified_trace_ready は route plus executable trace の差分教師として追加する
3. answer_only_keep は route plus closure-only あるいは query-commit の補助教師として追加する
4. manual_audit_priority は raw のまま trace 化しないが、追加根拠で query answer が一意化できる slice は answer-only へ昇格して使う
5. unresolved manual は training trace source ではなく rescue queue として別管理する
6. exclude_suspect は完全除外する

特に hard family への routing 導入では、既存 v2 の boxed behavior を壊しやすい full replacement を避け、v2 notebook 互換の生成形式に寄せる。

ここでいう manual rescue の対象は、すでに repo 内で筋の良い入口が見えているものに限る。

1. binary の hybrid consensus 系 answer-only
2. binary の structured-byte low-support answer-only
3. symbol numeric の operator-specific consensus answer-only
4. symbol numeric の prompt exact reread answer-only
5. glyph_len5 の将来的な constraint-solver 由来 answer-only

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

さらに binary では route granularity を 2 段に分ける。

1. exact solver がある row には exact route を付ける
2. exact solver が無いが query answer は一意な row には coarse route のみを付ける

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

加えて、次の 2 条件も固定する。

7. internal skeleton 上で boxed answer を想定しても、実際の `generated_cot` には boxed answer を残さない
8. route token 自体の効果は ablation で検証し、効かないなら trace 品質改善を主眼に戻す
9. `max_lora_rank = 32` の容量制約を前提に、route label と style vocabulary は小さい canonical set に制限する
10. no-route exact trace が coarse-route や exact-route と同等以上なら、route は必須要素ではなく optional metadata へ下げる

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
5. Final answer contract

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

ただし、ここは単に operator-decorrelation synthetic を足せば済む family ではない。

現在の symbol 失点は少なくとも 3 つに割れている。

1. operator token を信じすぎる誤り
2. sign / prefix / zero-pad の format branch 誤り
3. single-example tail における prompt-local 非一意性

積極導入すべきポイントは次である。

1. operator symbol を直接信用しない
2. same-op だけでなく output behavior から rule family を読む
3. decorative operator swap を adversarial variation として学習させる

ここでは synthetic data 側で、同一 exact rule を複数 operator token で包んだ prompt を意図的に生成する価値がある。

つまり学習目標は、operator token classification ではなく、example output pattern matching にすることだ。

ただし trace 教師化は verified と strong answer-only に限る。same_operator_example_count が 0 の numeric tail は final-answer supervision に留め、procedure teacher へは上げない。

実装対象は次の 3 層に分ける。

1. strict snapshot の verified numeric rows には route_trace_short を付ける
2. operator-specific consensus や prompt exact reread で answer が一意な rows には route_query_commit あるいは route_closure_only を付ける
3. same_operator_example_count が 0 の tail は route を弱めた final-answer supervision に留める

v2 適合の観点では、symbol は binary よりもさらに保守的に混ぜる。

理由は次の通り。

1. current symbol accuracy は低いが、glyph_len5 が大きく混ざる family でもある
2. operator-decorrelation は numeric_2x2 には効くが、symbol 全体へ広げるとノイズになりうる
3. v2 の broad score を守るには、numeric verified と narrow answer-only に限定して差分注入しつつ、glyph を別トラックで扱う方が安全である

### 6.6 symbol_equation.glyph_len5

この slice は latent rule の一意化ができていないため、discussion 的な solver trace をそのまま積極導入する対象ではない。

ただし、ここを「諦める」と読むのは誤りである。

public eval では `glyph_len5` が `0/20` で、symbol family 崩壊の主因になっている。repo 内 `artifacts/template_summary_v1.csv` でも train 側 `glyph_len5 = 823` 行が確認でき、完全放置のコストは大きい。

現時点の repo 知見は次の通りである。

1. multiset 整合は `70` 行ある
2. order DAG 整合は `46` 行ある
3. exact examples-only では unique latent rule がまだ立たない

したがって方針は 2 本立てにする。

1. training track: coarse route plus answer-only supervision を少量使う
2. research track: constraint solver あるいは Z3 で latent rule 一意化を並列で掘る

ここは route teacher を作るとしても shallow に留める。

推奨:

1. `symbol_equation.glyph_len5.coarse` の coarse route のみ
2. final-answer supervision あるいは boxed-only closure のみ
3. synthetic CoT は、constraint-solver 側で本当に一意化できた後に限る
4. symbol 全体の混合では glyph が numeric を飲み込まないよう比率上限を設ける

### 6.7 bit_manipulation

既存の bit synthetic 路線を核にしつつ、discussion の routing を前置する形が最適である。

現在の bit_synth_exact_trace_cot_v1 と v1.1 は executable trace 側はかなり強いが、family routing を明示的に学ばせる設計ではない。

ここに追加したいのは次の 2 層である。

1. coarse route: bit_manipulation
2. exact route: binary_structured_byte_formula, binary_affine_xor, binary_bit_permutation_bijection など

exact route の canonical set は repo 内 solver family だけで閉じず、discussion で共有された 52-function boolean taxonomy と突き合わせて管理する。

目的は public taxonomy へ寄せること自体ではなく、repo 内 route label が外部知見で説明不能な独自断片へ崩れるのを防ぐことにある。

ただし、binary の主戦場を structured formula だけに縮めるのも誤りである。

実データから見ると、次の 2 つを同時に満たしている。

1. specialized benchmark では structured formula 系が deepest bottleneck である
2. public 60-row slice では `bit_other` が `46/60` を占める

したがって binary branch は 2 正面で進める。

1. structured verified を厚くする深さの改善
2. bit_other exact / consensus / answer-only を増やす幅の改善

推奨 trace 骨格:

1. Route: bit_manipulation.<exact solver family>
2. Check examples: 1 から 2 行
3. So the rule is <exact executable rule>
4. Query execution
5. Final answer contract

これなら discussion の factory 発想と、既存 exact-trace generator の両方を維持できる。

ただし v2 に混ぜる順番は重要である。

最初の対象は `bit_structured_byte_formula`、`binary_structured_byte_formula_abstract`、`binary_structured_byte_not_formula` の verified 強 slice に限らない。

優先対象は次の 3 層とする。

1. structured verified route-aware rows
2. affine_xor / two-bit boolean / permutation / byte transform など bit_other verified route-aware rows
3. hybrid consensus や prompt-local unique answer の answer-only rows

特に `binary_structured_byte_not_formula` は v2 specialized benchmark で最弱級なので、structured verified の中に埋めず explicit priority として扱う。

理由は、current v2 の最大ボトルネックが structured binary である一方、public slice の大半は bit_other であり、片側だけではテスト分布に対して歪な teacher になるからである。

特に重要なのは、exact route が付かない row をゼロ扱いしないことだ。

hybrid consensus のように trace 一意性は無いが query answer は一意な slice は、README.md の Accuracy 前提では strong answer-only source である。

加えて binary track の QC では、metric bug の有無に関わらず `exact_8bit + leading_zero` の正しさを主指標に置く。

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

- raw manual は使用しない
- ただし追加根拠で answer-only へ昇格した manual-origin rows は answer-only lane で使用する

### 7.2.1 v2 適合の混合ルール

mixed corpus は次の順で増やす。

1. base v2 を固定する
2. binary branch と symbol branch は直列ではなく並列で作る
3. binary verified route-aware rows と bit_other verified route-aware rows を同時に追加する
4. binary boxed success が維持されることを確認しつつ、manual-origin answer-only rescue rows を低比率で加える
5. symbol numeric verified と operator-specific answer-only を同時に追加する
6. glyph は coarse answer-only を上限付きで最後に差し込む

ここでの原則は、hard family の改善量より先に boxed stability を見ることだ。

また、delta が小さすぎて学習で吸収される事態を避けるため、比率も固定する。

delta pool 内の初期目安は次の通りとする。

1. binary verified route-aware: `45-55%`
2. binary answer-only rescue: `15-20%`
3. symbol numeric route-aware: `20-25%`
4. symbol numeric answer-only rescue: `10-15%`
5. glyph coarse answer-only: `0-10%`

実数帯も固定する。

repo 内 artifact では `numeric_2x2 verified = 110`、`numeric_2x2 answer_only = 587`、`glyph_len5 answer_only = 823` が確認できるため、初回 delta pool は numeric verified を上限に逆算して `440-550` 行帯で始める。

このときの初回 build target は次の通り。

1. binary verified route-aware: `198-303` 行
2. binary answer-only rescue: `66-110` 行
3. symbol numeric route-aware: `88-110` 行
4. symbol numeric answer-only rescue: `44-82` 行
5. glyph coarse answer-only: `0-55` 行

ここで glyph はゼロでもよいが、入れる場合も numeric を上回らせない。

raw 行数と effective exposure は同一ではない。`+20%` 目標は oversampling や `TYPE_SAMPLES` 側の配分で達成し、初回 delta pool 自体は safe source の上限で制御する。

全体としては、hard-family delta の effective exposure が現行 v2 sampled rows に対して `+20%` を下回らないようにする。少量追加だけで満足する案は不採用とする。

### 7.3 推奨 assistant skeleton

full style:

1. Route
2. Check examples
3. Solver lock
4. Query apply
5. Constraints line
6. internal final answer placeholder

short style:

1. Route
2. Solver lock
3. Query apply
4. internal final answer placeholder

closure-only style:

1. Route
2. Final answer contract
3. internal final answer placeholder

ただし v2 に直接混ぜる行では、assistant skeleton は notebook 互換の都合上「generated_cot に boxed answer を持たせない」形式へ変換して保持する。

したがって学習データ生成時の内部 skeleton と、notebook へ渡す実際の `generated_cot` 形式は分けて考える。

## 8. discussion を本当に活かす synthetic 施策

### 8.1 route-only pretraining slice を作る

solve 全体を出させる前に、問題文から family を見抜く短い supervision を混ぜる価値がある。

ただし別タスク化しすぎると本番 prompt と乖離するため、最終的な assistant message の最初の 1 行だけに route を入れる形がよい。

同時に、route token 自体が本当に効くかを検証するため、少なくとも次の 3 arm を並列比較する。

1. no-route exact trace
2. coarse-route exact trace
3. exact-route exact trace

これで差が出ない場合、route token を目的化せず trace quality と answer-only rescue を主軸に戻す。

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

さらに glyph では `route_trace_full` を禁止し、binary unknown-solver rows でも exact route が無い場合は coarse route plus closure-only へ落とす。

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

ただし提出互換の本線は `versions/v5/code/train_transformers_submission_v5.py` である。

したがって、この plan で作る route-aware delta は v2 augmentation の形で設計しても、最終的には v5 側から読める single-file build artifact として渡す。

言い換えると、v2 は教師分布の出発点であり、submission path は v5 で閉じる。

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
9. route token の有無で hard family が本当に改善しているか
10. glyph の投入量が numeric_2x2 の改善を邪魔していないか
11. manual-origin answer-only rows が fake trace へ化けていないか

## 9.4 v2 適合 QC の主要指標

この plan を v2 に混ぜる際は、少なくとも以下を毎回比較する。

1. overall accuracy
2. binary accuracy
3. symbol accuracy
4. binary boxed_extraction_success_rate
5. binary format_failure_rate
6. binary format_ok_content_wrong_rate
7. binary exact_string_match_rate
8. binary official_current_metric_proxy
9. symbol numeric accuracy
10. symbol glyph accuracy
11. gravity / roman / text / unit accuracy

判断ルールは次の通り。

1. binary accuracy が少し伸びても boxed success が大きく落ちる案は不採用
2. binary boxed success が維持され、format_ok_content_wrong が下がる案を最優先する
3. symbol 改善が numeric だけで glyph が据え置きの案は、glyph track を別に持たない限り不完全とみなす
4. symbol 改善のために easy family が崩れる案は不採用

## 10. 実装優先順位

### Track A: binary depth and width

baseline v2 互換の binary route-aware augmentation を作る。

理由:

1. exact executable seed が既にある
2. QC の仕組みも既にある
3. structured binary は v2 の最大ボトルネックである
4. public slice では bit_other の占有率も高く、幅の改善も同時に必要である
5. boxed success 0.8333 を維持したまま内容改善を狙える

この track では、base v2 を残したまま次を並列で差分追加する。

1. structured verified binary の route-aware short trace
2. bit_other verified binary の route-aware short trace
3. hybrid consensus など manual-origin answer-only rescue

### Track B: symbol numeric

symbol_equation.numeric_2x2 に operator-decorrelation と operator-specific answer-only rescue を導入する。

ここでの主眼は、operator token の decorrelation だけではなく、format branch の揺れを減らすことにある。

### Track C: glyph research and bounded supervision

glyph_len5 は coarse answer-only supervision を少量使いながら、constraint solver / Z3 による latent rule recovery を別トラックで進める。

ここは「後回し」ではなく「trace 化を急がない parallel research target」として扱う。

### Track D: easy-family stabilization

text_decryption verified slice に route_trace、answer-only slice に route_closure_only を導入する。

roman、unit、gravity の route_trace_short synthetic は必要になった場合だけ少量使う。目的は easy family を強く改善することではなく、mixed corpus 内で coarse family route token を完全に欠落させないことにある。

### Track E: all-family integration

上記 track を直列完了待ちせず、並列で回した上で最終 mixed corpus を作る。

## 11. 期待される改善仮説

### 11.1 何が改善するか

1. family の誤ルーティングが減る
2. symbol で operator token への過学習が減る
3. binary で exact solver family の呼び分けが安定する
4. binary の unknown-solver 領域でも query-commit answer-only が効く
5. glyph_len5 を放置したまま symbol 全体が止まる事態を避けられる

ただし v2 適合の初期フェーズでは、最も現実的な期待値は次である。

1. boxed close は維持
2. binary の content error を structured と bit_other の両方で減らす
3. symbol numeric を引き上げる
4. glyph はまず 0 点固定からの脱出ルートを作る

つまり最初から boxed failure 改善を狙うというより、already good な boxed behavior を保持したまま hard family の内容改善を狙う。

### 11.2 何は改善しないか

1. answer-only row の procedure 一意性不足そのもの
2. solver library に存在しない genuinely new family
3. glyph_len5 の完全解決を短期で保証すること

したがって、この approach は万能 solver ではなく、既存 repo がすでに持つ rule inventory をモデル内部へルータ付きで蒸留する手段と位置付けるべきである。

ただし glyph については、未解決だから除外するのではなく、answer-only supervision と solver research を分離して進める。

## 12. 最初の具体的成果物

この plan に基づく最初の実装対象は次である。

1. baseline v2 互換の binary route-aware delta builder single file
2. route serialization specification
3. binary boxed-preservation and exact-string QC single file
4. numeric_2x2 operator-decorrelation builder single file
5. glyph_len5 constraint-solver feasibility memo
6. manual-origin answer-only rescue ledger
7. family-balanced route-aware mix manifest compatible with `versions/v5/code/train_transformers_submission_v5.py`

## 13. 一言でまとめると

discussion の価値は、長い CoT ではなく、proof-first な family routing をモデルに学ばせる発想にある。

本 repo ではそれを、ledger で安全性が確認された row と exact synthetic seed に限定して、baseline v2 の boxed behavior を壊さない short route declaration plus executable trace と、manual-origin answer-only rescue の二層教師として混ぜるのが最も筋がよい。