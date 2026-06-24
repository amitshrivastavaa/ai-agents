"""tree_of_thoughts — deliberate reasoning as search, on the Game of 24.

Given four numbers, reach 24 using + - * / (each number once). The catch that
makes this a perfect offline reasoning demo: every "thought" is *exactly*
checkable, so we can compare how different amounts of deliberation pay off:

* **random** — sample full random play-outs and hope one hits 24 (no thinking).
* **tree-of-thoughts** — beam search over partial states, scoring each candidate
  "thought" by a Monte-Carlo value (sampled look-ahead) and keeping only the most
  promising — the test-time-compute idea, made concrete.
* **brute force** — the exact solver / verifier (ground truth).

Tree-of-Thoughts solves nearly everything the brute solver can, while exploring
far fewer states than brute force and succeeding far more often than random.
Uses exact arithmetic (``fractions``) so 8/(3-8/3)=24 is found, not missed.
"""
from .game24 import Step, exact_solve, expression, is_goal, reachable
from .search import compare, random_search, tot_search

__all__ = [
    "Step", "exact_solve", "expression", "is_goal", "reachable",
    "compare", "random_search", "tot_search",
]
