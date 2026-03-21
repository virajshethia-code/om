#!/usr/bin/env python3
"""
demo.py — Darshana Router in action

Demonstrates the Buddhi layer routing queries to the six darshana engines,
with guna (processing mode) classification and pramana (epistemic source)
tagging.

Run:
    cd /Users/harsh/om/src && python3 demo.py
"""

import sys
import os

# Ensure the src directory is on the path so the import works
# whether invoked as `python3 demo.py` from src/ or from elsewhere.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from darshana_router import (
    DarshanaRouter,
    PramanaTagger,
    Guna,
    Pramana,
)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

GUNA_DESCRIPTIONS = {
    Guna.SATTVA: "precision mode -- strict validation, low temperature",
    Guna.RAJAS: "exploration mode -- creative divergence, high temperature",
    Guna.TAMAS: "retrieval mode -- cached patterns, efficient lookup",
}

PRAMANA_DESCRIPTIONS = {
    Pramana.PRATYAKSHA: "direct perception (from input/tools)",
    Pramana.ANUMANA: "inference (derived through reasoning)",
    Pramana.UPAMANA: "analogy (understood by comparison)",
    Pramana.SHABDA: "testimony (from authority/training data)",
}

SEPARATOR = "=" * 72
THIN_SEP = "-" * 72


def print_header(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def print_section(title: str) -> None:
    print(f"\n  {title}")
    print(f"  {THIN_SEP[:len(title) + 4]}")


# ---------------------------------------------------------------------------
# Demo queries — one designed to trigger each darshana
# ---------------------------------------------------------------------------

DEMO_QUERIES = [
    {
        "label": "NYAYA (Logic & Validation)",
        "query": (
            "Is this argument valid? All mammals are warm-blooded. "
            "Whales are mammals. Therefore whales are warm-blooded. "
            "But what about exceptions — is the logic sound?"
        ),
    },
    {
        "label": "SAMKHYA (Decomposition & Classification)",
        "query": (
            "Break down the architecture of a modern web application. "
            "What are the layers, and how do they relate to each other?"
        ),
    },
    {
        "label": "YOGA (Focus & Noise Filtering)",
        "query": (
            "I have too many priorities right now — a product launch, "
            "three bug reports, a hiring decision, and a board deck due Friday. "
            "What should I focus on first? What actually matters here?"
        ),
    },
    {
        "label": "VEDANTA (Synthesis & Contradiction Resolution)",
        "query": (
            "Our engineering team says we need to move fast and ship, "
            "but the security team says we need to slow down and audit. "
            "These positions seem to contradict each other, yet both are right. "
            "How do they fit together? Is there a deeper, unified principle underneath?"
        ),
    },
    {
        "label": "MIMAMSA (Interpretation & Action Extraction)",
        "query": (
            "The spec says: 'The system should handle authentication, "
            "support SSO, and degrade gracefully when the identity provider "
            "is unavailable.' What exactly should I implement? "
            "What are the concrete requirements?"
        ),
    },
    {
        "label": "VAISHESHIKA (Atomic Analysis & Root Cause)",
        "query": (
            "The API returns a 500 error intermittently. Sometimes it works, "
            "sometimes it doesn't. What is this made of at the lowest level? "
            "I need to find the root cause and debug this."
        ),
    },
]


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def run_demo() -> None:
    print()
    print("  THE DARSHANA ROUTER -- Buddhi Layer Proof of Concept")
    print("  A Hindu Philosophical Framework for AGI Reasoning")
    print()
    print("  Six queries. Six darshanas. One cognitive architecture.")
    print()

    router = DarshanaRouter()
    tagger = PramanaTagger()

    for i, item in enumerate(DEMO_QUERIES, 1):
        label = item["label"]
        query = item["query"]

        print_header(f"Query {i}/6: {label}")
        print(f"\n  \"{query}\"")

        # Route
        result = router.route_and_reason(query)
        routing = result.routing

        # Routing decision
        print_section("BUDDHI (Routing Decision)")
        print(f"\n{router.explain_routing(routing)}")

        # Guna
        print_section("GUNA (Processing Mode)")
        guna_desc = GUNA_DESCRIPTIONS.get(routing.guna, "")
        print(f"  Mode: {routing.guna.value} -- {guna_desc}")

        # Reasoning from top engine(s)
        for output in result.reasoning:
            print_section(f"ENGINE: {output.engine.upper()}")
            print(f"\n  Approach:\n")
            for line in output.approach.split("\n"):
                print(f"    {line}")

            # Pramana tags
            if output.pramana_tags:
                print(f"\n  Pramana tags:")
                for tag in output.pramana_tags:
                    pdesc = PRAMANA_DESCRIPTIONS.get(tag.source, "")
                    print(f"    [{tag.source.value}] (confidence: {tag.confidence}) {pdesc}")
                    print(f"      \"{tag.claim}\"")
                    if tag.note:
                        print(f"      Note: {tag.note}")

        # Demo the pramana tagger on a sample claim related to the query
        sample_claims = [
            "The input says all mammals are warm-blooded.",
            "Based on the architecture, the frontend likely depends on the API layer.",
            "Similar to triage in an emergency room, we should prioritize by urgency.",
            "According to the documentation, SSO requires SAML or OIDC.",
            "Therefore, the 500 error probably originates in the database connection pool.",
            "It is known that graceful degradation requires fallback mechanisms.",
        ]
        claim = sample_claims[i - 1]
        tag = tagger.tag(claim)

        print_section("PRAMANA TAGGER (Epistemic Provenance)")
        pdesc = PRAMANA_DESCRIPTIONS.get(tag.source, "")
        print(f"  Sample claim: \"{claim}\"")
        print(f"  Tagged as:    {tag.source.value} -- {pdesc}")
        print(f"  Confidence:   {tag.confidence}")
        print(f"  Note:         {tag.note}")

        print()

    # Summary
    print_header("SUMMARY")
    print()
    print("  The Darshana Router demonstrates how Hindu philosophy's six schools")
    print("  provide complementary reasoning strategies for an AGI system:")
    print()
    print("    Nyaya       -> validates truth claims with formal logic")
    print("    Samkhya     -> decomposes systems into enumerated layers")
    print("    Yoga        -> filters noise and focuses on what matters")
    print("    Vedanta     -> resolves contradictions through synthesis")
    print("    Mimamsa     -> extracts actionable steps from text")
    print("    Vaisheshika -> finds root causes through atomic analysis")
    print()
    print("  Supporting subsystems:")
    print("    Guna Engine     -> adapts processing mode to the task")
    print("    Pramana Tagger  -> tags every claim with its epistemic source")
    print()
    print("  This is a proof of concept. In production, each engine's prompt")
    print("  template would be sent to an LLM for execution, with the guna")
    print("  controlling generation parameters and the pramana tagger auditing")
    print("  every output claim.")
    print()
    print("  See THESIS.md for the full architectural description.")
    print()


if __name__ == "__main__":
    run_demo()
