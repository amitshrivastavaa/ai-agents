# transformer — a decoder block from scratch + the induction circuit

> Two things in one MVP. **The block:** the real components of a Transformer
> decoder layer — LayerNorm, causal scaled-dot-product attention, multi-head
> projection, an MLP, and the pre-norm residual wiring — in readable pure Python.
> **The circuit:** *why* Transformers learn in context. Continuing a repeated
> pattern (`… A B … A → B`) provably needs **two** attention layers — a
> previous-token head feeding an induction head — and we wire exactly that, no
> training, from the block's own attention.

Caps the lab's from-scratch Transformer thread:
[`bpe`](../bpe/) → [`micrograd`](../micrograd/) → [`attention`](../attention/) →
**transformer**. Offline, deterministic, no numpy.

## Quick start

```sh
python -m labs.transformer.demo
python -m labs.transformer.cli induct --text "a b c a b c a"
python -m labs.transformer.cli pattern --block 4 --repeats 3
python -m labs.transformer.cli block
```

```
2) Induction — continue a repeated pattern  '… A B … A → B':
     'abcabca'         → next token: 'b'
     'xyzwxyzw'        → next token: 'x'

   next-token accuracy on the repeated region (avg of 20 patterns):
     two-layer circuit (prev-token head → induction head): 100.0%
     one-layer ablation (no prev-token head)             :   0.0%
```

## 1. The block (`block.py`)

A pre-norm causal decoder block:

```
x = x + MultiHeadAttention(LayerNorm(x))     # causal self-attention
x = x + MLP(LayerNorm(x))                     # position-wise feed-forward
```

The pieces are all here and checkable as properties:

- **`attention(Q,K,V, causal=True)`** — `softmax(QKᵀ/√d)·V` with a causal mask, so
  each position attends only to itself and the past. Attention rows are
  probability distributions; the upper triangle is exactly zero.
- **`layernorm`** — normalizes each vector to mean 0, variance 1.
- **`multihead`** — splits the projected stream into heads, attends per head, and
  recombines through an output projection.
- **residual stream** — zero the two sublayer output weights (`Wo`, `W2`) and the
  whole block collapses to the **identity**: the residual path carries the input
  through untouched. (A nice from-scratch sanity check.)

## 2. The induction circuit (`induction.py`)

In-context learning's simplest form is *induction*: see `A B` earlier, then on the
next `A`, predict `B`. Anthropic's interpretability work showed this is a
**two-layer circuit**:

1. **Previous-token head** (layer 1): each position attends to the one before it
   and writes that token's identity into the residual stream. Built with a purely
   *positional* query/key — with `qᵢ = [i−1, 1]` and `kⱼ = [2C·j, −C·j²]`, the
   score `qᵢ·kⱼ = −C·((i−1)−j)²` (up to a constant), so attention peaks at `j=i−1`.
2. **Induction head** (layer 2): the current token queries those previous-token
   marks, attends to positions whose *predecessor* equals it, and copies the token
   there — the token that last followed the current one.

Both layers are the block's genuine `attention`, with Q/K/V constructed directly
(exactly how the circuit is described by its QK/OV maps). A **BOS sentinel** gives
position 0 a real predecessor, removing the beginning-of-sequence artifact. The
result: it continues repeated patterns with **100% accuracy**, while a **one-layer
ablation** (match the current token to past tokens and copy them — no
previous-token head) scores **0%**. That gap *is* the reason induction needs two
layers.

## Tests

```sh
python -m unittest labs.transformer.tests.test_transformer -v
```

13 tests: softmax/layernorm/attention-causality/multihead shapes; the block's
output shape, causal no-future-leak, residual-identity-when-zeroed, determinism;
and the circuit — clean examples (`abcabca→b`), 100% on repeated patterns, the
one-layer ablation failing, and the previous-token head marking the right
predecessor.
