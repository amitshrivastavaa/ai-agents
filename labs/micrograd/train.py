"""Toy datasets and a full-batch SGD training loop over the autograd engine."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .._kernel import rng
from .nn import MLP


@dataclass
class Dataset:
    name: str
    X: list[list[float]]
    y: list[float]
    task: str           # "clf" (labels ±1) or "reg" (real targets)


def _xor() -> Dataset:
    X = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
    y = [-1.0, 1.0, 1.0, -1.0]   # parity / XOR — not linearly separable
    return Dataset("xor", X, y, "clf")


def _blobs(n: int = 40, seed: str = "blobs") -> Dataset:
    r = rng(seed)
    X, y = [], []
    for _ in range(n):
        if r.random() < 0.5:
            X.append([r.gauss(-1.2, 0.4), r.gauss(-1.2, 0.4)]); y.append(-1.0)
        else:
            X.append([r.gauss(1.2, 0.4), r.gauss(1.2, 0.4)]); y.append(1.0)
    return Dataset("blobs", X, y, "clf")


def _circles(n: int = 44, seed: str = "circles") -> Dataset:
    r = rng(seed)
    X, y = [], []
    for i in range(n):
        inner = i % 2 == 0
        radius = (0.5 if inner else 1.6) + r.gauss(0, 0.1)
        theta = r.uniform(0, 2 * math.pi)
        X.append([radius * math.cos(theta), radius * math.sin(theta)])
        y.append(1.0 if inner else -1.0)   # concentric — needs a hidden layer
    return Dataset("circles", X, y, "clf")


def _sine(n: int = 24, seed: str = "sine") -> Dataset:
    X = [[x] for x in [(-3 + 6 * i / (n - 1)) for i in range(n)]]
    y = [math.sin(x[0]) for x in X]
    return Dataset("sine", X, y, "reg")


DATASETS = {"xor": _xor, "blobs": _blobs, "circles": _circles, "sine": _sine}


def get_dataset(name: str) -> Dataset:
    try:
        return DATASETS[name]()
    except KeyError:
        raise KeyError(f"unknown dataset {name!r}; choose from {sorted(DATASETS)}") from None


@dataclass
class TrainResult:
    dataset: str
    model: MLP
    loss_history: list[float]
    final_loss: float
    accuracy: float | None       # for classification


def _predict(model: MLP, x):
    out = model(x)
    return out


def train(data: Dataset, *, hidden=(8,), epochs: int = 100, lr: float = 0.05,
          seed: str = "mlp") -> TrainResult:
    nin = len(data.X[0])
    model = MLP(nin, [*hidden, 1], seed=seed)
    n = len(data.X)
    history: list[float] = []

    for epoch in range(epochs):
        model.zero_grad()
        total = None
        for xi, yi in zip(data.X, data.y):
            pred = _predict(model, xi)
            err = (pred - yi) ** 2
            total = err if total is None else total + err
        loss = total * (1.0 / n)
        loss.backward()
        # simple SGD with a touch of decay for stability
        rate = lr * (1.0 / (1.0 + 0.01 * epoch))
        for p in model.parameters():
            p.data -= rate * p.grad
        history.append(loss.data)

    accuracy = None
    if data.task == "clf":
        correct = sum(1 for xi, yi in zip(data.X, data.y)
                      if (1.0 if _predict(model, xi).data >= 0 else -1.0) == yi)
        accuracy = correct / n
    return TrainResult(data.name, model, history, history[-1], accuracy)
