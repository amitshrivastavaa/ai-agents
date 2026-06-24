# attention — the transformer's core, and an induction head

> The one operation at the heart of every transformer —
> `Attention(Q, K, V) = softmax(Q·Kᵀ/√d)·V` — built from scratch, plus the
> circuit that gives transformers their in-context magic: an **induction head**
> that continues a pattern it was never trained on. Show it `A B C A B C A` and
> it predicts `B`.

No numpy, no training. Fully offline and deterministic. This caps the lab's
"build the LLM from scratch" thread: tokenizer ([`bpe`](../bpe/)) → autograd
([`micrograd`](../micrograd/)) → experts ([`moe`](../moe/)) → **attention**.

## Quick start

```sh
python -m labs.attention.demo
python -m labs.attention.cli predict A B C A B C A
python -m labs.attention.cli predict the cat sat the cat
python -m labs.attention.cli selfattn a b a c a
```

```
sequence : A B C A B C A
predicted next token: 'B'

the induction head attended back to where 'A' last appeared, and copied
what followed:

  pos  token   attention
    0  A       ███████████▉ 0.50
    3  A       ███████████▉ 0.50      ← both earlier A's were followed by B
```

## Attention = a soft dictionary lookup

`attention(Q, K, V)` scores each query against every key (dot product), softmaxes
the scores into weights, and returns the weighted blend of values. It's
content-addressable memory: a query retrieves *what it matches*. `self_attention`
sets `Q = K = V = X`, so each token attends over the sequence by similarity —
identical tokens attend to each other, unique ones attend to themselves.

`scale` is the softmax temperature (default `1/√d`, the textbook value). A larger
scale sharpens attention onto a single key — which is what a *trained* model
achieves through the magnitude of its learned weights; here we just set it.

## The induction head (in-context learning, no training)

The circuit mechanistic-interpretability found inside real transformers, wired
by hand:

- **K[i]** = embedding of token *i*    — "where did this token appear?"
- **V[i]** = embedding of token *i+1*  — "what came after it?"
- **Q**    = embedding of the last token — "what are we continuing?"

`softmax(Q·Kᵀ)` lights up the positions whose token matches the query, and the
weighted sum of values returns the token that followed each — the prediction. So
the head **finds where the current token appeared before and copies what came
next**. That single mechanism is how a model continues `A B C A B C A → B`, or
`the cat sat the cat → sat`, having never been trained on those strings — the
essence of in-context learning.

## Tests

```sh
python -m unittest labs.attention.tests.test_attention -v
```
