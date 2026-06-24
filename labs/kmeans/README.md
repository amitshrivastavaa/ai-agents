# kmeans — k-means clustering (with k-means++ and the elbow)

> Group points by who they're closest to. **Lloyd's algorithm** alternates two
> steps — assign each point to its nearest centroid, then move each centroid to
> its cluster's mean — and each step can only *lower* the total within-cluster
> squared distance (the **inertia**). The catch is where you start: a bad random
> seeding lands in a bad local optimum. **k-means++** fixes that by seeding
> centroids spread out, and the **elbow** in inertia-vs-k reveals how many
> clusters there really are.

Pure stdlib, deterministic. The unsupervised companion to the lab's
[`pca`](../pca/).

## Quick start

```sh
python -m labs.kmeans.demo
python -m labs.kmeans.cli cluster --k 4
python -m labs.kmeans.cli compare
python -m labs.kmeans.cli elbow
```

```
400 points, 4 hidden blobs. k-means++ found them (○◆▲■, @=centroid):
  |        ○○ ○○○○ ○   ▲▲▲▲▲@▲▲▲▲▲ |
  |   ■■■■■@■■■ ■■                  |
  |    ◆◆◆◆@◆◆◆ ◆                   |
  purity vs the true blobs: 99%

How many clusters? The elbow in inertia-vs-k:
   k=2  █████                  780
   k=4  █                      184   ← elbow (true k=4)
   k=5  █                      166
```

## How it works (`kmeans.py`)

- **Lloyd's iteration**: assign → re-mean → repeat until the assignment stops
  changing. Both moves are guaranteed not to raise inertia, so it converges to a
  local optimum (here, ~3 iterations). `history` records the monotone descent.
- **k-means++ init**: the first centroid is a random point; each next one is
  sampled with probability proportional to its **squared distance** to the nearest
  chosen centroid — so seeds land far apart. This is the difference between a
  great clustering and a terrible one (see below).
- **Inertia** = Σ squared distance from each point to its centroid — the objective
  k-means minimizes, and the y-axis of the elbow plot.

## What it shows

- **Recovers the blobs** — on separated 2-D clusters, purity vs the ground-truth
  labels is ~99%.
- **Init decides everything** — over many seeds, k-means++ reaches far lower mean
  *and* worst-case inertia than random init (random regularly falls into bad
  optima; k-means++ rarely does).
- **The elbow finds k** — inertia drops steeply up to the true number of clusters
  and flattens after, so the kink reveals `k` without knowing it in advance.
- **Deterministic** — seeded init, identical clustering every run.

## Tests

```sh
python -m unittest labs.kmeans.tests.test_kmeans -v
```

7 tests: inertia is monotone non-increasing, Lloyd converges before `max_iter`,
separated blobs are recovered (>90% purity), k-means++ beats random init on mean
and worst-case inertia, the elbow bottoms out at the true `k`, labels/centroids
are consistent, and it's deterministic.
