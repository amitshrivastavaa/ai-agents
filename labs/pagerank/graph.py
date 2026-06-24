"""Directed graphs as ``{node: [out-neighbours]}`` + a few example webs."""
from __future__ import annotations


def web():
    """The classic little web. C is everyone's destination → highest rank."""
    return {
        "A": ["B", "C"],
        "B": ["C"],
        "C": ["A"],
        "D": ["C"],
    }


def star(n=6):
    """A hub linked by ``n`` spokes; the hub links back to one spoke."""
    g = {"hub": ["s0"]}
    for i in range(n):
        g[f"s{i}"] = ["hub"]
    return g


def chain(n=6):
    """A → B → C → … → (dangling last node)."""
    g = {}
    names = [chr(ord("A") + i) for i in range(n)]
    for i, name in enumerate(names):
        g[name] = [names[i + 1]] if i + 1 < n else []     # last node dangles
    return g


def two_communities():
    """Two dense clusters joined by a single bridge edge."""
    g = {
        "a1": ["a2", "a3"], "a2": ["a1", "a3"], "a3": ["a1", "a2", "b1"],
        "b1": ["b2", "b3"], "b2": ["b1", "b3"], "b3": ["b1", "b2"],
    }
    return g


GRAPHS = {"web": web(), "star": star(), "chain": chain(),
          "communities": two_communities()}


def nodes(graph):
    return list(graph)


def edges(graph):
    return [(u, v) for u, outs in graph.items() for v in outs]
