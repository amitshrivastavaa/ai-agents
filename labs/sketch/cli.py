"""CLI for the streaming-sketches lab.

    python -m labs.sketch.cli countmin --n 200000 --width 2000
    python -m labs.sketch.cli hll --n 100000 --p 12
"""
from __future__ import annotations

import argparse
import sys

from .._kernel import rng
from .countmin import CountMin
from .hyperloglog import HyperLogLog
from .demo import _stream


def _cmd_countmin(args) -> int:
    stream, hot = _stream(args.n, seed=args.seed)
    truth = {}
    for x in stream:
        truth[x] = truth.get(x, 0) + 1
    cm = CountMin(width=args.width, depth=args.depth)
    for x in stream:
        cm.add(x)
    print(f"# Count-Min  ({args.depth}×{args.width} counters, {args.n:,} events)\n")
    print(f"   {'key':>9} {'true':>8} {'est':>8} {'overshoot':>10}")
    for k in hot:
        e = cm.estimate(k)
        print(f"   {k:>9} {truth[k]:>8,} {e:>8,} {e - truth[k]:>+10}")
    over = [cm.estimate(x) - truth[x] for x in truth]
    print(f"\n   never underestimates: {all(o >= 0 for o in over)}   "
          f"mean overshoot {sum(over) / len(over):.2f} over {len(truth):,} keys")
    return 0


def _cmd_hll(args) -> int:
    print(f"# HyperLogLog  (p={args.p}, {1 << args.p:,} registers)\n")
    print(f"   {'true distinct':>14} {'estimate':>10} {'error':>7}")
    for true_n in (args.n // 100, args.n // 10, args.n):
        hll = HyperLogLog(p=args.p)
        for i in range(true_n):
            hll.add("item_" + str(i))
        est = hll.count()
        print(f"   {true_n:>14,} {est:>10,.0f} {abs(est - true_n) / true_n * 100:>6.2f}%")
    print(f"\n   fixed {1 << args.p:,}-register memory at every scale.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="sketch", description="Streaming sketches: Count-Min + HyperLogLog.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("countmin", help="approximate frequencies")
    p.add_argument("--n", type=int, default=200_000)
    p.add_argument("--width", type=int, default=2000)
    p.add_argument("--depth", type=int, default=5)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_countmin)

    p = sub.add_parser("hll", help="approximate cardinality")
    p.add_argument("--n", type=int, default=100_000)
    p.add_argument("--p", type=int, default=12)
    p.set_defaults(func=_cmd_hll)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
