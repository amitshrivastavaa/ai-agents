"""Demo: the agent learns the famous cliff-walk, then a maze.

    python -m labs.qlearning.demo
"""
from __future__ import annotations

from .agent import evaluate, train
from .dp import value_iteration
from .gridworld import get_map
from .render import policy_arrows, value_heatmap

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values):
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    n = max(1, len(values) // 50)
    return "".join(_SPARK[min(7, int((values[i] - lo) / span * 7))]
                   for i in range(0, len(values), n))


def main() -> int:
    for name in ("cliff", "maze"):
        env = get_map(name)
        res = train(env, episodes=500, seed="demo")
        reached, steps, total, _ = evaluate(env, res.agent)
        V_opt, _ = value_iteration(env)
        values = {s: res.agent.value(s) for s in env.states()}
        print("=" * 52)
        print(f"'{name}' — learning from reward, no model of the world\n")
        print(f"  reward/episode: {_spark(res.smoothed())}  "
              f"{res.smoothed()[0]:.0f} → {res.smoothed()[-1]:.0f}")
        print(f"  greedy policy : {'reaches goal' if reached else 'fails'} in {steps} steps")
        print(f"  V(start)      : learned {res.agent.value(env.start):.1f} vs "
              f"optimal {V_opt[env.start]:.1f}\n")
        print(policy_arrows(env, res.agent))
        print()
        print(value_heatmap(env, values))
        print()
    print("=" * 52)
    print("Early on it stumbles into the cliff for -100; by the end it has learned")
    print("the optimal route — purely by acting and updating Q(s,a) from reward.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
