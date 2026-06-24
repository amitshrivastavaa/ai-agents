"""flow — flow matching / rectified flow, from scratch.

The generative method now powering Stable Diffusion 3 and Flux: instead of
reversing a noisy diffusion SDE, learn a **velocity field** and integrate a
deterministic ODE that flows a Gaussian straight onto the data.

This MVP uses the *analytic* marginal velocity for an empirical target (no
training needed, exactly like the lab's `diffusion` MVP uses the analytic score):

    v(x,t) = (ŷ(x,t) − x) / (1 − t),   ŷ = posterior-mean data point.

Integrating `dx/dt = v(x,t)` from `x₀ ~ N(0,I)` carries noise onto the target —
ring, clusters, grid, moons, spiral — in ~16 deterministic steps, where a noisy
Langevin diffusion sampler needs far more. Offline, deterministic.
"""
from . import targets
from .field import base_sample, weights, denoiser, velocity
from .sample import (integrate, generate, nearest_data_rmse, mode_coverage,
                     straightness)

__all__ = [
    "targets",
    "base_sample", "weights", "denoiser", "velocity",
    "integrate", "generate", "nearest_data_rmse", "mode_coverage", "straightness",
]
