"""symbolic_regression — evolve a *formula* that fits the data.

Give it points sampled from a hidden function and it searches the space of
mathematical expressions — built from +, −, ×, ÷, sin, and constants — for one
that reproduces them. The search is genetic programming over expression trees:
crossover swaps sub-formulas between parents, mutation rewrites a sub-formula,
and the fitness is just *how well the expression fits*, evaluated exactly.

That "the verifier is a clock" loop is the heart of evolutionary program search
(AlphaEvolve & friends): you don't need to know the answer, only how to score a
guess. It rediscovers equations like ``x*x - 2`` and ``x*sin(x)`` from numbers
alone, and prefers simple formulas over bloated ones. Fully offline,
deterministic.
"""
from .expr import Expr, evaluate, random_tree, size
from .gp import GPResult, evolve
from .targets import TARGETS, get_target

__all__ = ["Expr", "evaluate", "random_tree", "size",
           "GPResult", "evolve", "TARGETS", "get_target"]
