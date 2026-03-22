from __future__ import annotations

import gc
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

PROMPT_BLOCK_MARKERS = {
    "bit_manipulation": (
        "\n\nHere are some examples of input -> output:\n",
        "\n\nNow, determine the output for: ",
    ),
    "gravity_constant": (
        "Here are some example observations:\n",
        "\nNow, determine the falling distance for t = ",
    ),
    "unit_conversion": (
        "For example:\n",
        "\nNow, convert the following measurement: ",
    ),
    "text_decryption": (
        "Here are some examples:\n",
        "\nNow, decrypt the following text: ",
    ),
    "roman_numeral": (
        "Some examples are given below:\n",
        "\nNow, write the number ",
    ),
    "symbol_equation": (
        "Below are a few examples:\n",
        "\nNow, determine the result for: ",
    ),
}

ANSWER_TYPE_HINTS = {
    "numeric": "Keep the numeric formatting consistent with the examples and do not append extra numbers.",
    "8bit_binary": "Return exactly eight binary digits.",
    "roman_numeral": "Return an uppercase Roman numeral with canonical subtractive notation.",
    "multiword_text": "Preserve spaces and word order exactly.",
    "single_word_text": "Return the decoded word only.",
    "symbolic_or_other": "Preserve punctuation and symbol order exactly.",
}


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)



def release_memory() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()



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



def add_difficulty_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = add_dataset_features(df)
    if "answer" in enriched.columns:
        enriched["answer_chars"] = enriched["answer"].astype(str).str.len()
    prompt_q75 = float(enriched["prompt_chars"].quantile(0.75)) if len(enriched) else 0.0
    scores = []
    for row in enriched.itertuples(index=False):
        score = 0
        template = getattr(row, "template", "unknown")
        answer_type = getattr(row, "answer_type", "")
        answer_text = str(getattr(row, "answer", ""))
        if template in HARD_TEMPLATES:
            score += 2
        if answer_type in ("symbolic_or_other", "multiword_text"):
            score += 2
        elif answer_type in ("8bit_binary", "roman_numeral"):
            score += 1
        if getattr(row, "prompt_chars", 0) >= prompt_q75:
            score += 1
        if any(ch in answer_text for ch in ("{", "}", "\\")):
            score += 1
        scores.append(score)
    enriched["difficulty_score"] = scores
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



def make_stratified_folds(df: pd.DataFrame, num_folds: int, seed: int) -> list[pd.DataFrame]:
    if num_folds < 2:
        raise ValueError("num_folds must be >= 2")

    enriched = add_dataset_features(df)
    group_cols = ["template"]
    if "answer_type" in enriched.columns:
        group_cols.append("answer_type")

    rng = np.random.default_rng(seed)
    fold_parts: list[list[pd.DataFrame]] = [[] for _ in range(num_folds)]
    for _, group in enriched.groupby(group_cols, sort=False, dropna=False):
        shuffled = group.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000_000)))
        for fold_idx, part in enumerate(np.array_split(shuffled, num_folds)):
            if len(part) > 0:
                fold_parts[fold_idx].append(part)

    folds = []
    for parts in fold_parts:
        if parts:
            fold_df = pd.concat(parts, ignore_index=True)
        else:
            fold_df = enriched.iloc[0:0].copy()
        fold_df = fold_df.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000_000))).reset_index(drop=True)
        folds.append(fold_df)
    return folds



def print_split_summary(name: str, df: pd.DataFrame) -> None:
    print(f"[{name}] rows={len(df)}")
    if "template" in df.columns:
        print(df["template"].value_counts().sort_index())
    if "answer_type" in df.columns:
        print(df["answer_type"].value_counts().sort_index())
    if "difficulty_score" in df.columns:
        print("difficulty_mean=", round(float(df["difficulty_score"].mean()), 3))



def build_metric_user_content(prompt: str) -> str:
    return prompt.strip() + "\n" + BOX_INSTRUCTION



def build_assistant_content(answer: Any) -> str:
    ans = str(answer).strip()
    if "{" in ans or "}" in ans:
        return f"Final answer: {ans}"
    return f"\\boxed{{{ans}}}"



def _extract_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None



def build_trace_assistant_content(
    prompt: str,
    answer: Any,
    template: str | None = None,
    answer_type: str | None = None,
) -> str:
    template = template or detect_template(prompt)
    answer_type = answer_type or detect_answer_type(answer)
    format_hint = ANSWER_TYPE_HINTS.get(answer_type, "Return the canonical final answer only.")
    answer_text = str(answer).strip()

    if template == "gravity_constant":
        target_time = _extract_match(r"Now, determine the falling distance for t = ([0-9.]+)s", prompt)
        reasoning = (
            f"Infer the Wonderland gravity from the observation pairs, then substitute t = {target_time}s into d = 0.5*g*t^2."
            if target_time is not None
            else "Infer the Wonderland gravity from the observation pairs, then apply d = 0.5*g*t^2 to the target time."
        )
    elif template == "unit_conversion":
        target_measurement = _extract_match(r"Now, convert the following measurement: ([^\n]+)", prompt)
        reasoning = (
            f"Infer the hidden conversion rule from the example measurements and apply it to {target_measurement}."
            if target_measurement is not None
            else "Infer the hidden conversion rule from the example measurements and apply it to the target measurement."
        )
    elif template == "roman_numeral":
        target_number = _extract_match(r"Now, write the number (\d+) in the Wonderland numeral system", prompt)
        reasoning = (
            f"Convert {target_number} into the Wonderland numeral system using standard Roman-style subtractive notation."
            if target_number is not None
            else "Convert the target number into the Wonderland numeral system using canonical Roman-style notation."
        )
    elif template == "bit_manipulation":
        reasoning = "Infer the deterministic bit operation from the eight binary input/output examples, then apply it to the target 8-bit string."
    elif template == "text_decryption":
        reasoning = "Infer the text transformation from the ciphertext/plaintext pairs, then decode the target phrase exactly."
    elif template == "symbol_equation":
        reasoning = "Infer the deterministic symbol rewrite pattern from the example equations, then apply it to the target expression without normalizing symbols."
    else:
        reasoning = "Infer the hidden transformation rule from the examples and apply it to the target case."

    final_line = build_assistant_content(answer_text)
    return "\n".join(
        [
            f"Task type: {template}",
            f"Answer format: {answer_type}",
            f"Reasoning plan: {reasoning}",
            format_hint,
            final_line,
        ]
    )



def build_messages(
    prompt: str,
    answer: Any | None = None,
    style: str = "direct",
    template: str | None = None,
    answer_type: str | None = None,
) -> list[dict[str, str]]:
    messages = [{"role": "user", "content": build_metric_user_content(prompt)}]
    if answer is not None:
        if style == "trace":
            content = build_trace_assistant_content(
                prompt,
                answer,
                template=template,
                answer_type=answer_type,
            )
        else:
            content = build_assistant_content(answer)
        messages.append({"role": "assistant", "content": content})
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
    messages = build_messages(prompt, answer, style="direct")
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



def build_sft_text(example: dict[str, Any], tokenizer, style: str = "direct") -> dict[str, str]:
    messages = build_messages(
        example["prompt"],
        example["answer"],
        style=style,
        template=example.get("template"),
        answer_type=example.get("answer_type"),
    )
    text = apply_chat_template_safe(tokenizer, messages, add_generation_prompt=False)
    return {"text": text}



def build_sft_dataset(df: pd.DataFrame, tokenizer, style: str = "direct") -> Dataset:
    enriched = add_dataset_features(df)
    rows = []
    for row in enriched.itertuples(index=False):
        item = {
            "prompt": row.prompt,
            "answer": row.answer,
            "template": getattr(row, "template", detect_template(row.prompt)),
            "answer_type": getattr(row, "answer_type", detect_answer_type(row.answer)),
        }
        text = build_sft_text(item, tokenizer, style=style)["text"]
        rows.append(
            {
                "text": text,
                "id": getattr(row, "id", None),
                "template": item["template"],
                "answer_type": item["answer_type"],
            }
        )
    print(f"Built SFT dataset ({style}): rows={len(rows)}")
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



def _shuffle_example_lines(prompt: str, start_marker: str, end_marker: str, seed: int) -> str:
    if start_marker not in prompt or end_marker not in prompt:
        return prompt
    prefix, rest = prompt.split(start_marker, 1)
    middle, suffix = rest.split(end_marker, 1)
    lines = [line for line in middle.splitlines() if line.strip()]
    if len(lines) < 2:
        return prompt
    rng = random.Random(seed)
    shuffled = lines[:]
    for _ in range(5):
        rng.shuffle(shuffled)
        if shuffled != lines:
            break
    if shuffled == lines:
        return prompt
    return prefix + start_marker + "\n".join(shuffled) + end_marker + suffix



def augment_prompt_example_order(prompt: str, seed: int) -> str:
    template = detect_template(prompt)
    markers = PROMPT_BLOCK_MARKERS.get(template)
    if markers is None:
        return prompt
    start_marker, end_marker = markers
    return _shuffle_example_lines(prompt, start_marker, end_marker, seed)



def expand_with_prompt_augmentations(
    df: pd.DataFrame,
    copies_per_row: int,
    seed: int,
    hard_templates_extra_copies: int = 0,
) -> pd.DataFrame:
    if copies_per_row <= 0 and hard_templates_extra_copies <= 0:
        return df.iloc[0:0].copy()

    enriched = add_dataset_features(df)
    rows: list[dict[str, Any]] = []
    for row_idx, row in enumerate(enriched.to_dict("records")):
        extra = copies_per_row
        if row.get("template") in HARD_TEMPLATES:
            extra += hard_templates_extra_copies
        for copy_idx in range(extra):
            augmented_prompt = augment_prompt_example_order(
                row["prompt"],
                seed + (row_idx * 101) + copy_idx,
            )
            if augmented_prompt == row["prompt"]:
                continue
            new_row = dict(row)
            if new_row.get("id") is not None:
                new_row["id"] = f"{new_row['id']}__aug{copy_idx + 1}"
            new_row["prompt"] = augmented_prompt
            new_row["augmented"] = True
            rows.append(new_row)
    if not rows:
        return enriched.iloc[0:0].copy()
    augmented_df = pd.DataFrame(rows)
    if "augmented" not in augmented_df.columns:
        augmented_df["augmented"] = True
    return augmented_df.reset_index(drop=True)



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


def resolve_repo_root() -> Path:
    candidates: list[Path] = []

    env_root = os.environ.get("NEMOTRON_REPO_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser().resolve())

    script_path = globals().get("__file__")
    if script_path:
        resolved_script = Path(script_path).resolve()
        candidates.append(resolved_script.parent)
        candidates.extend(resolved_script.parents)

    cwd = Path.cwd().resolve()
    candidates.append(cwd)
    candidates.extend(cwd.parents)

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if (
            (candidate / "README.md").exists()
            and (candidate / "data" / "train.csv").exists()
            and (candidate / "versions").exists()
        ):
            return candidate

    raise FileNotFoundError(
        "Could not resolve repository root. Set NEMOTRON_REPO_ROOT to the repository path."
    )


def detect_runtime_profile() -> str:
    override = os.environ.get("NEMOTRON_RUNTIME_PROFILE") or os.environ.get("NEMOTRON_GPU_PROFILE")
    if override:
        return override.strip().lower()

    if not torch.cuda.is_available():
        return "default"

    gpu_name = torch.cuda.get_device_name(0).lower()
    if "blackwell" in gpu_name or "rtx pro 6000" in gpu_name:
        return "blackwell"
    if "a6000" in gpu_name:
        return "a6000"
    return "default"


def cleanup_checkpoints(output_dir: Path) -> None:
    for checkpoint_dir in output_dir.glob("checkpoint-*"):
        shutil.rmtree(checkpoint_dir, ignore_errors=True)



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



def import_trl():
    try:
        from trl import SFTConfig, SFTTrainer
    except ImportError as exc:
        raise ImportError(
            "trl is required for this version. Install it as in baseline/start.ipynb or baseline/nvidia-nemotron-sfttrainer-training.ipynb."
        ) from exc
    return SFTConfig, SFTTrainer



def build_sft_config(
    output_dir: Path,
    num_train_epochs: float,
    max_length: int,
    learning_rate: float,
    train_batch_size: int,
    eval_batch_size: int,
    gradient_accumulation_steps: int,
    warmup_ratio: float,
    save_strategy: str,
    evaluation_strategy: str,
    eval_steps: int,
    save_steps: int,
    max_grad_norm: float = 1.0,
    bf16: bool = True,
    weight_decay: float = 0.0,
    load_best_model_at_end: bool | None = None,
):
    SFTConfig, _ = import_trl()
    kwargs = dict(
        output_dir=str(output_dir),
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=eval_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        logging_steps=10,
        bf16=bf16,
        max_grad_norm=max_grad_norm,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        warmup_ratio=warmup_ratio,
        weight_decay=weight_decay,
        save_strategy=save_strategy,
        evaluation_strategy=evaluation_strategy,
        eval_steps=eval_steps,
        save_steps=save_steps,
        save_total_limit=2,
        load_best_model_at_end=(evaluation_strategy != "no") if load_best_model_at_end is None else load_best_model_at_end,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        dataset_text_field="text",
        packing=False,
        gradient_checkpointing=True,
    )

    signature = inspect.signature(SFTConfig.__init__).parameters
    if "max_length" in signature:
        kwargs["max_length"] = max_length
    elif "max_seq_length" in signature:
        kwargs["max_seq_length"] = max_length
    if "gradient_checkpointing_kwargs" in signature:
        kwargs["gradient_checkpointing_kwargs"] = {"use_reentrant": True}

    return SFTConfig(**kwargs)



def build_sft_trainer(model, tokenizer, train_dataset, eval_dataset, args):
    _, SFTTrainer = import_trl()
    trainer_kwargs = dict(
        model=model,
        train_dataset=train_dataset,
        args=args,
    )
    if eval_dataset is not None:
        trainer_kwargs["eval_dataset"] = eval_dataset
    signature = inspect.signature(SFTTrainer.__init__).parameters
    if "processing_class" in signature:
        trainer_kwargs["processing_class"] = tokenizer
    else:
        trainer_kwargs["tokenizer"] = tokenizer
    return SFTTrainer(**trainer_kwargs)



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



def load_lora_model(
    base_model_path: str,
    config,
    *,
    load_in_4bit: bool,
    lora_r: int,
    lora_alpha: int,
    lora_dropout: float,
    target_modules,
    adapter_path: str | Path | None = None,
):
    from peft import LoraConfig, PeftModel, get_peft_model
    from transformers import AutoModelForCausalLM

    # Keep the entire model on a concrete device and avoid any offload/meta path.
    if torch.cuda.is_available():
        model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            config=config,
            trust_remote_code=True,
            device_map={"": 0},
            local_files_only=True,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            config=config,
            trust_remote_code=True,
            local_files_only=True,
            low_cpu_mem_usage=False,
        )
    apply_nemotron_runtime_patches(model)

    if adapter_path is not None:
        model = PeftModel.from_pretrained(model, str(adapter_path), is_trainable=True)
    else:
        lora_kwargs = dict(
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=target_modules,
            inference_mode=False,
        )
        if "use_rslora" in inspect.signature(LoraConfig.__init__).parameters:
            lora_kwargs["use_rslora"] = True
        model = get_peft_model(model, LoraConfig(**lora_kwargs))

    if torch.cuda.is_available():
        model.to(torch.device("cuda:0"))
    else:
        model.to(torch.device("cpu"))

    model.config.use_cache = False
    try:
        model.print_trainable_parameters()
    except Exception:
        pass
    return model



def _load_adapter_weights(path: Path) -> dict[str, torch.Tensor]:
    if path.name.endswith(".safetensors"):
        from safetensors.torch import load_file

        return load_file(str(path), device="cpu")
    return torch.load(path, map_location="cpu")



def _save_adapter_weights(state: dict[str, torch.Tensor], path: Path) -> None:
    if path.name.endswith(".safetensors"):
        from safetensors.torch import save_file

        save_file(state, str(path))
        return
    torch.save(state, path)



def _resolve_adapter_weight_path(adapter_dir: Path) -> Path:
    candidates = [
        adapter_dir / "adapter_model.safetensors",
        adapter_dir / "adapter_model.bin",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No adapter weights found in {adapter_dir}")



def merge_adapter_directories(
    adapter_dirs: list[Path | str],
    output_dir: Path | str,
    weights: list[float] | None = None,
) -> Path:
    paths = [Path(path) for path in adapter_dirs]
    if not paths:
        raise ValueError("adapter_dirs must not be empty")

    if weights is None:
        weights = [1.0 / len(paths)] * len(paths)
    if len(weights) != len(paths):
        raise ValueError("weights must have the same length as adapter_dirs")

    total = float(sum(weights))
    if total <= 0:
        raise ValueError("weights must sum to a positive value")
    norm_weights = [float(weight) / total for weight in weights]

    ref_weight_path = _resolve_adapter_weight_path(paths[0])
    ref_state = _load_adapter_weights(ref_weight_path)
    merged = {key: tensor.float() * norm_weights[0] for key, tensor in ref_state.items()}

    for path, weight in zip(paths[1:], norm_weights[1:]):
        state = _load_adapter_weights(_resolve_adapter_weight_path(path))
        if state.keys() != ref_state.keys():
            missing = sorted(set(ref_state) ^ set(state))
            raise ValueError(f"Adapter key mismatch for {path}: {missing[:10]}")
        for key in merged:
            merged[key] = merged[key] + state[key].float() * weight

    output_dir = Path(output_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(paths[0], output_dir)

    final_state = {key: value.to(ref_state[key].dtype) for key, value in merged.items()}
    out_weight_path = _resolve_adapter_weight_path(output_dir)
    _save_adapter_weights(final_state, out_weight_path)
    return output_dir



def package_adapter_dir(adapter_dir: Path, submission_zip: Path) -> dict[str, Any]:
    adapter_dir = Path(adapter_dir)
    submission_zip = Path(submission_zip)
    submission_zip.parent.mkdir(parents=True, exist_ok=True)

    adapter_config_path = adapter_dir / "adapter_config.json"
    if not adapter_config_path.exists():
        raise FileNotFoundError("adapter_config.json not found")

    with adapter_config_path.open("r", encoding="utf-8") as handle:
        adapter_cfg = json.load(handle)

    if int(adapter_cfg["r"]) > 32:
        raise ValueError(f"LoRA rank must be <= 32, got {adapter_cfg['r']}")

    _resolve_adapter_weight_path(adapter_dir)

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



def save_adapter_submission(model, adapter_dir: Path, submission_zip: Path) -> dict[str, Any]:
    adapter_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(adapter_dir, safe_serialization=True)
    return package_adapter_dir(adapter_dir, submission_zip)



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

# ==========================================
# Version entrypoint
# ==========================================

import inspect
import json
from pathlib import Path

import pandas as pd
from transformers import EarlyStoppingCallback, Trainer, TrainingArguments


def build_runtime_settings() -> dict[str, Any]:
    profile = detect_runtime_profile()
    settings: dict[str, Any] = {
        "profile": profile,
        "train_batch_size": 1,
        "eval_batch_size": 1,
        "grad_accum_steps": 16,
        "stage1_epochs": 0.75,
        "stage2_epochs": 0.25,
        "stage1_learning_rate": 2.2e-4,
        "stage2_learning_rate": 1.5e-4,
        "stage1_max_steps": 360,
        "stage2_max_steps": 120,
        "hard_boost_frac": 0.50,
        "format_boost_frac": 0.50,
        "eval_steps": 25,
        "save_steps": 25,
        "post_train_eval_samples": 64,
    }
    if profile == "blackwell":
        settings.update(
            train_batch_size=2,
            grad_accum_steps=8,
            stage1_epochs=0.75,
            stage2_epochs=0.25,
            stage1_max_steps=360,
            stage2_max_steps=120,
            hard_boost_frac=0.50,
            format_boost_frac=0.50,
        )
    elif profile == "a6000":
        settings.update(
            train_batch_size=1,
            grad_accum_steps=16,
            stage1_epochs=0.60,
            stage2_epochs=0.20,
            stage1_max_steps=280,
            stage2_max_steps=90,
            hard_boost_frac=0.35,
            format_boost_frac=0.50,
        )
    return settings


RUNTIME_SETTINGS = build_runtime_settings()
RUNTIME_PROFILE = str(RUNTIME_SETTINGS["profile"])
SEED = 42
VAL_RATIO = 0.10
MAX_LENGTH = 384
STAGE1_EPOCHS = float(RUNTIME_SETTINGS["stage1_epochs"])
STAGE2_EPOCHS = float(RUNTIME_SETTINGS["stage2_epochs"])
STAGE1_LEARNING_RATE = float(RUNTIME_SETTINGS["stage1_learning_rate"])
STAGE2_LEARNING_RATE = float(RUNTIME_SETTINGS["stage2_learning_rate"])
STAGE1_MAX_STEPS = int(RUNTIME_SETTINGS["stage1_max_steps"])
STAGE2_MAX_STEPS = int(RUNTIME_SETTINGS["stage2_max_steps"])
TRAIN_BATCH_SIZE = int(RUNTIME_SETTINGS["train_batch_size"])
EVAL_BATCH_SIZE = int(RUNTIME_SETTINGS["eval_batch_size"])
GRAD_ACCUM_STEPS = int(RUNTIME_SETTINGS["grad_accum_steps"])
WARMUP_RATIO = 0.10
WEIGHT_DECAY = 0.0
MAX_GRAD_NORM = 0.3
LORA_R = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05
LOAD_IN_4BIT = False
HARD_MIN_SCORE = 3
HARD_BOOST_FRAC = float(RUNTIME_SETTINGS["hard_boost_frac"])
FORMAT_BOOST_FRAC = float(RUNTIME_SETTINGS["format_boost_frac"])
FOCUS_ANSWER_TYPES = {"symbolic_or_other", "multiword_text", "8bit_binary"}

OUTPUT_ROOT = Path("/kaggle/working/nemotron_v4_hard_mining")
ADAPTER_DIR = OUTPUT_ROOT / "adapter"
SUBMISSION_ZIP = Path("/kaggle/working/submission_v4.zip")
OFFLOAD_DIR = Path(os.environ.get("NEMOTRON_OFFLOAD_DIR", "/tmp/nemotron_offload"))
REPO_ROOT = "/kaggle/input"
TRAIN_PATH = "/kaggle/input/nvidia-nemotron-3-reasoning-challenge/train.csv"
BASE_MODEL = "/kaggle/input/models/metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1"
RUN_POST_TRAIN_EVAL = os.environ.get("NEMOTRON_RUN_POST_TRAIN_EVAL", "0") == "1"
POST_TRAIN_EVAL_SAMPLES = int(RUNTIME_SETTINGS["post_train_eval_samples"])
EVAL_STEPS = int(RUNTIME_SETTINGS["eval_steps"])
SAVE_STEPS = int(RUNTIME_SETTINGS["save_steps"])


def build_training_arguments(
    output_dir: Path,
    num_train_epochs: float,
    learning_rate: float,
    *,
    max_steps: int | None = None,
) -> TrainingArguments:
    kwargs = dict(
        output_dir=str(output_dir),
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        logging_steps=10,
        bf16=True,
        fp16=False,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        warmup_ratio=WARMUP_RATIO,
        weight_decay=WEIGHT_DECAY,
        max_grad_norm=MAX_GRAD_NORM,
        gradient_checkpointing=True,
        remove_unused_columns=False,
        report_to="none",
        dataloader_num_workers=2,
    )
    signature = inspect.signature(TrainingArguments.__init__).parameters
    strategy_key = "evaluation_strategy" if "evaluation_strategy" in signature else "eval_strategy" if "eval_strategy" in signature else None
    if strategy_key is not None:
        kwargs[strategy_key] = "steps"
    if "eval_steps" in signature:
        kwargs["eval_steps"] = EVAL_STEPS
    if "save_strategy" in signature:
        kwargs["save_strategy"] = "steps"
    if "save_steps" in signature:
        kwargs["save_steps"] = SAVE_STEPS
    if "save_total_limit" in signature:
        kwargs["save_total_limit"] = 1
    if "load_best_model_at_end" in signature:
        kwargs["load_best_model_at_end"] = True
    if "metric_for_best_model" in signature:
        kwargs["metric_for_best_model"] = "eval_loss"
    if "greater_is_better" in signature:
        kwargs["greater_is_better"] = False
    if "group_by_length" in signature:
        kwargs["group_by_length"] = True
    if max_steps is not None and "max_steps" in signature:
        kwargs["max_steps"] = max_steps
    if "gradient_checkpointing_kwargs" in signature:
        kwargs["gradient_checkpointing_kwargs"] = {"use_reentrant": False}
    return TrainingArguments(**kwargs)


def main() -> None:
    set_global_seed(SEED)
    maybe_apply_triton_environment_fixes()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    OFFLOAD_DIR.mkdir(parents=True, exist_ok=True)

    base_model_path = resolve_base_model_path(BASE_MODEL, use_kagglehub=True)
    print("Base model:", base_model_path)
    print(
        json.dumps(
            {
                "runtime_profile": RUNTIME_PROFILE,
                "train_batch_size": TRAIN_BATCH_SIZE,
                "grad_accum_steps": GRAD_ACCUM_STEPS,
                "stage1_epochs": STAGE1_EPOCHS,
                "stage2_epochs": STAGE2_EPOCHS,
                "stage1_max_steps": STAGE1_MAX_STEPS,
                "stage2_max_steps": STAGE2_MAX_STEPS,
                "hard_boost_frac": HARD_BOOST_FRAC,
                "format_boost_frac": FORMAT_BOOST_FRAC,
            },
            indent=2,
            ensure_ascii=False,
        )
    )

    train_df = add_difficulty_features(pd.read_csv(TRAIN_PATH))
    tr_df, val_df = stratified_train_val_split(train_df, val_ratio=VAL_RATIO, seed=SEED)
    tr_df = add_difficulty_features(tr_df)
    val_df = add_difficulty_features(val_df)

    hard_df = tr_df[tr_df["difficulty_score"] >= HARD_MIN_SCORE].copy().reset_index(drop=True)
    format_df = tr_df[tr_df["answer_type"].isin(FOCUS_ANSWER_TYPES)].copy().reset_index(drop=True)
    hard_val_df = val_df[val_df["difficulty_score"] >= HARD_MIN_SCORE].copy().reset_index(drop=True)
    if len(hard_val_df) == 0:
        hard_val_df = val_df.copy().reset_index(drop=True)

    stage1_parts = [tr_df]
    if HARD_BOOST_FRAC > 0 and len(hard_df) > 0:
        stage1_parts.append(hard_df.sample(frac=HARD_BOOST_FRAC, random_state=SEED))
    if FORMAT_BOOST_FRAC > 0 and len(format_df) > 0:
        stage1_parts.append(format_df.sample(frac=FORMAT_BOOST_FRAC, random_state=SEED + 1))
    stage1_df = pd.concat(stage1_parts, ignore_index=True).sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    focus_mask = (tr_df["difficulty_score"] >= HARD_MIN_SCORE) | tr_df["answer_type"].isin(FOCUS_ANSWER_TYPES)
    stage2_df = tr_df[focus_mask].copy().reset_index(drop=True)
    if len(stage2_df) == 0:
        stage2_df = tr_df.copy().reset_index(drop=True)

    print_split_summary("train_stage1_boosted", stage1_df)
    print_split_summary("train_stage2_focus", stage2_df)
    print_split_summary("valid", val_df)
    print_split_summary("valid_hard", hard_val_df)

    config, tokenizer = load_tokenizer(base_model_path)
    collator = CompletionOnlyCollator(tokenizer)
    stage1_train_ds = build_completion_only_dataset(tokenizer, stage1_df, MAX_LENGTH)
    stage2_train_ds = build_completion_only_dataset(tokenizer, stage2_df, MAX_LENGTH)
    val_ds = build_completion_only_dataset(tokenizer, val_df, MAX_LENGTH)
    hard_val_ds = build_completion_only_dataset(tokenizer, hard_val_df, MAX_LENGTH)

    model = load_lora_model(
        base_model_path,
        config,
        load_in_4bit=LOAD_IN_4BIT,
        lora_r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES_EXPLICIT,
    )

    stage1_trainer = Trainer(
        model=model,
        args=build_training_arguments(
            OUTPUT_ROOT / "stage1",
            STAGE1_EPOCHS,
            STAGE1_LEARNING_RATE,
            max_steps=STAGE1_MAX_STEPS,
        ),
        train_dataset=stage1_train_ds,
        eval_dataset=val_ds,
        data_collator=collator,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=4, early_stopping_threshold=0.002)],
    )
    print("Stage 1 boosted full training...")
    stage1_trainer.train()
    cleanup_checkpoints(OUTPUT_ROOT / "stage1")

    stage2_trainer = Trainer(
        model=stage1_trainer.model,
        args=build_training_arguments(
            OUTPUT_ROOT / "stage2",
            STAGE2_EPOCHS,
            STAGE2_LEARNING_RATE,
            max_steps=STAGE2_MAX_STEPS,
        ),
        train_dataset=stage2_train_ds,
        eval_dataset=hard_val_ds,
        data_collator=collator,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=4, early_stopping_threshold=0.002)],
    )
    print("Stage 2 hard-example polish...")
    stage2_trainer.train()

    print("Saving adapter and packaging submission...")
    adapter_cfg = save_adapter_submission(stage2_trainer.model, ADAPTER_DIR, SUBMISSION_ZIP)
    print(json.dumps(adapter_cfg, indent=2, ensure_ascii=False))
    cleanup_checkpoints(OUTPUT_ROOT / "stage2")

    if RUN_POST_TRAIN_EVAL:
        quick_validate(
            stage2_trainer.model,
            tokenizer,
            hard_val_df,
            OUTPUT_ROOT / "quick_val_hard_predictions.csv",
            max_samples=POST_TRAIN_EVAL_SAMPLES,
        )

    summary = {
        "train_rows": len(tr_df),
        "valid_rows": len(val_df),
        "stage1_rows": len(stage1_df),
        "stage2_rows": len(stage2_df),
        "hard_valid_rows": len(hard_val_df),
        "hard_min_score": HARD_MIN_SCORE,
        "focus_answer_types": sorted(FOCUS_ANSWER_TYPES),
        "max_length": MAX_LENGTH,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "submission_zip": str(SUBMISSION_ZIP),
    }
    with (OUTPUT_ROOT / "run_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
