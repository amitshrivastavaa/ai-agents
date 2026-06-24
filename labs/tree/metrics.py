"""Accuracy and a tiny train/test depth sweep."""
from __future__ import annotations

from .tree import DecisionTree


def accuracy(y_pred, y_true):
    return sum(1 for a, b in zip(y_pred, y_true) if a == b) / len(y_true)


def depth_sweep(Xtr, ytr, Xte, yte, depths=range(1, 11)):
    """(depth, train_acc, test_acc) for each depth — shows the overfitting gap."""
    out = []
    for d in depths:
        t = DecisionTree(max_depth=d).fit(Xtr, ytr)
        out.append((d, accuracy(t.predict(Xtr), ytr), accuracy(t.predict(Xte), yte)))
    return out
