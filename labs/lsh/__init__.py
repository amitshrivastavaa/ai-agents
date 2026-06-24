"""lsh — locality-sensitive hashing for approximate nearest-neighbour search.

The trick that makes vector search (and RAG-at-scale, and every vector DB)
sublinear instead of `O(N)`. Random-hyperplane **SimHash** turns each vector into
a bit signature with one magic property: two vectors at angle θ share a bit with
probability exactly `1 − θ/π`, so similar vectors land in the same bucket and
dissimilar ones don't. A multi-table index then scores only the handful of
vectors that share a query's bucket.

This MVP shows it hitting **~90% recall@10 while scanning ~10–15% of the data**
(a several-× speedup), the clean recall/speedup dial (tables vs bits), and
verifies the `1 − θ/π` collision law empirically. Companion to the lab's `rag`
(exact TF-IDF) MVP — this is how you scale retrieval. Offline, deterministic.
"""
from .data import make_dataset, make_queries, cosine, normalize
from .hashing import SimHash, angle, collision_prob
from .index import LSHIndex
from .eval import recall_at_k, build

__all__ = [
    "make_dataset", "make_queries", "cosine", "normalize",
    "SimHash", "angle", "collision_prob",
    "LSHIndex", "recall_at_k", "build",
]
