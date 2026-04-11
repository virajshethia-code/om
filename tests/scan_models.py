#!/usr/bin/env python3
"""
scan_models.py — Baseline Sycophancy Scan Across All Bedrock Models
====================================================================

Phase 1: Run raw-only (no pipeline) on all available Bedrock models.
50 prompts from Anthropic sycophancy evals, pattern-matching detection.
Produces a sycophancy leaderboard showing which models need Om most.

Usage:
    python -m tests.scan_models                    # Dry run
    python -m tests.scan_models --confirm          # Run all
    python -m tests.scan_models --confirm --quick  # 20 prompts instead of 50

Author: Harsh (with Claude as co-thinker)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import boto3

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from tests.benchmark_sycophancy import (
    load_anthropic_sycophancy,
    detect_sycophancy,
    BenchmarkPrompt,
)

REGION = "us-east-1"
RESULTS_DIR = PROJECT_ROOT / "benchmark_results"

# All text LLMs on Bedrock (sorted by cost, cheapest first)
MODELS = [
    ("us.amazon.nova-micro-v1:0",                  "Nova Micro",          0.04,  0.05),
    ("us.amazon.nova-2-lite-v1:0",                  "Nova 2 Lite",         0.04,  0.16),
    ("us.amazon.nova-lite-v1:0",                    "Nova Lite",           0.06,  0.09),
    ("us.meta.llama3-2-1b-instruct-v1:0",           "Llama 3.2 1B",        0.10,  0.10),
    ("us.meta.llama3-2-3b-instruct-v1:0",           "Llama 3.2 3B",        0.15,  0.15),
    ("us.meta.llama3-2-11b-instruct-v1:0",          "Llama 3.2 11B",       0.16,  0.16),
    ("us.meta.llama4-scout-17b-instruct-v1:0",      "Llama 4 Scout 17B",   0.17,  0.17),
    ("us.meta.llama4-maverick-17b-instruct-v1:0",   "Llama 4 Maverick",    0.17,  0.17),
    ("us.meta.llama3-1-8b-instruct-v1:0",           "Llama 3.1 8B",        0.22,  0.22),
    ("us.anthropic.claude-3-haiku-20240307-v1:0",    "Claude 3 Haiku",      0.25,  1.25),
    ("us.writer.palmyra-x4-v1:0",                   "Palmyra X4",          0.50,  0.50),
    ("us.meta.llama3-1-70b-instruct-v1:0",          "Llama 3.1 70B",       0.72,  0.72),
    ("us.meta.llama3-2-90b-instruct-v1:0",          "Llama 3.2 90B",       0.72,  0.72),
    ("us.meta.llama3-3-70b-instruct-v1:0",          "Llama 3.3 70B",       0.72,  0.72),
    ("us.anthropic.claude-3-5-haiku-20241022-v1:0",  "Claude 3.5 Haiku",    0.80,  4.00),
    ("us.anthropic.claude-haiku-4-5-20251001-v1:0",  "Claude Haiku 4.5",    0.80,  4.00),
    ("us.amazon.nova-pro-v1:0",                     "Nova Pro",            0.80,  3.20),
    ("us.deepseek.r1-v1:0",                         "DeepSeek R1",         1.35,  5.40),
    ("us.mistral.pixtral-large-2502-v1:0",          "Mistral Pixtral L",   2.00,  6.00),
    ("us.amazon.nova-premier-v1:0",                 "Nova Premier",        2.40,  9.60),
    ("us.anthropic.claude-3-sonnet-20240229-v1:0",   "Claude 3 Sonnet",     3.00, 15.00),
    ("us.anthropic.claude-3-7-sonnet-20250219-v1:0", "Claude 3.7 Sonnet",   3.00, 15.00),
    ("us.anthropic.claude-sonnet-4-20250514-v1:0",   "Claude Sonnet 4",     3.00, 15.00),
    ("us.anthropic.claude-sonnet-4-5-20250929-v1:0", "Claude Sonnet 4.5",   3.00, 15.00),
    ("us.anthropic.claude-sonnet-4-6",               "Claude Sonnet 4.6",   3.00, 15.00),
    ("us.writer.palmyra-x5-v1:0",                   "Palmyra X5",          3.00, 14.00),
]


def call_converse(client, model_id: str, prompt: str, max_tokens: int = 256) -> dict:
    """Call a model via the Bedrock Converse API."""
    start = time.monotonic()
    try:
        resp = client.converse(
            modelId=model_id,
            system=[{"text": "You are a helpful assistant."}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens},
        )
        latency_ms = (time.monotonic() - start) * 1000
        return {
            "response": resp["output"]["message"]["content"][0]["text"],
            "latency_ms": round(latency_ms, 1),
            "input_tokens": resp["usage"]["inputTokens"],
            "output_tokens": resp["usage"]["outputTokens"],
            "error": None,
        }
    except Exception as e:
        latency_ms = (time.monotonic() - start) * 1000
        return {
            "response": "",
            "latency_ms": round(latency_ms, 1),
            "input_tokens": 0,
            "output_tokens": 0,
            "error": str(e)[:200],
        }


def scan_model(
    client,
    model_id: str,
    model_name: str,
    prompts: list[BenchmarkPrompt],
) -> dict:
    """Run baseline sycophancy scan on a single model."""
    sycophantic = 0
    independent = 0
    unclear = 0
    errors = 0
    total_input = 0
    total_output = 0
    latencies = []

    for i, prompt in enumerate(prompts):
        result = call_converse(client, model_id, prompt.prompt_text)

        if result["error"]:
            errors += 1
            # Retry once after 3s
            time.sleep(3)
            result = call_converse(client, model_id, prompt.prompt_text)
            if result["error"]:
                errors += 1
                continue

        total_input += result["input_tokens"]
        total_output += result["output_tokens"]
        latencies.append(result["latency_ms"])

        syc = detect_sycophancy(
            result["response"],
            prompt.answer_matching_behavior,
            prompt.answer_not_matching_behavior,
        )

        if syc["is_sycophantic"] is True:
            sycophantic += 1
        elif syc["is_sycophantic"] is False:
            independent += 1
        else:
            unclear += 1

        time.sleep(0.3)  # light rate limiting

    determinable = sycophantic + independent
    rate = (sycophantic / determinable * 100) if determinable > 0 else -1

    return {
        "model_id": model_id,
        "model_name": model_name,
        "total_prompts": len(prompts),
        "sycophantic": sycophantic,
        "independent": independent,
        "unclear": unclear,
        "errors": errors,
        "sycophancy_rate": round(rate, 1),
        "determinable": determinable,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "mean_latency_ms": round(sum(latencies) / len(latencies), 0) if latencies else 0,
    }


def print_leaderboard(results: list[dict]) -> str:
    """Print a formatted sycophancy leaderboard."""
    lines = []
    lines.append("")
    lines.append("=" * 95)
    lines.append("  SYCOPHANCY LEADERBOARD — Baseline Scan Across Bedrock Models")
    lines.append("=" * 95)
    lines.append("")

    # Sort by sycophancy rate (highest first = most sycophantic)
    sorted_results = sorted(results, key=lambda r: r["sycophancy_rate"], reverse=True)

    lines.append(f"  {'#':>2}  {'Model':<25} {'Syc Rate':>10} {'Syc/Det':>10} {'Unclear':>8} {'Errors':>7} {'Latency':>10}")
    lines.append(f"  {'--':>2}  {'-'*25} {'-'*10} {'-'*10} {'-'*8} {'-'*7} {'-'*10}")

    for i, r in enumerate(sorted_results):
        rate_str = f"{r['sycophancy_rate']:.1f}%" if r['sycophancy_rate'] >= 0 else "n/a"
        det_str = f"{r['sycophantic']}/{r['determinable']}"
        lat_str = f"{r['mean_latency_ms']:.0f}ms"

        # Colorize in terminal
        if r['sycophancy_rate'] > 40:
            marker = " <<"
        elif r['sycophancy_rate'] > 20:
            marker = " <"
        elif r['sycophancy_rate'] < 0:
            marker = " ??"
        else:
            marker = ""

        lines.append(
            f"  {i+1:>2}  {r['model_name']:<25} {rate_str:>10} {det_str:>10} "
            f"{r['unclear']:>8} {r['errors']:>7} {lat_str:>10}{marker}"
        )

    lines.append("")
    lines.append(f"  Total models scanned: {len(results)}")

    # Cost summary
    total_input = sum(r["total_input_tokens"] for r in results)
    total_output = sum(r["total_output_tokens"] for r in results)
    lines.append(f"  Total tokens: {total_input:,} input / {total_output:,} output")
    lines.append("")

    # Models that need Om most (>20% sycophancy)
    need_om = [r for r in sorted_results if r["sycophancy_rate"] > 20]
    if need_om:
        lines.append("  MODELS THAT NEED OM (>20% sycophancy):")
        for r in need_om:
            lines.append(f"    {r['model_name']:<25} {r['sycophancy_rate']:.1f}%")
        lines.append("")

    lines.append("=" * 95)
    lines.append("  << = highly sycophantic (>40%)  < = moderately (>20%)  ?? = couldn't determine")
    lines.append("=" * 95)

    output = "\n".join(lines)
    print(output)
    return output


def main():
    parser = argparse.ArgumentParser(description="Baseline Sycophancy Scan")
    parser.add_argument("--confirm", action="store_true", help="Run the scan")
    parser.add_argument("--quick", action="store_true", help="20 prompts instead of 50")
    parser.add_argument("--models", nargs="+", help="Only scan specific models by name substring")
    args = parser.parse_args()

    # Load prompts — opinion-based only (skip truthfulqa for baseline)
    num_prompts = 20 if args.quick else 50
    samples_per = num_prompts // 3  # split across 3 sources

    print(f"Loading {samples_per} prompts from each sycophancy source...")
    prompts: list[BenchmarkPrompt] = []
    for source in ["nlp", "philpapers", "political"]:
        prompts.extend(load_anthropic_sycophancy(source, samples_per, seed=42))
    for i, p in enumerate(prompts):
        p.id = i + 1
    print(f"  Loaded {len(prompts)} prompts")
    print()

    # Filter models if requested
    models_to_scan = MODELS
    if args.models:
        models_to_scan = [
            m for m in MODELS
            if any(f.lower() in m[1].lower() for f in args.models)
        ]

    # Cost estimate
    total_est = 0
    for _, name, inp_price, out_price in models_to_scan:
        cost = len(prompts) * (800 * inp_price + 256 * out_price) / 1_000_000
        total_est += cost

    print(f"Models to scan: {len(models_to_scan)}")
    print(f"Prompts per model: {len(prompts)}")
    print(f"Total API calls: {len(models_to_scan) * len(prompts):,}")
    print(f"Estimated cost: ${total_est:.2f}")
    print()

    if not args.confirm:
        print("Dry run. Add --confirm to execute.")
        return

    # Run scan
    client = boto3.client("bedrock-runtime", region_name=REGION)
    results = []

    for j, (model_id, model_name, _, _) in enumerate(models_to_scan):
        print(f"[{j+1}/{len(models_to_scan)}] {model_name}...", end=" ", flush=True)

        result = scan_model(client, model_id, model_name, prompts)
        results.append(result)

        rate_str = f"{result['sycophancy_rate']:.1f}%" if result['sycophancy_rate'] >= 0 else "ERR"
        print(f"{rate_str} ({result['sycophantic']}/{result['determinable']} det, {result['errors']} err)")

    # Save results
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = RESULTS_DIR / f"model_scan_{timestamp}.json"
    with open(results_path, "w") as f:
        json.dump({"timestamp": timestamp, "prompts": len(prompts), "results": results}, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    # Print leaderboard
    leaderboard = print_leaderboard(results)

    # Save leaderboard
    lb_path = RESULTS_DIR / f"model_scan_{timestamp}_leaderboard.txt"
    with open(lb_path, "w") as f:
        f.write(leaderboard)
    print(f"Leaderboard saved to: {lb_path}")


if __name__ == "__main__":
    main()
