了解。  
**「Mac で MLX 学習 → MLX→PEFT 変換 → Mac で軽い確認 → CUDA/Linux で PEFT/Transformers 検証」**までを、**実装抜き**で、できるだけ実務向けに整理します。  
先に要点だけ言うと、**この流れは十分現実的**です。ただし **MLX→PEFT は現状“公式逆変換コマンド”が見当たらない**ので、そこだけは**自前 exporter を前提**に進めるのが安全です。`mlx-lm` の学習物は `adapters/` 配下に保存され、読み込み側も `adapter_config.json` と `adapters.safetensors` を前提にしています。一方、PEFT は `adapter_model.safetensors` と `adapter_config.json` を要求します。 

---

## まず前提として固定すべきこと

### 1) ベースモデルの“正体”を固定する
Linux/CUDA 側の検証では、**最終的に差し込みたい official base** を固定してください。Nemotron の BF16 モデルカードでは `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` が Transformers / vLLM 利用例として案内されており、NVIDIA の Nemotron 3 公開ページでも **BF16 が post-trained Nano、Base-BF16 は pre-trained base** と分けて公開されています。したがって、**提出互換を意識した検証先は `...-A3B-BF16` で固定**するのが自然です。 

### 2) LoRA 方式は“標準 LoRA”に絞る
vLLM 側の `PEFTHelper` は、**`modules_to_save` は `None` であること、`use_dora` は未対応、`bias` は `none`、rank は `max_lora_rank` 以下**を明示的に検証します。したがって、**Mac 側の探索段階から DoRA や特殊設定を避け、標準 LoRA に寄せる**のがベストです。 

### 3) 4bit は探索用、最終候補は BF16 で再確認
`mlx-lm` は、**量子化モデルを指すと QLoRA、非量子化モデルを指すと通常 LoRA**になります。なので 4bit MLX は探索に向いていますが、Linux 側 official 検証先は BF16 です。  
そのため、これは私の運用推奨ですが、**粗い sweep は 4bit MLX、最終候補だけ BF16 MLX でもう一度回してから export** すると、Mac→Linux のズレをかなり減らせます。これは `mlx-lm` の QLoRA 対応と、Nemotron の official BF16 運用例からの実務的な推論です。 

### 4) プロンプト契約を Mac / Linux で完全一致させる
Nemotron の model card では、**`tokenizer.apply_chat_template(..., add_generation_prompt=True)`** を使う例が示され、`enable_thinking` は既定で有効です。比較検証では、**同じ tokenizer、同じ chat template、同じ `enable_thinking` 設定、同じ stop 条件**を使わないと、変換ミスなのか prompt 差分なのか切り分けにくくなります。 

---

# Phase A: Mac 側の具体手順
目的は、**MLX で学習し、export 前の“正”を作ること**です。

## A-1. 環境と対象を固定する
最初に固定するものは以下です。

- `mlx-lm` のバージョン
- MLX 変換済みベースの repo / commit / snapshot
- 学習 YAML
- 学習データの版
- 比較用サンプルプロンプト集合
- 生成条件  
  - `max_new_tokens`
  - `temperature`
  - `top_p`
  - `seed`
  - `enable_thinking`
  - stop 条件

`mlx-lm` は Apple silicon 向けの LLM 実行・微調整パッケージで、LoRA 学習の主コマンドは `mlx_lm.lora`、生成は `mlx_lm.generate` です。大きなモデルでは macOS 15 以降の wired memory の話もあるため、**まず再現可能な環境を固定してから実験に入る**のが重要です。 

## A-2. ベースモデル単体で“基準出力”を取る
LoRA 学習前に、**ベースモデル単体**で 5〜20 個くらいの固定プロンプトに対する出力を保存します。  
ここでの目的は精度評価ではなく、**後で「学習は効いているか」「chat template が壊れていないか」を見る基準点**を持つことです。Nemotron の official 例に合わせて、**Transformers 側でも再現しやすい chat template 形式**で保存しておくのがよいです。 

## A-3. `mlx_lm.lora` で学習し、成果物を `adapter_path` に集約する
`mlx-lm` の LoRA ドキュメントでは、LoRA 学習の主コマンドは `mlx_lm.lora` で、**既定では `adapters/` に adapter config と learned weights を保存**し、出力先は `--adapter-path` で変えられます。さらに、現行の読み込みコードは **`adapter_config.json` と `adapters.safetensors` を読む**前提です。  
したがって、**1 trial = 1 adapter ディレクトリ**にし、後工程で迷子にならないようにします。 

## A-4. 学習直後に MLX ネイティブ推論で“golden samples”を作る
学習が終わったら、その trial の adapter を使って **MLX ネイティブ推論**を行い、固定プロンプト集合に対する出力を保存します。  
保存対象は少なくとも次です。

- 入力 prompt
- 生出力 raw text
- 必要なら抽出後 final answer
- 生成条件
- 使用した base / adapter / trial ID

ここで保存したものが、Linux 側比較の**golden reference**になります。MLX では `mlx_lm.generate --adapter-path ...` による生成が案内されています。 

## A-5. Mac 側の“軽い整合確認”は、まず構造確認に徹する
Mac 側でやる軽い確認は、**数値一致検証ではなく構造確認**を中心にするのが賢いです。確認項目は次です。

- `fine_tune_type` が `lora` である
- `adapter_path/adapter_config.json` が存在する
- `adapter_path/adapters.safetensors` が存在する
- `lora_parameters.rank / scale / dropout / keys` が期待通り
- trial ごとに base が混ざっていない
- 量子化ベースか BF16 ベースかが明確

MLX の学習設定例では LoRA 設定名は **`rank` / `scale` / `dropout` / `keys`** です。後の export でここが PEFT 側の `r / lora_alpha / lora_dropout / target_modules` に対応します。 

## A-6. Export は「custom exporter を 1 個に固定」する
ここが一番大事です。  
`mlx_lm.convert` の documented な役割は **Hugging Face model → MLX** 方向で、現時点では **MLX → PyTorch/PEFT の公式逆変換コマンドは文書化されていません**。`mlx-lm` 側でも reverse convert を求める issue が立っています。  
なので運用としては、**trial ごとに場当たり変換するのではなく、exporter を 1 本に固定**してください。これで事故率が一気に下がります。 

## A-7. Exporter の仕様を先に決める
実装は不要とのことなので、**仕様だけ**書きます。Mac 側 exporter は次の責務を持たせるのがよいです。

1. **入力**: MLX の `adapter_path/`  
2. **出力**: PEFT 形式の `converted_adapter/`  
3. **重みファイル名変換**: `adapters.safetensors` → `adapter_model.safetensors`  
4. **キー変換**: PEFT 互換の key naming に合わせる  
5. **config 変換**: MLX config → PEFT `adapter_config.json`  
6. **manifest 出力**: trial ID、base model、MLX rank/scale、PEFT r/alpha、target_modules を記録  
7. **検証ログ出力**: 変換した tensor 数、shape、dtype の一覧

PEFT の checkpoint 形式は **`adapter_model.safetensors` と `adapter_config.json`** が必須で、LoRA weight keys は **`base_model.model....lora_A.weight` / `lora_B.weight`** 形式を使います。 

## A-8. Export 規約はこれで固定する
MLX source と PEFT checkpoint 仕様から、変換ルールは以下で固定するのが妥当です。

- MLX の `lora_a` → PEFT の `lora_A.weight`
- MLX の `lora_b` → PEFT の `lora_B.weight`
- key prefix は **`base_model.model.`** を付与
- MLX の `lora_a` / `lora_b` は shape が PEFT と向きが違うため、**転置**して保存
- PEFT config の  
  - `r = rank`
  - `lora_alpha = scale * rank`
  - `lora_dropout = dropout`
  - `target_modules = keys` 由来
  - `peft_type = "LORA"`
  - `inference_mode = true`
  - `bias = "none"`
  - `modules_to_save = null`
  - `use_dora = false`
  - `use_rslora = false`（少なくとも最初は）

MLX の `LoRALinear` は `lora_a` を `(input_dims, r)`、`lora_b` を `(r, output_dims)` で持ち、forward は `scale * ((x @ lora_a) @ lora_b)` です。PEFT は LoRA weight として `lora_A.weight` / `lora_B.weight` を保存し、`base_model.model.` prefix を要求します。vLLM は PEFT config を読み、**DoRA 非対応・`modules_to_save=None`・bias 非対応**を確認します。 

## A-9. Mac 側で export 後にやる“最終軽チェック”
Mac 側で export 後に最低限確認すべきものは次です。

- `converted_adapter/adapter_model.safetensors` がある
- `converted_adapter/adapter_config.json` がある
- `base_model_name_or_path` が **Linux で使う official base** と一致している
- `r`, `lora_alpha`, `target_modules` が MLX 側の trial 設定と矛盾していない
- `use_dora=false`, `modules_to_save=null`, `bias=none`

ここでは **Transformers 実ロードまでは Mac で無理にやらなくてよい**です。30B 級で Mac 側の追加検証まで背負うと重いので、**Mac は“学習・export・構造確認・golden sample 採取”まで**に寄せるのが実務的です。PEFT / Transformers の authoritative check は Linux に回します。 

---

# Phase B: CUDA/Linux 側の具体手順
目的は、**変換後 adapter が official base に正しく刺さり、Mac 側の挙動を壊していないか**を確認することです。

## B-1. Linux 側は“検証専用”のクリーン環境を作る
CUDA/Linux 側では、**学習ではなく検証専用環境**に分けるのがよいです。  
ここで固定するものは次です。

- CUDA / driver
- PyTorch
- Transformers
- PEFT
- safetensors
- 必要なら vLLM
- official base model revision

Nemotron の model card は **Transformers と vLLM の使用例**を示しており、NVIDIA のカスタマイズ文書でも `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` を customization target としています。 

## B-2. まず official base 単体で Linux 推論を確認する
いきなり adapter を載せず、まず **base 単体**で次を確認します。

- tokenizer がロードできる
- `trust_remote_code=True` が必要なら通る
- `apply_chat_template` が想定通りに動く
- 固定 sample が問題なく生成できる

Nemotron の official 使用例でも、Transformers で **`AutoTokenizer` / `AutoModelForCausalLM`** を使い、`trust_remote_code=True` と `apply_chat_template()` を使っています。 

## B-3. 次に PEFT adapter を local dir からロードする
Transformers / PEFT 側では、**local directory にある `adapter_config.json` と adapter weights** をロードできます。  
つまり Linux 側の第一関門は単純で、**`converted_adapter/` が “普通の PEFT LoRA ディレクトリ”として読めるか**です。これは `from_pretrained()` でも `load_adapter()` でも可能です。 

## B-4. 構造検証では“ロードできた”だけで満足しない
Linux 側での構造検証では、最低限次を確認します。

- missing / unexpected key が出ていないか
- adapter が有効化されているか
- target module 数が不自然でないか
- active adapter が意図した 1 本だけか
- ベース単体時と adapter 有効時で出力が変化するか

PEFT には adapter の load や状態確認の仕組みがあり、Transformers の `PeftAdapterMixin` も local path から adapter をロードできます。**“ロード成功”だけでなく、実際に adapter が forward に参加しているか**まで確認すべきです。 

## B-5. Mac 側の golden samples と比較する
ここが本丸です。  
比較は次の順でやるのがよいです。

1. **同一 prompt / 同一 chat template / 同一 generation 条件**で Linux 出力を取る  
2. Mac 側で保存した MLX native 出力と並べる  
3. 比較対象を3段階に分ける  
   - raw text  
   - 抽出後 final answer  
   - 必要なら token 単位の冒頭比較

比較用 sample は 5〜20 個で十分です。  
特に今回の用途では、**最初は “final answer が一致するか / 挙動が同等か” を主判定**にし、raw text の完全一致は補助指標にするのが現実的です。4bit MLX で学習した trial を BF16 Linux に持ってきた場合、数値誤差や量子化差で完全一致しないことはありえます。だからこそ、**最終候補は BF16 MLX でもう一度作る**運用が効きます。これは MLX の QLoRA 対応と official BF16 base 運用からの推奨です。 

## B-6. 差が出たときの切り分け順
Linux 側で差分が出たら、疑う順番はこれです。

1. **base model が違う**  
2. **chat template / `enable_thinking` / prompt 組み立てが違う**  
3. **MLX `scale` → PEFT `lora_alpha` 変換が違う**  
4. **tensor 転置が漏れている**  
5. **target_modules が不足・過剰**  
6. **DoRA / bias / `modules_to_save` など vLLM 非互換設定が混入**  
7. **4bit trial を BF16 base に持ち込んだことで比較が荒れている**

この順で見ると、だいたい原因が詰められます。MLX source は `scale` を明示的に forward に掛けており、PEFT / vLLM は `lora_alpha` と rank を config から解釈します。vLLM も unsupported な設定を明示的に弾きます。 

---

# 精度を落としにくい運用ルール

## 1) “量産 trial” と “本命 trial” を分ける
- **量産 trial**: Mac + MLX 4bit で高速探索  
- **本命 trial**: Mac + MLX BF16 で再学習 / 再export  
- **検証 trial**: Linux + official BF16 base で PEFT 検証

この 3 段階に分けると、Mac の速さを活かしつつ、最終的な互換性も担保しやすいです。 

## 2) exporter の入力・出力仕様を固定し、trial ごとに変えない
一度 exporter の規約を決めたら、**trial ごとに key mapping や config mapping を変えない**でください。  
trial ごとに変えるべきなのは **LoRA の中身**だけで、**変換ロジック自体は固定**が鉄則です。PEFT checkpoint format は要求ファイルと key naming が明確です。 

## 3) prompt 比較セットを固定資産にする
比較セットは、毎回その場で作るのではなく固定してください。  
おすすめは以下の 3 群です。

- reasoning が短い問題
- reasoning が長い問題
- boxed answer / 数値抽出に近い問題

Nemotron は reasoning trace を生成しうるモデルなので、**短問・長問・最終解答型**を混ぜると、壊れ方が見えやすいです。model card でも reasoning/chat 用モデルであることが説明されています。 

## 4) Linux 側で通った artifact だけを“採用候補”にする
Mac 側でよく見えても、**Linux で official base + PEFT が通らないものは不採用**にした方がいいです。  
理由は単純で、**真の互換性判定環境は Linux/CUDA 側**だからです。Transformers / PEFT / vLLM の正式なロード条件はそちらにあります。 

---

# ここまででの完了条件
あなたの今回の範囲なら、**次の条件を満たしたら完了**です。

- Mac で MLX 学習が回る  
- Mac で MLX native 推論結果を golden sample として保存できる  
- MLX adapter を PEFT 形式へ export できる  
- Linux で official Nemotron BF16 base + converted adapter をロードできる  
- 固定 sample で、Mac 側の変換前推論結果と比べて**致命的な差がない**と判断できる  

ここまで通れば、次の段階として **vLLM smoke test** に進む価値があります。vLLM は LoRA adapter のディレクトリ構造と config を前提に読み込むので、その前段としては十分よいゲートです。 

---

# 参考文献
- MLX LM README（生成・変換・Apple silicon 向け概要） 
- MLX LM LoRA ドキュメント（`mlx_lm.lora`, `adapter_path`, 学習/生成フロー） 
- MLX LM source: `tuner/utils.py`（`adapter_config.json` + `adapters.safetensors` を読む現行仕様） 
- MLX LM source: `tuner/lora.py`（`lora_a` / `lora_b` の shape と `scale` の扱い） 
- MLX-LM issue #320（現状の `convert` が HF→MLX 方向であり、逆変換要望があること） 
- Hugging Face PEFT checkpoint format（PEFT 形式の必要ファイル、key prefix） 
- Transformers PEFT docs / PeftAdapterMixin（local dir から adapter を load できること） 
- vLLM tensorizer / LoRA resolver docs（LoRA adapter のディレクトリ構造、`adapter_config.json` 前提） 
- vLLM source: `peft_helper.py`（`modules_to_save`, DoRA, bias, rank 制約） 
- NVIDIA Nemotron BF16 model card（Transformers / vLLM 利用例、`enable_thinking`） 
- NVIDIA Nemotron 3 公開ページ / NVIDIA customization docs（BF16 と Base-BF16 の位置づけ、customization target） 

必要なら次に、  
**この手順に対応した「チェックリスト版」**  
または  
**「Mac 側 exporter 仕様書（入出力・検証項目・失敗時の診断表）」**  
に落として出します。