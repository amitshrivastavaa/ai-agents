"""Demo: weak stumps, boosted into a sharp non-linear fit.

    python -m labs.boosting.demo
"""
from __future__ import annotations

import math

from .gbm import GradientBoosting, mse
from .regtree import RegTree
from .data import make, split


def curve(gb, truth_fn, X, lo=-3.0, hi=3.0, w=58, h=13):
    xs = [lo + (hi - lo) * i / (w - 1) for i in range(w)]
    pred = [gb.predict([[x]])[0] for x in xs]
    true = [truth_fn(x) for x in xs]
    ylo = min(min(pred), min(true)) - 0.2
    yhi = max(max(pred), max(true)) + 0.2

    def row(v):
        return round((v - ylo) / (yhi - ylo) * (h - 1))

    grid = [[" "] * w for _ in range(h)]
    for c in range(w):
        r = row(true[c])
        if 0 <= r < h:
            grid[h - 1 - r][c] = "·"
    for c in range(w):
        r = row(pred[c])
        if 0 <= r < h:
            grid[h - 1 - r][c] = "━"
    return ["  |" + "".join(r) + "|" for r in grid]


def main() -> int:
    truth_fn = lambda x: math.sin(1.5 * x)
    X, y, _ = make("sine", n=240, noise=0.08, seed="demo")
    Xtr, ytr, Xte, yte = split(X, y, seed="demo")

    gb = GradientBoosting(n_estimators=150, learning_rate=0.1, max_depth=2).fit(Xtr, ytr)
    stump = RegTree(max_depth=2).fit(Xtr, ytr)

    print("Gradient boosting — the engine behind XGBoost / LightGBM.\n")
    print("Each new tree fits the *residual* (where the ensemble is still wrong) —")
    print("gradient descent in function space. 150 shallow stumps, composed:\n")
    print("  · = true sin(1.5x)   ━ = boosted ensemble")
    for line in curve(gb, truth_fn, X):
        print(line)

    print(f"\n  one depth-2 stump  : test MSE {mse(stump.predict(Xte), yte):.3f}  (can't bend)")
    print(f"  150-stump boosting : test MSE {mse(gb.predict(Xte), yte):.3f}  "
          f"({mse(stump.predict(Xte), yte) / mse(gb.predict(Xte), yte):.0f}× better)\n")

    print("Residuals shrink with every tree (training MSE, gradient descent):")
    tl = gb.train_loss
    for k in (1, 5, 15, 50, 150):
        bar = "█" * round(40 * tl[k - 1] / tl[0])
        print(f"   {k:>3} trees  {bar:<40} {tl[k - 1]:.3f}")

    print("\nShrinkage — the learning rate trades trees for caution:")
    for lr in (0.5, 0.1, 0.03):
        g = GradientBoosting(n_estimators=200, learning_rate=lr, max_depth=2).fit(Xtr, ytr)
        print(f"   lr={lr:<4}  train MSE {mse(g.predict(Xtr), ytr):.3f}  "
              f"test MSE {mse(g.predict(Xte), yte):.3f}")
    print("\n  A big lr reaches a low train error in few trees; a small lr takes more")
    print("  trees but each step is gentler — the regularization knob behind XGBoost.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
