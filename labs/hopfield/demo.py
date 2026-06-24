"""Demo: a corrupted glyph snaps back, then classic vs modern under noise.

    python -m labs.hopfield.demo
"""
from __future__ import annotations

from .network import ClassicHopfield, ModernHopfield, overlap
from .patterns import GLYPHS, corrupt, occlude, side_by_side


def main() -> int:
    net = ClassicHopfield().store(GLYPHS)
    print(f"Stored {len(GLYPHS)} patterns: {', '.join(GLYPHS)}\n")

    true = GLYPHS["X"]
    cue = corrupt(true, 0.3, seed="demo")
    res = net.recall(cue)
    print("Hand it a 30%-corrupted X and it settles back to the clean attractor:\n")
    print(side_by_side(("target X", true), ("30% noise", cue), ("recalled", res.pattern)))
    print(f"\n  → recalled '{res.label}', overlap {overlap(res.pattern, true):.0%}, "
          f"energy {res.energy_history[0]:.0f} → {res.energy_history[-1]:.0f} (monotonic descent)")

    print("\nEven with the bottom rows erased, a partial cue is enough:\n")
    res = net.recall(occlude(GLYPHS["H"], 0.4))
    print(side_by_side(("target H", GLYPHS["H"]), ("erased", occlude(GLYPHS["H"], 0.4)),
                       ("recalled", res.pattern)))

    print("\n" + "=" * 40)
    print("Modern dense memory is more robust as noise rises:\n")
    modern = ModernHopfield().store(GLYPHS)
    print(f"  {'noise':>6}{'classic':>10}{'modern':>10}")
    for noise in (0.2, 0.3, 0.4, 0.5):
        c = m = cnt = 0
        for g, vec in GLYPHS.items():
            for k in range(6):
                cue = corrupt(vec, noise, seed=f"{g}{k}")
                c += overlap(net.recall(cue).pattern, vec)
                m += overlap(modern.recall(cue).pattern, vec)
                cnt += 1
        print(f"  {noise:>5.0%}{c / cnt:>10.2f}{m / cnt:>10.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
