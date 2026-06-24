"""The random surfer — a Monte-Carlo definition of PageRank.

Walk the graph: with probability ``damping`` follow a random out-link, else
(or when stuck on a dangling node) teleport to a random page. The fraction of
time spent on each page converges to its PageRank — so this is an independent
check that the power-iteration computed the right thing.
"""
from __future__ import annotations

from .._kernel import rng


def surf(graph, damping=0.85, steps=200_000, seed="surf"):
    ns = list(graph)
    r = rng("pagerank-surfer", seed, steps)
    visits = {u: 0 for u in ns}
    cur = ns[r.randrange(len(ns))]
    for _ in range(steps):
        visits[cur] += 1
        outs = graph[cur]
        if outs and r.random() < damping:
            cur = outs[r.randrange(len(outs))]
        else:
            cur = ns[r.randrange(len(ns))]          # teleport / dangling escape
    return {u: visits[u] / steps for u in ns}
