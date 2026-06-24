"""`python -m labs` — a launcher to browse and run the MVP demos locally.

    python -m labs            # list every MVP
    python -m labs pca        # run one demo
    python -m labs --all      # run them all, top to bottom
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parent


def mvps():
    return sorted(p.parent.name for p in LABS.glob("*/demo.py"))


def main(argv):
    names = mvps()
    if argv and argv[0] in ("--all", "-a"):
        for n in names:
            print("\n" + "=" * 72 + f"\n  python -m labs.{n}.demo\n" + "=" * 72)
            subprocess.call([sys.executable, "-m", f"labs.{n}.demo"])
        return 0
    if argv and argv[0] in names:
        return subprocess.call([sys.executable, "-m", f"labs.{argv[0]}.demo"])
    if argv:
        print(f"unknown MVP {argv[0]!r}\n")

    print(f"labs — {len(names)} self-contained AI/ML MVPs (offline, deterministic)\n")
    for i, n in enumerate(names):
        end = "\n" if (i + 1) % 4 == 0 else ""
        print(f"  {n:<18}", end=end)
    if len(names) % 4:
        print()
    print("\n  python -m labs <name>    run one demo")
    print("  python -m labs --all     run every demo")
    print("  open docs/index.html     the full visual gallery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
