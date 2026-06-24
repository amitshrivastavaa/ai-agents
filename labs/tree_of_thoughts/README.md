# tree_of_thoughts — deliberate reasoning as search

> Give it four numbers; it reaches **24** with `+ - * /` by *searching over
> thoughts* — generating partial solutions, scoring each by a sampled
> look-ahead, and keeping only the promising ones. The clearest possible demo of
> "test-time compute": more thinking, applied where it counts.

The Game of 24 is the canonical Tree-of-Thoughts benchmark, and a perfect
offline one: every thought is *exactly* checkable (we use `fractions`, so
`8 / (3 - 8/3) = 24` is found, not lost to float error). Fully stdlib,
deterministic.

## Quick start

```sh
python -m labs.tree_of_thoughts.demo                  # the hard puzzle + a comparison
python -m labs.tree_of_thoughts.cli solve 3 3 8 8     # watch it reason to 24
python -m labs.tree_of_thoughts.cli solve 4 6 8 2 --method random
python -m labs.tree_of_thoughts.cli compare           # tot vs random vs brute
python -m labs.tree_of_thoughts.cli list
```

## The three searchers

| Method | How much it deliberates |
| --- | --- |
| `random` | none — sample full random play-outs and hope one lands on 24. |
| `tree_of_thoughts` | **beam search over partial states**; each candidate thought is scored by a **Monte-Carlo value** (sampled look-ahead) and only the top `beam_width` are kept. |
| `brute_force` | the exact solver / verifier — explores everything (ground truth). |

A "thought" is a state: the numbers left to combine. Each step merges two of them
with an operator, shrinking four numbers → three → two → one. Reaching `[24]` wins.

## The result

```
The famously hard puzzle (3, 3, 8, 8) — only 8 / (3 - 8/3) works.
  random play-outs   ✗ missed                                   (600 states)
  tree-of-thoughts   ✅  8 / 3 = 8/3  →  3 - 8/3 = 1/3  →  8 / 1/3 = 24   (187 states)

Across a 10-puzzle suite (8 solvable):
  random            5/8     333 states
  tree_of_thoughts  8/8     172 states
  brute_force       8/8     367 states
```

Tree-of-Thoughts **matches brute force's correctness while examining ~2× fewer
states**, and beats random — which wanders through *more* states yet solves
*fewer*. Scoring and pruning thoughts (deliberation) is what buys the
efficiency. Crank `--beam` / `--samples` to spend more test-time compute; drop
them to watch accuracy fall — the trade-off, in your hands.

## Why offline works here

The Tree-of-Thoughts paper uses an LLM to *value* each thought. Here the value is
a Monte-Carlo estimate — a handful of random completions, counting how often they
hit 24 — so the whole method runs with no model and stays deterministic. Same
shape, exact arithmetic, no API key.

## Tests

```sh
python -m unittest labs.tree_of_thoughts.tests.test_tot -v
```
