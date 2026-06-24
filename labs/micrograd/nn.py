"""A minimal neural-network library built on the autograd :class:`Value`."""
from __future__ import annotations

from .._kernel import rng
from .engine import Value


class Module:
    def parameters(self) -> list[Value]:
        return []

    def zero_grad(self) -> None:
        for p in self.parameters():
            p.grad = 0.0


class Neuron(Module):
    def __init__(self, nin: int, *, nonlin: bool = True, r=None):
        scale = nin ** -0.5
        self.w = [Value(r.gauss(0.0, scale)) for _ in range(nin)]
        self.b = Value(0.0)
        self.nonlin = nonlin

    def __call__(self, x):
        act = self.b
        for wi, xi in zip(self.w, x):
            act = act + wi * xi
        return act.tanh() if self.nonlin else act

    def parameters(self):
        return self.w + [self.b]


class Layer(Module):
    def __init__(self, nin: int, nout: int, *, nonlin: bool = True, r=None):
        self.neurons = [Neuron(nin, nonlin=nonlin, r=r) for _ in range(nout)]

    def __call__(self, x):
        outs = [n(x) for n in self.neurons]
        return outs[0] if len(outs) == 1 else outs

    def parameters(self):
        return [p for n in self.neurons for p in n.parameters()]


class MLP(Module):
    """A multilayer perceptron with tanh hidden layers and a linear output."""

    def __init__(self, nin: int, nouts: list[int], *, seed: str = "mlp"):
        r = rng(seed, nin, tuple(nouts))
        sizes = [nin] + nouts
        last = len(nouts) - 1
        self.layers = [
            Layer(sizes[i], sizes[i + 1], nonlin=(i != last), r=r)
            for i in range(len(nouts))
        ]

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]
