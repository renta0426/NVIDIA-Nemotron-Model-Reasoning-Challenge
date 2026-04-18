# cuda-train-data-analysis-v1 A-Open symbol wall breakthrough assessment

## Question

`A-Open-ProgressPrizePublication/README.md` では symbol 系、特に equation / cryptarithm が壁になっている。  
今回の `prompt_verified_trace` / `synthetic_trace_hypothesis` / `no_trace_teacher` の整理で、その壁を打破できるかを評価する。

## What A-Open README says the wall is

公開 README 上では、symbol の壁は大きく 3 種類ある。

1. **unseen query operator を仮定で埋めている**
   - `equation_numeric_guess` は examples に無い operator を abs-diff と仮定している
   - `cryptarithm_guess` は examples に無い question operator を concat と仮定している
2. **cryptarithm の CoT をうまく書けていない**
   - multiplication / division / abs diff を仮定した decode は一部できても、モデルを正答へ導く trace を作れなかった
3. **モデル自体が symbol tokenization に弱い**
   - splitting / concatenation が苦手
   - text 単位で trace を書くと tokenization 由来の難しさを踏みやすい

要するに、A-Open 側の壁は「programmatic solve rate が低い」だけではなく、

- unseen operator semantics の不足
- cryptarithm での trace 設計不足
- symbol tokenization weakness

が重なったものとして書かれている。

## What the new organization changes

今回の整理で変わったのは、symbol supervision を 3 層に分けて扱えるようになった点。

1. `prompt_verified_trace`
   - prompt-only で一意かつ trace-safe
   - strict teacher としてそのまま使える
2. `synthetic_trace_hypothesis`
   - accuracy 目的では有用な一貫 trace を書ける
   - ただし benchmark row の semantics を証明したものではない
   - gold が candidate selection に入る場合は明示的に隔離される
3. `no_trace_teacher`
   - current prompt / gold / DSL だけでは trace teacher にしない方がよい

この整理で重要なのは、**A-Open の accuracy 目的**と**strict verified の証明目的**を切り離せたこと。

## Can it break the wall?

### 1. `equation_numeric_deduce` には効く可能性が高い

ここは最も効果が出やすい。

- `prompt_verified_trace`: `110`
- `synthetic_trace_hypothesis` のうち `equation_numeric_deduce`
  - `unique_rule_below_verified_support`: `114`
  - `answer_conditioned_family_choice`: `275`
  - `answer_conditioned_rule_choice`: `47`

特に `114` 行は、規則ほぼ一意で support だけが薄い slice なので、A-Open 的な deterministic CoT 学習には相性が良い。  
また `family_choice` / `rule_choice` も、strict verified には使えないが、**accuracy 向け pseudo-trace** としては使える。

したがって、A-Open README の equation wall に対しては、

- verified trace だけを主力にする
- その周辺に `unique_rule_below_verified_support` を first expansion として足す
- さらに `family_choice` / `rule_choice` を low-ratio で混ぜる

という段階投入が可能になった。

### 2. `equation_numeric_guess` にも一定の改善余地がある

ここも abs-diff fallback 一本よりは改善余地がある。

- `answer_conditioned_operator_semantics`: `108`
- `answer_conditioned_rule_choice`: `1`
- `prompt_exact_conflict` で blocked: `27`

つまり全部は無理だが、**少なくとも 108 行は “abs-diff 一択” ではなく synthetic supervision として管理できる**。  
これは A-Open README の「unseen operator は abs-diff と仮定」という単一 fallback より柔らかく、accuracy 目的では有利。

### 3. `cryptarithm_deduce` には部分的には効くが、壁の本体は残る

ここは半分だけ効く。

- `answer_conditioned_operator_semantics`: `306`
- `answer_conditioned_latent_hypothesis`: `353`

この 659 行を strict verified にはできないが、A-Open の SFT は accuracy 目的なので、pseudo-trace として投入する価値はある。  
ただし README で本人が書いている通り、cryptarithm の本当の難所は「trace をどう書けば Nemotron が symbol split / concat を間違えず追えるか」であり、**tier 分離だけでは tokenization weakness を解決しない**。

つまり、

- trace policy の整理は「どの trace を安全に混ぜるか」を改善する
- しかし「モデルが symbol をうまく分解・連結できない」という低レベル weakness は別問題

である。

### 4. `cryptarithm_guess` の壁は、この整理だけでは破れない

ここが最重要。

- `cryptarithm_guess`: `164`
- 全て `answer_conditioned_operator_semantics`

この slice は、strict verified ではもちろん無理だが、accuracy 目的の pseudo-trace としては使える。  
ただし、A-Open README の現在の fallback concat 仮定よりは柔軟になる一方で、**根本の unseen operator semantics が prompt から出ない**という事実は変わらない。

したがって、この整理だけで

- `cryptarithm_guess` を programmatically solve できるようになる
- official semantics 不在を埋められる
- strict 90% verified ceiling を突破できる

わけではない。

## Net assessment

### 打破できる部分

- A-Open の **accuracy-oriented SFT policy** はかなり改善できる
- 特に `equation_numeric_deduce` と `equation_numeric_guess` は、fallback 一本より良い trace curriculum を作れる
- `cryptarithm_deduce` も、trace を全部捨てるのではなく pseudo-trace として再利用できる
- `verified` と `pseudo-trace` を混ぜて事故るリスクを下げられる

### 打破できない部分

- unseen operator semantics そのもの
- `cryptarithm_guess` の identifiability
- symbol tokenization / splitting / concatenation weakness
- strict verified coverage ceiling

## Practical recommendation for A-Open style training

1. `prompt_verified_trace` を core trace teacher にする
2. `unique_rule_below_verified_support` (`114`) を first synthetic expansion にする
3. `equation_numeric_deduce` の `family_choice / rule_choice` を second expansion にする
4. `equation_numeric_guess` / `cryptarithm_deduce` / `cryptarithm_guess` の `answer_conditioned_operator_semantics` は low-ratio に留める
5. `no_trace_teacher` は trace SFT に入れない
6. tokenization weakness に対しては、A-Open README が示す通り **text ではなく token-aware trace 設計** を別軸で進める

## Conclusion

**部分的には打破できるが、全部ではない。**

今回の整理は、

- symbol 問題を「strict verified か否か」だけで見るのをやめ
- **accuracy に効く synthetic trace** を安全に再利用する土台を作る

という意味では、A-Open README がぶつかった wall をかなり実務的に前進させる。

ただし本丸である

- `cryptarithm_guess` の unseen operator semantics
- cryptarithm 系の tokenization / splitting / concatenation weakness

は別問題なので、**この整理だけで wall 全体を打破したとは言えない**。  
一番正確な言い方は、

> strict verified wall は破れないが、 accuracy wall にはかなり効く

である。
