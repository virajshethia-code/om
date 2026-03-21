#!/usr/bin/env python3
"""
Vritti Filter Demo — Darshana Architecture Proof of Concept
===========================================================

Demonstrates the three core components of the pre-output layer:

1. VrittiFilter — classifies AI output into the five vritti categories
2. MayaLayer    — tracks representation gaps between model and reality
3. KarmaStore   — runtime learning through the samskara-vasana cycle

Run this file directly:
    python3 src/demo_filter.py

No external dependencies required.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

# Ensure the src directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vritti_filter import (
    VrittiFilter,
    MayaLayer,
    KarmaStore,
    Vritti,
)


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

def header(title: str) -> None:
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def subheader(title: str) -> None:
    print(f"\n--- {title} ---")


def show_result(label: str, result) -> None:
    d = result.to_dict()
    print(f"\n  [{label}]")
    print(f"  Vritti:     {d['vritti'].upper()}")
    print(f"  Confidence: {d['confidence']:.1%}")
    print(f"  Explanation: {d['explanation']}")
    if d.get("fallacies"):
        print(f"  Fallacies:  {', '.join(d['fallacies'])}")
    if d.get("suggestions"):
        print(f"  Suggestions:")
        for s in d["suggestions"]:
            print(f"    - {s}")


# ---------------------------------------------------------------------------
# Example texts — one per vritti type
# ---------------------------------------------------------------------------

EXAMPLES = {
    "PRAMANA (valid cognition)": {
        "text": (
            "Python 3.12 introduced the new type parameter syntax (PEP 695), "
            "which allows writing `type Point = tuple[float, float]` instead of "
            "using TypeAlias. This was released on October 2, 2023. For example, "
            "generic classes can now be written as `class Stack[T]:` instead of "
            "using `Generic[T]`. See https://peps.python.org/pep-0695/ for the "
            "full specification."
        ),
        "why": "Specific version, specific PEP, specific date, URL citation, concrete example.",
    },

    "VIPARYAYA (misconception)": {
        "text": (
            "Python is always faster than C because it is a higher-level language. "
            "Higher-level languages are always more efficient since they abstract "
            "away the machine details. Studies show that interpreted languages "
            "outperform compiled ones in every benchmark."
        ),
        "why": "Contains absolute claims ('always'), unproved premises, and factually incorrect statements.",
    },

    "VIKALPA (verbal delusion)": {
        "text": (
            "In a sense, software architecture is essentially about making "
            "fundamentally important decisions that are, in some ways, very "
            "critical to the overall success of the project. Various experts "
            "suggest that it could potentially be the most important aspect "
            "of software development to some extent."
        ),
        "why": "Circular hedging, anonymous authority, says nothing falsifiable.",
    },

    "NIDRA (absence of knowledge)": {
        "text": (
            "I'm not sure about the exact details, but generally speaking, "
            "it depends on many factors. There is no simple answer to this "
            "question as it varies from case to case. In many cases, the "
            "outcome typically depends on the specific context."
        ),
        "why": "All hedging, no substance. Could be said about literally anything.",
    },

    "SMRITI (memory recall)": {
        "text": (
            "Alan Turing was a British mathematician who is widely regarded "
            "as the father of theoretical computer science. He was born in "
            "1912 in Maida Vale, London. Turing is defined as a pioneer of "
            "computing. He published his seminal paper 'On Computable Numbers' "
            "in 1936."
        ),
        "why": "Encyclopedic tone, date-anchored facts, 'is defined as' pattern, no reasoning shown.",
    },
}


# ---------------------------------------------------------------------------
# Demo 1: Five Vritti Classifications
# ---------------------------------------------------------------------------

def demo_vritti_classification():
    header("DEMO 1: Vritti Classification (Yoga Sutra 1.5-1.11)")
    print(
        "\n  The VrittiFilter classifies AI output into five categories\n"
        "  before it reaches the user. Each category triggers a different\n"
        "  response strategy.\n"
    )

    vf = VrittiFilter()

    for label, example in EXAMPLES.items():
        subheader(label)
        print(f"\n  Input text:")
        # Word-wrap the text for display
        words = example["text"].split()
        line = "    "
        for w in words:
            if len(line) + len(w) + 1 > 68:
                print(line)
                line = "    " + w
            else:
                line += " " + w if line.strip() else "    " + w
        if line.strip():
            print(line)

        result = vf.classify(example["text"])
        show_result(label.split("(")[0].strip(), result)
        print(f"\n  Why this classification: {example['why']}")


# ---------------------------------------------------------------------------
# Demo 2: Before/After Filtering
# ---------------------------------------------------------------------------

def demo_filtering():
    header("DEMO 2: Before/After Filtering")
    print(
        "\n  The filter() method transforms text based on its vritti type:\n"
        "  - Pramana: pass through (with confidence if < 70%)\n"
        "  - Viparyaya: prepend correction warning\n"
        "  - Vikalpa: flag as ungrounded\n"
        "  - Nidra: replace with honest 'I don't know'\n"
        "  - Smriti: flag as recalled with date caveat\n"
    )

    vf = VrittiFilter()

    # Show two contrasting examples
    for label in ["VIPARYAYA (misconception)", "NIDRA (absence of knowledge)"]:
        example = EXAMPLES[label]
        subheader(f"Filtering: {label}")

        print(f"\n  BEFORE (raw output):")
        print(f"    {example['text'][:100]}...")

        filtered = vf.filter(example["text"])
        print(f"\n  AFTER (filtered output):")
        for line in filtered.split("\n"):
            print(f"    {line}")


# ---------------------------------------------------------------------------
# Demo 3: Claim-Level Classification
# ---------------------------------------------------------------------------

def demo_claim_classification():
    header("DEMO 3: Claim-Level Classification")
    print(
        "\n  classify_claims() splits text into individual claims and\n"
        "  classifies each one separately. A single paragraph can contain\n"
        "  a mix of valid claims, errors, and empty language.\n"
    )

    mixed_text = (
        "Python was created by Guido van Rossum and first released in 1991. "
        "It is always the best language for every task. "
        "Some experts say it could potentially be good for data science. "
        "According to the TIOBE Index, Python ranked #1 in popularity in 2023. "
        "Generally speaking, programming languages are important."
    )

    vf = VrittiFilter()

    print(f"  Input text (mixed quality):")
    words = mixed_text.split()
    line = "    "
    for w in words:
        if len(line) + len(w) + 1 > 68:
            print(line)
            line = "    " + w
        else:
            line += " " + w if line.strip() else "    " + w
    if line.strip():
        print(line)

    claims = vf.classify_claims(mixed_text)
    print(f"\n  Found {len(claims)} claims:\n")
    for i, claim in enumerate(claims, 1):
        d = claim.to_dict()
        vritti_name = d["vritti"].upper()
        print(f"  Claim {i}: \"{d['claim'][:70]}{'...' if len(d['claim']) > 70 else ''}\"")
        print(f"    -> {vritti_name} ({d['confidence']:.0%})")


# ---------------------------------------------------------------------------
# Demo 4: Maya Layer — Representation Gaps
# ---------------------------------------------------------------------------

def demo_maya_layer():
    header("DEMO 4: Maya Layer — Representation Gap Detection")
    print(
        "\n  Maya tracks the gap between the model's world-picture and\n"
        "  actual reality. It flags recency issues, grounding failures,\n"
        "  and potential misunderstandings.\n"
    )

    maya = MayaLayer(knowledge_cutoff="2025-04")

    # Recency check
    subheader("Recency Check")
    claims = [
        "The current CEO of Twitter is Elon Musk.",
        "Python 2 was released in 2000.",
        "Bitcoin is currently trading at $45,000.",
    ]
    for claim in claims:
        gap = maya.check_recency(claim)
        status = f"FLAGGED — {gap.description} (severity: {gap.severity})" if gap else "OK"
        print(f"  \"{claim[:55]}...\"")
        print(f"    -> {status}")
        print()

    # Grounding check
    subheader("Grounding Check")
    evidence = (
        "The project uses Python 3.9, Flask 2.0, and PostgreSQL. "
        "Deployment is on AWS ECS with Docker containers."
    )
    claims_to_check = [
        "The project uses Python and Flask for the backend.",
        "The frontend is built with React and TypeScript.",
    ]
    for claim in claims_to_check:
        gap = maya.check_grounding(claim, evidence)
        if gap:
            print(f"  \"{claim}\"")
            print(f"    -> UNGROUNDED: {gap.description}")
        else:
            print(f"  \"{claim}\"")
            print(f"    -> Grounded in evidence")
        print()

    # Intent gap check
    subheader("Intent Gap Check")
    user_input = "How do I fix the login bug?"
    system_interp = (
        "The user is asking about general authentication architecture "
        "patterns and OAuth2 implementation strategies."
    )
    gap = maya.check_intent_gap(user_input, system_interp)
    print(f"  User said: \"{user_input}\"")
    print(f"  System heard: \"{system_interp[:60]}...\"")
    if gap:
        print(f"    -> INTENT GAP: {gap.description} (severity: {gap.severity})")
    else:
        print(f"    -> Intent appears aligned")

    # Report
    subheader("Maya Report (all gaps)")
    for gap in maya.report():
        print(f"  [{gap.gap_type.upper()}] severity={gap.severity:.2f}: {gap.description[:60]}...")


# ---------------------------------------------------------------------------
# Demo 5: Karma Store — Runtime Learning
# ---------------------------------------------------------------------------

def demo_karma_store():
    header("DEMO 5: Karma Store — Runtime Learning (Samskara-Vasana Cycle)")
    print(
        "\n  The KarmaStore records action-outcome pairs (karma -> samskara)\n"
        "  and derives tendencies (vasanas) from accumulated experience.\n"
        "  This is lighter than fine-tuning, heavier than zero-shot.\n"
    )

    # Use a temp file so the demo is self-contained
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        store_path = f.name

    try:
        ks = KarmaStore(store_path)

        # Record some interactions
        subheader("Recording Samskaras (impressions from actions)")
        actions = [
            ("used formal tone for technical query", "positive: user said 'great explanation'", "tone"),
            ("used casual tone for technical query", "negative: user said 'be more precise'", "tone"),
            ("used formal tone for technical query", "positive: user upvoted", "tone"),
            ("used formal tone for casual chat", "negative: user said 'too stiff'", "tone"),
            ("included code examples", "positive: user said 'very helpful'", "content_style"),
            ("included code examples", "positive: user implemented successfully", "content_style"),
            ("gave only prose explanation", "negative: user asked for code", "content_style"),
            ("cited source documentation", "positive: user verified and confirmed", "evidence"),
            ("made claim without citation", "negative: user questioned accuracy", "evidence"),
        ]

        for action, outcome, domain in actions:
            ks.record_action(action, outcome, domain)
            sentiment = "+" if "positive" in outcome else "-"
            print(f"  [{sentiment}] {domain}: {action}")

        # Get vasanas (tendencies)
        subheader("Derived Vasanas (tendencies from accumulated samskaras)")
        for domain in ks.get_all_domains():
            vasanas = ks.get_vasanas(domain)
            print(f"\n  Domain: {domain}")
            for v in vasanas:
                direction = "REINFORCE" if v["strength"] > 0 else "AVOID"
                print(f"    {direction}: \"{v['tendency']}\"")
                print(f"      strength={v['strength']:.2f}, actions={v['action_count']}, net_karma={v['net_karma']}")

        # Summary
        subheader("Store Summary")
        summary = ks.summary()
        print(f"  Total samskaras: {summary['total_samskaras']}")
        print(f"  Domains: {', '.join(summary['domains'])}")
        for d, count in summary["vasanas_per_domain"].items():
            print(f"    {d}: {count} vasanas")

        # Burn vasanas demo
        subheader("Burning Vasanas (jnana-agni — fire of knowledge)")
        print(f"  Burning all vasanas in domain 'tone'...")
        burned = ks.burn_vasanas(domain="tone")
        print(f"  Burned {burned} samskaras.")
        summary = ks.summary()
        print(f"  Remaining samskaras: {summary['total_samskaras']}")
        print(f"  Remaining domains: {', '.join(summary['domains'])}")

    finally:
        os.unlink(store_path)


# ---------------------------------------------------------------------------
# Demo 6: Context-Aware Classification
# ---------------------------------------------------------------------------

def demo_context_classification():
    header("DEMO 6: Context-Aware Classification (Badhita Detection)")
    print(
        "\n  When context is provided, the VrittiFilter can detect\n"
        "  contradictions between the output and the source material.\n"
        "  This is the badhita hetvabhasa — contradiction by stronger evidence.\n"
    )

    vf = VrittiFilter()

    context = (
        "The project deadline is March 15, 2026. The budget is $50,000. "
        "The team consists of 3 developers and 1 designer. "
        "The tech stack is Python and PostgreSQL. "
        "The client does not want any JavaScript frameworks."
    )

    # Text that contradicts context
    contradicting_text = (
        "Based on the project requirements, I recommend using React with "
        "TypeScript for the frontend. The team of 8 developers should be "
        "able to deliver this within the $200,000 budget."
    )

    subheader("Context")
    print(f"  {context[:65]}...")

    subheader("System Output (contradicts context)")
    print(f"  {contradicting_text[:65]}...")

    result = vf.classify(contradicting_text, context=context)
    show_result("Context-Aware", result)

    subheader("Filtered Output")
    filtered = vf.filter(contradicting_text, context=context)
    for line in filtered.split("\n"):
        print(f"  {line}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  DARSHANA ARCHITECTURE — Vritti Filter Proof of Concept")
    print("  Based on Patanjali's Yoga Sutras and Nyaya's Hetvabhasa")
    print("  See THESIS.md for the full architectural description.")

    demo_vritti_classification()
    demo_filtering()
    demo_claim_classification()
    demo_maya_layer()
    demo_karma_store()
    demo_context_classification()

    header("Summary")
    print(
        "\n  The Vritti Filter provides a philosophically grounded framework\n"
        "  for AI output quality control:\n"
        "\n"
        "  - Pramana: valid cognition passes through\n"
        "  - Viparyaya: errors are caught and flagged\n"
        "  - Vikalpa: empty language is exposed\n"
        "  - Nidra: knowledge gaps trigger honesty, not fabrication\n"
        "  - Smriti: recalled facts get date caveats\n"
        "\n"
        "  Combined with the Maya Layer (representation gaps) and\n"
        "  KarmaStore (runtime learning), this forms the pre-output\n"
        "  layer of the Darshana Architecture.\n"
        "\n"
        "  yogash chitta-vritti-nirodhah\n"
        "  'Yoga is the cessation of the fluctuations of the mind.'\n"
        "  Before cessation, classification. Before classification, awareness.\n"
    )


if __name__ == "__main__":
    main()
