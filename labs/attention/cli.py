"""CLI for attention + the induction head.

    python -m labs.attention.cli predict A B C A B C A
    python -m labs.attention.cli predict the cat sat the cat
    python -m labs.attention.cli selfattn a b a c a
"""
from __future__ import annotations

import argparse
import sys

from .attention import self_attention
from .induction import induction_head
from .render import attention_bars, self_attention_grid


def _one_hot_seq(seq):
    vocab = sorted(set(seq))
    idx = {t: i for i, t in enumerate(vocab)}
    d = len(vocab)
    return [[1.0 if i == idx[t] else 0.0 for i in range(d)] for t in seq]


def _cmd_predict(args) -> int:
    seq = args.tokens
    if len(seq) < 2:
        print("give at least two tokens, e.g. A B C A B C A")
        return 1
    pred, weights, _ = induction_head(seq)
    top = max(range(len(weights)), key=lambda i: weights[i])
    print(f"sequence : {' '.join(map(str, seq))}")
    print(f"predicted next token: {pred!r}\n")
    print("the induction head attended back to where the current token "
          f"({seq[-1]!r}) last appeared (position {top}), and copied what followed:\n")
    print(attention_bars(seq, weights))
    return 0


def _cmd_selfattn(args) -> int:
    seq = args.tokens
    X = _one_hot_seq(seq)
    _, A = self_attention(X, scale=args.scale)
    print(f"self-attention over: {' '.join(map(str, seq))}\n")
    print("each row is a token attending over the sequence "
          "(brighter = more attention):\n")
    print(self_attention_grid(seq, A))
    print("\nidentical tokens attend to each other; unique tokens attend to themselves.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="attention", description="Scaled dot-product attention and an induction head.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("predict", help="in-context next-token prediction")
    p.add_argument("tokens", nargs="+")
    p.set_defaults(func=_cmd_predict)

    p = sub.add_parser("selfattn", help="show the self-attention matrix")
    p.add_argument("tokens", nargs="+")
    p.add_argument("--scale", type=float, default=8.0)
    p.set_defaults(func=_cmd_selfattn)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
