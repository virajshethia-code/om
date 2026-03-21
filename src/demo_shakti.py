"""
demo_shakti.py -- Demonstrate the Shakti compute/energy management system
=========================================================================

Shows:
1. Model selection based on guna mode
2. Budget allocation for a session
3. Cache hit saving cost
4. Cost estimation before a query
5. Shakti report with usage breakdown
6. Efficiency scoring

Run:
    python -m src.demo_shakti
    # or
    python src/demo_shakti.py

No API keys needed -- this is pure simulation.
"""

from __future__ import annotations

import os
import sys
import tempfile

# Allow running as standalone script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shakti import ShaktiConfig, ShaktiManager, ModelTier


def divider(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    # Use a temporary database so we don't pollute the real one
    db_fd, db_path = tempfile.mkstemp(suffix=".db", prefix="shakti_demo_")
    os.close(db_fd)

    try:
        config = ShaktiConfig(
            daily_budget_usd=5.00,
            monthly_budget_usd=100.00,
            max_calls_per_minute=30,
            db_path=db_path,
        )
        shakti = ShaktiManager(config=config)

        # -----------------------------------------------------------------
        # 1. Model Selection based on Guna
        # -----------------------------------------------------------------
        divider("1. MODEL SELECTION BASED ON GUNA")

        test_cases = [
            ("sattva", 0.9, "Complex logic proof (high complexity)"),
            ("sattva", 0.5, "Moderate analysis (mid complexity)"),
            ("sattva", 0.1, "Simple fact check (low complexity)"),
            ("rajas",  0.5, "Creative brainstorm"),
            ("tamas",  0.2, "Retrieve a definition"),
        ]

        for guna, complexity, description in test_cases:
            spec, params = shakti.select_model(guna, complexity)
            print(f"  {description}")
            print(f"    Guna: {guna}, Complexity: {complexity}")
            print(f"    -> Model: {spec.name} ({spec.tier.value})")
            print(f"       Temp: {params['temperature']}, "
                  f"Max tokens: {params['max_tokens']}, "
                  f"Reason: {params['reason']}")
            print()

        # -----------------------------------------------------------------
        # 2. Budget Allocation for a Session
        # -----------------------------------------------------------------
        divider("2. BUDGET ALLOCATION FOR A SESSION")

        darshanas = ["nyaya", "vedanta", "yoga", "mimamsa", "samkhya", "vaisheshika"]
        for d in darshanas:
            normal_tokens = shakti.allocate(darshana=d, depth_mode="normal")
            deep_tokens = shakti.allocate(darshana=d, depth_mode="deep")
            print(f"  {d:12s}  normal: {normal_tokens:5d} tokens  "
                  f"deep: {deep_tokens:5d} tokens")

        remaining = shakti.remaining_budget()
        print(f"\n  Budget remaining: "
              f"${remaining['daily_remaining_usd']:.2f} today, "
              f"${remaining['monthly_remaining_usd']:.2f} this month")

        # -----------------------------------------------------------------
        # 3. Simulate some API calls to populate the ledger
        # -----------------------------------------------------------------
        divider("3. SIMULATING API CALLS")

        # Simulate a session of mixed calls
        simulated_calls = [
            # (darshana, guna, model, tier, tokens_in, tokens_out, cost, latency)
            ("nyaya",       "sattva", "claude-opus-4-20250514",   "opus",   850, 1600, 0.1328, 3200),
            ("vedanta",     "sattva", "claude-opus-4-20250514",   "opus",   920, 2100, 0.1713, 4100),
            ("yoga",        "tamas",  "claude-haiku-4-20250514",  "haiku",  480,  700, 0.0032, 800),
            ("mimamsa",     "rajas",  "claude-sonnet-4-20250514", "sonnet", 620, 1050, 0.0177, 1500),
            ("samkhya",     "sattva", "claude-sonnet-4-20250514", "sonnet", 710, 1180, 0.0198, 1800),
            ("vaisheshika", "tamas",  "claude-haiku-4-20250514",  "haiku",  550,  850, 0.0038, 900),
            # Some wasteful calls: tamas queries on opus
            ("yoga",        "tamas",  "claude-opus-4-20250514",   "opus",   500,  800, 0.0675, 2000),
            ("mimamsa",     "tamas",  "claude-opus-4-20250514",   "opus",   600,  900, 0.0765, 2200),
            # Repeat query (will be cached)
            ("nyaya",       "sattva", "claude-sonnet-4-20250514", "sonnet", 850, 1500, 0.0480, 1600),
        ]

        for i, (d, g, model, tier, tin, tout, cost, lat) in enumerate(simulated_calls):
            qhash = shakti.query_hash(f"simulated query {i} about {d}", d, g)
            shakti.spend(
                tokens_in=tin,
                tokens_out=tout,
                model=model,
                tier=tier,
                cost=cost,
                darshana=d,
                guna=g,
                query_hash=qhash,
                latency_ms=lat,
            )
            print(f"  [{i+1}] {d:12s} {g:7s} {tier:6s} "
                  f"${cost:.4f} ({tin}+{tout} tokens, {lat}ms)")

        total_spent = sum(c[6] for c in simulated_calls)
        print(f"\n  Total simulated spend: ${total_spent:.4f}")

        # -----------------------------------------------------------------
        # 4. Cache Hit Saving Cost
        # -----------------------------------------------------------------
        divider("4. CACHE HIT SAVING COST")

        # Cache a response
        test_query = "What are the five niyamas in Yoga philosophy?"
        qhash = shakti.query_hash(test_query, "yoga", "tamas")

        print(f"  Query: \"{test_query}\"")
        print(f"  Hash:  {qhash}")
        print()

        # First check -- miss
        cached = shakti.check_cache(qhash)
        print(f"  First check: {'HIT' if cached else 'MISS'}")

        # Cache the response
        response_text = (
            "The five niyamas (observances) in Yoga are: "
            "1. Shaucha (cleanliness), 2. Santosha (contentment), "
            "3. Tapas (discipline), 4. Svadhyaya (self-study), "
            "5. Ishvara Pranidhana (surrender to a higher principle)."
        )
        shakti.cache_response(qhash, response_text, darshana="yoga", guna="tamas")
        print(f"  Cached response ({len(response_text)} chars, TTL={config.cache_ttl}s)")

        # Second check -- hit
        cached = shakti.check_cache(qhash)
        print(f"  Second check: {'HIT' if cached else 'MISS'}")
        if cached:
            print(f"    Response: {cached['response'][:80]}...")
            print(f"    Hit count: {cached['hit_count']}")
            print(f"    Pramana: smriti (from memory -- zero cost)")

        # Record the cache hit in the ledger
        shakti.spend(
            tokens_in=0, tokens_out=0, model="cache",
            tier="cache", cost=0.0, darshana="yoga",
            guna="tamas", query_hash=qhash, cache_hit=True,
        )
        print(f"\n  Cost of cache hit: $0.0000")

        # Estimate what it WOULD have cost
        est = shakti.estimate_cost(
            test_query, darshana="yoga", depth_mode="normal", guna="tamas"
        )
        print(f"  Cost if we had called the LLM: ${est['estimated_cost_usd']:.4f} "
              f"({est['model']}, ~{est['estimated_input_tokens']}+{est['estimated_output_tokens']} tokens)")

        # -----------------------------------------------------------------
        # 5. Cost Estimation Before a Query
        # -----------------------------------------------------------------
        divider("5. COST ESTIMATION BEFORE A QUERY")

        estimation_cases = [
            ("Prove that P implies Q using modus ponens",
             "nyaya", "deep", "sattva", 0.8),
            ("What are the components of a React application?",
             "vaisheshika", "normal", "tamas", 0.2),
            ("Generate 10 creative names for a meditation app",
             "yoga", "normal", "rajas", 0.4),
            ("Synthesize the arguments for and against microservices",
             "vedanta", "deep", "sattva", 0.9),
        ]

        for query, d, depth, guna, complexity in estimation_cases:
            est = shakti.estimate_cost(query, d, depth, guna, complexity)
            proceed, reason = shakti.should_proceed(est["estimated_cost_usd"])
            print(f"  \"{query[:50]}...\"")
            print(f"    Darshana: {d}, Depth: {depth}, Guna: {guna}")
            print(f"    Model: {est['model']} ({est['tier']})")
            print(f"    Est. tokens: {est['estimated_input_tokens']} in / "
                  f"{est['estimated_output_tokens']} out")
            print(f"    Est. cost: ${est['estimated_cost_usd']:.6f}")
            print(f"    Proceed: {'YES' if proceed else 'NO'} ({reason})")
            print()

        # -----------------------------------------------------------------
        # 6. Shakti Report with Usage Breakdown
        # -----------------------------------------------------------------
        divider("6. SHAKTI REPORT")
        print(shakti.format_report())

        # -----------------------------------------------------------------
        # 7. Efficiency Scoring
        # -----------------------------------------------------------------
        divider("7. EFFICIENCY SCORING")

        eff = shakti.efficiency_score()
        print(f"  Overall Efficiency: {eff['score']:.1%}")
        print()

        if eff["breakdown"]:
            print("  Breakdown by guna+tier:")
            for combo, data in eff["breakdown"].items():
                bar = "#" * int(data["efficiency"] * 20)
                print(f"    {combo:16s}  ${data['cost']:.4f}  "
                      f"({data['calls']} calls)  "
                      f"eff={data['efficiency']:.0%} {bar}")
            print()

        if eff["suggestions"]:
            print("  Optimization suggestions:")
            for s in eff["suggestions"]:
                print(f"    * {s}")
        else:
            print("  No optimization suggestions -- good allocation!")

        # -----------------------------------------------------------------
        # 8. PranaScheduler demo
        # -----------------------------------------------------------------
        divider("8. PRANA SCHEDULER (Rate Limiting)")

        prana = shakti.prana
        print(f"  Status: {prana.status()}")

        # Simulate rate limiting
        print(f"\n  Simulating 5 rapid calls:")
        for i in range(5):
            wait = prana.breathe()
            if wait > 0:
                print(f"    Call {i+1}: wait {wait:.1f}s")
            else:
                print(f"    Call {i+1}: proceed immediately")

        # Simulate failures triggering circuit breaker
        print(f"\n  Simulating API failures:")
        for i in range(6):
            delay = prana.record_failure()
            print(f"    Failure {i+1}: backoff={delay:.1f}s, "
                  f"circuit={'OPEN' if prana.circuit_open else 'closed'}")

        # Show circuit breaker effect on model selection
        spec, params = shakti.select_model("sattva", 0.9)
        print(f"\n  Model selection with open circuit:")
        print(f"    Requested: sattva, complexity=0.9 (would normally get opus)")
        print(f"    Got: {spec.name} ({spec.tier.value}) -- {params['reason']}")

        # Reset
        prana.reset()
        print(f"\n  After reset: {prana.status()}")

        print(f"\n{'='*60}")
        print(f"  Demo complete. Temp DB: {db_path}")
        print(f"{'='*60}")

    finally:
        # Clean up temp database
        try:
            os.unlink(db_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()
