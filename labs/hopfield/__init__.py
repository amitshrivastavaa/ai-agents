"""hopfield — associative memory that recovers patterns from corrupted cues.

Store a handful of patterns as attractors in an energy landscape; hand the
network a noisy or half-erased version of one and it settles back into the
clean original. Two flavours:

* **classic** — the Hebbian Hopfield network (Nobel 2024): weights are the sum
  of outer products, recall is sign-update descent on an energy that only ever
  decreases.
* **modern** — dense associative memory with a softmax retrieval rule (the
  "Hopfield ≈ attention" connection): far higher capacity and sharper recall.

Fully offline, deterministic, and rendered in ASCII so you can watch a smudged
glyph snap back into focus.
"""
from .network import ClassicHopfield, ModernHopfield, overlap
from .patterns import GLYPHS, SIZE, corrupt, occlude, render, to_vec

__all__ = [
    "ClassicHopfield", "ModernHopfield", "overlap",
    "GLYPHS", "SIZE", "corrupt", "occlude", "render", "to_vec",
]
