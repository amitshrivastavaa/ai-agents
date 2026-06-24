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
      <div class="cap">inspired by ${(lab.inspired_by && esc(lab.inspired_by)) || "—"}</div>
      <nav class="sessnav">
        <a href="#/${encodeURIComponent(prev.name)}">‹ ${esc(prev.name)}</a>
        <button id="replay">▶ replay</button>
        <a href="${encodeURI(lab.source_url)}" target="_blank" rel="noopener">view source ↗</a>
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
