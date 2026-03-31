# Binary問題でこれまで試した合成データアプローチの整理

## 目的

このメモは、binary 問題に対してこれまで repo 内で実際に試した「学習データ側の介入」を、README 準拠の評価前提で、**分析レポート → 学習 CSV → manifest → 生成スクリプト**の順に遡って整理したものです。

前提として `README.md` の評価は `\boxed{}` 優先抽出で、boxed が崩れると fallback 抽出に落ち、binary のような exact 8-bit 文字列はそこで非常に壊れやすいです。したがって binary 用の合成データでは、**規則学習そのもの**だけでなく、**leading zero を含む 8-bit を boxed で短く閉じる出力契約**も重要になります。(`README.md:31-46`)

なお、この文書でいう「合成データ」は、外部 LLM で自由生成した大規模 synthetic corpus ではなく、主に以下を指します。

- 解析済み `train.csv` 行から作った **rule-based teacher trace**
- 既存行の一部を **boxed-only supervision** に落とした teacher
- binary trace を **DSL / hybrid narrative** に再表現した teacher
- 旧 800 行版のような **binary CoT 差し替え mix**

---

## まず結論だけ

これまで binary で試したデータ介入は、大きく分けて 6 系統ありました。

| 系統 | 学習 CSV | binary 行数 | binary teacher の形 | 何を変えたか | 観測された結果 |
| --- | --- | ---: | --- | --- | --- |
| 1 | `rule_based_verified_600_training_data.csv` | 100 | 短い rule-based trace | verified-only で 6 family を均等 100 ずつ | sample では binary `5/10`。主失敗は formatting collapse |
| 2 | `rule_based_verified_600_training_data_v2.csv` | 300 | 長い自然言語 binary CoT | 500 非 binary を維持し、binary を 300 行へ置換 | binary `5/10` 据え置き、非 binary に副作用 |
| 3 | `rule_based_binary_guarded_800_training_data.csv` | 200 | short trace + exact 8-bit contract | verified-only のまま binary を bonus 増量し、`box-only-final` を強調 | `result/0` で binary `11/60`、根本改善には不足 |
| 4 | `phase1_assistant_only_training_data.csv` | 280 | 160 trace + 120 boxed-only | binary / text / symbol に answer-only row を導入 | `result/1` で overall 改善、binary は `12/60` 止まり |
| 5 | `phase2_binary_dsl_training_data.csv` | 280 | 160 DSL trace + 120 boxed-only | Phase 1 の 160 verified binary 行だけ DSL 化 | `result/2` で official-like `13/60`、exact は `9/60` |
| 6 | `phase2_binary_hybrid_training_data.csv` | 280 | 160 hybrid narrative + 120 boxed-only | DSL を自然言語化。ID 集合は Phase 2 DSL と同一 | `result/2-1` で binary `8/60` に悪化 |

重要なのは、**binary に対して「量を増やす」「自然言語 CoT を厚くする」「DSL にする」「DSL を自然言語化する」まで一通り試している**ことです。そのうえで、`bit_structured_byte_formula` の本丸は最後まで押し上がっていません。(`baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:309-407`, `baseline/cot/phase0_offline_eval/result/0/reports/train_rule_based_cot_baseline_result0_deep_analysis.md:107-166`, `baseline/cot/phase0_offline_eval/result/1/reports/phase1_result1_deep_analysis.md:134-171`, `baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md:135-182`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:95-179`)

---

## 1. `rule_based_verified_600_training_data.csv`

### 何を狙ったデータか

最初の基礎版です。`verified_trace_ready` のみを使い、6 family を **100 行ずつ均等**に揃えた 600 行構成でした。binary もこの時点では **100 行だけ**です。(`baseline/cot/build_rule_based_training_dataset.py:15-27,159-219`, `baseline/cot/rule_based_verified_600_training_manifest.json:1-49`)

### 生成方法

生成スクリプトは `baseline/cot/build_rule_based_training_dataset.py` です。

1. ソースは `cuda-train-data-analysis-v1/artifacts/train_verified_trace_ready_v1.csv`
2. `selection_tier == verified_trace_ready`
3. `verified_trace_ready == true`
4. `teacher_solver_candidate` が空でない
5. family ごとに quota を満たすように `template_subtype` 単位の round-robin で選ぶ
6. 各 family に対し短い rule-based `<think>...</think>` を生成する

binary trace は特に単純で、`teacher_solver_candidate` や structured formula 名から rule 名を作り、

```text
<think>The examples match the verified bit rule xor(ror1,shr3).
Applying that same transformation to 10000011 gives 11010001.</think>
```

のような短い自然言語 trace を付けています。(`baseline/cot/build_rule_based_training_dataset.py:271-347`)

### binary に対するデータ上の特徴

- binary は 100 行だけ
- すべて `verified_trace_ready`
- すべて trace teacher
- `<think>` 内に query 適用結果や最終 answer がそのまま入る
- boxed-only row はまだ無い

manifest 上の内訳は以下です。

- `bit_manipulation = 100`
- `bit_structured_byte_formula = 34`
- `bit_other = 33`
- `bit_permutation_inversion = 33`
- binary solver は `binary_bit_permutation_bijection 31`, `binary_structured_byte_formula 29`, `binary_affine_xor 24` など  
  (`baseline/cot/rule_based_verified_600_training_manifest.json:6-49`)

### 観測された結果

sample 分析では binary は `5/10` で、誤答の多くが `1`, `001`, `-0`, `10` のような **短い断片抽出崩壊**でした。つまりこの段階の主問題は、「binary rule を全く学べていない」よりも、**README の boxed-first 評価に対して final answer emission が弱い**ことでした。(`baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:52-79,87-139`)

---

## 2. `rule_based_verified_600_training_data_v2.csv` の旧 800 行版

### 何を狙ったデータか

これは「binary だけを増やせば改善するか」を見るための、**旧 binary-heavy 800 行版**です。

分析レポート上では、

- non-binary 500 行は 600 版から維持
- binary 100 行は置換
- 置換先は「baseline 側 binary CoT 300 行」

と明記されています。(`baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:309-346`)

### 生成方法

この旧 800 行版については、**現 repo に再現用スクリプトが残っていません**。  
そのため生成方法は、以下 2 つから再構成するしかありません。

1. 上記分析レポートの説明
2. 実在する CSV `baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv`

CSV を見ると実際に

- 総行数 `800`
- `gravity/unit/roman/text/symbol` は各 `100`
- `binary` は `300`

になっており、レポート記述と一致します。実際の binary row は rule-based short trace ではなく、次のような**長い自然言語 CoT**でした。

```text
The transformation seems complex and non-linear. Analyzing the provided examples:
01010001 -> 11011101
00001001 -> 01101101
...
```

別の行では

```text
The task is to deduce a bit manipulation rule from examples and apply it.
10001110 -> 00100110
10011001 -> 01000100
...
```

となっており、少なくとも CSV 上では **「短い verified rule trace」ではなく「長めの natural-language binary CoT」** が入っています。(`baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv:1-12` と実ファイル確認)

### binary に対するデータ上の特徴

- binary 行数を `100 -> 300` に増量
- non-binary 構成は基本維持
- binary teacher は short trace ではなく、より長い reasoning 風 CoT
- boxed-only supervision はまだ無い

### 観測された結果

レポート上の比較では、binary は **`5/10 -> 5/10` で改善なし**でした。  
ただし failure mode は変わっており、

- 600 版: `1`, `001`, `-0`, `10` のような崩れた誤答
- 旧 800 版: `00011101`, `11000010`, `00011100` のような **整った 8-bit だが間違った誤答**

へ移っています。つまり「binary を厚くした」こと自体は **format を少し整えた**ものの、**規則推定そのもの**は改善していません。さらに gravity / text にも副作用が出ました。(`baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:326-407`)

---

## 3. `rule_based_binary_guarded_800_training_data.csv`

### 何を狙ったデータか

旧 800 行版の反省を受けて作られた、**binary_guarded 800** です。  
狙いは「binary を増やす」こと自体ではなく、

- verified-only を維持する
- 危ない binary 行を混ぜない
- binary trace では最終 8-bit 答えを `<think>` 内で再掲しない
- `leading zeros` と `box-only-final` を強く意識させる

ことでした。(`baseline/cot/build_rule_based_training_dataset_binary_guarded.py:21-37,202-315`, `baseline/cot/output-csv/rule_based_binary_guarded_800_manifest.json:1-70`)

### 生成方法

生成スクリプトは `baseline/cot/build_rule_based_training_dataset_binary_guarded.py` です。

#### 3.1 ソースとフィルタ

- source: `cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv`
- 基本は `verified_trace_ready` のみ
- binary bonus は「strong verified rule」のみ追加

strong binary bonus 候補は、

- 強い binary solver に属するか
- `bit_structured_formula_safe_support >= 4`
- もしくは `bit_structured_formula_abstract_support >= 20`

で判定されます。(`baseline/cot/build_rule_based_training_dataset_binary_guarded.py:202-225,288-315`)

#### 3.2 quota 設計

- base quota: 6 family × 100 = 600
- bonus quota:
  - binary +100
  - gravity +25
  - unit +25
  - roman +25
  - text +25

合計 800 行です。(`baseline/cot/build_rule_based_training_dataset_binary_guarded.py:21-37`)

manifest の実数も

- binary `200`
- gravity `125`
- unit `125`
- roman `125`
- text `125`
- symbol `100`

になっています。(`baseline/cot/output-csv/rule_based_binary_guarded_800_manifest.json:5-29`)

#### 3.3 binary teacher の作り方

binary trace 自体は short trace のままですが、600 版と違って

```text
<think>The examples match the verified bit rule xor(shl1,shr4).
I apply the same transformation to the query byte and keep the result as one exact 8-bit binary string with leading zeros.
I will present only that final byte in the box.</think>
```

のように、**答えを `<think>` に書かず**、

- exact 8-bit
- leading zeros
- final byte は box にだけ出す

を明示しています。(`baseline/cot/build_rule_based_training_dataset_binary_guarded.py:365-427`, `baseline/cot/output-csv/rule_based_binary_guarded_800_training_data.csv:1-12`)

manifest にも

- `uses_only_verified_trace_ready_rows = true`
- `binary_bonus_requires_strong_verified_rule = true`
- `binary_trace_does_not_repeat_final_answer_inside_think = true`

が残っています。(`baseline/cot/output-csv/rule_based_binary_guarded_800_manifest.json:55-66`)

### 観測された結果

この CSV は `train_rule_based_cot_baseline.ipynb` の学習データとして使われ、Phase 0 `result/0` の対象になりました。(`baseline/cot/train_rule_based_cot_baseline.ipynb:248,292`)

結果は

- overall `216/320 = 0.6750`
- binary `11/60 = 0.1833`
- `bit_structured_byte_formula = 1/14`

で、**format 寄りの改善はあるが、本丸の structured binary を押し切れていない**状態でした。誤答 49 件の多くは「gold 8-bit を一度も安定提示できていない」形です。(`baseline/cot/phase0_offline_eval/result/0/reports/train_rule_based_cot_baseline_result0_deep_analysis.md:9-21,107-166`)

---

## 4. `phase1_assistant_only_training_data.csv`

### 何を狙ったデータか

Phase 1 は「binary teacher そのもの」だけでなく、**データの役割分担**を変えたのがポイントです。

- verified row は short trace teacher のまま使う
- 一部 hard family は answer-only row を追加する
- 特に binary では **trace と boxed-only を分離**する

という設計になっています。(`baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.py:29-42,297-348,463-570`, `baseline/cot/phase1_assistant_only/artifacts/phase1_assistant_only_manifest.json:1-78`)

### 生成方法

source は `train_row_analysis_v1.csv` です。  
quota は以下の 2 層です。

#### 4.1 verified mix

- gravity `120`
- unit `120`
- roman `120`
- text `100`
- bit `160`
- symbol `60`

合計 `680` 行。すべて `verified_trace_ready` です。(`baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.py:29-36,297-316`)

#### 4.2 answer-only mix

- text `20`
- bit `120`
- symbol `80`

合計 `220` 行。すべて `answer_only_keep` です。(`baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.py:37-42,328-348`)

#### 4.3 出力 schema

出力は `assistant_style` を持つようになり、

- `trace_boxed`: `generated_cot` あり
- `boxed_only`: `generated_cot == ""`

に分かれます。binary では

- verified binary trace `160`
- answer-only binary boxed row `120`

です。(`baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.py:463-570`, `baseline/cot/phase1_assistant_only/artifacts/phase1_assistant_only_manifest.json:20-78`)

実データを見ると、boxed-only row は本当に `generated_cot` が空です。

```text
id=19f4b3d6, label=binary, assistant_style=boxed_only, source_selection_tier=answer_only_keep
generated_cot=""
```

つまりこの行では、assistant teacher は実質的に **最終 `\boxed{answer}` のみ**です。実装側でも boxed-only row が CoT を持たないことを検証しています。(`baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.py:492-510`)

### binary に対するデータ上の意味

この設計は、「binary で長い reasoning を学ばせる」よりも、

- 一部は短い verified trace で rule hint を与える
- 一部は boxed-only で exact final answer closure だけを学ばせる

という分担です。

### 観測された結果

`result/1` では overall は `0.7031` に改善しましたが、binary は **`11/60 -> 12/60`** と微増に留まりました。

- `verified_trace_ready`: `7/20 -> 8/20`
- `answer_only_keep`: `3/20 -> 3/20`
- `manual_audit_priority`: `1/20 -> 1/20`

で、主改善は binary ではなく text / gravity の answer emission 安定化でした。(`baseline/cot/phase0_offline_eval/result/1/reports/phase1_result1_deep_analysis.md:9-23,134-171`)

---

## 5. `phase2_binary_dsl_training_data.csv`

### 何を狙ったデータか

Phase 2 DSL は、「Phase 1 の 900-row mixture は維持したまま、**verified binary 160 行だけ**をもっと構造化された teacher に置き換えたらどうなるか」を見る実験です。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_manifest.json:1-75`, `baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md:9-29`)

### 生成方法

repo の現行スクリプト `build_phase2_binary_dsl_dataset.py` は今は hybrid 版を出力する形ですが、DSL artifact / manifest とレポートから、DSL 版の設計は以下まで追えます。

#### 5.1 mixture は Phase 1 と同一

- 総行数 `900`
- family counts も同一
- `assistant_style_counts`: `trace_boxed=680`, `boxed_only=220`
- binary は `160 trace + 120 boxed_only`

つまり **変えたのは 160 行の verified binary trace だけ**です。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_manifest.json:1-75`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:12-29`)

#### 5.2 DSL trace の形

実際の CSV を見ると、binary trace は次のような DSL です。

```text
<think>family=binary
rule=xor(shl1,shr4)
query=10011111
step1=shl1(query)=00111110
step2=shr4(query)=00001001
apply=xor(step1,step2)
constraints=exact_8bit,leading_zeros,box_only_final</think>
```

別の byte transform では

```text
<think>family=binary
rule=lrot
query=01100000
apply=lrot(query)
constraints=exact_8bit,leading_zeros,box_only_final</think>
```

という形でした。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_training_data.csv` 実データ確認)

#### 5.3 生成ロジック

レポートと manifest を合わせると、binary verified rows は

- `dsl_exact_formula = 133`
- `dsl_byte_transform = 14`
- `generic_solver_family = 13`

に分かれます。  
つまり大半は **構文解析できる exact formula** から step 展開され、一部は byte transform、残りは generic な solver-family trace です。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_manifest.json:58-74`)

また設計上、

- answer-only binary rows は boxed-only のまま
- `<think>` 内で最終 8-bit 答えを再掲しない
- `constraints=exact_8bit,leading_zeros,box_only_final`

が入っています。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_manifest.json:58-74`)

### 観測された結果

`result/2` では official-like binary は `13/60` まで上がりましたが、

- exact 8-bit は `9/60`
- tolerance-only 正解が `4/60`
- `bit_structured_byte_formula` は **`0/14` のまま**

でした。  
つまり DSL は metric 上の見かけを少し押し上げた一方で、**hard structured byte の本丸は動かせていません**。(`baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md:135-182`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:108-149`)

---

## 6. `phase2_binary_hybrid_training_data.csv`

### 何を狙ったデータか

DSL が「堅すぎてモデルに乗らない」可能性を見て、同じ 160 binary verified rows を **自然言語 hybrid narrative** に言い換えた実験です。(`baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:1-29`)

### 生成方法

#### 6.1 変えたのは 160 行だけ

`result/2-1` レポートがはっきり書いている通り、

- 900 行の ID 集合は DSL 版と完全一致
- 変わったのは **160 行の `binary + trace_boxed` の `generated_cot` だけ**
- non-binary row と binary boxed-only row は同一

です。(`baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:12-29`)

#### 6.2 hybrid trace の作り方

現行スクリプトの `build_phase2_binary_dsl_dataset.py` は hybrid 版の生成ロジックを持っており、

- まず `resolve_binary_rule(...)` で rule を解決
- exact formula が構文解析できれば `build_binary_hybrid_trace(...)`
- 失敗すれば `build_binary_generic_trace(...)`

という流れです。(`baseline/cot/phase2_binary_dsl/build_phase2_binary_dsl_dataset.py:482-685`)

実際の hybrid trace は例えば

```text
<think>The examples support the verified binary rule xor(shl1,shr4).
I apply the same byte transformation to the query 10011111.
Useful intermediate byte operations are shl1(query)=00111110; shr4(query)=00001001.
I then ...
```

のような形で、DSL の各 step を自然言語へ展開しています。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_training_data.csv:1-12` と実データ確認)

manifest でも

- `binary_trace_style = hybrid_narrative`
- `hybrid_exact_formula = 133`
- `hybrid_byte_transform = 14`
- `generic_solver_family = 13`

となっています。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_manifest.json:58-75`)

#### 6.3 長さの変化

binary trace 160 行の平均 `generated_cot` 長は

- DSL: `180.6 chars`
- Hybrid: `363.8 chars`

で、ほぼ倍増しています。つまり hybrid は「少し自然化」ではなく、**teacher をかなり長文化する介入**でした。(`baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:22-29` と実測)

### 観測された結果

これは明確に失敗でした。

- overall `0.7094 -> 0.6750`
- binary `13/60 -> 8/60`
- verified binary `7/20 -> 7/20` で据え置き
- `manual_audit_priority 4/20 -> 0/20`
- `bit_structured_byte_formula` は **`0/14` のまま**

でした。さらに text も `43/50 -> 36/50` に落ちています。(`baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:31-52,95-149,181-208`)

要するに、DSL を自然言語化しても binary の intended slice は強くならず、むしろ **長い reasoning を誘発して final boxed answer discipline を壊した** と読むのが自然です。

---

## 7. ここまでで「何を変えたか」を軸に見る

binary 向けに、これまで実際に動かしたデータ介入を変数別に並べるとこうです。

### 7.1 量を増やす

- `100 binary` → `300 binary` まで増やした旧 800 行版
- `100 binary` → `200 binary` に増やした guarded 800
- `200 binary` → `280 binary` に増やした Phase 1/2

**結論:** 単純増量だけでは structured binary は改善しませんでした。

### 7.2 trace の文体を変える

- short rule-based trace
- long natural-language binary CoT
- contract-focused short trace
- DSL scratchpad
- hybrid narrative

**結論:** 文体はかなり試したが、`bit_structured_byte_formula` の本丸は最後まで改善しませんでした。

### 7.3 boxed-only supervision を混ぜる

- Phase 1 で初導入
- binary `120` 行を boxed-only にした
- Phase 2 DSL / Hybrid でもそのまま維持

**結論:** overall の emission 安定化には効いたが、binary exact reasoning を大きく押し上げるほどではありませんでした。

### 7.4 `<think>` に答えを書くか書かないか

- 600 版は `<think>` に答えを直接書く設計
- guarded 800 以降は binary trace で final answer 再掲を避ける設計

**結論:** README の boxed-first metric を意識した設計改善としては筋が良いが、これ単独で binary hard を解くには不足でした。

---

## 8. この履歴から分かること

### 8.1 すでに試したもの

すでに試した binary synthetic-data 介入は、かなり広いです。

- verified-only short trace
- binary-heavy natural-language CoT
- exact 8-bit contract を強調した guarded trace
- trace / boxed-only 分離
- DSL scratchpad
- DSL の自然言語化

なので、**「まだ binary teacher を少し工夫すれば一気に解けるはず」**とは言いにくい段階です。

### 8.2 逆に、まだ本質的に解けていないこと

ずっと解けていないのは、

- `bit_structured_byte_formula`
- verified binary の hard slice
- 最後に 8-bit exact byte を固定するところまで含めた policy

です。とくに Phase 2 では special な binary teacher を持つのが **900 行中 160 行だけ**で、mixed SFT の中で binary signal が埋もれやすい設計でした。(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_manifest.json:20-68`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md:12-29`)

### 8.3 一番重要な整理

ここまでの履歴を一言でまとめると、

> binary 問題に対して「どんな teacher を見せるか」はかなり試した。  
> しかし mixed SFT のままでは、teacher の文体変更や行数増量だけで hard binary の rule induction / exact 8-bit closure を安定獲得するところまでは届いていない。

ということです。

---

## 9. 参考にした主なファイル

- `README.md`
- `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md`
- `baseline/cot/phase0_offline_eval/result/0/reports/train_rule_based_cot_baseline_result0_deep_analysis.md`
- `baseline/cot/phase0_offline_eval/result/1/reports/phase1_result1_deep_analysis.md`
- `baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md`
- `baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md`
- `baseline/cot/build_rule_based_training_dataset.py`
- `baseline/cot/build_rule_based_training_dataset_binary_guarded.py`
- `baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.py`
- `baseline/cot/phase2_binary_dsl/build_phase2_binary_dsl_dataset.py`
- `baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv`
- `baseline/cot/output-csv/rule_based_binary_guarded_800_training_data.csv`
- `baseline/cot/phase1_assistant_only/artifacts/phase1_assistant_only_training_data.csv`
- `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_training_data.csv`
- `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_training_data.csv`
