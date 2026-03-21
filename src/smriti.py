"""
smriti.py — Persistent Memory System for the Darshana Architecture
===================================================================

Smriti (स्मृति) from root स्मृ (smṛ, to remember) — not passive storage, but
ACTIVE remembering. In Hindu philosophy, memory has structure:

    Samskara (संस्कार) — impressions left by experience. Not the experience
                         itself, but its TRACE. Like a groove worn in wood.

    Vasana (वासना)     — tendencies that accumulate from repeated samskaras.
                         Like weights in a neural net. They bias future action.

    Smriti (स्मृति)    — the act of recalling a samskara when triggered by
                         relevant context. Not retrieval — RECOGNITION.

This module replaces the in-memory KnowledgeMap (ahamkara.py) and the flat-JSON
KarmaStore (vritti_filter.py) with a proper SQLite-backed memory system that
persists across sessions and supports decay, strengthening, bias detection,
and intelligent retrieval.

Philosophical basis:
    Yoga Sutra 1.11: anubhūta-viṣayāsampramoṣaḥ smṛtiḥ
    "Memory is the non-stealing of an experienced object."
    — Memory is defined by what it RETAINS, not what it stores.

    Bhagavad Gita 4.37: jñānāgniḥ sarva-karmāṇi bhasmasāt kurute
    "The fire of knowledge burns all karma to ashes."
    — Outdated vasanas can and should be cleared (jnana_agni).

Architecture reference: THESIS.md, Karma/Vasana Store section.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PramanaType(Enum):
    """
    The four valid means of knowledge from Nyaya epistemology.

    Each pramana has a different decay rate — pratyaksha (direct observation)
    is the most durable, shabda (testimony) the least.
    """
    PRATYAKSHA = "pratyaksha"   # direct perception — tool output, user input
    ANUMANA    = "anumana"      # inference — derived by reasoning
    UPAMANA    = "upamana"      # analogy — understood by comparison
    SHABDA     = "shabda"       # testimony — from training data or authority

    @property
    def decay_multiplier(self) -> float:
        """
        How fast memories of this pramana type decay.
        Lower = slower decay = more durable.
        """
        return {
            PramanaType.PRATYAKSHA: 0.5,   # slowest decay — direct experience persists
            PramanaType.ANUMANA:    0.8,
            PramanaType.UPAMANA:    1.0,
            PramanaType.SHABDA:     1.5,   # fastest decay — hearsay fades quickest
        }[self]


class SourceType(Enum):
    """Where a memory originated."""
    USER_INTERACTION = "user_interaction"
    TOOL_OUTPUT      = "tool_output"
    INFERENCE        = "inference"
    TRAINING         = "training"
    CORRECTION       = "correction"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SamskaraRecord:
    """
    A single memory impression, as returned from the database.

    Not a raw row — a structured object with all fields parsed.
    """
    id: str
    content: str
    keywords: List[str]
    pramana: PramanaType
    source: SourceType
    confidence: float
    created_at: float
    last_accessed: float
    access_count: int
    darshana_context: str
    domain: str

    @property
    def age_days(self) -> float:
        return (time.time() - self.created_at) / 86400.0

    @property
    def recency_score(self) -> float:
        """Score from 0-1 based on how recently this was accessed. Half-life of 14 days."""
        days_since_access = (time.time() - self.last_accessed) / 86400.0
        return math.exp(-0.693 * days_since_access / 14.0)

    def __repr__(self) -> str:
        return (
            f"Samskara(id={self.id[:8]}..., confidence={self.confidence:.2f}, "
            f"pramana={self.pramana.value}, age={self.age_days:.1f}d, "
            f"accesses={self.access_count})"
        )


@dataclass
class VasanaRecord:
    """An accumulated tendency derived from repeated samskaras."""
    id: str
    domain: str
    tendency: str
    strength: float
    samskara_count: int
    last_updated: float
    keywords: List[str]

    def __repr__(self) -> str:
        return (
            f"Vasana(domain={self.domain}, strength={self.strength:.2f}, "
            f"samskaras={self.samskara_count})"
        )


# ---------------------------------------------------------------------------
# SmritiStore — the main memory class
# ---------------------------------------------------------------------------

class SmritiStore:
    """
    SQLite-backed persistent memory for the Darshana Architecture.

    This is the foundation layer. Everything else — VasanaEngine,
    RetrievalEngine, SmritiReport — operates on top of this store.

    Usage::

        store = SmritiStore()  # default: ~/.darshana/smriti.db
        store.store(
            content="User prefers concise code examples over verbose explanations",
            pramana="pratyaksha",
            source="user_interaction",
            keywords=["preference", "code", "concise"],
            darshana_context="mimamsa",
        )
        results = store.recall("code style preference", limit=5)
    """

    # Schema version for future migrations
    SCHEMA_VERSION = 1

    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Args:
            db_path: Path to SQLite database file.
                     Default: ~/.darshana/smriti.db
        """
        if db_path is None:
            db_dir = Path.home() / ".darshana"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(db_dir / "smriti.db")
        else:
            parent = Path(db_path).parent
            parent.mkdir(parents=True, exist_ok=True)
            self.db_path = db_path

        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Thread-safe connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        with self._connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS samskaras (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    keywords TEXT NOT NULL,           -- JSON array of strings
                    pramana TEXT NOT NULL,             -- pratyaksha/anumana/upamana/shabda
                    source TEXT NOT NULL,              -- user_interaction/tool_output/inference/training/correction
                    confidence REAL NOT NULL DEFAULT 0.8,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    darshana_context TEXT DEFAULT 'general',
                    domain TEXT DEFAULT 'general'
                );

                CREATE TABLE IF NOT EXISTS vasanas (
                    id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    tendency TEXT NOT NULL,
                    strength REAL NOT NULL DEFAULT 0.0,
                    samskara_count INTEGER NOT NULL DEFAULT 0,
                    last_updated REAL NOT NULL,
                    keywords TEXT NOT NULL DEFAULT '[]' -- JSON array
                );

                CREATE TABLE IF NOT EXISTS retrievals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    samskara_id TEXT NOT NULL,
                    relevance_score REAL NOT NULL,
                    retrieved_at REAL NOT NULL,
                    FOREIGN KEY (samskara_id) REFERENCES samskaras(id)
                );

                CREATE TABLE IF NOT EXISTS schema_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_samskaras_domain ON samskaras(domain);
                CREATE INDEX IF NOT EXISTS idx_samskaras_pramana ON samskaras(pramana);
                CREATE INDEX IF NOT EXISTS idx_samskaras_confidence ON samskaras(confidence);
                CREATE INDEX IF NOT EXISTS idx_samskaras_created_at ON samskaras(created_at);
                CREATE INDEX IF NOT EXISTS idx_vasanas_domain ON vasanas(domain);
                CREATE INDEX IF NOT EXISTS idx_retrievals_samskara ON retrievals(samskara_id);
                CREATE INDEX IF NOT EXISTS idx_retrievals_time ON retrievals(retrieved_at);
            """)

            # Store schema version
            conn.execute(
                "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
                ("schema_version", str(self.SCHEMA_VERSION)),
            )

    # -------------------------------------------------------------------
    # Core operations
    # -------------------------------------------------------------------

    @staticmethod
    def _generate_id(content: str, timestamp: float) -> str:
        """Deterministic ID from content + time."""
        raw = f"{content}:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def _extract_domain(content: str) -> str:
        """
        Heuristic domain extraction from content text.

        Looks for common domain signals in the content. Falls back to 'general'.
        """
        content_lower = content.lower()
        domain_signals: Dict[str, List[str]] = {
            "programming":    ["code", "function", "variable", "api", "debug", "syntax", "compile", "runtime"],
            "communication":  ["tone", "formal", "casual", "response", "user prefer", "style", "polite"],
            "reasoning":      ["logic", "inference", "proof", "fallacy", "argument", "syllogism", "deduc"],
            "data":           ["database", "query", "schema", "table", "sql", "data model", "index"],
            "philosophy":     ["darshana", "vedanta", "nyaya", "samkhya", "yoga", "mimamsa", "vaisheshika"],
            "mathematics":    ["equation", "theorem", "proof", "calculate", "algebra", "geometry"],
            "science":        ["experiment", "hypothesis", "theory", "observation", "empirical"],
            "creativity":     ["creative", "write", "story", "poem", "design", "art", "metaphor"],
            "system":         ["architecture", "pipeline", "layer", "module", "component", "infrastructure"],
            "user_preference": ["prefer", "like", "dislike", "want", "style", "format"],
        }

        best_domain = "general"
        best_score = 0
        for domain, signals in domain_signals.items():
            score = sum(1 for s in signals if s in content_lower)
            if score > best_score:
                best_score = score
                best_domain = domain
        return best_domain

    def store(
        self,
        content: str,
        pramana: str = "shabda",
        source: str = "training",
        keywords: Optional[List[str]] = None,
        confidence: float = 0.8,
        darshana_context: str = "general",
        domain: Optional[str] = None,
    ) -> SamskaraRecord:
        """
        Store a new memory impression (samskara).

        Args:
            content: The memory content — what was learned/observed.
            pramana: How this was learned (pratyaksha/anumana/upamana/shabda).
            source: Where it came from (user_interaction/tool_output/inference/training/correction).
            keywords: List of retrieval keywords. Auto-extracted if None.
            confidence: Initial confidence (0.0-1.0). Default 0.8.
            darshana_context: Which darshana engine was active.
            domain: Topic domain. Auto-detected if None.

        Returns:
            The created SamskaraRecord.
        """
        now = time.time()
        sid = self._generate_id(content, now)

        # Validate pramana
        try:
            pramana_enum = PramanaType(pramana)
        except ValueError:
            pramana_enum = PramanaType.SHABDA

        # Validate source
        try:
            source_enum = SourceType(source)
        except ValueError:
            source_enum = SourceType.TRAINING

        # Auto-extract keywords if not provided
        if keywords is None:
            keywords = self._extract_keywords(content)

        # Auto-detect domain if not provided
        if domain is None:
            domain = self._extract_domain(content)

        confidence = max(0.0, min(1.0, confidence))

        with self._connection() as conn:
            conn.execute(
                """INSERT INTO samskaras
                   (id, content, keywords, pramana, source, confidence,
                    created_at, last_accessed, access_count, darshana_context, domain)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sid,
                    content,
                    json.dumps(keywords),
                    pramana_enum.value,
                    source_enum.value,
                    confidence,
                    now,
                    now,
                    0,
                    darshana_context,
                    domain,
                ),
            )

        return SamskaraRecord(
            id=sid,
            content=content,
            keywords=keywords,
            pramana=pramana_enum,
            source=source_enum,
            confidence=confidence,
            created_at=now,
            last_accessed=now,
            access_count=0,
            darshana_context=darshana_context,
            domain=domain,
        )

    def recall(self, query: str, limit: int = 5) -> List[SamskaraRecord]:
        """
        Recall memories relevant to a query.

        Ranking formula: keyword_match * recency_score * confidence * log(access_count + 1)

        Each recalled memory is strengthened (spaced repetition effect).

        Args:
            query: The retrieval query.
            limit: Maximum number of results.

        Returns:
            List of SamskaraRecords, most relevant first.
        """
        query_words = set(self._tokenize(query))
        if not query_words:
            return []

        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM samskaras WHERE confidence > 0.01").fetchall()

        scored: List[Tuple[float, SamskaraRecord]] = []
        now = time.time()

        for row in rows:
            record = self._row_to_record(row)
            kw_set = set(w.lower() for w in record.keywords)
            content_words = set(self._tokenize(record.content))
            all_words = kw_set | content_words

            # Keyword match score
            if not all_words:
                continue
            overlap = query_words & all_words
            keyword_score = len(overlap) / max(len(query_words), 1)

            if keyword_score == 0:
                continue

            # Recency score (exponential decay, half-life 14 days)
            days_since_access = (now - record.last_accessed) / 86400.0
            recency = math.exp(-0.693 * days_since_access / 14.0)

            # Access frequency boost (logarithmic)
            freq_boost = math.log(record.access_count + 2)  # +2 so new items get > 0

            # Combined score
            score = keyword_score * recency * record.confidence * freq_boost

            scored.append((score, record))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [rec for _, rec in scored[:limit]]

        # Strengthen recalled memories and log retrievals
        self._log_retrievals(query, results, scored[:limit])
        for rec in results:
            self.strengthen(rec.id)

        return results

    def strengthen(self, samskara_id: str, boost: float = 0.02) -> None:
        """
        Strengthen a memory through recall (spaced repetition).

        Each access increases confidence slightly and updates last_accessed.
        Confidence is capped at 1.0.
        """
        now = time.time()
        with self._connection() as conn:
            conn.execute(
                """UPDATE samskaras
                   SET confidence = MIN(1.0, confidence + ?),
                       last_accessed = ?,
                       access_count = access_count + 1
                   WHERE id = ?""",
                (boost, now, samskara_id),
            )

    def decay(self, half_life_days: float = 30.0) -> int:
        """
        Apply confidence decay to all memories.

        Confidence decays exponentially based on time since last access.
        Different pramana types decay at different rates:
        - pratyaksha: slowest (direct experience persists)
        - shabda: fastest (hearsay fades quickly)

        Args:
            half_life_days: Base half-life in days. Actual half-life is
                           adjusted by pramana type.

        Returns:
            Number of memories affected.
        """
        now = time.time()
        affected = 0

        with self._connection() as conn:
            rows = conn.execute("SELECT id, pramana, confidence, last_accessed FROM samskaras").fetchall()

            for row in rows:
                pramana = PramanaType(row["pramana"])
                days_since = (now - row["last_accessed"]) / 86400.0

                # Adjust half-life by pramana type
                effective_half_life = half_life_days / pramana.decay_multiplier

                # Exponential decay: C(t) = C0 * 2^(-t/half_life)
                decay_factor = math.pow(2, -days_since / effective_half_life)
                new_confidence = row["confidence"] * decay_factor

                if abs(new_confidence - row["confidence"]) > 0.001:
                    conn.execute(
                        "UPDATE samskaras SET confidence = ? WHERE id = ?",
                        (new_confidence, row["id"]),
                    )
                    affected += 1

        return affected

    def get_samskara(self, samskara_id: str) -> Optional[SamskaraRecord]:
        """Retrieve a specific samskara by ID."""
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM samskaras WHERE id = ?", (samskara_id,)).fetchone()
        return self._row_to_record(row) if row else None

    def all_samskaras(self, domain: Optional[str] = None, pramana: Optional[str] = None) -> List[SamskaraRecord]:
        """Retrieve all samskaras, optionally filtered."""
        clauses: List[str] = []
        params: List[Any] = []

        if domain is not None:
            clauses.append("domain = ?")
            params.append(domain)
        if pramana is not None:
            clauses.append("pramana = ?")
            params.append(pramana)

        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        with self._connection() as conn:
            rows = conn.execute(f"SELECT * FROM samskaras{where} ORDER BY created_at DESC", params).fetchall()
        return [self._row_to_record(r) for r in rows]

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Extract meaningful words from text."""
        # Remove punctuation, split, lowercase, filter short/stop words
        words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        stop_words = {
            "the", "and", "for", "are", "but", "not", "you", "all",
            "can", "has", "her", "was", "one", "our", "out", "this",
            "that", "with", "have", "from", "they", "been", "said",
            "each", "which", "their", "will", "other", "about", "many",
            "then", "them", "these", "some", "would", "make", "like",
            "into", "could", "time", "very", "when", "what", "your",
            "how", "its", "than", "now", "way",
        }
        return [w for w in words if w not in stop_words]

    @staticmethod
    def _extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from content using frequency and position."""
        words = re.findall(r'[a-zA-Z]{3,}', content.lower())
        stop_words = {
            "the", "and", "for", "are", "but", "not", "you", "all",
            "can", "has", "her", "was", "one", "our", "out", "this",
            "that", "with", "have", "from", "they", "been", "said",
            "each", "which", "their", "will", "other", "about", "many",
            "then", "them", "these", "some", "would", "make", "like",
            "into", "could", "time", "very", "when", "what", "your",
            "how", "its", "than", "now", "way",
        }
        filtered = [w for w in words if w not in stop_words]

        # Score by frequency + position bonus (earlier words score higher)
        scores: Dict[str, float] = {}
        for i, w in enumerate(filtered):
            position_bonus = 1.0 / (1.0 + i * 0.1)
            scores[w] = scores.get(w, 0) + 1.0 + position_bonus

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in ranked[:max_keywords]]

    def _row_to_record(self, row: sqlite3.Row) -> SamskaraRecord:
        """Convert a database row to a SamskaraRecord."""
        return SamskaraRecord(
            id=row["id"],
            content=row["content"],
            keywords=json.loads(row["keywords"]),
            pramana=PramanaType(row["pramana"]),
            source=SourceType(row["source"]),
            confidence=row["confidence"],
            created_at=row["created_at"],
            last_accessed=row["last_accessed"],
            access_count=row["access_count"],
            darshana_context=row["darshana_context"],
            domain=row["domain"],
        )

    def _log_retrievals(
        self,
        query: str,
        records: List[SamskaraRecord],
        scored: List[Tuple[float, SamskaraRecord]],
    ) -> None:
        """Log retrieval events for analytics."""
        now = time.time()
        with self._connection() as conn:
            for score, record in scored:
                conn.execute(
                    "INSERT INTO retrievals (query, samskara_id, relevance_score, retrieved_at) VALUES (?, ?, ?, ?)",
                    (query, record.id, score, now),
                )


# ---------------------------------------------------------------------------
# VasanaEngine — accumulated tendencies
# ---------------------------------------------------------------------------

class VasanaEngine:
    """
    Manages vasanas (accumulated tendencies) derived from samskaras.

    Vasanas are like weights in a neural network — they represent the
    system's accumulated biases and preferences in different domains.
    Unlike samskaras (individual memories), vasanas are aggregate patterns.

    The engine automatically aggregates samskaras by domain and computes
    tendency strength. It also provides bias detection and the critical
    jnana_agni (fire of knowledge) method for burning outdated tendencies.
    """

    def __init__(self, store: SmritiStore) -> None:
        self.store = store

    def update_vasanas(self) -> int:
        """
        Recompute all vasanas from current samskaras.

        Groups samskaras by domain, extracts common themes, and computes
        strength based on samskara count and confidence.

        Returns:
            Number of vasanas updated.
        """
        with self.store._connection() as conn:
            # Get all domains
            domains = conn.execute(
                "SELECT DISTINCT domain FROM samskaras WHERE confidence > 0.05"
            ).fetchall()

            count = 0
            for domain_row in domains:
                domain = domain_row["domain"]
                samskaras = conn.execute(
                    "SELECT * FROM samskaras WHERE domain = ? AND confidence > 0.05 ORDER BY confidence DESC",
                    (domain,),
                ).fetchall()

                if not samskaras:
                    continue

                # Compute aggregate tendency
                total_confidence = sum(s["confidence"] for s in samskaras)
                avg_confidence = total_confidence / len(samskaras)

                # Strength is a function of count and average confidence
                # More samskaras + higher confidence = stronger vasana
                strength = min(1.0, avg_confidence * math.log(len(samskaras) + 1) / math.log(10))

                # Extract common keywords across samskaras in this domain
                all_keywords: Dict[str, int] = {}
                for s in samskaras:
                    for kw in json.loads(s["keywords"]):
                        all_keywords[kw] = all_keywords.get(kw, 0) + 1

                top_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
                keyword_list = [kw for kw, _ in top_keywords]

                # Build tendency description from most common content patterns
                tendency = self._summarize_tendency(domain, samskaras)

                vid = hashlib.sha256(f"vasana:{domain}".encode()).hexdigest()[:16]
                now = time.time()

                conn.execute(
                    """INSERT OR REPLACE INTO vasanas
                       (id, domain, tendency, strength, samskara_count, last_updated, keywords)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (vid, domain, tendency, strength, len(samskaras), now, json.dumps(keyword_list)),
                )
                count += 1

        return count

    def get_tendency(self, domain: str) -> Optional[VasanaRecord]:
        """
        Get the accumulated tendency for a domain.

        Args:
            domain: The domain to query.

        Returns:
            VasanaRecord if the domain has accumulated tendencies, else None.
        """
        with self.store._connection() as conn:
            row = conn.execute("SELECT * FROM vasanas WHERE domain = ?", (domain,)).fetchone()

        if row is None:
            return None

        return VasanaRecord(
            id=row["id"],
            domain=row["domain"],
            tendency=row["tendency"],
            strength=row["strength"],
            samskara_count=row["samskara_count"],
            last_updated=row["last_updated"],
            keywords=json.loads(row["keywords"]),
        )

    def all_vasanas(self) -> List[VasanaRecord]:
        """Get all vasanas, sorted by strength descending."""
        with self.store._connection() as conn:
            rows = conn.execute("SELECT * FROM vasanas ORDER BY strength DESC").fetchall()
        return [
            VasanaRecord(
                id=r["id"], domain=r["domain"], tendency=r["tendency"],
                strength=r["strength"], samskara_count=r["samskara_count"],
                last_updated=r["last_updated"], keywords=json.loads(r["keywords"]),
            )
            for r in rows
        ]

    def detect_bias(self, query: str, response: str) -> List[Dict[str, Any]]:
        """
        Check if vasanas (accumulated tendencies) may be distorting a response.

        Compares the response against known vasanas to identify potential biases.
        This is NOT censorship — it is epistemic transparency. The system should
        know when its past experiences are coloring its present judgment.

        Args:
            query: The original query.
            response: The generated response to check.

        Returns:
            List of bias warnings, each with domain, tendency, strength, and explanation.
        """
        warnings: List[Dict[str, Any]] = []
        query_words = set(SmritiStore._tokenize(query))
        response_words = set(SmritiStore._tokenize(response))

        with self.store._connection() as conn:
            vasanas = conn.execute("SELECT * FROM vasanas WHERE strength > 0.3").fetchall()

        for v in vasanas:
            v_keywords = set(json.loads(v["keywords"]))

            # Check if this vasana's domain is relevant to the query
            query_overlap = query_words & v_keywords
            response_overlap = response_words & v_keywords

            if len(query_overlap) >= 1 or len(response_overlap) >= 2:
                # This vasana's domain is active — flag potential bias
                warnings.append({
                    "domain": v["domain"],
                    "tendency": v["tendency"],
                    "strength": v["strength"],
                    "overlapping_keywords": list((query_overlap | response_overlap) & v_keywords),
                    "warning": (
                        f"Vasana detected in domain '{v['domain']}' "
                        f"(strength {v['strength']:.2f}): {v['tendency']}. "
                        f"This accumulated tendency may be influencing the response."
                    ),
                })

        return warnings

    def jnana_agni(
        self,
        domain: Optional[str] = None,
        before_date: Optional[float] = None,
        min_strength: float = 0.0,
    ) -> int:
        """
        The fire of knowledge burns outdated vasanas.

        BG 4.37: jñānāgniḥ sarva-karmāṇi bhasmasāt kurute
        "The fire of knowledge reduces all karma to ashes."

        This clears vasanas that are outdated, weak, or domain-specific.
        Unlike forgetting samskaras (which removes data), burning vasanas
        removes BIASES — it frees the system from accumulated prejudice.

        Args:
            domain: If specified, only burn vasanas in this domain.
            before_date: If specified, only burn vasanas last updated before this timestamp.
            min_strength: Only burn vasanas weaker than this threshold (default: burn all matching).

        Returns:
            Number of vasanas burned.
        """
        clauses: List[str] = []
        params: List[Any] = []

        if domain is not None:
            clauses.append("domain = ?")
            params.append(domain)
        if before_date is not None:
            clauses.append("last_updated < ?")
            params.append(before_date)
        if min_strength > 0:
            clauses.append("strength < ?")
            params.append(min_strength)

        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        with self.store._connection() as conn:
            cursor = conn.execute(f"DELETE FROM vasanas{where}", params)
            return cursor.rowcount

    @staticmethod
    def _summarize_tendency(domain: str, samskaras: List[sqlite3.Row]) -> str:
        """Build a human-readable tendency summary from samskaras."""
        if not samskaras:
            return f"No clear tendency in {domain}"

        # Take the most confident samskaras as representative
        top = samskaras[:min(3, len(samskaras))]
        snippets = []
        for s in top:
            content = s["content"]
            # Truncate long content
            if len(content) > 80:
                content = content[:77] + "..."
            snippets.append(content)

        return f"Based on {len(samskaras)} memories: {'; '.join(snippets)}"


# ---------------------------------------------------------------------------
# RetrievalEngine — intelligent memory retrieval
# ---------------------------------------------------------------------------

class RetrievalEngine:
    """
    Retrieves relevant memories and formats them for LLM consumption.

    This is the smṛ (remembering) in smriti — the active process of
    recognizing which past experiences are relevant to the present moment.
    """

    def __init__(self, store: SmritiStore) -> None:
        self.store = store

    def relevant_memories(self, query: str, limit: int = 10) -> List[Tuple[float, SamskaraRecord]]:
        """
        Find samskaras relevant to a query, with relevance scores.

        Ranking: keyword_match * recency_score * confidence * access_frequency

        Args:
            query: The retrieval query.
            limit: Maximum number of results.

        Returns:
            List of (score, SamskaraRecord) tuples, highest score first.
        """
        query_words = set(SmritiStore._tokenize(query))
        if not query_words:
            return []

        with self.store._connection() as conn:
            rows = conn.execute("SELECT * FROM samskaras WHERE confidence > 0.01").fetchall()

        scored: List[Tuple[float, SamskaraRecord]] = []
        now = time.time()

        for row in rows:
            record = self.store._row_to_record(row)
            kw_set = set(w.lower() for w in record.keywords)
            content_words = set(SmritiStore._tokenize(record.content))
            all_words = kw_set | content_words

            if not all_words:
                continue

            overlap = query_words & all_words
            keyword_score = len(overlap) / max(len(query_words), 1)

            if keyword_score == 0:
                continue

            # Recency
            days_since = (now - record.last_accessed) / 86400.0
            recency = math.exp(-0.693 * days_since / 14.0)

            # Access frequency (logarithmic)
            freq = math.log(record.access_count + 2)

            score = keyword_score * recency * record.confidence * freq
            scored.append((score, record))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:limit]

    def context_window(self, query: str, max_tokens: int = 2000) -> str:
        """
        Build a context window of relevant memories for an LLM call.

        Formats memories as structured context that can be prepended to
        a prompt. Estimates token count as ~4 chars per token.

        Args:
            query: The query to find context for.
            max_tokens: Maximum approximate token count for the context.

        Returns:
            Formatted string of relevant memories.
        """
        memories = self.relevant_memories(query, limit=20)
        if not memories:
            return "# Smriti Context\nNo relevant memories found.\n"

        lines: List[str] = ["# Smriti Context (Relevant Memories)", ""]
        char_budget = max_tokens * 4  # rough chars-per-token estimate
        chars_used = len(lines[0]) + len(lines[1])

        for i, (score, record) in enumerate(memories, 1):
            entry_lines = [
                f"## Memory {i} (relevance: {score:.3f})",
                f"- **Content**: {record.content}",
                f"- **Pramana**: {record.pramana.value} | **Confidence**: {record.confidence:.2f}",
                f"- **Source**: {record.source.value} | **Domain**: {record.domain}",
                f"- **Age**: {record.age_days:.1f} days | **Accesses**: {record.access_count}",
                "",
            ]
            entry_text = "\n".join(entry_lines)
            entry_chars = len(entry_text)

            if chars_used + entry_chars > char_budget:
                lines.append(f"... ({len(memories) - i + 1} more memories omitted for token budget)")
                break

            lines.extend(entry_lines)
            chars_used += entry_chars

        return "\n".join(lines)

    def forget(self, older_than_days: float = 365, min_confidence: float = 0.1) -> int:
        """
        Prune very old, low-confidence memories.

        This is not jnana_agni (which burns biases). This is natural
        forgetting — the system lets go of faint, ancient impressions
        that no longer serve it.

        Args:
            older_than_days: Only forget memories older than this.
            min_confidence: Only forget memories with confidence below this.

        Returns:
            Number of memories forgotten.
        """
        cutoff = time.time() - (older_than_days * 86400.0)

        with self.store._connection() as conn:
            # First delete retrieval logs for these samskaras
            conn.execute(
                """DELETE FROM retrievals WHERE samskara_id IN (
                       SELECT id FROM samskaras
                       WHERE created_at < ? AND confidence < ?
                   )""",
                (cutoff, min_confidence),
            )

            cursor = conn.execute(
                "DELETE FROM samskaras WHERE created_at < ? AND confidence < ?",
                (cutoff, min_confidence),
            )
            return cursor.rowcount


# ---------------------------------------------------------------------------
# SmritiReport — analytics and introspection
# ---------------------------------------------------------------------------

class SmritiReport:
    """
    Analytics and introspection over the memory system.

    Provides stats, domain analysis, and gap detection — the system's
    ability to know what it DOESN'T know.
    """

    def __init__(self, store: SmritiStore) -> None:
        self.store = store

    def stats(self) -> Dict[str, Any]:
        """
        Comprehensive statistics about the memory system.

        Returns:
            Dict with total memories, breakdowns by pramana/source/domain,
            average confidence, and age information.
        """
        with self.store._connection() as conn:
            total = conn.execute("SELECT COUNT(*) as n FROM samskaras").fetchone()["n"]

            if total == 0:
                return {
                    "total_memories": 0,
                    "by_pramana": {},
                    "by_source": {},
                    "by_domain": {},
                    "avg_confidence": 0.0,
                    "oldest": None,
                    "newest": None,
                    "total_vasanas": 0,
                    "total_retrievals": 0,
                }

            # By pramana
            by_pramana = {}
            for row in conn.execute("SELECT pramana, COUNT(*) as n FROM samskaras GROUP BY pramana"):
                by_pramana[row["pramana"]] = row["n"]

            # By source
            by_source = {}
            for row in conn.execute("SELECT source, COUNT(*) as n FROM samskaras GROUP BY source"):
                by_source[row["source"]] = row["n"]

            # By domain
            by_domain = {}
            for row in conn.execute("SELECT domain, COUNT(*) as n FROM samskaras GROUP BY domain"):
                by_domain[row["domain"]] = row["n"]

            # Averages and extremes
            agg = conn.execute(
                """SELECT AVG(confidence) as avg_conf,
                          MIN(created_at) as oldest,
                          MAX(created_at) as newest
                   FROM samskaras"""
            ).fetchone()

            # Vasana count
            vasana_count = conn.execute("SELECT COUNT(*) as n FROM vasanas").fetchone()["n"]

            # Retrieval count
            retrieval_count = conn.execute("SELECT COUNT(*) as n FROM retrievals").fetchone()["n"]

        return {
            "total_memories": total,
            "by_pramana": by_pramana,
            "by_source": by_source,
            "by_domain": by_domain,
            "avg_confidence": round(agg["avg_conf"], 4),
            "oldest_timestamp": agg["oldest"],
            "newest_timestamp": agg["newest"],
            "oldest_age_days": round((time.time() - agg["oldest"]) / 86400.0, 1) if agg["oldest"] else None,
            "newest_age_days": round((time.time() - agg["newest"]) / 86400.0, 1) if agg["newest"] else None,
            "total_vasanas": vasana_count,
            "total_retrievals": retrieval_count,
        }

    def domains(self) -> List[Dict[str, Any]]:
        """
        What topics does the system have memory about?

        Returns:
            List of domain dicts with count, average confidence, and pramana breakdown.
        """
        with self.store._connection() as conn:
            rows = conn.execute(
                """SELECT domain,
                          COUNT(*) as count,
                          AVG(confidence) as avg_conf,
                          SUM(access_count) as total_accesses
                   FROM samskaras
                   GROUP BY domain
                   ORDER BY count DESC"""
            ).fetchall()

        result = []
        for row in rows:
            result.append({
                "domain": row["domain"],
                "memory_count": row["count"],
                "avg_confidence": round(row["avg_conf"], 4),
                "total_accesses": row["total_accesses"],
            })
        return result

    def gaps(self, query: str) -> Dict[str, Any]:
        """
        What does the system NOT know about this query?

        Analyzes the query against existing knowledge to identify gaps.
        This is the Nidra (absence) detector applied to memory.

        Args:
            query: The query to analyze for knowledge gaps.

        Returns:
            Dict with coverage assessment, matched/unmatched terms,
            and confidence levels.
        """
        query_words = set(SmritiStore._tokenize(query))
        if not query_words:
            return {
                "query": query,
                "coverage": 0.0,
                "matched_terms": [],
                "unmatched_terms": [],
                "relevant_domains": [],
                "assessment": "Query could not be analyzed.",
            }

        # Collect all keywords from memory
        with self.store._connection() as conn:
            rows = conn.execute("SELECT keywords, domain, confidence FROM samskaras WHERE confidence > 0.05").fetchall()

        all_memory_words: Dict[str, float] = {}  # word -> max confidence
        domain_words: Dict[str, set] = {}

        for row in rows:
            kws = json.loads(row["keywords"])
            domain = row["domain"]
            conf = row["confidence"]

            if domain not in domain_words:
                domain_words[domain] = set()

            for kw in kws:
                kw_lower = kw.lower()
                all_memory_words[kw_lower] = max(all_memory_words.get(kw_lower, 0), conf)
                domain_words[domain].add(kw_lower)

        # Find matches and gaps
        matched = []
        unmatched = []
        for word in query_words:
            if word in all_memory_words:
                matched.append({"term": word, "max_confidence": all_memory_words[word]})
            else:
                unmatched.append(word)

        coverage = len(matched) / len(query_words) if query_words else 0.0

        # Find which domains are relevant
        relevant_domains = []
        for domain, words in domain_words.items():
            overlap = query_words & words
            if overlap:
                relevant_domains.append({
                    "domain": domain,
                    "matching_terms": list(overlap),
                    "coverage": len(overlap) / len(query_words),
                })
        relevant_domains.sort(key=lambda x: x["coverage"], reverse=True)

        # Assessment
        if coverage >= 0.8:
            assessment = "Strong coverage — the system has substantial memory about this topic."
        elif coverage >= 0.5:
            assessment = "Partial coverage — some relevant memory exists, but there are significant gaps."
        elif coverage >= 0.2:
            assessment = "Weak coverage — the system has limited memory about this topic."
        else:
            assessment = "Nidra (absence) — the system has very little or no memory about this topic."

        return {
            "query": query,
            "coverage": round(coverage, 4),
            "matched_terms": matched,
            "unmatched_terms": list(unmatched),
            "relevant_domains": relevant_domains,
            "assessment": assessment,
        }


# ---------------------------------------------------------------------------
# Convenience: unified Smriti interface
# ---------------------------------------------------------------------------

class Smriti:
    """
    Unified interface to the entire Smriti memory system.

    Combines SmritiStore, VasanaEngine, RetrievalEngine, and SmritiReport
    into a single object for convenient use.

    Usage::

        memory = Smriti()
        memory.store("Python prefers snake_case", pramana="pratyaksha", source="tool_output")
        results = memory.recall("python naming convention")
        context = memory.context_window("how to name variables in python")
        stats = memory.stats()
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self._store = SmritiStore(db_path)
        self.vasana_engine = VasanaEngine(self._store)
        self.retrieval_engine = RetrievalEngine(self._store)
        self.report = SmritiReport(self._store)

    # -- SmritiStore delegates --

    def store(self, content: str, **kwargs) -> SamskaraRecord:
        """Store a new memory. See SmritiStore.store() for parameters."""
        return self._store.store(content, **kwargs)

    def recall(self, query: str, limit: int = 5) -> List[SamskaraRecord]:
        """Recall relevant memories. See SmritiStore.recall()."""
        return self._store.recall(query, limit=limit)

    def decay(self, half_life_days: float = 30.0) -> int:
        """Apply confidence decay. See SmritiStore.decay()."""
        return self._store.decay(half_life_days)

    def strengthen(self, samskara_id: str, boost: float = 0.02) -> None:
        """Strengthen a memory. See SmritiStore.strengthen()."""
        self._store.strengthen(samskara_id, boost)

    def get_samskara(self, samskara_id: str) -> Optional[SamskaraRecord]:
        """Get a specific samskara. See SmritiStore.get_samskara()."""
        return self._store.get_samskara(samskara_id)

    # -- VasanaEngine delegates --

    def update_vasanas(self) -> int:
        """Recompute vasanas from samskaras."""
        return self.vasana_engine.update_vasanas()

    def get_tendency(self, domain: str) -> Optional[VasanaRecord]:
        """Get accumulated tendency for a domain."""
        return self.vasana_engine.get_tendency(domain)

    def detect_bias(self, query: str, response: str) -> List[Dict[str, Any]]:
        """Check if vasanas are distorting a response."""
        return self.vasana_engine.detect_bias(query, response)

    def jnana_agni(self, domain: Optional[str] = None, before_date: Optional[float] = None) -> int:
        """Burn outdated vasanas."""
        return self.vasana_engine.jnana_agni(domain=domain, before_date=before_date)

    # -- RetrievalEngine delegates --

    def relevant_memories(self, query: str, limit: int = 10) -> List[Tuple[float, SamskaraRecord]]:
        """Find relevant memories with scores."""
        return self.retrieval_engine.relevant_memories(query, limit=limit)

    def context_window(self, query: str, max_tokens: int = 2000) -> str:
        """Build context window for LLM call."""
        return self.retrieval_engine.context_window(query, max_tokens=max_tokens)

    def forget(self, older_than_days: float = 365, min_confidence: float = 0.1) -> int:
        """Prune old low-confidence memories."""
        return self.retrieval_engine.forget(older_than_days, min_confidence)

    # -- SmritiReport delegates --

    def stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return self.report.stats()

    def domains(self) -> List[Dict[str, Any]]:
        """Get domain breakdown."""
        return self.report.domains()

    def gaps(self, query: str) -> Dict[str, Any]:
        """Detect knowledge gaps for a query."""
        return self.report.gaps(query)

    @property
    def db_path(self) -> str:
        return self._store.db_path
