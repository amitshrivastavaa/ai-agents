"""CLI for speculative decoding.

    python -m labs.speculative.cli run --prompt "A good agent" --steps 40
    python -m labs.speculative.cli run --k 4
    python -m labs.speculative.cli compare
"""
from __future__ import annotations

import argparse
import sys

from .corpus import CORPUS
from .ngram import NgramModel, tokenize
from .speculative import speculative_decode, target_greedy


def _models():
    return (NgramModel(order=2).train(CORPUS), NgramModel(order=4).train(CORPUS))


def _cmd_run(args) -> int:
    draft, target = _models()
    prompt = tokenize(args.prompt)
    base_tokens, base_calls = target_greedy(target, prompt, args.steps)
    res = speculative_decode(draft, target, prompt, args.steps, k=args.k)
    print(f"# speculative decoding  (draft bigram, target 4-gram, k={args.k})\n")
    print("  generated: " + " ".join(res.tokens))
    print()
    print(f"  target calls : {res.target_calls}  (vs {base_calls} for pure target decoding)")
    print(f"  speedup      : {res.speedup:.2f}× fewer target calls")
    print(f"  acceptance   : {res.acceptance_rate:.1f} draft tokens accepted per round (of {args.k})")
    print(f"  lossless     : {'✅ identical to pure target output' if res.tokens == base_tokens else '✗ MISMATCH'}")
    return 0


def _cmd_compare(args) -> int:
    draft, target = _models()
    prompt = tokenize("A language model")
    _, base = target_greedy(target, prompt, args.steps)
    print(f"draft tokens (k) vs speedup  ({args.steps}-token continuation):\n")
    print(f"  {'k':>3}{'target calls':>14}{'speedup':>10}{'lossless':>10}")
    base_tokens, _ = target_greedy(target, prompt, args.steps)
    for k in (1, 2, 3, 4, 6, 8):
        r = speculative_decode(draft, target, prompt, args.steps, k=k)
        ok = "yes" if r.tokens == base_tokens else "NO"
        print(f"  {k:>3}{r.target_calls:>14}{r.speedup:>9.2f}×{ok:>10}")
    print("\nThe output never changes — only the number of expensive target calls does.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="speculative", description="Lossless LLM speedup by drafting and verifying.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run")
    p.add_argument("--prompt", default="A good agent")
    p.add_argument("--steps", type=int, default=40)
    p.add_argument("--k", type=int, default=4)
    p.set_defaults(func=_cmd_run)

    p = sub.add_parser("compare")
    p.add_argument("--steps", type=int, default=40)
    p.set_defaults(func=_cmd_compare)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
