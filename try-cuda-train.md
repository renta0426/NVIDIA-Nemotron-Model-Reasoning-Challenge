ここではbaseline/nvidia-nemotron-sfttrainer-training.ipynbを大幅に改善する実装を考える。

baseline/nvidia-nemotron-sfttrainer-training.ipynbの結果を見る限り、**前回の改善は「学習の形」は少し良くなったが、スコアを動かす本丸には届いていない**です。  
LBスコア0.75–0.8 を狙うなら、LoRA の細かい設定より前に、**何を教師信号としてモデルに入れるか**を変える必要があります。

---

# まず、なぜほとんど効かなかったのか

ログからボトルネックはかなり明確です。

## 1. supervised tokens が少なすぎる
前回ログ:

- `tokenized samples: 3300`
- `total supervised tokens: 43,739`
- trainable params: `434,659,328`

つまり、**4.35億個の学習パラメータに対して、正味の教師トークンが 4.3 万しかない**。  
ざっくり言うと、

- **1 supervised token / 約 9,900 trainable params**

です。

これは、30B級モデルの reasoning 挙動を動かすには弱すぎます。  
前回の学習は「boxed answer のフォーマット」を少し寄せる効果はあっても、  
**“例から規則を推論して答えを出し切る” 能力を変えるには信号が薄すぎる**です。

---

## 2. 実際に失敗しているのは「考え始めるが終われない」こと
あなたの smoke test 出力:

- `We need to infer transformation rule...`
- `Let's map each word...`
- `Next`

となっていて、**思考開始までは行くが、最終 boxed answer まで収束していない**。

つまり弱点は:

- reasoning を始める能力が無い  
ではなく
- **thinking mode の中で、規則を確定→適用→boxed answer で終了する軌道**が学習されていない

です。

metric は `enable_thinking=True` で prompt を作っています。  
なので train でも、**thinking mode における正しい出力構造**を教えないと、  
ベースモデルの「長く考え始める癖」だけが出て終わります。

---

## 3. このコンペは「答えだけ学習」では伸びにくい
このデータは 6 family に分かれていますが、どれも本質は

- prompt 内の few-shot 例から
- 暗黙ルールを同定し
- 1回適用する

タスクです。

なので、必要なのは単なる answer imitation ではなく、  
**“この family ではどう規則を復元し、どう適用するか” の中間表現**です。

つまり必要なのは:

- ただの SFT ではなく
- **verified teacher trace の distillation**

です。

---

# 0.75–0.8 を狙うために足りないもの

結論だけ言うと、足りないのは次の 3 つです。

## A. verified reasoning trace
答えだけではなく、

- どう規則を見つけたか
- どう target に適用したか
- どう boxed answer で終えるか

を、**正解付きで**入れる必要があります。

---

## B. family ごとの solver / teacher
このデータは family がはっきり分かれています。

- binary
- gravity
- unit
- roman
- text
- symbol

全部を素の LoRA に学ばせるより、  
**family ごとに programmatic teacher を作って、その思考を蒸留する**方が圧倒的に強いです。

重要なのは、**提出時に solver を使うわけではない**ことです。  
solver はあくまで **train 用の教師生成器** です。

---

## C. thinking mode の終了形式を学習させる
train の assistant 出力を

```text
<think>
...
</think>
\boxed{answer}
```

に統一します。

これで inference 側の `enable_thinking=True` と整合します。  
前回はここがズレていて、  
**“考え始めるが boxed に着地しない”** という失敗がそのまま出ています。

---

# 提案する本命アプローチ

今回は、単なる answer-only SFT をやめて、  
**solver-distilled CoT LoRA** にします。

流れはこうです。

---

## 学習戦略

### 1. train 各サンプルに対して family を分類

### 2. family ごとの lightweight solver を走らせる
例えば:

- **unit**: 例から `y = ax` or `y = ax + b` を推定
- **gravity**: 例から `y = a * sqrt(x)` を推定
- **roman**: 最後の整数を Roman に変換
- **text**: 例の encoded→decoded から文字置換を復元
- **binary**: bit op ライブラリから合う変換を探索
- **symbol**: 文字置換 or 整数の一次変換を探索

### 3. solver が ground truth と一致したサンプルだけ
**高品質 rationale** を生成して teacher trace 化

例:

```text
<think>
The examples fit this rule: reverse the 8 bits, then flip every bit.
Applying it to 01010110 gives 01101010.
</think>
\boxed{01101010}
```

### 4. solver が失敗したものは fallback で answer-only
つまり dataset を

- 高品質 trace 付きデータ
- box 着地だけ教える短いデータ

の mixture にする。

---

# この方式が前回より本質的に強い理由

前回との差は「パラメータ」ではなく「教師信号」です。

## 前回
- supervised tokens ≈ 43k
- 内容はほぼ answer のみ
- thinking mode における着地を教えていない

## 今回
- supervised tokens を数倍に増やせる
- reasoning path を直接蒸留
- `</think>\n\boxed{}` の終了形式を学習
- family ごとの algorithm induction を明示

つまりこれは、  
**LoRA の微調整**ではなく、  
**“ベースモデルの思考軌道を hidden test 分布に合わせて再配線する”** 変更です。

---

# 実装方針
以下の notebook は次を全部含みます。

1. family 分類  
2. verified solver 実装  
3. teacher trace 生成  
4. training set 構築  
5. LoRA 学習  
6. zip 化

---
 
前回の結果を見ると、**「LoRAの当て方」ではなく「教師信号の質」が足りない**です。  
このコンペで 0.75–0.8 を狙うなら、**答えだけを覚えさせる SFT** では足りず、**各 family の規則復元を“検証済み teacher trace”として蒸留**する必要があります。

---

# 再考察: 0.8 はこの方針で可能か

## 結論
**可能性はある**です。  
ただし前提があります。

- hidden test が、train で見えている **6 family の同分布拡張**であること
- family ごとの **programmatic solver** で十分な割合を train 上で再現できること
- LoRA には **「think して boxed で着地する軌道」** を学ばせること

前回ほぼ伸びなかった理由は明確で、

1. **answer-only に近く、教師トークンが薄すぎた**
2. **thinking mode の終了を教えていなかった**
3. **family ごとの規則復元を学習させていなかった**

からです。

なので今回は、  
**verified solver → short CoT teacher trace → completion-only LoRA**  
に変えます。

---

# 方針の根拠

train の特徴はすでにかなりはっきりしています。

- 9500件
- 6 family がほぼ均等
- 各 family は「few-shot 例から規則を復元して1回適用する」型
- metric は `enable_thinking=True` + `\boxed{}` 抽出
- hidden test は数百問規模

この条件だと、強い方法は大きく2つしかありません。

### 1. 直接 solver を提出時に使う
→ **不可**。提出は LoRA のみ。

### 2. solver の挙動を LoRA に蒸留する
→ **可**。これが本筋。

つまり、train の答えを使って  
**「その問題では実際にどう解いたか」**を programmatic に再構成し、  
それを teacher として学習させるのが最も理にかなっています。

---

# 今回の実装の要点

## 変更点
- **family classifier** を作る
- **family ごとの solver** を作る
  - roman: 厳密変換
  - unit: affine / scale rule 推定
  - gravity: sqrt/linear rule 推定
  - text: 文字置換復元
  - binary: bit permutation + inversion / bit-op DSL
  - symbol: 一部のみ solver、残りは terse supervision
- **solver が正答を再現したサンプルだけ** verbose trace を付ける
- 失敗例は **短い boxed supervision**
- 学習は **completion-only**
- train は **短くて高品質な 700–1000 件程度**
- thinking prefix に合わせて、assistant completion を  
  `... </think>\n\boxed{...}`  
  で統一

---

# 重要な期待値の置き方
正直に言うと、**0.8 を“保証”はできません**。  
一番大きい不確実性は **binary / symbol family の hidden 分布が train の想定 DSL にどこまで乗るか** です。

ただし、**0.64–0.68 から 0.75+ を狙う筋道**としては、  
これがかなり本命です。  
少なくとも、前回の「answer-only に近い薄い SFT」よりずっと根拠があります。

---

# 実装コード
以下は **Kaggle notebook でそのまま上から順に実行**できる形で書いています。  
途中で solver coverage を見て、必要なら quota だけ調整できます。

---

## Cell 1: Setup / imports / environment fix

```python
import os
import re
import gc
import sys
import stat
import math
import time
import json
import random
import shutil
import zipfile
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset

import kagglehub
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType

# -------------------------
# Reproducibility
# -------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# -------------------------
# Triton / Nemotron fixes
# -------------------------
def _pure_rmsnorm_fn(x, weight, bias=None, z=None, eps=1e-5,
                     group_size=None, norm_before_gate=True, upcast=True):
    dtype = x.dtype
    if upcast:
        x = x.float()
    variance = x.pow(2).mean(-1, keepdim=True)
    x_normed = x * torch.rsqrt(variance + eps)
    out = x_normed * weight.float()
    if bias is not None:
        out = out + bias.float()
    if z is not None:
        out = out * F.silu(z.float())
    return out.to(dtype)

for _, mod in list(sys.modules.items()):
    if hasattr(mod, "rmsnorm_fn"):
        mod.rmsnorm_fn = _pure_rmsnorm_fn

src = "/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell"
dst = "/tmp/ptxas-blackwell"
if os.path.exists(src):
    shutil.copy2(src, dst)
    os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    import triton.backends.nvidia as nv_backend
    src_bin = os.path.join(os.path.dirname(nv_backend.__file__), "bin")
    dst_bin = "/tmp/triton_nvidia_bin"
    shutil.copytree(src_bin, dst_bin, dirs_exist_ok=True)

    for f in os.listdir(dst_bin):
        fp = os.path.join(dst_bin, f)
        if os.path.isfile(fp):
            os.chmod(fp, os.stat(fp).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    nv_backend.__file__ = os.path.join(dst_bin, "..", "__init__.py")
    os.environ["TRITON_PTXAS_PATH"] = dst
    os.environ["TRITON_PTXAS_BLACKWELL_PATH"] = dst

try:
    import triton.backends.nvidia.compiler as nv_compiler
    nv_compiler.get_ptxas_version = lambda arch: "12.0"
except Exception as e:
    print("compiler patch skipped:", e)

print("Setup done.")
```

---

## Cell 2: Paths / hyperparameters

```python
MODEL_PATH = kagglehub.model_download(
    "metric/nemotron-3-nano-30b-a3b-bf16/transformers/default"
)

TRAIN_PATH = "/kaggle/input/nvidia-nemotron-3-reasoning-challenge/train.csv"
TEST_PATH = "/kaggle/input/nvidia-nemotron-3-reasoning-challenge/test.csv"

OUTPUT_DIR = "/kaggle/working/adapter"
ZIP_PATH = "/kaggle/working/submission.zip"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Metric と一致
EVAL_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)

# Training budget
PACK_LEN = 384
PER_DEVICE_BATCH = 1
GRAD_ACCUM = 8
NUM_EPOCHS = 1
LR = 1.2e-4
MAX_GRAD_NORM = 1.0

# LoRA
LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.03

# solved trace を優先
SOLVED_QUOTAS = {
    "roman": 180,
    "unit": 180,
    "gravity": 180,
    "binary": 160,
    "text": 130,
    "symbol": 70,
}

# unsolved / hard は terse supervision
TERSE_QUOTAS = {
    "roman": 15,
    "unit": 15,
    "gravity": 15,
    "binary": 20,
    "text": 30,
    "symbol": 60,
}

print("MODEL_PATH:", MODEL_PATH)
print("OUTPUT_DIR:", OUTPUT_DIR)
```

---

## Cell 3: Load data / tokenizer / family classification

```python
train_df = pd.read_csv(TRAIN_PATH)
print("train rows:", len(train_df))
display(train_df.head(2))
```

```python
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

BINARY_ANS_RE = re.compile(r"^[01]{8}$")
ROMAN_ANS_RE = re.compile(r"^[IVXLCDM]+$")
NUMERIC_RE = re.compile(r"^-?\d+(?:\.\d+)?$")

def classify_family(prompt: str, answer: str) -> str:
    p = str(prompt).lower()
    a = str(answer).strip()

    if BINARY_ANS_RE.fullmatch(a):
        return "binary"
    if " " in a:
        return "text"
    if ROMAN_ANS_RE.fullmatch(a):
        return "roman"

    if ("gravity" in p) or ("gravitational" in p) or ("fall time" in p) or ("falls" in p) or ("dropped" in p):
        return "gravity"

    if ("unit conversion" in p) or ("measurement" in p) or ("convert the following measurement" in p):
        return "unit"

    if ("decode" in p) or ("decrypt" in p) or ("cipher" in p) or ("encoded" in p) or ("secret message" in p):
        return "text"

    return "symbol"

train_df["family"] = [
    classify_family(p, a) for p, a in zip(train_df["prompt"], train_df["answer"])
]

print(train_df["family"].value_counts())
```

---

## Cell 4: Common utilities

```python
def normalize_answer(x: str) -> str:
    return str(x).strip()

def verify_answer(gt: str, pred: str) -> bool:
    gt = normalize_answer(gt)
    pred = normalize_answer(pred)
    try:
        a = float(gt)
        b = float(pred)
        return math.isclose(a, b, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return gt.lower() == pred.lower()

def safe_float(x: str) -> Optional[float]:
    try:
        return float(str(x).strip())
    except Exception:
        return None

def decimals_in_str(x: str) -> int:
    x = str(x).strip()
    if "." in x:
        return len(x.split(".")[-1])
    return 0

def format_float(x: float, decimals: int) -> str:
    return f"{x:.{decimals}f}"

def median_decimals(values: List[str], default: int = 2) -> int:
    ds = [decimals_in_str(v) for v in values if re.search(r"\d", str(v))]
    if not ds:
        return default
    ds = sorted(ds)
    return ds[len(ds) // 2]

def clean_token(x: str) -> str:
    x = str(x).strip()
    x = x.strip("`\"' ")
    return x

def safe_apply_chat_template(messages, add_generation_prompt=True):
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=True,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
        )
    except Exception:
        text = ""
        for m in messages:
            text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
        if add_generation_prompt:
            text += "<|im_start|>assistant\n"
        return text

def build_prompt_text(prompt: str) -> str:
    user_content = str(prompt) + EVAL_SUFFIX
    return safe_apply_chat_template(
        [{"role": "user", "content": user_content}],
        add_generation_prompt=True
    )

def build_completion(answer: str, rationale: Optional[str]) -> str:
    ans = str(answer).strip()
    rationale = (rationale or "").strip()

    # chat template が <think> まで入れているケースに合わせる
    if rationale:
        body = rationale
    else:
        body = "Apply the rule from the examples to the target."

    # completion は think の中身 + close + boxed
    return body + "\n</think>\n\\boxed{" + ans + "}"

def common_prefix_len(a: List[int], b: List[int]) -> int:
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def tokenize_completion_only(prompt: str, answer: str, rationale: Optional[str]):
    prompt_text = build_prompt_text(prompt)
    # prompt_text の末尾が <think> でない fallback も考慮
    if "<think>" not in prompt_text[-80:]:
        full_text = prompt_text + "<think>\n" + build_completion(answer, rationale)
    else:
        full_text = prompt_text + build_completion(answer, rationale)

    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]

    prefix_len = common_prefix_len(prompt_ids, full_ids)

    input_ids = list(full_ids)
    if len(input_ids) == 0 or input_ids[-1] != tokenizer.eos_token_id:
        input_ids.append(tokenizer.eos_token_id)

    labels = input_ids.copy()
    for i in range(min(prefix_len, len(labels))):
        labels[i] = -100

    if all(x == -100 for x in labels):
        labels[-1] = tokenizer.eos_token_id

    return {"input_ids": input_ids, "labels": labels}
```

---

## Cell 5: Parsing helpers

```python
QUOTE_PAIR_RE = re.compile(r'(["\'])(.*?)\1\s*(?:->|becomes)\s*(["\'])(.*?)\3', re.IGNORECASE)
BINARY_PAIR_RE = re.compile(r'([01]{8})\s*(?:->|becomes)\s*([01]{8})', re.IGNORECASE)
NUM_ARROW_RE = re.compile(r'(-?\d+(?:\.\d+)?)\s*(?:[A-Za-z%°/]+)?\s*(?:->|becomes)\s*(-?\d+(?:\.\d+)?)', re.IGNORECASE)
NUM_WITH_UNIT_RE = re.compile(r'(-?\d+(?:\.\d+)?)\s*([A-Za-z%°/]+)')
ROMAN_PAIR_RE = re.compile(r'(\d+)\s*(?:->|becomes)\s*([IVXLCDM]+)', re.IGNORECASE)

def extract_quoted_pairs(prompt: str) -> List[Tuple[str, str]]:
    pairs = []
    for m in QUOTE_PAIR_RE.finditer(prompt):
        lhs = m.group(2)
        rhs = m.group(4)
        pairs.append((lhs, rhs))
    return pairs

def extract_all_quoted(prompt: str) -> List[str]:
    out = []
    for m in re.finditer(r'(["\'])(.*?)\1', prompt):
        out.append(m.group(2))
    return out

def extract_binary_examples_target(prompt: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    pairs = [(a, b) for a, b in BINARY_PAIR_RE.findall(prompt)]
    all_bins = re.findall(r'[01]{8}', prompt)
    target = all_bins[-1] if all_bins else None
    return pairs, target

def extract_numeric_examples(prompt: str) -> List[Tuple[float, float]]:
    pairs = []
    for a, b in NUM_ARROW_RE.findall(prompt):
        fa, fb = safe_float(a), safe_float(b)
        if fa is not None and fb is not None:
            pairs.append((fa, fb))
    return pairs

def extract_last_number(prompt: str) -> Optional[float]:
    nums = re.findall(r'-?\d+(?:\.\d+)?', prompt)
    if not nums:
        return None
    return safe_float(nums[-1])

def extract_last_lhs_with_most_common_unit(prompt: str) -> Optional[float]:
    matches = NUM_WITH_UNIT_RE.findall(prompt)
    if not matches:
        return extract_last_number(prompt)
    units = [u for _, u in matches]
    if not units:
        return extract_last_number(prompt)
    unit = max(set(units), key=units.count)
    vals = [safe_float(v) for v, u in matches if u == unit]
    vals = [v for v in vals if v is not None]
    return vals[-1] if vals else extract_last_number(prompt)

def extract_generic_line_pairs(prompt: str) -> List[Tuple[str, str]]:
    pairs = []
    for line in prompt.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.search(r'(.+?)\s*(?:->|becomes)\s*(.+)$', line, flags=re.IGNORECASE)
        if not m:
            continue
        lhs = clean_token(m.group(1))
        rhs = clean_token(m.group(2))
        if len(lhs) <= 64 and len(rhs) <= 64:
            pairs.append((lhs, rhs))
    return pairs

def extract_generic_short_targets(prompt: str) -> List[str]:
    out = []
    quoted = extract_all_quoted(prompt)
    out.extend(quoted)
    for tok in re.findall(r'[@#\$%\^\&\*\+\-=/\\\|\(\)\[\]\{\}:;,.<>!?~_A-Za-z0-9]+', prompt):
        if 1 <= len(tok) <= 32:
            out.append(tok)
    return out
```

---

## Cell 6: Numeric-rule solvers (unit / gravity)

```python
def fit_linear_basis(xs: List[float], ys: List[float], basis_fns, basis_name: str):
    A = np.array([[fn(x) for fn in basis_fns] for x in xs], dtype=np.float64)
    y = np.array(ys, dtype=np.float64)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    max_err = float(np.max(np.abs(pred - y)))
    return coef, max_err, basis_name

def eval_linear_basis(x: float, coef, basis_fns):
    row = np.array([fn(x) for fn in basis_fns], dtype=np.float64)
    return float(row @ coef)

def solve_numeric_family(prompt: str, answer: str, family: str):
    pairs = extract_numeric_examples(prompt)
    if len(pairs) < 2:
        return None

    xs = [a for a, _ in pairs]
    ys = [b for _, b in pairs]
    target_x = extract_last_lhs_with_most_common_unit(prompt)
    if target_x is None:
        target_x = extract_last_number(prompt)
    if target_x is None:
        return None

    if family == "gravity":
        candidates = [
            ("y = a*sqrt(x)", [lambda x: math.sqrt(max(x, 0.0))]),
            ("y = a*sqrt(x) + b", [lambda x: math.sqrt(max(x, 0.0)), lambda x: 1.0]),
            ("y = a*x + b", [lambda x: x, lambda x: 1.0]),
            ("y = a*x", [lambda x: x]),
        ]
    else:  # unit
        candidates = [
            ("y = a*x + b", [lambda x: x, lambda x: 1.0]),
            ("y = a*x", [lambda x: x]),
            ("y = x + b", [lambda x: 1.0]),  # handled separately below
        ]

    ans_dec = max(decimals_in_str(answer), median_decimals([str(y) for y in ys], default=2))

    # special-case y = x + b
    if family == "unit":
        diffs = [y - x for x, y in pairs]
        if max(abs(d - diffs[0]) for d in diffs) < 1e-6:
            pred = target_x + diffs[0]
            pred_s = format_float(pred, ans_dec)
            if verify_answer(answer, pred_s):
                rationale = (
                    f"The examples show a constant offset: output = input + {diffs[0]:.6g}. "
                    f"Applying it to {target_x:.6g} gives {pred_s}."
                )
                return pred_s, rationale

    best = None
    for name, basis in candidates:
        try:
            coef, max_err, _ = fit_linear_basis(xs, ys, basis, name)
            pred = eval_linear_basis(target_x, coef, basis)
            pred_s = format_float(pred, ans_dec)
            if verify_answer(answer, pred_s):
                best = (pred_s, name, coef, max_err)
                break
        except Exception:
            pass

    if best is None:
        return None

    pred_s, name, coef, max_err = best
    coef_txt = ", ".join(f"{c:.6g}" for c in np.array(coef).tolist())
    rationale = (
        f"The examples fit the rule {name}. "
        f"Estimated coefficients: [{coef_txt}]. "
        f"Applying the same rule to the target gives {pred_s}."
    )
    return pred_s, rationale
```
---

## Cell 7: Roman solver

```python
def int_to_roman(n: int) -> str:
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = []
    for v, sym in vals:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)

def solve_roman(prompt: str, answer: str):
    nums = re.findall(r'\d+', prompt)
    if not nums:
        return None

    target = int(nums[-1])
    pred = int_to_roman(target)

    if not verify_answer(answer, pred):
        return None

    rationale = (
        f"This is standard Roman numeral conversion. "
        f"Convert {target} using subtractive notation to get {pred}."
    )
    return pred, rationale, "roman_standard"
```

---

## Cell 8: Text substitution solver

```python
def build_char_map_from_pairs(pairs: List[Tuple[str, str]]) -> Optional[Dict[str, str]]:
    mapping = {}
    reverse_mapping = {}

    for src, tgt in pairs:
        if len(src) != len(tgt):
            return None

        for s, t in zip(src, tgt):
            if s in mapping and mapping[s] != t:
                return None
            mapping[s] = t

            # space は多対一でも壊さない
            if s != " " and t != " ":
                if t in reverse_mapping and reverse_mapping[t] != s:
                    return None
                reverse_mapping[t] = s

    return mapping

def decode_with_char_map(text: str, mapping: Dict[str, str]) -> Optional[str]:
    out = []
    for ch in text:
        if ch in mapping:
            out.append(mapping[ch])
        elif ch in " .,;:!?'-()[]{}":
            out.append(ch)
        else:
            # 未知文字が英字なら失敗扱い
            if ch.isalpha():
                return None
            out.append(ch)
    return "".join(out)

def choose_text_target(prompt: str, pairs: List[Tuple[str, str]]) -> Optional[str]:
    quoted = extract_all_quoted(prompt)
    if quoted:
        # 典型的には example pairs + 最後に target quoted string
        if len(quoted) >= 2 * len(pairs) + 1:
            return quoted[-1]

        rhs_set = set(b for _, b in pairs)
        candidates = [q for q in quoted if q not in rhs_set]
        if candidates:
            return candidates[-1]
        return quoted[-1]

    # fallback: 最後の非矢印 line
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    for line in reversed(lines):
        if ("->" in line) or ("becomes" in line.lower()):
            continue
        m = re.search(r'["\'](.+?)["\']', line)
        if m:
            return m.group(1).strip()
        if ":" in line:
            cand = clean_token(line.split(":")[-1])
            if 1 <= len(cand) <= 128:
                return cand
    return None

def solve_text_substitution(prompt: str, answer: str):
    pairs = extract_quoted_pairs(prompt)
    if len(pairs) < 2:
        return None

    mapping = build_char_map_from_pairs(pairs)
    if mapping is None:
        return None

    target = choose_text_target(prompt, pairs)
    if not target:
        return None

    pred = decode_with_char_map(target, mapping)
    if pred is None:
        return None

    if not verify_answer(answer, pred):
        return None

    mapped_chars = sum(1 for k in mapping if k.isalpha())
    rationale = (
        f"The examples define a character-by-character substitution cipher. "
        f"Using the recovered mapping ({mapped_chars} letter mappings), "
        f"decoding the target phrase gives {pred!r}."
    )
    return pred, rationale, "text_char_substitution"
```

---

## Cell 9: Binary solver  
**8-bit permutation + optional per-bit inversion** を厳密に探索します。  
これは「bit manipulation」family に対して前回よりかなり本質的に強い部分です。

```python
def _bitstr_to_vec(s: str) -> List[int]:
    return [int(c) for c in s.strip()]

def _vec_to_bitstr(v: List[int]) -> str:
    return "".join(str(int(x)) for x in v)

def fit_binary_permutation_with_inversion(
    pairs: List[Tuple[str, str]]
) -> Optional[List[Tuple[str, int, int]]]:
    """
    各 output bit j が
      - input bit i
      - or NOT input bit i
      - or constant 0/1
    のいずれかで説明できるかを探索する。
    返り値:
      list of length 8
      each item is:
        ("input", i, flip) or ("const", bit, 0)
    """
    if len(pairs) < 2:
        return None

    X = [_bitstr_to_vec(a) for a, _ in pairs]
    Y = [_bitstr_to_vec(b) for _, b in pairs]

    if not all(len(x) == 8 for x in X) or not all(len(y) == 8 for y in Y):
        return None

    candidates = {j: [] for j in range(8)}

    for j in range(8):
        ycol = [y[j] for y in Y]

        # constant 0 / 1
        if all(v == 0 for v in ycol):
            candidates[j].append(("const", 0, 0))
        if all(v == 1 for v in ycol):
            candidates[j].append(("const", 1, 0))

        # input bit or flipped input bit
        for i in range(8):
            xcol = [x[i] for x in X]

            if all(yv == xv for xv, yv in zip(xcol, ycol)):
                candidates[j].append(("input", i, 0))

            if all(yv == (1 - xv) for xv, yv in zip(xcol, ycol)):
                candidates[j].append(("input", i, 1))

        if len(candidates[j]) == 0:
            return None

    # real input bits は重複使用しない permutation を優先
    order = sorted(range(8), key=lambda j: len(candidates[j]))

    def dfs(idx: int, used_inputs: set, assign: Dict[int, Tuple[str, int, int]]):
        if idx == len(order):
            out = [None] * 8
            for j, spec in assign.items():
                out[j] = spec
            return out

        j = order[idx]
        for spec in candidates[j]:
            kind, val, flip = spec

            if kind == "input":
                if val in used_inputs:
                    continue
                used_inputs.add(val)
                assign[j] = spec
                res = dfs(idx + 1, used_inputs, assign)
                if res is not None:
                    return res
                used_inputs.remove(val)
                assign.pop(j, None)
            else:
                assign[j] = spec
                res = dfs(idx + 1, used_inputs, assign)
                if res is not None:
                    return res
                assign.pop(j, None)

        return None

    return dfs(0, set(), {})

def apply_binary_spec(target: str, spec: List[Tuple[str, int, int]]) -> str:
    x = _bitstr_to_vec(target)
    out = []
    for kind, val, flip in spec:
        if kind == "const":
            bit = val
        else:
            bit = x[val]
            if flip:
                bit = 1 - bit
        out.append(bit)
    return _vec_to_bitstr(out)

def describe_binary_spec(spec: List[Tuple[str, int, int]]) -> str:
    pieces = []
    for j, (kind, val, flip) in enumerate(spec, start=1):
        if kind == "const":
            pieces.append(f"o{j}={val}")
        else:
            src = f"i{val+1}"
            if flip:
                src = f"NOT({src})"
            pieces.append(f"o{j}={src}")
    return ", ".join(pieces)

def solve_binary(prompt: str, answer: str):
    pairs, target = extract_binary_examples_target(prompt)
    if len(pairs) < 3 or target is None:
        return None

    spec = fit_binary_permutation_with_inversion(pairs)
    if spec is None:
        return None

    pred = apply_binary_spec(target, spec)
    if not verify_answer(answer, pred):
        return None

    desc = describe_binary_spec(spec)
    rationale = (
        f"Each output bit is determined independently from one input bit "
        f"(possibly flipped). The recovered bit mapping is: {desc}. "
        f"Applying this mapping to {target} gives {pred}."
    )
    return pred, rationale, "binary_bit_permutation_inversion"
```

---

## Cell 10: Symbol solver  
`symbol` は hardest family なので、**狙い撃ちで解けるものだけ取る**方針です。

```python
def extract_last_nonexample_candidate(prompt: str) -> Optional[str]:
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    for line in reversed(lines):
        if ("->" in line) or ("becomes" in line.lower()):
            continue

        m = re.search(r'["\'](.+?)["\']', line)
        if m:
            cand = clean_token(m.group(1))
            if cand:
                return cand

        if ":" in line:
            cand = clean_token(line.split(":")[-1])
            if 1 <= len(cand) <= 64:
                return cand

        # 単独 token っぽい最後の line
        cand = clean_token(line)
        if 1 <= len(cand) <= 32 and " " not in cand:
            return cand

    tokens = [t for t in extract_generic_short_targets(prompt) if 1 <= len(t) <= 32]
    return tokens[-1] if tokens else None

def solve_symbol_numeric_affine(prompt: str, answer: str):
    pairs = extract_generic_line_pairs(prompt)

    num_pairs = []
    for lhs, rhs in pairs:
        if re.fullmatch(r'-?\d+', lhs) and re.fullmatch(r'-?\d+', rhs):
            num_pairs.append((int(lhs), int(rhs)))

    if len(num_pairs) < 2:
        return None

    xs = [x for x, _ in num_pairs]
    ys = [y for _, y in num_pairs]

    target_num = extract_last_number(prompt)
    if target_num is None:
        return None

    candidates = [
        ("y = a*x + b", [lambda x: x, lambda x: 1.0]),
        ("y = a*x", [lambda x: x]),
    ]

    for name, basis in candidates:
        try:
            coef, max_err, _ = fit_linear_basis(xs, ys, basis, name)
            pred = eval_linear_basis(target_num, coef, basis)
            pred_round = int(round(pred))

            if abs(pred - pred_round) > 1e-6:
                continue

            pred_s = str(pred_round)
            if verify_answer(answer, pred_s):
                rationale = (
                    f"The examples fit the integer rule {name}. "
                    f"Applying it to {int(target_num)} gives {pred_s}."
                )
                return pred_s, rationale, "symbol_numeric_affine"
        except Exception:
            pass

    return None

def solve_symbol_char_sub(prompt: str, answer: str):
    pairs = extract_generic_line_pairs(prompt)
    pairs = [(clean_token(a), clean_token(b)) for a, b in pairs]

    # same-length short string pairs only
    pairs = [
        (a, b) for a, b in pairs
        if 1 <= len(a) <= 32 and 1 <= len(b) <= 32 and len(a) == len(b)
    ]
    if len(pairs) < 2:
        return None

    mapping = build_char_map_from_pairs(pairs)
    if mapping is None:
        return None

    target = extract_last_nonexample_candidate(prompt)
    if not target:
        return None

    pred = decode_with_char_map(target, mapping)
    if pred is None:
        return None

    if not verify_answer(answer, pred):
        return None

    rationale = (
        f"The examples are consistent with a character-level symbol substitution. "
        f"Applying the recovered mapping to {target!r} gives {pred!r}."
    )
    return pred, rationale, "symbol_char_substitution"

def solve_symbol(prompt: str, answer: str):
    for fn in [solve_symbol_numeric_affine, solve_symbol_char_sub]:
        out = fn(prompt, answer)
        if out is not None:
            return out
    return None
```

---

## Cell 11: Master solver / teacher generation

```python
def solve_row(prompt: str, answer: str, family: str):
    if family == "roman":
        return solve_roman(prompt, answer)

    if family == "unit":
        out = solve_numeric_family(prompt, answer, family="unit")
        if out is None:
            return None
        pred, rationale = out
        return pred, rationale, "unit_numeric_rule"

    if family == "gravity":
        out = solve_numeric_family(prompt, answer, family="gravity")
        if out is None:
            return None
        pred, rationale = out
        return pred, rationale, "gravity_numeric_rule"

    if family == "binary":
        return solve_binary(prompt, answer)

    if family == "text":
        return solve_text_substitution(prompt, answer)

    if family == "symbol":
        return solve_symbol(prompt, answer)

    return None
```

```python
teacher_ok = []
teacher_pred = []
teacher_rationale = []
teacher_solver = []

family_stats = {fam: {"total": 0, "solved": 0} for fam in sorted(train_df["family"].unique())}

t0 = time.time()
for idx, row in enumerate(train_df.itertuples(index=False), start=1):
    fam = row.family
    family_stats[fam]["total"] += 1

    solved = solve_row(row.prompt, row.answer, fam)
    if solved is None:
        teacher_ok.append(False)
        teacher_pred.append(None)
        teacher_rationale.append(None)
        teacher_solver.append(None)
    else:
        pred, rationale, solver_name = solved
        ok = verify_answer(row.answer, pred)
        teacher_ok.append(ok)
        teacher_pred.append(pred if ok else None)
        teacher_rationale.append(rationale if ok else None)
        teacher_solver.append(solver_name if ok else None)
        if ok:
            family_stats[fam]["solved"] += 1

    if idx % 1000 == 0:
        print(f"processed {idx}/{len(train_df)} rows...")

train_df["teacher_ok"] = teacher_ok
train_df["teacher_pred"] = teacher_pred
train_df["teacher_rationale"] = teacher_rationale
train_df["teacher_solver"] = teacher_solver

elapsed = time.time() - t0
print(f"teacher scan done in {elapsed:.1f}s")
```

```python
coverage_rows = []
for fam, d in family_stats.items():
    total = d["total"]
    solved = d["solved"]
    cov = solved / total if total else 0.0
    coverage_rows.append({"family": fam, "total": total, "solved": solved, "coverage": cov})

coverage_df = pd.DataFrame(coverage_rows).sort_values("family").reset_index(drop=True)
display(coverage_df)

print("overall coverage:", train_df["teacher_ok"].mean())
display(train_df[train_df["teacher_ok"]][["family", "teacher_solver"]].value_counts().head(20))
```

### coverage の見方
この方針が 0.8 を狙えるかの目安として、だいたい次が欲しいです。

- `roman`: 0.95 以上
- `unit`: 0.70 以上
- `gravity`: 0.70 以上
- `binary`: 0.60 以上
- `text`: 0.50 以上
- `symbol`: 0.10〜0.20 以上

ここがかなり低い場合、train 信号が足りません。  
ただ、**roman / unit / gravity / binary** の4 family が強ければ、全体はかなり持ち上がります。

---

## Cell 12: Distilled training set construction

```python
def sample_family_records(df: pd.DataFrame, family: str, solved_quota: int, terse_quota: int, seed: int = 42):
    fam_df = df[df["family"] == family].copy()

    solved_df = fam_df[fam_df["teacher_ok"]].sample(frac=1.0, random_state=seed)
    unsolved_df = fam_df[~fam_df["teacher_ok"]].sample(frac=1.0, random_state=seed + 1)

    records = []

    # solved trace records
    take_solved = solved_df.head(min(solved_quota, len(solved_df)))
    for row in take_solved.itertuples(index=False):
        records.append({
            "id": row.id,
            "family": row.family,
            "answer": row.answer,
            "prompt": row.prompt,
            "rationale": row.teacher_rationale,
            "record_type": "solved_trace",
            "solver": row.teacher_solver,
        })

    used_ids = set(take_solved["id"].tolist())

    # terse records: unsolved 優先、足りなければ solved の残り
    terse_pool = pd.concat([
        unsolved_df,
        solved_df[~solved_df["id"].isin(used_ids)]
    ], axis=0).drop_duplicates(subset=["id"])

    take_terse = terse_pool.head(min(terse_quota, len(terse_pool)))
    for row in take_terse.itertuples(index=False):
        records.append({
            "id": row.id,
            "family": row.family,
            "answer": row.answer,
            "prompt": row.prompt,
            "rationale": None,
            "record_type": "terse_boxed",
            "solver": row.teacher_solver if hasattr(row, "teacher_solver") else None,
        })

    return records

all_records = []
for fam in sorted(SOLVED_QUOTAS.keys()):
    recs = sample_family_records(
        train_df,
        family=fam,
        solved_quota=SOLVED_QUOTAS[fam],
        terse_quota=TERSE_QUOTAS[fam],
        seed=SEED,
    )
    all_records.extend(recs)

distill_df = pd.DataFrame(all_records).sample(frac=1.0, random_state=SEED).reset_index(drop=True)

print("distilled records:", len(distill_df))
display(distill_df["family"].value_counts())
display(distill_df["record_type"].value_counts())
display(distill_df.head(3))
```

---

## Cell 13: Tokenization

```python
tokenized_samples = []
bad_rows = 0

for row in distill_df.itertuples(index=False):
    try:
        tok = tokenize_completion_only(
            prompt=row.prompt,
            answer=row.answer,
            rationale=row.rationale,
        )
        tokenized_samples.append(tok)
    except Exception as e:
        bad_rows += 1

print("tokenized_samples:", len(tokenized_samples))
print("bad_rows:", bad_rows)

total_tokens = sum(len(x["input_ids"]) for x in tokenized_samples)
total_supervised = sum(sum(t != -100 for t in x["labels"]) for x in tokenized_samples)

print("total tokens:", total_tokens)
print("total supervised tokens:", total_supervised)
print("avg tokens/sample:", total_tokens / max(len(tokenized_samples), 1))
print("avg supervised/sample:", total_supervised / max(len(tokenized_samples), 1))
```

---

## Cell 14: Packed dataset

```python
class PackedCausalDataset(Dataset):
    def __init__(self, samples: List[Dict], block_size: int):
        self.block_size = block_size

        flat_input_ids = []
        flat_labels = []

        for s in samples:
            flat_input_ids.extend(s["input_ids"])
            flat_labels.extend(s["labels"])

        usable_len = (len(flat_input_ids) // block_size) * block_size
        flat_input_ids = flat_input_ids[:usable_len]
        flat_labels = flat_labels[:usable_len]

        self.examples = []
        for i in range(0, usable_len, block_size):
            ids = flat_input_ids[i:i + block_size]
            labels = flat_labels[i:i + block_size]
            self.examples.append({
                "input_ids": torch.tensor(ids, dtype=torch.long),
                "attention_mask": torch.ones(block_size, dtype=torch.long),
                "labels": torch.tensor(labels, dtype=torch.long),
            })

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]

class SimpleCollator:
    def __call__(self, batch):
        return {
            "input_ids": torch.stack([x["input_ids"] for x in batch]),
            "attention_mask": torch.stack([x["attention_mask"] for x in batch]),
            "labels": torch.stack([x["labels"] for x in batch]),
        }

train_dataset = PackedCausalDataset(tokenized_samples, block_size=PACK_LEN)
collator = SimpleCollator()

steps_per_epoch = math.ceil(len(train_dataset) / PER_DEVICE_BATCH / GRAD_ACCUM)
print("packed blocks:", len(train_dataset))
print("steps_per_epoch:", steps_per_epoch)
```

---

## Cell 15: Load model + LoRA

```python
gc.collect()
torch.cuda.empty_cache()

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    trust_remote_code=True,
    dtype=torch.bfloat16,
)

# Nemotron fast path を切る
for name, mod in list(sys.modules.items()):
    if "modeling_nemotron_h" in name and hasattr(mod, "is_fast_path_available"):
        mod.is_fast_path_available = False
        print(f"Patched {name}: is_fast_path_available = False")

if hasattr(model.config, "use_cache"):
    model.config.use_cache = False

try:
    model.gradient_checkpointing_enable()
except Exception as e:
    print("gradient_checkpointing_enable failed:", e)

try:
    model.enable_input_require_grads()
except Exception as e:
    print("enable_input_require_grads skipped:", e)

def find_target_modules(model) -> List[str]:
    preferred = {"q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"}
    found = set()

    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            leaf = name.split(".")[-1]
            if leaf in preferred:
                found.add(leaf)

    found = sorted(found)
    if not found:
        raise ValueError("No standard projection modules found for LoRA.")
    return found

target_modules = find_target_modules(model)
print("LoRA target modules:", target_modules)
```

```python
lora_config = LoraConfig(
    r=LORA_RANK,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    target_modules=target_modules,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

---

## Cell 16: Training

```python
total_optim_steps = steps_per_epoch * NUM_EPOCHS
warmup_steps = max(10, int(total_optim_steps * 0.05))

print("total_optim_steps:", total_optim_steps)
print("warmup_steps:", warmup_steps)
```

```python
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,

    per_device_train_batch_size=PER_DEVICE_BATCH,
    gradient_accumulation_steps=GRAD_ACCUM,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LR,
    lr_scheduler_type="cosine",
    warmup_steps=warmup_steps,

    bf16=True,
    optim="adamw_torch",
    max_grad_norm=MAX_GRAD_NORM,

    logging_steps=10,
    save_strategy="no",
    report_to="none",

    dataloader_num_workers=2,
    remove_unused_columns=False,
    gradient_checkpointing=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=collator,
)

print("Starting training...")
train_result = trainer.train()
print(train_result)
```

---

## Cell 17: Save adapter + submission.zip

```python
gc.collect()
torch.cuda.empty_cache()

trainer.model.save_pretrained(OUTPUT_DIR)

print(f"Saved files in {OUTPUT_DIR}:")
for f in os.listdir(OUTPUT_DIR):
    fp = os.path.join(OUTPUT_DIR, f)
    if os.path.isfile(fp):
        print(f"  {f:30s} {os.path.getsize(fp)/1024/1024:.2f} MB")
```

```python
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for fname in os.listdir(OUTPUT_DIR):
        fpath = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(fpath):
            zf.write(fpath, arcname=fname)

print(f"Created {ZIP_PATH} ({os.path.getsize(ZIP_PATH)/1024/1024:.2f} MB)")

with zipfile.ZipFile(ZIP_PATH, "r") as zf:
    names = zf.namelist()
    print("ZIP contents:", names)
    assert "adapter_config.json" in names, "adapter_config.json is missing!"
    print("✓ submission.zip is ready.")
```

---

## Cell 18: Optional smoke test

```python
test_df = pd.read_csv(TEST_PATH)
model.eval()

def build_infer_prompt(prompt: str) -> str:
    user_content = str(prompt) + EVAL_SUFFIX
    return safe_apply_chat_template(
        [{"role": "user", "content": user_content}],
        add_generation_prompt=True
    )

for i, row in test_df.head(3).iterrows():
    prompt_text = build_infer_prompt(row["prompt"])
    inputs = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=False)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=160,
            do_sample=False,
            temperature=0.0,
            top_p=1.0,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    gen = out[0][inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(gen, skip_special_tokens=False)

    print("=" * 80)
    print("ID:", row["id"])
    print(text[:600])
```

---

# この版の意図を短く整理

今回の改善の本質は、前回と違って **LoRA そのものではなく教師データの質を変えている**ことです。

## 前回
- answer-only 寄り
- supervised token が少ない
- 「考え始めるが boxed に着地しない」

## 今回
- **verified solver** が解けた問題だけ trace 化
- `</think>\n\boxed{...}` を直接学習
- hidden test と同じ `enable_thinking=True` の出力軌道に寄せる
- binary / numeric / text の **family-specific rule induction** を明示

---

# 0.8 に対する現実的な見立て

率直に言うと、**0.8 は solver coverage 次第**です。  
この notebook で特に重要なのは **Cell 11 の coverage 表**です。

もし coverage が例えば:

- roman ≈ 1.00
- unit ≈ 0.85
- gravity ≈ 0.80
- binary ≈ 0.70
- text ≈ 0.60
- symbol ≈ 0.15

くらい出るなら、**0.75+ は十分視野**です。  
0.8 も hidden test が train 同分布なら狙えます。

逆に、binary や text の coverage が低いなら、  
次にやるべきは LoRA の調整ではなく **solver DSL の拡張**です。

---

# 次に必要ならできること
必要なら次のどちらかを続けて出せます。

1. **binary solver をさらに強化した版**
   - swap / rotate / xor-constant / bitcount 系 DSL 追加

2. **local CV 評価付き版**
   - family stratified split で submit 前に期待値を見積もる

必要なら次は **「Cell 11 の coverage が低かった時の強化版」** をそのまま実装します。

