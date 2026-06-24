"""Demo: same text, far fewer target calls.

    python -m labs.speculative.demo
"""
from __future__ import annotations

from .corpus import CORPUS
from .ngram import NgramModel, tokenize
from .speculative import speculative_decode, target_greedy


def main() -> int:
    draft = NgramModel(order=2).train(CORPUS)
    target = NgramModel(order=4).train(CORPUS)
    prompt = tokenize("A good agent")
    steps = 40

    base_tokens, base_calls = target_greedy(target, prompt, steps)
    print("Pure target decoding — one expensive target call per token:\n")
    print("  " + " ".join(base_tokens))
    print(f"\n  → {base_calls} target calls for {steps} tokens.\n")

    print("=" * 60)
    print("Speculative decoding — a bigram draft guesses, the 4-gram target")
    print("verifies a whole block per call:\n")
    res = speculative_decode(draft, target, prompt, steps, k=4)
    print("  " + " ".join(res.tokens))
    print(f"\n  → {res.target_calls} target calls for {steps} tokens "
          f"({res.speedup:.2f}× fewer).")
    print(f"  → {res.acceptance_rate:.1f} of 4 draft tokens accepted per round on average.")
    print(f"  → output identical to pure target decoding: {res.tokens == base_tokens}")
    print("\nLossless: only fast guesses the target confirms are kept, and the first")
    print("miss is corrected — so the text is exactly the target's, computed faster.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
