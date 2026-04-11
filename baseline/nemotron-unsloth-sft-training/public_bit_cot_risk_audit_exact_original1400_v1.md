# public bit CoT risk audit exact-original1400 v1

## README contract

- Evaluation and submission contract is taken from README.md.
- Binary answers are judged by final-answer accuracy, with boxed extraction prioritized.
- This audit therefore treats teacher rows as risky when the generated CoT contains mechanically detectable unsupported inference steps even if the final answer is present.

## Input artifact

- source CSV: `baseline/nemotron-unsloth-sft-training/artifacts/training_source_repro_public_bit_exact_original1400_v1_2026-04-11.csv`
- audited bit rows: `1400`

## Mechanical risk rules

- `zero_evidence_constant_fill`: `Matching output` is `none`, `left=0`, `right=0`, and `Selected` still fixes `C0` or `C1`.
- `zero_evidence_forced_selection`: `Matching output` is `none`, `left=0`, `right=0`, and `Selected` still fixes any operator.
- `continuity_only_fill`: direct match is absent but `Selected` relies only on continuity extrapolation.
- `off_template_selection`: `Selected` is neither in direct candidates nor equal to the stated continuity best.
- `local_partial_support`: carried over from the generator metadata, used only as a secondary signal.
- `low_supported_bits`: generator metadata says at most 6 of 8 bits were directly supported.
- `short_total_span`: generator metadata says the continuity evidence span is short (`<20`).

## Summary counts

- high risk rows: `126`
- medium risk rows: `0`
- low risk rows: `18`
- clean rows: `1256`
- rows with any `Matching output = none`: `126`
- rows with zero-evidence forced selection: `126`
- rows with zero-evidence constant fill: `126`
- rows with continuity-only fill: `0`
- rows with off-template selection: `0`

## Top flagged examples

| id | fully_supported | supported_bits | total_span | risk_level | risk_flags | zero_evidence_bits | continuity_only_bits |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: |
| a6192d29 | False | 2 | 2 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 6 | 0 |
| 25a8aeb1 | False | 3 | 5 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 5 | 0 |
| 8bca1334 | False | 3 | 5 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 5 | 0 |
| 12154247 | False | 4 | 6 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 4 | 0 |
| 202af98d | False | 4 | 4 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 4 | 0 |
| 44fb2f96 | False | 4 | 6 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 4 | 0 |
| 5ba26f21 | False | 4 | 4 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 4 | 0 |
| 7bad754f | False | 4 | 6 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 4 | 0 |
| 7c27d6df | False | 4 | 6 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 4 | 0 |
| 8dcbf9d4 | False | 4 | 6 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 4 | 0 |
| 000b53cf | False | 5 | 11 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 3 | 0 |
| 00890aff | False | 5 | 7 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 3 | 0 |
| 06120e47 | False | 5 | 9 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 3 | 0 |
| 2230fad0 | False | 5 | 9 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 3 | 0 |
| 27c3ce54 | False | 5 | 11 | high | zero_evidence_constant_fill|zero_evidence_forced_selection|local_partial_support|low_supported_bits|short_total_span | 3 | 0 |

## Interpretation

- This audit is artifact-level: it judges the generated CoT text that is actually being trained on.
- It does not prove that the underlying public strategy can never justify these rows under a better implementation.
- It does show which rows, in the current artifact, contain mechanically detectable unsupported or weakly supported inference steps and should be down-weighted, filtered, or re-generated before SFT.

ーーー
生成済み BIT CoT から、危険な teacher を機械的に落とすためのヒューリスティック判定を実装し、1400件版に実際に当てて件数と具体例を出します。最終的に、再利用できる判定基準とその結果を artifact として残します。

To Do 項目が 5 件作成されました

判定基準を既存生成物の構造に合わせるため、まず artifact の列構成と CoT の型を確認します。これで false positive の少ないルールに寄せます。

`**/baseline/nemotron-unsloth-sft-training/**/*.py` に一致するファイルを検索しました。一致するものはありません

`**/baseline/nemotron-unsloth-sft-training/**/*.md` に一致するファイルを検索しました。一致 4

[](file:///home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/baseline/nemotron-unsloth-sft-training/artifacts/training_source_repro_public_bit_exact_original1400_v1_2026-04-11.csv#1-1) の 1 から 20 行を読み取り

判定を再現可能にするため、CoT 本文から危険シグナルを直接拾う単一スクリプトを追加し、1400件版に実行して CSV とサマリーを出します。

パッチを生成中 (359 行)、[](file:///home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/baseline/nemotron-unsloth-sft-training/audit_public_bit_cot_risk_v1.py) 内


```

```
スクリプトは入れました。次に 1400件版へ実行して、実際の high/medium risk 行数と代表例を確定します。

開始中: *1400件 artifact に適用* (4/5)

実データへ適用して件数とサマリー artifact を出します。結果次第で閾値やルールの妥当性も点検します。

Ran terminal command:  /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/.venv/bin/python baseline/nemotron-unsloth-sft-training/audit_public_bit_cot_risk_v1.py

結果はかなりはっきりしていて、high risk 126件がちょうど zero-evidence forced selection と一致しました。出力が想定どおりかを確認し、返答に使う代表例を拾います。

チェックされた [](file:///home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/baseline/nemotron-unsloth-sft-training/audit_public_bit_cot_risk_v1.py)、問題は見つかりませんでした

[](file:///home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/baseline/nemotron-unsloth-sft-training/public_bit_cot_risk_audit_exact_original1400_v1.md) の読み取り

[](file:///home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/baseline/nemotron-unsloth-sft-training/artifacts/public_bit_cot_risk_audit_exact_original1400_v1.csv#1-1) の 1 から 20 行を読み取り

補助的な弱シグナルだけで low に落ちている行も確認します。これで、危険と弱い候補を分けて説明できます。

Ran terminal command:  /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/.venv/bin/python - <<'PY'
import csv
from pathlib import Path
path = Path('baseline/nemotron-unsloth-sft-training/artifacts/public_bit_cot_risk_audit_exact_original1400_v1.csv')
rows=[]
with path.open(encoding='utf-8', newline='') as f:
    rows=list(csv.DictReader(f))
low=[r for r in rows if r['risk_level']=='low']
print('low_count', len(low))
for r in low[:10]:
    print(r['id'], r['fully_supported'], r['supported_bits'], r['total_span'], r['risk_flags'])
PY

1400件版 public BIT CoT に対する機械的リスク監査を実装して実行し、危険行の判定 CSV と Markdown サマリーを生成しました。高リスク 126 件は、CoT 本文上で `Matching output = none` かつ `left=0/right=0` の bit に対して、それでも `Selected` で定数や規則を確定している行として抽出できました。

完了済み: *1400件 artifact に適用* (4/5)



機械的判定を実装して、1400件版に当てました。追加したスクリプトは audit_public_bit_cot_risk_v1.py です。結果は public_bit_cot_risk_audit_exact_original1400_v1.csv と public_bit_cot_risk_audit_exact_original1400_v1.md に保存しました。

今回の判定は local の fully supported / partially supported だけには依存していません。CoT 本文から直接、`Matching output`、`Left / Right continuity`、`Selected` を読んで複数のルールで判定しています。主な基準は次です。

1. `zero_evidence_constant_fill`
`Matching output` が `none` で、しかも `left=0` かつ `right=0` なのに、`Selected` で `C0` または `C1` を確定している。

2. `zero_evidence_forced_selection`
同じく direct match も continuity evidence も無いのに、何らかの規則を `Selected` で確定している。

3. `continuity_only_fill`
direct match は無いが、continuity だけで補完している。

4. `off_template_selection`
`Selected` が direct candidates にも continuity best にも載っていない。

5. 補助信号
`supported_bits <= 6`、`total_span < 20` など。これは単独では危険と断定せず、弱い候補として扱っています。

実測結果はかなり明確でした。

1. 高リスク: 126件
2. 中リスク: 0件
3. 低リスク: 18件
4. クリーン: 1256件

高リスク 126件は、全件が `Matching output = none` を含み、しかもその bit で `left=0/right=0` のまま `Selected` を確定していました。つまり、今の生成 artifact に限れば、この 126件は「根拠ゼロの bit 補完を含む CoT teacher」と機械的に言えます。代表例は formatted_train_dataset_repro_public_bit_exact_original1400_v1_2026-04-11.csv formatted_train_dataset_repro_public_bit_exact_original1400_v1_2026-04-11.csv formatted_train_dataset_repro_public_bit_exact_original1400_v1_2026-04-11.csv formatted_train_dataset_repro_public_bit_exact_original1400_v1_2026-04-11.csv です。

一方で低リスク 18件は、今のルールでは `short_total_span` だけで落ちている fully supported 行でした。これは危険というより、監視対象に近いです。例として public_bit_cot_risk_audit_exact_original1400_v1.csv の `risk_level=low` 行を見ると、`fully_supported=True` かつ `supported_bits=8` で、単に `total_span` が短いだけです。

要するに、今回の機械的判定で安全に切れるのは次です。

1. 126件は、現 artifact の CoT teacher としては危険寄り
2. 1256件は、少なくとも今回の本文監査では明確な unsupported inference は見つからない
3. 18件は危険断定ではなく要注意

次にやるならこの順が自然です。

1. この 126件を学習から外した filtered 1274件版を作る
2. 126件を answer-only に落とした版を作る
3. 1274件版と 1400件版で同条件の学習比較を取る

変更を行いました。