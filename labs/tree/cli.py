"""CLI for the decision-tree lab.

    python -m labs.tree.cli classify --data moons --depth 7
    python -m labs.tree.cli sweep --data moons
"""
from __future__ import annotations

import argparse
import sys

from .tree import DecisionTree
from .data import DATASETS, train_test_split
from .metrics import accuracy, depth_sweep
from .demo import boundary


def _cmd_classify(args) -> int:
    X, y = DATASETS[args.data](n=args.n, seed=args.seed)
    Xtr, ytr, Xte, yte = train_test_split(X, y, seed=args.seed)
    t = DecisionTree(max_depth=args.depth, criterion=args.criterion).fit(Xtr, ytr)
    print(f"# decision tree on {args.data!r}  (max_depth={args.depth}, {args.criterion})\n")
    for line in boundary(t, X, y):
        print(line)
    print(f"\n  train {accuracy(t.predict(Xtr), ytr) * 100:.0f}%  "
          f"test {accuracy(t.predict(Xte), yte) * 100:.0f}%  "
          f"depth {t.depth()}  leaves {t.n_leaves()}")
    return 0


def _cmd_sweep(args) -> int:
    X, y = DATASETS[args.data](n=args.n, seed=args.seed)
    Xtr, ytr, Xte, yte = train_test_split(X, y, seed=args.seed)
    print(f"# depth sweep on {args.data!r}\n")
    print(f"   {'depth':>5} {'train':>8} {'test':>8}")
    for d, tr, te in depth_sweep(Xtr, ytr, Xte, yte, depths=range(1, 12)):
        print(f"   {d:>5} {tr * 100:>7.0f}% {te * 100:>7.0f}%")
    print("\n   train ↑ with depth; test peaks then overfits.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="tree", description="A CART decision tree from scratch.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("classify", help="fit + plot the decision boundary")
    p.add_argument("--data", default="moons", choices=list(DATASETS))
    p.add_argument("--depth", type=int, default=7)
    p.add_argument("--n", type=int, default=400)
    p.add_argument("--criterion", default="gini", choices=("gini", "entropy"))
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_classify)

    p = sub.add_parser("sweep", help="train/test accuracy vs depth")
    p.add_argument("--data", default="moons", choices=list(DATASETS))
    p.add_argument("--n", type=int, default=400)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_sweep)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
