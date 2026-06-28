"""The orchestration contract — how Maxout actually puts your quota to work.

The analytics in this package are real and run offline on a Task log. This module
defines the interface that *produces* that log, plus a SimulatedRunner for the
demo. The real ClaudeCodeRunner would:

  1. scan a repo for work -> a prioritized backlog
        (failing tests, TODO/FIXME, outdated deps, open CVEs, low-coverage files,
         lint/type debt), ranked by the agent-performance ROI we already compute
  2. for each item, drive `claude -p` headless on a fresh git worktree to
     implement + run the tests, retrying within a per-task credit cap
  3. open a PR via the GitHub API and record a Task for the analytics
  4. stop when the weekly credit budget is hit — so you "finish it every week"

Keeping this as an interface (not a half-wired integration) is deliberate: the
value to demo today is the engine + analytics; the live wiring plugs in here.
"""
from __future__ import annotations

from typing import Protocol

from .sample_data import sample_dataset


class TaskRunner(Protocol):
    def run_week(self, week, repos, credit_budget): ...


class SimulatedRunner:
    """Returns the deterministic sample so the report runs offline, no API."""

    def run_week(self, week=None, repos=None, credit_budget=1000.0):
        tasks, _ = sample_dataset()
        return [t for t in tasks if week is None or t.week == week]
