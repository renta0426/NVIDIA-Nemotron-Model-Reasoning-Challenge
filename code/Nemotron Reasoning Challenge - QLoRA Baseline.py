# ============================================
# Nemotron Reasoning Challenge - QLoRA Baseline
# ============================================

# このコードでパブリックリーダーボードスコアが0.58-0.62程度

import os
import re
import json
import math
import time
import random
import zipfile
import inspect
from pathlib import Path

import kagglehub

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
    set_seed,
    EarlyStoppingCallback,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
)

from transformers import AutoConfig

# -----------------------------
# Config
# -----------------------------
SEED = 42
VAL_RATIO = 0.05

# 96GB GPU なら 4096 はかなり安全。余裕があれば 6144 に上げてもよい
MAX_LENGTH = 1024

NUM_EPOCHS = 1
LEARNING_RATE = 2e-4
TRAIN_BATCH_SIZE = 1
EVAL_BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
WARMUP_RATIO = 0.03


LORA_R = 16
LORA_ALPHA = 32
# TRAIN_FRAC = 0.2

LORA_DROPOUT = 0.05

OUTPUT_ROOT = Path("/kaggle/working/nemotron_q_lora_baseline")
ADAPTER_DIR = OUTPUT_ROOT / "adapter"
SUBMISSION_ZIP = Path("/kaggle/working/submission.zip")

TRAIN_PATH = "./data/train.csv"
TEST_PATH = "./data/test.csv"

BOX_INSTRUCTION = (
    "Please put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)

set_seed(SEED)
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

# -----------------------------
# Resolve base model path
# -----------------------------
import glob
import os


# BASE_MODEL = kagglehub.model_download("metric/nemotron-3-nano-30b-a3b-bf16/transformers/default")
BASE_MODEL = "./1"

# -----------------------------
# Load data
# -----------------------------
train_df = pd.read_csv(TRAIN_PATH)
print("train_df shape:", train_df.shape)

# test は学習には使わない。提出確認用のみ
if os.path.exists(TEST_PATH):
    test_df = pd.read_csv(TEST_PATH)
    print("test_df shape:", test_df.shape)

# シャッフルして split
train_df = train_df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
n_val = max(1, int(len(train_df) * VAL_RATIO))
val_df = train_df.iloc[:n_val].copy().reset_index(drop=True)
tr_df = train_df.iloc[n_val:].copy().reset_index(drop=True)

print(f"train split: {len(tr_df)}")
print(f"valid split: {len(val_df)}")

# -----------------------------
# Tokenizer / chat template
# -----------------------------


# ① Config（必須）
config = AutoConfig.from_pretrained(
    BASE_MODEL,
    trust_remote_code=True,
    local_files_only=True
)

# ② Tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    config=config,
    trust_remote_code=True,
    local_files_only=True
)



if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

def apply_chat_template_safe(messages, add_generation_prompt):
    """
    metric は tokenizer.apply_chat_template(..., enable_thinking=True) を使っているので、
    可能なら同様に合わせる。
    """
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
        # 最終fallback
        chunks = []
        for m in messages:
            chunks.append(f"{m['role'].upper()}:\n{m['content']}")
        if add_generation_prompt:
            chunks.append("ASSISTANT:\n")
        return "\n\n".join(chunks)

def build_user_content(prompt: str) -> str:
    return prompt.strip() + "\n" + BOX_INSTRUCTION

def build_assistant_content(answer) -> str:
    ans = str(answer).strip()
    return f"\\boxed{{{ans}}}"

def build_example(prompt: str, answer, max_length: int):
    """
    completion-only loss 用に、assistant 側だけ labels を有効化する。
    """
    messages = [
        {"role": "user", "content": build_user_content(prompt)},
        {"role": "assistant", "content": build_assistant_content(answer)},
    ]

    full_text = apply_chat_template_safe(messages, add_generation_prompt=False)
    prefix_text = apply_chat_template_safe(messages[:1], add_generation_prompt=True)

    full_ids = tokenizer(
        full_text,
        add_special_tokens=False,
        truncation=True,
        max_length=max_length,
    )["input_ids"]

    prefix_ids = tokenizer(
        prefix_text,
        add_special_tokens=False,
        truncation=True,
        max_length=max_length,
    )["input_ids"]

    # prompt が長すぎて answer 部分が落ちたケースは除外
    if len(full_ids) <= len(prefix_ids):
        return None

    labels = [-100] * len(prefix_ids) + full_ids[len(prefix_ids):]

    return {
        "input_ids": full_ids,
        "attention_mask": [1] * len(full_ids),
        "labels": labels,
    }

def build_dataset(df: pd.DataFrame, max_length: int) -> Dataset:
    rows = []
    dropped = 0

    for row in df.itertuples(index=False):
        ex = build_example(row.prompt, row.answer, max_length=max_length)
        if ex is None:
            dropped += 1
            continue
        rows.append(ex)

    print(f"Built {len(rows)} examples, dropped={dropped}")
    return Dataset.from_list(rows)

train_ds = build_dataset(tr_df, MAX_LENGTH)
val_ds = build_dataset(val_df, MAX_LENGTH)

# -----------------------------
# Data collator
# -----------------------------
class CompletionOnlyCollator:
    def __init__(self, tokenizer, pad_to_multiple_of=8):
        self.tokenizer = tokenizer
        self.pad_to_multiple_of = pad_to_multiple_of

    def __call__(self, features):
        batch = self.tokenizer.pad(
            [
                {
                    "input_ids": f["input_ids"],
                    "attention_mask": f["attention_mask"],
                }
                for f in features
            ],
            padding=True,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )

        max_len = batch["input_ids"].shape[1]
        labels = []
        for f in features:
            lab = f["labels"]
            pad_len = max_len - len(lab)
            labels.append(lab + [-100] * pad_len)

        batch["labels"] = torch.tensor(labels, dtype=torch.long)
        return batch

collator = CompletionOnlyCollator(tokenizer)


# -----------------------------
# Load base model in 4bit
# -----------------------------
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

print("Loading base model...")


# ③ Model
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    config=config,
    trust_remote_code=True,
    device_map="auto",
    local_files_only=True,
    quantization_config=bnb_config
)


# ============================
# Nemotron rope_scaling fix
# ============================
if hasattr(model.config, "rope_scaling"):
    if isinstance(model.config.rope_scaling, dict):
        if "type" not in model.config.rope_scaling:
            model.config.rope_scaling["type"] = "linear"





# =========================================================
# Minimal fix:
# Nemotron の Mamba fast CUDA kernels を無効化
# Blackwell + causal_conv1d / mamba_ssm の kernel 不整合回避
# =========================================================
import inspect

def disable_nemotron_fast_path(model):
    try:
        # Nemotron mixer クラスの定義モジュールを取得
        m = inspect.getmodule(model.backbone.layers[0].mixer.__class__)
    except Exception:
        m = inspect.getmodule(model.__class__)

    if m is not None and hasattr(m, "is_fast_path_available"):
        print("Before patch: is_fast_path_available =", m.is_fast_path_available)
        m.is_fast_path_available = False
        print("After patch : is_fast_path_available =", m.is_fast_path_available)
    else:
        print("WARNING: could not patch is_fast_path_available")

disable_nemotron_fast_path(model)

# =========================================================
# Minimal fix:
# MoE routing weights(float32) -> hidden_states dtype(bfloat16)
# =========================================================
import inspect

def patch_nemotron_moe_dtype(model):
    m = inspect.getmodule(model.backbone.layers[0].mixer.__class__)
    patched = []

    for name, cls in vars(m).items():
        if isinstance(cls, type) and hasattr(cls, "moe"):
            old_moe = cls.moe

            def new_moe(self, hidden_states, topk_indices, topk_weights, _old_moe=old_moe):
                topk_weights = topk_weights.to(hidden_states.dtype)
                return _old_moe(self, hidden_states, topk_indices, topk_weights)

            cls.moe = new_moe
            patched.append(name)

    print("Patched MoE dtype classes:", patched)

patch_nemotron_moe_dtype(model)


model.config.use_cache = False
model = prepare_model_for_kbit_training(model)

target_modules = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]

lora_kwargs = dict(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=target_modules,
    inference_mode=False,
)

# PEFT の version 差分吸収
if "use_rslora" in inspect.signature(LoraConfig.__init__).parameters:
    lora_kwargs["use_rslora"] = True

peft_config = LoraConfig(**lora_kwargs)
model = get_peft_model(model, peft_config)

# =========================================================
# Minimal fix:
# NemotronHMLP.forward に Byte が入ると LoRA dropout で落ちる
# -> expert input を class-level で bf16 に矯正
# =========================================================
def patch_nemotron_mlp_forward_dtype(model):
    m = inspect.getmodule(model.backbone.layers[0].mixer.__class__)

    cls = getattr(m, "NemotronHMLP", None)
    if cls is None:
        raise RuntimeError("NemotronHMLP not found")

    old_forward = cls.forward

    def new_forward(self, x, _old_forward=old_forward):
        if (not torch.is_floating_point(x)) or x.dtype == torch.uint8:
            x = x.to(torch.bfloat16)
        return _old_forward(self, x)

    cls.forward = new_forward
    print("Patched NemotronHMLP.forward")

patch_nemotron_mlp_forward_dtype(model)

try:
    model.print_trainable_parameters()
except Exception:
    pass

# -----------------------------
# Training args
# -----------------------------
training_args = TrainingArguments(
    output_dir=str(OUTPUT_ROOT / "checkpoints"),

    max_steps=100,
    eval_strategy="steps",
    eval_steps=50,
    save_strategy="steps",
    save_steps=50,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,

    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=TRAIN_BATCH_SIZE,
    per_device_eval_batch_size=EVAL_BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,

    logging_steps=10,
    bf16=True,
    fp16=False,

    optim="paged_adamw_8bit",
    lr_scheduler_type="cosine",
    warmup_ratio=WARMUP_RATIO,
    weight_decay=0.0,
    max_grad_norm=0.3,

    gradient_checkpointing=True, # 高メモリならFalse
    remove_unused_columns=False,
    report_to="none",
    dataloader_num_workers=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    data_collator=collator,
    callbacks=[
        EarlyStoppingCallback(
            early_stopping_patience=3,
            early_stopping_threshold=0.01,
        )
    ],
)

# -----------------------------
# Train
# -----------------------------
print("Start training...")
trainer.train()

# -----------------------------
# Save LoRA adapter
# -----------------------------
print("Saving adapter...")
trainer.model.save_pretrained(ADAPTER_DIR, safe_serialization=True)

adapter_config_path = ADAPTER_DIR / "adapter_config.json"
assert adapter_config_path.exists(), "adapter_config.json not found"

with open(adapter_config_path, "r") as f:
    adapter_cfg = json.load(f)

assert int(adapter_cfg["r"]) <= 32, f"LoRA rank must be <= 32, got {adapter_cfg['r']}"

adapter_weight_exists = (
    (ADAPTER_DIR / "adapter_model.safetensors").exists()
    or (ADAPTER_DIR / "adapter_model.bin").exists()
)
assert adapter_weight_exists, "adapter_model.safetensors or adapter_model.bin not found"

print("Adapter config:")
print(json.dumps(adapter_cfg, indent=2, ensure_ascii=False))

# -----------------------------
# Package submission.zip
# -----------------------------
print("Creating submission.zip ...")
with zipfile.ZipFile(SUBMISSION_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for p in ADAPTER_DIR.rglob("*"):
        if p.is_file():
            # zip root に adapter files を置く
            zf.write(p, arcname=p.relative_to(ADAPTER_DIR).as_posix())

with zipfile.ZipFile(SUBMISSION_ZIP, "r") as zf:
    names = zf.namelist()
    assert any(n.endswith("adapter_config.json") for n in names), "zip missing adapter_config.json"
    assert any(
        n.endswith("adapter_model.safetensors") or n.endswith("adapter_model.bin")
        for n in names
    ), "zip missing adapter weights"

print(f"Submission ready: {SUBMISSION_ZIP}")
print("Zip contents:")
with zipfile.ZipFile(SUBMISSION_ZIP, "r") as zf:
    for n in zf.namelist():
        print(" -", n)

# -----------------------------
# Optional: quick local check
# -----------------------------
RUN_QUICK_EVAL = False

def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"

    matches = re.findall(r'\\boxed\{([^}]*)(?:\}|$)', text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()

    patterns = [
        r'The final answer is:\s*([^\n]+)',
        r'Final answer is:\s*([^\n]+)',
        r'Final answer\s*[:：]\s*([^\n]+)',
        r'final answer\s*[:：]\s*([^\n]+)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1].strip()

    matches = re.findall(r'-?\d+(?:\.\d+)?', text)
    if matches:
        return matches[-1]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"

def verify(stored_answer: str, predicted: str) -> bool:
    stored_answer = stored_answer.strip()
    predicted = predicted.strip()
    try:
        stored_num = float(stored_answer)
        predicted_num = float(predicted)
        return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == stored_answer.lower()

@torch.inference_mode()
def generate_one(prompt: str, max_new_tokens: int = 256) -> str:
    messages = [{"role": "user", "content": build_user_content(prompt)}]
    prompt_text = apply_chat_template_safe(messages, add_generation_prompt=True)
    inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

    model.config.use_cache = True
    out = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    gen_ids = out[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(gen_ids, skip_special_tokens=True)

if RUN_QUICK_EVAL:
    sample_val = val_df.sample(min(32, len(val_df)), random_state=SEED)
    correct = 0
    rows = []
    for r in sample_val.itertuples(index=False):
        raw = generate_one(r.prompt)
        pred = extract_final_answer(raw)
        ok = verify(str(r.answer), str(pred))
        correct += int(ok)
        rows.append({
            "id": r.id,
            "answer": r.answer,
            "pred": pred,
            "ok": ok,
            "raw": raw,
        })
    acc = correct / len(sample_val)
    print("Quick val acc:", acc)
    pd.DataFrame(rows).to_csv(OUTPUT_ROOT / "quick_val_predictions.csv", index=False)
