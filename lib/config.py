"""Application config loaded from environment variables.

Centralizing config keeps secrets out of agent code and makes it easy to swap
models per environment (dev/stage/prod) without code changes.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Runtime config for an agent invocation."""

    anthropic_api_key: str
    default_model: str = "claude-opus-4-7"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return cls(
            anthropic_api_key=api_key,
            default_model=os.environ.get("CLAUDE_MODEL", cls.default_model),
            log_level=os.environ.get("LOG_LEVEL", cls.log_level),
        )
