"""forest — a random forest, from scratch (an ensemble of the lab's decision tree).

One decision tree is high-variance: it overfits, and small data changes swing it
a lot. A **random forest** trains many trees on bootstrap resamples with random
feature subsets, so they overfit in different directions, and votes them — the
noise cancels and the result is more accurate and far more stable. It also yields
a free validation score from each point's **out-of-bag** trees.

Reuses ``tree.DecisionTree`` (extended with ``max_features``). Offline,
deterministic. Caps the lab's tree thread: ``tree`` → ``forest``.
"""
from .forest import RandomForest

__all__ = ["RandomForest"]
