"""
shakti.py -- Compute/Energy Management for the Darshana Architecture
====================================================================

Shakti (शक्ति) from root शक् (shak, to be able/powerful) -- energy, power,
capacity. In Hindu philosophy, Shiva (consciousness/architecture) is inert
without Shakti (energy/compute). The architecture is nothing without
intelligent energy allocation.

Every LLM call costs money and time. Shakti solves this by:

1. Selecting the cheapest model that can handle the task (guna-aware)
2. Tracking token budgets so you never blow past $100/day
3. Caching previous responses (tamas optimization -- smriti pramana)
4. Rate-limiting gracefully with exponential backoff (PranaScheduler)
5. Recording every call in a persistent ledger for cost analysis

Components:

    ShaktiConfig     -- budget, model tiers, rate limits
    ShaktiManager    -- the main compute allocator
    PranaScheduler   -- rate limiting, backoff, circuit breaker
    ShaktiLedger     -- persistent SQLite cost tracking

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Model tier enum
# ---------------------------------------------------------------------------

class ModelTier(Enum):
    """Model tiers ordered by cost and capability."""
    HAIKU = "haiku"
    SONNET = "sonnet"
    OPUS = "opus"


# ---------------------------------------------------------------------------
# ShaktiConfig -- energy configuration
# ---------------------------------------------------------------------------

@dataclass
class ModelSpec:
    """Specification for a single model tier."""
    name: str                    # Anthropic model identifier
    tier: ModelTier
    cost_per_1k_input: float     # USD per 1K input tokens
    cost_per_1k_output: float    # USD per 1K output tokens
    max_tokens: int              # max output tokens
    default_temperature: float   # default temperature for this tier


@dataclass
class ShaktiConfig:
    """
    Energy configuration for the Darshana system.

    Controls budgets, model selection, and rate limits. Defaults are
    conservative -- a researcher or solo dev who wants to keep costs
    under $5/day.
    """
    # Budget
    daily_budget_usd: float = 5.00
    monthly_budget_usd: float = 100.00

    # Rate limits
    max_calls_per_minute: int = 30
    max_tokens_per_call: int = 4096

    # Model definitions (Anthropic Claude pricing as of 2025)
    models: Dict[str, ModelSpec] = field(default_factory=dict)

    # Cache TTL in seconds (default 1 hour)
    cache_ttl: int = 3600

    # Database path for ledger and cache
    db_path: str = "shakti.db"

    def __post_init__(self):
        if not self.models:
            self.models = {
                ModelTier.HAIKU: ModelSpec(
                    name="claude-haiku-4-20250514",
                    tier=ModelTier.HAIKU,
                    cost_per_1k_input=0.0008,
                    cost_per_1k_output=0.004,
                    max_tokens=4096,
                    default_temperature=0.3,
                ),
                ModelTier.SONNET: ModelSpec(
                    name="claude-sonnet-4-20250514",
                    tier=ModelTier.SONNET,
                    cost_per_1k_input=0.003,
                    cost_per_1k_output=0.015,
                    max_tokens=4096,
                    default_temperature=0.5,
                ),
                ModelTier.OPUS: ModelSpec(
                    name="claude-opus-4-20250514",
                    tier=ModelTier.OPUS,
                    cost_per_1k_input=0.015,
                    cost_per_1k_output=0.075,
                    max_tokens=4096,
                    default_temperature=0.3,
                ),
            }

    def get_model(self, tier: ModelTier) -> ModelSpec:
        return self.models[tier]

    def estimate_call_cost(
        self, tier: ModelTier, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost in USD for a single call."""
        spec = self.models[tier]
        return (
            (input_tokens / 1000.0) * spec.cost_per_1k_input
            + (output_tokens / 1000.0) * spec.cost_per_1k_output
        )


# ---------------------------------------------------------------------------
# ShaktiLedger -- persistent cost tracking (SQLite)
# ---------------------------------------------------------------------------

class ShaktiLedger:
    """
    Persistent cost tracking in SQLite.

    Every LLM call is recorded with full metadata: model, tokens, cost,
    which darshana engine, which guna mode, and a query hash for cache
    correlation.

    This is the karma-ledger of compute -- every action recorded, nothing
    lost, patterns emerge from accumulation.
    """

    DDL = """
    CREATE TABLE IF NOT EXISTS shakti_ledger (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp   TEXT    NOT NULL,
        model       TEXT    NOT NULL,
        tier        TEXT    NOT NULL,
        tokens_in   INTEGER NOT NULL,
        tokens_out  INTEGER NOT NULL,
        cost_usd    REAL    NOT NULL,
        darshana    TEXT    NOT NULL DEFAULT '',
        guna        TEXT    NOT NULL DEFAULT '',
        query_hash  TEXT    NOT NULL DEFAULT '',
        cache_hit   INTEGER NOT NULL DEFAULT 0,
        latency_ms  REAL    NOT NULL DEFAULT 0.0
    );

    CREATE TABLE IF NOT EXISTS shakti_cache (
        query_hash  TEXT    PRIMARY KEY,
        response    TEXT    NOT NULL,
        darshana    TEXT    NOT NULL DEFAULT '',
        guna        TEXT    NOT NULL DEFAULT '',
        created_at  TEXT    NOT NULL,
        expires_at  TEXT    NOT NULL,
        hit_count   INTEGER NOT NULL DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON shakti_ledger(timestamp);
    CREATE INDEX IF NOT EXISTS idx_ledger_darshana ON shakti_ledger(darshana);
    CREATE INDEX IF NOT EXISTS idx_ledger_guna ON shakti_ledger(guna);
    CREATE INDEX IF NOT EXISTS idx_cache_expires ON shakti_cache(expires_at);
    """

    def __init__(self, db_path: str = "shakti.db"):
        self.db_path = db_path
        self._local = threading.local()
        # Initialize tables using a temporary connection
        conn = self._get_conn()
        conn.executescript(self.DDL)
        conn.commit()

    def _get_conn(self) -> sqlite3.Connection:
        """Thread-local connection to avoid SQLite threading issues."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    # -- Recording --

    def record(
        self,
        model: str,
        tier: str,
        tokens_in: int,
        tokens_out: int,
        cost_usd: float,
        darshana: str = "",
        guna: str = "",
        query_hash: str = "",
        cache_hit: bool = False,
        latency_ms: float = 0.0,
    ) -> None:
        """Record a single LLM call in the ledger."""
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO shakti_ledger
               (timestamp, model, tier, tokens_in, tokens_out, cost_usd,
                darshana, guna, query_hash, cache_hit, latency_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.utcnow().isoformat(),
                model,
                tier,
                tokens_in,
                tokens_out,
                cost_usd,
                darshana,
                guna,
                query_hash,
                1 if cache_hit else 0,
                latency_ms,
            ),
        )
        conn.commit()

    # -- Summaries --

    def _sum_since(self, since: str) -> Dict[str, Any]:
        """Aggregate costs and tokens since a given ISO timestamp."""
        conn = self._get_conn()
        row = conn.execute(
            """SELECT
                 COUNT(*)          AS calls,
                 COALESCE(SUM(tokens_in), 0)   AS total_in,
                 COALESCE(SUM(tokens_out), 0)  AS total_out,
                 COALESCE(SUM(cost_usd), 0.0)  AS total_cost,
                 COALESCE(SUM(cache_hit), 0)    AS cache_hits
               FROM shakti_ledger
               WHERE timestamp >= ?""",
            (since,),
        ).fetchone()
        return {
            "calls": row["calls"],
            "tokens_in": row["total_in"],
            "tokens_out": row["total_out"],
            "cost_usd": round(row["total_cost"], 6),
            "cache_hits": row["cache_hits"],
        }

    def daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Summary for a single day (default: today)."""
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        return self._sum_since(date + "T00:00:00")

    def weekly_summary(self) -> Dict[str, Any]:
        since = (datetime.utcnow() - timedelta(days=7)).isoformat()
        return self._sum_since(since)

    def monthly_summary(self) -> Dict[str, Any]:
        since = (datetime.utcnow() - timedelta(days=30)).isoformat()
        return self._sum_since(since)

    def cost_per_darshana(self) -> Dict[str, float]:
        """Total cost breakdown by darshana engine (all time)."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT darshana, SUM(cost_usd) AS cost
               FROM shakti_ledger
               WHERE darshana != ''
               GROUP BY darshana
               ORDER BY cost DESC"""
        ).fetchall()
        return {row["darshana"]: round(row["cost"], 6) for row in rows}

    def cost_per_guna(self) -> Dict[str, float]:
        """Total cost breakdown by guna mode (all time)."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT guna, SUM(cost_usd) AS cost
               FROM shakti_ledger
               WHERE guna != ''
               GROUP BY guna
               ORDER BY cost DESC"""
        ).fetchall()
        return {row["guna"]: round(row["cost"], 6) for row in rows}

    def cost_per_tier(self) -> Dict[str, float]:
        """Total cost breakdown by model tier (all time)."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT tier, SUM(cost_usd) AS cost
               FROM shakti_ledger
               GROUP BY tier
               ORDER BY cost DESC"""
        ).fetchall()
        return {row["tier"]: round(row["cost"], 6) for row in rows}

    def most_expensive_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return the most expensive queries by total cost."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT query_hash, SUM(cost_usd) AS total_cost,
                      COUNT(*) AS call_count,
                      GROUP_CONCAT(DISTINCT darshana) AS darshanas
               FROM shakti_ledger
               WHERE query_hash != ''
               GROUP BY query_hash
               ORDER BY total_cost DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [
            {
                "query_hash": row["query_hash"],
                "total_cost": round(row["total_cost"], 6),
                "call_count": row["call_count"],
                "darshanas": row["darshanas"] or "",
            }
            for row in rows
        ]

    def total_calls(self) -> int:
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) AS c FROM shakti_ledger").fetchone()
        return row["c"]

    # -- Cache operations --

    def cache_get(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached response if it exists and hasn't expired."""
        conn = self._get_conn()
        now = datetime.utcnow().isoformat()
        row = conn.execute(
            """SELECT response, darshana, guna, created_at, hit_count
               FROM shakti_cache
               WHERE query_hash = ? AND expires_at > ?""",
            (query_hash, now),
        ).fetchone()
        if row is None:
            return None
        # Increment hit count
        conn.execute(
            "UPDATE shakti_cache SET hit_count = hit_count + 1 WHERE query_hash = ?",
            (query_hash,),
        )
        conn.commit()
        return {
            "response": row["response"],
            "darshana": row["darshana"],
            "guna": row["guna"],
            "created_at": row["created_at"],
            "hit_count": row["hit_count"] + 1,
        }

    def cache_put(
        self,
        query_hash: str,
        response: str,
        darshana: str = "",
        guna: str = "",
        ttl: int = 3600,
    ) -> None:
        """Store a response in the cache with a TTL in seconds."""
        conn = self._get_conn()
        now = datetime.utcnow()
        expires = now + timedelta(seconds=ttl)
        conn.execute(
            """INSERT OR REPLACE INTO shakti_cache
               (query_hash, response, darshana, guna, created_at, expires_at, hit_count)
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (
                query_hash,
                response,
                darshana,
                guna,
                now.isoformat(),
                expires.isoformat(),
            ),
        )
        conn.commit()

    def cache_stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        conn = self._get_conn()
        now = datetime.utcnow().isoformat()
        total = conn.execute("SELECT COUNT(*) AS c FROM shakti_cache").fetchone()["c"]
        active = conn.execute(
            "SELECT COUNT(*) AS c FROM shakti_cache WHERE expires_at > ?", (now,)
        ).fetchone()["c"]
        total_hits = conn.execute(
            "SELECT COALESCE(SUM(hit_count), 0) AS h FROM shakti_cache"
        ).fetchone()["h"]
        return {"total_entries": total, "active_entries": active, "total_hits": total_hits}

    def cache_clear_expired(self) -> int:
        """Remove expired cache entries. Returns count removed."""
        conn = self._get_conn()
        now = datetime.utcnow().isoformat()
        cursor = conn.execute(
            "DELETE FROM shakti_cache WHERE expires_at <= ?", (now,)
        )
        conn.commit()
        return cursor.rowcount


# ---------------------------------------------------------------------------
# PranaScheduler -- rate limiting, backoff, circuit breaker
# ---------------------------------------------------------------------------

class PranaScheduler:
    """
    Prana (प्राण) -- breath, vital force, rhythm.

    Manages the rhythm of API calls: rate limiting, exponential backoff
    on errors, and a circuit breaker that switches to cheaper models
    when the expensive ones keep failing.

    The metaphor is breathing: steady rhythm under normal conditions,
    slower and deeper when stressed, and an emergency shift when the
    system is suffocating.
    """

    def __init__(
        self,
        max_calls_per_minute: int = 30,
        backoff_base: float = 1.0,
        backoff_max: float = 60.0,
        circuit_breaker_threshold: int = 5,
    ):
        self.max_calls_per_minute = max_calls_per_minute
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.circuit_breaker_threshold = circuit_breaker_threshold

        # State
        self._call_timestamps: List[float] = []
        self._consecutive_failures: int = 0
        self._circuit_open: bool = False
        self._last_failure_time: float = 0.0
        self._lock = threading.Lock()

    @property
    def circuit_open(self) -> bool:
        """True if the circuit breaker has tripped (too many failures)."""
        return self._circuit_open

    @property
    def consecutive_failures(self) -> int:
        return self._consecutive_failures

    def breathe(self) -> float:
        """
        Rate limiter. Returns the number of seconds to wait before the
        next call can proceed. Returns 0.0 if the call can proceed
        immediately.

        Call this BEFORE every API call. If it returns > 0, sleep that
        long (or use asyncio.sleep in async code).
        """
        with self._lock:
            now = time.monotonic()
            # Prune timestamps older than 60 seconds
            cutoff = now - 60.0
            self._call_timestamps = [
                t for t in self._call_timestamps if t > cutoff
            ]

            if len(self._call_timestamps) >= self.max_calls_per_minute:
                # Must wait until the oldest call in the window expires
                oldest = self._call_timestamps[0]
                wait = 60.0 - (now - oldest) + 0.1  # small buffer
                return max(wait, 0.0)

            # Record this call
            self._call_timestamps.append(now)
            return 0.0

    def record_success(self) -> None:
        """Record a successful API call. Resets failure counter."""
        with self._lock:
            self._consecutive_failures = 0
            self._circuit_open = False

    def record_failure(self) -> float:
        """
        Record a failed API call. Returns the backoff delay in seconds.

        If consecutive failures exceed the circuit breaker threshold,
        the circuit opens -- signaling that the caller should switch
        to a cheaper/different model.
        """
        with self._lock:
            self._consecutive_failures += 1
            self._last_failure_time = time.monotonic()

            if self._consecutive_failures >= self.circuit_breaker_threshold:
                self._circuit_open = True

            # Exponential backoff: base * 2^(failures-1), capped
            delay = min(
                self.backoff_base * (2 ** (self._consecutive_failures - 1)),
                self.backoff_max,
            )
            return delay

    def reset(self) -> None:
        """Full reset of the scheduler state."""
        with self._lock:
            self._call_timestamps.clear()
            self._consecutive_failures = 0
            self._circuit_open = False
            self._last_failure_time = 0.0

    def status(self) -> Dict[str, Any]:
        """Current scheduler status."""
        with self._lock:
            now = time.monotonic()
            cutoff = now - 60.0
            recent = [t for t in self._call_timestamps if t > cutoff]
            return {
                "calls_last_minute": len(recent),
                "max_calls_per_minute": self.max_calls_per_minute,
                "consecutive_failures": self._consecutive_failures,
                "circuit_open": self._circuit_open,
                "utilization": round(len(recent) / self.max_calls_per_minute, 3),
            }


# ---------------------------------------------------------------------------
# ShaktiManager -- the main compute allocator
# ---------------------------------------------------------------------------

class ShaktiManager:
    """
    The central compute allocator for the Darshana Architecture.

    Responsibilities:
    - Select the right model based on guna mode and task complexity
    - Track and enforce token budgets (daily/monthly)
    - Estimate costs before committing to a call
    - Check cache before calling the LLM (tamas optimization)
    - Generate usage reports with efficiency scoring

    Usage::

        shakti = ShaktiManager()
        model, params = shakti.select_model(guna="sattva", task_complexity=0.8)
        if shakti.should_proceed(estimated_cost=0.02):
            # make the call...
            shakti.spend(tokens_in=500, tokens_out=1000,
                         model=model, cost=0.02, darshana="nyaya", guna="sattva")
    """

    # Typical token usage per darshana (input + output estimates)
    DARSHANA_TOKEN_PROFILES: Dict[str, Dict[str, int]] = {
        "nyaya":       {"input": 800, "output": 1500},   # formal logic is verbose
        "vaisheshika": {"input": 600, "output": 1000},   # decomposition is structured
        "samkhya":     {"input": 700, "output": 1200},   # classification/enumeration
        "yoga":        {"input": 500, "output": 800},    # focused, concise
        "mimamsa":     {"input": 600, "output": 1000},   # text-to-action, moderate
        "vedanta":     {"input": 900, "output": 2000},   # synthesis is the most expansive
    }

    # Depth mode multipliers
    DEPTH_MULTIPLIERS: Dict[str, float] = {
        "deep": 2.0,    # deep mode uses ~2x tokens
        "broad": 1.5,   # broad (multi-engine) uses ~1.5x per engine
        "normal": 1.0,
    }

    def __init__(self, config: Optional[ShaktiConfig] = None):
        self.config = config or ShaktiConfig()
        self.ledger = ShaktiLedger(db_path=self.config.db_path)
        self.prana = PranaScheduler(
            max_calls_per_minute=self.config.max_calls_per_minute,
        )

    # -- Model Selection --

    def select_model(
        self,
        guna: str,
        task_complexity: float = 0.5,
    ) -> Tuple[ModelSpec, Dict[str, Any]]:
        """
        Select the appropriate model based on guna mode and task complexity.

        Guna-to-tier mapping:
        - sattva (precision): best available model for complex tasks,
          sonnet for moderate, haiku only for trivial
        - rajas (exploration): sonnet with higher temperature --
          opus is wasted on creative divergence
        - tamas (retrieval): haiku or cache -- cheapest possible

        Args:
            guna: Processing mode ("sattva", "rajas", "tamas").
            task_complexity: 0.0 (trivial) to 1.0 (extremely complex).

        Returns:
            Tuple of (ModelSpec, parameters dict with temperature, max_tokens).
        """
        # Circuit breaker override: if the expensive models keep failing,
        # fall back to haiku regardless
        if self.prana.circuit_open:
            spec = self.config.get_model(ModelTier.HAIKU)
            return spec, {
                "temperature": spec.default_temperature,
                "max_tokens": min(spec.max_tokens, self.config.max_tokens_per_call),
                "reason": "circuit_breaker_fallback",
            }

        # Budget check: if we're over 90% of daily budget, force haiku
        daily = self.ledger.daily_summary()
        budget_usage = daily["cost_usd"] / self.config.daily_budget_usd if self.config.daily_budget_usd > 0 else 0
        if budget_usage > 0.9:
            spec = self.config.get_model(ModelTier.HAIKU)
            return spec, {
                "temperature": spec.default_temperature,
                "max_tokens": min(spec.max_tokens, self.config.max_tokens_per_call),
                "reason": "budget_conservation",
            }

        if guna == "tamas":
            # Tamas: cheapest model, low tokens, low temperature
            spec = self.config.get_model(ModelTier.HAIKU)
            return spec, {
                "temperature": 0.2,
                "max_tokens": min(2048, self.config.max_tokens_per_call),
                "reason": "tamas_efficiency",
            }

        elif guna == "rajas":
            # Rajas: mid-tier, higher temperature for exploration
            spec = self.config.get_model(ModelTier.SONNET)
            return spec, {
                "temperature": 0.8,
                "max_tokens": self.config.max_tokens_per_call,
                "reason": "rajas_exploration",
            }

        else:
            # Sattva: tier depends on complexity
            if task_complexity >= 0.7:
                tier = ModelTier.OPUS
            elif task_complexity >= 0.3:
                tier = ModelTier.SONNET
            else:
                tier = ModelTier.HAIKU

            spec = self.config.get_model(tier)
            return spec, {
                "temperature": spec.default_temperature,
                "max_tokens": self.config.max_tokens_per_call,
                "reason": f"sattva_complexity_{task_complexity:.1f}",
            }

    # -- Token Budget Management --

    def allocate(self, darshana: str = "", depth_mode: str = "normal") -> int:
        """
        How many output tokens this task should get based on remaining budget.

        Returns a recommended max_tokens value. If budget is tight, this
        will be lower than the config default.
        """
        remaining = self.remaining_budget()
        if remaining["daily_remaining_usd"] <= 0:
            return 256  # minimal survival tokens

        # Base allocation from darshana profile
        profile = self.DARSHANA_TOKEN_PROFILES.get(darshana, {"output": 1000})
        base_tokens = profile["output"]

        # Apply depth multiplier
        multiplier = self.DEPTH_MULTIPLIERS.get(depth_mode, 1.0)
        recommended = int(base_tokens * multiplier)

        # Cap at config limit
        recommended = min(recommended, self.config.max_tokens_per_call)

        # If budget is getting tight (< 25% remaining), reduce allocation
        daily_fraction = remaining["daily_remaining_usd"] / self.config.daily_budget_usd
        if daily_fraction < 0.25:
            recommended = int(recommended * daily_fraction * 2)  # scale down
            recommended = max(recommended, 256)  # but never below 256

        return recommended

    def spend(
        self,
        tokens_in: int,
        tokens_out: int,
        model: str,
        tier: str,
        cost: float,
        darshana: str = "",
        guna: str = "",
        query_hash: str = "",
        cache_hit: bool = False,
        latency_ms: float = 0.0,
    ) -> None:
        """Record a spend in the ledger."""
        self.ledger.record(
            model=model,
            tier=tier,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost,
            darshana=darshana,
            guna=guna,
            query_hash=query_hash,
            cache_hit=cache_hit,
            latency_ms=latency_ms,
        )

    def remaining_budget(self) -> Dict[str, float]:
        """What's left today and this month."""
        daily = self.ledger.daily_summary()
        monthly = self.ledger.monthly_summary()
        return {
            "daily_spent_usd": daily["cost_usd"],
            "daily_remaining_usd": round(
                self.config.daily_budget_usd - daily["cost_usd"], 6
            ),
            "monthly_spent_usd": monthly["cost_usd"],
            "monthly_remaining_usd": round(
                self.config.monthly_budget_usd - monthly["cost_usd"], 6
            ),
        }

    def should_proceed(self, estimated_cost: float) -> Tuple[bool, str]:
        """
        Check if we should proceed with a call given its estimated cost.

        Returns:
            (proceed: bool, reason: str)
        """
        remaining = self.remaining_budget()

        if remaining["daily_remaining_usd"] < estimated_cost:
            return False, (
                f"Daily budget exhausted. "
                f"Remaining: ${remaining['daily_remaining_usd']:.4f}, "
                f"Estimated: ${estimated_cost:.4f}"
            )

        if remaining["monthly_remaining_usd"] < estimated_cost:
            return False, (
                f"Monthly budget exhausted. "
                f"Remaining: ${remaining['monthly_remaining_usd']:.4f}, "
                f"Estimated: ${estimated_cost:.4f}"
            )

        if remaining["daily_remaining_usd"] < estimated_cost * 2:
            return True, (
                f"WARNING: This call will use >{50}% of remaining daily budget. "
                f"Remaining: ${remaining['daily_remaining_usd']:.4f}"
            )

        return True, "OK"

    # -- Cost Estimation --

    def estimate_cost(
        self,
        query: str,
        darshana: str = "",
        depth_mode: str = "normal",
        guna: str = "sattva",
        task_complexity: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Estimate the cost of a query before executing it.

        Takes into account the darshana engine's typical token usage,
        the depth mode, and the model tier that would be selected for
        the given guna.
        """
        # Get expected model
        spec, params = self.select_model(guna, task_complexity)

        # Get token estimates
        profile = self.DARSHANA_TOKEN_PROFILES.get(
            darshana, {"input": 700, "output": 1000}
        )
        multiplier = self.DEPTH_MULTIPLIERS.get(depth_mode, 1.0)

        # Add query length to input estimate
        query_tokens = len(query.split()) * 1.3  # rough approximation
        est_input = int((profile["input"] + query_tokens) * multiplier)
        est_output = int(profile["output"] * multiplier)

        cost = self.config.estimate_call_cost(spec.tier, est_input, est_output)

        return {
            "model": spec.name,
            "tier": spec.tier.value,
            "estimated_input_tokens": est_input,
            "estimated_output_tokens": est_output,
            "estimated_cost_usd": round(cost, 6),
            "depth_mode": depth_mode,
            "reason": params.get("reason", ""),
        }

    # -- Caching (Tamas optimization) --

    @staticmethod
    def query_hash(query: str, darshana: str = "", guna: str = "") -> str:
        """Generate a deterministic hash for a query + context."""
        raw = f"{query.strip().lower()}|{darshana}|{guna}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def check_cache(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """
        Check if a response exists in cache.

        A cache hit means zero cost -- the response is tagged as
        pramana=smriti (from memory, not fresh reasoning).
        """
        return self.ledger.cache_get(query_hash)

    def cache_response(
        self,
        query_hash: str,
        response: str,
        darshana: str = "",
        guna: str = "",
        ttl: Optional[int] = None,
    ) -> None:
        """Store a response in the cache."""
        if ttl is None:
            ttl = self.config.cache_ttl
        self.ledger.cache_put(
            query_hash=query_hash,
            response=response,
            darshana=darshana,
            guna=guna,
            ttl=ttl,
        )

    # -- Shakti Report --

    def report(self) -> Dict[str, Any]:
        """
        Full Shakti usage report: today, this week, this month.
        Broken down by model tier, darshana, and guna.
        """
        daily = self.ledger.daily_summary()
        weekly = self.ledger.weekly_summary()
        monthly = self.ledger.monthly_summary()
        remaining = self.remaining_budget()
        cache = self.ledger.cache_stats()

        return {
            "daily": daily,
            "weekly": weekly,
            "monthly": monthly,
            "budget": {
                "daily_budget_usd": self.config.daily_budget_usd,
                "daily_remaining_usd": remaining["daily_remaining_usd"],
                "monthly_budget_usd": self.config.monthly_budget_usd,
                "monthly_remaining_usd": remaining["monthly_remaining_usd"],
            },
            "by_tier": self.ledger.cost_per_tier(),
            "by_darshana": self.ledger.cost_per_darshana(),
            "by_guna": self.ledger.cost_per_guna(),
            "cache": cache,
            "prana": self.prana.status(),
            "most_expensive_queries": self.ledger.most_expensive_queries(5),
        }

    def efficiency_score(self) -> Dict[str, Any]:
        """
        Ratio of insight-per-token.

        Efficiency is measured by how much of the budget goes to
        appropriate model tiers. Specifically:

        - Tamas queries handled by haiku = efficient
        - Tamas queries handled by opus = wasteful
        - Sattva queries handled by opus = appropriate (if complex)
        - Cache hits = maximally efficient

        Returns a score from 0.0 (all waste) to 1.0 (perfect allocation),
        plus optimization suggestions.
        """
        conn = self.ledger._get_conn()

        # Get guna/tier distribution
        rows = conn.execute(
            """SELECT guna, tier, SUM(cost_usd) AS cost, COUNT(*) AS calls
               FROM shakti_ledger
               WHERE guna != '' AND tier != ''
               GROUP BY guna, tier"""
        ).fetchall()

        if not rows:
            return {
                "score": 1.0,
                "suggestions": ["No data yet -- start making calls."],
                "breakdown": {},
            }

        total_cost = sum(row["cost"] for row in rows)
        if total_cost == 0:
            return {"score": 1.0, "suggestions": [], "breakdown": {}}

        # Score each guna/tier combination
        # Efficient = tamas+haiku, sattva+opus (complex), rajas+sonnet
        # Wasteful = tamas+opus, tamas+sonnet
        efficiency_map = {
            ("tamas", "haiku"):  1.0,
            ("tamas", "sonnet"): 0.3,
            ("tamas", "opus"):   0.1,
            ("rajas", "haiku"):  0.5,
            ("rajas", "sonnet"): 1.0,
            ("rajas", "opus"):   0.4,
            ("sattva", "haiku"): 0.6,
            ("sattva", "sonnet"): 0.8,
            ("sattva", "opus"):  1.0,
        }

        weighted_score = 0.0
        breakdown = {}
        suggestions = []

        for row in rows:
            key = (row["guna"], row["tier"])
            eff = efficiency_map.get(key, 0.5)
            weight = row["cost"] / total_cost
            weighted_score += eff * weight
            breakdown[f"{row['guna']}+{row['tier']}"] = {
                "cost": round(row["cost"], 6),
                "calls": row["calls"],
                "efficiency": eff,
            }

            # Generate suggestions for wasteful combinations
            if eff < 0.5 and row["cost"] > total_cost * 0.1:
                pct = round(row["cost"] / total_cost * 100)
                suggestions.append(
                    f"{pct}% of budget went to {row['tier']} on {row['guna']} tasks "
                    f"-- consider using a cheaper model."
                )

        # Bonus for cache hits
        cache = self.ledger.cache_stats()
        daily = self.ledger.daily_summary()
        if daily["calls"] > 0:
            cache_ratio = daily["cache_hits"] / daily["calls"]
            if cache_ratio > 0.3:
                weighted_score = min(1.0, weighted_score + 0.05)
            if cache_ratio < 0.1 and daily["calls"] > 10:
                suggestions.append(
                    "Low cache hit rate. Consider caching tamas (retrieval) queries."
                )

        return {
            "score": round(weighted_score, 3),
            "suggestions": suggestions,
            "breakdown": breakdown,
        }

    def format_report(self) -> str:
        """Human-readable Shakti report."""
        r = self.report()
        eff = self.efficiency_score()

        lines = [
            "=" * 60,
            "  SHAKTI REPORT -- Compute Energy Dashboard",
            "=" * 60,
            "",
            f"  Daily:   ${r['daily']['cost_usd']:.4f} spent "
            f"/ ${r['budget']['daily_budget_usd']:.2f} budget "
            f"({r['daily']['calls']} calls, {r['daily']['cache_hits']} cache hits)",
            f"  Weekly:  ${r['weekly']['cost_usd']:.4f} spent "
            f"({r['weekly']['calls']} calls)",
            f"  Monthly: ${r['monthly']['cost_usd']:.4f} spent "
            f"/ ${r['budget']['monthly_budget_usd']:.2f} budget "
            f"({r['monthly']['calls']} calls)",
            "",
            "  Remaining:",
            f"    Today: ${r['budget']['daily_remaining_usd']:.4f}",
            f"    Month: ${r['budget']['monthly_remaining_usd']:.4f}",
            "",
        ]

        if r["by_tier"]:
            lines.append("  Cost by Model Tier:")
            for tier, cost in r["by_tier"].items():
                lines.append(f"    {tier:8s}  ${cost:.6f}")
            lines.append("")

        if r["by_darshana"]:
            lines.append("  Cost by Darshana:")
            for d, cost in r["by_darshana"].items():
                lines.append(f"    {d:12s}  ${cost:.6f}")
            lines.append("")

        if r["by_guna"]:
            lines.append("  Cost by Guna:")
            for g, cost in r["by_guna"].items():
                lines.append(f"    {g:8s}  ${cost:.6f}")
            lines.append("")

        lines.append(f"  Efficiency Score: {eff['score']:.1%}")
        if eff["suggestions"]:
            lines.append("  Suggestions:")
            for s in eff["suggestions"]:
                lines.append(f"    - {s}")

        lines.append("")
        lines.append(f"  Cache: {r['cache']['active_entries']} active entries, "
                      f"{r['cache']['total_hits']} total hits")

        prana = r["prana"]
        lines.append(f"  Prana: {prana['calls_last_minute']}/{prana['max_calls_per_minute']} "
                      f"calls/min, circuit={'OPEN' if prana['circuit_open'] else 'closed'}")

        if r["most_expensive_queries"]:
            lines.append("")
            lines.append("  Most Expensive Queries:")
            for q in r["most_expensive_queries"][:3]:
                lines.append(
                    f"    {q['query_hash'][:8]}... ${q['total_cost']:.6f} "
                    f"({q['call_count']} calls, {q['darshanas']})"
                )

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)
