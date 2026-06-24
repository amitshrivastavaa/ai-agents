"""Demo: exploration vs exploitation on a 5-armed bandit.

    python -m labs.bandits.demo
"""
from __future__ import annotations

from .run import evaluate

_LV = "▁▂▃▄▅▆▇█"


def spark(curve, lo, hi, width=30) -> str:
    n = len(curve)
    pts = [curve[min(n - 1, round(i * (n - 1) / (width - 1)))] for i in range(width)]
    span = (hi - lo) or 1.0
    return "".join(_LV[max(0, min(7, round((v - lo) / span * 7)))] for v in pts)


def main() -> int:
    probs = [0.2, 0.5, 0.75, 0.55, 0.3]
    best = max(range(len(probs)), key=lambda i: probs[i])
    horizon, runs = 2000, 60

    print("A 5-armed bandit. True win-rates are HIDDEN from the player:")
    print("   arms:  " + "  ".join(f"#{i}:{p:.2f}" for i, p in enumerate(probs)))
    print(f"   (the best is arm #{best} at {probs[best]:.2f} — the player must discover it)\n")
    print(f"Cumulative regret over {horizon} pulls, averaged across {runs} runs.")
    print("Regret = lost reward vs always playing the best arm. Lower + flatter = better.\n")

    avg, pct = evaluate(probs, horizon=horizon, runs=runs)
    gmax = max(c[-1] for c in avg.values())

    print(f"   {'policy':14s} {'regret over time':30s}  {'final':>7}  optimal-pulls")
    for name in avg:
        c = avg[name]
        print(f"   {name:14s} {spark(c, 0, gmax)}  {c[-1]:7.1f}      {pct[name] * 100:4.1f}%")

    print()
    print("Read it off the curves:")
    print("  • random / greedy keep climbing at a constant slope — LINEAR regret.")
    print("    Greedy fixates on whichever arm paid off first and never escapes.")
    print("  • ε-greedy explores 10% forever, so it learns fast but keeps paying a")
    print("    small tax: the curve bends but never fully flattens.")
    print("  • UCB1 (optimism) and Thompson (Bayesian sampling) explore *less* as")
    print("    they grow confident — SUBLINEAR regret, the curve goes flat. Thompson")
    print(f"    finds the best arm {pct['Thompson'] * 100:.0f}% of pulls and nearly stops losing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
