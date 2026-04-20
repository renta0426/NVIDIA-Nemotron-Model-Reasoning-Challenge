# symbol 90% accuracy strategy assessment

## Question

`README.md` と `A-Open-ProgressPrizePublication/README.md`、`appendix/Nemotron-Cascade-2`、`appendix/DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models.md` を踏まえて、**operator semantics が prompt に無い row** と **Nemotron の低レベル symbol 処理の弱さ**まで含めて、`symbol_equation` を accuracy で 90% へ近づける最有力戦略を整理する。

ここでの対象は strict `verified_trace_ready` ではなく、README 契約どおり **final boxed answer accuracy** である。

## First constraint: 90% はほぼ cryptarithm 問題で決まる

`symbol_equation` は `1,555` 行で、

- `equation_numeric_*`: `732`
- `cryptarithm_*`: `823`

に分かれる。

`A-Open-ProgressPrizePublication/README.md` の現状 solve rate は

- `equation_numeric_deduce`: `541 / 596`
- `equation_numeric_guess`: `22 / 136`
- `cryptarithm_deduce`: `47 / 659`
- `cryptarithm_guess`: `11 / 164`

なので、current symbol solve は `621 / 1555 = 39.9%` にすぎない。

さらに、

1. **equation が現状のままでは 90% は不可能**
   - equation 現状 `563 / 732` のまま `1,400` を目指すと、cryptarithm で `837 / 823` が必要になる
2. **equation を完璧にしても足りない**
   - equation を `732 / 732` にしても、cryptarithm で `668 / 823 = 81.2%` が必要

つまり、symbol 90% は **equation 改善の延長**ではなく、**cryptarithm を 8 割超まで押し上げる戦い**である。

## What is missing today

今足りないものは 5 つある。

| 欠けているもの | いま起きていること | 90% に必要な変化 |
| --- | --- | --- |
| prompt 外 operator semantics への対応 | unseen query operator row は strict では証明不能で、A-Open は abs-diff / concat fallback に寄っている | **corpus-level family prior** か **generator 回収**で「この benchmark では何が起きやすいか」を学ばせる |
| low-level symbol transduction | A-Open README が splitting / concatenation / text-to-character 弱さを明言 | **token-first** の symbol curriculum で、文字分解・連結・反転・桁操作を別訓練に切る |
| hard synthetic data | A-Open README は synthetic problem generation をまだ十分やれていない | **family-aware generator** で大量生成し、held-out validation を確保する |
| verifier-aware teacher selection | いまは deterministic CoT の手設計が中心で、探索・検証・蒸留の loop が弱い | **generate-verify-refine を offline distillation** に変える |
| training-serving alignment | A-Open README は SVD 変換由来の boxed 崩れや degeneration を報告 | easy categories を落とさない **serve-safe post-tune** が必要 |

## Why synthetic trace policy helps but is not enough

今回追加した `prompt_verified_trace / synthetic_trace_hypothesis / no_trace_teacher` の分離は有効だが、これは主に **data governance** の改善である。

- `prompt_verified_trace` は core trace teacher にできる
- `synthetic_trace_hypothesis` は pseudo-trace として accuracy 目的で使える
- しかし unseen operator semantics そのものや tokenization weakness はこれだけでは解けない

したがって、この整理は必要条件だが十分条件ではない。

## Most promising strategy: generator recovery + token-first scaling + verifier distillation

最有力なのは、A-Open の deterministic CoT 路線を捨てることではなく、**その上位互換**にすることだと考える。

### 1. Stage 0: serve-safe baseline を先に直す

最初にやるべきは symbol 以前に、A-Open README 自身が挙げている training-serving misalignment の修正である。

- `\boxed{}` を落とす
- 前の token を繰り返す
- template を崩す
- text-to-character で落ちる

この漏れが残ったまま cryptarithm を上げても、easy slice の取りこぼしで相殺される。

ここは Nemotron-Cascade-2 メモでいう **structured output を独立サブタスクとして扱う** 方針と整合する。

### 2. Stage 1: token-first symbol micro-curriculum

symbol で一番不足しているのは「長い CoT」より **細かい transduction skill** である。A-Open README の

- tokenization awareness
- splitting / concatenation weakness
- text-to-character weakness

はそのまま bottleneck を指している。

ここでは task を細かく分ける。

1. 文字列を 1 文字ずつ列挙する
2. 2 文字を左右に split / reverse する
3. 記号列を digits / chars に分解する
4. concat / reverse-concat を token 安全に書く
5. 2 桁数の tens / ones を取り出して再合成する
6. 記号 operator を inventory として読む

重要なのは、**text ではなく token を一次表現として生成する** こと。A-Open README も text ではなく token を直接持つ方向を improvement として挙げている。

### 3. Stage 2: symbol family generator を回収して synthetic scaling する

operator semantics が prompt に無い row を本当に解きたいなら、必要なのは「もっと綺麗な CoT」ではなく **family prior** である。

strict verified の観点では prompt 外情報は不可だが、accuracy 目的では train set 全体から latent family を学んでよい。  
ここで最重要なのは、

- `equation_numeric_*`
- `cryptarithm_deduce`
- `cryptarithm_guess`

それぞれについて **generator / latent program library を回収**し、そこから無限に近い synthetic 問題を作ることである。

作るべき synthetic は 2 種類ある。

1. **witness-complete tasks**
   - query operator が examples に十分現れる
   - latent rule が一意に定まる
   - deduce skill を鍛える
2. **guess-mode tasks**
   - query operator を intentionally hidden にする
   - ただし generator 上は正解が既知
   - model に「family prior に基づいて guess する」訓練をさせる

これは strict verified を増やす方法ではないが、**prompt に無い operator semantics を benchmark 分布上で当てる力**を作る最短ルートである。

### 4. Stage 3: offline generate-verify-refine を teacher distillation に変える

Nemotron-Cascade-2 の競技メモで重要なのは、

- tool use は本番ではなく teacher data 作成に使う
- generate-verify-refine の利益は offline distillation に変える
- proof generation と proof verification を分ける

という点である。

symbol ではこれをそのまま使う。

1. 強い teacher / solver / search で複数 trace を出す
2. exact solver / generator / answer checker で検証する
3. 最短かつ token-safe な canonical trace を残す
4. LoRA にはその distilled trace だけを教える

つまり、本番で tool use するのではなく、**teacher だけが search し、student は単発 deterministic 推論で再現**する。

### 5. Stage 4: cryptarithm には「deterministic proof mode」と「guess mode」を分ける

A-Open README 自身が「cryptarithm は guess を学ばせる必要がある」と書いている。ここは重要で、いまの deterministic CoT 一本足では `cryptarithm_guess` に届かない。

必要なのは 1 本の trace に全部押し込むことではなく、mode を分けることである。

- **proof mode**
  - examples から operator / mapping を十分拘束できる row
  - strict / near-strict synthetic trace を使う
- **guess mode**
  - prompt だけでは operator が未拘束
  - family prior と operator prior に基づいて候補を比較する
  - 「証明した」とは書かず、「この family ではこの候補が最も整合的」と書く

この mode 分離がないと、モデルは

- 解ける問題でも guess っぽくなる
- guess すべき問題で偽の deterministic proof を書く

のどちらかに崩れやすい。

### 6. Stage 5: RL は最後に使う。しかも raw benchmark ではなく verifiable synthetic に限定する

GRPO / RL は有望だが、**最初の主役ではない**。

DeepSeekMath の示唆はかなり明確で、

- RL は有効
- ただし improvement は主に **Maj@K を押し上げる** 方向で、Pass@K を根本的に増やしたわけではない
- reward が弱い / noisy と fundamental capability は伸びにくい

つまり、RL は「既に候補集合の中に正解がある」状況では強いが、**operator semantics 自体を知らない状態**を単独で解決する薬ではない。

したがって symbol で RL を使うなら条件は厳しい。

1. **reward が信頼できる task に限定する**
   - raw benchmark の ambiguous row ではなく
   - synthetic generator で答えと latent steps が既知な row に限定
2. **online RFT を先、GRPO を後**
   - まず正解 rollout を増やす
   - その後に group-relative な濃淡づけを入れる
3. **process reward を入れる**
   - split が正しい
   - concat が正しい
   - mapping が整合
   - final boxed answer が正しい
4. **overlong penalty / dynamic filtering**
   - Nemotron-Cascade-2 の通り、easy すぎる or impossible すぎる batch を薄くし、長すぎる trace を罰する
5. **MOPD 的な replay**
   - numeral / unit / gravity / easy equation を混ぜ直して drift を防ぐ

要するに、**RL は symbol generator ができた後の last-mile optimizer** である。

## Why pure GRPO is not the answer

純粋に GRPO だけ強くしても、9割への本丸には届きにくい。

理由は 3 つある。

1. **reward が作れない row が多い**
   - prompt-only で semantics が決まらない row に、正しい process reward を付けられない
2. **RL は distribution shaping 寄り**
   - DeepSeekMath の議論では、RL は correct response を top 側へ押し上げる効果が中心
3. **cryptarithm の主障害は token skill と data coverage**
   - split / concat / reverse / mapping の局所 skill が弱いままだと、policy optimization だけでは伸びにくい

なので、優先順位は

1. serve-safe 修正
2. token-first SFT
3. generator-backed synthetic scaling
4. verifier distillation
5. そのあと RL

である。

## Similar-paper takeaways

この方針は appendix で読んだ論文群とも整合する。

- **DeepSeekMath**
  - code prior が math reasoning を助ける
  - GRPO は効くが、reward reliability と data source が重要
  - process supervision が outcome-only より良い
- **Nemotron-Cascade 2**
  - 段階的 post-training
  - structured output を独立に鍛える
  - generate-verify-refine は offline distillation に落とす
  - dynamic filtering / overlong penalty / replay が有効
- **Math-Shepherd / PRM 系**
  - step-level verification を reward に入れる
- **PAL / Program-of-Thought**
  - computation を自然言語から切り離し、プログラムや正規化された中間表現へ落とす

symbol ではこのうち **PAL 的な中間表現**が特に重要で、自然文の CoT より

- split result
- reversed digits
- candidate operator family
- mapped symbol sequence

のような canonical intermediate を教える方がよい。

## Practical conclusion

symbol 9割 accuracy に最も近い戦略は、**RL first** ではなく次の 5 点セットである。

1. **training-serving misalignment を先に潰す**
2. **token-first symbol micro-curriculum を大量投入する**
3. **generator / family library を回収し、witness-complete と guess-mode の synthetic を大量生成する**
4. **teacher の search / verify を offline distillation に変える**
5. **最後に verifiable synthetic 上で online RFT → process-GRPO をかける**

短く言うと、

> **symbol 9割の本命は、GRPO 単体ではなく、generator 回収で semantics を外挿可能にし、token-first synthetic scaling で cryptarithm を別物に変え、その上で verifier-aware distillation と軽い RL で仕上げること**

である。

## Final assessment

現状足りないのは「もう少し強い RL」ではない。  
本当に足りないのは、

- **cryptarithm を 8 割超で解ける generator-backed data**
- **Nemotron の symbol split / concat / char conversion を矯正する token-level curriculum**
- **guess すべき row を guess mode として扱う明示的 policy**

の 3 つである。

よって、**最も有力なのは generator recovery を中心に据えた cascade training** であり、GRPO はその後段で使うべきである。
