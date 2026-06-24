"""CLI for the constitutional self-refine loop.

    python -m labs.constitutional.cli refine "This is STUPID and just useless!!!"
    python -m labs.constitutional.cli refine "Email me at a@b.com" --constitution safety
    python -m labs.constitutional.cli refine "Hey guys" --json
    python -m labs.constitutional.cli principles
"""
from __future__ import annotations

import argparse
import json
import sys

from .constitution import PRESETS, get_constitution
from .refine import refine


def _cmd_refine(args) -> int:
    text = " ".join(args.text)
    transcript = refine(text, args.constitution, max_rounds=args.max_rounds)
    if args.json:
        print(json.dumps(transcript.to_dict(), indent=2))
    else:
        print(transcript.markdown())
    return 0


def _cmd_principles(args) -> int:
    print("Constitutions:\n")
    for name, rules in PRESETS.items():
        print(f"  {name}:")
        for p in rules:
            print(f"    [sev {p.severity}] {p.id:<12} {p.description}")
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="constitutional",
        description="Critique and revise text against a constitution until it's clean.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("refine", help="refine a piece of text")
    p.add_argument("text", nargs="+")
    p.add_argument("--constitution", default="professional",
                   help=f"one of: {', '.join(PRESETS)}")
    p.add_argument("--max-rounds", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_refine)

    sub.add_parser("principles", help="list constitutions and their principles").set_defaults(
        func=_cmd_principles)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
