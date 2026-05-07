"""Shared LLM helpers: cached system prompts and a tool-use loop runner.

Every agent in this repo follows the same pattern: a cached system prompt, a
set of tools, and a loop that dispatches tool calls until the model stops.
This module encapsulates that loop so individual agents stay focused on
their domain logic (prompts, tools, output parsing).
"""
from __future__ import annotations

from typing import Any, Callable

import anthropic


def cached_system(text: str) -> list[dict]:
    """Wrap a system prompt in a single cached text block.

    All agents share this so the system prompt is never invalidated by a
    per-request value (timestamp, request ID, etc.). Render-time inputs that
    vary per request belong in the user message, not here.
    """
    return [
        {
            "type": "text",
            "text": text,
            "cache_control": {"type": "ephemeral"},
        }
    ]


class ToolLoopExceeded(RuntimeError):
    """Raised when the tool loop hits `max_iterations` without `end_turn`."""


def run_tool_loop(
    client: anthropic.Anthropic,
    *,
    model: str,
    system: list[dict] | str,
    tools: list[dict],
    dispatch: Callable[[str, dict], str],
    messages: list[dict],
    max_tokens: int = 16000,
    max_iterations: int = 12,
    thinking: dict | None = None,
    output_config: dict | None = None,
    on_text: Callable[[str], None] | None = None,
    on_tool_use: Callable[[str, dict], None] | None = None,
) -> "anthropic.types.Message":
    """Drive a tool-use loop until the model produces a non-tool stop.

    Args:
        client: Anthropic client instance.
        model: Model ID (e.g. ``claude-opus-4-7``).
        system: System prompt — pass the result of `cached_system(...)` to
            keep prefix caching effective.
        tools: JSON-schema tool definitions.
        dispatch: Callback that executes a tool by name and returns the
            string content for the matching `tool_result` block.
        messages: Mutable conversation. Mutated in place across iterations.
        max_tokens: Per-response cap.
        max_iterations: Safety cap on loop turns.
        thinking: Optional thinking config (e.g. ``{"type": "adaptive"}``).
        output_config: Optional structured-output config — applied to every
            iteration; only constrains the final text response.
        on_text: Optional callback fired for each non-empty text block.
        on_tool_use: Optional callback fired before each tool dispatch.

    Returns:
        The final Anthropic ``Message`` (the one that stopped the loop).

    Raises:
        ToolLoopExceeded: If `max_iterations` is reached.
    """
    for _ in range(max_iterations):
        kwargs: dict[str, Any] = dict(
            model=model,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )
        if thinking is not None:
            kwargs["thinking"] = thinking
        if output_config is not None:
            kwargs["output_config"] = output_config

        response = client.messages.create(**kwargs)

        if on_text is not None:
            for block in response.content:
                if block.type == "text" and block.text.strip():
                    on_text(block.text)

        if response.stop_reason != "tool_use":
            return response

        messages.append({"role": "assistant", "content": response.content})

        tool_results: list[dict] = []
        for block in response.content:
            if block.type == "tool_use":
                if on_tool_use is not None:
                    on_tool_use(block.name, dict(block.input))
                result = dispatch(block.name, dict(block.input))
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    raise ToolLoopExceeded(
        f"tool loop exceeded {max_iterations} iterations without end_turn"
    )
