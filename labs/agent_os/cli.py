"""CLI for the agent_os micro-runtime.

    python -m labs.agent_os.cli list
    python -m labs.agent_os.cli run --workload report --goal "Will agents replace SaaS?"
    python -m labs.agent_os.cli run --workload ci --trace
    python -m labs.agent_os.cli run --workload ci_broken
"""
from __future__ import annotations

import argparse
import json
import sys

from .kernel import Kernel, RunReport
from .workloads import WORKLOADS, get_workload


def run_workload(name: str, *, goal: str | None = None, workers: int = 3,
                 seed: str = "os") -> tuple[Kernel, RunReport]:
    wl = get_workload(name, goal)
    kernel = Kernel(max_workers=workers, seed=seed)
    for kind, handler in wl.handlers.items():
        kernel.register(kind, handler)
    for task in wl.seeds:
        kernel.add(task)
    return kernel, kernel.run()


def _print_report(name: str, kernel: Kernel, report: RunReport, *, show_trace: bool) -> None:
    print(f"# agent_os · workload '{name}'  "
          f"(workers={kernel.max_workers})\n")

    print("Schedule (tasks dispatched per step — same step = ran concurrently):")
    for i, ids in enumerate(report.schedule, 1):
        marker = "  ║" if len(ids) > 1 else "  │"
        print(f"{marker} step {i:>2}: {', '.join(ids)}")
    print()

    print("Final task states:")
    for t in report.tasks.values():
        icon = {"done": "✓", "failed": "✗", "cancelled": "⊘",
                "pending": "…", "running": "▸"}.get(t.state.value, "?")
        attempts = f"  ({t.attempts}×)" if t.attempts > 1 else ""
        print(f"  {icon} {t.id:<14} {t.state.value}{attempts}")
    print()

    if show_trace:
        print("Trace:")
        for ev in report.trace:
            print(f"  s{ev.step:>2} {ev.task_id:<14} {ev.action:<7} {ev.detail}")
        print()

    bb = report.blackboard
    if "report" in bb:
        print("Blackboard → report artifact:\n")
        for line in bb["report"].splitlines():
            print(f"  | {line}")
        print()
    else:
        print("Blackboard:")
        for k in sorted(bb):
            print(f"  {k} = {bb[k]!r}")
        print()

    c = report.counts()
    verdict = "✅ succeeded" if report.succeeded else (
        "⏱ timed out" if report.timed_out else "⚠️ finished with failures/cancellations")
    print(f"{verdict} in {report.steps} steps — "
          f"{c['done']} done, {c['failed']} failed, {c['cancelled']} cancelled")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent_os",
        description="A micro OS: schedule a graph of agent tasks over a blackboard.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list workloads")
    p.set_defaults(cmd="list")

    p = sub.add_parser("run", help="run a workload")
    p.add_argument("--workload", default="report", help=f"one of: {', '.join(WORKLOADS)}")
    p.add_argument("--goal", default=None, help="goal text (report workload)")
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--seed", default="os")
    p.add_argument("--trace", action="store_true", help="print the full event trace")
    p.add_argument("--json", action="store_true")
    p.set_defaults(cmd="run")

    args = parser.parse_args(argv)

    if args.cmd == "list":
        print("Available workloads:\n")
        for name, builder in WORKLOADS.items():
            print(f"  {name:<10} {builder().description}")
        return 0

    try:
        kernel, report = run_workload(args.workload, goal=args.goal,
                                      workers=args.workers, seed=args.seed)
    except KeyError as e:
        parser.error(str(e))
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        _print_report(args.workload, kernel, report, show_trace=args.trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
