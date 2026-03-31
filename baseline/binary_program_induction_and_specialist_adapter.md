# Binary Program Induction and Specialist Adapter Plan

## 0. この文書の位置づけ

この計画書は、以下の既存整理を前提にした次段階の実行計画である。

- `README.md`
- `baseline/binary_bit_manipulation_difficulty_report_2026-03-29.md`
- `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md`
- `baseline/cot/train_rule_based_cot_baseline.ipynb`
- `discussion/ How did you resolve these problems by human?.md`
- `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`

最重要の前提は `README.md` である。  
このコンペは Nemotron-3-Nano-30B + LoRA adapter を `vLLM` で推論し、最終スコアは **Accuracy** で決まる。最終答えは `\boxed{}` を優先抽出し、失敗時は他ヒューリスティックや最後の数値にフォールバックする。binary family ではこの仕様が特に厳しい。`00110100` のような 8-bit string は、途中 reasoning がそれっぽくても最後の boxed answer が崩れた時点で即失点になる。  
参照: `README.md`

---

## 1. 先に結論

この課題に対する次の主戦略は、**binary-first だが binary-only ではない**。

つまり、

1. **official-like な評価系を先に固定する**
2. **現行 notebook の学習 plumbing を直す**
3. **binary を natural-language CoT ではなく program induction として再設計する**
4. **ただし 0.9 を狙うには symbol 側の監視も切らない**
5. **specialist adapter + merge は有望だが、plumbing 修正より後に置く**

という順で進める。

この順番が重要である。  
いきなり merge, synthetic, RL へ進むのではなく、まず現行 baseline のボトルネックが

- 評価ミスマッチ
- 学習 objective のズレ
- binary 教師の形式不足
- multi-task interference

のどこにあるかを official-like に観測できるようにする。

---

## 2. 既存資料から見える確定事項

### 2.1 README が binary に厳しい

`README.md` の評価仕様では、

- score は Accuracy
- `\boxed{}` が最優先で抽出される
- boxed が壊れると fallback 抽出に落ちる
- binary は数値誤差救済ではなく **exact string** 寄り

である。

したがって binary では

- rule discovery
- query への適用
- 8-bit fixed string の維持
- final boxed closure

の全てが必要になる。

### 2.2 rule-based 600 の主失点は binary

`baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md` では、30 サンプル中 24 正解、失点 6 件のうち 5 件が binary だった。しかも多くは `1`, `001`, `-0`, `10` のような **短い断片抽出** で落ちている。

つまり binary の主問題は「全く解けていない」だけではなく、

- output contract の弱さ
- boxed/fallback failure

が強く効いている。

### 2.3 binary は curated されても trace-safe 教師が潤沢ではない

`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` の最終値では、

- overall safe core: `6486 verified_trace_ready + 1397 answer_only_keep = 7883`
- binary: `1004 verified / 281 answer_only / 302 manual / 15 exclude`

である。

これは binary が

- curated total は増えた
- しかし trace-safe 教師はまだ限定的
- manual や weak rows を雑に CoT 化すると危険

であることを意味する。

### 2.4 現行 notebook には high-ROI な修正点が残っている

`baseline/cot/train_rule_based_cot_baseline.ipynb` では、

- `tokenizer.apply_chat_template(...)` で user + assistant 全文を 1 つの `text` にする
- `SFTTrainer(..., dataset_text_field="text")` で学習する
- completion-only / assistant-only loss mask は入っていない
- `target_modules="all-linear"` で rank 32 の単一 LoRA を全体に当てる

という形になっている。

つまり今の baseline は、binary 専門設計へ進む前に、

- assistant-only loss
- template 整合
- update 範囲の見直し

だけで改善余地がある。

### 2.5 discussion は raw manual 教師化の危険を示している

`discussion/ How did you resolve these problems by human?.md` に出てくる unseen operator や hallucination 疑いの問題は、

- 人間でも puzzle としてかなり厳しい
- prompt exact reread や reverse-digit 型 reasoning が必要
- 一部は raw のまま一般化教師にしにくい

ことを示している。

よって `manual_audit_priority` を raw synthetic CoT 付きで一括投入する方針は避ける。

---

## 3. この計画の設計原則

## 原則1: eval-first

leaderboard だけ見ていると、

- binary reasoning が改善したのか
- binary formatting だけ改善したのか
- general family が壊れたのか

を区別できない。

したがって、まず official-like な offline eval を固定する。

## 原則2: binary-first, symbol-aware

binary は最大の壁だが、`FINAL_SUMMARY_REPORT.md` を見る限り `symbol_equation` も大きな残課題である。  
0.9 を binary だけで取り切れる保証はない。

したがって、

- binary を主対象にする
- ただし symbol watch set を常に並走させる

という運用にする。

## 原則3: plumbing before sophistication

最初に直すべきは、

- assistant-only loss
- train/infer template 整合
- curated mix 設計
- format hardening

であり、merge, synthetic, RL はその後である。

## 原則4: verified と answer-only を役割分離する

- `verified_trace_ready` は trace 教師の本体
- `answer_only_keep` は final answer / formatting 安定化用
- `manual_audit_priority` はそのまま CoT 化しない
- `exclude_suspect` は使わない

この線引きは維持する。

## 原則5: binary は自然文 CoT ではなく executable scratchpad

binary の本質は「ルール名を言えること」ではない。  
必要なのは、I/O examples から latent byte-function を読み取り、query に適用し、8-bit exact answer を boxed で閉じることである。

したがって binary 教師は、

- 長い自然文
- 雰囲気説明

よりも、

- rule
- query apply
- result

が短く構造化された scratchpad を優先する。

---

## 4. やらないこと

この文書では、次を現時点の非推奨事項とする。

1. **manual 全件への一括 synthetic CoT 付与**
2. **binary 300 行置換のような強い単発 mixed SFT**
3. **eval 固定前の merge 最適化**
4. **assistant-only loss 未修正のまま RL/DPO に進むこと**
5. **easy synthetic binary の大量水増し**
6. **binary だけ解ければ 0.9 に届くと仮定すること**

---

## 5. 改訂後の実行順

## Phase 0. Official-like offline eval を固定する

最優先。ここをやらずに次へ進まない。

### 0-1. 全体指標

毎回最低限出すもの:

- overall accuracy
- family 別 accuracy
- template_subtype 別 accuracy
- answer type 別 accuracy
- prompt 長 / example 数別 accuracy

### 0-2. binary 専用指標

- boxed 抽出成功率
- extracted answer が `^[01]{8}$` を満たす率
- 先頭ゼロ保持率
- format failure 率
- format OK だが中身誤り率
- solver family 別精度

### 0-3. 干渉監視セット

毎回同じ 3 セットで見る:

- `General Stable Set`
- `Binary Hard Set`
- `Symbol Watch Set`

### 0-4. holdout 設計

random split ではなく、binary は少なくとも次を用意する。

- `bit_structured_formula_abstract_family` holdout
- `teacher_solver_candidate` holdout
- gap structure holdout
- prompt signature holdout

### 0-5. official 寄せ

評価条件は README に寄せる。

- `temperature = 0.0`
- `top_p = 1.0`
- boxed-first extraction
- final answer grading を README 準拠で再現

---

## Phase 1. 学習 plumbing を直して再ベースライン

ここは binary 専門設計より前に実施する。  
最も ROI が高い。

### 1-1. assistant-only loss へ変更

現行 notebook は user + assistant を連結した `text` に対して全文 SFT をしている。  
まずこれを、assistant completion のみに loss が乗る形へ修正する。

狙い:

- prompt token の学習浪費を減らす
- final boxed answer の学習密度を上げる
- binary の exact closure を強める

### 1-2. train/infer template を整合させる

学習時と推論時で chat template, thinking mode, generation prompt の形がズレると、

- final answer style drift
- `<think>` 境界の不安定化
- binary boxed failure

が起きやすい。

したがって、学習時テンプレートは推論時にできるだけ揃える。

### 1-3. 600 件均等 baseline を卒業する

旧 600-row は比較用 baseline としては有用だったが、次段階では狭すぎる。

次に使う mixture は少なくとも

- `verified_trace_ready`
- `answer_only_keep`
- family anchor rows
- binary format hardening rows

を役割分離して混ぜる。

### 1-4. answer-only の使い方を分ける

answer-only は全て同じ扱いにしない。

- binary answer-only: boxed-only か ultra-short
- easy family replay: short stable completion
- text/symbol: exact answer closure を壊さない短形式

### 1-5. update 範囲の比較を入れる

`all-linear` 一本ではなく、少なくとも次を比較する。

- all-linear
- attention-only
- MLP-only
- upper layers only

狙いは、binary を上げつつ non-binary を壊しにくい更新範囲を見つけること。

### Phase 1 の成功条件

- overall が baseline より改善
- binary format failure が低下
- General Stable Set を壊さない
- Symbol Watch Set の大崩れがない

---

## Phase 2. binary 教師を program induction 用に作り直す

Phase 1 の後に着手する。

### 2-1. verified binary は短い DSL を既定値にしない

`baseline/cot/phase0_offline_eval/result/1/reports/phase1_result1_deep_analysis.md` と  
`baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md` を踏まえると、Phase 2 の短い DSL scratchpad は **format collapse を少し減らしたが、verified / structured-byte-formula slice の直接改善には届かなかった**。  
特に `result/2` では

- `verified_trace_ready`: `8/20 -> 7/20`
- `answer_only_keep`: `3/20 -> 2/20`
- `structured byte formula`: 依然 `0/14`

であり、短い構造化形式を次の既定値にする根拠は弱い。

したがって次段階では、binary verified rows を **bare DSL ではなく compact narrative / hybrid trace** に切り替える。

イメージ:

```text
<think>
The examples support the verified binary rule xor(rol1(x), shl2(x)).
I apply the same byte transformation to query 00110100.
Useful intermediate bytes are rol1(query)=01101000 and shl2(query)=11010000.
I keep the result as one exact 8-bit string with leading zeros and will place only that final byte in the box.
</think>

\boxed{10111000}
```

大事なのは、

- rule 名だけで終わらない
- query apply を明示する
- 必要なら中間 byte を 1-2 個だけ見せる
- 8-bit exactness を保つ
- final answer は `<think>` 内に再掲しない

ことである。

### 2-2. binary answer-only は boxed-only を基本にする

`answer_only_keep` へ雑な synthetic CoT を足さない。

基本形:

```text
\boxed{00110100}
```

または必要最小限:

```text
<think>Apply the verified rule to the query.</think>

\boxed{00110100}
```

### 2-3. no-answer-leak を守る

binary では `<think>` 内に最終 8-bit answer を再掲しない設計も有効である。  
README の boxed-first extraction を考えると、数字断片を増やしすぎない方が安全な場合がある。

### 2-4. binary holdout で再評価する

改善判定は random holdout ではなく、

- formula family holdout
- solver family holdout
- hard slice holdout

で行う。

### Phase 2 の成功条件

- binary verified slice の accuracy 改善
- 8-bit regex exact 率の改善
- 先頭ゼロ保持率の改善
- format collapse (`1`, `10`, `001`, `-0`) の減少

### 2-5. Phase 2 失敗後の次計画

次に notebook で試すべきなのは、**データ集合や assistant-only plumbing は維持しつつ、binary trace だけを hybrid trace に差し替える実験** である。

順番は次の通り。

1. raw DSL を既定値から外す
2. binary verified を compact narrative / hybrid trace に変える
3. binary answer-only は boxed-only のまま維持する
4. Phase 1 と同じ general mixture を壊さないかを再監視する

この方針なら、

- README 準拠の boxed-first 評価を意識した output contract は維持できる
- short DSL 仮説だけを切り戻せる
- 失敗時も specialist / merge へ進む前に原因を切り分けられる

---

## Phase 3. specialist adapter を分離して merge する

これは有望だが、Phase 1 と Phase 2 の後で行う。

### 3-1. Adapter G: general

用途:

- easy family の安定維持
- text / gravity / unit / roman の replay
- boxed formatting の全体安定化

### 3-2. Adapter B: binary specialist

用途:

- binary verified hybrid trace
- binary answer-only format hardening
- 必要に応じて binary synthetic

### 3-3. Adapter S: symbol specialist

binary 改善後も 0.9 に届かない場合の次手。  
最初から必須とは限らないが、設計としては作れるようにしておく。

### 3-4. merge 方法

候補:

- linear / SVD
- TIES
- DARE + TIES

外部根拠:

- TIES は sign conflict と redundant delta を処理して merge 干渉を下げる
- DARE は delta sparsification を通じて merge 前処理として有効

### 3-5. 注意点

- 同一 base model を前提にする
- tokenizer / special token を揃える
- merge weight は validation で探索する
- rank<=32 制約に最終的に収まる形で圧縮する

### Phase 3 の成功条件

- binary gain がある
- general family retention がある
- merge 後の総合点が source adapter を上回る

---

## Phase 4. synthetic binary を投入する

Phase 3 までで方向が合っていることを確認してから着手する。

### 4-1. 何を生成するか

verified DSL family から、real-like prompt 形式の synthetic puzzle を作る。

必要条件:

- 7-10 examples
- query 1 本
- 8-bit I/O
- real に近い prompt surface
- leading zero を十分含む
- near-miss hard cases を含む

### 4-2. 何を生成しないか

- easy rule だけの大量複製
- manual rows を無理に正解化した synthetic
- answer leakage を含む trace

### 4-3. 学習上の位置づけ

synthetic は general adapter に大量混入しない。  
まずは binary specialist に限定して使う。

### 外部根拠

ARC 系では free-form CoT 単発より search / synthesis / verification を伴う系が強い。  
SOAR のような self-improving program synthesis 系は、program induction 型タスクに対して search loop の有効性を示している。

### Phase 4 の成功条件

- binary hard slice の改善
- formula holdout での generalization 改善
- non-binary side effect が小さい

---

## Phase 5. RL / preference 学習は最後に使う

RL/DPO は方針としては正しいが、最後でよい。

### 5-1. 向いている対象

binary は verifiable task なので reward を自動化しやすい。

候補 reward:

- exact answer
- boxed success
- `^[01]{8}$`
- trailing numeric noise penalty

### 5-2. DPO/ORPO の向き先

format collapse が主なら、

- 正例: `\boxed{00110100}`
- 負例: `1`, `10`, `001`, `-0`, boxed 後に追加数値あり

のような pair を作って format-only 矯正を狙える。

### 5-3. ただし general に直で掛けない

RL/DPO は binary specialist にのみ適用し、その後 merge する方が安全である。

### Phase 5 の成功条件

- binary format failure の更なる減少
- exact 8-bit boxed output の増加
- general family の維持

---

## 6. 文献的に見た妥当性

この計画の根拠は repo 内分析だけではない。

### 6.1 CoT は有効だが万能ではない

Chain-of-Thought は arithmetic / symbolic reasoning を大きく改善する。  
しかし binary の harder slice は、自然文 CoT を長くするだけでは閉じない可能性が高い。

### 6.2 compositional hard tasks では段階分解が効く

Least-to-Most Prompting は SCAN のような compositional task で CoT より大きく改善した。  
binary でも、

- rule family 仮説
- query apply
- final answer

へ分解する設計は筋が良い。

### 6.3 ARC 系は program induction と search が効く

ARC は examples から exact output を作る benchmark であり、binary とかなり近い性質を持つ。  
最近の強い流れは free-form reasoning だけではなく、program synthesis / search / verification loop を伴う。

### 6.4 merge 技術は specialist 戦略を後押しする

TIES / DARE のような merge 技術は、複数 task-specific delta の干渉低減に意味がある。  
したがって「binary specialist を別に作って最後に merge」という考え方は、外部知見とも整合する。

---

## 7. 現実的な見立て

## 7-1. binary は最大の壁だが、唯一の壁ではない

現状の各資料から見て、binary は最大のボトルネックである。  
ただし `symbol_equation` を放置して 0.9 に届くとは限らない。

したがって、この文書の戦略名は

**binary program induction and specialist adapter**

のままでよいが、運用上は

**binary-first, symbol-aware**

で実施する。

## 7-2. まず勝つべき相手は自分の baseline

最初の勝ち筋は、

- merge で派手に伸ばすこと
- RL で一発逆転すること

ではない。

先に取るべき改善は、

- official-like eval 固定
- assistant-only loss
- template 整合
- curated mixture の再設計
- binary DSL 教師

である。

---

## 8. 改訂版ロードマップ

## Sprint 1: plumbing と evaluation の修正

- official-like offline eval
- binary format metrics
- General Stable Set / Binary Hard Set / Symbol Watch Set
- assistant-only loss
- train/infer template 整合
- curated mixture への移行

見る指標:

- overall
- family 別
- binary format failure
- symbol drop の有無

## Sprint 2: binary teacher redesign

- verified binary を hybrid trace 化
- binary answer-only を boxed-only 化
- no-answer-leak 設計
- formula holdout / hard slice holdout で検証

見る指標:

- binary verified slice accuracy
- 8-bit exact rate
- leading-zero retention

## Sprint 3: specialist + merge

- General adapter
- Binary adapter
- 必要なら Symbol adapter
- TIES / DARE / SVD の比較

見る指標:

- binary gain
- general retention
- merged adapter 総合点

## Sprint 4: synthetic

- verified family 条件付き synthetic binary
- near-miss / ambiguity-rich prompt 生成
- binary specialist への限定投入

見る指標:

- binary hard slice
- formula holdout
- side effect

## Sprint 5: RL/DPO

- binary specialist のみ
- format reward / exactness reward
- merge 再最適化

見る指標:

- format collapse の削減
- exact boxed 8-bit 出力率

---

## 9. 最優先3つ

最後に、今すぐやるべきことだけに絞る。

### 最優先1

**official-like offline eval を固定する**

### 最優先2

**assistant-only loss と template 整合で再ベースラインする**

### 最優先3

**binary verified 教師を short DSL から hybrid trace へ切り替える**

specialist adapter + merge は有望だが、この 3 つの後でよい。

---

## 10. 最終まとめ

この計画の改訂ポイントは 3 つである。

1. **binary は program induction として扱う**
2. **ただし merge や RL の前に、まず学習 plumbing を直す**
3. **0.9 を狙うために binary-first で進みつつ symbol 監視を切らない**

要するに、次の設計思想で進める。

- README 準拠の eval-first
- binary-first, symbol-aware
- verified / answer-only / manual の役割分離
- hybrid trace / executable scratchpad 教師
- specialist は後段で merge
- RL は最後

これが、現時点で最も実行可能性が高く、かつ既存分析と矛盾しない改訂版プランである。
