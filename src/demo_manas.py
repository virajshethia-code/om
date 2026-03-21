#!/usr/bin/env python3
"""
demo_manas.py — Demonstration of the Manas Attention/Context Management System
===============================================================================

Shows all six capabilities of Manas:
1. Adding items to the context window
2. Relevance scoring as query changes
3. Eviction when over token budget
4. Three attention modes producing different contexts
5. Conversation tracking with summarization
6. Attention report showing what's in/out

Run:
    python -m src.demo_manas
    # or
    python src/demo_manas.py

Author: Harsh (with Claude as co-thinker)
"""

from __future__ import annotations

import sys
import os

# Allow running as script or module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.manas import (
    Manas,
    DhyanaPipeline,
    ConversationTracker,
    AttentionMode,
    ContextSource,
    create_manas,
)


def divider(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_1_adding_items():
    """Demo 1: Adding items to the context window."""
    divider("DEMO 1: Adding Items to the Context Window")

    manas = create_manas(
        max_tokens=50_000,
        system_prompt="You are a Darshana reasoning engine. Apply the six schools of Hindu philosophy as cognitive frameworks.",
    )

    # Add various types of context
    manas.add(
        "The user is building an ERP system for a crane manufacturing company.",
        source="memory",
        importance=0.8,
        topic="erp",
    )
    manas.add(
        "Previous analysis showed that database latency is the primary bottleneck.",
        source="memory",
        importance=0.7,
        topic="performance",
    )
    manas.add(
        "The current stack is React + Supabase with ~50 concurrent users.",
        source="perception",
        importance=0.6,
        topic="architecture",
    )
    manas.add(
        "User asked: Should we switch from Supabase to a self-hosted PostgreSQL?",
        source="conversation",
        importance=0.5,
    )
    manas.add(
        "Supabase free tier has a 500MB database limit. Current usage: 340MB.",
        source="perception",
        importance=0.7,
        topic="infrastructure",
    )
    manas.add(
        "The Nyaya engine concluded: the argument for self-hosting is logically valid but the premises about cost savings are unverified.",
        source="inference",
        importance=0.6,
        topic="database",
    )

    print(f"Items in context: {len(manas._items)}")
    print(f"Total tokens:     {manas.current_tokens()}")
    print(f"Pinned items:     {sum(1 for i in manas._items if i.pinned)}")
    print()

    for item in manas._items:
        pin = "[PINNED]" if item.pinned else "       "
        print(f"  {pin} [{item.source.value:12s}] imp={item.importance_score:.1f}  "
              f"tokens={item.token_estimate:4d}  {item.content[:60]}...")

    return manas


def demo_2_relevance_scoring(manas: Manas):
    """Demo 2: Relevance scoring as query changes."""
    divider("DEMO 2: Relevance Scoring as Query Changes")

    queries = [
        "What is the database performance bottleneck?",
        "How much does Supabase cost vs self-hosted PostgreSQL?",
        "What React components need refactoring?",
    ]

    for query in queries:
        print(f"QUERY: \"{query}\"")
        manas.refresh_scores(query)

        scored = sorted(manas._items, key=lambda i: -i.relevance_score)
        for item in scored:
            pin = "*" if item.pinned else " "
            bar = "#" * int(item.relevance_score * 20)
            print(f"  {pin} rel={item.relevance_score:.3f} [{bar:20s}] {item.content[:55]}...")

        print()

    return manas


def demo_3_eviction():
    """Demo 3: Eviction when over token budget."""
    divider("DEMO 3: Eviction Under Token Budget Pressure")

    # Create a small-budget manas to force eviction
    manas = Manas(max_tokens=200)  # very tight — roughly 800 chars

    manas.add("CRITICAL: Always validate user input before database writes.", source="system", pinned=True)

    items_text = [
        ("High-priority bug: login form crashes on Safari.", "perception", 0.9),
        ("Meeting notes from last sprint planning.", "memory", 0.3),
        ("User preferences: dark mode, compact tables.", "memory", 0.4),
        ("API response times averaged 450ms yesterday.", "perception", 0.6),
        ("The team decided to use TypeScript for all new code.", "memory", 0.7),
        ("Old discussion about Python vs JavaScript for backend.", "memory", 0.2),
        ("Current deployment uses Vercel with auto-scaling.", "perception", 0.5),
        ("User asked about export functionality last session.", "conversation", 0.3),
    ]

    print(f"Budget: {manas.max_tokens} tokens")
    print(f"Adding {len(items_text) + 1} items...\n")

    for content, source, importance in items_text:
        manas.add(content, source=source, importance=importance)
        tokens = manas.current_tokens()
        evicted_count = len(manas._evicted)
        status = "OVER BUDGET - evicting!" if tokens > manas.max_tokens else "within budget"
        print(f"  +add ({tokens:4d} tokens, {evicted_count} evicted) {status}")

    print(f"\n--- Final state ---")
    print(f"  Active items:  {len(manas._items)}")
    print(f"  Evicted items: {len(manas._evicted)}")
    print(f"  Total tokens:  {manas.current_tokens()}")
    print()

    print("  Surviving items:")
    for item in manas._items:
        pin = "[PINNED]" if item.pinned else "       "
        print(f"    {pin} score={item.combined_score:.3f}  {item.content[:55]}...")

    print("\n  Evicted items:")
    for item in manas._evicted:
        print(f"           score={item.combined_score:.3f}  {item.content[:55]}...")


def demo_4_attention_modes():
    """Demo 4: Three attention modes producing different contexts."""
    divider("DEMO 4: Three Attention Modes (Pratyahara / Dharana / Dhyana)")

    manas = create_manas(max_tokens=50_000, system_prompt="Darshana reasoning engine.")

    # Add a mix of items at different relevance levels
    items = [
        ("Database query optimization techniques for PostgreSQL.", "memory", 0.8, "database"),
        ("The user's company has 50 employees across 3 locations.", "memory", 0.4, "company"),
        ("React rendering performance can be improved with memo.", "memory", 0.3, "frontend"),
        ("PostgreSQL EXPLAIN output showed sequential scan on orders table.", "perception", 0.9, "database"),
        ("Indexes on (customer_id, order_date) would help the slow query.", "inference", 0.85, "database"),
        ("Company holiday policy: 15 days PTO per year.", "memory", 0.1, "hr"),
        ("Previous conversation about hiring a DBA.", "conversation", 0.5, "database"),
        ("Supabase connection pooling is limited to 60 connections.", "perception", 0.7, "database"),
        ("The marketing team wants a new landing page.", "conversation", 0.15, "marketing"),
        ("Node.js event loop can bottleneck under CPU-heavy workloads.", "memory", 0.35, "backend"),
    ]

    for content, source, importance, topic in items:
        manas.add(content, source=source, importance=importance, topic=topic)

    query = "How do we fix the slow database queries?"

    for mode_name in ["pratyahara", "dharana", "dhyana"]:
        mode_label = {
            "pratyahara": "PRATYAHARA (broad/withdrawal)",
            "dharana": "DHARANA (focused/concentration)",
            "dhyana": "DHYANA (deep/meditation)",
        }[mode_name]

        # Reset scores between modes (since refresh_scores mutates state)
        for item in manas._items:
            item.query_age = 0

        context = manas.assemble(query, mode=mode_name)
        lines = [l for l in context.split('\n') if l.strip()]

        print(f"--- {mode_label} ---")
        print(f"    Items passing threshold: {len(lines)} lines")
        print(f"    Context length: {len(context)} chars (~{len(context)//4} tokens)")
        print()
        # Show first few lines
        for line in lines[:8]:
            print(f"    {line[:75]}")
        if len(lines) > 8:
            print(f"    ... ({len(lines) - 8} more lines)")
        print()


def demo_5_conversation_tracking():
    """Demo 5: Conversation tracking with summarization."""
    divider("DEMO 5: Conversation Tracking with Summarization")

    tracker = ConversationTracker(
        max_turns_before_summary=6,
        summary_group_size=4,
    )

    # Simulate a multi-turn conversation
    conversation = [
        ("user", "We need to improve our ERP system's performance. What should we look at first?"),
        ("assistant", "I'd recommend starting with database query analysis. The most common bottlenecks in ERP systems are: 1) Missing indexes on frequently queried columns, 2) N+1 query patterns in ORM usage, 3) Unoptimized report generation queries."),
        ("user", "Good point. We decided to focus on the reports first because they're the most user-visible."),
        ("assistant", "Smart choice. For report optimization, I'd suggest: materialized views for summary reports, query caching for repeated parameter combinations, and async generation for large exports. Should I analyze your specific report queries?"),
        ("user", "Yes, but I prefer we start with the order summary report. It takes 30 seconds to load."),
        ("assistant", "30 seconds is very slow. Let me look at that. The order summary report likely involves joining orders, line_items, customers, and products tables. With 50 concurrent users, that's a significant load."),
        ("user", "Exactly. We also want to add a new dashboard for the warehouse team."),
        ("assistant", "For the warehouse dashboard, I'd recommend a real-time approach using Supabase's realtime subscriptions. However, given the performance concerns, we should optimize the underlying queries first before adding new load."),
        ("user", "That makes sense. Let's prioritize: 1) Fix order report, 2) Then warehouse dashboard."),
        ("assistant", "Agreed. I'll focus on the order summary report optimization. Key decisions: reports first, order summary specifically, then warehouse dashboard after."),
    ]

    for i, (role, content) in enumerate(conversation):
        tracker.add_turn(role, content)
        unsummarized = sum(1 for t in tracker._turns if not t.summarized)
        label = f"Turn {i+1:2d}"
        print(f"  {label}: [{role:9s}] {content[:50]}...")
        if tracker.summary_count > 0 and unsummarized <= tracker.max_turns_before_summary:
            # A compaction just happened
            if i > 0 and sum(1 for t in tracker._turns[:i] if not t.summarized) > unsummarized:
                print(f"           >>> Compaction triggered! Summaries: {tracker.summary_count}")

    print(f"\n--- Conversation State ---")
    print(f"  Total turns:      {tracker.turn_count}")
    print(f"  Summaries:        {tracker.summary_count}")
    print(f"  Unsummarized:     {sum(1 for t in tracker._turns if not t.summarized)}")

    print(f"\n--- get_history(max_tokens=800) ---")
    history = tracker.get_history(max_tokens=800)
    print(history)


def demo_6_attention_report():
    """Demo 6: Attention report showing what's in and what's out."""
    divider("DEMO 6: Attention Report + What Am I Missing?")

    manas = Manas(max_tokens=300)

    manas.add("Always use parameterized queries to prevent SQL injection.", source="system", pinned=True)
    manas.add("PostgreSQL supports partial indexes for filtered queries.", source="memory", importance=0.8, topic="database")
    manas.add("The order table has 2.3 million rows.", source="perception", importance=0.9, topic="database")
    manas.add("React 19 introduced new concurrent features.", source="memory", importance=0.3, topic="frontend")
    manas.add("Team standup is at 9:30 AM daily.", source="memory", importance=0.1, topic="process")
    manas.add("EXPLAIN ANALYZE on the order query shows hash join cost of 45000.", source="perception", importance=0.85, topic="database")
    manas.add("The CEO wants the report fixed by Friday.", source="conversation", importance=0.7, topic="deadline")

    # Some items got evicted due to tight budget
    report = manas.report()

    print(f"--- Attention Report ---")
    print(f"  Active items:    {report['active_count']}")
    print(f"  Evicted items:   {report['evicted_count']}")
    print(f"  Tokens used:     {report['total_tokens']} / {report['max_tokens']}")
    print(f"  Utilization:     {report['utilization_pct']}%")
    print(f"  Pinned items:    {report['pinned_count']}")

    print(f"\n  Active items (by combined score):")
    for item in report["items"]:
        pin = "[PIN]" if item["pinned"] else "     "
        print(f"    {pin} score={item['combined']:.3f} rel={item['relevance']:.2f} "
              f"imp={item['importance']:.2f} {item['content_preview'][:45]}")

    if report["evicted"]:
        print(f"\n  Recently evicted:")
        for item in report["evicted"]:
            print(f"          score={item['combined']:.3f} {item['content_preview'][:45]}")

    # What am I missing?
    query = "How to optimize the database query performance?"
    missing = manas.what_am_i_missing(query)

    if missing:
        print(f"\n--- What Am I Missing? (query: \"{query}\") ---")
        for item in missing:
            print(f"  relevance={item['would_be_relevance']:.3f}  {item['content_preview'][:55]}")
    else:
        print(f"\n  No relevant evicted items found for: \"{query}\"")


def demo_dhyana_pipeline():
    """Bonus: DhyanaPipeline deep focus mode."""
    divider("BONUS: DhyanaPipeline (Deep Focus)")

    manas = create_manas(max_tokens=50_000, system_prompt="Darshana engine: deep analysis mode.")

    # Populate with mixed topics
    db_items = [
        "PostgreSQL VACUUM ANALYZE should run after bulk inserts.",
        "Index-only scans avoid heap fetches when all columns are in the index.",
        "Connection pooling with PgBouncer reduces connection overhead.",
        "The slow query joins 4 tables: orders, items, customers, products.",
        "Adding a composite index on (customer_id, order_date) reduced query time by 60%.",
    ]
    other_items = [
        "The React app uses TanStack Query for server state management.",
        "Tailwind CSS v4 has a new configuration system.",
        "The marketing team requested a new email template.",
    ]

    for text in db_items:
        manas.add(text, source="memory", importance=0.8, topic="database")
    for text in other_items:
        manas.add(text, source="memory", importance=0.4, topic="frontend")

    pipeline = DhyanaPipeline(manas)

    # Deep focus on database
    print("Topic: 'database query optimization'\n")

    deep_context = pipeline.focus("database query optimization")
    print(f"Context assembled: {len(deep_context)} chars (~{len(deep_context)//4} tokens)")
    print()

    for line in deep_context.split('\n'):
        if line.strip():
            print(f"  {line}")

    print()
    focus_report = pipeline.report("database query optimization")
    print(f"  Matching items:  {focus_report['matching_items']}")
    print(f"  Matching tokens: {focus_report['total_tokens']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  MANAS (manas) — Attention/Context Management")
    print("  The inner sense organ that coordinates all other senses.")
    print("  Part of the Darshana Architecture.")
    print()

    # Demo 1 & 2: adding and scoring
    manas = demo_1_adding_items()
    demo_2_relevance_scoring(manas)

    # Demo 3: eviction
    demo_3_eviction()

    # Demo 4: attention modes
    demo_4_attention_modes()

    # Demo 5: conversation tracking
    demo_5_conversation_tracking()

    # Demo 6: attention report
    demo_6_attention_report()

    # Bonus: deep focus
    demo_dhyana_pipeline()

    divider("COMPLETE")
    print("Manas manages what the system pays attention to.")
    print("Without it, intelligence is just data flooding a fixed window.")
    print("With it, every token in the context window EARNS its place.\n")


if __name__ == "__main__":
    main()
