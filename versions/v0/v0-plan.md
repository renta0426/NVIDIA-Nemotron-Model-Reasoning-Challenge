v0-plan.md
Version: 0.1  
Owner: me  
Scope: 0-1〜0-4 の基盤固定  
Purpose: 以降の全実験でブレない「評価・分割・プロンプト・目標設定」の唯一の土台を作る

0. この v0 の位置づけ

この v0 は、今後の全ての実験に先立って 絶対に固定すべき前提 を決めるためのもの。  
ここで曖昧さを残すと、以後のスコア差分が「モデル改善」なのか「評価条件のズレ」なのか判別不能になる。

この v0 の責務は次の 4 点のみ。

- 0-1. 正とする評価条件を固定する
- 0-2. visible test.csv をどう扱うかを固定する
- 0-3. 推論時プロンプトの不変条件を固定する
- 0-4. 実験の採用基準とスコア目標を固定する

この v0 では、まだ以下はやらない。

- 合成データ生成の本格設計
- LoRA ハイパラ探索
- RL / DPO / GRPO
- specialist merge
- 生成データの curriculum 最適化

それらは全て、この v0 の上に積む。

1. Source of Truth（最重要）

このコンペには、公開文面どうし・コードどうしのズレがある。  
よって、何を正とするかの優先順位を明示して固定する。

1.1 優先順位

優先順位 A: Kaggle スタッフの公式回答
あなたが提示した公式回答:

The parameters on the Evaluation page override the default parameters.

これを最上位とする。

優先順位 B: Evaluation page / README 記載の公式運用値
したがって、本番採点パラメータは以下を正とする。

- max_lora_rank = 32
- max_tokens = 7680
- top_p = 1.0
- temperature = 0.0
- max_num_seqs = 64
- gpu_memory_utilization = 0.85
- max_model_len = 8192

優先順位 C: metric notebook の実装
ただし、パラメータ以外の動作は notebook 実装を正とする。

具体的には:

- extract_final_answer() の挙動
- verify() の挙動
- user_content の作り方
- tokenizer.apply_chat_template(..., add_generation_prompt=True, enable_thinking=True)
- LoRARequest での読み込み方法
- \boxed{} 優先、fallback ありの抽出ロジック

優先順位 D: docstring / 説明文
コードと docstring が食い違う場合は、docstring ではなくコードを正とする。

例:
- extract_final_answer() は doc 説明上は曖昧だが、実コードでは 最後の数値を拾う
- score() の docstring より、実際の extract_final_answer() 実装を優先する

2. v0 の最終成果物

この v0 完了時点で、以下が揃っていることを完了条件とする。

必須成果物
1. official 評価設定ファイル
2. notebook default 再現設定ファイル
3. competition prompt builder
4. metric faithful extractor / verifier
5. public test 隔離ルール
6. train-only validation split
7. 評価レポートの共通スキーマ
8. 採用基準（promotion rule）
9. 最小 smoke 実行コマンド
10. ユニットテスト

3. ディレクトリ構成

以下を最小構成として固定する。text
project/
├── README.md
├── v0-plan.md
├── conf/
│   ├── eval/
│   │   ├── official_lb.yaml
│   │   ├── notebook_default.yaml
│   │   └── local_debug.yaml
│   ├── data/
│   │   └── split_policy.yaml
│   └── runtime/
│       └── paths.yaml
├── data/
│   ├── raw/
│   │   ├── train.csv
│   │   └── test.csv
│   ├── public_smoke/
│   │   └── test_public.csv
│   ├── processed/
│   │   ├── train_metadata.parquet
│   │   ├── train_splits.parquet
│   │   └── prompt_snapshots.parquet
│   └── eval_packs/
│       ├── shadow_128.csv
│       ├── shadow_256.csv
│       └── hard_shadow_256.csv
├── src/
│   ├── metric_fidelity/
│   │   ├── config.py
│   │   ├── prompting.py
│   │   ├── extraction.py
│   │   ├── verify.py
│   │   ├── score_rows.py
│   │   └── tests_reference.py
│   ├── data/
│   │   ├── family_parser.py
│   │   ├── metadata_builder.py
│   │   ├── split_builder.py
│   │   └── smoke_guard.py
│   ├── eval/
│   │   ├── run_local_eval.py
│   │   ├── compare_local_vs_kaggle.py
│   │   └── report.py
│   └── utils/
│       ├── io.py
│       ├── hashes.py
│       └── logging.py
├── scripts/
│   ├── prepare_public_smoke.py
│   ├── build_metadata.py
│   ├── build_splits.py
│   ├── build_prompt_snapshots.py
│   ├── run_shadow_eval.sh
│   └── validate_v0.sh
└── tests/
    ├── test_extraction.py
    ├── test_verify.py
    ├── test_prompt_builder.py
    ├── test_public_smoke_isolation.py
    └── test_split_integrity.py
0-1. 正とする評価条件を固定する

0-1-1. 結論

本番を模す primary mode
以後の 全モデル選定の第一指標 は、以下の official_lb を用いる。

- max_lora_rank = 32
- max_tokens = 7680
- top_p = 1.0
- temperature = 0.0
- max_num_seqs = 64
- gpu_memory_utilization = 0.85
- max_model_len = 8192
- prompt 組み立ては metric notebook と同一
- enable_thinking = True
- add_generation_prompt = True

notebook 再現の secondary mode
比較用に notebook_default も保持する。

- max_tokens = 3584
- temperature = 1.0
- max_num_seqs = 128
- max_model_len = 4096

ただし、モデル採用の主判定には使わない。  
これは以下の用途に限定する。

- metric notebook の挙動差確認
- stochastic robustness 観察
- 過去の仮説との比較
- Kaggle notebook での再現確認

0-1-2. 評価モードを 3 つに分離する

Mode A: official_lb
最重要。採用判定の主指標。yaml
conf/eval/official_lb.yaml
name: official_lb
max_lora_rank: 32
max_tokens: 7680
top_p: 1.0
temperature: 0.0
max_num_seqs: 64
gpu_memory_utilization: 0.85
max_model_len: 8192
enable_thinking: true
add_generation_prompt: true
boxed_instruction: "Please put your final answer inside \\boxed{}. For example: \\boxed{your answer}"
strict_chat_template: true
Mode B: notebook_default
副指標。あくまで参考。yaml
conf/eval/notebook_default.yaml
name: notebook_default
max_lora_rank: 32
max_tokens: 3584
top_p: 1.0
temperature: 1.0
max_num_seqs: 128
gpu_memory_utilization: 0.85
max_model_len: 4096
enable_thinking: true
add_generation_prompt: true
boxed_instruction: "Please put your final answer inside \\boxed{}. For example: \\boxed{your answer}"
strict_chat_template: true
Mode C: local_debug
ローカル開発用。速度優先。採用判定には使わない。yaml
conf/eval/local_debug.yaml
name: local_debug
max_lora_rank: 32
max_tokens: 1024
top_p: 1.0
temperature: 0.0
max_num_seqs: 16
gpu_memory_utilization: 0.75
max_model_len: 4096
enable_thinking: true
add_generation_prompt: true
boxed_instruction: "Please put your final answer inside \\boxed{}. For example: \\boxed{your answer}"
strict_chat_template: true
0-1-3. 実装ルール

Rule 1: score() の default を信用しない
ローカル rerun では 必ず config を明示指定する。  
暗黙 default 禁止。

禁止python
score(solution, submission, row_id_column_name="id")
正python
score(
    solution,
    submission,
    row_id_column_name="id",
    max_lora_rank=32,
    max_tokens=7680,
    top_p=1.0,
    temperature=0.0,
    max_num_seqs=64,
    gpu_memory_utilization=0.85,
    max_model_len=8192,
)
Rule 2: prompt / extraction / verify は metric faithful 実装をコピーフリーズする
以後、独自改変禁止。  
改変する場合は別名関数にする。

Rule 3: 公式評価との差異は常にログに残す
ローカルが MLX / HF / Transformers、Kaggle が vLLM なので、backend 差はゼロにならない可能性がある。  
そのため official_lb は パラメータ faithful + metric faithful を意味し、backend faithful は Kaggle 最終確認で担保する。

0-1-4. 実装対象関数

src/metric_fidelity/config.pypython
from dataclasses import dataclass

@dataclass(frozen=True)
class EvalConfig:
    name: str
    max_lora_rank: int
    max_tokens: int
    top_p: float
    temperature: float
    max_num_seqs: int
    gpu_memory_utilization: float
    max_model_len: int
    enable_thinking: bool
    add_generation_prompt: bool
    boxed_instruction: str
    strict_chat_template: bool = True
src/metric_fidelity/prompting.pypython
def build_user_content(raw_prompt: str, boxed_instruction: str) -> str:
    return raw_prompt + "\n" + boxed_instruction

def apply_competition_chat_template(tokenizer, user_content: str, *, enable_thinking: bool, add_generation_prompt: bool, strict_chat_template: bool = True) -> str:
    try:
        return tokenizer.apply_chat_template(
            [{"role": "user", "content": user_content}],
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=enable_thinking,
        )
    except Exception:
        if strict_chat_template:
            raise
        return user_content
src/metric_fidelity/extraction.py
metric notebook 実装をそのまま移植する。  
仕様差分を入れない。

src/metric_fidelity/verify.py
math.isclose(rel_tol=1e-2, abs_tol=1e-5) を固定する。

src/metric_fidelity/score_rows.py
行単位で次を返す。

- id
- family
- raw_output
- extracted_answer
- gold_answer
- is_correct
- format_bucket
- has_boxed
- boxed_count
- contains_risky_chars
- output_num_tokens_est
- eval_mode

0-1-5. 絶対に必要なテスト

extraction unit tests
最低限このケースを固定する。

1. \boxed{42} → 42
2. The final answer is: 3.14 → 3.14
3. Final answer: 7 → 7
4. 数字が複数ある文 → 最後の数値
5. boxed が複数ある → 最後の非空 boxed
6. \boxed{} 空 → 空 boxed 挙動確認
7. \boxed{abc 未閉じ → abc
8. 答えに } を含む → boxed が途中切断されることを再現
9. 数値がなく最終行だけある → 最終行採用
10. None → NOT_FOUND

verify unit tests
1. "1.00" と "1" は一致
2. "0.0099" と "0.01" の tolerance
3. "XIV" と "xiv" は一致
4. "0101" と "101" は不一致
5. "abc" と "ABC" は一致
6. "1,000" は float 変換不可なので文字列比較になる点を確認

prompt builder tests
1. 改行位置一致
2. instruction 文言一致
3. apply_chat_template の rendered string snapshot 一致
4. enable_thinking=True を常に通す
5. 例外時 fallback を strict モードでは許さない

0-1-6. Kaggle/backend 差を測る shadow pack を作る

Mac 上の local inference backend は Kaggle の vLLM と完全一致しない可能性がある。  
したがって、backend drift を測る固定パックを v0 で作る。

shadow_128.csv
用途:
- 速い比較
- 日次チェック

shadow_256.csv
用途:
- serious candidate の比較

hard_shadow_256.csv
用途:
- 難例に対する backend 差 / format 差確認

構成ルール
- train からのみ抽出
- family stratified
- answer_type stratified
- risky char を含む symbol を必ず含める
- rounding sensitive な numeric も含める

ログで見るべき差分
- local_extracted == kaggle_extracted
- local_correct == kaggle_correct
- family 別一致率
- boxed 有無差
- output length 差

運用ルール
- serious candidate は Kaggle で shadow_256 を最低1回通す
- local vs kaggle の extracted 一致率が 98% 未満なら、その local backend でのモデル選定を一時停止して原因調査する

0-1-7. 0-1 の完了条件

- [ ] official_lb.yaml がある
- [ ] notebook_default.yaml がある
- [ ] metric faithful extract_final_answer() / verify() 実装済み
- [ ] prompt builder 実装済み
- [ ] unit tests 全通過
- [ ] shadow_128 / shadow_256 / hard_shadow_256 作成済み
- [ ] Kaggle で official mode を明示指定した rerun 手順が文書化済み

0-2. visible test.csv をどう扱うかを固定する

0-2-1. 結論

data/test.csv は 性能評価に一切使わない。  
用途は以下に限定する。

- submission zip の smoke test
- prompt rendering の確認
- extraction の確認
- end-to-end 推論パイプライン確認

禁止事項
- visible test score を validation score と呼ぶ
- visible test に合わせて prompt やモデルを調整する
- visible test を split に混ぜる
- README / notebook / report に visible test を性能根拠として書く

0-2-2. 運用ルール

Rule 1: 原本を隔離する
data/raw/test.csv は直接使わない。  
以下へコピーして扱う。bash
python scripts/prepare_public_smoke.py
出力:text
data/public_smoke/test_public.csv
Rule 2: 全 evaluation script は明示的にデータソースを受け取る
暗黙で test.csv を読むスクリプトを作らない。

禁止python
df = pd.read_csv("data/raw/test.csv")
正python
df = pd.read_csv(args.input_csv)
Rule 3: smoke 用と validation 用で出力先を分離する
- public smoke の結果: outputs/smoke/...
- train-derived validation の結果: outputs/valid/...

0-2-3. train-only validation を v0 で作る

visible test が使えないため、v0 で train から正式な検証系を作る。

split は 3 系統作る

Split A: cv5_strat_family
最重要。日常運用の主評価。

- 5-fold
- family stratified
- answer_type stratified
- fold ごとの件数偏り最小化

Split B: holdout_hard
hard case 専用 holdout。

- rounding hard
- risky chars
- long text phrase
- bit ambiguity high
- symbol 長短混在
- roman subtractive edge

Split C: group_shift
同族 shift 検証。

family 内で以下の signature で grouped split を切る。

- bit: 推定 op family
- gravity: g bin
- unit: ratio bin
- text: cipher family
- roman: decade bin / subtractive bin
- symbol: transduction family

最低限 v0 で必要なのは A と B
C は parser 精度が上がったら追加でよい。  
ただしメタデータ列は最初から用意しておく。

0-2-4. train metadata を先に作る

必須列
- id
- prompt
- answer
- family
- subfamily
- answer_type
- answer_len
- prompt_len_chars
- prompt_len_words
- special_chars
- contains_right_brace
- contains_backslash
- contains_backtick
- num_examples_est
- difficulty_hint
- risk_flag
- is_public_test_overlap
- fold_cv5
- is_hard_holdout

family の初期ルールベース分類
まずは regex ベースで十分。

bit
- "8-bit" / "binary" / "bit" / 00101101 のような 8bit pattern

gravity
- "gravity" / "d = 0.5" / "fall" / "distance"

unit
- "conversion" / "units" / "convert" / 実例の比率表現

text_decrypt
- "decode" / "decrypt" / "cipher" / "encoded"

roman
- "Roman numerals" / "Roman numeral" / XIV など

symbol_equation
- 上記のどれでもない短い記号列変換系

実装ファイル
- src/data/family_parser.py
- src/data/metadata_builder.py

0-2-5. public overlap を厳格に管理する

test.csv の 3 件が train と一致していることが既に分かっている。  
よって metadata に次を必ず付与する。

- is_public_test_overlap
- public_test_overlap_type (id_match, prompt_match, exact_row_match)

ルール
- overlap 行は validation fold に入れてよいが、public smoke と同列に扱わない
- report の集計時には is_public_test_overlap を除外した値も必ず出す

0-2-6. 0-2 の完了条件

- [ ] data/public_smoke/test_public.csv を生成済み
- [ ] train_metadata.parquet を生成済み
- [ ] cv5_strat_family を生成済み
- [ ] holdout_hard を生成済み
- [ ] public test を validation に使うコードパスが存在しない
- [ ] smoke 出力先と validation 出力先が分離済み

0-3. 推論時プロンプトの不変条件を固定する

0-3-1. 結論

本番推論プロンプトは変更できないものとして扱う。  
よって、v0 では「推論 prompt を 1 箇所で生成し、全実験でそれを使い回す」ことを固定する。

本番 prompt 構造
metric notebook 実装に従い、user content は以下。text
{raw_prompt}
Please put your final answer inside \boxed{}. For example: \boxed{your answer}
これをpython
tokenizer.apply_chat_template(
    [{"role": "user", "content": user_content}],
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True,
)
へ通す。

不変条件
- system prompt を足さない
- few-shot を足さない
- role を増やさない
- boxed instruction を変更しない
- enable_thinking=False にしない
- 別 chat template を使わない

0-3-2. 実装上の強制策

Rule 1: prompt builder を単一関数に閉じ込める
全ての推論系コードは必ずこれを通る。python
def build_competition_prompt(tokenizer, raw_prompt: str, eval_config: EvalConfig) -> str:
    user_content = build_user_content(raw_prompt, eval_config.boxed_instruction)
    return apply_competition_chat_template(
        tokenizer,
        user_content,
        enable_thinking=eval_config.enable_thinking,
        add_generation_prompt=eval_config.add_generation_prompt,
        strict_chat_template=eval_config.strict_chat_template,
    )
Rule 2: prompt 文字列を snapshot 保存する
train の先頭 100 件、各 family から 5 件、public smoke 全件について  
rendered prompt の hash と全文を保存する。

出力:
- data/processed/prompt_snapshots.parquet

列:
- id
- family
- raw_prompt_hash
- rendered_prompt_hash
- rendered_prompt_text
- tokenizer_name
- tokenizer_revision
- eval_mode

Rule 3: tokenizer バージョンを pin する
推論 prompt が tokenizer 実装依存になるため、base model tokenizer revision を固定する。  
revision 未固定の pip install -U transformers のような運用は禁止。

0-3-3. strict / non-strict の方針

metric notebook には try/except fallback があるが、v0 では次の方針にする。

local development
- strict_chat_template=True
- chat template が落ちたら 即失敗
- fallback は使わない

Kaggle smoke / emergency only
- metric notebook faithful のため fallback 実装は保持
- ただし fallback が発生したら warning を出す
- serious run で fallback 発生は NG 判定

理由
base model が公式 model card 通りなら chat template は使えるはず。  
silent fallback は distribution shift を隠すため危険。

0-3-4. 学習データ側への反映

推論 prompt が固定なので、SFT / DPO / synthetic でも user 側はこれに合わせる。

学習データの user 側
全データで、user メッセージは以下とする。text
{original_problem_prompt}
Please put your final answer inside \boxed{}. For example: \boxed{your answer}
assistant 側
v0 ではまだ多様化しすぎない。  
最低限、以下 2 種だけを許す。

Style A: standard boxedtext
...reasoning...
\boxed{ANSWER}
Style B: fallback final answer linetext
...reasoning...
Final answer: ANSWER
重要
- user 側の instruction を downstream で変えない
- prompt 実験は「学習対象の出力スタイル」で行い、推論時 user prompt は変えない

0-3-5. prompt fidelity テスト

snapshot test
以下の 3 水準で snapshot を固定する。

1. family ごとの代表 1 件
2. public smoke 3 件
3. hard case 代表 10 件

比較項目
- 改行数
- 末尾 instruction 一致
- rendered prompt hash
- assistant generation prefix の有無
- thinking token / template 差分

失敗時の扱い
- tokenizer 更新
- model revision 更新
- prompt builder 改変
のいずれかが原因なので、以後の実験を止めて原因調査

0-3-6. 0-3 の完了条件

- [ ] competition prompt builder 実装済み
- [ ] prompt snapshots 保存済み
- [ ] strict mode で全 family の prompt render 成功
- [ ] tokenizer revision 固定済み
- [ ] SFT 用 user prompt も competition form に統一済み
- [ ] prompt 改変禁止ルールを文書化済み

0-4. 実験の採用基準とスコア目標を固定する

0-4-1. 結論

このコンペの最終目標は top10 / 0.9+ だが、v0 ではそれを  
日々の意思決定に使える運用指標 に分解する。

Primary metric
official_lb 条件での train-derived validation accuracy

Secondary metrics
- hard holdout accuracy
- family 別 accuracy
- extraction fail 率
- format fail 率
- local vs kaggle drift
- output length 異常率

重要方針
overall だけで採用しない。  
family 崩壊や format 崩壊を見逃さない。

0-4-2. 目標値を 3 段階に分ける

段階 1: v0 完了目標（基盤成立）
これはスコア目標ではなく、基盤品質目標。

- official_lb で deterministic rerun ができる
- split が固定される
- family 別レポートが出る
- public smoke と validation が混ざらない
- prompt drift がない

段階 2: 実験運用目標（本格探索開始ライン）
local OOF で以下を目指す。

- cv5_strat_family mean >= 0.88
- holdout_hard >= 0.84
- extraction fail rate = 0.78

段階 3: top10 狙い目標
モデル選定の最終目標値。

- cv5_strat_family mean >= 0.93
- holdout_hard >= 0.90
- extraction fail rate = 0.87
- local vs kaggle extracted agreement >= 98.5%

0-4-3. family 別の目標値

最終的な狙い値を以下に置く。

| family | target |
|---|---:|
| roman | 0.995+ |
| unit | 0.990+ |
| gravity | 0.985+ |
| bit | 0.940+ |
| text_decrypt | 0.920+ |
| symbol_equation | 0.890+ |

補足
- roman / unit / gravity は落としてはいけない family
- bit / text / symbol が勝負所
- hidden test の分布ズレに備え、overall 0.90 で安心せず 0.93 以上を目指す

0-4-4. モデル採用の promotion rule

Rule A: 日常の実験採用
新モデルを「現行 best 候補」に昇格させる条件:

- official_lb cv mean が +0.003 以上改善
- holdout_hard が悪化しない
- どの family も -0.010 を超えて悪化しない
- extraction fail rate が悪化しない

Rule B: serious candidate 化
Kaggle shadow rerun に回す条件:

- official_lb cv mean が現 best 比 +0.005 以上
  または
- holdout_hard が +0.008 以上
- prompt / extraction / packaging smoke を通過
- local drift 懸念がない

Rule C: 本提出候補
- Kaggle official settings で shadow rerun 済み
- PEFT load OK
- public smoke OK
- best 比で local 指標改善
- catastrophic family drop なし

0-4-5. スコアレポートのフォーマットを固定する

全実験で必ず次の表を出す。

summary.csv
- run_name
- model_name
- adapter_name
- eval_mode
- split_name
- overall_acc
- hard_acc
- extraction_fail_rate
- format_fail_rate
- avg_output_len
- timestamp

family_metrics.csv
- run_name
- family
- n
- acc
- extraction_fail_rate
- format_fail_rate
- avg_output_len

row_level.parquet
- id
- family
- prompt_hash
- gold_answer
- raw_output
- extracted_answer
- is_correct
- has_boxed
- boxed_count
- fallback_type
- contains_extra_numbers
- contains_risky_chars
- eval_mode

0-4-6. bootstrap / CI を毎回出す

データ数 9500 は十分あるが、split 差や family 差がある。  
よって mean accuracy だけでなく、bootstrap CI を毎回出す。

実装
- 1000 bootstrap
- overall 95% CI
- family 別 95% CI
- best run との差の bootstrap delta

採用ルール
平均差が +0.002 程度なら、CI を見てから判断する。  
誤差内の改善を本採用しない。

0-4-7. v0 で最初に記録すべき baseline

以下の 3 本を最初の基準点として固定保存する。

1. base / no adapter
2. dummy adapter / random-like smoke adapter
3. first minimal real-only LoRA baseline

これをもとに、以後の改善幅を常に比較する。

0-4-8. 0-4 の完了条件

- [ ] primary / secondary metrics が固定済み
- [ ] family target が固定済み
- [ ] promotion rule が固定済み
- [ ] report schema 実装済み
- [ ] bootstrap CI を出せる
- [ ] baseline 3 本の記録先が用意されている

4. 実装順序

この順でやる。順序を崩さない。

Step 1
conf/eval/official_lb.yaml と notebook_default.yaml を作る

Step 2
extract_final_answer(), verify(), build_user_content(), build_competition_prompt() を実装

Step 3
unit tests を書いて全部通す

Step 4
prepare_public_smoke.py を書いて public test を隔離

Step 5
build_metadata.py を書いて family / risk metadata を付ける

Step 6
build_splits.py を書いて cv5_strat_family と holdout_hard を作る

Step 7
prompt snapshots を保存して drift guard を作る

Step 8
run_local_eval.py で report schema を固定

Step 9
shadow packs を作る

Step 10
Kaggle 上で official config 明示 rerun 手順を確認

5. 直ちに実行するコマンドbash
python scripts/prepare_public_smoke.py
python scripts/build_metadata.py --input data/raw/train.csv --output data/processed/train_metadata.parquet
python scripts/build_splits.py --input data/processed/train_metadata.parquet --output data/processed/train_splits.parquet
python scripts/build_prompt_snapshots.py --input data/processed/train_splits.parquet
pytest tests/test_extraction.py tests/test_verify.py tests/test_prompt_builder.py tests/test_public_smoke_isolation.py tests/test_split_integrity.py -q
bash scripts/validate_v0.sh
6. validate_v0.sh の中身bash
#!/usr/bin/env bash
set -euo pipefail

echo "[1/6] unit tests"
pytest tests/test_extraction.py tests/test_verify.py tests/test_prompt_builder.py tests/test_public_smoke_isolation.py tests/test_split_integrity.py -q

echo "[2/6] metadata existence"
test -f data/processed/train_metadata.parquet

echo "[3/6] split existence"
test -f data/processed/train_splits.parquet

echo "[4/6] prompt snapshots existence"
test -f data/processed/prompt_snapshots.parquet

echo "[5/6] public smoke isolation"
test -f data/public_smoke/test_public.csv

echo "[6/6] config existence"
test -f conf/eval/official_lb.yaml
test -f conf/eval/notebook_default.yaml

echo "v0 validation passed."
7. この v0 で固定される意思決定

この v0 が完了したら、以後の全実験で以下を固定する。

1. 本番相当評価は official_lb 設定で見る
2. visible test.csv は smoke 専用
3. 推論 prompt は competition form から動かさない
4. overall ではなく family / format / hard split を併記する
5. 改善判定は promotion rule に従う
6. backend 差は shadow pack で常時監視する

8. v0 完了後に着手する次フェーズ

v0 の次にやるべきは以下。

- v1: family parser 高精度化 + baseline LoRA
- v2: sibling synthetic data
- v3: distilled traces
- v4: format sharpening
- v5: correction / preference / RFT

ただし、v0 が完全に固まるまでは先に進まない。

補足だけ短く言う。

今回の重要修正点
前回は metric notebook の score() デフォルト値を正としたが、  
今回の Kaggle スタッフ回答により、評価パラメータは Evaluation page の値を正とすべき。  
つまり v0 では primary mode を README/Evaluation page 準拠に修正するのが正しい。

特に影響が大きいのは:

- temperature=0.0 → 本番は deterministic 寄り
- max_tokens=7680 → 長めの reasoning も許容
- max_model_len=8192 → context 余裕あり
- max_num_seqs=64 → throughput 条件が notebook default と違う

なので、以後の全設計は  
「greedy/deterministic 本番最適化」 を主軸に置くべき。

必要なら次にそのまま続けて、  
src/metric_fidelity/* と scripts/* の実装仕様書  
まで書ける。  
さらに踏み込むなら、build_metadata.py と build_splits.py の具体ロジック もそのままコード化前提で詰められる。
