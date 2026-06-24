"""CLI for the random-forest lab.

    python -m labs.forest.cli compare --data moons
    python -m labs.forest.cli trees --data moons
"""
from __future__ import annotations

import argparse
import statistics
import sys

from .forest import RandomForest
from ..tree.tree import DecisionTree
from ..tree.data import DATASETS, train_test_split
from ..tree.metrics import accuracy


def _cmd_compare(args) -> int:
    print(f"# forest vs single tree on {args.data!r}  ({args.runs} splits)\n")
    f_acc, t_acc, oob = [], [], []
    for s in range(args.runs):
        X, y = DATASETS[args.data](n=args.n, seed=("c", s))
        Xtr, ytr, Xte, yte = train_test_split(X, y, seed=("c", s))
        f = RandomForest(n_trees=args.trees, max_depth=args.depth, seed=s).fit(Xtr, ytr)
        t = DecisionTree(max_depth=args.depth).fit(Xtr, ytr)
        f_acc.append(accuracy(f.predict(Xte), yte))
        t_acc.append(accuracy(t.predict(Xte), yte))
        oob.append(f.oob_score(Xtr, ytr))
    print(f"  single tree : {sum(t_acc) / len(t_acc) * 100:5.1f}%  ± {statistics.pstdev(t_acc) * 100:.1f}")
    print(f"  forest      : {sum(f_acc) / len(f_acc) * 100:5.1f}%  ± {statistics.pstdev(f_acc) * 100:.1f}")
    print(f"  forest OOB  : {sum(oob) / len(oob) * 100:5.1f}%  (≈ test, validation for free)")
    wins = sum(1 for a, b in zip(f_acc, t_acc) if a >= b)
    print(f"\n  forest ≥ single tree in {wins}/{args.runs} splits.")
    return 0


def _cmd_trees(args) -> int:
    print(f"# accuracy vs number of trees on {args.data!r}\n")
    print(f"   {'trees':>6} {'mean acc':>10} {'std':>7}")
    for nt in (1, 3, 5, 10, 25, 50):
        accs = []
        for s in range(args.runs):
            X, y = DATASETS[args.data](n=args.n, seed=("t", s))
            Xtr, ytr, Xte, yte = train_test_split(X, y, seed=("t", s))
            f = RandomForest(n_trees=nt, max_depth=args.depth, seed=("t", s)).fit(Xtr, ytr)
            accs.append(accuracy(f.predict(Xte), yte))
        print(f"   {nt:>6} {sum(accs) / len(accs) * 100:>9.1f}% {statistics.pstdev(accs) * 100:>6.1f}")
    print("\n  more trees → variance falls, accuracy stabilizes.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="forest", description="A random forest from scratch (bagging + feature subsampling).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("compare", help="forest vs single tree")
    p.add_argument("--data", default="moons", choices=list(DATASETS))
    p.add_argument("--trees", type=int, default=25)
    p.add_argument("--depth", type=int, default=8)
    p.add_argument("--n", type=int, default=400)
    p.add_argument("--runs", type=int, default=12)
    p.set_defaults(func=_cmd_compare)

    p = sub.add_parser("trees", help="accuracy/variance vs number of trees")
    p.add_argument("--data", default="moons", choices=list(DATASETS))
    p.add_argument("--depth", type=int, default=8)
    p.add_argument("--n", type=int, default=400)
    p.add_argument("--runs", type=int, default=10)
    p.set_defaults(func=_cmd_trees)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
