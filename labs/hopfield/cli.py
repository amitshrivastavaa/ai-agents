"""CLI for the Hopfield associative memory.

    python -m labs.hopfield.cli recall --glyph X --noise 0.3
    python -m labs.hopfield.cli recall --glyph T --occlude 0.5 --net modern
    python -m labs.hopfield.cli sweep
    python -m labs.hopfield.cli list
"""
from __future__ import annotations

import argparse
import sys

from .network import ClassicHopfield, ModernHopfield, overlap
from .patterns import GLYPHS, corrupt, occlude, side_by_side


def _net(name):
    return ModernHopfield().store(GLYPHS) if name == "modern" else ClassicHopfield().store(GLYPHS)


def _cmd_recall(args) -> int:
    if args.glyph not in GLYPHS:
        print(f"unknown glyph {args.glyph!r}; choose from {list(GLYPHS)}")
        return 1
    true = GLYPHS[args.glyph]
    cue = occlude(true, args.occlude) if args.occlude else corrupt(true, args.noise, seed=args.seed)
    net = _net(args.net)
    res = net.recall(cue)
    print(f"# {args.net} Hopfield · cue = {args.glyph} "
          f"({'occluded ' + str(args.occlude) if args.occlude else f'{args.noise:.0%} noise'})\n")
    print(side_by_side((f"target {args.glyph}", true), ("cue", cue), ("recalled", res.pattern)))
    print(f"\n  recalled '{res.label}'  ·  overlap to target {overlap(res.pattern, true):.0%}")
    if res.energy_history:
        print(f"  energy {res.energy_history[0]:.1f} → {res.energy_history[-1]:.1f} "
              f"over {res.sweeps} sweeps (only ever decreases)")
    return 0


def _cmd_sweep(args) -> int:
    classic = ClassicHopfield().store(GLYPHS)
    modern = ModernHopfield().store(GLYPHS)
    print("avg overlap-to-target across all glyphs (higher = better recall)\n")
    print(f"  {'noise':>6}{'classic':>10}{'modern':>10}")
    for noise in (0.1, 0.2, 0.3, 0.4, 0.5):
        c = m = cnt = 0
        for g, vec in GLYPHS.items():
            for k in range(args.trials):
                cue = corrupt(vec, noise, seed=f"{g}{k}")
                c += overlap(classic.recall(cue).pattern, vec)
                m += overlap(modern.recall(cue).pattern, vec)
                cnt += 1
        print(f"  {noise:>5.0%}{c / cnt:>10.2f}{m / cnt:>10.2f}")
    print("\nModern dense memory (softmax retrieval ≈ attention) degrades more")
    print("gracefully than the classic Hebbian net as corruption rises.")
    return 0


def _cmd_list(_args) -> int:
    print("Stored patterns:", ", ".join(GLYPHS))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hopfield", description="Associative memory: recover patterns from corrupted cues.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("recall")
    p.add_argument("--glyph", default="X")
    p.add_argument("--noise", type=float, default=0.3)
    p.add_argument("--occlude", type=float, default=0.0, help="erase bottom fraction instead")
    p.add_argument("--net", choices=("classic", "modern"), default="classic")
    p.add_argument("--seed", default="cue")
    p.set_defaults(func=_cmd_recall)

    p = sub.add_parser("sweep")
    p.add_argument("--trials", type=int, default=6)
    p.set_defaults(func=_cmd_sweep)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
