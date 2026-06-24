# boosting — gradient boosting, from scratch

> The method that wins tabular ML (XGBoost, LightGBM, CatBoost). Where a random
> forest builds trees *in parallel* and averages them, **gradient boosting** builds
> them *sequentially* — each new tree fits the **residual**, the part the ensemble
> still gets wrong, and is added (shrunk by a learning rate) to the prediction. For
> squared loss the residual is exactly the negative gradient of the loss, so each
> tree is one step of **gradient descent in function space**. A pile of weak stumps,
> each fixing the last one's mistakes, becomes a sharp non-linear fit.

Self-contained (its own small `RegTree`). Offline, deterministic. Completes the
tree thread: [`tree`](../tree/) → [`forest`](../forest/) (bagging) → **boosting**.

## Quick start

```sh
python -m labs.boosting.demo
python -m labs.boosting.cli fit --data wiggle --trees 150
python -m labs.boosting.cli trees --data sine
```

```
  · = true sin(1.5x)   ━ = boosted ensemble
  |━━━━                                ━━━━━━   |
  |    ··                          ━━          |
  |       ━                     ━━             |   the stumps trace the curve
  |               ━━━━━━━                    ━━━|

  one depth-2 stump  : test MSE 0.109  (can't bend)
  150-stump boosting : test MSE 0.009  (12× better)
```

## How it works (`gbm.py`)

```
F₀(x) = mean(y)
repeat for m = 1..M:
    rᵢ   = yᵢ − F(xᵢ)                  # residual = −∂ ½(y−F)² / ∂F  (neg. gradient)
    hₘ   = regression tree fit to r    # one descent direction
    F(x) += learning_rate · hₘ(x)      # a shrunk step
```

The weak learner is a shallow `RegTree` (`regtree.py`) that splits to minimize the
children's summed squared error and predicts leaf means. Stacking ~150 of them at
depth 2 turns a learner that *can't bend* into one that traces `sin(1.5x)` to the
noise floor.

## What it shows

- **Weak → strong.** A single depth-2 stump gets ~0.1 test MSE on a sine; 150
  boosted stumps reach ~0.009 — an order of magnitude better.
- **Monotone descent.** Training MSE falls with every tree (1.0 → ~0.002) — that's
  the "gradient descent in function space" made literal, and the test fit sharpens
  then plateaus.
- **Shrinkage.** The learning rate is the regularization knob: a big rate reaches
  low train error in few trees; a small rate takes more trees but steps gently —
  the trade-off XGBoost exposes as `eta` × `n_estimators`.
- **Deterministic** — same data, same ensemble.

## Tests

```sh
python -m unittest labs.boosting.tests.test_boosting -v
```

8 tests: the regression tree handles a constant and captures a step in one split;
boosting's training loss is monotone, it beats a single weak learner by >3×, more
trees lower the error, it fits a noisy function to the noise floor, `staged_predict`
returns the right stages, and it's deterministic.
