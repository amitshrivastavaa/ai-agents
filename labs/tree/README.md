# tree — a decision tree (CART), from scratch

> The most interpretable classifier there is: a cascade of yes/no questions
> ("is feature 3 ≤ 0.7?") that carves feature space into rectangles, each labeled
> by majority vote. Greedily pick the split that most reduces **impurity** (Gini
> or entropy), recurse, repeat. Each cut is axis-aligned, yet stacking them models
> curved, non-linear boundaries a single linear classifier can't — and it's the
> building block of random forests and gradient boosting (XGBoost).

Pure stdlib, deterministic. The supervised companion to the lab's
[`kmeans`](../kmeans/) and [`pca`](../pca/).

## Quick start

```sh
python -m labs.tree.demo
python -m labs.tree.cli classify --data moons --depth 7
python -m labs.tree.cli sweep --data xor
```

```
Two interleaving 'moons' (o/#) — a curved boundary from straight cuts:
  |·················o·o···········░░░░░░░░░░|
  |······o·oooooooooo·············░░░░░░░░░░|
  |····oo·ooo···░░####░░░·oooo····░░##░░░░░░|
  |·············░░░░##########░###░#░░░░░░░░|   ← axis-aligned staircase
  train 100%, test 94%   (depth 7, 15 leaves)
```

## How it works (`tree.py`)

- **Impurity** — `gini(y) = 1 − Σ pₖ²` or `entropy(y) = −Σ pₖ log₂ pₖ`. Zero for a
  pure node, maximal for a uniform mix.
- **Best split** — for every feature and every midpoint threshold, compute the
  weighted impurity of the two children; keep the split with the largest
  **information gain** (parent impurity − children impurity).
- **Recurse** until a node is pure, hits `max_depth`/`min_samples`, or no split
  helps; label each leaf by majority vote. Prediction walks the questions down to
  a leaf.

## What it shows

- **Carves non-linear boundaries** — on two interleaving moons it builds a
  staircase boundary and generalizes (~94% test); multiclass 3-blob data is
  separated perfectly in 3 leaves.
- **The bias/variance dial** — the depth sweep shows train accuracy climbing to
  100% while test accuracy peaks and then the gap widens: textbook overfitting,
  visible in one table.
- **Beats linear on XOR** — a linear model is stuck at ~50% on XOR; the tree
  reaches ~100%. (Honest detail: XOR's *first* split has near-zero gain, so greedy
  CART needs a few levels to find the checkerboard — the well-known myopia that
  ensembles fix.)
- **Deterministic** — same data, same tree.

## Tests

```sh
python -m unittest labs.tree.tests.test_tree -v
```

9 tests: Gini/entropy values, separable blobs classified ~perfectly, a pure node
is a single leaf, moons generalizes (>85%), deeper trees fit training monotonically
better, XOR is ~chance at depth 1 and solved by depth 6, prediction shape, and
determinism.
