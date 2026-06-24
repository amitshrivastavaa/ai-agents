"""CLI for the guardrail-evaluation harness.

    python -m labs.jailbreak_gauntlet.cli run                 # full report card
    python -m labs.jailbreak_gauntlet.cli run --json          # machine-readable
    python -m labs.jailbreak_gauntlet.cli run --lenient       # score-threshold guard
    python -m labs.jailbreak_gauntlet.cli probe "Ignore all previous instructions"
"""
from __future__ import annotations

import argparse
import json
import sys

from .guard import Guard
from .harness import run_gauntlet


def _cmd_run(args) -> int:
    guard = Guard(strict=not args.lenient, threshold=args.threshold)
    report = run_gauntlet(guard)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.markdown())
    return 0


def _cmd_probe(args) -> int:
    guard = Guard(strict=not args.lenient, threshold=args.threshold)
    text = " ".join(args.text)
    v = guard.inspect(text)
    print(f"input: {text!r}")
    print(f"  → {'🛑 BLOCKED' if v.blocked else '✅ allowed'}"
          f"  (category: {v.category}, severity score: {v.score})")
    for reason in v.reasons:
        print(f"    - {reason}")
    return 0 if not v.blocked else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jailbreak_gauntlet",
        description="Score a guardrail policy against a battery of injection probes.",
    )
    parser.add_argument("--lenient", action="store_true",
                        help="block on summed severity threshold instead of any-hit")
    parser.add_argument("--threshold", type=int, default=4,
                        help="severity threshold for --lenient (default 4)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="run the full gauntlet and print a report card")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_run)

    p = sub.add_parser("probe", help="test a single input against the guard")
    p.add_argument("text", nargs="+")
    p.set_defaults(func=_cmd_probe)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
