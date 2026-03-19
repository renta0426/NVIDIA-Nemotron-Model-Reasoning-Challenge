from __future__ import annotations

import inspect
import json
import math
import os
import random
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from datasets import Dataset
from transformers import AutoConfig, AutoTokenizer

BOX_INSTRUCTION = (
    "Please put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)

TEMPLATE_PREFIX_TO_NAME = {
    "In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers.": "bit_manipulation",
    "In Alice's Wonderland, the gravitational constant has been secretly changed.": "gravity_constant",
    "In Alice's Wonderland, a secret unit conversion is applied to measurements.": "unit_conversion",
    "In Alice's Wonderland, secret encryption rules are used on text.": "text_decryption",
    "In Alice's Wonderland, numbers are secretly converted into a different numeral system.": "roman_numeral",
    "In Alice's Wonderland, a secret set of transformation rules is applied to equations.": "symbol_equation",
}

EASY_TEMPLATES = (
    "gravity_constant",
    "unit_conversion",
    "roman_numeral",
)

HARD_TEMPLATES = (
    "bit_manipulation",
    "text_decryption",
    "symbol_equation",
)

TARGET_MODULES_EXPLICIT = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)



def detect_template(prompt: str) -> str:
    stripped = prompt.strip()
    for prefix, name in TEMPLATE_PREFIX_TO_NAME.items():
        if stripped.startswith(prefix):
            return name

    lower = stripped.lower()
    if "bit manipulation" in lower:
        return "bit_manipulation"
    if "gravitational constant" in lower:
        return "gravity_constant"
    if "unit conversion" in lower:
        return "unit_conversion"
    if "encryption rules are used on text" in lower or "decrypt the following text" in lower:
        return "text_decryption"
    if "different numeral system" in lower:
        return "roman_numeral"
    if "transformation rules is applied to equations" in lower or "determine the result for" in lower:
        return "symbol_equation"
    return "unknown"



def detect_answer_type(answer: Any) -> str:
    text = str(answer).strip()
    if re.fullmatch(r"[01]{8}", text):
        return "8bit_binary"
    if re.fullmatch(r"[IVXLCDM]+", text):
        return "roman_numeral"
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
        return "numeric"
    if " " in text:
        return "multiword_text"
    if re.fullmatch(r"[A-Za-z]+", text):
        return "single_word_text"
    return "symbolic_or_other"



def add_dataset_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["template"] = enriched["prompt"].map(detect_template)
    enriched["prompt_chars"] = enriched["prompt"].str.len()
    if "answer" in enriched.columns:
        enriched["answer_type"] = enriched["answer"].map(detect_answer_type)
    return enriched



def stratified_train_val_split(
    df: pd.DataFrame,
    val_ratio: float,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    enriched = add_dataset_features(df)
    group_cols = ["template"]
    if "answer_type" in enriched.columns:
        group_cols.append("answer_type")

    rng = np.random.default_rng(seed)
    train_parts: list[pd.DataFrame] = []
    val_parts: list[pd.DataFrame] = []

    for _, group in enriched.groupby(group_cols, sort=False, dropna=False):
        group = group.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000_000)))
        if len(group) <= 1:
            n_val = 0
        else:
            n_val = int(round(len(group) * val_ratio))
            n_val = max(1, n_val)
            n_val = min(n_val, len(group) - 1)

        val_parts.append(group.iloc[:n_val])
        train_parts.append(group.iloc[n_val:])

    train_df = pd.concat(train_parts, ignore_index=True)
    val_df = pd.concat(val_parts, ignore_index=True)

    train_df = train_df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    val_df = val_df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return train_df, val_df



def print_split_summary(name: str, df: pd.DataFrame) -> None:
    print(f"[{name}] rows={len(df)}")
    if "template" in df.columns:
        print(df["template"].value_counts().sort_index())
    if "answer_type" in df.columns:
        print(df["answer_type"].value_counts().sort_index())



def build_metric_user_content(prompt: str) -> str:
    return prompt.strip() + "\n" + BOX_INSTRUCTION



def build_assistant_content(answer: Any) -> str:
    ans = str(answer).strip()
    # The competition extractor truncates boxed answers that contain literal braces.
    # For those cases, prefer a supported fallback format that preserves the full answer.
    if "{" in ans or "}" in ans:
        return f"Final answer: {ans}"
    return f"\\boxed{{{ans}}}"



def build_messages(prompt: str, answer: Any | None = None) -> list[dict[str, str]]:
    messages = [{"role": "user", "content": build_metric_user_content(prompt)}]
    if answer is not None:
        messages.append({"role": "assistant", "content": build_assistant_content(answer)})
    return messages



def apply_chat_template_safe(tokenizer, messages, add_generation_prompt: bool) -> str:
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
        chunks = []
        for message in messages:
            chunks.append(f"{message['role'].upper()}:\n{message['content']}")
        if add_generation_prompt:
            chunks.append("ASSISTANT:\n")
        return "\n\n".join(chunks)



def build_completion_only_example(tokenizer, prompt: str, answer: Any, max_length: int) -> dict[str, list[int]] | None:
    messages = build_messages(prompt, answer)
    full_text = apply_chat_template_safe(tokenizer, messages, add_generation_prompt=False)
    prefix_text = apply_chat_template_safe(tokenizer, messages[:1], add_generation_prompt=True)

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

    if len(full_ids) <= len(prefix_ids):
        return None

    labels = [-100] * len(prefix_ids) + full_ids[len(prefix_ids):]
    return {
        "input_ids": full_ids,
        "attention_mask": [1] * len(full_ids),
        "labels": labels,
    }



def build_completion_only_dataset(tokenizer, df: pd.DataFrame, max_length: int) -> Dataset:
    rows = []
    dropped = 0
    for row in df.itertuples(index=False):
        example = build_completion_only_example(tokenizer, row.prompt, row.answer, max_length=max_length)
        if example is None:
            dropped += 1
            continue
        rows.append(example)
    print(f"Built completion-only dataset: kept={len(rows)} dropped={dropped}")
    return Dataset.from_list(rows)



def build_sft_text(example: dict[str, Any], tokenizer) -> dict[str, str]:
    messages = build_messages(example["prompt"], example["answer"])
    text = apply_chat_template_safe(tokenizer, messages, add_generation_prompt=False)
    return {"text": text}



def build_sft_dataset(df: pd.DataFrame, tokenizer) -> Dataset:
    rows = []
    for row in df.itertuples(index=False):
        item = {"prompt": row.prompt, "answer": row.answer}
        text = build_sft_text(item, tokenizer)["text"]
        rows.append(
            {
                "text": text,
                "id": getattr(row, "id", None),
                "template": getattr(row, "template", detect_template(row.prompt)),
            }
        )
    print(f"Built SFT dataset: rows={len(rows)}")
    return Dataset.from_list(rows)



class CompletionOnlyCollator:
    def __init__(self, tokenizer, pad_to_multiple_of: int = 8):
        self.tokenizer = tokenizer
        self.pad_to_multiple_of = pad_to_multiple_of

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, torch.Tensor]:
        batch = self.tokenizer.pad(
            [
                {
                    "input_ids": feature["input_ids"],
                    "attention_mask": feature["attention_mask"],
                }
                for feature in features
            ],
            padding=True,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )

        max_len = batch["input_ids"].shape[1]
        labels = []
        for feature in features:
            label = feature["labels"]
            pad_len = max_len - len(label)
            labels.append(label + [-100] * pad_len)

        batch["labels"] = torch.tensor(labels, dtype=torch.long)
        return batch



def maybe_apply_triton_environment_fixes() -> None:
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

    for _, module in list(sys.modules.items()):
        if hasattr(module, "rmsnorm_fn"):
            module.rmsnorm_fn = _pure_rmsnorm_fn

    src = "/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell"
    dst = "/tmp/ptxas-blackwell"
    if not os.path.exists(src):
        return

    try:
        shutil.copy2(src, dst)
        os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        os.environ["TRITON_PTXAS_PATH"] = dst
        os.environ["TRITON_PTXAS_BLACKWELL_PATH"] = dst

        import triton.backends.nvidia as nv_backend

        src_bin = os.path.join(os.path.dirname(nv_backend.__file__), "bin")
        dst_bin = "/tmp/triton_nvidia_bin"
        shutil.copytree(src_bin, dst_bin, dirs_exist_ok=True)
        for filename in os.listdir(dst_bin):
            file_path = os.path.join(dst_bin, filename)
            if os.path.isfile(file_path):
                os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        nv_backend.__file__ = os.path.join(dst_bin, "..", "__init__.py")
    except Exception as exc:
        print(f"WARNING: Triton environment fix skipped: {exc}")



def resolve_base_model_path(base_model: str, use_kagglehub: bool = False) -> str:
    candidates = [base_model, os.environ.get("NEMOTRON_BASE_MODEL")]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))

    if use_kagglehub:
        import kagglehub

        return kagglehub.model_download(
            "metric/nemotron-3-nano-30b-a3b-bf16/transformers/default"
        )

    raise FileNotFoundError(
        "Base model path was not found. Set NEMOTRON_BASE_MODEL or pass an existing --base-model path."
    )



def load_tokenizer(base_model_path: str):
    config = AutoConfig.from_pretrained(
        base_model_path,
        trust_remote_code=True,
        local_files_only=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_path,
        config=config,
        trust_remote_code=True,
        local_files_only=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return config, tokenizer



def fix_rope_scaling(model) -> None:
    if hasattr(model.config, "rope_scaling") and isinstance(model.config.rope_scaling, dict):
        model.config.rope_scaling.setdefault("type", "linear")



def disable_nemotron_fast_path(model) -> None:
    try:
        module = inspect.getmodule(model.backbone.layers[0].mixer.__class__)
    except Exception:
        module = inspect.getmodule(model.__class__)

    if module is None or not hasattr(module, "is_fast_path_available"):
        print("WARNING: could not patch is_fast_path_available")
        return
    if getattr(module, "_copilot_fast_path_disabled", False):
        return

    print("Before patch: is_fast_path_available =", module.is_fast_path_available)
    module.is_fast_path_available = False
    module._copilot_fast_path_disabled = True
    print("After patch : is_fast_path_available =", module.is_fast_path_available)



def patch_nemotron_moe_dtype(model) -> None:
    module = inspect.getmodule(model.backbone.layers[0].mixer.__class__)
    if module is None:
        print("WARNING: could not locate Nemotron mixer module")
        return

    patched = []
    for name, cls in vars(module).items():
        if not isinstance(cls, type) or not hasattr(cls, "moe"):
            continue
        if getattr(cls, "_copilot_moe_dtype_patch", False):
            continue

        old_moe = cls.moe

        def new_moe(self, hidden_states, topk_indices, topk_weights, _old_moe=old_moe):
            topk_weights = topk_weights.to(hidden_states.dtype)
            return _old_moe(self, hidden_states, topk_indices, topk_weights)

        cls.moe = new_moe
        cls._copilot_moe_dtype_patch = True
        patched.append(name)

    print("Patched MoE dtype classes:", patched)



def patch_nemotron_mlp_forward_dtype(model) -> None:
    module = inspect.getmodule(model.backbone.layers[0].mixer.__class__)
    if module is None:
        raise RuntimeError("Could not locate Nemotron mixer module")

    cls = getattr(module, "NemotronHMLP", None)
    if cls is None:
        raise RuntimeError("NemotronHMLP not found")
    if getattr(cls, "_copilot_forward_dtype_patch", False):
        return

    old_forward = cls.forward

    def new_forward(self, x, _old_forward=old_forward):
        if (not torch.is_floating_point(x)) or x.dtype == torch.uint8:
            x = x.to(torch.bfloat16)
        return _old_forward(self, x)

    cls.forward = new_forward
    cls._copilot_forward_dtype_patch = True
    print("Patched NemotronHMLP.forward")



def apply_nemotron_runtime_patches(model) -> None:
    fix_rope_scaling(model)
    disable_nemotron_fast_path(model)
    patch_nemotron_moe_dtype(model)
    patch_nemotron_mlp_forward_dtype(model)
    model.config.use_cache = False



def save_adapter_submission(model, adapter_dir: Path, submission_zip: Path) -> dict[str, Any]:
    adapter_dir.mkdir(parents=True, exist_ok=True)
    submission_zip.parent.mkdir(parents=True, exist_ok=True)

    model.save_pretrained(adapter_dir, safe_serialization=True)

    adapter_config_path = adapter_dir / "adapter_config.json"
    if not adapter_config_path.exists():
        raise FileNotFoundError("adapter_config.json not found")

    with adapter_config_path.open("r", encoding="utf-8") as handle:
        adapter_cfg = json.load(handle)

    if int(adapter_cfg["r"]) > 32:
        raise ValueError(f"LoRA rank must be <= 32, got {adapter_cfg['r']}")

    adapter_weight_exists = (
        (adapter_dir / "adapter_model.safetensors").exists()
        or (adapter_dir / "adapter_model.bin").exists()
    )
    if not adapter_weight_exists:
        raise FileNotFoundError("adapter_model.safetensors or adapter_model.bin not found")

    with zipfile.ZipFile(submission_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in adapter_dir.rglob("*"):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(adapter_dir).as_posix())

    with zipfile.ZipFile(submission_zip, "r") as archive:
        names = archive.namelist()
        if not any(name.endswith("adapter_config.json") for name in names):
            raise RuntimeError("zip missing adapter_config.json")
        if not any(
            name.endswith("adapter_model.safetensors") or name.endswith("adapter_model.bin")
            for name in names
        ):
            raise RuntimeError("zip missing adapter weights")

    return adapter_cfg



def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"

    matches = re.findall(r'\\boxed\{([^}]*)(?:\}|$)', text)
    if matches:
        non_empty = [match.strip() for match in matches if match.strip()]
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



def verify_answer(expected: str, predicted: str) -> bool:
    expected = str(expected).strip()
    predicted = str(predicted).strip()
    try:
        expected_num = float(expected)
        predicted_num = float(predicted)
        return math.isclose(expected_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == expected.lower()



@torch.inference_mode()
def generate_one(model, tokenizer, prompt: str, max_new_tokens: int = 256) -> str:
    messages = [{"role": "user", "content": build_metric_user_content(prompt)}]
    prompt_text = apply_chat_template_safe(tokenizer, messages, add_generation_prompt=True)
    inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

    model.config.use_cache = True
    output = model.generate(
        **inputs,
        do_sample=False,
        temperature=0.0,
        top_p=1.0,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    generated_ids = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated_ids, skip_special_tokens=True)



def quick_validate(
    model,
    tokenizer,
    val_df: pd.DataFrame,
    output_csv: Path,
    max_samples: int | None = 64,
    max_new_tokens: int = 256,
) -> float:
    if len(val_df) == 0:
        raise ValueError("Validation dataframe is empty")

    if max_samples is not None:
        sample_df = val_df.sample(min(max_samples, len(val_df)), random_state=42)
    else:
        sample_df = val_df

    rows = []
    correct = 0
    for row in sample_df.itertuples(index=False):
        raw = generate_one(model, tokenizer, row.prompt, max_new_tokens=max_new_tokens)
        pred = extract_final_answer(raw)
        ok = verify_answer(str(row.answer), str(pred))
        correct += int(ok)
        rows.append(
            {
                "id": getattr(row, "id", None),
                "template": getattr(row, "template", detect_template(row.prompt)),
                "answer": row.answer,
                "pred": pred,
                "ok": ok,
                "raw": raw,
            }
        )

    acc = correct / len(sample_df)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    print(f"Quick validation accuracy over {len(sample_df)} rows: {acc:.4f}")
    return acc
