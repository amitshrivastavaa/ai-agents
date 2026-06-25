# labs/ showcase — "the lab terminal" — design

**Date:** 2026-06-24
**Status:** Approved (design); pending implementation plan
**Topic:** A deployable, terminal-aesthetic static site that showcases every
`labs/` MVP by rendering its pre-captured demo output.

## Goal

Give the `labs/` collection a public face: a single static site, shareable as a
link and pleasant to browse, that presents each lab's working demo. It must
stay true to the repo's ethos — **offline, stdlib-only, deterministic, zero
runtime dependencies** — and grow automatically as new labs land.

Non-goal: live code execution. Outputs are captured at build time.

## User decisions (from brainstorming)

- **Purpose:** deployable *and* interactive — but interactivity is browsing, not
  live execution.
- **Interactivity depth:** pre-rendered output, no live exec.
- **Visual direction:** terminal / phosphor-green (CRT), with one borrowing from
  the editorial direction — a short caption line under each output block.
- **Layout:** boot-menu launcher (grid landing → full-screen session view).
- **Accent:** subtle per-theme accent tint over the phosphor base (not strict
  monochrome).
- **Capture scope (v1):** `demo.py` only per lab.

## The experience

### Landing — boot-menu launcher
- Phosphor-green terminal styling on near-black.
- ASCII title banner + one-line subtitle ("N working AI-agent MVPs, offline,
  from scratch").
- A grid of every lab as `[NN] name — one-line tagline`. Taglines come from the
  existing README table (no duplicated copy).
- Theme filter chips + a `/` search box that fuzzy-filters the grid as you type.

### Session view — one lab
- A terminal window: prompt line `$ python -m labs.<name>.demo`, then the lab's
  **real captured stdout** in mono phosphor.
- A short **caption** under each output block explaining what the visitor is
  seeing (the one editorial borrow).
- Footer controls: `← back to menu`, `‹ prev / next ›` lab, `view source` link
  to the lab's folder/README on GitHub.
- A `▶ replay` toggle that progressively types out the pre-captured text — a
  reveal animation only, **no live execution**.

## Architecture — three decoupled pieces

### 1. Generator — `labs/_showcase/build.py` (stdlib only)
Responsibilities:
- Discover labs by globbing `labs/*/demo.py` (skips `_kernel`, `_showcase`).
- Run each `demo.py` in a subprocess (`python -m labs.<name>.demo`), capturing
  stdout. Fail the build if any demo exits non-zero or emits nothing.
- Parse the `labs/README.md` MVP table to extract each lab's `tagline` (the
  "What it is" column) and `inspired_by` ("Inspired by" column).
- Apply a small in-generator theme map (lab name → primary theme).
- Render `data.json` + static HTML/CSS/JS into an output dir (default `site/`).

Interface: `python -m labs._showcase.build --out site/`. Depends on Python
stdlib only. Deterministic — seeded demos produce stable captures.

### 2. Frontend — `labs/_showcase/static/`
Hand-written `index.html`, `app.js`, `style.css`. Vanilla — **no framework, no
Node, no build step**. Loads `data.json`, renders the launcher and session
views, and handles filter/search/replay entirely client-side. Runs by opening
`index.html` in any browser.

The generator copies `static/` into the output dir alongside the generated
`data.json`, producing a self-contained `site/`.

### 3. Deploy — `.github/workflows/showcase.yml`
On push to `main`: run the generator, upload the output as a GitHub Pages
artifact, deploy. Pages source = GitHub Actions. Build output (`site/`) is
gitignored; nothing generated is committed.

### Approaches considered
- **(chosen) stdlib generator + vanilla static site** — matches the repo's
  zero-dependency ethos, builds with one `python -m` command, slots into
  existing CI.
- Astro/Vite SSG — nicer component DX but drags a Node toolchain into a
  deliberately stdlib-only repo. Rejected.
- Hand-maintained HTML — doesn't scale to 35 labs and won't auto-grow. Rejected.

## Content model

Per lab, captured at build time:
- `name` — directory name.
- `theme` — primary theme tag (from the generator's theme map).
- `tagline`, `inspired_by` — parsed from `labs/README.md`.
- `demo` — captured stdout of `python -m labs.<name>.demo`.
- `source_url` — GitHub link to the lab folder.

Auto-discovery means the site grows as new labs land — no per-lab wiring.

**Themes (~6), one primary tag per lab,** kept in a single map in the generator
(so no edits to 35 lab folders):
Agents · Reinforcement Learning · Evolution & Swarms · Generative Models ·
Transformers & LLM internals · Classical AI & Math.

Each theme gets a subtle accent tint layered over the phosphor base.

## Build & deploy

```sh
python -m labs._showcase.build --out site/   # self-contained static site/
```
Open `site/index.html` locally, or let the Action publish to GitHub Pages on
every push to `main`. A failing demo capture fails the build — an extra
correctness gate alongside `labs-ci`.

## Testing

Generator gets stdlib `unittest` tests under `labs/_showcase/tests/`, runnable
via the existing `unittest discover -s labs -t . -p 'test_*.py'`:
- discovery finds every lab that has a `demo.py`;
- the README parser returns a non-empty tagline for each discovered lab;
- every demo capture exits 0 and is non-empty;
- emitted `data.json` matches its expected schema (required keys present);
- `data.json` contains exactly one entry per discovered lab (the frontend is a
  single page that renders all views client-side from this data — there is no
  per-lab HTML file);
- every lab in the theme map exists, and every discovered lab has a theme
  (no orphans on either side).

## Out of scope (YAGNI)

- Live Python / Pyodide execution.
- Any backend.
- Per-lab parameter controls.
- `cli.py` variant captures (v1 is `demo.py` only).
- Custom domain, analytics.

All are straightforward to add later without reworking the architecture.

## Open risks / notes

- **Long outputs** (e.g. `morphogenesis`, `diffusion`) are captured in full; the
  session terminal pane scrolls. Acceptable for v1.
- **Demo runtime** in CI: capturing ~35 demos must stay within a reasonable CI
  budget; demos are fast (stdlib, seeded), but the build should run them
  sequentially with a per-demo timeout and surface any slow ones.
- **README table parsing** is coupled to the table's current shape; the parser
  should degrade gracefully (fall back to a blank tagline) rather than crash if
  a row is malformed, and a test guards the happy path.
