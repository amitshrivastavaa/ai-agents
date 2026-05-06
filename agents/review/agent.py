"""
review-agent: a CLI code-review agent for git diffs.

Uses Claude Opus 4.7 with adaptive thinking and prompt caching. Exposes a
read_file tool so the model can pull in surrounding source for context, then
streams a structured review to stdout.

Run from the repo root:
    python -m agents.review.agent                    # review staged changes
    python -m agents.review.agent --base main        # review current branch vs main
    python -m agents.review.agent --diff path.diff   # review a saved diff
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import anthropic

from lib.tools import READ_FILE_TOOL, read_file

MODEL = "claude-opus-4-7"
MAX_TOKENS = 32000
MAX_TOOL_ITERATIONS = 12

SYSTEM_PROMPT = """You are a senior code reviewer. You will be given a unified \
git diff. Produce a focused, actionable review.

Approach:
1. Read the diff carefully. If you need to see the surrounding code in any \
file (more context than the diff hunks show), call the `read_file` tool. \
Don't speculate when you can verify.
2. Group findings by severity: BLOCKER, MAJOR, MINOR, NIT. Skip empty groups.
3. For each finding: cite file:line, state the issue in one sentence, then \
explain why and suggest a concrete fix. Quote the offending code briefly.
4. End with a one-paragraph summary covering correctness, security, and \
maintainability.

Focus on: bugs, security issues (injection, auth, secrets), race conditions, \
error handling gaps, API misuse, and unclear logic. Skip pure style nits \
unless they obscure intent. Don't praise; reviewers don't pad.

If the diff looks fine, say so plainly and stop."""


def get_diff(args: argparse.Namespace) -> str:
    if args.diff:
        return Path(args.diff).read_text()
    if args.base:
        cmd = ["git", "diff", f"{args.base}...HEAD"]
    elif args.unstaged:
        cmd = ["git", "diff"]
    else:
        cmd = ["git", "diff", "--cached"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def dispatch_tool(name: str, tool_input: dict) -> str:
    if name == "read_file":
        return read_file(
            tool_input["path"],
            tool_input.get("start_line"),
            tool_input.get("end_line"),
        )
    return f"Error: unknown tool {name!r}"


def review(diff: str) -> None:
    if not diff.strip():
        print("No changes to review.", file=sys.stderr)
        return

    client = anthropic.Anthropic()

    # Cache the system prompt (stable across calls within the loop) so each
    # tool-result roundtrip reuses the prefix.
    system = [
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    user_content = (
        "Review the following diff. Use `read_file` if you need surrounding "
        "context.\n\n<diff>\n" + diff + "\n</diff>"
    )
    messages: list[dict] = [{"role": "user", "content": user_content}]

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=system,
            tools=[READ_FILE_TOOL],
            messages=messages,
        )

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(block.text)

        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(
                    f"\n[tool] read_file {block.input.get('path')}",
                    file=sys.stderr,
                )
                result = dispatch_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )
        messages.append({"role": "user", "content": tool_results})
    else:
        print(
            f"\n[review-agent] hit max tool iterations ({MAX_TOOL_ITERATIONS})",
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--base",
        help="Base ref to diff against (e.g. main). Reviews <base>...HEAD.",
    )
    source.add_argument(
        "--diff",
        help="Path to a saved diff file to review instead of running git.",
    )
    source.add_argument(
        "--unstaged",
        action="store_true",
        help="Review unstaged working-tree changes (default: staged).",
    )
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        return 1

    try:
        diff = get_diff(args)
    except subprocess.CalledProcessError as e:
        print(f"Error: git failed: {e.stderr}", file=sys.stderr)
        return 1

    review(diff)
    return 0


if __name__ == "__main__":
    sys.exit(main())
