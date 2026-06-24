"""A Transformer decoder block, from scratch — the real components.

Pure stdlib, no numpy; everything operates on lists of per-position vectors so
the linear algebra stays readable. A pre-norm decoder block is

    x = x + MHA(LayerNorm(x))          # causal multi-head self-attention
    x = x + MLP(LayerNorm(x))          # position-wise feed-forward

with residual streams around each sublayer. The pieces here — `layernorm`,
scaled-dot-product `attention` with a causal mask, `multihead`, and the `MLP` —
are also the primitives the induction circuit in ``induction.py`` is wired from.
"""
from __future__ import annotations

import math

from .._kernel import rng

NEG_INF = float("-inf")


def softmax(xs):
    finite = [x for x in xs if x != NEG_INF]
    m = max(finite)
    e = [(math.exp(x - m) if x != NEG_INF else 0.0) for x in xs]
    s = sum(e)
    return [x / s for x in e]


def layernorm(x, gain=None, bias=None, eps=1e-5):
    n = len(x)
    mu = sum(x) / n
    var = sum((xi - mu) ** 2 for xi in x) / n
    out = [(xi - mu) / math.sqrt(var + eps) for xi in x]
    if gain is not None:
        out = [o * g for o, g in zip(out, gain)]
    if bias is not None:
        out = [o + b for o, b in zip(out, bias)]
    return out


def linear(x, W, b=None):
    """W is a list of rows (out_dim × in_dim); returns the out_dim vector W·x+b."""
    out = [sum(wij * xj for wij, xj in zip(row, x)) for row in W]
    if b is not None:
        out = [o + bi for o, bi in zip(out, b)]
    return out


def gelu(x):
    return 0.5 * x * (1.0 + math.tanh(0.7978845608 * (x + 0.044715 * x ** 3)))


def attention(Q, K, V, causal=True, scale=None):
    """Scaled dot-product attention. Q/K/V are length-L lists of vectors.

    Returns ``(outputs, weights)`` — outputs[i] = Σ_j w[i][j]·V[j], with a causal
    mask so position i only attends to j ≤ i.
    """
    L = len(Q)
    dk = len(K[0])
    scale = scale if scale is not None else 1.0 / math.sqrt(dk)
    outs, weights = [], []
    for i in range(L):
        logits = [(scale * sum(Q[i][d] * K[j][d] for d in range(dk))
                   if not (causal and j > i) else NEG_INF) for j in range(L)]
        w = softmax(logits)
        weights.append(w)
        dv = len(V[0])
        outs.append([sum(w[j] * V[j][d] for j in range(L)) for d in range(dv)])
    return outs, weights


def _split_heads(vecs, n_heads):
    h = len(vecs[0]) // n_heads
    return [[v[head * h:(head + 1) * h] for v in vecs] for head in range(n_heads)]


def multihead(X, Wq, Wk, Wv, Wo, n_heads, causal=True):
    """Multi-head self-attention over a sequence X (list of d_model vectors)."""
    Q = [linear(x, Wq) for x in X]
    K = [linear(x, Wk) for x in X]
    V = [linear(x, Wv) for x in X]
    qh, kh, vh = _split_heads(Q, n_heads), _split_heads(K, n_heads), _split_heads(V, n_heads)
    head_outs = [attention(qh[i], kh[i], vh[i], causal=causal)[0] for i in range(n_heads)]
    concat = [[c for head in range(n_heads) for c in head_outs[head][pos]]
              for pos in range(len(X))]
    return [linear(c, Wo) for c in concat]


def _rand_matrix(rows, cols, r, scale):
    return [[r.uniform(-scale, scale) for _ in range(cols)] for _ in range(rows)]


class TransformerBlock:
    """A pre-norm causal decoder block with random (untrained) weights."""

    def __init__(self, d_model=16, n_heads=4, d_ff=32, seed="tb"):
        self.d_model, self.n_heads = d_model, n_heads
        r = rng("transformer", seed)
        s = 1.0 / math.sqrt(d_model)
        self.Wq = _rand_matrix(d_model, d_model, r, s)
        self.Wk = _rand_matrix(d_model, d_model, r, s)
        self.Wv = _rand_matrix(d_model, d_model, r, s)
        self.Wo = _rand_matrix(d_model, d_model, r, s)
        self.W1 = _rand_matrix(d_ff, d_model, r, s)
        self.b1 = [0.0] * d_ff
        self.W2 = _rand_matrix(d_model, d_ff, r, s)
        self.b2 = [0.0] * d_model
        self.ln1_g = [1.0] * d_model
        self.ln2_g = [1.0] * d_model

    def _mlp(self, x):
        h = [gelu(v) for v in linear(x, self.W1, self.b1)]
        return linear(h, self.W2, self.b2)

    def forward(self, X):
        normed = [layernorm(x, self.ln1_g) for x in X]
        attn = multihead(normed, self.Wq, self.Wk, self.Wv, self.Wo, self.n_heads)
        X = [[a + b for a, b in zip(x, o)] for x, o in zip(X, attn)]      # residual
        normed = [layernorm(x, self.ln2_g) for x in X]
        ff = [self._mlp(x) for x in normed]
        return [[a + b for a, b in zip(x, o)] for x, o in zip(X, ff)]     # residual
