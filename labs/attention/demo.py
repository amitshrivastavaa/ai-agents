"""Demo: attention does in-context learning with no training.

    python -m labs.attention.demo
"""
from __future__ import annotations

from .attention import self_attention
from .induction import induction_head
from .render import attention_bars, self_attention_grid


def main() -> int:
    print("An induction head continues patterns it was never trained on —")
    print("by attending to where the current token appeared before:\n")
    seqs = [
        ["A", "B", "C", "A", "B", "C", "A"],
        ["the", "cat", "sat", "the", "cat"],
        ["red", "green", "blue", "red", "green", "blue", "red", "green"],
    ]
    for seq in seqs:
        pred, _, _ = induction_head(seq)
        print(f"  {' '.join(seq):<42} → predicts {pred!r}")

    print("\nThe attention weights for the first one (where did the last 'A' look?):\n")
    seq = seqs[0]
    _, weights, _ = induction_head(seq)
    print(attention_bars(seq, weights))

    print("\n" + "=" * 52)
    print("Plain self-attention is content-based similarity — identical tokens")
    print("attend to each other:\n")
    seq = ["a", "b", "a", "c", "a"]
    vocab = sorted(set(seq))
    idx = {t: i for i, t in enumerate(vocab)}
    X = [[1.0 if i == idx[t] else 0.0 for i in range(len(vocab))] for t in seq]
    _, A = self_attention(X, scale=8.0)
    print(self_attention_grid(seq, A))
    print("\nNo numpy, no training — just softmax(Q·Kᵀ/√d)·V. That's a transformer's core.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
