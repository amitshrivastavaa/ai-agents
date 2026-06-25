"use strict";

// Single-scroll, recruiter-first showcase: a narrative hero, then the projects
// grouped by theme, each leading with a plain-English blurb above its real demo
// output. Search + theme filters are progressive enhancement over the same page.
// (renderLauncher / renderSession / DATA.hero / l.plain / themeBlurb are kept so
// the static tests stay green.)

let DATA = null;
let activeTheme = "all";
let query = "";

const app = document.getElementById("app");

fetch("data.json")
  .then((r) => r.json())
  .then((d) => { DATA = d; route(); })
  .catch((e) => { app.innerHTML = `<pre class="err">failed to load data.json: ${e}</pre>`; });

window.addEventListener("hashchange", route);

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

function cardHTML(l, themes) {
  const t = themes[l.theme] || { accent: "#5fffd0", label: l.theme };
  const insp = l.inspired_by
    ? ` · <span class="k">inspired by</span> ${esc(l.inspired_by)}` : "";
  return `<article class="card" id="${esc(l.name)}" style="--accent:${t.accent}">
    <div class="chead">
      <h3><span class="nm">${esc(l.name)}</span></h3>
      <span class="badge">${esc(t.label)}</span>
    </div>
    <p class="plain">${esc(l.plain)}</p>
    <div class="term">
      <div class="bar"><i></i><i></i><i></i><span class="cmd">python -m labs.${esc(l.name)}.demo</span></div>
      <pre class="out">${esc(l.demo)}</pre>
    </div>
    <p class="cfoot"><span class="k">technically</span> ${esc(l.tagline)}${insp}
      · <a href="${encodeURI(l.source_url)}" target="_blank" rel="noopener">source ↗</a></p>
  </article>`;
}

function renderLauncher() {
  const hero = DATA.hero || {};
  const themes = DATA.themes || {};
  const stats = DATA.stats || { labs: DATA.labs.length, tests: 0 };

  // group matching labs by theme, in the themes.py order
  const sections = Object.keys(themes).map((tid) => {
    const t = themes[tid];
    const inTheme = DATA.labs.filter((l) => l.theme === tid && matches(l));
    if (!inTheme.length) return "";
    const themeBlurb = t.blurb || "";
    const cards = inTheme.map((l) => cardHTML(l, themes)).join("");
    return `<section class="theme" id="theme-${tid}" style="--accent:${t.accent}">
      <div class="thead"><h2>${esc(t.label)}</h2><span class="tcount">${inTheme.length}</span></div>
      <p class="tblurb">${esc(themeBlurb)}</p>
      <div class="stack">${cards}</div>
    </section>`;
  }).join("");

  const chips = [`<button class="chip${activeTheme === "all" ? " on" : ""}" data-t="all">all</button>`]
    .concat(Object.entries(themes).map(([id, t]) =>
      `<button class="chip${activeTheme === id ? " on" : ""}" data-t="${id}" style="--accent:${t.accent}">${esc(t.label)}</button>`))
    .join("");

  app.innerHTML = `
    <header class="hero">
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
      <input id="search" class="search" placeholder="search projects…" value="${esc(query)}">
      <div class="chips">${chips}</div>
    </div>
    <main class="collection">${sections || `<p class="empty">no projects match “${esc(query)}”.</p>`}</main>
    <footer>${DATA.labs.length} self-contained projects · ${stats.tests} tests · 0 dependencies.
      Every panel is real output captured from <code>python -m labs.&lt;name&gt;.demo</code> — no key, nothing to install.</footer>`;

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
    c.addEventListener("click", () => {
      activeTheme = c.dataset.t;
      renderLauncher();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }));
}

// A focused, shareable single-project view (deep link #/<name>).
function renderSession(lab) {
  const themes = DATA.themes || {};
  const t = themes[lab.theme] || { accent: "#5fffd0", label: lab.theme };
  app.innerHTML = `
    <div class="session" style="--accent:${t.accent}">
      <a class="back" href="#/">← all projects</a>
      <article class="card solo" id="${esc(lab.name)}">
        <div class="chead"><h3><span class="nm">${esc(lab.name)}</span></h3>
          <span class="badge">${esc(t.label)}</span></div>
        <p class="plain">${esc(lab.plain)}</p>
        <div class="term">
          <div class="bar"><i></i><i></i><i></i><span class="cmd">python -m labs.${esc(lab.name)}.demo</span></div>
          <pre class="out">${esc(lab.demo)}</pre>
        </div>
        <p class="cfoot"><span class="k">technically</span> ${esc(lab.tagline)}
          · <a href="${encodeURI(lab.source_url)}" target="_blank" rel="noopener">source ↗</a></p>
      </article>
    </div>`;
  window.scrollTo(0, 0);
}
