"""Demo: count a huge stream in tiny memory — frequencies and cardinality.

    python -m labs.sketch.demo
"""
from __future__ import annotations

from .._kernel import rng
from .countmin import CountMin
from .hyperloglog import HyperLogLog


def _stream(n, seed="demo"):
    r = rng("sketch-demo", seed, n)
    hot = ["login", "search", "feed", "profile", "logout"]
    out = []
    for _ in range(n):
        if r.random() < 0.45:                       # a few endpoints dominate
            out.append(hot[r.randrange(len(hot))])
        else:
            out.append("rare/" + str(r.randrange(20000)))
    return out, hot


def main() -> int:
    n = 200_000
    stream, hot = _stream(n)
    truth = {}
    for x in stream:
        truth[x] = truth.get(x, 0) + 1
    distinct = len(truth)

    print("Streaming sketches — count the uncountable in fixed memory.\n")
    print(f"A stream of {n:,} events over {distinct:,} distinct keys.")
    print("Exact counting needs a counter per key; sketches need a fixed grid.\n")

    # ── Count-Min Sketch ──
    cm = CountMin(width=2000, depth=5)
    for x in stream:
        cm.add(x)
    print(f"Count-Min Sketch  ({cm.d}×{cm.w} = {cm.d * cm.w:,} counters, fixed):")
    print(f"   {'key':>9} {'true':>8} {'estimate':>9} {'error':>6}")
    for k in hot:
        e = cm.estimate(k)
        print(f"   {k:>9} {truth[k]:>8,} {e:>9,} {e - truth[k]:>+6}")
    print(f"   never underestimates; overshoot is bounded and tiny vs the "
          f"{distinct:,}-key exact table.\n")

    # ── HyperLogLog ──
    hll = HyperLogLog(p=12)
    for x in stream:
        hll.add(x)
    est = hll.count()
    print(f"HyperLogLog  ({hll.m:,} one-byte registers ≈ {hll.m // 1024} KB, fixed):")
    print(f"   distinct keys — true {distinct:,}, estimated {est:,.0f}  "
          f"({abs(est - distinct) / distinct * 100:.1f}% error)")
    print(f"   …measured in a few KB, no matter if it's thousands or billions.")
    print("\nBoth read each event once and never grow — the shape of every")
    print("real-time analytics / large-scale n-gram counting pipeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
