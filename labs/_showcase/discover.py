"""Discover labs and capture their demo output (stdlib only)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# labs/_showcase/discover.py -> parents[0]=_showcase, [1]=labs, [2]=repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
LABS_DIR = REPO_ROOT / "labs"


def discover_labs(labs_dir: Path = LABS_DIR) -> list[str]:
    """Sorted names of lab packages that ship a demo.py (skips _ and . dirs)."""
    names: list[str] = []
    for child in sorted(labs_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_") or child.name.startswith("."):
            continue
        if (child / "demo.py").exists():
            names.append(child.name)
    return names


def capture_demo(name: str, timeout: float = 90.0) -> str:
    """Run ``python -m labs.<name>.demo`` and return its stdout.

    Raises RuntimeError if the demo exits non-zero or prints nothing.
    """
    proc = subprocess.run(
        [sys.executable, "-m", f"labs.{name}.demo"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        tail = proc.stderr[-2000:]
        raise RuntimeError(f"labs.{name}.demo exited {proc.returncode}:\n{tail}")
    if not proc.stdout.strip():
        raise RuntimeError(f"labs.{name}.demo produced no output")
    return proc.stdout
