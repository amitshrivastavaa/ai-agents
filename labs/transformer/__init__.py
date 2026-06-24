"""transformer — a decoder block from scratch + the induction circuit.

Two things in one MVP:

1. **The block.** The real components of a Transformer decoder layer —
   `layernorm`, scaled-dot-product `attention` with a causal mask, `multihead`
   projection, an `MLP`, and the pre-norm residual wiring — as readable pure-Python
   (no numpy). Verified by properties: causal (no future leak), LayerNorm
   normalizes, and with the sublayer output weights zeroed the block is the
   identity (the residual stream).

2. **The induction circuit.** Why Transformers learn *in context*. Continuing a
   repeated pattern (`… A B … A → B`) provably needs **two** attention layers — a
   previous-token head feeding an induction head — and we wire exactly that from
   the block's attention primitive (no training). It continues repeated patterns
   with 100% accuracy; the one-layer ablation scores 0%.

Caps the lab's from-scratch Transformer thread: `bpe` → `micrograd` →
`attention` → `transformer`. Offline, deterministic.
"""
from .block import (TransformerBlock, attention, multihead, layernorm, linear,
                    softmax, gelu)
from . import induction
from .induction import predict, next_token, one_layer_predict
from .tasks import repeat_pattern, induction_accuracy

__all__ = [
    "TransformerBlock", "attention", "multihead", "layernorm", "linear",
    "softmax", "gelu",
    "induction", "predict", "next_token", "one_layer_predict",
    "repeat_pattern", "induction_accuracy",
]
