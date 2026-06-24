"""Measure LSH quality: recall vs the exact answer, and how much work it saved."""
from __future__ import annotations

from .index import LSHIndex


def recall_at_k(index: LSHIndex, queries, k=10):
    """Average fraction of the true top-k that LSH retrieves, and the average
    candidate fraction (work done vs. a brute-force scan)."""
    n = len(index.data)
    recalls, fracs = [], []
    for q in queries:
        true = set(index.brute_force(q, k))
        got, ncand = index.query(q, k)
        recalls.append(len(set(got) & true) / k)
        fracs.append(ncand / n)
    return sum(recalls) / len(recalls), sum(fracs) / len(fracs)


def build(data, n_bits=14, n_tables=8, seed="idx"):
    return LSHIndex(len(data[0]), n_bits=n_bits, n_tables=n_tables, seed=seed).add(data)
