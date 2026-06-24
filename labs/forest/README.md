# forest — a random forest, from scratch

> One decision tree is a high-variance learner: it overfits, and a small change
> in the data swings it a lot. A **random forest** fixes that with two doses of
> randomness — **bagging** (each tree trains on a bootstrap resample) and
> **feature subsampling** (each split sees only a random feature subset) — so the
> trees overfit in *different* directions. Vote them together and the noise
> cancels: more accurate, far more stable, and with a validation score thrown in
> for free.

Literally an ensemble of the lab's [`tree`](../tree/) `DecisionTree` (extended
with `max_features`). Offline, deterministic. Caps the tree thread:
`tree` → `forest`.

## Quick start

```sh
python -m labs.forest.demo
python -m labs.forest.cli compare --data moons
python -m labs.forest.cli trees --data moons
```

```
  single tree test accuracy : 94.2%
  forest      test accuracy : 97.5%
  forest out-of-bag accuracy: 96.8%   (validation for free)

More trees → less variance (mean ± std over 10 splits):
    1 trees   94.6% ± 2.7
   15 trees   97.6% ± 1.1
   40 trees   98.0% ± 1.2
```

## How it works (`forest.py`)

- **Bagging** — for each of `n_trees`, draw a bootstrap sample (n points *with
  replacement*) and train a tree on it. ~37% of points are left out of each tree.
- **Feature subsampling** — each tree's splits consider only `√d` random features
  (`max_features="sqrt"`, added to `DecisionTree`), decorrelating the trees so
  their errors are more independent.
- **Vote** — predict by majority over all trees. Averaging independent overfits
  cancels their variance — the bias/variance trade-off, won by ensembling.
- **Out-of-bag score** — each point is predicted using only the trees that *didn't*
  train on it, giving an honest validation estimate with **no held-out set**.

## What it shows

- **Beats the single tree** — on noisy moons the forest reaches ~97–98% vs ~94%
  for one tree, winning the large majority of random splits.
- **Variance collapses with more trees** — the std of test accuracy roughly halves
  going from 1 → 25 trees, while the mean rises and then plateaus.
- **OOB ≈ test** — the free out-of-bag estimate tracks held-out test accuracy to
  within a couple of points.
- **Still solves XOR** and separates multiclass blobs near-perfectly.
- **Deterministic** — seeded bootstraps + seeded trees, identical every run.

## Tests

```sh
python -m unittest labs.forest.tests.test_forest -v
```

7 tests: blobs near-perfect, the forest beats a single tree on average, more trees
reduce variance, OOB tracks test accuracy, XOR is solved, prediction shape, and
determinism.
