from __future__ import annotations

import inspect
import json
from pathlib import Path

import pandas as pd
import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

from nemotron_reasoning_common import (
    EASY_TEMPLATES,
    HARD_TEMPLATES,
    add_dataset_features,
    apply_nemotron_runtime_patches,
    build_sft_dataset,
    load_tokenizer,
    maybe_apply_triton_environment_fixes,
    print_split_summary,
    quick_validate,
    resolve_base_model_path,
    save_adapter_submission,
    set_global_seed,
    stratified_train_val_split,
)

# =========================================================
# Nemotron Reasoning Challenge - Score-Seeking Alt Version
# =========================================================
# More aggressive variant inspired by higher-scoring notebook baselines:
# - Uses TRL SFTTrainer.
# - Uses all-linear LoRA targeting.
# - Uses a dataset-shaped curriculum (easy templates -> full dataset -> hard templates).
# - Defaults to bf16 full-model LoRA like the stronger notebook variants.
#   Set LOAD_IN_4BIT=True if you need a more memory-efficient run.
# - Shrinks sequence length to match the short-context dataset.

SEED = 42
VAL_RATIO = 0.10
MAX_LENGTH = 384
STAGE1_EPOCHS = 0.35
STAGE2_EPOCHS = 1.25
STAGE3_EPOCHS = 0.35
LEARNING_RATE = 2.0e-4
GRAD_ACCUM_STEPS = 8
TRAIN_BATCH_SIZE = 1
EVAL_BATCH_SIZE = 1
WARMUP_RATIO = 0.10
MAX_GRAD_NORM = 1.0
LORA_R = 32
LORA_ALPHA = 64
LORA_DROPOUT = 0.05
LOAD_IN_4BIT = False

OUTPUT_ROOT = Path("/kaggle/working/nemotron_alt_sft")
ADAPTER_DIR = OUTPUT_ROOT / "adapter"
SUBMISSION_ZIP = Path("/kaggle/working/submission_alt_v2.zip")
REPO_ROOT = Path(__file__).resolve().parents[3]
TRAIN_PATH = REPO_ROOT / "data/train.csv"
BASE_MODEL = REPO_ROOT / "1"
RUN_POST_TRAIN_EVAL = True
POST_TRAIN_EVAL_SAMPLES = 128
EVAL_STEPS = 100
SAVE_STEPS = 100



def _import_trl():
    try:
        from trl import SFTConfig, SFTTrainer
    except ImportError as exc:
        raise ImportError(
            "trl is required for the alternate version. Install it as in baseline/start.ipynb or baseline/nvidia-nemotron-sfttrainer-training.ipynb."
        ) from exc
    return SFTConfig, SFTTrainer



def build_sft_config(output_dir: Path, num_train_epochs: float, save_strategy: str, evaluation_strategy: str):
    SFTConfig, _ = _import_trl()
    kwargs = dict(
        output_dir=str(output_dir),
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,
        num_train_epochs=num_train_epochs,
        learning_rate=LEARNING_RATE,
        logging_steps=10,
        bf16=True,
        max_grad_norm=MAX_GRAD_NORM,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        warmup_ratio=WARMUP_RATIO,
        save_strategy=save_strategy,
        evaluation_strategy=evaluation_strategy,
        eval_steps=EVAL_STEPS,
        save_steps=SAVE_STEPS,
        save_total_limit=2,
        load_best_model_at_end=(evaluation_strategy != "no"),
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        dataset_text_field="text",
        packing=False,
        gradient_checkpointing=True,
    )

    signature = inspect.signature(SFTConfig.__init__).parameters
    if "max_length" in signature:
        kwargs["max_length"] = MAX_LENGTH
    elif "max_seq_length" in signature:
        kwargs["max_seq_length"] = MAX_LENGTH
    if "gradient_checkpointing_kwargs" in signature:
        kwargs["gradient_checkpointing_kwargs"] = {"use_reentrant": True}

    return SFTConfig(**kwargs)



def build_sft_trainer(model, tokenizer, train_dataset, eval_dataset, args):
    _, SFTTrainer = _import_trl()
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



def load_model(base_model_path: str, config):
    if LOAD_IN_4BIT:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
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
    else:
        model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            config=config,
            trust_remote_code=True,
            device_map="auto",
            local_files_only=True,
            torch_dtype=torch.bfloat16,
        )
        apply_nemotron_runtime_patches(model)

    lora_kwargs = dict(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules="all-linear",
        inference_mode=False,
    )
    if "use_rslora" in inspect.signature(LoraConfig.__init__).parameters:
        lora_kwargs["use_rslora"] = True

    model = get_peft_model(model, LoraConfig(**lora_kwargs))
    model.config.use_cache = False
    try:
        model.print_trainable_parameters()
    except Exception:
        pass
    return model



def main() -> None:
    set_global_seed(SEED)
    maybe_apply_triton_environment_fixes()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

    base_model_path = resolve_base_model_path(BASE_MODEL, use_kagglehub=True)
    print("Base model:", base_model_path)

    train_df = pd.read_csv(TRAIN_PATH)
    train_df = add_dataset_features(train_df)
    tr_df, val_df = stratified_train_val_split(train_df, val_ratio=VAL_RATIO, seed=SEED)

    easy_stage_df = tr_df[tr_df["template"].isin(EASY_TEMPLATES)].copy().reset_index(drop=True)
    hard_stage_df = tr_df[tr_df["template"].isin(HARD_TEMPLATES)].copy().reset_index(drop=True)

    print_split_summary("train_full", tr_df)
    print_split_summary("train_stage1_easy", easy_stage_df)
    print_split_summary("train_stage3_hard", hard_stage_df)
    print_split_summary("valid", val_df)

    config, tokenizer = load_tokenizer(base_model_path)
    model = load_model(base_model_path, config)

    full_train_ds = build_sft_dataset(tr_df, tokenizer)
    val_ds = build_sft_dataset(val_df, tokenizer)

    if len(easy_stage_df) > 0:
        easy_train_ds = build_sft_dataset(easy_stage_df, tokenizer)
        stage1_args = build_sft_config(
            OUTPUT_ROOT / "stage1",
            num_train_epochs=STAGE1_EPOCHS,
            save_strategy="no",
            evaluation_strategy="no",
        )
        stage1_trainer = build_sft_trainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=easy_train_ds,
            eval_dataset=None,
            args=stage1_args,
        )
        print("Stage 1 curriculum training (easy templates)...")
        stage1_trainer.train()

    stage2_args = build_sft_config(
        OUTPUT_ROOT / "stage2",
        num_train_epochs=STAGE2_EPOCHS,
        save_strategy="steps",
        evaluation_strategy="steps",
    )
    stage2_trainer = build_sft_trainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=full_train_ds,
        eval_dataset=val_ds,
        args=stage2_args,
    )

    print("Stage 2 full-dataset training...")
    stage2_trainer.train()

    if STAGE3_EPOCHS > 0 and len(hard_stage_df) > 0:
        hard_train_ds = build_sft_dataset(hard_stage_df, tokenizer)
        stage3_args = build_sft_config(
            OUTPUT_ROOT / "stage3",
            num_train_epochs=STAGE3_EPOCHS,
            save_strategy="steps",
            evaluation_strategy="steps",
        )
        stage3_trainer = build_sft_trainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=hard_train_ds,
            eval_dataset=val_ds,
            args=stage3_args,
        )
        print("Stage 3 hard-template polish...")
        stage3_trainer.train()
        final_model = stage3_trainer.model
    else:
        final_model = stage2_trainer.model

    print("Saving adapter and packaging submission...")
    adapter_cfg = save_adapter_submission(final_model, ADAPTER_DIR, SUBMISSION_ZIP)
    print(json.dumps(adapter_cfg, indent=2, ensure_ascii=False))

    if RUN_POST_TRAIN_EVAL:
        quick_validate(
            final_model,
            tokenizer,
            val_df,
            OUTPUT_ROOT / "quick_val_predictions.csv",
            max_samples=POST_TRAIN_EVAL_SAMPLES,
        )

    summary = {
        "train_rows": len(tr_df),
        "valid_rows": len(val_df),
        "stage1_rows": len(easy_stage_df),
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "learning_rate": LEARNING_RATE,
        "stage1_epochs": STAGE1_EPOCHS,
        "stage2_epochs": STAGE2_EPOCHS,
        "stage3_epochs": STAGE3_EPOCHS,
        "stage3_rows": len(hard_stage_df),
        "load_in_4bit": LOAD_IN_4BIT,
        "submission_zip": str(SUBMISSION_ZIP),
    }
    with (OUTPUT_ROOT / "run_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
