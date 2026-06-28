"""The orchestration layer — how Maxout puts your quota to work.

`SimulatedRunner` feeds the demo offline. `ClaudeCodeRunner` is the real thing:
it drives `claude -p` headless over a repo's backlog. It's runnable on a machine
where Claude Code Max is authenticated; `dry_run=True` (default) just records the
backlog as 'open' Tasks without calling claude or touching git, so it's safe to
run anywhere (and is what the analytics demo uses).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import Protocol

from .model import Task
from .sample_data import sample_dataset
from .scanner import BacklogItem


class TaskRunner(Protocol):
    def run_week(self, week, repos, credit_budget): ...


class SimulatedRunner:
    """Returns the deterministic sample so the report runs offline, no API."""

    def run_week(self, week=None, repos=None, credit_budget=1000.0):
        tasks, _ = sample_dataset()
        return [t for t in tasks if week is None or t.week == week]


class ClaudeCodeRunner:
    """Drive `claude -p` headless over a repo backlog, stopping at a credit budget."""

    def __init__(self, repo, week, claude_bin="claude"):
        self.repo = repo
        self.week = week
        self.claude_bin = claude_bin

    def _instruction(self, item: BacklogItem) -> str:
        how = {
            "tests": "Write a focused unittest for this module, then run it and make it pass.",
            "docs": "Add concise docstrings to the module and its public functions/classes.",
            "todo": "Resolve this TODO/FIXME properly and remove the marker.",
            "bug": "Replace the bare except with a specific exception and handle it.",
            "refactor": "Split this oversized module into smaller cohesive modules; keep tests green.",
        }.get(item.kind, "Improve this file.")
        return (f"In {item.path} (around line {item.line}): {how} "
                f"Keep the change minimal and run the repo's tests before finishing.")

    def run_item(self, item: BacklogItem, dry_run=True) -> Task:
        repo_name = os.path.basename(os.path.abspath(self.repo))
        if dry_run or shutil.which(self.claude_bin) is None:
            return Task(week=self.week, repo=repo_name, kind=item.kind,
                        status="open", credits=float(item.est_credits))

        # Real execution (runs on a machine with your authenticated Claude Code Max).
        branch = f"maxout/{item.kind}-{os.path.splitext(os.path.basename(item.path))[0]}"
        subprocess.run(["git", "-C", self.repo, "switch", "-c", branch], check=False)
        proc = subprocess.run(
            [self.claude_bin, "-p", self._instruction(item), "--permission-mode", "acceptEdits"],
            cwd=self.repo, capture_output=True, text=True, timeout=900)
        # The branch is left for you to review + open a PR; status is 'open' until merged.
        return Task(week=self.week, repo=repo_name, kind=item.kind,
                    status="open" if proc.returncode == 0 else "failed",
                    credits=float(item.est_credits))

    def run_backlog(self, items, dry_run=True, budget_credits=1000) -> list:
        tasks, spent = [], 0
        for item in items:
            if spent + item.est_credits > budget_credits:
                break          # stop at the weekly quota — "finish it every week"
            tasks.append(self.run_item(item, dry_run=dry_run))
            spent += item.est_credits
        return tasks
