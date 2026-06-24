"""Tournaments and evolution over IPD strategies.

* :func:`tournament` — Axelrod round-robin among named strategies.
* :func:`replicator` — replicator dynamics: a population's strategy *mix*
  shifts toward whatever is scoring above average. Watch cooperation take over.
* :func:`coevolve_memory1` — a genetic algorithm over memory-one genomes that
  co-evolve against each other; it can rediscover Tit-for-Tat / Pavlov.
"""
from __future__ import annotations

from .._kernel import rng
from .game import play_match
from .strategies import DETERMINISTIC, Memory1, STRATEGIES, get_strategy


# ------------------------------- tournament ----------------------------------
def tournament(names: list[str] | None = None, *, rounds: int = 100,
               seed: str = "tourney") -> list[dict]:
    names = names or list(STRATEGIES)
    fns = [(n, get_strategy(n)) for n in names]
    totals = {n: 0 for n in names}
    coops = {n: 0 for n in names}
    games = {n: 0 for n in names}
    for i, (na, fa) in enumerate(fns):
        for j, (nb, fb) in enumerate(fns):
            r = rng(seed, "match", na, nb, i, j)
            sa, _, ca, _ = play_match(fa, fb, rounds, r)
            totals[na] += sa
            coops[na] += ca
            games[na] += 1
    ranked = []
    for n in names:
        ranked.append({
            "name": n,
            "avg_per_round": totals[n] / (games[n] * rounds),
            "coop_rate": coops[n] / (games[n] * rounds),
            "total": totals[n],
        })
    ranked.sort(key=lambda d: d["avg_per_round"], reverse=True)
    return ranked


# ---------------------------- replicator dynamics ----------------------------
def replicator(names: list[str] | None = None, *, generations: int = 40,
               rounds: int = 80, seed: str = "rep") -> list[dict]:
    names = names or list(DETERMINISTIC)
    fns = [get_strategy(n) for n in names]
    k = len(names)
    # average per-round payoff of i playing j
    M = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            r = rng(seed, "M", names[i], names[j])
            sa, _, _, _ = play_match(fns[i], fns[j], rounds, r)
            M[i][j] = sa / rounds
    frac = [1.0 / k] * k
    history = [dict(zip(names, frac))]
    for _ in range(generations):
        fitness = [sum(frac[j] * M[i][j] for j in range(k)) for i in range(k)]
        avg = sum(frac[i] * fitness[i] for i in range(k)) or 1.0
        frac = [max(0.0, frac[i] * fitness[i] / avg) for i in range(k)]
        s = sum(frac) or 1.0
        frac = [f / s for f in frac]
        history.append(dict(zip(names, frac)))
    return history


# --------------------------- memory-1 co-evolution ---------------------------
def _random_mem1(r) -> Memory1:
    return Memory1(*[r.random() for _ in range(5)])


def _crossover(a: Memory1, b: Memory1, r) -> Memory1:
    ga, gb = a.genome(), b.genome()
    return Memory1(*[ga[i] if r.random() < 0.5 else gb[i] for i in range(5)])


def _mutate(m: Memory1, rate: float, r) -> Memory1:
    g = list(m.genome())
    for i in range(5):
        if r.random() < rate:
            g[i] = min(1.0, max(0.0, g[i] + r.uniform(-0.35, 0.35)))
    return Memory1(*g)


def _roulette(pop, scores, total, r):
    x = r.random() * total
    acc = 0.0
    for idx, s in enumerate(scores):
        acc += s
        if acc >= x:
            return pop[idx]
    return pop[-1]


def coevolve_memory1(*, pop_size: int = 30, generations: int = 30, rounds: int = 40,
                     mutation: float = 0.12, elite: int = 2,
                     seed: str = "coevo") -> list[dict]:
    pop = [_random_mem1(rng(seed, "init", i)) for i in range(pop_size)]
    history: list[dict] = []
    for gen in range(generations):
        scores = [0.0] * pop_size
        coop_moves = 0
        total_moves = 0
        for i in range(pop_size):
            for j in range(i, pop_size):
                r = rng(seed, "match", gen, i, j)
                sa, sb, ca, cb = play_match(pop[i], pop[j], rounds, r)
                scores[i] += sa
                scores[j] += sb
                coop_moves += ca + cb
                total_moves += 2 * rounds
        order = sorted(range(pop_size), key=lambda x: scores[x], reverse=True)
        best = pop[order[0]]
        history.append({
            "gen": gen,
            "avg_coop": coop_moves / total_moves,
            "best_score": scores[order[0]],
            "best_genome": tuple(round(x, 2) for x in best.genome()),
            "nearest": best.nearest_named(),
        })
        # next generation: elitism + fitness-proportional crossover + mutation
        total = sum(scores) or 1.0
        newpop = [pop[order[t]] for t in range(elite)]
        slot = elite
        while len(newpop) < pop_size:
            pa = _roulette(pop, scores, total, rng(seed, "selA", gen, slot))
            pb = _roulette(pop, scores, total, rng(seed, "selB", gen, slot))
            child = _crossover(pa, pb, rng(seed, "cx", gen, slot))
            child = _mutate(child, mutation, rng(seed, "mut", gen, slot))
            newpop.append(child)
            slot += 1
        pop = newpop
    return history
