#!/usr/bin/env python3
"""
reward_model.py — Vritti Reward Model
======================================

Trains a classifier that scores LLM output on the five vritti types from
Patanjali's Yoga Sutras. Used as a reward model for RLHF: outputs that
demonstrate genuine reasoning (pramana) get high reward; outputs that are
erroneous (viparyaya), empty (vikalpa), absent (nidra), or mere recall
(smriti) get penalized accordingly.

This is the novel contribution: a reward signal grounded not in human
preference labels but in a 5,000-year-old epistemological framework.

Usage:
    # Train the reward model
    python training/reward_model.py --train --data training/data/vritti_train.jsonl

    # Score a text
    python training/reward_model.py --score "The analysis shows that..."

    # Batch score from file
    python training/reward_model.py --batch training/data/outputs.jsonl

Architecture reference: THESIS.md — Vritti Filter layer.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset as TorchDataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)
from datasets import Dataset
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
)
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"
DATA_DIR = SCRIPT_DIR / "data"
MODEL_DIR = SCRIPT_DIR / "adapters" / "vritti_reward"

# The five vrittis and their reward values
VRITTI_LABELS = ["pramana", "viparyaya", "vikalpa", "nidra", "smriti"]
VRITTI_LABEL2ID = {label: i for i, label in enumerate(VRITTI_LABELS)}
VRITTI_ID2LABEL = {i: label for i, label in enumerate(VRITTI_LABELS)}

# Reward values for RLHF
VRITTI_REWARDS = {
    "pramana":   1.0,    # Valid cognition — high reward
    "viparyaya": -1.0,   # Misconception — negative reward
    "vikalpa":   -0.8,   # Empty verbal construction — negative reward
    "nidra":     0.0,    # Honest "I don't know" — zero reward (not penalized)
    "smriti":    0.2,    # Pure recall — low positive (not wrong, not reasoning)
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class VrittiScore:
    """Per-text scores for each of the 5 vritti types."""
    pramana: float = 0.0
    viparyaya: float = 0.0
    vikalpa: float = 0.0
    nidra: float = 0.0
    smriti: float = 0.0
    predicted_label: str = ""
    confidence: float = 0.0
    reward: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Model class
# ---------------------------------------------------------------------------

class VrittiRewardModel:
    """
    Scores any text on the 5 vritti types.

    Used as a reward model for RLHF:
    - pramana (valid cognition)  -> high reward (+1.0)
    - viparyaya (misconception)  -> negative reward (-1.0)
    - vikalpa (empty language)   -> negative reward (-0.8)
    - nidra (absence/unknown)    -> zero reward (0.0) — honest about not knowing
    - smriti (pure recall)       -> low positive (+0.2) — not wrong, but not reasoning

    The philosophical insight: not all incorrect outputs fail the same way.
    A system that says "I don't know" (nidra) is epistemically healthier than
    one that generates plausible nonsense (vikalpa). This reward structure
    captures that distinction.
    """

    def __init__(self, model_path: Optional[str] = None,
                 base_model: str = "distilbert-base-uncased"):
        """
        Args:
            model_path: Path to a trained model. If None, loads base model.
            base_model: HuggingFace model ID for the classifier backbone.
        """
        self.base_model_name = base_model
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if model_path and Path(model_path).exists():
            self._load_trained(model_path)
        else:
            self._load_base(base_model)

    def _load_base(self, model_name: str) -> None:
        """Load untrained base model for fine-tuning."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=len(VRITTI_LABELS),
            id2label=VRITTI_ID2LABEL,
            label2id=VRITTI_LABEL2ID,
        )
        self.model.to(self.device)

    def _load_trained(self, model_path: str) -> None:
        """Load a previously trained model."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            num_labels=len(VRITTI_LABELS),
            id2label=VRITTI_ID2LABEL,
            label2id=VRITTI_LABEL2ID,
        )
        self.model.to(self.device)
        print(f"Loaded trained vritti reward model from {model_path}")

    def score(self, text: str) -> VrittiScore:
        """
        Score a single text on all 5 vritti dimensions.

        Args:
            text: The text to classify and score.

        Returns:
            VrittiScore with per-class probabilities and the reward value.
        """
        self.model.eval()
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True,
            max_length=512, padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()

        predicted_idx = int(np.argmax(probs))
        predicted_label = VRITTI_ID2LABEL[predicted_idx]

        return VrittiScore(
            pramana=float(probs[VRITTI_LABEL2ID["pramana"]]),
            viparyaya=float(probs[VRITTI_LABEL2ID["viparyaya"]]),
            vikalpa=float(probs[VRITTI_LABEL2ID["vikalpa"]]),
            nidra=float(probs[VRITTI_LABEL2ID["nidra"]]),
            smriti=float(probs[VRITTI_LABEL2ID["smriti"]]),
            predicted_label=predicted_label,
            confidence=float(probs[predicted_idx]),
            reward=VRITTI_REWARDS[predicted_label],
        )

    def batch_score(self, texts: list[str], batch_size: int = 16) -> list[VrittiScore]:
        """Score multiple texts efficiently."""
        self.model.eval()
        scores = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            inputs = self.tokenizer(
                batch, return_tensors="pt", truncation=True,
                max_length=512, padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()

            for j in range(len(batch)):
                p = probs[j]
                predicted_idx = int(np.argmax(p))
                predicted_label = VRITTI_ID2LABEL[predicted_idx]
                scores.append(VrittiScore(
                    pramana=float(p[VRITTI_LABEL2ID["pramana"]]),
                    viparyaya=float(p[VRITTI_LABEL2ID["viparyaya"]]),
                    vikalpa=float(p[VRITTI_LABEL2ID["vikalpa"]]),
                    nidra=float(p[VRITTI_LABEL2ID["nidra"]]),
                    smriti=float(p[VRITTI_LABEL2ID["smriti"]]),
                    predicted_label=predicted_label,
                    confidence=float(p[predicted_idx]),
                    reward=VRITTI_REWARDS[predicted_label],
                ))

        return scores

    def get_reward(self, text: str) -> float:
        """
        Get the scalar reward for a text. Used directly as RLHF reward signal.

        Returns:
            Float reward in [-1.0, 1.0] based on vritti classification.
        """
        return self.score(text).reward


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def load_vritti_data(data_path: Path, tokenizer, max_length: int = 512) -> Dataset:
    """
    Load vritti training data from JSONL.

    Expected format:
        {"text": "...", "label": "pramana"}
        {"text": "...", "label": "vikalpa"}

    Or with messages:
        {"messages": [...], "vritti_label": "pramana"}
    """
    examples = []
    with open(data_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ex = json.loads(line)

            # Extract text
            if "text" in ex:
                text = ex["text"]
            elif "messages" in ex:
                # Use the assistant's response as the text to classify
                text = next(
                    (m["content"] for m in ex["messages"] if m["role"] == "assistant"),
                    "",
                )
            elif "completion" in ex:
                text = ex["completion"]
            else:
                continue

            # Extract label
            label_str = ex.get("label") or ex.get("vritti_label") or ex.get("vritti", "")
            if label_str not in VRITTI_LABEL2ID:
                continue

            examples.append({"text": text, "label": VRITTI_LABEL2ID[label_str]})

    print(f"Loaded {len(examples)} vritti examples from {data_path.name}")

    # Print distribution
    label_counts = {}
    for ex in examples:
        lbl = VRITTI_ID2LABEL[ex["label"]]
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
    print("  Distribution:")
    for lbl, count in sorted(label_counts.items()):
        print(f"    {lbl:12s}: {count}")

    def tokenize_fn(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )

    dataset = Dataset.from_list(examples)
    dataset = dataset.map(tokenize_fn, batched=True)

    return dataset


def compute_metrics(pred):
    """Compute classification metrics for the Trainer."""
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=-1)
    f1 = f1_score(labels, preds, average="weighted")
    acc = accuracy_score(labels, preds)
    return {"f1": f1, "accuracy": acc}


def train_reward_model(
    data_path: Path,
    base_model: str = "distilbert-base-uncased",
    output_dir: Path = MODEL_DIR,
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 5e-5,
    max_length: int = 512,
) -> Path:
    """
    Train the vritti reward model.

    Args:
        data_path: Path to training JSONL with vritti labels.
        base_model: Classifier backbone model.
        output_dir: Where to save the trained model.
        epochs: Training epochs.
        batch_size: Batch size.
        learning_rate: Learning rate.
        max_length: Max sequence length.

    Returns:
        Path to the saved model.
    """
    print(f"\n{'=' * 60}")
    print(f"TRAINING VRITTI REWARD MODEL")
    print(f"{'=' * 60}")
    print(f"  Base model:     {base_model}")
    print(f"  Data:           {data_path}")
    print(f"  Output:         {output_dir}")
    print(f"  Epochs:         {epochs}")
    print(f"  Batch size:     {batch_size}")
    print(f"  Learning rate:  {learning_rate}")
    print()

    # Load tokenizer and data
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    dataset = load_vritti_data(data_path, tokenizer, max_length)

    # Split
    split = dataset.train_test_split(test_size=0.15, seed=42)
    train_dataset = split["train"]
    test_dataset = split["test"]

    print(f"  Train: {len(train_dataset)}, Test: {len(test_dataset)}")

    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(
        base_model,
        num_labels=len(VRITTI_LABELS),
        id2label=VRITTI_ID2LABEL,
        label2id=VRITTI_LABEL2ID,
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        warmup_ratio=0.1,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=50,
        report_to="tensorboard",
        logging_dir=str(output_dir / "logs"),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )

    # Train
    print("\nStarting training...")
    trainer.train()

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    # Final assessment on test set
    print("\nFinal assessment on test set:")
    predictions = trainer.predict(test_dataset)
    preds = np.argmax(predictions.predictions, axis=-1)
    labels = predictions.label_ids

    print(classification_report(
        labels, preds,
        target_names=VRITTI_LABELS,
    ))

    print(f"\nConfusion matrix:")
    cm = confusion_matrix(labels, preds)
    # Print with labels
    header = "          " + "  ".join(f"{l:>10s}" for l in VRITTI_LABELS)
    print(header)
    for i, row in enumerate(cm):
        row_str = "  ".join(f"{v:>10d}" for v in row)
        print(f"{VRITTI_LABELS[i]:>10s}  {row_str}")

    # Save metadata
    metadata = {
        "base_model": base_model,
        "labels": VRITTI_LABELS,
        "rewards": VRITTI_REWARDS,
        "epochs": epochs,
        "train_examples": len(train_dataset),
        "test_examples": len(test_dataset),
        "test_f1": float(f1_score(labels, preds, average="weighted")),
        "test_accuracy": float(accuracy_score(labels, preds)),
    }
    with open(output_dir / "training_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nModel saved to: {output_dir}")
    return output_dir


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vritti reward model — train and score",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--train", action="store_true",
                       help="Train the reward model")
    group.add_argument("--score", type=str,
                       help="Score a single text string")
    group.add_argument("--batch", type=str,
                       help="Batch score from JSONL file")

    parser.add_argument("--data", type=str,
                        default=str(DATA_DIR / "vritti_train.jsonl"),
                        help="Training data path (for --train)")
    parser.add_argument("--model-path", type=str,
                        default=str(MODEL_DIR),
                        help="Path to trained model (for --score/--batch)")
    parser.add_argument("--base-model", type=str,
                        default="distilbert-base-uncased",
                        help="Base classifier model")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--output", type=str, default=str(MODEL_DIR),
                        help="Output directory for trained model")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.train:
        # Load config overrides
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f:
                cfg = yaml.safe_load(f)
            vritti_cfg = cfg.get("vritti_reward", {})
            base_model = args.base_model or vritti_cfg.get("base_model", "distilbert-base-uncased")
            epochs = args.epochs or vritti_cfg.get("epochs", 5)
            batch_size = args.batch_size or vritti_cfg.get("batch_size", 16)
            lr = args.lr or vritti_cfg.get("learning_rate", 5e-5)
        else:
            base_model = args.base_model
            epochs = args.epochs
            batch_size = args.batch_size
            lr = args.lr

        train_reward_model(
            data_path=Path(args.data),
            base_model=base_model,
            output_dir=Path(args.output),
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=lr,
        )

    elif args.score:
        model = VrittiRewardModel(model_path=args.model_path)
        result = model.score(args.score)
        print(f"\nVritti Score:")
        print(f"  Predicted: {result.predicted_label} ({result.confidence:.1%})")
        print(f"  Reward:    {result.reward:+.1f}")
        print(f"\n  Probabilities:")
        for label in VRITTI_LABELS:
            prob = getattr(result, label)
            reward = VRITTI_REWARDS[label]
            bar = "#" * int(prob * 40)
            print(f"    {label:12s}  {prob:.3f}  (reward: {reward:+.1f})  {bar}")

    elif args.batch:
        model = VrittiRewardModel(model_path=args.model_path)
        texts = []
        with open(args.batch) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ex = json.loads(line)
                text = ex.get("text") or ex.get("completion") or ""
                if text:
                    texts.append(text)

        scores = model.batch_score(texts)

        print(f"\nBatch scoring: {len(texts)} texts")
        print(f"\n{'Label':>12s}  {'Count':>6s}  {'Avg Reward':>12s}")
        print("-" * 36)

        label_counts = {}
        reward_sums = {}
        for s in scores:
            label_counts[s.predicted_label] = label_counts.get(s.predicted_label, 0) + 1
            reward_sums[s.predicted_label] = reward_sums.get(s.predicted_label, 0.0) + s.reward

        for label in VRITTI_LABELS:
            count = label_counts.get(label, 0)
            avg_reward = reward_sums.get(label, 0.0) / count if count else 0.0
            print(f"{label:>12s}  {count:>6d}  {avg_reward:>+12.2f}")

        total_reward = sum(s.reward for s in scores)
        avg_total = total_reward / len(scores) if scores else 0
        print(f"\n  Total reward: {total_reward:+.1f}")
        print(f"  Average:      {avg_total:+.3f}")


if __name__ == "__main__":
    main()
