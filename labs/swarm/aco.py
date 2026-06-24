"""The ant colony: pheromone-guided tour construction with evaporation.

Each iteration: every ant builds a tour, choosing the next city with probability
∝ ``pheromone**alpha * (1/distance)**beta``; then pheromone evaporates and is
re-deposited in proportion to tour quality (plus an elitist boost for the best
tour so far). Short edges accumulate pheromone and the colony converges.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .._kernel import rng
from .tsp import TSP, nearest_neighbor, tour_length


@dataclass
class ACOResult:
    best_tour: list[int]
    best_length: float
    history: list[float]          # best-so-far length per iteration
    iterations: int

    @property
    def improvement(self) -> float:
        return self.history[0] - self.best_length if self.history else 0.0


@dataclass
class AntColony:
    n_ants: int = 20
    alpha: float = 1.0            # pheromone influence
    beta: float = 4.0            # distance (heuristic) influence
    rho: float = 0.5             # evaporation rate
    q: float = 1.0               # deposit scale
    elitist: float = 3.0         # extra reinforcement of the best tour
    iterations: int = 80
    seed: str = "aco"

    def solve(self, tsp: TSP) -> ACOResult:
        n = tsp.n
        dist = tsp.dist
        eta = [[0.0 if i == j else 1.0 / dist[i][j] for j in range(n)] for i in range(n)]
        nn_len = tour_length(nearest_neighbor(tsp), dist)
        tau0 = 1.0 / (n * nn_len) if nn_len else 1.0
        tau = [[tau0] * n for _ in range(n)]

        best_tour, best_len = None, float("inf")
        history: list[float] = []

        for it in range(self.iterations):
            tours: list[tuple[list[int], float]] = []
            for k in range(self.n_ants):
                r = rng(self.seed, it, k)
                tour = self._construct(n, tau, eta, start=k % n, r=r)
                length = tour_length(tour, dist)
                tours.append((tour, length))
                if length < best_len:
                    best_tour, best_len = tour, length

            # evaporate everywhere
            for i in range(n):
                row = tau[i]
                for j in range(n):
                    row[j] *= (1.0 - self.rho)
            # deposit: every ant, weighted by tour quality
            for tour, length in tours:
                add = self.q / length
                self._lay(tau, tour, add)
            # elitist reinforcement of the best-so-far tour
            self._lay(tau, best_tour, self.elitist * self.q / best_len)

            history.append(best_len)

        return ACOResult(best_tour, best_len, history, self.iterations)

    def _construct(self, n, tau, eta, *, start, r) -> list[int]:
        unvisited = set(range(n))
        unvisited.discard(start)
        tour = [start]
        cur = start
        while unvisited:
            weights = []
            total = 0.0
            for j in unvisited:
                w = (tau[cur][j] ** self.alpha) * (eta[cur][j] ** self.beta)
                weights.append((j, w))
                total += w
            cur = self._roulette(weights, total, r)
            tour.append(cur)
            unvisited.discard(cur)
        return tour

    @staticmethod
    def _roulette(weights, total, r):
        if total <= 0:
            return weights[r.randrange(len(weights))][0]
        x = r.random() * total
        acc = 0.0
        for j, w in weights:
            acc += w
            if acc >= x:
                return j
        return weights[-1][0]

    @staticmethod
    def _lay(tau, tour, amount):
        n = len(tour)
        for i in range(n):
            a, b = tour[i], tour[(i + 1) % n]
            tau[a][b] += amount
            tau[b][a] += amount
