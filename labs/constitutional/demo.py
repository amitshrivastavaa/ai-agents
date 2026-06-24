"""Demo: refine a few messy messages and watch violations fall to zero.

    python -m labs.constitutional.demo
"""
from __future__ import annotations

from .refine import refine

SAMPLES = [
    ("professional",
     "Hey guys, this REALLY stupid plan is GUARANTEED to always work, obviously!!!"),
    ("safety",
     "Sure, reach me at jane.doe@example.com or 555-867-5309; my SSN is 123-45-6789."),
    ("all",
     "Honestly this idea is just basically useless and the author is an idiot."),
]


def main() -> int:
    for constitution, text in SAMPLES:
        t = refine(text, constitution)
        print("=" * 74)
        print(f"[{constitution}]")
        print(f"  before: {t.original}")
        print(f"  after : {t.final}")
        path = " → ".join(str(len(r.violations)) for r in t.rounds) + " → 0"
        print(f"  violations per round: {path}   "
              f"({'converged' if t.converged else 'NOT converged'} in {t.num_rounds})")
    print("=" * 74)
    print("Draft → critique → revise → re-critique, until the constitution is satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
