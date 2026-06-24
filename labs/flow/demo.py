"""Demo: turn Gaussian noise into a shape with a deterministic ODE.

    python -m labs.flow.demo
"""
from __future__ import annotations

from . import targets
from .field import base_sample
from .sample import (generate, nearest_data_rmse, mode_coverage, straightness,
                     integrate)


def scatter(points, lo=-6.0, hi=6.0, w=27, h=13, ch="•"):
    grid = [[" "] * w for _ in range(h)]
    for p in points:
        x, y = p[0], p[1]
        cx = round((x - lo) / (hi - lo) * (w - 1))
        cy = round((y - lo) / (hi - lo) * (h - 1))
        if 0 <= cx < w and 0 <= cy < h:
            grid[h - 1 - cy][cx] = ch
    return [" |" + "".join(row) + "|" for row in grid]


def _side_by_side(a, b, gap="   "):
    return "\n".join(x + gap + y for x, y in zip(a, b))


_LV = "█▇▆▅▄▃▂▁"


def main() -> int:
    data = targets.get("ring")
    noise = base_sample(220, 2, seed="demo")
    gen = generate(data, 220, steps=16, seed="demo")

    print("Flow matching / rectified flow — the engine of Stable Diffusion 3 & Flux,")
    print("built from scratch with the *analytic* velocity field (no training).\n")
    print("Start: 220 samples of Gaussian noise        After 16 ODE steps:")
    print(_side_by_side(scatter(noise, ch="·"), scatter(gen, ch="•")))
    print(f"\n   noise N(0,I)  →  the field v(x,t)=(ŷ−x)/(1−t) carries every point")
    print(f"   onto the ring.  on-ring RMSE = {nearest_data_rmse(gen, data):.3f},  "
          f"all {int(mode_coverage(gen, data) * 100)}% of modes covered.\n")

    print("Few steps suffice — that's the point of a straight-path ODE vs. noisy")
    print("Langevin diffusion. Error (nearest-data RMSE) vs. number of ODE steps:\n")
    rmses = []
    for s in (2, 4, 8, 16, 32):
        r = nearest_data_rmse(generate(data, 160, steps=s, seed="e"), data)
        rmses.append((s, r))
    hi = max(r for _, r in rmses) or 1.0
    for s, r in rmses:
        bar = "█" * round(36 * r / hi)
        print(f"   {s:2d} steps  {bar:<36} {r:.3f}")

    strs = [straightness(integrate(x0, data, 32, "euler")[1])
            for x0 in base_sample(60, 2, seed="s")]
    print(f"\n   trajectories are nearly straight: mean path/displacement = "
          f"{sum(strs) / len(strs):.2f}  (1.00 = a line).")
    print("   Deterministic: same seed → same samples, every run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
