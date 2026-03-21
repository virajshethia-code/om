#!/usr/bin/env python3
"""
generate_data.py — Training Data Generator for Darshana Architecture Fine-Tuning
=================================================================================

Generates 8 JSONL datasets:
  - 6 darshana reasoning datasets (30 examples each, 180 total)
  - 1 router dataset (100 examples)
  - 1 vritti classification dataset (50 examples)
  - 1 combined/shuffled dataset

Each example is chat-format JSONL suitable for OpenAI, Anthropic, or HuggingFace
fine-tuning pipelines.

Usage:
    python training/generate_data.py              # Generate all datasets
    python training/generate_data.py --validate   # Validate existing JSONL
    python training/generate_data.py --stats      # Print dataset statistics

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
SRC_DIR = SCRIPT_DIR.parent / "src"

# Add src to path so we can import prompts
sys.path.insert(0, str(SRC_DIR))
from prompts import DARSHANA_PROMPTS  # noqa: E402

# ---------------------------------------------------------------------------
# Output files
# ---------------------------------------------------------------------------

DARSHANA_NAMES = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]

OUTPUT_FILES = {name: DATA_DIR / f"{name}_train.jsonl" for name in DARSHANA_NAMES}
OUTPUT_FILES["router"] = DATA_DIR / "router_train.jsonl"
OUTPUT_FILES["vritti"] = DATA_DIR / "vritti_train.jsonl"
OUTPUT_FILES["combined"] = DATA_DIR / "combined_train.jsonl"

# ---------------------------------------------------------------------------
# Domain categories for diverse coverage
# ---------------------------------------------------------------------------

DOMAINS = [
    "software_engineering",
    "business_strategy",
    "scientific_analysis",
    "personal_decisions",
    "debugging",
    "ethics",
    "project_planning",
    "legal_contractual",
    "creative_decisions",
    "education",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_message(system: str, user: str, assistant: str) -> Dict[str, Any]:
    """Create a single chat-format training example."""
    return {
        "messages": [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user.strip()},
            {"role": "assistant", "content": assistant.strip()},
        ]
    }


def write_jsonl(path: Path, examples: List[Dict[str, Any]]) -> None:
    """Write a list of examples to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"  Wrote {len(examples):>4d} examples to {path.name}")


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars per token for English)."""
    return len(text) // 4


# ###########################################################################
#
#  IMPORT EXAMPLE DATA FROM SEPARATE MODULES
#  Each darshana's examples live in training/examples/<darshana>.py
#  This keeps the main script manageable while housing all content.
#
# ###########################################################################

def _import_examples():
    """Import example generators from the examples package."""
    examples_dir = SCRIPT_DIR / "examples"
    sys.path.insert(0, str(SCRIPT_DIR))
    from examples import (
        generate_nyaya_examples,
        generate_samkhya_examples,
        generate_yoga_examples,
        generate_vedanta_examples,
        generate_mimamsa_examples,
        generate_vaisheshika_examples,
        generate_router_examples,
        generate_vritti_examples,
    )
    return {
        "nyaya": generate_nyaya_examples,
        "samkhya": generate_samkhya_examples,
        "yoga": generate_yoga_examples,
        "vedanta": generate_vedanta_examples,
        "mimamsa": generate_mimamsa_examples,
        "vaisheshika": generate_vaisheshika_examples,
        "router": generate_router_examples,
        "vritti": generate_vritti_examples,
    }


# ###########################################################################
#
#  MAIN GENERATION PIPELINE
#
# ###########################################################################

def generate_all() -> Dict[str, List[Dict[str, Any]]]:
    """Generate all training datasets. Returns dict of name -> examples."""
    generators = _import_examples()
    datasets: Dict[str, List[Dict[str, Any]]] = {}

    print("Generating training datasets...")
    print("=" * 60)

    for name in DARSHANA_NAMES:
        print(f"\n  [{name.upper()}]")
        datasets[name] = generators[name]()
        print(f"    Generated {len(datasets[name])} examples")

    print(f"\n  [ROUTER]")
    datasets["router"] = generators["router"]()
    print(f"    Generated {len(datasets['router'])} examples")

    print(f"\n  [VRITTI]")
    datasets["vritti"] = generators["vritti"]()
    print(f"    Generated {len(datasets['vritti'])} examples")

    # Combined dataset: merge all + shuffle
    combined = []
    for name, exs in datasets.items():
        combined.extend(exs)
    random.seed(42)
    random.shuffle(combined)
    datasets["combined"] = combined

    return datasets


def write_all(datasets: Dict[str, List[Dict[str, Any]]]) -> None:
    """Write all datasets to JSONL files."""
    print("\n" + "=" * 60)
    print("Writing JSONL files...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, exs in datasets.items():
        write_jsonl(OUTPUT_FILES[name], exs)
    print("\nDone.")


# ###########################################################################
#
#  VALIDATION
#
# ###########################################################################

def validate_all() -> bool:
    """Validate all JSONL files are parseable and well-formed."""
    print("Validating JSONL files...")
    print("=" * 60)
    all_valid = True

    for name, path in OUTPUT_FILES.items():
        if not path.exists():
            print(f"  {path.name}: MISSING")
            all_valid = False
            continue

        errors = []
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if "messages" not in obj:
                        errors.append(f"  Line {i}: missing 'messages' key")
                    else:
                        msgs = obj["messages"]
                        roles = [m.get("role") for m in msgs]
                        if roles != ["system", "user", "assistant"]:
                            errors.append(f"  Line {i}: unexpected roles {roles}")
                        for m in msgs:
                            if not m.get("content", "").strip():
                                errors.append(f"  Line {i}: empty content for role={m.get('role')}")
                    count += 1
                except json.JSONDecodeError as e:
                    errors.append(f"  Line {i}: JSON parse error: {e}")

        if errors:
            print(f"  {path.name}: INVALID ({len(errors)} errors in {count} examples)")
            for err in errors[:5]:
                print(f"    {err}")
            if len(errors) > 5:
                print(f"    ... and {len(errors) - 5} more")
            all_valid = False
        else:
            print(f"  {path.name}: OK ({count} examples)")

    return all_valid


# ###########################################################################
#
#  STATISTICS
#
# ###########################################################################

def print_stats() -> None:
    """Print statistics about generated datasets."""
    print("Dataset Statistics")
    print("=" * 60)

    total_examples = 0
    total_tokens = 0

    for name, path in OUTPUT_FILES.items():
        if name == "combined":
            continue
        if not path.exists():
            print(f"  {name:>15s}: FILE NOT FOUND")
            continue

        count = 0
        tokens = 0
        response_lengths = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                count += 1
                for msg in obj.get("messages", []):
                    content = msg.get("content", "")
                    tokens += estimate_tokens(content)
                    if msg.get("role") == "assistant":
                        response_lengths.append(len(content.split()))

        avg_words = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        min_words = min(response_lengths) if response_lengths else 0
        max_words = max(response_lengths) if response_lengths else 0

        print(f"  {name:>15s}: {count:>4d} examples | ~{tokens:>7,d} tokens | "
              f"response words: avg={avg_words:.0f} min={min_words} max={max_words}")
        total_examples += count
        total_tokens += tokens

    # Combined stats
    combined_path = OUTPUT_FILES["combined"]
    if combined_path.exists():
        with open(combined_path, "r") as f:
            combined_count = sum(1 for line in f if line.strip())
    else:
        combined_count = 0

    print(f"\n  {'COMBINED':>15s}: {combined_count:>4d} examples")
    print(f"  {'TOTAL':>15s}: {total_examples:>4d} examples | ~{total_tokens:>7,d} tokens")

    # Domain coverage (check queries for domain keywords)
    print(f"\n  Domain coverage check:")
    domain_keywords = {
        "software_engineering": ["api", "code", "deploy", "test", "database", "bug", "ci/cd", "server", "microservice"],
        "business_strategy": ["pricing", "startup", "revenue", "market", "growth", "profit", "competitor", "business model"],
        "scientific_analysis": ["study", "experiment", "hypothesis", "data", "correlation", "peer review", "immune", "climate"],
        "personal_decisions": ["relocat", "career", "job offer", "graduate degree", "buy a house", "relationship"],
        "debugging": ["slow", "error", "memory leak", "502", "performance", "crash", "timeout"],
        "ethics": ["ethical", "bias", "privacy", "data sell", "autonomous", "consent", "moral"],
        "project_planning": ["launch", "deadline", "estimate", "scrum", "technical debt", "requirements"],
        "legal_contractual": ["contract", "nda", "sla", "license", "gdpr", "compliance", "legal"],
        "creative_decisions": ["game", "film", "novel", "music", "podcast", "design", "creative"],
        "education": ["student", "learning", "course", "school", "teach", "mentor", "grade"],
    }

    for name, path in OUTPUT_FILES.items():
        if name in ("combined", "router", "vritti"):
            continue
        if not path.exists():
            continue

        domain_hits = {d: 0 for d in DOMAINS}
        with open(path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                query = obj["messages"][1]["content"].lower()
                for domain, keywords in domain_keywords.items():
                    if any(kw in query for kw in keywords):
                        domain_hits[domain] += 1
                        break

        covered = [d for d, c in domain_hits.items() if c > 0]
        print(f"    {name:>15s}: {len(covered)}/{len(DOMAINS)} domains covered")


# ###########################################################################
#
#  CLI ENTRY POINT
#
# ###########################################################################

def main():
    parser = argparse.ArgumentParser(
        description="Generate training datasets for Darshana Architecture fine-tuning"
    )
    parser.add_argument("--validate", action="store_true",
                        help="Validate existing JSONL files")
    parser.add_argument("--stats", action="store_true",
                        help="Print statistics about generated data")
    args = parser.parse_args()

    if args.validate:
        valid = validate_all()
        sys.exit(0 if valid else 1)

    if args.stats:
        print_stats()
        sys.exit(0)

    # Default: generate all
    datasets = generate_all()
    write_all(datasets)

    print("\n" + "=" * 60)
    print("Generation complete. Run with --validate or --stats for more info.")


if __name__ == "__main__":
    main()
