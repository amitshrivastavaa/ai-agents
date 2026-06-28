"""Render the weekly Maxout report — the thing you read Monday morning."""
from __future__ import annotations

from .analytics import (agent_performance, by_kind, latest_week, per_repo,
                        streak, trend, utilization, value_summary)
from .model import KIND_LABELS
from .sample_data import sample_dataset

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values):
    if not values:
        return ""
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1
    return "".join(_SPARK[int((v - lo) / rng * (len(_SPARK) - 1))] for v in values)


def _bar(frac, width=18):
    n = int(round(frac * width))
    return "#" * n + "." * (width - n)


def render(tasks, available, week=None) -> str:
    week = week or latest_week(tasks)
    u = utilization(tasks, available, week)
    v = value_summary(tasks, week)
    tr = trend(tasks, available)

    out = []
    out.append("MAXOUT · weekly Claude Code Max report".center(64))
    out.append("=" * 64)
    out.append(f"  Week {week}")
    out.append("")
    out.append(f"  QUOTA USED:  {u['pct'] * 100:.0f}%   "
               f"({u['used']:.0f}/{u['available']:.0f} credits · "
               f"{u['idle']:.0f} left on the table)")
    out.append(f"     ~${u['usd_equiv']:.0f} of capacity put to work · "
               f"{streak(tasks, available)}-week streak ≥80% · "
               f"{u['wasted_credits']:.0f}cr on PRs that didn't land")
    out.append("")
    out.append(f"  SHIPPED:  {v['prs_merged']} of {v['prs_opened']} PRs merged "
               f"({v['acceptance_rate'] * 100:.0f}% accepted) · ~{v['hours_saved']:.0f}h saved")
    out.append(f"     {v['bugs_fixed']} bugs · +{v['tests_coverage_delta']:.1f}pt coverage · "
               f"{v['deps_updated']} deps · {v['cves_patched']} CVEs · "
               f"{v['docs_pages']} docs · {v['todos_closed']} TODOs")
    out.append("")
    out.append("  Where the capacity went")
    bk = by_kind(tasks, week)
    maxc = max((d["credits"] for d in bk.values()), default=1)
    for k, d in sorted(bk.items(), key=lambda kv: -kv[1]["credits"]):
        out.append(f"    {KIND_LABELS[k]:<18} {_bar(d['credits'] / maxc)} "
                   f"{d['credits']:>5.0f}cr  {d['merged']}/{d['attempted']} merged")
    out.append("")
    out.append("  Momentum")
    out.append(f"    Utilization   {_spark([t['pct'] for t in tr])}   "
               f"{tr[0]['pct'] * 100:.0f}% → {tr[-1]['pct'] * 100:.0f}%")
    out.append(f"    Hours saved   {_spark([t['hours_saved'] for t in tr])}   "
               f"{sum(t['hours_saved'] for t in tr):.0f}h over {len(tr)} weeks")
    out.append("")
    out.append("  Autopilot reliability (acceptance by task type)")
    for k, d in sorted(agent_performance(tasks).items(),
                       key=lambda kv: -kv[1]["acceptance_rate"]):
        out.append(f"    {KIND_LABELS[k]:<18} {d['acceptance_rate'] * 100:>3.0f}% accepted · "
                   f"{d['roi_min_per_credit']:.1f} min saved/credit")
    out.append("")
    out.append("  By repo")
    for r, d in per_repo(tasks).items():
        out.append(f"    {r:<8} {d['merged']:>2} merged · {d['credits']:>5.0f}cr · "
                   f"+{d['coverage_delta']:.1f}pt · {d['hours_saved']:.0f}h")
    return "\n".join(out)


def main():
    tasks, available = sample_dataset()
    print(render(tasks, available))


if __name__ == "__main__":
    main()
