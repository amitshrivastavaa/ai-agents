"""An induction head: in-context next-token prediction via attention.

The circuit: to continue a sequence, look back for an earlier occurrence of the
*current* token, attend to it, and copy the token that *followed* it. Wiring
that into Q/K/V is all it takes — no training:

* **K[i]** = embedding of token *i*       ("where did this token appear?")
* **V[i]** = embedding of token *i+1*      ("what came after it?")
* **Q**    = embedding of the last token   ("what are we continuing?")

``softmax(Q·Kᵀ)`` lights up the positions whose token matches the query, and the
weighted sum of values returns the token that followed — the prediction.
"""
from __future__ import annotations

from .attention import attention


def _one_hot(index: int, dim: int) -> list[float]:
    v = [0.0] * dim
    v[index] = 1.0
    return v


def induction_head(seq: list, *, scale: float = 8.0):
    """Return (predicted_token, attention_weights, positions).

    ``attention_weights[i]`` is how strongly the head attended to sequence
    position ``i`` (0 … len-2). ``scale`` sharpens the softmax — real models get
    this from the magnitude of learned weights; here we set it directly.
    """
    if len(seq) < 2:
        raise ValueError("need at least two tokens to induce a continuation")
    vocab = sorted(set(seq), key=lambda t: (str(type(t)), t))
    idx = {t: i for i, t in enumerate(vocab)}
    d = len(vocab)

    K = [_one_hot(idx[seq[i]], d) for i in range(len(seq) - 1)]      # token i
    V = [_one_hot(idx[seq[i + 1]], d) for i in range(len(seq) - 1)]  # token i+1
    Q = [_one_hot(idx[seq[-1]], d)]                                  # last token

    out, weights = attention(Q, K, V, scale=scale)
    pred_index = max(range(d), key=lambda j: out[0][j])
    return vocab[pred_index], weights[0], list(range(len(seq) - 1))


def predict_next(seq: list, *, scale: float = 8.0):
    """Just the predicted next token."""
    return induction_head(seq, scale=scale)[0]
