"""CLI for the multi-armed bandit lab.

    python -m labs.bandits.cli compare --horizon 2000 --runs 60
    python -m labs.bandits.cli pulls --policy Thompson
"""
from __future__ import annotations

import argparse
import sys

from .bandit import BernoulliBandit
from .run import evaluate, simulate, make_policies
from .demo import spark

PROBS = [0.2, 0.5, 0.75, 0.55, 0.3]


def _cmd_compare(args) -> int:
    avg, pct = evaluate(PROBS, horizon=args.horizon, runs=args.runs)
    gmax = max(c[-1] for c in avg.values())
    print(f"# regret over {args.horizon} pulls × {args.runs} runs   arms={PROBS}\n")
    print(f"  {'policy':14s} {'regret over time':30s} {'final':>8}  optimal")
    for name in avg:
        c = avg[name]
        print(f"  {name:14s} {spark(c, 0, gmax)} {c[-1]:8.1f}   {pct[name] * 100:4.1f}%")
    print("\n  lower + flatter = better. UCB1/Thompson go sublinear; random/greedy don't.")
    return 0


def _cmd_pulls(args) -> int:
    bandit = BernoulliBandit(PROBS, seed=("cli", 0))
    pols = make_policies(len(PROBS), 0)
    if args.policy not in pols:
        print(f"unknown policy {args.policy!r}; choose from {list(pols)}")
        return 2
    pol = pols[args.policy]
    _, chosen = simulate(bandit, pol, args.horizon)
    counts = [chosen.count(i) for i in range(len(PROBS))]
    top = max(counts)
    print(f"# arm-pull counts for {args.policy} over {args.horizon} pulls\n")
    for i, (p, c) in enumerate(zip(PROBS, counts)):
        star = "  ← best arm" if i == bandit.best_arm else ""
        bar = "█" * round(28 * c / top) if top else ""
        print(f"  arm #{i} (p={p:.2f})  {bar} {c}{star}")
    print(f"\n  {counts[bandit.best_arm] / args.horizon * 100:.0f}% of pulls went to the best arm.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="bandits", description="Multi-armed bandits: exploration vs exploitation.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("compare", help="regret of all five policies")
    p.add_argument("--horizon", type=int, default=2000)
    p.add_argument("--runs", type=int, default=60)
    p.set_defaults(func=_cmd_compare)

    p = sub.add_parser("pulls", help="where one policy spends its pulls")
    p.add_argument("--policy", default="Thompson")
    p.add_argument("--horizon", type=int, default=2000)
    p.set_defaults(func=_cmd_pulls)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
