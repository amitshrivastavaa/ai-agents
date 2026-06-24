"""CLI for the PCA lab.

    python -m labs.pca.cli axes
    python -m labs.pca.cli scree --rank 3 --dim 40
"""
from __future__ import annotations

import argparse
import sys

from .pca import PCA
from .data import correlated_2d, low_rank
from .linalg import dot


def _cmd_axes(args) -> int:
    pts, axis = correlated_2d(n=400, angle=args.angle, seed=args.seed)
    p = PCA(2).fit(pts)
    evr = p.explained_variance_ratio
    print(f"# principal axes of a 2-D cloud (true angle {args.angle})\n")
    print(f"  PC1 = ({p.components[0][0]:+.3f}, {p.components[0][1]:+.3f})   "
          f"explains {evr[0] * 100:.1f}%")
    print(f"  PC2 = ({p.components[1][0]:+.3f}, {p.components[1][1]:+.3f})   "
          f"explains {evr[1] * 100:.1f}%")
    print(f"\n  PC1 · true-axis = {abs(dot(p.components[0], axis)):.4f}   "
          f"PC1 · PC2 = {dot(p.components[0], p.components[1]):+.1e}")
    return 0


def _cmd_scree(args) -> int:
    X = low_rank(n=200, dim=args.dim, rank=args.rank, noise=args.noise, seed=args.seed)
    p = PCA(min(args.dim, 12)).fit(X)
    evr = p.explained_variance_ratio
    print(f"# scree plot — {args.dim}-D data of true rank {args.rank}\n")
    cum = 0.0
    for i, r in enumerate(evr):
        cum += r
        bar = "█" * round(40 * r)
        print(f"  PC{i + 1:<2} {bar:<40} {r * 100:5.1f}%  (cum {cum * 100:5.1f}%)")
    print(f"\n  variance collapses after PC{args.rank} — the true dimensionality.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pca", description="Principal Component Analysis from scratch.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("axes", help="principal axes of a 2-D cloud")
    p.add_argument("--angle", type=float, default=0.5)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_axes)

    p = sub.add_parser("scree", help="variance explained per component")
    p.add_argument("--dim", type=int, default=40)
    p.add_argument("--rank", type=int, default=3)
    p.add_argument("--noise", type=float, default=0.03)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_scree)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
