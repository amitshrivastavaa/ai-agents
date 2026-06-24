# symbolic_regression — evolve the equation from the data

> Give it points sampled from a hidden function and it **rediscovers the
> formula** — searching the space of mathematical expressions for one that
> reproduces the numbers. From `(x, y)` pairs alone it recovers `x*x - 2`,
> `x*sin(x)`, and `(x*x - 1)*x`.

The search is **genetic programming over expression trees**, and the fitness is
just *how well a formula fits*, evaluated exactly. That "you don't need to know
the answer, only how to score a guess" loop is the heart of evolutionary program
search — the idea behind **AlphaEvolve** ("the verifier was a clock"). Fully
offline, deterministic.

## Quick start

```sh
python -m labs.symbolic_regression.demo
python -m labs.symbolic_regression.cli discover --target quadratic
python -m labs.symbolic_regression.cli discover --target damped --gens 60
python -m labs.symbolic_regression.cli list
```

```
target    hidden formula   discovered                  MSE
linear    2*x + 1          ((x + x) + 1)               0   ✅
quadratic x*x - 2          (((x * x) - 1) + -1)        0   ✅
cubic     x*x*x - x        (((x * x) + -1) * x)        ~0  ✅   ← found the factored form
damped    x*sin(x)         (sin(x) * x)                0   ✅
```

## How it works

- **Expressions are trees** of operators (`+ − × ÷ sin neg`) over the variable
  `x` and constants. Operators are *protected* (÷0 → 1, results clamped) so every
  random formula evaluates to a finite number.
- **Genetic programming.** Start from a population of random trees. Each
  generation: score each by mean-squared error against the data (plus a small
  size penalty — Occam's razor), keep the elite, and breed the rest by
  **crossover** (graft a sub-formula from one parent into another) and
  **mutation** (rewrite a random sub-formula). Repeat until the error hits zero.
- **The verifier is the data.** The search never sees the target formula — only
  how far each guess's outputs are from the observed `y`. That's all it needs.

A light, semantics-preserving simplifier tidies the winner for display (`--a → a`,
`a*1 → a`, constant folding), so you get a readable equation, not a tangle of
double negatives.

## Why it matters

This is the smallest honest version of evolutionary program/algorithm discovery:
a population of candidate *programs*, a runnable *verifier*, and selection. Scale
the operator set and the verifier and the same loop searches for algorithms, not
just formulas — which is exactly how systems like AlphaEvolve find new ones.

## Tests

```sh
python -m unittest labs.symbolic_regression.tests.test_symbolic_regression -v
```
