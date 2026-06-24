"""micrograd — a tiny reverse-mode autograd engine, and a net that learns on it.

The whole substrate of deep learning, from scratch and in the standard library:
a scalar :class:`Value` that records the operations performed on it into a graph,
a ``backward()`` that walks that graph in reverse applying the chain rule, a
small MLP built out of Values, and an SGD training loop that genuinely drives a
loss down — solving XOR, separating 2-D clusters, and fitting a curve.

No numpy, no framework — backprop you can read end to end. (Homage to Karpathy's
micrograd; the "build ML from scratch" thread that keeps trending.)
"""
from .engine import Value
from .nn import MLP, Layer, Neuron
from .train import DATASETS, TrainResult, get_dataset, train

__all__ = ["Value", "MLP", "Layer", "Neuron",
           "DATASETS", "TrainResult", "get_dataset", "train"]
