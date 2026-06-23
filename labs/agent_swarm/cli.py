"""Command-line entry point for the agent_swarm deliberation engine.

    python -m labs.agent_swarm.cli --panel trading "Go long NVDA into earnings?"
    python -m labs.agent_swarm.cli --list
    python -m labs.agent_swarm.cli --panel vc --json "Lead the seed in an AI devtools startup?"

Runs fully offline by default; set ANTHROPIC_API_KEY (and `pip install
anthropic`) to route the personas through a real model instead.
"""
from __future__ import annotations

import argparse
import json
import sys

from .._kernel import get_brain, mode
from .engine import deliberate
from .personas import PANELS, get_panel


def _list_panels() -> str:
    rows = ["Available panels:\n"]
    for p in PANELS.values():
        rows.append(f"  {p.id:<13} {p.title:<26} — {p.question_hint}")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent_swarm",
        description="A panel of specialist agents debates your question and votes.",
    )
    parser.add_argument("question", nargs="*", help="the question to deliberate")
    parser.add_argument("--panel", default="trading",
                        help=f"which panel (default: trading). One of: {', '.join(PANELS)}")
    parser.add_argument("--list", action="store_true", help="list available panels and exit")
    parser.add_argument("--json", action="store_true",
                        help="emit the decision record as JSON instead of a transcript")
    parser.add_argument("--out", metavar="FILE", help="write the markdown transcript to FILE")
    parser.add_argument("--online", action="store_true",
                        help="force the real-model path (requires ANTHROPIC_API_KEY)")
    args = parser.parse_args(argv)

    if args.list:
        print(_list_panels())
        return 0

    question = " ".join(args.question).strip()
    if not question:
        parser.error("provide a question, e.g. \"Go long NVDA into earnings?\" (or use --list)")

    try:
        panel = get_panel(args.panel)
    except KeyError as e:
        parser.error(str(e))

    brain = get_brain() if args.online else (get_brain() if mode() == "online" else None)
    result = deliberate(panel, question, brain=brain)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(result.transcript_md())
        print(f"wrote transcript to {args.out}  (verdict: {result.decision.verdict})")

    if args.json:
        print(json.dumps(result.record(), indent=2))
    elif not args.out:
        print(result.transcript_md())
    return 0


if __name__ == "__main__":
    sys.exit(main())
