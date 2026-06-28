"""Analytics over a log of autopilot Tasks.

Five families of metric:
  * utilization  — how much of your weekly quota you actually used
  * value        — what shipped (PRs, bugs, coverage, deps, CVEs, hours saved)
  * by_kind      — where the capacity went this week
  * agent_perf   — how reliable the autopilot is, per task type
  * per_repo / trend / streak — distribution and momentum over time
"""
from __future__ import annotations

from .model import KINDS, CREDIT_USD


def weeks(tasks):
    return sorted({t.week for t in tasks})


def latest_week(tasks):
    ws = weeks(tasks)
    return ws[-1] if ws else None


def _wk(tasks, week):
    return [t for t in tasks if t.week == week]


def utilization(tasks, available, week) -> dict:
    ws = _wk(tasks, week)
    used = round(sum(t.credits for t in ws), 1)
    avail = available.get(week, 0.0)
    wasted = round(sum(t.credits for t in ws if not t.shipped), 1)
    return {
        "week": week,
        "used": used,
        "available": avail,
        "pct": round(used / avail, 4) if avail else 0.0,
        "idle": round(avail - used, 1),
        "usd_equiv": round(used * CREDIT_USD, 2),
        "wasted_credits": wasted,   # spent on PRs that didn't merge / failed runs
    }


def value_summary(tasks, week) -> dict:
    ws = _wk(tasks, week)
    created = [t for t in ws if t.created_pr]
    merged = [t for t in ws if t.shipped]
    opened = len(created)
    return {
        "prs_opened": opened,
        "prs_merged": len(merged),
        "prs_rejected": sum(1 for t in ws if t.status == "rejected"),
        "failed": sum(1 for t in ws if t.status == "failed"),
        "acceptance_rate": round(len(merged) / opened, 4) if opened else 0.0,
        "rework_rate": round(sum(1 for t in ws if t.status == "changes_requested") / opened, 4) if opened else 0.0,
        "bugs_fixed": sum(t.bugs_fixed for t in merged),
        "tests_coverage_delta": round(sum(t.coverage_delta for t in merged), 2),
        "deps_updated": sum(t.deps_updated for t in merged),
        "cves_patched": sum(t.cves_patched for t in merged),
        "docs_pages": sum(t.docs_pages for t in merged),
        "todos_closed": sum(t.todos_closed for t in merged),
        "lines_changed": sum(t.lines_changed for t in merged),
        "files_changed": sum(t.files_changed for t in merged),
        "hours_saved": round(sum(t.minutes_saved for t in merged) / 60.0, 1),
    }


def by_kind(tasks, week) -> dict:
    ws = _wk(tasks, week)
    out = {}
    for k in KINDS:
        ks = [t for t in ws if t.kind == k]
        if not ks:
            continue
        merged = [t for t in ks if t.shipped]
        out[k] = {
            "attempted": len(ks),
            "merged": len(merged),
            "credits": round(sum(t.credits for t in ks), 1),
            "hours_saved": round(sum(t.minutes_saved for t in merged) / 60.0, 1),
        }
    return out


def agent_performance(tasks) -> dict:
    """Reliability + ROI per task type across all weeks (drives prioritization)."""
    out = {}
    for k in KINDS:
        ks = [t for t in tasks if t.kind == k]
        if not ks:
            continue
        created = [t for t in ks if t.created_pr]
        merged = [t for t in ks if t.shipped]
        credits = sum(t.credits for t in ks)
        mins = sum(t.minutes_saved for t in merged)
        out[k] = {
            "attempted": len(ks),
            "acceptance_rate": round(len(merged) / len(created), 4) if created else 0.0,
            "avg_credits": round(credits / len(ks), 1),
            "roi_min_per_credit": round(mins / credits, 2) if credits else 0.0,
        }
    return out


def per_repo(tasks) -> dict:
    out = {}
    for r in sorted({t.repo for t in tasks}):
        rs = [t for t in tasks if t.repo == r]
        merged = [t for t in rs if t.shipped]
        out[r] = {
            "tasks": len(rs),
            "merged": len(merged),
            "credits": round(sum(t.credits for t in rs), 1),
            "coverage_delta": round(sum(t.coverage_delta for t in merged), 2),
            "bugs_fixed": sum(t.bugs_fixed for t in merged),
            "cves_patched": sum(t.cves_patched for t in merged),
            "hours_saved": round(sum(t.minutes_saved for t in merged) / 60.0, 1),
        }
    return out


def trend(tasks, available) -> list:
    out = []
    for w in weeks(tasks):
        u = utilization(tasks, available, w)
        v = value_summary(tasks, w)
        out.append({"week": w, "pct": u["pct"], "used": u["used"],
                    "merged": v["prs_merged"], "hours_saved": v["hours_saved"]})
    return out


def streak(tasks, available, target=0.8) -> int:
    """Consecutive most-recent weeks at/above the utilization target."""
    s = 0
    for w in reversed(weeks(tasks)):
        if utilization(tasks, available, w)["pct"] >= target:
            s += 1
        else:
            break
    return s
