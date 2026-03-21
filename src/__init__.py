"""
Darshana Architecture — A Hindu Philosophical Framework for AGI

This package implements the Shaddarshana Router (Buddhi Layer), six
specialized reasoning engines, the Guna processing-mode controller,
and the Pramana epistemic-provenance tagger.

See THESIS.md at the repository root for the full architectural
description and philosophical grounding.
"""

from .darshana_router import (
    DarshanaRouter,
    GunaEngine,
    PramanaTagger,
    NyayaEngine,
    SamkhyaEngine,
    YogaEngine,
    VedantaEngine,
    MimamsaEngine,
    VaisheshikaEngine,
    Guna,
    Pramana,
)

__version__ = "0.1.0"
__all__ = [
    "DarshanaRouter",
    "GunaEngine",
    "PramanaTagger",
    "NyayaEngine",
    "SamkhyaEngine",
    "YogaEngine",
    "VedantaEngine",
    "MimamsaEngine",
    "VaisheshikaEngine",
    "Guna",
    "Pramana",
]
