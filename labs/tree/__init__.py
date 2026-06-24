"""tree — a CART decision tree for classification, from scratch.

Greedily split on the (feature, threshold) that most reduces impurity (Gini or
entropy), recurse, and label leaves by majority vote. Each split is an
axis-aligned cut, so the tree tiles feature space into rectangles — enough to
model non-linear boundaries (moons, even XOR) that a single linear classifier
can't. The building block of random forests and gradient boosting (XGBoost).

Pure stdlib, deterministic. Supervised companion to the lab's `kmeans`/`pca`.
"""
from .tree import DecisionTree, gini, entropy
from .data import blobs, xor, moons, train_test_split, DATASETS
from .metrics import accuracy, depth_sweep

__all__ = [
    "DecisionTree", "gini", "entropy",
    "blobs", "xor", "moons", "train_test_split", "DATASETS",
    "accuracy", "depth_sweep",
]
