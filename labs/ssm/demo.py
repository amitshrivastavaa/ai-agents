"""Demo: the SSM duality, and why Mamba needs *selectivity*.

    python -m labs.ssm.demo
"""
from __future__ import annotations

from .ssm import ssm_scan, ssm_conv
from .selective import sample_and_hold
from .tasks import make_task, best_lti, mse

_LEVELS = "▁▂▃▄▅▆▇█"


def spark(seq, lo=-1.0, hi=1.0) -> str:
    out = []
    span = (hi - lo) or 1.0
    for v in seq:
        f = (round(v, 3) - lo) / span          # quantize: 1e-9 diffs can't flip a level
        i = max(0, min(len(_LEVELS) - 1, round(f * (len(_LEVELS) - 1))))
        out.append(_LEVELS[i])
    return "".join(out)


def main() -> int:
    # ── 1. The SSM duality: recurrence == convolution (for fixed params) ──
    x = [1.0, -0.5, 2.0, 0.3, -1.0, 0.7, 0.0, 1.5]
    ys, _ = ssm_scan(x, 0.8, 0.5, 1.2, d=0.1)
    yc = ssm_conv(x, 0.8, 0.5, 1.2, d=0.1)
    diff = max(abs(p - q) for p, q in zip(ys, yc))
    print("1) SSM duality — the SAME linear-time-invariant model two ways:")
    print("   recurrence  h_t = a·h_{t-1} + b·x_t   (fast to run, O(n))")
    print("   convolution y   = K * x,  K[k] = c·b·a^k   (fast to train, parallel)")
    print(f"   max |recurrence − convolution| = {diff:.2e}  → identical.\n")

    # ── 2. Selectivity: the sample-and-hold / selective-copy task ──
    values, gates, target = make_task(seed="mamba")
    sel = sample_and_hold(values, gates, delta_write=12.0)
    lti_mse, a, b, lti = best_lti(values, gates, target)
    sel_mse = mse(sel, target)
    writes = [(t, values[t]) for t in range(len(values)) if gates[t]]

    print("2) Selective copy — capture the value at each ↑write, hold it until the")
    print("   next one, ignore the stream in between:\n")
    print(f"   writes : " + "  ".join(f"t={t}:{v:+.2f}" for t, v in writes))
    gate_row = "".join("↑" if g else "·" for g in gates)
    print(f"   gate   {gate_row}")
    print(f"   target {spark(target)}   (the sample-and-hold we want)")
    print(f"   MAMBA  {spark(sel)}   selective SSM,   MSE = {sel_mse:.1e}")
    print(f"   LTI    {spark(lti)}   best fixed (a={a:.2f}, b={b:.2f}), MSE = {lti_mse:.3f}")
    print()
    print(f"   The selective SSM is {lti_mse / sel_mse:,.0f}× closer to the target.")
    print("   No constant-dynamics (LTI) model can do this: holding wants a≈1,")
    print("   capturing wants a≈0, and a fixed a can't be both. Letting the timestep")
    print("   Δ_t depend on the input — Mamba's one idea — is what makes it possible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
