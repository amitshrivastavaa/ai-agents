"""Core data model: a Task is one unit of work the autopilot attempted."""
from __future__ import annotations

from dataclasses import dataclass

# A "credit" is an abstract unit of weekly Claude Code Max quota (roughly
# proportional to tokens / session time). CREDIT_USD is an illustrative API-rate
# value used only to frame ROI ("you put ~$X of capacity to work").
CREDIT_USD = 0.018

KINDS = ("bug_fix", "tests", "deps", "cve", "docs", "refactor", "todo", "perf")
KIND_LABELS = {
    "bug_fix": "Bug fixes",
    "tests": "Test coverage",
    "deps": "Dependency updates",
    "cve": "Security patches",
    "docs": "Documentation",
    "refactor": "Refactors",
    "todo": "TODO cleanup",
    "perf": "Performance",
}

# PR lifecycle. 'failed' = the agent couldn't finish (burns credits, no PR).
STATUSES = ("merged", "open", "changes_requested", "rejected", "failed")


@dataclass(frozen=True)
class Task:
    week: str          # ISO-ish week label, e.g. "2026-W24"
    repo: str
    kind: str          # one of KINDS
    status: str        # one of STATUSES
    credits: float     # quota consumed (spent whether or not it shipped)
    minutes_saved: float = 0.0
    coverage_delta: float = 0.0   # percentage points (tests)
    bugs_fixed: int = 0
    deps_updated: int = 0
    cves_patched: int = 0
    docs_pages: int = 0
    todos_closed: int = 0
    lines_changed: int = 0
    files_changed: int = 0
    risk: str = "low"  # low|med|high

    @property
    def created_pr(self) -> bool:
        return self.status != "failed"

    @property
    def shipped(self) -> bool:
        return self.status == "merged"
