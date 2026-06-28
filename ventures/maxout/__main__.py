"""CLI: print this week's Maxout report from the sample, or your own run log.

    python -m ventures.maxout                 # built-in sample
    python -m ventures.maxout runs.json       # your logged runs

runs.json format:
    {"available": {"2026-W24": 1000}, "tasks": [{"week": "...", "repo": "...",
     "kind": "bug_fix", "status": "merged", "credits": 80, ...}, ...]}
"""
from __future__ import annotations

import json
import sys

from .model import Task
from .report import render
from .sample_data import sample_dataset


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return [Task(**t) for t in data.get("tasks", [])], data.get("available", {})


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    tasks, available = load_json(argv[0]) if argv else sample_dataset()
    print(render(tasks, available))


if __name__ == "__main__":
    main()
