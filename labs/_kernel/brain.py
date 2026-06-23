"""LLM backend abstraction: a real Anthropic brain plus an offline fallback.

Every lab MVP runs in one of two modes:

* **online** — if ``ANTHROPIC_API_KEY`` is set *and* the ``anthropic`` SDK is
  importable, :func:`get_brain` returns an :class:`AnthropicBrain` that calls
  the real model.
* **offline** — otherwise :func:`get_brain` returns ``None`` and each MVP falls
  back to its own deterministic, stdlib-only reasoning. This guarantees every
  demo runs on a fresh clone with no key and nothing installed.

Keeping the online path behind a tiny, uniform interface means an MVP's engine
never branches on "do we have a model?" beyond a single ``brain is None`` check.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")


def api_key() -> str | None:
    """Return the Anthropic API key from the environment, or ``None``."""
    return os.environ.get("ANTHROPIC_API_KEY") or None


def anthropic_available() -> bool:
    """True only if both a key and the SDK are present."""
    if not api_key():
        return False
    try:
        import anthropic  # noqa: F401
    except Exception:
        return False
    return True


@dataclass
class AnthropicBrain:
    """Thin wrapper over the Anthropic Messages API.

    Exposes a single ``complete`` entry point plus a ``complete_json`` helper
    that asks for and best-effort parses a JSON object — enough for the
    structured persona/agent responses the MVPs need without dragging in a
    schema dependency.
    """

    model: str = DEFAULT_MODEL
    max_tokens: int = 1024
    online: bool = True

    def __post_init__(self) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key())

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if system:
            kwargs["system"] = system
        msg = self._client.messages.create(**kwargs)
        return "".join(
            b.text for b in msg.content if getattr(b, "type", "") == "text"
        )

    def complete_json(self, prompt: str, **kwargs) -> dict:
        raw = self.complete(prompt, **kwargs)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"model did not return JSON: {raw[:200]!r}")
        return json.loads(match.group(0))


def get_brain(model: str | None = None) -> AnthropicBrain | None:
    """Return an online brain if available, else ``None`` (offline mode)."""
    if anthropic_available():
        return AnthropicBrain(model=model or DEFAULT_MODEL)
    return None


def mode() -> str:
    """``"online"`` if a real brain is available, else ``"offline"``."""
    return "online" if anthropic_available() else "offline"
