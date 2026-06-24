"""CLI for the HMM lab.

    python -m labs.hmm.cli casino --n 200
    python -m labs.hmm.cli decode --rolls 6661345266
"""
from __future__ import annotations

import argparse
import sys

from .casino import casino_hmm, sample, accuracy
from .demo import spark


def _cmd_casino(args) -> int:
    m = casino_hmm()
    rolls, hidden = sample(m, n=args.n, seed=args.seed)
    path, _ = m.viterbi(rolls)
    post = m.forward_backward(rolls)
    w = min(args.n, 96)
    print(f"# dishonest casino  ({args.n} rolls, seed={args.seed!r})\n")
    print("  rolls   " + "".join(rolls[:w]))
    print("  true    " + "".join("L" if s == "L" else "." for s in hidden[:w]))
    print("  viterbi " + "".join("L" if s == "L" else "." for s in path[:w]))
    print("  P(load) " + spark([p["L"] for p in post][:w]))
    print(f"\n  accuracy {accuracy(hidden, path) * 100:.0f}%   log P(rolls) {m.forward(rolls):.1f}")
    return 0


def _cmd_decode(args) -> int:
    m = casino_hmm()
    rolls = list(args.rolls)
    path, logp = m.viterbi(rolls)
    post = m.forward_backward(rolls)
    print(f"# decode {args.rolls!r}\n")
    print("  rolls  " + " ".join(rolls))
    print("  die    " + " ".join(path))
    print("  P(L)   " + " ".join(f"{p['L']:.1f}" for p in post))
    print(f"\n  best-path log-prob {logp:.2f}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="hmm", description="Hidden Markov Models: Viterbi + forward-backward.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("casino", help="generate and decode a dishonest-casino run")
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_casino)

    p = sub.add_parser("decode", help="decode a specific roll string")
    p.add_argument("--rolls", default="6661345266666654")
    p.set_defaults(func=_cmd_decode)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
