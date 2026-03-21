#!/usr/bin/env python3
"""
finetune.py — Darshana LoRA Fine-Tuning Pipeline
=================================================

Fine-tunes open-source LLMs into specialized darshana reasoning engines
using LoRA (Low-Rank Adaptation). Produces lightweight adapters that bolt
onto a base model without modifying its weights.

Usage:
    # Single darshana
    python training/finetune.py --darshana nyaya --base-model meta-llama/Llama-3.2-3B-Instruct

    # All six darshanas
    python training/finetune.py --all --base-model meta-llama/Llama-3.2-3B-Instruct

    # Router model (Buddhi layer)
    python training/finetune.py --router --base-model meta-llama/Llama-3.2-3B-Instruct

    # Vritti classifier
    python training/finetune.py --vritti --base-model meta-llama/Llama-3.2-3B-Instruct

    # Resume from checkpoint
    python training/finetune.py --darshana nyaya --resume training/adapters/nyaya/checkpoint-400

Architecture reference: THESIS.md — Shaddarshana Engines layer.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import yaml
import torch
from datasets import Dataset, load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"
DATA_DIR = SCRIPT_DIR / "data"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "adapters"

DARSHANAS = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]

# VRAM estimates (GB) per model size with 4-bit quantization + LoRA
VRAM_ESTIMATES = {
    "3B": {"load": 4, "train": 6, "time_per_epoch_1k": "~8 min"},
    "7B": {"load": 6, "train": 10, "time_per_epoch_1k": "~18 min"},
    "8B": {"load": 7, "train": 12, "time_per_epoch_1k": "~22 min"},
    "13B": {"load": 10, "train": 18, "time_per_epoch_1k": "~40 min"},
}


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """Load YAML configuration, falling back to defaults if missing."""
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {
        "base_model": "meta-llama/Llama-3.2-3B-Instruct",
        "lora": {"rank": 16, "alpha": 32, "dropout": 0.05,
                 "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"]},
        "training": {"epochs": 3, "batch_size": 4, "learning_rate": 2e-4,
                     "warmup_steps": 100, "max_length": 2048,
                     "gradient_accumulation_steps": 4},
        "quantization": {"load_in_4bit": True},
    }


# ---------------------------------------------------------------------------
# VRAM / time estimation
# ---------------------------------------------------------------------------

def estimate_resources(model_name: str, data_path: Path, epochs: int) -> None:
    """Print estimated VRAM and training time before starting."""
    # Detect model size from name
    size_key = "7B"  # default
    for key in ["3B", "7B", "8B", "13B"]:
        if key.lower() in model_name.lower() or key in model_name:
            size_key = key
            break

    est = VRAM_ESTIMATES.get(size_key, VRAM_ESTIMATES["7B"])

    # Count training examples
    n_examples = 0
    if data_path.exists():
        with open(data_path) as f:
            n_examples = sum(1 for _ in f)

    print("\n" + "=" * 60)
    print("RESOURCE ESTIMATES")
    print("=" * 60)
    print(f"  Model:            {model_name} ({size_key} class)")
    print(f"  Training data:    {n_examples} examples from {data_path.name}")
    print(f"  Epochs:           {epochs}")
    print(f"  VRAM to load:     ~{est['load']} GB (4-bit quantized)")
    print(f"  VRAM to train:    ~{est['train']} GB (with LoRA gradients)")
    print(f"  Time per epoch:   {est['time_per_epoch_1k']} (per 1k examples, A100)")
    if n_examples > 0:
        scale = n_examples / 1000
        print(f"  Est. total time:  ~{int(scale * 8 * epochs)} - {int(scale * 22 * epochs)} min")
    print("=" * 60 + "\n")

    # Check available VRAM
    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_mem / (1024**3)
        print(f"  GPU detected:     {torch.cuda.get_device_name(0)}")
        print(f"  Available VRAM:   {vram_gb:.1f} GB")
        if vram_gb < est["train"]:
            print(f"  WARNING: {vram_gb:.1f} GB may be insufficient. "
                  f"Need ~{est['train']} GB. Consider reducing batch_size or max_length.")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        print("  GPU detected:     Apple MPS (Metal)")
        print("  NOTE: MPS works but is slower than CUDA. bitsandbytes 4-bit")
        print("        requires CUDA; training will use fp16/fp32 on MPS.")
    else:
        print("  WARNING: No GPU detected. Training on CPU will be very slow.")
    print()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_training_data(data_path: Path, tokenizer, max_length: int) -> Dataset:
    """
    Load and tokenize training data from JSONL.

    Expected JSONL format (chat-style):
        {"messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]}

    Or simple prompt/completion:
        {"prompt": "...", "completion": "..."}
    """
    if not data_path.exists():
        print(f"ERROR: Training data not found at {data_path}")
        print(f"Generate data first: python training/generate_data.py --darshana <name>")
        sys.exit(1)

    examples = []
    with open(data_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))

    if not examples:
        print(f"ERROR: No examples found in {data_path}")
        sys.exit(1)

    print(f"Loaded {len(examples)} training examples from {data_path.name}")

    def format_example(ex: dict) -> str:
        """Convert to chat format string for tokenization."""
        if "messages" in ex:
            # Chat format — use the tokenizer's chat template if available
            try:
                return tokenizer.apply_chat_template(
                    ex["messages"], tokenize=False, add_generation_prompt=False
                )
            except Exception:
                # Fallback: manual formatting
                parts = []
                for msg in ex["messages"]:
                    role = msg["role"]
                    content = msg["content"]
                    if role == "system":
                        parts.append(f"<|system|>\n{content}")
                    elif role == "user":
                        parts.append(f"<|user|>\n{content}")
                    elif role == "assistant":
                        parts.append(f"<|assistant|>\n{content}")
                return "\n".join(parts)
        elif "prompt" in ex and "completion" in ex:
            return f"{ex['prompt']}\n{ex['completion']}"
        else:
            raise ValueError(f"Unknown data format. Keys: {list(ex.keys())}")

    # Tokenize
    texts = [format_example(ex) for ex in examples]

    def tokenize_fn(batch):
        tokenized = tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    dataset = Dataset.from_dict({"text": texts})
    dataset = dataset.map(tokenize_fn, batched=True, remove_columns=["text"])

    return dataset


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_base_model(model_name: str, config: dict):
    """Load base model with 4-bit quantization (if CUDA available)."""
    use_4bit = config.get("quantization", {}).get("load_in_4bit", True)
    use_cuda = torch.cuda.is_available()

    quant_config = None
    if use_4bit and use_cuda:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        print(f"Loading {model_name} with 4-bit quantization (NF4)...")
    else:
        if use_4bit and not use_cuda:
            print("4-bit quantization requires CUDA. Loading in float16/float32...")
        else:
            print(f"Loading {model_name} without quantization...")

    # Determine dtype
    dtype = torch.float16 if (use_cuda or (hasattr(torch.backends, "mps")
                              and torch.backends.mps.is_available())) else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quant_config,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id

    return model, tokenizer


# ---------------------------------------------------------------------------
# LoRA setup
# ---------------------------------------------------------------------------

def setup_lora(model, config: dict):
    """Apply LoRA adapters to the model."""
    lora_cfg = config.get("lora", {})

    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_cfg.get("rank", 16),
        lora_alpha=lora_cfg.get("alpha", 32),
        lora_dropout=lora_cfg.get("dropout", 0.05),
        target_modules=lora_cfg.get("target_modules", ["q_proj", "v_proj", "k_proj", "o_proj"]),
        bias="none",
    )

    # Prepare for k-bit training if quantized
    if hasattr(model, "is_quantized") and model.is_quantized:
        model = prepare_model_for_kbit_training(model)

    model = get_peft_model(model, peft_config)

    # Print trainable parameters
    trainable, total = model.get_nb_trainable_parameters()
    pct = 100 * trainable / total if total > 0 else 0
    print(f"\nLoRA applied:")
    print(f"  Trainable params:  {trainable:,} / {total:,} ({pct:.2f}%)")
    print(f"  Rank:              {lora_cfg.get('rank', 16)}")
    print(f"  Alpha:             {lora_cfg.get('alpha', 32)}")
    print(f"  Target modules:    {lora_cfg.get('target_modules', [])}")
    print()

    return model


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_darshana(
    darshana: str,
    model_name: str,
    config: dict,
    resume_from: Optional[str] = None,
    epochs: Optional[int] = None,
    lr: Optional[float] = None,
    batch_size: Optional[int] = None,
    lora_rank: Optional[int] = None,
) -> Path:
    """
    Fine-tune a single darshana adapter.

    Args:
        darshana: Name of the darshana (or "router" / "vritti").
        model_name: HuggingFace model identifier.
        config: Loaded config dict.
        resume_from: Path to checkpoint to resume from.
        epochs: Override epochs from config.
        lr: Override learning rate from config.
        batch_size: Override batch size from config.
        lora_rank: Override LoRA rank from config.

    Returns:
        Path to the saved adapter directory.
    """
    train_cfg = config.get("training", {})
    _epochs = epochs or train_cfg.get("epochs", 3)
    _lr = lr or train_cfg.get("learning_rate", 2e-4)
    _batch_size = batch_size or train_cfg.get("batch_size", 4)

    if lora_rank:
        config.setdefault("lora", {})["rank"] = lora_rank

    # Data path
    data_path = DATA_DIR / f"{darshana}_train.jsonl"

    # Output path
    output_dir = Path(config.get("output_dir", DEFAULT_OUTPUT_DIR))
    if not output_dir.is_absolute():
        output_dir = SCRIPT_DIR.parent / output_dir
    adapter_dir = output_dir / darshana

    print(f"\n{'=' * 60}")
    print(f"FINE-TUNING: {darshana.upper()}")
    print(f"{'=' * 60}")
    print(f"  Base model:    {model_name}")
    print(f"  Data:          {data_path}")
    print(f"  Output:        {adapter_dir}")
    print(f"  Epochs:        {_epochs}")
    print(f"  Learning rate: {_lr}")
    print(f"  Batch size:    {_batch_size}")

    # Estimate resources
    estimate_resources(model_name, data_path, _epochs)

    # Load model and tokenizer
    model, tokenizer = load_base_model(model_name, config)

    # Apply LoRA
    model = setup_lora(model, config)

    # Load data
    max_length = train_cfg.get("max_length", 2048)
    dataset = load_training_data(data_path, tokenizer, max_length)

    # Split into train/eval (90/10)
    split = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = split["train"]
    eval_dataset = split["test"]

    print(f"Train examples: {len(train_dataset)}, Eval examples: {len(eval_dataset)}")

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(adapter_dir),
        num_train_epochs=_epochs,
        per_device_train_batch_size=_batch_size,
        per_device_eval_batch_size=_batch_size,
        gradient_accumulation_steps=train_cfg.get("gradient_accumulation_steps", 4),
        learning_rate=_lr,
        weight_decay=train_cfg.get("weight_decay", 0.01),
        warmup_steps=train_cfg.get("warmup_steps", 100),
        lr_scheduler_type=train_cfg.get("lr_scheduler", "cosine"),
        fp16=train_cfg.get("fp16", True) and torch.cuda.is_available(),
        logging_steps=train_cfg.get("logging_steps", 10),
        save_steps=train_cfg.get("save_steps", 200),
        eval_steps=train_cfg.get("eval_steps", 200),
        eval_strategy="steps",
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="tensorboard",
        logging_dir=str(adapter_dir / "logs"),
        remove_unused_columns=False,
    )

    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        padding=True,
        return_tensors="pt",
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    # Train (with optional resume)
    print("\nStarting training...")
    start_time = time.time()

    trainer.train(resume_from_checkpoint=resume_from)

    elapsed = time.time() - start_time
    minutes = elapsed / 60

    print(f"\nTraining complete in {minutes:.1f} minutes.")

    # Save the final adapter
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    # Save training metadata
    metadata = {
        "darshana": darshana,
        "base_model": model_name,
        "epochs": _epochs,
        "learning_rate": _lr,
        "batch_size": _batch_size,
        "lora_rank": config.get("lora", {}).get("rank", 16),
        "lora_alpha": config.get("lora", {}).get("alpha", 32),
        "train_examples": len(train_dataset),
        "eval_examples": len(eval_dataset),
        "training_time_minutes": round(minutes, 1),
        "final_eval_loss": trainer.state.best_metric,
    }
    with open(adapter_dir / "training_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Adapter saved to: {adapter_dir}")
    print(f"Metadata saved to: {adapter_dir / 'training_metadata.json'}")

    return adapter_dir


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune darshana reasoning models with LoRA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Fine-tune Nyaya specialist
  python training/finetune.py --darshana nyaya

  # Fine-tune all 6 darshanas
  python training/finetune.py --all

  # Fine-tune the router (Buddhi layer)
  python training/finetune.py --router

  # Fine-tune the vritti classifier
  python training/finetune.py --vritti

  # Custom settings
  python training/finetune.py --darshana nyaya --epochs 5 --lr 1e-4 --lora-rank 32
""",
    )

    # What to train
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--darshana", choices=DARSHANAS,
                       help="Fine-tune a single darshana specialist")
    group.add_argument("--all", action="store_true",
                       help="Fine-tune all 6 darshana specialists")
    group.add_argument("--router", action="store_true",
                       help="Fine-tune the Buddhi routing model")
    group.add_argument("--vritti", action="store_true",
                       help="Fine-tune the vritti classification model")

    # Model
    parser.add_argument("--base-model", type=str, default=None,
                        help="HuggingFace model ID (overrides config.yaml)")

    # Training hyperparameters
    parser.add_argument("--epochs", type=int, default=None,
                        help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=None,
                        help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Per-device batch size")
    parser.add_argument("--lora-rank", type=int, default=None,
                        help="LoRA rank (default: 16)")
    parser.add_argument("--max-length", type=int, default=None,
                        help="Max sequence length")

    # Resume
    parser.add_argument("--resume", type=str, default=None,
                        help="Path to checkpoint to resume from")

    # Config
    parser.add_argument("--config", type=str, default=str(CONFIG_PATH),
                        help="Path to config YAML")

    return parser.parse_args()


def main():
    args = parse_args()

    # Load config
    config = load_config(Path(args.config))

    # Apply CLI overrides
    model_name = args.base_model or config.get("base_model", "meta-llama/Llama-3.2-3B-Instruct")
    if args.max_length:
        config.setdefault("training", {})["max_length"] = args.max_length

    # Determine what to train
    targets: list[str] = []
    if args.all:
        targets = list(DARSHANAS)
    elif args.darshana:
        targets = [args.darshana]
    elif args.router:
        targets = ["router"]
    elif args.vritti:
        targets = ["vritti"]

    print(f"\nDarshana Fine-Tuning Pipeline")
    print(f"Targets: {', '.join(t.upper() for t in targets)}")
    print(f"Base model: {model_name}")
    print()

    # Train each target
    results = {}
    for target in targets:
        try:
            adapter_path = train_darshana(
                darshana=target,
                model_name=model_name,
                config=config,
                resume_from=args.resume,
                epochs=args.epochs,
                lr=args.lr,
                batch_size=args.batch_size,
                lora_rank=args.lora_rank,
            )
            results[target] = {"status": "success", "path": str(adapter_path)}
        except Exception as e:
            print(f"\nERROR training {target}: {e}")
            results[target] = {"status": "error", "error": str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    for target, result in results.items():
        status = result["status"]
        if status == "success":
            print(f"  {target.upper():15s} OK  -> {result['path']}")
        else:
            print(f"  {target.upper():15s} FAIL -> {result['error']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
