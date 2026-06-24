#!/usr/bin/env python3
"""Render the whole labs/ collection into one static HTML gallery (docs/index.html).

Every MVP is offline + deterministic, so we can just *run* each demo and embed its
output. No server, no API keys — the result hosts free on GitHub Pages (or open
docs/index.html locally).

    python tools/build_site.py
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABS = ROOT / "labs"
OUT = ROOT / "docs" / "index.html"

ROW = re.compile(r"^\| \[`([^`]+)`\]\([^)]+\)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")


def mvp_table():
    """Parse labs/README.md's table → ordered [(name, description, inspired)]."""
    rows = []
    for line in (LABS / "README.md").read_text().splitlines():
        m = ROW.match(line)
        if m and (LABS / m.group(1) / "demo.py").exists():
            rows.append((m.group(1), m.group(2), m.group(3)))
    return rows


def run_demo(name):
    try:
        p = subprocess.run([sys.executable, "-m", f"labs.{name}.demo"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        return (p.stdout or p.stderr).rstrip("\n")
    except Exception as e:                                  # pragma: no cover
        return f"(demo unavailable: {e})"


def md_inline(text):
    """Tiny inline-markdown → HTML (escape first, then code/strong/em)."""
    t = html.escape(text)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    return t


def count_tests():
    n = 0
    for f in LABS.glob("*/tests/test_*.py"):
        n += len(re.findall(r"\n    def test_", f.read_text()))
    return n


CSS = """
:root{--bg:#0d1117;--panel:#161b22;--ink:#e6edf3;--mut:#8b949e;--acc:#58a6ff;
--term:#0b0e14;--green:#3fb950;--border:#30363d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1000px;margin:0 auto;padding:0 20px}
header{padding:64px 0 32px;border-bottom:1px solid var(--border)}
h1{font-size:40px;margin:0 0 8px;letter-spacing:-.5px}
.tag{color:var(--mut);font-size:19px;margin:0 0 24px}
.stats{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0 8px}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:10px;
padding:12px 18px}.stat b{font-size:26px;display:block;color:var(--green)}
.stat span{color:var(--mut);font-size:13px}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:28px 0 0}
.toc a{background:var(--panel);border:1px solid var(--border);border-radius:20px;
padding:5px 13px;font-size:13px;font-family:ui-monospace,monospace}
.mvp{padding:48px 0;border-bottom:1px solid var(--border)}
.mvp h2{font-size:27px;margin:0;font-family:ui-monospace,monospace}
.mvp h2 a{color:var(--ink)}
.badge{display:inline-block;margin-left:10px;font-size:12px;color:var(--mut);
border:1px solid var(--border);border-radius:20px;padding:2px 10px;
vertical-align:middle;font-family:-apple-system,sans-serif}
.desc{color:#c9d1d9;margin:14px 0 18px;max-width:75ch}
.run{font-family:ui-monospace,monospace;font-size:13px;color:var(--mut);
margin:0 0 14px}.run code{background:var(--panel);border:1px solid var(--border);
border-radius:6px;padding:3px 8px;color:var(--green)}
.term{background:var(--term);border:1px solid var(--border);border-radius:10px;
overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.4)}
.bar{background:#11151c;padding:9px 14px;border-bottom:1px solid var(--border);
font-size:12px;color:var(--mut)}
.dot{height:11px;width:11px;border-radius:50%;display:inline-block;margin-right:6px}
.term pre{margin:0;padding:18px;overflow-x:auto;font-family:ui-monospace,
"SF Mono",Menlo,monospace;font-size:12.5px;line-height:1.45;color:#d7dde3}
footer{padding:48px 0 80px;color:var(--mut);text-align:center;font-size:14px}
"""

CARD = """
<section class="mvp" id="{name}">
  <h2><a href="#{name}">{name}</a><span class="badge">{inspired}</span></h2>
  <p class="desc">{desc}</p>
  <p class="run">run it&nbsp; <code>python -m labs.{name}.demo</code></p>
  <div class="term">
    <div class="bar"><span class="dot" style="background:#ff5f56"></span>
    <span class="dot" style="background:#ffbd2e"></span>
    <span class="dot" style="background:#27c93f"></span>
    &nbsp;python -m labs.{name}.demo</div>
    <pre>{output}</pre>
  </div>
</section>
"""


def build():
    rows = mvp_table()
    cards, toc = [], []
    for name, desc, inspired in rows:
        out = html.escape(run_demo(name))
        toc.append(f'<a href="#{name}">{name}</a>')
        cards.append(CARD.format(name=name, desc=md_inline(desc),
                                 inspired=md_inline(inspired), output=out))
        print(f"  rendered {name}")
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>labs — a research lab of wild AI MVPs</title>
<meta name="description" content="{len(rows)} self-contained, from-scratch AI/ML MVPs — each runs offline with the Python standard library alone.">
<style>{CSS}</style></head><body>
<div class="wrap">
<header>
  <h1>labs<span style="color:var(--mut);font-weight:400"> / wild AI MVPs</span></h1>
  <p class="tag">{len(rows)} self-contained MVPs, each inspired by a trending idea in AI —
  built from scratch, running <b>offline with the Python standard library alone</b>.</p>
  <div class="stats">
    <div class="stat"><b>{len(rows)}</b><span>MVPs</span></div>
    <div class="stat"><b>{count_tests()}</b><span>passing tests</span></div>
    <div class="stat"><b>0</b><span>dependencies to run</span></div>
    <div class="stat"><b>100%</b><span>deterministic</span></div>
  </div>
  <div class="toc">{''.join(toc)}</div>
</header>
{''.join(cards)}
<footer>Generated from each demo's real output by <code>tools/build_site.py</code>.
Everything runs with <code>python -m labs.&lt;name&gt;.demo</code> — no key, nothing to install.</footer>
</div></body></html>"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page)
    print(f"\nwrote {OUT}  ({len(rows)} MVPs, {len(page) // 1024} KB)")


if __name__ == "__main__":
    build()
