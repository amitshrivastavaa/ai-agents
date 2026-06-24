"""CLI for the Gaussian-process lab.

    python -m labs.gp.cli fit --length 1.0
    python -m labs.gp.cli uncertainty
"""
from __future__ import annotations

import argparse
import math
import sys

from .gp import GP, rbf
from .demo import plot

_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "line": lambda x: 0.3 * x,
}


def _cmd_fit(args) -> int:
    f = _FUNCS[args.func]
    Xtrain = [0.0, 0.6, 1.2, 1.8, 2.4, 7.0, 7.6, 8.2]
    ytrain = [f(x) for x in Xtrain]
    gp = GP(rbf(length=args.length, var=1.0), noise=args.noise).fit(Xtrain, ytrain)
    print(f"# GP fit to {args.func!r}  (lengthscale={args.length}, noise={args.noise})")
    print("  o=data  ━=mean  ·=true  ░=95% band\n")
    for line in plot(gp, f, Xtrain, ytrain, -1.0, 9.5):
        print(line)
    return 0


def _cmd_uncertainty(args) -> int:
    f = math.sin
    Xtrain = [0.0, 1.0, 2.0, 3.0]
    gp = GP(rbf(length=1.0, var=1.0), noise=1e-3).fit(Xtrain, [f(x) for x in Xtrain])
    print("# predictive std vs. distance from the nearest data point\n")
    print(f"  {'x':>5} {'dist':>6} {'std':>7}  band")
    for x in [0.0, 0.5, 1.0, 2.5, 4.0, 6.0, 9.0]:
        m, v = gp.predict(x)
        s = math.sqrt(v)
        dist = min(abs(x - xt) for xt in Xtrain)
        bar = "█" * round(s * 30)
        print(f"  {x:>5.1f} {dist:>6.1f} {s:>7.3f}  {bar}")
    print("\n  std → noise floor at the data, → prior (1.0) far from it.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="gp", description="Gaussian Process regression with calibrated uncertainty.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("fit", help="fit a function and plot the band")
    p.add_argument("--func", default="sin", choices=list(_FUNCS))
    p.add_argument("--length", type=float, default=1.0)
    p.add_argument("--noise", type=float, default=1e-3)
    p.set_defaults(func=_cmd_fit)

    p = sub.add_parser("uncertainty", help="std vs distance from data")
    p.set_defaults(func=_cmd_uncertainty)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
