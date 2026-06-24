"""CLI for the transformer-block lab.

    python -m labs.transformer.cli induct --text "a b c a b c a"
    python -m labs.transformer.cli pattern --block 4 --repeats 3
    python -m labs.transformer.cli block
"""
from __future__ import annotations

import argparse
import sys

from .block import TransformerBlock, layernorm
from . import induction as I
from .tasks import repeat_pattern, induction_accuracy


def _cmd_induct(args) -> int:
    preds = I.predict(args.text)
    toks = [c for c in args.text if c != " "]
    print(f"# induction circuit on {args.text!r}\n")
    print("  token:      " + " ".join(toks))
    print("  next-guess: " + " ".join(preds))
    print(f"\n  predicted continuation after the sequence: {I.next_token(args.text)!r}")
    return 0


def _cmd_pattern(args) -> int:
    print(f"# repeated-pattern induction  (block={args.block}, repeats={args.repeats})\n")
    print(f"  {'seed':>4}  {'sequence':<24} two-layer  one-layer")
    for s in range(args.runs):
        seq = repeat_pattern(args.symbols, args.block, args.repeats, seed=s)
        a2 = induction_accuracy(seq, I.predict, block=args.block)
        a1 = induction_accuracy(seq, I.one_layer_predict, block=args.block)
        print(f"  {s:>4}  {seq:<24} {a2 * 100:7.0f}%  {a1 * 100:8.0f}%")
    print("\n  two layers → perfect continuation; one layer → can't induct.")
    return 0


def _cmd_block(args) -> int:
    blk = TransformerBlock(d_model=args.d_model, n_heads=args.heads, seed=args.seed)
    X = [[((i * 7 + d * 3) % 11 - 5) / 5.0 for d in range(args.d_model)]
         for i in range(args.length)]
    Y = blk.forward(X)
    X2 = [r[:] for r in X]
    X2[-1] = [v + 1.0 for v in X2[-1]]
    Y2 = blk.forward(X2)
    leak = max(abs(Y[i][d] - Y2[i][d])
               for i in range(args.length - 1) for d in range(args.d_model))
    print(f"# transformer block  (d_model={args.d_model}, heads={args.heads}, "
          f"len={args.length})\n")
    print(f"  forward output: {len(Y)} positions × {len(Y[0])} dims")
    print(f"  causal check  : last-token perturbation leaks {leak:.1e} to earlier outputs")
    ln = layernorm(X[0])
    print(f"  layernorm     : mean {sum(ln) / len(ln):+.1e}, "
          f"std {(sum(v * v for v in ln) / len(ln)) ** 0.5:.4f}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="transformer", description="A Transformer block + the induction circuit.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("induct", help="run the induction circuit on text")
    p.add_argument("--text", default="a b c a b c a")
    p.set_defaults(func=_cmd_induct)

    p = sub.add_parser("pattern", help="two-layer vs one-layer on repeated patterns")
    p.add_argument("--symbols", type=int, default=8)
    p.add_argument("--block", type=int, default=4)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--runs", type=int, default=8)
    p.set_defaults(func=_cmd_pattern)

    p = sub.add_parser("block", help="inspect a transformer block")
    p.add_argument("--d_model", type=int, default=16)
    p.add_argument("--heads", type=int, default=4)
    p.add_argument("--length", type=int, default=6)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_block)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
