"""Demo: react vs. reason across every map, then a watched episode.

    python -m labs.world_model.demo
"""
from __future__ import annotations

from .cli import _cmd_compare, _cmd_run
from .env import get_map
from .planners import ReactivePlanner, LookaheadPlanner
from .runner import run_episode


class _NS:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def main() -> int:
    print("Three agents, one world model — reflex, sampling, search:\n")
    _cmd_compare(_NS(map=None))

    print("\n" + "=" * 60)
    print("On 'lava_gap', greedy walks straight into the lava…\n")
    env = get_map("lava_gap")
    ep = run_episode(env, ReactivePlanner(), map_name="lava_gap")
    print(env.render(pos=ep.trajectory[-1], path=ep.trajectory))
    print(f"  → {ep.outcome} after {ep.steps} steps\n")

    print("…while the lookahead planner finds the safe detour:\n")
    ep = run_episode(env, LookaheadPlanner(), map_name="lava_gap")
    print(env.render(pos=ep.trajectory[-1], path=ep.trajectory))
    print(f"  → {ep.outcome} in {ep.steps} steps (optimal)")
    print("\n  S start · G goal · # wall · L lava · * path · @ final")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
