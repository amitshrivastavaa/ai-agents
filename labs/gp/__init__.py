"""gp — Gaussian Process regression, from scratch.

Bayesian non-parametric regression: put a prior over functions, condition on the
data, and read off a posterior **mean and variance** in closed form. With an RBF
kernel the predictive distribution is

    mean(x*) = k*ᵀ K⁻¹ y,     var(x*) = k(x*,x*) − k*ᵀ K⁻¹ k*.

The point is the variance — **calibrated uncertainty** that shrinks to the noise
floor at the data and grows back to the prior away from it, so the model knows
what it doesn't know. Solved through a Cholesky factor of the kernel matrix; no
training loop, no randomness. Complements the lab's Bayesian `kalman` filter.
"""
from .linalg import cholesky, chol_solve, solve_lower, solve_upper_T
from .gp import GP, rbf

__all__ = ["GP", "rbf", "cholesky", "chol_solve", "solve_lower", "solve_upper_T"]
