"""
guard.py — One-Line Inference-Time Quality Guard for Any LLM Client
====================================================================

    from darshana import guard
    client = guard(anthropic.Anthropic(api_key="..."))

Every call through the guarded client automatically:
1. Detects the model's capability level
2. Applies the minimum intervention (instruction for strong, structure for weak)
3. Runs the Vritti filter on the response
4. Attaches quality metadata to the response

The guarded client is a drop-in replacement — same API, same return types,
with quality improvements applied transparently.

Based on the adhikara-bheda principle: match the intervention to the model.

Author: Harsh (with Claude as co-thinker)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

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

    # Check strong models (exact substring match)
    for pattern in STRONG_MODELS:
        if pattern in model_lower:
            return "strong"

    # Check weak models (family match)
    for pattern in WEAK_MODELS:
        if pattern in model_lower:
            return "weak"

    return "unknown"


# ---------------------------------------------------------------------------
# Vritti metadata attached to responses
# ---------------------------------------------------------------------------

@dataclass
class VrittiMeta:
    """Quality metadata attached to guarded responses."""
    vritti: str           # pramana, viparyaya, vikalpa, nidra, smriti
    confidence: float     # 0.0 - 1.0
    novelty: int          # 0 - 100
    intervention: str     # "instruction", "structure", "both", "none"
    model_class: str      # "strong", "weak", "unknown"


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
        query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    query = content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            query = block.get("text", "")
                            break
                        elif isinstance(block, str):
                            query = block
                            break
                break

        # Apply intervention based on model class
        system = kwargs.get("system", "")
        if isinstance(system, list):
            # Anthropic format: [{"type": "text", "text": "..."}]
            system_text = " ".join(
                b.get("text", "") for b in system if isinstance(b, dict)
            )
        else:
            system_text = system or ""

        if model_class == "strong":
            # Instruction only — append anti-syc to system prompt
            intervention = "instruction"
            new_system = system_text + ANTI_SYC_INSTRUCTION if system_text else ANTI_SYC_INSTRUCTION.strip()
            kwargs["system"] = new_system

        elif model_class == "weak":
            # Structure + instruction — route and apply darshana prompt
            intervention = "both"
            routing = self._router.route(query)
            engine = routing.top_engines[0]
            darshana_prompt = get_darshana_prompt(engine, guna=routing.guna.value)
            if system_text:
                new_system = system_text + "\n\n" + darshana_prompt
            else:
                new_system = darshana_prompt
            kwargs["system"] = new_system

        else:
            # Unknown model — default to instruction (safe, cheap)
            intervention = "instruction"
            new_system = system_text + ANTI_SYC_INSTRUCTION if system_text else ANTI_SYC_INSTRUCTION.strip()
            kwargs["system"] = new_system

        # Make the original API call
        response = self._original.create(**kwargs)

        # Extract response text for vritti analysis
        response_text = ""
        if hasattr(response, "content") and response.content:
            for block in response.content:
                if hasattr(block, "text"):
                    response_text += block.text

        # Run vritti filter (no LLM call, pattern-based only)
        if response_text:
            vr = self._vritti.classify(response_text)
            novelty = self._vritti.novelty_score(response_text)
            meta = VrittiMeta(
                vritti=vr.vritti.value,
                confidence=round(vr.confidence, 3),
                novelty=novelty,
                intervention=intervention,
                model_class=model_class,
            )
        else:
            meta = VrittiMeta(
                vritti="unknown",
                confidence=0.0,
                novelty=0,
                intervention=intervention,
                model_class=model_class,
            )

        # Attach metadata to response (non-destructive)
        response._darshana = meta

        return response


class GuardedClient:
    """
    Wraps an LLM client to apply Om's inference-time quality guard.

    Usage:
        from darshana import guard
        client = guard(anthropic.Anthropic())
        response = client.messages.create(...)
        print(response._darshana.vritti)  # quality metadata
    """

    def __init__(self, original_client, model_class: str = "unknown"):
        self._original = original_client
        self._model_class = model_class

        # Wrap the messages interface
        if hasattr(original_client, "messages"):
            self.messages = GuardedMessages(
                original_client.messages, model_class
            )

        # Pass through everything else
        self._wrap_passthrough()

    def _wrap_passthrough(self):
        """Forward all non-messages attributes to the original client."""
        for attr in dir(self._original):
            if attr.startswith("_") or attr == "messages":
                continue
            if not hasattr(self, attr):
                try:
                    setattr(self, attr, getattr(self._original, attr))
                except AttributeError:
                    pass

    def __getattr__(self, name):
        """Fall through to original client for anything we don't wrap."""
        return getattr(self._original, name)


def guard(client, model_class: str = "unknown") -> GuardedClient:
    """
    Wrap any LLM client with Om's inference-time quality guard.

    Args:
        client: An Anthropic, AnthropicBedrock, or OpenAI client instance.
        model_class: Override auto-detection. One of "strong", "weak", "unknown".
            - "strong": applies instruction only (optimal for Claude 4.5+)
            - "weak": applies structure + instruction (needed for Llama, Nova, etc.)
            - "unknown": auto-detects from model name in each call

    Returns:
        A GuardedClient that behaves identically to the original but applies
        the appropriate sycophancy intervention on every call.

    Example:
        from darshana import guard
        import anthropic

        # One line to add Om
        client = guard(anthropic.Anthropic())

        # Use exactly as before
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            messages=[{"role": "user", "content": "Is this argument valid?"}],
        )

        # Quality metadata is attached
        print(response._darshana.vritti)       # "pramana"
        print(response._darshana.intervention)  # "instruction"
        print(response._darshana.model_class)   # "strong"
    """
    return GuardedClient(client, model_class)
