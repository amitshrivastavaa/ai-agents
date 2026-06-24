"""Shared, dependency-free building blocks reused across lab MVPs."""
from .brain import AnthropicBrain, anthropic_available, get_brain, mode
from .text import headline, keywords, pick, rng, stable_seed, tokens

__all__ = [
    "AnthropicBrain",
    "anthropic_available",
    "get_brain",
    "mode",
    "headline",
    "keywords",
    "pick",
    "rng",
    "stable_seed",
    "tokens",
]
