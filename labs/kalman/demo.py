"""Demo: see a moving object through measurement noise.

    python -m labs.kalman.demo
"""
from __future__ import annotations

from .run import track


def plot(series, w=58, h=12):
    xs = [p[0] for pts, _ in series for p in pts]
    ys = [p[1] for pts, _ in series for p in pts]
    lox, hix, loy, hiy = min(xs), max(xs), min(ys), max(ys)
    grid = [[" "] * w for _ in range(h)]
    for pts, ch in series:
        for x, y in pts:
            cx = round((x - lox) / (hix - lox) * (w - 1)) if hix > lox else 0
            cy = round((y - loy) / (hiy - loy) * (h - 1)) if hiy > loy else 0
            grid[h - 1 - cy][cx] = ch
    return [" |" + "".join(r) + "|" for r in grid]


def main() -> int:
    r = track(steps=90, meas_std=3.0, kind="sine", q=0.05, seed="demo")

    print("Kalman filter — optimal tracking through noise.\n")
    print("An object moves along a smooth path; our sensor reports its position")
    print("with heavy Gaussian noise (σ=3). The filter fuses a motion model with")
    print("each noisy reading to recover the path — and the unseen velocity.\n")

    print("  noisy measurements ('x' = sensor, '·' = true path):")
    for line in plot([(r["truth"], "·"), (r["meas"], "x")]):
        print(line)
    print("\n  Kalman estimate ('o' = filter, '·' = true path):")
    for line in plot([(r["truth"], "·"), (r["est"], "o")]):
        print(line)

    print(f"\n  position RMSE vs. ground truth (lower is better):")
    print(f"     raw measurements   {r['rmse_meas']:.2f}")
    print(f"     moving average(5)  {r['rmse_ma']:.2f}   (a naive smoother)")
    print(f"     Kalman filter      {r['rmse_filt']:.2f}   "
          f"← {(1 - r['rmse_filt'] / r['rmse_meas']) * 100:.0f}% less error than the sensor")

    # velocity recovery on a true constant-velocity track
    line = track(steps=120, meas_std=3.0, kind="line", q=0.001, seed="demo")
    vx, vy = line["vel"][-1]
    print(f"\n  It also recovers velocity it never measured (true vx=1.00, vy=0.50):")
    print(f"     estimated  vx={vx:.2f}, vy={vy:.2f}")
    print(f"  And the Kalman gain settles to a constant {line['gains'][-1]:.3f} — the")
    print("  steady-state of the optimal estimator for this system.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
