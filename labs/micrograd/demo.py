"""Demo: an autograd engine learns XOR, separates circles, and fits a curve.

    python -m labs.micrograd.demo
"""
from __future__ import annotations

from .render import decision_boundary, regression_plot, sparkline
from .train import get_dataset, train


def main() -> int:
    print("A scalar autograd engine + SGD, learning from scratch:\n")

    xor = get_dataset("xor")
    res = train(xor, hidden=(8,), epochs=120, seed="demo")
    print(f"1) XOR (not linearly separable) → accuracy {res.accuracy:.0%}, "
          f"loss {res.loss_history[0]:.2f}→{res.final_loss:.3f}  {sparkline(res.loss_history)}")
    print(decision_boundary(res.model, xor, width=34, height=12))

    circ = get_dataset("circles")
    res = train(circ, hidden=(8,), epochs=160, seed="s")
    print(f"\n2) Concentric circles → accuracy {res.accuracy:.0%}  {sparkline(res.loss_history)}")
    print(decision_boundary(res.model, circ, width=34, height=14))

    sine = get_dataset("sine")
    res = train(sine, hidden=(10,), epochs=120, seed="demo")
    print(f"\n3) Regression: fit sin(x) → MSE {res.final_loss:.4f}  {sparkline(res.loss_history)}")
    print(regression_plot(res.model, sine))

    print("\nNo numpy, no framework — just Value, backward(), and gradient descent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
