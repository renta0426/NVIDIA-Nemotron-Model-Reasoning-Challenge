# v10 BIT mainline strategy 2026-04-23

> 目的: v10 を、BIT 大幅改善に向けた本命 Run として設計し、official leaderboard `0.87` 到達を狙う。
> 起点: `versions/v20_to_088_reassessment_2026-04-18.md` の 15 節「BIT 大幅強化に向けた使用可能資産の棚卸し」。
> 一次根拠: `README.md`, `A-Open-ProgressPrizePublication/README.md`, `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`, `cuda-train-data-analysis-v1/BIT_MANIPULATION_STRONG_GROUP_SYNTHESIS_REFERENCE.md`, `versions/v20_corrective_corpus_v6_mainline/v20_corrective_corpus_v6_mainline-results.md`, `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7-1_reassessment_2026-04-22.md`, `versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md`。

## 1. 先に結論

v10 の主戦略は、**`v4` 系 public-safe backbone を token-safe に固定したまま、`v6` 系の BIT gain と新しい frontier lane だけを狭く重ねる mixed mainline** である。

今回やるべきことは、binary の総量をさらに増やすことではない。README が示す通り、勝ち筋は

- bit_manipulation を主戦場に置くこと
- deterministic chain-of-thought を保つこと
- boxed-first extraction 契約を壊さないこと
- tokenization weakness を無視しないこと

の 4 点にある。したがって v10 は、次の 3 点を同時に満たす run でなければならない。

1. `v4` が持っていた public-safe な answer surface を失わないこと
2. `v6` が見せた BIT content gain を public mainline 側へ移植すること
3. persistent hard core に対して、既存の family-level exact pack ではなく query-specific frontier teacher を追加すること

言い換えると、v10 は `v8` のような teacher architecture 置換ではない。**`v4_public_base` を土台に残し、`v6` と audited binary ledger を donor に使い、足りない frontier だけを新規作成する run** である。

## 2. README から外してはいけない制約

`README.md` と `A-Open-ProgressPrizePublication/README.md` から、v10 の設計制約はかなり明確である。

1. 評価は deterministic decoding で行われる
   - `temperature = 0.0`
   - `top_p = 1.0`
   - `max_tokens = 7680`
   - `max_model_len = 8192`

2. 評価契約は boxed-first extraction である
   - final answer は `\boxed{}` が最優先
   - 箱が壊れると fallback が働いても hidden/public で不利になりやすい

3. 最大の差分源は bit_manipulation である
   - A-Open README は bit を main upside と明言している
   - easy family の完全性は重要だが、0.87 へ押し上げる主レバーではない

4. より高い solve rate には programmatic insight が要る
   - ratio tuning だけでは足りない
   - broad exact expansion だけでも足りない
   - deterministic teacher を frontier-specific に作り直す必要がある

従って v10 の設計原則は、次の一文に集約できる。

**bit の correctness を上げる設計変更だけを mainline に入れ、surface は壊さないために最低限の guardrail を厚く残す。**

## 3. ここまでの実測が示したこと

### 3.1 スコア一覧

| version | validation | proxy | proxy binary | official leaderboard | 読み |
| --- | ---: | ---: | ---: | ---: | --- |
| `v20` | `837/950 = 0.8811` | `176/200 = 0.8800` | `76/92 = 0.8261` | `0.84-0.85` | A-Open winning line の再現基準 |
| `v4_mainline` | `813/950 = 0.8558` | `179/200 = 0.8950` | `79/92 = 0.8587` | `0.85-0.86` | この系列の best public |
| `v6_mainline` | `829/950 = 0.8726` | `180/200 = 0.9000` | `80/92 = 0.8696` | `0.83-0.85` | strongest BIT donor, ただし public blind spot |
| `v7-1` | `839/950 = 0.8832` | `178/200 = 0.8900` | `78/92 = 0.8478` | `0.84` | token-safe repair, frontier gain なし |
| `v8` | `834/950 = 0.8779` | `178/200 = 0.8900` | `78/92 = 0.8478` | `0.83-0.84` | data-policy miss |

この表から v10 の前提は 4 つに絞られる。

1. `v4` を超えない限り public mainline にはなれない
2. `v6` は mainline ではないが、BIT donor としては最重要である
3. `v7-1` の local 改善は主に numeral 回復であり、frontier 解決ではない
4. `v8` は symbol と short exact の比率を上げても BIT も public も伸びないことを示した

### 3.2 失敗から分かった設計上の禁止事項

`v7`, `v7-1`, `v8` を通すと、mainline でやってはいけないことは明確である。

1. `v4_public_base` を text 再生成や別 base snapshot で置き換えること
   - `v7` は retokenization で崩壊した
   - `v8` は token bug ではないが、v4 dominant donor mix 自体を外して public を悪化させた

2. symbol lane に mainline 予算を厚く張ること
   - `v4`, `v6`, `v7-1`, `v8` の symbol proxy はすべて `24/32`
   - `v8` は `96 unique + 192 repeated` を symbol に使っても `0` 行しか動かなかった

3. easy guardrail を削って BIT へ振り切ること
   - `v6` では numeral no-box
   - `v8` では boxed されたまま Roman numeral が `0` へ drift
   - README の boxed-first 契約と真っ向から衝突する

4. manual 全体を trace teacher 化すること
   - `FINAL_SUMMARY_REPORT.md` は `manual_audit_priority` の raw CoT 化を明確に非推奨としている
   - manual は frontier 再審査対象であり、そのまま教師集合ではない

## 4. v10 の支配仮説

v10 の仮説は単純で、しかも falsifiable である。

**`v4` の public-safe token distribution を維持したまま、`v6` の BIT donor と新規 frontier lane を narrow に追加すれば、`v6` の binary gain を維持しつつ `v4` の public edge を失わない。**

これが誤りなら、v10 は少なくとも次のどちらかで失敗する。

1. proxy binary は上がるが public が `v4` を超えない
2. public は維持されても proxy binary が `80/92` に届かない

したがって v10 の可否は、次の組み合わせで判定できる。

- public: `0.86` 安定ではなく `0.87` 接触が見えるか
- proxy binary: `81/92` を最低、理想は `82/92` 以上か
- easy-family regression: numeral / unit / gravity / cipher の boxed tail を落としていないか

## 5. v10 で使う資産

### 5.1 Backbone

mainline backbone は `v4_public_base` 系を使う。ここは変更しない。

理由:

- `v4` はこの corrective family の best public
- `v7-1` でも価値があったのは text 入替ではなく token-safe reuse の回復だった
- `v8` は `04-08-16-14` base + synthetic overlay に戻して public を落とした

v10 では backbone について次を固定条件とする。

1. `v4_public_base` は token-safe に再利用する
2. donor の row text 再生成で public-safe supervision を壊さない
3. backbone の easy-family surface mass を縮めすぎない

### 5.2 BIT verified donor

BIT 側の raw material は十分ある。

- final ledger: `1602` rows
- `verified_trace_ready = 1229`
- `answer_only_keep = 271`
- `manual_audit_priority = 87`
- `exclude_suspect = 15`

さらに large-scale synthesis の reusable seed も既にある。

- solver-native synthesis seed: `1004`
- exact-trace-safe subset: `817`

group 別には次が中心である。

- `binary_structured_byte_formula`: `446`
- `binary_structured_byte_formula_abstract`: `152`
- `binary_structured_byte_not_formula`: `25`
- `binary_two_bit_boolean`: `135`
- `binary_three_bit_boolean`: `17`
- `binary_affine_xor`: `133`
- `binary_bit_permutation_bijection`: `78`
- `binary_bit_permutation_independent`: `7`
- `binary_byte_transform`: `11`

この意味は重要である。**v10 に必要なのは BIT データ探索ではなく、既存 verified asset の再編成である。**

### 5.3 Hard-core donor としての `v6`

`v6` が見せた価値は次である。

- proxy `180/200`
- proxy binary `80/92`
- `c30a782a`, `59c78e51` のような earlier runs では弱かった row を回収
- `format_ok_content_wrong_rate = 0.1209`

dataset composition も v10 への移植単位として分かりやすい。

- `binary_structured_exact_core: 168 unique / 341 repeated`
- `binary_logic_exact: 56 unique / 114 repeated`
- `binary_permutation_exact: 48 unique / 98 repeated`
- `binary_prompt_local_exact: 64 unique / 64 repeated`
- `anti_default1_commit: 9`

ただし `v6` をそのまま mainline にしてはいけない。

理由:

- public は `v4` を超えなかった
- numeral `11` 行が no-box で落ちた
- persistent binary hard core `11` 行が残った

従って v10 では `v6` を **public mainline ではなく narrow binary donor** として使う。

## 6. v10 の corpus architecture

v10 は 5 lane 構成にする。

### Lane 0. Public-safe backbone

役割:

- `v4` 系 public-safe token distribution を維持する
- easy family の boxed terminal surface を保持する
- mixed mainline の中心 mass を安定化する

ルール:

- token-safe reuse を mandatory にする
- 別 base snapshot への置換をしない
- overlay 側だけを更新する

### Lane 1. Exact BIT core donor

対象:

- `binary_structured_exact_core`
- `binary_logic_exact`
- `binary_permutation_exact`
- `binary_prompt_local_exact`

役割:

- `v6` で確認された content gain を移植する
- README の deterministic exact teacher 方針を mainline に戻す

v10 での方針:

- structured だけでなく permutation/bijection の比重を `v6` より上げる
- family abstraction だけで終わる例を減らし、query-specific closure を厚くする
- prompt-local は teacher-feasible row だけを trace 化する

### Lane 2. Frontier hard-core lane

これが v10 の新規性であり、本命部分である。

対象は、少なくとも次の 3 群である。

1. persistent proxy hard core `11` 行
   - `012fb81b`
   - `01e09228`
   - `101410e4`
   - `12154247`
   - `12fd5b6c`
   - `1532c0d1`
   - `2230fad0`
   - `257e7158`
   - `2d790c98`
   - `31966698`
   - `a6192d29`

2. public-sensitive regression anchors
   - `c30a782a`
   - `13009e35`
   - `069dbaab`
   - `0a50c4a8`
   - `0dd5caf4`
   - `13c8ae90`
   - `26a70ae0`
   - `6a333ed6`

3. highest-priority manual bit_other queue
   - audit priority `14.5` の `bit_other` 群
   - まず `069dbaab`, `101410e4`, `12154247`, `2230fad0`, `257e7158` を最優先に扱う

Lane 2 の原則:

1. manual を一括 CoT 化しない
2. query-specific exact closure が立つ行だけ trace teacher にする
3. exact closure が立たないが gold が clean な行は answer-only / contrastive closure に留める
4. `default 1` への逃避を狙い撃つ contrast pair を作る

### Lane 3. Anti-`default 1` contrast lane

`v20`, `v4`, `v5a` から `v6` まで、binary wrong rows の主 failure mode は `default 1` だった。v6 でも `anti_default1_commit` は `9` 行までしか入っていない。

v10 ではここを独立 lane として強化する。

対象:

- `bit_other` hard rows
- `bit_structured_byte_formula` persistent misses
- `answer_only_keep` に安全に留める narrow hybrid consensus rows

作り方:

1. positive pair
   - exact rule を適用すると gold になる row

2. negative pair
   - superficially similar だが `default 1` が誤りになる row

3. final closure
   - 「なぜ `1` 埋めではなくこの bit patternか」を query の末尾で確定する短い exact closure

ここは broad family coverage ではなく、**wrong default を出したくなる局面の反例教育**に徹する。

### Lane 4. Surface guardrail

v10 の surface lane は cheap だが削ってはいけない。

最低限残すもの:

- numeral boxed closure
- cipher boxed closure
- unit tail stabilization
- gravity fragile tail
- minimal symbol-prefix repair

v8 の反省を踏まえ、ここは `v6` より薄くしない。少なくとも v6 相当、できれば少し厚めに戻す。

理由:

- `v6` は no-box debt を残した
- `v8` は boxed のまま answer-space drift を起こした
- public blind spot は binary だけではなく extraction-sensitive slice を含んでいる

## 7. v10 で増やすべきもの、切るべきもの

### 7.1 増やすべきもの

1. permutation / bijection lane
   - `v5a` と `v8` はここが薄かった
   - `binary_bit_permutation_bijection = 78`, `binary_bit_permutation_independent = 7` は mainline で薄く扱いすぎていた

2. query-specific structured-byte closure
   - abstract family 名だけでは hard row が消えない
   - `bit_structured_byte_formula = 830` と母数が大きく、public 影響も重い

3. prompt-local exact reread lane
   - prompt-backed manual exact reread は `+62 verified` の実績がある
   - ただし teacher-feasible row のみに限定する

4. anti-`default 1` repeated commit
   - `9` 行では足りない
   - v10 では hard watchlist を覆える密度まで増やす

5. guardrail repeated rows
   - v8 はここを削りすぎた
   - mainline では token mass として十分残す

### 7.2 mainline から切るべきもの

1. broad symbol exact lane
   - measured return が `0`
   - 本命 run の予算配分先ではない

2. manual mass-CoT
   - `FINAL_SUMMARY_REPORT.md` の運用ルールに反する
   - 教師汚染の危険が高い

3. answer-only の full reasoning teacher 化
   - `answer_only_keep` は final-answer supervision に限定する
   - trace teacher と混同しない

4. bit token representation 変更
   - base64 / nibble 圧縮は README 上の将来候補ではある
   - ただし v10 本流へ入れると解釈不能になる
   - これは v10 ではなく side branch に送る

5. matching / token-skill の broad 復帰
   - 診断枝としては意味がある
   - しかし v10 mainline の主要差分にしてはいけない

## 8. v10 の具体配分

v10 の unique overlay は、v8 のような 78.93% BIT / 16.05% symbol / 5.02% guardrail ではなく、次の配分を推奨する。

- BIT exact + frontier: `88-90%`
- surface guardrail: `10-12%`
- symbol mainline: `0%`

ただし、ここで言う BIT `88-90%` は broad exact expansion ではない。内訳を分ける。

- `40-45%`: structured exact core
- `15-18%`: permutation / bijection / independent
- `12-15%`: prompt-local exact
- `10-12%`: anti-default1 contrast
- `10-12%`: frontier query-specific hard-core lane

guardrail は少なくとも次を確保する。

- numeral boxed lane は `v8` の `18` より明確に厚くする
- symbol-prefix minimal repair は `0` にしない
- repeated surface tail は `v6` 相当以上を維持する

token mass の目安も置いておく。

1. `v8` のように総 tokens を `28.2M` まで縮めない
2. `v7-1` のような `32.9M` フル mass までは戻さなくてもよいが、surface debt を起こさない範囲を守る
3. 実務上は `30M` 前後を中心に、short closure と guardrail の両立を狙う

## 9. v10 の評価ゲート

v10 は aggregate score だけで昇格させてはいけない。README 契約とこれまでの blind spot を踏まえ、少なくとも 5 つの gate を置く。

### Gate 1. Public-risk mini gate

含めるもの:

- `v4 > v6` だった hidden-sensitive slice
- numeral no-box rows
- boxed Roman -> `0` drift rows
- `c30a782a`, `13009e35`, `069dbaab` など public-sensitive binary rows

条件:

- v4 より悪化しない

### Gate 2. Proxy binary gate

条件:

- minimum: `81/92`
- target: `82/92`
- ideal: `83/92`

### Gate 3. Content-vs-format gate

条件:

- binary `format_failure_rate` は `v6` 以下を維持
- `format_ok_content_wrong_rate` は `v6 = 0.1209` を超えない

ここで format failure を下げるだけでは不十分で、content drift も悪化させないことが必要。

### Gate 4. Easy-family guardrail gate

条件:

- numeral の boxed drift を起こさない
- unit `171/171` 維持
- gravity / cipher の validation debt を増やさない

### Gate 5. Hard watchlist gate

条件:

- persistent hard core `11` 行のうち複数を改善する
- `c30a782a`, `13009e35`, `069dbaab` を regress させない
- `0a50c4a8`, `0dd5caf4` のような anchor を再度落とさない

## 10. 実務的な v10 build order

v10 を組む順番も重要である。順番を誤ると、また「何が効いたのか分からない mixed run」になる。

1. `v4_public_base` token-safe backbone を固定する
2. `v6` donor から、BIT gain が測定済みの pack だけを移植する
3. ledger から `verified_trace_ready` を中心に frontier hard-core pack を作る
4. `answer_only_keep` は final-answer stabilizer と anti-default1 negative pair に限定して使う
5. minimal surface guardrail を v6 以上に積む
6. symbol mainline lane は入れない

ここで重要なのは、**frontier lane 以外は新規発明しない**ことである。mainline の未知部分を最小化する。

## 11. v10 の採用基準

v10 を本命として採用する最低条件は次に置く。

1. official leaderboard で `0.86` 安定ではなく、`0.87` 接触が見えること
2. proxy binary `82/92` 以上が見えること
3. public-risk mini gate で `v4` を下回らないこと
4. hard watchlist で net positive が出ること
5. numeral / unit / gravity / cipher で明確な regression を起こさないこと

逆に、次の形なら不採用である。

1. `v6` 型
   - proxy は強いが public が伸びない

2. `v7-1` 型
   - validation は上がるが bit frontier は進まない

3. `v8` 型
   - short exact と symbol 配分を増やしたのに、bit も public も伸びない

## 12. 最終判断

v10 で必要なのは、これ以上の broad exploration ではない。必要なのは、既に揃っている asset を **public-safe backbone / exact BIT donor / frontier hard-core lane** に分け直すことだ。

最も重要な変更点は次の 4 つである。

1. `v4_public_base` を mainline の中心に戻す
2. `v6` を public mainline ではなく BIT donor として限定利用する
3. `1229 verified` と `1004 synthesis-stable seed` を使って BIT major lane を再設計する
4. persistent hard core と anti-`default 1` に、query-specific frontier teacher を新規投入する

つまり v10 は、

**「v4 の public-safe distribution を保ちながら、v6 の BIT gain と audited ledger の frontier pack を narrow に追加する、本命の mixed mainline」**

として設計するのが最も筋が良い。

official `0.87` を狙うなら、ratio tuning の延長ではなく、この形で踏み込むべきである。