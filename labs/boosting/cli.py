"""CLI for the gradient-boosting lab.

    python -m labs.boosting.cli fit --data sine --trees 150
    python -m labs.boosting.cli trees --data wiggle
"""
from __future__ import annotations

import argparse
import math
import sys

from .gbm import GradientBoosting, mse
from .regtree import RegTree
from .data import make, split

_TRUTH = {
    "step": lambda x: (1.0 if x > 0 else -1.0) + (0.5 if x > 1.5 else 0.0),
    "sine": lambda x: math.sin(1.5 * x),
    "wiggle": lambda x: math.sin(2 * x) + 0.4 * x,
}


def _cmd_fit(args) -> int:
    from .demo import curve
    X, y, _ = make(args.data, n=240, noise=args.noise, seed=args.seed)
    Xtr, ytr, Xte, yte = split(X, y, seed=args.seed)
    gb = GradientBoosting(n_estimators=args.trees, learning_rate=args.lr,
                          max_depth=args.depth).fit(Xtr, ytr)
    stump = RegTree(max_depth=args.depth).fit(Xtr, ytr)
    print(f"# gradient boosting on {args.data!r}  "
          f"({args.trees} depth-{args.depth} trees, lr={args.lr})\n")
    print("  · = truth   ━ = boosted ensemble")
    for line in curve(gb, _TRUTH[args.data], X):
        print(line)
    print(f"\n  single weak learner test MSE {mse(stump.predict(Xte), yte):.3f}  →  "
          f"boosting {mse(gb.predict(Xte), yte):.3f}")
    return 0


def _cmd_trees(args) -> int:
    X, y, _ = make(args.data, n=240, noise=args.noise, seed=args.seed)
    Xtr, ytr, Xte, yte = split(X, y, seed=args.seed)
    gb = GradientBoosting(n_estimators=200, learning_rate=args.lr,
                          max_depth=args.depth).fit(Xtr, ytr)
    print(f"# test MSE vs number of trees on {args.data!r}\n")
    stages = [1, 2, 5, 10, 25, 50, 100, 200]
    staged = gb.staged_predict(Xte, stages)
    hi = mse(staged[1], yte)
    for k in stages:
        m = mse(staged[k], yte)
        print(f"  {k:>3} trees  {'█' * round(40 * m / hi):<40} {m:.3f}")
    print("\n  each tree fits the leftover residual; the fit sharpens then plateaus.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="boosting", description="Gradient boosting from scratch.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("fit", help="fit + plot a 1-D function")
    p.add_argument("--data", default="sine", choices=list(_TRUTH))
    p.add_argument("--trees", type=int, default=150)
    p.add_argument("--lr", type=float, default=0.1)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--noise", type=float, default=0.08)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_fit)

    p = sub.add_parser("trees", help="MSE vs number of trees")
    p.add_argument("--data", default="sine", choices=list(_TRUTH))
    p.add_argument("--lr", type=float, default=0.1)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--noise", type=float, default=0.08)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_trees)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
