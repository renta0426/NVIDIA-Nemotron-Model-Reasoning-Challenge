**「MLXで学習済みの LoRA アダプタを、できるだけ意味を変えずに、このコンペの提出要件に合う PEFT/vLLM 形式へ変換する」ことだけ**に絞って、計画を組み直します。  
**探索・再学習・精度向上のための試行は対象外**とします。

---

# 目的の再定義

このタスクの目的は次の 1 点です。

> **既存の MLX LoRA アダプタを、提出可能な PEFT 形式へ高忠実度で変換し、コンペ evaluator と同系統の vLLM 環境で壊れていないことを確認する。**

したがって、**「どの rank が良いか」「6bit と BF16 のどちらが強いか」**のような話は、ここでは扱いません。  
扱うのは **変換の正確性・互換性・提出パッケージの健全性**だけです。

---

# このコンペ前提で最初に固定すべきこと

あなたが貼ってくれた metric コードを見る限り、評価時は次の前提です。

- evaluator 側で **固定の Nemotron BF16 ベース**をロードする
- 提出物は **LoRA adapter のディレクトリ**である
- zip 展開後、**最初に見つかった `adapter_config.json`** のあるディレクトリが採用される
- 推論は **vLLM** で行われる
- prompt 末尾に **`\boxed{}` 指示**が付与される
- tokenizer の **chat template** を通し、`enable_thinking=True` で生成する
- 採点は **生成全文ではなく抽出された final answer** ベース

この前提だと、**変換タスクの真のゴールは「PEFT/Transformers で読めること」ではなく、「vLLM evaluator にそのまま刺さること」**です。  
つまり、**最終判定系は Linux/CUDA + vLLM** に置くべきです。

---

# 変換タスクの入出力を明確化する

## 入力
入力は **すでに存在する MLX adapter ディレクトリ**です。  
`mlx-lm` の LoRA/QLoRA フローでは、adapter config と学習済み重みは既定で `adapters/` に保存され、出力先は `--adapter-path` で変更できます。さらに loader 側は `adapter_config.json` を読んで LoRA 層を差し込み、`adapters.safetensors` をロードします。 

## 出力
出力は **PEFT 互換 adapter ディレクトリ**です。  
PEFT の checkpoint 形式では、少なくとも **`adapter_model.safetensors`** と **`adapter_config.json`** が必要です。Transformers/PEFT も、ローカルディレクトリから adapter を読む際にこの構成を前提にします。 

---

# 変換タスクのベストプラクティス

## 1) 変換対象は「標準 LoRA」のみに限定する
`mlx-lm` は `lora` / `dora` / `full` を扱えますが、vLLM 側は **`modules_to_save` は `None` のみ対応、DoRA は未対応、bias 付き adapter も未対応、rank は `max_lora_rank` 以下**という制約を持っています。したがって、**変換対象として受け入れる MLX adapter は `fine_tune_type == "lora"` に限定**するのが安全です。 

## 2) 変換ロジックは 1 本に固定する
PEFT 形式への変換では、**重みファイル名・state_dict key・config 項目・スケーリングの意味**を揃える必要があります。PEFT 自身も「他形式から PEFT 形式へ変換するには、正しい key mapping と `adapter_config.json` が必要」と明記しています。したがって、trial ごとに変換方法を変えるのではなく、**custom exporter を 1 本に固定して、その exporter だけを信頼できる変換器として運用する**のが最善です。 

## 3) 変換の本質は「MLX の LoRA 意味論」を PEFT/vLLM に写すこと
MLX の `LoRALinear` は、`lora_a` を `(input_dims, r)`、`lora_b` を `(r, output_dims)` で持ち、forward は **`y + scale * ((x @ lora_a) @ lora_b)`** です。PEFT 側の LoRA は `lora_A.weight` / `lora_B.weight` を checkpoint に持ち、vLLM は通常 LoRA で **`lora_alpha / r`** を scaling として扱います。したがって、**変換で最も重要なのは shape 向きと scale/alpha の一致**です。標準 LoRA として対応づけるなら、実務上は **`lora_alpha = scale * r`** を守るのが基本になります。 

---

# 変換仕様として先に固定すべきもの

以下は、**実装ではなく仕様**として固定するべき項目です。

## A. ファイル構成
変換後ディレクトリは最低限これに揃えます。

- `adapter_model.safetensors`
- `adapter_config.json`

PEFT はこの 2 つを要求します。`README.md` は任意です。 

## B. 重みキーの命名
PEFT の LoRA checkpoint では、LoRA の学習パラメータは **`base_model.model....lora_A.weight`** と **`base_model.model....lora_B.weight`** 形式になります。PEFT docs は、**PEFT 形式へ変換するときは `base_model.model.` prefix を付ける必要がある**と明記しています。 

## C. MLX→PEFT のテンソル対応
MLX の `lora_a` / `lora_b` は PEFT と向きが異なるため、**転置が必要**です。  
つまり、仕様上は次を守る前提にします。

- MLX `lora_a` → PEFT `lora_A.weight`
- MLX `lora_b` → PEFT `lora_B.weight`
- 保存時に **PEFT が期待する向きへ転置**
- key prefix は **`base_model.model.`**

これは MLX の shape 定義と PEFT の checkpoint key 規約から直接導かれる対応です。 

## D. config の意味対応
PEFT `adapter_config.json` は少なくとも以下を整合させます。

- `peft_type = "LORA"`
- `r = MLX rank`
- `lora_alpha = MLX scale * rank`
- `lora_dropout = MLX dropout`
- `target_modules = MLX keys`
- `bias = "none"`
- `modules_to_save = null`
- `use_dora = false`
- `use_rslora = false` を初期方針にする
- `inference_mode = true`

vLLM の `PEFTHelper` が legal check で見るのは主に `r`, `lora_alpha`, `target_modules`, `bias`, `modules_to_save`, `use_dora`, `use_rslora` です。特に `modules_to_save != None`、`use_dora=True`、`bias!="none"`、`r > max_lora_rank` は弾かれます。 

---

# 変換専用フローに絞った実務手順

---

## Phase 1: Mac 側で「入力 artifact を凍結」する
ここでは **学習はしない**です。  
やることは、**変換元として使う MLX adapter を 1 個確定する**ことだけです。

固定する項目:

- 変換元 `adapter_path`
- 変換元 MLX ベースモデルの識別子
- `mlx-lm` のバージョン
- 元 adapter の `adapter_config.json`
- 元 adapter の `adapters.safetensors`

MLX loader は `adapter_config.json` と `adapters.safetensors` を前提に adapter を適用するので、**この 2 ファイルを source of truth とする**のが正しいです。 

### Phase 1 の完了条件
- `adapter_config.json` が存在する
- `adapters.safetensors` が存在する
- `fine_tune_type == "lora"` である
- `lora_parameters` に `rank / scale / dropout / keys` がある

---

## Phase 2: Mac 側で MLX→PEFT 変換する
ここが本体です。  
ただし実装は不要とのことなので、**変換器が満たすべき責務**だけを定義します。

### exporter の責務
1. **入力**: MLX adapter ディレクトリ  
2. **出力**: PEFT adapter ディレクトリ  
3. **重みファイル名**を `adapters.safetensors` → `adapter_model.safetensors` に変換  
4. **state_dict key** を PEFT 命名へ変換  
5. **テンソル向き**を PEFT が読む形へ変換  
6. **`adapter_config.json`** を PEFT/vLLM 互換で生成  
7. **manifest** を出力し、元 MLX config と変換後 config の対応を記録する

PEFT docs が言うとおり、変換で重要なのは「正しい parameter-name → tensor の対応」です。ここを曖昧にしないため、**exporter には manifest 出力を必須**にすると後で診断しやすいです。 

### Phase 2 の完了条件
- `adapter_model.safetensors` が生成されている
- PEFT 用 `adapter_config.json` が生成されている
- `r`, `lora_alpha`, `lora_dropout`, `target_modules` が source と整合している
- `bias="none"`, `modules_to_save=null`, `use_dora=false` になっている

---

## Phase 3: Mac 側で「静的検査」だけ行う
ここでは **推論品質の議論はしません**。  
やるのは、**変換後 artifact が形式的に妥当か**の確認だけです。

確認項目:

- 変換後ディレクトリに **`adapter_model.safetensors`** がある
- 変換後ディレクトリに **`adapter_config.json`** がある
- `peft_type == "LORA"`
- `r <= 32`
- `bias == "none"`
- `modules_to_save == null`
- `use_dora == false`
- `target_modules` が空でない
- manifest に **MLX scale → PEFT lora_alpha** の変換結果が記録されている

vLLM の legal check はこの種の config 項目に依存するので、**ここで落ちるものは Linux に持っていかない**のが効率的です。 

### Phase 3 の完了条件
- config 上の vLLM 非互換要素がない
- 変換ログ上、tensor 数・shape・dtype が不自然でない

---

## Phase 4: CUDA/Linux で PEFT/Transformers ロード確認
ここから先が **提出互換の本番検証**です。

### 4-1. official Nemotron BF16 ベースを固定する
Nemotron の公式 model card では `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` に対する Transformers / vLLM 利用例が示されています。したがって、**Linux 側の検証ベースはこのモデル系に固定**するのが自然です。 

### 4-2. base 単体が普通に読めることを確認する
Nemotron では tokenizer に chat template があり、`apply_chat_template(..., add_generation_prompt=True)` を使う流れが公式に示されています。`enable_thinking` は既定で `True` です。したがって、まず **base 単体で tokenizer / model / chat template が正常**であることを確認します。 

### 4-3. converted adapter を PEFT/Transformers で読む
Transformers の PEFT 統合では、**ローカルディレクトリに `adapter_config.json` と adapter weights があれば `from_pretrained()` / `load_adapter()` で読める**とされています。したがって、Linux 側の第一関門は **「converted adapter が普通の PEFT adapter としてロードできるか」**です。 

### 4-4. ここで見るべきもの
- missing key / unexpected key がない
- adapter が active になっている
- target module 数が不自然でない
- base 単体と adapter 有効時で出力が変わる

ここではまだ metric スコアは見ません。  
見るのは **「PEFT として成立しているか」**だけです。 

### Phase 4 の完了条件
- official base + converted adapter が PEFT/Transformers でロード可能
- 明らかな key mismatch がない
- adapter 適用時に forward が成立する

---

## Phase 5: CUDA/Linux で vLLM の metric 互換 smoke test を行う
ここが**変換タスクの最終判定**です。  
このコンペは evaluator が vLLM で LoRA を差して採点するので、**Transformers で通るだけでは十分ではありません**。

### 5-1. vLLM で local adapter directory を読む
vLLM の LoRA 機能は、`LoRARequest` に local path を渡して adapter を使えます。また vLLM docs でも、LoRA adapter をローカルディレクトリから扱う前提が示されています。 

### 5-2. vLLM で重要な legal 条件
vLLM `PEFTHelper` は少なくとも以下を確認します。

- `r` が `max_lora_rank` 以下
- `modules_to_save is None`
- `use_dora == false`
- `bias == "none"`

加えて、`use_rslora` が `false` なら scaling は `lora_alpha / r`、`true` なら `lora_alpha / sqrt(r)` になります。変換 fidelity の観点では、**最初は `use_rslora=false` に固定**するのが無難です。 

### 5-3. smoke test のやり方
ここでは **少数サンプルで十分**です。  
評価コードに合わせて、

- prompt 末尾に `\boxed{}` 指示を付ける
- tokenizer の chat template を適用する
- `enable_thinking=True` を使う
- evaluator 相当の生成設定で回す
- final answer 抽出が破綻していないかを見る

という最低限の確認をします。

Nemotron 側は `apply_chat_template()` を使う前提で、thinking は既定で有効です。評価コードもこれに近い流れです。 

### Phase 5 の完了条件
- vLLM が adapter をロードできる
- legal check で落ちない
- few-shot の smoke test で生成が成立する
- `\boxed{}` を含む回答が少なくとも壊れていない

---

# 提出パッケージ化の注意

これは **あなたが貼った metric コードに強く依存する実務注意**です。

## 1) zip には adapter を 1 つだけ入れる
`generate_standard_submission()` は zip 展開後に **最初に見つかった `adapter_config.json`** を拾います。  
つまり、**複数 trial の残骸を zip に混ぜるのは危険**です。

**推奨**:
- zip のトップ配下に提出対象 adapter ディレクトリを 1 個だけ置く
- 余計な `checkpoint-*` や別 adapter を入れない

## 2) fused model は不要
このコンペは **LoRA adapter 提出**です。  
したがって、MLX の `fuse` を使ってベースにマージした重みを提出物にする必要はありません。むしろ evaluator は **固定ベース + LoRA** で動くので、提出物は adapter だけにすべきです。MLX 側にも `fuse` はありますが、それは別用途です。 

## 3) `base_model_name_or_path` は「整合させる」が安全
PEFT config には base model 情報を入れるのが標準です。vLLM の filesystem resolver は `adapter_config.json` の `base_model_name_or_path` と base model 名の一致も見ます。一方で、現在のコンペ metric のように `LoRARequest` にローカルパスを直接渡す経路では、少なくとも `PEFTHelper` の legal check の主眼は `r / lora_alpha / target_modules / bias / modules_to_save / use_dora / use_rslora` です。  
したがって、**このフィールドは evaluator での唯一の成否判定とは限らないが、PEFT 標準メタデータとして整合させておくべき**、という扱いが妥当です。 

---

# 変換タスクとしての Done 条件

このタスクの完了条件は、精度改善ではなく次です。

1. **MLX adapter source が凍結されている**  
2. **PEFT 形式の `adapter_model.safetensors` + `adapter_config.json` が生成される**  
3. **static preflight で vLLM 非互換設定がない**  
4. **Linux で official Nemotron BF16 base + PEFT adapter がロードできる**  
5. **Linux で vLLM smoke test が通る**  
6. **提出 zip に adapter が 1 個だけ入っている**

この 6 条件を満たせば、  
**「MLX 由来 LoRA を、提出要件へ高忠実度に変換する」タスクとしては完了**です。

---

# あなたの元文書を、変換専用に直すなら削るべきもの

以下は今回のタスク範囲外なので、文書から外してよいです。

- 6bit で探索、BF16 で再学習、のような**探索戦略**
- rank / alpha / dropout / target_modules の**最適化議論**
- train.csv を使った**精度評価の設計**
- Mac 側での golden sample を使った**改善ループ**
- 「どの trial を採用するか」の**モデル選定議論**

代わりに残すべきなのは、

- **source artifact の固定**
- **変換仕様**
- **PEFT 互換検証**
- **vLLM metric 互換検証**
- **提出 zip の衛生管理**

です。

---

# 参考文献
- MLX LM LoRA ドキュメント: `mlx_lm.lora` が主コマンドで、adapter config と learned weights は既定で `adapters/` に保存され、`--adapter-path` で変更できます。生成は `mlx_lm.generate --adapter-path` で行えます。 
- MLX LM source (`tuner/utils.py`): loader は `adapter_config.json` を読み、LoRA 層を差し込み、`adapters.safetensors` をロードします。 
- MLX LM source (`tuner/lora.py`): `LoRALinear` の `lora_a`, `lora_b`, `scale`, forward の意味が確認できます。 
- PEFT checkpoint format: PEFT 形式には `adapter_model.safetensors` と `adapter_config.json` が必要で、LoRA keys は `base_model.model....lora_A.weight` / `lora_B.weight` 形式です。 
- Transformers PEFT docs: local directory に `adapter_config.json` と adapter weights があれば adapter をロードできます。 
- vLLM `PEFTHelper`: `modules_to_save=None`、DoRA 非対応、bias 非対応、rank 制限、`lora_alpha/r` スケーリングが確認できます。 
- vLLM LoRA docs / filesystem resolver: local adapter directory の扱いと、resolver での `adapter_config.json` / `base_model_name_or_path` の利用が確認できます。 
- NVIDIA Nemotron BF16 model card: `apply_chat_template()`、`enable_thinking=True` 既定、Transformers / vLLM 利用例が示されています。 
- MLX-LM issue #320: 少なくとも公開議論上、`mlx_lm.convert` は HF→MLX 方向が中心で、MLX→PyTorch/PEFT の reverse convert 需要があることが分かります。 
