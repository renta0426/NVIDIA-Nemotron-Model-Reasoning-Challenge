from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_CSV = Path(__file__).resolve().parent / "rule_based_verified_600_training_data.csv"
DEFAULT_OUTPUT_DIR = Path("/kaggle/working/adapter")
SUBSAMPLE_SIZE = 600
LORA_RANK = 32
MAX_SEQ_LEN = 2048
NUM_EPOCHS = 2
BATCH_SIZE = 1
GRAD_ACCUM = 4
LR = 1e-4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Baseline-compatible training script that reads a prebuilt external CSV with "
            "columns id,prompt,answer,generated_cot,label and keeps the baseline template/config."
        )
    )
    parser.add_argument("--dataset-csv", type=Path, default=DEFAULT_DATASET_CSV)
    parser.add_argument("--model-path", type=str, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_training_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    required = {"id", "prompt", "answer", "generated_cot", "label"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    if len(frame) != SUBSAMPLE_SIZE:
        raise ValueError(f"Expected {SUBSAMPLE_SIZE} rows in {path}, found {len(frame)}")
    if frame[list(sorted(required))].isnull().any().any():
        raise ValueError(f"Null values detected in required columns: {path}")
    return frame


def import_training_stack() -> dict[str, object]:
    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    return {
        "torch": torch,
        "Dataset": Dataset,
        "LoraConfig": LoraConfig,
        "TaskType": TaskType,
        "get_peft_model": get_peft_model,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "SFTConfig": SFTConfig,
        "SFTTrainer": SFTTrainer,
    }


def patch_runtime() -> None:
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    try:
        import triton.backends.nvidia.compiler as nv_compiler
    except Exception:
        return
    os.environ.setdefault("TRITON_PTXAS_BLACKWELL_PATH", "/tmp/ptxas-blackwell")
    nv_compiler.get_ptxas_version = lambda arch: "12.0"
    for name, mod in sys.modules.items():
        if "modeling_nemotron_h" in name:
            mod.is_fast_path_available = False


def build_training_text_builder(tokenizer: object):
    def build_training_text(example: dict[str, str]) -> dict[str, str]:
        prompt = example["prompt"]
        answer = example["answer"]
        cot = example["generated_cot"]
        user_msg = prompt + "\nPut your final answer inside \\boxed{}."
        assistant_msg = f"{cot}\n\n\\boxed{{{answer}}}"
        try:
            messages = [
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg},
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        except Exception:
            text = (
                f"<|im_start|>user\n{user_msg}<|im_end|>\n"
                f"<|im_start|>assistant\n{assistant_msg}<|im_end|>"
            )
        return {"text": text}

    return build_training_text


def train(args: argparse.Namespace) -> None:
    frame = load_training_frame(args.dataset_csv)
    stack = import_training_stack()
    patch_runtime()
    tokenizer = stack["AutoTokenizer"].from_pretrained(args.model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    dataset = stack["Dataset"].from_pandas(frame)
    dataset = dataset.map(build_training_text_builder(tokenizer), remove_columns=dataset.column_names)

    if args.dry_run:
        sample = dataset[0]["text"]
        print(f"Dry run OK: {len(frame)} rows loaded from {args.dataset_csv}")
        print(sample[:600])
        return

    torch = stack["torch"]
    model = stack["AutoModelForCausalLM"].from_pretrained(
        args.model_path,
        device_map={"": 0},
        trust_remote_code=True,
        dtype=torch.bfloat16,
    )
    model.gradient_checkpointing_enable()
    lora_config = stack["LoraConfig"](
        r=LORA_RANK,
        lora_alpha=32,
        target_modules="all-linear",
        lora_dropout=0.05,
        bias="none",
        task_type=stack["TaskType"].CAUSAL_LM,
    )
    model = stack["get_peft_model"](model, lora_config)
    training_args = stack["SFTConfig"](
        output_dir=str(args.output_dir),
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LR,
        logging_steps=5,
        bf16=True,
        max_grad_norm=1.0,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        save_strategy="no",
        report_to="none",
        dataset_text_field="text",
        max_length=MAX_SEQ_LEN,
        packing=False,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )
    trainer = stack["SFTTrainer"](
        model=model,
        train_dataset=dataset,
        processing_class=tokenizer,
        args=training_args,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    print("Starting training...")
    trainer.train()
    trainer.model.save_pretrained(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    print(f"Adapter saved to {args.output_dir}")


def main() -> None:
    args = parse_args()
    train(args)


if __name__ == "__main__":
    main()