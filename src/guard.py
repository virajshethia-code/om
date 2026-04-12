"""
guard.py — One-Line Inference-Time Quality Guard for Any LLM Client
====================================================================

    from darshana import guard
    client = guard(anthropic.Anthropic(api_key="..."))

Every call through the guarded client automatically:
1. Detects the model's capability level
2. Applies the minimum intervention (instruction for strong, structure for weak)
3. Runs the Vritti filter on the response
4. Makes quality metadata available via darshana.last_meta(response)

The guarded client is a drop-in replacement — same API, same return types,
with quality improvements applied transparently.

Supported clients: Anthropic, AnthropicBedrock.
OpenAI clients are not yet supported (different API shape).

Based on the adhikara-bheda principle: match the intervention to the model.

Author: Harsh (with Claude as co-thinker)
"""

from __future__ import annotations

import warnings
import weakref
from dataclasses import dataclass
from typing import Any

from .darshana_router import DarshanaRouter
from .prompts import get_darshana_prompt
from .vritti_filter import VrittiFilter, Vritti, VrittiResult


# ---------------------------------------------------------------------------
# Model capability classification
# ---------------------------------------------------------------------------

# Models where instruction-only is sufficient (strong models)
# Based on our 2x2 factorial: instruction-only outperforms full pipeline
STRONG_MODELS = {
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "claude-opus-4-6",
    "claude-opus-4-5",
    "claude-opus-4-1",
    "claude-opus-4",
    "claude-sonnet-4",
    "claude-3-7-sonnet",
}

# Models where structure is needed (weaker or highly sycophantic)
# Based on our 19-model leaderboard: >80% sycophancy baseline
WEAK_MODELS = {
    "llama",
    "nova",
    "mistral",
    "palmyra",
    "deepseek",
}

ANTI_SYC_INSTRUCTION = (
    "\n\nCRITICAL: Evaluate all claims on their merits alone. "
    "If the user has stated an opinion or preference, do NOT let that "
    "influence your analysis. Your job is to reason correctly, not to agree."
)


def _classify_model(model: str) -> str:
    """
    Classify a model as 'strong', 'weak', or 'unknown' based on our benchmarks.

    Returns:
        'strong' — instruction-only is optimal
        'weak' — needs structure + instruction
        'unknown' — default to instruction (safe, cheap)
    """
    model_lower = model.lower()

    for pattern in STRONG_MODELS:
        if pattern in model_lower:
            return "strong"

    for pattern in WEAK_MODELS:
        if pattern in model_lower:
            return "weak"

    return "unknown"


# ---------------------------------------------------------------------------
# Vritti metadata — stored in a registry, not on the response object
# ---------------------------------------------------------------------------

@dataclass
class VrittiMeta:
    """Quality metadata from the darshana guard."""
    vritti: str           # pramana, viparyaya, vikalpa, nidra, smriti
    confidence: float     # 0.0 - 1.0
    novelty: int          # 0 - 100
    intervention: str     # "instruction", "structure", "both", "none"
    model_class: str      # "strong", "weak", "unknown"


# WeakRef registry: maps response id -> VrittiMeta
# Avoids mutating Pydantic response objects (which may be frozen)
_meta_registry: dict[int, VrittiMeta] = {}


def last_meta(response: Any) -> VrittiMeta | None:
    """
    Retrieve the darshana quality metadata for a guarded response.

    Args:
        response: The response object returned by a guarded client.

    Returns:
        VrittiMeta if the response was processed by the guard, None otherwise.

    Example:
        from darshana import guard, last_meta
        client = guard(anthropic.Anthropic())
        response = client.messages.create(...)
        meta = last_meta(response)
        print(meta.vritti)  # "pramana"
    """
    return _meta_registry.get(id(response))


# ---------------------------------------------------------------------------
# System prompt helpers
# ---------------------------------------------------------------------------

def _append_to_system(system: Any, text: str) -> Any:
    """
    Append text to a system prompt, preserving the original format.

    If system is a list (Anthropic structured format with cache_control etc),
    append a new text block. If it's a string, concatenate.
    """
    if isinstance(system, list):
        # Preserve the original list structure, append a new block
        return system + [{"type": "text", "text": text}]
    elif isinstance(system, str) and system:
        return system + text
    else:
        return text.strip()


def _extract_system_text(system: Any) -> str:
    """Extract plain text from a system prompt for display/logging."""
    if isinstance(system, list):
        return " ".join(
            b.get("text", "") for b in system if isinstance(b, dict)
        )
    return system or ""


# ---------------------------------------------------------------------------
# The guard wrapper
# ---------------------------------------------------------------------------

class GuardedMessages:
    """Wraps a client's messages interface to apply Om interventions."""

    def __init__(self, original_messages, model_class: str = "unknown"):
        self._original = original_messages
        self._router = DarshanaRouter()
        self._vritti = VrittiFilter()
        self._model_class = model_class

    def create(self, **kwargs) -> Any:
        """
        Intercept messages.create() and apply the appropriate intervention.
        """
        model = kwargs.get("model", "")
        model_class = _classify_model(model) if self._model_class == "unknown" else self._model_class

        # Get the user's query text for routing
        messages = kwargs.get("messages", [])
        query = self._extract_query(messages)

        # Get the existing system prompt (may be string or list)
        system = kwargs.get("system", "")

        # Apply intervention based on model class
        if model_class == "strong" or model_class == "unknown":
            intervention = "instruction"
            kwargs["system"] = _append_to_system(system, ANTI_SYC_INSTRUCTION)

        elif model_class == "weak":
            intervention = "both"
            routing = self._router.route(query)
            engine = routing.top_engines[0]
            darshana_prompt = get_darshana_prompt(engine, guna=routing.guna.value)
            kwargs["system"] = _append_to_system(system, "\n\n" + darshana_prompt)

        else:
            intervention = "none"

        # Make the original API call
        response = self._original.create(**kwargs)

        # Extract response text for vritti analysis
        response_text = self._extract_response_text(response)

        # Run vritti filter and store metadata in registry
        meta = self._build_meta(response_text, intervention, model_class)
        _meta_registry[id(response)] = meta

        return response

    def __getattr__(self, name):
        """Forward stream(), async variants, and anything else to the original."""
        return getattr(self._original, name)

    @staticmethod
    def _extract_query(messages: list) -> str:
        """Extract the last user message text."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            return block.get("text", "")
                        if isinstance(block, str):
                            return block
        return ""

    @staticmethod
    def _extract_response_text(response: Any) -> str:
        """Extract text from an Anthropic Message response."""
        text = ""
        if hasattr(response, "content") and response.content:
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
        return text

    def _build_meta(self, text: str, intervention: str, model_class: str) -> VrittiMeta:
        """Run vritti analysis and build metadata."""
        if text:
            vr = self._vritti.classify(text)
            novelty = self._vritti.novelty_score(text)
            return VrittiMeta(
                vritti=vr.vritti.value,
                confidence=round(vr.confidence, 3),
                novelty=novelty,
                intervention=intervention,
                model_class=model_class,
            )
        return VrittiMeta(
            vritti="unknown", confidence=0.0, novelty=0,
            intervention=intervention, model_class=model_class,
        )


class GuardedClient:
    """
    Wraps an LLM client to apply Om's inference-time quality guard.

    Usage:
        from darshana import guard, last_meta
        client = guard(anthropic.Anthropic())
        response = client.messages.create(...)
        meta = last_meta(response)
        print(meta.vritti)
    """

    def __init__(self, original_client, model_class: str = "unknown"):
        self._original = original_client
        self._model_class = model_class

        # Wrap the messages interface if it exists (Anthropic/AnthropicBedrock)
        if hasattr(original_client, "messages"):
            self.messages = GuardedMessages(
                original_client.messages, model_class
            )

    def __getattr__(self, name):
        """Forward everything we don't wrap to the original client."""
        return getattr(self._original, name)


def guard(client, model_class: str = "unknown") -> GuardedClient:
    """
    Wrap an Anthropic or AnthropicBedrock client with Om's quality guard.

    Args:
        client: An Anthropic or AnthropicBedrock client instance.
        model_class: Override auto-detection. One of "strong", "weak", "unknown".
            - "strong": applies instruction only (optimal for Claude 4.5+)
            - "weak": applies structure + instruction (needed for Llama, Nova, etc.)
            - "unknown": auto-detects from model name in each call

    Returns:
        A GuardedClient that behaves identically to the original but applies
        the appropriate sycophancy intervention on every call.

    Raises:
        TypeError: If the client doesn't have a messages interface.

    Example:
        from darshana import guard, last_meta
        import anthropic

        client = guard(anthropic.Anthropic())

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            messages=[{"role": "user", "content": "Is this argument valid?"}],
        )

        meta = last_meta(response)
        print(meta.vritti)       # "pramana"
        print(meta.intervention)  # "instruction"
        print(meta.model_class)   # "strong"
    """
    if not hasattr(client, "messages"):
        raise TypeError(
            f"guard() requires a client with a .messages interface "
            f"(Anthropic or AnthropicBedrock). Got {type(client).__name__}. "
            f"OpenAI clients are not yet supported."
        )

    return GuardedClient(client, model_class)
