"""CLI for the k-means lab.

    python -m labs.kmeans.cli cluster --k 4
    python -m labs.kmeans.cli compare
    python -m labs.kmeans.cli elbow
"""
from __future__ import annotations

import argparse
import sys

from .data import blobs
from .kmeans import KMeans
from .metrics import purity, best_of, elbow
from .demo import scatter


def _cmd_cluster(args) -> int:
    X, true, _ = blobs(n=400, k=args.true_k, spread=args.spread, seed=args.seed)
    km = best_of(X, k=args.k, restarts=5, seed=args.seed)
    print(f"# k-means (k={args.k}) on {args.true_k} blobs\n")
    for line in scatter(X, km.labels, km.centroids):
        print(line)
    print(f"\n  purity {purity(km.labels, true, args.k) * 100:.0f}%   "
          f"inertia {km.inertia:.0f}   {km.n_iter} iters")
    return 0


def _cmd_compare(args) -> int:
    X, _, _ = blobs(n=400, k=4, spread=0.5, seed=args.seed)
    print(f"# k-means++ vs random init  (k=4, {args.runs} seeds)\n")
    for init in ("kmeans++", "random"):
        vals = [KMeans(k=4, init=init, seed=(init, s)).fit(X).inertia
                for s in range(args.runs)]
        print(f"  {init:9s}  mean {sum(vals) / len(vals):7.0f}  "
              f"best {min(vals):7.0f}  worst {max(vals):7.0f}")
    print("\n  k-means++ spreads the seeds → lower, more reliable inertia.")
    return 0


def _cmd_elbow(args) -> int:
    X, _, _ = blobs(n=400, k=args.true_k, spread=0.5, seed=args.seed)
    print(f"# elbow method  ({args.true_k} true blobs)\n")
    el = elbow(X, ks=range(1, 9), seed=args.seed)
    hi = el[0][1]
    for k, inertia in el:
        print(f"  k={k}  {'█' * round(42 * inertia / hi):<42} {inertia:6.0f}")
    print(f"\n  the kink at k={args.true_k} is the natural number of clusters.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="kmeans", description="k-means clustering with k-means++ and the elbow method.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("cluster", help="cluster blobs and show purity")
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--true-k", type=int, default=4)
    p.add_argument("--spread", type=float, default=0.5)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_cluster)

    p = sub.add_parser("compare", help="k-means++ vs random init")
    p.add_argument("--runs", type=int, default=20)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_compare)

    p = sub.add_parser("elbow", help="inertia vs k")
    p.add_argument("--true-k", type=int, default=4)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_elbow)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
