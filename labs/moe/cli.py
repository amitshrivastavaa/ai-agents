"""CLI for the mixture-of-experts router.

    python -m labs.moe.cli train --dataset piecewise --experts 3 --watch
    python -m labs.moe.cli train --dataset fan --experts 4
    python -m labs.moe.cli compare --dataset piecewise
    python -m labs.moe.cli list
"""
from __future__ import annotations

import argparse
import sys

from .data import DATASETS, get_dataset
from .moe import MixtureOfExperts, single_model_error
from .render import plot_fit


def _cmd_train(args) -> int:
    data = get_dataset(args.dataset)
    single = single_model_error(data)
    moe = MixtureOfExperts(k=args.experts).train(data)
    err = moe.train_error(data)
    print(f"# mixture of {args.experts} experts on '{data.name}'\n")
    print(f"  single model MSE : {single:.4f}")
    print(f"  mixture MSE      : {err:.4f}   ({single / max(err, 1e-9):.1f}× better)")
    print(f"  load per expert  : {moe.load()}   (router keeps them all busy)")
    print(f"  gate centres     : {[round(c, 2) for c, _ in moe.regions()]}")
    if args.watch:
        print("\n  data (·) and the mixture's fit, labelled by routed expert:\n")
        print(plot_fit(data, moe))
    return 0


def _cmd_compare(args) -> int:
    data = get_dataset(args.dataset)
    single = single_model_error(data)
    print(f"'{data.name}' — single model MSE = {single:.4f}\n")
    print(f"  {'experts':>8}{'MSE':>10}{'vs single':>12}")
    for k in (1, 2, 3, 4, 5, 6):
        err = MixtureOfExperts(k=k).train(data).train_error(data)
        print(f"  {k:>8}{err:>10.4f}{single / max(err, 1e-9):>10.1f}×")
    print("\nAdding experts helps until there's one per regime, then plateaus —")
    print("the router has carved the input into specialists.")
    return 0


def _cmd_list(_args) -> int:
    for name in DATASETS:
        d = get_dataset(name)
        print(f"  {name:<10} {len(d.X)} points, {len(set(d.region))} regimes")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="moe", description="Route inputs to specializing experts (mixture of experts).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("train")
    p.add_argument("--dataset", default="piecewise")
    p.add_argument("--experts", type=int, default=3)
    p.add_argument("--watch", action="store_true")
    p.set_defaults(func=_cmd_train)

    p = sub.add_parser("compare")
    p.add_argument("--dataset", default="piecewise")
    p.set_defaults(func=_cmd_compare)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
