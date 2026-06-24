"""Demo: rediscover four hidden equations from sampled points.

    python -m labs.symbolic_regression.demo
"""
from __future__ import annotations

from .gp import evolve
from .targets import TARGETS


def main() -> int:
    print("Given only (x, y) points, evolve a formula that reproduces them:\n")
    print(f"  {'target':<10}{'hidden formula':<16}{'discovered':<26}{'MSE':>10}")
    print("  " + "-" * 62)
    for name, target in TARGETS.items():
        res = evolve(target, seed="demo")
        mark = "✅" if res.solved else "≈"
        print(f"  {name:<10}{target.formula:<16}{res.formula:<26}{res.best_mse:>10.2g} {mark}")
    print("\nThe search never knows the answer — only how to score a guess (the error).")
    print("That's the engine behind evolutionary program search like AlphaEvolve:")
    print("a verifier you can run, and a population of guesses that climb toward it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
