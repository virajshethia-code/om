#!/usr/bin/env python3
"""
evaluate.py — Darshana Model Evaluation
========================================

Evaluates fine-tuned darshana adapters on method adherence, depth, novelty,
and vritti classification. Produces side-by-side comparisons of base model
vs fine-tuned model on the same prompts.

Usage:
    # Evaluate a single adapter
    python training/evaluate.py --adapter training/adapters/nyaya/ \\
        --test-data training/data/nyaya_test.jsonl

    # Compare base vs fine-tuned
    python training/evaluate.py --adapter training/adapters/nyaya/ \\
        --test-data training/data/nyaya_test.jsonl --compare

    # Evaluate all adapters
    python training/evaluate.py --all

Architecture reference: THESIS.md — Vritti Filter layer.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# ---------------------------------------------------------------------------
# Add parent to path so we can import the vritti_filter
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vritti_filter import VrittiFilter  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
ADAPTERS_DIR = SCRIPT_DIR / "adapters"

DARSHANAS = ["nyaya", "samkhya", "yoga", "vedanta", "mimamsa", "vaisheshika"]

# Method-specific structural markers that each darshana's output MUST contain.
# These are the minimum structural requirements from prompts.py.
METHOD_MARKERS = {
    "nyaya": {
        "required": [
            r"CLAIM:",
            r"SYLLOGISM:",
            r"Pratijna:",
            r"Hetu:",
            r"Udaharana:",
            r"Upanaya:",
            r"Nigamana:",
            r"HETVABHASA AUDIT:",
            r"(?:Asiddha|ASIDDHA):",
            r"(?:Viruddha|VIRUDDHA):",
            r"FAILURE POINT:",
            r"INSIGHT:",
        ],
        "weight": 1.0,
    },
    "samkhya": {
        "required": [
            r"SYSTEM:",
            r"TARGET COUNT:",
            r"ENUMERATION:",
            r"NON-OBVIOUS",
            r"CAUSAL CHAIN:",
            r"COMPLETENESS AUDIT:",
            r"TOTAL COUNT:",
        ],
        "weight": 1.0,
    },
    "yoga": {
        "required": [
            r"COMPLETE INPUT INVENTORY:",
            r"SIGNAL SCORES:",
            r"DISCARDED",
            r"RETAINED SIGNAL:",
            r"DHARANA POINT:",
            r"SECOND-ORDER FOCUS:",
            r"VRITTI AUDIT:",
        ],
        "weight": 1.0,
    },
    "vedanta": {
        "required": [
            r"THE CONTRADICTION:",
            r"SUPERIMPOSITION.*Adhyaropa",
            r"NEGATION.*Apavada",
            r"WHAT REMAINS.*Sat",
            r"(?:THE REFRAMING|MAHAVAKYA|Mahavakya)",
            r"RE-DERIVATION:",
        ],
        "weight": 1.0,
    },
    "mimamsa": {
        "required": [
            r"SENTENCE CLASSIFICATION",
            r"VIDHI",
            r"ARTHAVADA",
            r"VIDHI DECOMPOSITION:",
            r"Agent:",
            r"Action:",
            r"(?:SHADLINGA|AMBIGUITY)",
            r"EXECUTION SEQUENCE:",
        ],
        "weight": 1.0,
    },
    "vaisheshika": {
        "required": [
            r"DECOMPOSITION TREE:",
            r"ATOM",
            r"PADARTHA CLASSIFICATION:",
            r"Dravya:",
            r"Guna:",
            r"Karma:",
            r"(?:UNEXPECTED ATOM|THE UNEXPECTED)",
            r"(?:SAMAVAYA|SAMYOGA|ESSENTIAL.*ACCIDENTAL)",
            r"COMPOSITION MAP:",
        ],
        "weight": 1.0,
    },
    "router": {
        "required": [
            r"(?:engine|darshana|route)",
            r"(?:confidence|score|probability)",
        ],
        "weight": 1.0,
    },
    "vritti": {
        "required": [
            r"(?:pramana|viparyaya|vikalpa|nidra|smriti)",
        ],
        "weight": 1.0,
    },
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class MethodMetrics:
    """Assessment metrics for a single example."""
    method_adherence: float = 0.0      # 0-1: fraction of structural markers present
    depth_score: int = 0               # 0-100: from vritti_filter.depth_test
    novelty_score: int = 0             # 0-100: from vritti_filter.novelty_score
    vritti_class: str = ""             # pramana / viparyaya / vikalpa / nidra / smriti
    vritti_confidence: float = 0.0     # 0-1
    markers_found: list = field(default_factory=list)
    markers_missing: list = field(default_factory=list)


@dataclass
class AssessmentReport:
    """Aggregated assessment report."""
    darshana: str
    adapter_path: str
    n_examples: int = 0
    avg_method_adherence: float = 0.0
    avg_depth: float = 0.0
    avg_novelty: float = 0.0
    vritti_distribution: dict = field(default_factory=dict)
    pramana_rate: float = 0.0          # fraction classified as pramana
    per_example: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Assessment functions
# ---------------------------------------------------------------------------

def compute_method_adherence(text: str, darshana: str) -> tuple[float, list, list]:
    """
    Check if the output follows the darshana's specific method structure.

    Returns:
        (score, markers_found, markers_missing)
    """
    markers = METHOD_MARKERS.get(darshana, {}).get("required", [])
    if not markers:
        return 1.0, [], []

    found = []
    missing = []
    for marker in markers:
        if re.search(marker, text, re.IGNORECASE):
            found.append(marker)
        else:
            missing.append(marker)

    score = len(found) / len(markers) if markers else 1.0
    return score, found, missing


def generate_response(model, tokenizer, prompt: str, system_prompt: str = "",
                      max_new_tokens: int = 1024) -> str:
    """Generate a response from the model given a prompt."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        text = tokenizer.apply_chat_template(messages, tokenize=False,
                                              add_generation_prompt=True)
    except Exception:
        text = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the new tokens
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return response.strip()


def assess_single(text: str, query: str, darshana: str,
                  vritti_filter: VrittiFilter) -> MethodMetrics:
    """Assess a single model output."""
    # Method adherence
    adherence, found, missing = compute_method_adherence(text, darshana)

    # Depth and novelty from vritti_filter
    depth = vritti_filter.depth_test(text, query)
    novelty = vritti_filter.novelty_score(text)

    # Vritti classification
    vritti_result = vritti_filter.classify(text, context=query)

    return MethodMetrics(
        method_adherence=adherence,
        depth_score=depth.score if hasattr(depth, "score") else int(depth),
        novelty_score=novelty,
        vritti_class=vritti_result.vritti.value if hasattr(vritti_result.vritti, "value") else str(vritti_result.vritti),
        vritti_confidence=vritti_result.confidence,
        markers_found=[str(m) for m in found],
        markers_missing=[str(m) for m in missing],
    )


def run_adapter_assessment(
    adapter_path: Path,
    test_data_path: Path,
    darshana: str,
    compare: bool = False,
    max_examples: int = 50,
) -> AssessmentReport:
    """
    Run full assessment on a fine-tuned adapter.

    Args:
        adapter_path: Path to the LoRA adapter.
        test_data_path: Path to test JSONL.
        darshana: Which darshana this adapter is for.
        compare: If True, also generate responses from the base model.
        max_examples: Maximum examples to assess (generation is slow).

    Returns:
        AssessmentReport with aggregated metrics.
    """
    # Load training metadata to find base model
    meta_path = adapter_path / "training_metadata.json"
    if meta_path.exists():
        with open(meta_path) as f:
            metadata = json.load(f)
        base_model_name = metadata.get("base_model", "meta-llama/Llama-3.2-3B-Instruct")
    else:
        base_model_name = "meta-llama/Llama-3.2-3B-Instruct"

    print(f"\nAssessing {darshana.upper()} adapter")
    print(f"  Adapter:    {adapter_path}")
    print(f"  Test data:  {test_data_path}")
    print(f"  Base model: {base_model_name}")

    # Load test data
    if not test_data_path.exists():
        print(f"ERROR: Test data not found at {test_data_path}")
        sys.exit(1)

    examples = []
    with open(test_data_path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))

    examples = examples[:max_examples]
    print(f"  Examples:   {len(examples)}")

    # Load model + adapter
    print(f"\nLoading base model...")
    quant_config = None
    if torch.cuda.is_available():
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=quant_config,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading LoRA adapter from {adapter_path}...")
    ft_model = PeftModel.from_pretrained(base_model, str(adapter_path))
    ft_model.set_adapter("default")

    # Initialize vritti filter
    vf = VrittiFilter()

    # Run assessment
    report = AssessmentReport(
        darshana=darshana,
        adapter_path=str(adapter_path),
        n_examples=len(examples),
    )

    vritti_counts = {}
    total_adherence = 0.0
    total_depth = 0.0
    total_novelty = 0.0

    for i, ex in enumerate(examples):
        # Extract query from the example
        if "messages" in ex:
            query = next(
                (m["content"] for m in ex["messages"] if m["role"] == "user"), ""
            )
            system_prompt = next(
                (m["content"] for m in ex["messages"] if m["role"] == "system"), ""
            )
            reference = next(
                (m["content"] for m in ex["messages"] if m["role"] == "assistant"), ""
            )
        elif "prompt" in ex:
            query = ex["prompt"]
            system_prompt = ""
            reference = ex.get("completion", "")
        else:
            continue

        print(f"\n  [{i+1}/{len(examples)}] Generating response...")

        # Generate from fine-tuned model
        ft_response = generate_response(ft_model, tokenizer, query, system_prompt)

        # Assess fine-tuned response
        metrics = assess_single(ft_response, query, darshana, vf)

        total_adherence += metrics.method_adherence
        total_depth += metrics.depth_score
        total_novelty += metrics.novelty_score

        vritti_counts[metrics.vritti_class] = vritti_counts.get(metrics.vritti_class, 0) + 1

        example_result = {
            "query": query[:100] + "..." if len(query) > 100 else query,
            "metrics": asdict(metrics),
            "ft_response_preview": ft_response[:300] + "..." if len(ft_response) > 300 else ft_response,
        }

        # Compare with base model if requested
        if compare:
            # Temporarily disable adapter
            ft_model.disable_adapter_layers()
            base_response = generate_response(ft_model, tokenizer, query, system_prompt)
            ft_model.enable_adapter_layers()

            base_metrics = assess_single(base_response, query, darshana, vf)
            example_result["base_metrics"] = asdict(base_metrics)
            example_result["base_response_preview"] = (
                base_response[:300] + "..." if len(base_response) > 300 else base_response
            )

        report.per_example.append(example_result)

    n = len(examples) or 1
    report.avg_method_adherence = total_adherence / n
    report.avg_depth = total_depth / n
    report.avg_novelty = total_novelty / n
    report.vritti_distribution = vritti_counts
    report.pramana_rate = vritti_counts.get("pramana", 0) / n

    return report


def print_report(report: AssessmentReport) -> None:
    """Pretty-print an assessment report."""
    print(f"\n{'=' * 60}")
    print(f"ASSESSMENT REPORT: {report.darshana.upper()}")
    print(f"{'=' * 60}")
    print(f"  Adapter:              {report.adapter_path}")
    print(f"  Examples assessed:    {report.n_examples}")
    print()
    print(f"  Method adherence:     {report.avg_method_adherence:.1%}")
    print(f"  Average depth:        {report.avg_depth:.0f}/100")
    print(f"  Average novelty:      {report.avg_novelty:.0f}/100")
    print(f"  Pramana rate:         {report.pramana_rate:.1%}")
    print()
    print(f"  Vritti distribution:")
    for vritti, count in sorted(report.vritti_distribution.items(),
                                 key=lambda x: -x[1]):
        pct = count / report.n_examples if report.n_examples else 0
        bar = "#" * int(pct * 30)
        print(f"    {vritti:12s}  {count:3d} ({pct:5.1%})  {bar}")

    # Per-example details (first 5)
    if report.per_example:
        print(f"\n  Sample results (first 5):")
        for i, ex in enumerate(report.per_example[:5]):
            m = ex["metrics"]
            print(f"\n    [{i+1}] {ex['query']}")
            print(f"        Adherence: {m['method_adherence']:.0%}  "
                  f"Depth: {m['depth_score']}  Novelty: {m['novelty_score']}  "
                  f"Vritti: {m['vritti_class']}")
            if "base_metrics" in ex:
                bm = ex["base_metrics"]
                print(f"        BASE:  Adherence: {bm['method_adherence']:.0%}  "
                      f"Depth: {bm['depth_score']}  Novelty: {bm['novelty_score']}  "
                      f"Vritti: {bm['vritti_class']}")

    print(f"\n{'=' * 60}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assess fine-tuned darshana adapters",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--adapter", type=str,
                       help="Path to a single adapter directory")
    group.add_argument("--all", action="store_true",
                       help="Assess all adapters in training/adapters/")

    parser.add_argument("--test-data", type=str, default=None,
                        help="Path to test JSONL (auto-detected if not given)")
    parser.add_argument("--darshana", type=str, default=None,
                        help="Darshana name (auto-detected from adapter path)")
    parser.add_argument("--compare", action="store_true",
                        help="Also run base model for side-by-side comparison")
    parser.add_argument("--max-examples", type=int, default=50,
                        help="Max examples to assess (default: 50)")
    parser.add_argument("--output", type=str, default=None,
                        help="Save report as JSON to this path")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.all:
        # Assess every adapter found
        adapter_dirs = sorted(ADAPTERS_DIR.iterdir()) if ADAPTERS_DIR.exists() else []
        adapter_dirs = [d for d in adapter_dirs if d.is_dir() and (d / "adapter_config.json").exists()]

        if not adapter_dirs:
            print(f"No adapters found in {ADAPTERS_DIR}")
            sys.exit(1)

        reports = []
        for adapter_dir in adapter_dirs:
            darshana = adapter_dir.name
            test_data = DATA_DIR / f"{darshana}_test.jsonl"
            if not test_data.exists():
                print(f"Skipping {darshana}: no test data at {test_data}")
                continue

            report = run_adapter_assessment(
                adapter_path=adapter_dir,
                test_data_path=test_data,
                darshana=darshana,
                compare=args.compare,
                max_examples=args.max_examples,
            )
            print_report(report)
            reports.append(report)

        if args.output:
            with open(args.output, "w") as f:
                json.dump([asdict(r) for r in reports], f, indent=2)
            print(f"\nFull report saved to {args.output}")

    else:
        adapter_path = Path(args.adapter)
        darshana = args.darshana or adapter_path.name
        test_data = Path(args.test_data) if args.test_data else DATA_DIR / f"{darshana}_test.jsonl"

        report = run_adapter_assessment(
            adapter_path=adapter_path,
            test_data_path=test_data,
            darshana=darshana,
            compare=args.compare,
            max_examples=args.max_examples,
        )
        print_report(report)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(asdict(report), f, indent=2)
            print(f"\nFull report saved to {args.output}")


if __name__ == "__main__":
    main()
