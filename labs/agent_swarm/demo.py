"""Scripted demo: run a few canned questions across panels, offline.

    python -m labs.agent_swarm.demo
"""
from __future__ import annotations

from .engine import deliberate
from .personas import get_panel

SCENARIOS = [
    ("trading", "Go long NVDA into earnings after a record-demand quarter?"),
    ("trading", "Short the overvalued meme stock into its crowded, frothy rally?"),
    ("hiring", "Hire the senior backend candidate who aced system design but rambled in the values round?"),
    ("architecture", "Adopt event sourcing for the orders service to future-proof the platform?"),
    ("vc", "Lead the seed round in a pre-revenue AI devtools startup with a strong founder?"),
]


def main() -> int:
    for panel_id, question in SCENARIOS:
        panel = get_panel(panel_id)
        result = deliberate(panel, question)
        d = result.decision
        print("=" * 78)
        print(f"[{panel.title}] {question}")
        print(f"  → VERDICT: {d.verdict}   (score {d.score:+.2f}, "
              f"confidence {d.confidence:.0%}, consensus {d.consensus:.0%})")
        print(f"    {d.rationale}")
        if d.tensions:
            print(f"    dissent: {d.tensions[0]}")
    print("=" * 78)
    print("Run a single one in full:  python -m labs.agent_swarm.cli --panel trading "
          "\"<your question>\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
