"""The TSP problem: cities, distances, and baseline solvers."""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field

from .._kernel import rng


@dataclass
class TSP:
    name: str
    cities: list[tuple[float, float]]
    known_optimal: float | None = None  # set for instances with an analytic answer
    dist: list[list[float]] = field(default_factory=list)

    def __post_init__(self):
        n = len(self.cities)
        self.dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    (ax, ay), (bx, by) = self.cities[i], self.cities[j]
                    self.dist[i][j] = math.hypot(ax - bx, ay - by)

    @property
    def n(self) -> int:
        return len(self.cities)


def tour_length(tour: list[int], dist: list[list[float]]) -> float:
    return sum(dist[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def nearest_neighbor(tsp: TSP, start: int = 0) -> list[int]:
    n = tsp.n
    unvisited = set(range(n)) - {start}
    tour = [start]
    cur = start
    while unvisited:
        nxt = min(unvisited, key=lambda j: tsp.dist[cur][j])
        tour.append(nxt)
        unvisited.discard(nxt)
        cur = nxt
    return tour


def random_tour(tsp: TSP, seed="rand") -> list[int]:
    tour = list(range(tsp.n))
    rng(seed, tsp.name).shuffle(tour)
    return tour


def optimal(tsp: TSP) -> float | None:
    """Exact optimum by brute force for small n, the analytic value if known,
    else None."""
    if tsp.known_optimal is not None:
        return tsp.known_optimal
    if tsp.n > 9:
        return None
    best = math.inf
    for perm in itertools.permutations(range(1, tsp.n)):
        best = min(best, tour_length([0, *perm], tsp.dist))
    return best


# ------------------------------- instances -----------------------------------
def _circle(n: int, r: float = 10.0) -> TSP:
    cities = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n))
              for k in range(n)]
    # optimal tour of points on a circle is the perimeter polygon
    opt = n * 2 * r * math.sin(math.pi / n)
    return TSP(f"circle{n}", cities, known_optimal=opt)


def _random(n: int, seed: str) -> TSP:
    r = rng("cities", seed, n)
    cities = [(round(r.uniform(0, 20), 2), round(r.uniform(0, 20), 2)) for _ in range(n)]
    return TSP(f"random{n}", cities)


INSTANCES: dict[str, TSP] = {
    "circle": _circle(12),
    "random8": _random(8, "a"),
    "random15": _random(15, "b"),
}


def get_instance(name: str) -> TSP:
    try:
        return INSTANCES[name]
    except KeyError:
        raise KeyError(f"unknown instance {name!r}; choose from {sorted(INSTANCES)}") from None
