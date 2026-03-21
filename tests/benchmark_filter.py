#!/usr/bin/env python3
"""
benchmark_filter.py — Vritti Filter Accuracy Benchmark
========================================================

10 text samples spanning all 5 vritti categories. Validates that the
VrittiFilter correctly classifies each type of mental modification
before it reaches the user.

This is the output gate of the Darshana Architecture — the last line
of defence between the system's reasoning and the user's screen.

Vritti categories (Yoga Sutra 1.5-1.11):
    1. Pramana    — valid cognition, grounded in evidence
    2. Viparyaya  — misconception, logical error
    3. Vikalpa    — verbal delusion, sounds right but empty
    4. Nidra      — absence of knowledge, the system is guessing
    5. Smriti     — memory recall, encyclopedic regurgitation

Runs entirely offline — no API keys, no LLM calls.

Usage:
    python -m tests.benchmark_filter   (from /Users/harsh/om/)
    python tests/benchmark_filter.py   (from /Users/harsh/om/)

Author: Harsh (with Claude as co-thinker)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure the src directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vritti_filter import VrittiFilter, Vritti, Pramana, VrittiResult


# ---------------------------------------------------------------------------
# The 10 benchmark samples
# ---------------------------------------------------------------------------

BENCHMARK_SAMPLES: list[dict] = [
    # --- PRAMANA (Valid cognition) — 2 samples ---
    {
        "id": 1,
        "text": (
            "According to the PostgreSQL 16 documentation (https://www.postgresql.org/docs/16/), "
            "JSONB columns support GIN indexes. Because our query filters on nested JSON fields, "
            "therefore adding a GIN index on the 'metadata' column will reduce scan time from "
            "sequential O(n) to index-assisted O(log n). Specifically, the query "
            "SELECT * FROM events WHERE metadata @> '{\"type\": \"click\"}' "
            "showed a 94% improvement in our benchmark of 1.2 million rows."
        ),
        "expected": "pramana",
        "category": "PRAMANA",
        "why": "Cited source, specific numbers, logical chain from premise to conclusion.",
    },
    {
        "id": 2,
        "text": (
            "The memory leak originates in the WebSocket handler at line 247 of server.py. "
            "Data shows that each connection allocates a 64KB buffer that is never freed "
            "on disconnect. Evidence: heap profiler output shows 12,847 unreleased Buffer "
            "objects after 3 hours of load testing with 500 concurrent connections, "
            "consuming 803MB. The fix is to call buffer.release() in the on_close callback."
        ),
        "expected": "pramana",
        "category": "PRAMANA",
        "why": "Grounded in direct observation (pratyaksha), specific, actionable.",
    },
    # --- VIPARYAYA (Misconception / logical error) — 2 samples ---
    {
        "id": 3,
        "text": (
            "All successful startups use microservices, therefore if we use microservices "
            "we will be successful. Every company that failed was using monoliths, which "
            "proves that monoliths always lead to failure. Since no one has ever succeeded "
            "with a monolith, the proof is clear that microservices are the only viable "
            "architecture."
        ),
        "expected": "viparyaya",
        "category": "VIPARYAYA",
        "why": "Multiple fallacies: affirming the consequent, false absolutes, overgeneralisation.",
    },
    {
        "id": 4,
        "text": (
            "The code is correct because it passes all tests. The tests are correct because "
            "they were written to match the code. Therefore the system is proven to be "
            "bug-free. Since the tests never fail, there can never be any bugs, and "
            "all users who report issues are wrong."
        ),
        "expected": "viparyaya",
        "category": "VIPARYAYA",
        "why": "Circular reasoning (viruddha), proof claim, absolute quantifiers.",
    },
    # --- VIKALPA (Verbal delusion / empty hedging) — 2 samples ---
    {
        "id": 5,
        "text": (
            "Essentially, the situation is essentially one where various factors "
            "could potentially play a role in some ways. It is widely recognized "
            "that certain experts believe this might possibly be an area where, "
            "to some extent, progress could potentially be made, though it is "
            "what it is at the end of the day."
        ),
        "expected": "vikalpa",
        "category": "VIKALPA",
        "why": "Circular hedging, anonymous authority, double hedging, cliches.",
    },
    {
        "id": 6,
        "text": (
            "In a sense, the architecture could might potentially offer some "
            "benefits in certain scenarios. Various experts suggest that this "
            "approach may possibly have merit, and it has been broadly acknowledged "
            "that to some extent these considerations are extremely important "
            "in the broader context of the overall landscape."
        ),
        "expected": "vikalpa",
        "category": "VIKALPA",
        "why": "Every sentence hedges, no falsifiable claim, intensifier-stacking.",
    },
    # --- NIDRA (Absence of knowledge) — 2 samples ---
    {
        "id": 7,
        "text": (
            "I'm not sure about the specifics of this configuration. Generally, "
            "it depends on many factors and there are various considerations. "
            "Typically the answer varies depending on context, and in many cases "
            "it's complicated. I'm unable to verify the exact details."
        ),
        "expected": "nidra",
        "category": "NIDRA",
        "why": "Explicit uncertainty, deflection to context, complexity shield.",
    },
    {
        "id": 8,
        "text": (
            "There is no simple answer to this. It depends on your specific use "
            "case and there are many factors to consider. Generally speaking, "
            "the results will vary. In many cases, the best approach depends "
            "on context. Usually the right choice is situational."
        ),
        "expected": "nidra",
        "category": "NIDRA",
        "why": "All deflection, no substance — the system has nothing to say.",
    },
    # --- SMRITI (Memory recall / encyclopedic) — 2 samples ---
    {
        "id": 9,
        "text": (
            "Kubernetes was founded in 2014 by Google. It is defined as an "
            "open-source container orchestration platform. Docker was invented "
            "by Solomon Hykes and was published in 2013. According to the CNCF, "
            "Kubernetes is the process of automating deployment, scaling, and "
            "management of containerized applications."
        ),
        "expected": "smriti",
        "category": "SMRITI",
        "why": "Encyclopedic pattern, date-anchored facts, textbook definitions.",
    },
    {
        "id": 10,
        "text": (
            "REST is defined as Representational State Transfer. It was a "
            "concept established in 2000 by Roy Fielding. HTTP is the process "
            "of transferring hypertext documents. As stated by Fielding, REST "
            "is a type of architectural style for distributed hypermedia systems. "
            "GraphQL was invented by Facebook and published in 2015."
        ),
        "expected": "smriti",
        "category": "SMRITI",
        "why": "Pure recall — definitions, dates, attributed facts, no fresh reasoning.",
    },
    # --- DISGUISED SMRITI (sounds analytical, is just recall) — 2 samples ---
    {
        "id": 11,
        "text": (
            "The Israeli-Palestinian conflict has been a major source of "
            "instability in the Middle East. It's well known that the "
            "occupation has been a key factor in the ongoing tensions. "
            "The settlements have been a significant obstacle to peace. "
            "Obviously, the humanitarian situation has been a critical "
            "concern for the international community. As everyone knows, "
            "the two-state solution has been the primary diplomatic "
            "framework discussed by world leaders."
        ),
        "expected": "smriti",
        "category": "SMRITI",
        "why": "Disguised recall: every claim is common knowledge wrapped in analytical framing.",
    },
    {
        "id": 12,
        "text": (
            "Climate change has been a defining challenge of our era. "
            "Rising sea levels have been a major concern for coastal "
            "communities. Obviously, carbon emissions have been the "
            "primary driver of global warming. It's well known that "
            "the Paris Agreement was a significant milestone. Renewable "
            "energy has been a key part of the solution, and as everyone "
            "knows, solar and wind costs have fallen dramatically."
        ),
        "expected": "smriti",
        "category": "SMRITI",
        "why": "Disguised recall: organized Wikipedia with 'obviously' and 'well known' framing.",
    },
    # --- GENUINE ANUMANA (real novel reasoning chain) — 1 sample ---
    {
        "id": 13,
        "text": (
            "What most analyses of database performance miss is that the "
            "bottleneck isn't the query engine — it's the serialization layer. "
            "Because each row must be deserialized from the on-disk format, "
            "which involves memory allocation, this creates GC pressure that "
            "causes latency spikes. This implies that columnar storage isn't "
            "just faster for analytics — it actually reduces garbage collection "
            "overhead, which is the real reason Parquet outperforms row-based "
            "formats in JVM-based systems. Therefore the fix for our p99 "
            "latency spike at 890ms is not query optimization but changing "
            "the storage format."
        ),
        "expected": "pramana",
        "category": "PRAMANA",
        "why": "Genuine anumana: novel causal chain connecting serialization to GC to latency.",
    },
    # --- PRAMANA-VRITTI MISMATCH — 1 sample ---
    {
        "id": 14,
        "text": (
            "Kubernetes was founded in 2014 by Google. It is defined as an "
            "open-source container orchestration platform. Docker was invented "
            "by Solomon Hykes."
        ),
        "expected": "smriti",
        "category": "SMRITI",
        "why": "Cross-validation test: if tagged as pratyaksha pramana, the mismatch should fire.",
        "cross_validate": {
            "pramana_tag": "pratyaksha",
            "expect_mismatch": True,
        },
    },
    # --- DEPTH TEST PASS — 1 sample ---
    {
        "id": 15,
        "text": (
            "The memory leak originates in the WebSocket handler at line 247. "
            "Data shows each connection allocates a 64KB buffer never freed "
            "on disconnect — 12,847 unreleased Buffer objects after 3 hours "
            "with 500 concurrent connections, consuming 803MB. Therefore the "
            "OOM kill at hour 4 is caused by this specific leak. This implies "
            "the fix is not to increase memory but to call buffer.release() in "
            "the on_close callback. Consequently any handler creating buffers "
            "without a cleanup hook will reproduce this failure."
        ),
        "expected": "pramana",
        "category": "PRAMANA",
        "why": "Passes depth test: specific evidence, reasoning chain, non-obvious conclusion.",
        "depth_test": {
            "query": "Why does the server crash after 4 hours?",
            "expect_score_above": 50,
        },
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_benchmark() -> None:
    """Execute all 15 samples and print a formatted report."""

    vf = VrittiFilter()
    results: list[dict] = []
    timings: list[float] = []
    cross_validation_results: list[dict] = []
    depth_test_results: list[dict] = []

    pramana_map = {
        "pratyaksha": Pramana.PRATYAKSHA,
        "anumana": Pramana.ANUMANA,
        "upamana": Pramana.UPAMANA,
        "shabda": Pramana.SHABDA,
    }

    for entry in BENCHMARK_SAMPLES:
        t0 = time.perf_counter()
        classification = vf.classify(entry["text"])
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        timings.append(elapsed_ms)

        actual = classification.vritti.value
        correct = actual == entry["expected"]

        result_entry = {
            "id": entry["id"],
            "category": entry["category"],
            "expected": entry["expected"],
            "actual": actual,
            "correct": correct,
            "confidence": classification.confidence,
            "explanation": classification.explanation,
            "fallacies": [f.value for f in classification.fallacies],
            "suggestions": classification.suggestions,
            "time_ms": elapsed_ms,
            "text_preview": entry["text"][:80] + "...",
            "why": entry["why"],
        }

        # Cross-validation extra
        if "cross_validate" in entry:
            cv = entry["cross_validate"]
            tag = pramana_map[cv["pramana_tag"]]
            report = vf.cross_validate(classification, tag)
            cv_pass = (not report.consistent) == cv["expect_mismatch"]
            result_entry["cross_validate_pass"] = cv_pass
            cross_validation_results.append({
                "id": entry["id"],
                "consistent": report.consistent,
                "expected_mismatch": cv["expect_mismatch"],
                "pass": cv_pass,
                "mismatches": [m.flag for m in report.mismatches],
            })

        # Depth test extra
        if "depth_test" in entry:
            dt = entry["depth_test"]
            depth = vf.depth_test(entry["text"], dt["query"])
            dt_pass = depth.score >= dt["expect_score_above"]
            result_entry["depth_test_pass"] = dt_pass
            depth_test_results.append({
                "id": entry["id"],
                "score": depth.score,
                "threshold": dt["expect_score_above"],
                "pass": dt_pass,
                "breakdown": depth.breakdown,
            })

        results.append(result_entry)

    # --- Compute stats ---
    total = len(results)
    correct_count = sum(1 for r in results if r["correct"])
    accuracy = correct_count / total
    correct_confs = [r["confidence"] for r in results if r["correct"]]
    incorrect_confs = [r["confidence"] for r in results if not r["correct"]]
    avg_correct_conf = sum(correct_confs) / len(correct_confs) if correct_confs else 0.0
    avg_incorrect_conf = sum(incorrect_confs) / len(incorrect_confs) if incorrect_confs else 0.0

    # --- Print report ---
    print()
    print("=" * 100)
    print("  VRITTI FILTER BENCHMARK — 15 Text Samples Across 5 Vritti Categories")
    print("  (includes disguised smriti, cross-validation, and depth tests)")
    print("=" * 100)
    print()

    # Main results table
    hdr = f"{'#':>2}  {'Category':<12} {'Expected':<12} {'Classified':<12} {'Conf':>6} {'Time':>7}  {'':>4}  Preview"
    print(hdr)
    print("-" * len(hdr) + "-" * 30)

    for r in results:
        mark = " OK " if r["correct"] else "MISS"
        style = "" if r["correct"] else " <<"
        print(
            f"{r['id']:>2}  "
            f"{r['category']:<12} "
            f"{r['expected']:<12} "
            f"{r['actual']:<12} "
            f"{r['confidence']:>5.3f} "
            f"{r['time_ms']:>6.2f}ms "
            f"[{mark}] "
            f"{r['text_preview'][:50]}...{style}"
        )

    print()
    print("-" * 100)
    print()

    # Summary
    print("SUMMARY")
    print(f"  Accuracy:                 {correct_count}/{total} ({accuracy:.0%})")
    print(f"  Avg confidence (correct): {avg_correct_conf:.3f}")
    if incorrect_confs:
        print(f"  Avg confidence (wrong):   {avg_incorrect_conf:.3f}")
    else:
        print(f"  Avg confidence (wrong):   n/a (no misclassifications)")
    print()

    # Timing
    avg_time = sum(timings) / len(timings)
    print("TIMING")
    print(f"  Average:   {avg_time:.3f} ms per sample")
    print(f"  Min:       {min(timings):.3f} ms")
    print(f"  Max:       {max(timings):.3f} ms")
    print()

    # Per-vritti accuracy
    print("PER-VRITTI ACCURACY")
    categories = ["PRAMANA", "VIPARYAYA", "VIKALPA", "NIDRA", "SMRITI"]
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_correct = sum(1 for r in cat_results if r["correct"])
        cat_total = len(cat_results)
        pct = (cat_correct / cat_total * 100) if cat_total > 0 else 0
        bar = "#" * int(pct / 5)
        print(f"  {cat:<12} {cat_correct}/{cat_total}  ({pct:5.1f}%)  {bar}")
    print()

    # Detailed results for each sample
    print("DETAILED CLASSIFICATION RESULTS")
    print("-" * 90)
    for r in results:
        mark = "CORRECT" if r["correct"] else "MISCLASSIFIED"
        print(f"  Sample #{r['id']} [{mark}]")
        print(f"    Expected:    {r['expected']}")
        print(f"    Classified:  {r['actual']} (confidence {r['confidence']:.3f})")
        print(f"    Explanation: {r['explanation'][:100]}...")
        if r["fallacies"]:
            print(f"    Fallacies:   {', '.join(r['fallacies'])}")
        if r["suggestions"]:
            for s in r["suggestions"][:2]:
                print(f"    Suggestion:  {s}")
        print(f"    Why expected: {r['why']}")
        print()

    # Misclassified
    misses = [r for r in results if not r["correct"]]
    if misses:
        print("MISCLASSIFIED SAMPLES")
        print("-" * 90)
        for r in misses:
            print(f"  Sample #{r['id']}:")
            print(f"    Text: {r['text_preview']}")
            print(f"    Expected {r['expected']} but got {r['actual']} (conf {r['confidence']:.3f})")
            print(f"    Why expected: {r['why']}")
            print(f"    Filter's explanation: {r['explanation'][:120]}")
            print()
        print("  NOTE: Misclassifications reveal where vritti categories overlap.")
        print("  A text with both viparyaya (errors) and vikalpa (hedging)")
        print("  signals is genuinely ambiguous — the filter picks the stronger signal.")
        print()
    else:
        print(f"NO MISCLASSIFICATIONS — all {total} samples classified correctly.")
        print()

    # Cross-validation results
    if cross_validation_results:
        print("CROSS-VALIDATION RESULTS (FIX 2)")
        print("-" * 90)
        for cv in cross_validation_results:
            mark = "PASS" if cv["pass"] else "FAIL"
            print(f"  Sample #{cv['id']} [{mark}]")
            print(f"    Consistent: {cv['consistent']}, Expected mismatch: {cv['expected_mismatch']}")
            if cv["mismatches"]:
                for m in cv["mismatches"]:
                    print(f"    Mismatch: {m[:100]}")
            print()

    # Depth test results
    if depth_test_results:
        print("DEPTH TEST RESULTS (FIX 3)")
        print("-" * 90)
        for dt in depth_test_results:
            mark = "PASS" if dt["pass"] else "FAIL"
            print(f"  Sample #{dt['id']} [{mark}]")
            print(f"    Score: {dt['score']}/100 (threshold: {dt['threshold']})")
            print(f"    Breakdown: {dt['breakdown']}")
            print()

    # Novelty scores for all samples
    print("NOVELTY SCORES (FIX 1)")
    print("-" * 90)
    for entry in BENCHMARK_SAMPLES:
        ns = vf.novelty_score(entry["text"])
        print(f"  Sample #{entry['id']:>2} ({entry['category']:<12}): novelty={ns:>3}/100")
    print()

    # Final verdict
    print("=" * 100)
    if accuracy >= 0.9:
        print(f"  VERDICT: {accuracy:.0%} accuracy. The Vritti Filter catches what it should.")
    elif accuracy >= 0.7:
        print(f"  VERDICT: {accuracy:.0%} accuracy. Good discrimination, patterns can be tuned.")
    else:
        print(f"  VERDICT: {accuracy:.0%} accuracy. Pattern library needs expansion.")
    print("=" * 100)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_benchmark()
