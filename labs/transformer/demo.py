"""Demo: a Transformer block's parts, and the 2-layer induction circuit.

    python -m labs.transformer.demo
"""
from __future__ import annotations

from .block import TransformerBlock, layernorm
from . import induction as I
from .tasks import repeat_pattern, induction_accuracy


def _pstdev(xs):
    mu = sum(xs) / len(xs)
    return (sum((x - mu) ** 2 for x in xs) / len(xs)) ** 0.5


def main() -> int:
    print("A Transformer decoder block, from scratch — and the circuit that makes")
    print("Transformers learn in context. (caps the bpe → micrograd → attention thread)\n")

    # ── Part 1: the block is well-formed ──
    blk = TransformerBlock(d_model=16, n_heads=4, d_ff=32, seed="demo")
    X = [[((i * 7 + d * 3) % 11 - 5) / 5.0 for d in range(16)] for i in range(6)]
    Y = blk.forward(X)

    X2 = [row[:] for row in X]
    X2[-1] = [v + 1.0 for v in X2[-1]]
    Y2 = blk.forward(X2)
    leak = max(abs(Y[i][d] - Y2[i][d]) for i in range(5) for d in range(16))

    ln = layernorm([3.0, 1.0, 4.0, 1.0, 5.0, 9.0])
    blk.Wo = [[0.0] * 16 for _ in range(16)]
    blk.W2 = [[0.0] * 32 for _ in range(16)]
    ident = max(abs(blk.forward(X)[i][d] - X[i][d]) for i in range(6) for d in range(16))

    print("1) The block — pre-norm  x = x + MHA(LN x);  x = x + MLP(LN x):")
    print(f"   • causal mask:     perturbing the last token changes earlier")
    print(f"                      outputs by {leak:.1e}  (no future leak)")
    print(f"   • LayerNorm:       mean={sum(ln) / len(ln):+.1e}, std={_pstdev(ln):.4f}  (→0, →1)")
    print(f"   • residual stream: with the attn & MLP output weights zeroed, the")
    print(f"                      block is the identity to {ident:.1e}\n")

    # ── Part 2: the induction circuit ──
    print("2) Induction — continue a repeated pattern  '… A B … A → B':")
    for t in ("abcabca", "xyzwxyzw", "1 2 3 1 2 3 1"):
        print(f"     {t!r:18}→ next token: {I.next_token(t)!r}")

    seq = repeat_pattern(n_symbols=8, block=4, repeats=3, seed="demo")
    toks = list(seq)
    preds = I.predict(seq)
    print(f"\n   sequence {seq!r}  (a 4-token block, repeated):")
    print("   token: " + " ".join(toks))
    print("   guess: " + "  " + " ".join(preds[:-1]) + "   ← each sits under the token it predicts")

    acc2 = sum(induction_accuracy(repeat_pattern(8, 4, 3, s), I.predict, block=4)
               for s in range(20)) / 20
    acc1 = sum(induction_accuracy(repeat_pattern(8, 4, 3, s), I.one_layer_predict, block=4)
               for s in range(20)) / 20
    print(f"\n   next-token accuracy on the repeated region (avg of 20 patterns):")
    print(f"     two-layer circuit (prev-token head → induction head): {acc2 * 100:5.1f}%")
    print(f"     one-layer ablation (no prev-token head)             : {acc1 * 100:5.1f}%")
    print("\n   Induction *needs two layers*: layer 1 marks each token with its")
    print("   predecessor, layer 2 finds where the current token occurred before")
    print("   and copies what came next. One layer alone can only echo — 0%.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
