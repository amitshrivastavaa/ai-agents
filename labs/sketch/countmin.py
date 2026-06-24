"""Count-Min Sketch — approximate frequencies of a stream in fixed memory.

A ``depth × width`` grid of counters and ``depth`` independent hashes. To add an
item, bump one counter per row; to estimate its count, take the **minimum** of
those counters (collisions only ever *add*, so the min is the tightest bound).

Guarantees: the estimate **never underestimates**, and overshoots the true count
by at most ``ε·N`` (``ε = e/width``) with probability ``1 − δ`` (``δ = e^{−depth}``)
— all in `O(depth·width)` memory regardless of how many distinct items stream by.
That is how you count n-grams (or track heavy hitters) at web scale.
"""
from __future__ import annotations

from .hashing import h64


class CountMin:
    def __init__(self, width=512, depth=5, seed="cm"):
        self.w = width
        self.d = depth
        self.seed = seed
        self.rows = [[0] * width for _ in range(depth)]
        self.total = 0

    def _col(self, i, x):
        return h64(x, (self.seed, i)) % self.w

    def add(self, x, count=1):
        self.total += count
        for i in range(self.d):
            self.rows[i][self._col(i, x)] += count
        return self

    def estimate(self, x):
        return min(self.rows[i][self._col(i, x)] for i in range(self.d))

    def heavy_hitters(self, candidates, frac=0.01):
        """Items whose estimated count exceeds ``frac`` of the total stream."""
        thresh = frac * self.total
        scored = [(x, self.estimate(x)) for x in candidates]
        return sorted([s for s in scored if s[1] >= thresh],
                      key=lambda kv: kv[1], reverse=True)
