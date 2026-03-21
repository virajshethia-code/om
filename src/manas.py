"""
manas.py — Attention and Context Management for the Darshana Architecture
=========================================================================

    मनस् (Manas) — from root मन् (man, to think)
    The "inner sense organ" that coordinates all other senses.

In Samkhya philosophy, Manas sits between Ahamkara (the self-model) and the
Jnanendriyas (sense organs). It is the ROUTER and MANAGER of attention — the
faculty that decides what gets processed, what gets held, and what gets released.

The problem this solves: LLMs have fixed context windows. As conversations grow,
important context gets pushed out. There is no intelligent management of what
stays and what goes. The model has no concept of "relevance" or "importance" —
everything in the window is treated equally, and when you hit the limit, the
oldest content is blindly truncated.

Manas implements attention as architecture:

    ContextItem     — a piece of information with relevance, importance, and source
    Manas           — the attention manager that assembles optimal context
    DhyanaPipeline  — deep focus mode for single-topic maximum-depth analysis
    ConversationTracker — conversation compaction with summarization

The three attention modes map directly to Yoga's progressive stages:

    Pratyahara (withdrawal)    — broad, gather everything possibly relevant
    Dharana (concentration)    — focused, only highly relevant items
    Dhyana (meditation)        — deep, one topic only, maximum depth

This is the piece that makes the whole architecture work in practice.
Context management IS intelligence.

Architecture reference: THESIS.md, Manas (Attention Router) under Ahamkara Layer.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AttentionMode(Enum):
    """
    The three modes of attention, mapped from Yoga's progressive stages.

    Pratyahara: sense withdrawal — gather broadly, low threshold.
    Dharana:    concentration   — focus on relevant items, moderate threshold.
    Dhyana:     meditation      — single topic, high threshold, maximum depth.
    """
    PRATYAHARA = "pratyahara"
    DHARANA    = "dharana"
    DHYANA     = "dhyana"


class ContextSource(Enum):
    """Where a context item originated."""
    SYSTEM      = "system"       # system instructions, architecture rules
    USER        = "user"         # direct user input
    MEMORY      = "memory"       # retrieved from SmritiStore / long-term memory
    PERCEPTION  = "perception"   # tool output, API responses, observations
    INFERENCE   = "inference"    # derived by reasoning engines
    CONVERSATION = "conversation"  # prior conversation turns


# Relevance threshold per mode — the minimum combined score for inclusion
MODE_THRESHOLDS: Dict[AttentionMode, float] = {
    AttentionMode.PRATYAHARA: 0.10,   # broad — include almost everything
    AttentionMode.DHARANA:    0.35,   # focused — only clearly relevant
    AttentionMode.DHYANA:     0.60,   # deep — only the most relevant
}

# Section headers for assembled context output
SOURCE_SECTION_HEADERS: Dict[ContextSource, str] = {
    ContextSource.SYSTEM:       "[SYSTEM]",
    ContextSource.USER:         "[USER]",
    ContextSource.MEMORY:       "[MEMORY]",
    ContextSource.PERCEPTION:   "[PERCEPTION]",
    ContextSource.INFERENCE:    "[INFERENCE]",
    ContextSource.CONVERSATION: "[CONVERSATION]",
}


# ---------------------------------------------------------------------------
# ContextItem — a single piece of information in the attention window
# ---------------------------------------------------------------------------

@dataclass
class ContextItem:
    """
    A discrete piece of information managed by Manas.

    Each item carries metadata that determines whether it stays in the
    attention window or gets evicted when space is needed:

        content:          the text itself
        source:           where it came from (user, memory, perception, etc.)
        relevance_score:  0-1, how relevant to the CURRENT query
        importance_score: 0-1, how important overall (system instructions = high)
        added_at:         epoch timestamp when added
        token_estimate:   rough token count (len / 4)
        pinned:           if True, NEVER evicted (system instructions, user rules)
        topic:            optional topic tag for Dhyana filtering
        query_age:        how many queries ago this was last relevant
    """
    content: str
    source: ContextSource
    relevance_score: float = 0.5
    importance_score: float = 0.5
    added_at: float = field(default_factory=time.time)
    token_estimate: int = 0
    pinned: bool = False
    topic: str = ""
    query_age: int = 0
    _evicted: bool = field(default=False, repr=False)

    def __post_init__(self):
        if self.token_estimate == 0:
            self.token_estimate = max(1, len(self.content) // 4)

    @property
    def combined_score(self) -> float:
        """
        The composite score used for eviction and ordering.

        relevance × importance, with a recency bonus that decays
        as the item ages (measured in queries, not wall-clock time).
        """
        recency_bonus = 1.0 / (1.0 + 0.15 * self.query_age)
        return self.relevance_score * self.importance_score * recency_bonus

    @property
    def age_seconds(self) -> float:
        return time.time() - self.added_at

    def to_dict(self) -> dict:
        return {
            "content_preview": self.content[:80] + ("..." if len(self.content) > 80 else ""),
            "source": self.source.value,
            "relevance": round(self.relevance_score, 3),
            "importance": round(self.importance_score, 3),
            "combined": round(self.combined_score, 3),
            "tokens": self.token_estimate,
            "pinned": self.pinned,
            "topic": self.topic,
            "query_age": self.query_age,
        }


# ---------------------------------------------------------------------------
# Manas — the attention manager
# ---------------------------------------------------------------------------

class Manas:
    """
    The attention and context management engine.

    Manas decides what information is present in the LLM's context window
    at any given moment. It manages a pool of ContextItems, scores them
    for relevance against the current query, evicts low-value items when
    the token budget is exceeded, and assembles the final context string
    in an ordered, sectioned format.

    Usage::

        manas = Manas(max_tokens=100000)

        # Add system instructions (pinned — never evicted)
        manas.add("You are a Darshana reasoning engine.", source="system", pinned=True)

        # Add conversation and memory items
        manas.add("User asked about Rust rewrite.", source="conversation")
        manas.add("Previous analysis: latency is the bottleneck.", source="memory")

        # Assemble context for a new query
        context = manas.assemble("Should we use async Rust or Go?", mode="dharana")

    Args:
        max_tokens: The total token budget for the context window.
    """

    def __init__(self, max_tokens: int = 100_000) -> None:
        self.max_tokens = max_tokens
        self._items: List[ContextItem] = []
        self._evicted: List[ContextItem] = []
        self._query_count: int = 0

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def add(
        self,
        content: str,
        source: str = "user",
        importance: float = 0.5,
        pinned: bool = False,
        topic: str = "",
        relevance: float = 0.5,
    ) -> ContextItem:
        """
        Add a new item to the attention window.

        If the source is "system", importance defaults to 1.0 and pinned
        defaults to True (unless explicitly overridden).

        Args:
            content: The text to add.
            source: One of: system, user, memory, perception, inference, conversation.
            importance: 0-1, how important this item is overall.
            pinned: If True, this item is never evicted.
            topic: Optional topic tag for Dhyana mode filtering.
            relevance: Initial relevance score (will be re-scored on assemble).

        Returns:
            The created ContextItem.
        """
        ctx_source = ContextSource(source) if isinstance(source, str) else source

        # System items are high-importance and pinned by default
        if ctx_source == ContextSource.SYSTEM:
            if importance == 0.5:  # default wasn't overridden
                importance = 1.0
            pinned = True

        item = ContextItem(
            content=content,
            source=ctx_source,
            relevance_score=relevance,
            importance_score=importance,
            pinned=pinned,
            topic=topic,
        )

        self._items.append(item)

        # Auto-evict if over budget
        if self.current_tokens() > self.max_tokens:
            self.evict()

        return item

    def current_tokens(self) -> int:
        """Total estimated tokens across all items in the window."""
        return sum(item.token_estimate for item in self._items)

    def evict(self) -> List[ContextItem]:
        """
        Remove lowest-value items until within token budget.

        Eviction order: lowest combined_score first.
        Pinned items are NEVER evicted — if the pinned items alone exceed
        the budget, we log a warning but do not remove them.

        Returns:
            List of items that were evicted.
        """
        newly_evicted: List[ContextItem] = []

        while self.current_tokens() > self.max_tokens:
            # Find the lowest-scoring unpinned item
            unpinned = [i for i in self._items if not i.pinned]
            if not unpinned:
                # Only pinned items remain — cannot evict further
                break

            victim = min(unpinned, key=lambda i: i.combined_score)
            victim._evicted = True
            self._items.remove(victim)
            self._evicted.append(victim)
            newly_evicted.append(victim)

        return newly_evicted

    # ------------------------------------------------------------------
    # Relevance scoring
    # ------------------------------------------------------------------

    def score_relevance(self, item: ContextItem, query: str) -> float:
        """
        Score how relevant an item is to the current query.

        Uses keyword overlap (Jaccard-like) plus a recency bonus.
        This is intentionally simple — no embeddings, no external models.
        The philosophy: good-enough relevance scoring with zero dependencies
        beats perfect scoring that requires a vector database.

        Args:
            item: The context item to score.
            query: The current user query.

        Returns:
            A relevance score between 0.0 and 1.0.
        """
        query_terms = self._extract_terms(query)
        item_terms = self._extract_terms(item.content)

        if not query_terms or not item_terms:
            return 0.1  # minimal baseline — never fully zero

        # Keyword overlap (Jaccard similarity)
        overlap = query_terms & item_terms
        union = query_terms | item_terms
        jaccard = len(overlap) / len(union) if union else 0.0

        # Boost for exact phrase matches (bigrams)
        query_bigrams = self._extract_bigrams(query)
        item_bigrams = self._extract_bigrams(item.content)
        bigram_overlap = query_bigrams & item_bigrams
        bigram_boost = min(0.3, len(bigram_overlap) * 0.1) if bigram_overlap else 0.0

        # Recency bonus: items added recently get a small boost
        recency = 1.0 / (1.0 + 0.1 * item.query_age)
        recency_boost = 0.1 * recency

        # Pinned items get a minimum floor
        pin_floor = 0.3 if item.pinned else 0.0

        score = jaccard + bigram_boost + recency_boost
        score = max(score, pin_floor)
        return min(1.0, score)

    def refresh_scores(self, query: str) -> None:
        """
        Re-score all items in the window for the new query.

        Also increments query_age on every item — items that were
        relevant 5 queries ago but not now will naturally drop.
        """
        self._query_count += 1

        for item in self._items:
            item.query_age += 1
            item.relevance_score = self.score_relevance(item, query)

            # If this item is now relevant, reset its query age
            if item.relevance_score > 0.4:
                item.query_age = 0

    # ------------------------------------------------------------------
    # Context assembly
    # ------------------------------------------------------------------

    def assemble(
        self,
        query: str,
        mode: str = "dharana",
    ) -> str:
        """
        Assemble the optimized context string for an LLM call.

        This is the primary output of Manas — the curated, ordered,
        token-budgeted context that goes into the LLM's window.

        Steps:
        1. Refresh relevance scores for the new query
        2. Filter by attention mode threshold
        3. Evict if over budget
        4. Order: pinned first, then by combined_score descending
        5. Group by source section with headers
        6. Truncate if needed, always preserving pinned items

        Args:
            query: The current user query.
            mode: One of "pratyahara", "dharana", "dhyana".

        Returns:
            The assembled context string with section headers.
        """
        attention_mode = AttentionMode(mode) if isinstance(mode, str) else mode
        threshold = MODE_THRESHOLDS[attention_mode]

        # Step 1: refresh scores
        self.refresh_scores(query)

        # Step 2: filter by threshold (pinned items always pass)
        active_items = [
            item for item in self._items
            if item.pinned or item.combined_score >= threshold
        ]

        # Step 3: evict if total is over budget
        # (The main eviction handles the full pool, but here we also
        #  respect the budget for just the active set.)
        self.evict()

        # Re-filter after eviction
        active_items = [
            item for item in self._items
            if item.pinned or item.combined_score >= threshold
        ]

        # Step 4: sort — pinned first, then by combined score descending
        active_items.sort(key=lambda i: (not i.pinned, -i.combined_score))

        # Step 5: group by source and build sections
        sections: Dict[ContextSource, List[ContextItem]] = {}
        for item in active_items:
            sections.setdefault(item.source, []).append(item)

        # Step 6: assemble the output string
        # Order: SYSTEM first, then other sections by highest item score
        parts: List[str] = []
        token_budget_remaining = self.max_tokens

        # Always include SYSTEM section first
        source_order = [ContextSource.SYSTEM]
        for src in [ContextSource.MEMORY, ContextSource.PERCEPTION,
                     ContextSource.CONVERSATION, ContextSource.USER,
                     ContextSource.INFERENCE]:
            if src in sections:
                source_order.append(src)

        for source in source_order:
            if source not in sections:
                continue

            header = SOURCE_SECTION_HEADERS[source]
            section_items = sections[source]
            section_text = f"\n{header}\n"

            for item in section_items:
                entry = item.content.strip()
                entry_tokens = item.token_estimate

                if entry_tokens <= token_budget_remaining or item.pinned:
                    section_text += f"{entry}\n\n"
                    token_budget_remaining -= entry_tokens

            parts.append(section_text)

        return "\n".join(parts).strip()

    # ------------------------------------------------------------------
    # Attention report
    # ------------------------------------------------------------------

    def report(self) -> Dict[str, Any]:
        """
        Full attention report: what's in context, what was evicted, utilization.

        Returns a dict with:
            active_count:   number of items in the window
            evicted_count:  number of items evicted
            total_tokens:   tokens currently used
            max_tokens:     token budget
            utilization:    percentage of budget used
            pinned_count:   number of pinned (never-evict) items
            items:          list of item summaries (sorted by combined score)
            evicted:        list of evicted item summaries
        """
        total = self.current_tokens()
        utilization = (total / self.max_tokens * 100) if self.max_tokens > 0 else 0

        active_sorted = sorted(self._items, key=lambda i: -i.combined_score)

        return {
            "active_count": len(self._items),
            "evicted_count": len(self._evicted),
            "total_tokens": total,
            "max_tokens": self.max_tokens,
            "utilization_pct": round(utilization, 1),
            "pinned_count": sum(1 for i in self._items if i.pinned),
            "items": [item.to_dict() for item in active_sorted],
            "evicted": [item.to_dict() for item in self._evicted[-10:]],  # last 10
        }

    def what_am_i_missing(self, query: str) -> List[Dict[str, Any]]:
        """
        Find evicted items that might be relevant to the current query.

        This is the Manas equivalent of "tip of the tongue" — things the
        system once knew but no longer has in its attention window.

        Args:
            query: The current query to check relevance against.

        Returns:
            List of evicted items with their would-be relevance scores,
            sorted by relevance descending.
        """
        missing: List[Dict[str, Any]] = []

        for item in self._evicted:
            relevance = self.score_relevance(item, query)
            if relevance > 0.2:
                info = item.to_dict()
                info["would_be_relevance"] = round(relevance, 3)
                missing.append(info)

        missing.sort(key=lambda x: -x["would_be_relevance"])
        return missing

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_terms(text: str) -> set:
        """Extract lowercase word-level terms, filtering stopwords and short words."""
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "to", "of", "in", "for",
            "on", "with", "at", "by", "from", "as", "into", "through", "during",
            "before", "after", "above", "below", "between", "out", "off", "over",
            "under", "again", "further", "then", "once", "here", "there", "when",
            "where", "why", "how", "all", "each", "every", "both", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "because", "but", "and",
            "or", "if", "while", "about", "up", "it", "its", "he", "she", "they",
            "them", "his", "her", "their", "this", "that", "these", "those", "what",
            "which", "who", "whom", "i", "me", "my", "we", "us", "our", "you",
        }
        words = set(re.findall(r'[a-z0-9]+', text.lower()))
        return {w for w in words if len(w) > 2 and w not in stopwords}

    @staticmethod
    def _extract_bigrams(text: str) -> set:
        """Extract consecutive word-pair bigrams for phrase matching."""
        words = re.findall(r'[a-z0-9]+', text.lower())
        return {f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)}


# ---------------------------------------------------------------------------
# DhyanaPipeline — deep focus mode
# ---------------------------------------------------------------------------

class DhyanaPipeline:
    """
    Deep focus mode for single-topic maximum-depth analysis.

    In Yoga, Dhyana is the seventh limb — sustained meditation on a single
    object. The mind holds one thing with such intensity that everything
    else falls away. DhyanaPipeline implements this architecturally.

    Given a single topic, it:
    1. Filters ALL context items for that topic
    2. Pulls additional relevant items from any available memory store
    3. Assembles a maximum-depth context window focused entirely on one subject
    4. Returns the deepest possible context for a darshana engine

    Usage::

        pipeline = DhyanaPipeline(manas)
        deep_context = pipeline.focus("database performance")

    Args:
        manas: The Manas attention manager to use as the base.
        memory_store: Optional external memory store with a search() method.
    """

    def __init__(
        self,
        manas: Manas,
        memory_store: Any = None,
    ) -> None:
        self.manas = manas
        self.memory_store = memory_store

    def focus(
        self,
        topic: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Assemble maximum-depth context on a single topic.

        Steps:
        1. Score all items against the topic
        2. If a memory_store is available, search for additional items
        3. Add retrieved memories to the manas pool
        4. Assemble with dhyana mode (highest threshold)
        5. Return the focused context

        Args:
            topic: The single topic to focus on.
            max_tokens: Optional override for the token budget.

        Returns:
            The deep-focus context string.
        """
        # Pull from memory store if available
        if self.memory_store is not None:
            try:
                # SmritiStore-compatible interface: search(query, top_k)
                memories = self.memory_store.search(topic, top_k=20)
                for mem in memories:
                    # Adapt to different memory store return formats
                    if isinstance(mem, dict):
                        content = mem.get("content", mem.get("text", str(mem)))
                        score = mem.get("score", mem.get("relevance", 0.7))
                    elif isinstance(mem, str):
                        content = mem
                        score = 0.7
                    else:
                        content = str(mem)
                        score = 0.7

                    # Only add if not already in the pool (by content prefix)
                    existing_prefixes = {i.content[:50] for i in self.manas._items}
                    if content[:50] not in existing_prefixes:
                        self.manas.add(
                            content=content,
                            source="memory",
                            importance=0.8,
                            topic=topic,
                            relevance=score,
                        )
            except Exception:
                # Memory store unavailable — proceed with what we have
                pass

        # Tag items whose topic matches
        topic_terms = Manas._extract_terms(topic)
        for item in self.manas._items:
            if item.topic and Manas._extract_terms(item.topic) & topic_terms:
                item.relevance_score = max(item.relevance_score, 0.7)

        # Override budget if requested
        original_max = self.manas.max_tokens
        if max_tokens is not None:
            self.manas.max_tokens = max_tokens

        # Assemble with dhyana mode
        context = self.manas.assemble(topic, mode="dhyana")

        # Restore budget
        self.manas.max_tokens = original_max

        return context

    def report(self, topic: str) -> Dict[str, Any]:
        """
        Report on what depth of information is available for a topic.

        Returns:
            Dict with topic, matching item count, total tokens available,
            and whether a memory store was consulted.
        """
        topic_terms = Manas._extract_terms(topic)
        matching = []
        for item in self.manas._items:
            item_terms = Manas._extract_terms(item.content)
            if item_terms & topic_terms:
                matching.append(item)

        return {
            "topic": topic,
            "matching_items": len(matching),
            "total_tokens": sum(i.token_estimate for i in matching),
            "memory_store_available": self.memory_store is not None,
            "items": [i.to_dict() for i in matching[:10]],
        }


# ---------------------------------------------------------------------------
# ConversationTracker — conversation compaction with summarization
# ---------------------------------------------------------------------------

@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    role: str       # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)
    token_estimate: int = 0
    summarized: bool = False

    def __post_init__(self):
        if self.token_estimate == 0:
            self.token_estimate = max(1, len(self.content) // 4)


class ConversationTracker:
    """
    Tracks conversation history with intelligent compaction.

    As conversations grow, older turns are summarized to save tokens.
    Summaries preserve: key decisions, user preferences, important facts,
    and the flow of reasoning. The raw content is discarded but the
    information density is maintained.

    This is the Smriti (memory) aspect of Manas — remembering what
    matters, letting go of what doesn't.

    Usage::

        tracker = ConversationTracker()
        tracker.add_turn("user", "Should we use Rust or Go?")
        tracker.add_turn("assistant", "Let me analyze both options...")

        # Get conversation for context assembly
        history = tracker.get_history(max_tokens=5000)

    Args:
        max_turns_before_summary: After this many unsummarized turns,
            trigger compaction of the oldest turns.
        summary_group_size: Number of turns to compress into one summary.
    """

    def __init__(
        self,
        max_turns_before_summary: int = 10,
        summary_group_size: int = 4,
    ) -> None:
        self.max_turns_before_summary = max_turns_before_summary
        self.summary_group_size = summary_group_size
        self._turns: List[ConversationTurn] = []
        self._summaries: List[str] = []

    def add_turn(self, role: str, content: str) -> None:
        """
        Add a conversation turn.

        If unsummarized turns exceed the threshold, trigger compaction
        of the oldest group.

        Args:
            role: "user" or "assistant".
            content: The turn content.
        """
        self._turns.append(ConversationTurn(role=role, content=content))

        # Check if compaction is needed
        unsummarized = [t for t in self._turns if not t.summarized]
        if len(unsummarized) > self.max_turns_before_summary:
            self._compact()

    def get_history(self, max_tokens: int = 5000) -> str:
        """
        Get the conversation history, fitting within the token budget.

        Strategy:
        - Include ALL summaries (they're already compact)
        - Include recent unsummarized turns, newest first
        - Truncate from the middle if needed

        Args:
            max_tokens: Maximum tokens for the returned history.

        Returns:
            Formatted conversation history string.
        """
        parts: List[str] = []
        tokens_used = 0

        # First: include summaries (they're cheap)
        if self._summaries:
            summary_header = "[Earlier conversation summary]\n"
            for summary in self._summaries:
                summary_text = f"{summary_header}{summary}\n"
                summary_tokens = len(summary_text) // 4
                if tokens_used + summary_tokens <= max_tokens:
                    parts.append(summary_text)
                    tokens_used += summary_tokens
                summary_header = ""  # only first gets the header

        # Then: include recent unsummarized turns (newest = most relevant)
        unsummarized = [t for t in self._turns if not t.summarized]

        # Add from most recent, but display in chronological order
        turns_to_include: List[ConversationTurn] = []
        for turn in reversed(unsummarized):
            if tokens_used + turn.token_estimate <= max_tokens:
                turns_to_include.append(turn)
                tokens_used += turn.token_estimate
            else:
                break

        turns_to_include.reverse()  # back to chronological order

        if turns_to_include:
            for turn in turns_to_include:
                prefix = "User" if turn.role == "user" else "Assistant"
                parts.append(f"{prefix}: {turn.content}")

        return "\n\n".join(parts)

    @property
    def turn_count(self) -> int:
        """Total number of turns (including summarized)."""
        return len(self._turns)

    @property
    def summary_count(self) -> int:
        """Number of compaction summaries generated."""
        return len(self._summaries)

    def _compact(self) -> None:
        """
        Compress the oldest unsummarized turns into a summary.

        The summary extraction is done heuristically (no LLM call) to
        keep Manas dependency-free. It preserves:
        - Key decisions (words like "decided", "chose", "will", "should")
        - User preferences (words like "prefer", "want", "like", "need")
        - Important facts (sentences with names, numbers, or technical terms)
        - Questions asked (sentences ending with ?)
        """
        unsummarized = [t for t in self._turns if not t.summarized]
        if len(unsummarized) < self.summary_group_size:
            return

        group = unsummarized[:self.summary_group_size]
        summary = self._extract_summary(group)
        self._summaries.append(summary)

        # Mark as summarized
        for turn in group:
            turn.summarized = True

    def _extract_summary(self, turns: List[ConversationTurn]) -> str:
        """
        Extract a summary from a group of turns.

        Heuristic summarization — no LLM required:
        1. Extract sentences with decision/preference/fact markers
        2. Keep questions the user asked
        3. Keep the first and last sentence of each turn as bookends
        4. Compress to roughly 1/4 of original length
        """
        important_patterns = [
            r'\b(decided|chose|choose|will|should|must|agreed|concluded)\b',
            r'\b(prefer|want|need|like|important|critical|key)\b',
            r'\b(because|therefore|however|but|although|instead)\b',
            r'\d+',  # numbers are often important
        ]

        key_sentences: List[str] = []
        topics_seen: set = set()

        for turn in turns:
            sentences = re.split(r'(?<=[.!?])\s+', turn.content)
            prefix = f"[{turn.role}]"

            if not sentences:
                continue

            # Always keep first sentence (sets context)
            first = sentences[0].strip()
            if first and len(first) > 10:
                key_sentences.append(f"{prefix} {first}")

            # Keep sentences matching important patterns
            for sentence in sentences[1:]:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 10:
                    continue

                # Questions are always important
                if sentence.endswith("?"):
                    key_sentences.append(f"{prefix} {sentence}")
                    continue

                # Check importance patterns
                for pattern in important_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        key_sentences.append(f"{prefix} {sentence}")
                        break

            # Extract topic terms for dedup
            for term in Manas._extract_terms(turn.content):
                topics_seen.add(term)

        # Deduplicate near-identical sentences
        seen_prefixes: set = set()
        unique_sentences: List[str] = []
        for s in key_sentences:
            prefix_key = s[:40].lower()
            if prefix_key not in seen_prefixes:
                seen_prefixes.add(prefix_key)
                unique_sentences.append(s)

        # Join and enforce a reasonable length
        summary = " | ".join(unique_sentences)

        # If summary is still very long, truncate
        max_len = sum(t.token_estimate for t in turns)  # in chars (/4 for tokens)
        if len(summary) > max_len:
            summary = summary[:max_len] + "..."

        topic_tags = ", ".join(sorted(topics_seen)[:8])
        return f"Topics: {topic_tags}\n{summary}"


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

def create_manas(
    max_tokens: int = 100_000,
    system_prompt: Optional[str] = None,
) -> Manas:
    """
    Create a Manas instance with optional system prompt pre-loaded.

    Args:
        max_tokens: Token budget for the context window.
        system_prompt: If provided, added as a pinned system item.

    Returns:
        A configured Manas instance.
    """
    m = Manas(max_tokens=max_tokens)
    if system_prompt:
        m.add(system_prompt, source="system", pinned=True)
    return m
