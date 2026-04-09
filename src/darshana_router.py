"""
darshana_router.py — The Buddhi Layer of the Darshana Architecture

This module implements the Shaddarshana Router: a classifier that takes an
input query and routes it to one or more of six specialized reasoning engines,
each derived from a classical school of Hindu philosophy.

The six engines (darshanas) are complementary, not competing. Each addresses
a different aspect of cognition:

    Nyaya       — epistemology, formal logic, proof chains
    Vaisheshika — ontology, atomic decomposition, type systems
    Samkhya     — enumeration, classification, layer mapping
    Yoga        — attention, noise filtering, focus
    Mimamsa     — hermeneutics, text-to-action, intent parsing
    Vedanta     — synthesis, contradiction resolution, meta-reasoning

Supporting subsystems (from the Ahamkara layer):

    GunaEngine     — sets processing mode (Sattva / Rajas / Tamas)
    PramanaTagger  — tags knowledge claims by epistemic source

Architecture reference: See THESIS.md for the full layer model derived
from Samkhya's 25 Tattvas.

This proof-of-concept uses keyword/pattern matching for classification.
In production the Buddhi layer would be a trained classifier or an LLM
call with structured output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Guna(Enum):
    """
    The three Gunas — fundamental processing modes from Samkhya philosophy.

    In Samkhya, the three gunas are the constituent qualities of Prakriti
    (nature/matter). Here they control HOW the system reasons:

        Sattva — clarity, precision, low temperature. For logic, facts,
                 and validation where accuracy is paramount.
        Rajas  — activity, exploration, high temperature. For creative,
                 novel, or open-ended problems requiring divergent thinking.
        Tamas  — inertia, retrieval, efficiency. For routine queries
                 where cached patterns and known answers suffice.
    """
    SATTVA = "sattva"
    RAJAS = "rajas"
    TAMAS = "tamas"


class Pramana(Enum):
    """
    The four Pramanas — valid means of knowledge from Nyaya epistemology.

    Every knowledge claim should be tagged with HOW it was derived. This is
    the foundation of epistemic honesty in the Darshana Architecture.

        Pratyaksha — direct perception. Data from input, sensors, or tools.
                     Highest confidence.
        Anumana    — inference. Derived through reasoning. Medium confidence;
                     check for logical fallacies.
        Upamana    — analogy. Understanding through comparison. Lower
                     confidence; flag as analogical reasoning.
        Shabda     — testimony. From authority, training data, or documents.
                     Confidence depends on source reliability and recency.
    """
    PRATYAKSHA = "pratyaksha"
    ANUMANA = "anumana"
    UPAMANA = "upamana"
    SHABDA = "shabda"


# ---------------------------------------------------------------------------
# Data classes for structured output
# ---------------------------------------------------------------------------

@dataclass
class PramanaTag:
    """A knowledge claim annotated with its epistemic source."""
    claim: str
    source: Pramana
    confidence: float  # 0.0 to 1.0
    note: str = ""


@dataclass
class RoutingDecision:
    """Structured routing decision with depth intelligence."""
    selected_engines: List[str]  # ordered by relevance
    depth_mode: str  # "deep" or "broad"
    reasoning: str  # why these engines were selected


@dataclass
class RoutingResult:
    """The Buddhi layer's classification of a query."""
    query: str
    engine_scores: Dict[str, float]  # engine name -> confidence 0.0–1.0
    guna: Guna
    top_engines: List[str] = field(default_factory=list)
    decision: Optional[RoutingDecision] = None

    def __post_init__(self):
        if not self.top_engines:
            # Activate engines above the threshold, or at least the top one
            sorted_engines = sorted(
                self.engine_scores.items(), key=lambda x: x[1], reverse=True
            )
            self.top_engines = [
                name for name, score in sorted_engines if score >= 0.3
            ]
            if not self.top_engines and sorted_engines:
                self.top_engines = [sorted_engines[0][0]]


@dataclass
class ReasoningOutput:
    """Structured output from a single darshana engine."""
    engine: str
    approach: str
    prompt_template: str
    pramana_tags: List[PramanaTag] = field(default_factory=list)
    guna: Guna = Guna.SATTVA


@dataclass
class DarshanaResult:
    """Combined output from the full routing + reasoning pipeline."""
    query: str
    routing: RoutingResult
    reasoning: List[ReasoningOutput] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Guna Engine — Dynamic Processing Mode
# ---------------------------------------------------------------------------

class GunaEngine:
    """
    Determines the processing mode (guna) for a given query.

    In Samkhya philosophy, the three gunas pervade all of Prakriti. Every
    phenomenon is a mixture of sattva (clarity), rajas (activity), and
    tamas (inertia). The GunaEngine reads the query and decides which
    mode should dominate.

    This is analogous to dynamically setting an LLM's temperature and
    retrieval strategy based on task type — but framed as a first-class
    architectural decision rather than a knob to tune.
    """

    # Patterns that suggest each guna
    _SATTVA_PATTERNS: List[str] = [
        r"\b(prove|valid\w*|correct\w*|true|false|logic\w*|fact\w*|verif\w*|check)\b",
        r"\b(precise\w*|exact\w*|formal\w*|rigorous|definit\w*)\b",
        r"\b(debug\w*|error|bug|fix\w*|root cause)\b",
        r"\b(type|schema|constraint\w*|invariant)\b",
    ]

    _RAJAS_PATTERNS: List[str] = [
        r"\b(creat\w*|innovat\w*|imagin\w*|explor\w*|brainstorm\w*|novel)\b",
        r"(what if|could we|how might|possibilit\w*|alternat\w*)",
        r"\b(design\w*|invent\w*|generat\w*|ideat\w*|diverg\w*)\b",
        r"\b(vision\w*|inspir\w*|transform\w*|rethink|reimagin\w*)\b",
    ]

    _TAMAS_PATTERNS: List[str] = [
        r"(what is|define|look up|retrieve|recall|find)\b",
        r"\b(standard|convention\w*|usual\w*|typical\w*|common)\b",
        r"(how do I|tutorial|example|step.by.step|recipe)",
        r"\b(list|show me|get|fetch|search)\b",
    ]

    def classify(self, query: str) -> Guna:
        """
        Classify a query into its dominant guna (processing mode).

        Returns the guna with the highest pattern match count.
        Defaults to Sattva (precision) when ambiguous — it is safer
        to be precise than to hallucinate creatively.
        """
        q = query.lower()
        scores = {
            Guna.SATTVA: self._score(q, self._SATTVA_PATTERNS),
            Guna.RAJAS: self._score(q, self._RAJAS_PATTERNS),
            Guna.TAMAS: self._score(q, self._TAMAS_PATTERNS),
        }
        return max(scores, key=scores.get)  # type: ignore[arg-type]

    @staticmethod
    def _score(text: str, patterns: List[str]) -> float:
        """Count how many pattern groups match, normalized."""
        hits = sum(1 for p in patterns if re.search(p, text))
        return hits / len(patterns) if patterns else 0.0


# ---------------------------------------------------------------------------
# Pramana Tagger — Epistemic Provenance
# ---------------------------------------------------------------------------

class PramanaTagger:
    """
    Tags knowledge claims with their epistemic source (pramana).

    In Nyaya epistemology, valid knowledge (prama) can only arise through
    recognized means (pramanas). By tagging every claim, the system
    maintains transparency about WHERE its knowledge comes from and
    HOW confident it should be.

    This is the architectural antidote to hallucination: not suppressing
    uncertain outputs, but labeling them honestly.
    """

    # Heuristic patterns for each pramana type
    _PRATYAKSHA_MARKERS = [
        r"\b(the input says|the data shows|the file contains|observed|measured)\b",
        r"\b(user said|user provided|given that|from the (input|query|context))\b",
    ]
    _ANUMANA_MARKERS = [
        r"\b(therefore|thus|implies|because|if .+ then|it follows|we can infer)\b",
        r"\b(likely|probably|suggests|indicates|based on)\b",
    ]
    _UPAMANA_MARKERS = [
        r"\b(like|similar to|analogous|resembles|just as|compared to)\b",
        r"\b(metaphor|analogy|parallel|reminiscent)\b",
    ]
    _SHABDA_MARKERS = [
        r"\b(according to|the documentation says|research shows)\b",
        r"\b(it is known|generally|traditionally|the spec says|defined as)\b",
    ]

    def tag(self, claim: str) -> PramanaTag:
        """
        Analyze a knowledge claim and return its most likely pramana.

        Scores each pramana type by pattern matches and returns the
        best fit. Confidence reflects how clearly the claim maps to
        a single pramana.
        """
        c = claim.lower()
        scores = {
            Pramana.PRATYAKSHA: self._score(c, self._PRATYAKSHA_MARKERS),
            Pramana.ANUMANA: self._score(c, self._ANUMANA_MARKERS),
            Pramana.UPAMANA: self._score(c, self._UPAMANA_MARKERS),
            Pramana.SHABDA: self._score(c, self._SHABDA_MARKERS),
        }

        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_score = scores[best]
        total = sum(scores.values())

        # Confidence is the proportion of signal attributable to the best pramana.
        # If nothing matches, default to Shabda (training data) with low confidence.
        if total == 0:
            return PramanaTag(
                claim=claim,
                source=Pramana.SHABDA,
                confidence=0.3,
                note="No clear epistemic markers; defaulting to testimony (shabda).",
            )

        confidence = round(best_score / total, 2)
        notes = {
            Pramana.PRATYAKSHA: "Derived directly from input data or observation.",
            Pramana.ANUMANA: "Inferred through reasoning; verify logical chain.",
            Pramana.UPAMANA: "Based on analogy; may not transfer perfectly.",
            Pramana.SHABDA: "From authority or reference material; check recency.",
        }
        return PramanaTag(
            claim=claim,
            source=best,
            confidence=confidence,
            note=notes[best],
        )

    @staticmethod
    def _score(text: str, patterns: List[str]) -> float:
        return sum(1 for p in patterns if re.search(p, text))


# ---------------------------------------------------------------------------
# Base Darshana Engine
# ---------------------------------------------------------------------------

class DarshanaEngine:
    """
    Abstract base for the six darshana reasoning engines.

    Each engine encapsulates the reasoning STYLE of one philosophical
    school. In this POC, that style is expressed as a structured prompt
    template that describes how the darshana would approach the problem.

    In production, these templates would be sent to an LLM with the
    query and context to generate actual reasoning.
    """

    name: str = "base"
    description: str = ""

    # Keyword patterns that indicate this engine should activate.
    # Each sublist is an OR-group; the engine's score is the fraction
    # of groups that matched.
    trigger_patterns: List[str] = []

    def score(self, query: str) -> float:
        """
        Return a 0.0–1.0 confidence that this engine is relevant to the query.
        """
        if not self.trigger_patterns:
            return 0.0
        q = query.lower()
        hits = sum(1 for p in self.trigger_patterns if re.search(p, q))
        return round(hits / len(self.trigger_patterns), 3)

    def reason(self, query: str, context: Optional[Dict] = None) -> ReasoningOutput:
        """
        Apply this darshana's reasoning style to the query.

        Returns a ReasoningOutput with an approach description and a
        prompt template that an LLM could execute.
        """
        raise NotImplementedError


# ---------------------------------------------------------------------------
# The Six Engines
# ---------------------------------------------------------------------------

class NyayaEngine(DarshanaEngine):
    """
    Nyaya — The Engine of Logic and Epistemology

    Nyaya is the school of logic, debate, and valid knowledge. Its
    contribution to Indian philosophy is the Nyaya Sutra's rigorous
    system of syllogistic reasoning (the five-membered syllogism) and
    its classification of logical fallacies (hetvabhasa).

    In the Darshana Architecture, Nyaya handles truth claims, argument
    validation, proof construction, and fallacy detection.
    """

    name = "nyaya"
    description = "Formal logic, proof chains, validation, fallacy detection"

    trigger_patterns = [
        r"\b(true|false|correct\w*|incorrect\w*|valid\w*|invalid\w*)\b",
        r"\b(prove|proof|disprove|demonstrat\w*|verif\w*)\b",
        r"\b(logic\w*|fallac\w*|syllogism)\b",
        r"\b(argument|premise|conclusion|therefore|implies)\b",
        r"(is this (right|correct|true|wrong)|does this follow)",
        r"\b(contradiction|inconsisten\w*|paradox)\b",
        r"(if .+ then|necessary|sufficient)",
        r"\bmust be (wrong|right|correct|true|false)\b",
        r"\bshould .+ because\b",
    ]

    def reason(self, query: str, context: Optional[Dict] = None) -> ReasoningOutput:
        ctx = context or {}
        return ReasoningOutput(
            engine=self.name,
            approach=(
                "Apply Nyaya's five-membered syllogism (panchavayava):\n"
                "1. Pratijna (thesis) — state the claim to be evaluated\n"
                "2. Hetu (reason) — identify the supporting reason\n"
                "3. Udaharana (example) — find a corroborating instance\n"
                "4. Upanaya (application) — apply the general rule to this case\n"
                "5. Nigamana (conclusion) — derive the validated result\n\n"
                "Then scan for hetvabhasa (fallacies): is the reason\n"
                "unestablished, contradictory, inconclusive, or circular?"
            ),
            prompt_template=(
                "You are reasoning in the Nyaya tradition — rigorous logical analysis.\n\n"
                f"QUERY: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. Identify the central claim or truth question.\n"
                "2. Construct a formal argument for it (thesis, reason, example, "
                "application, conclusion).\n"
                "3. Check for logical fallacies in the argument.\n"
                "4. If the claim is false, construct the counter-argument.\n"
                "5. State your conclusion with explicit confidence level.\n"
                "6. Tag each step with its pramana (source of knowledge)."
            ),
            pramana_tags=[
                PramanaTag(
                    claim="Applying formal syllogistic reasoning to evaluate the query.",
                    source=Pramana.ANUMANA,
                    confidence=0.8,
                    note="Nyaya's method is inferential by nature.",
                )
            ],
            guna=Guna.SATTVA,
        )


class SamkhyaEngine(DarshanaEngine):
    """
    Samkhya — The Engine of Enumeration and Classification

    Samkhya (literally "counting/enumeration") is the oldest systematic
    philosophy in India. It enumerates 25 tattvas (principles) that
    compose all of reality, from pure consciousness (Purusha) down to
    the five gross elements.

    In the Darshana Architecture, Samkhya handles decomposition tasks:
    breaking complex systems into their constituent layers, classifying
    components, and mapping hierarchies.
    """

    name = "samkhya"
    description = "Decomposition, classification, enumeration, layer mapping"

    trigger_patterns = [
        r"\b(parts?|components?|layers?|levels?|tiers?)\b",
        r"\b(break (this |it )?down|decompos\w*|analyz\w*|dissect)\b",
        r"\b(classif\w*|categoriz\w*|taxonom\w*|typolog\w*|sort)\b",
        r"\b(architect\w*|structur\w*|hierarch\w*|organiz\w*)\b",
        r"(how many|enumerate|list (the|all)|what are the)",
        r"\b(system|pipeline|workflow|process)\b",
    ]

    def reason(self, query: str, context: Optional[Dict] = None) -> ReasoningOutput:
        return ReasoningOutput(
            engine=self.name,
            approach=(
                "Apply Samkhya's enumerative method:\n"
                "1. Identify the whole (the system or concept to decompose)\n"
                "2. Enumerate its tattvas (constituent principles/layers)\n"
                "3. Map causal relationships — which layers emerge from which\n"
                "4. Classify each component by its nature (purusha vs prakriti,\n"
                "   abstract vs concrete, input vs output)\n"
                "5. Verify completeness — are all 'tattvas' accounted for?"
            ),
            prompt_template=(
                "You are reasoning in the Samkhya tradition — systematic enumeration "
                "and classification.\n\n"
                f"QUERY: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. Identify the system or concept to decompose.\n"
                "2. List its fundamental components (tattvas) in hierarchical order.\n"
                "3. For each component, state: what it is, what it does, "
                "and what it depends on.\n"
                "4. Draw the causal/compositional hierarchy.\n"
                "5. Check for completeness — is anything missing from the enumeration?"
            ),
            pramana_tags=[
                PramanaTag(
                    claim="Decomposition is based on analysis of the query's structure.",
                    source=Pramana.ANUMANA,
                    confidence=0.7,
                    note="Classification involves inferential judgment.",
                )
            ],
            guna=Guna.SATTVA,
        )


class YogaEngine(DarshanaEngine):
    """
    Yoga — The Engine of Focus and Noise Filtering

    Yoga (from 'yuj', to yoke/unite) is the science of disciplined
    attention. Patanjali's Yoga Sutras define yoga as 'chitta vritti
    nirodha' — the cessation of mental fluctuations.

    In the Darshana Architecture, Yoga handles information overload:
    filtering noise, ranking by relevance, extracting signal, and
    focusing computation on what actually matters.
    """

    name = "yoga"
    description = "Noise filtering, focus, relevance ranking, signal extraction"

    trigger_patterns = [
        r"\b(focus\w*|priorit\w*|important|matters?|relevant|key)\b",
        r"\b(noise|overload|too (many|much)|overwhelm\w*|clutter)\b",
        r"\b(filter\w*|distill\w*|extract\w*|essential|core|crux)\b",
        r"\b(signal|rank\w*|sort by|top|most important)\b",
        r"(what (matters|should I focus on)|where to start)",
        r"\b(simplif\w*|reduc\w*|streamline|cut through)\b",
    ]

    def reason(self, query: str, context: Optional[Dict] = None) -> ReasoningOutput:
        return ReasoningOutput(
            engine=self.name,
            approach=(
                "Apply Yoga's pratyahara (sense withdrawal) and dharana (concentration):\n"
                "1. Pratyahara — withdraw from the noise. List all inputs, then\n"
                "   identify which are distractions vs. genuine signal.\n"
                "2. Dharana — fix attention on the core. What is the ONE thing\n"
                "   that matters most here?\n"
                "3. Dhyana — sustained focus. Explore that core deeply rather\n"
                "   than broadly.\n"
                "4. Vritti classification — categorize each piece of information\n"
                "   as pramana (valid), viparyaya (misconception), vikalpa\n"
                "   (verbal noise), nidra (absent), or smriti (memory)."
            ),
            prompt_template=(
                "You are reasoning in the Yoga tradition — disciplined attention "
                "and noise reduction.\n\n"
                f"QUERY: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. List all pieces of information or factors present in the query.\n"
                "2. Classify each as: signal (directly relevant), noise (distraction), "
                "or context (useful background).\n"
                "3. Rank the signal items by importance.\n"
                "4. State the single most important thing to focus on.\n"
                "5. Suggest what to ignore entirely."
            ),
            pramana_tags=[
                PramanaTag(
                    claim="Relevance ranking is based on analysis of the query's context.",
                    source=Pramana.ANUMANA,
                    confidence=0.6,
                    note="Prioritization involves subjective judgment.",
                )
            ],
            guna=Guna.RAJAS,
        )


class VedantaEngine(DarshanaEngine):
    """
    Vedanta — The Engine of Synthesis and Unification

    Vedanta (literally 'end of the Vedas') seeks the ultimate reality
    beneath surface appearances. Advaita Vedanta's core insight is that
    apparent contradictions dissolve when viewed from a higher level of
    abstraction — the famous 'neti neti' (not this, not this) method
    of stripping away surface features to find deeper unity.

    In the Darshana Architecture, Vedanta handles contradiction resolution,
    finding unifying abstractions, and meta-level reasoning about the
    reasoning process itself.
    """

    name = "vedanta"
    description = "Contradiction resolution, unifying abstractions, meta-reasoning"

    trigger_patterns = [
        # Contradiction / tension language
        r"\b(contradict\w*|paradox\w*|conflict\w*|inconsisten\w*|tension)\b",
        r"(\bbut\b.*\b(says?|think|believe|argue|is)|however|on the other hand)",
        r"(seems? contradict\w*|doesn'?t make sense that|who'?s right)",
        r"(say.+\bcorrect\b.+\bbut\b|say.+\bright\b.+\bbut\b|say.+\bbut\b.+\bsay)",
        # Integration / synthesis language
        r"\b(unif\w*|synthes\w*|reconcil\w*|integrat\w*|harmoniz\w*)\b",
        r"(how do (these|they) fit|big(ger)? picture|what'?s really going on)",
        # Abstract / deeper meaning
        r"\b(underlying|deeper|fundamental|ultimate|overarching)\b",
        r"(what does it (all )?mean|why does this matter|what'?s the point)",
        # Opposing perspectives
        r"(both .+ and|neither .+ nor|on one hand)",
        r"\b(vs\.?|versus|on the other)\b",
        r"\b(meta|abstract\w*|transcend\w*|beyond)\b",
        r"(how (do|can) (these|they) .*(fit|work) together)",
    ]

    def reason(self, query: str, context: Optional[Dict] = None) -> ReasoningOutput:
        return ReasoningOutput(
            engine=self.name,
            approach=(
                "Apply Vedanta's method of adhyaropa-apavada (superimposition\n"
                "and negation):\n"
                "1. State the apparent contradiction or multiplicity.\n"
                "2. Neti neti — strip away surface differences. What do the\n"
                "   conflicting positions share at a deeper level?\n"
                "3. Identify the adhyaropa (superimposition) — what false\n"
                "   distinction is creating the appearance of conflict?\n"
                "4. Find the unifying abstraction that resolves the paradox.\n"
                "5. Re-derive the surface positions from the unified view,\n"
                "   showing how they are partial truths of a larger whole."
            ),
            prompt_template=(
                "You are reasoning in the Vedanta tradition — seeking unity beneath "
                "apparent contradiction.\n\n"
                f"QUERY: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. Identify the conflicting positions or contradictions.\n"
                "2. For each position, state what it gets RIGHT.\n"
                "3. Find the level of abstraction where the contradiction dissolves.\n"
                "4. Propose a unifying framework or principle.\n"
                "5. Show how each original position is a partial view of the "
                "unified truth."
            ),
            pramana_tags=[
                PramanaTag(
                    claim="Synthesis requires reasoning beyond what is directly stated.",
                    source=Pramana.ANUMANA,
                    confidence=0.65,
                    note="Vedantic unification is inherently inferential and interpretive.",
                )
            ],
            guna=Guna.RAJAS,
        )


class MimamsaEngine(DarshanaEngine):
    """
    Mimamsa — The Engine of Interpretation and Action

    Purva Mimamsa is the school of textual interpretation. It was
    originally developed to interpret Vedic injunctions — extracting
    precise instructions for action from complex, layered texts.
    Mimamsa developed sophisticated hermeneutic rules (e.g., the six
    lingas for determining the meaning of a passage).

    In the Darshana Architecture, Mimamsa handles specs, requirements,
    instructions, and any situation where text must be converted into
    clear, actionable steps.
    """

    name = "mimamsa"
    description = "Text interpretation, command extraction, intent parsing, action inference"

    trigger_patterns = [
        # Action extraction
        r"(what should (I|we) do|action\s*items?|next steps?|todo|obligations?)",
        r"(what do they (actually )?want|tell me what to fix)",
        # Text types that need interpretation
        r"\b(meeting notes?|contract|email|spec\b|requirements?\s*doc)",
        r"\b(error message|log message|stack trace)\b",
        # Instruction / command language
        r"\b(instruct\w*|command\w*|direct\w*|order\w*|requir\w*)\b",
        r"\b(interpret\w*|intent\w*|parse|extract\w*)\b",
        # Implementation / execution
        r"\b(implement\w*|execute|carry out|perform|build)\b",
        r"\b(requirement\w*|acceptance criteria|user stor\w*|task)\b",
        # Procedural
        r"(how (do|should|to)|guide|procedure)",
        # Obligation / duty language
        r"(obligat\w*|we'?re (supposed|required|obligated) to|must we|need to do)",
    ]

    def reason(self, query: str, context: Optional[Dict] = None) -> ReasoningOutput:
        return ReasoningOutput(
            engine=self.name,
            approach=(
                "Apply Mimamsa's hermeneutic method (the six lingas):\n"
                "1. Upakrama-upasamhara — what does the text begin and end with?\n"
                "   (Identify the framing intent.)\n"
                "2. Abhyasa — what is repeated or emphasized?\n"
                "   (Find the core directive.)\n"
                "3. Apurvata — what is novel or unique to this text?\n"
                "   (Identify non-obvious requirements.)\n"
                "4. Phala — what outcome/result is described?\n"
                "   (Define the success criteria.)\n"
                "5. Arthavada — what is explanatory vs. prescriptive?\n"
                "   (Separate rationale from instruction.)\n"
                "6. Yukti — what is logically consistent?\n"
                "   (Resolve ambiguities using reason.)"
            ),
            prompt_template=(
                "You are reasoning in the Mimamsa tradition — precise interpretation "
                "of text to extract actionable instructions.\n\n"
                f"QUERY: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. Identify the text, spec, or instructions to interpret.\n"
                "2. Extract explicit commands (vidhi — direct injunctions).\n"
                "3. Identify implicit requirements (not stated but necessary).\n"
                "4. Separate explanation/rationale from actionable directives.\n"
                "5. Produce a clear, ordered list of actions to take.\n"
                "6. Flag any ambiguities that need clarification."
            ),
            pramana_tags=[
                PramanaTag(
                    claim="Interpretation of instructions from the provided text.",
                    source=Pramana.SHABDA,
                    confidence=0.75,
                    note="Mimamsa's input is textual authority; interpretation is inferential.",
                )
            ],
            guna=Guna.SATTVA,
        )


class VaisheshikaEngine(DarshanaEngine):
    """
    Vaisheshika — The Engine of Atomic Analysis

    Vaisheshika (from 'vishesha', particularity) is the school of
    ontology and atomic analysis. It classifies all of reality into
    six padarthas (categories): dravya (substance), guna (quality),
    karma (action), samanya (universal), vishesha (particularity),
    and samavaya (inherence).

    In the Darshana Architecture, Vaisheshika handles tasks that
    require finding the irreducible components of a system — debugging,
    root cause analysis, type checking, and building ontologies.
    """

    name = "vaisheshika"
    description = "Atomic decomposition, irreducible components, type checking, ontology"

    trigger_patterns = [
        r"(what is (this|it) made of|composed of|consists? of)",
        r"\b(atom\w*|irreducib\w*|primitiv\w*|elementary)\b",
        r"\b(debug\w*|root cause|source of|origin of|where does)\b",
        r"\b(type|types?|kind|category|class of|ontolog\w*)\b",
        r"\b(smallest|minimal|simplest|basic|core unit)\b",
        r"\b(substance|propert\w*|qualit\w*|attribute\w*|inherent)\b",
        r"(by property|one by one|each (field|attribute|property|element))",
        r"\b(isolat\w*|pinpoint|narrow down|specific\w*|exact cause)\b",
        r"(look\w* wrong|what'?s wrong|find the (bug|issue|error|problem))",
    ]

    def reason(self, query: str, context: Optional[Dict] = None) -> ReasoningOutput:
        return ReasoningOutput(
            engine=self.name,
            approach=(
                "Apply Vaisheshika's padartha (category) analysis:\n"
                "1. Dravya (substance) — what are the irreducible entities?\n"
                "2. Guna (quality) — what properties does each entity have?\n"
                "3. Karma (action) — what does each entity DO?\n"
                "4. Samanya (universal) — what category does each belong to?\n"
                "5. Vishesha (particularity) — what makes each unique?\n"
                "6. Samavaya (inherence) — what connections are inseparable\n"
                "   (not accidental but definitional)?"
            ),
            prompt_template=(
                "You are reasoning in the Vaisheshika tradition — finding the "
                "irreducible atoms of the problem.\n\n"
                f"QUERY: {query}\n\n"
                "INSTRUCTIONS:\n"
                "1. Identify the system or concept to analyze.\n"
                "2. Decompose it to its smallest meaningful units (paramanu).\n"
                "3. For each unit, classify: what IS it (substance), what are "
                "its PROPERTIES (quality), what does it DO (action).\n"
                "4. Identify which properties are inherent (samavaya) vs. "
                "accidental (samyoga).\n"
                "5. Build a type hierarchy from the atomic units upward.\n"
                "6. If debugging: trace the issue to the specific atom that "
                "is behaving incorrectly."
            ),
            pramana_tags=[
                PramanaTag(
                    claim="Atomic decomposition based on analysis of the system's structure.",
                    source=Pramana.ANUMANA,
                    confidence=0.7,
                    note="Ontological analysis is inferential, grounded in observation.",
                )
            ],
            guna=Guna.SATTVA,
        )


# ---------------------------------------------------------------------------
# The Darshana Router — Buddhi Layer
# ---------------------------------------------------------------------------

class DarshanaRouter:
    """
    The Buddhi (discriminative intelligence) layer of the Darshana Architecture.

    In Samkhya philosophy, Buddhi is the first evolute of Prakriti — the
    faculty of discrimination and decision. It is fast, pre-reflective,
    and determines the broad category of a stimulus before deeper
    processing begins.

    The DarshanaRouter takes a query, classifies it using keyword patterns,
    determines the appropriate guna (processing mode), and routes it to
    one or more of the six darshana engines.

    Usage:
        router = DarshanaRouter()
        result = router.route("Is this argument valid?")
        # result.top_engines -> ["nyaya"]
        # result.guna -> Guna.SATTVA

        full = router.route_and_reason("Break down this system for me.")
        # full.reasoning -> [ReasoningOutput from samkhya engine]
    """

    def __init__(
        self,
        activation_threshold: float = 0.3,
        max_engines: int = 3,
        depth_mode: Optional[str] = None,
    ):
        """
        Args:
            activation_threshold: Minimum score for an engine to be activated.
                Engines below this are considered irrelevant to the query.
            max_engines: Maximum number of engines to activate simultaneously.
                Complex queries may trigger multiple darshanas. Default 3.
            depth_mode: Override depth mode. "deep" (max 2 engines, more tokens
                per engine) or "broad" (max 4 engines, less each). If None,
                the router selects automatically based on score distribution.
        """
        self.activation_threshold = activation_threshold
        self.max_engines = max_engines
        self.depth_mode_override = depth_mode

        self.engines: Dict[str, DarshanaEngine] = {
            "nyaya": NyayaEngine(),
            "samkhya": SamkhyaEngine(),
            "yoga": YogaEngine(),
            "vedanta": VedantaEngine(),
            "mimamsa": MimamsaEngine(),
            "vaisheshika": VaisheshikaEngine(),
        }

        self.guna_engine = GunaEngine()
        self.pramana_tagger = PramanaTagger()

    def _select_engines(
        self, sorted_engines: List[Tuple[str, float]]
    ) -> Tuple[List[str], str, str]:
        """
        Smart depth selection: pick engines based on score distribution.

        Returns (selected_engines, depth_mode, reasoning).

        Rules:
            1. Filter to engines above activation_threshold.
            2. If the top engine has >2x the score of the second, go deep
               (use only 1 engine).
            3. If scores are close (within 30% of each other), activate
               2-3 for multi-perspective analysis.
            4. Respect max_engines cap and depth_mode override.
        """
        # Filter candidates above threshold
        candidates = [
            (name, score)
            for name, score in sorted_engines
            if score >= self.activation_threshold
        ]

        # Fallback: if nothing above threshold, pick the engine with the
        # highest score. If ALL scores are 0 (no patterns matched at all),
        # default to mimamsa — it handles direct questions and text
        # interpretation without imposing heavy reasoning structure.
        if not candidates:
            top_name, top_score = sorted_engines[0] if sorted_engines else ("mimamsa", 0.0)
            if top_score == 0.0:
                top_name = "mimamsa"
            return (
                [top_name],
                "deep",
                f"No engine scored above threshold; defaulting to {top_name}.",
            )

        top_name, top_score = candidates[0]

        # Apply depth_mode override if set
        if self.depth_mode_override == "deep":
            effective_max = min(2, self.max_engines)
        elif self.depth_mode_override == "broad":
            effective_max = min(4, self.max_engines)
        else:
            effective_max = self.max_engines

        # Rule: if top engine dominates (>2x second), go deep with just 1
        if len(candidates) == 1:
            return (
                [top_name],
                "deep",
                f"Only {top_name} scored above threshold ({top_score:.3f}). Going deep.",
            )

        second_name, second_score = candidates[1]

        if top_score > 2 * second_score and second_score > 0:
            return (
                [top_name],
                "deep",
                f"{top_name} ({top_score:.3f}) dominates {second_name} ({second_score:.3f}) "
                f"by >2x. Going deep on single engine.",
            )

        # Rule: if scores are close (within 30%), activate multiple
        close_engines = [top_name]
        for name, score in candidates[1:]:
            if score >= top_score * 0.7:  # within 30% of the top
                close_engines.append(name)
            else:
                break

        selected = close_engines[:effective_max]

        if len(selected) == 1:
            depth = "deep"
            reasoning = f"Only {top_name} scored competitively ({top_score:.3f}). Going deep."
        elif len(selected) <= 2:
            depth = "deep"
            score_summary = ", ".join(
                f"{n}={s:.3f}" for n, s in candidates[: len(selected)]
            )
            reasoning = f"Close scores ({score_summary}). Deep multi-perspective analysis."
        else:
            depth = "broad"
            score_summary = ", ".join(
                f"{n}={s:.3f}" for n, s in candidates[: len(selected)]
            )
            reasoning = f"Multiple engines relevant ({score_summary}). Broad analysis."

        # Allow depth_mode override to force the mode
        if self.depth_mode_override in ("deep", "broad"):
            depth = self.depth_mode_override

        return selected, depth, reasoning

    def route(self, query: str) -> RoutingResult:
        """
        Classify a query and determine which engines should handle it.

        This is the core Buddhi operation: fast discrimination before
        expensive reasoning begins.

        Returns a RoutingResult with engine scores, the selected guna,
        the list of engines to activate, and a RoutingDecision with
        depth intelligence.
        """
        scores = {name: engine.score(query) for name, engine in self.engines.items()}
        guna = self.guna_engine.classify(query)

        sorted_engines = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected, depth_mode, reasoning = self._select_engines(sorted_engines)

        decision = RoutingDecision(
            selected_engines=selected,
            depth_mode=depth_mode,
            reasoning=reasoning,
        )

        return RoutingResult(
            query=query,
            engine_scores=scores,
            guna=guna,
            top_engines=selected,
            decision=decision,
        )

    def route_and_reason(
        self, query: str, context: Optional[Dict] = None
    ) -> DarshanaResult:
        """
        Full pipeline: classify, route, and generate reasoning output.

        This activates the top engine(s) and collects their structured
        reasoning output. In production, these outputs would be sent
        to an LLM for execution. The RoutingDecision's depth_mode
        informs how much compute each engine should receive.

        Args:
            query: The input query or problem.
            context: Optional dict of additional context (e.g., previous
                reasoning, user preferences, session state).

        Returns:
            A DarshanaResult containing the routing decision and
            reasoning output from each activated engine.
        """
        routing = self.route(query)
        reasoning_outputs = []

        # Use the decision's selected_engines (ordered by relevance)
        engines_to_use = (
            routing.decision.selected_engines
            if routing.decision
            else routing.top_engines
        )

        for engine_name in engines_to_use:
            engine = self.engines[engine_name]
            output = engine.reason(query, context)
            output.guna = routing.guna
            reasoning_outputs.append(output)

        return DarshanaResult(
            query=query,
            routing=routing,
            reasoning=reasoning_outputs,
        )

    def explain_routing(self, result: RoutingResult) -> str:
        """
        Produce a human-readable explanation of a routing decision.

        Useful for debugging and for demonstrating the system's
        self-awareness (Ahamkara layer).
        """
        lines = [
            f"Query: {result.query}",
            f"Guna (processing mode): {result.guna.value}",
            "",
            "Engine scores:",
        ]

        sorted_scores = sorted(
            result.engine_scores.items(), key=lambda x: x[1], reverse=True
        )
        for name, score in sorted_scores:
            marker = " <-- ACTIVATED" if name in result.top_engines else ""
            bar = "#" * int(score * 30)
            lines.append(f"  {name:<14} {score:.3f} {bar}{marker}")

        return "\n".join(lines)
