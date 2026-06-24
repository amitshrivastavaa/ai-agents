"""CLI for the conformal-prediction lab.

    python -m labs.conformal.cli coverage --alpha 0.1
    python -m labs.conformal.cli band
"""
from __future__ import annotations

import argparse
import sys

from .data import heteroscedastic, split
from .conformal import calibrate, coverage, mean_width
from .demo import band_plot


def _cmd_coverage(args) -> int:
    X, y = heteroscedastic(n=700, seed=args.seed)
    print(f"# conformal coverage over {args.runs} random splits\n")
    print(f"   {'alpha':>6} {'target':>8} {'measured':>10} {'mean width':>12}")
    for alpha in (0.05, 0.1, 0.2, 0.3):
        covs, widths = [], []
        for s in range(args.runs):
            tr, cal, te = split(X, y, seed=("s", s))
            p = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=alpha, k=args.k)
            covs.append(coverage(p, te[0], te[1]))
            widths.append(mean_width(p, te[0]))
        print(f"   {alpha:>6} {1 - alpha:>8.2f} {sum(covs) / len(covs):>10.3f} "
              f"{sum(widths) / len(widths):>12.2f}")
    print("\n   measured coverage tracks 1−α regardless of α — the guarantee.")
    return 0


def _cmd_band(args) -> int:
    X, y = heteroscedastic(n=700, seed="demo")
    tr, cal, te = split(X, y, seed="ten")
    norm = args.adaptive
    p = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=args.alpha, k=9, normalized=norm)
    kind = "adaptive" if norm else "standard"
    print(f"# {int((1 - args.alpha) * 100)}% conformal band ({kind})  "
          f"(░ band, ━ pred, · covered, × missed)\n")
    for line in band_plot(p, tr[0], tr[1], te[0], te[1]):
        print(line)
    print(f"\n   coverage {coverage(p, te[0], te[1]) * 100:.0f}%  "
          f"mean width {mean_width(p, te[0]):.2f}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="conformal", description="Distribution-free prediction intervals.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("coverage", help="coverage vs alpha over many splits")
    p.add_argument("--alpha", type=float, default=0.1)
    p.add_argument("--runs", type=int, default=40)
    p.add_argument("--k", type=int, default=9)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_coverage)

    p = sub.add_parser("band", help="plot the prediction band")
    p.add_argument("--alpha", type=float, default=0.1)
    p.add_argument("--adaptive", action="store_true", help="noise-adaptive intervals")
    p.set_defaults(func=_cmd_band)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
