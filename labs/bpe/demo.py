"""Demo: train a tokenizer, show the subwords it discovers, tokenize, round-trip.

    python -m labs.bpe.demo
"""
from __future__ import annotations

from .bpe import BPETokenizer
from .corpus import CORPUS


def main() -> int:
    tok = BPETokenizer().train(CORPUS, vocab_size=400)
    print(f"Trained {len(tok.merges)} merges on a {len(CORPUS)}-char corpus "
          f"(vocab {tok.vocab_size}).\n")

    print("The subwords BPE discovered (first 18 merges):")
    print("  " + "  ".join(repr(s) for _, s in tok.learned_tokens()[:18]))

    sample = "An intelligent agent plans ahead and learns from memory."
    ids = tok.encode(sample)
    print(f"\nTokenizing: {sample!r}")
    print("  " + " | ".join(tok.token_str(i) for i in ids))
    print(f"  {len(sample.encode())} bytes → {len(ids)} tokens "
          f"({len(sample.encode()) / len(ids):.2f}× compression)")

    print("\nByte-level means exact round-trips for anything, even emoji:")
    for s in (sample, "café — déjà vu 🤖 naïve", "x"):
        print(f"  decode(encode({s[:20]!r}…)) == original : {tok.decode(tok.encode(s)) == s}")

    print("\nCompression grows as the vocabulary grows:")
    for vs in (256, 300, 400, 512):
        t = BPETokenizer().train(CORPUS, vocab_size=vs)
        print(f"  vocab {vs:>4}: {t.compression(CORPUS):.2f}×")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
