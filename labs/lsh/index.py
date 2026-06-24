"""A multi-table LSH index for approximate nearest-neighbour search.

Each of ``n_tables`` tables hashes every vector to an ``n_bits`` signature and
buckets by it. A query gathers the union of same-bucket items across tables (the
**candidates**) and ranks only those by exact cosine — so it scores a small
fraction of the dataset instead of all of it. More tables → more recall; more
bits → smaller buckets (fewer candidates, less recall). That is the LSH dial.
"""
from __future__ import annotations

from .hashing import SimHash
from .data import cosine


class LSHIndex:
    def __init__(self, dim: int, n_bits=14, n_tables=8, seed="idx"):
        self.dim = dim
        self.n_bits = n_bits
        self.tables = [SimHash(dim, n_bits, seed=(seed, t)) for t in range(n_tables)]
        self.buckets = [dict() for _ in range(n_tables)]
        self.data = []

    def add(self, items):
        for v in items:
            i = len(self.data)
            self.data.append(v)
            for t, h in enumerate(self.tables):
                self.buckets[t].setdefault(h.signature(v), []).append(i)
        return self

    def candidates(self, v):
        cand = set()
        for t, h in enumerate(self.tables):
            cand.update(self.buckets[t].get(h.signature(v), ()))
        return cand

    def query(self, v, k=10):
        """Return ``(top_k_indices, n_candidates_examined)``."""
        cand = self.candidates(v)
        ranked = sorted(cand, key=lambda i: cosine(v, self.data[i]), reverse=True)
        return ranked[:k], len(cand)

    def brute_force(self, v, k=10):
        order = sorted(range(len(self.data)), key=lambda i: cosine(v, self.data[i]),
                       reverse=True)
        return order[:k]
