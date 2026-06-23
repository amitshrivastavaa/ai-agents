"""Deterministic, dependency-free text utilities shared across lab MVPs.

Offline mode must be *reproducible* — same input, same output — so we never
use Python's built-in ``hash()`` (it is salted per process via PYTHONHASHSEED).
All randomness is derived from ``hashlib`` so demos and tests are stable across
runs and machines.
"""
from __future__ import annotations

import hashlib
import random
import re

_STOPWORDS = frozenset(
    """
    a an the and or but if then else for to of in on at by with without from into
    over under again further is are was were be been being do does did doing have
    has had having i you he she it we they them this that these those as so than too
    very can will just should would could may might must shall not no nor our your
    their about above below up down out off only own same now what when which who
    whom whose why how all any both each few more most other some such only
    """.split()
)


def stable_seed(*parts: object) -> int:
    """A deterministic 64-bit seed from arbitrary parts.

    Unlike the built-in ``hash()``, this is stable across processes, which is
    what offline reproducibility requires.
    """
    joined = "\x1f".join(str(p) for p in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def rng(*parts: object) -> random.Random:
    """A seeded RNG keyed on the given parts — reproducible across processes."""
    return random.Random(stable_seed(*parts))


def keywords(text: str, *, limit: int = 8) -> list[str]:
    """Extract salient lowercase keywords, stopwords removed, order-preserving."""
    seen: dict[str, None] = {}
    for raw in re.findall(r"[A-Za-z][A-Za-z0-9'+-]*", text.lower()):
        if len(raw) < 3 or raw in _STOPWORDS:
            continue
        seen.setdefault(raw.strip("'+-"), None)
    seen.pop("", None)
    return list(seen)[:limit]


def headline(text: str, *, width: int = 70) -> str:
    """First sentence-ish chunk of ``text``, trimmed to ``width`` chars."""
    first = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0].strip()
    if len(first) > width:
        first = first[: width - 1].rstrip() + "…"
    return first


def pick(seq, *seed_parts):
    """Deterministically pick one element of ``seq`` keyed on ``seed_parts``."""
    items = list(seq)
    if not items:
        raise ValueError("cannot pick from an empty sequence")
    return items[rng(*seed_parts).randrange(len(items))]
