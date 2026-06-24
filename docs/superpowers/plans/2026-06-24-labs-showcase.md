# labs Showcase ("the lab terminal") Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deployable, terminal-aesthetic static site that showcases every `labs/` MVP by rendering its pre-captured demo output.

**Architecture:** A stdlib-only Python generator (`labs/_showcase/`) auto-discovers every lab with a `demo.py`, runs it in a subprocess to capture stdout, joins that with README taglines and a theme map, and writes a `data.json` plus a copied vanilla static frontend into an output dir. The frontend is a single page (no framework, no Node) that renders a boot-menu launcher and per-lab session views from `data.json`. A GitHub Actions workflow builds and deploys to GitHub Pages.

**Tech Stack:** Python 3.11+ standard library only (generator + tests via `unittest`); vanilla HTML/CSS/JS (frontend); GitHub Actions + Pages (deploy).

## Global Constraints

- **Stdlib only.** The generator and its tests import nothing outside the Python standard library. No third-party deps.
- **Python floor:** `from __future__ import annotations` at the top of every module; `3.11` is the CI interpreter (`3.12` local). PEP 604 (`X | None`) type hints are fine.
- **Determinism:** demos are seeded and reproducible; capture stdout verbatim, assert non-empty + exit 0, never assert exact demo text in tests.
- **No live execution in the frontend.** Outputs are captured at build time. The `replay` feature only re-reveals already-captured text.
- **Naming:** package is `labs/_showcase/`. The leading underscore means it is NOT a runnable lab — it must be excluded from lab/demo discovery everywhere.
- **Test layout:** tests live in `labs/_showcase/tests/test_*.py` and are picked up by the existing `python -m unittest discover -s labs -t . -p 'test_*.py'`.
- **Repo URL for source links:** `https://github.com/amitshrivastavaa/ai-agents/tree/main/labs`.

---

### Task 1: Package scaffold, theme map, and CI smoke-test fix

Creates the `labs/_showcase` package, the theme assignment data, and — critically — fixes `labs-ci.yml` so the new underscore package is excluded from the demo smoke-test. After this task, `_showcase` exists and CI stays green.

**Files:**
- Create: `labs/_showcase/__init__.py`
- Create: `labs/_showcase/themes.py`
- Create: `labs/_showcase/tests/__init__.py`
- Create: `labs/_showcase/tests/test_themes.py`
- Modify: `.github/workflows/labs-ci.yml` (demo smoke-test filter)

**Interfaces:**
- Produces: `THEMES: dict[str, dict[str, str]]` (theme id → `{"label", "accent"}`); `THEME_MAP: dict[str, str]` (lab name → theme id); `theme_for(name: str) -> str` (returns mapped theme id, defaulting to `"classical"`).

- [ ] **Step 1: Create the package `__init__.py`**

Create `labs/_showcase/__init__.py`:

```python
"""_showcase — the build pipeline for the labs showcase site ("the lab terminal").

NOT a runnable lab. This package discovers every lab with a ``demo.py``,
captures its output, and generates a static, terminal-aesthetic site. The
leading underscore marks it as infrastructure so lab/demo discovery skips it.

    python -m labs._showcase.build --out site/
"""
```

- [ ] **Step 2: Create the tests package marker**

Create `labs/_showcase/tests/__init__.py`:

```python
"""Tests for the labs showcase build pipeline (offline, stdlib only)."""
```

- [ ] **Step 3: Write the failing test for the theme data**

Create `labs/_showcase/tests/test_themes.py`:

```python
"""Tests for the showcase theme map — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_themes -v
"""
from __future__ import annotations

import unittest

from labs._showcase.themes import THEME_MAP, THEMES, theme_for


class ThemeTests(unittest.TestCase):
    def test_every_mapped_theme_is_defined(self):
        for name, theme in THEME_MAP.items():
            self.assertIn(theme, THEMES, f"{name} -> unknown theme {theme!r}")

    def test_themes_have_label_and_accent(self):
        for tid, meta in THEMES.items():
            self.assertIn("label", meta)
            self.assertIn("accent", meta)
            self.assertTrue(meta["accent"].startswith("#"), tid)

    def test_theme_for_defaults_to_classical(self):
        self.assertEqual(theme_for("totally_new_lab"), "classical")
        self.assertEqual(theme_for("hopfield"), "classical")
        self.assertEqual(theme_for("agent_swarm"), "agents")
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `python -m unittest labs._showcase.tests.test_themes -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'labs._showcase.themes'`

- [ ] **Step 5: Create `themes.py`**

Create `labs/_showcase/themes.py`:

```python
"""Theme assignment for the labs showcase.

Each lab gets one *primary* theme (editorial — easily tweaked). ``THEMES`` holds
the display label and a subtle accent tint layered over the phosphor-green base.
"""
from __future__ import annotations

# theme id -> display label + accent colour (hex), layered over phosphor green.
THEMES: dict[str, dict[str, str]] = {
    "agents":       {"label": "Agents",                       "accent": "#3ad6ff"},
    "rl":           {"label": "Reinforcement Learning",       "accent": "#ffb454"},
    "evolution":    {"label": "Evolution & Swarms",           "accent": "#a6ff5f"},
    "generative":   {"label": "Generative Models",            "accent": "#ff6fd0"},
    "transformers": {"label": "Transformers & LLM internals", "accent": "#b39dff"},
    "classical":    {"label": "Classical AI & Math",          "accent": "#5fffd0"},
}

# lab directory name -> theme id. Keep in sync with the labs that ship a demo.py;
# test_build.py::test_theme_map_matches_discovered_labs guards both directions.
THEME_MAP: dict[str, str] = {
    "agent_memory": "agents",
    "agent_os": "agents",
    "agent_swarm": "agents",
    "constitutional": "agents",
    "jailbreak_gauntlet": "agents",
    "tiny_town": "agents",
    "tree_of_thoughts": "agents",
    "bandits": "rl",
    "grpo": "rl",
    "qlearning": "rl",
    "world_model": "rl",
    "evo_arena": "evolution",
    "neuroevolution": "evolution",
    "prompt_evolver": "evolution",
    "swarm": "evolution",
    "symbolic_regression": "evolution",
    "diffusion": "generative",
    "flow": "generative",
    "morphogenesis": "generative",
    "attention": "transformers",
    "bpe": "transformers",
    "moe": "transformers",
    "rag": "transformers",
    "speculative": "transformers",
    "ssm": "transformers",
    "transformer": "transformers",
    "gp": "classical",
    "hmm": "classical",
    "hopfield": "classical",
    "kalman": "classical",
    "lsh": "classical",
    "micrograd": "classical",
    "pagerank": "classical",
    "planner": "classical",
    "repo_cartographer": "classical",
}


def theme_for(name: str) -> str:
    """Theme id for a lab; unmapped labs fall back to 'classical' so the build
    never crashes (a CI test nudges you to assign new labs explicitly)."""
    return THEME_MAP.get(name, "classical")
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `python -m unittest labs._showcase.tests.test_themes -v`
Expected: PASS (3 tests)

- [ ] **Step 7: Fix the demo smoke-test filter in `labs-ci.yml`**

In `.github/workflows/labs-ci.yml`, the inline Python that lists demos skips only `_kernel`. Change it to skip every underscore-prefixed package so `_showcase` (and any future infra package) is excluded.

Replace:

```python
for m in pkgutil.iter_modules(labs.__path__):
    if m.ispkg and m.name != "_kernel":
        print(f"labs.{m.name}.demo")
```

with:

```python
for m in pkgutil.iter_modules(labs.__path__):
    if m.ispkg and not m.name.startswith("_"):
        print(f"labs.{m.name}.demo")
```

- [ ] **Step 8: Verify the smoke-test filter no longer lists `_showcase`**

Run:
```bash
python - <<'PY'
import pkgutil, labs
demos = [m.name for m in pkgutil.iter_modules(labs.__path__)
         if m.ispkg and not m.name.startswith("_")]
assert "_showcase" not in demos and "_kernel" not in demos, demos
assert "hopfield" in demos, demos
print("ok:", len(demos), "demos")
PY
```
Expected: `ok: <N> demos` (no assertion error)

- [ ] **Step 9: Commit**

```bash
git add labs/_showcase/__init__.py labs/_showcase/themes.py \
        labs/_showcase/tests/__init__.py labs/_showcase/tests/test_themes.py \
        .github/workflows/labs-ci.yml
git commit -m "labs/_showcase: scaffold package + theme map; exclude _ pkgs from demo smoke-test"
```

---

### Task 2: README table parser

Parses the `labs/README.md` MVP table into per-lab `{tagline, inspired_by}` so the showcase reuses existing copy instead of duplicating it.

**Files:**
- Create: `labs/_showcase/readme.py`
- Create: `labs/_showcase/tests/test_readme.py`

**Interfaces:**
- Produces: `parse_readme(text: str) -> dict[str, dict[str, str]]` mapping lab name → `{"tagline": str, "inspired_by": str}`.

- [ ] **Step 1: Write the failing test**

Create `labs/_showcase/tests/test_readme.py`:

```python
"""Tests for the README MVP-table parser — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_readme -v
"""
from __future__ import annotations

import unittest

from labs._showcase.readme import parse_readme

SAMPLE = """\
# labs

| MVP | What it is | Inspired by |
| --- | --- | --- |
| [`agent_swarm`](agent_swarm/) | A panel of agents debates and votes. | the viral *TradingAgents* firm |
| [`hopfield`](hopfield/) | Associative memory from corrupted cues. | Hopfield networks (Nobel 2024) |

_(more landing through the night)_
"""


class ParseReadmeTests(unittest.TestCase):
    def test_extracts_each_lab(self):
        out = parse_readme(SAMPLE)
        self.assertEqual(set(out), {"agent_swarm", "hopfield"})

    def test_tagline_and_inspired_by(self):
        out = parse_readme(SAMPLE)
        self.assertEqual(out["hopfield"]["tagline"],
                         "Associative memory from corrupted cues.")
        self.assertEqual(out["hopfield"]["inspired_by"],
                         "Hopfield networks (Nobel 2024)")

    def test_ignores_header_separator_and_prose(self):
        out = parse_readme(SAMPLE)
        self.assertNotIn("MVP", out)
        self.assertNotIn("---", out)
        self.assertEqual(len(out), 2)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest labs._showcase.tests.test_readme -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'labs._showcase.readme'`

- [ ] **Step 3: Implement `readme.py`**

Create `labs/_showcase/readme.py`:

```python
"""Parse the labs/README.md MVP table into per-lab metadata.

Table rows look like:

    | [`agent_swarm`](agent_swarm/) | A panel of agents ... | the viral *Trading* ... |

We pull the lab name (the link target), the "What it is" column (tagline), and
the "Inspired by" column. Header, separator, and prose lines are ignored.
"""
from __future__ import annotations

import re

# | [`name`](name/) | tagline | inspired_by |
_ROW = re.compile(r"^\|\s*\[`?([a-z0-9_]+)`?\]\([a-z0-9_]+/\)\s*\|(.*)\|(.*)\|\s*$")


def parse_readme(text: str) -> dict[str, dict[str, str]]:
    """Map lab name -> {'tagline', 'inspired_by'} from the README MVP table."""
    out: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        m = _ROW.match(line.strip())
        if not m:
            continue
        name, tagline, inspired = m.group(1), m.group(2), m.group(3)
        out[name] = {
            "tagline": tagline.strip(),
            "inspired_by": inspired.strip(),
        }
    return out
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest labs._showcase.tests.test_readme -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Sanity-check against the real README**

Run:
```bash
python - <<'PY'
from pathlib import Path
from labs._showcase.readme import parse_readme
data = parse_readme(Path("labs/README.md").read_text())
assert "hopfield" in data and data["hopfield"]["tagline"], data.get("hopfield")
print("parsed", len(data), "labs; hopfield ->", data["hopfield"]["tagline"][:50])
PY
```
Expected: `parsed <N> labs; hopfield -> ...` with N ≥ 30.

- [ ] **Step 6: Commit**

```bash
git add labs/_showcase/readme.py labs/_showcase/tests/test_readme.py
git commit -m "labs/_showcase: parse README MVP table into per-lab metadata"
```

---

### Task 3: Lab discovery and demo capture

Finds labs that ship a `demo.py` and captures each demo's stdout via subprocess.

**Files:**
- Create: `labs/_showcase/discover.py`
- Create: `labs/_showcase/tests/test_discover.py`

**Interfaces:**
- Produces: `REPO_ROOT: Path`; `LABS_DIR: Path`; `discover_labs(labs_dir: Path = LABS_DIR) -> list[str]` (sorted lab names with a `demo.py`, skipping `_`/`.` dirs); `capture_demo(name: str, timeout: float = 90.0) -> str` (stdout; raises `RuntimeError` on non-zero exit or empty output).

- [ ] **Step 1: Write the failing test**

Create `labs/_showcase/tests/test_discover.py`:

```python
"""Tests for lab discovery + demo capture — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_discover -v
"""
from __future__ import annotations

import unittest

from labs._showcase.discover import capture_demo, discover_labs


class DiscoverTests(unittest.TestCase):
    def test_finds_known_labs(self):
        names = discover_labs()
        self.assertIn("hopfield", names)
        self.assertIn("agent_swarm", names)

    def test_skips_private_packages(self):
        names = discover_labs()
        self.assertNotIn("_kernel", names)
        self.assertNotIn("_showcase", names)

    def test_sorted(self):
        names = discover_labs()
        self.assertEqual(names, sorted(names))


class CaptureTests(unittest.TestCase):
    def test_capture_returns_nonempty_output(self):
        out = capture_demo("hopfield")
        self.assertTrue(out.strip())
        self.assertIn("recalled", out)

    def test_capture_raises_on_unknown_lab(self):
        with self.assertRaises(RuntimeError):
            capture_demo("does_not_exist_xyz")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest labs._showcase.tests.test_discover -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'labs._showcase.discover'`

- [ ] **Step 3: Implement `discover.py`**

Create `labs/_showcase/discover.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest labs._showcase.tests.test_discover -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add labs/_showcase/discover.py labs/_showcase/tests/test_discover.py
git commit -m "labs/_showcase: discover labs with a demo.py and capture their output"
```

---

### Task 4: Static frontend (launcher + session view)

The vanilla single-page frontend: phosphor terminal theme, boot-menu launcher, per-lab session view with replay. No framework, no build step.

**Files:**
- Create: `labs/_showcase/static/index.html`
- Create: `labs/_showcase/static/style.css`
- Create: `labs/_showcase/static/app.js`
- Create: `labs/_showcase/tests/test_static.py`

**Interfaces:**
- Produces: a static bundle copied verbatim by the build (Task 5). `app.js` fetches `data.json` (shape from Task 5: `{"themes": {...}, "labs": [{name, theme, tagline, inspired_by, demo, source_url}]}`).

- [ ] **Step 1: Write the failing test (content anchors)**

Create `labs/_showcase/tests/test_static.py`:

```python
"""Tests that the static frontend ships the expected hooks — stdlib only.

    python -m unittest labs._showcase.tests.test_static -v
"""
from __future__ import annotations

import unittest
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "static"


class StaticAssetTests(unittest.TestCase):
    def test_files_exist(self):
        for f in ("index.html", "style.css", "app.js"):
            self.assertTrue((STATIC / f).is_file(), f)

    def test_index_wires_assets(self):
        html = (STATIC / "index.html").read_text()
        self.assertIn("style.css", html)
        self.assertIn("app.js", html)
        self.assertIn('id="app"', html)

    def test_app_js_loads_data_and_has_views(self):
        js = (STATIC / "app.js").read_text()
        self.assertIn("data.json", js)
        self.assertIn("renderLauncher", js)
        self.assertIn("renderSession", js)

    def test_style_uses_accent_variable(self):
        css = (STATIC / "style.css").read_text()
        self.assertIn("--accent", css)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest labs._showcase.tests.test_static -v`
Expected: FAIL (files do not exist yet)

- [ ] **Step 3: Create `index.html`**

Create `labs/_showcase/static/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>labs · the lab terminal</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="app"><pre class="boot">booting…</pre></div>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 4: Create `style.css`**

Create `labs/_showcase/static/style.css`:

```css
:root {
  --bg: #060a06;
  --fg: #33ff66;
  --dim: #1f8a3b;
  --accent: #33ff66;
  --panel: #0a0e0a;
  --line: #14301c;
  font-size: 15px;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  line-height: 1.45;
}
a { color: inherit; text-decoration: none; }
.boot { padding: 40px; color: var(--dim); }

/* masthead */
.masthead { padding: 34px 24px 10px; border-bottom: 1px solid var(--line); }
.banner { margin: 0; color: var(--accent); text-shadow: 0 0 10px rgba(51,255,102,.4);
  font-size: 13px; white-space: pre; overflow-x: auto; }
.sub { color: var(--dim); margin: 8px 0 0; font-size: 13px; }

/* toolbar */
.toolbar { padding: 16px 24px; position: sticky; top: 0; background: var(--bg);
  border-bottom: 1px solid var(--line); z-index: 5; }
.search { width: 100%; max-width: 420px; background: var(--panel); color: var(--fg);
  border: 1px solid var(--dim); border-radius: 6px; padding: 8px 12px;
  font: inherit; outline: none; }
.search:focus { box-shadow: 0 0 0 2px rgba(51,255,102,.25); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.chip { background: transparent; color: var(--dim); border: 1px solid var(--line);
  border-radius: 999px; padding: 4px 12px; font: inherit; font-size: 12px; cursor: pointer; }
.chip.on { color: var(--accent); border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent) inset; }

/* launcher grid */
.grid { display: grid; gap: 14px; padding: 22px 24px;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.card { display: block; background: var(--panel); border: 1px solid var(--line);
  border-left: 3px solid var(--accent); border-radius: 8px; padding: 14px 16px;
  transition: transform .1s, box-shadow .1s; }
.card:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(0,0,0,.4); }
.card-id { color: var(--accent); font-size: 12px; }
.card-name { color: var(--fg); font-size: 17px; margin: 2px 0 6px; }
.card-tag { color: var(--dim); font-size: 12.5px; }
.empty { padding: 40px 24px; color: var(--dim); }

/* session view */
.session { max-width: 920px; margin: 0 auto; padding: 24px; }
.winbar { display: flex; align-items: center; gap: 12px; background: var(--panel);
  border: 1px solid var(--line); border-bottom: none; border-radius: 8px 8px 0 0;
  padding: 8px 12px; }
.dots i { width: 11px; height: 11px; border-radius: 50%; display: inline-block; margin-right: 5px; }
.dots i:nth-child(1){ background:#ff5f56 } .dots i:nth-child(2){ background:#ffbd2e }
.dots i:nth-child(3){ background:#27c93f }
.winbar .title { color: var(--dim); }
.winbar .back { margin-left: auto; color: var(--accent); }
.meta { display: flex; gap: 10px; align-items: center; background: var(--panel);
  border-left: 1px solid var(--line); border-right: 1px solid var(--line); padding: 10px 14px; }
.badge { color: var(--accent); border: 1px solid var(--accent); border-radius: 999px;
  font-size: 11px; padding: 2px 9px; }
.meta .tag { color: var(--dim); font-size: 13px; }
.term { background: #040604; border: 1px solid var(--line); padding: 14px 16px; }
.cmd { color: var(--accent); margin-bottom: 8px; }
.out { margin: 0; color: var(--fg); white-space: pre; overflow-x: auto;
  font-size: 12.5px; line-height: 1.3; text-shadow: 0 0 6px rgba(51,255,102,.25); }
.cap { background: var(--panel); border: 1px solid var(--line); border-top: none;
  color: var(--dim); font-size: 12px; padding: 10px 14px; font-style: italic; }
.sessnav { display: flex; gap: 16px; align-items: center; margin-top: 16px;
  flex-wrap: wrap; color: var(--dim); }
.sessnav a, .sessnav button { color: var(--accent); background: transparent;
  border: 1px solid var(--line); border-radius: 6px; padding: 6px 12px;
  font: inherit; font-size: 13px; cursor: pointer; }
.err { color: #ff6b6b; padding: 24px; }
```

- [ ] **Step 5: Create `app.js`**

Create `labs/_showcase/static/app.js`:

```javascript
"use strict";

let DATA = null;
let activeTheme = "all";
let query = "";
let typer = null;

const app = document.getElementById("app");

fetch("data.json")
  .then((r) => r.json())
  .then((d) => { DATA = d; route(); })
  .catch((e) => { app.innerHTML = `<pre class="err">failed to load data.json: ${e}</pre>`; });

window.addEventListener("hashchange", route);

function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function route() {
  if (!DATA) return;
  const name = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  const lab = DATA.labs.find((l) => l.name === name);
  if (lab) renderSession(lab); else renderLauncher();
}

function renderLauncher() {
  const themes = DATA.themes;
  const q = query.toLowerCase();
  const labs = DATA.labs.filter((l) => {
    const okTheme = activeTheme === "all" || l.theme === activeTheme;
    const okQ = !q || l.name.includes(q) || l.tagline.toLowerCase().includes(q);
    return okTheme && okQ;
  });

  const chips = [`<button class="chip${activeTheme === "all" ? " on" : ""}" data-t="all">all</button>`]
    .concat(Object.entries(themes).map(([id, t]) =>
      `<button class="chip${activeTheme === id ? " on" : ""}" data-t="${id}" style="--accent:${t.accent}">${esc(t.label)}</button>`))
    .join("");

  const cards = labs.map((l, i) => {
    const t = themes[l.theme] || { accent: "#33ff66" };
    const n = String(i + 1).padStart(2, "0");
    return `<a class="card" href="#/${encodeURIComponent(l.name)}" style="--accent:${t.accent}">
        <div class="card-id">[${n}]</div>
        <div class="card-name">${esc(l.name)}</div>
        <div class="card-tag">${esc(l.tagline)}</div>
      </a>`;
  }).join("");

  app.innerHTML = `
    <header class="masthead">
      <pre class="banner">//// the lab terminal ////</pre>
      <p class="sub">${DATA.labs.length} working AI-agent MVPs · offline · stdlib-only · from scratch</p>
    </header>
    <div class="toolbar">
      <input id="search" class="search" placeholder="/ search labs…" value="${esc(query)}">
      <div class="chips">${chips}</div>
    </div>
    <div class="grid">${cards || '<p class="empty">no labs match.</p>'}</div>`;

  const search = document.getElementById("search");
  search.addEventListener("input", (e) => {
    query = e.target.value;
    const pos = e.target.selectionStart;
    renderLauncher();
    const s = document.getElementById("search");
    s.focus();
    s.setSelectionRange(pos, pos);
  });
  app.querySelectorAll(".chip").forEach((c) =>
    c.addEventListener("click", () => { activeTheme = c.dataset.t; renderLauncher(); }));
}

function renderSession(lab) {
  const t = DATA.themes[lab.theme] || { accent: "#33ff66", label: lab.theme };
  const idx = DATA.labs.indexOf(lab);
  const prev = DATA.labs[(idx - 1 + DATA.labs.length) % DATA.labs.length];
  const next = DATA.labs[(idx + 1) % DATA.labs.length];

  app.innerHTML = `
    <div class="session" style="--accent:${t.accent}">
      <div class="winbar">
        <span class="dots"><i></i><i></i><i></i></span>
        <span class="title">${esc(lab.name)} — demo</span>
        <a class="back" href="#/">← menu</a>
      </div>
      <div class="meta">
        <span class="badge">${esc(t.label)}</span>
        <span class="tag">${esc(lab.tagline)}</span>
      </div>
      <div class="term">
        <div class="cmd">$ python -m labs.${esc(lab.name)}.demo</div>
        <pre class="out" id="out"></pre>
      </div>
      <div class="cap">inspired by ${esc(lab.inspired_by) || "—"}</div>
      <nav class="sessnav">
        <a href="#/${encodeURIComponent(prev.name)}">‹ ${esc(prev.name)}</a>
        <button id="replay">▶ replay</button>
        <a href="${esc(lab.source_url)}" target="_blank" rel="noopener">view source ↗</a>
        <a href="#/${encodeURIComponent(next.name)}">${esc(next.name)} ›</a>
      </nav>
    </div>`;

  const out = document.getElementById("out");
  out.textContent = lab.demo;
  document.getElementById("replay").addEventListener("click", () => typeOut(out, lab.demo));
  window.scrollTo(0, 0);
}

function typeOut(el, text) {
  if (typer) clearInterval(typer);
  el.textContent = "";
  let i = 0;
  const step = Math.max(1, Math.floor(text.length / 600));
  typer = setInterval(() => {
    i += step;
    el.textContent = text.slice(0, i);
    if (i >= text.length) { clearInterval(typer); typer = null; }
  }, 16);
}
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `python -m unittest labs._showcase.tests.test_static -v`
Expected: PASS (4 tests)

- [ ] **Step 7: Commit**

```bash
git add labs/_showcase/static/ labs/_showcase/tests/test_static.py
git commit -m "labs/_showcase: vanilla phosphor-terminal frontend (launcher + session view)"
```

---

### Task 5: Build orchestrator

Ties it together: `collect()` assembles the data structure; `build()` writes `data.json` and copies the static bundle; `main()` is the `--out` CLI. Includes the two-directional theme/lab coverage cross-check.

**Files:**
- Create: `labs/_showcase/build.py`
- Create: `labs/_showcase/tests/test_build.py`

**Interfaces:**
- Consumes: `discover_labs`, `capture_demo`, `LABS_DIR` (Task 3); `parse_readme` (Task 2); `THEMES`, `theme_for`, `THEME_MAP` (Task 1); the static bundle (Task 4).
- Produces: `collect(names: list[str] | None = None) -> dict`; `build(out_dir: Path, names: list[str] | None = None) -> dict`; `main(argv: list[str] | None = None) -> int`. Data shape: `{"themes": THEMES, "labs": [{"name","theme","tagline","inspired_by","demo","source_url"}]}`.

- [ ] **Step 1: Write the failing test**

Create `labs/_showcase/tests/test_build.py`:

```python
"""Tests for the showcase build orchestrator — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_build -v
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from labs._showcase.build import build, collect, main
from labs._showcase.discover import discover_labs
from labs._showcase.themes import THEME_MAP

REQUIRED_KEYS = {"name", "theme", "tagline", "inspired_by", "demo", "source_url"}


class CollectTests(unittest.TestCase):
    def test_collect_one_lab_has_required_keys(self):
        data = collect(names=["hopfield"])
        self.assertIn("themes", data)
        self.assertEqual(len(data["labs"]), 1)
        entry = data["labs"][0]
        self.assertEqual(REQUIRED_KEYS, set(entry))
        self.assertEqual(entry["name"], "hopfield")
        self.assertEqual(entry["theme"], "classical")
        self.assertTrue(entry["demo"].strip())
        self.assertTrue(entry["tagline"])
        self.assertTrue(entry["source_url"].endswith("/hopfield"))


class BuildTests(unittest.TestCase):
    def test_build_writes_site(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "site"
            build(out, names=["hopfield"])
            data = json.loads((out / "data.json").read_text())
            self.assertEqual(len(data["labs"]), 1)
            for f in ("index.html", "style.css", "app.js"):
                self.assertTrue((out / f).is_file(), f)

    def test_main_returns_zero(self):
        with tempfile.TemporaryDirectory() as d:
            rc = main(["--out", str(Path(d) / "site")])
            self.assertEqual(rc, 0)


class CoverageTests(unittest.TestCase):
    def test_theme_map_matches_discovered_labs(self):
        discovered = set(discover_labs())
        mapped = set(THEME_MAP)
        self.assertEqual(
            discovered, mapped,
            f"unmapped labs: {discovered - mapped}; stale map entries: {mapped - discovered}",
        )
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest labs._showcase.tests.test_build -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'labs._showcase.build'`

- [ ] **Step 3: Implement `build.py`**

Create `labs/_showcase/build.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest labs._showcase.tests.test_build -v`
Expected: PASS (4 tests). The `test_theme_map_matches_discovered_labs` test confirms every discovered lab is themed and the map has no stale entries.

- [ ] **Step 5: Run the full build end-to-end and open it**

Run:
```bash
python -m labs._showcase.build --out site
python -c "import pathlib,json; d=json.loads(pathlib.Path('site/data.json').read_text()); print('built', len(d['labs']), 'labs')"
open site/index.html   # macOS; or: python -m http.server -d site 8000
```
Expected: `built <N> labs` (N ≥ 30) and the launcher renders in the browser; clicking a card shows its captured demo output; `▶ replay` re-types it; theme chips and `/` search filter the grid.

- [ ] **Step 6: Commit**

```bash
git add labs/_showcase/build.py labs/_showcase/tests/test_build.py
git commit -m "labs/_showcase: build orchestrator (collect + data.json + static copy + CLI)"
```

---

### Task 6: Deploy workflow, gitignore, and README pointer

Wires CI/CD: a GitHub Pages deploy workflow, ignores the build output, and points the README at the showcase.

**Files:**
- Create: `.github/workflows/showcase.yml`
- Modify: `.gitignore`
- Modify: `labs/README.md` (the "Run everything" section)

**Interfaces:**
- Consumes: `python -m labs._showcase.build --out site` (Task 5).

- [ ] **Step 1: Ignore the build output**

Add to `.gitignore` (under the existing build-artifact entries):

```gitignore
# Generated showcase site (regenerable build output).
site/
```

- [ ] **Step 2: Create the deploy workflow**

Create `.github/workflows/showcase.yml`:

```yaml
name: showcase

# Build the stdlib-only labs showcase and publish it to GitHub Pages.
# One-time setup: repo Settings → Pages → Source = "GitHub Actions".

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Build the showcase (stdlib only, no deps)
        run: python -m labs._showcase.build --out site
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - id: deploy
        uses: actions/deploy-pages@v4
```

- [ ] **Step 3: Point the README at the showcase**

In `labs/README.md`, find the "## Run everything" section and add a showcase subsection immediately after its code block:

```markdown
## The showcase site ("the lab terminal")

Build a deployable, terminal-aesthetic static site that renders every lab's
demo output — a boot-menu launcher plus a per-lab session view:

```sh
python -m labs._showcase.build --out site
python -m http.server -d site 8000   # then open http://localhost:8000
```

It auto-discovers every lab with a `demo.py`, so the site grows as new MVPs
land. On every push to `main`, `.github/workflows/showcase.yml` builds and
deploys it to GitHub Pages.
```

- [ ] **Step 4: Verify the build still runs clean from scratch**

Run:
```bash
rm -rf site && python -m labs._showcase.build --out site && test -f site/index.html && echo "build ok"
```
Expected: `built <N> labs -> site/` then `build ok`.

- [ ] **Step 5: Run the whole lab test suite (regression gate)**

Run: `python -m unittest discover -s labs -t . -p 'test_*.py'`
Expected: OK — all lab tests pass, including the five new `labs/_showcase/tests/` modules.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/showcase.yml .gitignore labs/README.md
git commit -m "labs/_showcase: GitHub Pages deploy workflow + README pointer"
```

- [ ] **Step 7: One-time manual step (not code)**

In the GitHub repo: **Settings → Pages → Source → "GitHub Actions"**. Then push to `main` (or run the `showcase` workflow via *Actions → Run workflow*) and confirm the deployment URL renders.

---

## Self-Review

**Spec coverage:**
- Terminal/phosphor visual + caption borrow → Task 4 (`style.css`, `.cap` line in `app.js`). ✓
- Boot-menu launcher + session view → Task 4 (`renderLauncher`, `renderSession`). ✓
- Per-theme accent tints → Task 1 (`THEMES.accent`) + Task 4 (`--accent`). ✓
- Generator: discover, capture, parse README, theme map, emit data.json + copy static → Tasks 1–5. ✓
- Vanilla frontend, no Node → Task 4. ✓
- GitHub Actions → Pages deploy; `site/` gitignored → Task 6. ✓
- Auto-discovery / grows as labs land → Task 3 `discover_labs` + Task 5 default. ✓
- `demo.py`-only capture (v1) → Task 5 `capture_demo`. ✓
- Tests: discovery finds all labs, README parser, captures exit 0 & non-empty, data.json schema, one entry per lab, theme/lab coverage both directions → Tasks 1–5 test files. ✓
- Build fails loudly on demo error → Task 3 `capture_demo` raises. ✓
- `_showcase` excluded from demo smoke-test → Task 1 Step 7. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code. ✓

**Type consistency:** `discover_labs`, `capture_demo`, `parse_readme`, `theme_for`, `THEMES`, `THEME_MAP`, `collect`, `build`, `main` are used with identical signatures across tasks. `data.json` keys (`themes`, `labs`, `name`, `theme`, `tagline`, `inspired_by`, `demo`, `source_url`) match between Task 5 (producer), Task 5 tests (`REQUIRED_KEYS`), and Task 4 (`app.js` consumer). ✓

**Risks carried from spec:** long outputs scroll in `.out` (acceptable v1); per-demo `timeout=90s` guards CI runtime; README parser degrades to blank tagline (`meta.get(..., "")`) rather than crashing on a malformed row. ✓
