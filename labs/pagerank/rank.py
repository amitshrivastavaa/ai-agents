"""PageRank by power iteration — the dominant eigenvector of the Google matrix.

A web-surfer who, with probability ``damping`` follows a random out-link and
otherwise teleports to a random page, visits page ``p`` a ``r[p]`` fraction of the
time in the long run. That stationary distribution ``r`` is PageRank, and it
satisfies

    r[p] = (1−d)/N  +  d · ( Σ_{q→p} r[q]/outdeg(q)  +  dangling-mass/N )

Iterating that fixed point from the uniform vector converges to ``r`` — the
power-iteration that ranked the early web.
"""
from __future__ import annotations


def pagerank(graph, damping=0.85, tol=1e-12, max_iter=500):
    """Return ``(ranks, iterations)``. Ranks are a dict summing to 1."""
    ns = list(graph)
    n = len(ns)
    out = {u: len(graph[u]) for u in ns}
    r = {u: 1.0 / n for u in ns}
    iters = 0
    for iters in range(1, max_iter + 1):
        dangling = sum(r[u] for u in ns if out[u] == 0)
        base = (1.0 - damping) / n + damping * dangling / n
        new = {u: base for u in ns}
        for u in ns:
            if out[u]:
                share = damping * r[u] / out[u]
                for v in graph[u]:
                    new[v] += share
        diff = sum(abs(new[u] - r[u]) for u in ns)
        r = new
        if diff < tol:
            break
    return r, iters


def ranked(graph, **kw):
    """Nodes sorted by descending PageRank, as ``[(node, rank), …]``."""
    r, _ = pagerank(graph, **kw)
    return sorted(r.items(), key=lambda kv: kv[1], reverse=True)
