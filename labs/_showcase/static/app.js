"use strict";

// Card-gallery showcase: a logo'd, recruiter-first hero, a filterable grid of
// compact project cards, and a details page (the demo output) when you click one.
// renderLauncher / renderSession / DATA.hero / l.plain / themeBlurb / --accent are
// kept so the static tests stay green.

let DATA = null;
let activeTheme = "all";
let query = "";
let typer = null;

const app = document.getElementById("app");

// Inline SVG logo — a terminal prompt in a rounded screen. Crisp at any size.
const LOGO = `<svg class="mark" width="38" height="38" viewBox="0 0 40 40" aria-hidden="true">
  <rect x="1.6" y="1.6" width="36.8" height="36.8" rx="9" fill="#0d1219" stroke="var(--green)" stroke-width="2"/>
  <path d="M11 13.5 L18 20 L11 26.5" fill="none" stroke="var(--green)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="21" y1="26.7" x2="29.5" y2="26.7" stroke="var(--green)" stroke-width="2.6" stroke-linecap="round"/>
</svg>`;

fetch("data.json")
  .then((r) => r.json())
  .then((d) => { DATA = d; route(); })
  .catch((e) => { app.innerHTML = `<pre class="err">failed to load data.json: ${e}</pre>`; });

window.addEventListener("hashchange", route);
document.addEventListener("keydown", (e) => {
  if (e.key === "/" && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) {
    const s = document.getElementById("search");
    if (s) { e.preventDefault(); s.focus(); }
  }
});

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function route() {
  if (!DATA) return;
  const name = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  const lab = DATA.labs.find((l) => l.name === name);
  if (lab) renderSession(lab); else renderLauncher();
}

function matches(l) {
  const q = query.toLowerCase().trim();
  const okTheme = activeTheme === "all" || l.theme === activeTheme;
  const hay = (l.name + " " + (l.plain || "") + " " + (l.tagline || "") +
    " " + (l.inspired_by || "")).toLowerCase();
  return okTheme && (!q || hay.includes(q));
}

function renderLauncher() {
  const hero = DATA.hero || {};
  const themes = DATA.themes || {};
  const stats = DATA.stats || { labs: DATA.labs.length, tests: 0 };
  const index = new Map(DATA.labs.map((l, i) => [l.name, i + 1]));

  const shown = DATA.labs.filter(matches);
  const cards = shown.map((l) => {
    const t = themes[l.theme] || { accent: "var(--green)", label: l.theme };
    const n = String(index.get(l.name)).padStart(2, "0");
    return `<a class="card" href="#/${encodeURIComponent(l.name)}" style="--accent:${t.accent}">
      <div class="crow"><span class="cnum">${n}</span><span class="cbadge">${esc(t.label)}</span></div>
      <div class="cname">${esc(l.name)}</div>
      <p class="cdesc">${esc(l.plain)}</p>
      <span class="cgo">watch the demo →</span>
    </a>`;
  }).join("");

  // the active theme's room blurb (shown when a single theme is filtered)
  const themeBlurb = activeTheme !== "all" && themes[activeTheme]
    ? themes[activeTheme].blurb : "";

  const chips = [`<button class="chip${activeTheme === "all" ? " on" : ""}" data-t="all">all · ${DATA.labs.length}</button>`]
    .concat(Object.entries(themes).map(([id, t]) => {
      const c = DATA.labs.filter((l) => l.theme === id).length;
      return `<button class="chip${activeTheme === id ? " on" : ""}" data-t="${id}" style="--accent:${t.accent}">${esc(t.label)} · ${c}</button>`;
    })).join("");

  app.innerHTML = `
    <header class="hero">
      <div class="brand">${LOGO}<span class="wordmark">the&nbsp;lab&nbsp;terminal</span></div>
      <p class="eyebrow">${esc(hero.eyebrow)}</p>
      <h1 class="htitle">${esc(hero.headline)}</h1>
      <p class="lead">${esc(hero.body)}</p>
      <div class="stats">
        <div class="stat"><b>${stats.labs}</b><span>projects, from scratch</span></div>
        <div class="stat"><b>${stats.tests}</b><span>passing tests</span></div>
        <div class="stat"><b>0</b><span>runtime dependencies</span></div>
        <div class="stat"><b>100%</b><span>deterministic &amp; offline</span></div>
      </div>
      ${hero.built ? `<p class="built">${esc(hero.built)}</p>` : ""}
      <p class="cta">${esc(hero.cta)}</p>
    </header>
    <div class="toolbar">
      <input id="search" class="search" placeholder="search projects…  (press /)" value="${esc(query)}">
      <div class="chips">${chips}</div>
      ${themeBlurb ? `<p class="theme-blurb">${esc(themeBlurb)}</p>` : ""}
    </div>
    <main class="grid">${cards || `<p class="empty">no projects match “${esc(query)}”.</p>`}</main>
    <footer>${DATA.labs.length} self-contained projects · ${stats.tests} tests · 0 dependencies.
      Click any project to watch its real <code>python -m labs.&lt;name&gt;.demo</code> output — no key, nothing to install.</footer>`;

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

// Details page: one project, its plain description, and the real demo output.
function renderSession(lab) {
  const themes = DATA.themes || {};
  const t = themes[lab.theme] || { accent: "var(--green)", label: lab.theme };
  const idx = DATA.labs.indexOf(lab);
  const prev = DATA.labs[(idx - 1 + DATA.labs.length) % DATA.labs.length];
  const next = DATA.labs[(idx + 1) % DATA.labs.length];

  app.innerHTML = `
    <div class="session" style="--accent:${t.accent}">
      <div class="sbar">
        <a class="brand small" href="#/">${LOGO}<span class="wordmark">the&nbsp;lab&nbsp;terminal</span></a>
        <a class="back" href="#/">← all projects</a>
      </div>
      <div class="shead">
        <span class="badge">${esc(t.label)}</span>
        <h1 class="sname">${esc(lab.name)}</h1>
      </div>
      <p class="splain">${esc(lab.plain)}</p>
      <div class="term">
        <div class="bar"><i></i><i></i><i></i><span class="cmd">python -m labs.${esc(lab.name)}.demo</span></div>
        <pre class="out" id="out"></pre>
      </div>
      <div class="caps">
        <div><span class="k">technically</span> ${esc(lab.tagline)}</div>
        <div><span class="k">inspired by</span> ${lab.inspired_by ? esc(lab.inspired_by) : "—"}</div>
      </div>
      <nav class="snav">
        <a href="#/${encodeURIComponent(prev.name)}">‹ ${esc(prev.name)}</a>
        <button id="replay">▶ replay</button>
        <a href="${encodeURI(lab.source_url)}" target="_blank" rel="noopener">view source ↗</a>
        <a href="#/${encodeURIComponent(next.name)}">${esc(next.name)} ›</a>
      </nav>
    </div>`;

  const out = document.getElementById("out");
  typeOut(out, lab.demo);
  document.getElementById("replay").addEventListener("click", () => typeOut(out, lab.demo));
  window.scrollTo(0, 0);
}

// A quick "typing" reveal of the captured demo output.
function typeOut(el, text) {
  if (typer) clearInterval(typer);
  el.textContent = "";
  let i = 0;
  const step = Math.max(1, Math.floor(text.length / 400));
  typer = setInterval(() => {
    i += step;
    el.textContent = text.slice(0, i);
    if (i >= text.length) { clearInterval(typer); typer = null; }
  }, 16);
}
