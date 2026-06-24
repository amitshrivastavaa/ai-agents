"""CLI for the logistic-regression lab.

    python -m labs.logreg.cli fit --data linear
    python -m labs.logreg.cli loss
"""
from __future__ import annotations

import argparse
import sys

from .logreg import LogisticRegression
from .data import linear, moons, split
from .demo import boundary, spark

_DATA = {"linear": linear, "moons": moons}


def _acc(yh, y):
    return sum(1 for a, b in zip(yh, y) if a == b) / len(y)


def _cmd_fit(args) -> int:
    X, y = _DATA[args.data](n=400, seed=args.seed)
    Xtr, ytr, Xte, yte = split(X, y, seed=args.seed)
    m = LogisticRegression(lr=args.lr, epochs=args.epochs, l2=args.l2).fit(Xtr, ytr)
    print(f"# logistic regression on {args.data!r}  (lr={args.lr}, epochs={args.epochs}, l2={args.l2})\n")
    for line in boundary(m, X, y):
        print(line)
    print(f"\n  test accuracy {_acc(m.predict(Xte), yte) * 100:.0f}%   "
          f"w=({m.w[0]:+.2f}, {m.w[1]:+.2f})  b={m.b:+.2f}  loss {m.loss_history[-1]:.3f}")
    return 0


def _cmd_loss(args) -> int:
    X, y = _DATA[args.data](n=400, seed=args.seed)
    Xtr, ytr, _, _ = split(X, y, seed=args.seed)
    m = LogisticRegression(lr=args.lr, epochs=args.epochs).fit(Xtr, ytr)
    lh = m.loss_history
    pts = [lh[min(len(lh) - 1, round(i * (len(lh) - 1) / 49))] for i in range(50)]
    print(f"# cross-entropy loss over {args.epochs} epochs ({args.data!r})\n")
    print("  " + spark(pts))
    print(f"\n  {lh[0]:.3f} → {lh[-1]:.3f}   monotone (convex): "
          f"{all(lh[i] >= lh[i + 1] - 1e-9 for i in range(len(lh) - 1))}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="logreg", description="Logistic regression by gradient descent.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("fit", help="fit + plot the linear boundary")
    p.add_argument("--data", default="linear", choices=list(_DATA))
    p.add_argument("--lr", type=float, default=0.5)
    p.add_argument("--epochs", type=int, default=300)
    p.add_argument("--l2", type=float, default=0.0)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_fit)

    p = sub.add_parser("loss", help="the convex loss curve")
    p.add_argument("--data", default="linear", choices=list(_DATA))
    p.add_argument("--lr", type=float, default=0.5)
    p.add_argument("--epochs", type=int, default=300)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_loss)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
