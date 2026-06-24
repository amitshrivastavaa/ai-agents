"""CLI for the world_model planning demo.

    python -m labs.world_model.cli compare                 # all planners × all maps
    python -m labs.world_model.cli compare --map river
    python -m labs.world_model.cli run --map lava_gap --planner lookahead --watch
    python -m labs.world_model.cli list
"""
from __future__ import annotations

import argparse
import sys

from .env import MAPS, get_map
from .planners import _PLANNERS, get_planner
from .runner import run_episode

_OUTCOME = {"goal": "✅ reached goal", "lava": "🔥 died in lava", "timeout": "🌀 trapped"}


def _cmd_list(_args) -> int:
    print("Maps:    " + ", ".join(MAPS))
    print("Planners: " + ", ".join(_PLANNERS))
    print("\n  reactive  — greedy toward the goal, no lookahead (reflex)")
    print("  rollout   — simulates many imagined futures, picks the best (sampling)")
    print("  lookahead — searches the model for the optimal safe path (search)")
    return 0


def _cmd_run(args) -> int:
    env = get_map(args.map)
    planner = get_planner(args.planner)
    ep = run_episode(env, planner, map_name=args.map)
    print(f"map '{args.map}' · planner '{args.planner}'  →  {_OUTCOME[ep.outcome]} "
          f"in {ep.steps} steps (reward {ep.total_reward:+.0f})\n")
    if args.watch:
        print(env.render(pos=ep.trajectory[-1], path=ep.trajectory))
        print("\n  S start · G goal · # wall · L lava · * path taken · @ final position")
    return 0


def _cmd_compare(args) -> int:
    maps = [args.map] if args.map else list(MAPS)
    planners = list(_PLANNERS)
    print(f"{'map':<10} " + "  ".join(f"{p:<14}" for p in planners))
    print("-" * (10 + 16 * len(planners)))
    for mname in maps:
        env = get_map(mname)
        cells = []
        for pname in planners:
            ep = run_episode(env, get_planner(pname), map_name=mname)
            tag = {"goal": f"goal {ep.steps:>2}st", "lava": "DIED 🔥",
                   "timeout": "trapped 🌀"}[ep.outcome]
            cells.append(f"{tag:<14}")
        print(f"{mname:<10} " + "  ".join(cells))
    print("\nreflex dies on hazards; sampling (rollout) clears local-hazard detours")
    print("but a myopic policy stays trapped in complex mazes; only search")
    print("(lookahead) reliably reaches the goal everywhere.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="world_model",
        description="React vs. reason: planners that simulate before they act.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    p = sub.add_parser("run")
    p.add_argument("--map", default="lava_gap")
    p.add_argument("--planner", default="lookahead")
    p.add_argument("--watch", action="store_true", help="render the path taken")
    p.set_defaults(func=_cmd_run)

    p = sub.add_parser("compare")
    p.add_argument("--map", default=None, help="a single map (default: all)")
    p.set_defaults(func=_cmd_compare)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
