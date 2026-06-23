"""Demo: run all three workloads and show the scheduler at work.

    python -m labs.agent_os.demo
"""
from __future__ import annotations

from .cli import _print_report, run_workload


def main() -> int:
    for name in ("report", "ci", "ci_broken"):
        kernel, report = run_workload(name, seed="demo")
        print("=" * 74)
        _print_report(name, kernel, report, show_trace=(name == "ci"))
        print()
    print("=" * 74)
    print("Note how 'report' fans out 4 research tasks across steps (parallel workers),")
    print("'ci' retries the flaky test, and 'ci_broken' cancels everything downstream")
    print("of the failed build — all from the same scheduler.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
