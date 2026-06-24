"""Demo: noise becomes a ring, then a spiral, via diffusion sampling.

    python -m labs.diffusion.demo
"""
from __future__ import annotations

from .._kernel import rng
from .diffusion import generate, nearest_mode_distance
from .render import scatter
from .target import get_target


def main() -> int:
    for name in ("ring", "spiral"):
        target = get_target(name)
        r = rng("noise", name)
        noise = [(r.gauss(0, 12), r.gauss(0, 12)) for _ in range(300)]
        samples = generate(target, n=300, seed="demo")
        print("=" * 47)
        print(f"target '{name}': start from pure noise …\n")
        print(scatter(noise, target, height=15))
        print(f"\n… and {len(samples)} annealed-Langevin steps later, the samples")
        print("have settled onto the target shape:\n")
        print(scatter(samples, target, height=15))
        print(f"\n  mean distance to nearest mode: {nearest_mode_distance(noise, target):.1f}"
              f"  →  {nearest_mode_distance(samples, target):.2f}\n")
    print("=" * 47)
    print("No training, no neural net — the score ∇log p(x) is analytic for a")
    print("mixture of Gaussians, and following it from noise IS a diffusion model.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
