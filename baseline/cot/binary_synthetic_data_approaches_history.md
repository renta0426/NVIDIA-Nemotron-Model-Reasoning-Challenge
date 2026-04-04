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

---

## 11. bit_synth_exact_trace_cot_v1 学習後の binary 生成傾向補遺（2026-04-05）

依頼により、`cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/result/v1` の binary 60 問を、README.md の Evaluation 節にある boxed-first 抽出前提で再点検した。今回の v1 は `cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/BIT_SYNTH_EXACT_TRACE_COT_V1_REPORT.md` にある通り、10,000 行の bit manipulation 専用 exact-trace teacher で学習しており、teacher 文面自体が `Check examples:`、`So the rule is ...`、`Constraints: exact_8bit, leading_zeros, box_only_final.` を持つ。生成文はこの teacher をほぼそのまま模倣する方向へ一気に寄った。

### 11.1 まず結論

- binary の artifact 上スコアは `27/60` で、これまでの best だった result/2 の `13/60` から大きく伸びた。
- ただし improvement の中身は「gold に到達する回数が激増した」ではなく、「短い exact-trace 文の末尾に 8-bit 値を置くので README の fallback で拾われやすくなった」が主因である。
- 実際、binary の `gold_anywhere` は result/2 が `28/60`、v1 も `28/60` で同数だった。内部で gold 文字列に触れている総数はほぼ増えていない。
- 一方で raw length は result/2 の平均 `15,893.5` 文字から v1 の `518.5` 文字へ激減し、1 出力あたりの 8-bit 断片数も `128.9` から `12.17` へ落ちた。長文迷走が消え、最後の 8-bit が際立つようになった。
- ただし boxed formatting 自体は直っていない。v1 binary 60 問は `format_bucket=numeric_fallback` が全件で、末尾は `\boxed{...}` ではなく backspace を含む `oxed{...}` になっており、README の boxed-first ではなく last-number fallback に依存している。

### 11.2 result/2 系との比較表

`phase0_eval_row_level.csv` と raw text を基に、binary のみを比較すると以下になる。

| run | artifact correct | prediction==gold | gold_anywhere | mean raw chars | mean 8-bit fragments | 先頭パターン |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `0` | 11/60 | 11/60 | 23/60 | 15,783.8 | 87.50 | `We need to infer ...` |
| `2` | 13/60 | 9/60 | 28/60 | 15,893.5 | 128.90 | `We need to infer ...` |
| `2_1_2` | 8/60 | 7/60 | 30/60 | 16,330.4 | 172.35 | `We need to infer ...` |
| `2_2_1` | 8/60 | 8/60 | 25/60 | 16,046.2 | 164.03 | `We need to infer ...` |
| `v1` | 27/60 | 13/60 | 28/60 | 518.5 | 12.17 | `Check examples: ...` |

ここで重要なのは、v1 だけが `gold_anywhere` を増やさずに artifact score を伸ばしている点である。つまり、長い chain-of-thought のどこかで正解に触れる確率は旧 run と大差ないが、生成終端が短く整理されたことで最終抽出が有利になった。

### 11.3 v1 の文体変化

v1 binary 60/60 は全件で次の特徴を共有していた。

- `Check examples:` で始まる
- `So the rule is ...` を明示する
- query に対して `shl`, `shr`, `ror`, `rol`, `nibble_swap`, `choose`, `majority`, `xor`, `or`, `and` などの中間値を 8-bit のまま列挙する
- 末尾に `Constraints: exact_8bit, leading_zeros, box_only_final.` を付ける
- 最後は `</think> oxed{10100001}` のような短い終端になる

旧 run では binary 60/60 が `We need to infer the transformation rule from examples.` で始まり、その後に 1.5 万文字級の探索が続いて 8-bit 断片を大量散布していた。v1 は training report で設計した exact-trace teacher をほぼ忠実に再生しており、ここが最大の変化である。

### 11.4 改善が出た slice

artifact 基準では、binary 改善は以下に集中した。

| slice | result/2 | v1 |
| --- | ---: | ---: |
| `bit_other` | 13/46 | 21/46 |
| `bit_structured_byte_formula` | 0/14 | 6/14 |
| `verified_trace_ready` | 7/20 | 12/20 |
| `answer_only_keep` | 2/20 | 9/20 |
| `manual_audit_priority` | 4/20 | 6/20 |
| `binary_affine_xor` | 7/20 | 12/20 |

特に大きいのは、過去 run でほぼ崩れていた `bit_structured_byte_formula` が `0/14 -> 6/14` に跳ねたことと、`answer_only_keep` が `2/20 -> 9/20` に伸びたことである。v1 だけが初めて取れた binary 問題は 20 件あり、そのうち 6 件は `bit_structured_byte_formula`、5 件は `manual_audit_priority` だった。つまり exact-trace teacher は、最も不安定だった structured-byte と hard manual 群に対して新しい当たり方を作っている。

### 11.5 ただし「最終 8-bit が合う」件数はそこまで多くない

raw text の最終 8-bit だけを厳しく見ると、v1 binary 60 問は次の 3 群に分かれた。

| slice | last 8-bit exact | gold は本文中にあるが最終誤り | gold に未到達 |
| --- | ---: | ---: | ---: |
| `bit_other` | 11/46 | 9/46 | 26/46 |
| `bit_structured_byte_formula` | 2/14 | 6/14 | 6/14 |
| `verified_trace_ready` | 7/20 | 5/20 | 8/20 |
| `answer_only_keep` | 4/20 | 7/20 | 9/20 |
| `manual_audit_priority` | 2/20 | 3/20 | 15/20 |

ここから分かるのは、v1 の本質が「全文迷走から short program trace への置換」であり、正しい最終 8-bit を安定に出し切るところまではまだ半分しか届いていないということだ。特に `bit_structured_byte_formula` は 14 問中 6 問で本文中に gold があるのに、最後の 8-bit は別値になっている。

### 11.6 representative cases

#### 11.6.1 新しく取れた verified_trace_ready: `069dbaab`

- gold: `00010000`
- result/2 は `We need to infer ...` から長く探索し、最後は `0` に落ちた。
- v1 は `Check examples: - 10000101 -> 00000000 because rol2=00010110, shl4=01010000; and(rol2,shl4) matches ... So the rule is and(rol2,shl4).` と rule 名を固定し、query に対して各中間値を 8-bit で計算したうえで末尾を `oxed{00010000}` で閉じている。
- この型は v1 で最も多い改善で、「自然言語で可能性を列挙する」旧 run から、「既知 operator を 1 本に決めて適用する」短手順へ切り替わった。

#### 11.6.2 新しく取れた structured formula: `3376d8b7`

- gold: `00100010`
- result/2 は長文列挙ののち `00000100` で終了。
- v1 は `choose(shl1,shr5,ror1)` を明示し、`Query x = 01000100` に対して `shl1(x) = 10001000`, `shr5(x) = 00000010`, `ror1(x) = 00100010` と並べ、その最後の候補を終端に置いた。
- structured-byte が伸びた理由はここにあり、teacher が `operator 名 -> query 実行 -> exact_8bit 制約` を一筆書きで教えたことで、rule search が「曖昧な説明」から「候補演算子の固定」へ変わった。

#### 11.6.3 gold には触れるが最後を外す: `0528d502`

- gold: `00011111`
- v1 の本文中には `01110100 -> 00011111 is consistent with the same GF(2) equations.` と gold 文字列そのものが出てくる。
- それでも最終 prediction は `10010101` で、query に対する最後の書き戻しを誤っている。
- これは v1 に多い失敗で、teacher 的な文体は獲得したが、「例示行で出てきた正しい 8-bit」と「query に対する最終 8-bit」の混線が残る。

#### 11.6.4 旧 run で安定していた問題を落とす: `bcdf9198`

- gold: `11111111`
- result/2 は `All given inputs map to 11111111` と実質的に定数関数として捉え、そのまま `\boxed{11111111}` に着地した。
- v1 は `or(rol3,shl4)` という具体 rule を当てに行き、examples もそれに整合しているように書くが、最後は `oxed{00110011}` を出して外した。
- v1 は rule を必ず名指ししようとするため、実際には「定数に近い簡単な見抜き」で十分な問題まで operator fitting に寄り、そこで外すケースがある。

#### 11.6.5 artifact 上の正誤フラグがそのままは信用できない: `12e947ca`

- `phase0_eval_row_level.csv` では `gold=00111110`, `prediction=00111111` なのに `is_correct=True` になっている。
- raw_output 末尾も `oxed{00111111}` で、本文中に `00111110` は出ていない。
- 同種の `prediction != gold` かつ `is_correct=True` は v1 binary に 14 件あり、result/2 にも 4 件ある。
- したがって、この補遺では artifact score 自体は記録しつつ、生成文の解釈では `raw_output` と `extracted_answer` を優先した。

### 11.7 何が改善し、何が未解決か

- 改善したのは、binary を「長文で迷走する問題」から「短い rule execution を書いて最後の 8-bit を置く問題」へ変えた点である。
- 特に training report が狙った `Check examples -> So the rule is -> exact_8bit constraint` は、そのまま生成に転写された。
- 一方で README が本来最優先する `\boxed{}` 形式はまだ壊れており、v1 では boxed-first improvement ではなく fallback optimization になっている。
- また gold 到達数自体は旧 best とほぼ同じなので、「新しく解けるようになった」というより「答えを extraction-friendly な位置へ置けるようになった」寄りの改善である。
- 次に詰めるべきは、`gold_inside_but_final_wrong` の 15 件をどう last 8-bit exact へ寄せるか、および `\boxed` の backspace 崩れを止めて README の primary path に乗せることだと判断する。

### 11.8 10000件 teacher との一致度と「正しく学習できたか」

この v1 について、「10000件 synthetic teacher の傾向を学べたか」と「提出要件まで含めて正しく学習できたか」は分けて見る必要がある。

まず、teacher 文体そのものはかなり強く学習できている。`BIT_SYNTH_EXACT_TRACE_COT_V1_REPORT.md` で設計した teacher は、

- `Check examples:` で例を確認する
- `So the rule is ...` で規則名を固定する
- query に対する中間値を 8-bit のまま列挙する
- `Constraints: exact_8bit, leading_zeros, box_only_final.` を付ける

という短い exact-trace だったが、v1 の binary 出力はこの骨格にほぼ全面的に寄っている。以前の run 群が `We need to infer ...` から始まる長文探索だったのに対し、v1 は平均出力長が大きく縮み、teacher の表層スタイルと局所手順をそのまま転写したような挙動になっている。したがって、**文体と手順テンプレートの学習という意味では yes** である。

一方で、README が本当に欲しているのは boxed-first で安定に extract できる最終回答である。ここではまだ未完成で、v1 binary は全件が実質 `numeric_fallback` 依存、しかも末尾の `\boxed{}` は backspace 崩れを含む `oxed{...}` になっている。さらに `gold_anywhere` は result/2 と同じ `28/60` で、内部で gold 文字列に触れる総量自体はほとんど増えていない。つまり、**答えへ到達する推論能力が劇的に増えたというより、短い trace を書いて最後の 8-bit を拾われやすい位置に置くことを学んだ** と見る方が正確である。

したがって、「正しく学習できてるか」への結論は次の通りになる。

- teacher の文体、規則固定、8-bit 中間計算の並べ方は正しく学習できている
- binary 専門データの効果で `bit_structured_byte_formula` と `answer_only_keep` は実際に改善している
- ただし boxed 終端、最終 8-bit の確定、gold を本文中で作れても最後を外さないこと、の 3 点は未完成
- 提出仕様まで含めた意味では「半分は yes、半分は no」で、まだ fully correct learning とは言えない

要するに v1 は、binary teacher を学習していない run ではなく、**teacher をかなり忠実に模倣できているが、README の primary extraction path まで仕上がっていない run** である。この解釈が、27/60 まで伸びたのに `gold_anywhere` が増えていないことと最も整合する。

---

## 10. Phase 2 specialist merge 系 result の再点検（2026-04-04）

README.md の boxed-first 抽出を前提に、binary watch 60 問について result/0, 1, 2, 2-1, 2_1_merge_lora, 2_1_2, 2_2_merge_lora, 2_2_1 を横断比較した。今回の重点は、phase2_1_2_merge_lora の評価結果である result/2_1_2 と、phase2_2_1_merge_lora の評価結果である result/2_2_1 を、既存の 0 系列全体の流れに置き直すことにある。

### 10.1 スコアの位置づけ

| result | correct | rows | accuracy |
| --- | ---: | ---: | ---: |
| 0 | 11 | 60 | 0.1833 |
| 1 | 12 | 60 | 0.2000 |
| 2 | 13 | 60 | 0.2167 |
| 2-1 | 8 | 60 | 0.1333 |
| 2_1_merge_lora | 10 | 60 | 0.1667 |
| 2_1_2 | 8 | 60 | 0.1333 |
| 2_2_merge_lora | 10 | 60 | 0.1667 |
| 2_2_1 | 8 | 60 | 0.1333 |

- result/2 が binary の局所ピークで 13/60。
- result/2_1_2 は 8/60 で、result/2_1_merge_lora の 10/60 からさらに後退した。
- result/2_2_1 も 8/60 で、result/2_2_merge_lora の 10/60 から後退した。
- verified_trace_ready は 7/20 で固定されたままなのに対し、answer_only_keep と manual_audit_priority が specialist 系で落ちている。

### 10.2 target result ごとの確認

#### result/2_1_2

- overall は 0.6500、binary は 8/60、symbol は 26/60。binary を専門化した割に binary 自体が 2_1_merge_lora 比で 3 改善 5 退行だった。
- binary の boxed 成功は 8 件しかなく、52 件が numeric_fallback のまま終わる。つまり 8-bit を出せないのではなく、最後を boxed で閉じる policy が弱い。
- bit_structured_byte_formula は 0/14 まで悪化し、2_1_merge_lora の 2/14 を失った。specialist 化で hardest slice を守れなかった。
- 一方で symbol は 21/60 から 26/60 へ大きく戻しており、binary specialist merge は binary 改善ではなく numeric_2x2 の副次回復として現れている。

#### result/2_2_1

- overall は 0.6531、binary は 8/60、symbol は 25/60。symbol specialist 系としては symbol 全体を維持しつつ binary を 2 点失った。
- binary の boxed 成功は 10 件に留まり、50 件が numeric_fallback。result/2_2_merge_lora の 11 boxed / 49 fallback より悪い。
- symbol は 25/60 を維持したが、中身は numeric_2x2 が 25/40 から 24/40 へ微減し、glyph_len5 が 0/20 から 1/20 へ初めて 1 件だけ取れた構図である。
- symbolic answer type は 2/24 に伸びたが、empty box が 8 件まで増えており、glyph 出力の安定化ではなく部分的な当たりに留まる。

### 10.3 binary failure mode の横断所見

- result/0 から result/2_2_1 まで、binary は常に長文 reasoning と last_number fallback が支配的である。
- specialist 系の 2_1_2 / 2_2_1 は特に boxed 件数が少なく、README 想定の extraction 契約からさらに離れた。
- bit_structured_byte_formula は result/1 と result/2_1_merge_lora で一瞬 2/14 まで届いたが、2_1_2 と 2_2_1 では再び 0/14。抽象規則の再現より先に終端フォーマットが壊れている。
- 60 問中 37 問は全 result で常敗、全 result 通算で常勝は 2 問しかない。binary は 1 問単位で見ても安定な policy がほぼ形成されていない。

### 10.4 1問ずつ見た生成の変化

以下は watch 60 問それぞれについて、正誤の遷移、予測値の推移、実際の生成文の冒頭、そして所見を圧縮して残したメモである。snip は raw_output の冒頭要約。

#### 00066667
- gold: 10010111 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:○ 2_2_1:×
- prediction path: 0=179 / 1=1 / 2=1 / 2-1=7 / 2_1_merge_lora=0 / 2_1_2=7 / 2_2_merge_lora=10101000 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs (8-bit) and outputs. 1) 01010001 -> 11011...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 01010001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01010001 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01010001 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 004ef7c7
- gold: 11111111 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:○ 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=5 / 1=01 / 2=11100100 / 2-1=22 / 2_1_merge_lora=8 / 2_1_2=10010000 / 2_2_merge_lora=1 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 11101001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11101001 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11101001 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。

#### 008b52fd
- gold: 01100101 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=010 / 1=3 / 2=1 / 2-1=28 / 2_1_merge_lora=1 / 2_1_2=10 / 2_2_merge_lora=11001011 / 2_2_1=4
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary inputs to outputs. Let's list examples wit...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10011001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10011001 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10011001 -...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 009a74b6
- gold: 11111011 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:○ 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=000 / 2=8 / 2-1=110 / 2_1_merge_lora=11101010 / 2_1_2=3 / 2_2_merge_lora=2 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary, output also 8-bit. Let's list examples ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 01110101 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 01110101 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。

#### 021ed764
- gold: 11111101 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=4 / 2=00 / 2-1=1 / 2_1_merge_lora=4 / 2_1_2=0 / 2_2_merge_lora=1000 / 2_2_1=8
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit. Let...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs also 8-bit. Le...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 02324ba1
- gold: 11101011 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=9 / 2=0 / 2-1=1 / 2_1_merge_lora=3 / 2_1_2=3 / 2_2_merge_lora=5 / 2_2_1=3
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary numbers. Output also 8-bit bina...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs also 8-bit. Le...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10000010 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10000010 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 予測が 1 桁または 2 桁断片に崩れやすく、実質的に reasoning の末尾数字を拾っている。

#### 0290f51a
- gold: 10101111 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:○ 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=3 / 1=100 / 2=10010010 / 2-1=3 / 2_1_merge_lora=1011010 / 2_1_2=1 / 2_2_merge_lora=3 / 2_2_1=6
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to ded...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to ded...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 02a5a1ca
- gold: 01101101 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=00000011 / 1=1 / 2=00001011 / 2-1=11111110 / 2_1_merge_lora=5 / 2_1_2=00101100 / 2_2_merge_lora=001011 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10111001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10111001 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10111001 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 0528d502
- gold: 00011111 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=4 / 1=03 / 2=72 / 2-1=01 / 2_1_merge_lora=2 / 2_1_2=10 / 2_2_merge_lora=2 / 2_2_1=01011011
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs (8-bit) and outputs. I'll write them as b...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. I'll parse ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 01110100 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 01110100 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。

#### 06881e47
- gold: 11111100 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=5 / 2=01100000 / 2-1=7 / 2_1_merge_lora=1 / 2_1_2=0 / 2_2_merge_lora=2 / 2_2_1=3
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. Let's list examples with 8-bit binary strings. I'll den...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10000001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10000001 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10000001 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 069dbaab
- gold: 00010000 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=11001100 / 2=0 / 2-1=2 / 2_1_merge_lora=5 / 2_1_2=-5 / 2_2_merge_lora=4 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs (8-bit) and outputs. I'll write them as b...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with input and output (8-bit strings). ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 01110111 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 01110111 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 08b2b48d
- gold: 10101011 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=3 / 1=5 / 2=0 / 2-1=5 / 2_1_merge_lora=1 / 2_1_2=1 / 2_2_merge_lora=3 / 2_2_1=11100101
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary inputs and outputs. Let's list examples: 1...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs (8-bit) and outputs. 1) 01100001 -> 00101...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01100001 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 01100001 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 08df5363
- gold: 01011100 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=0 / 2=1 / 2-1=0010 / 2_1_merge_lora=1 / 2_1_2=1 / 2_2_merge_lora=2 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 01001101...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01001101 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01001101 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 094de91f
- gold: 10011001 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=8 / 2=0 / 2-1=1 / 2_1_merge_lora=00011 / 2_1_2=2 / 2_2_merge_lora=3 / 2_2_1=3
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with 8-bit binary strings. I'll denote ...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list them: 1) 11100111 -> 01000001 2) 11001011 -> 110...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to ded...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11100111 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 0a6d48aa
- gold: 11100011 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=3 / 1=2 / 2=0 / 2-1=3 / 2_1_merge_lora=0 / 2_1_2=1 / 2_2_merge_lora=00001 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary numbers. Let's list examples with input an...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 11011100...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11011100 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11011100 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 0df8306a
- gold: 10000000 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:○ 1:○ 2:○ 2-1:× 2_1_merge_lora:○ 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=10000000 / 1=10000000 / 2=10000000 / 2-1=-6 / 2_1_merge_lora=10000000 / 2_1_2=3 / 2_2_merge_lora=7 / 2_2_1=1
- 0: fmt=boxed, fb=boxed_non_empty, box=10000000, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=boxed, fb=boxed_non_empty, box=10000000, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs seem to be 8-b...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。

#### 0ec17d2e
- gold: 00111111 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=0 / 2=1 / 2-1=0100 / 2_1_merge_lora=0 / 2_1_2=10 / 2_2_merge_lora=0 / 2_2_1=7
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. Let's list inputs (8 bits) to outputs (8 bits). Write t...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11001101 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11001101 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 0f7be6a8
- gold: 01000000 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:○ 1:○ 2:○ 2-1:○ 2_1_merge_lora:○ 2_1_2:○ 2_2_merge_lora:○ 2_2_1:○
- prediction path: 0=01000000 / 1=01000000 / 2=01000000 / 2-1=01000000 / 2_1_merge_lora=01000000 / 2_1_2=01000000 / 2_2_merge_lora=01000000 / 2_2_1=01000000
- 0: fmt=boxed, fb=boxed_non_empty, box=01000000, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output appears to be i...
- 2: fmt=boxed, fb=boxed_non_empty, box=01000000, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output appears to be i...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=EMPTY, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=01000000, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: 全 result で安定正答。binary watch 全体ではごく少ない、8-bit exact closure まで一貫して守れたケース。

#### 101410e4
- gold: 10001101 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:○ 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:○ 2_2_1:×
- prediction path: 0=6 / 1=0 / 2=10100011 / 2-1=0010 / 2_1_merge_lora=1 / 2_1_2=3 / 2_2_merge_lora=10000011 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with 8-bit binary strings. I'll denote ...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. I'll parse ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 00010101 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 00010101 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 12154247
- gold: 10111101 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=64 / 2=0 / 2-1=2 / 2_1_merge_lora=1 / 2_1_2=1 / 2_2_merge_lora=7 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary numbers. Let's list examples with input an...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 11101101...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11101101 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11101101 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 予測が 1 桁または 2 桁断片に崩れやすく、実質的に reasoning の末尾数字を拾っている。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 12e947ca
- gold: 00111110 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=1 / 2=1 / 2-1=0 / 2_1_merge_lora=4 / 2_1_2=100 / 2_2_merge_lora=0 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit. Let...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with input (8-bit) and output (8-bit). ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10010001 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10010001 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 12fd5b6c
- gold: 11001111 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0111 / 1=2 / 2=1 / 2-1=2 / 2_1_merge_lora=0 / 2_1_2=0 / 2_2_merge_lora=1 / 2_2_1=8
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with 8-bit binary strings. I'll denote ...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 11011011...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11011011 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11011011 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 143627c4
- gold: 11001001 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=000 / 2=0 / 2-1=011100 / 2_1_merge_lora=1 / 2_1_2=1 / 2_2_merge_lora=1010 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary numbers. Let's list examples with input an...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 11000001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11000001 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11000001 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 18564041
- gold: 00000000 / subtype: bit_other / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=20 / 2=1 / 2-1=2 / 2_1_merge_lora=1 / 2_1_2=2 / 2_2_merge_lora=10111100 / 2_2_1=6
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit bina...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs are also 8-bit...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 1bf84ce3
- gold: 00000000 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=4 / 2=1110 / 2-1=0001 / 2_1_merge_lora=5 / 2_1_2=01001001 / 2_2_merge_lora=01100011 / 2_2_1=0100
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with 8-bit binary strings. I'll denote ...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list them: 1) 01001001 -> 00010000 2) 00011110 -> 100...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list examples: 1) 0100100...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list examples: 1) 0100100...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。

#### 20abedb7
- gold: 00010000 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=4 / 1=1 / 2=3 / 2-1=11 / 2_1_merge_lora=1 / 2_1_2=10000100 / 2_2_merge_lora=00011000 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary numbers. Let's list examples with input an...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 11110110...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11110110 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 11110110 -...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 2230fad0
- gold: 01001010 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=0 / 2=1 / 2-1=1100 / 2_1_merge_lora=0 / 2_1_2=100 / 2_2_merge_lora=1 / 2_2_1=7
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary inputs and outputs. Let's list examples wi...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. I'll parse ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00011001 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 00011001 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 24ef5b88
- gold: 00100111 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:○ 1:○ 2:○ 2-1:○ 2_1_merge_lora:× 2_1_2:○ 2_2_merge_lora:× 2_2_1:○
- prediction path: 0=00100111 / 1=00100110 / 2=00100111 / 2-1=00100111 / 2_1_merge_lora=1 / 2_1_2=00100111 / 2_2_merge_lora=0 / 2_2_1=00100111
- 0: fmt=boxed, fb=boxed_non_empty, box=00100111, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit. Let...
- 2: fmt=boxed, fb=boxed_non_empty, box=00100111, snip=We need to infer the transformation rule from examples. Let's list examples with input and output. I'll parse each:...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=00100111, snip=We need to infer transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to ded...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=00100111, snip=We need to infer transformation rule from examples. Let's list inputs and outputs: 1) 01111011 -> 10111101 2) 00001...
- assessment: 大半の result で正答しており、policy 崩壊は限定的。merge 系で一時退行しても 8-bit exact answer 自体は保持できている。

#### 2630aaf8
- gold: 10111110 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0000 / 1=3 / 2=1110011 / 2-1=0110 / 2_1_merge_lora=0 / 2_1_2=0 / 2_2_merge_lora=0 / 2_2_1=111000
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs (8-bit) and outputs. I'll write them as b...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10111000...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10111000 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10111000 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 2841d283
- gold: 10010111 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=00110000 / 1=2 / 2=0 / 2-1=6 / 2_1_merge_lora=6 / 2_1_2=5 / 2_2_merge_lora=6 / 2_2_1=6
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit. Let...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs also 8-bit. Le...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 2d790c98
- gold: 01111011 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=0011 / 2=1 / 2-1=00001110 / 2_1_merge_lora=1 / 2_1_2=01000001 / 2_2_merge_lora=7 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary numbers. Let's list examples with input an...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. I'll parse ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10000010 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10000010 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 2ead53dc
- gold: 00000101 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:○ 1:○ 2:○ 2-1:○ 2_1_merge_lora:○ 2_1_2:○ 2_2_merge_lora:× 2_2_1:○
- prediction path: 0=00000101 / 1=00000101 / 2=00000101 / 2-1=00000101 / 2_1_merge_lora=00000101 / 2_1_2=00000101 / 2_2_merge_lora=2 / 2_2_1=00000101
- 0: fmt=boxed, fb=boxed_non_empty, box=EMPTY, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary numbers. Output also 8-bit bina...
- 2: fmt=boxed, fb=boxed_non_empty, box=00000101, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs are also 8-bit...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=00000101, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit? All outputs show...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=00000101, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Observations: ou...
- assessment: 大半の result で正答しており、policy 崩壊は限定的。merge 系で一時退行しても 8-bit exact answer 自体は保持できている。

#### 32e5fe87
- gold: 00000000 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:○ 1:○ 2:○ 2-1:○ 2_1_merge_lora:× 2_1_2:○ 2_2_merge_lora:○ 2_2_1:○
- prediction path: 0=00000000 / 1=00000000 / 2=00000000 / 2-1=00000000 / 2_1_merge_lora=1 / 2_1_2=00000000 / 2_2_merge_lora=00000000 / 2_2_1=00000000
- 0: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output appears to be 8...
- 2: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer the rule from examples. All outputs are 8-bit binary with leading zeros, only last few bits maybe ...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer transformation rule from examples. All outputs are 8-bit binary ending with many zeros, only last ...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=EMPTY, snip=We need to infer transformation rule from examples. All outputs are 8-bit binary ending with many zeros, only last ...
- assessment: 大半の result で正答しており、policy 崩壊は限定的。merge 系で一時退行しても 8-bit exact answer 自体は保持できている。

#### 3376d8b7
- gold: 00100010 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=4 / 1=10010000 / 2=00000100 / 2-1=1 / 2_1_merge_lora=1 / 2_1_2=0000010 / 2_2_merge_lora=01010000 / 2_2_1=04
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary strings. Output also 8-bit. Let's list e...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 00110001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00110001 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00110001 -...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。

#### 3564baf1
- gold: 10101101 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=001 / 1=1 / 2=11 / 2-1=1 / 2_1_merge_lora=-7 / 2_1_2=1 / 2_2_merge_lora=01101111 / 2_2_1=1101
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs (8-bit) and outputs. I'll write them as b...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10011111...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10011111 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10011111 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 3a90fdf6
- gold: 10100000 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=00000000 / 2=00000000 / 2-1=1 / 2_1_merge_lora=010000 / 2_1_2=0100 / 2_2_merge_lora=1 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit bina...
- 2: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary. Outputs are also 8-bit binary....
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Many map to 0000...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Many map to 0000...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。

#### 4195699e
- gold: 01100000 / subtype: bit_other / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:○ 2_2_1:×
- prediction path: 0=001 / 1=1 / 2=00010000 / 2-1=00011111 / 2_1_merge_lora=00010000 / 2_1_2=5 / 2_2_merge_lora=01100000 / 2_2_1=5
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. 8-bit binary numbers. Let's list examples with input and ou...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. I'll parse ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10000001 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10000001 -...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 52a9d5e4
- gold: 11011111 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:○ 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=11011111 / 2=010 / 2-1=000010 / 2_1_merge_lora=1 / 2_1_2=4 / 2_2_merge_lora=1 / 2_2_1=11
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation from examples. Let's list examples with input and output. 1) 00010111 -> 110010...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 00010111 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 00010111 ->...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。

#### 5356c59d
- gold: 01111111 / subtype: bit_other / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:○ 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=7 / 2=01101000 / 2-1=3 / 2_1_merge_lora=0 / 2_1_2=2 / 2_2_merge_lora=110110 / 2_2_1=00
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit. Let...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary, output also 8-bit. Let's list examples ...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。

#### 55f5e590
- gold: 10001111 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:○ 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=10001111 / 1=2 / 2=0 / 2-1=0 / 2_1_merge_lora=0 / 2_1_2=11001111 / 2_2_merge_lora=7 / 2_2_1=1
- 0: fmt=boxed, fb=boxed_non_empty, box=10001111, snip=We need to infer the bit transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit....
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs also 8-bit. Le...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 567e3da4
- gold: 10000100 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:○ 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=00000100 / 1=10000100 / 2=3 / 2-1=0 / 2_1_merge_lora=1000 / 2_1_2=0 / 2_2_merge_lora=1 / 2_2_1=1
- 0: fmt=boxed, fb=boxed_non_empty, box=00000100, snip=We need to infer the transformation rule from examples. Input 8-bit binary to output 8-bit binary. Let's list examp...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 00110001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00110001 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00110001 -...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。

#### 5f29ae58
- gold: 00000000 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:○ 2:× 2-1:× 2_1_merge_lora:○ 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=0 / 2=00101000 / 2-1=2 / 2_1_merge_lora=0 / 2_1_2=1 / 2_2_merge_lora=1 / 2_2_1=6
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. Let's list examples with 8-bit binary strings. I'll den...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10011010...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10011010 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list examples: 1) 1001101...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 6818b555
- gold: 10000000 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=3 / 2=7 / 2-1=0 / 2_1_merge_lora=0 / 2_1_2=0 / 2_2_merge_lora=0 / 2_2_1=101101
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. 8-bit binary inputs to outputs also 8-bit? The examples out...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs are also 8-bit...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs also 8-bit. Many outputs are 000...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs also 8-bit. Many outputs are 000...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### 71e6cae8
- gold: 00000000 / subtype: bit_other / tier: answer_only_keep / solver: none
- correct path: 0:○ 1:○ 2:○ 2-1:○ 2_1_merge_lora:× 2_1_2:○ 2_2_merge_lora:○ 2_2_1:○
- prediction path: 0=00000000 / 1=00000000 / 2=00000000 / 2-1=00000000 / 2_1_merge_lora=1 / 2_1_2=00000000 / 2_2_merge_lora=00000000 / 2_2_1=00000000
- 0: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary numbers. Output appears to be 8...
- 2: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer the rule from examples. All outputs are 8-bit with leading zeros. The outputs are either 00000001 ...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output always 8-bit, often 00000000...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output always 8-bit, often 00000000...
- assessment: 大半の result で正答しており、policy 崩壊は限定的。merge 系で一時退行しても 8-bit exact answer 自体は保持できている。

#### 783a1317
- gold: 00111110 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=0 / 2=0 / 2-1=1 / 2_1_merge_lora=3 / 2_1_2=01001010 / 2_2_merge_lora=00100101 / 2_2_1=1
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with input (8 bits) -> output (8 bits)....
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs also 8-bit. Le...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to fin...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to fin...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 7e527a97
- gold: 00000110 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=3 / 2=6 / 2-1=0 / 2_1_merge_lora=0 / 2_1_2=0 / 2_2_merge_lora=0 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit bina...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs are also 8-bit...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01011000 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01011000 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 予測が 1 桁または 2 桁断片に崩れやすく、実質的に reasoning の末尾数字を拾っている。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### 846176af
- gold: 01000000 / subtype: bit_other / tier: answer_only_keep / solver: none
- correct path: 0:○ 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=01000000 / 1=11 / 2=0 / 2-1=00000000 / 2_1_merge_lora=00000000 / 2_1_2=00000000 / 2_2_merge_lora=10000000 / 2_2_1=10000000
- 0: fmt=boxed, fb=boxed_non_empty, box=01000000, snip=We need to infer the transformation rule from examples. 8-bit binary inputs to outputs also 8-bit. Let's list examp...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the rule from examples. All inputs are 8-bit binary strings. Outputs are also 8-bit strings, but s...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Many outputs are...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=10000000, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Many outputs are...
- assessment: gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。

#### 88fff090
- gold: 01101000 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=11000010 / 2=8 / 2-1=00100 / 2_1_merge_lora=1 / 2_1_2=1 / 2_2_merge_lora=0 / 2_2_1=001011
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary strings. Output also 8-bit. Let's list e...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs are also 8-bit...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11000010 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 11000010 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。

#### 9dfcd4be
- gold: 10101010 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=1 / 2=1 / 2-1=01010000 / 2_1_merge_lora=0 / 2_1_2=0 / 2_2_merge_lora=0 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs (8-bit binary) and outputs. 1) 00101001 -...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 00101001...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit. Let's list examp...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。

#### ab064b6a
- gold: 11111111 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=5 / 2=01100011 / 2-1=1 / 2_1_merge_lora=6 / 2_1_2=1 / 2_2_merge_lora=00101011 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary numbers. Let's list examples with input an...
- 2: fmt=boxed, fb=boxed_non_empty, box=01100011, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10100100...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10100100 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 10100100 -...
- assessment: boxed 到達が散発的で、ほとんどの run は unboxed 長文のまま終わっている。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### b80795b4
- gold: 00010000 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=56 / 2=1 / 2-1=00000 / 2_1_merge_lora=1 / 2_1_2=0 / 2_2_merge_lora=0100 / 2_2_1=011
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with 8-bit binary strings. Examples: 1)...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs (8-bit strings). We'll try to...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10100010 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10100010 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### ba73cc70
- gold: 00011101 / subtype: bit_other / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=11 / 1=20 / 2=0 / 2-1=0 / 2_1_merge_lora=0 / 2_1_2=0 / 2_2_merge_lora=1 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit bina...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs are also 8-bit...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01011110 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 01011110 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 予測が 1 桁または 2 桁断片に崩れやすく、実質的に reasoning の末尾数字を拾っている。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### bcdf9198
- gold: 11111111 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:○ 1:× 2:○ 2-1:○ 2_1_merge_lora:○ 2_1_2:○ 2_2_merge_lora:○ 2_2_1:○
- prediction path: 0=11111111 / 1=3 / 2=11111111 / 2-1=11111111 / 2_1_merge_lora=11111111 / 2_1_2=11111111 / 2_2_merge_lora=11111111 / 2_2_1=11111111
- 0: fmt=boxed, fb=boxed_non_empty, box=11111111, snip=We need to infer the transformation rule from examples. All given inputs map to 11111111. Let's examine patterns. I...
- 2: fmt=boxed, fb=boxed_non_empty, box=11111111, snip=We need to infer the rule from examples. All given inputs map to 11111111. That suggests the rule outputs all 1s if...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=11111111, snip=We need to infer transformation rule from examples. All given inputs map to 11111111. That's all ones. So maybe rul...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=EMPTY, snip=We need to infer transformation rule from examples. All given inputs map to 11111111. That's all ones. So maybe rul...
- assessment: 大半の result で正答しており、policy 崩壊は限定的。merge 系で一時退行しても 8-bit exact answer 自体は保持できている。

#### bdb93228
- gold: 11111101 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:○ 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=2 / 1=7 / 2=1 / 2-1=3 / 2_1_merge_lora=11110100 / 2_1_2=4 / 2_2_merge_lora=10 / 2_2_1=0000010
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary numbers. Let's list examples with indices ...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 00001000...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00001000 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list examples: 1) 0000100...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 途中の result で一度は拾えていたが、specialist merge の 2_1_2 / 2_2_1 ではむしろ壊れた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### bdd63604
- gold: 01010101 / subtype: bit_structured_byte_formula / tier: answer_only_keep / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=0 / 1=0110 / 2=0 / 2-1=8 / 2_1_merge_lora=8 / 2_1_2=4 / 2_2_merge_lora=01010 / 2_2_1=01
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list examples with 8-bit binary strings. I'll denote ...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 10100110...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10100110 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 10100110 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 structured_byte_formula 系で、抽象ルールの復元そのものが全期間で不安定。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### c095f799
- gold: 10011111 / subtype: bit_other / tier: manual_audit_priority / solver: none
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=1 / 1=0 / 2=7 / 2-1=0101101 / 2_1_merge_lora=001 / 2_1_2=110 / 2_2_merge_lora=0 / 2_2_1=00011100
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the bit transformation rule from examples. 8-bit binary inputs and outputs. Let's list examples: 1...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Let's list inputs and outputs as 8-bit strings. 1) 00001011...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 00001011 ->...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs to outputs. Let's list them: 1) 00001011 ->...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 8-bit 文字列を出す回はあるが、例の丸写しや規則取り違えで exact byte が一致しない。 gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### c625ba91
- gold: 11111111 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:○ 1:○ 2:○ 2-1:○ 2_1_merge_lora:○ 2_1_2:○ 2_2_merge_lora:○ 2_2_1:○
- prediction path: 0=11111111 / 1=11111111 / 2=11111111 / 2-1=11111111 / 2_1_merge_lora=11111111 / 2_1_2=11111111 / 2_2_merge_lora=11111111 / 2_2_1=11111111
- 0: fmt=boxed, fb=boxed_non_empty, box=11111111, snip=We need to infer the transformation rule from examples. All given inputs map to 11111111. Let's list them: 11010011...
- 2: fmt=boxed, fb=boxed_non_empty, box=11111111, snip=We need to infer the rule. All given examples map to 11111111. So any input maps to all ones? But maybe there is a ...
- 2_1_2: fmt=boxed, fb=boxed_non_empty, box=11111111, snip=We need to infer transformation rule. All given inputs map to 11111111 except maybe some? Let's list inputs and out...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=11111111, snip=We need to infer transformation rule from examples. All given inputs map to 11111111 (all ones). Wait all examples ...
- assessment: 全 result で安定正答。binary watch 全体ではごく少ない、8-bit exact closure まで一貫して守れたケース。

#### cb7c2230
- gold: 10100000 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:× 2:× 2-1:× 2_1_merge_lora:× 2_1_2:× 2_2_merge_lora:× 2_2_1:×
- prediction path: 0=5 / 1=2 / 2=4 / 2-1=1 / 2_1_merge_lora=1 / 2_1_2=111 / 2_2_merge_lora=010 / 2_2_1=0
- 0: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. Input 8-bit binary string. Output also 8-bit. Let's list ex...
- 2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Outputs also 8-bit. Le...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00100011 -...
- 2_2_1: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. 8-bit binary inputs and outputs. Let's list them: 1) 00100011 -...
- assessment: 全 result で boxed に閉じず、README の boxed-first 抽出ではなく last_number fallback に落ち続けた。 出力長の中央値がかなり長く、例列挙のまま完走して最後の数値に吸われる failure が主流。

#### de11a23a
- gold: 00000001 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:× 1:○ 2:× 2-1:× 2_1_merge_lora:○ 2_1_2:○ 2_2_merge_lora:○ 2_2_1:×
- prediction path: 0=00000000 / 1=00000001 / 2=00000000 / 2-1=00000000 / 2_1_merge_lora=00000001 / 2_1_2=1 / 2_2_merge_lora=00000001 / 2_2_1=00000000
- 0: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output also 8-bit bina...
- 2: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer the rule from examples. All outputs are 8-bit binary with leading zeros, and they seem to be eithe...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit binary strings, b...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=00000000, snip=We need to infer transformation rule from examples. Input 8-bit binary strings, output also 8-bit binary strings, b...
- assessment: gold 自体は raw output に含む run があり、形式または最終コミットの失敗が混ざっている。

#### e368d23f
- gold: 00001101 / subtype: bit_other / tier: verified_trace_ready / solver: binary_affine_xor
- correct path: 0:○ 1:○ 2:○ 2-1:○ 2_1_merge_lora:○ 2_1_2:× 2_2_merge_lora:○ 2_2_1:○
- prediction path: 0=00001101 / 1=00001101 / 2=00001101 / 2-1=00001101 / 2_1_merge_lora=00001101 / 2_1_2=1 / 2_2_merge_lora=00001101 / 2_2_1=00001101
- 0: fmt=boxed, fb=boxed_non_empty, box=00001101, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output appears to be i...
- 2: fmt=boxed, fb=boxed_non_empty, box=00001101, snip=We need to infer the transformation rule from examples. All inputs are 8-bit binary strings. Output appears to be t...
- 2_1_2: fmt=numeric_fallback, fb=last_number, box=none, snip=We need to infer transformation rule from examples. Let's list input and output bits. I'll index bits from left (MS...
- 2_2_1: fmt=boxed, fb=boxed_non_empty, box=00001101, snip=We need to infer transformation rule from examples. Let's list input and output bits. I'll write them as 8-bit stri...
- assessment: 大半の result で正答しており、policy 崩壊は限定的。merge 系で一時退行しても 8-bit exact answer 自体は保持できている。

