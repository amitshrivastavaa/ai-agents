"""CLI for the GRPO lab.

    python -m labs.grpo.cli train --contexts 6 --actions 6 --method grpo
    python -m labs.grpo.cli compare
"""
from __future__ import annotations

import argparse
import sys

from .task import VerifiableTask
from .train import train, accuracy, steps_to_threshold
from .demo import spark


def _cmd_train(args) -> int:
    task = VerifiableTask(args.contexts, args.actions, seed=args.seed)
    pol, hist = train(task, steps=args.steps, group_size=args.group,
                      lr=args.lr, method=args.method, seed=args.seed)
    print(f"# {args.method} on {args.contexts} prompts × {args.actions} actions\n")
    print(f"  correct-prob: chance {task.chance():.2f}  {spark(hist)}  {hist[-1]:.2f}")
    print(f"  reached 95%  : step {steps_to_threshold(hist, 0.95)} of {args.steps}")
    print(f"  accuracy     : {accuracy(pol, task) * 100:.0f}%\n")
    for s in range(args.contexts):
        a = pol.greedy(s)
        ok = "ok" if a == task.answers[s] else "MISS"
        print(f"   prompt #{s}: {a} (want {task.answers[s]})  {ok}")
    return 0


def _cmd_compare(args) -> int:
    print(f"# GRPO vs REINFORCE  ({args.contexts}×{args.actions}, {args.runs} seeds)\n")
    rows = {}
    for method in ("grpo", "reinforce"):
        steps_list, finals = [], []
        for seed in range(args.runs):
            task = VerifiableTask(args.contexts, args.actions, seed=("cmp", seed))
            _, h = train(task, steps=args.steps, group_size=args.group,
                         lr=args.lr, method=method, seed=seed)
            steps_list.append(steps_to_threshold(h, 0.95))
            finals.append(h[-1])
        rows[method] = (sum(steps_list) / len(steps_list), sum(finals) / len(finals))
    print(f"  {'method':24s}{'steps→95%':>12}{'final prob':>12}")
    for method, label in (("grpo", "GRPO (group baseline)"),
                          ("reinforce", "REINFORCE (no baseline)")):
        st, fn = rows[method]
        print(f"  {label:24s}{st:>12.0f}{fn:>12.3f}")
    speedup = rows["reinforce"][0] / rows["grpo"][0]
    print(f"\n  GRPO's centered, normalized advantage converges {speedup:.1f}× faster.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="grpo", description="GRPO: group-relative policy optimization from scratch.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("train", help="train one policy and show the result")
    p.add_argument("--contexts", type=int, default=6)
    p.add_argument("--actions", type=int, default=6)
    p.add_argument("--steps", type=int, default=500)
    p.add_argument("--group", type=int, default=16)
    p.add_argument("--lr", type=float, default=0.5)
    p.add_argument("--method", choices=("grpo", "reinforce"), default="grpo")
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_train)

    p = sub.add_parser("compare", help="GRPO vs REINFORCE convergence")
    p.add_argument("--contexts", type=int, default=6)
    p.add_argument("--actions", type=int, default=6)
    p.add_argument("--steps", type=int, default=500)
    p.add_argument("--group", type=int, default=16)
    p.add_argument("--lr", type=float, default=0.5)
    p.add_argument("--runs", type=int, default=6)
    p.set_defaults(func=_cmd_compare)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
