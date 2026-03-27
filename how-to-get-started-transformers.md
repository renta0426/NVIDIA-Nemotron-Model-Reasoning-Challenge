以下は、そのまま **README / 実験手順書** として使える形でまとめたものです。  
**前提だけ最初に明確化**します。

- **この手順は MLX 不使用、量子化不使用、Transformers 版の `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` を直接ベースにして LoRA を作る**流れです。公式 README には `AutoModelForCausalLM.from_pretrained(..., trust_remote_code=True)` の利用例があり、repo には `config.json`、`configuration_nemotron_h.py`、`modeling_nemotron_h.py`、tokenizer 類、分割 `safetensors` が揃っています。PEFT 公式 docs でも `save_pretrained()` により `adapter_config.json` と `adapter_model.safetensors` を保存する流れが案内されています。 
- ただし **NVIDIA の公式モデルカード上のサポート実行環境は Linux / NVIDIA H100・A100** です。PyTorch 自体は macOS の `mps` デバイスをサポートしているため、**Apple Silicon Mac 上で Transformers + PEFT による LoRA 作成と smoke test は可能**ですが、**あなたが貼った評価 metric そのものの vLLM/CUDA/Triton 実行を macOS ネイティブで完全再現することは想定しない**、という整理にします。 

---

# NVIDIA Nemotron Model Reasoning Challenge 向け  
# Mac 完結 LoRA 実験ドキュメント
**対象**: Apple Silicon Mac  
**禁止事項**: MLX / 量子化モデル / DoRA / `modules_to_save` 利用  
**提出物**: `submission.zip` 内に PEFT 形式 LoRA アダプタ

---

## 1. このドキュメントのゴール

この手順で行うのは次の 4 つだけです。

1. **公式 HF の BF16 Nemotron を固定 revision で取得**
2. **Mac 上で Transformers + PEFT により LoRA を学習**
3. **提出互換の静的検証**
4. **`submission.zip` を作成**

モデル改善の話はしません。  
提出互換性だけを満たす実装に絞ります。

---

## 2. 公式ソースに基づく提出互換ルール

### ベースモデル
この手順では **`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`** を使います。公式 README には Transformers での利用例、`trust_remote_code=True`、chat template、vLLM 利用例が載っています。repo 本体も custom code 前提です。 

### 保存形式
PEFT 公式 docs では、LoRA 保存物は `save_pretrained()` により **`adapter_config.json`** と **`adapter_model.safetensors`** が基本形です。 

### vLLM 互換制約
vLLM 公式 docs / source docs 上、LoRA で少なくとも次を守る必要があります。

- **rank は `max_lora_rank` 以下**
- **`modules_to_save` は `None`**
- **`use_dora` は `False`**
- **`bias` は `"none"`**
- `target_modules` は suffix 指定で扱われる 

### Nemotron 側の target_modules
公式 model code では、少なくとも次の名前が確認できます。

- attention: `q_proj`, `k_proj`, `v_proj`, `o_proj`
- MLP/MoE: `up_proj`, `down_proj`
- Mamba: `in_proj`, `out_proj`
- **`gate_proj` は見当たりません** 

---

## 3. Mac 側の前提

### 必須
- **Apple Silicon Mac**
- **macOS 12.3 以上**
- PyTorch の `mps` が有効であること 

### 実務上の目安
公式 repo の files page ではモデル本体は **63.2GB**、重みは 13 分割 safetensors です。LoRA ではベース重みは凍結されますが、それでも Mac の統合メモリにはかなり余裕が必要です。**128GB 統合メモリ以上を実務上の目安**にしてください。これは公式 minimum ではなく、repo サイズからの運用上の判断です。 

---

## 4. revision を固定する

Hugging Face Hub 公式 docs の `snapshot_download()` は **`revision` に branch / tag / commit hash を指定可能**です。repo は更新され得るので、**`main` を直接使わず commit 固定**にします。Nemotron の files page も最近更新されています。 

---

## 5. 推奨ディレクトリ構成

```text
nemotron-mac-lora/
├─ data/
│  └─ train.csv
├─ output/
│  └─ nemotron_lora/
├─ train_lora_macos.py
├─ smoke_test_adapter.py
├─ validate_submission.py
├─ make_submission_zip.py
└─ requirements.txt
```

---

## 6. セットアップ

## 6.1 Python 仮想環境

PyTorch の macOS 向け公式インストール案内では、macOS 10.15+、Python 3.10 以降、`pip` 利用が前提です。 

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install torch torchvision
```

## 6.2 追加パッケージ

Nemotron の公式 README は **Transformers 4.57.3 でテスト済み**と明記しています。PEFT は現行 stable を使います。 

`requirements.txt`:

```txt
transformers==4.57.3
peft==0.18.0
accelerate>=1.0.0
datasets>=3.0.0
huggingface_hub>=0.30.0
pandas>=2.0.0
safetensors>=0.4.0
sentencepiece>=0.2.0
```

インストール:

```bash
pip install -r requirements.txt
```

## 6.3 MPS 確認

```bash
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("mps built:", torch.backends.mps.is_built())
print("mps available:", torch.backends.mps.is_available())
PY
```

---

## 7. 学習用データの前提

`train.csv` は少なくとも次を持つ想定です。

- `id`
- `prompt`
- `answer`

このドキュメントでは、**提出フォーマットとの整合だけを目的に**、学習ターゲットを `\boxed{...}` で包みます。  
これはあなたが貼った評価コードが boxed answer を優先抽出するためです。

---

## 8. 学習スクリプト

`train_lora_macos.py`

```python
import argparse
import gc
import json
from pathlib import Path

import pandas as pd
import torch
from huggingface_hub import snapshot_download
from peft import LoraConfig, TaskType, get_peft_model
from torch.optim import AdamW
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
ALLOWED_TARGET_SUFFIXES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "up_proj",
    "down_proj",
    "in_proj",
    "out_proj",
]

BOXED_INSTRUCTION = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--train_csv", type=str, required=True)
    p.add_argument("--output_dir", type=str, required=True)
    p.add_argument("--cache_dir", type=str, default="./hf_cache")
    p.add_argument("--revision", type=str, default="main")
    p.add_argument("--max_rows", type=int, default=32)
    p.add_argument("--max_length", type=int, default=1024)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--weight_decay", type=float, default=0.0)
    p.add_argument("--grad_accum", type=int, default=4)
    p.add_argument("--lora_r", type=int, default=16)
    p.add_argument("--lora_alpha", type=int, default=32)
    p.add_argument("--lora_dropout", type=float, default=0.0)
    return p.parse_args()


def require_mps():
    if not torch.backends.mps.is_available():
        raise RuntimeError(
            "MPS is not available. This script is intended for Apple Silicon Mac with MPS enabled."
        )
    return "mps"


def download_snapshot(cache_dir: str, revision: str) -> str:
    allow_patterns = [
        "*.json",
        "*.py",
        "*.jinja",
        "*.txt",
        "*.model",
        "*.safetensors",
        "tokenizer*",
        "special_tokens_map.json",
        "chat_template.jinja",
    ]
    local_path = snapshot_download(
        repo_id=MODEL_ID,
        revision=revision,
        cache_dir=cache_dir,
        allow_patterns=allow_patterns,
    )
    return local_path


def load_tokenizer_and_model(model_path: str, device: str):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Local Mac training uses float16 on MPS.
    # The base repository is still the official BF16 Transformers repo.
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        device_map={"": device},
        attn_implementation="eager",
    )
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    return tokenizer, model


def discover_target_modules(model):
    found = []
    for name, module in model.named_modules():
        suffix = name.split(".")[-1]
        if suffix in ALLOWED_TARGET_SUFFIXES and hasattr(module, "weight"):
            found.append(suffix)
    found = sorted(set(found))

    required_core = {"q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj"}
    missing = sorted(required_core - set(found))
    if missing:
        raise RuntimeError(f"Missing expected target modules: {missing}")

    return found


def maybe_apply_chat_template(tokenizer, messages):
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
            enable_thinking=True,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )


def format_example(tokenizer, prompt: str, answer: str, max_length: int):
    user_content = str(prompt) + BOXED_INSTRUCTION
    assistant_content = f"\\boxed{{{str(answer).strip()}}}"
    text = maybe_apply_chat_template(
        tokenizer,
        [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ],
    )

    enc = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
        padding=False,
    )
    enc["labels"] = enc["input_ids"].clone()
    return enc


def move_batch_to_device(batch, device):
    return {k: v.to(device) for k, v in batch.items()}


def normalize_adapter_config(output_dir: Path, revision: str, target_modules):
    cfg_path = output_dir / "adapter_config.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    cfg["base_model_name_or_path"] = MODEL_ID
    cfg["revision"] = revision
    cfg["bias"] = "none"
    cfg["use_dora"] = False
    cfg["modules_to_save"] = None
    cfg["target_modules"] = target_modules

    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    meta = {
        "base_model_id": MODEL_ID,
        "revision": revision,
        "target_modules": target_modules,
    }
    with open(output_dir / "training_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def main():
    args = parse_args()
    if args.lora_r > 32:
        raise ValueError("This competition requires LoRA rank <= 32.")

    device = require_mps()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/6] Downloading pinned snapshot: {MODEL_ID} @ {args.revision}")
    model_path = download_snapshot(args.cache_dir, args.revision)

    print(f"[2/6] Loading tokenizer and model on {device}")
    tokenizer, model = load_tokenizer_and_model(model_path, device)

    print("[3/6] Discovering Nemotron target modules")
    target_modules = discover_target_modules(model)
    print("target_modules =", target_modules)

    print("[4/6] Wrapping with PEFT LoRA")
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=target_modules,
        bias="none",
        use_dora=False,
        modules_to_save=None,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    print("[5/6] Loading train.csv")
    df = pd.read_csv(args.train_csv).head(args.max_rows)
    if not {"prompt", "answer"}.issubset(df.columns):
        raise ValueError("train.csv must contain at least 'prompt' and 'answer' columns.")

    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    model.train()
    global_step = 0

    for epoch in range(args.epochs):
        print(f"== epoch {epoch + 1}/{args.epochs} ==")
        optimizer.zero_grad(set_to_none=True)

        for i, row in enumerate(df.itertuples(index=False), start=1):
            batch = format_example(
                tokenizer=tokenizer,
                prompt=row.prompt,
                answer=row.answer,
                max_length=args.max_length,
            )
            batch = move_batch_to_device(batch, device)

            outputs = model(**batch)
            loss = outputs.loss / args.grad_accum
            loss.backward()

            if i % args.grad_accum == 0 or i == len(df):
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1
                print(f"step={global_step} loss={float(loss.item() * args.grad_accum):.6f}")
                if device == "mps":
                    torch.mps.empty_cache()

    print("[6/6] Saving adapter")
    model.save_pretrained(
        str(output_dir),
        safe_serialization=True,
        save_embedding_layers=False,
    )
    normalize_adapter_config(output_dir, args.revision, target_modules)

    del model
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    print(f"done: {output_dir}")


if __name__ == "__main__":
    main()
```

### 実行例

`revision` は **固定 commit** を入れてください。未固定なら `main` でも動きますが、本番提出用には非推奨です。

```bash
python train_lora_macos.py \
  --train_csv ./data/train.csv \
  --output_dir ./output/nemotron_lora \
  --cache_dir ./hf_cache \
  --revision main \
  --max_rows 16 \
  --max_length 1024 \
  --epochs 1 \
  --lora_r 16 \
  --lora_alpha 32
```

---

## 9. ローカル smoke test

`smoke_test_adapter.py`

```python
import argparse
import torch
from huggingface_hub import snapshot_download
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"

BOXED_INSTRUCTION = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--adapter_dir", type=str, required=True)
    p.add_argument("--cache_dir", type=str, default="./hf_cache")
    p.add_argument("--revision", type=str, default="main")
    p.add_argument("--prompt", type=str, required=True)
    p.add_argument("--max_new_tokens", type=int, default=128)
    return p.parse_args()


def main():
    args = parse_args()

    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS not available.")

    model_path = snapshot_download(
        repo_id=MODEL_ID,
        revision=args.revision,
        cache_dir=args.cache_dir,
        allow_patterns=[
            "*.json",
            "*.py",
            "*.jinja",
            "*.txt",
            "*.model",
            "*.safetensors",
            "tokenizer*",
            "special_tokens_map.json",
            "chat_template.jinja",
        ],
    )

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        device_map={"": "mps"},
        attn_implementation="eager",
    )
    model = PeftModel.from_pretrained(base, args.adapter_dir, is_trainable=False)
    model.eval()

    user_content = args.prompt + BOXED_INSTRUCTION
    try:
        input_ids = tokenizer.apply_chat_template(
            [{"role": "user", "content": user_content}],
            tokenize=True,
            add_generation_prompt=True,
            enable_thinking=True,
            return_tensors="pt",
        )
    except TypeError:
        input_ids = tokenizer.apply_chat_template(
            [{"role": "user", "content": user_content}],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        )

    input_ids = input_ids.to("mps")

    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

    print(tokenizer.decode(out[0], skip_special_tokens=False))


if __name__ == "__main__":
    main()
```

### 実行例

```bash
python smoke_test_adapter.py \
  --adapter_dir ./output/nemotron_lora \
  --revision main \
  --prompt "If x + 3 = 10, what is x?"
```

---

## 10. 提出互換の静的検証

vLLM 側の official docs で、`modules_to_save`、`use_dora`、`bias`、`r` に制約があるので、zip 前に静的検証します。 

`validate_submission.py`

```python
import argparse
import json
from pathlib import Path

ALLOWED_TARGET_SUFFIXES = {
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "up_proj",
    "down_proj",
    "in_proj",
    "out_proj",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter_dir", type=str, required=True)
    args = ap.parse_args()

    adapter_dir = Path(args.adapter_dir)
    cfg_path = adapter_dir / "adapter_config.json"
    weights_path = adapter_dir / "adapter_model.safetensors"

    if not cfg_path.exists():
        raise SystemExit("ERROR: adapter_config.json not found")
    if not weights_path.exists():
        raise SystemExit("ERROR: adapter_model.safetensors not found")
    if weights_path.stat().st_size == 0:
        raise SystemExit("ERROR: adapter_model.safetensors is empty")

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    errors = []

    r = cfg.get("r")
    if r is None or int(r) > 32:
        errors.append(f"r must be <= 32, got {r}")

    if cfg.get("bias") != "none":
        errors.append(f"bias must be 'none', got {cfg.get('bias')}")

    if cfg.get("use_dora", False):
        errors.append("use_dora must be false")

    if cfg.get("modules_to_save", None) is not None:
        errors.append(f"modules_to_save must be null/None, got {cfg.get('modules_to_save')}")

    target_modules = cfg.get("target_modules")
    if not isinstance(target_modules, list) or not target_modules:
        errors.append("target_modules must be a non-empty list")
    else:
        unknown = sorted(set(target_modules) - ALLOWED_TARGET_SUFFIXES)
        if unknown:
            errors.append(f"unknown target_modules for this recipe: {unknown}")

    if errors:
        raise SystemExit("INVALID ADAPTER:\n- " + "\n- ".join(errors))

    print("VALID")
    print(f"adapter_dir = {adapter_dir}")
    print(f"r = {r}")
    print(f"target_modules = {target_modules}")


if __name__ == "__main__":
    main()
```

### 実行例

```bash
python validate_submission.py --adapter_dir ./output/nemotron_lora
```

---

## 11. `submission.zip` の作成

`make_submission_zip.py`

```python
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter_dir", type=str, required=True)
    ap.add_argument("--zip_path", type=str, default="submission.zip")
    args = ap.parse_args()

    adapter_dir = Path(args.adapter_dir)
    zip_path = Path(args.zip_path)

    if not (adapter_dir / "adapter_config.json").exists():
        raise SystemExit("adapter_config.json not found")
    if not (adapter_dir / "adapter_model.safetensors").exists():
        raise SystemExit("adapter_model.safetensors not found")

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for p in sorted(adapter_dir.rglob("*")):
            if p.is_file():
                zf.write(p, arcname=p.relative_to(adapter_dir))

    print(f"created: {zip_path.resolve()}")


if __name__ == "__main__":
    main()
```

### 実行例

```bash
python make_submission_zip.py \
  --adapter_dir ./output/nemotron_lora \
  --zip_path ./submission.zip
```

---

## 12. 提出前チェックリスト

- [ ] ベースは **`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`**
- [ ] **MLX を使っていない**
- [ ] **量子化していない**
- [ ] `trust_remote_code=True` でロードしている
- [ ] `adapter_config.json` がある
- [ ] `adapter_model.safetensors` がある
- [ ] `r <= 32`
- [ ] `bias == "none"`
- [ ] `use_dora == false`
- [ ] `modules_to_save == null`
- [ ] `target_modules` はこのレシピの Nemotron suffix に限定
- [ ] zip 名は `submission.zip`

---

## 13. 公式ソースに照らした注意点

1. **Nemotron の公式 README は Transformers 利用を明示**していますが、同時に **NVIDIA GPU / Linux 向け最適化**も明示しています。したがって Mac 実験は「公式提出形式を作るためのローカル作業」と割り切るのが正しいです。 
2. **PEFT 保存形式は提出形式として自然**です。`save_pretrained()` で adapter 本体と config を保存できます。 
3. **vLLM 制約は必ず守る**必要があります。特に `modules_to_save=None`、`use_dora=False`、`bias="none"` は外さないでください。 
4. **target_modules は Nemotron 実装に合わせる**必要があります。このレシピでは `q_proj/k_proj/v_proj/o_proj/up_proj/down_proj/in_proj/out_proj` のみを使い、`gate_proj` は使いません。 
5. **revision 固定は必須運用**です。Hub docs でも `snapshot_download(revision=...)` が正式です。repo も最近更新されています。 

---
