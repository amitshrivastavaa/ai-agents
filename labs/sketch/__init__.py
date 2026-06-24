"""sketch — streaming probabilistic data structures, from scratch.

Two sublinear-memory sketches that read a stream once and never grow:

* **Count-Min Sketch** — approximate item *frequencies*. A grid of counters +
  hashing; the estimate never underestimates and overshoots by at most ``ε·N``.
  How you count n-grams or find heavy hitters at scale.
* **HyperLogLog** — approximate *cardinality* (distinct count) from the maximum
  leading-zero run across hashed items, with ~``1.04/√m`` relative error in a few
  kilobytes — independent of the true count.

Offline, deterministic (SHA-256 hashing), with measurable error bounds.
"""
from .hashing import h64
from .countmin import CountMin
from .hyperloglog import HyperLogLog

__all__ = ["h64", "CountMin", "HyperLogLog"]
