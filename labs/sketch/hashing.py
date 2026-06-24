"""Deterministic 64-bit hashing for the sketches.

Uses SHA-256 (like the lab kernel) so the bits are well-distributed *and* stable
across processes — sketches must be reproducible, and Python's built-in ``hash``
is salted per run.
"""
from __future__ import annotations

import hashlib

_MASK64 = (1 << 64) - 1


def h64(item, seed=0) -> int:
    digest = hashlib.sha256(f"{seed}\x1f{item}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") & _MASK64
