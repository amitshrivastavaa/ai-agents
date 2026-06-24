"""logreg — logistic regression by gradient descent, from scratch.

The canonical linear classifier: ``P(y=1|x) = σ(w·x + b)``, fit by minimizing the
**convex** cross-entropy loss, so gradient descent reaches the global optimum with
no local minima. Outputs are genuine, reasonably-calibrated probabilities, and the
weights are interpretable.

It's the **discriminative** counterpart to the lab's generative `naivebayes` (learn
the boundary vs. model each class), and the linear baseline the non-linear `tree`/
`forest` are measured against. Offline, deterministic.
"""
from .logreg import LogisticRegression, sigmoid
from .data import linear, moons, split

__all__ = ["LogisticRegression", "sigmoid", "linear", "moons", "split"]
