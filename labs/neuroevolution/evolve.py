"""An evolution strategy that breeds CartPole controllers — no gradients.

Each generation: score every candidate by how long it balances (averaged over a
few episodes with shared seeds for a fair comparison), keep the elite, and fill
the rest of the population with mutated copies of good parents.
"""
from __future__ import annotations

from dataclasses import dataclass

from .._kernel import rng
from .cartpole import CartPole
from .policy import Policy, param_count


@dataclass
class EvolveResult:
    best_policy: Policy
    best_fitness: float
    history: list[float]          # best fitness per generation
    generations: int
    hidden: int


def fitness(policy: Policy, *, gen: int, episodes: int = 3, max_steps: int = 500) -> float:
    env = CartPole(max_steps=max_steps)
    total = 0
    for e in range(episodes):
        total += env.rollout(policy, seed=f"ep-{gen}-{e}")
    return total / episodes


def _mutate(params: list[float], sigma: float, r) -> list[float]:
    return [p + r.gauss(0.0, sigma) for p in params]


def evolve(*, population: int = 24, generations: int = 18, hidden: int = 6,
           sigma: float = 0.5, elite: int = 3, episodes: int = 3,
           max_steps: int = 500, seed: str = "evo") -> EvolveResult:
    r = rng(seed, "init")
    n = param_count(hidden)
    pop = [[r.gauss(0.0, 0.5) for _ in range(n)] for _ in range(population)]

    best_params, best_fit = pop[0], -1.0
    history: list[float] = []

    for gen in range(generations):
        scored = sorted(
            ((params, fitness(Policy(params, hidden), gen=gen, episodes=episodes,
                              max_steps=max_steps)) for params in pop),
            key=lambda pf: pf[1], reverse=True,
        )
        if scored[0][1] > best_fit:
            best_params, best_fit = list(scored[0][0]), scored[0][1]
        history.append(scored[0][1])

        # next generation: elites carried over, rest are mutated good parents
        nxt = [list(p) for p, _ in scored[:elite]]
        mr = rng(seed, "mutate", gen)
        rate = sigma * (1.0 / (1.0 + 0.05 * gen))   # anneal the mutation size
        while len(nxt) < population:
            parent = scored[mr.randrange(elite * 2)][0]   # tournament among the top
            nxt.append(_mutate(parent, rate, mr))
        pop = nxt

    return EvolveResult(Policy(best_params, hidden), best_fit, history, generations, hidden)
