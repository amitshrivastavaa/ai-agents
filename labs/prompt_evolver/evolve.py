"""The genetic algorithm: selection, order-aware crossover, mutation, elitism.

A *genome* is an ordered list of directive ids (no duplicates) — i.e. a prompt.
Everything is seeded through ``labs/_kernel``'s deterministic RNG, so a given
``(task, seed)`` evolves identically every run.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .._kernel import mode, rng


@dataclass
class Result:
    task_id: str
    best_genome: list[str]
    best_fitness: float
    baseline_genome: list[str]
    baseline_fitness: float
    history: list[tuple[float, float]]  # (best, mean) per generation
    generations: int
    population: int
    run_mode: str
    rendered_prompt: str = ""

    @property
    def improvement(self) -> float:
        return self.best_fitness - self.baseline_fitness


def _random_genome(vocab: list[str], r) -> list[str]:
    k = r.randint(0, len(vocab))
    g = r.sample(vocab, k)
    return g


def _tournament(scored: list[tuple[list[str], float]], r, size: int = 3) -> list[str]:
    contenders = [scored[r.randrange(len(scored))] for _ in range(size)]
    return list(max(contenders, key=lambda s: s[1])[0])


def _crossover(a: list[str], b: list[str], r) -> list[str]:
    """One-point crossover on ordered genomes, then de-dupe keeping first seen."""
    if not a:
        return list(b)
    if not b:
        return list(a)
    child = a[: r.randint(0, len(a))] + b[r.randint(0, len(b)):]
    seen: set[str] = set()
    out: list[str] = []
    for x in child:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _mutate(g: list[str], vocab: list[str], r) -> list[str]:
    g = list(g)
    op = r.choice(("add", "remove", "swap", "add"))  # bias toward exploring additions
    if op == "add":
        missing = [v for v in vocab if v not in g]
        if missing:
            g.insert(r.randint(0, len(g)), r.choice(missing))
    elif op == "remove" and g:
        g.pop(r.randrange(len(g)))
    elif op == "swap" and len(g) >= 2:
        i, j = r.randrange(len(g)), r.randrange(len(g))
        g[i], g[j] = g[j], g[i]
    return g


def evolve(
    task,
    *,
    population: int = 30,
    generations: int = 25,
    elite: int = 3,
    mutation_rate: float = 0.35,
    seed: str = "evolve",
    brain=None,
) -> Result:
    """Evolve a prompt for ``task`` and return the best found plus its history."""
    vocab = list(task.directives)
    r = rng(seed, task.id, population, generations)

    cache: dict[tuple[str, ...], float] = {}

    def fitness(g: list[str]) -> float:
        key = tuple(g)
        if key not in cache:
            cache[key] = task.evaluate(g, brain)
        return cache[key]

    baseline = task.baseline()
    base_fit = fitness(baseline)

    pop = [_random_genome(vocab, r) for _ in range(population)]
    pop[0] = baseline  # always seed the baseline so we can only improve on it

    history: list[tuple[float, float]] = []
    best_overall: list[str] = baseline
    best_overall_fit = base_fit

    for _ in range(generations):
        scored = sorted(((g, fitness(g)) for g in pop), key=lambda s: s[1], reverse=True)
        gen_best, gen_best_fit = scored[0]
        gen_mean = sum(f for _, f in scored) / len(scored)
        history.append((gen_best_fit, gen_mean))
        if gen_best_fit > best_overall_fit:
            best_overall, best_overall_fit = list(gen_best), gen_best_fit

        nxt: list[list[str]] = [list(g) for g, _ in scored[:elite]]
        while len(nxt) < population:
            child = _crossover(_tournament(scored, r), _tournament(scored, r), r)
            if r.random() < mutation_rate:
                child = _mutate(child, vocab, r)
            nxt.append(child)
        pop = nxt

    return Result(
        task_id=task.id,
        best_genome=best_overall,
        best_fitness=best_overall_fit,
        baseline_genome=baseline,
        baseline_fitness=base_fit,
        history=history,
        generations=generations,
        population=population,
        run_mode="online" if brain is not None else mode(),
        rendered_prompt=task.render(best_overall),
    )
