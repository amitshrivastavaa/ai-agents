"""Demo: catch the dishonest casino with Viterbi + posterior decoding.

    python -m labs.hmm.demo
"""
from __future__ import annotations

from .casino import casino_hmm, sample, accuracy

_LV = " ▁▂▃▄▅▆▇█"


def spark(ps):
    return "".join(_LV[min(8, max(0, round(p * 8)))] for p in ps)


def main() -> int:
    m = casino_hmm()
    rolls, hidden = sample(m, n=120, seed=14)
    path, logp = m.viterbi(rolls)
    post = m.forward_backward(rolls)
    p_loaded = [p["L"] for p in post]

    print("The dishonest casino — a HMM you can actually see work.\n")
    print("A dealer secretly switches between a FAIR die and a LOADED one")
    print("(which rolls 6 half the time). You see only the rolls. Which die")
    print("was in play when? That hidden sequence is what Viterbi recovers.\n")

    w = 90
    print("  rolls   " + "".join(rolls[:w]))
    print("  true    " + "".join("█" if s == "L" else "·" for s in hidden[:w]) + "   (█=loaded)")
    print("  viterbi " + "".join("█" if s == "L" else "·" for s in path[:w]) + "   (most likely path)")
    print("  P(load) " + spark(p_loaded[:w]) + "   (forward-backward posterior)")

    print(f"\n  decode accuracy: {accuracy(hidden, path) * 100:.0f}%   "
          f"(loaded {sum(s == 'L' for s in hidden)}/{len(hidden)} rolls)")
    print(f"  log P(rolls) from the forward algorithm: {m.forward(rolls):.1f}")
    print("\n  Viterbi gives the single best F/L path; the posterior sparkline shows")
    print("  its confidence — tall where the loaded die is almost certain, short in")
    print("  the brief, ambiguous excursions it can't quite pin down.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
