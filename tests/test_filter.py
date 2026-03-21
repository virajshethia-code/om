"""
test_filter.py — Tests for the Vritti Filter, Maya Layer, and Karma Store

Validates the pre-output cognitive classification layer based on
Patanjali's Yoga Sutras (1.5-1.11), the Maya representation gap tracker,
and the Karma runtime learning store.

Each test includes a docstring explaining the philosophical concept
being verified.
"""

import pytest
import sys
import os
import tempfile

# Ensure the src package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vritti_filter import (
    VrittiFilter,
    MayaLayer,
    KarmaStore,
    Vritti,
    Pramana,
    ConsistencyReport,
    DepthScore,
    VrittiResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vf():
    return VrittiFilter()


@pytest.fixture
def maya():
    return MayaLayer(knowledge_cutoff="2025-04")


@pytest.fixture
def karma_store():
    """Provide a KarmaStore backed by a temporary file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    store = KarmaStore(path)
    yield store
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


# ---------------------------------------------------------------------------
# Vritti Classification Tests
# ---------------------------------------------------------------------------

class TestPramanaClassification:
    """Tests for Pramana — valid cognition (Yoga Sutra 1.7)."""

    def test_specific_sourced_text_is_pramana(self, vf):
        """Pramana is valid cognition grounded in evidence.

        Yoga Sutra 1.7 defines pramana as arising from pratyaksha
        (perception), anumana (inference), or agama (testimony).
        Text with specific details, citations, concrete examples,
        and verifiable claims should classify as pramana.
        """
        text = (
            "Python 3.12 introduced the new type parameter syntax (PEP 695), "
            "released on October 2, 2023. For example, generic classes can now "
            "be written as `class Stack[T]:` instead of using `Generic[T]`. "
            "See https://peps.python.org/pep-0695/ for the full specification."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.PRAMANA

    def test_data_grounded_claim_is_pramana(self, vf):
        """Claims grounded in empirical data — pratyaksha pramana."""
        text = (
            "The data shows that server response time averages 142ms "
            "across 10,000 requests. Measurements indicate a p99 latency "
            "of 890ms, specifically in the /api/users endpoint."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.PRAMANA


class TestViparyayaDetection:
    """Tests for Viparyaya — misconception (Yoga Sutra 1.8)."""

    def test_contradictory_claims_detected(self, vf):
        """Viparyaya is 'knowledge of a form not corresponding to the thing'.

        Yoga Sutra 1.8: viparyayo mithya-jnanam atad-rupa-pratistham.
        Text containing factually incorrect statements, absolute claims
        that are demonstrably false, or internal contradictions should
        classify as viparyaya.
        """
        text = (
            "Python is always faster than C because it is a higher-level language. "
            "Higher-level languages are always more efficient since they abstract "
            "away the machine details. Studies show that interpreted languages "
            "outperform compiled ones in every benchmark."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.VIPARYAYA

    def test_context_contradiction_detected(self, vf):
        """Badhita hetvabhasa: contradiction by stronger evidence.

        When the system's output contradicts the user's own context,
        the Maya/Vritti system should flag it as viparyaya. The context
        is the 'stronger evidence' that overrides the model's claim.
        """
        context = "The team consists of 3 developers. The budget is $50,000."
        text = "The team of 8 developers should deliver this within the $200,000 budget."
        result = vf.classify(text, context=context)
        assert result.vritti == Vritti.VIPARYAYA


class TestVikalpaDetection:
    """Tests for Vikalpa — verbal delusion (Yoga Sutra 1.9)."""

    def test_hedging_empty_language_detected(self, vf):
        """Vikalpa is 'knowledge based on words alone, with no reality'.

        Yoga Sutra 1.9: shabda-jnana-anupati vastu-shunyo vikalpah.
        Text that sounds meaningful but conveys no falsifiable content —
        hedging, circular definitions, appeals to unnamed authorities —
        should classify as vikalpa.
        """
        text = (
            "In a sense, software architecture is essentially about making "
            "fundamentally important decisions that are, in some ways, very "
            "critical to the overall success of the project. Various experts "
            "suggest that it could potentially be the most important aspect "
            "of software development to some extent."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.VIKALPA


class TestNidraDetection:
    """Tests for Nidra — absence of knowledge (Yoga Sutra 1.10)."""

    def test_no_real_knowledge_detected(self, vf):
        """Nidra is 'the vritti whose object is absence'.

        Yoga Sutra 1.10: abhava-pratyaya-alambana vrittir nidra.
        When the system has no real knowledge to offer and fills the
        space with hedging, deflection, and 'it depends' — that is
        nidra. The honest response is to admit the gap.
        """
        text = (
            "I'm not sure about the exact details, but generally speaking, "
            "it depends on many factors. There is no simple answer to this "
            "question as it varies from case to case. In many cases, the "
            "outcome typically depends on the specific context."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.NIDRA


class TestSmritiDetection:
    """Tests for Smriti — memory recall (Yoga Sutra 1.11)."""

    def test_encyclopedic_recall_detected(self, vf):
        """Smriti is 'the non-loss of a previously experienced object'.

        Yoga Sutra 1.11: anubhuta-vishaya-asampramoshah smritih.
        Encyclopedic regurgitation of memorized facts — biographical
        data, date-anchored claims, textbook definitions — without
        fresh reasoning should classify as smriti.
        """
        text = (
            "Alan Turing was a British mathematician who is widely regarded "
            "as the father of theoretical computer science. He was born in "
            "1912 in Maida Vale, London. Turing is defined as a pioneer of "
            "computing. He published his seminal paper 'On Computable Numbers' "
            "in 1936."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.SMRITI


# ---------------------------------------------------------------------------
# Vritti Filter Output Tests
# ---------------------------------------------------------------------------

class TestVrittiFilterOutput:
    """Tests for the filter() output gate."""

    def test_pramana_passes_through(self, vf):
        """Valid cognition should pass through without warning."""
        text = (
            "Python 3.12 introduced PEP 695 on October 2, 2023. "
            "See https://peps.python.org/pep-0695/ for details."
        )
        filtered = vf.filter(text)
        # Should not contain warning headers
        assert "VIPARYAYA" not in filtered
        assert "VIKALPA" not in filtered

    def test_nidra_replaced_with_honesty(self, vf):
        """Nidra (absence) should be replaced with an honest admission."""
        text = (
            "I'm not sure about the details, but generally it depends. "
            "There is no simple answer as it varies from case to case."
        )
        filtered = vf.filter(text)
        assert "don't have reliable knowledge" in filtered


# ---------------------------------------------------------------------------
# Maya Layer Tests
# ---------------------------------------------------------------------------

class TestMayaRecency:
    """Tests for the Maya Layer — representation gap tracking."""

    def test_current_claim_flagged(self, maya):
        """Maya tracks the gap between model knowledge and reality.

        In Vedanta, Maya is not 'illusion' but the gap between
        appearance (pratibhasika) and reality (paramarthika). Claims
        using 'currently', 'now', or 'today' depend on up-to-date
        information the model may not have.
        """
        gap = maya.check_recency("Bitcoin is currently trading at $45,000.")
        assert gap is not None
        assert gap.gap_type == "recency"

    def test_historical_claim_not_flagged(self, maya):
        """Static historical facts should not trigger recency flags."""
        gap = maya.check_recency("Python was created by Guido van Rossum.")
        assert gap is None

    def test_position_claim_flagged(self, maya):
        """Claims about positions (CEO, president) change over time."""
        gap = maya.check_recency("The current CEO of OpenAI is Sam Altman.")
        assert gap is not None

    def test_grounding_check_detects_ungrounded(self, maya):
        """The Maya grounding check detects claims not supported by evidence.

        This is the most important Maya check — when the model generates
        claims about a topic, but the user's own documents say something
        different, Maya flags the representation gap.
        """
        evidence = "The project uses Python and PostgreSQL."
        claim = "The frontend is built with React and TypeScript."
        gap = maya.check_grounding(claim, evidence)
        assert gap is not None
        assert gap.gap_type == "grounding"


# ---------------------------------------------------------------------------
# Karma Store Tests
# ---------------------------------------------------------------------------

class TestKarmaStore:
    """Tests for the Karma Store — runtime learning via karma-samskara-vasana."""

    def test_record_and_retrieve(self, karma_store):
        """Karma (action) produces Samskara (impression).

        Every action leaves an impression. The KarmaStore records
        action-outcome pairs so the system can learn from experience
        without retraining.
        """
        karma_store.record_action(
            action="used formal tone",
            outcome="positive: user appreciated clarity",
            domain="tone",
        )
        domains = karma_store.get_all_domains()
        assert "tone" in domains

    def test_vasana_derivation(self, karma_store):
        """Samskaras accumulate into Vasanas (tendencies).

        Repeated positive outcomes for the same action create a
        reinforcing vasana (tendency). The system develops behavioral
        patterns from accumulated experience.
        """
        karma_store.record_action("cited sources", "positive: user verified", "evidence")
        karma_store.record_action("cited sources", "positive: user trusted", "evidence")
        karma_store.record_action("no citation", "negative: user questioned", "evidence")

        vasanas = karma_store.get_vasanas("evidence")
        assert len(vasanas) > 0

    def test_burn_vasanas(self, karma_store):
        """Jnana-agni — the fire of knowledge burns outdated karma.

        Bhagavad Gita 4.37: 'As a blazing fire turns firewood to ashes,
        so does the fire of knowledge burn all karma to ashes.'
        The burn_vasanas() method clears outdated biases so the system
        can start fresh in a domain.
        """
        karma_store.record_action("action1", "positive: good", "tone")
        karma_store.record_action("action2", "negative: bad", "tone")
        karma_store.record_action("action3", "positive: ok", "style")

        burned = karma_store.burn_vasanas(domain="tone")
        assert burned == 2

        domains = karma_store.get_all_domains()
        assert "tone" not in domains
        assert "style" in domains

    def test_summary(self, karma_store):
        """The karma store should provide a summary of its state."""
        karma_store.record_action("a1", "positive: ok", "d1")
        karma_store.record_action("a2", "negative: bad", "d2")

        summary = karma_store.summary()
        assert summary["total_samskaras"] == 2
        assert "d1" in summary["domains"]
        assert "d2" in summary["domains"]

    def test_empty_store(self, karma_store):
        """A fresh store should have no samskaras or domains."""
        summary = karma_store.summary()
        assert summary["total_samskaras"] == 0
        assert summary["domains"] == []


# ---------------------------------------------------------------------------
# FIX 1: Disguised Smriti / Novelty Score Tests
# ---------------------------------------------------------------------------

class TestDisguisedSmriti:
    """Tests for detecting recall disguised as analysis."""

    def test_organized_recall_caught(self, vf):
        """Text that sounds analytical but is just organized common knowledge.

        This is the Palestine failure mode: every claim could be found on
        Wikipedia, presented in analytical framing ('key factor',
        'has been a major issue') but containing no novel reasoning.
        """
        text = (
            "The Israeli-Palestinian conflict has been a major source of "
            "instability in the Middle East. It's well known that the "
            "occupation has been a key factor in the ongoing tensions. "
            "The settlements have been a significant obstacle to peace. "
            "Obviously, the humanitarian situation has been a critical "
            "concern for the international community. As everyone knows, "
            "the two-state solution has been the primary diplomatic "
            "framework discussed by world leaders."
        )
        result = vf.classify(text)
        assert result.vritti == Vritti.SMRITI, (
            f"Expected smriti for disguised recall, got {result.vritti.value}"
        )

    def test_novelty_score_low_for_common_knowledge(self, vf):
        """Novelty score should be low for organized common knowledge."""
        text = (
            "Obviously, climate change has been a major challenge for the "
            "world. It's well known that rising temperatures have caused "
            "sea levels to rise. As everyone knows, carbon emissions have "
            "been a key driver of global warming."
        )
        score = vf.novelty_score(text)
        assert score < 30, f"Expected novelty < 30 for common knowledge, got {score}"

    def test_novelty_score_high_for_genuine_insight(self, vf):
        """Novelty score should be high for text with genuine novel connections."""
        text = (
            "What most analyses of database performance miss is that the "
            "bottleneck isn't the query engine — it's the serialization layer. "
            "Because each row must be deserialized from the on-disk format, "
            "which involves memory allocation, this creates GC pressure that "
            "causes latency spikes. This implies that columnar storage isn't "
            "just faster for analytics — it actually reduces garbage collection "
            "overhead, which is the real reason Parquet outperforms row-based "
            "formats in JVM-based systems."
        )
        score = vf.novelty_score(text)
        assert score > 50, f"Expected novelty > 50 for genuine insight, got {score}"


# ---------------------------------------------------------------------------
# FIX 2: Cross-Validation Tests
# ---------------------------------------------------------------------------

class TestCrossValidation:
    """Tests for pramana-vritti cross-validation."""

    def test_pramana_shabda_mismatch(self, vf):
        """If vritti is PRAMANA but pramana is SHABDA, flag the mismatch.

        This catches the case where training-data recall is presented
        as freshly validated cognition.
        """
        vritti_result = VrittiResult(
            vritti=Vritti.PRAMANA,
            confidence=0.8,
            explanation="test",
        )
        report = vf.cross_validate(vritti_result, Pramana.SHABDA)
        assert not report.consistent
        assert len(report.mismatches) == 1
        assert "training data" in report.mismatches[0].flag

    def test_pramana_anumana_low_confidence(self, vf):
        """Weak inference presented as established fact."""
        vritti_result = VrittiResult(
            vritti=Vritti.PRAMANA,
            confidence=0.4,
            explanation="test",
        )
        report = vf.cross_validate(vritti_result, Pramana.ANUMANA)
        assert not report.consistent
        assert "Weak inference" in report.mismatches[0].flag

    def test_smriti_pratyaksha_mismatch(self, vf):
        """Memory recall presented as direct observation."""
        vritti_result = VrittiResult(
            vritti=Vritti.SMRITI,
            confidence=0.7,
            explanation="test",
        )
        report = vf.cross_validate(vritti_result, Pramana.PRATYAKSHA)
        assert not report.consistent
        assert "direct observation" in report.mismatches[0].flag

    def test_consistent_pramana_pratyaksha(self, vf):
        """Valid cognition from direct observation — should be consistent."""
        vritti_result = VrittiResult(
            vritti=Vritti.PRAMANA,
            confidence=0.9,
            explanation="test",
        )
        report = vf.cross_validate(vritti_result, Pramana.PRATYAKSHA)
        assert report.consistent
        assert len(report.mismatches) == 0


# ---------------------------------------------------------------------------
# FIX 3: Depth Test
# ---------------------------------------------------------------------------

class TestDepthTest:
    """Tests for the analysis depth scorer."""

    def test_shallow_list_scores_low(self, vf):
        """Parallel list of general assertions should score low."""
        text = (
            "There are several important considerations. First, cost is a "
            "factor. Second, performance matters. Third, security is key. "
            "Fourth, scalability is important. Fifth, maintainability counts."
        )
        depth = vf.depth_test(text, "What should I consider for my architecture?")
        assert depth.score < 30, f"Expected depth < 30, got {depth.score}"

    def test_deep_analysis_scores_high(self, vf):
        """Genuine reasoning chain with evidence should score high."""
        text = (
            "The memory leak originates in the WebSocket handler. Data shows "
            "each connection allocates a 64KB buffer that is never freed on "
            "disconnect — 12,847 unreleased Buffer objects after 3 hours of "
            "load testing with 500 connections, consuming 803MB. Therefore "
            "the OOM kill at hour 4 is caused by this specific leak. This "
            "implies that the fix is not to increase memory limits but to call "
            "buffer.release() in the on_close callback, which in turn means "
            "the issue will recur in any handler that creates buffers without "
            "a cleanup hook."
        )
        depth = vf.depth_test(text, "Why does the server crash after 4 hours?")
        assert depth.score >= 50, f"Expected depth >= 50, got {depth.score}"
        assert depth.specific_evidence_count >= 1
        assert depth.reasoning_chain_count >= 1

    def test_short_text_scores_zero(self, vf):
        """Very short text can't be deep."""
        depth = vf.depth_test("Yes.", "Should I use React?")
        assert depth.score == 0
