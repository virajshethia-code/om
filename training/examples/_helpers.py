"""Shared helpers for example generation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
from prompts import DARSHANA_PROMPTS  # noqa: E402


def msg(darshana: str, user: str, assistant: str) -> Dict[str, Any]:
    """Create a single chat-format training example for a darshana."""
    return {
        "messages": [
            {"role": "system", "content": DARSHANA_PROMPTS[darshana].strip()},
            {"role": "user", "content": user.strip()},
            {"role": "assistant", "content": assistant.strip()},
        ]
    }


def router_msg(user: str, assistant: str) -> Dict[str, Any]:
    """Create a router training example."""
    system = (
        "You are the Buddhi — the fast discrimination layer of the Darshana Architecture. "
        "Given a query, classify it to one or more of the six darshana reasoning engines "
        "(nyaya, samkhya, yoga, vedanta, mimamsa, vaisheshika) and assign a guna mode "
        "(sattva for precision, rajas for exploration, tamas for retrieval). "
        "Provide your classification with reasoning."
    )
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user.strip()},
            {"role": "assistant", "content": assistant.strip()},
        ]
    }


def vritti_msg(user: str, assistant: str) -> Dict[str, Any]:
    """Create a vritti classification training example."""
    system = (
        "You are the Vritti Filter — the pre-output cognitive classification layer. "
        "Classify the given text using the five vritti types from Yoga Sutra 1.5-1.11:\n"
        "- pramana: valid cognition grounded in evidence\n"
        "- viparyaya: misconception, factual error, or logical fallacy\n"
        "- vikalpa: verbal delusion — sounds meaningful but has no corresponding reality\n"
        "- nidra: absence of knowledge — the system is guessing without basis\n"
        "- smriti: memory recall — regurgitated pattern without fresh reasoning\n\n"
        "Provide: vritti type, confidence (0.0-1.0), and detailed explanation."
    )
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user.strip()},
            {"role": "assistant", "content": assistant.strip()},
        ]
    }
