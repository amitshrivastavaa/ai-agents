"""pagerank — the eigenvector that ranked the web, from scratch.

PageRank scores a node by the long-run fraction of time a **random surfer**
spends there: with probability ``damping`` it follows a random out-link, else it
teleports to a random page. That stationary distribution is the dominant
eigenvector of the "Google matrix", and **power iteration** from the uniform
vector converges to it.

This MVP computes it, and *proves* it two ways — the power iteration and an
independent Monte-Carlo random surfer agree to ~0.001. Offline, deterministic.
Companion to the lab's `repo_cartographer` graph analysis.
"""
from . import graph
from .rank import pagerank, ranked
from .surfer import surf

__all__ = ["graph", "pagerank", "ranked", "surf"]
