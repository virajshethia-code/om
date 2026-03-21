"""
antahkarana.py — The Inner Instrument: Master Pipeline of the Darshana Architecture
====================================================================================

    अन्तःकरण (Antahkarana) = अन्तः (antaḥ, inner) + करण (karaṇa, instrument)

In Samkhya and Vedanta, the Antahkarana is the COMPLETE inner organ of cognition.
It is not one faculty but the integration of all four:

    Manas    — the assembling mind (gathers inputs, manages context)
    Buddhi   — the discriminating intellect (routes, classifies, decides)
    Ahamkara — the self-referential faculty (tracks what I know, tried, failed)
    Chitta   — the memory-field (stores samskaras, recalls relevant experience)

No single faculty is sufficient. Manas without Buddhi is noise. Buddhi without
Ahamkara is reckless. Ahamkara without Chitta is amnesiac. Together they form
the Antahkarana — the one organ through which Purusha (awareness) engages Prakriti
(the world).

This module is the capstone of the Darshana Architecture. It wires together every
component into a single pipeline:

    Perceive → Remember → Assemble → Route → Reason → Filter → Learn → Respond

Every step is optional. If a module is missing, the pipeline degrades gracefully
rather than crashing. The minimum viable pipeline is: Route → Reason → Respond.

Usage:

    from src.antahkarana import Antahkarana

    mind = Antahkarana(api_key="sk-ant-...", budget_daily=10.0)
    response = mind.think("Should we rewrite our backend in Rust?")

    print(response.text)           # The answer
    print(response.darshana)       # Which engine(s) reasoned
    print(response.vritti)         # Output quality classification
    print(response.cost)           # What this query cost
    print(response.depth_score)    # How deep was the analysis
    print(response.self_check)     # Vritti + pramana cross-validation

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Conditional imports — each module is optional. The pipeline degrades
# gracefully if any module is unavailable.
# ---------------------------------------------------------------------------

_MODULES_AVAILABLE: Dict[str, bool] = {}

# Buddhi (router) — REQUIRED for routing, but we can fall back to defaults
try:
    from .darshana_router import (
        DarshanaRouter,
        PramanaTagger,
        Guna,
        Pramana,
        PramanaTag,
        RoutingResult,
    )
    _MODULES_AVAILABLE["buddhi"] = True
except ImportError:
    _MODULES_AVAILABLE["buddhi"] = False

# LLM wrapper — the reasoning engine
try:
    from .darshana_llm import (
        DarshanaLLM,
        DarshanaResponse,
        MultiDarshanaResponse,
    )
    _MODULES_AVAILABLE["darshana_llm"] = True
except ImportError:
    _MODULES_AVAILABLE["darshana_llm"] = False

# Vritti filter — output classification
try:
    from .vritti_filter import (
        VrittiFilter,
        Vritti,
        VrittiResult,
        MayaLayer,
        KarmaStore,
        ConsistencyReport,
        DepthScore,
    )
    _MODULES_AVAILABLE["vritti"] = True
except ImportError:
    _MODULES_AVAILABLE["vritti"] = False

# Ahamkara — self-model
try:
    from .ahamkara import (
        Ahamkara,
        IntrospectionReport,
        Strategy,
        KnowledgeClaim,
    )
    _MODULES_AVAILABLE["ahamkara"] = True
except ImportError:
    _MODULES_AVAILABLE["ahamkara"] = False

# Yaksha — multi-darshana parallel reasoning
try:
    from .yaksha import YakshaProtocol, YakshaResult
    _MODULES_AVAILABLE["yaksha"] = True
except ImportError:
    _MODULES_AVAILABLE["yaksha"] = False

# Prompts
try:
    from .prompts import get_darshana_prompt, build_multi_darshana_prompt
    _MODULES_AVAILABLE["prompts"] = True
except ImportError:
    _MODULES_AVAILABLE["prompts"] = False

# Perception and memory modules (being built by other agents)
try:
    from .smriti import SmritiStore  # type: ignore[import-not-found]
    _MODULES_AVAILABLE["smriti"] = True
except ImportError:
    _MODULES_AVAILABLE["smriti"] = False

try:
    from .pratyaksha import EnvironmentSniffer  # type: ignore[import-not-found]
    _MODULES_AVAILABLE["pratyaksha"] = True
except ImportError:
    _MODULES_AVAILABLE["pratyaksha"] = False


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

logger = logging.getLogger("darshana.antahkarana")


# ---------------------------------------------------------------------------
# Pipeline step trace
# ---------------------------------------------------------------------------

@dataclass
class PipelineStep:
    """Record of a single step in the Antahkarana pipeline."""
    name: str
    status: str  # "completed", "skipped", "degraded", "failed"
    duration_ms: float = 0.0
    detail: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "status": self.status,
            "duration_ms": round(self.duration_ms, 1),
        }
        if self.detail:
            d["detail"] = self.detail
        if self.data:
            d["data"] = self.data
        return d


@dataclass
class PipelineTrace:
    """Complete trace of the full Antahkarana pipeline for one query."""
    query: str
    steps: List[PipelineStep] = field(default_factory=list)
    total_duration_ms: float = 0.0
    modules_available: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "total_duration_ms": round(self.total_duration_ms, 1),
            "modules_available": self.modules_available,
            "steps": [s.to_dict() for s in self.steps],
        }

    def summary(self) -> str:
        lines = [f"Pipeline Trace: {self.query[:80]}"]
        lines.append(f"Total: {self.total_duration_ms:.0f}ms")
        lines.append("")
        for i, step in enumerate(self.steps, 1):
            icon = {"completed": "+", "skipped": "-", "degraded": "~", "failed": "!"}
            marker = icon.get(step.status, "?")
            line = f"  [{marker}] {i}. {step.name} ({step.status}, {step.duration_ms:.0f}ms)"
            if step.detail:
                line += f" — {step.detail}"
            lines.append(line)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Enriched response — the Antahkarana's output
# ---------------------------------------------------------------------------

@dataclass
class AntahkaranaResponse:
    """
    The complete output of the Antahkarana pipeline.

    This is the Purusha-level view: the witness sees every layer of processing
    and their results unified into a single object. Every field is populated
    by a specific pipeline step.

    Attributes:
        text:            The final answer (post-vritti filtering).
        raw_text:        The unfiltered LLM output.
        darshana:        Which reasoning engine(s) were used.
        vritti:          Output quality classification (pramana/viparyaya/etc).
        pramana:         How the primary claim was derived.
        guna:            Processing mode used (sattva/rajas/tamas).
        memories_used:   What memories informed this response.
        cost:            Estimated cost of this query (USD).
        depth_score:     How deep was the analysis (0-100).
        novelty_score:   How novel vs pure recall (0-100).
        self_check:      Vritti + pramana cross-validation result.
        confidence:      Overall confidence in the response.
        model:           The LLM model used.
        latency_ms:      Total wall-clock time.
        input_tokens:    Tokens consumed.
        output_tokens:   Tokens generated.
        perceptions:     Environmental data gathered (step 1).
        strategy:        Ahamkara's pre-query strategy (step 3).
        routing:         Buddhi's routing decision (step 4).
        maya_gaps:       Representation gaps detected.
        pipeline_trace:  Full trace of all pipeline steps.
    """
    text: str = ""
    raw_text: str = ""
    darshana: List[str] = field(default_factory=list)
    vritti: str = "unknown"
    pramana: str = "unknown"
    guna: str = "unknown"
    memories_used: List[str] = field(default_factory=list)
    cost: float = 0.0
    depth_score: int = 0
    novelty_score: int = 50
    self_check: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    model: str = ""
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    perceptions: List[str] = field(default_factory=list)
    strategy: Optional[Dict] = None
    routing: Optional[Dict] = None
    maya_gaps: List[Dict] = field(default_factory=list)
    pipeline_trace: Optional[PipelineTrace] = None

    def to_dict(self) -> dict:
        d = {
            "text": self.text,
            "darshana": self.darshana,
            "vritti": self.vritti,
            "pramana": self.pramana,
            "guna": self.guna,
            "memories_used": self.memories_used,
            "cost": round(self.cost, 6),
            "depth_score": self.depth_score,
            "novelty_score": self.novelty_score,
            "self_check": self.self_check,
            "confidence": round(self.confidence, 3),
            "model": self.model,
            "latency_ms": round(self.latency_ms, 1),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }
        if self.perceptions:
            d["perceptions"] = self.perceptions
        if self.maya_gaps:
            d["maya_gaps"] = self.maya_gaps
        return d


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

# Approximate per-token costs (USD) for common Anthropic models.
# These are estimates; actual pricing may differ.
_MODEL_COSTS: Dict[str, Dict[str, float]] = {
    "claude-sonnet-4-20250514": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
    "claude-haiku-4-20250514": {"input": 0.80 / 1_000_000, "output": 4.0 / 1_000_000},
    "claude-opus-4-20250514": {"input": 15.0 / 1_000_000, "output": 75.0 / 1_000_000},
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate USD cost for a single API call."""
    costs = _MODEL_COSTS.get(model, {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000})
    return input_tokens * costs["input"] + output_tokens * costs["output"]


# ---------------------------------------------------------------------------
# Antahkarana — The Master Pipeline
# ---------------------------------------------------------------------------

class Antahkarana:
    """
    The complete inner instrument of the Darshana Architecture.

    Antahkarana integrates all four cognitive faculties:

        Manas    — context assembly (system instructions + memories + perceptions)
        Buddhi   — routing and discrimination (DarshanaRouter)
        Ahamkara — self-model (knowledge map, attempt log, vasanas)
        Chitta   — memory field (SmritiStore for long-term memory)

    The think() method runs the full 9-step pipeline. Every step is optional;
    the system works with whatever modules are available.

    Args:
        api_key:      Anthropic API key (or set ANTHROPIC_API_KEY env var).
        model:        Model identifier. Defaults to claude-sonnet-4-20250514.
        memory_path:  Path for SmritiStore (long-term memory database).
        state_path:   Path for Ahamkara state persistence.
        budget_daily: Daily spending cap in USD. Default 10.0.
        max_tokens:   Maximum tokens per LLM response. Default 4096.
        max_engines:  Maximum darshana engines to activate. Default 2.
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        memory_path: Optional[str] = None,
        state_path: Optional[str] = None,
        budget_daily: float = 10.0,
        max_tokens: int = 4096,
        max_engines: int = 2,
    ) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens
        self.max_engines = max_engines
        self._budget_daily = budget_daily
        self._spent_today: float = 0.0
        self._budget_reset_day: str = time.strftime("%Y-%m-%d")
        self._last_trace: Optional[PipelineTrace] = None
        self._interaction_count: int = 0

        # Expand ~ in paths
        if memory_path:
            memory_path = os.path.expanduser(memory_path)
        if state_path:
            state_path = os.path.expanduser(state_path)

        # --- Initialize available subsystems ---

        # Buddhi (router) — fast classification
        self._router: Optional[DarshanaRouter] = None
        if _MODULES_AVAILABLE["buddhi"]:
            self._router = DarshanaRouter(
                activation_threshold=0.3,
                max_engines=max_engines,
            )
            logger.info("Buddhi (router) initialized")

        # DarshanaLLM — the reasoning engine
        self._llm: Optional[DarshanaLLM] = None
        if _MODULES_AVAILABLE["darshana_llm"] and self.api_key:
            try:
                self._llm = DarshanaLLM(
                    model=self.model,
                    api_key=self.api_key,
                    max_tokens=max_tokens,
                    max_engines=max_engines,
                )
                logger.info("DarshanaLLM initialized")
            except (ValueError, Exception) as e:
                logger.warning(f"DarshanaLLM init failed: {e}")

        # Vritti filter — output classification
        self._vritti_filter: Optional[VrittiFilter] = None
        self._maya_layer: Optional[MayaLayer] = None
        if _MODULES_AVAILABLE["vritti"]:
            self._vritti_filter = VrittiFilter()
            self._maya_layer = MayaLayer(knowledge_cutoff="2025-05")
            logger.info("Vritti filter initialized")

        # Ahamkara — self-model
        self._ahamkara: Optional[Ahamkara] = None
        if _MODULES_AVAILABLE["ahamkara"]:
            aham_path = state_path or (
                os.path.join(os.path.dirname(memory_path), "ahamkara_state.json")
                if memory_path else None
            )
            try:
                self._ahamkara = Ahamkara(persist_path=aham_path)
                logger.info(f"Ahamkara initialized (persist={aham_path})")
            except Exception as e:
                logger.warning(f"Ahamkara init failed: {e}")

        # Pramana tagger
        self._pramana_tagger: Optional[PramanaTagger] = None
        if _MODULES_AVAILABLE["buddhi"]:
            self._pramana_tagger = PramanaTagger()

        # SmritiStore — long-term memory (future module)
        self._smriti: Any = None
        if _MODULES_AVAILABLE["smriti"]:
            try:
                self._smriti = SmritiStore(memory_path or "~/.darshana/smriti.db")
                logger.info("SmritiStore initialized")
            except Exception as e:
                logger.warning(f"SmritiStore init failed: {e}")

        # EnvironmentSniffer — perception (future module)
        self._sniffer: Any = None
        if _MODULES_AVAILABLE["pratyaksha"]:
            try:
                self._sniffer = EnvironmentSniffer()
                logger.info("EnvironmentSniffer initialized")
            except Exception as e:
                logger.warning(f"EnvironmentSniffer init failed: {e}")

        logger.info(
            f"Antahkarana initialized. Modules: "
            + ", ".join(f"{k}={'ON' if v else 'OFF'}" for k, v in _MODULES_AVAILABLE.items())
        )

    # ======================================================================
    # PUBLIC API: think()
    # ======================================================================

    def think(
        self,
        query: str,
        context: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> AntahkaranaResponse:
        """
        Process a query through the full Antahkarana pipeline.

        The nine steps:
            1. PRATYAKSHA  — gather perceptions
            2. SMRITI      — recall relevant memories
            3. MANAS       — assemble context window
            4. BUDDHI      — route to darshana engine(s)
            5. SHAKTI      — select model and allocate budget
            6. DARSHANA    — actual reasoning (LLM call)
            7. VRITTI      — filter and classify output
            8. AHAMKARA    — self-check and learn
            9. RESPOND     — return enriched response

        Args:
            query:   The user's question or problem.
            context: Optional grounding context (documents, prior conversation).
            mode:    Force a mode: "deep" (dhyana), "broad" (pratyahara), or None (auto).

        Returns:
            AntahkaranaResponse with the answer and full pipeline metadata.
        """
        pipeline_start = time.monotonic()
        trace = PipelineTrace(query=query, modules_available=dict(_MODULES_AVAILABLE))
        response = AntahkaranaResponse()

        # Budget check
        self._maybe_reset_budget()
        if self._spent_today >= self._budget_daily:
            response.text = (
                "[SHAKTI EXHAUSTED] Daily budget of "
                f"${self._budget_daily:.2f} reached. "
                f"Spent: ${self._spent_today:.4f}. "
                "Use budget_remaining() to check, or wait until tomorrow."
            )
            response.pipeline_trace = trace
            return response

        # --- Step 1: PRATYAKSHA — gather perceptions ---
        perceptions = self._step_pratyaksha(query, trace)

        # --- Step 2: SMRITI — recall relevant memories ---
        memories = self._step_smriti(query, trace)

        # --- Step 3: MANAS — assemble context window ---
        assembled_context = self._step_manas(query, context, perceptions, memories, trace)

        # --- Step 4: BUDDHI — route to darshana engine(s) ---
        routing_result = self._step_buddhi(query, mode, trace)

        # --- Step 5: SHAKTI — budget check and model selection ---
        self._step_shakti(trace)

        # --- Step 6: DARSHANA — actual reasoning ---
        darshana_response = self._step_darshana(query, assembled_context, mode, trace)

        # --- Step 7: VRITTI — filter output ---
        vritti_data = self._step_vritti(query, darshana_response, assembled_context, trace)

        # --- Step 8: AHAMKARA — self-check and learn ---
        ahamkara_data = self._step_ahamkara(query, darshana_response, vritti_data, trace)

        # --- Step 9: RESPOND — assemble the final response ---
        total_ms = (time.monotonic() - pipeline_start) * 1000
        trace.total_duration_ms = total_ms

        # Populate response from pipeline outputs
        if darshana_response:
            response.text = vritti_data.get("filtered_text", darshana_response.text)
            response.raw_text = darshana_response.raw_text
            response.darshana = darshana_response.darshana
            response.guna = darshana_response.guna
            response.model = darshana_response.model
            response.input_tokens = darshana_response.input_tokens
            response.output_tokens = darshana_response.output_tokens
            response.pramana = darshana_response.pramana

            # Cost
            cost = _estimate_cost(
                self.model, darshana_response.input_tokens, darshana_response.output_tokens
            )
            self._spent_today += cost
            response.cost = cost

            # Maya gaps
            if darshana_response.maya_gaps:
                response.maya_gaps = darshana_response.maya_gaps

        # Vritti data
        response.vritti = vritti_data.get("vritti", "unknown")
        response.confidence = vritti_data.get("confidence", 0.0)
        response.depth_score = vritti_data.get("depth_score", 0)
        response.novelty_score = vritti_data.get("novelty_score", 50)
        response.self_check = vritti_data.get("self_check", {})

        # Memory + perception
        response.memories_used = memories
        response.perceptions = perceptions

        # Routing
        if routing_result and _MODULES_AVAILABLE["buddhi"]:
            response.routing = {
                "engines": routing_result.top_engines,
                "guna": routing_result.guna.value,
                "scores": routing_result.engine_scores,
            }

        # Strategy from ahamkara
        response.strategy = ahamkara_data.get("strategy")

        response.latency_ms = total_ms
        response.pipeline_trace = trace
        self._last_trace = trace
        self._interaction_count += 1

        trace.steps.append(PipelineStep(
            name="9. RESPOND",
            status="completed",
            detail=f"Assembled response in {total_ms:.0f}ms total",
        ))

        return response

    # ======================================================================
    # PUBLIC API: think_deep() — forces dhyana mode
    # ======================================================================

    def think_deep(self, query: str, context: Optional[str] = None) -> AntahkaranaResponse:
        """
        Deep analysis: dhyana mode, single darshana, maximum depth.

        Forces sattva guna and selects the single best-matching darshana
        engine. The LLM gets maximum tokens and the vritti filter expects
        high depth scores.

        Use for: complex technical decisions, debugging, formal reasoning.
        """
        return self.think(query, context=context, mode="deep")

    # ======================================================================
    # PUBLIC API: think_broad() — forces pratyahara mode / Yaksha Protocol
    # ======================================================================

    def think_broad(self, query: str, context: Optional[str] = None) -> AntahkaranaResponse:
        """
        Broad analysis: pratyahara mode, multi-darshana, Yaksha Protocol.

        Runs multiple darshana engines on the same query and synthesizes
        their perspectives. More expensive but reveals tensions and
        consensus across philosophical viewpoints.

        Use for: strategic decisions, contradictions, open-ended questions.
        """
        return self.think(query, context=context, mode="broad")

    # ======================================================================
    # PUBLIC API: teach() — store a memory / samskara
    # ======================================================================

    def teach(
        self,
        fact: str,
        pramana: str = "pratyaksha",
        confidence: float = 0.9,
        source: str = "user",
    ) -> str:
        """
        Teach the system a fact. Stores it as a knowledge claim in Ahamkara.

        Args:
            fact:       The knowledge to remember.
            pramana:    How this knowledge was derived (pratyaksha/anumana/upamana/shabda).
            confidence: How certain this is (0.0 to 1.0).
            source:     Where it came from.

        Returns:
            Confirmation message.
        """
        if self._ahamkara:
            kc = self._ahamkara.register_knowledge(
                claim=fact,
                pramana=pramana,
                confidence=confidence,
                source=source,
            )
            logger.info(f"Knowledge registered: {fact[:60]}...")
            return (
                f"Registered as {kc.pramana} knowledge with "
                f"confidence {kc.confidence:.2f} in domain '{kc.domain}'."
            )

        # Fallback: store in SmritiStore if available
        if self._smriti:
            self._smriti.store(fact, pramana=pramana, confidence=confidence)
            return f"Stored in SmritiStore with pramana={pramana}."

        return "No memory system available. Fact noted but not persisted."

    # ======================================================================
    # PUBLIC API: forget() — controlled forgetting
    # ======================================================================

    def forget(
        self,
        domain: Optional[str] = None,
        before: Optional[float] = None,
    ) -> str:
        """
        Controlled forgetting. Remove knowledge claims by domain or age.

        Args:
            domain: If provided, forget only claims in this domain.
            before: If provided, forget claims registered before this epoch time.

        Returns:
            Summary of what was forgotten.
        """
        if not self._ahamkara:
            return "No Ahamkara available. Nothing to forget."

        claims = self._ahamkara.knowledge.all_claims()
        to_remove = []
        for kc in claims:
            match_domain = (domain is None) or (kc.domain == domain)
            match_time = (before is None) or (kc.registered_at < before)
            if match_domain and match_time:
                to_remove.append(kc)

        # Remove by rebuilding the list (KnowledgeMap stores claims in a list)
        remaining = [kc for kc in claims if kc not in to_remove]
        self._ahamkara.knowledge._claims = remaining
        self._ahamkara._save()

        count = len(to_remove)
        return (
            f"Forgot {count} knowledge claim(s)"
            + (f" in domain '{domain}'" if domain else "")
            + (f" before {time.ctime(before)}" if before else "")
            + "."
        )

    # ======================================================================
    # PUBLIC API: what_do_i_know() — memory query
    # ======================================================================

    def what_do_i_know(self, topic: str) -> Dict[str, Any]:
        """
        Query the system's knowledge about a topic.

        Returns:
            Dict with relevant knowledge claims and identified gaps.
        """
        result: Dict[str, Any] = {"topic": topic, "claims": [], "gaps": []}

        if self._ahamkara:
            claims = self._ahamkara.query_knowledge(topic)
            result["claims"] = [
                {
                    "claim": kc.claim,
                    "pramana": kc.pramana,
                    "confidence": round(kc.confidence, 3),
                    "source": kc.source,
                    "age_days": round(kc.age_days(), 1),
                }
                for kc in claims[:10]
            ]
            result["gaps"] = self._ahamkara.knowledge.knowledge_gaps(topic)

        if self._smriti:
            try:
                memories = self._smriti.relevant_memories(topic)
                result["long_term_memories"] = memories[:5]
            except Exception:
                pass

        return result

    # ======================================================================
    # PUBLIC API: introspect() — full cognitive self-report
    # ======================================================================

    def introspect(self) -> Dict[str, Any]:
        """
        Full self-report using the Ahamkara layer.

        Returns the system's epistemic state: what it knows, what it has
        tried, what biases it carries, and strategic recommendations.
        """
        report: Dict[str, Any] = {
            "interaction_count": self._interaction_count,
            "budget": {
                "daily_limit": self._budget_daily,
                "spent_today": round(self._spent_today, 4),
                "remaining": round(self._budget_daily - self._spent_today, 4),
            },
            "modules": dict(_MODULES_AVAILABLE),
            "model": self.model,
        }

        if self._ahamkara:
            introspection = self._ahamkara.introspect()
            report["ahamkara"] = introspection.to_dict()

        return report

    # ======================================================================
    # PUBLIC API: budget_remaining()
    # ======================================================================

    def budget_remaining(self) -> Dict[str, float]:
        """Return Shakti (budget) report."""
        self._maybe_reset_budget()
        return {
            "daily_limit": self._budget_daily,
            "spent_today": round(self._spent_today, 6),
            "remaining": round(self._budget_daily - self._spent_today, 6),
            "utilization_pct": round(
                (self._spent_today / max(self._budget_daily, 0.001)) * 100, 2
            ),
        }

    # ======================================================================
    # PUBLIC API: pipeline_trace()
    # ======================================================================

    def pipeline_trace(self) -> Optional[PipelineTrace]:
        """Return the full pipeline trace from the last query."""
        return self._last_trace

    # ======================================================================
    # INTERNAL: Pipeline steps
    # ======================================================================

    def _step_pratyaksha(self, query: str, trace: PipelineTrace) -> List[str]:
        """Step 1: PRATYAKSHA — gather perceptions from environment."""
        step_start = time.monotonic()
        perceptions: List[str] = []

        if not self._sniffer:
            trace.steps.append(PipelineStep(
                name="1. PRATYAKSHA",
                status="skipped",
                detail="No EnvironmentSniffer available",
            ))
            return perceptions

        try:
            perceptions = self._sniffer.perceive(query)
            duration = (time.monotonic() - step_start) * 1000
            trace.steps.append(PipelineStep(
                name="1. PRATYAKSHA",
                status="completed",
                duration_ms=duration,
                detail=f"Gathered {len(perceptions)} perception(s)",
            ))
        except Exception as e:
            duration = (time.monotonic() - step_start) * 1000
            trace.steps.append(PipelineStep(
                name="1. PRATYAKSHA",
                status="failed",
                duration_ms=duration,
                detail=f"Error: {e}",
            ))
            logger.warning(f"Pratyaksha failed: {e}")

        return perceptions

    def _step_smriti(self, query: str, trace: PipelineTrace) -> List[str]:
        """Step 2: SMRITI — recall relevant memories."""
        step_start = time.monotonic()
        memories: List[str] = []

        # Try SmritiStore first (long-term memory)
        if self._smriti:
            try:
                raw = self._smriti.relevant_memories(query)
                memories.extend(raw[:5])
            except Exception as e:
                logger.warning(f"SmritiStore recall failed: {e}")

        # Also check Ahamkara's knowledge map
        if self._ahamkara:
            try:
                claims = self._ahamkara.query_knowledge(query)
                for kc in claims[:5]:
                    if kc.confidence > 0.3:
                        memories.append(
                            f"[{kc.pramana}, conf={kc.confidence:.2f}] {kc.claim}"
                        )
            except Exception as e:
                logger.warning(f"Ahamkara knowledge query failed: {e}")

        duration = (time.monotonic() - step_start) * 1000
        if memories:
            trace.steps.append(PipelineStep(
                name="2. SMRITI",
                status="completed",
                duration_ms=duration,
                detail=f"Recalled {len(memories)} relevant memory(s)",
            ))
        elif self._smriti or self._ahamkara:
            trace.steps.append(PipelineStep(
                name="2. SMRITI",
                status="completed",
                duration_ms=duration,
                detail="No relevant memories found",
            ))
        else:
            trace.steps.append(PipelineStep(
                name="2. SMRITI",
                status="skipped",
                detail="No memory system available",
            ))

        return memories

    def _step_manas(
        self,
        query: str,
        user_context: Optional[str],
        perceptions: List[str],
        memories: List[str],
        trace: PipelineTrace,
    ) -> Optional[str]:
        """Step 3: MANAS — assemble context window."""
        step_start = time.monotonic()
        parts: List[str] = []

        # Pin system instructions
        # (handled by the LLM layer's system prompt, but we add supplementary context)

        # Add memories
        if memories:
            parts.append("RELEVANT MEMORIES:")
            for m in memories:
                parts.append(f"  - {m}")

        # Add perceptions
        if perceptions:
            parts.append("\nENVIRONMENT PERCEPTIONS:")
            for p in perceptions:
                parts.append(f"  - {p}")

        # Add user-provided context
        if user_context:
            parts.append(f"\nUSER CONTEXT:\n{user_context}")

        # Ahamkara strategy (if available)
        strategy_data = None
        if self._ahamkara:
            try:
                strategy = self._ahamkara.strategize(query)
                strategy_data = strategy.to_dict()
                if strategy.warnings:
                    parts.append("\nAHAMKARA WARNINGS:")
                    for w in strategy.warnings:
                        parts.append(f"  - {w}")
                if strategy.relevant_knowledge:
                    parts.append("\nRELEVANT PRIOR KNOWLEDGE:")
                    for kc in strategy.relevant_knowledge:
                        parts.append(
                            f"  - [{kc['pramana']}] {kc['claim']} "
                            f"(conf: {kc['confidence']})"
                        )
            except Exception as e:
                logger.warning(f"Ahamkara strategize failed: {e}")

        assembled = "\n".join(parts) if parts else None
        duration = (time.monotonic() - step_start) * 1000

        trace.steps.append(PipelineStep(
            name="3. MANAS",
            status="completed",
            duration_ms=duration,
            detail=f"Assembled {len(parts)} context section(s)",
            data={"strategy": strategy_data} if strategy_data else {},
        ))

        return assembled

    def _step_buddhi(
        self, query: str, mode: Optional[str], trace: PipelineTrace,
    ) -> Optional[RoutingResult]:
        """Step 4: BUDDHI — route to darshana engine(s)."""
        step_start = time.monotonic()

        if not self._router:
            trace.steps.append(PipelineStep(
                name="4. BUDDHI",
                status="skipped",
                detail="No router available; LLM layer will handle routing",
            ))
            return None

        try:
            routing = self._router.route(query)
            duration = (time.monotonic() - step_start) * 1000

            # Mode override
            if mode == "deep":
                # Single best engine for deep analysis
                routing.top_engines = routing.top_engines[:1]
                routing.guna = Guna.SATTVA
            elif mode == "broad":
                # Multiple engines for broad analysis
                sorted_engines = sorted(
                    routing.engine_scores.items(), key=lambda x: x[1], reverse=True
                )
                routing.top_engines = [name for name, _ in sorted_engines[:min(4, len(sorted_engines))]]
                routing.guna = Guna.RAJAS

            trace.steps.append(PipelineStep(
                name="4. BUDDHI",
                status="completed",
                duration_ms=duration,
                detail=(
                    f"Routed to {', '.join(routing.top_engines)} "
                    f"(guna: {routing.guna.value})"
                ),
                data={
                    "engines": routing.top_engines,
                    "guna": routing.guna.value,
                    "scores": {k: round(v, 3) for k, v in routing.engine_scores.items()},
                },
            ))
            return routing

        except Exception as e:
            duration = (time.monotonic() - step_start) * 1000
            trace.steps.append(PipelineStep(
                name="4. BUDDHI",
                status="failed",
                duration_ms=duration,
                detail=f"Routing error: {e}",
            ))
            logger.warning(f"Buddhi routing failed: {e}")
            return None

    def _step_shakti(self, trace: PipelineTrace) -> None:
        """Step 5: SHAKTI — budget check and model selection."""
        remaining = self._budget_daily - self._spent_today
        trace.steps.append(PipelineStep(
            name="5. SHAKTI",
            status="completed",
            detail=(
                f"Model: {self.model} | "
                f"Budget: ${remaining:.4f} remaining of ${self._budget_daily:.2f}"
            ),
            data={
                "model": self.model,
                "budget_remaining": round(remaining, 4),
            },
        ))

    def _step_darshana(
        self,
        query: str,
        context: Optional[str],
        mode: Optional[str],
        trace: PipelineTrace,
    ) -> Optional[DarshanaResponse]:
        """Step 6: DARSHANA — actual reasoning via LLM."""
        step_start = time.monotonic()

        if not self._llm:
            trace.steps.append(PipelineStep(
                name="6. DARSHANA",
                status="skipped",
                detail="No LLM available (missing API key or darshana_llm module)",
            ))
            return None

        try:
            if mode == "broad":
                # Multi-darshana synthesis
                multi_resp = self._llm.think_multi(query, context=context)
                resp = multi_resp.synthesis
            else:
                resp = self._llm.think(query, context=context)

            duration = (time.monotonic() - step_start) * 1000
            trace.steps.append(PipelineStep(
                name="6. DARSHANA",
                status="completed",
                duration_ms=duration,
                detail=(
                    f"Engine(s): {', '.join(resp.darshana)} | "
                    f"Tokens: {resp.input_tokens}in/{resp.output_tokens}out | "
                    f"LLM latency: {resp.latency_ms:.0f}ms"
                ),
            ))
            return resp

        except Exception as e:
            duration = (time.monotonic() - step_start) * 1000
            trace.steps.append(PipelineStep(
                name="6. DARSHANA",
                status="failed",
                duration_ms=duration,
                detail=f"LLM call failed: {e}",
            ))
            logger.error(f"Darshana reasoning failed: {e}")
            return None

    def _step_vritti(
        self,
        query: str,
        darshana_response: Optional[DarshanaResponse],
        context: Optional[str],
        trace: PipelineTrace,
    ) -> Dict[str, Any]:
        """Step 7: VRITTI — filter and classify output."""
        step_start = time.monotonic()
        result: Dict[str, Any] = {
            "vritti": "unknown",
            "confidence": 0.0,
            "filtered_text": "",
            "depth_score": 0,
            "novelty_score": 50,
            "self_check": {},
        }

        if not darshana_response:
            trace.steps.append(PipelineStep(
                name="7. VRITTI",
                status="skipped",
                detail="No darshana response to filter",
            ))
            return result

        raw_text = darshana_response.raw_text or darshana_response.text

        if not self._vritti_filter:
            # Degraded mode — pass through with data from darshana_response
            result["vritti"] = darshana_response.vritti
            result["confidence"] = darshana_response.confidence
            result["filtered_text"] = darshana_response.text
            trace.steps.append(PipelineStep(
                name="7. VRITTI",
                status="degraded",
                detail="No VrittiFilter; using DarshanaLLM's built-in classification",
            ))
            return result

        try:
            # Full vritti classification
            vritti_result = self._vritti_filter.classify(raw_text, context=context)
            filtered_text = self._vritti_filter.filter(raw_text, context=context)

            result["vritti"] = vritti_result.vritti.value
            result["confidence"] = vritti_result.confidence
            result["filtered_text"] = filtered_text

            # Depth score
            try:
                depth = self._vritti_filter.depth_test(raw_text, query=query)
                result["depth_score"] = depth.score
            except (AttributeError, TypeError, Exception):
                pass

            # Novelty score
            try:
                result["novelty_score"] = self._vritti_filter.novelty_score(raw_text)
            except (AttributeError, Exception):
                pass

            # Cross-validation (self_check): vritti vs pramana
            try:
                # cross_validate expects a Pramana enum, not PramanaTag object
                pramana_enum = None
                if darshana_response.pramana_tag and hasattr(darshana_response.pramana_tag, "source"):
                    pramana_enum = darshana_response.pramana_tag.source
                elif darshana_response.pramana:
                    # Try to resolve from the string value
                    from .vritti_filter import Pramana as VrittiPramana
                    try:
                        pramana_enum = VrittiPramana(darshana_response.pramana)
                    except (ValueError, KeyError):
                        pramana_enum = VrittiPramana.SHABDA

                if pramana_enum:
                    consistency = self._vritti_filter.cross_validate(
                        vritti_result, pramana_enum
                    )
                    result["self_check"] = consistency.to_dict()
                else:
                    result["self_check"] = {
                        "vritti": vritti_result.vritti.value,
                        "pramana": darshana_response.pramana,
                        "note": "Pramana enum could not be resolved",
                    }
            except (AttributeError, Exception):
                result["self_check"] = {
                    "vritti": vritti_result.vritti.value,
                    "pramana": darshana_response.pramana,
                    "note": "Cross-validation not available",
                }

            duration = (time.monotonic() - step_start) * 1000
            trace.steps.append(PipelineStep(
                name="7. VRITTI",
                status="completed",
                duration_ms=duration,
                detail=(
                    f"Classified as {vritti_result.vritti.value} "
                    f"(confidence: {vritti_result.confidence:.2f}) | "
                    f"Depth: {result['depth_score']} | "
                    f"Novelty: {result['novelty_score']}"
                ),
            ))

        except Exception as e:
            duration = (time.monotonic() - step_start) * 1000
            result["filtered_text"] = darshana_response.text
            trace.steps.append(PipelineStep(
                name="7. VRITTI",
                status="failed",
                duration_ms=duration,
                detail=f"Filter error: {e}",
            ))
            logger.warning(f"Vritti filter failed: {e}")

        return result

    def _step_ahamkara(
        self,
        query: str,
        darshana_response: Optional[DarshanaResponse],
        vritti_data: Dict[str, Any],
        trace: PipelineTrace,
    ) -> Dict[str, Any]:
        """Step 8: AHAMKARA — self-check, learn from this interaction."""
        step_start = time.monotonic()
        result: Dict[str, Any] = {}

        if not self._ahamkara:
            trace.steps.append(PipelineStep(
                name="8. AHAMKARA",
                status="skipped",
                detail="No Ahamkara self-model available",
            ))
            return result

        try:
            # Determine success: pramana vritti = success, others = nuanced
            vritti = vritti_data.get("vritti", "unknown")
            confidence = vritti_data.get("confidence", 0.0)
            success = vritti == "pramana" and confidence > 0.4

            # Record the attempt
            if darshana_response:
                for engine in darshana_response.darshana:
                    self._ahamkara.record_attempt(
                        query=query,
                        darshana=engine,
                        success=success,
                        reason=f"vritti={vritti}, confidence={confidence:.2f}",
                    )

                # Detect bias in the response
                biases = self._ahamkara.vasanas.detect_bias(
                    query, darshana_response.raw_text or ""
                )
                if biases:
                    result["bias_warnings"] = [b["concern"] for b in biases[:3]]

            # Get strategy that was used (for the response)
            try:
                strategy = self._ahamkara.strategize(query)
                result["strategy"] = strategy.to_dict()
            except Exception:
                pass

            duration = (time.monotonic() - step_start) * 1000
            detail_parts = [f"Recorded interaction (success={success})"]
            if result.get("bias_warnings"):
                detail_parts.append(f"{len(result['bias_warnings'])} bias warning(s)")
            trace.steps.append(PipelineStep(
                name="8. AHAMKARA",
                status="completed",
                duration_ms=duration,
                detail=" | ".join(detail_parts),
            ))

        except Exception as e:
            duration = (time.monotonic() - step_start) * 1000
            trace.steps.append(PipelineStep(
                name="8. AHAMKARA",
                status="failed",
                duration_ms=duration,
                detail=f"Self-model error: {e}",
            ))
            logger.warning(f"Ahamkara step failed: {e}")

        return result

    # ======================================================================
    # INTERNAL: Budget management
    # ======================================================================

    def _maybe_reset_budget(self) -> None:
        """Reset daily budget if the day has changed."""
        today = time.strftime("%Y-%m-%d")
        if today != self._budget_reset_day:
            self._spent_today = 0.0
            self._budget_reset_day = today

    # ======================================================================
    # Representation
    # ======================================================================

    def __repr__(self) -> str:
        active = sum(1 for v in _MODULES_AVAILABLE.values() if v)
        total = len(_MODULES_AVAILABLE)
        return (
            f"Antahkarana(model={self.model!r}, "
            f"modules={active}/{total} active, "
            f"interactions={self._interaction_count}, "
            f"budget_remaining=${self._budget_daily - self._spent_today:.4f})"
        )
