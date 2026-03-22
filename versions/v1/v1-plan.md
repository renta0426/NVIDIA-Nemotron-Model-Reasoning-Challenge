# v1 plan

## Goal

現在の `code/Nemotron Reasoning Challenge - QLoRA Baseline.py` を土台に、メモリ使用量を大きく悪化させずに精度改善を狙う実用版を作る。

## Main changes

- repository rule に合わせて implementation を single-file に再構成する
- metric と同一の prompt 形式を維持する
- template + answer_type ベースの validation split を使う
- 100 step 打ち切りをやめ、実質 1 epoch 学習にする
- データ分析で学習テキスト長が近似 `p95=137` に収まることを確認し、`MAX_LENGTH` を 1024 -> 384 に圧縮する
- bit / text / symbol の hard templates を軽く増幅して学習配分を寄せる
- LoRA を `r=24, alpha=48` に増やす
- Nemotron patch / packaging / local quick validation を共通化する

## Code layout

- `code/train.py`: practical QLoRA training / packaging entrypoint with all helpers inlined for standalone execution

以下、kaggle環境で動作するまでに修正した内容。

---

# 0. 事前の重要変更（エラーではないが前提）
## QLoRA/4bit → 非量子化 BF16 LoRA へ変更
### 元の状態
- `BitsAndBytesConfig(...)`
- `quantization_config=bnb_config`
- `prepare_model_for_kbit_training(model)`
- `optim="paged_adamw_8bit"`

### 修正
- `BitsAndBytesConfig` を使わない
- `quantization_config=...` を削除
- `prepare_model_for_kbit_training(model)` を削除
- モデルロードを BF16 に変更
- optimizer を通常版に変更

```python
torch_dtype=torch.bfloat16
bf16=True
fp16=False
optim="adamw_torch"
```

---

# 1. `__file__` が未定義
## エラー
```python
NameError: name '__file__' is not defined
```

## 原因
Notebook / Kaggle では `__file__` が定義されない。

## 修正
```python
# 削除
REPO_ROOT = Path(__file__).resolve().parents[3]
TRAIN_PATH = REPO_ROOT / "data/train.csv"
BASE_MODEL = REPO_ROOT / "1"
```

を、絶対パスに置換：

```python
TRAIN_PATH = Path("/kaggle/input/nvidia-nemotron-3-reasoning-challenge/train.csv")
BASE_MODEL = "/kaggle/input/models/metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1"
```

---

# 2. `evaluation_strategy` が未対応
## エラー
```python
TypeError: TrainingArguments.__init__() got an unexpected keyword argument 'evaluation_strategy'
```

## 原因
その環境の `TrainingArguments` は `evaluation_strategy` ではなく `eval_strategy` を受ける。

## 修正
```python
evaluation_strategy="steps",
```

を

```python
eval_strategy="steps",
```

に変更。

---

# 3. `device_map="auto"` で offload 先が必要
## エラー
```python
ValueError: The current `device_map` had weights offloaded to the disk ... Please provide an `offload_folder` for them in `from_pretrained`.
```

## 原因
`device_map="auto"` で一部重みをディスク退避する必要があり、`offload_folder` 指定が必要だった。  
Nemotron/MoE 系で起きやすい。

## 修正
モデルロードに `offload_folder` を追加。

```python
OFFLOAD_DIR = OUTPUT_ROOT / "offload"
OFFLOAD_DIR.mkdir(parents=True, exist_ok=True)

model = AutoModelForCausalLM.from_pretrained(
    ...,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    offload_folder=str(OFFLOAD_DIR),
)
```

---

# 4. `OFFLOAD_DIR` 未定義
## エラー
```python
NameError: name 'OFFLOAD_DIR' is not defined
```

## 原因
`from_pretrained(..., offload_folder=str(OFFLOAD_DIR))` を追加したが、  
その前に `OFFLOAD_DIR` を定義していなかった。

## 修正
モデルロード前に定義・作成。

```python
OFFLOAD_DIR = OUTPUT_ROOT / "offload"
OFFLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

---

# 5. ディスク容量不足
## エラー
```python
OSError: [Errno 28] No space left on device
```

派生して:
- papermill 保存失敗
- notebook JSON 破損系エラー
- nbconvert 失敗

## 原因
主に以下で `/kaggle/working` を圧迫した。
- `offload_folder`
- checkpoint 保存
- 学習後評価の出力
- notebook 実行ログの肥大化

## 修正
### 5-1. offload先を `/tmp` に変更
```python
OFFLOAD_DIR = Path("/tmp/nemotron_offload")
OFFLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

```python
offload_folder=str(OFFLOAD_DIR)
```

### 5-2. checkpoint 保存を停止
```python
save_strategy="no",
```

### 5-3. ベストモデル自動ロードは後で無効化
この時点ではセットで問題になったので最終的に後述の修正。

### 5-4. 学習後評価を停止
```python
RUN_POST_TRAIN_EVAL = False
```

### 5-5. 可能なら EarlyStopping を外す
```python
callbacks=[]
```
または callbacks 自体を削除。

### 5-6. 再実行前に掃除
```python
import shutil, os
shutil.rmtree("/kaggle/working/nemotron_q_lora_v1", ignore_errors=True)
shutil.rmtree("/tmp/nemotron_offload", ignore_errors=True)
if os.path.exists("/kaggle/working/submission_v1.zip"):
    os.remove("/kaggle/working/submission_v1.zip")
```

---

# 6. `group_by_length` が未対応
## エラー
```python
TypeError: TrainingArguments.__init__() got an unexpected keyword argument 'group_by_length'
```

## 原因
その環境の `TrainingArguments` では `group_by_length` がサポートされていない。

## 修正
```python
group_by_length=True,
```

を削除。

---

# 7. `load_best_model_at_end=True` と `save_strategy="no"` が衝突
## エラー
```python
ValueError: --load_best_model_at_end requires the save and eval strategy to match
- Evaluation strategy: IntervalStrategy.STEPS
- Save strategy: SaveStrategy.NO
```

## 原因
checkpoint を保存しない設定なのに、  
「最後にベストモデルを読み込む」が有効だった。

## 修正
```python
load_best_model_at_end=False,
```

に変更。

最終的にこの組み合わせに修正：

```python
eval_strategy="steps",
save_strategy="no",
load_best_model_at_end=False,
```

---

# 8. 速度改善のための設定変更（エラーではない）
正常動作後、速度が遅かったため調整。

## 状況
- `6/668`
- GPU使用率 50%
- 96GB 中かなり余裕あり

## 推奨修正
### 8-1. gradient checkpointing を無効化
```python
gradient_checkpointing=False,
```

### 8-2. バッチを増やして accumulation を減らす
```python
TRAIN_BATCH_SIZE = 2
GRAD_ACCUM_STEPS = 8
```

さらに余裕があれば：

```python
TRAIN_BATCH_SIZE = 4
GRAD_ACCUM_STEPS = 4
```

### 8-3. 学習中 eval を止めるなら
```python
eval_strategy="no",
```

### 8-4. `TRAIN_BATCH_SIZE` が `per_device_train_batch_size` に対応
コード上は直接 `per_device_train_batch_size` ではなく、

```python
per_device_train_batch_size=TRAIN_BATCH_SIZE
```

なので、触るべき変数は `TRAIN_BATCH_SIZE`。

---

# 最終的に入った主要修正一覧
以下が実際の要点です。

## パス修正
```python
TRAIN_PATH = Path("/kaggle/input/nvidia-nemotron-3-reasoning-challenge/train.csv")
BASE_MODEL = "/kaggle/input/models/metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1"
```

## 非量子化 BF16 化
```python
torch_dtype=torch.bfloat16
bf16=True
fp16=False
optim="adamw_torch"
```

## `TrainingArguments` 互換修正
```python
eval_strategy="steps"   # evaluation_strategy ではない
# group_by_length は削除
```

## offload 対応
```python
OFFLOAD_DIR = Path("/tmp/nemotron_offload")
OFFLOAD_DIR.mkdir(parents=True, exist_ok=True)

offload_folder=str(OFFLOAD_DIR)
```

## 容量対策
```python
save_strategy="no"
load_best_model_at_end=False
RUN_POST_TRAIN_EVAL = False
```

## 速度対策
```python
TRAIN_BATCH_SIZE = 2   # または 4
GRAD_ACCUM_STEPS = 8   # または 4
gradient_checkpointing=False
```

---

# 一行要約
今回ハマったのは主にこの7つです。

1. `__file__` 問題  
2. `evaluation_strategy` 非対応  
3. `offload_folder` 必須  
4. `OFFLOAD_DIR` 未定義  
5. ディスク容量不足  
6. `group_by_length` 非対応  
7. `load_best_model_at_end` と `save_strategy="no"` の衝突  

---

#結果

実行時間: 4h

パブリックリーダーボードスコア:0.47~0.52

所感: ベースラインや自己ベスト(QLoRA Baseline.pyで
0.62)と比較して大幅悪化

