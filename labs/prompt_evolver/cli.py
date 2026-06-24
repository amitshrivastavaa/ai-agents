"""CLI for the evolutionary prompt optimizer.

    python -m labs.prompt_evolver.cli list
    python -m labs.prompt_evolver.cli run --task sentiment
    python -m labs.prompt_evolver.cli run --task slugify --generations 30 --json
"""
from __future__ import annotations

import argparse
import json
import sys

from .._kernel import get_brain, mode
from .evolve import Result, evolve
from .tasks import TASKS, get_task

_SPARK = "▁▂▃▄▅▆▇█"


def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    return "".join(_SPARK[min(len(_SPARK) - 1, int((v - lo) / span * (len(_SPARK) - 1)))]
                    for v in values)


def _print_report(task, result: Result) -> None:
    best_curve = [b for b, _ in result.history]
    print(f"# Evolving a prompt for: {task.title}  (mode: {result.run_mode})")
    print(f"  population {result.population} · {result.generations} generations\n")
    print(f"  baseline prompt : {result.baseline_genome}")
    print(f"  baseline fitness: {result.baseline_fitness:.3f}")
    print(f"  evolved  prompt : {result.best_genome}")
    print(f"  evolved  fitness: {result.best_fitness:.3f}   "
          f"(+{result.improvement:.3f} improvement)")
    print(f"  best-per-gen     : {_sparkline(best_curve)}  "
          f"{best_curve[0]:.2f} → {best_curve[-1]:.2f}\n")
    print("  ── evolved prompt ──")
    for line in result.rendered_prompt.splitlines():
        print(f"  | {line}")


def _cmd_list(_args) -> int:
    print("Available tasks:\n")
    for t in TASKS.values():
        print(f"  {t.id:<10} {t.title}")
        print(f"             directives: {', '.join(t.directives)}")
    return 0


def _cmd_run(args) -> int:
    task = get_task(args.task)
    brain = get_brain() if mode() == "online" else None
    result = evolve(
        task,
        population=args.population,
        generations=args.generations,
        seed=args.seed,
        brain=brain,
    )
    if args.json:
        print(json.dumps({
            "task": result.task_id,
            "mode": result.run_mode,
            "baseline_genome": result.baseline_genome,
            "baseline_fitness": round(result.baseline_fitness, 4),
            "best_genome": result.best_genome,
            "best_fitness": round(result.best_fitness, 4),
            "improvement": round(result.improvement, 4),
            "history": [[round(b, 4), round(m, 4)] for b, m in result.history],
            "rendered_prompt": result.rendered_prompt,
        }, indent=2))
    else:
        _print_report(task, result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prompt_evolver",
        description="Evolve a prompt that maximizes accuracy on a labeled task.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list tasks").set_defaults(func=_cmd_list)

    p = sub.add_parser("run", help="evolve a prompt for a task")
    p.add_argument("--task", default="sentiment", help=f"one of: {', '.join(TASKS)}")
    p.add_argument("--generations", type=int, default=25)
    p.add_argument("--population", type=int, default=30)
    p.add_argument("--seed", default="evolve")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
