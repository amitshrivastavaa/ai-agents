"""Demo: evolve prompts for both tasks and show the before/after.

    python -m labs.prompt_evolver.demo
"""
from __future__ import annotations

from .cli import _print_report
from .evolve import evolve
from .tasks import TASKS


def main() -> int:
    for task in TASKS.values():
        result = evolve(task, seed="demo")
        print("=" * 78)
        _print_report(task, result)
        print()
    print("=" * 78)
    print("The optimizer discovered the helpful directives, dropped the harmful/no-op")
    print("ones, and (for slugify) found a working step ORDER — purely from accuracy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
