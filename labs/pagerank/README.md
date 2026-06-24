# pagerank — the eigenvector that ranked the web

> PageRank scores a page by the long-run fraction of time a **random surfer**
> spends on it: with probability `d` it follows a random out-link, otherwise it
> teleports to a random page. That stationary distribution is the dominant
> eigenvector of the "Google matrix", and **power iteration** from the uniform
> vector converges straight to it. This MVP computes it — and *proves* it two
> independent ways agree.

Foundational graph centrality (and the ancestor of modern graph-embedding and
GNN ideas). Offline, deterministic. Companion to the lab's
[`repo_cartographer`](../repo_cartographer/).

## Quick start

```sh
python -m labs.pagerank.demo
python -m labs.pagerank.cli rank --graph communities
python -m labs.pagerank.cli verify --graph web
python -m labs.pagerank.cli damping --graph web
```

```
PageRank (power iteration, converged in 56 steps):
      C  ██████████████████████████████████ 0.394   ← linked by A, B, D
      A  ████████████████████████████████   0.373
      B  █████████████████                  0.196
      D  ███                                0.038   ← nobody links to D
```

## How it works

PageRank `r` is the fixed point (`rank.py`):

```
r[p] = (1−d)/N  +  d · ( Σ_{q→p} r[q]/outdeg(q)  +  dangling_mass/N )
```

- The `(1−d)/N` term is the **teleport** (random jump), which guarantees the walk
  is ergodic and the iteration converges to a unique answer.
- `Σ r[q]/outdeg(q)` is **rank flowing in** along links — a page is important if
  important pages point to it.
- **Dangling nodes** (no out-links) would leak probability; their mass is
  redistributed uniformly so `r` stays a distribution.

Iterating that map from the uniform vector is **power iteration** on the Google
matrix — it converges geometrically (here, ~56 steps to 1e-12).

## Proven two ways

`surfer.py` runs the literal **random surfer** as a Monte-Carlo walk and counts
visits. Its visit frequencies match the power-iteration ranks to **~0.001** on
every graph — because PageRank *is* that walk's stationary distribution. Two
completely different computations, the same vector.

The **damping** factor `d` interpolates between them: `d=0` is pure teleport
(uniform ranks); `d→1` lets the link structure dominate (and risks rank sinks
without the teleport safety net).

## Tests

```sh
python -m unittest labs.pagerank.tests.test_pagerank -v
```

8 tests: ranks form a positive distribution on every graph, power iteration
converges, the expected node wins/loses on the classic web, PageRank matches the
random surfer, `d=0` is uniform, dangling nodes keep the sum at 1, more in-links
mean more rank, and it's deterministic.
