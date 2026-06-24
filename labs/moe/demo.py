"""Demo: experts specialize on regimes a single model can't capture.

    python -m labs.moe.demo
"""
from __future__ import annotations

from .data import get_dataset
from .moe import MixtureOfExperts, single_model_error
from .render import plot_fit


def main() -> int:
    for name, k in (("piecewise", 3), ("fan", 4)):
        data = get_dataset(name)
        single = single_model_error(data)
        moe = MixtureOfExperts(k=k).train(data)
        err = moe.train_error(data)
        print("=" * 60)
        print(f"'{name}' — one model can't fit {len(set(data.region))} regimes; "
              f"{k} experts can.\n")
        print(f"  single model MSE : {single:.4f}")
        print(f"  {k}-expert mixture : {err:.4f}   ({single / max(err, 1e-9):.1f}× better)")
        print(f"  load per expert  : {moe.load()}")
        print(f"  gate centres     : {[round(c, 2) for c, _ in moe.regions()]}\n")
        print(plot_fit(data, moe))
        print()
    print("=" * 60)
    print("Each digit on the curve is the expert the gate routed that input to —")
    print("the router carved the input space into specialists. That's all an MoE")
    print("LLM (Mixtral & friends) does: send each token to a few of many experts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
