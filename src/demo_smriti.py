#!/usr/bin/env python3
"""
demo_smriti.py — Demonstration of the Smriti Memory System
===========================================================

Shows all major capabilities:
1. Storing memories from different sources with different pramanas
2. Retrieving relevant memories for a new query
3. Confidence decay over simulated time
4. Vasana detection (accumulated bias)
5. Building a context window for an LLM call
6. Memory stats and gap detection

Run: python3 -m src.demo_smriti
  or: python3 src/demo_smriti.py

Uses a temporary database — no state is left behind.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time

# Handle import whether run as module or script
try:
    from smriti import Smriti, SmritiStore, VasanaEngine, RetrievalEngine, SmritiReport
except ImportError:
    from src.smriti import Smriti, SmritiStore, VasanaEngine, RetrievalEngine, SmritiReport


def divider(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main() -> None:
    # Use a temp file so the demo is self-contained
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    print(f"Smriti Demo — database at: {db_path}")

    memory = Smriti(db_path)

    # ------------------------------------------------------------------
    # 1. Storing memories from different sources with different pramanas
    # ------------------------------------------------------------------
    divider("1. STORING SAMSKARAS (Impressions)")

    memories_to_store = [
        {
            "content": "Python uses snake_case for variable and function names by convention (PEP 8)",
            "pramana": "pratyaksha",
            "source": "tool_output",
            "keywords": ["python", "snake_case", "naming", "convention", "pep8"],
            "confidence": 0.95,
            "darshana_context": "nyaya",
            "domain": "programming",
        },
        {
            "content": "User prefers concise code examples over verbose explanations",
            "pramana": "pratyaksha",
            "source": "user_interaction",
            "keywords": ["preference", "concise", "code", "examples"],
            "confidence": 0.9,
            "domain": "user_preference",
        },
        {
            "content": "SQLite supports WAL mode for better concurrent read performance",
            "pramana": "shabda",
            "source": "training",
            "keywords": ["sqlite", "wal", "concurrent", "performance", "database"],
            "confidence": 0.7,
            "domain": "data",
        },
        {
            "content": "The Nyaya school uses a five-part syllogism: pratijna, hetu, udaharana, upanaya, nigamana",
            "pramana": "shabda",
            "source": "training",
            "keywords": ["nyaya", "syllogism", "logic", "pratijna", "hetu"],
            "confidence": 0.75,
            "domain": "philosophy",
        },
        {
            "content": "React components should be split when they exceed 200 lines",
            "pramana": "anumana",
            "source": "inference",
            "keywords": ["react", "components", "refactoring", "code", "lines"],
            "confidence": 0.6,
            "domain": "programming",
        },
        {
            "content": "User corrected: do not assume macOS when the user mentions 'terminal' — could be Linux",
            "pramana": "pratyaksha",
            "source": "correction",
            "keywords": ["terminal", "macos", "linux", "assumption", "correction"],
            "confidence": 0.95,
            "domain": "user_preference",
        },
        {
            "content": "Exponential backoff with jitter is better than fixed retry intervals for API calls",
            "pramana": "anumana",
            "source": "inference",
            "keywords": ["backoff", "jitter", "retry", "api", "resilience"],
            "confidence": 0.8,
            "domain": "programming",
        },
        {
            "content": "The Darshana Architecture uses Samkhya tattvas as processing layers",
            "pramana": "pratyaksha",
            "source": "tool_output",
            "keywords": ["darshana", "samkhya", "tattva", "architecture", "layers"],
            "confidence": 0.95,
            "domain": "philosophy",
        },
        {
            "content": "Tailwind CSS utility classes reduce context switching compared to separate CSS files",
            "pramana": "upamana",
            "source": "inference",
            "keywords": ["tailwind", "css", "utility", "classes", "styling"],
            "confidence": 0.65,
            "domain": "programming",
        },
        {
            "content": "User's timezone is IST (UTC+5:30), based in India",
            "pramana": "pratyaksha",
            "source": "user_interaction",
            "keywords": ["timezone", "ist", "india", "utc"],
            "confidence": 0.99,
            "domain": "user_preference",
        },
    ]

    for mem in memories_to_store:
        record = memory.store(**mem)
        print(f"  Stored: {record}")

    print(f"\n  Total samskaras stored: {len(memories_to_store)}")

    # ------------------------------------------------------------------
    # 2. Retrieving relevant memories for a new query
    # ------------------------------------------------------------------
    divider("2. RECALLING MEMORIES (Retrieval)")

    queries = [
        "python naming conventions",
        "how should I structure React code",
        "what does the user prefer",
        "Hindu philosophy logic system",
    ]

    for query in queries:
        print(f"  Query: '{query}'")
        results = memory.recall(query, limit=3)
        if results:
            for r in results:
                print(f"    -> [{r.confidence:.2f}] {r.content[:70]}...")
        else:
            print(f"    -> No relevant memories found")
        print()

    # ------------------------------------------------------------------
    # 3. Confidence decay over simulated time
    # ------------------------------------------------------------------
    divider("3. CONFIDENCE DECAY (Simulated Time)")

    # Show current confidence levels
    print("  Before decay:")
    all_mems = memory._store.all_samskaras()
    for m in all_mems[:5]:
        print(f"    [{m.pramana.value:12s}] conf={m.confidence:.3f}  {m.content[:50]}...")

    # Simulate aging by backdating last_accessed
    # We'll directly update the database to simulate 60 days passing
    print("\n  Simulating 60 days passing...")
    sixty_days_ago = time.time() - (60 * 86400)
    with memory._store._connection() as conn:
        conn.execute("UPDATE samskaras SET last_accessed = ?", (sixty_days_ago,))

    # Now apply decay
    affected = memory.decay(half_life_days=30.0)
    print(f"  Decay applied to {affected} memories")

    print("\n  After decay (60 days, half-life=30 days):")
    all_mems = memory._store.all_samskaras()
    for m in all_mems[:5]:
        print(f"    [{m.pramana.value:12s}] conf={m.confidence:.3f}  {m.content[:50]}...")

    print("\n  Note: pratyaksha memories decay slowest (multiplier 0.5x),")
    print("        shabda memories decay fastest (multiplier 1.5x)")

    # Reset last_accessed to now for remaining demos
    with memory._store._connection() as conn:
        conn.execute("UPDATE samskaras SET last_accessed = ?", (time.time(),))

    # ------------------------------------------------------------------
    # 4. Vasana detection (accumulated bias)
    # ------------------------------------------------------------------
    divider("4. VASANA DETECTION (Accumulated Bias)")

    # First, update vasanas from current samskaras
    vasana_count = memory.update_vasanas()
    print(f"  Computed {vasana_count} vasanas from samskaras\n")

    # Show all vasanas
    all_vasanas = memory.vasana_engine.all_vasanas()
    for v in all_vasanas:
        print(f"  Domain: {v.domain}")
        print(f"    Strength: {v.strength:.3f}")
        print(f"    Based on: {v.samskara_count} samskaras")
        print(f"    Keywords: {', '.join(v.keywords[:5])}")
        print()

    # Check for bias in a response
    test_query = "What naming convention should I use?"
    test_response = (
        "You should use snake_case for all your code. "
        "Python's convention is the best approach for any language."
    )
    print(f"  Checking for bias in response to: '{test_query}'")
    print(f"  Response: '{test_response[:60]}...'")
    biases = memory.detect_bias(test_query, test_response)
    if biases:
        for b in biases:
            print(f"\n    WARNING: {b['warning']}")
    else:
        print(f"\n    No vasana-based bias detected.")

    # ------------------------------------------------------------------
    # 5. Building a context window for an LLM call
    # ------------------------------------------------------------------
    divider("5. CONTEXT WINDOW FOR LLM")

    context_query = "How should I structure a Python project with good naming?"
    print(f"  Query: '{context_query}'")
    print(f"  Max tokens: 2000\n")

    context = memory.context_window(context_query, max_tokens=2000)
    print(context)

    # ------------------------------------------------------------------
    # 6. Memory stats and gap detection
    # ------------------------------------------------------------------
    divider("6. MEMORY STATS & GAP DETECTION")

    stats = memory.stats()
    print("  Memory Statistics:")
    print(f"    Total memories: {stats['total_memories']}")
    print(f"    Average confidence: {stats['avg_confidence']:.4f}")
    print(f"    Total vasanas: {stats['total_vasanas']}")
    print(f"    Total retrievals: {stats['total_retrievals']}")
    print(f"\n    By pramana:")
    for p, n in stats["by_pramana"].items():
        print(f"      {p}: {n}")
    print(f"\n    By source:")
    for s, n in stats["by_source"].items():
        print(f"      {s}: {n}")
    print(f"\n    By domain:")
    for d, n in stats["by_domain"].items():
        print(f"      {d}: {n}")

    # Domain analysis
    print("\n  Domain Analysis:")
    for d in memory.domains():
        print(f"    {d['domain']}: {d['memory_count']} memories, avg confidence {d['avg_confidence']:.3f}")

    # Gap detection
    print("\n  Gap Detection:")
    gap_queries = [
        "python naming conventions",       # should have good coverage
        "kubernetes deployment strategies", # should have NO coverage
        "Darshana architecture layers",     # should have partial coverage
    ]
    for q in gap_queries:
        gap = memory.gaps(q)
        print(f"\n    Query: '{q}'")
        print(f"    Coverage: {gap['coverage']:.1%}")
        print(f"    Matched: {[m['term'] for m in gap['matched_terms']]}")
        print(f"    Unmatched: {gap['unmatched_terms']}")
        print(f"    Assessment: {gap['assessment']}")

    # ------------------------------------------------------------------
    # 7. Jnana Agni — burn outdated vasanas
    # ------------------------------------------------------------------
    divider("7. JNANA AGNI (Burning Outdated Vasanas)")

    print(f"  Vasanas before: {len(memory.vasana_engine.all_vasanas())}")

    # Burn weak vasanas
    burned = memory.jnana_agni(domain=None, before_date=None)
    print(f"  Burned (all): {burned}")

    # Rebuild and show
    memory.update_vasanas()
    print(f"  Vasanas after rebuild: {len(memory.vasana_engine.all_vasanas())}")

    # Burn only a specific domain
    burned = memory.vasana_engine.jnana_agni(domain="programming", min_strength=0.0)
    print(f"  Burned 'programming' vasana: {burned}")
    print(f"  Remaining vasanas: {len(memory.vasana_engine.all_vasanas())}")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    divider("DONE")
    print(f"  Database: {db_path}")
    print(f"  (Temporary file — will be cleaned up by OS)")

    # Clean up temp file
    try:
        os.unlink(db_path)
        print(f"  Cleaned up database file.")
    except OSError:
        pass

    print()


if __name__ == "__main__":
    main()
