"""Maxout — make sure your Claude Code Max quota turns into shipped work every week.

A backlog-finder + task-runner that points idle Claude Code Max capacity at your
own repos (bugs, tests, deps, CVEs, docs, TODOs), opens PRs you review, logs each
run, and reports the analytics: how much of your quota you actually used, what it
shipped, and how reliable the autopilot was.
"""
from .model import Task
from .analytics import utilization, value_summary, agent_performance
from .report import render

__all__ = ["Task", "utilization", "value_summary", "agent_performance", "render"]
