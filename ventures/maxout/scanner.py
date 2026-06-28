"""Backlog finder — scan a repo for real, actionable work.

Deterministic, stdlib-only (uses `ast`). Each finding becomes a BacklogItem the
runner can hand to Claude Code. Signals:
  * module missing a docstring                         -> docs
  * public functions/classes lacking docstrings        -> docs
  * source module with no test file                    -> tests
  * TODO / FIXME / HACK / XXX markers                  -> todo
  * bare `except:` (swallows errors)                   -> bug
  * oversized file (> MAX_LINES)                        -> refactor
"""
from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "site", "dist", "build"}
SKIP_STEMS = {"__init__", "__main__", "demo", "cli", "conftest", "setup"}
MARKER = re.compile(r"#.*\b(TODO|FIXME|HACK|XXX)\b")
BARE_EXCEPT = re.compile(r"^\s*except\s*:")
MAX_LINES = 400

EST = {"tests": 120, "docs": 30, "todo": 30, "bug": 60, "refactor": 160}


@dataclass(frozen=True)
class BacklogItem:
    kind: str
    path: str
    line: int
    summary: str
    est_credits: int


def _has_test(py_path: str) -> bool:
    d = os.path.dirname(py_path)
    stem = os.path.splitext(os.path.basename(py_path))[0]
    candidates = [
        os.path.join(d, "tests", f"test_{stem}.py"),
        os.path.join(d, f"test_{stem}.py"),
        os.path.join(os.path.dirname(d), "tests", f"test_{stem}.py"),
    ]
    return any(os.path.exists(c) for c in candidates)


def scan_file(path: str, rel: str):
    items = []
    try:
        src = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return items
    lines = src.splitlines()

    if len(lines) > MAX_LINES:
        items.append(BacklogItem("refactor", rel, 1,
                                 f"{len(lines)} lines — split into smaller modules", EST["refactor"]))
    for i, ln in enumerate(lines, 1):
        if MARKER.search(ln):
            items.append(BacklogItem("todo", rel, i, ln.strip()[:80], EST["todo"]))
        if BARE_EXCEPT.match(ln):
            items.append(BacklogItem("bug", rel, i, "bare 'except:' swallows errors", EST["bug"]))

    stem = os.path.splitext(os.path.basename(path))[0]
    is_src = stem not in SKIP_STEMS and "/tests/" not in rel.replace(os.sep, "/")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return items

    if is_src and lines and ast.get_docstring(tree) is None:
        items.append(BacklogItem("docs", rel, 1, "module missing a docstring", EST["docs"]))

    missing = [n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
               and not n.name.startswith("_") and ast.get_docstring(n) is None]
    if is_src and missing:
        shown = ", ".join(missing[:3]) + ("…" if len(missing) > 3 else "")
        items.append(BacklogItem("docs", rel, 1,
                                 f"{len(missing)} public def(s) lack docstrings: {shown}", EST["docs"]))

    if is_src and not _has_test(path):
        items.append(BacklogItem("tests", rel, 1, "no test file for this module", EST["tests"]))
    return items


def scan_repo(root="."):
    items = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                p = os.path.join(dirpath, fn)
                items.extend(scan_file(p, os.path.relpath(p, root)))
    return items
