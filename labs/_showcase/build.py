"""Build the labs showcase — a static, terminal-aesthetic site.

    python -m labs._showcase.build --out site/

stdlib only. Discovers every lab with a demo.py, captures its output, joins it
with the README taglines and theme map, writes data.json, and copies the static
frontend into the output dir.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .discover import LABS_DIR, capture_demo, discover_labs
from .readme import parse_readme
from .themes import THEMES, theme_for

STATIC_DIR = Path(__file__).resolve().parent / "static"
REPO_URL = "https://github.com/amitshrivastavaa/ai-agents/tree/main/labs"


def collect(names: list[str] | None = None) -> dict:
    """Assemble the showcase data structure (themes + per-lab entries)."""
    if names is None:
        names = discover_labs()
    readme = parse_readme((LABS_DIR / "README.md").read_text(encoding="utf-8"))
    labs = []
    for name in names:
        meta = readme.get(name, {})
        labs.append({
            "name": name,
            "theme": theme_for(name),
            "tagline": meta.get("tagline", ""),
            "inspired_by": meta.get("inspired_by", ""),
            "demo": capture_demo(name),
            "source_url": f"{REPO_URL}/{name}",
        })
    return {"themes": THEMES, "labs": labs}


def build(out_dir: Path, names: list[str] | None = None) -> dict:
    """Generate the full static site into out_dir; returns the data structure."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = collect(names)
    for item in STATIC_DIR.iterdir():
        if item.is_file():
            shutil.copy2(item, out_dir / item.name)
    (out_dir / "data.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="labs._showcase.build",
        description="Build the static labs showcase site.")
    parser.add_argument("--out", default="site",
                        help="output directory (default: site)")
    args = parser.parse_args(argv)
    data = build(Path(args.out))
    print(f"built {len(data['labs'])} labs -> {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
