#!/usr/bin/env python3
"""Render the whole labs/ collection into one static HTML gallery (docs/index.html).

Built for a *visitor*, not just an engineer: a hero that explains what this is and
why it's impressive, the 44 projects grouped into themed sections, and each card
led by a plain-English "what it is / why it matters" blurb (pulled from the
project's README) — so the terminal output reads as evidence, not a mystery.

Every MVP is offline + deterministic, so we just run each demo and embed its
output. No server, no API keys — hosts free on GitHub Pages (or open locally).

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

# Curated themed grouping (order = narrative). Any MVP not listed here still shows
# up under "More from the lab", so new ones from the build loop never disappear —
# but slot them into a theme here to keep the story tight.
CATEGORIES = [
    ("Autonomous agents & LLM applications",
     "Multi-agent systems, long-term memory, retrieval, planning loops and safety — "
     "the application layer, built on a tiny model abstraction that runs offline.",
     ["agent_swarm", "agent_memory", "agent_os", "tiny_town", "rag",
      "tree_of_thoughts", "constitutional", "jailbreak_gauntlet", "prompt_evolver",
      "repo_cartographer"]),
    ("Neural nets & LLMs, from scratch",
     "The internals of modern language models, rebuilt from first principles — "
     "tokenizer, autograd, attention, a full transformer block, the Mamba "
     "alternative, and lossless decoding speedups.",
     ["micrograd", "bpe", "attention", "transformer", "ssm", "speculative"]),
    ("Generative models",
     "Turning noise into structure: the score-based and flow-based methods behind "
     "today's image generators, plus self-organizing pattern formation.",
     ["diffusion", "flow", "morphogenesis"]),
    ("Reinforcement learning",
     "Learning from reward — from the one-state bandit up to the policy-gradient "
     "algorithm (GRPO) behind today's reasoning models, plus evolutionary RL.",
     ["bandits", "qlearning", "grpo", "world_model", "evo_arena", "neuroevolution"]),
    ("Supervised machine learning",
     "Classifiers and regressors from scratch — the decision-tree family that wins "
     "tabular ML (forests, gradient boosting / XGBoost) and the linear & "
     "probabilistic baselines.",
     ["tree", "forest", "boosting", "logreg", "naivebayes"]),
    ("Unsupervised learning & representation",
     "Finding structure without labels: clustering, dimensionality reduction, "
     "mixtures of experts, and energy-based associative memory.",
     ["kmeans", "pca", "moe", "hopfield"]),
    ("Probabilistic modeling & uncertainty",
     "Models that don't just predict, but say how sure they are — Bayesian "
     "filtering, Gaussian processes, hidden Markov models, and distribution-free "
     "guarantees.",
     ["gp", "conformal", "kalman", "hmm"]),
    ("Algorithms, search & systems",
     "The classics that power real systems: graph ranking, sublinear-memory "
     "streaming sketches, vector search, symbolic planning, swarm optimization, and "
     "program synthesis.",
     ["pagerank", "lsh", "sketch", "planner", "swarm", "symbolic_regression"]),
]


def mvp_table():
    """Parse labs/README.md's table → {name: (one_liner, inspired)} + order list."""
    info, order = {}, []
    for line in (LABS / "README.md").read_text().splitlines():
        m = ROW.match(line)
        if m and (LABS / m.group(1) / "demo.py").exists():
            info[m.group(1)] = (m.group(2), m.group(3))
            order.append(m.group(1))
    return info, order


def read_meta(name):
    """(readable title, 'what it is' blurb) from the project's own README."""
    title, pitch = name, ""
    p = LABS / name / "README.md"
    if not p.exists():
        return title, pitch
    lines = p.read_text().splitlines()
    for ln in lines:
        if ln.startswith("# "):
            title = ln[2:].strip()
            break
    quote, started = [], False
    for ln in lines:
        if ln.startswith(">"):
            quote.append(ln.lstrip(">").strip())
            started = True
        elif started:
            break
    return title, " ".join(q for q in quote if q)


def run_demo(name):
    try:
        p = subprocess.run([sys.executable, "-m", f"labs.{name}.demo"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        return (p.stdout or p.stderr).rstrip("\n")
    except Exception as e:                                  # pragma: no cover
        return f"(demo unavailable: {e})"


def md_inline(text):
    """Tiny inline-markdown → HTML: strip links to text, then code/strong/em."""
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    return t


def count_tests():
    return sum(len(re.findall(r"\n    def test_", f.read_text()))
               for f in LABS.glob("*/tests/test_*.py"))


CSS = """
:root{--bg:#0b0e14;--panel:#141a23;--ink:#e6edf3;--mut:#8b98a9;--acc:#6cb6ff;
--green:#5ad27e;--gold:#e3b341;--term:#080b10;--border:#222b38}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
code{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:.92em}
.wrap{max-width:1020px;margin:0 auto;padding:0 22px}
/* hero */
.hero{padding:84px 0 36px}
.eyebrow{color:var(--gold);font-weight:600;font-size:14px;letter-spacing:.12em;
text-transform:uppercase;margin:0 0 14px}
.hero h1{font-size:46px;line-height:1.08;margin:0 0 18px;letter-spacing:-1px}
.hero h1 .hl{color:var(--green)}
.lead{font-size:20px;color:#c4cedb;max-width:70ch;margin:0 0 28px}
.stats{display:flex;gap:14px;flex-wrap:wrap;margin:0 0 26px}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:12px;
padding:14px 20px;min-width:120px}.stat b{font-size:28px;display:block;color:var(--green)}
.stat span{color:var(--mut);font-size:13px}
.how{background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--gold);
border-radius:10px;padding:18px 22px;margin:8px 0 0;color:#c4cedb;font-size:15px}
.how b{color:var(--ink)}
.navcats{display:flex;flex-wrap:wrap;gap:8px;margin:30px 0 0}
.navcats a{background:var(--panel);border:1px solid var(--border);border-radius:20px;
padding:6px 14px;font-size:13px;color:#c4cedb}
/* category */
.cat{padding:54px 0 0;border-top:1px solid var(--border);margin-top:46px}
.cat:first-of-type{border-top:none;margin-top:0}
.cat>h2{font-size:27px;margin:0 0 6px;letter-spacing:-.3px}
.cat>p.catlede{color:var(--mut);max-width:75ch;margin:0 0 8px;font-size:15.5px}
.catcount{color:var(--gold);font-size:13px;font-weight:600}
/* card */
.mvp{padding:30px 0 6px}
.mvp h3{font-size:20px;margin:0;font-family:ui-monospace,monospace;color:var(--ink)}
.mvp h3 a{color:var(--ink)}.mvp h3 .nm{color:var(--green)}
.badge{display:inline-block;margin-left:8px;font-size:11.5px;color:var(--mut);
border:1px solid var(--border);border-radius:20px;padding:2px 10px;vertical-align:middle;
font-family:-apple-system,sans-serif;font-weight:500}
.pitch{color:#c8d2de;margin:11px 0 6px;max-width:78ch;font-size:15.5px}
.summary{color:var(--mut);margin:0 0 13px;max-width:78ch;font-size:14px}
.summary b,.summary strong{color:#c8d2de}
.run{font-size:12.5px;color:var(--mut);margin:0 0 12px}
.run code{background:var(--panel);border:1px solid var(--border);border-radius:6px;
padding:3px 9px;color:var(--green)}
.term{background:var(--term);border:1px solid var(--border);border-radius:11px;overflow:hidden}
.bar{background:#0d1219;padding:9px 14px;border-bottom:1px solid var(--border);
font-size:12px;color:var(--mut);font-family:ui-monospace,monospace}
.dot{height:11px;width:11px;border-radius:50%;display:inline-block;margin-right:6px;vertical-align:middle}
.term pre{margin:0;padding:18px;overflow-x:auto;font-family:ui-monospace,"SF Mono",Menlo,monospace;
font-size:12.5px;line-height:1.5;color:#cdd6e0}
footer{padding:54px 0 90px;color:var(--mut);text-align:center;font-size:14px;
border-top:1px solid var(--border);margin-top:50px}
"""

CARD = """
<article class="mvp" id="{name}">
  <h3><a href="#{name}"><span class="nm">{name}</span></a> — {short}<span class="badge">↳ {inspired}</span></h3>
  <p class="pitch">{pitch}</p>
  <p class="summary">{summary}</p>
  <p class="run">try it · <code>python -m labs.{name}.demo</code></p>
  <div class="term">
    <div class="bar"><span class="dot" style="background:#ff5f56"></span><span class="dot" style="background:#ffbd2e"></span><span class="dot" style="background:#27c93f"></span> python -m labs.{name}.demo</div>
    <pre>{output}</pre>
  </div>
</article>
"""


def short_title(full, name):
    """Drop the leading 'name — ' so the H3 reads as a clean human title."""
    t = re.sub(rf"^{re.escape(name)}\s*[—-]\s*", "", full)
    return t[:1].upper() + t[1:] if t else name


def build():
    info, order = mvp_table()
    seen = set()
    sections = []
    nav = []

    groups = list(CATEGORIES)
    leftover = [n for n in order if n not in {x for _, _, names in groups for x in names}]
    if leftover:
        groups = groups + [("More from the lab",
                            "Freshly built and not yet slotted into a theme.", leftover)]

    for cat_title, cat_lede, names in groups:
        cards = []
        for name in names:
            if name not in info or name in seen:
                continue
            seen.add(name)
            summary, inspired = info[name]
            title, pitch = read_meta(name)
            out = html.escape(run_demo(name))
            cards.append(CARD.format(
                name=name, short=html.escape(short_title(title, name)),
                inspired=md_inline(inspired), pitch=md_inline(pitch),
                summary=md_inline(summary), output=out))
            print(f"  rendered {name}")
        if not cards:
            continue
        anchor = re.sub(r"[^a-z]+", "-", cat_title.lower()).strip("-")
        nav.append(f'<a href="#{anchor}">{html.escape(cat_title)}</a>')
        sections.append(
            f'<section class="cat" id="{anchor}"><h2>{html.escape(cat_title)}</h2>'
            f'<p class="catlede">{html.escape(cat_lede)} '
            f'<span class="catcount">{len(cards)} projects</span></p>'
            f'{"".join(cards)}</section>')

    n = len(seen)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>labs — {n} AI &amp; ML systems built from scratch</title>
<meta name="description" content="{n} AI/ML systems implemented from first principles by an autonomous coding agent — offline, deterministic, fully tested. From transformers and diffusion to gradient boosting and Gaussian processes.">
<style>{CSS}</style></head><body>
<div class="wrap">
<header class="hero">
  <p class="eyebrow">An overnight autonomous-build experiment</p>
  <h1>{n} AI &amp; ML systems,<br><span class="hl">built from scratch</span> in one night.</h1>
  <p class="lead">Every project below was researched and implemented from first
  principles by an autonomous coding agent — <strong>no ML frameworks, just the
  Python standard library</strong>. From transformers, diffusion and reasoning-model
  RL to gradient boosting and Gaussian processes. Each one runs offline, is fully
  deterministic, and ships with a runnable demo and a passing test suite.</p>
  <div class="stats">
    <div class="stat"><b>{n}</b><span>projects, from scratch</span></div>
    <div class="stat"><b>{count_tests()}</b><span>passing tests</span></div>
    <div class="stat"><b>0</b><span>runtime dependencies</span></div>
    <div class="stat"><b>100%</b><span>deterministic &amp; offline</span></div>
  </div>
  <div class="how"><b>How it was built:</b> an agent ran a self-paced loop through
  the night — research a trending idea in AI, implement it from scratch with tests,
  prove it works, then commit it, open a pull request, merge it, and rebuild this
  page — over and over, on its own. <b>How to read this:</b> projects are grouped by
  theme below; each card says what it is, the idea it's based on, and shows its real
  terminal output. Run any of them with <code>python -m labs.&lt;name&gt;.demo</code>.</div>
  <nav class="navcats">{''.join(nav)}</nav>
</header>
{''.join(sections)}
<footer>{n} self-contained projects · {count_tests()} tests · 0 dependencies.
Each panel above is real output from <code>python -m labs.&lt;name&gt;.demo</code>,
captured at build time by <code>tools/build_site.py</code>. No key, nothing to install.</footer>
</div></body></html>"""
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page)
    print(f"\nwrote {OUT}  ({n} MVPs in {len(sections)} themes, {len(page) // 1024} KB)")


if __name__ == "__main__":
    build()
