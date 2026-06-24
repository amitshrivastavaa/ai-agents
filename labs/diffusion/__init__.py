"""diffusion — generate samples from noise with a score-based diffusion model.

Start from pure noise and walk it, step by step, into samples that match a
target distribution — the inference process at the heart of every diffusion
model (Stable Diffusion & friends), here on 2-D toy shapes you can watch form in
ASCII.

The offline trick: a diffusion model's only learned component is the **score**
∇log p(x). For a target that's a mixture of Gaussian modes the score is
*analytic*, so we can run the real sampler — **annealed Langevin dynamics** (the
score-based generative sampler) — with no training at all. Noise → ring, spiral,
or clusters, exactly as the math predicts. Fully offline, deterministic.
"""
from .diffusion import generate, score
from .target import TARGETS, get_target

__all__ = ["generate", "score", "TARGETS", "get_target"]
