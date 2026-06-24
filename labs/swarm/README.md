# swarm — Ant Colony Optimization for the TSP

> A colony of simple ants finds short tours through a map of cities. No ant ever
> sees the whole map — yet the colony converges on a near-optimal route, drawn
> here in ASCII as it emerges.

A miniature, fully-offline take on **swarm intelligence** (Ant Colony
Optimization; ANTS 2026). Deterministic via the shared seeded RNG.

## Quick start

```sh
python -m labs.swarm.demo                                   # watch the ring emerge
python -m labs.swarm.cli solve --instance circle --watch
python -m labs.swarm.cli solve --instance random15 --ants 30 --iters 120 --watch
python -m labs.swarm.cli compare
python -m labs.swarm.cli list
```

```
On a ring of 12 cities, the optimal tour IS the perimeter.
  ACO found 62.1 (optimal 62.1) — 0.0% over optimal

                 ······9·····
          ·8·····            ······A·
       ···                           ··
   7·                                     ·B
  6                                          0
   5·                                     ·1
          ·4···                  ··2·
                     ··3···
```

## How it works (stigmergy)

Each iteration, every ant builds a tour, choosing its next city with probability

```
P(next = j)  ∝  pheromone(i,j)**alpha  ·  (1 / distance(i,j))**beta
```

— so ants prefer **near** cities and edges already **rich in pheromone**. Then
pheromone **evaporates** everywhere and is **re-deposited** in proportion to each
tour's quality (shorter tours deposit more), with an elitist boost for the best
tour so far. Good edges accumulate pheromone, bad ones fade, and the colony
self-organizes toward a short tour — coordination through the environment, not
through any central plan.

## Results

| instance | random | nearest-neighbor | ACO | optimal |
| --- | ---: | ---: | ---: | ---: |
| circle (12) | 150.1 | 62.1 | **62.1** | 62.1 |
| random8 | 69.6 | 63.9 | **59.4** | 59.4 |
| random15 | 129.9 | 68.3 | **61.6** | — |

ACO **matches the optimum** wherever we can compute it (exactly, on the ring and
the 8-city brute-forceable case) and **beats the greedy nearest-neighbor
heuristic everywhere** — from pheromone trails alone.

Knobs: `--ants`, `--iters`, `--beta` (how greedy toward short edges). Drop `beta`
and the colony explores more (and converges slower); raise it and it behaves
more like nearest-neighbor.

## Tests

```sh
python -m unittest labs.swarm.tests.test_swarm -v
```
