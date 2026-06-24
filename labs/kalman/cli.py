"""CLI for the Kalman-filter lab.

    python -m labs.kalman.cli track --kind sine --noise 3
    python -m labs.kalman.cli gain --kind line
"""
from __future__ import annotations

import argparse
import sys

from .run import track
from .demo import plot


def _cmd_track(args) -> int:
    r = track(steps=args.steps, meas_std=args.noise, kind=args.kind,
              q=args.q, seed=args.seed)
    print(f"# tracking a {args.kind!r} trajectory, sensor σ={args.noise}\n")
    print("  measurements ('x') vs true path ('·'):")
    for line in plot([(r["truth"], "·"), (r["meas"], "x")]):
        print(line)
    print("\n  Kalman estimate ('o') vs true path ('·'):")
    for line in plot([(r["truth"], "·"), (r["est"], "o")]):
        print(line)
    print(f"\n  RMSE — measurements {r['rmse_meas']:.2f} | "
          f"moving-avg {r['rmse_ma']:.2f} | Kalman {r['rmse_filt']:.2f}")
    return 0


def _cmd_gain(args) -> int:
    r = track(steps=args.steps, meas_std=args.noise, kind=args.kind,
              q=args.q, seed=args.seed)
    print(f"# Kalman gain K[0,0] converging to steady state ({args.kind!r})\n")
    gains = r["gains"]
    hi = max(gains)
    for i in range(0, len(gains), max(1, len(gains) // 16)):
        bar = "█" * round(34 * gains[i] / hi)
        print(f"  step {i:3d}  {bar:<34} {gains[i]:.4f}")
    print(f"\n  settles to {gains[-1]:.4f} — the optimal steady-state gain.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="kalman", description="Kalman filter: optimal tracking through noise.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("track", help="filter a noisy trajectory")
    p.add_argument("--kind", default="sine", choices=("line", "sine", "turn"))
    p.add_argument("--noise", type=float, default=3.0)
    p.add_argument("--steps", type=int, default=90)
    p.add_argument("--q", type=float, default=0.05)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_track)

    p = sub.add_parser("gain", help="watch the Kalman gain converge")
    p.add_argument("--kind", default="line", choices=("line", "sine", "turn"))
    p.add_argument("--noise", type=float, default=3.0)
    p.add_argument("--steps", type=int, default=60)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_gain)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
