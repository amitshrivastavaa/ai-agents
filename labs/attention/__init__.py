"""attention — scaled dot-product attention from scratch, and an induction head.

The one operation at the heart of every transformer:

    Attention(Q, K, V) = softmax(Q·Kᵀ / √d) · V

— a soft, content-addressable lookup: each query retrieves a blend of values,
weighted by how well it matches each key. Built here in plain Python (no numpy).

On top of it, a hand-wired **induction head** — the circuit mechanistic-
interpretability found inside real transformers — does *in-context learning*
with no training at all: shown ``A B C A B C A`` it predicts ``B``, by attending
to where the current token appeared before and copying what came next. That's
how a model continues a pattern it has never been trained on.

Fully offline, deterministic. Caps the lab's "build the LLM from scratch"
thread: tokenizer (`bpe`) → autograd (`micrograd`) → experts (`moe`) → attention.
"""
from .attention import attention, self_attention, softmax
from .induction import induction_head, predict_next

__all__ = ["attention", "self_attention", "softmax", "induction_head", "predict_next"]
