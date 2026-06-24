"""Demo: watch deliberation solve the famously hard puzzle, then compare.

    python -m labs.tree_of_thoughts.demo
"""
from __future__ import annotations

from .game24 import expression
from .search import brute_force, compare, random_search, tot_search


def main() -> int:
    hard = (3, 3, 8, 8)
    print(f"The famously hard puzzle {hard} — only 8 / (3 - 8/3) works.\n")
    for fn, label in ((random_search, "random play-outs"),
                      (tot_search, "tree-of-thoughts")):
        res = fn(hard)
        mark = "✅" if res.solved else "✗ missed"
        sol = f"  {expression(res.path)}" if res.solved else ""
        print(f"  {label:<18} {mark}{sol}   ({res.nodes} states)")

    print("\n" + "=" * 64)
    print("Across a 10-puzzle suite (8 solvable):\n")
    c = compare()
    print(f"  {'method':<18}{'solved':>10}{'avg states':>14}")
    for m in ("random", "tree_of_thoughts", "brute_force"):
        print(f"  {m:<18}{c[m]['solved']:>4}/{c['solvable']:<5}{c[m]['avg_nodes']:>14}")
    print("\nMore thinking, applied where it counts — not more wandering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
