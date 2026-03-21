"""
Vritti Filter — Pre-Output Cognitive Classification
====================================================

Implementation of the Vritti Filter layer from the Darshana Architecture.

In Patanjali's Yoga Sutras (1.5-1.11), all mental activity (chitta-vritti) falls
into exactly five categories. This module applies that classification to AI-generated
text BEFORE it reaches the user, catching errors, empty language, and knowledge gaps
that would otherwise pass through unchecked.

The five vrittis:

    Pramana (प्रमाण)   — Valid cognition, grounded in evidence
    Viparyaya (विपर्यय) — Misconception, factual error or logical fallacy
    Vikalpa (विकल्प)    — Verbal delusion, sounds right but means nothing
    Nidra (निद्रा)      — Absence of knowledge, the system is guessing
    Smriti (स्मृति)     — Memory recall, regurgitated without fresh reasoning

Companion classes:

    MayaLayer   — Tracks representation gaps (model vs. reality)
    KarmaStore  — Runtime learning via the karma-samskara-vasana cycle

References:
    - Yoga Sutras of Patanjali, Pada I, Sutras 5-11
    - Nyaya Sutras, Chapter 1 (hetvabhasa / logical fallacies)
    - THESIS.md in this repository for the full Darshana Architecture

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Enums and data classes
# ---------------------------------------------------------------------------

class Vritti(Enum):
    """
    The five vrittis (mental modifications) from Yoga Sutra 1.5.

    yogash chitta-vritti-nirodhah — Yoga is the cessation of the
    fluctuations of the mind. Before cessation, we must first
    *classify* those fluctuations. That is what this module does.
    """

    PRAMANA = "pramana"
    """Valid cognition (YS 1.7): pratyaksha, anumana, agama."""

    VIPARYAYA = "viparyaya"
    """Misconception (YS 1.8): knowledge of a form that does not
    correspond to the thing itself."""

    VIKALPA = "vikalpa"
    """Verbal delusion (YS 1.9): knowledge based on words alone,
    with no corresponding reality."""

    NIDRA = "nidra"
    """Absence (YS 1.10): the mental modification that has
    absence / nothingness as its object."""

    SMRITI = "smriti"
    """Memory (YS 1.11): the recall of previously experienced
    objects, without fresh cognition."""


class Hetvabhasa(Enum):
    """
    The five logical fallacies (hetvabhasa) from Nyaya philosophy.

    Nyaya's contribution to Indian logic was formalising what makes
    a reasoning chain *invalid*. These map directly to failure modes
    in AI reasoning.
    """

    ASIDDHA = "asiddha"
    """Unproved premise — the hetu (reason) itself is not established.
    AI equivalent: citing a 'fact' that is fabricated."""

    VIRUDDHA = "viruddha"
    """Contradictory middle — the reason proves the opposite of the
    conclusion. AI equivalent: internal contradiction."""

    ANAIKANTIKA = "anaikantika"
    """Inconclusive — the reason is too broad, could prove anything.
    AI equivalent: vague reasoning that doesn't narrow to a conclusion."""

    SATPRATIPAKSHA = "satpratipaksha"
    """Counter-balanced — an equally strong reason exists for the
    opposite conclusion. AI equivalent: ignoring counter-evidence."""

    BADHITA = "badhita"
    """Contradicted by stronger evidence — the conclusion is overridden
    by a more authoritative source. AI equivalent: contradicting
    provided context or documents."""


@dataclass
class VrittiResult:
    """Result of classifying a piece of text."""

    vritti: Vritti
    confidence: float
    explanation: str
    fallacies: list[Hetvabhasa] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "vritti": self.vritti.value,
            "confidence": round(self.confidence, 3),
            "explanation": self.explanation,
            "fallacies": [f.value for f in self.fallacies],
            "suggestions": self.suggestions,
        }


@dataclass
class ClaimResult:
    """Result of classifying a single extracted claim."""

    claim: str
    vritti: Vritti
    confidence: float
    explanation: str
    fallacies: list[Hetvabhasa] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "claim": self.claim,
            "vritti": self.vritti.value,
            "confidence": round(self.confidence, 3),
            "explanation": self.explanation,
            "fallacies": [f.value for f in self.fallacies],
        }


@dataclass
class MayaGap:
    """A representation gap detected by the Maya Layer."""

    gap_type: str
    description: str
    severity: float  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "gap_type": self.gap_type,
            "description": self.description,
            "severity": round(self.severity, 3),
        }


@dataclass
class Samskara:
    """
    An impression left by an action — the building block of vasanas.

    karma (action) → samskara (impression) → vasana (tendency)

    Each samskara records what was done, what happened, and when.
    Over time, samskaras in the same domain accumulate into vasanas.
    """

    action: str
    outcome: str
    domain: str
    timestamp: float = field(default_factory=time.time)
    weight: float = 1.0


# ---------------------------------------------------------------------------
# Pattern libraries (the heuristic core of the POC)
# ---------------------------------------------------------------------------

# Indicators of VIKALPA (verbal delusion / empty language)
VIKALPA_PATTERNS: list[tuple[str, str]] = [
    (r"\b(essentially|basically|fundamentally)\b.*\b(is|are|means)\b.*\b(essentially|basically|fundamentally)\b",
     "circular definition — the explanation uses the same hedging as the claim"),
    (r"\b(it is what it is|at the end of the day|when all is said and done)\b",
     "cliche substituting for analysis"),
    (r"\b(very|extremely|incredibly|absolutely)\s+(unique|important|critical|essential)\b",
     "intensifier-stacking without substance"),
    (r"\b(some|certain|various)\s+(experts?|researchers?|studies|people|sources)\s+(say|suggest|believe|think|argue|claim)\b",
     "unattributed appeal to anonymous authority"),
    (r"\b(could|might|may)\s+(potentially|possibly|perhaps)\b",
     "double hedging — epistemic uncertainty stacked on uncertainty"),
    (r"\bin\s+a\s+sense\b|\bin\s+some\s+ways?\b|\bto\s+some\s+extent\b",
     "qualifier that drains the claim of falsifiable content"),
    (r"(?:^|\.\s+)(?:It|This|That) (?:is|has been|remains) (?:widely |generally |broadly )?(?:known|accepted|recognized|understood|acknowledged)",
     "appeal to common knowledge without citation"),
]

# Indicators of NIDRA (absence of real knowledge)
NIDRA_PATTERNS: list[tuple[str, str]] = [
    (r"\b(I'm not sure|I don't have|I cannot confirm|I'm unable to verify)\b",
     "explicit uncertainty admission"),
    (r"\b(generally|typically|usually|often|sometimes|in many cases)\b",
     "frequency hedging suggesting no specific knowledge"),
    (r"\b(it depends|there are many factors|context matters|varies)\b",
     "deflection to context without providing substance"),
    (r"\b(there is no simple answer|it's complicated|it's nuanced)\b",
     "complexity shield avoiding a direct answer"),
]

# Indicators of SMRITI (pure memory recall, encyclopedic tone)
SMRITI_PATTERNS: list[tuple[str, str]] = [
    (r"(?:was|is|were)\s+(?:a|an|the)\s+\w+\s+(?:who|which|that)\s+",
     "encyclopedic 'X was a Y who Z' biographical pattern"),
    (r"\b(?:born|founded|established|invented|discovered|published)\s+(?:in|on|at)\s+\d{4}\b",
     "date-anchored factual claim typical of memorised knowledge"),
    (r"\b(?:is defined as|refers to|is the process of|is a type of)\b",
     "textbook definition pattern"),
    (r"\b(?:According to|As stated by|As defined by)\s+[A-Z]",
     "attributed factual recall"),
]

# Indicators of VIPARYAYA (misconception / logical error)
VIPARYAYA_PATTERNS: list[tuple[str, str]] = [
    (r"\b(always|never|all|none|every|no one)\b",
     "absolute quantifier — potential overgeneralisation (anaikantika)"),
    (r"\b(therefore|thus|hence|so)\b.*\b(because|since|as)\b",
     "circular reasoning — conclusion embedded in the premise (viruddha)"),
    (r"\b(proves?|proof)\s+that\b",
     "proof claim — requires strong validation"),
]

# Positive indicators of PRAMANA (valid cognition)
PRAMANA_INDICATORS: list[tuple[str, str]] = [
    (r"(?:https?://|doi:|arxiv:)\S+",
     "contains a citation or URL (shabda pramana with source)"),
    (r"\b(because|since|given that)\b.*\b(therefore|thus|we can conclude)\b",
     "explicit logical chain from premise to conclusion (anumana)"),
    (r"\b(data shows|evidence suggests|measurements indicate|results demonstrate)\b",
     "grounded in empirical evidence (pratyaksha)"),
    (r"\b(for example|for instance|such as|e\.g\.|specifically)\b",
     "provides specific examples, not just generalities"),
    (r"\b(step \d|first|second|third|finally)\b.*\b(step \d|first|second|third|finally)\b",
     "structured reasoning with explicit steps"),
]


# ---------------------------------------------------------------------------
# VrittiFilter — the core classifier
# ---------------------------------------------------------------------------

class VrittiFilter:
    """
    Pre-output cognitive classification filter.

    Sits at the end of the reasoning pipeline and classifies the system's
    own output into the five vritti categories before it reaches the user.
    This is the Yoga layer of the Darshana Architecture — not attention
    management during processing, but quality control before release.

    Usage::

        vf = VrittiFilter()
        result = vf.classify("The Earth is flat because it looks flat.")
        print(result.vritti)        # Vritti.VIPARYAYA
        print(result.explanation)   # explanation of the error

        filtered = vf.filter("Some experts say things are complex.")
        print(filtered)             # text with vikalpa warning prepended

    Philosophical basis:
        Yoga Sutra 1.5: vrittayah panchatayyah klishtaklishtah
        "The vrittis are fivefold, painful and not painful."
    """

    def __init__(self) -> None:
        self._compiled_vikalpa = [(re.compile(p, re.IGNORECASE), d) for p, d in VIKALPA_PATTERNS]
        self._compiled_nidra = [(re.compile(p, re.IGNORECASE), d) for p, d in NIDRA_PATTERNS]
        self._compiled_smriti = [(re.compile(p, re.IGNORECASE), d) for p, d in SMRITI_PATTERNS]
        self._compiled_viparyaya = [(re.compile(p, re.IGNORECASE), d) for p, d in VIPARYAYA_PATTERNS]
        self._compiled_pramana = [(re.compile(p, re.IGNORECASE), d) for p, d in PRAMANA_INDICATORS]

    # ---- public API -------------------------------------------------------

    def classify(self, text: str, context: Optional[str] = None) -> VrittiResult:
        """
        Classify a text into one of the five vritti categories.

        Args:
            text: The system-generated text to classify.
            context: Optional grounding context (user query, source docs).
                     Used to detect contradictions (badhita hetvabhasa).

        Returns:
            VrittiResult with the classification, confidence, and explanation.

        The classification logic uses a weighted scoring approach:
        each pattern match adds evidence for a particular vritti.
        The vritti with the strongest cumulative signal wins.
        Context comparison, when available, adds higher-weight signals.
        """
        scores: dict[Vritti, float] = {v: 0.0 for v in Vritti}
        evidence: dict[Vritti, list[str]] = {v: [] for v in Vritti}
        fallacies: list[Hetvabhasa] = []

        # --- Pattern-based scoring ---

        for pattern, desc in self._compiled_vikalpa:
            if pattern.search(text):
                scores[Vritti.VIKALPA] += 1.0
                evidence[Vritti.VIKALPA].append(desc)

        for pattern, desc in self._compiled_nidra:
            if pattern.search(text):
                scores[Vritti.NIDRA] += 1.0
                evidence[Vritti.NIDRA].append(desc)

        for pattern, desc in self._compiled_smriti:
            if pattern.search(text):
                scores[Vritti.SMRITI] += 1.0
                evidence[Vritti.SMRITI].append(desc)

        for pattern, desc in self._compiled_viparyaya:
            if pattern.search(text):
                scores[Vritti.VIPARYAYA] += 0.8
                evidence[Vritti.VIPARYAYA].append(desc)

        for pattern, desc in self._compiled_pramana:
            if pattern.search(text):
                scores[Vritti.PRAMANA] += 1.0
                evidence[Vritti.PRAMANA].append(desc)

        # --- Structural analysis ---

        # Specificity check: specific nouns/numbers suggest grounding
        specific_numbers = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))
        proper_nouns = len(re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", text))
        word_count = len(text.split())

        if word_count > 0:
            specificity = (specific_numbers + proper_nouns * 0.5) / word_count
            if specificity > 0.05:
                scores[Vritti.PRAMANA] += specificity * 10
                evidence[Vritti.PRAMANA].append(
                    f"text has high specificity ({specific_numbers} numbers, "
                    f"{proper_nouns} proper nouns in {word_count} words)"
                )
            elif specificity < 0.01 and word_count > 20:
                scores[Vritti.VIKALPA] += 0.5
                evidence[Vritti.VIKALPA].append(
                    "low specificity — few concrete details in a long passage"
                )

        # Sentence diversity: repeated structure suggests memorised content
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) >= 3:
            starts = [s.split()[0].lower() if s.split() else "" for s in sentences]
            unique_ratio = len(set(starts)) / len(starts)
            if unique_ratio < 0.4:
                scores[Vritti.SMRITI] += 0.7
                evidence[Vritti.SMRITI].append(
                    "repetitive sentence structure suggests rote recall"
                )

        # --- Hetvabhasa detection ---
        fallacies.extend(self._detect_fallacies(text, context))
        if fallacies:
            scores[Vritti.VIPARYAYA] += len(fallacies) * 1.5
            for f in fallacies:
                evidence[Vritti.VIPARYAYA].append(f"logical fallacy: {f.value}")

        # --- Context-based checks (highest weight) ---
        if context:
            contradiction_score = self._check_context_contradiction(text, context)
            if contradiction_score > 0:
                scores[Vritti.VIPARYAYA] += contradiction_score * 3.0
                evidence[Vritti.VIPARYAYA].append(
                    "text appears to contradict the provided context (badhita)"
                )
                if Hetvabhasa.BADHITA not in fallacies:
                    fallacies.append(Hetvabhasa.BADHITA)

        # --- Determine winner ---
        # Default to pramana with low confidence if nothing fires
        if all(s == 0.0 for s in scores.values()):
            scores[Vritti.PRAMANA] = 0.3

        winner = max(scores, key=scores.get)  # type: ignore[arg-type]
        total = sum(scores.values()) or 1.0
        confidence = scores[winner] / total

        explanation = self._build_explanation(winner, evidence[winner])

        return VrittiResult(
            vritti=winner,
            confidence=min(confidence, 1.0),
            explanation=explanation,
            fallacies=fallacies,
            suggestions=self._suggest_improvements(winner, evidence[winner]),
        )

    def filter(self, text: str, context: Optional[str] = None) -> str:
        """
        Classify and transform the text based on its vritti type.

        This is the main output gate. Depending on classification:

        - **Pramana**: pass through with confidence annotation.
        - **Viparyaya**: prepend a correction warning, suggest fixes.
        - **Vikalpa**: prepend a "sounds right but ungrounded" warning.
        - **Nidra**: replace with an honest "I don't know" response.
        - **Smriti**: flag as recalled knowledge with a date caveat.

        Args:
            text: The system-generated text to filter.
            context: Optional grounding context.

        Returns:
            The text, potentially modified or replaced.
        """
        result = self.classify(text, context)

        if result.vritti == Vritti.PRAMANA:
            if result.confidence > 0.7:
                return text
            return f"[Confidence: {result.confidence:.0%}] {text}"

        elif result.vritti == Vritti.VIPARYAYA:
            warning = (
                f"[VRITTI FILTER — VIPARYAYA DETECTED]\n"
                f"Potential misconception identified: {result.explanation}\n"
            )
            if result.fallacies:
                fallacy_names = ", ".join(f.value for f in result.fallacies)
                warning += f"Logical fallacies (hetvabhasa): {fallacy_names}\n"
            if result.suggestions:
                warning += "Suggestions:\n"
                for s in result.suggestions:
                    warning += f"  - {s}\n"
            warning += f"---\n{text}"
            return warning

        elif result.vritti == Vritti.VIKALPA:
            return (
                f"[VRITTI FILTER — VIKALPA WARNING]\n"
                f"This response may sound plausible but lacks grounded content.\n"
                f"Issue: {result.explanation}\n"
                f"---\n{text}"
            )

        elif result.vritti == Vritti.NIDRA:
            return (
                f"I don't have reliable knowledge about this topic.\n"
                f"(Nidra detected: {result.explanation})\n"
                f"Rather than generating a potentially unreliable response, "
                f"I'm being transparent about this gap."
            )

        elif result.vritti == Vritti.SMRITI:
            return (
                f"[VRITTI FILTER — SMRITI FLAG]\n"
                f"This appears to be recalled from training data rather than "
                f"freshly reasoned. {result.explanation}\n"
                f"Caveat: this information may be outdated or lack nuance "
                f"that fresh reasoning would provide.\n"
                f"---\n{text}"
            )

        return text  # fallback

    def classify_claims(self, text: str) -> list[ClaimResult]:
        """
        Split text into individual claims and classify each one.

        This provides granular analysis — a single paragraph might contain
        one valid claim (pramana), one unsupported claim (vikalpa), and one
        recalled fact (smriti). Treating the whole paragraph as one vritti
        would lose this nuance.

        Args:
            text: The text to decompose and classify.

        Returns:
            A list of ClaimResult objects, one per extracted claim.
        """
        claims = self._extract_claims(text)
        results = []
        for claim in claims:
            r = self.classify(claim)
            results.append(ClaimResult(
                claim=claim,
                vritti=r.vritti,
                confidence=r.confidence,
                explanation=r.explanation,
                fallacies=r.fallacies,
            ))
        return results

    # ---- private helpers --------------------------------------------------

    def _detect_fallacies(self, text: str, context: Optional[str] = None) -> list[Hetvabhasa]:
        """
        Detect Nyaya's five hetvabhasas (logical fallacies) in text.

        This is a heuristic implementation. A production system would use
        a proper logical parser, but pattern matching catches the common cases.
        """
        fallacies = []
        text_lower = text.lower()

        # ASIDDHA: unproved premise — citing facts without any support
        if re.search(r"\b(studies show|research proves?|science says|experts agree)\b", text_lower):
            if not re.search(r"(?:https?://|doi:|\(\d{4}\)|\[\d+\])", text):
                fallacies.append(Hetvabhasa.ASIDDHA)

        # VIRUDDHA: contradictory middle — text contradicts itself
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10]
        for i, s1 in enumerate(sentences):
            for s2 in sentences[i + 1:]:
                if self._sentences_contradict(s1, s2):
                    fallacies.append(Hetvabhasa.VIRUDDHA)
                    break
            if Hetvabhasa.VIRUDDHA in fallacies:
                break

        # ANAIKANTIKA: inconclusive — reason is too broad
        if re.search(r"\b(everything|anything|all things)\s+(is|are|can be|could be)\b", text_lower):
            fallacies.append(Hetvabhasa.ANAIKANTIKA)

        # SATPRATIPAKSHA: ignoring counter-evidence
        if re.search(r"\b(on the other hand|however|but|conversely|although)\b", text_lower):
            # This is actually GOOD — acknowledging counter-evidence
            pass
        elif re.search(r"\b(clearly|obviously|undeniably|undoubtedly)\b", text_lower):
            # Asserting certainty without addressing counter-arguments
            if len(sentences) > 2:
                fallacies.append(Hetvabhasa.SATPRATIPAKSHA)

        # BADHITA: contradicted by provided context
        if context and self._check_context_contradiction(text, context) > 0.5:
            fallacies.append(Hetvabhasa.BADHITA)

        return fallacies

    def _check_context_contradiction(self, text: str, context: str) -> float:
        """
        Check whether the text contradicts the provided context.

        Uses multiple heuristics:
        1. Negation mismatch — context negates X, text affirms X (or vice versa)
        2. Numerical mismatch — same entity with different numbers
        3. Negated-topic violation — context says "not X", text recommends X

        Returns a score from 0.0 (no contradiction) to 1.0 (strong contradiction).
        """
        text_lower = text.lower()
        context_lower = context.lower()
        text_words = set(re.findall(r"\b\w{4,}\b", text_lower))
        context_words = set(re.findall(r"\b\w{4,}\b", context_lower))
        score = 0.0

        # --- 1. Negated-topic violation ---
        # Find things the context explicitly negates/rejects, then check
        # if the text affirms or recommends those same things.
        negation_scopes = re.findall(
            r"(?:not|don't|doesn't|does not|do not|no|never|without|"
            r"can't|cannot|won't|will not|didn't|did not)\s+"
            r"(?:want|use|need|like|include|have|allow|support|require|recommend)?\s*"
            r"(?:any\s+)?(\w[\w\s]{2,30}?)(?:\.|,|$)",
            context_lower,
        )
        for negated_topic in negation_scopes:
            negated_words = set(negated_topic.strip().split())
            # Check if text affirms/uses/recommends any of these words
            for word in negated_words:
                if len(word) >= 4 and word in text_words:
                    score = max(score, 0.8)

        # --- 2. Numerical mismatch ---
        # Extract "N entity" patterns from both and compare
        text_numbers = re.findall(
            r"(?:\$|USD\s?)?([\d,]+(?:\.\d+)?)\s*(%|dollars?|developers?|"
            r"people|team|members?|budget|engineers?|designers?|months?|weeks?|days?|hours?)",
            text_lower,
        )
        context_numbers = re.findall(
            r"(?:\$|USD\s?)?([\d,]+(?:\.\d+)?)\s*(%|dollars?|developers?|"
            r"people|team|members?|budget|engineers?|designers?|months?|weeks?|days?|hours?)",
            context_lower,
        )
        # Also catch "$N" patterns
        text_dollars = re.findall(r"\$([\d,]+(?:\.\d+)?)", text_lower)
        context_dollars = re.findall(r"\$([\d,]+(?:\.\d+)?)", context_lower)

        if text_dollars and context_dollars:
            text_vals = {float(v.replace(",", "")) for v in text_dollars}
            ctx_vals = {float(v.replace(",", "")) for v in context_dollars}
            if text_vals and ctx_vals and not text_vals & ctx_vals:
                # Different dollar amounts — likely contradiction
                score = max(score, 0.7)

        for t_num, t_unit in text_numbers:
            for c_num, c_unit in context_numbers:
                # Same unit, different number
                if t_unit == c_unit and t_num != c_num:
                    score = max(score, 0.6)

        # --- 3. Direct negation mismatch ---
        negation_patterns = [
            r"\bnot\s+\w+", r"\bnever\s+\w+", r"\bno\s+\w+",
            r"\bwithout\s+\w+", r"\bdoes(?:n't| not)\b",
            r"\bis(?:n't| not)\b", r"\bwas(?:n't| not)\b",
            r"\bcannot\b", r"\bcan't\b",
        ]
        shared = text_words & context_words
        if shared:
            text_negations = set()
            context_negations = set()
            for pattern in negation_patterns:
                text_negations.update(re.findall(pattern, text_lower))
                context_negations.update(re.findall(pattern, context_lower))

            if text_negations and not context_negations:
                for neg in text_negations:
                    if set(neg.split()) & shared:
                        score = max(score, 0.7)
            elif context_negations and not text_negations:
                for neg in context_negations:
                    if set(neg.split()) & shared:
                        score = max(score, 0.7)

        return score

    def _sentences_contradict(self, s1: str, s2: str) -> bool:
        """Heuristic check for two sentences contradicting each other."""
        s1_lower, s2_lower = s1.lower(), s2.lower()

        # Direct negation of the same subject
        negation_pairs = [
            (r"\bis\b", r"\bis not\b"),
            (r"\bis\b", r"\bisn't\b"),
            (r"\bcan\b", r"\bcannot\b"),
            (r"\bcan\b", r"\bcan't\b"),
            (r"\bwill\b", r"\bwill not\b"),
            (r"\bwill\b", r"\bwon't\b"),
            (r"\balways\b", r"\bnever\b"),
            (r"\ball\b", r"\bnone\b"),
            (r"\beveryone\b", r"\bno one\b"),
        ]
        for pos, neg in negation_pairs:
            if (re.search(pos, s1_lower) and re.search(neg, s2_lower)) or \
               (re.search(neg, s1_lower) and re.search(pos, s2_lower)):
                # Check they share a subject
                s1_words = set(re.findall(r"\b\w{4,}\b", s1_lower))
                s2_words = set(re.findall(r"\b\w{4,}\b", s2_lower))
                if len(s1_words & s2_words) >= 2:
                    return True
        return False

    def _extract_claims(self, text: str) -> list[str]:
        """
        Extract individual claims from a text.

        A claim is roughly one assertive sentence. We split on sentence
        boundaries and filter out questions, fragments, and connectives.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        claims = []
        for s in sentences:
            s = s.strip()
            if len(s) < 10:
                continue
            if s.endswith("?"):
                continue
            # Skip pure connective phrases
            if re.match(r"^(However|Moreover|Furthermore|In addition|Also|That said),?\s*$",
                        s, re.IGNORECASE):
                continue
            claims.append(s)
        return claims

    def _build_explanation(self, vritti: Vritti, evidence: list[str]) -> str:
        """Build a human-readable explanation from the classification evidence."""
        preambles = {
            Vritti.PRAMANA: "This text shows signs of valid, grounded cognition",
            Vritti.VIPARYAYA: "This text contains potential misconceptions or logical errors",
            Vritti.VIKALPA: "This text sounds plausible but lacks grounded content",
            Vritti.NIDRA: "This text shows signs of absent or uncertain knowledge",
            Vritti.SMRITI: "This text appears to be recalled from memory rather than reasoned",
        }
        explanation = preambles[vritti]
        if evidence:
            explanation += ": " + "; ".join(evidence[:3])
            if len(evidence) > 3:
                explanation += f" (+{len(evidence) - 3} more signals)"
        else:
            explanation += " (low-confidence classification based on absence of other signals)"
        return explanation

    def _suggest_improvements(self, vritti: Vritti, evidence: list[str]) -> list[str]:
        """Suggest improvements based on the vritti classification."""
        suggestions: dict[Vritti, list[str]] = {
            Vritti.PRAMANA: [],
            Vritti.VIPARYAYA: [
                "Verify factual claims against the provided context",
                "Check logical chain for circular reasoning or unsupported leaps",
                "Consider whether absolute statements should be qualified",
            ],
            Vritti.VIKALPA: [
                "Add specific examples, data, or citations",
                "Replace hedging language with concrete claims",
                "Ask: could this sentence apply to anything? If yes, it says nothing",
            ],
            Vritti.NIDRA: [
                "Acknowledge the knowledge gap explicitly",
                "Suggest where the user might find reliable information",
                "Avoid filling the gap with plausible-sounding generation",
            ],
            Vritti.SMRITI: [
                "Add a date caveat — this information may be outdated",
                "Show the reasoning chain, not just the recalled conclusion",
                "Cross-reference with provided context if available",
            ],
        }
        return suggestions.get(vritti, [])


# ---------------------------------------------------------------------------
# MayaLayer — Representation gap tracker
# ---------------------------------------------------------------------------

class MayaLayer:
    """
    Tracks the gap between the model's representation and reality.

    In Vedanta, Maya is not "illusion" in the Western sense — it is the
    gap between appearance and reality. The map is not the territory.
    A model's training data is not the world. This layer makes that gap
    explicit and trackable.

    From the Darshana Architecture (THESIS.md):
        "My data is from [date]. Reality may differ."
        "I'm reasoning about code, not executing it."
        "User's words != user's intent."
        Epistemic humility as architecture, not as safety fine-tune.

    Usage::

        maya = MayaLayer(knowledge_cutoff="2025-04")
        gap = maya.check_recency("The current president of X is Y")
        gaps = maya.report()
    """

    def __init__(self, knowledge_cutoff: Optional[str] = None) -> None:
        """
        Args:
            knowledge_cutoff: Date string (YYYY-MM) for the model's training
                              data cutoff. Used for recency checks.
        """
        self.knowledge_cutoff = knowledge_cutoff
        self._gaps: list[MayaGap] = []

    def check_recency(self, claim: str) -> Optional[MayaGap]:
        """
        Flag if a claim might be outdated.

        Checks for temporal markers (dates, "current", "now", "recently")
        that suggest the claim depends on up-to-date information.

        Args:
            claim: A single claim to check for recency issues.

        Returns:
            A MayaGap if a recency issue is detected, else None.
        """
        temporal_markers = [
            (r"\b(currently|now|today|at present|as of)\b",
             "claim uses present-tense temporal marker", 0.7),
            (r"\b(recent|recently|latest|newest|just|new)\b",
             "claim references recency", 0.8),
            (r"\b(20[2-9]\d)\b",
             "claim references a specific recent year", 0.6),
            (r"\b(this year|this month|this week)\b",
             "claim references the current time period", 0.9),
            (r"\b(president|CEO|leader|head of|prime minister|chairman)\b",
             "claim references a position that changes over time", 0.6),
            (r"\b(price|cost|rate|salary|worth|valued at)\b",
             "claim references a value that fluctuates", 0.5),
        ]

        for pattern, desc, severity in temporal_markers:
            if re.search(pattern, claim, re.IGNORECASE):
                cutoff_note = ""
                if self.knowledge_cutoff:
                    cutoff_note = f" (model knowledge cutoff: {self.knowledge_cutoff})"
                gap = MayaGap(
                    gap_type="recency",
                    description=f"{desc}{cutoff_note}",
                    severity=severity,
                )
                self._gaps.append(gap)
                return gap
        return None

    def check_grounding(self, claim: str, evidence: str) -> Optional[MayaGap]:
        """
        Check if a claim is supported by provided evidence.

        This is the most important Maya check — it catches cases where
        the model says something that the user's own documents contradict.

        Args:
            claim: The claim to verify.
            evidence: The source text / context to verify against.

        Returns:
            A MayaGap if the claim appears ungrounded, else None.
        """
        claim_keywords = set(re.findall(r"\b\w{4,}\b", claim.lower()))
        evidence_keywords = set(re.findall(r"\b\w{4,}\b", evidence.lower()))

        if not claim_keywords:
            return None

        overlap = claim_keywords & evidence_keywords
        coverage = len(overlap) / len(claim_keywords) if claim_keywords else 0

        if coverage < 0.2:
            gap = MayaGap(
                gap_type="grounding",
                description=(
                    f"Claim has low keyword overlap with evidence "
                    f"({coverage:.0%} coverage). The claim may not be "
                    f"supported by the provided context."
                ),
                severity=min(1.0, 1.0 - coverage),
            )
            self._gaps.append(gap)
            return gap
        return None

    def check_intent_gap(
        self, user_input: str, system_interpretation: str
    ) -> Optional[MayaGap]:
        """
        Flag potential misunderstanding between user intent and system interpretation.

        "User's words != user's intent." — the system might parse the words
        correctly but miss the actual question behind them.

        Args:
            user_input: What the user actually said.
            system_interpretation: How the system understood the query.

        Returns:
            A MayaGap if a potential misunderstanding is detected, else None.
        """
        user_words = set(re.findall(r"\b\w{3,}\b", user_input.lower()))
        interp_words = set(re.findall(r"\b\w{3,}\b", system_interpretation.lower()))

        if not user_words:
            return None

        # Check if the interpretation introduces many words not in the input
        novel_words = interp_words - user_words
        novel_ratio = len(novel_words) / len(interp_words) if interp_words else 0

        # Check if key user words are missing from interpretation
        lost_words = user_words - interp_words
        lost_ratio = len(lost_words) / len(user_words) if user_words else 0

        severity = 0.0
        issues = []

        if novel_ratio > 0.6:
            severity = max(severity, 0.6)
            issues.append(
                f"interpretation introduces {len(novel_words)} concepts "
                f"not present in user input"
            )

        if lost_ratio > 0.5:
            severity = max(severity, 0.7)
            issues.append(
                f"interpretation drops {len(lost_words)} words from "
                f"user input — possible topic drift"
            )

        # Check for question type mismatch
        user_is_question = "?" in user_input
        interp_is_question = "?" in system_interpretation
        if user_is_question and not interp_is_question:
            severity = max(severity, 0.4)
            issues.append("user asked a question but interpretation is declarative")

        if severity > 0.3:
            gap = MayaGap(
                gap_type="intent",
                description="; ".join(issues),
                severity=severity,
            )
            self._gaps.append(gap)
            return gap
        return None

    def report(self) -> list[MayaGap]:
        """
        Return all representation gaps detected so far.

        Returns:
            List of MayaGap objects, sorted by severity (highest first).
        """
        return sorted(self._gaps, key=lambda g: g.severity, reverse=True)

    def clear(self) -> None:
        """Clear all tracked gaps."""
        self._gaps.clear()


# ---------------------------------------------------------------------------
# KarmaStore — Runtime learning via samskara accumulation
# ---------------------------------------------------------------------------

class KarmaStore:
    """
    Runtime learning through the karma-samskara-vasana cycle.

    From the Darshana Architecture:
        Actions (karma) -> Impressions (samskara) -> Tendencies (vasana)

    This is lighter than fine-tuning but heavier than zero-shot. The system
    accumulates impressions from interactions and develops tendencies that
    influence future behaviour — without retraining.

    The store persists to a JSON file so tendencies survive across sessions.

    Usage::

        ks = KarmaStore("/tmp/karma.json")
        ks.record_action(
            action="used formal tone for technical query",
            outcome="user responded positively",
            domain="communication_style"
        )
        tendencies = ks.get_vasanas("communication_style")
        # -> [{"tendency": "formal tone works for technical queries", ...}]

    Philosophical basis:
        Bhagavad Gita 18.60: svabhava-jena kaunteya nibaddhah svena karmana
        "Bound by your own nature-born karma, O Kaunteya..."

        But also BG 4.37: jnanagnih sarva-karmani bhasma-sat kurute
        "The fire of knowledge burns all karma to ashes."
        Hence burn_vasanas() — outdated biases can be cleared.
    """

    def __init__(self, store_path: Optional[str] = None) -> None:
        """
        Args:
            store_path: Path to JSON file for persistence.
                        If None, operates in memory only.
        """
        self.store_path = Path(store_path) if store_path else None
        self._samskaras: list[dict] = []
        self._load()

    def record_action(
        self,
        action: str,
        outcome: str,
        domain: str = "general",
        weight: float = 1.0,
    ) -> Samskara:
        """
        Record an action and its outcome as a samskara (impression).

        Each action-outcome pair leaves an impression. Over time, impressions
        in the same domain accumulate into vasanas (tendencies) that can
        guide future decisions.

        Args:
            action: What the system did.
            outcome: What happened as a result (user feedback, success/failure).
            domain: Category for grouping related samskaras.
            weight: Importance multiplier (default 1.0).

        Returns:
            The created Samskara object.
        """
        samskara = Samskara(
            action=action,
            outcome=outcome,
            domain=domain,
            weight=weight,
        )
        self._samskaras.append(asdict(samskara))
        self._save()
        return samskara

    def get_vasanas(self, domain: str) -> list[dict]:
        """
        Get accumulated tendencies for a domain.

        Vasanas are derived from samskaras by grouping similar outcomes
        and computing a net tendency. Positive outcomes reinforce the
        associated action; negative outcomes weaken it.

        Args:
            domain: The domain to query.

        Returns:
            List of vasana dicts with keys: tendency, strength, action_count, domain.
        """
        domain_samskaras = [
            s for s in self._samskaras if s.get("domain") == domain
        ]
        if not domain_samskaras:
            return []

        # Group by action pattern and compute net tendency
        action_outcomes: dict[str, list[dict]] = {}
        for s in domain_samskaras:
            action = s["action"]
            action_outcomes.setdefault(action, []).append(s)

        vasanas = []
        for action, records in action_outcomes.items():
            positive = sum(
                r["weight"] for r in records
                if self._is_positive_outcome(r["outcome"])
            )
            negative = sum(
                r["weight"] for r in records
                if not self._is_positive_outcome(r["outcome"])
            )
            net = positive - negative
            strength = net / (positive + negative) if (positive + negative) > 0 else 0

            vasanas.append({
                "tendency": action,
                "strength": round(strength, 3),
                "action_count": len(records),
                "domain": domain,
                "net_karma": round(net, 3),
            })

        # Sort by absolute strength
        vasanas.sort(key=lambda v: abs(v["strength"]), reverse=True)
        return vasanas

    def get_all_domains(self) -> list[str]:
        """Return all domains that have recorded samskaras."""
        return sorted(set(s.get("domain", "general") for s in self._samskaras))

    def burn_vasanas(self, domain: Optional[str] = None) -> int:
        """
        Clear outdated biases — the jnana-agni (fire of knowledge).

        Bhagavad Gita 4.37: "As a blazing fire turns firewood to ashes,
        O Arjuna, so does the fire of knowledge burn to ashes all karma."

        In practice: remove samskaras that are old enough to be stale,
        or clear an entire domain when it's known to be outdated.

        Args:
            domain: If provided, burn only samskaras in this domain.
                    If None, burn all samskaras older than 30 days.

        Returns:
            Number of samskaras burned.
        """
        cutoff = time.time() - (30 * 24 * 3600)  # 30 days
        original_count = len(self._samskaras)

        if domain:
            self._samskaras = [
                s for s in self._samskaras
                if s.get("domain") != domain
            ]
        else:
            self._samskaras = [
                s for s in self._samskaras
                if s.get("timestamp", 0) > cutoff
            ]

        burned = original_count - len(self._samskaras)
        if burned > 0:
            self._save()
        return burned

    def summary(self) -> dict:
        """
        Return a summary of the karma store's state.

        Returns:
            Dict with total samskaras, domains, and vasana counts.
        """
        domains = self.get_all_domains()
        return {
            "total_samskaras": len(self._samskaras),
            "domains": domains,
            "vasanas_per_domain": {
                d: len(self.get_vasanas(d)) for d in domains
            },
        }

    # ---- private helpers --------------------------------------------------

    def _is_positive_outcome(self, outcome: str) -> bool:
        """Simple heuristic: classify an outcome as positive or negative."""
        positive_markers = [
            "positive", "success", "good", "helpful", "correct", "accepted",
            "worked", "resolved", "satisfied", "accurate", "liked", "approved",
        ]
        negative_markers = [
            "negative", "failure", "bad", "unhelpful", "incorrect", "rejected",
            "failed", "error", "unsatisfied", "inaccurate", "disliked", "wrong",
        ]
        outcome_lower = outcome.lower()
        pos_score = sum(1 for m in positive_markers if m in outcome_lower)
        neg_score = sum(1 for m in negative_markers if m in outcome_lower)
        return pos_score >= neg_score

    def _load(self) -> None:
        """Load samskaras from the JSON file."""
        if self.store_path and self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text())
                self._samskaras = data.get("samskaras", [])
            except (json.JSONDecodeError, KeyError):
                self._samskaras = []

    def _save(self) -> None:
        """Save samskaras to the JSON file."""
        if self.store_path:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            self.store_path.write_text(json.dumps(
                {"samskaras": self._samskaras},
                indent=2,
                default=str,
            ))
