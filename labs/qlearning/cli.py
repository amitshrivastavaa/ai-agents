"""CLI for the Q-learning gridworld agent.

    python -m labs.qlearning.cli train --map cliff --watch
    python -m labs.qlearning.cli train --map maze --episodes 600
    python -m labs.qlearning.cli list
"""
from __future__ import annotations

import argparse
import sys

from .agent import evaluate, train
from .dp import value_iteration
from .gridworld import MAPS, get_map
from .render import policy_arrows, value_heatmap

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values) -> str:
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    n = max(1, len(values) // 60)                     # downsample to ~60 cols
    pts = [values[i] for i in range(0, len(values), n)]
    return "".join(_SPARK[min(7, int((v - lo) / span * 7))] for v in pts)


def _cmd_train(args) -> int:
    env = get_map(args.map)
    res = train(env, episodes=args.episodes, seed=args.seed)
    reached, steps, total, _ = evaluate(env, res.agent)
    V_opt, _ = value_iteration(env)
    values = {s: res.agent.value(s) for s in env.states()}

    print(f"# Q-learning on '{args.map}'  ({args.episodes} episodes)\n")
    print(f"  learning curve : {_spark(res.smoothed())}  "
          f"{res.rewards[0]:.0f} → {res.smoothed()[-1]:.0f} avg reward")
    verdict = "✅ reaches the goal" if reached else "✗ does not reach the goal"
    print(f"  greedy policy  : {verdict} in {steps} steps (reward {total:.0f})")
    print(f"  V(start)       : learned {res.agent.value(env.start):.1f}  vs  "
          f"optimal {V_opt[env.start]:.1f} (value iteration)")
    if args.watch:
        print("\n  learned policy:\n")
        print(policy_arrows(env, res.agent))
        print("\n  value function (brighter = higher value):\n")
        print(value_heatmap(env, values))
    return 0


def _cmd_list(_args) -> int:
    for name, env in MAPS.items():
        print(f"  {name:<7} {env.width}×{env.height}, {len(env.pits)} pit-cells")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="qlearning", description="Learn a gridworld policy from reward (tabular Q-learning).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("train")
    p.add_argument("--map", default="cliff")
    p.add_argument("--episodes", type=int, default=400)
    p.add_argument("--seed", default="ql")
    p.add_argument("--watch", action="store_true")
    p.set_defaults(func=_cmd_train)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
