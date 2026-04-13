以下、そのまま v1-plan.md として保存できる形で書く。  
v0 完了を前提に、1-1〜1-5 を 実装仕様レベルまで落とす。

v1-plan.md
Version: 0.1  
Owner: me  
Prerequisite: v0-plan.md 完了済み  
Scope: 1-1〜1-5 の基盤構築  
Purpose: 今後の全実験で使い回す「評価・分割・分類・多視点診断」の中核を固定する

Historical plan note: this file preserves the original planning context, but the current authoritative competition contract is the top-level `README.md` Evaluation / Submitting section (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). If later sections in this historical plan mention older notebook/metric defaults, read them as historical notes rather than as the active contract.

0. この v1 の位置づけ

v0 で固定したのは、以下だった。

- official evaluation 条件
- public test の扱い
- competition prompt の不変条件
- 実験採用ルールの大枠

v1 では、その上に 実際に毎日回す基盤 を作る。

この v1 の責務は次の 5 点のみ。

- 1-1. metric faithful な local evaluator を作る
- 1-2. extraction 危険ケースのテストベッドを作る
- 1-3. 3 系統 validation を deterministic に作る
- 1-4. family classifier / parser を deterministic に作る
- 1-5. official deterministic 評価 + stochastic probe 評価の 2 軸を作る

ここで作るものは、今後の
- baseline LoRA
- synthetic data
- distillation
- DPO / RFT / RL
- adapter merge
のすべての比較土台になる。

したがってこの v1 では、速度よりも再現性と観測可能性を優先する。

1. v1 の最終成果物

必須成果物
1. metric_faithful_evaluator
2. row_level_eval_schema
3. extraction_risk_test_suite
4. train_metadata_v1.parquet
5. train_splits_v1.parquet
6. family_parser_v1
7. official_det@1 評価モード
8. sc_probe@K 評価モード
9. shadow pack / hard shadow pack
10. daily eval command / nightly eval command

2. 追加ディレクトリ構成

v0 構成に以下を追加する。text
project/
├── conf/
│   ├── eval/
│   │   ├── official_lb.yaml
│   │   ├── notebook_default.yaml
│   │   ├── local_debug.yaml
│   │   ├── sc_probe_k4.yaml
│   │   ├── sc_probe_k8.yaml
│   │   └── sc_probe_k16.yaml
│   └── parser/
│       ├── family_rules.yaml
│       └── hardness_rules.yaml
├── data/
│   ├── processed/
│   │   ├── train_metadata_v1.parquet
│   │   ├── train_splits_v1.parquet
│   │   ├── family_fixtures_v1.jsonl
│   │   └── extraction_fixtures_v1.jsonl
│   └── eval_packs/
│       ├── cv5_fold0.csv
│       ├── cv5_fold1.csv
│       ├── cv5_fold2.csv
│       ├── cv5_fold3.csv
│       ├── cv5_fold4.csv
│       ├── holdout_hard.csv
│       ├── group_shift_split0.csv
│       ├── group_shift_split1.csv
│       ├── group_shift_split2.csv
│       ├── shadow_128.csv
│       ├── shadow_256.csv
│       └── hard_shadow_256.csv
├── outputs/
│   ├── eval/
│   ├── reports/
│   └── audits/
├── src/
│   ├── metric_fidelity/
│   │   ├── types.py
│   │   ├── config.py
│   │   ├── prompting.py
│   │   ├── extraction.py
│   │   ├── verify.py
│   │   ├── annotate.py
│   │   ├── evaluator.py
│   │   └── aggregate.py
│   ├── backends/
│   │   ├── protocol.py
│   │   ├── replay_backend.py
│   │   ├── mlx_backend.py
│   │   └── hf_backend.py
│   ├── data/
│   │   ├── family_parser.py
│   │   ├── metadata_builder.py
│   │   ├── split_builder.py
│   │   ├── shadow_pack_builder.py
│   │   └── audits.py
│   └── eval/
│       ├── run_eval.py
│       ├── run_probe.py
│       ├── run_compare.py
│       └── report.py
└── tests/
    ├── test_extraction_risks.py
    ├── test_family_parser.py
    ├── test_family_count_regression.py
    ├── test_split_builder.py
    ├── test_eval_determinism.py
    └── test_probe_metrics.py
1-1. metric faithful な local evaluator を作る

1-1-1. 目的

local evaluator の役割は、「ローカル生成結果」を official metric と同じロジックで採点し、行レベルで失敗原因まで見えるようにすること。

重要なのは、ここでいう faithful が 3つの層に分かれること。

faithful にする層
1. prompt faithful
   - boxed instruction 追記
   - chat template
   - enable_thinking=True
   - add_generation_prompt=True

2. scoring faithful
   - extract_final_answer()
   - verify()
   - numeric tolerance
   - boxed 優先 / fallback 順

3. parameter faithful
   - official evaluation page の値
   - temperature=0.0
   - max_tokens=7680
   - max_model_len=8192
   - max_num_seqs=64

faithful にしきれない層
4. backend faithful
   - Kaggle は vLLM
   - ローカルは MLX / HF 等

これは完全一致しない可能性があるため、shadow pack で drift 監視する。

1-1-2. 設計原則

Principle 1: evaluator は backend 非依存
generation と scoring を分離する。

Principle 2: row-level 出力を必須にする
overall accuracy だけ返す evaluator は禁止。

Principle 3: prompt / output / extraction を全部保存
原因追跡できない評価は無価値。

Principle 4: deterministic mode は再現可能であること
同じ config・同じ backend・同じ adapter で同一結果になること。

1-1-3. コア型定義

src/metric_fidelity/types.pypython
from dataclasses import dataclass
from typing import Literal, Optional

ExtractionSource = Literal[
    "boxed",
    "final_answer_is",
    "final_answer_colon",
    "last_number",
    "last_line",
    "not_found",
]

FormatBucket = Literal[
    "clean_boxed",
    "clean_final_answer",
    "boxed_multiple",
    "boxed_empty",
    "boxed_unclosed",
    "boxed_truncated_right_brace",
    "extra_trailing_numbers",
    "last_number_fallback",
    "last_line_fallback",
    "not_found",
]

Family = Literal[
    "bit_manipulation",
    "gravity_constant",
    "unit_conversion",
    "text_decryption",
    "roman_numeral",
    "symbol_equation",
]

AnswerType = Literal[
    "numeric",
    "binary8",
    "roman",
    "text_phrase",
    "symbolic",
]

@dataclass(frozen=True)
class PromptRecord:
    id: str
    prompt: str
    answer: Optional[str] = None
    family: Optional[Family] = None
    answer_type: Optional[AnswerType] = None

@dataclass(frozen=True)
class GenerationRecord:
    id: str
    sample_idx: int
    seed: int
    raw_output: str
    raw_output_len_chars: int
    raw_output_num_lines: int
    raw_output_est_tokens: int

@dataclass(frozen=True)
class EvalRow:
    id: str
    sample_idx: int
    seed: int
    family: str
    answer_type: str
    gold_answer: str
    raw_output: str
    extracted_answer: str
    extraction_source: ExtractionSource
    format_bucket: FormatBucket
    has_boxed: bool
    boxed_count: int
    contains_extra_numbers: bool
    contains_risky_chars: bool
    is_correct: bool
    rendered_prompt_hash: str
    eval_mode: str
    backend_name: str
1-1-4. backend abstraction

src/backends/protocol.pypython
from typing import Protocol, Sequence
from src.metric_fidelity.types import GenerationRecord

class GenerationBackend(Protocol):
    backend_name: str

    def generate(
        self,
        rendered_prompts: Sequence[str],
        *,
        max_tokens: int,
        top_p: float,
        temperature: float,
        max_model_len: int,
        seeds: Sequence[int],
    ) -> list[list[GenerationRecord]]:
        """
        Return shape:
            outputsprompt_index
        """
        ...
v1 で最低限実装する backend
1. ReplayBackend
   - 既存 raw outputs を読み直す
   - evaluator 単体テスト用

2. MLXBackend
   - Mac ローカル主力
   - deterministic / stochastic probe 用

3. HFBackend
   - 必要なら PEFT smoke / small local baseline 用
   - 実験の保険

v1 で未実装でもよい backend
- Kaggle remote backend 自動実行
- distributed backend
- multi-node backend

1-1-5. evaluator の責務

src/metric_fidelity/evaluator.py
責務は以下に限定する。

1. prompt dataframe を受け取る
2. competition prompt を build
3. backend に生成依頼
4. extract_final_answer() 実行
5. verify() 実行
6. format / risk annotation
7. row-level 出力保存
8. aggregate 出力保存

擬似コードpython
def evaluate_dataset(df, backend, eval_config, out_dir):
1. build rendered prompts
    rendered = [build_competition_prompt(tokenizer, p, eval_config) for p in df["prompt"]]

2. generate
    seeds = resolve_seeds(eval_config)
    generations = backend.generate(
        rendered,
        max_tokens=eval_config.max_tokens,
        top_p=eval_config.top_p,
        temperature=eval_config.temperature,
        max_model_len=eval_config.max_model_len,
        seeds=seeds,
    )

3. score each sample
    rows = []
    for item, samples, rendered_prompt in zip(df.itertuples(index=False), generations, rendered):
        for sample in samples:
            extracted, source = extract_final_answer_with_source(sample.raw_output)
            bucket = classify_format_bucket(sample.raw_output, extracted, source)
            is_correct = verify(str(item.answer), str(extracted))
            rows.append(make_eval_row(...))

4. save row-level
    save_parquet(rows, out_dir / "row_level.parquet")

5. aggregate
    summary = aggregate_eval_rows(rows)
    save_csv(summary, out_dir / "summary.csv")
    save_csv(family_metrics(rows), out_dir / "family_metrics.csv")
    save_csv(failure_metrics(rows), out_dir / "failure_metrics.csv")
1-1-6. format / failure annotation を evaluator に内蔵する

単に is_correct だけでは不十分。  
次を evaluator が自動で付ける。

自動付与列
- extraction_source
- format_bucket
- has_boxed
- boxed_count
- contains_extra_numbers
- contains_risky_chars
- raw_output_len_chars
- raw_output_num_lines
- raw_output_est_tokens
- rendered_prompt_hash

contains_risky_chars の定義
raw output ではなく、gold answer もしくは extracted answer の中に以下がある場合 true。

- }
- {
- \
- newline
- backtick

contains_extra_numbers の定義
最終 answer 抽出後、その後ろに別数値がある場合 true。  
例:text
\boxed{42}
confidence 0.91
→ 42 の後ろに数値があるので true

1-1-7. 保存フォーマットを固定する

summary.csv
- run_name
- backend_name
- eval_mode
- dataset_name
- n_rows
- n_samples_per_prompt
- overall_acc
- majority_acc  # multi-sample のみ
- pass_at_k     # multi-sample のみ
- extraction_fail_rate
- format_fail_rate
- boxed_rate
- avg_output_len_chars
- timestamp

family_metrics.csv
- run_name
- family
- n
- acc
- majority_acc
- pass_at_k
- extraction_fail_rate
- format_fail_rate
- boxed_rate
- avg_output_len_chars

failure_metrics.csv
- run_name
- format_bucket
- n
- ratio

row_level.parquet
必須。今後の hard mining・correction data・DPO 用の種データにもなる。

1-1-8. 日常運用コマンドを固定する

quick deterministicbash
python -m src.eval.run_eval \
  --input data/eval_packs/shadow_128.csv \
  --config conf/eval/official_lb.yaml \
  --backend mlx \
  --adapter-path outputs/adapters/current_best \
  --out outputs/eval/official_det_shadow128
serious deterministicbash
python -m src.eval.run_eval \
  --input data/eval_packs/shadow_256.csv \
  --config conf/eval/official_lb.yaml \
  --backend mlx \
  --adapter-path outputs/adapters/candidate_x \
  --out outputs/eval/official_det_shadow256_candidate_x
1-1-9. 完了条件

- [ ] backend abstraction 実装
- [ ] evaluator 実装
- [ ] row-level / summary / family / failure report 出力
- [ ] ReplayBackend で evaluator 単体テスト可能
- [ ] MLXBackend で official_det@1 実行可能
- [ ] deterministic 再実行で同一ハッシュ確認済み

1-2. extraction 危険ケースのテストベッドを作る

1-2-1. 目的

このコンペでは、正しい reasoning をしていても extraction 事故で落ちる。  
したがって extraction は evaluator の一部ではなく、独立した品質保証対象として扱う。

特に危険なのは次。

- } を含む答え
- \boxed{} の複数出現
- \boxed{} の未閉じ
- trailing numbers
- fallback 発火時の予期せぬ抽出
- text / symbol での last line fallback

1-2-2. 実装対象

src/metric_fidelity/extraction.py
次の関数を用意する。python
def extract_final_answer_with_source(text: str | None) -> tuple[str, str]:
    """
    Returns:
        extracted_answer, extraction_source
    """
python
def classify_format_bucket(
    raw_output: str | None,
    extracted_answer: str,
    extraction_source: str,
) -> str:
    """
    Returns one of FormatBucket
    """
python
def detect_extra_trailing_numbers(raw_output: str, extracted_answer: str) -> bool:
    ...
1-2-3. fixture 主導にする

data/processed/extraction_fixtures_v1.jsonl
1 行 1 ケースで保存する。json
{
  "case_id": "boxed_simple_numeric",
  "raw_output": "The answer is \\boxed{42}",
  "expected_extracted": "42",
  "expected_source": "boxed",
  "expected_bucket": "clean_boxed"
}
fixture の系統
最低でも以下 30 ケースは作る。

A. boxed 正常
1. simple numeric
2. simple roman
3. simple binary
4. simple text phrase
5. simple symbolic

B. boxed 複数
6. earlier boxed wrong, later boxed correct
7. earlier boxed correct, later boxed wrong
8. multiple boxed with empty entries

C. boxed 異常
9. empty boxed
10. unclosed boxed
11. whitespace boxed
12. nested-like malformed boxed
13. answer contains } and gets truncated
14. answer contains \
15. answer contains newline

D. final answer fallback
16. The final answer is: ...
17. Final answer is: ...
18. Final answer: ...
19. final answer: ...
20. full-width colon

E. last number fallback
21. reasoning only with final numeric
22. multiple numbers, last one should win
23. negative number
24. decimal number
25. answer correct but confidence after it corrupts extraction

F. last line fallback
26. no numbers, final plain text line
27. symbol-only final line
28. roman-only final line

G. null / empty
29. None
30. empty string

1-2-4. property-based fuzz test を追加する

fixture だけだと抜けるので、簡易 fuzz を入れる。

fuzz する対象
- answer 文字列に {, }, \, digits, spaces, backticks を混ぜる
- prefix / suffix にランダムな reasoning を足す
- \boxed{...} / Final answer: ... / plain line をランダム生成

目的
- extractor がクラッシュしない
- source / bucket が空にならない
- None / 異常文字でも落ちない

注意
fuzz は correctness 保証ではなく、ロバスト性保証。

1-2-5. boxed 事故の可視化を標準出力する

tests/test_extraction_risks.py
失敗時には単なる assert ではなく、

- raw_output
- expected_extracted
- actual_extracted
- expected_bucket
- actual_bucket

を出す。

実装ルール
fixture は human-readable に保つ。  
1 ケース 1 行 jsonl で diff しやすくする。

1-2-6. 解析補助関数も作る

analyze_extraction_risk(answer: str) -> dict
返すもの:

- boxed_safe  
- contains_right_brace
- contains_backslash
- contains_newline
- contains_backtick
- risk_reason

boxed_safe の定義
以下をすべて満たす場合のみ true
- } を含まない
- newline を含まない
- control char を含まない

これは後の format policy 学習で使う。

1-2-7. 完了条件

- [ ] extraction fixture 30 ケース以上
- [ ] fixture tests 全通過
- [ ] fuzz tests 全通過
- [ ] extract_final_answer_with_source() 実装済み
- [ ] classify_format_bucket() 実装済み
- [ ] analyze_extraction_risk() 実装済み

1-3. 3 系統 validation を deterministic に作る

1-3-1. 目的

public test は使えない。  
よって train 9500 件から、性質の違う 3 種類の validation を固定する。

狙いは 3 つ。

1. 通常の改善を測る
2. 難例で壊れていないか測る
3. 同型問題への過学習を測る

1-3-2. split の定義

Split A: cv5_strat_family
目的:
- 日常運用の主指標
- 過度な分布崩れなし
- family / answer_type を均等に監視

方式:
- 5-fold
- stratified
- shuffle=True
- fixed random state

strata:
- family
- answer_type
- risk_bin

risk_bin の定義
hard_score を family 内 percentile で 3 分割する。

- risk_low
- risk_mid
- risk_high

最終 strata:text
{family}{answer_type}{risk_bin}
rare strata は family のみへ backoff。

Split B: holdout_hard
目的:
- hardest 近傍での性能を測る
- hardening / format policy / synthetic 効果を見る

方式:
- family ごとに hard_score 上位 20% を test 側へ
- 残りから 5% を random 補充
- total 約 25% holdout を想定
- deterministic sort + seed sampling

最終的に各 family 約 350〜450 件程度になるよう調整する。

Split C: group_shift
目的:
- template 近傍 memorization を見抜く
- 同じ “規則族” の leakage を減らす

方式:
- family ごとに group_signature を作る
- GroupShuffleSplit(n_splits=3, test_size=0.2)
- split0/1/2 を保存

重要
group_signature は完全 solver である必要はない。  
coarse でも leakage を減らせれば価値がある。

1-3-3. hard_score を deterministic に作る

v1 では、モデル依存ではなく 構造ベース hard_score を使う。  
将来 v2 以降で model-based hardness を追加する。

hard_score 共通形python
hard_score = family_specific_score + generic_risk_bonus
generic_risk_bonus
- contains_right_brace: +2
- contains_backslash: +1
- prompt_len_chars family 内 p75 以上: +1
- answer_len family 内 extreme（下位10% or 上位10%）: +1

1-3-4. family 別 hard_score 規則

bit_manipulation
- query が 00000000, 11111111, 10101010, 01010101 のいずれか: +2
- example 数 >= 9: +1
- candidate op fit が複数に割れる: +2
- prompt_len_chars family 内 p90 以上: +1

gravity_constant
- query t が family 内端部 bin: +1
- 推定 g が edge bin (18): +1
- answer が 1 decimal: +2
- 丸め境界近傍（第3小数位が 4 or 5 or 6）: +1

unit_conversion
- 推定 ratio が edge bin (1.8): +1
- 丸め境界近傍: +2
- query 値が range edge: +1

roman_numeral
- query value が subtractive set に属する: +2
- query value が decade edge (39,40,41,89,90,91,99,100 等): +1

text_decryption
- answer 語数 = 5: +1
- answer char_len family 内 p80 以上: +1
- rare token を含む: +1
- unique char ratio 高い: +1
- token length pattern が稀: +1

symbol_equation
- answer に }, {, \, backtick: +2
- answer_len = 1 or 4: +1
- digits と symbols 混在: +1
- query charset rarity 高: +1

1-3-5. group_signature の作り方

bit_manipulation
group_signature = "{fit_family}__ex{num_examples}__qhw{query_hamming_bin}"

ここで fit_family は簡易 op fitting による。
候補:
- not
- xor_mask
- and_mask
- or_mask
- lshift
- rshift
- lrot
- rrot
- reverse
- nibble_swap
- multi_fit
- unknown

gravity_constant
group_signature = "gbin{g_bin}__dec{answer_decimal_style}"

unit_conversion
group_signature = "rbin{ratio_bin}__qbin{query_bin}"

roman_numeral
group_signature = "decade{value//10}__sub{has_subtractive}"

text_decryption
group_signature = "wc{word_count}__lensig{token_len_sig}__charpat{char_overlap_bin}"

symbol_equation
group_signature = "atype{numeric_or_symbolic}__alen{answer_len}__risk{risk_class}"

1-3-6. split 生成アルゴリズム

src/data/split_builder.py
実装順序は固定する。

Step 1
metadata を読み込む

Step 2
hard_score / risk_bin / group_signature を付与

Step 3
cv5_strat_family を作るpython
StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=20260316,
)
Step 4
holdout_hard を作る
- family ごと sort by
  - hard_score desc
  - prompt_hash asc
- top 20% を hard holdout
- 残りから seed=20260317 で 5% random

Step 5
group_shift を作る
family ごとにpython
GroupShuffleSplit(
    n_splits=3,
    test_size=0.2,
    random_state=20260318 + split_idx,
)
を回して結合

1-3-7. split integrity test

テスト項目
1. 9500 行すべていずれかの split に含まれる
2. cv5 は各 row がちょうど 1 fold の valid に属する
3. holdout_hard は family ごとに最低 15% 以上
4. group_shift は同一 group_signature が train/test に漏れない
5. family 分布差が許容範囲内
6. public overlap が smoke 以外に混ざってもフラグが保持されている

許容差
- cv fold 間の family 比率差: ±1.5% 以内
- holdout_hard の family 件数偏差: ±10% 以内

1-3-8. shadow pack も v1 で作る

shadow_128.csv
各 family を均等に近く、軽く回せる固定パック。

- 128 rows
- family stratified
- risk 混合
- public overlap 除外

shadow_256.csv
- 256 rows
- serious local compare 用

hard_shadow_256.csv
- holdout_hard から 256 rows
- risky chars / rounding / subtractive を厚め

運用
- 日次 quick compare: shadow_128
- serious candidate: shadow_256
- hardening 効果: hard_shadow_256

1-3-9. 完了条件

- [ ] cv5_strat_family 生成済み
- [ ] holdout_hard 生成済み
- [ ] group_shift 3 split 生成済み
- [ ] shadow_128, shadow_256, hard_shadow_256 生成済み
- [ ] split integrity tests 全通過

1-4. family classifier / parser を deterministic に作る

1-4-1. 目的

family classifier / parser は、v1 の中心部品。  
役割は 4 つある。

1. split stratification
2. hard_score 計算
3. group_signature 計算
4. 失敗分析・将来の synthetic generator 接続

v1 では ルールベース固定 で作る。  
LLM 判定は禁止。

1-4-2. parser の出力仕様

src/data/family_parser.py
必ず以下を返す。python
@dataclass(frozen=True)
class ParsedExample:
    inp: str
    out: str

@dataclass(frozen=True)
class ParsedPrompt:
    family: str
    subfamily: str
    answer_type: str
    parse_ok: bool
    confidence: float

    examples: list[ParsedExample]
    query_raw: str | None

family-specific features
    num_examples: int | None
    query_value_float: float | None
    estimated_g: float | None
    estimated_ratio: float | None
    roman_query_value: int | None
    bit_query_binary: str | None

generic
    prompt_len_chars: int
    prompt_len_words: int
    special_chars: str
    contains_right_brace: bool
    contains_backslash: bool
    contains_backtick: bool
1-4-3. family detection の順序を固定する

順序は重要。以下で固定する。

1. roman_numeral
判定条件例:
- roman numeral
- roman numerals
- convert to roman
- query / examples に典型 Roman outputs

2. gravity_constant
判定条件例:
- gravity
- fall
- d = 0.5
- distance fallen

3. bit_manipulation
判定条件例:
- 8-bit
- binary
- bit manipulation
- prompt 内の 8bit pattern 数 >= 4

4. text_decryption
判定条件例:
- decrypt
- decode
- cipher
- encoded text

5. unit_conversion
判定条件例:
- convert
- conversion
- units
- examples に float pair が並ぶ

6. symbol_equation
上記のどれでもない場合の fallback。  
ただし parse_ok/confidence を低めに付ける。

1-4-4. family 別 parse ロジック

bit_manipulation
extract
- re.findall(r"\b[01]{8}\b", prompt)
- line 単位にも split して example/query を推定

examples 推定
- 行ごとに 8bit が 2 個あるなら example pair 候補
- 最後の単独 8bit を query 候補
- fallback: binary list の最後を query、前を pair 化

追加特徴
- query_hamming_weight
- answer_hamming_weight
- num_examples
- fit_family（簡易 fitting）

gravity_constant
extract
- float 数値を line 単位抽出
- 2 数値ある行を (t, d) example 候補
- 最後の単独 t を query 候補

追加特徴
- estimated_g = 2d/(tt) の median
- answer_decimal_style
- query_t_bin

unit_conversion
extract
- line ごとに float ペア抽出
- query value を最後の単独 float で推定

追加特徴
- estimated_ratio = out/inp の median
- ratio_bin
- query_value_bin

roman_numeral
extract
- integer と Roman token を line 単位で抽出
- examples の int→roman ペア
- 最後の単独 int を query 候補

追加特徴
- roman_query_value
- has_subtractive = query_value in subtractive_set

text_decryption
extract
- line 単位で quoted phrase / token sequence を抜く
- answer があれば word count / char stats を付与
- query phrase は最後の unpaired phrase 候補

追加特徴
- word_count
- token_len_signature
- char_overlap_bin
- rare_token_flag

v1 では cipher を完全に当てる必要はない。  
まず 構造特徴が安定して取れれば十分。

symbol_equation
extract
- 非空行から短い symbol-rich line を候補抽出
- query は最後の unpaired short expression 候補
- answer_type は gold answer から補強してよい

追加特徴
- answer_len
- contains_digit
- contains_symbol
- risk_class
- charset_signature

1-4-5. count regression を必須テストにする

あなたの既知分析結果を regression test に使う。

expected counts
- bit_manipulation: 1602
- gravity_constant: 1597
- unit_conversion: 1594
- text_decryption: 1576
- roman_numeral: 1576
- symbol_equation: 1555

許容
- 完全一致を目標
- まずは ±5 以内
- それを超えたら parser 修正を優先

テスト
tests/test_family_count_regression.py

1-4-6. manual audit を最初にやる

ルールベース parser は、テスト通過だけでは危険。  
v1 で最初に 120 件を目視監査する。

監査サンプル
- 各 family 20 件
- hard 10 件 + normal 10 件
- public overlap 3 件含む

チェック項目
- family 正しいか
- query 抽出が妥当か
- examples 数が妥当か
- risk flag が妥当か
- parse confidence が妥当か

出力
outputs/audits/family_parser_manual_audit_v1.csv

1-4-7. metadata builder の仕様

src/data/metadata_builder.py
出力:
data/processed/train_metadata_v1.parquet

必須列:
- id
- prompt
- answer
- family
- subfamily
- answer_type
- parse_ok
- parse_confidence
- num_examples
- query_raw
- group_signature
- hard_score
- risk_bin
- prompt_len_chars
- prompt_len_words
- answer_len
- contains_right_brace
- contains_backslash
- contains_backtick
- is_public_test_overlap

1-4-8. 完了条件

- [ ] family parser 実装済み
- [ ] metadata builder 実装済み
- [ ] family count regression 通過
- [ ] manual audit 実施済み
- [ ] train_metadata_v1.parquet 生成済み

1-5. official deterministic 評価 + stochastic probe 評価の 2 軸を作る

1-5-1. 方針

v0 で official primary mode は固定した。  
したがって v1 では、評価を以下の 2 軸に分ける。

1-5-2. Axis A: official_det@1

役割
- 最重要
- 昇格判定
- 提出候補選定
- 実験比較の本線

設定
conf/eval/official_lb.yaml をそのまま使う。

- temperature=0.0
- top_p=1.0
- max_tokens=7680
- max_model_len=8192
- max_num_seqs=64

指標
- overall_acc
- family_acc
- holdout_hard_acc
- extraction_fail_rate
- format_fail_rate

利用ルール
- promotion rule はこの軸で決める
- 日次 quick compare もこの軸

1-5-3. Axis B: sc_probe@K

役割
これは submit 指標ではない。  
latent solvability と instability を測る診断軸。

目的
- モデルが答えを “知っている” のに greedy で出せていないか確認
- hard example mining
- RFT / distillation 用の正解候補収集
- majority / shortest-correct 解析
- correction pair 作成

設定
official と同じ文脈長制約を保ち、温度だけ上げる。

conf/eval/sc_probe_k8.yamlyaml
name: sc_probe_k8
max_lora_rank: 32
max_tokens: 7680
top_p: 1.0
temperature: 1.0
max_num_seqs: 32
gpu_memory_utilization: 0.85
max_model_len: 8192
enable_thinking: true
add_generation_prompt: true
n_samples_per_prompt: 8
seed_list: [1001,1002,1003,1004,1005,1006,1007,1008]
同様に k4, k16 も持つ。

理由
notebook default と混ぜると、
- temperature
- max_tokens
- max_model_len
が同時に変わってしまう。  
それだと latent solvability の診断軸としてノイズが増える。

したがって probe は、official 条件のまま温度だけ上げる。

1-5-4. sc_probe の評価指標

1 問あたり次を出す。

row-wise metrics
- pass_at_k
- majority_answer
- majority_correct
- consensus_rate
- n_unique_answers
- n_correct
- shortest_correct_len_chars
- best_format_correct_exists
- det_answer_in_probe_set  # greedy answer が probe 中に含まれるか

aggregate metrics
- pass@k
- majority_acc
- mean_consensus_rate
- mean_unique_answers
- format_safe_correct_rate
- shortest_correct_avg_len

1-5-5. 判定ロジック

ケース A
official_det@1 も改善、pass@8 も改善  
→ 強い改善。昇格候補。

ケース B
official_det@1 は横ばい、pass@8 だけ改善  
→ latent ability は上がっている。  
→ distillation / RFT の種として有望。提出候補ではない。

ケース C
official_det@1 は改善、pass@8 が悪化  
→ greedy 特化で brittle 化している可能性。  
→ hard holdout と failure bucket を確認してから採用。

ケース D
majority_acc は高いが consensus_rate が低い  
→ 正答知識はあるが不安定。  
→ format sharpening / correction / short-trace distillation の対象。

1-5-6. run_probe.py の仕様

コマンドbash
python -m src.eval.run_probe \
  --input data/eval_packs/shadow_128.csv \
  --config conf/eval/sc_probe_k8.yaml \
  --backend mlx \
  --adapter-path outputs/adapters/current_best \
  --out outputs/eval/sc_probe_shadow128_current_best
出力
- summary.csv
- family_metrics.csv
- probe_metrics.csv
- row_level.parquet
- sample_level.parquet  # 全サンプル保持

sample_level.parquet
- id
- sample_idx
- seed
- raw_output
- extracted_answer
- is_correct
- format_bucket
- raw_output_len_chars

1-5-7. 日次 / 夜間運用を固定する

日次 quick
- official_det@1 on shadow_128
- 実行時間短い
- current best vs candidate を比較

夜間 standard
- official_det@1 on shadow_256
- sc_probe@8 on shadow_128
- serious run は hard_shadow_256 も追加

週次 serious
- official_det@1 on all cv folds
- official_det@1 on holdout_hard
- sc_probe@8 on hard_shadow_256

1-5-8. deterministic / stochastic 再現性テスト

deterministic test
同一 config・同一 seed・同一 backend で 2 回実行し、
- extracted_answer hash
- raw_output hash
が一致することを確認

stochastic probe test
同一 seed list で 2 回実行し、
- sample_idx ごとの extracted_answer
- pass@k
- majority answer
が一致すること

1-5-9. 完了条件

- [ ] official_det@1 実行可能
- [ ] sc_probe@4, @8, @16 実行可能
- [ ] row / sample / aggregate 出力整備済み
- [ ] deterministic reproducibility test 通過
- [ ] stochastic fixed-seed reproducibility test 通過

3. 実装順序

順序は固定。崩さない。

Step 1
types.py, evaluator.py, ReplayBackend を実装  
→ evaluator の単体動作を作る

Step 2
extraction.py, annotate.py, extraction fixtures, tests を実装  
→ extraction 品質を確定する

Step 3
family_parser.py, metadata_builder.py を実装  
→ metadata を作る

Step 4
split_builder.py, shadow_pack_builder.py を実装  
→ split と eval pack を固定する

Step 5
MLXBackend を evaluator に接続  
→ official_det@1 を回す

Step 6
run_probe.py, sc_probe configs を実装  
→ probe 指標を回す

Step 7
manual audit / count regression / split integrity / determinism tests を通す

4. 直ちに実行するコマンドbash
python scripts/build_metadata.py \
  --input data/raw/train.csv \
  --output data/processed/train_metadata_v1.parquet

python scripts/build_splits.py \
  --input data/processed/train_metadata_v1.parquet \
  --output data/processed/train_splits_v1.parquet

python scripts/build_shadow_packs.py \
  --input data/processed/train_splits_v1.parquet \
  --outdir data/eval_packs

pytest tests/test_extraction_risks.py \
       tests/test_family_parser.py \
       tests/test_family_count_regression.py \
       tests/test_split_builder.py \
       tests/test_eval_determinism.py \
       tests/test_probe_metrics.py -q

python -m src.eval.run_eval \
  --input data/eval_packs/shadow_128.csv \
  --config conf/eval/official_lb.yaml \
  --backend mlx \
  --adapter-path outputs/adapters/baseline \
  --out outputs/eval/baseline_shadow128_official

python -m src.eval.run_probe \
  --input data/eval_packs/shadow_128.csv \
  --config conf/eval/sc_probe_k8.yaml \
  --backend mlx \
  --adapter-path outputs/adapters/baseline \
  --out outputs/eval/baseline_shadow128_probe8
5. v1 完了後に固定されること

v1 が終わると、今後の全実験で以下が固定される。

1. 評価は必ず row-level まで保存する
2. extraction 事故は独立に数える
3. validation は cv / hard / group_shift の 3 面で見る
4. family / answer_type / risk を metadata として持つ
5. official greedy 指標と stochastic probe 指標を分ける
6. parser と split は deterministic で再生成可能
7. hard mining や correction data の元データが自動蓄積される

6. v1 の次に行く条件

以下を全部満たしたら v2 に進む。

- [ ] evaluator が official_det@1 で安定稼働
- [ ] extraction suite が安定
- [ ] parser count regression が通る
- [ ] split integrity が通る
- [ ] probe 指標が出せる
- [ ] baseline no-adapter / minimal adapter の結果が保存済み

v2 では、これを土台に
- sibling synthetic
- distilled traces
- baseline LoRA 比較
へ進む。

補足だけ短く。

この v1 の核心
今回の v1 の本質は、単に「評価コードを書く」ことではない。  
あとで synthetic / RFT / DPO にそのまま接続できる観測基盤を作ること。

なので特に重要なのはこの 4 つ。

- row_level.parquet を必須にすること
- format_bucket / extraction_source を標準列にすること
- hard_score と group_signature を metadata に入れること
- official_det@1 と sc_probe@K を明確に分けること

必要なら次にそのまま続けて、

1. family_parser.py の具体仕様
2. split_builder.py の具体仕様
3. run_eval.py / run_probe.py の CLI と内部処理
4. テストコードの雛形

まで、そのまま実装可能な粒度で落とせる。
