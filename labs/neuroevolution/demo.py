"""Demo: a random controller drops the pole; an evolved one balances it.

    python -m labs.neuroevolution.demo
"""
from __future__ import annotations

from .cartpole import CartPole
from .evolve import evolve
from .policy import Policy
from .render import frame, rollout_frames

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values):
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    return "".join(_SPARK[min(7, int((v - lo) / span * 7))] for v in values)


def main() -> int:
    print("A RANDOM neural controller — the pole tips over almost immediately:\n")
    rnd = Policy.random(6, seed="r")
    shots, steps = rollout_frames(rnd, seed="watch", every=3, max_frames=4)
    for step, fr, deg in shots:
        print(f"  step {step:>3} (pole {deg:+.1f}°)")
        print(fr + "\n")
    print(f"  → fell after {steps} steps.\n")
    print("=" * 44)

    print("Now EVOLVE a population of controllers (no gradients) …\n")
    res = evolve(population=24, generations=18, seed="demo")
    print(f"  best fitness per generation: {_spark(res.history)}  "
          f"{res.history[0]:.0f} → {res.best_fitness:.0f} / 500")
    fresh = sum(CartPole().rollout(res.best_policy, seed=f"f{i}") for i in range(5)) / 5
    print(f"  the evolved controller balances {fresh:.0f}/500 steps on unseen starts.\n")

    print("Watch it hold the pole upright:\n")
    shots, steps = rollout_frames(res.best_policy, seed="watch", every=40, max_frames=4)
    for step, fr, deg in shots:
        print(f"  step {step:>3} (pole {deg:+.1f}°)")
        print(fr + "\n")
    print(f"  → still balancing at {steps} steps. Evolution found a controller "
          "without ever computing a gradient.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
