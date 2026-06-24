"""constitutional — a self-critique & revision loop (Constitutional AI / Self-Refine).

An agent drafts text, *critiques* it against a constitution of principles, and
*revises* — then re-critiques, looping until the draft is clean. That
critique→revise loop is exactly the Constitutional-AI / Self-Refine pattern.

The offline-real trick: every principle ships a rule-checkable **detector** and
a deterministic **fix**, so the loop genuinely converges to zero violations
with no model. When ``ANTHROPIC_API_KEY`` is set, the same loop can route
critique/revision through a real model instead.
"""
from .constitution import PRESETS, Principle, get_constitution
from .refine import Transcript, Violation, critique, refine, revise

__all__ = [
    "PRESETS", "Principle", "get_constitution",
    "Transcript", "Violation", "critique", "refine", "revise",
]
