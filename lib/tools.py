"""Reusable tool definitions and executors for agents.

Each tool exposes:
  * a JSON-schema definition (for the Anthropic API `tools` parameter)
  * a Python executor that runs the tool against the current repo

Executors return the string content to send back as a `tool_result`.
"""
from __future__ import annotations

from .repo import repo_root


READ_FILE_TOOL = {
    "name": "read_file",
    "description": (
        "Read a file from the repository. Use this to see code surrounding a "
        "diff hunk, or to inspect a file referenced by the change. Returns "
        "the file contents with line numbers."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Repository-relative path to the file.",
            },
            "start_line": {
                "type": "integer",
                "description": "Optional 1-indexed start line (inclusive).",
            },
            "end_line": {
                "type": "integer",
                "description": "Optional 1-indexed end line (inclusive).",
            },
        },
        "required": ["path"],
    },
}


def read_file(
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> str:
    """Read a repo-relative file, sandboxed to the worktree."""
    root = repo_root()
    target = (root / path).resolve()
    # Refuse paths that escape the worktree.
    if not str(target).startswith(str(root)):
        return f"Error: path {path!r} is outside the repository."
    if not target.exists():
        return f"Error: file {path!r} does not exist."
    if not target.is_file():
        return f"Error: {path!r} is not a regular file."

    try:
        lines = target.read_text().splitlines()
    except UnicodeDecodeError:
        return f"Error: {path!r} is not a text file."

    start = max(1, start_line or 1)
    end = min(len(lines), end_line or len(lines))
    if start > len(lines):
        return f"Error: start_line {start} is past end of file ({len(lines)} lines)."

    width = len(str(end))
    numbered = "\n".join(
        f"{i:>{width}}\t{lines[i - 1]}" for i in range(start, end + 1)
    )
    return f"# {path} (lines {start}-{end} of {len(lines)})\n{numbered}"
