from __future__ import annotations

import inspect
import json
import os
from pathlib import Path

import pandas as pd
import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    EarlyStoppingCallback,
    TrainingArguments,
    Trainer,
)

from nemotron_reasoning_common import (
    HARD_TEMPLATES,
    TARGET_MODULES_EXPLICIT,
    CompletionOnlyCollator,
    add_dataset_features,
    apply_nemotron_runtime_patches,
    build_completion_only_dataset,
    load_tokenizer,
    maybe_apply_triton_environment_fixes,
    print_split_summary,
    quick_validate,
    resolve_base_model_path,
    save_adapter_submission,
    set_global_seed,
    stratified_train_val_split,
)

# ==========================================
# Nemotron Reasoning Challenge - QLoRA v1
# ==========================================
# Practical improvement over the current baseline:
# - Keeps the metric-aligned prompt exactly unchanged.
# - Uses a template-aware validation split.
# - Removes the severe 100-step undertraining cap.
# - Stays close to the existing ~30 GB memory envelope.
# - Shrinks sequence length to match the short-context dataset.

SEED = 42
VAL_RATIO = 0.10
MAX_LENGTH = 384
NUM_EPOCHS = 1.0
LEARNING_RATE = 2.5e-4
TRAIN_BATCH_SIZE = 1
EVAL_BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
WARMUP_RATIO = 0.10
WEIGHT_DECAY = 0.0
MAX_GRAD_NORM = 0.3

LORA_R = 24
LORA_ALPHA = 48
LORA_DROPOUT = 0.05

OUTPUT_ROOT = Path("/kaggle/working/nemotron_q_lora_v1")
ADAPTER_DIR = OUTPUT_ROOT / "adapter"
SUBMISSION_ZIP = Path("/kaggle/working/submission_v1.zip")
REPO_ROOT = Path(__file__).resolve().parents[3]
TRAIN_PATH = REPO_ROOT / "data/train.csv"
BASE_MODEL = REPO_ROOT / "1"
RUN_POST_TRAIN_EVAL = True
POST_TRAIN_EVAL_SAMPLES = 128
EVAL_STEPS = 100
SAVE_STEPS = 100
HARD_TEMPLATE_BOOST_FRAC = 0.50



def build_training_arguments() -> TrainingArguments:
    kwargs = dict(
        output_dir=str(OUTPUT_ROOT / "checkpoints"),
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        evaluation_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        logging_steps=10,
        bf16=True,
        fp16=False,
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        warmup_ratio=WARMUP_RATIO,
        weight_decay=WEIGHT_DECAY,
        max_grad_norm=MAX_GRAD_NORM,
        gradient_checkpointing=True,
        group_by_length=True,
        remove_unused_columns=False,
        report_to="none",
        dataloader_num_workers=2,
    )
    if "gradient_checkpointing_kwargs" in inspect.signature(TrainingArguments.__init__).parameters:
        kwargs["gradient_checkpointing_kwargs"] = {"use_reentrant": False}
    return TrainingArguments(**kwargs)



def main() -> None:
    set_global_seed(SEED)
    maybe_apply_triton_environment_fixes()

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

    print("Torch:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    base_model_path = resolve_base_model_path(BASE_MODEL, use_kagglehub=True)
    print("Base model:", base_model_path)

    train_df = pd.read_csv(TRAIN_PATH)
    train_df = add_dataset_features(train_df)
    tr_df, val_df = stratified_train_val_split(train_df, val_ratio=VAL_RATIO, seed=SEED)
    hard_boost_df = tr_df[tr_df["template"].isin(HARD_TEMPLATES)]
    if HARD_TEMPLATE_BOOST_FRAC > 0 and len(hard_boost_df) > 0:
        hard_boost_df = hard_boost_df.sample(frac=HARD_TEMPLATE_BOOST_FRAC, random_state=SEED)
        tr_df = (
            pd.concat([tr_df, hard_boost_df], ignore_index=True)
            .sample(frac=1.0, random_state=SEED)
            .reset_index(drop=True)
        )
        print(f"Applied hard-template boost: +{len(hard_boost_df)} rows")

    print_split_summary("train", tr_df)
    print_split_summary("valid", val_df)

    config, tokenizer = load_tokenizer(base_model_path)

    train_ds = build_completion_only_dataset(tokenizer, tr_df, MAX_LENGTH)
    val_ds = build_completion_only_dataset(tokenizer, val_df, MAX_LENGTH)
    collator = CompletionOnlyCollator(tokenizer)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    print("Loading base model in 4-bit...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        config=config,
        trust_remote_code=True,
        device_map="auto",
        local_files_only=True,
        quantization_config=bnb_config,
    )

    apply_nemotron_runtime_patches(model)
    model = prepare_model_for_kbit_training(model)

    lora_kwargs = dict(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=TARGET_MODULES_EXPLICIT,
        inference_mode=False,
    )
    if "use_rslora" in inspect.signature(LoraConfig.__init__).parameters:
        lora_kwargs["use_rslora"] = True

    peft_config = LoraConfig(**lora_kwargs)
    model = get_peft_model(model, peft_config)
    try:
        model.print_trainable_parameters()
    except Exception:
        pass

    trainer = Trainer(
        model=model,
        args=build_training_arguments(),
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=collator,
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=4,
                early_stopping_threshold=0.002,
            )
        ],
    )

    print("Start training v1...")
    trainer.train()

    print("Saving adapter and packaging submission...")
    adapter_cfg = save_adapter_submission(trainer.model, ADAPTER_DIR, SUBMISSION_ZIP)
    print(json.dumps(adapter_cfg, indent=2, ensure_ascii=False))

    if RUN_POST_TRAIN_EVAL:
        quick_validate(
            trainer.model,
            tokenizer,
            val_df,
            OUTPUT_ROOT / "quick_val_predictions.csv",
            max_samples=POST_TRAIN_EVAL_SAMPLES,
        )

    summary = {
        "train_rows": len(tr_df),
        "valid_rows": len(val_df),
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "learning_rate": LEARNING_RATE,
        "val_ratio": VAL_RATIO,
        "max_length": MAX_LENGTH,
        "submission_zip": str(SUBMISSION_ZIP),
    }
    with (OUTPUT_ROOT / "run_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
