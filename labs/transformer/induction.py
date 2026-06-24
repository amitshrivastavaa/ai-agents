"""The two-layer induction circuit — why Transformers do in-context learning.

Anthropic's interpretability work showed that a Transformer's ability to continue
a repeated pattern (``… A B … A → B``) is implemented by an **induction circuit**
that *needs two attention layers*:

1. a **previous-token head** (layer 1) writes, at each position, the identity of
   the *previous* token into the residual stream;
2. an **induction head** (layer 2) attends from the current token to positions
   whose *previous token* matches it, and copies the token found there — i.e. the
   token that last followed the current one.

We build it from the genuine scaled-dot-product ``attention`` in ``block.py`` by
constructing the Q/K/V vectors directly (exactly how the circuit is described in
terms of its QK and OV maps), so no training is required. A *single* such head
cannot do this — see :func:`one_layer_predict` — which is the whole point.
"""
from __future__ import annotations

from .block import attention


def _onehot(i, n):
    v = [0.0] * n
    v[i] = 1.0
    return v


def encode(text):
    """Tokens (chars, spaces dropped) → (ids, vocab, index)."""
    toks = [c for c in text if c != " "]
    vocab = sorted(set(toks))
    index = {t: i for i, t in enumerate(vocab)}
    return [index[t] for t in toks], vocab, index


def _prev_token_head(seq, V, strength=12.0):
    """Layer 1: each position attends to the one before it (positional QK).

    With q_i=[i−1, 1] and k_j=[2C·j, −C·j²], the score q_i·k_j equals
    −C·((i−1)−j)² up to a j-independent constant, so softmax peaks at j=i−1.
    The value copied is the token's one-hot → PREV[i] ≈ onehot(token_{i-1}).
    """
    L = len(seq)
    C = strength
    Q = [[i - 1.0, 1.0] for i in range(L)]
    K = [[2.0 * C * j, -C * j * j] for j in range(L)]
    Vv = [_onehot(seq[j], V) for j in range(L)]
    prev, _ = attention(Q, K, Vv, causal=True, scale=1.0)
    return prev


def _induction_head(seq, prev, V, strength=12.0):
    """Layer 2: attend from current token to positions whose PREV matches it,
    and copy the token there — the induction prediction."""
    L = len(seq)
    Q = [[strength * x for x in _onehot(seq[i], V)] for i in range(L)]
    K = prev                                          # keys = previous-token info
    Vv = [_onehot(seq[j], V) for j in range(L)]
    out, weights = attention(Q, K, Vv, causal=True, scale=1.0)
    return out, weights


def predict_dist(seq, dim, strength=12.0):
    """Two-layer circuit over token ids; returns per-position output distributions."""
    prev = _prev_token_head(seq, dim, strength)
    out, _ = _induction_head(seq, prev, dim, strength)
    return out


def _with_bos(seq, V):
    """Prepend a BOS sentinel so position 0 has a real 'previous token'.

    Without it, position 0 (no predecessor) attends to itself and its identity
    leaks into the previous-token channel, spuriously matching the first repeat.
    A BOS token — exactly what real LMs use — removes that boundary artifact.
    """
    return [V] + list(seq), V + 1


def predict(text, strength=12.0):
    """Per-position next-token predictions for ``text`` (list of token chars)."""
    seq, vocab, _ = encode(text)
    V = len(vocab)
    seq2, dim = _with_bos(seq, V)
    out = predict_dist(seq2, dim, strength)[1:]            # drop the BOS position
    return [vocab[max(range(V), key=lambda v: dist[v])] for dist in out]


def next_token(text, strength=12.0):
    """The circuit's guess for the token following ``text``."""
    return predict(text, strength)[-1]


def one_layer_predict(text, strength=12.0):
    """Ablation: a single head matching the current token to past tokens and
    copying them. Without the previous-token head it can only echo, not induct."""
    seq, vocab, _ = encode(text)
    V = len(vocab)
    seq2, dim = _with_bos(seq, V)
    Q = [[strength * x for x in _onehot(t, dim)] for t in seq2]
    K = [_onehot(t, dim) for t in seq2]                   # keys = the token itself
    Vv = [_onehot(t, dim) for t in seq2]
    out, _ = attention(Q, K, Vv, causal=True, scale=1.0)
    return [vocab[max(range(V), key=lambda v: dist[v])] for dist in out[1:]]
