"""repo_cartographer — map a Python codebase into a dependency graph.

Parse every module with the standard-library ``ast`` (no third-party deps, no
imports executed), resolve imports — including relative ones — into an internal
module graph, then answer the questions you actually ask about a codebase:

* **impact** — if I change module X, what transitively breaks?
* **deps** — what does X (transitively) depend on?
* **central** — which modules is everything leaning on?
* **cycles** — are there import cycles? (Tarjan SCCs)
* **orphans** — what does nobody import?

A pragmatic, fully-offline take on "code RAG" / repo understanding. It can even
map its own ``labs/`` package.
"""
from .graph import CodeGraph, Module
from .scan import scan

__all__ = ["CodeGraph", "Module", "scan"]
