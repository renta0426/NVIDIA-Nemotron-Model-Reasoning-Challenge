全ての出力:
train rows: 9500
id	prompt	answer
0	00066667	In Alice's Wonderland, a secret bit manipulati...	10010111
1	000b53cf	In Alice's Wonderland, a secret bit manipulati...

family
binary     1602
gravity    1597
unit       1594
text       1576
roman      1576
symbol     1555
Name: count, dtype: int64

processed 9000/9500 rows...
teacher scan done in 0.7s

family	total	solved	coverage
0	binary	1602	306	0.191011
1	gravity	1597	0	0.000000
2	roman	1576	1576	1.000000
3	symbol	1555	0	0.000000
4	text	1576	0	0.000000
5	unit	1594	1594	1.000000
overall coverage: 0.3658947368421053
family  teacher_solver                  
unit    unit_numeric_rule                   1594
roman   roman_standard                      1576
binary  binary_bit_permutation_inversion     306
Name: count, dtype: int64

distilled records: 675
family
roman      195
unit       195
binary     180
symbol      60
text        30
gravity     15
Name: count, dtype: int64
record_type
solved_trace    520
terse_boxed     155
Name: count, dtype: int64
id	family	answer	prompt	rationale	record_type	solver
0	412a209f	symbol	3032	In Alice's Wonderland, a secret set of transfo...	None	terse_boxed	None
1	4b5860cc	roman	III	In Alice's Wonderland, numbers are secretly co...	This is standard Roman numeral conversion. Con...	solved_trace	roman_standard
2	1a20cfff	unit	40.92	In Alice's Wonderland, a secret unit conversio...	None

tokenized_samples: 675
bad_rows: 0
total tokens: 141947
total supervised tokens: 36402
avg tokens/sample: 210.29185185185185
avg supervised/sample: 53.92888888888889

packed blocks: 369
steps_per_epoch: 47

Loading weights:   0%|          | 0/6243 [00:00<?, ?it/s]
Patched transformers_modules._1.modeling_nemotron_h: is_fast_path_available = False
LoRA target modules: ['down_proj', 'k_proj', 'o_proj', 'q_proj', 'up_proj', 'v_proj']

trainable params: 434,659,328 || all params: 32,012,596,672 || trainable%: 1.3578

total_optim_steps: 47
warmup_steps: 10


 [47/47 27:30, Epoch 1/1]
Step	Training Loss
10	16.887514
20	7.836857
30	3.115557
40	2.738178
TrainOutput(global_step=47, training_loss=6.834465919656957, metrics={'train_runtime': 1696.7141, 'train_samples_per_second': 0.217, 'train_steps_per_second': 0.028, 'total_flos': 2.6916806074023936e+16, 'train_loss': 6.834465919656957, 'epoch': 1.0}

Created /kaggle/working/submission.zip (1504.08 MB)
ZIP contents: ['adapter_model.safetensors', 'README.md', 'adapter_config.json']
✓ submission.zip is ready.

================================================================================
ID: 00066667
Each output bit is determined independently from one input bit (possibly flipped). The recovered bit mapping is: o1=i3, o2=i4, o3=i5, o4=i6, o5=i7, o6=i8, o7=i1, o8=i2. Applying this mapping to 00110100 gives 11010000.
</think>
\boxed{11010000}<|im_end|>
================================================================================
ID: 000b53cf
Each output bit is determined independently from one input bit (possibly flipped). The recovered bit mapping is: o1=i3, o2=i4, o3=i5, o4=i6, o5=i7, o6=i8, o7=i1, o8=i2. Applying this mapping to 11100000 gives 10000011.
</think>
\boxed{10000011}<|im_end|>
================================================================================
ID: 00189f6a
Apply the rule from the examples to the target.
</think>
\boxed{kingdom hides inside mountain}<|im_end|>

---

今回のモデルの結果：LBスコア0.47と、baseline/nvidia-nemotron-sfttrainer-training.ipynbの0.68より大幅悪化。

ーーーー
考察：

重要なのは **「答え」ではなく「検証済みの解法軌道」** を増やすことです。

## 結論
### 今やるべき順番
1. **train.csv から本当に取れる教師信号を再調査**
   - family分類
   - parser
   - solver
   - マッチ条件
   を見直す  
   → **最優先**

2. それでも取れない family が残るなら、  
   **強い外部モデルに「解法説明候補」を作らせる**  
   → ただし **そのまま信じない**

3. 外部モデルの出力は必ず
   - train の正解と一致
   - できれば規則を programmatic に検証
   できたものだけ採用  
   → **verified pseudo-teacher として蒸留**

---

## 端的に言うと
- **今不足しているのはデータ件数ではない**
- **不足しているのは、正しい規則復元付きの教師信号**
です。

だから最初にやるべきは  
**「train.csv にまだ眠っている verified teacher を掘る」こと**です。

---

## 外部モデルを使うべきか
### 使ってよい場合の答え
**Yes, ただし第二優先。**

でも目的は
- 模範解答を“作る”ことではなく、
- **模範的な reasoning trace の候補を作ること**

です。

train にはすでに answer があるので、欲しいのは  
**「どうその答えに至るか」** です。

---

## 重要な注意
### 外部モデルの CoT をそのまま蒸留するのは危険
理由:
- もっともらしいが規則が間違っていることがある
- hidden に一般化しないことがある
- family ごとの本当の transformation を外していることがある

なので使い方はこうです。

### 良い使い方
- prompt + answer を与える
- **規則候補**を出させる
- その規則で examples を再現できるか確認
- target に適用して answer と一致するか確認
- 一致したものだけ採用

つまり、
**LLM を teacher ではなく hypothesis generator として使う**
のが正しいです。

---

## 優先順位
### まずやるべき
- gravity 0件
- text 0件
- symbol 0件
- binary 0.19

これはかなりの確率で  
**「本当に解けない」より「今の parser/solver が prompt 形式を拾えていない」**  
です。

なので先に
- 生 prompt を数十件見る
- 例の書式を把握する
- regex / extraction を直す
- solver DSL を増やす

べきです。

---

## 判断基準
### train 再調査で十分な場合
coverage が例えば
- gravity 0.5+
- binary 0.4〜0.6
- text 0.3+
- symbol 0.1+
まで上がるなら、  
まずはそれで再学習する価値が高いです。

### それでもダメな場合
外部モデルで
- rationale生成
- family rule仮説生成
- synthetic explanation生成
をやって、  
**検証通過分だけ蒸留**します。

---

## 一言でまとめると
- **Yes：まず train.csv の再調査が本筋**
- **Yes：本当になければ外部モデル蒸留は有効**
- ただし蒸留対象は **answer ではなく verified trace**
- 外部モデルは **そのまま教師にせず、検証付きで使う**

---

## 実務的な最短方針
1. gravity/text/symbol の train サンプルを目視
2. parser 修正
3. solver 拡張
4. coverage 再計算
5. まだ低ければ GPT/Gemini に **trace候補生成**
6. **一致検証したものだけ** teacher 化
7. 再蒸留
