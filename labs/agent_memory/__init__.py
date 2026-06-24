"""agent_memory — a persistent memory layer that lets an agent grow with you.

Three memory systems working together:

* **episodic** — a time-stamped stream of observations (the "memory stream").
* **semantic** — higher-level insights distilled by *reflection* over episodes.
* **working** — the handful of most-recent episodes, the live context window.

Retrieval blends **relevance** (embedding similarity), **importance**, and
**recency** — the scoring from Stanford's *Generative Agents* — and the store
persists to JSON so memory survives across runs. Inspired by 2026's "agent that
grows with you" wave (Hermes & friends).

Runs offline with the stdlib alone: embeddings are a deterministic hashing
vectorizer, reflection is keyword clustering. A real model upgrades reflection
when ``ANTHROPIC_API_KEY`` is set.
"""
from .memory import Memory, MemoryStore, Scored

__all__ = ["Memory", "MemoryStore", "Scored"]
