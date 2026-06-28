"""A deterministic six-week run log that tells the real story: you start out
under-using your Max (~48%), then the autopilot ramps you to ~96% — with a mix
of merged / open / rejected / failed outcomes so the analytics are honest.
"""
from __future__ import annotations

from .model import KINDS, Task

REPOS = ("api", "web", "infra")
AVAIL = 1000.0
TARGETS = (0.48, 0.61, 0.72, 0.83, 0.91, 0.96)


def _value(kind, status, j) -> dict:
    v = dict(minutes_saved=0.0, coverage_delta=0.0, bugs_fixed=0, deps_updated=0,
             cves_patched=0, docs_pages=0, todos_closed=0, lines_changed=0,
             files_changed=0)
    if status != "merged":          # only merged work realizes value
        return v
    if kind == "bug_fix":
        v.update(bugs_fixed=1, minutes_saved=45 + 5 * (j % 4), lines_changed=30 + 10 * (j % 5), files_changed=1 + j % 3)
    elif kind == "tests":
        v.update(coverage_delta=round(0.6 + 0.3 * (j % 4), 2), minutes_saved=25 + 5 * (j % 3), lines_changed=60 + 15 * (j % 4), files_changed=1 + j % 2)
    elif kind == "deps":
        v.update(deps_updated=1 + j % 4, minutes_saved=12 + 3 * (j % 3), lines_changed=8 + 2 * (j % 3), files_changed=1)
    elif kind == "cve":
        v.update(cves_patched=1, minutes_saved=40 + 10 * (j % 3), lines_changed=12 + 4 * (j % 3), files_changed=1 + j % 2)
    elif kind == "docs":
        v.update(docs_pages=1 + j % 3, minutes_saved=18 + 4 * (j % 3), lines_changed=40 + 10 * (j % 4), files_changed=1 + j % 2)
    elif kind == "refactor":
        v.update(minutes_saved=50 + 8 * (j % 4), lines_changed=120 + 25 * (j % 5), files_changed=2 + j % 4)
    elif kind == "todo":
        v.update(todos_closed=1, minutes_saved=20 + 5 * (j % 3), lines_changed=20 + 8 * (j % 3), files_changed=1 + j % 2)
    elif kind == "perf":
        v.update(minutes_saved=35 + 7 * (j % 3), lines_changed=25 + 9 * (j % 4), files_changed=1 + j % 2)
    return v


def _risk(kind):
    if kind in ("refactor", "perf"):
        return "high"
    if kind in ("cve", "bug_fix"):
        return "med"
    return "low"


def sample_dataset():
    available = {}
    tasks = []
    for i, target in enumerate(TARGETS):
        wk = f"2026-W{20 + i:02d}"
        available[wk] = AVAIL
        n = 6 + i                          # 6..11 tasks/week
        per = round(target * AVAIL / n, 1)  # so the week's credits ~= target * quota
        for j in range(n):
            kind = KINDS[(i * 3 + j) % len(KINDS)]
            repo = REPOS[(i + j) % len(REPOS)]
            r = (i * 7 + j * 3) % 10
            status = ("merged" if r < 6 else "open" if r < 7 else
                      "changes_requested" if r < 8 else "rejected" if r < 9 else "failed")
            tasks.append(Task(week=wk, repo=repo, kind=kind, status=status,
                              credits=per, risk=_risk(kind), **_value(kind, status, j)))
    return tasks, available
