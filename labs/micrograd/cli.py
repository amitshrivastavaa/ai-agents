"""CLI for the from-scratch autograd engine + neural net.

    python -m labs.micrograd.cli train --dataset xor
    python -m labs.micrograd.cli train --dataset circles --epochs 150 --hidden 8,8
    python -m labs.micrograd.cli train --dataset sine
    python -m labs.micrograd.cli gradcheck
    python -m labs.micrograd.cli list
"""
from __future__ import annotations

import argparse
import sys

from .engine import Value
from .render import decision_boundary, regression_plot, sparkline
from .train import DATASETS, get_dataset, train


def _cmd_train(args) -> int:
    data = get_dataset(args.dataset)
    hidden = tuple(int(h) for h in args.hidden.split(",") if h)
    res = train(data, hidden=hidden, epochs=args.epochs, lr=args.lr, seed=args.seed)
    print(f"# MLP {[len(data.X[0]), *hidden, 1]} on '{data.name}'  "
          f"({len(res.model.parameters())} params, {args.epochs} epochs)\n")
    print(f"  loss {res.loss_history[0]:.3f} → {res.final_loss:.4f}   "
          f"{sparkline(res.loss_history)}")
    if res.accuracy is not None:
        print(f"  accuracy: {res.accuracy:.0%}\n")
        print(decision_boundary(res.model, data))
        print("  ░ = model predicts +1 · '+' / 'o' = training points (true class)")
    else:
        print(f"  final MSE: {res.final_loss:.4f}\n")
        print(regression_plot(res.model, data))
    return 0


def _cmd_gradcheck(_args) -> int:
    import math
    a, b, c = Value(-1.5), Value(2.0), Value(0.7)
    f = (a * b + c.tanh()) * b - a ** 2
    f.backward()
    fa = lambda x: ((x * 2.0) + math.tanh(0.7)) * 2.0 - x ** 2
    num_a = (fa(-1.5 + 1e-6) - fa(-1.5 - 1e-6)) / 2e-6
    print(f"  ∂f/∂a  autograd={a.grad:.5f}  numerical={num_a:.5f}  "
          f"{'✅ match' if abs(a.grad - num_a) < 1e-3 else '✗'}")
    return 0


def _cmd_list(_args) -> int:
    for name in DATASETS:
        d = DATASETS[name]()
        print(f"  {name:<8} {len(d.X)} points · {d.task}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="micrograd", description="A neural net trained by an autograd engine built from scratch.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("train")
    p.add_argument("--dataset", default="xor")
    p.add_argument("--hidden", default="8", help="comma-separated, e.g. 8 or 8,8")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--lr", type=float, default=0.05)
    p.add_argument("--seed", default="mlp")
    p.set_defaults(func=_cmd_train)

    sub.add_parser("gradcheck").set_defaults(func=_cmd_gradcheck)
    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
