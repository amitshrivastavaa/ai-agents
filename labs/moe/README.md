# moe — a mixture of experts

> A **router** sends each input to the **expert** best suited to it; the experts
> specialize on different regimes of the data, and together they fit a piecewise
> problem no single model can. Watch a few linear experts carve up a curve and
> beat one global fit by 14×.

The original Mixture-of-Experts idea (Jacobs et al., 1991) — which is exactly the
sparse top-k routing inside today's MoE LLMs (Mixtral & friends). Fully offline,
deterministic.

## Quick start

```sh
python -m labs.moe.demo
python -m labs.moe.cli train --dataset piecewise --experts 3 --watch
python -m labs.moe.cli train --dataset fan --experts 4 --watch
python -m labs.moe.cli compare --dataset piecewise
```

```
'piecewise' — one model can't fit 3 regimes; 3 experts can.
  single model MSE : 0.0341
  3-expert mixture : 0.0024   (14.5× better)
  load per expert  : [32, 42, 46]      ← the router keeps every expert busy
  gate centres     : [0.19, 0.49, 0.82]

   0011                          (each digit is the expert the gate routed
  0·  ·11                         that input to — experts 0, 1, 2 each own a
 0      ·1·         ·22·          contiguous slice and fit its slope)
0         1·    ·22·   ·2
            11 22
```

## How it works (proper MoE EM)

The gate scores experts by **input** location (a Gaussian bump around each
expert's centre). Training is expectation-maximization:

- **E-step** — each point's *responsibility* for an expert combines the gate
  with how well that expert predicts the target:
  `r ∝ gate_e(x) · 𝒩(y; expert_e(x), σ)`.
- **M-step** — every expert refits by **weighted least squares** (weighted by its
  responsibilities) and recentres its gate on the inputs it now owns. A starving
  expert is re-seeded — the load-balancing pressure that keeps all experts used.

At inference the gate sees only `x`, so it routes to the highest-gate expert
(top-1) and predicts with it (or blends the top experts softly).

## What you see

Adding experts helps until there's roughly one per regime, then plateaus — the
router has carved the input space into specialists:

| experts | piecewise MSE | vs single |
| ---: | ---: | ---: |
| 1 | 0.0341 | 1.0× |
| 2 | 0.0124 | 2.7× |
| 3 | 0.0024 | 14.5× |
| 4 | 0.0024 | 14.5× (plateau) |

Load stays balanced (`[32, 42, 46]`) and the gate centres land on the regime
midpoints — exactly the specialization an MoE is supposed to discover.

## Tests

```sh
python -m unittest labs.moe.tests.test_moe -v
```
