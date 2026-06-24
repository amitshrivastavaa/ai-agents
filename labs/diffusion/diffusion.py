"""Score-based diffusion: the analytic score, and annealed Langevin sampling.

For a target that is an equal-weight mixture of Gaussians with means ``μ_k`` and
variance ``v``, the score is

    ∇log p(x) = Σ_k  softmax_k(−‖x−μ_k‖²/2v) · (μ_k − x) / v

— a responsibility-weighted pull toward the modes. Smoothing the data with noise
``σ`` just inflates the variance to ``v = σ₀² + σ²``, which is exactly what a
diffusion model's denoiser approximates at each noise level. Annealed Langevin
walks samples from large noise to small, following that score, and they settle
onto the target shape.
"""
from __future__ import annotations

import math

from .._kernel import rng
from .target import Target


def score(point, modes, var: float):
    """Analytic score ∇log p(point) of the Gaussian mixture at variance ``var``."""
    px, py = point
    logits = []
    for mx, my in modes:
        d2 = (px - mx) ** 2 + (py - my) ** 2
        logits.append(-d2 / (2 * var))
    m = max(logits)
    weights = [math.exp(l - m) for l in logits]
    z = sum(weights) or 1.0
    sx = sy = 0.0
    for (mx, my), w in zip(modes, weights):
        r = w / z
        sx += r * (mx - px) / var
        sy += r * (my - py) / var
    return sx, sy


def _noise_levels(sigma_max: float, sigma_min: float, n: int) -> list[float]:
    ratio = (sigma_min / sigma_max) ** (1.0 / (n - 1))
    return [sigma_max * ratio ** i for i in range(n)]


def generate(target: Target, *, n: int = 200, levels: int = 12, steps: int = 18,
             eps: float = 0.08, sigma_max: float = 12.0, seed: str = "diff"):
    """Run annealed Langevin dynamics from noise; return the generated samples."""
    r = rng(seed, target.name)
    sigma_min = target.sigma0
    sigmas = _noise_levels(sigma_max, sigma_min, levels)

    samples = [(r.gauss(0, sigma_max), r.gauss(0, sigma_max)) for _ in range(n)]
    for sigma in sigmas:
        var = target.sigma0 ** 2 + sigma ** 2
        alpha = eps * (sigma / sigma_min) ** 2          # NCSN step-size schedule
        for _ in range(steps):
            new = []
            for (x, y) in samples:
                sx, sy = score((x, y), target.modes, var)
                nx = x + 0.5 * alpha * sx + math.sqrt(alpha) * r.gauss(0, 1)
                ny = y + 0.5 * alpha * sy + math.sqrt(alpha) * r.gauss(0, 1)
                new.append((nx, ny))
            samples = new
    return samples


def nearest_mode_distance(samples, target: Target) -> float:
    """Mean distance from each sample to its closest target mode (lower = better)."""
    total = 0.0
    for (x, y) in samples:
        total += min(math.hypot(x - mx, y - my) for mx, my in target.modes)
    return total / len(samples)
