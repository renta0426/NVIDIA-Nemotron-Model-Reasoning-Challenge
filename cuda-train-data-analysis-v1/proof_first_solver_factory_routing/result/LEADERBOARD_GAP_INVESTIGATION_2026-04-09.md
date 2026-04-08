# Leaderboard Gap Investigation 2026-04-09

## 1. 調査目的

`baseline/nemotron-sft-lora-with-cot-v2/result/v3f` は公式リーダーボードで `0.71-0.72` を出している一方、`cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result` 系の今回モデルは、ローカルでは大差がないように見えるにもかかわらず、公式リーダーボードで `0.56` に落ちる。

この差は一時的な submit ノイズではなく、提出時刻を変えても再現しているため、偶然ではなく **モデル側またはローカル評価側の構造的なズレ** とみなすべきである。

本調査では、`README.md` の Evaluation / Submitting を基準に、次を切り分ける。

1. そもそも local score の比較が正しいか
2. v3f と今回モデルの local parity は本当に成立しているか
3. それでも leaderboard だけ大差になるなら、どの種類の hidden 分布差を示唆するか
4. packaging failure ではなく hidden generalization failure と見る根拠はあるか

## 2. README.md を基準に固定する前提

`README.md` から外せない前提は次の通りである。

1. 評価は最終 answer の `Accuracy`
2. `\boxed{}` 抽出が最優先
3. 提出物は **単一の submit-compatible LoRA adapter を `submission.zip` に格納したもの**
4. Kaggle 側の実評価パラメータは Evaluation page の値であり、`temperature=0.0`, `max_tokens=7680`, `max_num_seqs=64`, `max_model_len=8192`

したがって、local で有効でも leaderboard で崩れる典型原因は次の 2 系統しかない。

1. local benchmark が hidden test の分布をほとんど表現していない
2. local pipeline は良いが、submit-compatible な単一 LoRA としてはその強みが再現されていない

今回は leaderboard が `0.00` や極端な failure ではなく `0.56` で安定しているため、後者のうち **zip 不成立や adapter 読み込み失敗のような packaging failure** より、**有効な adapter ではあるが hidden 分布で弱い** と読むのが妥当である。

## 3. まず local の比較基準自体を修正する必要がある

今回モデルだけでなく、`v3f` の Phase0 local artifact も、`build_phase0_offline_eval.py` の float-first verify を通しており、binary strict compare の意味では汚染されている。

つまり、保存済み Markdown の topline をそのまま比較すると誤る。

### 3.1 corrected Phase0 local320

| run | stored Phase0 | corrected Phase0 | corrected binary | corrected symbol | corrected text | corrected unit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `v3f` | `249/320 = 0.7781` | `240/320 = 0.7500` | `18/60 = 0.3000` | `24/60 = 0.4000` | `49/50 = 0.9800` | `49/50 = 0.9800` |
| `current` | `251/320 = 0.7844` | `241/320 = 0.7531` | `19/60 = 0.3167` | `24/60 = 0.4000` | `48/50 = 0.9600` | `50/50 = 1.0000` |

この corrected 比較では、両者は **ほぼ同点** である。今回モデルは local320 corrected では `+1/320` だけ上で、差は事実上ない。

### 3.2 binary specialized 563

| run | specialized accuracy |
| --- | ---: |
| `v3f` | `238/563 = 0.4227` |
| `current` | `234/563 = 0.4156` |

specialized でも差は小さい。つまり、

1. corrected local320 ではほぼ同点
2. specialized563 でもほぼ同点

にもかかわらず leaderboard では

1. `v3f`: `0.71-0.72`
2. `current`: `0.56`

となっている。

これは **local320 でも specialized563 でも見えていない hidden weakness** が、今回モデルにだけ強く存在することを意味する。

## 4. 「hidden が local と specialized の中間ぐらい」では今回の崩壊は説明できない

`v3f` の leaderboard `0.715` を、corrected local320 と specialized563 の凸結合で近似すると、

- `alpha = 0.8931`
- つまり hidden は、ざっくり `89.3%` が local320 側、`10.7%` が specialized563 側に近い混合

となる。

この同じ混合率を今回モデルへ当てると、予測スコアは

- predicted current = `0.717`

になる。

しかし実際の leaderboard は

- actual current = `0.560`

であり、差は

- unexplained gap = `-0.157`

ある。

したがって、今回の崩壊は次のどちらか、あるいは両方である。

1. hidden leaderboard half は local320 と specialized563 のどちらにも似ていない
2. 今回モデルは **その unseen slice でだけ極端に弱い**

これはかなり強い結論である。少なくとも、

- 「Phase0 corrected がほぼ同じだから hidden も似るはず」
- 「specialized でも大差がないから hidden も大差ないはず」

は成立しない。

## 5. local row-level 差分から見えること

### 5.1 corrected Phase0 320 での差分は本当に小さい

`current` と `v3f` の corrected Phase0 320 を row-level で突き合わせると、

- `current` の regressions: `5`
- `current` の improvements: `6`

しかない。

内訳は次の通り。

#### regressions

- family: `symbol 3`, `text 2`
- subtype: `numeric_2x2 3`, `text_monoalphabetic 2`

#### improvements

- family: `symbol 3`, `unit 1`, `text 1`, `binary 1`
- subtype: `numeric_2x2 3`, `unit_fixed_ratio 1`, `text_monoalphabetic 1`, `bit_other 1`

つまり、Phase0 320 の範囲では今回モデルは **広く崩れていない**。ここだけ見ると leaderboard `0.56` は予見不能である。

### 5.2 local320 は hidden 崩壊の監視セットとして弱すぎる

corrected Phase0 320 で今回モデルが失っているのは `text 1問` 程度で、binary もむしろ `v3f` より `+1` である。

したがって hidden で起きているのは、Phase0 320 が意図的に外している分布、もしくは family 内の unseen subtype での failure と考えるほかない。

## 6. specialized 563 の bucket 差分から見える hidden の向き

specialized563 で `current` と `v3f` を bucket 単位で比べると、今回モデルは「まんべんなく悪い」のではなく、**勝つ bucket と負ける bucket がはっきり分かれている**。

### 6.1 current が v3f より悪い bucket

| bucket | v3f | current | delta |
| --- | ---: | ---: | ---: |
| `supported_bijection` | `0.9400` | `0.8400` | `-0.1000` |
| `dominant_structured_safe` | `0.4417` | `0.4000` | `-0.0417` |
| `boolean_family` | `0.6167` | `0.6000` | `-0.0167` |
| `supported_affine_xor` | `0.4333` | `0.4167` | `-0.0167` |

### 6.2 current が v3f より良い bucket

| bucket | v3f | current | delta |
| --- | ---: | ---: | ---: |
| `rare_perm_independent` | `0.5714` | `0.7143` | `+0.1429` |
| `supported_not_structured` | `0.0182` | `0.0727` | `+0.0545` |
| `dominant_structured_abstract` | `0.3111` | `0.3556` | `+0.0444` |

specialized row-level diff でも、今回モデルの regressions は

- `dominant_structured_safe`: `13`
- `supported_bijection`: `7`

に集中している。

反対に improvements は

- `dominant_structured_safe`: `8`
- `dominant_structured_abstract`: `7`
- `supported_not_structured`: `3`

に出ている。

### 6.3 ここから言えること

今回モデルは、`v3f` より単純に劣っているのではなく、**safe/bijection 側を落として abstract / not_structured 側へ重心をずらした** run である。

したがって leaderboard `0.56` が出るためには、hidden half が次のどちらかである可能性が高い。

1. `supported_bijection` / `dominant_structured_safe` に近い unseen 問題が多い
2. あるいは current の route-aware style が unseen binary family で solver mislock を起こしている

## 7. 出力スタイル差は current の方が明確に route-conditioned である

出力スタイルの集計は次の通りだった。

### 7.1 Phase0 全体

| run | mean chars | route_rate | so_rule_rate | constraints_rate |
| --- | ---: | ---: | ---: | ---: |
| `v3f_phase0` | `3141.1` | `0.0` | `0.1531` | `0.0` |
| `current_phase0` | `3114.3` | `0.0` | `0.1688` | `0.0` |

Phase0 全体では、両者の style 差は小さい。

### 7.2 specialized563

| run | mean chars | route_rate | so_rule_rate | constraints_rate |
| --- | ---: | ---: | ---: | ---: |
| `v3f_spec` | `258.6` | `0.0` | `0.0` | `0.0` |
| `current_spec` | `369.0` | `1.0` | `1.0` | `1.0` |

今回モデルの specialized 出力は、ほぼ完全に次の style へ寄っている。

1. `Route: ...`
2. `Route granularity: exact`
3. `Check ex1 and ex2 ...`
4. `So the rule is ...`
5. `Constraints: exact_8bit, leading_zeros, box_only_final.`

sample でも、`current_spec` の先頭行はすべてこの形式で出ていた。

これはつまり、今回モデルが **proof-first / route-aware teacher の表面様式まで強く学習している**ことを意味する。

## 8. route-aware 設計メモ自身が、この failure mode を事前に警告していた

`cuda-train-data-analysis-v1/proof_first_solver_factory_routing/v3f_experiment_feedback_2026-04-08.md` には、すでに次の警告が書かれている。

1. current delta の `80/197` 行は `coarse + route_closure_only`
2. これは proof-first というより boxed short-answer bias に近い
3. `route_closure_only` を増やしすぎると boxed は守れても content miss を増やす危険がある
4. mainline へそのまま入れるのは危険

同ファイルでは、primary lane を

1. exact-route verified rows
2. coarse-route closure-only は低比率補助

にすべきだと明記している。

つまり、今回の leaderboard `0.56` は、**設計メモが危険視していた失敗形が hidden で顕在化した**ものとして読むのが一番整合的である。

## 9. packaging / submit 失敗説が主因である可能性は低い

packaging failure が主因なら、通常は次のような症状が出る。

1. スコアが極端に低い、あるいは 0 付近になる
2. 提出ごとの揺れが大きい
3. 読み込み失敗や adapter 無視に近い挙動になる

しかし今回観測されているのは、

1. 複数回提出しても `0.56` 付近で安定
2. discussion 上でも「recent notebook をそのまま実行して submit すると 0.56 が再現した」という第三者報告がある

という挙動である。

したがって、これは **submit そのものが壊れているのではなく、submit された単一 LoRA が hidden に対して弱い**とみる方が筋が通る。

## 10. 最も妥当な根本原因仮説

現時点での優先順位は次の通り。

### 仮説 A: hidden は current が落とす binary slice を強く含んでいる

最有力。

根拠:

1. corrected local320 はほぼ同点なのに leaderboard だけ大差
2. specialized563 でも小差なのに leaderboard だけ大差
3. current の regressions は `supported_bijection` / `dominant_structured_safe` に偏る
4. hidden 50% は public に見えている train-derived watch set と同分布である保証がない

要するに、今回モデルは **local で改善して見えた slice に最適化され、hidden の主成分には外した**可能性が高い。

### 仮説 B: route-aware textual commitment が unseen family で誤った solver lock を起こしている

かなり有力。

根拠:

1. current_spec の route / so_rule / constraints rate がすべて `1.0`
2. route-aware 設計メモ自身が coarse lane と closure-only の危険を警告していた
3. current は abstract / not_structured を拾う代わりに safe / bijection を落としており、**早すぎる route commitment** の失敗形と整合する

つまり current は「解く前に family と rule を決め打ちしすぎる」方向へ寄っている可能性がある。

### 仮説 C: local benchmark が easy 200 を含みすぎて hard shift を見逃している

有力。

Phase0 320 は `general_stable_set 200` を含むため、hidden の hard-family shift をかなり薄める。今回のような hidden binary collapse は、この構成では見えにくい。

### 仮説 D: packaging / adapter load failure

主因としては低い。

0.56 という安定値、第三者再現、複数 submit 再現があるため、壊れた zip より **弱いが有効な adapter** の方が説明力が高い。

## 11. 今回の発見から言えること

今回の 0.56 は悪いニュースであると同時に、かなり価値の高い情報でもある。

なぜなら、これで hidden leaderboard は少なくとも次を満たさないことが分かったからである。

1. corrected Phase0 320 の単純な延長ではない
2. specialized563 の単純な延長でもない
3. `abstract / supported_not_structured` を拾えば自然に伸びる分布でもない

むしろ hidden は、今回モデルが弱くした

1. `supported_bijection`
2. `dominant_structured_safe`
3. おそらく route mislock を起こしやすい unseen binary variants

に近い可能性が高い。

## 12. 実務上の次アクション

この調査結果に基づく next action は次の順が妥当である。

1. **current の route-aware delta を coarse lane なしで再学習する ablation を最優先で作る**
   - 特に `route_closure_only` を抜く
   - `exact-route verified` のみ残す
2. **hidden proxy を再設計する**
   - Phase0 320 ではなく、`supported_bijection` / `dominant_structured_safe` / unseen-safe-like binary を厚くした submit-proxy watch set を新設する
3. **specialized563 の勝ち負けではなく、current-v3f の row-level regressions を直接補修する**
   - とくに `binary_bit_permutation_bijection`
   - `binary_structured_byte_formula`
   - `binary_affine_xor`
4. **route phrase の表面転写を弱める**
   - `Route:` / `Constraints:` の文字列そのものを教師にするのではなく、最終 commit 前の solver lock だけを残す短い exact trace に寄せる

## 13. 最終結論

今回の leaderboard `0.56` は、local score の見かけの差よりもはるかに大きいが、調べると次が分かった。

1. `v3f` と `current` は corrected local320 ではほぼ同点である
2. specialized563 でも小差でしかない
3. したがって hidden `0.56` は local benchmark の単純外挿では説明できない
4. current の弱点は `supported_bijection` / `dominant_structured_safe` と route-conditioned exact commitment の脆さに寄っている可能性が高い
5. packaging failure より、**hidden binary distributionに対する generalization failure** とみるのが妥当である

要するに、今回の大きな発見は次の一文に尽きる。

> leaderboard は、current が local で拾えている binary 改善をほとんど評価しておらず、むしろ current が落とした safe/bijection 系または route mislock 系の unseen binary slice を強く含んでいる可能性が高い。