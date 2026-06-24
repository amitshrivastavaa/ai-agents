# micrograd — an autograd engine (and a net that learns) from scratch

> The entire substrate of deep learning, in the standard library: a scalar
> `Value` that records a computation graph, a `backward()` that walks it in
> reverse with the chain rule, a small MLP built from Values, and an SGD loop
> that genuinely drives loss down — solving XOR, separating circles, fitting a
> curve. No numpy, no framework. Backprop you can read end to end.

The "build ML from scratch" thread that keeps trending (homage to Karpathy's
micrograd). Deterministic, fully offline.

## Quick start

```sh
python -m labs.micrograd.demo                          # learn XOR, circles, sin(x)
python -m labs.micrograd.cli train --dataset xor
python -m labs.micrograd.cli train --dataset circles --epochs 160 --hidden 8
python -m labs.micrograd.cli train --dataset sine
python -m labs.micrograd.cli gradcheck                 # autograd vs numerical
```

```
1) XOR (not linearly separable) → accuracy 100%   █▇▆▅▄▃▂▁ …
   ░░░░░+░░░░░          o
   ░░░░░░░░░░░░░░
        ░░░░░░░░░░░░
   o          ░░░░░░+░
   ░ = model predicts +1 · '+'/'o' = training points (true class)
```

## The engine

`Value` is a scalar that remembers how it was made:

```python
from labs.micrograd import Value
a, b = Value(-1.5), Value(2.0)
f = (a * b + a.tanh()) * b
f.backward()        # fills a.grad, b.grad via reverse-mode autodiff
```

`backward()` topologically sorts the graph and applies the chain rule from the
output back to every leaf — exactly the algorithm under PyTorch/TensorFlow, in a
couple dozen lines. The grads match numerical differentiation (`cli gradcheck`).

One subtlety worth the comment in the code: the graph's child links are kept in
an **ordered tuple**, not a set — set iteration is id-based, and SGD is chaotic
enough that the resulting float-ordering differences make "the same run" diverge.
Ordered children → reproducible training.

## The net

`Neuron` → `Layer` → `MLP`, all built from `Value`, with tanh hidden units and a
linear output. `train()` does full-batch gradient descent: forward every point,
sum the squared error, one `backward()`, then `p.data -= lr * p.grad`.

| dataset | what it shows | result |
| --- | --- | --- |
| `xor` | a nonlinear function a single layer can't do | **100%** |
| `blobs` | two Gaussian clusters | ~100% |
| `circles` | concentric rings — needs a hidden layer | ~93% |
| `sine` | regression onto a curve | MSE ~0.04 |

`train --dataset circles --hidden 8,8` (two hidden layers) pushes circles to
~98%, at the cost of more scalar ops (it's pure Python — correctness over speed).

## Tests

```sh
python -m unittest labs.micrograd.tests.test_micrograd -v
```
