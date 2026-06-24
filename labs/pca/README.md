# pca — Principal Component Analysis (find the axes that matter)

> The workhorse of dimensionality reduction: find the directions your data
> *actually* varies along, and keep only those. Centre the data, form its
> covariance, and pull out the top eigenvectors — the **principal components**.
> Projecting onto the first few is the **optimal linear compression** (it
> minimizes reconstruction error for that many dimensions), and the variance
> they explain reveals the data's true dimensionality.

Built from scratch with **power iteration + deflation** (no numpy). Pure stdlib,
deterministic. Pairs with the lab's [`lsh`](../lsh/) (vectors) and [`gp`](../gp/).

## Quick start

```sh
python -m labs.pca.demo
python -m labs.pca.cli axes
python -m labs.pca.cli scree --rank 3 --dim 40
```

```
A 2-D cloud (·) with PC1 (█) drawn through the mean:
  |     · ··█████······    |
  |  ···████······         |
  PC1 explains 96% of the variance, PC2 just 4%.
  PC1 aligns with the true stretch axis to 1.000 (exact).

Compression — 40-D vectors that secretly live in a 3-D subspace:
     k   cumulative variance   reconstruction MSE
     1   ██████████            1.83
     3   ██████████████████████ 0.03   ← the elbow: true dimensionality
```

## How it works

- **Covariance** (`linalg.py`): centre the data and form the `d×d` covariance
  matrix — its eigenvectors are the principal axes, its eigenvalues the variance
  along each.
- **Power iteration**: repeatedly multiply a vector by the covariance and
  renormalize; it converges to the top eigenvector. **Deflation** subtracts that
  component off (`C ← C − λvvᵀ`) so the next iteration finds the second, and so on.
- **Project & reconstruct** (`pca.py`): `transform` projects centred data onto the
  components; `inverse_transform` rebuilds it. Keep `k` components → the best
  rank-`k` approximation of every point.

## What it shows

- **It recovers the real axes.** On a 2-D cloud stretched along a known
  direction, PC1 matches that axis to 1.000 and explains ~96% of the variance;
  the components come out orthonormal.
- **It finds the true dimensionality.** For 40-D vectors that secretly live in a
  3-D subspace, the reconstruction error falls off a cliff at **k=3** and the
  scree plot's variance collapses there — PCA *discovers* the rank.
- **It's the optimal linear compressor.** Its rank-`k` reconstruction beats
  keeping any `k` raw coordinates.
- **Exact & deterministic** — full-rank reconstruction is lossless; same seed,
  same components.

## Tests

```sh
python -m unittest labs.pca.tests.test_pca -v
```

9 tests: PC1 recovers the known axis, components are orthonormal, explained
variance is descending and ≤ 1 with the stretched axis dominating, reconstruction
error is monotone in `k`, rank-many components capture >95% variance, full-rank
reconstruction is near-exact, PCA beats a raw-coordinate subspace, and it's
deterministic.
