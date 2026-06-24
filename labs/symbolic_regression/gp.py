"""Genetic programming: evolve expression trees to fit the data.

Fitness is the mean-squared error against the points, plus a small parsimony
penalty on tree size (Occam's razor — prefer the simpler formula). Selection is
tournament; crossover swaps a random sub-formula from one parent into another;
mutation rewrites a random sub-formula. The best expression is the discovered
equation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .._kernel import rng
from .expr import (Expr, clone, evaluate, random_tree, replace_at, simplify,
                   size, subtree_at, to_string)
from .targets import Target

MAX_SIZE = 28


@dataclass
class GPResult:
    best: Expr
    best_mse: float
    formula: str
    history: list[float]
    generations: int
    size: int

    @property
    def solved(self) -> bool:
        return self.best_mse < 1e-6


def mse(tree: Expr, X, y) -> float:
    return sum((evaluate(tree, x) - t) ** 2 for x, t in zip(X, y)) / len(X)


def _cost(tree: Expr, X, y, parsimony: float) -> float:
    return mse(tree, X, y) + parsimony * size(tree)


def _tournament(scored, r, k):
    best = scored[r.randrange(len(scored))]
    for _ in range(k - 1):
        c = scored[r.randrange(len(scored))]
        if c[1] < best[1]:
            best = c
    return best[0]


def _crossover(a: Expr, b: Expr, r) -> Expr:
    donor = subtree_at(b, r.randrange(size(b)))
    return replace_at(a, r.randrange(size(a)), donor)


def _mutate(a: Expr, r) -> Expr:
    new = random_tree(r, max_depth=2)
    return replace_at(a, r.randrange(size(a)), new)


def evolve(target: Target, *, population: int = 300, generations: int = 40,
           parsimony: float = 0.002, tournament: int = 4, elite: int = 3,
           mutation_rate: float = 0.3, max_depth: int = 4,
           seed: str = "gp") -> GPResult:
    X, y = target.X, target.y
    r = rng(seed, target.name)
    pop = [random_tree(r, max_depth=max_depth) for _ in range(population)]

    best, best_cost = clone(pop[0]), float("inf")
    history: list[float] = []

    for _ in range(generations):
        scored = sorted(((t, _cost(t, X, y, parsimony)) for t in pop), key=lambda tc: tc[1])
        top, top_cost = scored[0]
        if top_cost < best_cost:
            best, best_cost = clone(top), top_cost
        history.append(mse(top, X, y))
        if mse(best, X, y) < 1e-9:
            break

        nxt = [clone(t) for t, _ in scored[:elite]]
        while len(nxt) < population:
            child = _crossover(_tournament(scored, r, tournament),
                               _tournament(scored, r, tournament), r)
            if size(child) > MAX_SIZE:
                child = clone(_tournament(scored, r, tournament))
            if r.random() < mutation_rate:
                child = _mutate(child, r)
            nxt.append(child)
        pop = nxt

    return GPResult(best, mse(best, X, y), to_string(simplify(best)), history,
                    len(history), size(best))
