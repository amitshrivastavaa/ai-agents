"""_showcase — the build pipeline for the labs showcase site ("the lab terminal").

NOT a runnable lab. This package discovers every lab with a ``demo.py``,
captures its output, and generates a static, terminal-aesthetic site. The
leading underscore marks it as infrastructure so lab/demo discovery skips it.

    python -m labs._showcase.build --out site/
"""
from __future__ import annotations

