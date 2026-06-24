"""HyperLogLog — count distinct items in (literally) a few kilobytes.

Intuition: hash each item to a random bit-string. Among many random strings, the
*maximum* number of leading zeros seen is a fingerprint of how many distinct
strings there were — if you've seen a hash starting with ``k`` zeros, you've
probably seen ~``2^k`` distinct items. HyperLogLog splits the stream across
``m = 2^p`` registers (by the first ``p`` bits) and harmonic-means their
estimates, getting a cardinality estimate with ~``1.04/√m`` relative error using
one small byte per register — independent of the true count.
"""
from __future__ import annotations

import math

from .hashing import h64

_BITS = 64


class HyperLogLog:
    def __init__(self, p=12, seed="hll"):
        self.p = p
        self.m = 1 << p
        self.seed = seed
        self.reg = [0] * self.m

    def add(self, x):
        h = h64(x, self.seed)
        j = h >> (_BITS - self.p)                    # first p bits → register
        rest = h & ((1 << (_BITS - self.p)) - 1)     # remaining bits
        width = _BITS - self.p
        rank = width - rest.bit_length() + 1         # leading zeros + 1
        if rank > self.reg[j]:
            self.reg[j] = rank
        return self

    def _alpha(self):
        m = self.m
        if m >= 128:
            return 0.7213 / (1 + 1.079 / m)
        return {16: 0.673, 32: 0.697, 64: 0.709}.get(m, 0.7213)

    def count(self):
        m = self.m
        z = sum(2.0 ** -r for r in self.reg)
        est = self._alpha() * m * m / z
        if est <= 2.5 * m:                           # small-range: linear counting
            zeros = self.reg.count(0)
            if zeros:
                return m * math.log(m / zeros)
        return est
