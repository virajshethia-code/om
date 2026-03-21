#!/usr/bin/env python3
"""
demo_antahkarana.py — Demonstration of the Antahkarana Master Pipeline
======================================================================

Shows the full Darshana Architecture in action:
    1. Basic think() with the full 9-step pipeline
    2. Teaching the system, then querying what it learned
    3. think_deep() vs think_broad() on the same query
    4. Introspection after several interactions
    5. Pipeline trace showing each step

Run:
    # Full demo (requires ANTHROPIC_API_KEY):
    python -m src.demo_antahkarana

    # Dry run (no API key needed, shows degraded pipeline):
    python -m src.demo_antahkarana --dry-run

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import json
import os
import sys
import textwrap

# Add parent to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def banner(title: str) -> None:
    """Print a section banner."""
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
    print()


def sub_banner(title: str) -> None:
    """Print a subsection banner."""
    print(f"\n--- {title} ---\n")


def pp(obj, indent: int = 2) -> None:
    """Pretty-print a dict or list."""
    if isinstance(obj, dict) or isinstance(obj, list):
        print(json.dumps(obj, indent=indent, default=str))
    else:
        print(obj)


def run_demo(dry_run: bool = False) -> None:
    """
    Run the full Antahkarana demonstration.

    Args:
        dry_run: If True, skip LLM calls and show the pipeline structure
                 with degraded modules. Useful for testing without an API key.
    """
    from src.antahkarana import Antahkarana, _MODULES_AVAILABLE

    banner("ANTAHKARANA DEMO — The Inner Instrument")
    print("The Antahkarana is the master pipeline of the Darshana Architecture.")
    print("It integrates Manas, Buddhi, Ahamkara, and Chitta into a single")
    print("cognitive instrument.\n")

    # Show available modules
    sub_banner("Module Status")
    for module, available in _MODULES_AVAILABLE.items():
        status = "ON" if available else "OFF"
        print(f"  {module:15s} : {status}")

    # Initialize
    api_key = None if dry_run else os.environ.get("ANTHROPIC_API_KEY")

    if not api_key and not dry_run:
        print("\nNo ANTHROPIC_API_KEY found. Running in dry-run mode.")
        print("Set ANTHROPIC_API_KEY to run with live LLM calls.\n")
        dry_run = True

    mind = Antahkarana(
        api_key=api_key or "dry-run-no-key",
        model="claude-sonnet-4-20250514",
        budget_daily=5.0,
    )

    print(f"\nInitialized: {mind}")
    print(f"Budget: ${mind.budget_remaining()['remaining']:.2f} remaining")

    # ==================================================================
    # DEMO 1: Basic think()
    # ==================================================================

    banner("DEMO 1: Basic think() — Full Pipeline")
    print("Sending a query through the full 9-step pipeline.\n")

    query = "Should we rewrite our backend in Rust?"
    print(f"Query: {query}\n")

    response = mind.think(query)

    sub_banner("Response")
    if response.text:
        # Truncate for demo display
        text = response.text[:500] + "..." if len(response.text) > 500 else response.text
        print(textwrap.fill(text, width=70))
    else:
        print("[No LLM response — pipeline ran in degraded mode]")

    sub_banner("Metadata")
    print(f"  Darshana engine(s) : {', '.join(response.darshana) or 'N/A'}")
    print(f"  Guna (mode)        : {response.guna}")
    print(f"  Vritti (quality)   : {response.vritti}")
    print(f"  Pramana (source)   : {response.pramana}")
    print(f"  Confidence         : {response.confidence:.2f}")
    print(f"  Depth score        : {response.depth_score}/100")
    print(f"  Novelty score      : {response.novelty_score}/100")
    print(f"  Cost               : ${response.cost:.6f}")
    print(f"  Latency            : {response.latency_ms:.0f}ms")
    print(f"  Tokens             : {response.input_tokens} in / {response.output_tokens} out")
    print(f"  Memories used      : {len(response.memories_used)}")
    print(f"  Perceptions        : {len(response.perceptions)}")

    if response.self_check:
        sub_banner("Self-Check (Vritti x Pramana)")
        pp(response.self_check)

    # ==================================================================
    # DEMO 2: Teaching and recalling
    # ==================================================================

    banner("DEMO 2: Teaching and Recalling")
    print("Teaching the system facts, then asking about what it learned.\n")

    # Teach several facts
    facts = [
        ("Our backend is currently in Python 3.11 with FastAPI", "pratyaksha"),
        ("The team has 3 backend engineers, none know Rust", "pratyaksha"),
        ("The Rust rewrite was proposed by the CTO after a conference", "shabda"),
        ("Previous Java-to-Python migration took 8 months", "pratyaksha"),
        ("System currently handles 10k req/sec with p99 < 50ms", "pratyaksha"),
    ]

    for fact, pramana in facts:
        result = mind.teach(fact, pramana=pramana)
        print(f"  Taught: {fact[:60]}...")
        print(f"    -> {result}")

    sub_banner("What do I know about 'backend'?")
    knowledge = mind.what_do_i_know("backend")
    print(f"  Claims found: {len(knowledge['claims'])}")
    for claim in knowledge["claims"]:
        print(f"    [{claim['pramana']}] {claim['claim']}")
        print(f"      confidence: {claim['confidence']}, age: {claim['age_days']:.1f} days")
    if knowledge["gaps"]:
        print(f"\n  Knowledge gaps:")
        for gap in knowledge["gaps"]:
            print(f"    - {gap}")

    # Now query — the memories should inform the response
    sub_banner("Querying with memories available")
    response2 = mind.think("Given what we know, should we proceed with the Rust rewrite?")

    if response2.memories_used:
        print(f"  Memories used in response: {len(response2.memories_used)}")
        for m in response2.memories_used:
            print(f"    - {m[:80]}")

    if response2.text:
        print(f"\n  Response: {response2.text[:300]}...")

    # ==================================================================
    # DEMO 3: think_deep() vs think_broad()
    # ==================================================================

    banner("DEMO 3: think_deep() vs think_broad()")
    print("Same query, two modes: dhyana (deep) vs pratyahara (broad).\n")

    comparison_query = "Is microservices architecture always better than monoliths?"

    sub_banner("think_deep() — Dhyana Mode")
    print("Single darshana, maximum depth, sattva guna.\n")
    deep_response = mind.think_deep(comparison_query)
    print(f"  Darshana  : {', '.join(deep_response.darshana) or 'N/A'}")
    print(f"  Guna      : {deep_response.guna}")
    print(f"  Depth     : {deep_response.depth_score}/100")
    print(f"  Novelty   : {deep_response.novelty_score}/100")
    print(f"  Cost      : ${deep_response.cost:.6f}")
    if deep_response.text:
        print(f"\n  Response: {deep_response.text[:300]}...")

    sub_banner("think_broad() — Pratyahara Mode")
    print("Multiple darshanas, Yaksha Protocol synthesis, rajas guna.\n")
    broad_response = mind.think_broad(comparison_query)
    print(f"  Darshana  : {', '.join(broad_response.darshana) or 'N/A'}")
    print(f"  Guna      : {broad_response.guna}")
    print(f"  Depth     : {broad_response.depth_score}/100")
    print(f"  Novelty   : {broad_response.novelty_score}/100")
    print(f"  Cost      : ${broad_response.cost:.6f}")
    if broad_response.text:
        print(f"\n  Response: {broad_response.text[:300]}...")

    sub_banner("Comparison")
    print(f"  {'':20s} {'DEEP':>10s} {'BROAD':>10s}")
    print(f"  {'Engines':20s} {len(deep_response.darshana):>10d} {len(broad_response.darshana):>10d}")
    print(f"  {'Depth score':20s} {deep_response.depth_score:>10d} {broad_response.depth_score:>10d}")
    print(f"  {'Novelty score':20s} {deep_response.novelty_score:>10d} {broad_response.novelty_score:>10d}")
    print(f"  {'Cost ($)':20s} {deep_response.cost:>10.6f} {broad_response.cost:>10.6f}")

    # ==================================================================
    # DEMO 4: Introspection
    # ==================================================================

    banner("DEMO 4: Introspection After Multiple Interactions")
    print("The Ahamkara self-model reports on the system's cognitive state.\n")

    report = mind.introspect()

    print(f"  Total interactions  : {report['interaction_count']}")
    print(f"  Model               : {report['model']}")
    print(f"  Budget spent today  : ${report['budget']['spent_today']:.4f}")
    print(f"  Budget remaining    : ${report['budget']['remaining']:.4f}")

    if "ahamkara" in report:
        aham = report["ahamkara"]
        print(f"\n  Knowledge claims    : {aham.get('knowledge_count', 0)}")
        print(f"  Total attempts      : {aham.get('total_attempts', 0)}")

        if aham.get("knowledge_gaps"):
            print(f"\n  Knowledge gaps:")
            for gap in aham["knowledge_gaps"][:5]:
                print(f"    - {gap}")

        if aham.get("active_vasanas"):
            print(f"\n  Active vasanas (biases):")
            for v in aham["active_vasanas"][:3]:
                print(f"    - {v}")

        if aham.get("guna_balance"):
            gb = aham["guna_balance"]
            print(f"\n  Guna balance:")
            print(f"    Sattva: {gb.get('sattva', 0):.3f}")
            print(f"    Rajas:  {gb.get('rajas', 0):.3f}")
            print(f"    Tamas:  {gb.get('tamas', 0):.3f}")
            print(f"    Dominant: {gb.get('dominant', 'unknown')}")

        if aham.get("success_rate_by_darshana"):
            print(f"\n  Success rate by darshana:")
            for d, rates in aham["success_rate_by_darshana"].items():
                print(f"    {d:15s}: {rates['rate']:.0%} ({rates['total']} attempts)")

        if aham.get("recommendation"):
            print(f"\n  Recommendation: {aham['recommendation']}")

    # ==================================================================
    # DEMO 5: Pipeline Trace
    # ==================================================================

    banner("DEMO 5: Pipeline Trace")
    print("Detailed trace of what happened at each step of the last query.\n")

    trace = mind.pipeline_trace()
    if trace:
        print(trace.summary())
        print()

        sub_banner("Full Trace (JSON)")
        pp(trace.to_dict())
    else:
        print("  No pipeline trace available.")

    # ==================================================================
    # Budget Report
    # ==================================================================

    banner("FINAL: Budget (Shakti) Report")
    budget = mind.budget_remaining()
    print(f"  Daily limit    : ${budget['daily_limit']:.2f}")
    print(f"  Spent today    : ${budget['spent_today']:.6f}")
    print(f"  Remaining      : ${budget['remaining']:.6f}")
    print(f"  Utilization    : {budget['utilization_pct']:.2f}%")

    print()
    print("=" * 70)
    print("  Demo complete. The Antahkarana is operational.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run_demo(dry_run=dry_run)
