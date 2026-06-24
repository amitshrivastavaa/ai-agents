"""CLI for the from-scratch BPE tokenizer.

    python -m labs.bpe.cli encode "An agent plans ahead and learns."
    python -m labs.bpe.cli merges --vocab 400
    python -m labs.bpe.cli compare
"""
from __future__ import annotations

import argparse
import sys

from .bpe import BPETokenizer
from .corpus import CORPUS


def _trained(vocab: int) -> BPETokenizer:
    return BPETokenizer().train(CORPUS, vocab_size=vocab)


def _cmd_encode(args) -> int:
    tok = _trained(args.vocab)
    text = " ".join(args.text)
    ids = tok.encode(text)
    pieces = " | ".join(tok.token_str(i) for i in ids)
    raw = len(text.encode("utf-8"))
    print(f"text  : {text!r}")
    print(f"bytes : {raw}")
    print(f"tokens: {len(ids)}  ({raw / max(1, len(ids)):.2f}× compression, vocab {tok.vocab_size})")
    print(f"ids   : {ids}")
    print(f"pieces: {pieces}")
    print(f"decode(encode(x)) == x : {tok.decode(ids) == text}")
    return 0


def _cmd_merges(args) -> int:
    tok = _trained(args.vocab)
    print(f"{len(tok.merges)} merges learned (vocab {tok.vocab_size}). "
          "First learned subwords:\n")
    for idx, s in tok.learned_tokens()[: args.n]:
        print(f"  {idx:>4}: {s!r}")
    return 0


def _cmd_compare(args) -> int:
    print("Compression vs. vocabulary size (on the training corpus):\n")
    print(f"  {'vocab':>6}{'merges':>8}{'compression':>14}")
    for vs in (256, 300, 350, 400, 512, 768):
        t = _trained(vs)
        print(f"  {t.vocab_size:>6}{len(t.merges):>8}{t.compression(CORPUS):>12.2f}×")
    print("\nMore merges → common chunks become single tokens → fewer tokens per text.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bpe", description="A byte-level BPE tokenizer built from scratch.")
    parser.add_argument("--vocab", type=int, default=400, help="target vocabulary size")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("encode")
    p.add_argument("text", nargs="+")
    p.set_defaults(func=_cmd_encode)

    p = sub.add_parser("merges")
    p.add_argument("-n", type=int, default=24)
    p.set_defaults(func=_cmd_merges)

    sub.add_parser("compare").set_defaults(func=_cmd_compare)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
