"""Git repository helpers."""
from __future__ import annotations

import subprocess
from pathlib import Path


def repo_root() -> Path:
    """Return the top-level directory of the current git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())
