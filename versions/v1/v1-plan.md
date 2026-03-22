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

---
実行ログ
Torch: 2.12.0.dev20260315+cu128
CUDA available: True
GPU: NVIDIA RTX PRO 6000 Blackwell Server Edition
Base model: /kaggle/input/models/metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1
Applied hard-template boost: +2130 rows
[train] rows=10679
template
bit_manipulation    2186
gravity_constant    1437
roman_numeral       1418
symbol_equation     2082
text_decryption     2121
unit_conversion     1435
Name: count, dtype: int64
answer_type
8bit_binary          2186
multiword_text       2121
numeric              3791
roman_numeral        1418
symbolic_or_other    1163
Name: count, dtype: int64
[valid] rows=951
template
bit_manipulation    160
gravity_constant    160
roman_numeral       158
symbol_equation     156
text_decryption     158
unit_conversion     159
Name: count, dtype: int64
answer_type
8bit_binary          160
multiword_text       158
numeric              388
roman_numeral        158
symbolic_or_other     87
Name: count, dtype: int64
Built completion-only dataset: kept=10679 dropped=0
Built completion-only dataset: kept=951 dropped=0
Loading base model ...
Before patch: is_fast_path_available = True
After patch : is_fast_path_available = False
Patched MoE dtype classes: ['NemotronHMOE']
Patched NemotronHMLP.forward
trainable params: 651,988,992 || all params: 32,229,926,336 || trainable%: 2.0229
Start training v1...
 [668/668 3:57:48, Epoch 1/1]
Step	Training Loss
10	40.007956
20	13.193459
30	9.474236
40	7.380049
50	7.089324
60	6.656832
70	6.738625
80	6.592314
90	6.570359
100	6.033590
110	6.550760
120	6.404257
130	6.518420
140	6.443168
150	6.331401
160	6.591895
500	5.398898
510	5.202986
520	4.933583
530	4.554744
540	4.622798
550	5.275050
560	4.545795
570	5.011707
580	4.861792
590	4.844991
600	4.798605
610	5.059732
620	5.006035
630	4.817180
640	5.081921
650	4.708760
660	4.663592

Saving adapter and packaging submission...
The following generation flags are not valid and may be ignored: ['temperature']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
WARNING:transformers_modules._1.modeling_nemotron_h:NemotronH requires an initialized `NemotronHHybridDynamicCache` to return a cache. None was provided, so no cache will be returned.
{
  "alora_invocation_tokens": null,
  "alpha_pattern": {},
  "arrow_config": null,
  "auto_mapping": null,
  "base_model_name_or_path": "/kaggle/input/models/metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1",
  "bias": "none",
  "corda_config": null,
  "ensure_weight_tying": false,
  "eva_config": null,
  "exclude_modules": null,
  "fan_in_fan_out": false,
  "inference_mode": true,
  "init_lora_weights": true,
  "layer_replication": null,
  "layers_pattern": null,
  "layers_to_transform": null,
  "loftq_config": {},
  "lora_alpha": 48,
  "lora_bias": false,
  "lora_dropout": 0.05,
  "megatron_config": null,
  "megatron_core": "megatron.core",
  "modules_to_save": null,
  "peft_type": "LORA",
  "peft_version": "0.18.1",
  "qalora_group_size": 16,
  "r": 24,
  "rank_pattern": {},
  "revision": null,
  "target_modules": [
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
    "q_proj"
  ],
  "target_parameters": null,
  "task_type": "CAUSAL_LM",
  "trainable_token_indices": null,
  "use_dora": false,
  "use_qalora": false,
  "use_rslora": true
}
Quick validation accuracy over 128 rows: 0.0469

---

## 追記考察（2026-03-22）

### 結論

今回の実行ログを見ても、`v1` に対する主たる考察は変わらない。  
`v1` は自己ベストの `QLoRA Baseline.py`（public LB `0.62`）より明確に悪く、悪化の主因は **metric の誤読** というより **学習 recipe の逸脱** にあるとみてよい。

ただし、ひとつ補正が必要である。  
`Quick validation accuracy over 128 rows: 0.0469` は public LB `0.47~0.52` と乖離が大きすぎるため、`v1` のローカル quick validation は **絶対的な性能指標としてはかなり信用しにくい**。  
README の Evaluation にある本番条件は `vLLM`、`max_tokens=7680`、`temperature=0.0`、`top_p=1.0`、`max_num_seqs=64`、`max_model_len=8192` である一方、この quick check は Hugging Face `generate` ベースかつ `max_new_tokens=256` であり、推論条件が一致していない。

### 今回のログが補強した点

1. **step inflation 仮説はかなり強くなった**
   - ログ上、hard-template boost により `+2130 rows` され、学習データは `10679` 行。
   - 実際の学習は `668/668 step` で完走している。
   - baseline は `max_steps=100` で止めていたため、`v1` はかなり長く回っている。
   - 小さく整った synthetic データに対して、これは過学習や最終 checkpoint 劣化を招きやすい。

2. **`eval/save/best model selection` を外した影響は大きい**
   - `v1` は実行都合で `eval_strategy="no"`、`save_strategy="no"`、`load_best_model_at_end=False` に寄っており、良い途中 checkpoint を拾えない。
   - 学習損失は下がっているが、それが leaderboard 最適とは限らない。
   - 特に `668 step` 走らせて最後の状態をそのまま提出する構成は、baseline より不利である可能性が高い。

3. **hard-template boost は方向として分かるが、全体 accuracy を落としうる**
   - boost 後の train 分布は `bit_manipulation / text_decryption / symbol_equation` 側にかなり寄っている。
   - この競技は 6 テンプレート全体の accuracy で決まるため、難所強化がそのまま全体改善になるとは限らない。

### 今回のログで修正すべき見方

- `Quick validation accuracy 0.0469` は「`v1` が完全に壊れている」ことの直接証拠とは言い切れない。
- むしろ、Hugging Face 側の生成経路では `temperature` 無視警告や cache 周りの warning も出ており、**ローカル quick validation が leaderboard proxy として弱い**ことを示している。
- したがって、`v1` の local quick val は比較用の軽い smoke test 以上には使わず、採択判断は public LB と recipe の妥当性で見るべき。

### 現時点の実務判断

- `v1` をこのまま伸ばす優先度は高くない。
- `v1` を再挑戦するなら、新しい工夫を足す前に以下を先に戻すべき。
  - 4bit QLoRA へ戻す
  - `eval/save/load_best_model_at_end` を復元する
  - `max_steps` を baseline 寄りに再導入する
  - hard-template boost は弱めるか、ablation 前提で扱う

- バージョン優先度は引き続き `v7` 本命、`v4` 次点でよい。
  - `v7` は hardest templates に specialist 容量を割きつつ、最終的に 1 adapter に merge できる。
  - `v4` は hard-example mining と hard validation がこの競技の構造に素直で、失敗しにくい。
