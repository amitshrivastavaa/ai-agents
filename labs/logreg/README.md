# logreg — logistic regression by gradient descent, from scratch

> The classifier every ML course starts with — and still a production workhorse.
> Model the probability of the positive class as a squashed linear score,
> `P(y=1|x) = σ(w·x + b)`, and fit `w, b` by minimizing **cross-entropy**. That
> loss is *convex*, so plain gradient descent slides straight to the global
> optimum — no local minima, no restarts — and the outputs are genuine, calibrated
> probabilities.

The **discriminative** counterpart to the lab's generative [`naivebayes`](../naivebayes/)
(learn the boundary vs. model each class), and the linear baseline the non-linear
[`tree`](../tree/)/[`forest`](../forest/) are measured against. Offline,
deterministic.

## Quick start

```sh
python -m labs.logreg.demo
python -m labs.logreg.cli fit --data linear
python -m labs.logreg.cli loss --data linear
```

```
It draws the best straight boundary between two classes (o / #):
  |··········░░░░░#░░░#░#############░░###░#░░░░░|
  |··oo····o··o·oooo###·o░#░######░###░░░░#░░░#░░|
  test accuracy 98%   weights w=(+3.31, +3.66), b=+0.60

loss (convex):  █▃▂▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁  (0.69 → 0.06)
  said 100% → actually 98% positive     ← the probabilities mean what they say
```

## How it works (`logreg.py`)

- **Standardize** features (zero mean, unit variance) so gradient descent is
  well-conditioned.
- **Gradient descent** on cross-entropy: the gradient is beautifully simple —
  `∂L/∂w = mean((σ(w·x+b) − y)·x)` — the prediction error times the input. Full-batch
  steps, optional **L2** weight decay.
- Because the loss is convex, the `loss_history` is **monotonically decreasing** and
  the fixed point it reaches is the unique global optimum.

## What it shows

- **A clean linear boundary** — ~97% on linearly separable data, with interpretable
  weights (sign = which way each feature votes).
- **Convex descent** — the loss curve only ever goes down to the global minimum;
  the test asserts it.
- **Real probabilities** — group predictions by confidence and the empirical
  positive rate matches (said 100% → ~98% positive). Useful when you need a *score*,
  not just a label.
- **Its honest limit** — one straight line tops out at ~86% on non-linear moons,
  which is exactly where trees/forests (or kernels) earn their keep.
- **Deterministic** — same data, same weights.

## Tests

```sh
python -m unittest labs.logreg.tests.test_logreg -v
```

7 tests: sigmoid, separates linear data (>90%), the loss is monotone-convex and
halves, probabilities are in range and calibrated, it underfits moons (the linear
limit), L2 shrinks the weights, and it's deterministic.
