"""CLI for the state-space model lab.

    python -m labs.ssm.cli duality
    python -m labs.ssm.cli hold --seed mamba
    python -m labs.ssm.cli kernel --a 0.9 --b 0.1
"""
from __future__ import annotations

import argparse
import sys

from .ssm import ssm_scan, ssm_conv, ssm_kernel
from .selective import sample_and_hold
from .tasks import make_task, best_lti, mse
from .demo import spark


def _cmd_duality(args) -> int:
    x = [1.0, -0.5, 2.0, 0.3, -1.0, 0.7, 0.0, 1.5]
    ys, _ = ssm_scan(x, args.a, args.b, args.c, d=args.d)
    yc = ssm_conv(x, args.a, args.b, args.c, d=args.d)
    diff = max(abs(p - q) for p, q in zip(ys, yc))
    print(f"# SSM duality  (a={args.a}, b={args.b}, c={args.c}, d={args.d})\n")
    print("  recurrence:  " + " ".join(f"{v:+.3f}" for v in ys))
    print("  convolution: " + " ".join(f"{v:+.3f}" for v in yc))
    print(f"\n  max difference = {diff:.2e}  → the recurrence IS the convolution.")
    return 0


def _cmd_kernel(args) -> int:
    k = ssm_kernel(args.a, args.b, args.c, args.length)
    print(f"# impulse response / convolution kernel  K[k] = c·b·a^k")
    print(f"  (a={args.a}, b={args.b}, c={args.c})\n")
    print("  " + " ".join(f"{v:.4f}" for v in k))
    print("  " + spark(k, lo=0.0, hi=max(k) if max(k) else 1.0))
    print(f"\n  sum = {sum(k):.4f}   (a<1 → a stable, decaying memory)")
    return 0


def _cmd_hold(args) -> int:
    values, gates, target = make_task(seed=args.seed)
    sel = sample_and_hold(values, gates, delta_write=args.delta)
    lti_mse, a, b, lti = best_lti(values, gates, target)
    sel_mse = mse(sel, target)
    writes = [(t, values[t]) for t in range(len(values)) if gates[t]]
    print(f"# selective copy  (seed={args.seed!r})\n")
    print("  writes : " + "  ".join(f"t={t}:{v:+.2f}" for t, v in writes))
    print("  gate   " + "".join("^" if g else "." for g in gates))
    print(f"  target {spark(target)}")
    print(f"  select {spark(sel)}   selective SSM   MSE={sel_mse:.1e}")
    print(f"  lti    {spark(lti)}   best fixed a={a:.2f},b={b:.2f}  MSE={lti_mse:.3f}")
    print(f"\n  selective is {lti_mse / sel_mse:,.0f}x closer — input-dependent Δ wins.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ssm", description="State-space models: the duality, and Mamba selectivity.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("duality", help="recurrence == convolution")
    p.add_argument("--a", type=float, default=0.8)
    p.add_argument("--b", type=float, default=0.5)
    p.add_argument("--c", type=float, default=1.2)
    p.add_argument("--d", type=float, default=0.1)
    p.set_defaults(func=_cmd_duality)

    p = sub.add_parser("kernel", help="the LTI impulse response")
    p.add_argument("--a", type=float, default=0.9)
    p.add_argument("--b", type=float, default=0.1)
    p.add_argument("--c", type=float, default=1.0)
    p.add_argument("--length", type=int, default=16)
    p.set_defaults(func=_cmd_kernel)

    p = sub.add_parser("hold", help="selective copy: Mamba vs best LTI")
    p.add_argument("--seed", default="mamba")
    p.add_argument("--delta", type=float, default=12.0)
    p.set_defaults(func=_cmd_hold)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
