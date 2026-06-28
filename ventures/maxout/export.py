"""Export computed analytics to ui/data.json so the static dashboard can read it.

    python -m ventures.maxout.export            # from the built-in sample
    python -m ventures.maxout.export runs.json  # from your own logged runs
"""
from __future__ import annotations

import json
import os
import sys

from .analytics import (agent_performance, by_kind, per_repo, trend,
                        utilization, value_summary, weeks)
from .model import KIND_LABELS, Task
from .sample_data import sample_dataset


def build_data(tasks, available) -> dict:
    by_week = {}
    for w in weeks(tasks):
        by_week[w] = {
            "utilization": utilization(tasks, available, w),
            "value": value_summary(tasks, w),
            "byKind": by_kind(tasks, w),
        }
    return {
        "weeks": weeks(tasks),
        "available": available,
        "byWeek": by_week,
        "agentPerformance": agent_performance(tasks),
        "perRepo": per_repo(tasks),
        "trend": trend(tasks, available),
        "kindLabels": KIND_LABELS,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        with open(argv[0], encoding="utf-8") as fh:
            raw = json.load(fh)
        tasks = [Task(**t) for t in raw.get("tasks", [])]
        available = raw.get("available", {})
    else:
        tasks, available = sample_dataset()

    data = build_data(tasks, available)
    out = os.path.join(os.path.dirname(__file__), "ui", "data.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print(f"wrote {out}  ({len(data['weeks'])} weeks, "
          f"{sum(len(w['byKind']) for w in data['byWeek'].values())} kind-rows)")


if __name__ == "__main__":
    main()
