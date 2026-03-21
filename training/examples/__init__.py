"""
examples — Training example generators for each darshana + router + vritti.

Each module exports a generate_<name>_examples() function that returns
a list of chat-format dicts ready for JSONL serialization.
"""

from examples.nyaya import generate_nyaya_examples
from examples.samkhya import generate_samkhya_examples
from examples.yoga import generate_yoga_examples
from examples.vedanta import generate_vedanta_examples
from examples.mimamsa import generate_mimamsa_examples
from examples.vaisheshika import generate_vaisheshika_examples
from examples.router import generate_router_examples
from examples.vritti import generate_vritti_examples

__all__ = [
    "generate_nyaya_examples",
    "generate_samkhya_examples",
    "generate_yoga_examples",
    "generate_vedanta_examples",
    "generate_mimamsa_examples",
    "generate_vaisheshika_examples",
    "generate_router_examples",
    "generate_vritti_examples",
]
